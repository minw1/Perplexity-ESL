import copy
import json
from perplexity.response import RespondOperation
from perplexity.set_utilities import Measurement
from perplexity.state import State


def sort_of(state, thing, possible_type):
    if thing == possible_type:
        return True
    for i in state.rel["specializes"]:
        if i[1] == possible_type:
            if sort_of(state, thing, i[0]):
                return True
    for i in state.rel["instanceOf"]:
        if i[1] == possible_type:
            if sort_of(state, thing, i[0]):
                return True
    return False


def all_instances(state, thing):
    proc = [thing]
    proc_idx = 0
    inst = set()

    # for i in state.rel["instanceOf"]:
    #    if(i[0] == thing):
    #        return thing

    while proc_idx < len(proc):
        to_process = proc[proc_idx]
        for i in state.rel["specializes"]:
            if i[1] == to_process:
                if i[0] not in proc:
                    proc += [i[0]]
        for i in state.rel["instanceOf"]:
            if i[1] == to_process:
                if i[0] not in inst:
                    yield i[0]
                    inst.add(i[0])
        proc_idx += 1


def all_instances_and_spec(state, thing):
    yield thing

    proc = [thing]
    proc_idx = 0
    inst = set()

    while proc_idx < len(proc):
        to_process = proc[proc_idx]
        for i in state.rel["specializes"]:
            if i[1] == to_process:
                if i[0] not in proc:
                    proc += [i[0]]
                    yield i[0]
        for i in state.rel["instanceOf"]:
            if i[1] == to_process:
                if i[0] not in inst:
                    yield i[0]
                    inst.add(i[0])
        proc_idx += 1


def all_ancestors(state, thing):
    proc = [thing]
    proc_idx = 0

    while proc_idx < len(proc):
        to_process = proc[proc_idx]
        for i in state.rel["instanceOf"]:
            if i[0] == to_process:
                if i[1] not in proc:
                    yield i[1]
                    proc += [i[1]]

        for i in state.rel["specializes"]:
            if i[0] == to_process:
                if i[1] not in proc:
                    proc += [i[1]]
                    yield i[1]
        proc_idx += 1


class AddRelOp(object):
    def __init__(self, rel):
        self.toAdd = rel

    def apply_to(self, state):
        state.mutate_add_rel(self.toAdd[0], self.toAdd[1], self.toAdd[2])


class AddBillOp(object):
    def __init__(self, item):
        self.toAdd = item

    def apply_to(self, state):
        prices = state.sys["prices"]
        assert (self.toAdd in prices)
        state.mutate_add_bill(prices[self.toAdd])


class ResetOrderAndBillOp(object):
    def apply_to(self, state):
        state.mutate_reset_bill()
        state.mutate_reset_order()


class ResponseStateOp(object):
    def __init__(self, item):
        self.toAdd = item

    def apply_to(self, state):
        state.mutate_set_response_state(self.toAdd)


