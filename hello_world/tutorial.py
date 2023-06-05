import copy
import json

import perplexity.messages
from perplexity.execution import report_error, call, execution_context
from perplexity.generation import english_for_delphin_variable
from perplexity.plurals import VariableCriteria
from perplexity.predications import combinatorial_predication_1, in_style_predication_2, \
    lift_style_predication_2
from perplexity.response import RespondOperation
from perplexity.set_utilities import Measurement
from perplexity.state import State
from perplexity.system_vocabulary import system_vocabulary, quantifier_raw
from perplexity.tree import find_predication_from_introduced
from perplexity.user_interface import UserInterface
from perplexity.utilities import ShowLogging
from perplexity.vocabulary import Predication, EventOption, ValueSize

vocabulary = system_vocabulary()


class WorldState(State):
    def __init__(self, relations, system):
        super().__init__([])
        self.rel = relations
        self.sys = system

    def all_individuals(self):
        for i in self.get_entities():
            yield i

    def add_rel(self, first, relation_name, second):
        new_relation = copy.deepcopy(self.rel)
        if relation_name not in new_relation:
            new_relation[relation_name] = [(first, second)]
        else:
            new_relation[relation_name] += [(first, second)]
        return WorldState(new_relation, self.sys)

    def mutate_add_rel(self, first, relation_name, second):
        new_relation = copy.deepcopy(self.rel)
        if relation_name not in new_relation:
            new_relation[relation_name] = [(first, second)]
        else:
            new_relation[relation_name] += [(first, second)]
        self.rel = new_relation

    def mutate_reset_rel(self, keyname):
        new_relation = copy.deepcopy(self.rel)
        new_relation.pop(keyname, None)
        self.rel = new_relation

    def mutate_add_bill(self, addition):
        new_relation = copy.deepcopy(self.rel)
        for i in range(len(new_relation["valueOf"])):
            if new_relation["valueOf"][i][1] == "bill1":
                new_relation["valueOf"][i] = (addition + new_relation["valueOf"][i][0], "bill1")
        self.rel = new_relation

    def mutate_set_response_state(self, new_state):
        self.sys["responseState"] = new_state

    def get_entities(self):
        entities = set()
        for i in self.rel.keys():
            for j in self.rel[i]:
                entities.add(j[0])
                entities.add(j[1])
        return entities

    def user_wants(self, wanted):
        # if wanted not in self.get_entities():
        #   return [RespondOperation("Sorry, we don't have that.")]

        if wanted[0] == "{":
            wanted_dict = json.loads(wanted)
            if wanted_dict["structure"] == "noun_for":
                if wanted_dict["noun"] == "table1":
                    if "at" in self.rel.keys():
                        if ("user", "table") in self.rel["at"]:
                            return [RespondOperation("Um... You're at a table. Can I get you something else?"),
                                    ResponseStateOp("anything_else")]
                    if wanted_dict["for_count"] > 2:
                        return [RespondOperation("Host: Sorry, we don't have a table with that many seats")]
                    if wanted_dict["for_count"] < 2:
                        return [RespondOperation("Johnny: Hey! That's not enough seats!")]
                    if wanted_dict["for_count"] == 2:
                        return (RespondOperation(
                            "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. "
                            "A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?"),
                                AddRelOp(("user", "at", "table")),ResponseStateOp("something_to_eat"))

                else:
                    wanted = wanted_dict["noun"]

        for i in all_instances_and_spec(self, "food"):
            if i == wanted:
                if "at" in self.rel.keys():
                    if ("user", "table") in self.rel["at"]:
                        if "ordered" in self.rel.keys():
                            if ("user", wanted) in self.rel["ordered"]:
                                return [RespondOperation(
                                    "Sorry, you got the last one of those. We don't have any more. Can I get you something else?"),
                                    ResponseStateOp("anything_else")]

                        return [RespondOperation("Excellent Choice! Can I get you anything else?"),
                                AddRelOp(("user", "ordered", wanted)), AddBillOp(wanted),
                                ResponseStateOp("anything_else")]
                return [RespondOperation("Sorry, you must be seated to order")]

        for i in all_instances_and_spec(self, "table"):
            if i == wanted:
                if "at" in self.rel.keys():
                    if ("user", "table") in self.rel["at"]:
                        return [RespondOperation("Um... You're at a table. Can I get you something else?"),
                                ResponseStateOp("anything_else")]
                return [RespondOperation("How many in your party?"), ResponseStateOp("anticipate_party_size")]
        for i in all_instances_and_spec(self, "menu"):
            if i == wanted:
                if "at" in self.rel.keys():
                    if ("user", "table") in self.rel["at"]:
                        if not ("user", "menu1") not in self.rel["have"]:
                            return [AddRelOp(("user", "have", "menu1")), RespondOperation("Waiter: Oh, I forgot to give you the menu? Here it is. The waiter walks off.\nSteak -- $5\nRoasted Chicken -- $7\nGrilled Salmon -- $12\nYou read the menu and then the waiter returns.\nWaiter: Have you decided what to order?"), ResponseStateOp("what_to_order")]
                        return [RespondOperation("Oh, I already gave you a menu. You look and see that there is a menu in front of you.\nSteak -- $5\nRoasted Chicken -- $7\nGrilled Salmon -- $12\nWaiter: Have you decided what to order?"), ResponseStateOp("what_to_order")]
                return [RespondOperation("Sorry, you must be seated to order")]

        if wanted == "bill1":
            for i in self.rel["valueOf"]:
                if i[1] == "bill1":
                    total = i[0]
                    if self.sys["responseState"] == "done_ordering":
                        return [RespondOperation(
                            "Your total is " + str(total) + " dollars. Would you like to pay by cash or card?"),
                            ResponseStateOp("way_to_pay")]
                    else:
                        return [RespondOperation("But... you haven't got any food yet!")]

        return [RespondOperation("Sorry, I can't get that for you at the moment.")]

    def user_wants_to_see(self, wanted):
        prompt_finish_order = "\nCan I get you anything else before I put your order in?" if self.sys[
                                                                                                 "responseState"] in [
                                                                                                 "anything_else",
                                                                                                 "anticipate_dish"] else ""
        if wanted == "menu1":
            return [RespondOperation("Here's the menu...\n...Steak -- $10..." + prompt_finish_order)]
        elif wanted == "table1":
            return [RespondOperation("All our tables are nice. Trust me on this one" + prompt_finish_order)]
        else:
            return [RespondOperation("Sorry, I can't show you that." + prompt_finish_order)]

    def no(self):
        if self.sys["responseState"] == "anything_else":
            items = [i for (x, i) in self.rel["ordered"]]
            for i in self.rel["have"]:
                if i[0] == "user":
                    if i[1] in items:
                        items.remove(i[1])

            item_str = " ".join(items)

            for i in items:
                self.add_rel("user", "have", i)

            return [RespondOperation(
                "Ok, I'll be right back with your meal.\nA few minutes go by and the robot returns with " + item_str + ".\nThe food is good, but nothing extraordinary."),
                ResponseStateOp("done_ordering")]
        elif self.sys["responseState"] == "initial":
            return [RespondOperation("Ok, Goodbye")]
        else:
            return [RespondOperation("Hmm. I didn't understand what you said. Could you say it another way?")]

    def yes(self):
        if self.sys["responseState"] in ["anything_else", "initial"]:
            return [RespondOperation("Ok, what?"), ResponseStateOp("anticipate_dish")]
        else:
            return [RespondOperation("Hmm. I didn't understand what you said. Could you say it another way?")]

    def unknown(self, x_binding):
        if self.sys["responseState"] == "way_to_pay":
            if x_binding.value[0] in ["cash", "card", "card, credit"]:
                return [RespondOperation("Ah. Perfect! Have a great rest of your day.")]
            else:
                return [RespondOperation("Hmm. I didn't understand what you said. Could you say it another way?")]
        elif self.sys["responseState"] in ["anticipate_dish", "anything_else", "initial"]:
            if x_binding.value[0] in self.get_entities():
                return self.handle_world_event(["user_wants", x_binding.value[0]])
            else:
                return [RespondOperation("Sorry, we don't have that")]
        elif self.sys["responseState"] in ["anticipate_party_size"]:
            if isinstance(x_binding.value[0], Measurement):
                return self.handle_world_event(["user_wants", json.dumps(
                    {"structure": "noun_for", "noun": "table1", "for_count": x_binding.value[0].count})])
            else:
                return [RespondOperation("Hmm. I didn't understand what you said. Could you say it another way?")]
        else:
            return [RespondOperation("Hmm. I didn't understand what you said. Could you say it another way?")]

    def party_size(self, args):
        if args[0] == "unknown":
            x_binding = args[1]
            if isinstance(x_binding.value[0], Measurement):
                return self.handle_world_event(["user_wants", json.dumps(
                    {"structure": "noun_for", "noun": "table1", "for_count": x_binding.value[0].count})])
            else:
                return [RespondOperation("Sorry, I didn't get that. How many in your party?")]
    def handle_world_event(self, args):
        # if self.sys["responseState"] == "anticipate_party_size":
        if args[0] == "user_wants":
            return self.user_wants(args[1])
        elif args[0] == "user_wants_to_see":
            return self.user_wants_to_see(args[1])
        elif args[0] == "no":
            return self.no()
        elif args[0] == "yes":
            return self.yes()
        elif args[0] == "unknown":
            return self.unknown(args[1])
        elif args[0] == "user_wants_to_sit":
            return self.user_wants("table1")


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
        state.mutate_add_rel(self.toAdd[0], self.toAdd[1], self.toAdd[2])


