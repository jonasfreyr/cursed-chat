import socket
import _thread
import curses


HOST = '127.0.0.1'   # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
conns = []
nicks = {}
def server_controller():
    global connects
    while True:
        comm = input(">> ")
        listi = comm.split(" ")

        if (listi[0] == "dc"):
            for a in nicks:
                print(listi[1], ":", nicks[a])
                if nicks[a] == listi[1]:
                    conns.remove(a)


def new_client(conn, addr):
    print("Connection started with:", addr)

    t = nicks[conn] + ": connected"
    for a in conns:
        if a != conn:
            a.sendall(t.encode())

    while True:
        try:
            data = conn.recv(1024).decode("utf-8")
        except ConnectionResetError:
            print("Connection ended with:", addr)

            t = nicks[conn] + ": disconnected"
            for a in conns:
                if a != conn:
                    a.sendall(t.encode())

            conns.remove(conn)
            break

        if conn not in conns:
            print("Connection ended with:", addr)

            t = nicks[conn] + ": disconnected"
            for a in conns:
                if a != conn:
                    a.sendall(t.encode())
            break

        else:
            print(addr, ": ", data)

            t = nicks[conn] + ": " + data
            for a in conns:
                if a != conn:
                    a.sendall(t.encode())


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(2)

    _thread.start_new_thread(server_controller, ())
    print("Server Started")

    while True:
        conn, addr = s.accept()

        nick = conn.recv(1024).decode("utf-8")
        conns.append(conn)
        nicks[conn] = nick

        _thread.start_new_thread(new_client, (conn, addr))