class WorldState(State):
    def __init__(self, relations, system):
        super().__init__([])
        self.rel = relations
        self.sys = system

    def all_individuals(self):
        for i in self.get_entities():
            yield i

    def bill_total(self):
        for i in self.rel["valueOf"]:
            if i[1] == "bill1":
                return i[0]

    def add_rel(self, first, relation_name, second):
        new_relation = copy.deepcopy(self.rel)
        if relation_name not in new_relation:
            new_relation[relation_name] = [(first, second)]
        else:
            new_relation[relation_name] += [(first, second)]
        return WorldState(new_relation, self.sys)

    def mutate_add_rel(self, first, relation_name, second):
        new_relation = copy.deepcopy(self.rel)
        if relation_name not in new_relation:
            new_relation[relation_name] = [(first, second)]
        else:
            new_relation[relation_name] += [(first, second)]
        self.rel = new_relation

    def mutate_reset_rel(self, keyname):
        new_relation = copy.deepcopy(self.rel)
        new_relation.pop(keyname, None)
        self.rel = new_relation

    def mutate_add_bill(self, addition):
        new_relation = copy.deepcopy(self.rel)
        for i in range(len(new_relation["valueOf"])):
            if new_relation["valueOf"][i][1] == "bill1":
                new_relation["valueOf"][i] = (addition + new_relation["valueOf"][i][0], "bill1")
        self.rel = new_relation

    def mutate_reset_bill(self):
        new_relation = copy.deepcopy(self.rel)
        for i in range(len(new_relation["valueOf"])):
            if new_relation["valueOf"][i][1] == "bill1":
                new_relation["valueOf"][i] = (0, "bill1")
        self.rel = new_relation

    def mutate_reset_order(self):
        new_relation = copy.deepcopy(self.rel)
        new_relation["ordered"] = []
        self.rel = new_relation

    def mutate_set_response_state(self, new_state):
        self.sys["responseState"] = new_state

    def get_entities(self):
        entities = set()
        for i in self.rel.keys():
            for j in self.rel[i]:
                entities.add(j[0])
                entities.add(j[1])
        return entities

    def get_reprompt(self):
        if self.sys["responseState"] == "something_to_eat":
            return " \nWaiter: Can I get you something to eat?"
        if self.sys["responseState"] == "anticipate_party_size":
            return " \nWaiter: How many in your party?"
        if self.sys["responseState"] == "anything_else":
            return " \nWaiter: Can I get you something else before I put your order in?"
        return ""

    def user_ordered_veg(self):
        veggies = list(all_instances(self, "veggie"))
        if "ordered" in self.rel.keys():
            for i in self.rel["ordered"]:
                if i[0] == "user":
                    if i[1] in veggies:
                        return True
        return False

    def user_wants(self, wanted):
        # if wanted not in self.get_entities():
        #   return [RespondOperation("Sorry, we don't have that.")]

        if wanted[0] == "{":
            wanted_dict = json.loads(wanted)
            if wanted_dict["structure"] == "noun_for":
                if wanted_dict["noun"] == "table1":
                    if "at" in self.rel.keys():
                        if ("user", "table") in self.rel["at"]:
                            return [RespondOperation("Um... You're at a table." + self.get_reprompt()),
                                    ResponseStateOp("anything_else")]
                    if wanted_dict["for_count"] > 2:
                        return [RespondOperation("Host: Sorry, we don't have a table with that many seats")]
                    if wanted_dict["for_count"] < 2:
                        return [RespondOperation("Johnny: Hey! That's not enough seats!")]
                    if wanted_dict["for_count"] == 2:
                        return (RespondOperation(
                            "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. "
                            "A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?"),
                                AddRelOp(("user", "at", "table")), ResponseStateOp("something_to_eat"))

                else:
                    wanted = wanted_dict["noun"]

        for i in all_instances_and_spec(self, "food"):
            if i == wanted:
                if "at" in self.rel.keys():
                    if ("user", "table") in self.rel["at"]:
                        if "ordered" in self.rel.keys():
                            if ("user", wanted) in self.rel["ordered"]:
                                return [RespondOperation(
                                    "Sorry, you got the last one of those. We don't have any more. Can I get you something else?"),
                                    ResponseStateOp("anything_else")]
                        assert(wanted in self.sys["prices"])
                        if self.sys["prices"][wanted] + self.bill_total() > 15:
                            return [RespondOperation("Son: Wait, we already spent $" + str(self.bill_total()) + " so if we get that, we won't be able to pay for it with $15." + self.get_reprompt())]

                        return [RespondOperation("Excellent Choice! Can I get you anything else?"),
                                AddRelOp(("user", "ordered", wanted)), AddBillOp(wanted),
                                ResponseStateOp("anything_else")]

                return [RespondOperation("Sorry, you must be seated to order")]

        for i in all_instances_and_spec(self, "table"):
            if i == wanted:
                if "at" in self.rel.keys():
                    if ("user", "table") in self.rel["at"]:
                        return [RespondOperation("Um... You're at a table." + self.get_reprompt())]
                return [RespondOperation("How many in your party?"), ResponseStateOp("anticipate_party_size")]
        for i in all_instances_and_spec(self, "menu"):
            if i == wanted:
                if "at" in self.rel.keys():
                    if ("user", "table") in self.rel["at"]:
                        if ("user", "menu1") not in self.rel["have"]:
                            return [AddRelOp(("user", "have", "menu1")), RespondOperation(
                                "Waiter: Oh, I forgot to give you the menu? Here it is. The waiter walks off.\nSteak -- $5\nRoasted Chicken -- $7\nGrilled Salmon -- $12\nYou read the menu and then the waiter returns.\nWaiter: What can I get you?"),
                                    ResponseStateOp("anticipate_dish")]
                        else:
                            return [RespondOperation(
                                "Oh, I already gave you a menu. You look and see that there is a menu in front of you.\nSteak -- $5\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n" + self.get_reprompt())]
                return [RespondOperation("Sorry, you must be seated to order")]

        if wanted == "bill1":
            for i in self.rel["valueOf"]:
                if i[1] == "bill1":
                    total = i[0]
                    if self.sys["responseState"] == "done_ordering":
                        return [RespondOperation(
                            "Your total is " + str(total) + " dollars. Would you like to pay by cash or card?"),
                            ResponseStateOp("way_to_pay")]
                    else:
                        return [RespondOperation("But... you haven't got any food yet!" + self.get_reprompt())]

        return [RespondOperation("Sorry, I can't get that for you at the moment.")]

    def user_wants_to_see(self, wanted):
        if wanted == "menu1":
            return self.user_wants("menu1")
        elif wanted == "table1":
            return [RespondOperation("All our tables are nice. Trust me on this one" + self.get_reprompt())]
        else:
            return [RespondOperation("Sorry, I can't show you that." + self.get_reprompt())]

    def no(self):
        if self.sys["responseState"] == "anything_else":
            if not self.user_ordered_veg():
                return [RespondOperation(
                    "Son: Dad! I’m vegetarian, remember?? Why did you only order meat? \nMaybe they have some other dishes that aren’t on the menu… You tell the waiter to restart your order.\nWaiter: Ok, can I get you something else to eat?"),
                    ResponseStateOp("something_to_eat"), ResetOrderAndBillOp()]

            items = [i for (x, i) in self.rel["ordered"]]
            for i in self.rel["have"]:
                if i[0] == "user":
                    if i[1] in items:
                        items.remove(i[1])

            item_str = " ".join(items)

            for i in items:
                self.add_rel("user", "have", i)

            return [RespondOperation(
                "Ok, I'll be right back with your meal.\nA few minutes go by and the robot returns with " + item_str + ".\nThe food is good, but nothing extraordinary."),
                ResponseStateOp("done_ordering")]
        elif self.sys["responseState"] == "something_to_eat":
            return [RespondOperation(
                "Well if you aren't going to order anything, you'll have to leave the restaurant, so I'll ask you again: can I get you something to eat?")]
        else:
            return [RespondOperation("Hmm. I didn't understand what you said." + self.get_reprompt())]

    def yes(self):
        if self.sys["responseState"] in ["anything_else", "something_to_eat"]:
            return [RespondOperation("Ok, what?"), ResponseStateOp("anticipate_dish")]
        else:
            return [RespondOperation("Hmm. I didn't understand what you said." + self.get_reprompt())]

    def unknown(self, x):
        if self.sys["responseState"] == "way_to_pay":
            if x in ["cash", "card", "card, credit"]:
                return [RespondOperation("Ah. Perfect! Have a great rest of your day.")]
            else:
                return [RespondOperation("Hmm. I didn't understand what you said." + self.get_reprompt())]
        elif self.sys["responseState"] in ["anticipate_dish", "anything_else", "initial"]:
            if x in self.get_entities():
                return self.handle_world_event(["user_wants", x])
            else:
                return [RespondOperation("Sorry, we don't have that")]
        elif self.sys["responseState"] in ["anticipate_party_size"]:
            if isinstance(x, Measurement):
                return self.handle_world_event(["user_wants", json.dumps(
                    {"structure": "noun_for", "noun": "table1", "for_count": x.count})])
            else:
                return [RespondOperation("Hmm. I didn't understand what you said." + self.get_reprompt())]
        else:
            return [RespondOperation("Hmm. I didn't understand what you said." + self.get_reprompt())]

    def party_size(self, args):

        x = args[1]
        if isinstance(x, Measurement):
            self.sys["responseState"] = "something_to_eat"
            return self.handle_world_event(["user_wants", json.dumps(
                {"structure": "noun_for", "noun": "table1", "for_count": x.count})])
        else:
            return [RespondOperation("Sorry, I didn't catch that. How many in your party?")]

    def handle_world_event(self, args):
        if self.sys["responseState"] == "anticipate_party_size":
            return self.party_size(args)
        if args[0] == "user_wants":
            return self.user_wants(args[1])
        elif args[0] == "user_wants_to_see":
            return self.user_wants_to_see(args[1])
        elif args[0] == "no":
            return self.no()
        elif args[0] == "yes":
            return self.yes()
        elif args[0] == "unknown":
            return self.unknown(args[1])
        elif args[0] == "user_wants_to_sit":
            return self.user_wants("table1")
