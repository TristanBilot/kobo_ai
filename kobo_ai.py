from enum import Enum
from dataclasses import dataclass
import random

class Rank(Enum):
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7 
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13

    def format(self):
        traductions = [str(i+1) for i in range(10)] + ['J', 'Q', 'K']
        print(len(traductions))
        return traductions[self.value-1]

class Suit(Enum):
    CLUB = 1
    DIAMOND = 2
    HEART = 3
    SPADE = 4

class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
        self.format = '{}'.format(self.rank.format())

    def __repr__(self):
        return '{}\n'.format(self.format)

    def __eq__(self, obj):
        return isinstance(obj, Card) and self.format == obj.format

class Game:
    def __init__(self, nb_players, nb_cards=4):
        self.nb_players = nb_players
        self.nb_cards = nb_cards
        self._init_game()

    def pop_card(self):
        if len(self.deck) == 0:
            raise EnvironmentError('The deck is empty!')
        return self.deck.pop()

    def launch(self):
        player = self.players[0]
        should_pop = True
        while True:
            if should_pop:
                deck_card = self.pop_card()
                should_pop = False

            print()
            for c in player.cards:
                print(c.format)
            print('New card => {}'.format(deck_card.format))

            answer = int(input('Your turn: '))
            # if not self._check_input(player, answer):
            #     continue
            should_pop = True

            player.handle_input(answer, deck_card)

            
    # def _check_input(self, player, answer):
    #     if self.possible_inputs.get(answer) is None:
    #         print('Invalid format, please try again.')
    #         return False
    #     if not player.has_this_card(answer):
    #         print('You do not possess this card.')
    #         return False
    #     return True


    def _init_game(self):
        deck = []
        possible_inputs = {}
        for suit in Suit:
            for rank in Rank:
                card = Card(rank, suit)
                deck.append(card)
                possible_inputs[card.format] = True
        random.shuffle(deck)
        self.deck = deck
        self.possible_inputs = possible_inputs

        players = []
        for _ in range(self.nb_players):
            cards = []
            for _ in range(self.nb_cards):
                cards.append(self.pop_card())
            players.append(Player(cards.copy()))
        self.players = players

class Player:
    def __init__(self, cards):
        self.cards = cards

    # def has_this_card(self, card_format):
    #     for c in self.cards:
    #         if c.format == card_format:
    #             return True
    #     return False

    def handle_input(self, answer, deck_card):
        selected = self.cards[answer]
        self.cards.pop(answer)
        self.cards.insert(answer, deck_card)

        for i in range(len(self.cards)):
            if self.cards[i] == selected:
                 self.cards.pop(i)

g = Game(2)
g.launch()