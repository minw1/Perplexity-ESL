## Representing File and Directory Names: `fw_seq` and `quoted`
There are several challenges with representing file and directory names in a phrase. First, the user may or may not represent them with some kind of escaping characters around them. For example, to move to the directory "blue" they could say:

~~~
go to 'blue'
go to "blue"
go to blue
~~~

The ERG will nicely recognize the different types of quotes as quotes, so those boil down to the same thing, but it will try to interpret the unquoted one as a "real" sentence, not a reference to "blue" as the name of a thing.

Furthermore, many of the specifiers the user may use for directories or files are not English:

~~~
go to /user/brett
list out f56.txt
~~~

The ERG will represent these, but they require implementing several more predications. The easiest approach is to require the user to quote anything that represents a file or folder.  We can attempt to do more options later.


If the user simply types in a phrase like "delete 'blue'", the ERG produces 4 parses. The first two attempt to interpret "blue" semantically as the color "blue" by using the predication `_blue_a_1`:

~~~
***** Parse #0:
Sentence Force: comm
[ "delete "blue""
  TOP: h0
  INDEX: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pronoun_q<0:13> LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
          [ pron<0:13> LBL: h7 ARG0: x3 ]
          [ _delete_v_1<0:6> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: sg ] ]
          [ udef_q<7:13> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ _blue_a_1<8:12> LBL: h12 ARG0: x8 ARG1: i13 ] >
  HCONS: < h0 qeq h1 h5 qeq h7 h10 qeq h12 > ]

-- Parse #0, Tree #0: 

               ┌────── pron(x3)
pronoun_q(x3,RSTR,BODY)            ┌────── _blue_a_1(x8,i13)
                    └─ udef_q(x8,RSTR,BODY)
                                        └─ _delete_v_1(e2,x3,x8)

...
    

***** Parse #1:
Sentence Force: prop-or-ques
[ "delete "blue""
  TOP: h0
  INDEX: e2 [ e SF: prop-or-ques TENSE: tensed MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _delete_v_1<0:6> LBL: h1 ARG0: e2 ARG1: i3 ARG2: x4 [ x PERS: 3 NUM: sg ] ]
          [ udef_q<7:13> LBL: h5 ARG0: x4 RSTR: h6 BODY: h7 ]
          [ _blue_a_1<8:12> LBL: h8 ARG0: x4 ARG1: i9 ] >
  HCONS: < h0 qeq h1 h6 qeq h8 > ]

-- Parse #1, Tree #0: 

            ┌────── _blue_a_1(x4,i9)
udef_q(x4,RSTR,BODY)
                 └─ _delete_v_1(e2,i3,x4)

~~~

That would be useful, perhaps, in a phrase like "She is 'blue'", where we do mean to use the "blue" semantically to mean "sad" but where the speaker is indicating this is a nonstandard or special use of the word by putting it in quotes. This is not we want, so we can move to the next parse:

~~~
***** Parse #2:
Sentence Force: comm
[ "delete "blue""
  TOP: h0
  INDEX: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pronoun_q<0:13> LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
          [ pron<0:13> LBL: h7 ARG0: x3 ]
          [ _delete_v_1<0:6> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: sg ] ]
          [ proper_q<7:13> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ fw_seq<-1:-1> LBL: h12 ARG0: x8 ARG1: i13 ]
          [ _blue_a_1<8:12> LBL: h12 ARG0: i13 ARG1: i14 ] >
  HCONS: < h0 qeq h1 h5 qeq h7 h10 qeq h12 > ]

-- Parse #2, Tree #0: 

                                                 ┌── _blue_a_1(i13,i14)
                                     ┌────── and(0,1)
               ┌────── pron(x3)      │             │
               │                     │             └ fw_seq(x8,i13)
pronoun_q(x3,RSTR,BODY)              │
                    └─ proper_q(x8,RSTR,BODY)
                                          └─ _delete_v_1(e2,x3,x8)

... 
    
~~~

