import threading, os, socket
import curses, datetime, sys
from requests import get
from client import input, refresh_input

WAN_IP = get('https://api.ipify.org').text
LOCAL_IP = socket.gethostbyname(socket.gethostname())
# print('My public IP address is: {}'.format(ip))

HOST = '0.0.0.0'   # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
conns = {}
ban_list = []
nicks = {}

start = datetime.datetime.now()

out_put = []
STRING = ''
STREAM = False
stdscr = ""
THREADS = []
BANNED_TEXT_FILE = "ban_list.txt"
LOG_TEXT_FILE = "log.txt"
MAX_SIZE_OF_LOG = 500

def command_log(strscr, *args):
    '''
    Reads out the log file
    Takes in nothing
    -stream Turns on stream mode
    '''
    global STREAM

    with open(LOG_TEXT_FILE, "r") as r:
        insert_to_output(r.read())

    if "-stream" in args:
        STREAM = not STREAM
        if STREAM:
            insert_to_output("stream mode on")
        else:
            insert_to_output("stream mode off")


def command_conns(strscr, *args):
    '''
    Prints out active connections
    Takes in nothing
    '''
    if len(conns) == 0:
        insert_to_output("No active connections!")
        return

    for connection in conns:
        insert_to_output("Connection with: \n Name: ", nicks[connection], "\n TCP address: ",
                             conns[connection])


def command_disconnect(strscr, *args):
    '''
    Disconnects the provided players
    Takes in players ids
    '''
    for name in args:
        for nick in nicks:
            if nicks[nick] == name:
                conn = nick

                if conn in conns:
                    conn.sendall(b"dc")
                    conn.close()
                    remove_user(conn)
                    break

        else:
            insert_to_output("Invalid name")


def command_ban(strscr, *args):
    '''
    Bans provided address
    Takes in ip address
    '''
    for ban in args:
        ban_list.append(ban)

    write_ban_list()


def command_print_ban_list(strscr, *args):
    '''
    Prints out ban list
    Takes in nothing
    '''
    insert_to_output("BAN LIST:")
    for banned in ban_list:
        insert_to_output("  " + str(banned))


def write_ban_list():
    with open(BANNED_TEXT_FILE, "w") as r:
        for ban in ban_list:
            r.write(ban + "\n")


def command_unban(strscr, *args):
    '''
    Un-bans provided address
    Takes in ip address
    '''
    for address in args:
        if address in ban_list:
            ban_list.remove(address)
        else:
            insert_to_output(address + ":", "Invalid address")

    write_ban_list()


def command_shutdown(strscr, *args):
    '''
    Shutdowns the server
    Takes in nothing
    '''
    for conn in conns:
        conn.sendall(b"dc")

    log("Server shutting down!")

    sys.exit()


def command_list_commands(strscr, *args):
    '''
    Lists all commands
    Takes in nothing
    '''
    # for command in commands:
    insert_to_output(*commands)


def command_man(strscr, *args):
    '''
    Shows what a command does
    Takes in commands
    '''
    for command in args:
        if command in commands:
            insert_to_output(command + ":", commands[command].__doc__)
        else:
            insert_to_output(command + ":", "Invalid command")


def command_uptime(strscr, *args):
    '''
    Show how long the server has been on
    Takes in nothing
    '''
    date = datetime.datetime.now()

    insert_to_output(str(date - start))


def command_address(strscr, *args):
    '''
    Show the address and the port of the server
    Takes in nothing
    '''
    insert_to_output("WAN IP: ", WAN_IP, "\nLocal IP: ", LOCAL_IP, "\nPORT: ", PORT)


def command_restart(strscr, *args):
    '''
    Restarts the server
    Takes in nothing
    Unreliable for anything other than linux
    '''
    for conn in conns:
        command_disconnect(nicks[conn])
    insert_to_output("Server restarting")
    os.execl(sys.executable, sys.executable, *sys.argv)


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
    log_size = os.path.getsize(LOG_TEXT_FILE) / 1000000
    if log_size < MAX_SIZE_OF_LOG:
        with open(LOG_TEXT_FILE, "a") as r:
            r.write(str(datetime.datetime.now()))
            r.write("\n")
            r.write(str(text))
            r.write("\n")
            r.write("\n")

    if STREAM:
        text_o = str(datetime.datetime.now())
        text_o += "\n"
        text_o += str(text)
        text_o += "\n"
        text_o += "\n"
        insert_to_output(text_o)

        print_output(stdscr)
        refresh_input(stdscr)


