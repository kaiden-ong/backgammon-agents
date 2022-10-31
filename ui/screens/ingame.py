"""
This class is used to display a graphical representation of a backgammon game.
Students should not modify this file.

"""
from ui.ui_objects import *

import gamemaster as gm
import pygame

# import threading
# from multiprocessing.pool import ThreadPool
# pool = ThreadPool(processes=1)
import concurrent.futures

TIME_LIMIT = 3
DEBUG = False
computing_game = True
expanded_x = WINDOW_WIDTH - EXPANDED_RIGHT_BAR + PADDING
adjusted_x = expanded_x + PADDING
buttons = [Button("Play", "Play", 900 - BUTTON_DIMENSIONS[4][0] - round(PADDING / 2), 200, GOLD, 4),
           Button("Step_Prev", "Step Prev", 900 - BUTTON_DIMENSIONS[4][0] - round(PADDING / 2),
                  200 + BUTTON_DIMENSIONS[4][1] + PADDING, GOLD, 4),
           Button("Step_Next", "Step Next", 900 + round(PADDING / 2), 200 + (BUTTON_DIMENSIONS[4][1] + PADDING), GOLD,
                  4),
           Button("Slower", "Slower", 900 - BUTTON_DIMENSIONS[4][0] - round(PADDING / 2),
                  200 + 2 * (BUTTON_DIMENSIONS[4][1] + PADDING), GOLD, 4),
           Button("Faster", "Faster", 900 + round(PADDING / 2), 200 + 2 * (BUTTON_DIMENSIONS[4][1] + PADDING), GOLD, 4),
           Button("Reset", "Reset", 900 - BUTTON_DIMENSIONS[4][0] - round(PADDING / 2),
                  200 + 3 * (BUTTON_DIMENSIONS[4][1] + PADDING), GOLD, 4),
           Button("Rerun", "Rerun", 900 + round(PADDING / 2), 200 + 3 * (BUTTON_DIMENSIONS[4][1] + PADDING), GOLD, 4)
           ]
compute_status = ["Computing match...", "Ready to display game"]
panel_middle = 900
player_names = ["None", "None"]
online = False
clock_speed_index = 2
CLOCK_SPEEDS = [10, 20, 40, 80, 160, 320]


