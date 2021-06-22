
class Trick:
	def __init__(self, trick_suit = None, cards_in_trick = []):
		self.trick_suit = trick_suit
		self.cards_in_trick = cards_in_trick
		self.nr_of_cards_in_trick = 0

	def set_suit(self, trick_suit):
		self.trick_suit = trick_suit

	def get_suit(self):
		return self.trick_suit

	def add_card(self, card):
		self.cards_in_trick += [int(card)]
		self.nr_of_cards_in_trick += 1

	def add_multiple_cards(self, cards):
		for card in cards:
			self.cards_in_trick += [int(card)]
			self.nr_of_cards_in_trick += 1

	def get_cards(self):
		return self.cards_in_trick

	def get_nr_of_cards(self):
		return len(self.cards_in_trick)