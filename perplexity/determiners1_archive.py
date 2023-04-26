import copy
import itertools
import logging
import sys
from perplexity.set_utilities import all_nonempty_subsets, all_combinations_with_elements_from_all, append_if_unique, \
    count_set, all_nonempty_subsets_stream
from perplexity.utilities import is_plural, at_least_one_generator
from importlib import import_module
from perplexity.variable_binding import VariableValueType
from perplexity.vocabulary import PluralType


# For phrases like "files are large" or "only 2 files are large" we need a gate around
# the quantifier that only returns answers if they meet some criteria
# Note that the thing being counted is the actual rstr values,
# so rstr_x = [a, b] would count as 2
def determiner_from_binding(state, binding):
    if binding.variable.determiner is not None:
        determiner_constraint = binding.variable.determiner[0]
        determiner_type = binding.variable.determiner[1]
        determiner_constraint_args = binding.variable.determiner[2]
        return [determiner_constraint, determiner_type, determiner_constraint_args]

    elif is_plural(state, binding.variable.name):
        # Plural determiner
        return ["number_constraint", "default", [1, float('inf'), False]]

    else:
        # A default singular determiner is not necessary because the quantifiers that
        # distinguish singular (like "the" and "only 1") already check for it.
        # Furthermore, adding it as ["number_constraint", "default", [1, 1, False]]
        # unnecessarily breaks optimizations that are possible in optimize_determiner_infos
        return


def quantifier_from_binding(state, binding):
    if binding.variable.quantifier is not None:
        quantifier_constraint = binding.variable.quantifier[0]
        quantifier_type = binding.variable.quantifier[1]
        quantifier_constraint_args = binding.variable.quantifier[2]
        return [quantifier_constraint, quantifier_type, quantifier_constraint_args]

    else:
        return None


# Return an iterator that yields lists of solutions ("a solution list") without combinatorial variables.
# These are lists of solutions because: If variable_name is a combinatorial variable it means that any combination
#   of values in it are true, so as long as one from the group remains at the end, the solution group is still valid.
#       For solution_group_combinatorial=true, it is the equivalent of breaking it into N more alternative
#           solutions with each solution having one of the combinations of possible values
#       For solution_group_combinatorial=false, it means that the solutions can't be broken up and must all be true.
#           But: the combinatorial variable means that *any* of the combinations for that variable can be true
#           if we just include all combinations in the non-combinatorial list, it will require them all to be true which isn't right
#           so instead we have to try every alternative by generating an entire new answer list for each alternative
# If it is not a combinatorial value, it gets added, as is, to set_solution_list
def solution_list_alternatives_without_combinatorial_variables(execution_context, variable_name, max_answer_count, solutions_orig,
                                                               cardinal_criteria, solution_group_combinatorial=False):
    variable_metadata = execution_context.get_variable_metadata(variable_name)
    variable_plural_type = variable_metadata["PluralType"]

    # set_solution_alternatives_list contains all the alternatives for
    # a combinatoric variable. set_solution_list contains all values that were not combinatoric
    set_solution_alternatives_list = []
    set_solution_list = []

    for solution in solutions_orig:
        binding = solution.get_binding(variable_name)
        if binding.variable.value_type == VariableValueType.combinatoric:
            # If variable_name is combinatoric, all of its appropriate alternative combinations
            # get added to set_solution_alternatives_list
            # Thus, if the variable_plural_type is collective, we only add sets > 1, etc
            min_size = 1
            max_size = None
            if variable_plural_type == PluralType.distributive:
                max_size = 1

            elif variable_plural_type == PluralType.collective:
                min_size = 2

            else:
                assert variable_plural_type == PluralType.all

            def binding_alternative_generator():
                for subset in all_nonempty_subsets_stream(binding.value, min_size=min_size, max_size=max_size):
                    yield solution.set_x(variable_name, subset, VariableValueType.set)

            binding_alternatives = binding_alternative_generator()
            set_solution_alternatives_list.append(binding_alternatives)

        else:
            set_solution_list.append(solution)

    # Flatten out the list of lists since they are all alternatives of the same variable
    if len(set_solution_alternatives_list) > 0:
        determiner_logger.debug(f"Found {len(set_solution_alternatives_list)} combinatoric answers")
        temp = [item for item in itertools.chain.from_iterable(set_solution_alternatives_list)]
        set_solution_alternatives_list = temp

    # Now the combination of set_solution_alternatives_list together with set_solution_list contain
    # all the alternative assignments of variable_name. Next, yield each combined alternative
    if solution_group_combinatorial:
        def combinatorial_solution_group_generator():
            for item in itertools.chain.from_iterable([set_solution_list, set_solution_alternatives_list]):
                if determiner_logger.isEnabledFor(logging.DEBUG):
                    determiner_logger.debug(f"Combinatorial answer: {item}")
                yield item

        yield combinatorial_solution_group_generator()

    else:
        determiner_logger.debug(f"Answers are not combinatorial")
        # See comments at top of function for what this is doing
        set_solution_alternatives_list = at_least_one_generator(set_solution_alternatives_list)
        alternative_yielded = False
        if set_solution_alternatives_list is not None:
            for alternative_list in all_nonempty_subsets_stream(set_solution_alternatives_list):
                # First add all the solutions that are shared between the alternatives
                # because they weren't combinatorial
                # Then add this combinatorial alternative
                def combinatorial_solution_group_generator():
                    yield from itertools.chain.from_iterable([copy.deepcopy(set_solution_list), alternative_list])

                yield combinatorial_solution_group_generator()
                alternative_yielded = True

        if not alternative_yielded:
            yield solutions_orig