class AddBillOp(object):
    def __init__(self, item):
        self.toAdd = item

    def apply_to(self, state):
        prices = state.sys["prices"]
        assert (self.toAdd in prices)
        state.mutate_add_bill(prices[self.toAdd])


class ResponseStateOp(object):
    def __init__(self, item):
        self.toAdd = item

    def apply_to(self, state):
        state.mutate_set_response_state(self.toAdd)


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

    yield from combinatorial_predication_1(state, x_who_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["generic_entity"])
def generic_entity(state, x_binding):
    def bound(val):
        # return val in state.ent
        return True

    def unbound():
        # for i in state.ent:
        #    yield i
        yield "generic_entity"

    yield from combinatorial_predication_1(state, x_binding, bound, unbound)


@Predication(vocabulary, names=["_okay_a_1"])
def _okay_a_1(state, i_binding, h_binding):
    yield from call(state, h_binding)


@Predication(vocabulary, names=["much-many_a"], handles=[("relevant_var", EventOption.optional)])
def much_many_a(state, e_binding, x_binding):
    if "relevant_var" in e_binding.value.keys():
        yield state.set_x(x_binding.variable.name, (json.dumps(
            {"relevant_var_name": e_binding.value["relevant_var"], "relevant_var_value": "to_determine",
             "structure": "price_type"}),))