This one is closer because it does indicate that `i13` is a `fw_seq`. `fw_seq` stands for "foreign word sequence" (since quotations often delineate foreign phrases), but it is also used for all kinds of quoted text. It is described in more detail [here](https://blog.inductorsoftware.com/docsproto/erg/ErgSemantics_ForeignExpressions/). In this case, it is telling us that the phrase includes a string in quotes (by using `fw_seq`), but also gives us the semantic interpretation of the phrase in quotes (by using `_blue_a_1`). That would be a good hint if our system was trying to see if the usage of "blue" was a "non-standard" use of the term to mean something like "sad" instead of saying "she is literally the color blue", but it still isn't quite the interpretation we want. 

The next one is what we need here:
~~~
***** CHOSEN Parse #3:
Sentence Force: comm
[ "delete "blue""
  TOP: h0
  INDEX: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pronoun_q<0:13> LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
          [ pron<0:13> LBL: h7 ARG0: x3 ]
          [ _delete_v_1<0:6> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: sg ] ]
          [ proper_q<7:13> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ fw_seq<-1:-1> LBL: h12 ARG0: x8 ARG1: i13 ]
          [ quoted<8:12> LBL: h12 ARG0: i13 CARG: "blue" ] >
  HCONS: < h0 qeq h1 h5 qeq h7 h10 qeq h12 > ]

-- Parse #3, Tree #0: 

                                                 ┌── quoted(blue,i13)
                                     ┌────── and(0,1)
               ┌────── pron(x3)      │             │
               │                     │             └ fw_seq(x8,i13)
pronoun_q(x3,RSTR,BODY)              │
                    └─ proper_q(x8,RSTR,BODY)
                                          └─ _delete_v_1(e2,x3,x8)
~~~
This parse doesn't try to deliver the semantic interpretation of the word in quotes, and instead just gives us the raw term using the predication `quoted`, meaning "this text was in quotes". Then, it uses `fw_seq` on the quoted variable `i13`. This will make more sense later since `fw_seq` is used to join together all the words in a quoted string. We'll see that next. For now, it is just a degenerate case that is there for consistency with more complicated quoted strings.

Note that `x8` is quantified by `proper_q` which is often used for proper nouns, but can be used as a marker of all kinds of "raw text". So, by the time `x8` gets to `_delete_v_1`, it should be a nicely quoted string, wrapped in some object, that `_delete_v_1` can use to delete the file.

So for this, we need to implement: `quoted(i)`, `fw_seq(x,i)` and update  `_delete_v_1(e,x,x)` to handle whatever they output.

