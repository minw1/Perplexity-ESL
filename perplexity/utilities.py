# Returns a dict:
# {
#     "Surface" : True | False
#     "Lemma" : "go"...
#     "Pos" : "v"...
#     "PredicateRaw":
#     "Sense": "dir"...
# }
import importlib
import inspect
import logging
import sys


def parse_predication_name(name):
    result = {"PredicateRaw": name}

    if name[0] == "_":
        params = name[1:].split("_")
        result["Surface"] = True
    else:
        params = name.split("_")
        result["Surface"] = False

    # From this point forward, everything up to the POS is the lemma
    # and everything after the POS is the sense
    got_pos = False
    for item in params:
        if not got_pos:
            # some words like "a" look like a POS so don't get tricked
            # From wiki entry: RmrsPos
            # Label	Explanation	Example	Comment
            # n := u	noun	banana_n_1	WordNet n
            # v := u	verb	bark_v_1	WordNet v
            # a := u	adjective or adverb (i.e. supertype of j and r)	fast_a_1
            # j := a	adjective	 	WordNet a
            # r := a	adverb	 	WordNet r
            # s := n, s:= v	verbal noun (used in Japanese and Korean)	benkyou_s_1
            # c := u	conjunction	and_c_1
            # p := u	adposition (preposition, postposition)	from_p_1, kara_p_1 (から_p_1)
            # q := u	quantifier (needs to be distinguished for scoping code)	this_q_1
            # x := u	other closed class	ahem_x_1
            # u	unknown
            if "Lemma" in result and item in ["n", "v", "a", "j", "r", "s", "c", "p", "q", "x", "u"]:
                result["Pos"] = item
                got_pos = True
            else:
                # Keep adding to the lemma until we find POS (if it exists)
                # e.g. d_fw_seq_end_z__xx
                result["Lemma"] = item if "Lemma" not in result else f"{result['Lemma']}_{item}"
        else:
            result["Sense"] = item if "Sense" not in result else f"{result['Sense']}_{item}"

    if "Lemma" not in result:
        result["Lemma"] = "#unknown#"

    if "Pos" not in result:
        # u for unknown
        result["Pos"] = "u"

    return result


def sentence_force(variables):
    for variable in variables.items():
        if "SF" in variable[1]:
            return variable[1]["SF"]


def ShowLogging(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(name)s %(asctime)s: %(message)s')
    file_handler = logging.StreamHandler(sys.stdout)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


# Get the actual module name even if it is the
# initial python file run, which gets the module
# name "__main__"
def module_name(obj):
    name = obj.__module__

    if "__main__" in name:
        # get parent modules of object
        mod_obj = inspect.getmodule(obj)  # type: module

        # from the filename of the module, get its name'
        mod_suffix = inspect.getmodulename(inspect.getmodule(obj).__file__)

        # join parent to child with a .
        name = '.'.join([mod_obj.__package__, mod_suffix]) if (mod_obj.__package__ != "" and mod_obj.__package__ is not None) else mod_suffix

    return name


# Takes a pair of module and function names as strings and
# imports the module and returns the function
def import_function_from_names(module_name, function_name):
    importlib.import_module(module_name)
    module = sys.modules[module_name]
    function = getattr(module, function_name)
    return function


pipeline_logger = logging.getLogger('Pipeline')
