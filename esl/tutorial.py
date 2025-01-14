import perplexity.messages
from esl.esl_planner import do_task
from perplexity.execution import report_error, call, execution_context
from perplexity.generation import english_for_delphin_variable
from perplexity.plurals import VariableCriteria, GlobalCriteria
from perplexity.predications import combinatorial_predication_1, in_style_predication_2, \
    lift_style_predication_2, concept_meets_constraint
from perplexity.system_vocabulary import system_vocabulary, quantifier_raw
from perplexity.transformer import TransformerMatch, TransformerProduction
from perplexity.tree import find_predication_from_introduced, get_wh_question_variable
from perplexity.user_interface import UserInterface
from perplexity.utilities import ShowLogging, sentence_force
from perplexity.vocabulary import Predication, EventOption, Transform, override_predications
from esl.worldstate import *

vocabulary = system_vocabulary()
override_predications(vocabulary, "user", ["card__cex__"])


# ******** Helpers ************
def convert_noun_structure(binding_value):
    new_list = []
    for item in binding_value:
        if hasattr(item, "is_concept"):
            new_list.append(item.modifiers())
        else:
            new_list.append(item)
    return tuple(new_list)


def variable_group_values_to_list(variable_group):
    return [binding.value for binding in variable_group.solution_values]


def check_concept_solution_group_constraints(state_list, x_what_variable_group, check_concepts):
    # These are concepts. Only need to check the first because:
    # If one item in the group is a concept, they all are
    if is_concept(x_what_variable_group.solution_values[0].value[0]):
        x_what_variable = x_what_variable_group.solution_values[0].variable.name

        # First we need to check to make sure that the specific concepts in the solution group like "steak", "menu",
        # etc meet the requirements I.e. if there are two preparations of steak on the menu and you say
        # "I'll have the steak" you should get an error
        x_what_values = [x.value for x in x_what_variable_group.solution_values]
        x_what_individuals_set = set()
        for value in x_what_values:
            x_what_individuals_set.update(value)
        concept_count, concept_in_scope_count, instance_count, instance_in_scope_count = count_of_instances_and_concepts(
            state_list[0], list(x_what_individuals_set))
        return concept_meets_constraint(state_list[0].get_binding("tree").value[0],
                                        x_what_variable_group.variable_constraints,
                                        concept_count,
                                        concept_in_scope_count,
                                        instance_count,
                                        instance_in_scope_count,
                                        check_concepts,
                                        variable=x_what_variable)


def is_present_tense(tree_info):
    return tree_info["Variables"][tree_info["Index"]]["TENSE"] in ["pres", "untensed"]


def is_future_tense(tree_info):
    return tree_info["Variables"][tree_info["Index"]]["TENSE"] in ["fut"]


def is_question(tree_info):
    return sentence_force(tree_info["Variables"]) in ["ques", "prop-or-ques"]


def is_wh_question(tree_info):
    if is_question(tree_info):
        return get_wh_question_variable(tree_info)

    return False


def is_request_from_tree(tree_info):
    introduced_predication = find_predication_from_introduced(tree_info["Tree"], tree_info["Index"])
    return sentence_force(tree_info["Variables"]) in ["ques", "prop-or-ques"] or \
        introduced_predication.name.endswith("_request") or \
        tree_info["Variables"][tree_info["Index"]]["TENSE"] == "fut"


def valid_player_request(state, x_objects, valid_types=None):
    # Things players can request
    if valid_types is None:
        valid_types = ["food", "table", "menu", "bill"]

    store_objects = [object_to_store(x) for x in x_objects]
    for store in store_objects:
        if not sort_of(state, store, valid_types):
            return False

    return True


# ******** Transforms ************
# Convert "would like <noun>" to "want <noun>"
@Transform(vocabulary)
def would_like_to_want_transformer():
    production = TransformerProduction(name="_want_v_1", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    like_match = TransformerMatch(name_pattern="_like_v_1", args_pattern=["e", "x", "x"],
                                  args_capture=[None, "x1", "x2"])
    return TransformerMatch(name_pattern="_would_v_modal", args_pattern=["e", like_match], args_capture=["e1", None],
                            removed=["_would_v_modal", "_like_v_1"], production=production)


# Convert "Can/could I x?", "I can/could x?" to "I x_request x?"
# "What can I x?"
@Transform(vocabulary)
def can_to_able_intransitive_transformer():
    production = TransformerProduction(name="$|name|_able", args={"ARG0": "$e1", "ARG1": "$x1"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x"], args_capture=[None, "x1"])
    return TransformerMatch(name_pattern="_can_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_can_v_modal"], production=production)


# Convert "can I have a table/steak/etc?" or "what can I have?"
# To: able_to
@Transform(vocabulary)
def can_to_able_transitive_transformer():
    production = TransformerProduction(name="$|name|_able", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"],
                              args_capture=[None, "x1", "x2"])
    return TransformerMatch(name_pattern="_can_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_can_v_modal"], production=production)

#Convert "Can you seat me" to "you seat_reqeuested me"

@Transform(vocabulary)
def can_to_requested_transitive_transformer():
    production = TransformerProduction(name="$|name|_requested", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"],
                              args_capture=[None, "x1", "x2"])
    return TransformerMatch(name_pattern="_can_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_can_v_modal"], production=production)


# Convert "I want to x y" to "I x_request y"
@Transform(vocabulary)
def want_removal_transitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"],
                              args_capture=[None, "x1", "x2"])
    return TransformerMatch(name_pattern="_want_v_1", args_pattern=["e", "x", target], args_capture=["e1", None, None],
                            removed=["_want_v_1"], production=production)


# Convert "I want to x" to "I x_request"
@Transform(vocabulary)
def want_removal_intransitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x"], args_capture=[None, "x1"])
    return TransformerMatch(name_pattern="_want_v_1", args_pattern=["e", "x", target], args_capture=["e1", None, None],
                            removed=["_want_v_1"], production=production)


# Convert "I would like to x y" to "I x_request y"
@Transform(vocabulary)
def would_like_removal_transitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"],
                              args_capture=[None, "x1", "x2"])
    like_match = TransformerMatch(name_pattern="_like_v_1", args_pattern=["e", "x", target],
                                  args_capture=[None, None, None])
    would_match = TransformerMatch(name_pattern="_would_v_modal", args_pattern=["e", like_match],
                                   args_capture=["e1", None], removed=["_would_v_modal", "_like_v_1"],
                                   production=production)
    return would_match


