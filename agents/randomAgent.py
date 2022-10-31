"""SkeletonAgent.py
This file defines a class BackgammonPlayer.
Instantiating this class creates an "agent"
that implements the introduce method and
the move method, and is capable of making
a legal move, but will not make any
effort to choose a good move.

S. Tanimoto, April 17, 2020.
 The get_all_moves function was updated April 24
so it only includes the pass move 'p' if there are
no other moves.

"""

# Access to the state class is not needed in the
# starter version of this agent.
# from boardState import *

from game_engine import genmoves
import random    # Used in the "move_randomly" method.


class BackgammonPlayer:
    def __init__(self):
        self.GenMoveInstance = genmoves.GenMoves()

    def introduce(self):
        return "I\'m random."

    def nickname(self):
        return "Random"

    def initialize_move_gen_for_state(self, state, who, die1, die2):
        self.move_generator = self.GenMoveInstance.gen_moves(state, who, die1, die2)

    def move(self, state, die1, die2):
        self.initialize_move_gen_for_state(state, state.whose_move, die1, die2)
        # return self.get_first_move()
        # return self.get_last_move()
        return self.move_randomly()

    def get_first_move(self):
        """Uses the mover to generate only one move."""
        try:
            m = next(self.move_generator)    # Gets a (move, state) pair.
            # print("next returns: ", m[0])    # Prints out the move.    For debugging.
            return m[0]    # Returns the move.
        except StopIteration as e:
            print("Exception generating the next move.")
            print(e)
            return "NO_MOVES"

    def get_last_move(self):
        """Chooses the last of the legal moves."""
        moves = self.get_all_moves()
        if len(moves) == 0:
            return "NO MOVES COULD BE FOUND"
        return moves[-1]

    def get_all_moves(self):
        """Uses the mover to generate all legal moves."""
        move_list = []
        done_finding_moves = False
        any_non_pass_moves = False
        while not done_finding_moves:
            try:
                m = next(self.move_generator)    # Gets a (move, state) pair.
                # print("next returns: ",m[0]) # Prints out the move.    For debugging.
                if m[0] != 'p':
                    any_non_pass_moves = True
                    move_list.append(m[0])    # Add the move to the list.
            except StopIteration as e:
                done_finding_moves = True
        if not any_non_pass_moves:
            move_list.append('p')
        return move_list

    def move_randomly(self):
        moves = self.get_all_moves()
        if len(moves) == 0:
            return "NO MOVES COULD BE FOUND"
        return random.choice(moves)