@Predication(vocabulary, names=["measure"])
def measure(state, e_binding, e_binding2, x_binding):
    yield state.add_to_e(e_binding2.variable.name, "relevant_var", x_binding.variable.name)


@Predication(vocabulary, names=["abstr_deg"])
def abstr_deg(state, x_binding):
    yield state.set_x(x_binding.variable.name, ("abstract_degree",))


@Predication(vocabulary, names=["card"])
def card(state, c_number, e_binding, x_binding):
    if state.get_binding(x_binding.variable.name).value[0] == "generic_entity":
        yield state.set_x(x_binding.variable.name, (Measurement("generic_cardinality", int(c_number)),))
    else:
        if state.get_binding(x_binding.variable.name).value[0] is str:
            yield state.set_x(x_binding.variable.name,
                              (Measurement(state.get_binding(x_binding.variable.name).value[0], int(c_number)),))


@Predication(vocabulary, names=["_for_p"])
def _for_p(state, e_binding, x_binding, x_binding2):
    what_is = state.get_binding(x_binding.variable.name).value[0]
    what_for = state.get_binding(x_binding2.variable.name).value[0]
    if not isinstance(what_for, Measurement):
        yield state
    else:
        what_measuring = what_for.measurement_type
        if not what_measuring == "generic_cardinality":
            yield state
        else:
            yield state.set_x(x_binding.variable.name,
                              (json.dumps({"structure": "noun_for", "noun": what_is, "for_count": what_for.count}),))


@Predication(vocabulary, names=["_cash_n_1"])
def _cash_n_1(state, x_bind):
    def bound(val):
        return val == "cash"

    def unbound():
        yield "cash"

    yield from combinatorial_predication_1(state, x_bind, bound, unbound)


