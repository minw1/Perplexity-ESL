## Title
Even 1 plural variable in an MRS will require grouping to represent the complete solution if they are acting alone: "men walk".   (the collective can be one solution). In this case you'd just expect one group. But: subsets of that group would also be true.

With two variables: men are walking a dog you'd still only expect one group in any world. But again, subsets would work.

So, some scenarios have a maximal answer that in one group represents all objects in any other answer. i.e. it is combinatorial

which files are in a folder

### Criteria Optimizations
It is key to remember that between(1, 1) means *at least* it it isn't set to exactly.
So, we should transform it to between(1, inf)

### Implied Outer Quantifier
which files are large?
    just returning 2 of N large files is correct, but not right
Theory: really people mean "(give me all answers to) which files are large?"

delete large files
    (all)
delete files
    (all)
delete 2 files
    (not all, just two)
Theory: delete should just do the *first answer*. Only works like above if we get the maximal answer

2 files are large

### Which Outputs are Needed?
Stepping back, what does the system actually *use* from the output? 

True or False
 doesn't have to return all answers, just one correct one. 

Unique Values: But "Which" ideally would group the answers. A human would say "these guys are walking this dog, and those guys are walking that dog" 
    If we are willing to not group the answers, "which" doesn't have to return all answers, just correct ones. Meaning: it can avoid enumerating all the answers that are just subsets of a correct one for, for example, a between(1, inf).

Commands: ? Unique values of all arguments ?
    Delete files (could be 2 files or all files)
    Need to decide if this a maximal or minimal solution

(actual solutions might be needed for abductive reasoning?)


# There is no reason to return all combinations at the end because nothing will use them?

### Archive
When numeric constraints are removed from an MRS we are left with a relatively straightforward constraint satisfaction problem that should be able to return solutions quickly, but there still may be *many* solutions.

Any variable that is plural can be combined with other plural variables in cdc (collective/distributive/cumulative) ways
    Actually, any plural variable that is combined with another variable *in any form* can form cdc groups: children are eating a (or 1) pizza. Requires cdc analysis to be true when people expect.

Actually, 


Phase 2 checks a given group to see if it meets the collective, distributive, cumulative criteria.

files are 20 mb: 

### Streaming All Combinations
See if adding the value to a set might meet the criteria, if so, create a new group. Leave the other one there so other groups using it will get created

build up sets and return them

### Removing sets that can't produce others
This trims the search space


### Which files are in a folder
Just needs to return unique files that are in a folder (which is all of them)
file between(1, inf)
folder between(1, 1) (at least)

Really this is just unique(x3)?