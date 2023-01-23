import copy
import logging
from file_system_example.objects import Actor, QuotedText


# The state representation used by the file system example
# note that the core system doesn't care at all what this object
# looks like. It is only the predications that interact with it
#
# "class" declares an object-oriented class in Python
# The parenthesis after the "State" class name surround
# the object the class derives from (object)
class State(object):
    # All class methods are indented under the
    # class and take "self" as their first argument.
    # "self" represents the class instance.

    # "__init__" is a special method name that
    # indicates the constructor, which is called to create
    # a new instance of the class. Arguments beyond "self"
    # get passed to the function when the instance is created
    def __init__(self, objects):
        # Class member variables are created by
        # simply assigning to them
        self.variables = dict()  # an empty dictionary

        # "objects" are passed to us as an argument
        # by whoever creates an instance of the class
        self.objects = objects

        # Remember all the operations applied to the state object
        self.operations = []

    # Defines what the default printed output of a state object is
    def __repr__(self):
        return ", ".join([variable_item[0] + " = " + str(variable_item[1]) for variable_item in self.variables.items() if variable_item[0] != 'tree'])

    # A standard "class method" is just a function definition,
    # indented properly, with "self" as the first argument

    # This is how predications will access the current value
    # of MRS variables like "x1" and "e1"
    def get_variable(self, variable_name):
        # "get()" is one way to access a value in a dictionary.
        # The second argument, "None", is what to return if the
        # key doesn't exist.  "None" is a built-in value in Python
        # like "null"
        return self.variables.get(variable_name, None)

    # This is how predications will set the value
    # of an "x" variable (or another type of variable
    # that is acting like an unquantified "x" variable)
    def set_x(self, variable_name, item):
        # Make a *copy* of the entire object using the built-in Python
        # class called "copy", we pass it "self" so it copies this
        # instance of the object
        new_state = copy.deepcopy(self)

        # Now we have a new "State" object with the same
        # world state that we can modify.

        # Dictionaries hold name/value pairs.
        # This is how you assign values to keys in dictionaries
        new_state.variables[variable_name] = item

        # "return" returns to the caller the new state with
        # that one variable set to a new value
        return new_state

    def add_to_e(self, eventName, key, value):
        newState = copy.deepcopy(self)
        if newState.get_variable(eventName) is None:
            newState.variables[eventName] = dict()

        newState.variables[eventName][key] = value
        return newState

    # This is an iterator (described above) that returns
    # all the objects in the world
    def all_individuals(self):
        for item in self.objects:
            yield item

    # Call to apply a list of operations to
    # a new State object
    def apply_operations(self, operation_list):
        newState = copy.deepcopy(self)
        for operation in operation_list:
            operation.apply_to(newState)
            newState.operations.append(operation)

        return newState

    def get_operations(self):
        return copy.deepcopy(self.operations)


# Optimized for the file system example
class FileSystemState(State):
    def __init__(self, file_system):
        super().__init__([])
        self.file_system = file_system
        self.current_user = Actor(name="User", person=1, file_system=file_system)
        self.actors = [self.current_user,
                       Actor(name="Computer", person=2, file_system=file_system)]

    def all_individuals(self):
        yield from self.file_system.all_individuals()
        yield from self.actors

    def user(self):
        return self.current_user


# Delete any object in the system
class DeleteOperation(object):
    def __init__(self, object_to_delete):
        self.object_to_delete = object_to_delete

    def apply_to(self, state):
        if isinstance(state, FileSystemState):
            if isinstance(self.object_to_delete, QuotedText):
                object_to_delete = state.file_system.item_from_path(self.object_to_delete.name)
            else:
                object_to_delete = self.object_to_delete

            state.file_system.delete_item(object_to_delete)

        else:
            for index in range(0, len(state.objects)):
                # Use the `unique_id` property to compare objects since they
                # may have come from different `State` objects and will thus be copies
                if state.objects[index].unique_id == self.object_to_delete.unique_id:
                    state.objects.pop(index)
                    break


pipeline_logger = logging.getLogger('Pipeline')
