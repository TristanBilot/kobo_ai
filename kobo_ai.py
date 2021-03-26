import ui_utils as ui
from enum import Enum
from dataclasses import dataclass
from typing import List
import random
import operator

class Rank(Enum):
    TEN = 0
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7 
    EIGHT = 8
    NINE = 9
    JACK = 10
    QUEEN = 11
    KING = 12

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

class CommandKeys(Enum):
    QuitKey = 'Q'
    KoboKey = 'K'

class PlayerInput:
    def __init__(self):
        self.is_index = False
        self.is_command = False
        self.is_kobo = False
        self.is_quit_key = False
        self.value = ''

    def input_loop(self, nb_cards, msg='', accept_indexes=False, accept_commands=False) -> int:
        """ loop asking the user to enter an answer.
        """
        self.value = self._input(msg)
        
        while (accept_indexes and accept_commands and not self._is_correct(nb_cards)) \
            or (accept_indexes and not accept_commands and not self._check_card_index(nb_cards)) \
            or (accept_commands and not accept_indexes and not self._check_command()):
            print(self._invalid_input_msg(nb_cards))
            print(accept_commands and not accept_indexes and not self._check_command())
            self.value = self._input(msg)
        if self._check_kobo():
            self.is_kobo = True
        if self._check_card_index(nb_cards):
            self.value = int(self.value) - 1
            self.is_index = True
        elif self._check_command():
            self.is_command = True
        if self.is_command and self.value == CommandKeys.QuitKey:
            self.is_quit_key = True

        # print(self.is_index)
        # print(self.is_command)
        # print(self.is_kobo)
        # print(self.is_quit_key)

    def _input(self, msg: str='') -> str:
        return input(msg)

    def _is_correct(self, nb_cards: int) -> bool:
        """ returns wether the user's input is correct. 
        In bound of the number of cards or a command.
        """
        return self._check_card_index(nb_cards) or self._check_command()

    def _check_card_index(self, nb_cards: int) -> bool:
        inp = self.value.split()
        if not 1 >= len(inp) <= 2:
            return False
        inp = inp[0]
        if not inp.isdigit():
            return False
        inp = int(inp)
        return 1 <= inp <= nb_cards

    def _check_command(self) -> bool:
        inp = self.value.split()
        print(inp)
        if not 1 >= len(inp) <= 2:
            return False
        cmd = inp[0]
        return self._is_valid_command(cmd)

    def _check_kobo(self) -> bool:
        inp = self.value.split()
        if len(inp) != 2:
            return False
        cmd = inp[1]
        is_kobo = self._is_valid_command(cmd) and cmd == CommandKeys.KoboKey
        if is_kobo:
            self.value = cmd[0]
        return is_kobo

    def _is_valid_command(self, cmd: str):
        return isinstance(cmd, str) and cmd in set(item.value for item in CommandKeys)

    def _invalid_input_msg(self, nb_cards: int):
        digit_valid = [*range(1, nb_cards + 1)]
        return 'Invalid command, valid commands: {}'.format( \
            [*digit_valid, *list(map(lambda x: x.value, [*CommandKeys]))])

class Game:
    def __init__(self, nb_cards=4):
        self.nb_cards = nb_cards
        self._init_players()
        self._init_game()
        self._displayed_cards = [0, 1]
        self._should_display_cards = True

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
        self.is_kobo = False

    def set_cards(self, cards):
        self.cards = cards
        for c in self.cards[:2]:
            c.discover(True)

    @property
    def nb_cards(self):
        return len(self.cards)

    def win(self):
        self.victories += 1

    def play(self, deck_card):
        pass

    def _apply_card_effects(self, thrown_cards):
        pass

    def _substitute_card(self, index: int, deck_card: Card):
        selected = self.cards[index]
        deck_card.discover(True)
        thrown_cards = [self.cards.pop(index)]
        self.cards.insert(index, deck_card)

        # remove all duplicates of the chosen card
        updated_cards = self.cards.copy()
        for i in range(len(self.cards)):
            c = self.cards[i]
            if c.is_discovered() and c == selected:
                thrown_cards.append(updated_cards.pop(i))
        self.cards = updated_cards
        return thrown_cards

    def _do_not_substitute_card(self, deck_card: Card):
        thrown_cards = []
        updated_cards = self.cards.copy()
        for i in range(len(self.cards)):
            c = self.cards[i]
            if c.is_discovered() and c == deck_card:
                thrown_cards.append(updated_cards.pop(i))
        self.cards = updated_cards
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

    def _trigger_queen_effect(self, card_index: int):
        self.cards[card_index].discover(True)

    def _trigger_jack_effect(
        self, 
        my_card_index: int, 
        other_card_index: int,
        other_cards: List[Card]
        ):
        self.cards[my_card_index].discover(False)
        other_cards[other_card_index].discover(False)
        self.cards[my_card_index], other_cards[other_card_index] = \
            other_cards[other_card_index], self.cards[my_card_index]