# Convert "I would like to x" to "I x_request x"
@Transform(vocabulary)
def would_like_removal_intransitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x"], args_capture=[None, "x1"])
    like_match = TransformerMatch(name_pattern="_like_v_1", args_pattern=["e", "x", target],
                                  args_capture=[None, None, None])
    would_match = TransformerMatch(name_pattern="_would_v_modal", args_pattern=["e", like_match],
                                   args_capture=["e1", None], removed=["_would_v_modal", "_like_v_1"],
                                   production=production)
    return would_match


# Convert "I would x y" to "I x_request y" (i.e. "I would have a menu")
@Transform(vocabulary)
def want_removal_transitive_transformer():
    production = TransformerProduction(name="$|name|_request", args={"ARG0": "$e1", "ARG1": "$x1", "ARG2": "$x2"})
    target = TransformerMatch(name_pattern="*", name_capture="name", args_pattern=["e", "x", "x"],
                              args_capture=[None, "x1", "x2"])
    return TransformerMatch(name_pattern="_would_v_modal", args_pattern=["e", target], args_capture=["e1", None],
                            removed=["_would_v_modal"], production=production)


# ***************************


@Predication(vocabulary, names=["pron"])
def pron(state, x_who_binding):
    person = int(state.get_binding("tree").value[0]["Variables"][x_who_binding.variable.name]["PERS"])
    plurality = "unknown"
    if "NUM" in state.get_binding("tree").value[0]["Variables"][x_who_binding.variable.name].keys():
        plurality = (state.get_binding("tree").value[0]["Variables"][x_who_binding.variable.name]["NUM"])

    def bound_variable(value):
        if person == 2 and value == "computer":
            return True
        if person == 1 and is_user_type(value):
            return True
        else:
            report_error(["dontKnowActor", x_who_binding.variable.name])

    def unbound_variable():
        if person == 2:
            yield "computer"
        if person == 1:
            if plurality == "pl":
                yield "user"
                yield "son1"

            else:
                yield "user"

    yield from combinatorial_predication_1(state, x_who_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["generic_entity"])
def generic_entity(state, x_binding):
    def bound(val):
        return val == Concept("generic_entity")

    def unbound():
        yield Concept("generic_entity")

    yield from combinatorial_predication_1(state, x_binding, bound, unbound)


@Predication(vocabulary, names=["_okay_a_1"])
def _okay_a_1(state, i_binding, h_binding):
    yield from call(state, h_binding)


@Predication(vocabulary, names=["much-many_a"], handles=[("Measure", EventOption.optional)])
def much_many_a(state, e_binding, x_binding):
    if "Measure" in e_binding.value.keys():
        measure_into_variable = e_binding.value["Measure"]["Value"]
        # if we are measuring x_binding should have a Concept() that is the type of measurement
        x_binding_value = x_binding.value
        if len(x_binding_value) == 1 and is_concept(x_binding_value[0]):
            # Set the actual value of the measurement to a string so that
            # a predication that receives it knows we are looking to fill in an unbound value
            measurement = Measurement(x_binding_value[0], measure_into_variable)

            # Replace x5 with measurement
            yield state.set_x(x_binding.variable.name, (measurement,))


@Predication(vocabulary, names=["measure"])
def measure(state, e_binding, e_binding2, x_binding):
    yield state.add_to_e(e_binding2.variable.name, "Measure",
                         {"Value": x_binding.variable.name,
                          "Originator": execution_context().current_predication_index()})


@Predication(vocabulary, names=["abstr_deg"])
def abstr_deg(state, x_binding):
    yield state.set_x(x_binding.variable.name, (Concept("abstract_degree"),))


@Predication(vocabulary, names=["card"])
def card(state, c_number, e_binding, x_binding):
    x_binding_value = state.get_binding(x_binding.variable.name).value
    if len(x_binding_value) == 1 and is_concept(x_binding_value[0]) and c_number.isnumeric():
        yield state.set_x(x_binding.variable.name, (x_binding_value[0].update_modifiers({"card": int(c_number)}),))


@Predication(vocabulary, names=["card"])
def card_system(state, c_number, e_binding, x_binding):
    if state.get_binding(x_binding.variable.name).value[0] != "generic_entity":
        yield from perplexity.system_vocabulary.card(state, c_number, e_binding, x_binding)


@Predication(vocabulary, names=["_for_p"])
def _for_p(state, e_binding, x_what_binding, x_for_binding):
    def both_bound_function(x_what, x_for):
        return True

    def x_what_unbound(x_for):
        yield None

    def x_for_unbound(x_what):
        yield None

    for solution in lift_style_predication_2(state, x_what_binding, x_for_binding,
                                             both_bound_function,
                                             x_what_unbound,
                                             x_for_unbound):
        x_what_value = solution.get_binding(x_what_binding.variable.name).value
        x_for_value = solution.get_binding(x_for_binding.variable.name).value
        if len(x_what_value) == 1 and is_concept(x_what_value[0]):
            modified = x_what_value[0].update_modifiers({"for": x_for_value})
            yield solution.set_x(x_what_binding.variable.name, (modified,))


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
    yield state.record_operations(state.handle_world_event(["unknown", x_binding.value[0]]))


@Predication(vocabulary, names=["unknown"])
def unknown_eu(state, e_binding, u_binding):
    yield state


@Predication(vocabulary, names=["_yes_a_1", "_yup_a_1", "_sure_a_1", "_yeah_a_1"])
def _yes_a_1(state, i_binding, h_binding):
    yield state.record_operations(state.handle_world_event(["yes"]))


@Predication(vocabulary, names=["_no_a_1", "_nope_a_1"])
def _no_a_1(state, i_binding, h_binding):
    yield state.record_operations(state.handle_world_event(["no"]))


@Predication(vocabulary, names=["person"])
def person(state, x_person_binding):
    yield from match_all_n("person", state, x_person_binding)


def handles_noun(state, noun_lemma):
    handles = ["thing"] + list(specializations(state, "thing"))
    return noun_lemma in handles


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

    # Yield the abstract type first, not as a combinatoric variable
    yield state.set_x(x_binding.variable.name, (Concept(noun_type),))

    yield from combinatorial_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["match_all_n"], matches_lemma_function=handles_noun)
def match_all_n_i(noun_type, state, x_binding, i_binding):
    yield from match_all_n(noun_type, state, x_binding)


@Predication(vocabulary, names=["_some_q"])
def the_q(state, x_variable_binding, h_rstr, h_body):
    # Set the constraint to be 1, inf but this is just temporary. When the constraints are optimized,
    # whatever the determiner constraint gets set to will replace these
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(execution_context().current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf'),
                                                                global_criteria=GlobalCriteria.all_rstr_meet_criteria))

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body)


