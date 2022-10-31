'''
Name(s): Kaiden Ong, Taylor Woodward
UW netid(s): kong314, taylorkw
'''

import math

from game_engine import genmoves


class BackgammonPlayer:

    def __init__(self):
        self.GenMoveInstance = genmoves.GenMoves()
        self.ply = 2
        self.eval = True
        self.specialStaticFunc = None
        self.states_explored = 0
        self.move_generator = None
        self.prune = True
        self.num_cutoffs = 0
        # feel free to create more instance variables as needed.

    # TODO: return a string containing your UW NETID(s)
    # For students in partnership: UWNETID + " " + UWNETID
    def nickname(self):
        # TODO: return a string representation of your UW netid(s)
        return "kong314 taylorkw"

    # If prune==True, then your Move method should use Alpha-Beta Pruning
    # otherwise Minimax
    def useAlphaBetaPruning(self, prune=False):
        # TODO: use the prune flag to indiciate what search alg to use
        self.states_explored = 0
        self.num_cutoffs = 0
        self.prune = prune

    def abp(self, state, whose_turn, ply, alpha, beta):
        if ply == 0:
            if not self.eval:
                return self.specialStaticFunc(state)
            else:
                return self.staticEval(state)

        if whose_turn == 0:
            best_score = -math.inf
            self.initialize_move_gen_for_state(state, whose_turn, 1, 6)
            possible_moves = self.get_moves()
            for move in possible_moves:
                self.states_explored += 1
                if move != 'p':
                    score = self.abp(move[1], not whose_turn, ply - 1, best_score, beta)
                    if best_score > beta:
                        self.num_cutoffs += 1
                        return beta
                    if score > best_score:
                        best_score = score
            return best_score
        elif whose_turn == 1:
            best_score = math.inf
            self.initialize_move_gen_for_state(state, whose_turn, 1, 6)
            possible_moves = self.get_moves()
            for move in possible_moves:
                self.states_explored += 1
                if move != 'p':
                    score = self.abp(move[1], not whose_turn, ply - 1, alpha, best_score)
                    if best_score < alpha:
                        self.num_cutoffs += 1
                        return alpha
                    if score < best_score:
                        best_score = score
            return best_score

    # Returns a tuple containing the number explored
    # states as well as the number of cutoffs.
    def statesAndCutoffsCounts(self):
        # TODO: return a tuple containing states and cutoff
        return self.states_explored, self.num_cutoffs

    # Given a ply, it sets a maximum for how far an agent
    # should go down in the search tree. maxply=2 indicates that
    # our search level will go two level deep.
    def setMaxPly(self, maxply=2):
        # TODO: set the max ply
        self.ply = maxply

    # If not None, it updates the internal static evaluation
    # function to be func
    def useSpecialStaticEval(self, func):
        # TODO: update your staticEval function appropriately
        if func is None:
            self.eval = False
            self.specialStaticFunc = func
        else:
            self.eval = True

    # Given a state and a roll of dice, it returns the best move for
    # the state.whose_move.
    # Keep in mind: a player can only pass if the player cannot move any checker with that role
    def move(self, state, die1=1, die2=6):
        # TODO: return a move for the current state and for the current player.
        # Hint: you can get the current player with state.whose_move
        print(self.statesAndCutoffsCounts())

        best_move = 'p'
        self.initialize_move_gen_for_state(state, state.whose_move, die1, die2)
        list_moves = self.get_moves()
        if len(list_moves) == 0:
            return best_move

        for move in list_moves:
            best_white = -math.inf
            best_red = math.inf
            self.states_explored += 1
            if move != 'p':
                if state.whose_move == 0:
                    if self.prune:
                        score = self.abp(move[1], not state.whose_move, self.ply, best_white, best_red)
                    else:
                        score = self.minimax(move[1], not state.whose_move, self.ply)
                    if score > best_white:
                        best_white = score
                        best_move = move[0]
                elif state.whose_move == 1:
                    if self.prune:
                        score = self.abp(move[1], not state.whose_move, self.ply, best_white, best_red)
                    else:
                        score = self.minimax(move[1], not state.whose_move, self.ply)
                    if score < best_red:
                        best_red = score
                        best_move = move[0]
        return best_move

    def minimax(self, state, whose_turn, ply):
        if ply == 0:
            if not self.eval:
                return self.specialStaticFunc(state)
            else:
                return self.staticEval(state)

        if whose_turn == 0:
            best_score = -math.inf
        elif whose_turn == 1:
            best_score = math.inf
        self.initialize_move_gen_for_state(state, whose_turn, 1, 6)
        possible_moves = self.get_moves()

        for move in possible_moves:
            self.states_explored += 1
            if move != 'p':
                score = self.minimax(move[1], not whose_turn, ply - 1)
                if(whose_turn == 0 and score > best_score) or (whose_turn == 1 and score < best_score):
                    best_score = score
        return best_score

    def initialize_move_gen_for_state(self, state, who, die1, die2):
        self.move_generator = self.GenMoveInstance.gen_moves(state, who, die1, die2)

    # get all moves based on die rolls
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
        eval = 0
        can_bear_white = 0  # how many of whites pieces are in the inner board
        can_bear_red = 0  # how many of reds pieces are in the inner board
        for i in range(0, 24):
            if len(state.pointLists[i]) != 0:
                if state.pointLists[i][0] == 0:
                    eval += (25 - (i + 1)) * len(state.pointLists[i])  # summing how many spots off white is
                    if i in range(19, 25):
                        can_bear_white += len(state.pointLists[i])
                elif state.pointLists[i][0] == 1:
                    eval -= (i + 1) * len(state.pointLists[i])  # summing how many spots off red is
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