`quoted` is special in that it has an argument called `CARG` (described in detail [here](https://blog.inductorsoftware.com/docsproto/erg/ErgSemantics_Essence/#further-ers-contents)). `CARG` is a way to pass a constant to a predication without holding in a variable. The argument will simply be raw text:

~~~
          [ quoted<8:12> LBL: h12 ARG0: i13 CARG: "blue" ]
~~~

It is also special in that it uses an `i` variable instead of an `x` variable to hold a value. This is because the ERG wanted to avoid having to have a quantifier for each quoted string, as would be required for an `x` argument. That pattern was covered in the [MRS topic](../devhowto/devhowtoMRS/#other-variables-types-i-u-p).

So, the implementation of `quoted` only has to take the `CARG` and put it into a new object called `QuotedText`, setting the `i` variable to that:

~~~
class QuotedText(object):
    def __init__(self, name):
        self.name = name
        
...

    
@Predication(vocabulary)
def quoted(state, c_raw_text, i_text):
    # c_raw_text_value will always be set
    c_raw_text_value = c_raw_text
    i_text_value = state.get_variable(i_text)

    if i_text_value is None:
        yield state.set_x(i_text, QuotedText(c_raw_text_value))
    else:
        if isinstance(i_text_value, QuotedText) and i_text_value.name == c_raw_text:
            yield state
~~~

The job of `fw_seq(x,i)` is only to set the value of `x` to whatever `i` is, or vice versa (other versions will get more interesting, as described below):

~~~
@Predication(vocabulary)
def fw_seq(state, x_phrase, i_part):
    x_phrase_value = state.get_variable(x_phrase)
    i_part_value = state.get_variable(i_part)
    if i_part_value is None:
        if x_phrase_value is None:
            # This should never happen since it basically means
            # "return all possible strings"
            assert False
        else:
            yield state.set_x(i_part, x_phrase_value)
    else:
        if x_phrase_value is None:
            yield state.set_x(x_phrase, i_part_value)

        elif x_phrase_value == i_part_value:
            yield state
~~~

... and `delete_v_1_comm` has to now include `QuotedText` as a valid thing to delete, and `DeleteOperation.apply_to()` has to be modified to handle converting a `QuotedText` object to a file using the `FileSystem.item_from_path()` method:

~~~
def delete_v_1_comm(state, e_introduced, x_actor, x_what):

    ...
    
        # If this is text, make sure it actually exists
        if isinstance(x_what_value, QuotedText):
            actual_item = state.file_system.item_from_path(x_what_value.name)
            if actual_item is not None:
                yield state.apply_operations([DeleteOperation(x_what_value)])
            else:
                report_error(["notFound", x_what])
        else:
            # Only allow deleting files and folders or
            # textual names of files
            if isinstance(x_what_value, (File, Folder, QuotedText)):
                yield state.apply_operations([DeleteOperation(x_what_value)])

            else:
                report_error(["cantDo", "delete", x_what])
            
            
def generate_message(tree_info, error_term):

    ...
    
    elif error_constant == "notFound":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info)
        return f"{arg1} was not found"
        
        
class DeleteOperation(object):
    
    ...
    
    def apply_to(self, state):
        if isinstance(state, FileSystemState):
            state.file_system.delete_item(self.object_to_delete)
            if isinstance(self.object_to_delete, QuotedText):
                object_to_delete = state.file_system.item_from_path(self.object_to_delete.name)
            else:
                object_to_delete = self.object_to_delete

            state.file_system.delete_item(object_to_delete)
            
~~~

`proper_q` can just be a default quantifier as described [here](../devhowto/devhowtoSimpleQuestions):

~~~
@Predication(vocabulary)
def proper_q(state, x_variable, h_rstr, h_body):
    yield from default_quantifier(state, x_variable, h_rstr, h_body) 
~~~

With those changes, we can now use some simple phrases with one word quoted files:

~~~
def Example23_reset():
    return FileSystemState(FileSystemMock([(True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {"size": 10000000}),
                                           (True, "/Desktop/the yearly budget.txt", {"size": 10000000}),
                                           (True, "/Desktop/blue", {"size": 1000})],
                                          "/Desktop"))


def Example23():
    user_interface = UserInterface(Example23_reset, vocabulary, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()
        
Test: "blue" is in this folder
Yes, that is true.

Test: delete "blue"
Done!

Test: "blue" is in this folder
thing is not in this folder
~~~

We are almost done, but that last message is not great. As always, when we add a new predication to the system, we need to teach [the NLG system](../devhowto/devhowtoConceptualFailures/) how to interpret the new predications so that it doesn't say 'thing' in the error:

~~~
def refine_nlg_with_predication(tree_info, variable, predication, nlg_data):
    
    ...
    
                # Some abstract predications *should* contribute to the
                # English description of a variable
                
                ...
                
                elif parsed_predication["Lemma"] == "quoted":
                    nlg_data["Topic"] = predication.args[0]

                elif parsed_predication["Lemma"] == "fw_seq":
                    string_list = []
                    for arg_index in range(1, len(predication.arg_names)):
                        if predication.args[arg_index][0] == "i":
                            # Use 1000 to make sure we go through the whole tree
                            string_list.append(english_for_delphin_variable(1000, predication.args[arg_index], tree_info, default_a_quantifier=False))

                        elif predication.args[arg_index][0] == "x":
                            # Use 1000 to make sure we go through the whole tree
                            string_list.append(english_for_delphin_variable(1000, predication.args[arg_index], tree_info, default_a_quantifier=False))
                            
                    nlg_data["Topic"] = f"\'{' '.join(string_list)}\'"
~~~

Now we get:

~~~
Test: "blue" is in this folder
'blue' is not in this folder
~~~

For longer quotes strings like:

> delete "the yearly budget.txt"

The ERG generates a few more variations of `fw_seq` since each only glues two things together:

~~~
Sentence Force: comm
[ "delete "the yearly budget.txt""
  TOP: h0
  INDEX: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pronoun_q<0:30> LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
          [ pron<0:30> LBL: h7 ARG0: x3 ]
          [ _delete_v_1<0:6> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: sg ] ]
          [ proper_q<7:30> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ fw_seq<7:30> LBL: h12 ARG0: x8 ARG1: x13 ARG2: i14 ]
          [ fw_seq<7:18> LBL: h12 ARG0: x13 ARG1: i15 ARG2: i16 ]
          [ quoted<8:11> LBL: h12 ARG0: i15 CARG: "the" ]
          [ quoted<12:18> LBL: h12 ARG0: i16 CARG: "yearly" ]
          [ quoted<19:29> LBL: h12 ARG0: i14 CARG: "budget.txt" ] >
  HCONS: < h0 qeq h1 h5 qeq h7 h10 qeq h12 > ]

                                                 ┌──────── quoted(budget.txt,i14)
                                                 │ ┌────── quoted(yearly,i16)
                                                 │ │ ┌──── quoted(the,i15)
                                     ┌────── and(0,1,2,3,4)
                                     │                 └─│ fw_seq(x13,i15,i16)
               ┌────── pron(x3)      │                   │
pronoun_q(x3,RSTR,BODY)              │                   │
                    │                │                   └ fw_seq(x8,x13,i14)
                    └─ proper_q(x8,RSTR,BODY)
                                          └─ _delete_v_1(e2,x3,x8)
~~~
The ERG converts the quoted phrase into a set of predications, one for each word in quotes:

~~~
          [ quoted<8:11> LBL: h12 ARG0: i15 CARG: "the" ]
          [ quoted<12:18> LBL: h12 ARG0: i16 CARG: "yearly" ]
          [ quoted<19:29> LBL: h12 ARG0: i14 CARG: "budget.txt" ]
~~~

And then indicates that they are all part of a sequence using the predication `fw_seq` in various forms:

~~~
          [ fw_seq<7:18> LBL: h12 ARG0: x13 ARG1: i15 ARG2: i16 ]
          [ fw_seq<7:30> LBL: h12 ARG0: x8 ARG1: x13 ARG2: i14 ]
~~~

The first `fw_seq` joins together `i15` and `i16` which are "the" and "yearly" and puts the result in `x13`. The next `fw_seq` joins together `x13` and `i14` (which is "budget.txt") and puts the result in `x8`. So now, `x8` has the entire string again. Note that `x8` is quantified by `proper_q` which is often used for proper nouns, but can be used as a marker of all kinds of "raw text". 

The only thing we need to add to make it all work is the implementation of `fw_seq(x,x,i)` and `fw_seq(x,i,i)`. We will need to name these differently because Python doesn't overloaded functions (same function name with different arguments):

~~~
@Predication(vocabulary)
def fw_seq2(state, x_phrase, i_part1, i_part2):
    x_phrase_value = state.get_variable(x_phrase)
    i_part1_value = state.get_variable(i_part1)
    i_part2_value = state.get_variable(i_part2)

    if isinstance(i_part1_value, QuotedText) and isinstance(i_part2_value, QuotedText):
        combined_value = QuotedText(" ".join([i_part1_value.name, i_part2_value.name]))
        if x_phrase_value is None:
            yield state.set_x(x_phrase, combined_value)

        elif isinstance(x_phrase_value, QuotedText) and x_phrase_value.name == combined_value.name:
            yield state


@Predication(vocabulary)
def fw_seq3(state, x_phrase, x_part1, i_part2):
    x_phrase_value = state.get_variable(x_phrase)
    x_part1_value = state.get_variable(x_part1)
    i_part2_value = state.get_variable(i_part2)

    if isinstance(x_part1_value, QuotedText) and isinstance(i_part2_value, QuotedText):
        combined_value = QuotedText(" ".join([x_part1_value.name, i_part2_value.name]))
        if x_phrase_value is None:
            yield state.set_x(x_phrase, combined_value)

        elif isinstance(x_phrase_value, QuotedText) and x_phrase_value.name == combined_value.name:
            yield state
~~~

And if we run it:

~~~
? "the yearly budget.txt" is in this folder
Yes, that is true.

? delete "the yearly budget.txt"
Done!

? "the yearly budget.txt" is in this folder
''the yearly' budget.txt' is not in this folder
~~~

Note that the error message for the last statement isn't quite right yet because we are putting quotes around each `fw_seq` pair of strings:

~~~
def refine_nlg_with_predication(tree_info, variable, predication, nlg_data):
    
    ...
    
                elif parsed_predication["Lemma"] == "fw_seq":
                    string_list = []
                    for arg_index in range(1, len(predication.arg_names)):
                        if predication.args[arg_index][0] == "i":
                            # Use 1000 to make sure we go through the whole tree
                            string_list.append(english_for_delphin_variable(1000, predication.args[arg_index], tree_info, default_a_quantifier=False))

                        elif predication.args[arg_index][0] == "x":
                            # Use 1000 to make sure we go through the whole tree
                            string_list.append(english_for_delphin_variable(1000, predication.args[arg_index], tree_info, default_a_quantifier=False))
                            
                    nlg_data["Topic"] = f"\'{' '.join(string_list)}\'"
~~~

Observe that the introduced variable of a non-final `fw_seq` predication is only used by another `fw_seq` predication:

~~~
Sentence Force: comm
[ "delete "the yearly budget.txt""
  TOP: h0
  INDEX: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pronoun_q<0:30> LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
          [ pron<0:30> LBL: h7 ARG0: x3 ]
          [ _delete_v_1<0:6> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: sg ] ]
          [ proper_q<7:30> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ fw_seq<7:30> LBL: h12 ARG0: x8 ARG1: x13 ARG2: i14 ]
          [ fw_seq<7:18> LBL: h12 ARG0: x13 ARG1: i15 ARG2: i16 ]
          [ quoted<8:11> LBL: h12 ARG0: i15 CARG: "the" ]
          [ quoted<12:18> LBL: h12 ARG0: i16 CARG: "yearly" ]
          [ quoted<19:29> LBL: h12 ARG0: i14 CARG: "budget.txt" ] >
  HCONS: < h0 qeq h1 h5 qeq h7 h10 qeq h12 > ]

                                                 ┌──────── quoted(budget.txt,i14)
                                                 │ ┌────── quoted(yearly,i16)
                                                 │ │ ┌──── quoted(the,i15)
                                     ┌────── and(0,1,2,3,4)
                                     │                 └─│ fw_seq(x13,i15,i16)
               ┌────── pron(x3)      │                   │
pronoun_q(x3,RSTR,BODY)              │                   │
                    │                │                   └ fw_seq(x8,x13,i14)
                    └─ proper_q(x8,RSTR,BODY)
                                          └─ _delete_v_1(e2,x3,x8)
~~~

So, we can write code to only put quotes around string generated by an `fw_seq` predication when it is used by something *besides* and `fw_seq` predication. First, let's create a utility function using our handy `walk_tree_predications_until()` helper that gathers all of the predications in the tree that consume a specific variable:

~~~
def find_predications_using_variable(term, variable):
    def match_predication_using_variable(predication):
        for arg_index in range(1, len(predication.arg_types)):
            if predication.arg_types[arg_index] not in ["c", "h"]:
                if predication.args[arg_index] == variable:
                    predication_list.append(predication)

    predication_list = []
    walk_tree_predications_until(term, match_predication_using_variable)

    return predication_list
~~~

Then, we can use `find_predications_using_variable()` to determine if a `fw_seq` is introducing a variable that is being used by something besides another `fw_seq`:

~~~
def refine_nlg_with_predication(tree_info, variable, predication, nlg_data):
    
    ...
    
                elif parsed_predication["Lemma"] == "fw_seq":
                    string_list = []
                    for arg_index in range(1, len(predication.arg_names)):
                        if predication.args[arg_index][0] == "i":
                            # Use 1000 to make sure we go through the whole tree
                            string_list.append(english_for_delphin_variable(1000, predication.args[arg_index], tree_info, default_a_quantifier=False))

                        elif predication.args[arg_index][0] == "x":
                            # Use 1000 to make sure we go through the whole tree
                            string_list.append(english_for_delphin_variable(1000, predication.args[arg_index], tree_info, default_a_quantifier=False))

                    # If the only thing consuming the introduced variable are other fw_seq predications
                    # Then this is not the final fw_seq, so don't put quotes around it
                    consuming_predications = find_predications_using_variable(tree_info["Tree"], predication.args[0])
                    if len([predication for predication in consuming_predications if predication.name != "fw_seq"]) == 0:
                        nlg_data["Topic"] = f"{' '.join(string_list)}"
                    else:
                        nlg_data["Topic"] = f"'{' '.join(string_list)}'"
~~~

Now, if we run the scenario again, we get a better answer:

~~~
? "the yearly budget.txt" is in this folder
Yes, that is true.

? delete "the yearly budget.txt"
Done!

? "the yearly budget.txt" is in this folder
'the yearly budget.txt' is not in this folder
~~~