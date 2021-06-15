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
				# TODO: Is hieronder 0 of agent handiger? Het zou altijd dezelfde lengte moeten hebben maar weet niet wat jullie netter vinden
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
		to_be_removed = []
		# If a fact is not in a world, queue it up fo removal
		for fact in fact_list:
			if not fact in world_facts:
				to_be_removed.append(fact)
		# And then remove all of them from the fact list
		for fact in to_be_removed:
			fact_list.remove(fact)
	return fact_list

def generate_mission(agents, deck):
	"""
	Randomly selects an agent and a card
	The mission indicates which agent should end up with which card
	"""
	mission_agent = random.choice(agents)
	mission_card = random.choice(deck)
	return [mission_agent, mission_card]

def determine_winner(trick, deck):
	"""
	This function determines the winner of a trick
	It does this by looping three times (based on number of players)
	Each loop it looks at one of the players and which card they played this trick
	Then it selects either the highest card played of the trick suit
	Or (if trump cards were played) the highest trump card
	"""
	winning_card = None
	winning_player = None

	for index in range(3):
		if winning_card == None:
			winning_card = trick["cards_in_trick"][index]
			winning_player = trick["player_order"][index]
		elif trick["trick_suit"] != "trump" and card_suit(trick["cards_in_trick"][index], deck) == "trump":
			winning_card = trick["cards_in_trick"][index]
			winning_player = trick["player_order"][index]
		elif trick["cards_in_trick"][index] > winning_card and trick["trick_suit"] == card_suit(trick["cards_in_trick"][index], deck):
			winning_card = trick["cards_in_trick"][index]
			winning_player = trick["player_order"][index]

	return winning_player

def set_player_order(starting_agent, trick):
	"""
	This function returns the new agent order based on which agent should be the starting agent
	"""
	#TODO maybe find a more elegant way to do this?

	if starting_agent == "a":
		trick["player_order"] = ["a", "b", "c"]
	elif starting_agent == "b":
		trick["player_order"] = ["b", "c", "a"]
	elif starting_agent == "c":
		trick["player_order"] = ["c", "a", "b"]

	return trick["player_order"]

def end_trick(trick, game):
	"""
	This function ends the current trick
	This means that it determines who won the trick
	Then adds the cards of this trick to the winners cards_won pile
	Then it resets the values of the trick, making the winning agent the first agent to play
	"""
	trick_suit = trick["trick_suit"]
	winning_agent = determine_winner(trick, game["deck"])

	print("The suit of this trick was", trick_suit, ". Player", winning_agent, "played the winning card and has thus won this trick.")
	print("Player", winning_agent, "will now start the new trick.")

	winning_agent_index = game["agents"].index(winning_agent)
	game["cards_won"][winning_agent_index] += trick["cards_in_trick"]

	trick["player_order"] = set_player_order(winning_agent, trick)
	trick["cards_in_trick"] = []
	trick["nr_of_cards_in_trick"] = 0
	trick["trick_suit"] = None
	return trick, game

def play_card(agents, player, card, ks):
	"""
	This function updates the kripke model based on the card that has been revealed
	"""
	#TODO merge or differentiate this function from communicate_card()
	agent_card = agents[player] + ":" + card
	ks = ks.short_solve(Atom(agent_card))
	print("The new kripke model:\n")
	print(ks)
	return ks

def communicate_card(agents, player, card, ks):
	"""
	This function updates the kripke model based on the card that has been revealed
	"""
	#TODO merge or differentiate this function from play_card()
	agent_card = agents[player] + ":" + card
	ks = ks.short_solve(Atom(agent_card))
	print("The new kripke model:\n")
	print(ks)
	return ks

def card_suit(card, deck):
	"""
	Returns which of the three suits the card has
	It does this by looking if the card is from the first, second or third part of the deck
	"""
	if (card / len(deck)) < 0.34:
		return "color 1"
	elif (card / len(deck)) < 0.67:
		return "color 2"
	return "trump"

