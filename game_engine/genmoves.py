"""genmoves.py

Provides functionality to generate one or more (or all) legal
moves from a given state.  To see an example of using this
functionality, examine the file SkeletonAgent.py.

S. Tanimoto, April 19, 2020, with a fix to the hit function and
its calling context on April 23.
On April 24, a bug was fixed so that passing on the second die
will be OK for ordinary moves (not moves from the bar or bearing
off).
April 26, fixed an issue with whose_move not being flipped, and
an issue when checking for a piece on the bar during the second
die consideration did not take into consideration the result of
the first die.
April 27, eliminated class variables GenMoves.pro and GenMoves.opp,
because they broke having multiple generator instances at the
same time.  Instead we now have additional local variables passed
as arguments down to helper functions: pro and opp. These help
maintain proper whose_move information in spite of having 2 dice.
(Flipping whose_move on each die was wrong!).
April 29, made sure to create a new state, even when passing.
"""

from game_engine.boardState import *

DEBUG = False


def report(*args):
    if DEBUG: print(*args)


class GenMoves:
    """This class encapsulates methods that allow finding all the
    legal moves from some given state."""

    def __init__(self):  # Does nothing more than instantiate the class.
        report("Instantiating GenMoves.")
        pass

    def gen_moves(self, state, whose_move, die1, die2, pro=W, opp=R):
        """To get any moves for a given state, etc., first call this to
        get a generator object.  Then keeping calling the 'next' function
        passing in the generator as the argument for each additional move
        wanted. When no more moves can be found, the StopIteration exception
        is raised."""
        self.current = state
        pro = whose_move  # protagonist (whose move it is)
        opp = 1 - whose_move  # Remember this for all moves from this state.
        self.die1 = die1
        self.die2 = die2
        if DEBUG:
            print("gen_moves called with dice:", die1, die2)

        '''We use a yield construct to produce a Python generator object.'''
        # Whenever a new move is requested, this method will yield a (move, state)
        # pair, where move is a string representation of the move, and
        # state is a new bgstate object created to show the result of the move.
        # The method makes other, temporary state objects, to represent situations,
        # where one of the two dice, but not the other, has been used.

        s = self.current
        yield from self.use_dice([self.die1, self.die2], s, '', pro, opp, reversing='')
        if self.die1 != self.die2:  # If they're not the same value, then
            # also, try them in reverse order:
            yield from self.use_dice([self.die2, self.die1], s, '', pro, opp, reversing=',R')
        new_state = bgstate(s)
        new_state.whose_move = opp
        yield 'p', new_state

    def use_dice(self, dice_list, s, move_so_far, pro, opp, reversing=''):
        # Use one die, and if successful,
        # either yield a (move, state) pair, or call recursively to
        # use a second die.

        report("Entering use_dice, with dice_list=", dice_list, "; move_so_far=" + move_so_far, "reversing=", reversing)
        if DEBUG and len(dice_list) == 1:
            report("==>  After using the first die, the state would be")
            report(s.prettyPrint())
        die = dice_list[0]  # Get first die on list (or the only die, if called with one).
        ndice = len(dice_list)

        w = pro  # abbreviate.
        # Generate "bar" moves first.
        if any_on_bar(s, w):
            # report("We've got to get off the bar.")
            # Try to move a checker off the bar with die1.
            if w == W:
                target = die - 1
            else:
                target = 24 - die
            report("target point is ", target + 1)
            if targetPointOK(s, w, target):

                if ndice == 1:  # Is this the second die?
                    move_string = move_so_far + ",0" + reversing  # 0 means move from bar.
                    new_state = bgstate(s)
                    new_state.whose_move = opp
                    move_from_bar(new_state, w, target, opp)
                    yield (move_string, new_state)
                else:
                    new_state = bgstate(s)
                    # new_state.whose_move = opp
                    move_from_bar(new_state, w, target, opp)  # Update state to facilitate part 2.
                    yield from self.use_dice(dice_list[1:], new_state, "0", pro, opp, reversing=reversing)

            else:
                if ndice == 1:
                    move_string = move_so_far + ",p" + reversing  # Can't get 2nd piece off bar, pass on that.
                    s.whose_move = opp
                    yield move_string, s

            # yield ('p', s)  # Can't get off the bar, so pass (in our rules this is OK)
            return  # Force StopIteration, since no other moves are legal when pieces are on the bar.

        report("Trying for a non-bar move now...")
        # NOTHING IS ON THE BAR NOW, SO,
        # Generate normal moves.
        # What can we do with the die?
        for i in range(24):
            # Look through all the points to find where our checkers are.
            # Is there a w checker on point i?
            if not pointHasMyChecker(s, w, i): continue

            # Can it move to point i + die  (or i - die, if red.) ?
            if w == W:
                target = i + die
            else:
                target = i - die
            if not targetPointOK(s, w, target): continue
            report("  Found a checker to move at ", i + 1)
            report("    It can move to target point ", target + 1)
            # If so, try it there.

            new_state = move_from(s, w, i, target, opp)  # Update state.
            if ndice == 1:
                move_string = move_so_far + "," + str(i + 1) + reversing
                new_state.whose_move = opp
                yield move_string, new_state

            # Now what can we do with the 2nd die after that?
            else:
                move_so_far = str(i + 1)
                yield from self.use_dice(dice_list[1:], new_state, move_so_far, pro, opp, reversing=reversing)

        if bearing_off_allowed(s, w):
            report("Checkers are all in home quadrant. Try to bear something off...")
            # First see if we have an exact match of die roll to checker distance from off.
            if w == W:
                possible_sourcePt = 24 - die
                report("Looking for a White checker at point", possible_sourcePt + 1)
            if w == R:
                possible_sourcePt = die - 1
                report("Looking for a Red checker at point", possible_sourcePt + 1)
            pointlist = s.pointLists[possible_sourcePt]
            if len(pointlist) > 0 and pointlist[0] == w:
                # We can bear this checker off.
                sourcePt = possible_sourcePt
                report(["White", "Red"][w] + " bearing off from " + str(sourcePt + 1))
                new_state = bear_off(s, w, sourcePt, opp)
                new_state.whose_move = opp
                if ndice == 1:
                    move_string = move_so_far + "," + str(sourcePt + 1) + reversing
                    yield move_string, new_state
                else:
                    move_so_far = str(sourcePt + 1)
                    yield from self.use_dice(dice_list[1:], new_state, move_so_far, pro, opp, reversing=reversing)

            # Now consider the case of an inexact match.
            good = True  # possible_sourcePt is not off the board.
            if w == W:
                possible_sourcePt = 25 - die  # White checker 1 closer than die's value.
                if possible_sourcePt == 24: good = False
                taboo_range = range(18, min(24, possible_sourcePt))  # No White checkers allowed lower than sourcePt.
            if w == R:
                possible_sourcePt = die - 2
                if possible_sourcePt == -1: good = False
                taboo_range = range(max(1, possible_sourcePt), 6)  # No Red checkers allowed greater than sourcePt.
            # report("In line 145 of genmoves.py, possible_sourcePt is ",possible_sourcePt)
            try:
                if good:
                    pointlist = s.pointLists[possible_sourcePt]
            except:
                report("===============ERROR BAD STATE???==================")
                report(s.prettyPrint())
            if good and len(pointlist) > 0 and pointlist[0] == w:
                report("Found a possible checker to bear off (via inexact match) at", possible_sourcePt + 1)
                # Make sure this checker does not have one further away.
                isFarthest = True
                for j in taboo_range:
                    if w in s.pointLists[j]:
                        isFarthest = False
                        break
                if isFarthest:
                    report("We have an OK inexact match, at ", possible_sourcePt + 1)
                    sourcePt = possible_sourcePt
                    new_state = bear_off(s, w, sourcePt, opp)
                    if ndice == 1:
                        move_string = move_so_far + "," + str(sourcePt + 1) + reversing
                        new_state.whose_move = opp
                        yield move_string, new_state
                    else:
                        move_so_far = str(sourcePt + 1)
                        yield from self.use_dice(dice_list[1:], new_state, move_so_far, pro, opp, reversing=reversing)

            if ndice == 1:
                s.whose_move = opp
                yield move_so_far + ",p" + reversing, s
            report("No other ways to bear off.")
            return
        # Handle case where one checker could move but the second could not:
        if ndice == 1:
            s.whose_move = opp
            yield move_so_far + ",p" + reversing, s

        report("No more ways to use the dice: ", dice_list)