# TODO: Bug in this code: it returns an answer before it is done iterating and
#  thus doesn't know the full list of solutions that go with it
# Convert each list of solutions into a list of (binding_value, [solutions]) pairs
# where binding_value has one rstr value and [solutions] is a list of
# all solutions that have that value.
def unique_rstr_solution_list_generator(variable_name, solutions_list):
    variable_assignments = set()
    for solution_index in range(len(solutions_list)):
        binding_value = solutions_list[solution_index].get_binding(variable_name).value
        if binding_value in variable_assignments:
            variable_assignments[binding_value][1].append(solution_index)
        else:
            unique_solution = (binding_value, [solution_index])
            variable_assignments.add(unique_solution)
            yield unique_solution


def unique_rstr_solution_list_generator2(previous_variable_name, variable_name, solutions_list):
    variable_assignments_by_previous = {}
    for solution_index in range(len(solutions_list)):
        previous_binding_value = solutions_list[solution_index].get_binding(previous_variable_name).value
        binding_value = solutions_list[solution_index].get_binding(variable_name).value
        if previous_binding_value in variable_assignments_by_previous:
            variable_assignments = variable_assignments_by_previous[previous_binding_value]
        else:
            variable_assignments = {}
            variable_assignments_by_previous[previous_binding_value] = variable_assignments

        if binding_value not in variable_assignments:
            variable_assignments[binding_value] = []

        variable_assignments[binding_value].append(solution_index)

    yield from [item.items() for item in variable_assignments_by_previous.values()]


# Ensure that solutions_orig is broken up into a set of solution groups that are not combinatoric in any way
# max_answer_count is the maximum number of individual items that will ever be used.
#   So, for "2 boys", it should be 2 since it must be no more than 2
#   but for "boys" it has to be None since it could be a huge set of boys
# combinatorial is True when any combination of the solutions can be used, otherwise, the exact set must be true
def determiner_solution_groups_helper(execution_context, previous_variable_name, variable_name, solutions_orig, determiner_criteria, solution_group_combinatorial=False, is_last_determiner=False, max_answer_count=float('inf')):
    # Loop through solution lists that don't contain combinatorial variables
    for solutions_list_generator in solution_list_alternatives_without_combinatorial_variables(execution_context, variable_name, max_answer_count, solutions_orig, determiner_criteria, solution_group_combinatorial):
        # Unfortunately, we need to materialize each solutions list to find all the duplicates
        solutions_list = list(solutions_list_generator)
        determiner_logger.debug(f"Creating determiner solution list size: {len(solutions_list)}:")

        if previous_variable_name is None:
            alternative_variable_names = [None]
        else:
            alternative_variable_names = [None, previous_variable_name]

        for distributive_previous_variable_name in alternative_variable_names:
            determiner_logger.debug(f"distributive_previous_variable_name: {distributive_previous_variable_name}:")

            # Get all the unique values assigned to this variable, and collect the solutions that go with them
            # Workaround: generate the list since it isn't properly formed lazily. It returns an answer before it is done iterating and
            # thus doesn't know the full list of solutions that go with it
            previous_variable_success_list_of_lists = []
            for variable_assignments in unique_rstr_solution_list_generator2(distributive_previous_variable_name, variable_name, solutions_list):
                # returns a set of solutions for this previous variable name
                previous_value_success_lists = []
                had_success = False
                for success_list in solve(variable_assignments, solutions_list, determiner_criteria, solution_group_combinatorial, is_last_determiner, max_answer_count):
                    had_success = True
                    if distributive_previous_variable_name is None:
                        # Not distributive so we can yield immediately
                        yield success_list
                    else:
                        # distributive: need to make sure all previous variables work distributively
                        previous_value_success_lists.append(success_list)

                if not had_success:
                    # distributive must succeed at least once for each previous value, so fail if one fails
                    # other modes will only have one list so that fails too
                    break
                else:
                    previous_variable_success_list_of_lists.append(previous_value_success_lists)

            if distributive_previous_variable_name is not None and len(previous_variable_success_list_of_lists) > 0:
                for item in all_combinations_with_elements_from_all(previous_variable_success_list_of_lists):
                    yield from item


