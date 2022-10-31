"""gamemaster.py

A simple game master program for Simplified Backgammon.

To use this program, edit the import statements below to import your
preferred playing agents, and set the time limit per move.

Then run the program under Python 3.x from a command line:
python3 gamemaster.py

The rules of the game are simplified for this version of Backgammon.
A. WHITE always plays first, so there is no initial rolling and
   requirement that the first player use the initial roll.
B. No doubling allowed. "Cube value" is therefore always 1.
C. A player may pass on any turn, in either of two ways:
     -- Pass on the whole turn.
     -- Pass on moving a second checker.
D. If no move is available to a player on its turn, then it MUST pass
   or forfeit the game.  If it can move only one checker, then it
   should do that and pass for the second checker.
E. If the dice come out doubles (like a pair of sixes), then unlike
   standard backgammon, where the player can move 4 checkers, we
   don't allow any special bonus.
F. Standard backgammon has a rule that if a player can only use one
   of the two dice, the player must use the larger number.  We do not
   follow that rule.  Either number may be used.
G. No special rules are in effect, like the Crawford rule, since
   we don't use the doubling cube.

This game master is very strict, in terms of requiring that the
playing agents describe legal moves.  If the game master detects
anything wrong with a player's move, the game ends and the player
with the questionable move forfeits the game.

Time limits are not implemented so just ignored in this version.

Includes a feature in deterministic mode that checks for 3 passes in
a row (no changes to the state except change of whose turn 3 times).
If this happens, the game is terminated and declared to be a tie.

Last updated April 24, 2020, to fix the checking whether moves exist
when a player passes.

Helpful notes on reading this code:
A "move" is a string that indicates the position of the checkers to be
moved and it is split into up to 3 parts: the position of the first checker
to be moved, the postion of the second checker to be moved, and
potentially a third "reverse" command.
So, '6,9' would mean that the checker at index 6 will be moved, followed by
the checker at index 9 which is moved next. To determine how far they
will move, look at the dice roll: the first dice is applied to the first
checker and the second dice roll is applied to the second checker.
So if we have move = '6,9' and dice = [1, 6] then the end positions of the
two checkers would be 7 and 15 (derived from 6+1 and 9+6 respectively).

In a move command, there are a few special characters:
1. 'p', which can replace an indices of a checker. It means that checker
"passes", aka it ignores the corresponding dice roll and doesn't move.
Ex. '6,p' given the roll [1, 6] results in the first checker moving to 7
but no other change (so the second roll of 6 is dropped).

2. 'q', which means quit. Primarily a user inputted command (your player
should never quit), this means the player gives up and wants to exit the game.

3. 'r', flips the values of the dice, so that the first checker is moved by
the second dice roll  and the second checker is moved by
the first dice roll.
Ex. to compute move '10,4,r' with dice rolls [1, 6], we compute that the
checker at position 10 gets +6 and the checker at position 4 gets +1, so the
final result of '10,4,r' + rolls [1,6] will be checkers at positions 16 and 5.

**IMPLEMENTATION DETAIL**
2. Again, note that to compute 'r', the dice values are flipped, NOT the checker positions.
Consider '8,7,r' with [1,6] and '7,8' with [1,6] (aka we flipped the checker positions
instead than the dice values like we were supposed to):
In '8,7,r' with [1,6], the checker at 8 gets +6, then the checker at 7 gets +1, so
we have final positions (14, 8).
In '7,8' with [1,6], the checker at 7 gets +1, then the checker at 8 gets +6.
So we might get (8, 14) if there were two checkers that moved, which is the opposite
of what we wanted. Additionally, in this case specifically, the second checker at 8
could be the same checker as the first! 7 goes to 8, then goes to 14. So with this case
(but not the other!), the checker at 7 could've have moved twice. So '7,8' with [1,6]
does not require 2 distinct checkers, while '8,7,r' with [1,6] does.
So to handle 'reverse', be sure to flip dice values, NOT checker positions.

1. There is duplicate methods in this class and in genmoves.py. Some of the methods
in genmoves.py do not seem to be the finished versions (as they were slightly different
from the original code in this method), but I don't know which to keep.
"""


