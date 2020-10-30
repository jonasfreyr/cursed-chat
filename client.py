import curses, socket, _thread

messages = []
STRING = ''


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
        elif char == curses.KEY_BACKSPACE or char == '\x08':
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
        stdscr.insstr(curses.LINES - 2 - index, 0, str(message))

    refresh_input(stdscr)

    stdscr.refresh()


def receive_data(conn, stdscr) -> None:
    while True:
        data = conn.recv(1024).decode("utf-8")

        messages.insert(0, data)

        print_messages(stdscr)


def c_main(stdscr) -> None:
    # host = input(stdscr, "Input Address: ")
    # port = input(stdscr, "Input Port: ")

    host = "127.0.0.1"
    port = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        name = input(stdscr, "Input Name: ", curses.LINES-1)

        nameE = name.encode()
        s.sendall(nameE)
        while True:
            _thread.start_new_thread(receive_data, (s, stdscr))
            message = input(stdscr, ">> ", curses.LINES-1)

            messages.insert(0, (name + ": " + message))

            print_messages(stdscr)

            message = message.encode()
            s.sendall(message)

def main() -> None:
    return curses.wrapper(c_main)


if __name__ == '__main__':
    exit(main())
