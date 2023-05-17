import copy

from perplexity.execution import report_error
from perplexity.generation import english_for_delphin_variable
from perplexity.predications import combinatorial_style_predication_1, in_style_predication_2, lift_style_predication_2
from perplexity.response import RespondOperation
from perplexity.state import State
from perplexity.system_vocabulary import system_vocabulary
from perplexity.user_interface import UserInterface
from perplexity.utilities import ShowLogging
from perplexity.vocabulary import Vocabulary, Predication
import perplexity.messages

vocabulary = system_vocabulary()


class WorldState(State):
    def __init__(self, relations, entities):
        super().__init__([])
        self.rel = relations
        self.ent = entities

    def all_individuals(self):
        for i in self.ent:
            return i

    def add_rel(self, relname, first, second):
        newrel = copy.deepcopy(self.rel)
        if not relname in newrel:
            newrel[relname] = [(first, second)]
        else:
            newrel[relname] += [(first, second)]
        return WorldState(newrel, self.ent)

    def _mutate_add_rel(self, relname, first, second):
        newrel = copy.deepcopy(self.rel)
        if not relname in newrel:
            newrel[relname] = [(first, second)]
        else:
            newrel[relname] += [(first, second)]
        self.rel = newrel


class AddRelOp(object):
    def __init__(self, rel):
        self.toAdd = rel

    def apply_to(self, state):
        state._mutate_add_rel(self.toAdd[0], self.toAdd[1], self.toAdd[2])


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


@Predication(vocabulary, names=["_pizza_n_1"])
def _pizza_n_1(state, x_binding):
    #print(state.rel)

    def bound_variable(value):
        if value in ["pizza"]:
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "pizza"

    yield from combinatorial_style_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["_steak_n_1"])
def _steak_n_1(state, x_binding):
    def bound_variable(value):
        if value in ["steak"]:
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "steak"

    yield from combinatorial_style_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["_table_n_1"])
def _table_n_1(state, x_binding):
    def bound_variable(value):
        if value in ["table"]:
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "table"

    yield from combinatorial_style_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["_ham_n_1"])
def _ham_n_1(state, x_binding):
    def bound_variable(value):
        if value in ["ham"]:
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "ham"

    yield from combinatorial_style_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["_soup_n_1"])
def _soup_n_1(state, x_binding):
    def bound_variable(value):
        if value in ["soup"]:
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "soup"

    yield from combinatorial_style_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["_salad_n_1"])
def _salad_n_1(state, x_binding):
    def bound_variable(value):
        if value in ["salad"]:
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "salad"

    yield from combinatorial_style_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["_special_n_1"])
def _special_n_1(state, x_binding):
    def bound_variable(value):
        if value in ["salad", "soup"]:
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "special"

    yield from combinatorial_style_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["_meat_n_1"])
def _meat_n_1(state, x_binding):
    def bound_variable(value):
        if value in ["meat", "steak", "ham"]:
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "ham"
        yield "steak"
        yield "meat"

    yield from combinatorial_style_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["_food_n_1"])
def _food_n_1(state, x_binding):
    def bound_variable(value):
        if value in ["meat", "steak", "ham", "food", "pizza"]:
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "ham"
        yield "steak"
        yield "meat"
        yield "pizza"
        yield "food"

    yield from combinatorial_style_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["_menu_n_1"])
def _menu_n_1(state, x_binding):
    def bound_variable(value):
        if value in ["menu"]:
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "menu"

    yield from combinatorial_style_predication_1(state, x_binding, bound_variable, unbound_variable)


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


@Predication(vocabulary, names=["_large_a_1"])
def large_a_1(state, e_introduced_binding, x_target_binding):
    def criteria_bound(value):
        if value == "file2.txt":
            return True

        else:
            report_error(["adjectiveDoesntApply", "large", x_target_binding.variable.name])
            return False

    def unbound_values():
        # Find all large things
        yield "file2.txt"

    yield from combinatorial_style_predication_1(state, x_target_binding, criteria_bound, unbound_values)


@Predication(vocabulary, names=["_want_v_1"])
def _want_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor_binding, x_object_binding):
        if "want" in state.rel.keys():
            if (x_actor_binding, x_object_binding) in state.rel["want"]:
                return True
        else:
            report_error(["verbDoesntApply", "large", x_actor_binding.variable.name])
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
            if x_obj == "table":
                operation = AddRelOp(("at", "user", "table"))
                yield success_state.record_operations([operation,RespondOperation("Right this way!\nThe robot shows you to a wooden table")])
            else:
                if "at" in success_state.rel.keys():
                    if ("user","table") in success_state.rel["at"]:
                        yield success_state.record_operations([RespondOperation("Coming right up!")])
                    else:
                        yield success_state.record_operations([RespondOperation("Sorry, you need to be seated to order.")])
                else:
                    yield success_state.record_operations([RespondOperation("Sorry, you need to be seated to order.")])

        else:
            yield success_state


@Predication(vocabulary, names=["_have_v_1"])
def _have_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor_binding, x_object_binding):
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

    yield from in_style_predication_2(state, x_actor_binding, x_object_binding, criteria_bound, havers_of_obj,
                                      had_of_actor)


@Predication(vocabulary, names=["_be_v_id"])
def _be_v_id(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor_binding, x_object_binding):
        if "be" in state.rel.keys():
            if (x_actor_binding, x_object_binding) in state.rel["be"]:
                return True

        else:
            report_error(["verbDoesntApply", "large", x_actor_binding.variable.name])
            return False

    def havers_of_obj(x_object_binding):
        if "be" in state.rel.keys():
            for i in state.rel["be"]:
                if i[1] == x_object_binding:
                    yield i[0]

    def had_of_actor(x_actor_binding):
        if "be" in state.rel.keys():
            for i in state.rel["be"]:
                if i[0] == x_actor_binding:
                    yield i[1]

    yield from in_style_predication_2(state, x_actor_binding, x_object_binding, criteria_bound, havers_of_obj,
                                      had_of_actor)


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
    initial_state = WorldState({}, ["pizza", "computer"])
    initial_state = initial_state.add_rel("want", "computer", "pizza")
    initial_state = initial_state.add_rel("want", "computer", "ham")
    initial_state = initial_state.add_rel("want", "user", "table")
    initial_state = initial_state.add_rel("want", "user", "steak")
    initial_state = initial_state.add_rel("on", "steak", "menu")
    initial_state = initial_state.add_rel("on", "pizza", "menu")
    initial_state = initial_state.add_rel("on", "ham", "menu")
    initial_state = initial_state.add_rel("have", "menu", "ham")
    initial_state = initial_state.add_rel("have", "menu", "steak")
    initial_state = initial_state.add_rel("have", "menu", "pizza")
    initial_state = initial_state.add_rel("have", "computer", "ham")
    initial_state = initial_state.add_rel("have", "computer", "steak")
    initial_state = initial_state.add_rel("have", "computer", "pizza")
    initial_state = initial_state.add_rel("be", "soup", "special")
    initial_state = initial_state.add_rel("be", "salad", "special")
    return initial_state


def hello_world():
    user_interface = UserInterface(reset, vocabulary)

    while True:
        user_interface.interact_once()
        print()


if __name__ == '__main__':
    ShowLogging("Pipeline")
    hello_world()
