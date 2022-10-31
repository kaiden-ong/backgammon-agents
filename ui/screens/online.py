"""
This file contains the online screen.
"""
from ui.ui_objects import *
import server.server_constants
import socket
import pickle
import pygame
import math

DEBUG = True
# local display values
right_x = BIG_MARGIN + round(WIDTH_INSIDE_MARGIN / 2)
far_right_x = BIG_MARGIN * 2 + WIDTH_INSIDE_MARGIN
y_scaling = (BUTTON_DIMENSIONS[2][1] + PADDING)
left_col_x = BIG_MARGIN + PADDING
right_col_x = round(BIG_MARGIN / 2 + WINDOW_WIDTH / 2 + PADDING)
UPLOAD_NEW_AGENT = False
SUCCESSFUL_UPLOAD_TIMER = 0

shown_ta_agents = 0  # this is an index to figure out which ta agents to show
# ta_buttons, ta_agents, student_buttons, student_agents will all be populated when this screen is loaded.
# for now, they hold filler values.
ta_agents = []
ta_buttons = [
    Button("ta_0", "(waiting on server)", left_col_x, 100 + y_scaling, GRAY, 2),
    Button("ta_1", "(waiting on server)", left_col_x, 100 + y_scaling * 2, GRAY, 2),
    Button("ta_2", "(waiting on server)", left_col_x, 100 + y_scaling * 3, GRAY, 2),
]

student_agents = []
student_buttons = [
    Button("student_0", "(waiting on server)", right_col_x, 100 + y_scaling * 2, GRAY, 2),
    Button("student_1", "(waiting on server)", right_col_x, 100 + y_scaling * 3, GRAY, 2),
    Button("student_2", "(waiting on server)", right_col_x, 100 + y_scaling * 4, GRAY, 2),
    Button("student_3", "(waiting on server)", right_col_x, 100 + y_scaling * 5, GRAY, 2),
    Button("student_4", "(waiting on server)", right_col_x, 100 + y_scaling * 6, GRAY, 2),
]
shown_student_agents = 0  # simliar to shown_ta_agents
buttons = [
    Button("ta_prev", "Prev", right_x - (PADDING + BUTTON_DIMENSIONS[1][0]) * 2, 100 + y_scaling * 4, PURPLE, 1),
    Button("ta_next", "Next", right_x - PADDING - BUTTON_DIMENSIONS[1][0], 100 + y_scaling * 4, PURPLE, 1),
    Button("student_prev", "Prev", far_right_x - (PADDING + BUTTON_DIMENSIONS[1][0]) * 2, 100 + y_scaling * 7 + PADDING * 2, PURPLE, 1),
    Button("student_next", "Next", far_right_x - PADDING - BUTTON_DIMENSIONS[1][0], 100 + y_scaling * 7 + PADDING * 2, PURPLE, 1),
    Button("upload", "Upload", right_x - PADDING - BUTTON_DIMENSIONS[1][0], 100 + y_scaling * 7 + PADDING * 2, PURPLE, 1),
    Button("logout", "Logout", far_right_x - BUTTON_DIMENSIONS[1][0], 75 / 2 - BUTTON_DIMENSIONS[1][1] / 2, GRAY, 3)
]
search_text_box = InputBox(right_col_x + 100, 100 + y_scaling - PADDING, 160, 33, "")


def receive_data(conn):
    """
    Used to receive data from the server (see server.py for communication protocol)
    """
    msg_length = conn.recv(server_constants.HEADER).decode(server_constants.FORMAT)
    if msg_length:
        msg_length = int(msg_length)
    msg = pickle.loads(conn.recv(msg_length))
    if msg == server_constants.DISCONNECT_MESSAGE:
        connected = False
    print(f"[RECEIVED]: {msg}")
    return msg


def send_data(client, msg):
    """
    Used to send a msg to the server (see server.py for communication protocol)
    """
    message = pickle.dumps(msg)
    send_length = str(len(message)).encode(server_constants.FORMAT)
    send_length += b' ' * (server_constants.HEADER - len(send_length))
    client.send(send_length)
    client.send(message)


