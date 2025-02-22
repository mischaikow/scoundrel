import random
from collections import deque
from enum import Enum

VALUE_MAPPING = {
    "A": 14,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
}


class Suit(Enum):
    spade = "♠"
    heart = "♥"
    diamond = "♦"
    club = "♣"


class Card:
    def __init__(self, suit, value_string):
        self.suit = suit
        self.value_string = value_string

    def __repr__(self) -> str:
        if self.suit == Suit.heart or self.suit == Suit.diamond:
            return (
                TextFormat.RED
                + self.value_string
                + "-"
                + self.suit.value
                + TextFormat.END
            )
        return self.value_string + "-" + self.suit.value

    def return_score(self) -> int:
        return VALUE_MAPPING[self.value_string]


class Deck:
    def __init__(self):
        self.cards = self.generate_cards()

    def generate_cards(self):
        cards = []
        for suit in Suit:
            for i in range(2, 11):
                cards.append(Card(suit, str(i)))

        for i in ["A", "J", "Q", "K"]:
            cards.append(Card(Suit.spade, i))
            cards.append(Card(Suit.club, i))

        random.shuffle(cards)
        return deque(cards)

    def deck_size(self) -> int:
        return len(self.cards)

    def draw_card(self) -> Card:
        if len(self.cards) == 0:
            return None
        return self.cards.popleft()

    def bottom_card(self, card: Card) -> None:
        self.cards.append(card)

    def bottom_card_list_random(self, cards) -> None:
        random.shuffle(cards)
        for a_card in cards:
            self.bottom_card(a_card)


class Game:

    def __init__(self):
        self.deck = Deck()
        self.cards_played = set()

        self.board = []

        self.weapon: int = None
        self.weapon_defeat_stack = []

        self.room = 0
        self.health = 20

        self.skipped_last_room = False

        self.game_ended = False

        self.next_room()

    # Drawing cards
    def draw_card(self):
        top_card = self.deck.draw_card()
        if top_card is None:
            self.game_ends()

        self.board.append(top_card)

    def next_room(self):
        if len(self.board) > 1:
            self.deck.bottom_card_list_random(self.board)
            self.board = []
            self.skipped_last_room = True
        else:
            self.skipped_last_room = False

        while len(self.board) < 4:
            self.draw_card()

        self.room += 1

    # Playing the game
    def play(self, user_input: str) -> None:
        if user_input.isdigit():
            self.card_play(int(user_input))
        elif user_input == "skip":
            self.next_room()
        elif user_input == "game over":
            self.game_ends()
        else:
            print("PANIC")

    def card_play(self, card_index: int) -> None:
        played_card = self.board.pop(card_index)
        self.cards_played.add(played_card)

        if played_card.suit == Suit.diamond:
            self.diamond_play(played_card)
        elif played_card.suit == Suit.heart:
            self.heart_play(played_card)
        else:
            self.black_play(played_card)

        if len(self.board) == 1:
            self.next_room()

    def diamond_play(self, card: Card) -> None:
        self.weapon = card.return_score()
        self.weapon_defeat_stack = []

    def heart_play(self, card: Card) -> None:
        self.health = min(20, self.health + card.return_score())

    def black_play(self, card: Card) -> None:
        if self.weapon is None:
            self.health -= card.return_score()
        elif (
            len(self.weapon_defeat_stack) == 0
            or self.weapon_defeat_stack[-1].return_score() > card.return_score()
        ):
            self.health -= max(0, card.return_score() - self.weapon)
            self.weapon_defeat_stack.append(card)
        else:
            self.health -= card.return_score()

    # Information displays

    # Game status
    def is_game_over(self) -> bool:
        if self.game_ended:
            return True

        if self.deck.deck_size() == 0:
            self.game_ends()
            print("you escaped!")
            return True

        if self.health <= 0:
            self.game_ends()
            print("you died.")
            return True

        return False

    def game_ends(self):
        self.game_ended = True


##  Command line interface
# Printing
class TextFormat:
    RED = "\033[31m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_board(game: Game) -> str:
    board_display = ""
    for i in range(len(game.board)):
        board_display += str(i + 1)
        board_display += "["
        board_display += "\033[1m" + str(game.board[i]) + "\033[0m"
        board_display += "]  "
    return board_display


def print_defeat_stack(game: Game) -> str:
    return "  ".join([str(x) for x in game.weapon_defeat_stack])


def print_game_weapon(game: Game) -> str:
    if game.weapon is None:
        return TextFormat.BOLD + "Unarmed" + TextFormat.END

    defeat_stack_string = ""
    if len(game.weapon_defeat_stack) > 0:
        defeat_stack_string = ":"
        defeat_stack_string += " ".join(
            x.value_string for x in game.weapon_defeat_stack
        )

    return TextFormat.BOLD + str(game.weapon) + TextFormat.END + defeat_stack_string


def print_health(game: Game) -> str:
    return TextFormat.BOLD + str(game.health) + TextFormat.END


def print_game_state(game: Game) -> None:
    print(f"    Room {game.room}")
    print()
    print(f" Contains:")
    print(f"    {print_board(game)}")
    print()
    print(f" Weapon:")
    print(f"    {print_game_weapon(game)}")
    print()
    print(f"Health:  {print_health(game)} / 20")
    print()
    print(game.cards_played)


# Input management
def print_skip_room_option(game: Game) -> str:
    if game.skipped_last_room:
        return "You cannot skip this room"
    return "Type 'S' to skip room"


def print_card_choices(game: Game) -> str:
    return f", pick card 1-{len(game.board)}"


def read_input(game: Game) -> str:
    while True:
        print(
            print_skip_room_option(game)
            + print_card_choices(game)
            + ", or 'Q' to quit"
            + ": "
        )

        next_action = input()

        if (
            next_action.isdigit()
            and 0 < int(next_action)
            and int(next_action) <= len(game.board)
        ):
            return str(int(next_action) - 1)
        elif next_action == "s" or next_action == "S":
            if game.skipped_last_room:
                print("Not allowed to skip")
            else:
                return "skip"
        elif next_action == "q" or next_action == "Q":
            return "game over"


game = Game()
while not game.is_game_over():
    print()
    print_game_state(game)
    user_input = read_input(game)
    game.play(user_input)
