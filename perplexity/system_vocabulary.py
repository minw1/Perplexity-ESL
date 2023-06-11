import copy
import logging

from perplexity.execution import execution_context, call, set_variable_execution_data, report_error, \
    get_variable_metadata
from perplexity.plurals import VariableCriteria, GlobalCriteria, NegatedPredication
from perplexity.predications import combinatorial_predication_1, discrete_variable_generator, all_combinations_of_states
from perplexity.set_utilities import all_combinations_with_elements_from_all, product_stream, all_nonempty_subsets
from perplexity.solution_groups import solution_groups
from perplexity.tree import TreePredication, gather_scoped_variables_from_tree_at_index, \
    gather_referenced_x_variables_from_tree
from perplexity.utilities import at_least_one_generator
from perplexity.vocabulary import Predication, Vocabulary, ValueSize

vocabulary = Vocabulary()


# Merge the system vocabulary into new_vocabulary
def system_vocabulary():
    return copy.deepcopy(vocabulary)


def rstr_reorderable(rstr):
    return isinstance(rstr, TreePredication) and rstr.name in ["place_n", "thing"]


# Yield all undetermined, unquantified answers
def quantifier_raw(state, x_variable_binding, h_rstr_orig, h_body_orig, criteria_predication=None):
    reverse = rstr_reorderable(h_rstr_orig)
    h_rstr = h_body_orig if reverse else h_rstr_orig
    h_body = h_rstr_orig if reverse else h_body_orig

    variable_name = x_variable_binding.variable.name
    rstr_values = []
    for rstr_solution in call(state, h_rstr):
        if criteria_predication is not None:
            alternative_states = criteria_predication(rstr_solution, rstr_solution.get_binding(x_variable_binding.variable.name))
        else:
            alternative_states = [rstr_solution]

        for alternative_state in alternative_states:
            rstr_values.extend(alternative_state.get_binding(variable_name).value)
            for body_solution in call(alternative_state, h_body):
                yield body_solution

    set_variable_execution_data(variable_name, "AllRstrValues", rstr_values)

    if not reverse and len(rstr_values) == 0:
        # If the rstr was actually run (i.e. not reversed) and produced no values:
        # Ignore whatever error the RSTR produced, this is a better one
        report_error(["doesntExist", ["AtPredication", h_body, x_variable_binding.variable.name]], force=True)


@Predication(vocabulary)
def thing(state, x_binding):
    def bound_variable(_):
        return True

    def unbound_variable():
        for item in state.all_individuals():
            yield item

    yield from combinatorial_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["_a_q"])
def a_q(state, x_variable_binding, h_rstr, h_body):
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(execution_context().current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=1))

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body)


# Several meanings:
# 1. Means "this" which only succeeds for rstrs that are the single in scope x set and there are no others that are in scope
#       "put the two keys in the lock": should only work if there are only two keys in scope:
#       run the rstr, run the cardinal (potentially fail), the run the body (potentially fail)
# 2. Means "the one and only" which only succeeds if the rstr is a single set and there are no other sets
#       same approach
@Predication(vocabulary, names=["_the_q"])
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


@Predication(vocabulary, names=["which_q", "_which_q"])
def which_q(state, x_variable_binding, h_rstr, h_body):
    current_predication = execution_context().current_predication()

    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(current_predication,
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf')))

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body)


@Predication(vocabulary, names=["udef_q", "pronoun_q", "proper_q"])
def generic_q(state, x_variable_binding, h_rstr, h_body):
    state = state.set_variable_data(x_variable_binding.variable.name,
                                    quantifier=VariableCriteria(execution_context().current_predication(),
                                                                x_variable_binding.variable.name,
                                                                min_size=1,
                                                                max_size=float('inf')))

    yield from quantifier_raw(state, x_variable_binding, h_rstr, h_body)


@Predication(vocabulary, names=["_a+few_a_1"])
def a_few_a_1(state, e_introduced_binding, x_target_binding):
    yield state.set_variable_data(x_target_binding.variable.name,
                                  determiner=VariableCriteria(execution_context().current_predication(),
                                                              x_target_binding.variable.name,
                                                              min_size=3,
                                                              max_size=5))


@Predication(vocabulary, names=["_and_c"])
def and_c(state, x_binding_introduced, x_binding_first, x_binding_second):
    size_total = len(x_binding_first.value) + len(x_binding_second.value)
    yield state.set_x(x_binding_introduced.variable.name,
                      x_binding_first.value + x_binding_second.value,
                      combinatoric=True,
                      determiner=VariableCriteria(execution_context().current_predication(),
                                                  x_binding_introduced.variable.name,
                                                  min_size=size_total,
                                                  max_size=size_total)
                      )