@Predication(vocabulary, names=["_vegetarian_a_1"])
def _vegetarian_a_1(state, e_introduced_binding, x_target_binding):
    def criteria_bound(value):
        veg = all_instances(state, "veggie")
        if value in veg:
            return True
        else:
            report_error(["Not Veg"])
            return False

    def unbound_values():
        # Find all large things
        for i in all_instances(state, "veggie"):
            yield i

    yield from combinatorial_predication_1(state, x_target_binding,
                                           criteria_bound,
                                           unbound_values)


class PastParticiple:
    def __init__(self, predicate_name_list, lemma):
        self.predicate_name_list = predicate_name_list
        self.lemma = lemma

    def predicate_function(self, state, e_introduced_binding, i_binding, x_target_binding):
        def bound(value):
            if (value, self.lemma) in state.all_rel("isAdj"):
                return True
            else:
                report_error(["Not" + self.lemma])
                return False

        def unbound():
            for i in state.all_rel("isAdj"):
                if i[1] == self.lemma:
                    yield i[0]

        yield from combinatorial_predication_1(state, x_target_binding,
                                               bound,
                                               unbound)


grilled = PastParticiple(["_grill_v_1"], "grilled")
roasted = PastParticiple(["_roast_v_cause"], "roasted")


@Predication(vocabulary, names=grilled.predicate_name_list)
def _grill_v_1(state, e_introduced_binding, i_binding, x_target_binding):
    yield from grilled.predicate_function(state, e_introduced_binding, i_binding, x_target_binding)


@Predication(vocabulary, names=roasted.predicate_name_list)
def _grill_v_1(state, e_introduced_binding, i_binding, x_target_binding):
    yield from roasted.predicate_function(state, e_introduced_binding, i_binding, x_target_binding)


@Predication(vocabulary, names=("_on_p_loc",))
def on_p_loc(state, e_introduced_binding, x_actor_binding, x_location_binding):
    def check_item_on_item(item1, item2):
        if (item1, item2) in state.all_rel("on"):
            return True
        else:
            report_error(["notOn", item1, item2])

    def all_item1_on_item2(item2):
        for i in state.all_rel("on"):
            if i[1] == item2:
                yield i[0]

    def all_item2_containing_item1(item1):
        for i in state.all_rel("on"):
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
    def criteria_bound(x_actor, x_object):
        if is_user_type(x_actor):
            return True
        elif "want" in state.rel.keys():
            if (x_actor, x_object) in state.all_rel("want"):
                return True
        else:
            report_error(["notwant", "want", x_actor])
            return False

    def wanters_of_obj(x_object):
        if "want" in state.rel.keys():
            for i in state.all_rel("want"):
                if i[1] == x_object:
                    yield i[0]

    def wanted_of_actor(x_actor):
        if "want" in state.rel.keys():
            for i in state.all_rel("want"):
                if i[0] == x_actor:
                    yield i[1]

    yield from in_style_predication_2(state, x_actor_binding, x_object_binding, criteria_bound,
                                      wanters_of_obj, wanted_of_actor)


@Predication(vocabulary, names=["solution_group__want_v_1"])
def want_group(state_list, has_more, e_introduced_binding_list, x_actor_variable_group, x_what_variable_group):
    current_state = copy.deepcopy(state_list[0])  #TODO: ask why this is-- why can we ignore all the other states

    # This may be getting called with concepts or instances, before we call the planner
    # we need to decide if we have the requisite amount of them
    if is_concept(x_actor_variable_group.solution_values[0]):
        # We don't want to deal with conceptual actors, fail this solution group
        # and wait for the one with real actors
        yield []

    # We do have lots of places where we deal with conceptual "wants", such as: "I want the menu", "I'll have a steak"
    # In fact, we *never* deal with wanting a particular instance because that would mean "I want that particular steak right there"
    # and we don't support that
    # These are concepts. Only need to check the first because:
    # If one item in the group is a concept, they all are
    if is_concept(x_what_variable_group.solution_values[0].value[0]):
        # We first check to make sure the constraints are valid for this concept.
        # Because in "I want x", 'x' is always a concept, but the constraint is on the instances
        # (as in "I want a steak" meaning "I want 1 instance of the concept of steak", we tell
        # check_concept_solution_group_constraints to check instances via check_concepts=False
        if check_concept_solution_group_constraints(state_list, x_what_variable_group, check_concepts=False):
            # If there is more than one concept here, they said something like "we want steaks and fries" but doing the magic
            # To figure that out how much of each is too much
            x_what_values = [x.value for x in x_what_variable_group.solution_values]
            x_what_individuals_set = set()
            for value in x_what_values:
                x_what_individuals_set.update(value)
            if len(x_what_individuals_set) > 1:
                yield [current_state.record_operations([RespondOperation("One thing at a time, please!")])]

            # At this point we are only dealing with one concept
            # Give them the max of what they specified
            first_x_what_binding_value = copy.deepcopy(x_what_variable_group.solution_values[0].value[0])
            first_x_what_binding_value = first_x_what_binding_value.update_modifiers(
                {"card": x_what_variable_group.variable_constraints.max_size})

            actor_values = [x.value for x in x_actor_variable_group.solution_values]
            current_state = do_task(current_state.world_state_frame(),
                                    [('satisfy_want', actor_values, [(first_x_what_binding_value,)])])
            if current_state is None:
                yield []
            else:
                yield [current_state]

        else:
            yield []


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


@Predication(vocabulary, names=["_give_v_1"])
def _give_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding, x_target_binding):
    if state.get_binding(x_actor_binding.variable.name).value[0] == "computer":
        if is_user_type(state.get_binding(x_target_binding.variable.name).value[0]):
            if not state.get_binding(x_object_binding.variable.name).value[0] is None:
                yield state.record_operations(
                    state.handle_world_event(
                        ["user_wants", state.get_binding(x_object_binding.variable.name).value[0]]))


@Predication(vocabulary, names=["_show_v_1"])
def _show_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding, x_target_binding):
    if state.get_binding(x_actor_binding.variable.name).value[0] == "computer":
        if is_user_type(state.get_binding(x_target_binding.variable.name).value[0]):
            if not state.get_binding(x_object_binding.variable.name).value[0] is None:
                if state.get_binding(x_object_binding.variable.name).value[0] == "menu1":
                    yield state.record_operations(
                        state.handle_world_event(
                            ["user_wants_to_see", state.get_binding(x_object_binding.variable.name).value[0]]))


