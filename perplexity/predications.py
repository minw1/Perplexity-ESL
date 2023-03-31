import itertools
from perplexity.variable_binding import VariableValueType


# Yields each possible variable set from binding based on what type of value it is
# "discrete" means it will generate specific all possible sets (i.e. not yield a combinatoric value)
# If a variable is combinatoric it means it represents all combinations of values in that set
def discrete_variable_set_generator(binding):
    if binding.variable.value_type == VariableValueType.set:
        # This is a single set that needs to be kept intact
        yield VariableValueType.set, binding.value
        return

    else:
        # Generate all possible sets
        assert binding.variable.value_type == VariableValueType.combinatoric

        min_set_size = 1
        max_set_size = len(binding.value)

        for value_set_size in range(min_set_size, max_set_size + 1):
            for value_set in itertools.combinations(binding.value, value_set_size):
                yield VariableValueType.set, value_set


# "'lift' style" means that:
# - a group behaves differently than an individual (like "men lifted a table")
# - thus the predication_function is called with sets of things
def lift_style_predication(state, binding1, binding2, prediction_function):
    # See if everything in binding1_set has the
    # prediction_function relationship to binding2_set
    for binding1_set_type, binding1_set in discrete_variable_set_generator(binding1):
        for binding2_set_type, binding2_set in discrete_variable_set_generator(binding2):
            # See if everything in binding1_set has the
            # prediction_function relationship to binding2_set
            success, set1_used_collective, set2_used_collective = prediction_function(binding1_set, binding2_set)
            if success:
                set1_used_collective = set1_used_collective if len(binding1_set) > 1 else False
                set2_used_collective = set2_used_collective if len(binding2_set) > 1 else False

                yield state.set_x(binding1.variable.name, binding1_set, binding1_set_type, used_collective=set1_used_collective) \
                    .set_x(binding2.variable.name,binding2_set,binding2_set_type, used_collective=set2_used_collective)


# "'in' style" means that:
# - {a, b} predicate {x, y} can be checked as a predicate x, a predicate y, etc.
# - that collective and distributive are both ok, but nothing special happens (unlike lift)
# - that the any combinatoric terms will be turned into single set terms (coll or dist)
def in_style_predication(state, binding1, binding2, prediction_function):
    # See if everything in binding1_set has the
    # prediction_function relationship to binding2_set
    for binding1_set_type, binding1_set in discrete_variable_set_generator(binding1):
        for binding2_set_type, binding2_set in discrete_variable_set_generator(binding2):
            # See if everything in binding1_set has the
            # prediction_function relationship to binding2_set
            sets_fail = False
            for binding1_item in binding1_set:
                for binding2_item in binding2_set:
                    if not prediction_function(binding1_item, binding2_item):
                        sets_fail = True
                        break
                if sets_fail:
                    break

            if not sets_fail:
                yield state.set_x(binding1.variable.name,
                                  binding1_set,
                                  binding1_set_type).set_x(binding2.variable.name,
                                                           binding2_set,
                                                           binding2_set_type)


# "Combinatorial Style" means: preserve (or create) a combinatorial set if possible
def combinatorial_style_predication(state, binding, all_individuals_generator, predication_function):
    if binding.variable.value_type == VariableValueType.set:
        # This is a single set that needs to be kept intact
        # and succeed or fail as a unit
        all_must_succeed = True

    else:
        all_must_succeed = False

    if binding.value is None:
        # Unbound variable means the incoming set contains "all individuals"
        iterator = all_individuals_generator

    else:
        # x is set to a set of values, restrict them to just those that match the predication_function
        iterator = binding.value

    values = []
    for value in iterator:
        if predication_function(value):
            values.append(value)
        elif all_must_succeed:
            # One didn't work, so fail
            return

    if len(values) > 0:
        yield state.set_x(binding.variable.name, values, binding.variable.value_type)