def solve(variable_assignments, solutions_list, determiner_criteria, solution_group_combinatorial, is_last_determiner, max_answer_count):
    if solution_group_combinatorial:
        # Get all the combinations of the variable assignments that meet the criteria
        # largest set of lists that can add up to self.count is where every list is 1 item long
        for combination in all_nonempty_subsets_stream(variable_assignments, min_size=1, max_size=max_answer_count):
            # The variable assignments in a combination could have duplicates: need to deduplicate them
            # combination is a list of 2 element lists
            unique_values = set([inner_item for item in combination for inner_item in item[0]])

            # Now see if it works for the determiner, which means the *values* meet the determiner
            # But each set of values might have multiple solutions that go with it, so this means
            # Any combination of them will also work
            if determiner_criteria(unique_values):
                # If we are not the last determiner, we need to return all possible combinations of solutions that contained the assignments
                # in case later determiners need them
                if not is_last_determiner:
                    # ... which means returning all combinations of the list of solutions that go with each rstr answer
                    # as long as there is at least one element from each
                    #
                    # 'combination' is a list of 2 element lists:
                    #   0 is a list of variable assignments
                    #   1 is a list of solutions that had that assignment
                    for possible_solution in all_combinations_with_elements_from_all([combination_item[1] for combination_item in combination]):
                        combination_solutions = []
                        for index in possible_solution:
                            combination_solutions.append(solutions_list[index])

                        yield combination_solutions

                else:
                    # The last determiner does not need to create groups outside of what it needs
                    # to do its job. Just return all the solutions combined together
                    yield itertools.chain([solutions_list[solution_index] for combination_item in combination for solution_index in combination_item[1]])

    else:
        # The variable assignments in a combination could have duplicates
        # Need to deduplicate them
        unique_values = set([inner_item for item in variable_assignments for inner_item in item[0]])
        if determiner_criteria(unique_values):
            yield solutions_list


# Set max to float('inf') to mean "no maximum"
def between_determiner(execution_context, previous_variable_name, variable_name, predication, all_rstr, solution_group, combinatorial, is_last_determiner, min_count, max_count, exactly):
    def criteria(rstr_value_list):
        cardinal_group_values_count = count_set(rstr_value_list)
        error_location = ["AfterFullPhrase", variable_name]

        # Even though this *looks* like exactly, it is picking out solutions where there just happen to be
        # N files, so it isn't really
        if cardinal_group_values_count > max_count:
            execution_context.report_error_for_index(0, ["moreThan", error_location, max_count], force=True)
            return False

        elif cardinal_group_values_count < min_count:
            execution_context.report_error_for_index(0, ["lessThan", error_location, min_count], force=True)
            return False

        else:
            nonlocal group_rstr
            group_rstr = rstr_value_list
            return True

    if exactly:
        error_location = ["AfterFullPhrase", variable_name]

        # "Only/Exactly", much like the quantifier "the" does more than just group solutions into groups ("only 2 files are in the folder")
        # it also limits *all* the solutions to that number. So we need to go to the bitter end before we know that that are "only 2"
        # group_rstr is set in the criteria each time a rstr is checked
        group_rstr = []
        unique_rstrs = set()
        groups = []
        for group in determiner_solution_groups_helper(execution_context, previous_variable_name, variable_name, solution_group, criteria, combinatorial, is_last_determiner, max_count):
            for item in group_rstr:
                append_if_unique(unique_rstrs, item)

            if len(unique_rstrs) > max_count:
                execution_context.report_error_for_index(0, ["moreThan", error_location, max_count], force=True)
                return

            else:
                groups.append(group)

        if len(unique_rstrs) < min_count:
            execution_context.report_error_for_index(0, ["lessThan", error_location, min_count], force=True)
            return

        else:
            yield from groups

    else:
        yield from determiner_solution_groups_helper(execution_context, previous_variable_name, variable_name, solution_group, criteria, combinatorial, is_last_determiner, max_count)


determiner_logger = logging.getLogger('Determiners')