def bear_off(state, who, source_pt, opp):
    report("In bear_off, checker to bear off is at ", source_pt + 1)
    new_state = bgstate(state)
    if who == W:
        new_state.white_off.append(W)
    else:
        new_state.red_off.append(R)
    # report("In bear_off, index is ",sourcePt)
    # report(new_state.prettyPrint())
    pointlist = new_state.pointLists[source_pt]
    pointlist.pop()
    # new_state.whose_move = opp
    return new_state


'''
  # So there is a checker to possibly bear off.
  # If it does not go exactly off, then there must be
  # no pieces of the same color behind it, and dest
  # can only be one further away.
  good = False
  if who==W:
    if dest_pt==25:
       good = True
    elif dest_pt==26:
       for point in range(18,src_pt-1):
         if W in state.pointLists[point]: return False
       good = True
  elif who==R:
    if dest_pt==0:
       good = True
    elif dest_pt== -1:
       for point in range(src_pt, 6):
         if R in state.pointLists[point]: return False
       good = True
  if not good: return False 
  born_off_state = bgstate(state)
  born_off_state.pointLists[src_pt-1].pop()
  if who==W: born_off_state.white_off.append(W)
  else:  born_off_state.red_off.append(R)
  return born_off_state
'''


def move_from(state, who, source_point, target_point, opp):
    new_state = bgstate(state)
    source_list = new_state.pointLists[source_point]
    target_list = new_state.pointLists[target_point]
    source_list.pop()
    hit(new_state, target_list, target_point, opp)
    target_list = new_state.pointLists[target_point]  # Refetch after possible change from hit.
    target_list.append(who)  # I'm not sure this inserts in pointLists properly if targetlist is empty.
    return new_state


