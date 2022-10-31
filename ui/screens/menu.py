"""
This class displays the menu.

TODO: should display visual error if user tries to log into offline server (currently only prints a message in console).
"""
from ui.ui_objects import *
#import server.server_constants as server
import pygame


DEBUG = False
# thanks to pygame spaghetti magic, textboxes have to be declared globally, because the .draw and .handle_event methods
# are located in different places. if have multiple, prob put these in a list.
# text_boxes = [InputBox(round(WINDOW_WIDTH / 2) - 120 - round(PADDING), WINDOW_HEIGHT / 2 - 50 + PADDING, 120, 36,
#                        str(server.SERVER))]
text_boxes = [InputBox(round(WINDOW_WIDTH / 2) - 120 - round(PADDING), WINDOW_HEIGHT / 2 - 50 + PADDING, 120, 36,
                       "(disabled)")]

buttons = [Button("CONNECT", "CONNECT", WINDOW_WIDTH / 2 + PADDING, WINDOW_HEIGHT / 2 - 50, GRAY, 0),
           Button("START", "START", WINDOW_WIDTH / 2 + PADDING, WINDOW_HEIGHT / 2 + PADDING * 2, GOLD, 0)]


def draw(win):
    win.fill(WHITE)
    pygame.draw.rect(win, GOLD, (0, 0, 150, WINDOW_HEIGHT))
    pygame.draw.rect(win, GOLD, (WINDOW_WIDTH - 150, 0, 150, WINDOW_HEIGHT))
    pygame.draw.rect(win, PURPLE, (0, 0, WINDOW_WIDTH, 150))
    pygame.draw.rect(win, PURPLE, (round(WINDOW_WIDTH / 4 - 8), round(WINDOW_HEIGHT / 3),
                                   round(WINDOW_WIDTH / 2 + 16), round(WINDOW_HEIGHT / 3 + PADDING * 4)))
    pygame.draw.rect(win, WHITE,
                     (round(WINDOW_WIDTH / 4 + PADDING * 3), round(WINDOW_HEIGHT / 3 + PADDING * 3),
                      round(WINDOW_WIDTH / 2 - PADDING * 6), round(WINDOW_HEIGHT / 3 - PADDING * 2)))

    text = TITLE_FONT.render("CSE 415 Backgammon", 1, WHITE)
    win.blit(text, (round(WINDOW_WIDTH / 2) - round(text.get_width() / 2), 25))

    text = BODY_FONT_SMALL.render("v0.1", 1, WHITE)
    win.blit(text, (WINDOW_WIDTH - text.get_width() - PADDING, 150 - text.get_height() - PADDING))

    text = BODY_FONT_SMALL.render("Server:", 1, PURPLE)
    win.blit(text, (text_boxes[0].rect.x - text.get_width() - PADDING, text_boxes[0].rect.y + int(text.get_height() / 2 - PADDING / 2)))

    text = BODY_FONT.render("Local Game:", 1, PURPLE)
    win.blit(text, (round(WINDOW_WIDTH / 2 - text.get_width() - PADDING),
                    round(WINDOW_HEIGHT / 2 + text.get_height() / 2 + PADDING / 2)))

    for t in text_boxes:
        t.draw(win)
    for b in buttons:
        b.draw(win)

    # comment out the below line to get of the red grid lines across the screen.
    # draw_grid_lines(win)

    pygame.display.update()


def run(window, p1, p2):
    """
    :param window: window to draw on
    :param p1: player 1 (must be of type BackgammmonPlayer)
    :param p2: same as above
    :return: the next screen to transition to
    """
    if DEBUG:
        print("menu screen")

    display_screen = "MENU"
    clock = pygame.time.Clock()
    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for b in buttons:
                    if b.click(pos):
                        if b.button_id == "CONNECT":
                            print("[DISABLED] online screen is currently not accessible.")
                        elif b.button_id == "START":
                            return "INGAME", p1, p2, None
            # for t in text_boxes:
            #     t.handle_event(event)

        draw(window)
