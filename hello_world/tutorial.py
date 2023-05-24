import copy

from perplexity.execution import report_error, call, execution_context
from perplexity.generation import english_for_delphin_variable
from perplexity.plurals import VariableCriteria
from perplexity.predications import combinatorial_style_predication_1, in_style_predication_2, lift_style_predication_2, \
    quantifier_raw
from perplexity.response import RespondOperation
from perplexity.state import State
from perplexity.system_vocabulary import system_vocabulary
from perplexity.user_interface import UserInterface
from perplexity.utilities import ShowLogging
from perplexity.vocabulary import Vocabulary, Predication, EventOption
from perplexity.tree import find_predication_from_introduced
from collections import deque
import perplexity.messages

vocabulary = system_vocabulary()


class WorldState(State):
    def __init__(self, relations, entities, system):
        super().__init__([])
        self.rel = relations
        self.ent = entities
        self.sys = system

    def all_individuals(self):
        for i in self.ent:
            return i

    def add_rel(self, first, relname, second):
        newrel = copy.deepcopy(self.rel)
        if not relname in newrel:
            newrel[relname] = [(first, second)]
        else:
            newrel[relname] += [(first, second)]
        return WorldState(newrel, self.ent, self.sys)

    def _mutate_add_rel(self, first, relname, second):
        newrel = copy.deepcopy(self.rel)
        if not relname in newrel:
            newrel[relname] = [(first, second)]
        else:
            newrel[relname] += [(first, second)]
        self.rel = newrel

    def _mutate_reset_rel(self, keyname):
        newrel = copy.deepcopy(self.rel)
        newrel.pop(keyname, None)
        self.rel = newrel
    def _mutate_set_bill(self, newval):
        newrel = copy.deepcopy(self.rel)
        for i in range(len(newrel["valueOf"])):
            if newrel["valueOf"][i][1] == "bill1":
                newrel["valueOf"][i][0] = (newval, "bill1")
        self.rel = newrel
    def _mutate_add_bill(self, addition):
        newrel = copy.deepcopy(self.rel)
        for i in range(len(newrel["valueOf"])):
            if newrel["valueOf"][i][1] == "bill1":
                newrel["valueOf"][i] = (addition + newrel["valueOf"][i][0], "bill1")
        self.rel = newrel

    def _mutate_set_response_state(self, newState):
        self.sys["responseState"] = newState

def sort_of(state, thing, possible_type):
    if thing == possible_type:
        return True
    for i in state.rel["specializes"]:
        if i[1] == possible_type:
            if sort_of(state, thing, i[0]):
                return True
    for i in state.rel["instanceOf"]:
        if i[1] == possible_type:
            if sort_of(state, thing, i[0]):
                return True
    return False


def all_instances(state, thing):
    proc = [thing]
    proc_idx = 0
    inst = set()

    # for i in state.rel["instanceOf"]:
    #    if(i[0] == thing):
    #        return thing

    while proc_idx < len(proc):
        to_process = proc[proc_idx]
        for i in state.rel["specializes"]:
            if i[1] == to_process:
                if i[0] not in proc:
                    proc += [i[0]]
        for i in state.rel["instanceOf"]:
            if i[1] == to_process:
                if i[0] not in inst:
                    yield i[0]
                    inst.add(i[0])
        proc_idx += 1


def all_instances_and_spec(state, thing):
    yield thing

    proc = [thing]
    proc_idx = 0
    inst = set()

    while proc_idx < len(proc):
        to_process = proc[proc_idx]
        for i in state.rel["specializes"]:
            if i[1] == to_process:
                if i[0] not in proc:
                    proc += [i[0]]
                    yield i[0]
        for i in state.rel["instanceOf"]:
            if i[1] == to_process:
                if i[0] not in inst:
                    yield i[0]
                    inst.add(i[0])
        proc_idx += 1


def all_ancestors(state, thing):
    proc = [thing]
    proc_idx = 0

    while proc_idx < len(proc):
        to_process = proc[proc_idx]
        for i in state.rel["instanceOf"]:
            if i[0] == to_process:
                if i[1] not in proc:
                    yield i[1]
                    proc += [i[1]]

        for i in state.rel["specializes"]:
            if i[0] == to_process:
                if i[1] not in proc:
                    proc += [i[1]]
                    yield i[1]
        proc_idx += 1


class AddRelOp(object):
    def __init__(self, rel):
        self.toAdd = rel

    def apply_to(self, state):
        state._mutate_add_rel(self.toAdd[0], self.toAdd[1], self.toAdd[2])