def draw(win, game, turn, play):
    """
    :param win: window to draw on
    :param game_record: a fully computed game.
    :param turn: which turn is being displayed
    :param play: true if ongoing, false if on pause.
    """

    win.fill(GRAY)
    win.blit(BACKGROUNDS[1], (0, 0))

    # "Players" box
    pygame.draw.rect(win, WHITE, (expanded_x, PADDING, EXPANDED_RIGHT_BAR - PADDING * 2, 130))

    text = BODY_FONT.render("AGENTS:", 1, METALLIC_GOLD)
    win.blit(text, (adjusted_x, PADDING * 2))

    text = BODY_FONT_SMALL.render(player_names[0] + " (" + PLAYER_COLOR_STR[0] + ")", 1, METALLIC_GOLD)
    win.blit(text, (panel_middle - text.get_width() / 2, (50 + PADDING)))

    text = BODY_FONT_SMALL.render("vs.", 1, METALLIC_GOLD)
    win.blit(text, (panel_middle - text.get_width() / 2, (50 + PADDING + text.get_height())))

    text = BODY_FONT_SMALL.render(player_names[1] + " (" + PLAYER_COLOR_STR[1] + ")", 1, METALLIC_GOLD)
    win.blit(text, (panel_middle - text.get_width() / 2, (50 + PADDING + text.get_height() * 2)))

    # "Playback" box
    pygame.draw.rect(win, WHITE, (expanded_x, 150 + PADDING, EXPANDED_RIGHT_BAR - PADDING * 2, 210))
    text = BODY_FONT.render("PLAYBACK:", 1, METALLIC_GOLD)
    win.blit(text, (adjusted_x, 144 + PADDING * 2))

    # label_size = text.get_height()
    # text = BODY_FONT_EXTRA_SMALL.render(compute_status[playback_isReady], 1, BLACK)
    # win.blit(text, (adjusted_x, 164 + label_size + PADDING * 2))

    # "Game" box
    pygame.draw.rect(win, WHITE, (expanded_x, 380 + PADDING, EXPANDED_RIGHT_BAR - PADDING * 2, 150))

    if not play:
        buttons[0].text = "Play"
    else:
        buttons[0].text = "Pause"

    for b in buttons:
        b.draw(win)

    # prints the game board
    if game:
        game_record = game[0]
        winner = game[1]

        # draw_board(win, game_record[turn])
        if int(turn / 2) >= len(game_record):
            # due to updating, this can happen after rerun
            draw_board(win, None, False)
        else:
            state = game_record[int(turn / 2)]

            draw_board(win, state, turn)
            draw_info(win, state, turn)

            if turn + 1 >= len(game_record) * 2:
                pygame.draw.rect(win, WHITE, (150, 200, 500, 100))

                if winner == -1:
                    text = SUB_TITLE_FONT.render("TIE GAME!", 1, RED)
                elif winner == 0 or winner == 1:
                    text = SUB_TITLE_FONT.render(
                        "WINNER: " + player_names[winner] + " (" + PLAYER_COLOR_STR[winner] + ")"
                        , 1, BLACK)
                else:
                    text = SUB_TITLE_FONT.render("ERROR: No result was found from game record" + player_names[winner],
                                                 1, BLACK)
                win.blit(text, (round(400 - text.get_width() / 2), round(250 - text.get_height() / 2)))
    else:
        draw_board(win, None, False)

    # comment out the below line to get grid lines across the screen or board (debug/design purposes)
    # draw_grid_lines(win)
    # draw_board_lines(win, False)

    pygame.display.update()