@Predication(vocabulary, names=["_card_n_1"])
def _card_n_1(state, x_bind):
    def bound(val):
        return val == "card"

    def unbound():
        yield "card"

    yield from combinatorial_predication_1(state, x_bind, bound, unbound)


@Predication(vocabulary, names=["_credit_n_1"])
def _credit_n_1(state, x_bind):
    def bound(val):
        return val == "credit"

    def unbound():
        yield "credit"

    yield from combinatorial_predication_1(state, x_bind, bound, unbound)


@Predication(vocabulary, names=["unknown"])
def unknown(state, e_binding, x_binding):
    yield state.record_operations(state.handle_world_event(["unknown", x_binding]))


@Predication(vocabulary, names=["unknown"])
def unknown_eu(state, e_binding, u_binding):
    yield state


@Predication(vocabulary, names=["_yes_a_1", "_yup_a_1", "_sure_a_1"])
def _yes_a_1(state, i_binding, h_binding):
    yield state.record_operations(state.handle_world_event(["yes"]))


@Predication(vocabulary, names=["_no_a_1", "_nope_a_1"])
def _no_a_1(state, i_binding, h_binding):
    yield state.record_operations(state.handle_world_event(["no"]))


def handles_noun(noun_lemma):
    return noun_lemma in ["special", "food", "menu", "soup", "salad", "table", "thing", "steak", "meat", "bill",
                          "check"]


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

    yield from combinatorial_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=handles_noun)
def match_all_n_i(noun_type, state, x_binding, i_binding):
    return match_all_n(noun_type, state, x_binding)


@Predication(vocabulary, names=("_on_p_loc",))
def on_p_loc(state, e_introduced_binding, x_actor_binding, x_location_binding):
    def check_item_on_item(item1, item2):
        if "on" in state.rel.keys():
            if (item1, item2) in state.rel["on"]:
                return True
            else:
                report_error(["notOn", item1, item2])
        else:
            report_error(["notOn", item1, item2])

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


@Predication(vocabulary, names=["_want_v_1"], handles=[("request_type", EventOption.optional)])
def _want_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor, x_object):
        if "want" in state.rel.keys():
            if (x_actor, x_object) in state.rel["want"]:
                return True
        elif x_actor == "user":
            return True
        else:
            report_error(["notwant", "want", x_actor])
            return False

    def wanters_of_obj(x_object):
        if "want" in state.rel.keys():
            for i in state.rel["want"]:
                if i[1] == x_object:
                    yield i[0]

    def wanted_of_actor(x_actor):
        if "want" in state.rel.keys():
            for i in state.rel["want"]:
                if i[0] == x_actor:
                    yield i[1]

    success_states = list(in_style_predication_2(state, x_actor_binding, x_object_binding, criteria_bound,
                                                 wanters_of_obj, wanted_of_actor))
    for success_state in success_states:
        x_act = success_state.get_binding(x_actor_binding.variable.name).value[0]
        x_obj = success_state.get_binding(x_object_binding.variable.name).value[0]
        if x_act == "user":
            if not x_obj is None:
                yield success_state.record_operations(state.handle_world_event(["user_wants", x_obj]))


@Predication(vocabulary, names=["_check_v_1"])
def _check_v_1(state, e_introduced_binding, x_actor_binding, i_object_binding):
    if i_object_binding.value is not None:
        return

    def criteria_bound(x):
        return x == "computer"

    def unbound():
        if False:
            yield None

    for success_state in combinatorial_predication_1(state, x_actor_binding, criteria_bound, unbound):
        yield success_state.record_operations(state.handle_world_event(["user_wants", "bill1"]))


@Predication(vocabulary, names=["_give_v_1", "_get_v_1"])
def _give_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding, x_target_binding):
    if state.get_binding(x_actor_binding.variable.name).value[0] == "computer":
        if state.get_binding(x_target_binding.variable.name).value[0] == "user":
            if not state.get_binding(x_object_binding.variable.name).value[0] is None:
                yield state.record_operations(
                    state.handle_world_event(
                        ["user_wants", state.get_binding(x_object_binding.variable.name).value[0]]))