@Predication(vocabulary, names=["_seat_v_cause","_seat_v_cause_requested"])
def _seat_v_cause(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor, x_object):
        return is_user_type(x_object)

    def wanters_of_obj(x_object):
        return #not currently going to support asking who is seating someone

    def wanted_of_actor(x_actor):
        return

    yield from in_style_predication_2(state, x_actor_binding, x_object_binding, criteria_bound,
                                      wanters_of_obj, wanted_of_actor)
@Predication(vocabulary, names=["solution_group__seat_v_cause","solution_group__seat_v_cause_requested"])
def _seat_v_cause_group(state_list, has_more, e_introduced_binding, x_actor_variable_group, x_what_variable_group):
    current_state = copy.deepcopy(state_list[0])
    actor_values = [x.value for x in x_actor_variable_group.solution_values]
    current_state = do_task(current_state.world_state_frame(),
                            [('satisfy_want', [('user',)], [(Concept("table"),)])])
    if current_state is None:
        yield []
    else:
        yield [current_state]

@Predication(vocabulary, names=["loc_nonsp"])
def loc_nonsp(state, e_introduced_binding, x_actor_binding, x_loc_binding):
    def item1_in_item2(item1, item2):
        if item2 == "today":
            return True

        if (item1, item2) in state.all_rel("contains"):
            return True
        return False

    def items_in_item1(item1):
        for i in state.all_rel("contains"):
            if i[0] == item1:
                yield i[1]

    def item1_in_items(item1):
        for i in state.all_rel("contains"):
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


@Predication(vocabulary, names=["_like_v_1"])
def _like_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding):
    if is_user_type(state.get_binding(x_actor_binding.variable.name).value[0]):
        if not state.get_binding(x_object_binding.variable.name).value[0] is None:
            yield state.record_operations(
                state.handle_world_event(["user_wants", state.get_binding(x_object_binding.variable.name).value[0]]))
    else:
        yield state


@Predication(vocabulary, names=["_please_a_1"])
def _please_a_1(state, e_introduced_binding, e_binding):
    yield state


@Predication(vocabulary, names=["_please_v_1"])
def _please_v_1(state, e_introduced_binding, i_binding1, i_binding2):
    yield state


@Predication(vocabulary, names=["polite"])
def polite(state, c_arg, i_binding, e_binding):
    yield state


@Predication(vocabulary, names=["_thanks_a_1", "_then_a_1"])
def _thanks_a_1(state, i_binding, h_binding):
    yield from call(state, h_binding)


# Scenarios:
#   - "I will sit down"
#   - "Will I sit down?"
@Predication(vocabulary, names=["_sit_v_down", "sit_v_1"])
def _sit_v_down_future(state, e_introduced_binding, x_actor_binding):
    tree_info = state.get_binding("tree").value[0]
    if not is_future_tense(tree_info): return
    if is_question(tree_info):
        # None of the future tense questions are valid english in this scenario
        report_error(["unexpected"])
        return

    def bound(x_actor):
        if is_user_type(x_actor):
            return True
        else:
            report_error(["unexpected"])
            return

    def unbound():
        if False:
            yield None

    yield from combinatorial_predication_1(state, x_actor_binding, bound, unbound)


@Predication(vocabulary, names=["solution_group__sit_v_down", "solution_group__sit_v_1"])
def _sit_v_down_future_group(state_list, has_more, e_list, x_actor_variable_group):
    tree_info = state_list[0].get_binding("tree").value[0]
    if not is_future_tense(tree_info): return

    # The planner will only satisfy a want wrt the players
    task = ('satisfy_want', variable_group_values_to_list(x_actor_variable_group), [[Concept("table")]])
    final_state = do_task(state_list[0].world_state_frame(), [task])
    if final_state:
        yield [final_state]
    else:
        yield []


# Scenarios:
#   "I sit down"
#   "Who sits down?"
@Predication(vocabulary, names=["_sit_v_down", "_sit_v_1"])
def invalid_present_intransitive(state, e_introduced_binding, x_actor_binding):
    if not is_present_tense(state.get_binding("tree").value[0]): return
    report_error(["unexpected"])
    if False: yield None


# Scenarios:
#   - "Can I sit down?" "Can I sit?" --> request for table
#   - "Who can sit down?"
#   -
#   Poor English:
#   - "Who sits down?"
#   - "Who is sitting down?"
#   - "I can sit down."
@Predication(vocabulary, names=["_sit_v_down_able", "_sit_v_1_able"])
def _sit_v_down_able(state, e_binding, x_actor_binding):
    tree_info = state.get_binding("tree").value[0]
    if not is_present_tense(tree_info): return
    if not is_question(tree_info):
        report_error(["unexpected"])
        return

    def bound(x_actor):
        if is_user_type(x_actor):
            return True
        else:
            report_error(["unexpected"])
            return

    def unbound():
        yield "user"

    yield from combinatorial_predication_1(state, x_actor_binding, bound, unbound)


@Predication(vocabulary, names=["solution_group__sit_v_down_able", "solution_group__sit_v_1_able"])
def _sit_v_down_able_group(state_list, has_more, e_introduced_binding_list, x_actor_variable_group):
    tree_info = state_list[0].get_binding("tree").value[0]
    if not is_present_tense(tree_info): return

    # If it is a wh_question, just answer it
    if is_wh_question(tree_info):
        yield state_list
    else:
        # The planner will only satisfy a want wrt the players
        task = ('satisfy_want', variable_group_values_to_list(x_actor_variable_group), [[Concept("table")]])
        final_state = do_task(state_list[0].world_state_frame(), [task])
        if final_state:
            yield [final_state]


# Scenarios:
#   "Can I see a menu? -> implied request
#   "I can see a menu. -> poor english
#   Anthing else --> don't understand
@Predication(vocabulary, names=["_see_v_1_able"])
def _see_v_1_able(state, e_introduced_binding, x_actor_binding, x_object_binding):
    tree_info = state.get_binding("tree").value[0]
    if not is_question(tree_info):
        report_error(["unexpected"])
        return

    def both_bound_prediction_function(x_actor, x_object):
        if is_user_type(x_actor):
            if valid_player_request(state, [x_object], valid_types=["menu"]):
                return True
            else:
                report_error(["unexpected"])
                return False

        else:
            # Anything about "you/they will have" is not good english
            report_error(["unexpected"])
            return False

    def actor_unbound(x_object):
        # Anything about "what will x have
        report_error(["unexpected"])
        if False:
            yield None

    def object_unbound(x_actor):
        report_error(["unexpected"])
        if False:
            yield None

    yield from in_style_predication_2(state, x_actor_binding, x_object_binding,
                                      both_bound_prediction_function,
                                      actor_unbound,
                                      object_unbound)