class AddBillOp(object):
    def __init__(self, item):
        self.toAdd = item

    def apply_to(self, state):
        prices = state.sys["prices"]
        assert(self.toAdd in prices)
        state._mutate_add_bill(prices[self.toAdd])

class ResponseStateOp(object):
    def __init__(self, item):
        self.toAdd = item

    def apply_to(self, state):
        state._mutate_set_response_state(self.toAdd)

def user_wants(state, wanted):
    if not wanted in state.ent:
        return [RespondOperation("Sorry, we don't have that.")]

    for i in all_instances_and_spec(state, "food"):
        if i == wanted:
            if "at" in state.rel.keys():
                if ("user", "table") in state.rel["at"]:
                    if "ordered" in state.rel.keys():
                        if ("user", wanted) in state.rel["ordered"]:
                            return [RespondOperation("Sorry, you got the last one of those. We don't have any more.")]

                    return [RespondOperation("Excellent Choice! Can I get you anything else?"),
                            AddRelOp(("user", "ordered", wanted)), AddBillOp(wanted), ResponseStateOp("anything_else")]
            return [RespondOperation("Sorry, you must be seated to order")]

    for i in all_instances_and_spec(state, "table"):
        if i == wanted:
            if "at" in state.rel.keys():
                if ("user", "table") in state.rel["at"]:
                    return [RespondOperation("Um... You're at a table")]
            return [AddRelOp(("user", "at", "table")),
                    RespondOperation(
                        "Robot: Right this way!\nThe robot shows you to a wooden table\nRobot: I hope you have a lovely dining experience with us today. Make sure to ask your waiter for the specials!\nA minute passes \nRobot Waiter: Hello! How can I help you?")]
    for i in all_instances_and_spec(state, "menu"):
        if i == wanted:
            if "at" in state.rel.keys():
                if ("user", "table") in state.rel["at"]:
                    return [RespondOperation("Here's the menu...\n...menu goes here...")]
            return [RespondOperation("Sorry, you must be seated to order")]

    if wanted == "bill1":
        for i in state.rel["valueOf"]:
            if i[1] == "bill1":
                total = i[0]
                if not total == 0:
                    return [RespondOperation("Your total is " + str(total) + " dollars. Would you like to pay by cash or card?"),ResponseStateOp("way_to_pay")]
                else:
                    return [RespondOperation("But... you haven't ordered anything yet!")]

    return [RespondOperation("Sorry, I can't get that for you at the moment.")]


@Predication(vocabulary, names=["pron"])
def pron(state, x_who_binding):
    person = int(state.get_binding("tree").value[0]["Variables"][x_who_binding.variable.name]["PERS"])

    def bound_variable(value):
        if person == 2 and value == "computer":
            return True
        if person == 1 and value == "user":
            return True
        else:
            report_error(["dontKnowActor", x_who_binding.variable.name])

    def unbound_variable():
        if person == 2:
            yield "computer"
        if person == 1:
            yield "user"
        else:
            report_error(["dontKnowActor", x_who_binding.variable.name])

    yield from combinatorial_style_predication_1(state, x_who_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["generic_entity"])
def generic_entity(state, x_who_binding):
    def bound(val):
        return val in state.ent

    def unbound():
        for i in state.ent:
            yield i

    yield from combinatorial_style_predication_1(state, x_who_binding, bound, unbound)

@Predication(vocabulary, names=["_cash_n_1"])
def _cash_n_1(state, x_bind):
    def bound(val):
        return val == "cash"

    def unbound():
        yield "cash"

    yield from combinatorial_style_predication_1(state, x_bind, bound, unbound)

@Predication(vocabulary, names=["_card_n_1"])
def _card_n_1(state, x_bind):
    def bound(val):
        return val == "card"

    def unbound():
        yield "card"

    yield from combinatorial_style_predication_1(state, x_bind, bound, unbound)



@Predication(vocabulary, names=["unknown"])
def unknown(state, e_binding, x_binding):
    if x_binding.value[0] in ["cash","card"] and state.sys["responseState"] == "way_to_pay":
        yield state.record_operations([RespondOperation("Ah. Perfect!")])
    else:
        yield state.record_operations([RespondOperation("Hmm. I didn't understand what you said. Could you say it another way?")])
@Predication(vocabulary, names=["unknown"])
def unknown_eu(state, e_binding, u_binding):
    yield state

