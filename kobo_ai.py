import ui_utils as ui
from enum import Enum
from dataclasses import dataclass
from typing import List
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

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
        self.format = '{}'.format(self.rank.format())
        self._is_discovered = False

    def discover(self, yes: bool):
        self._is_discovered = yes

    def is_discovered(self):
        return self._is_discovered

    def __repr__(self):
        return '{}'.format(self.format)

    def __eq__(self, obj):
        return isinstance(obj, Card) and self.format == obj.format

    def __hash__(self):
        return hash((self.rank, self.suit))

class Game:
    def __init__(self, nb_cards=4):
        self.nb_cards = nb_cards
        self._init_players()
        self._init_game()
        self._displayed_cards = [0, 1]
        self._should_display_cards = True
        Game.QuitKey = 'Q'

    def pop_card(self):
        if len(self.deck) == 0:
            print('The deck is empty!')
        return self.deck.pop()

    def launch(self):
        player, ai = self.player, self.ai_player
        player_turn = bool(random.randint(0, 1))

        while True:
            deck_card = self.pop_card()
            if player_turn:
                if self._should_display_cards:
                    player.display_cards(visible_cards=self._displayed_cards)
                thrown_cards = player.play(deck_card)
                self._displayed_cards = []
            else:
                # thrown_cards = ai.play(deck_card)
                thrown_cards = []
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

    def set_displayed_cards(self, cards: [int]):
        self._displayed_cards = cards

    def set_should_display_cards(self, should: bool):
        self._should_display_cards = should

class PlayerI:
    def __init__(self, game):
        self.game = game
        self.victories = 0

    def set_cards(self, cards):
        self.cards = cards
        for c in self.cards[:2]:
            c.discover(True)

    def win(self):
        self.victories += 1

    def play(self, deck_card):
        pass

    def _apply_card_effects(self, thrown_cards):
        pass

    def _substitute_card(self, answer: int, deck_card: Card):
        old_cards = self.cards.copy()
        selected = self.cards[answer]
        deck_card.discover(True)
        thrown_cards = [self.cards.pop(answer)]
        self.cards.insert(answer, deck_card)

        # remove all duplicates of the chosen card
        updated_cards = self.cards.copy()
        for i in range(len(self.cards)):
            c = self.cards[i]
            if c.is_discovered() and c == selected:
                thrown_cards.append(updated_cards.pop(i))
        self.cards = updated_cards

        print(old_cards)
        print(updated_cards)
        print(len(thrown_cards))
        return thrown_cards

    def _do_not_substitute_card(self, deck_card: Card):
        thrown_cards = [card for card in self.cards if card == deck_card] + [deck_card]
        return thrown_cards

    def display_cards(self, visible_cards: List[int]=[]):
        cards = ' '.join([self.cards[i].format if i in visible_cards else self.cards[i].format for i in range(len(self.cards))])
        styled = ui.wrap_str_in_stars(cards)
        print(styled)
        # print(' '.join([c.format for c in self.cards]))

    def _display_deck_card(self, card: Card):
        print(Colors.OKCYAN)
        print('New card')
        styled = ui.wrap_str_in_stars(card.format)
        print(styled + Colors.ENDC)

    def display_digit_error(self):
        digit_valid = [*range(1, len(self.cards) + 1)]
        print('Invalid command, valid commands: {}'.format(digit_valid))

    def _check_answer(self, answer):
        if not (self._check_digit(answer) or self._check_command(answer)):
            digit_valid = [*range(1, len(self.cards) + 1)]
            command_valid = answer == Game.QuitKey
            print('Invalid command, valid commands: {}'.format([*digit_valid, command_valid]))
            return False
        return True

    def _check_digit(self, answer):
        if not answer.isdigit():
            return False
        answer = int(answer)
        return answer <= len(self.cards) and answer >= 1

    
    def _check_command(self, answer):
        if not isinstance(answer, str):
            return False
        return answer == Game.QuitKey

    def input_loop(self, msg) -> int:
        """ loop asking the user to enter an answer: 
        * digit=index of chosen card).
        * Game.QuitKey=do not use the action.
        returns -1 if Game.QuitKey or digit.
        """
        self.display_cards()
        answer = input(msg)
        while not self._check_answer(answer):
            self.display_digit_error()
            answer = input(msg)
        if answer == Game.QuitKey:
            return -1
        return int(answer) - 1

class Player(PlayerI):
    def __init__(self, game):
        super().__init__(game)

    def play(self, deck_card):
        self._display_deck_card(deck_card)
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

    def _apply_card_effects(self, thrown_cards):
        self.game.set_should_display_cards(True)
        for card in thrown_cards:
            if card.rank == Rank.JACK:
                my_card = self.input_loop('Which card do you wanna switch? ')
                if my_card == -1:
                    break
                other_card = self.game.ai_player.input_loop('Which card do you wanna peek? ')
                
                self.cards[my_card].discover(False)
                self.game.ai_player.cards[other_card].discover(False)
                self.cards[my_card], self.game.ai_player.cards[other_card] = \
                    self.game.ai_player.cards[other_card], self.cards[my_card]

            if card.rank == Rank.QUEEN:
                hidden_card = self.input_loop('Which card do you wanna see? ')
                if hidden_card == -1:
                    break
                self.display_cards(visible_cards=[hidden_card])
                self.game.set_should_display_cards(False)

    def _display_opponent_cards(self):
        print(self.game.ai_player.cards)

    def display_cards(self, visible_cards: List[int]=[]):
        print(Colors.BOLD)
        print('Your cards')
        super().display_cards(visible_cards=visible_cards)

class AIPlayer(PlayerI):
    def __init__(self, game):
        super().__init__(game)

    def play(self, deck_card):
        # return []
        return self._substitute_card(0, deck_card)

    def _apply_card_effects(self, thrown_cards):
        pass

    def display_cards(self, visible_cards: List[int]=[]):
        print(Colors.BOLD)
        print('AI cards')
        super().display_cards(visible_cards=visible_cards)


g = Game()
g.launch()