@Predication(vocabulary, names=["solution_group__see_v_1_able"])
def _see_v_1_able_group(state_list, has_more, e_list, x_actor_variable_group, x_object_variable_group):
    # The only valid scenarios for will have are requests, so ...
    # The planner will only satisfy a want wrt the players
    task = ('satisfy_want',
            variable_group_values_to_list(x_actor_variable_group),
            variable_group_values_to_list(x_object_variable_group))
    final_state = do_task(state_list[0].world_state_frame(), [task])
    if final_state:
        yield [final_state]
    else:
        yield []


# Scenarios:
#   "I/we will see a menu" -> implied request
#   Poor English:
#       "I will see a table/steak, etc"
@Predication(vocabulary, names=["_see_v_1"])
def _see_v_1_future(state, e_introduced_binding, x_actor_binding, x_object_binding):
    tree_info = state.get_binding("tree").value[0]
    if not is_future_tense(tree_info): return
    if is_question(tree_info):
        # None of the future tense questions are valid english in this scenario
        report_error(["unexpected"])
        return

    def both_bound_prediction_function(x_actor, x_object):
        if is_user_type(x_actor):
            if valid_player_request(state, [x_object], valid_types=["menu"]):
                return True
            else:
                report_error(["unexpected"])
                return False

        else:
            # Anything about "you/they will have" is not good english
            report_error(["unexpected"])
            return False

    def actor_unbound(x_object):
        # Anything about "what will x have
        report_error(["unexpected"])
        if False:
            yield None

    def object_unbound(x_actor):
        report_error(["unexpected"])
        if False:
            yield None

    yield from in_style_predication_2(state, x_actor_binding, x_object_binding,
                                      both_bound_prediction_function,
                                      actor_unbound,
                                      object_unbound)


@Predication(vocabulary, names=["solution_group__see_v_1"])
def _see_v_1_future_group(state_list, has_more, e_list, x_actor_variable_group, x_object_variable_group):
    tree_info = state_list[0].get_binding("tree").value[0]
    if not is_future_tense(tree_info): return

    # The only valid scenarios for will have are requests, so ...
    # The planner will only satisfy a want wrt the players
    task = ('satisfy_want',
            variable_group_values_to_list(x_actor_variable_group),
            variable_group_values_to_list(x_object_variable_group))
    final_state = do_task(state_list[0].world_state_frame(), [task])
    if final_state:
        yield [final_state]
    else:
        yield []


# Scenarios:
#   - "Can I take a menu/table/steak?"
# All are poor english
@Predication(vocabulary, names=["_take_v_1_able"])
def _take_v_1_able(state, e_introduced_binding, x_actor_binding, x_object_binding):
    report_error(["unexpected"])
    if False: yield None


# Present tense scenarios:
#   "I get x?", "I get x" --> not great english, respond with an error
#   "What do I see?"
#   "Who sees an x?
#   "I see a menu?"
#   "I see a menu"
@Predication(vocabulary, names=["_get_v_1", "_take_v_1", "_see_v_1"])
def invalid_present_transitive(state, e_introduced_binding, x_actor_binding, x_object_binding):
    if not is_present_tense(state.get_binding("tree").value[0]): return
    report_error(["unexpected"])
    if False: yield None


# Scenarios:
#   - "I will have a steak/menu/table." --> restaurant frame special case for requesting
#   - "I will have a steak/menu/table?" --> Not good english
#   - "You/they, etc will have x" --> Not good english
#   - "Will I have a steak/menu/table?" --> Not good english
#   - "Will you have a table?" --> Not good english
#   - "What will I have?" --> Not good english
#   - "Who will have x?" --> Not good english
@Predication(vocabulary, names=["_have_v_1", "_take_v_1"])
def _have_v_1_future(state, e_introduced_binding, x_actor_binding, x_object_binding):
    tree_info = state.get_binding("tree").value[0]
    if not is_future_tense(tree_info): return
    if is_question(tree_info):
        # None of the future tense questions are valid english in this scenario
        report_error(["unexpected"])
        return

    def both_bound_prediction_function(x_actors, x_objects):
        if is_user_type(x_actors):
            return valid_player_request(state, x_objects)
        else:
            # Anything about "you/they will have" is not good english
            report_error(["unexpected"])
            return False

    def actor_unbound(x_object):
        # Anything about "what will x have
        report_error(["unexpected"])
        if False:
            yield None

    def object_unbound(x_actor):
        report_error(["unexpected"])
        if False:
            yield None

    yield from lift_style_predication_2(state, x_actor_binding, x_object_binding,
                                        both_bound_prediction_function,
                                        actor_unbound,
                                        object_unbound)


@Predication(vocabulary, names=["solution_group__have_v_1", "solution_group__take_v_1"])
def _have_v_1_future_group(state_list, has_more, e_variable_group, x_actor_variable_group, x_object_variable_group):
    tree_info = state_list[0].get_binding("tree").value[0]
    if not is_future_tense(tree_info): return

    # The only valid scenarios for will have are requests, so ...
    # The planner will only satisfy a want wrt the players
    task = ('satisfy_want',
            variable_group_values_to_list(x_actor_variable_group),
            variable_group_values_to_list(x_object_variable_group))
    final_state = do_task(state_list[0].world_state_frame(), [task])
    if final_state:
        yield [final_state]
    else:
        yield []


# Just purely answers questions about having things in the present tense
# Scenarios:
#   "do I/we have x?" --> ask about the state of the world
#   "what do you have?" --> implied menu request
@Predication(vocabulary, names=["_have_v_1"])
def _have_v_1_present(state, e_introduced_binding, x_actor_binding, x_object_binding):
    if not is_present_tense(state.get_binding("tree").value[0]): return

    def bound(x_actor, x_object):
        if (object_to_store(x_actor), object_to_store(x_object)) in rel_subjects_objects(state, "have"):
            return True
        else:
            report_error(["verbDoesntApply", x_actor, "have", x_object])
            return False

    def actor_from_object(x_object):
        found = False
        for i in rel_subjects(state, "have", x_object):
            found = True
            yield store_to_object(i)
        if not found:
            report_error(["Nothing_VTRANS_X", "have", x_object])

    def object_from_actor(x_actor):
        if x_actor == "computer":
            # - "What do you have?"-->
            #   - Conceptually, there are a lot of things the computer has
            #     - But: this isn't really what they are asking. This is something that is a special phrase in the "restaurant frame" which means: "what is on the menu"
            #     - So it is a special case that we interpret as a request for a menu
            yield Concept("menu")

        else:
            found = False
            for i in rel_objects(state, x_actor, "have"):
                found = True
                yield store_to_object(state, i)
            if not found:
                report_error(["X_VTRANS_Nothing", "have", x_actor])

    yield from in_style_predication_2(state, x_actor_binding, x_object_binding, bound, actor_from_object,
                                      object_from_actor)