@Predication(vocabulary, names=["_yes_a_1"])
def _yes_a_1(state, i_binding, h_binding):
    if state.sys["responseState"] == "anything_else":
        yield state.record_operations([RespondOperation("What else?"), ResponseStateOp("anticipate_dish")])
    else:
        yield state.record_operations([RespondOperation("Hmm. I didn't understand what you said. Could you say it another way?")])

@Predication(vocabulary, names=["_no_a_1"])
def _no_a_1(state, i_binding, h_binding):
    if state.sys["responseState"] == "anything_else":
        yield state.record_operations([RespondOperation("Ok, I'll be right back with your meal")])
    else:
        yield state.record_operations([RespondOperation("Hmm. I didn't understand what you said. Could you say it another way?")])


def handles_noun(noun_lemma):
    return noun_lemma in ["special", "food", "menu", "soup", "salad", "table", "thing", "steak", "meat", "bill", "check"]


# Simple example of using match_all that doesn't do anything except
# make sure we don't say "I don't know the word book"
@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=handles_noun)
def match_all_n(noun_type, state, x_binding):
    def bound_variable(value):
        if sort_of(state, value, noun_type):
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield from all_instances(state, noun_type)

    yield from combinatorial_style_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=handles_noun)
def match_all_n_i(noun_type, state, x_binding, i_binding):
    return match_all_n(noun_type, state, x_binding)


@Predication(vocabulary, names=("_on_p_loc",))
def on_p_loc(state, e_introduced_binding, x_actor_binding, x_location_binding):
    def check_item_on_item(item1, item2):
        if "on" in state.rel.keys():
            return (item1, item2) in state.rel["on"]
        else:
            report_error(["notOn"])

    def all_item1_on_item2(item2):
        if "on" in state.rel.keys():
            for i in state.rel["on"]:
                if i[1] == item2:
                    yield i[0]

    def all_item2_containing_item1(item1):
        if "on" in state.rel.keys():
            for i in state.rel["on"]:
                if i[0] == item1:
                    yield i[1]

    yield from in_style_predication_2(state,
                                      x_actor_binding,
                                      x_location_binding,
                                      check_item_on_item,
                                      all_item1_on_item2,
                                      all_item2_containing_item1)


@Predication(vocabulary, names=["_want_v_1"])
def _want_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor_binding, x_object_binding):
        if "want" in state.rel.keys():
            if (x_actor_binding, x_object_binding) in state.rel["want"]:
                return True
        elif x_actor_binding == "user":
            return True
        else:
            report_error(["verbDoesntApply", "want", x_actor_binding.variable.name])
            return False

    def wanters_of_obj(x_object_binding):
        if "want" in state.rel.keys():
            for i in state.rel["want"]:
                if i[1] == x_object_binding:
                    yield i[0]

    def wanted_of_actor(x_actor_binding):
        if "want" in state.rel.keys():
            for i in state.rel["want"]:
                if i[0] == x_actor_binding:
                    yield i[1]

    for success_state in in_style_predication_2(state, x_actor_binding, x_object_binding, criteria_bound,
                                                wanters_of_obj, wanted_of_actor):
        x_act = success_state.get_binding(x_actor_binding.variable.name).value[0]
        x_obj = success_state.get_binding(x_object_binding.variable.name).value[0]
        if x_act == "user":
            if not x_obj is None:
                yield success_state.record_operations(user_wants(state, x_obj))

@Predication(vocabulary, names=["_check_v_1"])
def _check_v_1(state, e_introduced_binding, x_actor_binding, i_object_binding):
    if i_object_binding.value is not None:
        return

    def criteria_bound(x):
        return x == "computer"

    def unbound():
        if False:
            yield None

    for success_state in combinatorial_style_predication_1(state, x_actor_binding, criteria_bound, unbound):
            yield success_state.record_operations(user_wants(state, "bill1"))


@Predication(vocabulary, names=["_give_v_1", "_get_v_1"])
def _give_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding, x_target_binding):
    if state.get_binding(x_actor_binding.variable.name).value[0] == "computer":
        if state.get_binding(x_target_binding.variable.name).value[0] == "user":
            if not state.get_binding(x_object_binding.variable.name).value[0] is None:
                yield state.record_operations(
                    user_wants(state, state.get_binding(x_object_binding.variable.name).value[0]))

@Predication(vocabulary, names=["_show_v_1"])
def _show_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding, x_target_binding):
    if state.get_binding(x_actor_binding.variable.name).value[0] == "computer":
        if state.get_binding(x_target_binding.variable.name).value[0] == "user":
            if not state.get_binding(x_object_binding.variable.name).value[0] is None:
                if state.get_binding(x_object_binding.variable.name).value[0] == "menu1":
                    yield state.record_operations(
                        user_wants(state, state.get_binding(x_object_binding.variable.name).value[0]))


