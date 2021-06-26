from mlsolver.kripke import World, KripkeStructure
from mlsolver.formula import *
from itertools import permutations
import random
import collections

from GameManager import GameManager

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

def generate_accessible_worlds(possible_worlds, hand_cards):
	"""
	Generates the worlds accessible given the current hand
	"""
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

	return accessible_worlds

def same_elements(list1, list2):
	return collections.Counter(list1) == collections.Counter(list2)

def generate_worlds(accessible_worlds, deck):
	"""
	For each permutation we create a world.
	We get the name by joining the values of the cards into a single string.
	We then get the truth values of the world by going over the cards in the world and marking:
	- The first third of the cards as belonging to agent a
	- The second third of the cards as belonging to agent b
	- The final third of the cards as belonging to agent c
	After that we check the world truth values against those of the other worlds.
	If the world does not exist yet we add it to the worlds list
	"""
	worlds = []

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


def initialise_worlds(agents, deck, hand_cards):
	"""
	Generates the starting worlds of the Kripke model based on the agents and deck
	First we make a list of all possible permutations of the deck
	From these permutations we then gather all of the ones that are accessible given the current hand cards.
	Finally we generate the worlds in the way needed to use them later
	"""
	possible_worlds = list(permutations(deck, len(deck)))
	accessible_worlds = generate_accessible_worlds(possible_worlds, hand_cards)
	worlds = generate_worlds(accessible_worlds, deck)
	
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

def generate_mission(agents, deck):
	"""
	Randomly selects an agent and a card
	The mission indicates which agent should end up with which card
	"""
	mission_agent = random.choice(agents)
	mission_card = random.choice(deck)
	while (mission_card / len(deck)) > 0.67:
		mission_card = random.choice(deck)
	return [mission_agent, mission_card]

def print_rules():
	"""
	A function which prints the rules of the game and gives a short explanation of what this program does.
	"""
	print("")
	print("Rules and Explanation:")
	print("In this version of The Crew, the players work together to make sure a specific player gets a specific card.")
	print("The cards are numbered 1 to 6. Cards 1 and 2 are of suit 1, cards 3 and 4 are of suit 2 and cards 5 and 6 are trump cards.")
	print("")
	print("The game is played in rounds called tricks. In a trick each player plays one card. The first card played determines the suit of the trick.")
	print("Subsequent cards have to be of the same suit, unless a player does not have any cards of that suit.")
	print("At the end of a trick, the winner is the player that played the highest card of the trick suit.")
	print("If one or more trump cards were played the winner is instead the player that played the highest trump card.")
	print("The winner of a trick gets the cards played during that trick in their won cards pile. This is how the mission can be accomplished.")
	print("")
	print("At any moment a player can choose to communicate one of the cards in their hand to the other palyers. Each player can only do this once during the game.")
	print("This program assists by keeping track of the cards communicated and showing the player which facts everyone should be aware of.")
	print("During play the program will also tell the player which tricks they should know can happen during this round.")
	print("It will also say if any of those will result in accomplishing the mission.")
	print("")
	print("minor note: each turn the hand cards of the palyers are printed.")
	print("This is to make it easier for the user to create specific situations and this is not considered to be known by the individual players.")
	print("")
	print("That was the explanation, good luck and have fun.")
	print("")
	input("pres enter to continue with the game.")

def game_loop(game):
	"""
	This function simulates the turns of each agent
	"""	
	mission_ongoing = True

	while mission_ongoing:



		print("Today's mission is for player " + game.mission[0] + " to obtain card number", game.mission[1])
		print("")

		print("The hands are currently as follows:")
		for i in range(3):
			print("    Hand of player " + game.agents[i] + ":", game.hand_cards[i])
		print("")

		game.is_game_winnable()

		print("This is the current common knowledge:")
		for fact in sorted(game.get_common_knowledge()):
			if fact[0] != "~":
				print("    Player " + fact[0] + " was dealt card number", fact[2])
			else:
				print("    Player " + fact[1] + " was not dealt card number", fact[3])
		print("")

		print("The current trick has these cards in it:")
		print(game.current_trick.get_cards())
		print("")

		print("It is the turn of player " + game.get_current_player_name())
		print("")

		action = input("Which action do you wish to perform? (type \"play\" to play a card, \"com\" to communicate a card or \"quit\" to quit)\n")
		print("")

		if action == "play":
			game.play_action()

		elif action == "com":
			game.communicate_card()

		elif action == "quit":
			print("See you next time!")
			break

		elif action == "rules":
			print_rules()

		else:
			print("Invalid action, please retry.\n")

		mission_ongoing = game.check_end_of_trick()

		print("")
		print("+----------+----------+----------+")
		print("")


def The_Crew_game():
	"""
	We initialise the kripke model based on the number of agents, "cards" in the deck and the cards in the hands of the agents
	Cards can be defined as suit 1 (1,2), suit 2 (3,4), trump suit(5,6).
	"""
	print("")
	print("Initializing Kripke model, this may take a few seconds")

	agents = ["a","b","c"]
	deck = [1,2,3,4,5,6]
	communications_per_agent = 1

	hand_a, hand_b, hand_c = deal_cards(deck, len(agents))
	hand_cards = [hand_a, hand_b, hand_c]

	ks = initialise_kripke_model(agents, deck, hand_cards)
	mission = generate_mission(agents, deck)

	real_world = []

	for hand in hand_cards:
		for card in hand:
			real_world.append(str(card))

	real_world = "".join(real_world)
	
	game = GameManager(ks, agents, deck, hand_cards, mission, communications_per_agent, real_world)
	
	print("""
    +--------------------+
    |     Welcome to     |
    |                    |
    |      THE CREW      |
    +--------------------+
""")
	print("For rules and explanation, type: \"rules\"")
	print("")

	game_loop(game)

##### MAIN #####
"""
Start the game
"""
The_Crew_game()

