"""backgState.py

A state class for the game of Backgammon.
S. Tanimoto, updated April 17, 2020.

"""
import random

W = 0
R = 1


def get_color(who):
    return ['White', 'Red'][who]


class bgstate:
    def __init__(self, old=None):
        """If called with an existing state ("old"), we'll create a
        deep copy of that state.  Otherwise, we create the initial
        state of the game."""
        if old:
            self.pointLists = [lst[:] for lst in old.pointLists]
            # pointLists is 2d array that represents the board.
            # pointLists[0] holds the checkers at position 1, pointLists[1] represents the checks at position 2, etc.
            # pointLists[n] might be [0, 0, 0, 0]. This would mean there are 4 white checkers at board position (n+1)
            self.bar = old.bar[:]  # the bar holds the "captured" pieces.
            self.white_off = old.white_off[:]  # holds the white checkers that have been removed (aka finished).
            self.red_off = old.red_off[:]  # holds the red checkers that have been removed.
            self.cube = old.cube  # unused
            self.offering_double = old.offering_double  # unused
            self.whose_move = old.whose_move  # tracks who's turn it is. will be 0 or 1.
            self.next_move = old.next_move  # tracks the next move that will be computed  mainly for GUI
            self.next_roll = old.next_roll  # tracks the next dice roll. Mainly for GUI
        else:
            self.bar = []
            self.white_off = []
            self.red_off = []
            self.cube = 1
            self.offering_double = False
            self.whose_move = W
            self.next_move = None
            self.next_roll = None
            self.pointLists = [
              [W, W],
              [],
              [],
              [],
              [],
              [R, R, R, R, R],
              [],
              [R, R, R],
              [],
              [],
              [],
              [W, W, W, W, W],
              [R, R, R, R, R],
              [],
              [],
              [],
              [W, W, W],
              [],
              [W, W, W, W, W],
              [],
              [],
              [],
              [],
              [R, R]]

    # changed 6.18.20 - Alex: Spaced out prettyPrint so numbers were more visible.
    # used in gamemaster.py() for console output.
    def pretty_print(self):
        top_numbers = " 13 14 15 16 17 18   19 20 21 22 23 24 \n"
        bottom_numbers = " 12 11 10  9  8  7   6  5  4  3  2  1 \n"
        hline = "+------------------+------------------+\n"
        s = top_numbers + hline
        point_lengths = [len(l) for l in self.pointLists]
        top_max_checkers = 0
        for i in range(12, 24):
            top_max_checkers = max(top_max_checkers, point_lengths[i])
        # print("top_max_checkers = ", top_max_checkers)

        for j in range(top_max_checkers):
            line = '|'
            for i in range(12, 24):
                if j < point_lengths[i]:
                    if self.pointLists[i][0] == W:
                        line += ' W '
                    else:
                        line += ' R '
                else:
                    line += '   '
                if i == 17:
                    line += '|'
            s += line + '|\n'
        bottom_max_checkers = 0
        for i in range(11, -1, -1):
            bottom_max_checkers = max(bottom_max_checkers, point_lengths[i])
        sb = ''
        for j in range(bottom_max_checkers):
            line = '|'
            for i in range(11, -1, -1):
                if j < point_lengths[i]:
                    if self.pointLists[i][0] == W:
                        line += ' W '
                    else:
                        line += ' R '
                else:
                    line += '   '
                if i == 6:
                    line += '|'
            sb = line + '|\n' + sb

        # print("bottom_max_checkers = ", bottom_max_checkers)
        s += hline + sb + hline + bottom_numbers

        if len(self.bar) > 0:
            line = 'bar:'
            for c in self.bar:
                if c == W:
                    line += 'W'
                elif c == R:
                    line += 'R'
            line += '\n'
            s += line
        if len(self.white_off) > 0:
            line = 'White off:'
            for c in self.white_off:
                if c == W:
                    line += 'W'
                elif c == R:
                    line += 'R'
            line += '\n'
            s += line
        if len(self.red_off) > 0:
            line = 'Red off:'
            for c in self.red_off:
                if c == W:
                    line += 'W'
                elif c == R:
                    line += 'R'
            line += '\n'
            s += line
        # if self.whose_move==W:
        #  line2 = "Next it's White's turn.\n"
        # else:
        #  line2 = "Next it's Red's turn.\n"
        # s += line2 + '===============================================\n'
        s += '===============================================\n'
        return s


def toss(deterministic=False):
    if deterministic:
        return 1, 6
    die1 = random.choice(range(1, 7))
    die2 = random.choice(range(1, 7))
    return die1, die2


if __name__ == '__main__':
    INITIAL_STATE = bgstate()
    print(INITIAL_STATE.pretty_print())