@Predication(vocabulary, names=["loc_nonsp"])
def loc_nonsp(state, e_introduced_binding, x_actor_binding, x_loc_binding):
    def item1_in_item2(item1, item2):
        if item2 == "today":
            return True

        if (item1, item2) in state.rel["contains"]:
            return True
        return False

    def items_in_item1(item1):
        for i in state.rel["contains"]:
            if i[0] == item1:
                yield i[1]

    def item1_in_items(item1):
        for i in state.rel["contains"]:
            if i[1] == item1:
                yield i[0]

    yield from in_style_predication_2(state, x_actor_binding, x_loc_binding, item1_in_item2, items_in_item1,
                                      item1_in_items)


@Predication(vocabulary, names=["loc_nonsp"])
def loc_nonsp_eex(state, e_introduced_binding, e_binding, x_loc_binding):
    yield state


@Predication(vocabulary, names=["_today_a_1"])
def _today_a_1(state, e_introduced_binding, x_binding):
    def bound_variable(value):
        if value in ["today"]:
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "today"

    yield from combinatorial_style_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["time_n"])
def time_n(state, x_binding):
    def bound_variable(value):
        if value in ["today", "yesterday", "tomorrow"]:
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "today"
        yield "yesterday"
        yield "tomorrow"

    yield from combinatorial_style_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["def_implicit_q", "def_explicit_q"])
def def_implicit_q(state, x_variable_binding, h_rstr, h_body):
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(execution_context().current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf')))

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body)


@Predication(vocabulary, names=["_like_v_1"])
def _like_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding):
    if state.get_binding(x_actor_binding.variable.name).value[0] == "user":
        if not state.get_binding(x_object_binding.variable.name).value[0] is None:
            yield state.record_operations(user_wants(state, state.get_binding(x_object_binding.variable.name).value[0]))


@Predication(vocabulary, names=["_would_v_modal"])
def _would_v_modal(state, e_introduced_binding, h_binding):
    yield from call(state, h_binding)


@Predication(vocabulary, names=["_please_a_1"])
def _please_a_1(state, e_introduced_binding, e_binding):
    yield state


@Predication(vocabulary, names=["_could_v_modal", "_can_v_modal"])
def _could_v_modal(state, e_introduced_binding, h_binding):
    yield from call(state, h_binding)


@Predication(vocabulary, names=["polite"])
def polite(state, c_arg, i_binding, e_binding):
    yield state

@Predication(vocabulary, names=["_thanks_a_1"])
def _thanks_a_1(state, i_binding, h_binding):
    yield from call(state,h_binding)

@Predication(vocabulary, names=["_have_v_1","_get_v_1"])
def _have_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor_binding, x_object_binding):
        j = state.get_binding("tree").value[0]["Index"]
        is_cond = find_predication_from_introduced(state.get_binding("tree").value[0]["Tree"], j).name in [
            "_could_v_modal", "_can_v_modal"]
        if (is_cond):
            return True
        else:
            if "have" in state.rel.keys():
                if (x_actor_binding, x_object_binding) in state.rel["have"]:
                    return True

            else:
                report_error(["verbDoesntApply", "large", x_actor_binding.variable.name])
                return False

    def havers_of_obj(x_object_binding):
        if "have" in state.rel.keys():
            for i in state.rel["have"]:
                if i[1] == x_object_binding:
                    yield i[0]

    def had_of_actor(x_actor_binding):
        if "have" in state.rel.keys():
            for i in state.rel["have"]:
                if i[0] == x_actor_binding:
                    yield i[1]

    for success_state in in_style_predication_2(state, x_actor_binding, x_object_binding, criteria_bound, havers_of_obj,
                                                had_of_actor):
        x_act = success_state.get_binding(x_actor_binding.variable.name).value[0]
        x_obj = success_state.get_binding(x_object_binding.variable.name).value[0]

        j = state.get_binding("tree").value[0]["Index"]
        is_cond = find_predication_from_introduced(state.get_binding("tree").value[0]["Tree"],
                                                   j).name in ["_could_v_modal", "_can_v_modal"]
        if is_cond:
            if x_act == "user":
                if not x_obj is None:
                    yield success_state.record_operations(user_wants(state, x_obj))
        else:
            yield success_state




@Predication(vocabulary, names=["poss"])
def poss(state, e_introduced_binding, x_object_binding, x_actor_binding):
    yield from _have_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding)


