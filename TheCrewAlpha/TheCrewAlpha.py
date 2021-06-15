from kripke import World, KripkeStructure
from mlsolver.formula import *
from mlsolver.formula import Atom, And, Not, Or, Box_a, Box_star
from itertools import permutations
import random
import collections

"""
ABOUT:
This program should simulate the logic of the card game the crew.
The goals is to be able to do this for at least 3 players and a deck of at least 6 cards.
"""

def deal_cards (deck, number_of_agents):
	"""
	This function randomly divides the items of the deck over the number of agents
	"""
	random.shuffle(deck)
	return [deck[agent::number_of_agents] for agent in range(number_of_agents)]

def same_elements(list1, list2):
    return collections.Counter(list1) == collections.Counter(list2)

def initialise_worlds(agents, deck, hand_cards):
	"""
	Generates the starting worlds of the Kripke model based on the agents and deck
	First we make a list of all possible permutations of the deck
	From these permutations we then gather all of the ones that are accessible given the current hand cards.
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
				# TODO: Is hieronder 0 of agent handiger? Het zou altijd dezelfde lengte moeten hebben maar weet niet wat jullie netter vinden
				if not world[(agent) * nr_of_cards_in_hand + card] == hand_cards[agent][card]:
					same_hand = False
			# if all cards in this agents hand match, then this world is accessible from the real world
			if same_hand:
				accessible = True
		if accessible:
			accessible_worlds.append(world)
	"""
	For each permutation we then create a world.
	We get the name by joining the values of the cards into a single string.
	We then get the truth values of the world by going over the cards in the world and marking:
	- The first third of the cards as belonging to agent a
	- The second third of the cards as belonging to agent b
	- The final third of the cards as belonging to agent c
	After that we check the world truth values against those of the other worlds.
	If the world does not exist yet we add it to the worlds list
	"""
	for world in accessible_worlds:
		world_name = ''.join(str(card) for card in world)
		world_truth_values = {}
		for card in world:
			if world.index(card) < len(deck) / 3:
				world_truth_values["a:" + str(card)] = True
			elif world.index(card) < len(deck) / 1.5:
				world_truth_values["b:" + str(card)] = True
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
		"a":set(),
		"b":set(),
		"c":set()
	}

	for agent in agents:
		for origin_world in worlds:
			for destination_world in worlds:
				if agent == "a" and origin_world.name[:int(len(deck)/3)] == destination_world.name[:int(len(deck)/3)]:
					relations["a"].add((origin_world.name,destination_world.name))
				elif agent == "b" and origin_world.name[int(len(deck)/3):int(len(deck)/1.5)] == destination_world.name[int(len(deck)/3):int(len(deck)/1.5)]:
					relations["b"].add((origin_world.name,destination_world.name))
				elif agent == "c" and origin_world.name[int(len(deck)/1.5):] == destination_world.name[int(len(deck)/1.5):]:
					relations["c"].add((origin_world.name,destination_world.name))

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

	print("Worlds: ", len(worlds))
	print("Relations: ", (len(relations["a"]) + len(relations["b"]) + len(relations["c"])))

	ks = KripkeStructure(worlds, relations)

	return ks

def get_list_of_facts(ks):
	"""
	Creates a complete list of all facts present in the model currently
	"""
	fact_list = list()
	# Go through all worlds and make a list of all existing facts
	for world in ks.worlds:
		fact_list += list(world.assignment.keys())
	# Remove duplicates by making it a dict and then converting back to a list
	return list(dict.fromkeys(fact_list))


def get_common_knowledge(ks):
	"""
	Generates a complete list of all the common knowlegde present in the model
	"""
	# First collect all facts
	fact_list = get_list_of_facts(ks)
	# Then loop through all worlds
	for world in ks.worlds:
		world_facts = list(world.assignment.keys())
		to_be_removed = set()
		# If a fact is not in a world, queue it up fo removal
		for fact in fact_list:
			if not fact in world_facts:
				to_be_removed.append(fact)
		# And then remove all of them from the fact list
		for fact in to_be_removed:
			fact_list.remove(fact)
	return fact_list

#WIP
def game_loop(agents, hand_cards, ks):
	"""
	This function simulates the turns of each agent
	"""
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

def The_Crew_game():
	"""
	We initialise the kripke model based on the number of agents, "cards" in the deck and the cards in the hands of the agents
	Cards can be defined as colour1 (1,2), colour2(3,4), trump cards(5,6).
	"""
	agents = ["a","b","c"]
	deck = [1,2,3]

	hand_a, hand_b, hand_c = deal_cards(deck, len(agents))
	hand_cards = [hand_a, hand_b, hand_c]

	ks = initialise_kripke_model(agents, deck, hand_cards)

	ks = ks.short_solve(And(Atom("a:1"), Atom("b:2")))

	print(get_common_knowledge(ks))
	
	#game_loop(agents, hand_cards, ks)


##### MAIN #####
"""
Start the game
"""
The_Crew_game()

