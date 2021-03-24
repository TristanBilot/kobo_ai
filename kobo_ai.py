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
        return traductions[self.value-1]

class Suit(Enum):
    CLUB = 1
    DIAMOND = 2
    HEART = 3
    SPADE = 4

class Command(Enum):
    Q = 1 # Q: Put a card back in the dec

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
    def __init__(self, nb_cards=4):
        self.nb_cards = nb_cards
        self._init_players()
        self._init_game()

    def pop_card(self):
        if len(self.deck) == 0:
            raise EnvironmentError('The deck is empty!')
        return self.deck.pop()

    def launch(self):
        player, ai = self.player, self.ai_player
        player_turn = bool(random.randint(0, 1))

        while True:
            deck_card = self.pop_card()
            if player_turn:
                thrown_cards = player.play(deck_card)
            else:
                thrown_cards = ai.play(deck_card)
            player_turn = not player_turn
            self.thrown_deck += thrown_cards

            if self._check_victory(player, ai):
                break

    def _init_players(self):
        self.ai_player = AIPlayer(self)
        self.player = Player(self)

    def _init_game(self):
        self.thrown_deck = []
        deck = []
        for suit in Suit:
            for rank in Rank:
                card = Card(rank, suit)
                deck.append(card)
        random.shuffle(deck)
        self.deck = deck

        cards = []
        nb_players = 2
        for _ in range(nb_players):
            tmp = []
            for _ in range(self.nb_cards):
                tmp.append(self.pop_card())
            cards.append(tmp.copy())
        self.ai_player.set_cards(cards[0])
        self.player.set_cards(cards[1])

    def _check_victory(self, player, ai_player):
        if len(player.cards) == 0:
            player.win()
            print('YOU WON')
            return True
        elif len(ai_player.cards) == 0:
            ai_player.win()
            print('THE AI WON')
            return True
        return False


class PlayerI:
    def __init__(self, game):
        self.game = game
        self.victories = 0

    def set_cards(self, cards):
        self.cards = cards

    def win(self):
        self.victories += 1

    def play(self, deck_card):
        pass

    def _apply_card_effects(self, thrown_cards):
        pass

    def _substitute_card(self, answer: int, deck_card: Card):
        selected = self.cards[answer]
        thrown_cards = [card for card in self.cards if card == selected]
        self.cards.pop(answer)
        self.cards.insert(answer, deck_card)

        # remove all duplicates of the chosen card
        self.cards = [card for card in self.cards if card != selected]
        return thrown_cards

    def _do_not_substitute_card(self, deck_card: Card):
        thrown_cards = [card for card in self.cards if card == deck_card] + [deck_card]
        return thrown_cards

    def display_cards(self, visible_card: int=None):
        print(' '.join([self.cards[i].format if i == visible_card else '*' for i in range(len(self.cards))]))
        # print(' '.join([c.format for c in self.cards]))

    def display_digit_error(self):
        digit_valid = [*range(1, len(self.cards) + 1)]
        print('Invalid command, valid commands: {}'.format(digit_valid))

    def check_digit(self, answer):
        if not answer.isdigit():
            return False
        answer = int(answer)
        return answer <= len(self.cards) and answer >= 1

    def input_digit_loop(self, msg) -> int:
        self.display_cards()
        digit = input(msg)
        while not self.check_digit(digit):
            self.display_digit_error()
            digit = input(msg)
        return int(digit) - 1

class Player(PlayerI):
    def __init__(self, game):
        super().__init__(game)

    def play(self, deck_card):
        self.display_cards()
        print('New card => {}'.format(deck_card.format))

        answer = input('Your turn: ')
        if not self._check_answer(answer):
            self.play(deck_card)
        return self._handle_answer(answer, deck_card)

    def _handle_answer(self, answer, deck_card):
        if answer.isdigit():
            answer = int(answer) - 1
            thrown_cards = self._substitute_card(answer, deck_card)
            self._apply_card_effects(thrown_cards)
            return thrown_cards
        else:
            thrown_cards = self._do_not_substitute_card(deck_card)
            self._apply_card_effects(thrown_cards)
            return thrown_cards

    def _check_answer(self, answer):
        if not (self.check_digit(answer) or self._check_command(answer)):
            digit_valid = [*range(1, len(self.cards) + 1)]
            command_valid = ' '.join(list(map(lambda x: x.name, Command)))
            print('Invalid command, valid commands: {}'.format([*digit_valid, command_valid]))
            return False
        return True

    def _check_command(self, answer):
        if not isinstance(answer, str):
            return False
        command_exists = [c.name for c in Command if c.name == answer]
        return len(command_exists) > 0

    def _apply_card_effects(self, thrown_cards):
        for card in thrown_cards:
            if card.rank == Rank.JACK:
                my_card = self.input_digit_loop('Which card do you wanna switch? ')
                other_card = self.game.ai_player.input_digit_loop('Which card do you wanna peek? ')
                
                self.cards[my_card], self.game.ai_player.cards[other_card] = \
                    self.game.ai_player.cards[other_card], self.cards[my_card]

            if card.rank == Rank.QUEEN:
                hidden_card = self.input_digit_loop('Which card do you wanna see? ')
                self.display_cards(visible_card=hidden_card)


    def _display_opponent_cards(self):
        print(self.game.ai_player.cards)

class AIPlayer(PlayerI):
    def __init__(self, game):
        super().__init__(game)

    def play(self, deck_card):
        # return []
        return self._substitute_card(0, deck_card)

    def _apply_card_effects(self, thrown_cards):
        pass


g = Game()
g.launch()