@Predication(vocabulary, names=["_show_v_1"])
def _show_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding, x_target_binding):
    if state.get_binding(x_actor_binding.variable.name).value[0] == "computer":
        if state.get_binding(x_target_binding.variable.name).value[0] == "user":
            if not state.get_binding(x_object_binding.variable.name).value[0] is None:
                if state.get_binding(x_object_binding.variable.name).value[0] == "menu1":
                    yield state.record_operations(
                        state.handle_world_event(
                            ["user_wants_to_see", state.get_binding(x_object_binding.variable.name).value[0]]))


@Predication(vocabulary, names=["_seat_v_cause"])
def _seat_v_cause(state, e_introduced_binding, x_actor_binding, x_object_binding):
    if state.get_binding(x_object_binding.variable.name).value[0] == "user":
        yield state.record_operations(state.handle_world_event(["user_wants", "table1"]))


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

    yield from combinatorial_predication_1(state, x_binding, bound_variable, unbound_variable)


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

    yield from combinatorial_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["def_implicit_q", "def_explicit_q"])
def def_implicit_q(state, x_variable_binding, h_rstr, h_body):
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(execution_context().current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf')))

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body)


@Predication(vocabulary, names=["_like_v_1"], handles=[("request_type", EventOption.optional)])
def _like_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding):
    if state.get_binding(x_actor_binding.variable.name).value[0] == "user":
        if not state.get_binding(x_object_binding.variable.name).value[0] is None:
            yield state.record_operations(
                state.handle_world_event(["user_wants", state.get_binding(x_object_binding.variable.name).value[0]]))
    else:
        yield state


@Predication(vocabulary, names=["_like_v_1", "_want_v_1"], handles=[("request_type", EventOption.optional)])
def _like_v_1_exh(state, e_introduced_binding, x_actor_binding, h_binding):
    event_to_mod = h_binding.args[0]

    yield from call(state.add_to_e(event_to_mod, "request_type", True), h_binding)


@Predication(vocabulary, names=["_would_v_modal"])
def _would_v_modal(state, e_introduced_binding, h_binding):
    yield from call(state, h_binding)


@Predication(vocabulary, names=["_please_a_1"])
def _please_a_1(state, e_introduced_binding, e_binding):
    yield state


@Predication(vocabulary, names=["_please_v_1"])
def _please_v_1(state, e_introduced_binding, i_binding1, i_binding2):
    yield state


@Predication(vocabulary, names=["_could_v_modal", "_can_v_modal"])
def _could_v_modal(state, e_introduced_binding, h_binding):
    yield from call(state, h_binding)


@Predication(vocabulary, names=["polite"])
def polite(state, c_arg, i_binding, e_binding):
    yield state


@Predication(vocabulary, names=["_thanks_a_1"])
def _thanks_a_1(state, i_binding, h_binding):
    yield from call(state, h_binding)

#
# @Predication(vocabulary, names=["_and_c"])
# def _and_c(state, x_binding_introduced, x_binding_first, x_binding_second):
#     assert(state.get_binding(x_binding_first.variable.name).value[0] is not None)
#     assert (state.get_binding(x_binding_second.variable.name).value[0] is not None)
#     yield state.set_x(x_binding_introduced.variable.name,
#                       state.get_binding(x_binding_first.variable.name).value + state.get_binding(x_binding_second.variable.name).value,
#                       combinatoric=True)


