from mlsolver.kripke import World, KripkeStructure
from mlsolver.formula import *
from Trick import Trick
import time

class GameManager:
	"""docstring for GameManager"""
	def __init__(self, kripke_model, agents, deck, hand_cards, mission, communications_per_agent, real_world):
		super(GameManager, self).__init__()

		self.kripke_model = kripke_model
		self.agents = agents
		self.deck = deck
		
		self.mission = mission
		self.hand_cards = hand_cards
		self.cards_won = [[] for i in range(3)]
		self.nr_of_communications = [communications_per_agent for i in range(len(agents))]

		self.current_trick = Trick()
		self.player_order = agents
		self.current_player = 0

		self.set_player_order(agents[self.get_commander()])
		self.kripke_model_single_card_update(self.player_order[self.current_player], str(6))

		self.real_world = real_world

	def world_connected(self, model_worlds, model_relations, test_world):
		"""
		Checks a worlds against a list of worlds and a list of relations
		If the worlds is connected to any world in the list of worlds based
		on the list of relation, return True 
		"""
		for agent in model_relations:
			for relation in model_relations[agent]:
				for world in model_worlds:
					if test_world in relation and world.name in relation:
						return True
		return False


	def generate_two_agent_model(self, kripke_model, agent_1, agent_2, source_world):
		"""
		Generates a kripke model that only has the worlds and relations of two of its agents
		connected to a source world. 
		This makes sure a connected graph is created and due to the fact that we know each agent
		considers the real world possible, will make sure that only the knowledge of the third
		agent is lost, if the real world is used as source world.
		"""
		two_agent_model_relations = {
					agent_1: kripke_model.relations[agent_1].copy(),
					agent_2: kripke_model.relations[agent_2].copy()
					}

		two_agent_model_worlds = []

		for i in range(len(kripke_model.worlds)):
			for world in kripke_model.worlds.copy():
				if not world in two_agent_model_worlds:
					if world.name == source_world:
						two_agent_model_worlds.append(World(world.name, world.assignment))
					elif self.world_connected(two_agent_model_worlds, two_agent_model_relations, world.name):
						two_agent_model_worlds.append(World(world.name, world.assignment))

		two_agent_model = KripkeStructure(kripke_model.worlds.copy(),two_agent_model_relations)

		return(KripkeStructure(two_agent_model_worlds, two_agent_model_relations))

	def check_if_trick_valid(self, trick):
		cards = trick.get_cards();
		suit = trick.get_suit();

		if self.get_card_suit(cards[1]) != suit and self.get_card_suit(cards[1]) != "trump":
			for card in self.get_agent_hand(self.player_order[1]):
				if self.get_card_suit(card) == suit:
					return False

		if self.get_card_suit(cards[2]) != suit and self.get_card_suit(cards[2]) != "trump":
			for card in self.get_agent_hand(self.player_order[2]):
				if self.get_card_suit(card) == suit:
					return False

		return True


	def is_game_winnable(self):
		"""
		Generates possible tricks in the current scenario.
		"""
		# Determine which players yet to play this trick
		#print(self.get_positive_common_knowledge(self.generate_two_agent_model(self.kripke_model, "b", "c", self.real_world)))
		not_played_yet = self.player_order[self.current_trick.get_nr_of_cards():]
		cards_played_this_trick = self.current_trick.get_cards()

		# Collect all played cards
		played_cards = self.current_trick.get_cards()
		for player in self.cards_won:
			for card in player:
				played_cards += [card]

		# Determine the cards each player has that are common knowledge
		playable_cards = {"a" : [], "b" : [], "c" : []}
		common_knowledge = []

		if len(not_played_yet) == 3:
			# If no card has been played yet in the current trick we get common knowledge from the complete model
			common_knowledge = self.get_positive_common_knowledge(self.kripke_model)
		elif len(not_played_yet) == 2:
			# If one card has been played, the knowledge of that player no longer matters, hence we use the CK from a two agent model
			model = self.generate_two_agent_model(self.kripke_model, not_played_yet[0], not_played_yet[1], self.real_world)
			common_knowledge = self.get_positive_common_knowledge(model)
			# The first player already played, so their card is already set.
			playable_cards[self.player_order[0]] = self.current_trick.get_cards()
		elif len(not_played_yet) == 1:
			# If two cards have been played no knowledge matters anymore, only all the cards in the hand of the last player do
			playable_cards[self.player_order[0]] = [self.current_trick.get_cards()[0]]
			playable_cards[self.player_order[1]] = [self.current_trick.get_cards()[1]]
			playable_cards[not_played_yet[0]] = self.get_agent_hand(not_played_yet[0])

		# For all players who have not played yet we add the cards that are common knowledge among those yet to play to their playable card list.
		for fact in common_knowledge:
			card = int(fact[2:])
			player = fact[0]
			if not card in played_cards and player in not_played_yet:
				playable_cards[player] += [card]
		
		#print(playable_cards)

		# Put all the pieces together and actually generate the tricks
		tricks = []
		for card_1 in playable_cards[self.player_order[0]]:
			for card_2 in playable_cards[self.player_order[1]]:
				for card_3 in playable_cards[self.player_order[2]]:
					cards = [card_1, card_2, card_3]
					first_player = self.player_order[0]
					suit = self.get_card_suit(cards[self.player_order.index(first_player)])
					trick = Trick(suit, cards)
					if self.check_if_trick_valid(trick):
						tricks += [trick]

		if len(tricks) > 0:
			print("Valid tricks that all players yet to play know can be played now:")
			for trick in tricks:
				print("    " + str(trick.get_cards()))

		# If a trick is winning, print it
		for trick in tricks:
			winning_agent = self.determine_winner(trick)
			if self.mission[0] == winning_agent and self.mission[1] in trick.get_cards():
				print("Of these, a winning trick is:", trick.get_cards())

		if len(tricks) > 0: print("")

	def get_current_player_name(self):
		"""
		Returns the name of the current player
		"""
		return str(self.player_order[self.current_player])

	def get_current_player_hand(self):
		"""
		Returns the hand cards of the current player
		"""
		hand_index = self.agents.index(self.get_current_player_name())
		return self.hand_cards[hand_index]

	def get_commander(self):
		"""
		Returns the commander of a game; the player who has the highest trump-card
		"""
		for player in range(len(self.hand_cards)):
			for card in range(len(self.hand_cards[player])):
				if self.hand_cards[player][card] == 6:
					return player

	def kripke_model_single_card_update(self, agent, card):
		"""
		Updates the kripke model based on a specific card becoming common knowledge
		"""
		agent_card = agent + ":" + card
		self.kripke_model = self.kripke_model.solve(Atom(agent_card))

	def get_card_suit(self, card):
		"""
		Returns which of the three suits the card has
		It does this by looking if the card is from the first, second or third part of the deck
		"""
		if (card / len(self.deck)) < 0.34:
			return "suit 1"
		elif (card / len(self.deck)) < 0.67:
			return "suit 2"
		return "trump"

	def play_action(self):
		"""
		This function lets the current agent play a card
		We first query the agent for which card they want to play from their hand
		We then update the kripke model with that card.
		If this is the first card of the trick it sets the trick color.
		Finally we remove the card from the current player's hand and add it to the cards in the current trick.
		"""
		player_hand = self.get_current_player_hand()
		has_trick_suit_card = False

		for card in player_hand:
			if self.get_card_suit(card) == self.current_trick.get_suit():
				has_trick_suit_card = True

		print("Player " + self.get_current_player_name() + " has the following cards in their hand:", player_hand)
		if self.current_trick.get_suit() != None: print("The current trick suit is", self.current_trick.get_suit())
		move = input("What card is played by player " + self.get_current_player_name() + "?\n")

		while (not move.isnumeric()) or (has_trick_suit_card and self.get_card_suit(int(move)) != "trump" and self.get_card_suit(int(move)) != self.current_trick.get_suit()) or int(move) not in player_hand:
			move = input("Invalid card. If they can, a player must follow suit. Please choose a different card.\n")

		print("Player "+ self.get_current_player_name() + " played card ", move)

		self.kripke_model_single_card_update(self.get_current_player_name(), move)

		if self.current_trick.get_nr_of_cards() == 0:
			self.current_trick.set_suit(self.get_card_suit(int(move)))

		self.hand_cards[self.agents.index(self.player_order[self.current_player])].remove(int(move))
		self.current_trick.add_card(move)
		self.current_player = (self.current_player + 1) % 3

	def ask_for_communicating_agent(self):
		"""
		This function querries the user to say which agent they want to have communicate one of their cards
		We check if this input is actually an agent and if this agent can still communicate.
		"""
		agent = input("Which player (a, b or c) would like to communicate a card? (type \"cancel\" to cancel)\n")
		print("")

		if agent == "cancel":
			return None

		while agent not in self.agents:
			print(str(agent), "is not a player, please try again. You can choose players:" ,self.agents)
			agent = input("Which player would like to communicate a card?\n")
			print("")


		agent_index = self.agents.index(agent)

		if self.nr_of_communications[agent_index] > 0:
			self.nr_of_communications[agent_index] -= 1
			return agent
		else:
			print("This player can no longer communicate.")
			return self.ask_for_communicating_agent()

	def get_agent_hand(self, agent):
		"""
		Returns the hand of a specifik agent
		"""
		hand_index = self.agents.index(agent)
		return self.hand_cards[hand_index]

	def communicate_card(self):
		"""
		This function is used to communicate a card
		First it asks which agent wants to communicate a card.
		Then it checks if this card is actually in that agent's hand.
		Finally it updates the kripke model with the revealed card.
		"""
		communicating_agent = self.ask_for_communicating_agent()

		if communicating_agent == None:
			return

		print("Player", communicating_agent, "has the following cards in their hand:", self.get_agent_hand(communicating_agent))

		communicated_card = input("What card would " + str(communicating_agent) + " like to communicate? (type \"cancel\" to cancel)\n")

		while (not communicated_card.isnumeric()) or int(communicated_card) not in self.get_agent_hand(communicating_agent) and communicated_card != "cancel":
			print("Player", communicating_agent, "does not have that card.")
			communicated_card = input("What card would " + str(communicating_agent) + " like to communicate? (type \"cancel\" to cancel)\n")

		if communicated_card != "cancel":
			print(communicating_agent + " communicated card " + communicated_card)
			self.kripke_model_single_card_update(str(communicating_agent), communicated_card)

	def determine_winner(self, trick):
		"""
		This function determines the winner of a trick
		It does this by looping three times (based on number of players)
		Each loop it looks at one of the players and which card they played this trick
		Then it selects either the highest card played of the trick suit
		Or (if trump cards were played) the highest trump card
		"""
		winning_card = None
		winning_player = None
		cards_in_trick = trick.get_cards()

		for index in range(3):
			if winning_card == None:
				winning_card = cards_in_trick[index]
				winning_player = self.player_order[index]
			elif trick.get_suit() != "trump" and self.get_card_suit(cards_in_trick[index]) == "trump":
				winning_card = cards_in_trick[index]
				winning_player = self.player_order[index]
			elif cards_in_trick[index] > winning_card and trick.get_suit() == self.get_card_suit(cards_in_trick[index]):
				winning_card = cards_in_trick[index]
				winning_player = self.player_order[index]

		return winning_player

	def set_player_order(self, starting_agent):
		"""
		This function returns the new agent order based on which agent should be the starting agent
		"""

		if starting_agent == "a":
			self.player_order = ["a", "b", "c"]
		elif starting_agent == "b":
			self.player_order = ["b", "c", "a"]
		elif starting_agent == "c":
			self.player_order = ["c", "a", "b"]
		else:
			print("------ERROR: COULD NOT SET NEW PLAYER ORDER------")

	def end_trick(self):
		"""
		This function ends the current trick
		This means that it determines who won the trick
		Then adds the cards of this trick to the winners cards_won pile
		Then it resets the values of the trick, making the winning agent the first agent to play
		"""
		#print("--------------------------------",self.current_trick.get_nr_of_cards(), self.current_trick.get_cards())
		winning_agent = self.determine_winner(self.current_trick)

		print("Player", winning_agent, "played the winning card of this trick.")
		print("Player", winning_agent, "will now start the new trick.")

		winning_agent_index = self.agents.index(winning_agent)
		self.cards_won[winning_agent_index] += self.current_trick.get_cards()
		self.current_trick.reset()
		
		self.set_player_order(winning_agent)

	def mission_passed(self):
		"""
		This function checks if the mission has been accomplished
		It does this by seeing if the mission agent has the mission card in their cards_won pile
		"""
		Mission_agent_index = self.agents.index(self.mission[0])
		#print(self.cards_won, "----------------------------")

		for card in self.cards_won[Mission_agent_index]:
			if card == self.mission[1]:
				return True

		return False

	def current_player_hand_empty(self):
		"""
		Returns if the hand of the current player is empty
		"""
		return not self.get_current_player_hand()

	def check_end_of_trick(self):
		"""
		Checks if the trick has ended and if the win or lose condition has been met
		"""
		#print("--------------------------------",self.current_trick.get_nr_of_cards(), self.current_trick.get_cards())
		if self.current_trick.get_nr_of_cards() == len(self.agents):
			self.end_trick()


			if self.mission_passed():
				print("Congratulations, you have passed your mission!")
				return False
			elif self.current_player_hand_empty():
				print("You have failed your mission, how unfortunate.")
				return False

		return True

	def get_positive_common_knowledge(self, ks):
		"""
		Generates a complete list of all the common knowlegde present in the model
		"""
		# First collect all possible true facts
		#fact_list = get_list_of_facts(ks)
		# Generate all possible false facts
		fact_list = list()
		for agent in self.agents:
			for card in self.deck:
				fact_list.append(agent + ":" + str(card))
		true_fact_list = fact_list.copy()
		#print("fact_list:", fact_list)

		# Then loop through all worlds
		for world in ks.worlds:
			#print(world.name)
			world_facts = list(world.assignment.keys())
			#print(world_facts)
			to_be_removed_true = []
			# If a fact is not in a world, queue it up fo removal
			for fact in fact_list:
				if not fact in world_facts:
					to_be_removed_true.append(fact)
			# And then remove all of them from the fact list
			#print(to_be_removed_true)
			for fact in to_be_removed_true:
				if fact in true_fact_list:
					true_fact_list.remove(fact)

		#print("Final list:", true_fact_list)
		return true_fact_list

	def get_common_knowledge(self):
		"""
		Generates a complete list of all the common knowlegde present in the model
		"""
		# First collect all possible true facts
		#fact_list = get_list_of_facts(ks)
		# Generate all possible false facts
		fact_list = list()
		for agent in self.agents:
			for card in self.deck:
				fact_list.append(agent + ":" + str(card))
		true_fact_list = fact_list.copy()
		false_fact_list = fact_list.copy()

		# Then loop through all worlds
		for world in self.kripke_model.worlds:
			world_facts = list(world.assignment.keys())
			to_be_removed_true = []
			to_be_removed_false = []
			# If a fact is not in a world, queue it up fo removal
			for fact in fact_list:
				if not fact in world_facts:
					to_be_removed_true.append(fact)
				else:
					to_be_removed_false.append(fact)
			# And then remove all of them from the fact list
			for fact in to_be_removed_true:
				if fact in true_fact_list:
					true_fact_list.remove(fact)
			for fact in to_be_removed_false:
				if fact in false_fact_list:
					false_fact_list.remove(fact)

		false_fact_list = ["~" + e for e in false_fact_list]
		return true_fact_list + false_fact_list
		