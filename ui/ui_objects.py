"""
This file contains classes for common UI elements that you'd think pygame would have, but doesn't.
"""
from ui.display_constants import *


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = INPUT_BOX_COLOR_INACTIVE
        self.text = text
        self.txt_surface = INPUT_BOX_FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = INPUT_BOX_COLOR_ACTIVE if self.active else INPUT_BOX_COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = INPUT_BOX_FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)


class Button:
    def __init__(self, button_id, text, x, y, color, type):
        self.button_id = button_id
        self.text = text
        self.x = x
        self.y = y
        self.width = BUTTON_DIMENSIONS[type][0]
        self.height = BUTTON_DIMENSIONS[type][1]
        self.color = color
        self.font = BUTTON_DEFAULT_FONT[type]
        self.font_color = BUTTON_FONT_COLORS[type]
        self.centered_text = (type != 2)  # type 2 buttons are not centered

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        text = self.font.render(self.text, 1, self.font_color)
        if self.centered_text:
            win.blit(text, (self.x + round(self.width / 2) - round(text.get_width() / 2),
                            self.y + round(self.height / 2) - round(text.get_height() / 2)))
        else:
            win.blit(text, (self.x + PADDING, self.y + round(self.height / 2) - round(text.get_height() / 2)))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if (self.x <= x1 <= self.x + self.width
                and self.y <= y1 <= self.y + self.height):
            return True
        else:
            return False


def draw_grid_lines(win):
    """ Prints out grid lines. helpful for design.
    Not really a ui object, more like a helpful method that all screen use. Prolly could put into a new class
    for helpful methods, but whatever.
    """
    x = 0
    y = 0
    spacing = 50

    # horizontal lines
    while x < WINDOW_WIDTH:
        text = BODY_FONT_SMALL.render(str(x), 1, GRAY)
        win.blit(text, (x, 5))
        pygame.draw.line(win, (255, 0, 0), (x, 0), (x, WINDOW_HEIGHT))
        x += spacing

    # vertical lines
    while y < WINDOW_HEIGHT:
        text = BODY_FONT_SMALL.render(str(y), 1, BLACK)
        win.blit(text, (5, y))
        pygame.draw.line(win, (255, 0, 0), (0, y), (WINDOW_WIDTH, y))
        y += spacing


def draw_board_lines(win, text_on):
    """
    nothing like a bit of guess and check to estimate where the columns are. These numbers are magical, and hard
    coded, so if window dimensions change, everything will explode.
    """
    x = 50
    y = 0
    spacing = 60
    adjusted = False

    while x < WINDOW_WIDTH:
        if text_on:
            text = BODY_FONT_SMALL.render(str(x), 1, GRAY)
            win.blit(text, (x, 5))
        pygame.draw.line(win, (255, 0, 0), (x, 0), (x, WINDOW_HEIGHT))
        x += spacing

        if x > 350 and not adjusted:  # the board has a little divider block so there needs another adjustment
            x += 38
            adjusted = True