class RequestVerbTransitive:
    def __init__(self, predicate_name_list, lemma, logic):
        self.predicate_name_list = predicate_name_list
        self.lemma = lemma
        self.logic = logic

    def predicate_func(self, state, e_binding, x_actor_binding, x_object_binding):
        j = state.get_binding("tree").value[0]["Index"]
        is_request = False
        if not e_binding is None:
            if e_binding.value is not None:
                if "request_type" in e_binding.value:
                    is_request = e_binding.value["request_type"]

        is_modal = find_predication_from_introduced(state.get_binding("tree").value[0]["Tree"], j).name in [
            "_could_v_modal", "_can_v_modal", "_would_v_modal"]
        is_future = (state.get_binding("tree").value[0]["Variables"][j]["TENSE"] == "fut")

        if self.lemma == "have":
            if state.get_binding(x_actor_binding.variable.name).value[0] == "computer":
                if state.get_binding(x_object_binding.variable.name).value is None:
                    yield state.record_operations(state.handle_world_event(["user_wants", "menu1"]))
                    return

        def bound(x_actor, x_object):
            if (is_modal or is_future or is_request) and (x_actor == ("user",) or x_actor == "user"):
                return True
            else:
                if self.lemma in state.rel.keys():
                    if (x_actor, x_object) in state.rel[self.lemma]:
                        return True
                    else:
                        report_error(["verbDoesntApply", x_actor, self.lemma, x_object])
                        return False

                else:
                    report_error(["verbDoesntApply", x_actor, self.lemma, x_object])
                    return False

        def actor_from_object(x_object):
            if self.lemma in state.rel.keys():
                something_sees = False
                for i in state.rel[self.lemma]:
                    if i[1] == x_object:
                        yield i[0]
                        something_sees = True
                if not something_sees:
                    report_error(["Nothing_VTRANS_X", self.lemma, x_object])
            else:
                report_error(["No_VTRANS", self.lemma, x_object])

        def object_from_actor(x_actor):
            if self.lemma in state.rel.keys():
                sees_something = False
                for i in state.rel[self.lemma]:
                    if i[0] == x_actor or i[0] == x_actor[0]:
                        yield i[1]
                        sees_something = True
                if not sees_something:
                    report_error(["X_VTRANS_Nothing", self.lemma, x_actor])
            else:
                report_error(["No_VTRANS", self.lemma, x_actor])

        state_exists = False
        for success_state in in_style_predication_2(state, x_actor_binding, x_object_binding, bound, actor_from_object,
                                                    object_from_actor):
            state_exists = True
            x_act = success_state.get_binding(x_actor_binding.variable.name).value[0]
            x_obj = success_state.get_binding(x_object_binding.variable.name).value[0]

            if (is_modal or is_future or is_request) and x_act == "user":
                if x_obj is not None:
                    yield success_state.record_operations(success_state.handle_world_event([self.logic, x_obj, x_act]))
            else:
                yield success_state
        if not state_exists:
            report_error(["RequestVerbTransitiveFailure"])

class RequestVerbIntransitive:
    def __init__(self, predicate_name_list, lemma, logic):
        self.predicate_name_list = predicate_name_list
        self.lemma = lemma
        self.logic = logic

    def predicate_func(self, state, e_binding, x_actor_binding):
        j = state.get_binding("tree").value[0]["Index"]
        is_request = False
        if not e_binding is None:
            if e_binding.value is not None:
                if "request_type" in e_binding.value:
                    is_request = e_binding.value["request_type"]
        is_modal = find_predication_from_introduced(state.get_binding("tree").value[0]["Tree"], j).name in [
            "_could_v_modal", "_can_v_modal", "_would_v_modal"]
        is_future = (state.get_binding("tree").value[0]["Variables"][j]["TENSE"] == "fut")

        def bound(x_actor):
            if (is_modal or is_future or is_request) and x_actor == "user":
                return True
            else:
                if self.lemma in state.rel.keys():
                    for pair in state.rel[self.lemma]:
                        if pair[0] == x_actor:
                            return True

                    report_error(["verbDoesntApply", x_actor, self.lemma, x_object])
                    return False

                else:
                    report_error(["verbDoesntApply", x_actor, self.lemma, x_object])
                    return False

        def unbound():
            if self.lemma in state.rel.keys():
                for i in state.rel[self.lemma]:
                    yield i[0]

        for success_state in combinatorial_predication_1(state, x_actor_binding, bound, unbound):
            x_act = success_state.get_binding(x_actor_binding.variable.name).value[0]

            if (is_modal or is_future or is_request) and x_act == "user":
                yield success_state.record_operations(success_state.handle_world_event([self.logic, x_act]))
            else:
                yield success_state


have = RequestVerbTransitive(["_have_v_1", "_get_v_1", "_take_v_1"], "have", "user_wants")
see = RequestVerbTransitive(["_see_v_1"], "see", "user_wants_to_see")
sit_down = RequestVerbIntransitive(["_sit_v_down"], "sitting_down", "user_wants_to_sit")


@Predication(vocabulary, names=have.predicate_name_list, handles=[("request_type", EventOption.optional)], arguments=[("e",), ("x"), ("x")])
def _have_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding):
    yield from have.predicate_func(state, e_introduced_binding, x_actor_binding, x_object_binding)