# Scenarios:
# - "Do you have a table?" --> implied table request
# - "what do you have?" --> implied menu request
# - "Do you have a/the menu?" --> implied menu request
# - "Do you have a/the bill?" --> implied bill request
# - "what specials do you have?" --> implied request for description of specials
#   "do I/we have x?" --> ask about the state of the world
# - "Do you have the table?" --> Should fail due to "the table" since there is neither 1 table, nor one conceptual table in scope
# - "Do you have a/the steak?" --> just asking about the steak, no implied request
# - "Do you have a bill?" --> just asking about the bill, no implied request
# - "Do you have menus?" --> Could mean "do you have conceptual menus?" or "implied menu request and thus instance check"
# - "Do you have steaks?" --> Could mean "do you have more than one preparation of steak" or "Do you have more than one instance of a steak"
@Predication(vocabulary, names=["solution_group__have_v_1"])
def _have_v_1_present_group(state_list, has_more, e_list, x_act_list, x_obj_list):
    # Ignore this group if it isn't present tense
    if not is_present_tense(state_list[0].get_binding("tree").value[0]): return

    if len(state_list) == 1:
        if len(x_act_list.solution_values) == 1 and \
                len(x_act_list.solution_values[0].value) == 1 and \
                x_act_list.solution_values[0].value[0] == "computer":
            # Questions about "Do you have a table/menu/bill?" are really implied requests in a restaurant
            # that mean "Can I have a table/menu/bill?"
            implied_request_concepts = [Concept("table"), Concept("menu"), Concept("bill")]
            if len(x_obj_list.solution_values) == 1 and \
                    len(x_obj_list.solution_values[0].value) == 1:
                if x_obj_list.solution_values[0].value[0] in implied_request_concepts:
                    # "Can I have a table/menu/bill?" is really about the instances
                    # thus check_concepts=False
                    # Fail this group if we don't meet the constraints
                    if not check_concept_solution_group_constraints(state_list, x_obj_list, check_concepts=False):
                        yield []

                    task = ('satisfy_want', [("user",)], variable_group_values_to_list(x_obj_list))
                    final_state = do_task(state_list[0].world_state_frame(), [task])
                    if final_state:
                        yield [final_state]
                        return
                    else:
                        yield []

                elif x_obj_list.solution_values[0].value[0] == Concept("special"):
                    # "Do you have specials?" is really about the concept of specials, so check_concepts=True
                    # Fail this group if we don't meet the constraints
                    if not check_concept_solution_group_constraints(state_list, x_obj_list, check_concepts=True):
                        yield []

                    task = ('describe_item', "special")
                    final_state = do_task(state_list[0].world_state_frame(), [task])
                    if final_state:
                        yield [final_state]
                        return
                    else:
                        yield []

    # Everything else is just an ask about if something has something like "Do I/we have x" or "Do you have a steak?"
    if not check_concept_solution_group_constraints(state_list, x_obj_list, check_concepts=False):
        yield []

    yield state_list