def hit(new_state, dest_pt_list, dest_pt, opp):
    """Performs changes for a hit, if appropriate.
    Otherwise, doesn't do anything."""
    if len(dest_pt_list) == 1 and dest_pt_list[0] == opp:  # Test if opponent is vulnerable at dest_pt.
        if opp == W:
            new_state.bar.insert(W, 0)  # Whites at front of bar
        else:
            new_state.bar.append(R)  # Reds at end of bar
        report("Hit happens! at", dest_pt + 1, "opp=", ['W', 'R'][opp])
        new_state.pointLists[dest_pt] = []  # Remove the hit piece from the board
    # return new_state


def any_on_bar(state, who):
    return who in state.bar


def move_from_bar(new_state, who, target, opp):
    remove_from_bar(new_state, who)
    move_to_target(new_state, who, target, opp)


def remove_from_bar(new_state, who):
    # removes a white from start of bar list,
    # or a red from the end of the bar list.
    if who == W:
        del new_state.bar[0]
    else:
        new_state.bar.pop()
    report("After removing a " + get_color(who) + " from the bar,")
    report("  the bar is now: " + str(new_state.bar))


def pointHasMyChecker(state, who, pt):
    pointlist = state.pointLists[pt]
    return len(pointlist) > 0 and pointlist[0] == who


def targetPointOK(state, who, target):
    """Return True if 'who' can move to the 'target' point,
    where target is in the range 0 to 23.
    This allows hits."""
    report("Entering targetPointOK with target", target + 1)
    if target < 0 or target > 23: return False  # Off the board.
    pointlist = state.pointLists[target]
    report("pointlist is ", pointlist)
    if len(pointlist) < 2: return True
    report("So this is a long pointlist.")
    if pointlist[0] == who: return True
    return False  # 2 or more opponent checkers.


def move_to_target(new_state, who, target, opp):
    target_list = new_state.pointLists[target]
    hit(new_state, target_list, target, opp)
    target_list = new_state.pointLists[target]  # Refetch after possible change from hit.
    target_list.append(who)


def bearing_off_allowed(state, who):
    # True provided no checkers of this color on the bar or in
    # first three quadrants.
    if any_on_bar(state, who): return False
    if who == W:
        point_range = range(0, 18)
    else:
        point_range = range(6, 24)
    pl = state.pointLists
    for i in point_range:
        if pl[i] == []:
            continue
        if pl[i][0] == who:
            return False
    return True