@Predication(vocabulary, names=see.predicate_name_list, handles=[("request_type", EventOption.optional)])
def _see_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding):
    yield from see.predicate_func(state, e_introduced_binding, x_actor_binding, x_object_binding)


@Predication(vocabulary, names=sit_down.predicate_name_list, handles=[("request_type", EventOption.optional)])
def _sit_v_down(state, e_introduced_binding, x_actor_binding):
    yield from sit_down.predicate_func(state, e_introduced_binding, x_actor_binding)


@Predication(vocabulary, names=["poss"])
def poss(state, e_introduced_binding, x_object_binding, x_actor_binding):
    def bound(x_actor, x_object):

        if "have" in state.rel.keys():
            if (x_actor, x_object) in state.rel["have"]:
                return True
            else:
                report_error(["verbDoesntApply", x_actor, "have", x_object])
                return False

        else:
            report_error(["verbDoesntApply", x_actor, "have", x_object])
            return False

    def actor_from_object(x_object):
        if "have" in state.rel.keys():
            for i in state.rel["have"]:
                if i[1] == x_object:
                    yield i[0]

    def object_from_actor(x_actor):
        if "have" in state.rel.keys():
            for i in state.rel["have"]:
                if i[0] == x_actor:
                    yield i[1]

    yield from in_style_predication_2(state, x_actor_binding, x_object_binding, bound, actor_from_object,
                                      object_from_actor)


@Predication(vocabulary, names=["_be_v_id"])
def _be_v_id(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor, x_object):
        if not x_object[0] == "{":
            first_in_second = x_actor in all_instances_and_spec(state, x_object)
            second_in_first = x_object in all_instances_and_spec(state, x_actor)

            return first_in_second or second_in_first
        else:
            x_object = json.loads(x_object)
            if x_object["structure"] == "price_type":
                if type(x_object["relevant_var_value"]) is int:
                    if not (x_actor, x_object["relevant_var_value"]) in state.sys["prices"]:
                        report_error("WrongPrice")
                        return False
            return True

    def unbound(x_object):
        for i in all_instances(state, x_object):
            yield i
        yield x_object

    for success_state in in_style_predication_2(state, x_actor_binding, x_object_binding, criteria_bound, unbound,
                                                unbound):
        x_obj = success_state.get_binding(x_object_binding.variable.name).value[0]
        x_act = success_state.get_binding(x_actor_binding.variable.name).value[0]
        if not x_obj[0] == "{":
            yield success_state
        else:
            x_obj = json.loads(x_obj)
            if x_obj["structure"] == "price_type":
                if x_obj["relevant_var_value"] == "to_determine":
                    if x_act in success_state.sys["prices"].keys():
                        yield success_state.set_x(x_obj["relevant_var_name"], (
                            str(x_act) + ": " + str(success_state.sys["prices"][x_act]) + " dollars",))
                    else:
                        yield success_state.record_operations([RespondOperation("Haha, it's not for sale.")])


@Predication(vocabulary, names=["_cost_v_1"])
def _cost_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor, x_object):
        if not x_object[0] == "{":
            report_error("Have not dealt with declarative cost")
        else:
            x_object = json.loads(x_object)
            if x_object["structure"] == "price_type":
                if type(x_object["relevant_var_value"]) is int:
                    if not (x_actor, x_object["relevant_var_value"]) in state.sys["prices"]:
                        report_error("WrongPrice")
                        return False
            return True

    def get_actor(x_object):
        if False:
            yield None

    def get_object(x_actor):
        if x_actor in state.sys["prices"].keys():
            yield str(x_actor) + ": " + str(state.sys["prices"][x_actor]) + " dollars"

    for success_state in in_style_predication_2(state, x_actor_binding, x_object_binding, criteria_bound, get_actor,
                                                get_object):
        x_obj = success_state.get_binding(x_object_binding.variable.name).value[0]
        x_act = success_state.get_binding(x_actor_binding.variable.name).value[0]
        if not x_obj[0] == "{":
            yield success_state
        else:
            x_obj = json.loads(x_obj)
            if x_obj["structure"] == "price_type":
                if x_obj["relevant_var_value"] == "to_determine":
                    if x_act in success_state.sys["prices"].keys():
                        yield success_state.set_x(x_obj["relevant_var_name"], (
                            str(x_act) + ": " + str(success_state.sys["prices"][x_act]) + " dollars",))
                    else:
                        yield success_state.record_operations([RespondOperation("Haha, it's not for sale.")])


