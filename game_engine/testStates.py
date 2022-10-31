'''testStates.py
This file provides several states representing various stages
in games of Backgammon.  It's intended for testing other software
on a variety of types of game boards.
Last updated: April 30, 2020, with a minor correction to the
last state.
S. Tanimoto, Univ. of Wash.
'''

from boardState import *

WHITE_TO_BEAR_OFF = bgstate()
WHITE_TO_BEAR_OFF.pointLists =[
[],
[],
[],
[],
[],
[],
[],
[R,R,R,R,R],
[],
[R,R,R],
[],
[],
[],
[R,R,R,R,R],
[],
[],
[],
[],
[W,W,W,W,W],
[W,W],
[W,W,W],
[W,W,W,W,W],
[],
[R,R] ]

RED_TO_BEAR_OFF = bgstate()
RED_TO_BEAR_OFF.pointLists =[
[R,R,R,R,R],
[],
[R,R,R],
[R,R],
[R,R,R,R,R],
[],
[],
[],
[],
[],
[],
[],
[],
[],
[],
[],
[],
[],
[],
[W,W,W,W,W],
[W,W],
[W,W,W],
[W,W,W,W,W],
[] ]