# Used only when there is a form of have that means "able to"
# The regular predication only checks if x is able to have y
# Scenarios:
#   "What can I have?" --> implied menu request
@Predication(vocabulary, names=["_have_v_1_able", "_get_v_1_able"])
def _have_v_1_able(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def both_bound_prediction_function(x_actors, x_objects):
        # Players are able to have any food, a table or a menu
        if is_user_type(x_actors):
            return valid_player_request(state, x_objects)

        # Food is able to have ingredients, restaurant can have food, etc.
        # Whatever we have modelled
        else:
            store_actors = [object_to_store(x) for x in x_actors]
            store_objects = [object_to_store(x) for x in x_objects]

            for store_actor in store_actors:
                for store_object in store_objects:
                    if not rel_check(state, store_actor, "have", store_object):
                        return False

            return True

    def actor_unbound(x_object):
        if False:
            yield None

    def object_unbound(x_actor):
        # This is a "What can I have?" type question
        # - Conceptually, there are a lot of things the user is able to have: a table, a bill, a menu, a steak, etc.
        #   - But: this isn't really what they are asking. This is something that is a special phrase in the "restaurant frame" which means: "what is on the menu"
        #     - So it is a special case that we interpret as a request for a menu
        if is_user_type(x_actor):
            yield (Concept("menu"),)

    yield from lift_style_predication_2(state, x_actor_binding, x_object_binding,
                                        both_bound_prediction_function,
                                        actor_unbound,
                                        object_unbound)


# The group predication for have_able can also generate an implied request,
# but only if it was a question with a bound actor
#
# Scenarios:
# - "who can have a steak?" -_> you, "there are more"
# - "What can I have?" --> implicit menu request
# - "Can I have a steak and a salad?" --> implicit order request
@Predication(vocabulary, names=["solution_group__have_v_1_able", "solution_group__get_v_1_able"])
def _have_v_1_able_group(state_list, has_more, e_variable_group, x_actor_variable_group, x_object_variable_group):
    # At this point they were *able* to have the item, now we see if this was an implicit request for it
    # If this is a question, but not a wh question, involving the players, then it is also a request for something
    tree_info = state_list[0].get_binding("tree").value[0]
    force = sentence_force(tree_info["Variables"])
    wh_variable = get_wh_question_variable(tree_info)
    if force in ["ques", "prop-or-ques"] and \
            ((wh_variable and x_object_variable_group.solution_values[0].value[0] == Concept("menu")) or \
             not get_wh_question_variable(tree_info)):
        # The planner will only satisfy a want wrt the players
        task = ('satisfy_want', variable_group_values_to_list(x_actor_variable_group),
                variable_group_values_to_list(x_object_variable_group))
        final_state = do_task(state_list[0].world_state_frame(), [task])
        if final_state:
            yield [final_state]
    else:
        # Not an implicit request
        yield state_list

        if has_more:
            yield True


@Predication(vocabulary, names=["poss"])
def poss(state, e_introduced_binding, x_object_binding, x_actor_binding):
    def bound(x_actor, x_object):
        if (x_actor, x_object) in state.all_rel("have"):
            return True
        else:
            report_error(["verbDoesntApply", x_actor, "have", x_object])
            return False

    def actor_from_object(x_object):
        for i in state.all_rel("have"):
            if i[1] == x_object:
                yield i[0]

    def object_from_actor(x_actor):
        for i in state.all_rel("have"):
            if i[0] == x_actor:
                yield i[1]

    yield from in_style_predication_2(state, x_actor_binding, x_object_binding, bound, actor_from_object,
                                      object_from_actor)


# Returns:
# the variable to measure into, the units to measure
# or None if not a measurement unbound variable
def measurement_information(x):
    if isinstance(x, Measurement) and isinstance(x.count, str):
        # if x is a Measurement() with a string as a value,
        # then we are being asked to measure x_actor
        measure_into_variable = x.count
        units = x.measurement_type
        if is_concept(units):
            return measure_into_variable, units.concept_name

    return None, None


@Predication(vocabulary, names=["_be_v_id"])
def _be_v_id(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor, x_object):
        measure_into_variable, units = measurement_information(x_object)
        if measure_into_variable is not None:
            return True

        else:
            first_in_second = x_actor in all_instances_and_spec(state, x_object)
            second_in_first = x_object in all_instances_and_spec(state, x_actor)
            return first_in_second or second_in_first

    def unbound(x_object):
        if is_concept(x_object):
            for i in all_instances(state, x_object.concept_name):
                yield i
            for i in specializations(state, x_object.concept_name):
                yield Concept(i)

    for success_state in in_style_predication_2(state, x_actor_binding, x_object_binding, criteria_bound, unbound,
                                                unbound):
        x_object_value = success_state.get_binding(x_object_binding.variable.name).value[0]
        x_actor_value = success_state.get_binding(x_actor_binding.variable.name).value[0]
        measure_into_variable, units = measurement_information(x_object_value)
        if measure_into_variable is not None:
            # This is a "how much is x" question and we need to measure the value
            # into the specified variable
            concept_item = instance_of_or_concept_name(state, x_actor_value)
            if units in ["generic_entity", "dollar"]:
                if concept_item in state.sys["prices"]:
                    price = Measurement("dollar", state.sys["prices"][concept_item])
                    # Remember that we now know the price
                    yield success_state.set_x(measure_into_variable, (price,)). \
                        record_operations([SetKnownPriceOp(concept_item)])
                elif concept_item == "bill":
                    total = list(rel_objects(state, "bill1", "valueOf"))
                    if len(total) == 0:
                        total.append(0)
                    price = Measurement("dollar", total[0])
                    yield success_state.set_x(measure_into_variable, (price,))

                else:
                    yield success_state.record_operations([RespondOperation("Haha, it's not for sale.")])
                    return False

        else:
            yield success_state


@Predication(vocabulary, names=["solution_group__be_v_id"])
def _be_v_id_group(state_list, has_more, e_introduced_binding_list, x_obj1_variable_group, x_obj2_variable_group):
    yield state_list


@Predication(vocabulary, names=["_cost_v_1"])
def _cost_v_1(state, e_introduced_binding, x_actor_binding, x_object_binding):
    def criteria_bound(x_actor, x_object):
        if not isinstance(x_object, Measurement):
            report_error("Have not dealt with declarative cost")
            yield False
        else:
            yield True  # will need to implement checking for price correctness in the future if user says "the soup costs one steak"

            '''
            x_object = json.loads(x_object)
            if x_object["structure"] == "price_type":
                if type(x_object["relevant_var_value"]) is int:
                    if not (instance_of_what(state, x_act), x_object["relevant_var_value"]) in state.sys["prices"]:
                        report_error("WrongPrice")
                        return False
            return True
            '''

    def get_actor(x_object):
        if False:
            yield None

    def get_object(x_actor):
        if isinstance(x_actor, Concept):
            concept_item = instance_of_or_concept_name(state, x_actor)
            if concept_item in state.sys["prices"].keys():
                yield concept_item + " : " + str(state.sys["prices"][concept_item]) + " dollars"
            else:
                yield "Ah. It's not for sale."
        else:
            yield None

    for success_state in in_style_predication_2(state, x_actor_binding, x_object_binding, criteria_bound, get_actor,
                                                get_object):
        x_object_value = success_state.get_binding(x_object_binding.variable.name).value[0]
        x_actor_value = success_state.get_binding(x_actor_binding.variable.name).value[0]
        measure_into_variable, units = measurement_information(x_object_value)
        if measure_into_variable is not None:
            # This is a "how much is x" question and we need to measure the value
            # into the specified variable
            concept_item = instance_of_or_concept_name(state, x_actor_value)
            if units in ["generic_entity", "dollar"]:
                if concept_item in state.sys["prices"]:
                    price = Measurement("dollar", state.sys["prices"][concept_item])
                    # Remember that we now know the price
                    yield success_state.set_x(measure_into_variable, (price,)). \
                        record_operations([SetKnownPriceOp(concept_item)])
                elif concept_item == "bill":
                    total = list(rel_objects(state, "bill1", "valueOf"))
                    if len(total) == 0:
                        total.append(0)
                    price = Measurement("dollar", total[0])
                    yield success_state.set_x(measure_into_variable, (price,))

                else:
                    yield success_state.record_operations([RespondOperation("Haha, it's not for sale.")])
                    return False

        else:
            yield success_state

@Predication(vocabulary, names=["solution_group__cost_v_1"])
def _cost_v_1_group(state_list, has_more, e_introduced_binding_list, x_act_variable_group, x_obj2_variable_group):
    if is_concept(x_act_variable_group.solution_values[0].value[0]):
        if not check_concept_solution_group_constraints(state_list, x_act_variable_group, check_concepts=True):
            yield []
            return
    yield state_list
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


# Any successful solution group that is a wh_question will call this
@Predication(vocabulary, names=["solution_group_wh"])
def wh_question(state_list, has_more, binding_list):
    current_state = do_task(state_list[0].world_state_frame(), [('describe', [x.value for x in binding_list])])
    if current_state is not None:
        yield (current_state,)
    else:
        yield state_list


# Generates all the responses that predications can
# return when an error occurs
def generate_custom_message(tree_info, error_term):
    # error_term is of the form: [index, error] where "error" is another
    # list like: ["name", arg1, arg2, ...]. The first item is the error
    # constant (i.e. its name). What the args mean depends on the error
    error_predicate_index = error_term[0]
    error_arguments = error_term[1]
    error_constant = error_arguments[0] if error_arguments is not None else "no error set"

    # See if the system can handle converting the error
    # to a message first
    system_message = perplexity.messages.generate_message(tree_info, error_term)
    if system_message is not None:
        return system_message

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
                               {"prices": {"salad": 3, "steak": 10, "broiled steak": 8, "soup": 4, "salmon": 12,
                                           "chicken": 7, "bacon": 2},
                                "responseState": "initial"
                                })

    initial_state = initial_state.add_rel("bill", "specializes", "thing")
    initial_state = initial_state.add_rel("check", "specializes", "thing")
    initial_state = initial_state.add_rel("kitchen", "specializes", "thing")
    # The computer has the concepts of the items so it can answer "do you have x?"
    initial_state = initial_state.add_rel("computer", "have", "kitchen")

    initial_state = initial_state.add_rel("table", "specializes", "thing")
    # The computer has the concepts of the items so it can answer "do you have x?"
    initial_state = initial_state.add_rel("computer", "have", "table")

    initial_state = initial_state.add_rel("menu", "specializes", "thing")
    # The computer has the concepts of the items so it can answer "do you have x?"
    initial_state = initial_state.add_rel("computer", "have", "menu")

    initial_state = initial_state.add_rel("person", "specializes", "thing")
    initial_state = initial_state.add_rel("son", "specializes", "person")

    initial_state = initial_state.add_rel("food", "specializes", "thing")
    initial_state = initial_state.add_rel("dish", "specializes", "food")
    initial_state = initial_state.add_rel("meat", "specializes", "dish")
    initial_state = initial_state.add_rel("veggie", "specializes", "dish")
    initial_state = initial_state.add_rel("special", "specializes", "dish")

    initial_state = initial_state.add_rel("pizza", "specializes", "meat")
    initial_state = initial_state.add_rel("steak", "specializes", "meat")
    initial_state = initial_state.add_rel("chicken", "specializes", "meat")
    initial_state = initial_state.add_rel("salmon", "specializes", "meat")
    initial_state = initial_state.add_rel("bacon", "specializes", "meat")
    initial_state = initial_state.add_rel("soup", "specializes", "veggie")
    initial_state = initial_state.add_rel("salad", "specializes", "veggie")

    # These concepts are "in scope" meaning it is OK to say "the X"
    initial_state = initial_state.add_rel("special", "conceptInScope", "true")

    # These concepts are only in scope in the table frame
    initial_state = initial_state.add_rel("menu", "conceptInScope", "true")
    initial_state = initial_state.add_rel("bill", "conceptInScope", "true")

    # The computer has the concepts of the items so it can answer "do you have steak?"
    initial_state = initial_state.add_rel("computer", "have", "menu")
    initial_state = initial_state.add_rel("computer", "have", "bill")

    # Instances below here
    # Location and "in scope" are modeled as who "has" a thing
    # If user or son has it, it is "in scope"
    # otherwise it is not
    initial_state = initial_state.add_rel("kitchen1", "instanceOf", "kitchen")

    initial_state = initial_state.add_rel("table1", "instanceOf", "table")
    initial_state = initial_state.add_rel("table1", "maxCap", 4)
    initial_state = initial_state.add_rel("table2", "instanceOf", "table")
    initial_state = initial_state.add_rel("table2", "maxCap", 4)
    initial_state = initial_state.add_rel("table3", "instanceOf", "table")
    initial_state = initial_state.add_rel("table3", "maxCap", 4)

    initial_state = initial_state.add_rel("menu1", "instanceOf", "menu")
    initial_state = initial_state.add_rel("menu2", "instanceOf", "menu")
    initial_state = initial_state.add_rel("menu3", "instanceOf", "menu")

    menu_types = ["bacon", "salmon", "steak", "chicken", "pizza"]
    special_types = ["soup", "salad"]
    dish_types = menu_types + special_types
    for dish_type in dish_types:
        # The computer has the concepts of the items so it can answer "do you have steak?"
        initial_state = initial_state.add_rel("computer", "have", dish_type)

        # These concepts are "in scope" meaning it is OK to say "the X"
        initial_state = initial_state.add_rel(dish_type, "conceptInScope", "true")

        if dish_type in menu_types:
            initial_state = initial_state.add_rel(dish_type, "on", "menu")
        else:
            initial_state = initial_state.add_rel(dish_type, "priceUnknownTo", "user")
            initial_state = initial_state.add_rel(dish_type, "specializes", "special")

        # Create the food instances
        for i in range(3):
            # Create an instance of this food
            food_instance = dish_type + str(i)
            initial_state = initial_state.add_rel(food_instance, "instanceOf", dish_type)

            # The kitchen is where all the food is
            initial_state = initial_state.add_rel("kitchen1", "have", food_instance)
            if dish_type == "chicken":
                initial_state = initial_state.add_rel(food_instance, "isAdj", "roasted")
            if dish_type == "salmon":
                initial_state = initial_state.add_rel(food_instance, "isAdj", "grilled")

    initial_state = initial_state.add_rel("computer", "have", "special")
    initial_state = initial_state.add_rel("bill1", "instanceOf", "bill")
    initial_state = initial_state.add_rel("bill1", "instanceOf", "check")
    initial_state = initial_state.add_rel(0, "valueOf", "bill1")
    initial_state = initial_state.add_rel("room", "contains", "user")

    initial_state = initial_state.add_rel("son1", "instanceOf", "son")
    initial_state = initial_state.add_rel("son1", "hasName", "your son")
    initial_state = initial_state.add_rel("user", "instanceOf", "person")
    initial_state = initial_state.add_rel("user", "hasName", "you")
    initial_state = initial_state.add_rel("user", "have", "son1")
    initial_state = initial_state.add_rel("user", "heardSpecials", "false")

    return initial_state


def error_priority(error_string):
    system_priority = perplexity.messages.error_priority(error_string)
    if system_priority is not None:
        return system_priority
    else:
        # Must be a message from our code
        error_constant = error_string[1][0]
        return error_priority_dict.get(error_constant, error_priority_dict["defaultPriority"])


error_priority_dict = {
    "defaultPriority": 1000
}


def hello_world():
    user_interface = UserInterface(reset, vocabulary, message_function=generate_custom_message,
                                   error_priority_function=error_priority, scope_function=in_scope,
                                   scope_init_function=in_scope_initialize)

    while True:
        user_interface.interact_once()
        print()


if __name__ == '__main__':
    # ShowLogging("Execution")
    # ShowLogging("Generation")
    # ShowLogging("UserInterface")
    ShowLogging("Pipeline")
    # ShowLogging("SString")
    # ShowLogging("Determiners")
    ShowLogging("SolutionGroups")

    print("Hello there, what can I do for you?")
    # ShowLogging("Pipeline")
    # ShowLogging("Transformer")
    hello_world()