from game_engine import genmoves
from game_engine.boardState import *
import copy
GENMOVES_INSTANCE = genmoves.GenMoves()
DONE = False

# Below are the agents used in "Play Offline"
# To change, simply add an import and change p1 or p2 to desired Agent
from agents import randomAgent, SkeletonAgent, backgammon_dsbg, backgammon_ssbg
##agent1 represents the white checkers and agent2 the red checkers
agent1 = backgammon_dsbg.BackgammonPlayer()
agent2 = SkeletonAgent.BackgammonPlayer()

DETERMINISTIC = True  # deterministic version: dice are loaded to give 1 and 6
# stochastic version (DETERMINISTIC = false): dice are rolled normally.

def run(white_player, red_player, max_secs_per_move, deterministic, print_to_console, initial_state):
    """Start and monitor a game of Simplified Backgammon.
    The two players are white and red, which must be instances of a class
    that implements method named "move".
    max_secs_per_move is the time limit.  If it's 0, then no time limit.
    initial_state is a function that should return a valid state
    from which the game should start.  The default is to start from the
    beginning -- the standard starting board for Backgammon.
    If deterministic is True, then instead of rolling dice randomly,
    fixed values (1, 6) come back.  This allows a variation of the game
    in which alpha-beta pruning makes sense.

    If print_to_console is true, the full game state of each turn will be printed.
    If set to false, only the final result is printed (White/Red won, or Tie game).
    """
    game_record = []  # is a list of all the game states.

    if print_to_console:
        print_game_intro(red_player, white_player)

    global DONE
    pass_count = 0  # Number of consecutive (full) passes. If 3,
    # and in deterministic mode, the game ends.
    turn_count = 0
    if initial_state:
        state = initial_state
    else:
        state = bgstate(None)

    winner = -1  # -1 = tie, 0 = white, 1 = red
    # this while loop runs the game.
    while not DONE:
        if print_to_console:
            print("computing turn " + str(turn_count))
        turn_count += 1

        # turn variables
        whose_move = state.whose_move

        die1, die2 = toss(deterministic)  # returns 2 dice rolls
        if print_to_console:
            print("\n After turn", turn_count, "the current state is:")
            print(state.pretty_print())
            print(get_color(whose_move) + ' to play...')
            print("The dice roll gives: " + str(die1) + ', ' + str(die2))

        # Each turn, one player gets to make a move.
        if whose_move == W:
            move = white_player.move(state, die1, die2)
        else:
            move = red_player.move(state, die1, die2)
        state.next_move = move

        if print_to_console:
            print(get_color(whose_move), "move command:", move)

        handle_special = check_for_special_move(move, state, die1, die2, deterministic, pass_count, print_to_console)
        if handle_special == "FORFEIT":
            # The player tried to make an invalid move, both players have passed 3 times in a row, or a player
            # uses the manual forfeit command (depreciated)
            print(get_color(state.whose_move) + " forfeited (" + str(turn_count) + " turns occurred.)")
            forfeit(whose_move, print_to_console)
            winner = 1 - whose_move
            break
        elif handle_special == "TIE":
            print("Game computed: Tie game. (" + str(turn_count) + " turns occurred.)")
            break
        elif handle_special == "PASS":
            # the only choice for the active player had was to double pass (p,p)
            # The other player may have moves available, so the game continues.
            pass_count += 1
            state.next_roll = [die1, die2]
            game_record.append(copy.deepcopy(state))

            state.whose_move = 1 - state.whose_move
        else:
            # The player had given a normal (or a reversed) move.
            if handle_special == "REVERSE":
                dice = [die2, die1]
            else:
                dice = [die1, die2]

            state.next_roll = dice
            game_record.append(copy.deepcopy(state))

            pass_count = 0
            if print_to_console:
                pretty_print_move(move, dice)
            checker_positions = move.split(",")
            state = handle_move([checker_positions[0], checker_positions[1]], state, dice, print_to_console)
            if type(state) == tuple and len(state) == 2 and state[0] == "FORFEIT":
                # If the player attempted an invalid move, they lose the game.
                print("Game computed: " + get_color(whose_move) + " forfeited " + "("
                      + str(turn_count) + " turns occurred.) due to " + state[1])
                forfeit(whose_move, False)
                winner = 1 - whose_move
                break

            if win_detected(state, state.whose_move):
                if print_to_console:
                    print(state.pretty_print())
                print("Game computed: " + get_color(whose_move) + " won! (" + str(turn_count)
                      + " turns occurred.)")
                state.next_roll = None
                winner = whose_move
                game_record.append(copy.deepcopy(state))
                break
            state.whose_move = 1 - state.whose_move
    return game_record, winner