@Predication(vocabulary, names=["_be_v_id"])
def _be_v_id(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor_binding, x_object_binding):
        first_in_second = x_actor_binding in all_instances_and_spec(state, x_object_binding)
        second_in_first = x_object_binding in all_instances_and_spec(state, x_actor_binding)

        return first_in_second or second_in_first

    def unbound(x_object_binding):
        for i in all_instances(state, x_object_binding):
            yield i
        yield x_object_binding

    yield from in_style_predication_2(state, x_actor_binding, x_object_binding, criteria_bound, unbound,
                                      unbound)


@Predication(vocabulary, names=["_be_v_there"])
def _be_v_there(state, e_introduced_binding, x_object_binding):
    def bound_variable(value):
        yield value in state.ent

    def unbound_variable():
        for i in state.ent:
            yield i

    yield from combinatorial_style_predication_1(state, x_object_binding, bound_variable, unbound_variable)


# Generates all the responses that predications can
# return when an error occurs
def generate_custom_message(tree_info, error_term):
    # See if the system can handle converting the error
    # to a message first
    system_message = perplexity.messages.generate_message(tree_info, error_term)
    if system_message is not None:
        return system_message

    # error_term is of the form: [index, error] where "error" is another
    # list like: ["name", arg1, arg2, ...]. The first item is the error
    # constant (i.e. its name). What the args mean depends on the error
    error_predicate_index = error_term[0]
    error_arguments = error_term[1]
    error_constant = error_arguments[0] if error_arguments is not None else "no error set"

    if error_constant == "notAThing":
        arg1 = error_arguments[1]
        # english_for_delphin_variable() converts a variable name like 'x3' into the english words
        # that it represented in the MRS
        arg2 = english_for_delphin_variable(error_predicate_index, error_arguments[2], tree_info)
        return f"{arg1} is not {arg2}"

    else:
        # No custom message, just return the raw error for debugging
        return str(error_term)


def reset():
    # return State([])
    # initial_state = WorldState({}, ["pizza", "computer", "salad", "soup", "steak", "ham", "meat","special"])
    initial_state = WorldState({},
                               ["salad", "soup", "soup1", "special", "salad1", "table", "table1", "menu", "menu1",
                                    "pizza", "pizza1", "steak", "steak1", "meat", "bill", "bill1", "check"],
                               {"prices": {"salad1": 3, "steak1": 10, "soup1": 4}, "responseState" : "default"

                                })

    initial_state = initial_state.add_rel("special", "specializes", "food")
    initial_state = initial_state.add_rel("table", "specializes", "thing")
    initial_state = initial_state.add_rel("menu", "specializes", "thing")
    initial_state = initial_state.add_rel("food", "specializes", "thing")
    initial_state = initial_state.add_rel("pizza", "specializes", "food")
    initial_state = initial_state.add_rel("meat", "specializes", "food")
    initial_state = initial_state.add_rel("steak", "specializes", "meat")

    initial_state = initial_state.add_rel("salad1", "instanceOf", "salad")
    initial_state = initial_state.add_rel("table1", "instanceOf", "table")
    initial_state = initial_state.add_rel("soup1", "instanceOf", "soup")
    initial_state = initial_state.add_rel("menu1", "instanceOf", "menu")
    initial_state = initial_state.add_rel("pizza1", "instanceOf", "pizza")
    initial_state = initial_state.add_rel("steak1", "instanceOf", "steak")

    initial_state = initial_state.add_rel("soup", "specializes", "special")
    initial_state = initial_state.add_rel("salad", "specializes", "special")
    initial_state = initial_state.add_rel("computer", "have", "salad1")
    initial_state = initial_state.add_rel("computer", "have", "soup1")
    initial_state = initial_state.add_rel("computer", "have", "steak1")
    initial_state = initial_state.add_rel("user","have","bill1")

    initial_state = initial_state.add_rel("steak1", "on", "menu1")

    initial_state = initial_state.add_rel("bill", "specializes", "thing")
    initial_state = initial_state.add_rel("check", "specializes", "thing")
    initial_state = initial_state.add_rel("bill1", "instanceOf", "bill")
    initial_state = initial_state.add_rel("bill1", "instanceOf", "check")
    initial_state = initial_state.add_rel(0, "valueOf", "bill1")

    initial_state = initial_state.add_rel("room", "contains", "user")

    return initial_state


def hello_world():
    user_interface = UserInterface(reset, vocabulary)

    while True:
        user_interface.interact_once()
        print()


if __name__ == '__main__':
    ShowLogging("Pipeline")
    hello_world()
