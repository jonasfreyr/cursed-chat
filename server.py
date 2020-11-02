import socket
import threading
import curses, datetime, sys
from client import input

HOST = '0.0.0.0'   # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
conns = {}
ban_list = []
nicks = {}

start = datetime.datetime.now()

out_put = []
STRING = ''

def command_log(strscr, *args):
    '''
        Reads out the log file
        Takes in nothing
    '''
    with open("log.txt", "r") as r:
        print(strscr, r.read())


def command_conns(strscr, *args):
    '''
    Prints out active connections
    Takes in nothing
    '''
    for connection in conns:
        if args:
            if str(connection) in args:
                print(strscr, "Connection with: \n Name: ", nicks[connection], "\n TCP address: ",
                      conns[connection])

        else:
            print(strscr, "Connection with: \n Name: ", nicks[connection], "\n TCP address: ",
              conns[connection])


def command_disconnect(strscr, *args):
    '''
    Disconnects the provided players
    Takes in players ids
    '''
    conn = ""
    for name in args:
        for nick in nicks:
            if nicks[nick] == name:
                conn = nick

                if conn in conns:
                    conn.sendall(b"dc")

        else:
            print(strscr, "Invalid name")


def command_ban(strscr, *args):
    '''
    Bans provided address
    Takes in ip address
    '''
    for ban in args:
        ban_list.append(ban)


def command_print_ban_list(strscr, *args):
    '''
    Prints out ban list
    Takes in nothing
    '''
    print(strscr, *ban_list)


def command_unban(strscr, *args):
    '''
    Un-bans provided address
    Takes in ip address
    '''
    for address in args:
        if address in ban_list:
            ban_list.remove(address)
        else:
            print(strscr, address + ":", "Invalid address")


def command_shutdown(strscr, *args):
    '''
    Shutdowns the server
    Takes in nothing
    '''
    for conn in conns:
        conn.sendall(b"dc")

    sys.exit()


def command_list_commands(strscr, *args):
    '''
    Lists all commands
    Takes in nothing
    '''
    # for command in commands:
    print(strscr, *commands)


def command_man(strscr, *args):
    '''
    Shows what a command does
    Takes in commands
    '''
    for command in args:
        if command in commands:
            print(strscr, command + ":", commands[command].__doc__)
        else:
            print(strscr, command + ":", "Invalid command")


def command_uptime(strscr, *args):
    '''
    Show how long the server has been on
    Takes in nothing
    '''
    date = datetime.datetime.now()

    print(strscr, str(date - start))


def command_address(strscr, *args):
    '''
    Show the address and the port of the server
    Takes in nothing
    '''
    print(strscr, "IP: ", HOST, "\nPORT: ", PORT)


def command_restart(strscr, *args):
    '''
    Restarts the server
    Takes in nothing
    '''
    # command_disconnect(*conns)
    print(strscr, "Not yet implemented")


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


def refresh_input(stdscr):
    global STRING
    stdscr.addstr(curses.LINES-1, 0, ">> ")
    stdscr.clrtoeol()
    stdscr.addstr(STRING)


def print(stdscr, *args):
    str_args = []
    for element in args:
        str_args.append(str(element))

    text = " ".join(str_args)

    text_list = text.split("\n")

    text_list.reverse()

    stdscr.clear()
    for index, text in enumerate(text_list):
        if curses.LINES - 2 - index > 0:
            stdscr.insstr(curses.LINES - 2 - index, 0, str(text))


def console(stdscr):
    t = threading.Thread(target=c_main, args=(stdscr,))
    t.daemon = True
    t.start()
    with open("log.txt", "w") as r:
        r.write(str(datetime.datetime.now()))
        r.write("\n")
        r.write("Server Started! \n")
        print(stdscr, "Server Started")
        r.write("\n")

    while True:
        c = input(stdscr, ">> ", curses.LINES-1)

        command = c.split(" ")
        expressions = command[1:]

        if command[0] in commands:
            commands[command[0]](stdscr, *expressions)
        '''
        else:
            try:
                exec(c)

            except (NameError, SyntaxError) as e:
                print(e)
        '''


def new_client(conn, addr):
    # print("Connection started with:", addr)

    log("Connection started with: " + str(addr))

    t = nicks[conn] + ": connected"
    for a in conns:
        if a != conn:
            a.sendall(t.encode())

    while True:
        try:
            data = conn.recv(1024).decode("utf-8")
        except ConnectionResetError:
            # print("Connection ended with:", addr)

            log("Connection ended with: " + str(addr))

            t = nicks[conn] + ": disconnected"
            for a in conns:
                if a != conn:
                    a.sendall(t.encode())

            remove_user(conn)
            break

        if conn not in conns:
            # print("Connection ended with:", addr)

            log("Connection ended with: " + str(addr))

            t = nicks[conn] + ": disconnected"
            for a in conns:
                if a != conn:
                    a.sendall(t.encode())
            break

        else:
            # print(addr, ": ", data)

            log(str(addr) + " : " + str(data))

            t = nicks[conn] + ": " + data
            for a in conns:
                if a != conn:
                    a.sendall(t.encode())


def c_main(stdscr):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(2)

        # _thread.start_new_thread(console, (stdscr, ))
        while True:
            conn, addr = s.accept()

            if addr[0] in ban_list:
                conn.close()

            else:
                nick = conn.recv(1024).decode("utf-8")
                conns[conn] = addr
                nicks[conn] = nick

                # _thread.start_new_thread(new_client, (conn, addr))
                t = threading.Thread(target=new_client, args=(conn, addr))
                t.daemon = True
                t.start()


def main() -> None:
    return curses.wrapper(console)


if __name__ == '__main__':
    main()