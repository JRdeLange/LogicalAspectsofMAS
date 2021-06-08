from mlsolver.kripke import World, KripkeStructure
from mlsolver.formula import *
from mlsolver.formula import Atom, And, Not, Or, Box_a, Box_star
from itertools import permutations
import random
import collections

"""
ABOUT:
This program should simulate the logic of the card game the crew.
The goals is to be able to do this for at least 3 players and a deck of at least 6 cards.
DONE:
- Implemented initial kripke model generation
TODO:
- Figure out how to do logic with such a large model
- Once that is done, make user interface to allow moves that influence the Kripke model 
"""


def deal_cards(deck, number_of_agents):
    random.shuffle(deck)
    return [deck[agent::number_of_agents] for agent in range(number_of_agents)]

def same_elements(list1, list2):
    return collections.Counter(list1) == collections.Counter(list2)

def initialise_worlds(agents, deck, hand_cards):
    """
    Generates the starting worlds of the Kripke model based on the agents and deck
    First we make a list of all possible permutations of the deck
    For each permutation we then create a world.
    We get the name by joining the values of the cards into a single string.
    We then get the truth values of the world by going over the cards in the world and marking:
    - The first third of the cards as belonging to agent a
    - The second third of the cards as belonging to agent b
    - The final third of the cards as belonging to agent c
    We then use the world name and truth values to add a new world to the initial worlds
    """
    worlds = []
    possible_worlds = list(permutations(deck, len(deck)))
    accessible_worlds = []
    nr_of_agents = len(hand_cards)
    nr_of_cards_in_hand = len(hand_cards[0])

    # check if for at least one agent a 'possible world' is accessible, if not don't include it in the kripke model
    # accessible becomes true if for at least one agent all its cards in his hand match another state
    for world in possible_worlds:
        accessible = False
        for agent in range(nr_of_agents):
            same_hand = True
            for card in range(nr_of_cards_in_hand):
                if not world[(agent) * nr_of_cards_in_hand + card] == hand_cards[agent][card]:
                    same_hand = False
            # if all cards in this agents hand match, then this world is accessible from the real world
            if same_hand:
                accessible = True
        if accessible:
            accessible_worlds.append(world)



    for world in accessible_worlds:
        world_name = ''.join(str(card) for card in world)
        world_truth_values = {}
        for card in world:
            if world.index(card) < len(deck) / 3:
                world_truth_values["a:" + str(card)] = True
            elif world.index(card) < len(deck) / 1.5:
                world_truth_values["b:" + str(card)] = True

    #print("Possible worlds: ", possible_worlds)
    #print("Accessible worlds: ", accessible_worlds)

            else:
                world_truth_values["c:" + str(card)] = True
        
        duplicate = False
        for checker in worlds:
            curr_world = list(world_truth_values.keys())
            checker = list(checker.assignment.keys())
            if same_elements(curr_world, checker):
                duplicate = True
        if not duplicate:
            worlds.append(World(world_name, world_truth_values))

    return worlds


def initialise_relations(agents, deck, worlds):
    """
    Generates the starting relations of the Kripke model based on the starting worlds
    We first declare three empty sets for the agents.
    We then go over each world combination for each agent.
    We then add a relation for the agent for each world combination where the agent has the same cards.
    (which is the starting knowledge of each agent, as each agent knows their own hand)
    """
    relations = {
        "a": set(),
        "b": set(),
        "c": set()
    }

    for agent in agents:
        for origin_world in worlds:
            for destination_world in worlds:
                if agent == "a" and origin_world.name[:int(len(deck) / 3)] == destination_world.name[
                                                                              :int(len(deck) / 3)]:
                    relations["a"].add((origin_world.name, destination_world.name))
                elif agent == "b" and origin_world.name[
                                      int(len(deck) / 3):int(len(deck) / 1.5)] == destination_world.name[
                                                                                  int(len(deck) / 3):int(
                                                                                          len(deck) / 1.5)]:
                    relations["b"].add((origin_world.name, destination_world.name))
                elif agent == "c" and origin_world.name[int(len(deck) / 1.5):] == destination_world.name[
                                                                                  int(len(deck) / 1.5):]:
                    relations["c"].add((origin_world.name, destination_world.name))

    return relations


def initialise_kripke_model(agents, deck, hand_cards):
    """
    Generates the starting kripke model based on the agents and deck used
    We first generate the starting worlds.
    We then generate the starting relations of those worlds.
    We then combine these into a kripke structure
    """

    worlds = initialise_worlds(agents, deck, hand_cards)

    relations = initialise_relations(agents, deck, worlds)

    ks = KripkeStructure(worlds, relations)

    print("Amount of worlds: ", len(worlds))
    print("Amount of relations: ", len(relations["a"]) + len(relations["b"]) + len(relations["c"]))

    return ks


# W.I.P.
def The_Crew_game(agents, deck, hand_cards, ks):
    while True:
        for agent in agents:
            print("It is the turn of agent " + agent)
            print("hand: " + str(hand_cards[agents.index(agent)]))
            action = input("Which action do you wish to perform?(type \"exit\" to quit)\n")
            if action == "exit":
                break
            else:
                pass
        if action == "exit":
            break


##### MAIN #####
"""
We initialise the kripke model based on the number of agents and "cards" in the deck
Cards can be defined as colour1 (1,2), colour2(3,4), trump cards(5,6).
"""
agents = ["a", "b", "c"]
# deck = [1, 2, 3]
deck = [1, 2, 3, 4, 5, 6]

hand_a, hand_b, hand_c = deal_cards(deck, len(agents))
hand_cards = [hand_a, hand_b, hand_c]
print("Handcards: ", hand_cards)

ks = initialise_kripke_model(agents, deck, hand_cards)

print("Kripke structure: ", ks)

t1=['a:2', 'a:4', 'b:1', 'b:6', 'c:5', 'c:3']
t2=['a:2', 'a:4', 'b:1', 'b:6', 'c:3', 'c:5']

# The_Crew_game(agents, deck, hand_cards, ks)

"""
Start the game
Work In Progress
"""
# The_Crew_game(agents, deck, ks)


"""
print statements for looking inside of the kripke model
"""
# for world in ks.worlds:
#   print(world.name)
# print(ks.relations)
# print(ks)