def print_game_intro(red, white):
    """Outputs the names and introductions of the two players."""
    print("The Simplified Backgammon Game-master (V20-1) says: Welcome!")
    print("Playing WHITE: " + str(white.nickname()))
    print("Playing RED: " + str(red.nickname()))


def check_for_special_move(move, state, die1, die2, deterministic, pass_count, print_to_console):
    """Takes in a move command check to see if it contains one of the special
  commands: p (pass), q (quit), or r (reverse). If it does, the method returns which 
  command. If not, the methods returns "NORMAL". 
  """

    if "q" in move or "Q" in move:  # quit
        if print_to_console:
            print(get_color(state.whose_move) + ' resigns. Game OVER!')
        return "FORFEIT"

    # Reminder: if the player attempts to double pass (p,p) while there are possible moves,
    # they automatically lose.
    move_list = move.split(",")
    if move_list[0] == "p" or move_list[0] == "P":  # explicit check for (p,p)
        if moves_exist(state, state.whose_move, die1, die2, print_to_console):
            if print_to_console:
                print("ILLEGAL MOVE: Attempted double pass, but possible moves still exist.")
            return "FORFEIT"
        else:
            if print_to_console:
                print("No possible moves, so a double pass is accepted. ")
            new_state = bgstate(state)
            new_state.whose_move = 1 - state.whose_move
            pass_count += 1
            if deterministic and pass_count == 3:
                tie(print_to_console)
                return "TIE"
            else:
                return "PASS"

    if "r" in move or "R" in move:
        return "REVERSE"

    return "NORMAL"


# Prints out a more human-readable version of a move command.
def pretty_print_move(move, dice):
    checker_positions = move.split(",")

    if len(checker_positions) == 3 and checker_positions[2] == 'r':
        first_dice = str(dice[1])
        second_dice = str(dice[0])
    else:
        first_dice = str(dice[0])
        second_dice = str(dice[1])

    if checker_positions[0] == 'p':
        first_part = "(pass)"
    else:
        first_part = "checker at " + checker_positions[0] + " will be moved by " + first_dice

    if checker_positions[1] == 'p':
        second_part = "(pass)"
    else:
        second_part = "checker at " + checker_positions[1] + " will be moved by " + second_dice

    print("Applying move..." + first_part + " and " + second_part)


