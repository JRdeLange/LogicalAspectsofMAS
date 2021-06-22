from kripke import World, KripkeStructure
from mlsolver.formula import *
from mlsolver.formula import Atom, And, Not, Or, Box_a, Box_star
from Trick import Trick

class GameManager:
	"""docstring for GameManager"""
	def __init__(self, kripke_model, agents, deck, hand_cards, mission):
		super(GameManager, self).__init__()

		self.kripke_model = kripke_model
		self.agents = agents
		self.deck = deck
		self.mission = mission
		self.hand_cards = hand_cards
		self.cards_won = [[] for i in range(3)]

		self.current_trick = Trick()
		self.player_order = agents
		self.current_player = 0

	def generate_tricks(self):
		"""
		Generates possible tricks in the current scenario.
		CURRENTLY ASSUMES THAT THE CURRENT PLAYER WILL START THE TRICK. THIS MATTERS FOR THE SUIT OF THE TRICK
		"""
		# Collect all played cards
		played_cards = self.current_trick.get_cards()
		for player in self.cards_won:
			for card in player:
				print(type(card))
				played_cards += [card]

		# Determine the cards each player has that are common knowledge
		common_knowledge_hands = {"a" : [], "b" : [], "c" : []}
		common_knowledge = self.get_positive_common_knowledge()
		playable_cards = []
		for fact in common_knowledge:
			card = int(fact[2:])
			player = fact[0]
			if not card in played_cards:
				common_knowledge_hands[player] += [card]
		
		# Put all the pieces together and actually generate the tricks
		tricks = []
		for card_a in common_knowledge_hands["a"]:
			for card_b in common_knowledge_hands["b"]:
				for card_c in common_knowledge_hands["c"]:
					trick = Trick()
					cards = [card_a, card_b, card_c]
					trick.add_multiple_cards(cards)
					first_player = self.get_current_player_name()
					trick.set_suit(self.get_card_suit(cards[self.player_order.index(first_player)]))
					tricks += [trick]

		# If a trick is winning, print it
		for trick in tricks:
			winning_agent = self.determine_winner(trick)
			if self.mission[0] == winning_agent and self.mission[1] in trick.get_cards():
				print("Winning trick is", trick.get_cards())

	def is_game_winnable(self):
		current_nr_of_cards = current_trick.get_nr_of_cards() 
		if current_nr_of_cards == 0:
			common_knowledge = get__positive_common_knowledge(kripke_model, agents, deck)
			# Generate possible tricks

		elif current_nr_of_cards == 1:
			pass
		else:
			pass

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

	def kripke_model_single_card_update(self, agent, card):
		"""
		Updates the kripke model based on a specifik card becoming common knowledge
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
		print("player " + self.get_current_player_name() + " has the following cards in their hand:", self.get_current_player_hand())
		move = input("What card is played by " + self.get_current_player_name() + "?\n")
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
		"""
		agent = input("Which player would like to communicate a card?\n")
		while agent not in self.agents:
			print(str(agent), "is not a player, please try again. You can choose players:" ,self.agents)
			agent = input("Which player would like to communicate a card?\n")
		return agent

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

		print("player ", communicating_agent, " has the following cards in their hand:", self.get_agent_hand(communicating_agent))

		communicated_card = input("What card would " + str(communicating_agent) + " like to communicate? (type \"cancel\" to cancel)\n")

		while int(communicated_card) not in self.get_agent_hand(communicating_agent) and communicated_card != "cancel":
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
		winning_agent = self.determine_winner(self.current_trick)

		print("The suit of this trick was", self.current_trick.get_suit(), ". Player", winning_agent, "played the winning card and has thus won this trick.")
		print("Player", winning_agent, "will now start the new trick.")

		winning_agent_index = self.agents.index(winning_agent)
		self.cards_won[winning_agent_index] += self.current_trick.get_cards()

		self.set_player_order(winning_agent)

		self.current_trick = Trick()

	def mission_passed(self):
		"""
		This function checks if the mission has been accomplished
		It does this by seeing if the mission agent has the mission card in their cards_won pile
		"""
		Mission_agent_index = self.agents.index(self.mission[0])

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
		if self.current_trick.get_nr_of_cards() == len(self.agents):
			self.end_trick()

			if self.mission_passed():
				print("Congratulations, you have passed your mission!")
				return False
			elif self.current_player_hand_empty():
				print("You have failed your mission, how unfortunate.")
				return False

		return True

	def get_positive_common_knowledge(self):
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

		# Then loop through all worlds
		for world in self.kripke_model.worlds:
			world_facts = list(world.assignment.keys())
			to_be_removed_true = []
			# If a fact is not in a world, queue it up fo removal
			for fact in fact_list:
				if not fact in world_facts:
					to_be_removed_true.append(fact)
			# And then remove all of them from the fact list
			for fact in to_be_removed_true:
				if fact in true_fact_list:
					true_fact_list.remove(fact)

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
		