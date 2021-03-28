from collections import defaultdict
import ui_utils as ui
from enum import Enum
from dataclasses import dataclass
from typing import List
import random
import operator

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
            self.value = self._input(msg)
        if self._check_kobo():
            self.is_kobo = True
        if self._check_card_index(nb_cards):
            self.value = int(self.value) - 1
            self.is_index = True
        elif self._check_command():
            self.is_command = True
        if self.is_command and self.value == CommandKeys.QuitKey.value:
            self.is_quit_key = True

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
            exit()
        return self.deck.pop()

    def launch(self):
        player, ai = self.player, self.ai_player
        player_turn = bool(random.randint(0, 1))
        thrown_cards: List[Card]

        while True:
            deck_card = self.pop_card()
            if player_turn:
                # if self._should_display_cards:
                #     player.display_cards(visible_cards=self._displayed_cards)
                # player._display_deck_card(deck_card)
                thrown_cards = player.play(deck_card)
                self._displayed_cards = []
            else:
                ai.display_cards()
                ai._display_deck_card(deck_card)
                thrown_cards = ai.play(deck_card)
            self._throw_duplicate_cards(thrown_cards, player_turn)
            self.thrown_deck += thrown_cards
            print(('PLAYER' if player_turn else 'AI') + ' PLAYS')
            visible_cards = [c for c in ai.cards if c.is_discovered()]
            if not player_turn:
                print(f'Visible cards: {visible_cards}')
                print(f'Cards: {ai.cards}')
                print(f'Kobo: {ai.is_kobo}')

            player_turn = not player_turn
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
        # self.ai_player.set_cards([Card(Rank.ACE, Suit.CLUB), Card(Rank.NINE, Suit.CLUB), Card(Rank.FOUR, Suit.CLUB), Card(Rank.NINE, Suit.CLUB)])
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
    
    def nb_occurences_in_deck(self, rank: Rank):
        return len([c for c in self.deck if c.rank == rank])

    def _throw_duplicate_cards(self, thrown_cards: List[Card], player_turn: bool):
        thrown_ranks = list(map(lambda x: x.rank, thrown_cards))
        other_player = self.player if not player_turn else self.ai_player
        for c in other_player.cards:
            if c.rank in thrown_ranks:
                print(f'{c} is a duplicate card!')
                other_player.cards.remove(c)
                # IMPORTANT  !!!  handle the effects of cards (queen or J if duplicate) use inheritance for methods


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

    @property
    def _hidden_cards(self):
        return [i for i in range(self.nb_cards) if not self.cards[i].is_discovered()]

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
                inp.input_loop(self.nb_cards, msg='Which card do you wanna switch? ', accept_indexes=True, accept_commands=True)
                if inp.is_quit_key:
                    break
                my_card = inp.value
                self.game.ai_player.display_cards()
                inp = PlayerInput()
                inp.input_loop(self.game.ai_player.nb_cards, msg='Which card do you wanna peek? ', accept_indexes=True)
                other_card = inp.value
                super()._trigger_jack_effect(my_card, other_card, self.game.ai_player.cards)

            if card.rank == Rank.QUEEN:
                inp = PlayerInput()
                inp.input_loop(self.game.ai_player.nb_cards, msg='Which card do you wanna see? ', accept_indexes=True, accept_commands=True)
                if inp.is_quit_key:
                    break
                hidden_card_index = inp.value
                super()._trigger_queen_effect(hidden_card_index)
                self.display_cards(visible_cards=[hidden_card_index])
                self.game.set_should_display_cards(False)

    def display_cards(self, visible_cards: List[int]=[]):
        print(Colors.BOLD)
        print('Your cards')
        super().display_cards(visible_cards=visible_cards)

    def _display_deck_card(self, card: Card):
        print(Colors.OKCYAN)
        super()._display_deck_card(card)

