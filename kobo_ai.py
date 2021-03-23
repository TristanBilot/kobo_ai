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

            
            player.display_cards()
            print('New card => {}'.format(deck_card.format))

            answer = int(input('Your turn: ')) - 1
            if not self._check_input(player, answer):
                continue
            should_pop = True

            player.handle_input(answer, deck_card)

    def _check_input(self, player, answer):
        return answer < player.nb_card()

    def _init_game(self):
        deck = []
        for suit in Suit:
            for rank in Rank:
                card = Card(rank, suit)
                deck.append(card)
        random.shuffle(deck)
        self.deck = deck

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

    def handle_input(self, answer, deck_card):
        selected = self.cards[answer]
        self.cards.pop(answer)
        self.cards.insert(answer, deck_card)

        # remove all duplicates of the chosen card
        self.cards = [card for card in self.cards if card != selected]

    def display_cards(self):
        # print(' '.join(['*' for _ in range(len(self.cards))]))
        print(' '.join([c.format for c in self.cards]))

    def has_this_card(self, answer):
        card = self.cards[answer]
        return card.format in list(map(lambda x: x.format(), self.cards))

    def nb_card(self):
        return len(self.cards)

g = Game(2)
g.launch()