def draw_board(win, state, turn):
    """
    :param win: window to draw on
    :param state: state of the computed game
    :param turn: which turn is being displayed
    :return:
    """

    if not state:
        pygame.draw.rect(win, WHITE, (150, 200, 500, 100))
        text = SUB_TITLE_FONT.render(
            "COMPUTING GAME...", 1, BLACK)
        win.blit(text, (round(400 - text.get_width() / 2), round(250 - text.get_height() / 2)))
        return

    dice_roll = state.next_roll

    # on integer turns (0.0, 1.0, 2.0, etc), a game state is displayed.
    # on .5 turns (0.5, 1.5, 2.5, etc.), a move is displayed (through highlighting)
    if turn % 2 == 1:
        draw_move = True
    else:
        draw_move = False

    if state.next_move or draw_move:
        move = state.next_move.split(",")
    else:
        return

    whose_move = state.whose_move
    apply_which_dice = 0
    num_dice_used = 0
    move_labels = []

    # top half of board
    for i in range(13, 25):
        # prints board positions
        text = BODY_FONT_EXTRA_SMALL.render(str(i), 1, WHITE)
        win.blit(text, (BOARD_X[i - 1 - 12] - round(text.get_width() / 2), 0))

        move_text = 0
        highlight = False
        double_highlight = False
        if (str(i) in move) and draw_move:
            highlight = True
            if str(i) == move[0]:
                apply_which_dice = 0
                if move[0] == move[1]:
                    double_highlight = True
            elif str(i) == move[1]:
                apply_which_dice = 1
        checkers = state.pointLists[i - 1]

        if len(checkers) > 0:
            img_index = checkers[0]
            if highlight and checkers[0] == whose_move:
                img_index += 2
            img = CHECKER_SPRITES[img_index]  # checkersList contains 1's and 0's, which indicate color.
            # 0 is white, 1 is red.

            cap = min(5, len(checkers))
            for n in range(0, cap):
                invert = cap - 1 - n  # need to draw a stack from top-down so highlighting works
                win.blit(img, (BOARD_X[i - 1 - 12] - round(img.get_width() / 2), 20 + invert * img.get_height()))

                if highlight and checkers[0] == whose_move:
                    move_labels.append([str(dice_roll[apply_which_dice]), [
                        BOARD_X[i - 1 - 12],
                        20 + round((invert + 1) * img.get_height()) + 2]
                    ])
                    num_dice_used += 1

                    if double_highlight:
                        apply_which_dice += 1

                    if move[0] != move[1]:
                        # if not a double highlight situation, make sure only the top one is highlighted
                        highlight = False
                        img = CHECKER_SPRITES[img_index - 2]
                    elif n >= 1:  # at most, only 0 and 1 should be highlighted.
                        highlight = False
                        img = CHECKER_SPRITES[img_index - 2]
            if len(checkers) > cap:
                overflow_text = str(len(checkers) - cap)
                text = BODY_FONT.render("[+" + overflow_text + "]", 1, WHITE)
                pygame.draw.rect(win, GOLD,
                                 (BOARD_X[i - 1 - 12] - round((text.get_width() + PADDING) / 2), round((n + 1.5) * img.get_height()),
                                  text.get_width() + PADDING, text.get_height()))
                win.blit(text, (BOARD_X[i - 1 - 12] - round(text.get_width() / 2), round((n + 1.5) * img.get_height())))

    # bottom half of board
    for i in range(1, 13):
        text = BODY_FONT_EXTRA_SMALL.render(str(i), 1, WHITE)
        win.blit(text, (BOARD_X[12 - i] - round(text.get_width() / 2), WINDOW_HEIGHT - text.get_height()))
        move_text = 0
        highlight = False
        double_highlight = False
        if (str(i) in move) and draw_move:
            highlight = True

            if str(i) == move[0]:
                apply_which_dice = 0
                if move[0] == move[1]:
                    double_highlight = True
            elif str(i) == move[1]:
                apply_which_dice = 1
        checkers = state.pointLists[i - 1]

        if len(checkers) > 0:
            img_index = checkers[0]
            if highlight and checkers[0] == whose_move:
                img_index += 2
            img = CHECKER_SPRITES[img_index]  # checkersList contains 1's and 0's, which indicate color.
            # 1 is white, 0 is red.

            cap = min(5, len(checkers))
            for n in range(0, min(5, cap)):
                temp = cap - n  # need to draw a stack from top-down so highlighting works
                win.blit(img, (BOARD_X[12 - i] - round(img.get_width() / 2),
                               WINDOW_HEIGHT - 20 - (temp) * img.get_height()))
                if highlight and checkers[0] == whose_move:
                    move_labels.append([str(dice_roll[apply_which_dice]), [
                        BOARD_X[12 - i],
                        WINDOW_HEIGHT - 20 - round((temp + 0.5) * img.get_height())]
                    ])
                    num_dice_used += 1

                    if double_highlight:
                        apply_which_dice += 1

                    if move[0] != move[1]:
                        # ^ on this stack, only one is highlighted
                        highlight = False
                        img = CHECKER_SPRITES[img_index - 2]
                    elif n >= 1:  # below the 2nd should never be highlighted.
                        highlight = False
                        img = CHECKER_SPRITES[img_index - 2]
            if len(checkers) > cap:
                overflow_text = str(len(checkers) - 5)
                text = BODY_FONT.render("[+" + overflow_text + "]", 1, WHITE)
                pygame.draw.rect(win, GOLD,
                                 (BOARD_X[12 - i] - round((text.get_width() + PADDING) / 2), round(WINDOW_HEIGHT - (n + 2.5) * img.get_height()),
                                  text.get_width() + PADDING, text.get_height()))
                win.blit(text, (BOARD_X[12 - i] - round(text.get_width() / 2), round(WINDOW_HEIGHT - (n + 2.5) * img.get_height())))

    bar = state.bar
    if len(bar) > 0:
        already_highlighted_one = False
        if apply_which_dice == 1:
            apply_which_dice = 0

        for n in range(0, len(bar)):
            index = bar[n]
            img = CHECKER_SPRITES[index]

            if bar[n] == whose_move and draw_move:
                if num_dice_used < 2:
                    if already_highlighted_one:
                        extra = 0
                        if apply_which_dice == 0:
                            extra = 1

                        # print("double_highlight found on bar! extra is " + str(extra) + " and apply is " + str(apply_which_dice))
                        if move[apply_which_dice + extra] != 'p':
                            move_labels.append([str(dice_roll[apply_which_dice + extra]), [
                                BOARD_BAR_X,
                                WINDOW_HEIGHT / 2 + round(img.get_height() * (n - 0.5))]
                            ])
                            num_dice_used += 1

                            index += 2
                            img = CHECKER_SPRITES[index]
                    elif move[apply_which_dice] != 'p':
                        move_labels.append([str(dice_roll[apply_which_dice]), [
                                BOARD_BAR_X,
                                WINDOW_HEIGHT / 2 + round(img.get_height() * (n - 0.5))]
                        ])
                        already_highlighted_one = True
                        num_dice_used += 1

                        index += 2
                        img = CHECKER_SPRITES[index]

            win.blit(img, (BOARD_BAR_X - round(img.get_width() / 2), WINDOW_HEIGHT / 2 + img.get_height() * n))

            if index >= 3:  # was just one of the special highlighted ones
                index -= 2

    for entry in move_labels:
        if not draw_move or move[0] == 'p':  # we are not drawing at all, or player double passes
            break
        label = str(entry[0])

        try:
            if num_dice_used == 1 and move[1] != 'p' and (len(state.pointLists[int(move[1]) - 1]) == 0 or state.pointLists[int(move[1]) - 1][0] != whose_move):
                # print("one checker gets a double move")
                label += " + " + str(dice_roll[1])
        except:
            print("now how the heck did that go wrong")
            print(move[1])
            print(len(state.pointLists[int(move[1])]))
            print(state.pointLists[int(move[1])][0])

        text = BODY_FONT_EXTRA_SMALL.render(label, 1, BLACK)
        pos = entry[1]
        pygame.draw.rect(win, GOLD, (pos[0] - round((text.get_width() + PADDING) / 2), pos[1],
                                     text.get_width() + PADDING, text.get_height() + 1))
        win.blit(text, (pos[0] - round(text.get_width() / 2), pos[1]))