@Predication(vocabulary, names=["implicit_conj"])
def implicit_conj(state, x_binding_introduced, x_binding_first, x_binding_second):
    yield from and_c(state, x_binding_introduced, x_binding_first, x_binding_second)


@Predication(vocabulary, names=["neg"])
def neg(state, e_introduced_binding, h_scopal):
    # Gather all the bound x variables and their values that are referenced in h_scopal
    referenced_x_variables = gather_referenced_x_variables_from_tree(h_scopal)
    combinatorial_referenced_x_values = {}
    for variable_name in referenced_x_variables:
        binding = state.get_binding(variable_name)
        if binding.value is not None and binding.variable.combinatoric:
            combinatorial_referenced_x_values[variable_name] = binding.value

    # Record all the variables this neg() has scope over so we can add it as an event later
    scoped_variables, _ = gather_scoped_variables_from_tree_at_index(state.get_binding("tree").value[0]["Tree"], execution_context().current_predication_index())
    negated_predication_info = NegatedPredication(execution_context().current_predication(), scoped_variables)

    # If a state makes h_scopal True, this predication fails since it is neg(). That part is straightforward.
    # However, we need to return the neg() success states too. neg() succeeds when h_scopal fails, but the problem is that
    # combinatorial variables can be in the incoming state, and thus an h_scopal like large(x) might fail for some subset of the combinatorial values
    # in x, and we won't know since we only see the successes coming out of large(x) (i.e. when it yields). We need a way to determine
    # if a particular value fails
    #
    # Furthermore, combinatorial variables might expand under neg(), like
    #   "which files are not in two folders": which_q(x3,_file_n_of(x3,i8),neg(e9,udef_q(x12,[_folder_n_of(x12,i19), card(2,e18,x12)],_in_p_loc(e2,x3,x12))))
    #   if x3 is combinatorial, it will expand under neg() effectively creating:
    #   which_q(x3,,neg(e9,[_file_n_of(x3,i8), udef_q(x12,[_folder_n_of(x12,i19), card(2,e18,x12)],_in_p_loc(e2,x3,x12)))])
    #   which is a different answer
    #
    # So, if there are combinatorial variables, we need to make them discrete before neg. The final subtlety is that *all combinations* of the
    # combinatorial variables must be tried, so we need to return the combinatorics. So, we need a function that returns the cartesian product
    # of all combinatorial variables
    h_scopal_has_quantifiers = len(scoped_variables) > 0
    if h_scopal_has_quantifiers:
        def state_generator():
            # Use state instead of negated_predications_state so the solution group processor doesn't think
            # this is negative: we want it evaluated positively
            for combination_state in all_combinations_of_states(state, combinatorial_referenced_x_values):
                # Use resolve_fragment to run numeric criteria on the "not" clause. So that a phrase like
                # "which files not in this folder are not large?" would work
                had_negative_success = False
                for _ in execution_context().resolve_fragment(combination_state, h_scopal):
                    # This is true, don't yield it since neg() makes it False
                    report_error(["notClause"], force=True)
                    had_negative_success = True

                if execution_context().has_not_understood_error():
                    # this was not a logical failure, we simply didn't understand
                    return

                if not had_negative_success:
                    # There were no solutions for this combination_state, so it is false, and thus true
                    # Record that this was a negative success for debugging purposes
                    combination_state = combination_state.add_to_e("negated_predications",
                                                                   execution_context().current_predication_index(),
                                                                   negated_predication_info)
                    yield combination_state.add_to_e("negated_successes", execution_context().current_predication_index(), True)

    else:
        def state_generator():
            # Use negated_predications_state so the solution group processor knows
            # this should be negated later when it runs
            negated_predications_state = state.add_to_e("negated_predications",
                                                        execution_context().current_predication_index(),
                                                        negated_predication_info)
            for combination_state in all_combinations_of_states(negated_predications_state, combinatorial_referenced_x_values):
                # No scoped variables, just run it directly
                had_negative_success = False
                for _ in call(combination_state, h_scopal):
                    # This is true, don't yield it since neg() makes it False
                    report_error(["notClause"], force=True)
                    had_negative_success = True

                if execution_context().has_not_understood_error():
                    # this was not a logical failure, we simply didn't understand
                    return

                if not had_negative_success:
                    # There were no solutions for this combination_state, so it is false, and thus true
                    # Record that this was a negative success for debugging purposes
                    yield combination_state.add_to_e("negated_successes", execution_context().current_predication_index(), True)

    yield from state_generator()


pipeline_logger = logging.getLogger('Pipeline')

