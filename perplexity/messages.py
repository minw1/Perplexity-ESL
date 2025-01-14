from perplexity.response import RespondOperation
from perplexity.sstring import s
from perplexity.tree import predication_from_index, find_predication_from_introduced, find_predication
from perplexity.utilities import parse_predication_name, sentence_force


# Implements the response for a given tree
# yields: response, solution_group that generated the response
# In scenarios where there is an open solution group (meaning like "files are ..." where there is an initial solution that will
# grow), this will yield once for every additional solution
def respond_to_mrs_tree(message_function, tree, solution_groups, error):
    # Tree can be None if we didn't have one of the
    # words in the vocabulary
    if tree is None:
        message = message_function(None, error)
        yield message, None
        return

    sentence_force_type = sentence_force(tree["Variables"])
    if sentence_force_type == "prop" or sentence_force_type == "prop-or-ques":
        # This was a proposition, so the user only expects
        # a confirmation or denial of what they said.
        # The phrase was "true" if there was at least one answer
        if solution_groups is not None:
            yield None, next(solution_groups)
            return

        else:
            message = message_function(tree, error)
            yield message, None
            return

    elif sentence_force_type == "ques":
        # See if this is a "WH" type question
        wh_predication = find_predication(tree["Tree"], "_which_q")
        if wh_predication is None:
            wh_predication = find_predication(tree["Tree"], "which_q")

        if wh_predication is None:
            # This was a simple question, so the user only expects
            # a yes or no.
            # The phrase was "true" if there was at least one answer
            if solution_groups is not None:
                yield "Yes.", next(solution_groups)
                return

            else:
                message = message_function(tree, error)
                yield message, None
                return

        else:
            # This was a "WH" question.
            # Return the values of the variable
            # asked about from the solution
            # The phrase was "true" if there was at least one answer
            if solution_groups is not None:
                # Build an error term that we can use to call generate_message
                # to get the response
                index_predication = find_predication_from_introduced(tree["Tree"], tree["Index"])
                wh_variable = wh_predication.introduced_variable()
                solution_group = next(solution_groups)

                # If any solution in the group has a RespondOperation in it, assume that the response
                # has been handled by that and just return an empty string
                # This is how the user can replace the default behavior of listing out the answers
                for solution in solution_group:
                    for operation in solution.get_operations():
                        if isinstance(operation, RespondOperation):
                            yield "", solution_group
                            return

                yield message_function(tree, [-1, ["answerWithList", index_predication, wh_variable, solution_group, solution_group[0]]]), solution_group

            else:
                message = message_function(tree, error)
                yield message, None
                return

    elif sentence_force_type == "comm":
        # This was a command so, if it works, just say so
        # We'll get better errors and messages in upcoming sections
        if solution_groups is not None:
            yield None, next(solution_groups)

        else:
            message = message_function(tree, error)
            yield message, None