def draw_info(win, state, turn):
    """
    Draws the "Game" rectangle on the bottom right that displays game info.
    :param win: window to draw on
    :param state: one game state
    :param turn: which turn
    """

    text = BODY_FONT.render("GAME:", 1, METALLIC_GOLD)
    win.blit(text, (adjusted_x, 380 + PADDING * 2))

    y = 400 + PADDING * 2
    actual_turn = round(turn / 2, 1)
    text = BODY_FONT_EXTRA_SMALL.render(
        "Current: " + player_names[state.whose_move] + " (" + PLAYER_COLOR_STR[state.whose_move] + ")", 1, BLACK)
    win.blit(text, (adjusted_x, y + (text.get_height()) * 1))
    text = BODY_FONT_EXTRA_SMALL.render("Turn: " + str(actual_turn), 1, BLACK)
    win.blit(text, (adjusted_x, y + (text.get_height()) * 2))
    text = BODY_FONT_EXTRA_SMALL.render("Speed: " + str(CLOCK_SPEEDS[clock_speed_index]), 1, BLACK)
    win.blit(text, (900, y + (text.get_height()) * 2))

    tmp = str(state.next_move)
    if state.next_move[-1] == 'R':
        tmp = tmp[0:(len(tmp) - 1)]
    text = BODY_FONT_EXTRA_SMALL.render("Move: " + tmp, 1, BLACK)
    win.blit(text, (adjusted_x, y + (text.get_height()) * 3))
    text = BODY_FONT_EXTRA_SMALL.render("Roll: " + str(state.next_roll), 1, BLACK)
    win.blit(text, (900, y + (text.get_height()) * 3))

    text = BODY_FONT_EXTRA_SMALL.render("White off: " + str(len(state.white_off)), 1, BLACK)
    win.blit(text, (adjusted_x, y + (text.get_height()) * 4))
    text = BODY_FONT_EXTRA_SMALL.render("Red off: " + str(len(state.red_off)), 1, BLACK)
    win.blit(text, (900, y + (text.get_height()) * 4))