def handle_move(checker_position, state, dice, print_to_console):
    """Updates the board state, given the two checkers to be moved and their corresponding dice rolls."""
    whose_move = state.whose_move
    player_color = str(get_color(state.whose_move))

    for i in range(2):  # for each of the two checkers
        # If the player wants to pass after the first checker was moved:
        if "P" in checker_position[i] or "p" in checker_position[i]:
            if print_to_console:
                print("Pass is accepted for the second die.")
            return state

        checker_position[i] = int(checker_position[i])  # Converting to int

        # Check if the given checker is on the bar
        if checker_position[i] == 0:
            if whose_move not in state.bar:
                if print_to_console:
                    print("ILLEGAL MOVE: attempted unnecessary move off bar.")
                return "FORFEIT", "ILLEGAL MOVE: attempted move off bar, but there are no checkers on the bar."
            state = handle_move_from_bar(state, whose_move, dice[i], print_to_console)
            continue
        if not can_move_checker(state, checker_position[i], checker_position, print_to_console):
            return "FORFEIT", "Agent has checkers stuck on the bar and cannot make a move."

        if whose_move == W:
            dest_pt = int(checker_position[i]) + dice[i]
        else:
            dest_pt = int(checker_position[i]) - dice[i]

        if (dest_pt > 24 or dest_pt < 1) and bearing_off_allowed(state):
            if print_to_console:
                print("Player", player_color, "proposes to bear off from", checker_position[i], "with die roll of", dice[i])
            born_off_state = bear_off(state, checker_position[i], dest_pt, whose_move)
            if not born_off_state:
                if print_to_console:
                    print("ILLEGAL MOVE: attempted bear off checker but cannot.")
                return "FORFEIT", "ILLEGAL MOVE: attempted bear off checker but cannot."
            else:
                state = born_off_state
                continue

        dest_pt_list = state.pointLists[dest_pt - 1]

        # Checking that the destination location not blocked.
        if len(dest_pt_list) > 1 and dest_pt_list[0] != whose_move:
            if print_to_console:
                print("ILLEGAL MOVE: Desired destination [" + str(
                dest_pt) + "] is blocked by the opponent. You can't move there.")
            return "FORFEIT", "ILLEGAL MOVE: Desired destination [" + str(
                dest_pt) + "] is blocked by the opponent. You can't move there."

        # So this move is legal. Update the state.

        # Remove checker from its starting point.
        state.pointLists[checker_position[i] - 1].pop()
        # If the destination point contains a single opponent, it's hit.
        state = hit(state, dest_pt)
        # Now move the checker into the destination point.
        state.pointLists[dest_pt - 1].append(whose_move)

    return state


def can_move_checker(state, checker_x_position, all_positions, print_to_console):
    """Checks that the given checker exists and can move"""
    whose_move = state.whose_move
    player_color = str(get_color(state.whose_move))
    checker_position = int(checker_x_position)

    # A player cannot have any checkers on the bar before they can move a checker elsewhere
    # If they did have a checker on the bar, the move command should've had a 0 (to move
    # that checker off) or a p (if they had no options).
    if any_on_bar(state, whose_move):
        if print_to_console:
            print("ILLEGAL MOVE: Attempted to move a non-bar checker, while there are still checkers on the bar."
                  + player_color + " forfeits.")
        return "FORFEIT"

    # Is the given checker even on the board?
    if checker_position < 1 or checker_position > 24:
        if print_to_console:
            print("ILLEGAL MOVE:" + str(checker_position),
                  "is not a valid point index. Point must be between 1 and 24, inclusive.")
        return "FORFEIT"

    # Is there at least one checker available on provided index?
    if whose_move not in state.pointLists[checker_position - 1]:
        if print_to_console:
            print("ILLEGAL MOVE: No " + player_color + " checker available at point " + str(checker_position))
        return "FORFEIT"

    else:
        return True


def hit(state, dest_pt):
    """Returns the state after an attempted hit. If hit misses, nothing is changed."""
    dest_pt_list = state.pointLists[dest_pt - 1]
    opponent = 1 - state.whose_move

    # If the destination point contains one of the opponents checkers,
    # then that checker is 'hit' and moved to the bar.
    # If the destination does not contain one of the opponenet, this method will not change the state.
    if len(dest_pt_list) == 1 and dest_pt_list[0] == opponent:
        if opponent == W:
            state.bar.insert(W, 0)  # Whites at front of bar
        else:
            state.bar.append(R)  # Reds at end of bar
        state.pointLists[dest_pt - 1] = []
    return state


def bearing_off_allowed(state):
    """Checks the gamestate too see if it it allows a player to bear off
    (put their checkers into the endzone). Returns True if the active player
    is allowed to bear off, False if not. """

    who = state.whose_move
    # True, provided no checkers of this color on the bar or in first three quadrants.
    if any_on_bar(state, who):
        return False
    if who == W:
        point_range = range(0, 18)
    else:
        point_range = range(6, 24)
    pl = state.pointLists
    for i in point_range:
        if not pl[i]:
            continue
        if pl[i][0] == who:
            return False
    return True