def generate_message(tree_info, error_term):
    error_predicate_index = error_term[0]
    error_arguments = error_term[1]
    error_constant = error_arguments[0] if error_arguments is not None else "no error set"
    arg_length = len(error_arguments) if error_arguments is not None else 0
    arg1 = error_arguments[1] if arg_length > 1 else None
    arg2 = error_arguments[2] if arg_length > 2 else None
    arg3 = error_arguments[3] if arg_length > 3 else None

    if error_constant == "answerWithList":
        # This is the default for a wh_question: just print out the values
        def answer_variable_value(answer_items):
            if len(answer_items) > 0:
                message = "\n".join([str(answer_item) for answer_item in answer_items])
                return message
            else:
                return ""

        wh_variable = arg2
        solution_group = arg3
        response = ""
        answer_items = set()
        for solution in solution_group:
            binding = solution.get_binding(wh_variable)
            if binding.variable.combinatoric:
                value_set = ((value, ) for value in binding.value)
                if value_set not in answer_items:
                    answer_items.add(value_set)
                    response += answer_variable_value(value_set)

            else:
                if binding.value not in answer_items:
                    answer_items.add(binding.value)
                    response +=  answer_variable_value([binding.value])

        return response


    elif error_constant == "beMoreSpecific":
        return f"Could you be more specific?"

    elif error_constant == "doesntExist":
        return s("There isn't {a arg1:sg} in the system", tree_info)

    # Used when you want to embed the error message directly in the code
    elif error_constant == "errorText":
        return error_arguments[1]

    elif error_constant == "formNotUnderstood":
        predication = predication_from_index(tree_info, error_predicate_index)
        parsed_predicate = parse_predication_name(predication.name)

        if len(error_arguments) > 1 and error_arguments[1] == "notHandled":
            # The event had something that the predication didn't know how to handle
            # See if there is information about where it came from
            if "Originator" in error_arguments[2][1]:
                originator_index = error_arguments[2][1]["Originator"]
                originator_predication = predication_from_index(tree_info, originator_index)
                parsed_originator = parse_predication_name(originator_predication.name)
                return f"I don't understand the way you are using '{parsed_originator['Lemma']}' with '{parsed_predicate['Lemma']}'"

        return f"I don't understand the way you are using: {parsed_predicate['Lemma']}"

    elif error_constant == "lessThan":
        return s("There are less than {*arg2} {bare arg1:sg@error_predicate_index}", tree_info)

    elif error_constant == "moreThan":
        return s("There {'is':<arg1} more than {arg1:@error_predicate_index}", tree_info)

    elif error_constant == "moreThan1":
        return s("There is more than one {bare arg1}", tree_info)

    elif error_constant == "moreThanN":
        # TODO: Make arg1 match arg2's plural
        return s("There {'is':<*arg2} more than {*arg2} {bare arg1:@error_predicate_index}", tree_info)  # s(None, arg1, count=int(arg2))}")

    elif error_constant == "notTrueForAll":
        return s("That isn't true for all {arg1:@error_predicate_index}", tree_info)

    elif error_constant == "notAllError":
        return s("That isn't true, there {'is':<arg2}n't {arg1} that {'is':<arg2}n't {arg2}", tree_info)

    elif error_constant == "notClause":
        return s("That isn't true")

    elif error_constant == "notError":
        return s("There isn't {an arg1}", tree_info)

    elif error_constant == "tooManyItemsTogether":
        return "I don't understand using terms in a way that means 'together' in that sentence"

    elif error_constant == "unexpected":
        return "I'm not sure what that means."

    elif error_constant == "unknownWords":
        lemmas_unknown = []
        lemmas_form_known = []
        for unknown_predication in error_arguments[1]:
            parsed_predicate = parse_predication_name(unknown_predication[0])
            if unknown_predication[3]:
                lemmas_form_known.append(parsed_predicate["Lemma"])
            else:
                lemmas_unknown.append(parsed_predicate["Lemma"])

        answers = []
        if len(lemmas_unknown) > 0:
            answers.append(f"I don't know the words: {', '.join(lemmas_unknown)}")

        if len(lemmas_form_known) > 0:
            answers.append(f"I don't know the way you used: {', '.join(lemmas_form_known)}")

        return " and ".join(answers)

    elif error_constant == "valueIsNotX":
        return s("{*arg1} is not {arg2}", tree_info)

    elif error_constant == "valueIsNotValue":
        return f"{arg1} is not {arg2}"

    elif error_constant == "xIsNotY":
        return s("{arg1:@error_predicate_index} is not {arg2:@error_predicate_index}", tree_info)

    elif error_constant == "xIsNotYValue":
        return s("{arg1} is not {*arg2}", tree_info)

    elif error_constant == "zeroCount":
        return s("I'm not sure which {bare arg1:@error_predicate_index} you mean.", tree_info)

    else:
        return None


def error_priority(error_string):
    global error_priority_dict
    if error_string is None:
        return 0

    else:
        if error_string[1] is None:
            return error_priority_dict["defaultPriority"]

        error_constant = error_string[1][0]
        priority = error_priority_dict.get(error_constant, None)
        if priority is not None:
            if error_constant == "unknownWords":
                priority -= len(error_string[1][1])

            return priority
        else:
            return None


# Highest numbers are best errors to return
# The absolute value of number doesn't mean anything, they are just for sorting
# The defaultPriority key is the default value for errors that aren't explicitly listed
error_priority_dict = {
    # Unknown words error should only be shown if
    # there are no other errors, AND the number
    # of unknown words is subtracted from it so
    # lower constants should be defined below this:
    # "unknownWordsMin": 800,
    "unknownWords": 900,
    # Slightly better than not knowing the word at all
    "formNotUnderstood": 901,
    "notClause": 910,
    # Lots of misinterpretations can generate this, so make it lower than default
    "doesntExist": 920,
    "defaultPriority": 1000,

    # This is just used when sorting to indicate no error, i.e. success.
    # Nothing should be higher
    "success": 10000000
}