class AIPlayer(PlayerI):
    def __init__(self, game):
        super().__init__(game)

    def play(self, deck_card):
        def get_best_hit_index(cards: List[Card], rank_to_ignore: Rank=None) -> int:
            """ returns the index of the card with the worst value.
            Does not take into account the duplicates.
            """
            worst, worst_idx = cards[0].rank.value, 0
            for i in range(1, len(cards)):
                c = cards[i]
                # if we have a queen and we also have 1 or more hidden cards
                if c.rank == Rank.QUEEN and len(self._hidden_cards) >= 1:
                    return i
                occurences = self.game.nb_occurences_in_deck(c.rank)
                # if only 1 or 2 card are remaining in the deck
                if occurences in [1, 2] and not is_a_great_card(c):
                    return i
                # get rank with highest value
                if c.rank.value > worst and c.rank != rank_to_ignore:
                    worst, worst_idx = c.rank.value, i
            return worst_idx

        def get_worst_combinaison_of_cards_index(cards: List[Card]) -> int:
            """ returns the index of the card which when played
            will lose the most points. Takes into account the duplicate
            cards which will lose more points.
            """
            card_values = defaultdict(int)
            for i in range(len(cards)):
                c = cards[i]
                card_values[c.rank.value] += c.rank.value
            max_combinaison_rank = max(card_values.items(), key=operator.itemgetter(1))[0]
            print(card_values.items())
            print(max_combinaison_rank)
            first_idx = next(i for i in range(len(cards)) if cards[i].rank.value == max_combinaison_rank)
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
            return next(iter(self._hidden_cards)) if len(self._hidden_cards) > 0 else -1

        def apply_card_effects(
            thrown_cards: List[Card], 
            cards: List[Card],
            other_player_cards: List[Card],
            deck_card: Card):
            def apply_jack_effect(thrown_cards: List[Card], cards: List[Card], other_player_cards: List[Card]):
                """ apply effect on all jack cards.
                """
                already_peeked_indexes = []
                for c in thrown_cards:
                    if c.rank == Rank.JACK and self.game.player.is_kobo: # only use the jack when the other is jack
                        random_index = get_random_card_index(other_player_cards, already_peeked_indexes)
                        already_peeked_indexes.append(random_index)
                        worst_card_idx = get_worst_combinaison_of_cards_index(cards)
                        self._trigger_jack_effect(worst_card_idx, random_index, thrown_cards)

            def apply_queen_effect(thrown_cards: List[Card], cards: List[Card], deck_card: Card):
                """ apply effect on all queen cards.
                """
                cards = cards.copy() + [deck_card]
                for c in thrown_cards:
                    if c.rank == Rank.QUEEN:
                        for i in range(len(cards)):
                            card = cards[i]
                            if not card.is_discovered():
                                print(f'DISCOVER {card}')
                                self._trigger_queen_effect(i)
                                break

            apply_jack_effect(thrown_cards, cards, other_player_cards)
            apply_queen_effect(thrown_cards, cards, deck_card)

        def is_a_great_card(card: Card) -> bool:
            r = card.rank
            return r == Rank.TEN or r == Rank.ACE or r == Rank.TWO

        def check_kobo(cards: List[Card]) -> bool:
            for c in cards:
                if not is_a_great_card(c):
                    return False
            return True
            
        def throw_deck_card(deck_card: Card):
            """ plays the peeked deck card.
            Applies substitutions and effects on cards.
            """
            thrown_cards = self._do_not_substitute_card(deck_card)
            apply_card_effects(thrown_cards, self.cards, self.game.ai_player.cards, deck_card)
            if check_kobo(self.cards):
                self.is_kobo = True
            return thrown_cards

        def throw_player_card(card_index: int, deck_card: Card):
            """ plays a card within the cards of the player.
            Applies substitutions and effects on cards.
            """
            thrown_cards = self._substitute_card(card_index, deck_card)
            apply_card_effects(thrown_cards, self.cards, self.game.ai_player.cards, deck_card)
            if check_kobo(self.cards):
                self.is_kobo = True
            return thrown_cards


        player = self.game.player
        cards = [c for c in self.cards if c.is_discovered()]
        hidden_card_index = get_hidden_card_index(self.cards)

        # handle kobo
        if player.is_kobo:
            if deck_card.rank == Rank.JACK: # deck card is jack
                return throw_deck_card(deck_card)
            else:
                jack_index = get_first_card_index(cards, Rank.JACK)
                if jack_index == -1: # found a jack in cards
                    return throw_player_card(jack_index, deck_card)
        
        # handle queen
        if deck_card.rank == Rank.QUEEN:
            print('QUEEN DECK')
            return throw_deck_card(deck_card)
        else:
            queen_index = get_first_card_index(cards, Rank.QUEEN)
            if queen_index != -1: # found a queen
                if hidden_card_index != -1: # found 1 hidden card
                    print('QUEEN CARDS')
                    return throw_player_card(queen_index, deck_card)

        # handle hidden cards discover
        if hidden_card_index != -1: # found a hidden card
            print('HIDDEN')
            return throw_player_card(hidden_card_index, deck_card)
        
        # handle every cards are great
        cards_with_deck_card = cards + [deck_card]
        best_hit_index = get_best_hit_index(cards_with_deck_card)
        best_hit_card = cards_with_deck_card[best_hit_index]
        if is_a_great_card(best_hit_card): # all cards are great
            self.is_kobo = True
            best_hit_index = get_worst_combinaison_of_cards_index(cards_with_deck_card)
            if best_hit_index == len(cards_with_deck_card) - 1: # best hit is the deck card
                print('KOBO DECK')
                return throw_deck_card(deck_card)
            else:
                print('KOBO CARDS')
                return throw_player_card(best_hit_index, deck_card)

        # handle deck card is a card we already have
        deck_card_index = get_first_card_index(cards, deck_card.rank)
        if deck_card_index != -1 and not is_a_great_card(deck_card):
            print('ALREADY HAVE THIS CARD')
            return throw_deck_card(deck_card)

        # default turn
        best_hit_index = get_best_hit_index(cards_with_deck_card)
        if best_hit_index == len(cards_with_deck_card) - 1: # best hit is the deck card
            print('CLASSIC DECK')
            return throw_deck_card(deck_card)
        else:
            print('CLASSIC CARDS')
            return throw_player_card(best_hit_index, deck_card)
        

    def display_cards(self, visible_cards: List[int]=[]):
        print(Colors.BOLD)
        print(Colors.FAIL)
        print('AI cards')
        super().display_cards(visible_cards=visible_cards)
        print(Colors.ENDC)

    def _display_deck_card(self, card: Card):
        print(Colors.FAIL)
        super()._display_deck_card(card)


g = Game()
g.launch()