def bear_off(state, src_pt, dest_pt, who):
    """Returns the state after bearing a checker off."""


    # Direct bear-off, if possible:
    pl = state.pointLists[src_pt - 1]
    if pl == [] or pl[0] != who:
        print("p1 is empty is of wrong type: " + str(who) + " bearing off from " + str(src_pt) + " to " + str(dest_pt))
        return False

    # So there is a checker to possibly bear off.
    # If it does not go exactly off, then there must be
    # no pieces of the same color behind it, and ROLL MUST BE GREATER THAN DIST (changed from exact + 1)
    good = True
    if who == W:
        if dest_pt < 25:
            print("BEARING OFF ERROR: destination is not off the board: " + str(who) + " bearing off from " + str(src_pt) + " to " + str(dest_pt))
            good = False
        elif dest_pt == 26:
            for point in range(18, src_pt - 1):
                if W in state.pointLists[point]:
                    print("BEARING OFF ERROR: destination is not off the board: " + str(who) + " bearing off from " + str(src_pt) + " to " + str(dest_pt))
                    good = False
    elif who == R:
        if dest_pt > 0:
            good = False
            print("BEARING OFF ERROR: there are checkers before target checker: " + str(who) + " bearing off from " + str(src_pt) + " to " + str(dest_pt))

        elif dest_pt == -1:
            for point in range(src_pt, 6):
                if R in state.pointLists[point]:
                    print("BEARING OFF ERROR: there are checkers before target checker: " + str(who) + " bearing off from " + str(src_pt) + " to " + str(dest_pt))
                    good = False
    if not good:
        return False
    born_off_state = bgstate(state)
    born_off_state.pointLists[src_pt - 1].pop()
    if who == W:
        born_off_state.white_off.append(W)
    else:
        born_off_state.red_off.append(R)
    return born_off_state


def moves_exist(state, who, die1, die2, print_to_console):
    """Uses gen_moves to check if any possible moves exist, given the state"""

    mover = GENMOVES_INSTANCE.gen_moves(state, who, die1, die2)
    so_far = True
    try:
        a_move = next(mover)
        if a_move[0] == 'p':  # Pass is the last "move" the game mover generates.
            so_far = False  # So there weren't any non-pass moves possible.
            # print("In moves_exist, the move is a pass: 'p'")
        # else:
        # print("In moves_exist, the move is",a_move[0])
    except:
        # print("In moves_exist, an exception was raised.")
        so_far = False
    if not so_far and print_to_console:
        print("Game master says: No moves exist in this situation.")
    # print("moves_exist returns",so_far)
    return so_far


def any_on_bar(state, who):
    """returns true if the given player has any checkers on the bar, false if not"""
    return who in state.bar


def handle_move_from_bar(state, who, die, print_to_console):
    """If successful moves a checker off the bar, returns the state
    if the move wasn't successful (blocked by opponent), then we were given
    an illegal move, so return "FORFEIT"
    """

    # We assume there is a piece of this color available on the bar.
    if who == W:
        target_point = die
    else:
        target_point = 25 - die
    point_list = state.pointLists[target_point - 1]
    if point_list != [] and point_list[0] != who and len(point_list) > 1:
        if print_to_console:
            print("ILLEGAL MOVE: Cannot move checker from bar to point " + str(target_point)
                  + ": destination is blocked.")
        return "FORFEIT"
    new_state = bgstate(state)
    new_state = hit(state, target_point)
    if who == W:
        del new_state.bar[0]
    else:
        new_state.bar.pop()
    new_state.pointLists[target_point - 1].append(who)

    return new_state


def forfeit(who, print_to_console):
    """Ends the ongoing run() loop due to a forfiet by one of the players"""
    global DONE
    if print_to_console:
        print("Player " + get_color(who) + " forfeits the game and loses.")
    DONE = True


def tie(print_to_console):
    """Ends the ongoing run() loop due to a tie"""

    global DONE
    if print_to_console:
        print("The players have chosen to pass, pass, and pass again. The game is a draw.")
    DONE = True


def win_detected(state, who):
    if who == W:
        return len(state.white_off) == 15
    else:
        return len(state.red_off) == 15
        
if __name__ == "__main__":
    run(agent1, agent2, 0, DETERMINISTIC, True, None)  # Start from normal initial state.
