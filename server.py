import socket
import _thread
import curses, datetime


HOST = '0.0.0.0'   # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
conns = {}
ban_list = []
nicks = {}

start = datetime.datetime.now()

def command_log(*args):
    '''
        Reads out the log file
        Takes in nothing
    '''
    with open("log.txt", "r") as r:
        print(r.read())


def command_conns(*args):
    '''
    Prints out active connections
    Takes in nothing
    '''
    for connection in conns:
        if args:
            if str(connection) in args:
                print("Connection with: \n Name: ", nicks[connection], "\n TCP address: ",
                      conns[connection])

        else:
            print("Connection with: \n Name: ", nicks[connection], "\n TCP address: ",
              conns[connection])


def command_disconnect(*args):
    '''
    Disconnects the provided players
    Takes in players ids
    '''
    for name in args:
        for nick in nicks:
            if nicks[nick] == name:
                conn = nick
                break

        if conn in conns:
            print("Yo")
            conn.sendall(b"dc")

        else:
            print("Invalid name")


def command_ban(*args):
    '''
    Bans provided address
    Takes in ip address
    '''
    for ban in args:
        ban_list.append(ban)


def command_print_ban_list(*args):
    '''
    Prints out ban list
    Takes in nothing
    '''
    print(ban_list)


def command_unban(*args):
    '''
    Un-bans provided address
    Takes in ip address
    '''
    for address in args:
        if address in ban_list:
            ban_list.remove(address)
        else:
            print(address + ":", "Invalid address")


def command_shutdown(*args):
    '''
    Shutdowns the server
    Takes in nothing
    '''
    for id in conns:
        conns[id].sendall(b"dc")

    quit()


def command_list_commands(*args):
    '''
    Lists all commands
    Takes in nothing
    '''
    for command in commands:
        print(command)


def command_man(*args):
    '''
    Shows what a command does
    Takes in commands
    '''
    for command in args:
        if command in commands:
            print(command + ":", commands[command].__doc__)
        else:
            print(command + ":", "Invalid command")


def command_uptime(*args):
    '''
    Show how long the server has been on
    Takes in nothing
    '''
    date = datetime.datetime.now()

    print(date - start)


def command_address(*args):
    '''
    Show the address and the port of the server
    Takes in nothing
    '''
    print("IP: ", HOST)
    print("PORT: ", PORT)


def command_restart(*args):
    '''
    Restarts the server
    Takes in nothing
    '''
    command_disconnect(*conns)
    print("Not yet implemented")

commands = {"log": command_log,
            "conns": command_conns,
            "dc": command_disconnect,
            "ban": command_ban,
            "shutdown": command_shutdown,
            "lc": command_list_commands,
            "man": command_man,
            "lb": command_print_ban_list,
            "unban": command_unban,
            "uptime": command_uptime,
            "restart": command_restart,
            "address": command_address
            }


def log(text):
    with open("log.txt", "a") as r:
        r.write(str(datetime.datetime.now()))
        r.write("\n")
        r.write(str(text))
        r.write("\n")
        r.write("\n")


def remove_user(conn):
    if conn in conns:
        del nicks[conn]
        del conns[conn]


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


def console(stdscr):
    with open("log.txt", "w") as r:
        r.write(str(datetime.datetime.now()))
        r.write("\n")
        r.write("Server Started! \n")
        r.write("\n")

    while True:
        c = input(stdscr, ">> ", curses.LINES-1)

        command = c.split(" ")
        expressions = command[1:]

        if command[0] in commands:
            commands[command[0]](*expressions)

        else:
            try:
                exec(c)

            except (NameError, SyntaxError) as e:
                print(e)


def new_client(conn, addr):
    print("Connection started with:", addr)

    log("Connection started with: " + str(addr))

    t = nicks[conn] + ": connected"
    for a in conns:
        if a != conn:
            a.sendall(t.encode())

    while True:
        try:
            data = conn.recv(1024).decode("utf-8")
        except ConnectionResetError:
            print("Connection ended with:", addr)

            log("Connection ended with: " + str(addr))

            t = nicks[conn] + ": disconnected"
            for a in conns:
                if a != conn:
                    a.sendall(t.encode())

            remove_user(conn)
            break

        if conn not in conns:
            print("Connection ended with:", addr)

            log("Connection ended with: " + str(addr))

            t = nicks[conn] + ": disconnected"
            for a in conns:
                if a != conn:
                    a.sendall(t.encode())
            break

        else:
            print(addr, ": ", data)

            log(str(addr) + " : " + str(data))

            t = nicks[conn] + ": " + data
            for a in conns:
                if a != conn:
                    a.sendall(t.encode())


def c_main(stdscr):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(2)

        _thread.start_new_thread(console, (stdscr, ))
        print("Server Started")

        while True:
            conn, addr = s.accept()

            if addr[0] in ban_list:
                conn.close()

            else:
                nick = conn.recv(1024).decode("utf-8")
                conns[conn] = addr
                nicks[conn] = nick

                _thread.start_new_thread(new_client, (conn, addr))


def main() -> None:
    return curses.wrapper(c_main)


if __name__ == '__main__':
    main()