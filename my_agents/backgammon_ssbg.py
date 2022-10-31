'''
Name(s):
UW netid(s):
'''

from game_engine import genmoves
import math

class BackgammonPlayer:
    def __init__(self):
        self.GenMoveInstance = genmoves.GenMoves()
        self.ply = 2
        self.eval = True
        self.specialStaticFunc = None
        # feel free to create more instance variables as needed.

    # TODO: return a string containing your UW NETID(s)
    # For students in partnership: UWNETID + " " + UWNETID
    def nickname(self):
        # TODO: return a string representation of your UW netid(s)
        return "kong314 taylorkw"

    # Given a ply, it sets a maximum for how far an agent
    # should go down in the search tree. Count the chance nodes
    # as a ply too!
    def setMaxPly(self, maxply=2):
        # TODO: set the max ply
        self.ply = maxply

    # If not None, it update the internal static evaluation
    # function to be func
    def useSpecialStaticEval(self, func):
        # TODO: update your staticEval function appropriately
        if func is None:
            self.eval = False
            self.specialStaticFunc = func
        else:
            self.eval = True

    def initialize_move_gen_for_state(self, state, who, die1, die2):
        self.move_generator = self.GenMoveInstance.gen_moves(state, who, die1, die2)

    # Given a state and a roll of dice, it returns the best move for
    # the state.whose_move
    # Keep in mind: a player can only pass if the player cannot move any checker with that role
    def move(self, state, die1, die2):
        # TODO: return a move for the current state and for the current player.
        # Hint: you can get the current player with state.whose_move

        best_move = 'p'
        self.initialize_move_gen_for_state(state, state.whose_move, die1, die2)
        list_moves = self.get_moves()
        if len(list_moves) == 0:
            return best_move

        for move in list_moves:
            best_white = -math.inf
            best_red = math.inf
            if move != 'p':
                if state.whose_move == 0:
                    score = self.expectimax(state, state.whose_move, die1, die2, self.ply, False)
                    if score > best_white:
                        best_white = score
                        best_move = move[0]
                elif state.whose_move == 1:
                    score = self.expectimax(state, state.whose_move, die1, die2, self.ply, False)
                    if score < best_red:
                        best_red = score
                        best_move = move[0]
        return best_move

    # Expectimax algorithm
    def expectimax(self, state, whose_turn, die1, die2, ply, expect):
        if ply == 0:
            if not self.eval:
                return self.specialStaticFunc(state)
            else:
                return self.staticEval(state)

        # If we are on a turn where a move may not be optimal, expect will be true and we find average static
        # evaluation of all moves
        if expect:
            score = 0
            num_moves = 0
            for i in range(1, 7):
                for j in range(1, 7):
                    self.initialize_move_gen_for_state(state, whose_turn, die1, die2)
            possible_moves = self.get_moves()
            for move in possible_moves:
                if move != 'p':
                    num_moves += 1
                    score += self.expectimax(move[1], whose_turn, die1, die2, ply - 1, not expect)
            score /= num_moves
            return score
        else:
            if whose_turn == 0:
                best_score = -math.inf
                self.initialize_move_gen_for_state(state, whose_turn, die1, die2)
                possible_moves = self.get_moves()
                for move in possible_moves:
                    if move != 'p':
                        score = self.expectimax(move[1], not whose_turn, die1, die2, ply - 1, not expect)
                        if score > best_score:
                            best_score = score
                return best_score
            elif whose_turn == 1:
                best_score = math.inf
                self.initialize_move_gen_for_state(state, whose_turn, die1, die2)
                possible_moves = self.get_moves()
                for move in possible_moves:
                    if move != 'p':
                        score = self.expectimax(move[1], not whose_turn, die1, die2, ply - 1, not expect)
                        if score < best_score:
                            best_score = score
                return best_score

    def get_moves(self):
        """Uses the mover to generate all legal moves. Returns an array of move commands"""
        move_list = []
        done_finding_moves = False
        any_non_pass_moves = False
        while not done_finding_moves:
            try:
                m = next(self.move_generator)    # Gets a (move, state) pair.
                # print("next returns: ",m[0]) # Prints out the move.    For debugging.
                if m[0] != 'p':
                    any_non_pass_moves = True
                    move_list.append(m)    # Add the move to the list.
            except StopIteration as e:
                done_finding_moves = True
        if not any_non_pass_moves:
            move_list.append('p')
        return move_list

    # Hint: Look at game_engine/boardState.py for a board state properties you can use.
    def staticEval(self, state):
        # TODO: return a number for the given state
        eval = 0
        can_bear_white = 0 # how many of whites pieces are in the inner board
        can_bear_red = 0 # how many of reds pieces are in the inner board
        for i in range(0, 24):
            if len(state.pointLists[i]) != 0:
                if state.pointLists[i][0] == 0:
                    eval += (25 - (i + 1)) * len(state.pointLists[i]) # summing how many spots off white is
                    if i in range(19, 25):
                        can_bear_white += len(state.pointLists[i])
                elif state.pointLists[i][0] == 1:
                    eval -= (i + 1) * len(state.pointLists[i]) # summing how many spots off red is
                    if i in range(1, 7):
                        can_bear_red -= len(state.pointLists[i])

        # Add points to eval if the move causes other player to move a piece to the bar
        if len(state.bar) > 0:
            if state.bar[0] == 0:
                eval += 50 * len(state.bar)
            elif state.bar[0] == 1:
                eval -= 50 * len(state.bar)

        # checking if all white/red pieces are in inner board and can start to bear off
        if can_bear_white == 15:
            eval += 25
        if can_bear_red == 15:
            eval -= 25
        return eval