@Predication(vocabulary, names=["_be_v_there"])
def _be_v_there(state, e_introduced_binding, x_object_binding):
    def bound_variable(value):
        yield value in state.get_entities()

    def unbound_variable():
        for i in state.get_entities():
            yield i

    yield from combinatorial_predication_1(state, x_object_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["compound"])
def compound(state, e_introduced_binding, x_first_binding, x_second_binding):
    assert (x_first_binding is not None)
    assert (x_second_binding is not None)
    yield state.set_x(x_first_binding.variable.name, (state.get_binding(x_first_binding.variable.name).value[0] + ", " +
                                                      state.get_binding(x_second_binding.variable.name).value[0],))


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
    if error_constant == "notOn":
        arg1 = error_arguments[1]
        arg2 = error_arguments[2]
        return f"No. {arg1} is not on {arg2}"
    if error_constant == "verbDoesntApply":
        return f"No. {error_arguments[1]} does not {error_arguments[2]} {error_arguments[3]}"
    else:
        # No custom message, just return the raw error for debugging
        return str(error_term)


def reset():
    # return State([])
    # initial_state = WorldState({}, ["pizza", "computer", "salad", "soup", "steak", "ham", "meat","special"])
    initial_state = WorldState({},
                               {"prices": {"salad1": 3, "steak1": 10, "soup1": 4}, "responseState": "initial"
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
    initial_state = initial_state.add_rel("table1", "maxCap", 4)

    initial_state = initial_state.add_rel("soup1", "instanceOf", "soup")
    initial_state = initial_state.add_rel("menu1", "instanceOf", "menu")
    initial_state = initial_state.add_rel("pizza1", "instanceOf", "pizza")
    initial_state = initial_state.add_rel("steak1", "instanceOf", "steak")

    initial_state = initial_state.add_rel("soup", "specializes", "special")
    initial_state = initial_state.add_rel("salad", "specializes", "special")
    initial_state = initial_state.add_rel("computer", "have", "salad1")
    initial_state = initial_state.add_rel("computer", "have", "soup1")
    initial_state = initial_state.add_rel("computer", "have", "steak1")
    initial_state = initial_state.add_rel("computer", "have", "table1")
    initial_state = initial_state.add_rel("computer", "have", "menu1")
    initial_state = initial_state.add_rel("user", "have", "bill1")

    initial_state = initial_state.add_rel("steak1", "on", "menu1")

    initial_state = initial_state.add_rel("bill", "specializes", "thing")
    initial_state = initial_state.add_rel("check", "specializes", "thing")
    initial_state = initial_state.add_rel("bill1", "instanceOf", "bill")
    initial_state = initial_state.add_rel("bill1", "instanceOf", "check")
    initial_state = initial_state.add_rel(0, "valueOf", "bill1")

    initial_state = initial_state.add_rel("room", "contains", "user")

    return initial_state


def error_priority(error_string):
    global error_priority_dict
    if error_string is None:
        return 0

    else:
        error_constant = error_string[1][0]
        priority = error_priority_dict.get(error_constant, error_priority_dict["defaultPriority"])
        if error_constant == "unknownWords":
            priority -= len(error_string[1][1])

        return priority


error_priority_dict = {
    # Unknown words error should only be shown if
    # there are no other errors, AND the number
    # of unknown words is subtracted from it so
    # lower constants should be defined below this:
    # "unknownWordsMin": 800,
    "unknownWords": 900,
    # Slightly better than not knowing the word at all
    "formNotUnderstood": 901,
    "defaultPriority": 1000,

    # This is just used when sorting to indicate no error, i.e. success.
    # Nothing should be higher
    "success": 10000000
}


def hello_world():
    user_interface = UserInterface(reset, vocabulary, message_function=generate_custom_message,
                                   error_priority_function=error_priority)

    while True:
        user_interface.interact_once()
        print()


if __name__ == '__main__':
    print("Hello there, what can I do for you?")
    ShowLogging("Pipeline")
    hello_world()