def remove_user(conn):
    if conn in conns:
        del nicks[conn]
        del conns[conn]


def insert_to_output(*args):
    str_args = []
    for element in args:
        str_args.append(str(element))

    text = " ".join(str_args)

    # text = text.strip()
    if text[-1] == "\n":
        text = text[:-1]

    text_list = text.split("\n")

    text_list.reverse()

    out_put.insert(0, text_list)


def print_output(stdscr):
    index = 0
    stdscr.clear()
    for element in out_put:
        for text in element:
            if curses.LINES - 2 - index > 0:
                stdscr.insstr(curses.LINES - 2 - index, 0, str(text))

            index += 1
        if curses.LINES - 2 - index > 0:
            stdscr.insstr(curses.LINES - 2 - index, 0, "-----------------------")
            index += 1


def console(yes):
    global stdscr
    stdscr = yes
    t = threading.Thread(target=c_main, args=(stdscr,))
    t.daemon = True
    t.start()
    with open(LOG_TEXT_FILE, "w") as r:
        r.write(str(datetime.datetime.now()))
        r.write("\n")
        r.write("Server Started! \n")
        insert_to_output("Server Started")
        r.write("\n")

    with open(BANNED_TEXT_FILE, "r") as r:
        banned_text = r.read()

    banned_list = banned_text.split()
    for banned in banned_list:
        ban_list.append(banned)

    print_output(stdscr)
    while True:
        stdscr.insstr(curses.LINES - 1, 0, ">> ")
        # curses.echo()
        # c = stdscr.getstr(curses.LINES-1, 3).decode(encoding="utf-8")
        # curses.echo(False)
        c = input(stdscr, ">> ", curses.LINES-1)
        # print(stdscr, c)
        command = c.split(" ")
        expressions = command[1:]

        if command[0] in commands:
            commands[command[0]](stdscr, *expressions)

        print_output(stdscr)

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
    conns_copy = conns.copy()
    for a in conns_copy:
        if a != conn:
            try:
                a.sendall(t.encode())
            except:
                log("Connection ended with: " + conn.getsockname()[0])
                a.close()
                remove_user(a)

    last_message = []
    while True:
        try:
            data = conn.recv(1024).decode("utf-8")

            if len(last_message) >= 5:
                now = datetime.datetime.now()
                summ = datetime.datetime(1, 1, 1)
                for date in last_message:
                    summ += now - date

                if summ.second <= 2:
                    log("Connection ended with: " + str(addr))
                    conn.sendall(b"dc")
                    remove_user(conn)
                    conn.close()
                    break

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

            if conn in nicks:
                t = nicks[conn] + ": disconnected"
                for a in conns:
                    if a != conn:
                        a.sendall(t.encode())
            break

        else:
            # print(addr, ": ", data)
            last_message.append(datetime.datetime.now())

            if len(last_message) > 5:
                last_message.remove(last_message[0])

            if data != "":
                log(str(addr) + " : " + str(data))

                t = nicks[conn] + ": " + data

                conns_copy = conns.copy()
                for a in conns_copy:
                    if a != conn:
                        try:
                            a.sendall(t.encode())
                        except:
                            log("Connection ended with: " + conn.getsockname()[0])
                            a.close()
                            remove_user(a)


def c_main(yes):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(2)

        # _thread.start_new_thread(console, (stdscr, ))
        connected_date_dict = {}
        while True:
            conn, addr = s.accept()

            if conn not in connected_date_dict:
                connected_date_dict[addr[0]] = datetime.datetime.now()

            elif (datetime.datetime.now() - connected_date_dict[addr[0]]).seconds <= 2:
                connected_date_dict[addr[0]] = datetime.datetime.now()
                conn.close()
                continue

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

                THREADS.append(t)


def main() -> None:
    try:
        return curses.wrapper(console)

    except:
        log(sys.exc_info()[0])
        sys.exit()


if __name__ == '__main__':
    main()