def redraw_window(win, player1, search_student):
    """
    :param win: window to draw on
    :param player1: the client's agent (BackgammonPlayer)
    :param search_student: search string
    """
    global SUCCESSFUL_UPLOAD_TIMER
    win.fill(GRAY)

    pygame.draw.rect(win, PURPLE, (0, 0, WINDOW_WIDTH, 75))
    text = SUB_TITLE_FONT.render("BACKGAMMON - ONLINE", 1, WHITE)
    win.blit(text, (BIG_MARGIN - PADDING * 2, PADDING * 3))

    # draws the "TA Bots" tab
    y = 75 + PADDING * 2
    x = BIG_MARGIN
    pygame.draw.rect(win, WHITE, (x, y, round(WIDTH_INSIDE_MARGIN / 2), 50 * TA_BOX_DISPLAY_SIZE + 90))
    text = BODY_FONT_BOLD.render("TA Bots", 1, WHITE)
    pygame.draw.rect(win, PURPLE, (x, y, round(WIDTH_INSIDE_MARGIN / 2), text.get_height() + PADDING))
    y += PADDING
    win.blit(text, (x + PADDING, y))
    for i in range(TA_BOX_DISPLAY_SIZE):
        i_adjusted = i + shown_ta_agents
        if i_adjusted >= len(ta_agents):
            break
        ta_buttons[i].text = ta_agents[i_adjusted]
        ta_buttons[i].draw(win)

    s = "Page " + str(round((shown_ta_agents / 3) + 1)) + " of " + str(math.ceil(len(ta_agents) / 3))
    text = BODY_FONT_EXTRA_SMALL.render(s, 1, BLACK)
    y = 290  # position after printing 3 buttons for TA bots
    win.blit(text, (right_x - (PADDING + BUTTON_DIMENSIONS[1][0]) * 2 - text.get_width() - PADDING,
                    round(y + (BUTTON_DIMENSIONS[1][1] - text.get_height()) / 2)))

    # draws the "Profile" tab
    y += BIG_MARGIN + PADDING * 2
    base = y + 140
    pygame.draw.rect(win, WHITE, (x, y, round(WIDTH_INSIDE_MARGIN / 2), base - y))
    text = BODY_FONT_BOLD.render("Profile", 1, WHITE)
    pygame.draw.rect(win, PURPLE, (x, y, round(WIDTH_INSIDE_MARGIN / 2), text.get_height() + PADDING))
    win.blit(text, (x + PADDING, y + PADDING))
    y += PADDING + text.get_height()
    pygame.draw.rect(win, GRAY,
                     (x + PADDING, y + PADDING,
                      round(WIDTH_INSIDE_MARGIN / 2) - PADDING * 2, 40))
    changed_text = ""
    if UPLOAD_NEW_AGENT:
        changed_text = "*"
        text = BODY_FONT_EXTRA_SMALL.render("Note: uploading will overwrite your old agent.", 1, BLACK)
        win.blit(text, (right_x - (PADDING * 2 + text.get_width() + BUTTON_DIMENSIONS[1][0]),
                        round(450 + (BUTTON_DIMENSIONS[1][1] - text.get_height()) / 2)))
        buttons[4].text = "Confirm"
    elif SUCCESSFUL_UPLOAD_TIMER > 0:
        SUCCESSFUL_UPLOAD_TIMER -= 1
        buttons[4].text = "Done!"
        buttons[4].color = GOLD
    else:
        buttons[4].text = "Upload"
        buttons[4].color = PURPLE

    text = BODY_FONT_SMALL.render("Current Agent: " + player1.nickname() + changed_text, 1, BLACK)
    win.blit(text, (x + PADDING * 2, round(y + PADDING / 2 + text.get_height() / 2)))
    text = BODY_FONT_SMALL.render("Total Wins: -1", 1, BLACK)  # should calculated from a server call to a db
    win.blit(text, (x - PADDING * 2 + round(WIDTH_INSIDE_MARGIN / 2 - text.get_width()),
                    round(y + PADDING / 2 + text.get_height() / 2)))

    # draws the "Students" tab
    x = round(BIG_MARGIN / 2 + WINDOW_WIDTH / 2)
    y = 75 + PADDING * 2
    pygame.draw.rect(win, WHITE, (x, y, round(WIDTH_INSIDE_MARGIN / 2), base - y))
    text = BODY_FONT_BOLD.render("Students", 1, WHITE)
    pygame.draw.rect(win, PURPLE, (x, y, round(WIDTH_INSIDE_MARGIN / 2), text.get_height() + PADDING))
    y += PADDING
    win.blit(text, (x + PADDING, y))
    text = BODY_FONT.render("Search: ", 1, BLACK)
    win.blit(text, (right_col_x, 100 + y_scaling - PADDING))
    pygame.draw.line(win, BLACK, (right_col_x, 100 + y_scaling + text.get_height()),
                     (right_col_x + round(WIDTH_INSIDE_MARGIN / 2) - PADDING * 2, 100 + y_scaling + text.get_height())
                     , 2)
    pygame.draw.line(win, BLACK, (right_col_x, 100 + y_scaling * 7),
                     (right_col_x + round(WIDTH_INSIDE_MARGIN / 2) - PADDING * 2, 100 + y_scaling * 7)
                     , 2)

    for i in range(STUDENT_BOX_DISPLAY_SIZE):
        i_adjusted = i + shown_student_agents
        if i_adjusted >= len(student_agents):
            break

        for b in student_agents:  # double for loop to match search string. potentially slow on high numbers of students.
            if b.upper().startswith(search_student.upper()):  # search is case insensitive
                student_buttons[i].text = student_agents[i_adjusted]
                student_buttons[i].draw(win)
                break
    s = "Page " + str(round((shown_student_agents / STUDENT_BOX_DISPLAY_SIZE) + 1)) + " of " \
        + str(math.ceil(len(student_agents) / STUDENT_BOX_DISPLAY_SIZE))
    text = BODY_FONT_EXTRA_SMALL.render(s, 1, BLACK)
    win.blit(text, (far_right_x - (PADDING + BUTTON_DIMENSIONS[1][0]) * 2 - text.get_width() - PADDING,
                    round(100 + y_scaling * 7 + PADDING * 2 + (BUTTON_DIMENSIONS[1][1] - text.get_height()) / 2)))

    for b in buttons:
        b.draw(win)

    search_text_box.draw(win)

    # draw_grid_lines(win)
    pygame.display.update()