class Player(PlayerI):
    def __init__(self, game):
        super().__init__(game)

    def play(self, deck_card):
        self._display_deck_card(deck_card)
        inp = PlayerInput()
        inp.input_loop(self.nb_cards, msg='Your turn: ', accept_indexes=True, accept_commands=True)
        self.is_kobo = inp.is_kobo
        return self._handle_input(inp, deck_card)

    def _handle_input(self, inp: PlayerInput, deck_card: Card):
        if inp.is_index:
            thrown_cards = self._substitute_card(inp.value, deck_card)
            self._apply_card_effects(thrown_cards)
            return thrown_cards
        elif inp.is_command:
            if inp.is_quit_key:
                thrown_cards = self._do_not_substitute_card(deck_card)
                self._apply_card_effects(thrown_cards)
                return thrown_cards

    def _apply_card_effects(self, thrown_cards):
        self.game.set_should_display_cards(True)
        for card in thrown_cards:
            if card.rank == Rank.JACK:
                self.display_cards()
                inp = PlayerInput()
                inp.input_loop(self.nb_cards, msg='Which card do you wanna switch? ', accept_indexes=True)
                my_card = inp.value
                if inp.is_quit_key:
                    break

                self.game.ai_player.display_cards()
                inp = PlayerInput()
                inp.input_loop(self.game.ai_player.nb_cards, msg='Which card do you wanna peek? ', accept_indexes=True)
                other_card = inp.value
                super()._trigger_jack_effect(my_card, other_card, self.game.ai_player.cards)

            if card.rank == Rank.QUEEN:
                inp = PlayerInput()
                inp.input_loop(self.game.ai_player.nb_cards, msg='Which card do you wanna see? ', accept_indexes=True)
                hidden_card_index = inp.value
                if inp.is_quit_key:
                    break
                super()._trigger_queen_effect(hidden_card_index)
                self.display_cards(visible_cards=[hidden_card_index])
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
        def get_worst_card_index(cards: List[Card], rank_to_ignore: Rank=None) -> int:
            """ returns the index of the card with the worst value.
            Does not take into account the duplicates.
            """
            worst = cards[0], worst_idx = 0
            for i in range(1, len(cards)):
                c = cards[i]
                if c.rank.value > worst and c.rank != rank_to_ignore:
                    worst = c.rank, worst_idx = i
            return worst_idx

        def get_worst_combinaison_of_cards_index(cards: List[Card]) -> int:
            """ returns the index of the card which when played
            will lose the most points. Takes into account the duplicate
            cards which will lose more points.
            """
            card_values = {}
            for i in range(len(cards)):
                c = cards[i]
                card_values[c.rank] += c.rank
            max_combinaison_rank = max(card_values.items(), key=operator.itemgetter(1))[0]
            first_idx = next(c for c in cards if c.rank == max_combinaison_rank)
            return first_idx

        def get_first_card_index(cards: List[Card], rank: Rank) -> int:
            for i in range(len(cards)):
                if cards[i].rank == rank:
                    return i
            return -1

        def get_random_card_index(
            cards: List[Card], 
            do_not_choose_indexes: List[int]=[]
            ) -> int:
            """ returns a pseudo random index from list of cards;
            some `do_not_choose_indexes` can be provide to avoid 
            to peek same card multiple times.
            """
            if len(cards) == 0:
                return 0
            for i in range(len(cards)):
                if i not in do_not_choose_indexes:
                    return i
            return random.randint(0, len(cards))

        def get_hidden_card_index(cards: List[Card]) -> int:
            """ returns the first index of a hidden card in `cards` or -1.
            """
            hidden_cards = [i for i in range(len(cards)) if not cards[i].is_discovered()]
            return next(hidden_cards) if len(hidden_cards) == 1 else -1

        def apply_card_effects(thrown_cards: List[Card]):
            def apply_jack_effect(cards: List[Card]):
                """ apply effect on all jack cards.
                """
                already_peeked_indexes = []
                for c in cards:
                    if c.rank == Rank.JACK:
                        random_index = get_random_card_index(player.cards, already_peeked_indexes)
                        already_peeked_indexes.append(random_index)
                        super()._trigger_jack_effect(worst_card_idx, random_index, player.cards)
                        worst_card_idx = get_worst_combinaison_of_cards_index(cards)

            def apply_queen_effect(cards: List[Card]):
                """ apply effect on all queen cards.
                """
                for c in cards:
                    if c.rank == Rank.QUEEN:
                        for card in cards:
                            if not card.is_discovered():
                                super()._trigger_queen_effect(card)
                                break

            apply_jack_effect(thrown_cards)
            apply_queen_effect(thrown_cards)
            

        player = self.game.player
        cards = [c for c in self.cards if c.is_discovered()]
        hidden_card_index = get_hidden_card_index(self.cards)

        # handle kobo
        if player.is_kobo:
            if deck_card.rank == Rank.JACK: # deck card is jack
                thrown_jack_cards = self._do_not_substitute_card(deck_card)
                apply_card_effects(thrown_jack_cards)
                return thrown_jack_cards
            else:
                jack_index = get_first_card_index(cards, Rank.JACK)
                if jack_index == -1: # found a jack in cards
                    thrown_jack_cards = self._substitute_card(jack_index, deck_card)
                    apply_card_effects(thrown_jack_cards)
                    return thrown_jack_cards
        
        # handle queen
        if deck_card.rank == Rank.QUEEN:
            thrown_queen_cards = self._do_not_substitute_card(deck_card)
            apply_card_effects(thrown_queen_cards)
            return thrown_queen_cards
        else:
            queen_index = get_first_card_index(cards, Rank.QUEEN)
            if queen_index != -1: # found a queen
                if hidden_card_index != -1: # found 1 hidden card
                    thrown_queen_cards = self._substitute_card(queen_index, deck_card)
                    apply_card_effects(thrown_queen_cards)
                    return thrown_queen_cards

        # handle hidden cards discover
        if hidden_card_index != -1: # found a hidden card
            thrown_cards = self._substitute_card(hidden_card_index, deck_card)
            apply_card_effects(thrown_cards)
            return thrown_cards
        
        # default turn
        worst_card_index = get_worst_card_index(cards)
        thrown_cards = self._substitute_card(worst_card_index, deck_card)
        return thrown_cards

    def _apply_card_effects(self, thrown_cards):
        self.game.set_should_display_cards(True)
        for card in thrown_cards:
            if card.rank == Rank.JACK:
                self.display_cards()
                inp = PlayerInput()
                inp.input_loop(self.nb_cards, msg='Which card do you wanna switch? ', accept_indexes=True)
                my_card = inp.value
                if inp.is_quit_key:
                    break

                self.game.ai_player.display_cards()
                inp = PlayerInput()
                inp.input_loop(self.game.ai_player.nb_cards, msg='Which card do you wanna peek? ', accept_indexes=True)
                other_card = inp.value
                super()._trigger_jack_effect(my_card, other_card, self.game.ai_player.cards)

            if card.rank == Rank.QUEEN:
                inp = PlayerInput()
                inp.input_loop(self.game.ai_player.nb_cards, msg='Which card do you wanna see? ', accept_indexes=True)
                hidden_card_index = inp.value
                if inp.is_quit_key:
                    break
                super()._trigger_queen_effect(hidden_card_index)
                self.display_cards(visible_cards=[hidden_card_index])
                self.game.set_should_display_cards(False)

    def display_cards(self, visible_cards: List[int]=[]):
        print(Colors.BOLD)
        print('AI cards')
        super().display_cards(visible_cards=visible_cards)


g = Game()
g.launch()