def compute_game(p1, p2, time_limit, is_deterministic, print_to_console, init_state):
    return gm.run(p1, p2, TIME_LIMIT, is_deterministic, False, None)


def run(window, p1, p2, deterministic, game):
    """
    :param window: window to draw on
    :param p1: player 1. Can be an agent (of type BackgammonPlayer) if client is playing offline or just a nickname
    (a string) if client was playing online. In the first case, run() will compute a game. In the second, run() will
    use the already computed game (recall that server computes games before returning them).
    :param p2: player 2. same as above
    :param game: either None or a fully computed game
    """

    if DEBUG:
        print("ingame screen")

    turn = 0  # -1 means a full game has been played out.
    display_delay = 18  # can adjust for shorter/longer turns
    delay_count = 0  # must reach display_delay to increment one "turn"
    play = False  # start on pause
    clock = pygame.time.Clock()
    global computing_game
    global clock_speed_index

    draw(window, None, turn, play)
    if not game:
        player_names[0] = p1.nickname()
        player_names[1] = p2.nickname()

        # https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(compute_game, p1, p2, TIME_LIMIT, deterministic, False, None)
            game = future.result()

        # other threading solutions
        # async_result = pool.apply_async(compute_game, (p1, p2, TIME_LIMIT, DETERMINISTIC, False, None))
        # game = async_result.get()

        # thread = threading.Thread(target=compute_game, args=(p1, p2, TIME_LIMIT, DETERMINISTIC, False, None))
        # thread.start()
        # game = thread.join()

        # game = gm.run(p1, p2, TIME_LIMIT, DETERMINISTIC, False, None)

    else:
        player_names[0] = p1
        player_names[1] = p2
        buttons[len(buttons) - 1].text = "Exit"
        computing_game = False
    game_record = game[0]
    winner = game[1]

    while True:
        clock.tick(CLOCK_SPEEDS[clock_speed_index])

        # increments counter
        if play:
            if turn != -1 and delay_count == display_delay:
                delay_count = 0
                if turn + 1 < len(game_record) * 2:
                    turn += 1
                else:
                    play = False
                if DEBUG:
                    print('turn ' + str(turn))
            else:
                delay_count += 1

        # handles button events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for b in buttons:
                    if b.click(pos):
                        if b.button_id == "Play":
                            play = not play
                        else:
                            if b.button_id == "Faster":
                                if clock_speed_index + 1 < len(CLOCK_SPEEDS):
                                    clock_speed_index += 1
                            elif b.button_id == "Slower":
                                if clock_speed_index > 0:
                                    clock_speed_index -= 1
                            else:
                                play = False  # all buttons cause auto pause
                                if b.button_id == "Step_Next":
                                    if turn + 1 < len(game_record) * 2:
                                        turn += 1
                                elif b.button_id == "Step_Prev":
                                    if turn > 0:
                                        turn -= 1

                                elif b.button_id == "Reset":
                                    turn = 0
                                    clock_speed_index = 3
                                elif b.button_id == "Rerun":
                                    if online:
                                        exit()
                                    else:
                                        turn = 0
                                        clock_speed_index = 3
                                        draw(window, None, turn, play)
                                        with concurrent.futures.ThreadPoolExecutor() as executor:
                                            future = executor.submit(compute_game, p1, p2, TIME_LIMIT, DETERMINISTIC, False, None)
                                            game = future.result()
        draw(window, game, turn, play)
