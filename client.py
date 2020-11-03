import curses, socket, sys, threading

messages = []
STRING = ''
host = "127.0.0.1"
port = 65432
DISCONNECTED = False


def input(stdscr, text, y=0, x=0):
    global STRING
    STRING = ''
    while True:
        stdscr.addstr(y, x, text)
        stdscr.clrtoeol()
        stdscr.addstr(STRING)

        char = stdscr.get_wch()

        # raise AssertionError(repr(char))

        if isinstance(char, str) and char.isprintable():
            STRING += char
        elif char == curses.KEY_BACKSPACE or char == '\x08' or char == '\b':
            STRING = STRING[:-1]
        elif char == '\n':
            break

        stdscr.refresh()

    return STRING


def refresh_input(stdscr):
    global STRING
    stdscr.addstr(curses.LINES-1, 0, ">> ")
    stdscr.clrtoeol()
    stdscr.addstr(STRING)


def print_messages(stdscr) -> None:
    stdscr.clear()
    for index, message in enumerate(messages):
        if curses.LINES - 2 - index > 0:
            stdscr.insstr(curses.LINES - 2 - index, 0, str(message))

    refresh_input(stdscr)

    stdscr.refresh()


def receive_data(conn, stdscr) -> None:
    global DISCONNECTED
    while True:
        data = conn.recv(1024).decode("utf-8")

        if data == "dc":
            DISCONNECTED = True

        # messages.insert(0, data)
        insert_into_messages(data)

        print_messages(stdscr)


def command_dc(s, *args):
    s.close()
    sys.exit()


def insert_into_messages(element):
    global messages
    messages.insert(0, element)


commands_dict = {
    ":dc:": command_dc
}

def c_main(stdscr) -> None:
    # host = input(stdscr, "Input Address: ")
    # port = input(stdscr, "Input Port: ")

    name = ""
    while len(name) <= 0:
        name = input(stdscr, "Input Name: ", curses.LINES - 1)

        if len(name) <= 0:
            stdscr.clear()
            stdscr.insstr(curses.LINES - 2, 0, "Name not long enough")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        nameE = name.encode()
        s.sendall(nameE)

        # _thread.start_new_thread(receive_data, (s, stdscr))


        receive_data_thread = threading.Thread(target=receive_data, args=(s, stdscr))
        receive_data_thread.daemon = True
        receive_data_thread.start()


        # process = multiprocessing.Process(target=receive_data, args=(s, stdscr))
        # process.start()

        while True:
            message = input(stdscr, ">> ", curses.LINES-1)

            if DISCONNECTED:
                command_dc(s)

            if len(message) > 0:
                msg = message.split()

                if msg[0] in commands_dict:
                    commands_dict[msg[0]](s,*msg[1:])

                insert_into_messages(name + ": " + message)

                print_messages(stdscr)

                message = message.encode()
                s.sendall(message)


def main() -> None:
    return curses.wrapper(c_main)


if __name__ == '__main__':
    main()