def ask_for_communicating_agent(agents):
	"""
	This function querries the user to say which agent they want to have communicate one of their cards
	"""
	agent = input("Which player would like to communicate a card?\n")
	while agent not in agents:
		print(str(agent), "is not a player, please try again. You can choose players:" ,agents)
		agent = input("Which player would like to communicate a card?\n")
	return agent

def mission_passed(game):
	"""
	This function checks if the mission has been accomplished
	It does this by seeing if the mission agent has the mission card in their cards_won pile
	"""
	Mission_agent_index = game["agents"].index(game["mission"][0])

	for card in game["cards_won"][Mission_agent_index]:
		if card == game["mission"][1]:
			return True

	return False

#WIP
def game_loop(agents, hand_cards, deck, ks):
	"""
	This function simulates the turns of each agent
	"""
	# TODO: Some cleaning up
	# TODO: Implement some way to limit how many communications the agents can do
	# TODO: Turn trick and game into a class (possibly merging them into a single game class)
	trick = {	"trick_suit" : None,
				"nr_of_cards_in_trick" : 0,
				"cards_in_trick" : [],
				"player_order" : agents}

	game = {	"kripke_model" : ks,
				"agents" : agents,
				"deck" : deck,
				"mission" : generate_mission(agents, deck),
				"hand_cards" : hand_cards,
				"cards_won" : [[] for i in range(3)]}

	print("Today's mission is", game["mission"])

	mission_ongoing = True
	current_player = 0

	while mission_ongoing:
		current_player_game_index = agents.index(trick["player_order"][current_player])

		print("It is the turn of player ", trick["player_order"][current_player])
		print("current common_knowledge:", get_common_knowledge(ks))
		action = input("Which action do you wish to perform? (type \"play\" to play a card, \"com\" to communicate a card or \"quit\" to quit)\n")

		if action == "play":
			print("player ", trick["player_order"][current_player], " has the following cards in their hand:", hand_cards[current_player_game_index])
			move = input("What card is played by " + str(trick["player_order"][current_player]) + "?\n")
			print("Player ", trick["player_order"][current_player], " played card ", move)
			ks = play_card(trick["player_order"], current_player, move, ks)

			if trick["nr_of_cards_in_trick"] == 0:
				trick["trick_suit"] = card_suit(int(move), deck)

			hand_cards[current_player].remove(int(move))
			trick["cards_in_trick"] += [int(move)]
			trick["nr_of_cards_in_trick"] += 1
			current_player = (current_player + 1) % 3

		elif action == "com":
			communicating_agent = ask_for_communicating_agent(agents)
			print("player ", communicating_agent, " has the following cards in their hand:", hand_cards[agents.index(communicating_agent)])
			communicated_card = input("What card would " + str(communicating_agent) + " like to communicate? (type \"cancel\" to cancel)\n")

			if communicated_card != "cancel":
				print(communicating_agent + " communicated card ", communicated_card)
				ks = communicate_card(trick["player_order"], trick["player_order"].index(communicating_agent), communicated_card, ks)

		elif action == "quit":
			print("See you next time!")
			break

		else:
			print("Invalid action, please retry.\n")

		if trick["nr_of_cards_in_trick"] == len(agents):
			trick, game = end_trick(trick, game)
			if mission_passed(game):
				print("Congratulations, you have passed your mission!")
				mission_ongoing = False
			elif not hand_cards[current_player_game_index]:
				print("You have failed your mission, how unfortunate.")
				mission_ongoing = False

def The_Crew_game():
	"""
	We initialise the kripke model based on the number of agents, "cards" in the deck and the cards in the hands of the agents
	Cards can be defined as colour1 (1,2), colour2(3,4), trump cards(5,6).
	"""
	agents = ["a","b","c"]
	deck = [1,2,3,4,5,6]

	hand_a, hand_b, hand_c = deal_cards(deck, len(agents))
	hand_cards = [hand_a, hand_b, hand_c]

	ks = initialise_kripke_model(agents, deck, hand_cards)

	game_loop(agents, hand_cards, deck, ks)
	
	#game_loop(agents, hand_cards, ks)


##### MAIN #####
"""
Start the game
"""
The_Crew_game()

