"""
This class handles the client side of the backgammon player.
Students should run this class to view games
"""
from ui import display_constants
from ui.screens import menu, ingame # online
import pygame
import sys

# Below are the agents used in "Play Offline"
# To change, simply add an import and change p1 or p2 to desired Agent
from agents import randomAgent, SkeletonAgent, backgammon_dsbg, backgammon_ssbg
player1 = backgammon_dsbg.BackgammonPlayer()
player2 = backgammon_ssbg.BackgammonPlayer()

DETERMINISTIC = True  # deterministic version: dice are loaded to give 1 and 6
# stochastic version (DETERMINISTIC = false): dice are rolled normally.



# DO NOT CHANGE ANY CODE BELOW THIS
# ------------------------------------------------------------------------------------------------------------------
username = "user"
pygame.init()
pygame.display.init()
pygame.display.set_caption("Backgammon")
window = pygame.display.set_mode((display_constants.WINDOW_WIDTH, display_constants.WINDOW_HEIGHT))
DEBUG = False

try:
    sys.path.append('~/ui')
    sys.path.append('~/server')
    sys.path.append('~/game_engine')
    sys.path.append('~/agents')
    print("Updated path - Backgammon GUI is ready to use.")
except:
    print("ERROR: ui, server, game_engine, or agents folder is missing. Could not update path")

def start_client():
    next_screen = menu.run(window, player1, player2)

    while True:
        if DEBUG:
            print(next_screen)
        if next_screen == "QUIT":
            pygame.quit()
            exit()
        elif next_screen == "MENU":
            next_screen = menu.run(window, player1, player2)
        elif next_screen == "ONLINE":
            raise NotImplementedError()
            # next_screen = online.run(window, username, player1)
        elif len(next_screen) > 1 and next_screen[0] == "INGAME":
            p1 = next_screen[1]
            p2 = next_screen[2]
            computed_game = next_screen[3]
            print(type(p1))
            print(type(p2))
            if p1 is not None:
                if p2 is not None:
                    next_screen = ingame.run(window, p1, p2, DETERMINISTIC, computed_game)
                else:
                    raise Exception("player2 should not be None")
            else:
                raise Exception("player1 should not be None")
        else:
            raise Exception("Invalid game state transition.")


start_client()