def handle_all_buttons(b, conn, pos, player1):
    """
    :param b: which button
    :param conn: handles connection to server
    :param pos: where the click
    :param player1: client's agent
    :return: after an opponent is clicked, returns the info required to shift to INGAME screen
    """
    global shown_student_agents
    global shown_ta_agents
    global UPLOAD_NEW_AGENT
    global SUCCESSFUL_UPLOAD_TIMER

    if b.click(pos):
        selected_button = b.button_id.split("_")
        if selected_button[0] == "ta":
            assert (len(selected_button) == 2)
            if selected_button[1] == "prev":
                if shown_ta_agents >= TA_BOX_DISPLAY_SIZE:
                    shown_ta_agents -= TA_BOX_DISPLAY_SIZE
            elif selected_button[1] == "next":
                if shown_ta_agents + TA_BOX_DISPLAY_SIZE < len(ta_agents):
                    shown_ta_agents += TA_BOX_DISPLAY_SIZE
            else:
                print("clicked ta_" + str(int(selected_button[1]) + shown_ta_agents))
                send_data(conn, "play game")
                send_data(conn, player1)
                send_data(conn, ta_agents[int(selected_button[1]) + shown_ta_agents])
                computed_game = receive_data(conn)
                send_data(conn, "success")
                return "INGAME", ta_agents[int(selected_button[1]) + shown_ta_agents], computed_game
        elif selected_button[0] == "student":
            if selected_button[1] == "prev":
                if shown_student_agents >= STUDENT_BOX_DISPLAY_SIZE:
                    shown_student_agents -= STUDENT_BOX_DISPLAY_SIZE
            elif selected_button[1] == "next":
                if shown_student_agents + STUDENT_BOX_DISPLAY_SIZE < len(student_agents):
                    shown_student_agents += STUDENT_BOX_DISPLAY_SIZE
            else:
                print("clicked students_" + str(int(selected_button[1]) + shown_student_agents))
                send_data(conn, "play game")
                send_data(conn, player1)
                send_data(conn, student_agents[int(selected_button[1]) + shown_student_agents])
                computed_game = receive_data(conn)
                send_data(conn, "success")
                return "INGAME", student_agents[int(selected_button[1]) + shown_student_agents], computed_game
        elif b.button_id == "upload":
            if b.text == "Upload":  # upload agent to server.
                UPLOAD_NEW_AGENT = True
                print("confirming upload")
            elif b.text == "Confirm":
                UPLOAD_NEW_AGENT = False
                SUCCESSFUL_UPLOAD_TIMER = 150
                send_data(conn, "upload")
                send_data(conn, player1)
                print(player1.nickname() + " uploaded!")
        elif selected_button[0] == "logout":  # disconnect from server
            print("not implemented")
    return "HANDLED"


def run(win, username, p1):
    """
    :param win: window to draw on
    :param username: client's username
    :param p1: client's agent (BackgammonPlayer)
    :return:
    """
    global ta_agents
    global student_agents

    # load data from server
    try:
        # load(username, p1)
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(server_constants.ADDR)
        print("[LOADING] User " + username + " connecting to server with agent [" + p1.nickname() + "]")

        # 1. send username
        send_data(conn, username)

        # 2. send agent
        send_data(conn, p1)

        # 3. receive account status
        user_status = receive_data(conn)

        # 4. get names of student agents
        student_agents = receive_data(conn)

        # 5. get names of ta_agents (solutions)
        ta_agents = receive_data(conn)
        if user_status == "new user":
            print("[CONNECTED] Welcome " + username + ". Please upload your first bot to get started!")
        elif user_status == "recognized user":
            print("[CONNECTED] welcome back " + username)

        if DEBUG:
            print("loaded", len(student_agents), "student agents,", len(ta_agents), "ta agents.")
    except Exception as e:
        print("[ERROR]:", e, "(server may be offline)")
        return "MENU"

    clock = pygame.time.Clock()
    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                # Thanks to Python's god awful Python typing system, we cannot combine these three loops
                # 'for b in buttons, ta_buttons, student_buttons'
                # causes a type error (Buttons are then converted into generic list objects).
                result = ""
                for b in buttons:
                    result = handle_all_buttons(b, conn, pos, p1)
                for b in ta_buttons:
                    result = handle_all_buttons(b, conn, pos, p1)
                    if len(result) == 3 and result[0] == "INGAME":
                        print("changing screen to ingame")
                        return result[0], p1.nickname(), str(result[1]), result[2]
                for b in student_buttons:
                    result = handle_all_buttons(b, conn, pos, p1)
                    if len(result) == 3 and result[0] == "INGAME":
                        print("changing screen to ingame")
                        return result[0], p1.nickname(), str(result[1]), result[2]

            search_text_box.handle_event(event)
        redraw_window(win, p1, search_text_box.text)
