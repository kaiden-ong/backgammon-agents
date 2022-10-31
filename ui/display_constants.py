"""
This file holds the many, many constants used in display. pygame sucks.
"""
import pygame

pygame.font.init()

# images
# -----------------------------------------------------------------
BACKGROUNDS = [pygame.image.load("ui/images/backgammon-board-dark.png"),
               pygame.image.load("ui/images/backgammon-board-light.png")]  # backgrounds only differ in color scheme
EXPANDED_RIGHT_BAR = 200
WINDOW_WIDTH = BACKGROUNDS[0].get_width() + EXPANDED_RIGHT_BAR
WINDOW_HEIGHT = BACKGROUNDS[0].get_height()
CHECKER_SPRITES = [pygame.image.load("ui/images/white_checker.png"),
                   pygame.image.load("ui/images/red_checker.png"),
                   pygame.image.load("ui/images/white_checker_highlighted.png"),
                   pygame.image.load("ui/images/red_checker_highlighted.png")]

# note: apparently, UW has an official guide to its graphics:
# fonts and colors taken from https://www.washington.edu/brand/graphic-elements/

# fonts
# -----------------------------------------------------------------
TITLE_FONT = pygame.font.Font("ui/fonts/EncodeSans_black.ttf", 69)
SUB_TITLE_FONT = pygame.font.Font("ui/fonts/UniSansBook.otf", 36)
BODY_FONT = pygame.font.Font("ui/fonts/OpenSans_regular.ttf", 24)
BODY_FONT_SMALL = pygame.font.Font("ui/fonts/OpenSans_regular.ttf", 16)
BODY_FONT_EXTRA_SMALL = pygame.font.Font("ui/fonts/OpenSans_regular.ttf", 12)
BODY_FONT_BOLD = pygame.font.Font("ui/fonts/OpenSans_bold.ttf", 24)


# colors
# -----------------------------------------------------------------
PURPLE = (51, 0, 111)
GOLD = (232, 211, 162)
METALLIC_GOLD = (124, 123, 76)
GRAY = (217, 217, 217)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)  # primarily for debugging/errors
BROWN = (102, 61, 20)


# UI
# -----------------------------------------------------------------
PADDING = 8  # px
BIG_MARGIN = 48
WIDTH_INSIDE_MARGIN = WINDOW_WIDTH - BIG_MARGIN * 3
MIDDLE_X = round(WINDOW_WIDTH / 2)
# 0 is standard button, 1 is smaller. 2 is menu_item button. Each is in [width, height]
BUTTON_DIMENSIONS = [[150, 50],
                     [100, 33],
                     [round(WIDTH_INSIDE_MARGIN / 2) - PADDING * 2, 40],
                     [100, 33],
                     [80, 28]]
BUTTON_DEFAULT_FONT = [BODY_FONT_BOLD,
                       BODY_FONT_SMALL,
                       BODY_FONT_SMALL,
                       BODY_FONT_SMALL,
                       BODY_FONT_SMALL]
BUTTON_FONT_COLORS = [WHITE,
                      WHITE,
                      BLACK,
                      BLACK,
                      WHITE]
INPUT_BOX_COLOR_INACTIVE = PURPLE
INPUT_BOX_COLOR_ACTIVE = PURPLE
INPUT_BOX_FONT = BODY_FONT_SMALL
BOARD_X = [50, 110, 170, 230, 290, 350, 448, 508, 568, 628, 688, 748]
BOARD_BAR_X = round((BOARD_X[5] + BOARD_X[6]) / 2)
# note that the real board starts at index 1
TA_BOX_DISPLAY_SIZE = 3
STUDENT_BOX_DISPLAY_SIZE = 5


# MISC
# -----------------------------------------------------------------
PLAYER_COLOR = [WHITE, RED]
PLAYER_COLOR_STR = ["White", "Red"]
