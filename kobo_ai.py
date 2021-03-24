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

class Command(Enum):
    N = 1

    def __str__(self):
        return str(self.value)

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
    def __init__(self, nb_players=2, nb_cards=4):
        self.nb_players = nb_players
        self.nb_cards = nb_cards
        self._init_game()

    def pop_card(self):
        if len(self.deck) == 0:
            raise EnvironmentError('The deck is empty!')
        return self.deck.pop()

    def launch(self):
        player, ai = self.players[0], self.players[1]
        player_turn = bool(random.randint(0, 1))

        while True:
            deck_card = self.pop_card()
            if player_turn:
                thrown_cards = player.play(deck_card)
            else:
                thrown_cards = ai.play(deck_card)
            player_turn = not player_turn
            self.thrown_deck += thrown_cards

    def _init_game(self):
        self.thrown_deck = []
        deck = []
        for suit in Suit:
            for rank in Rank:
                card = Card(rank, suit)
                deck.append(card)
        random.shuffle(deck)
        self.deck = deck

        players = []
        for i in range(self.nb_players):
            cards = []
            for _ in range(self.nb_cards):
                cards.append(self.pop_card())
            if i == 0:
                players.append(Player(cards.copy()))
            if i == 1:
                players.append(AIPlayer(cards.copy(), self))
        self.players = players

class PlayerI:
    def __init__(self, cards):
        self.cards = cards

    def play(self, deck_card):
        pass

    def substitute_card(self, answer, deck_card):
        selected = self.cards[answer]
        thrown_cards = [card for card in self.cards if card == selected]
        self.cards.pop(answer)
        self.cards.insert(answer, deck_card)

        # remove all duplicates of the chosen card
        self.cards = [card for card in self.cards if card != selected]
        return thrown_cards

    def display_cards(self):
        # print(' '.join(['*' for _ in range(len(self.cards))]))
        print(' '.join([c.format for c in self.cards]))

class Player(PlayerI):
    def play(self, deck_card):
        self.display_cards()
        print('New card => {}'.format(deck_card.format))

        answer = str(input('Your turn: '))
        if not self._check_answer(answer):
            self.play(deck_card)
        return self._handle_answer(answer, deck_card)

    def _handle_answer(self, answer, deck_card):
        if answer.isdigit():
            answer = int(answer) - 1
            return self.substitute_card(answer, deck_card)
        else:
            return []

    def _check_answer(self, answer):
        def check_digit(answer):
            if not answer.isdigit():
                return False
            answer = int(answer)
            return answer <= len(self.cards) and answer >= 1

        def check_command(answer):
            if not isinstance(answer, str):
                return False
            command_exists = [c.name for c in Command if c.name == answer]
            return len(command_exists) > 0

        if not (check_digit(answer) or check_command(answer)):
            print('Invalid command, valid commands: {}'.format(
                [*range(1, len(self.cards) + 1), ' '.join(list(map(lambda x: x.name, Command)))] 
            ))
            return False
        return True

class AIPlayer(PlayerI):
    def __init__(self, cards, game):
        super().__init__(cards)
        self.game = game

    def play(self, deck_card):

        return self.substitute_card(1, deck_card)


g = Game()
g.launch()