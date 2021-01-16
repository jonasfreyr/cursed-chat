import pyaudio
import socket
from threading import Thread

frames = []

voice_connected_date_dict = []

HOST = '0.0.0.0'   # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)


def v_main():
    # FORMAT = pyaudio.paInt16
    CHUNK = 1024
    CHANNELS = 2
    RATE = 44100

    VOICE_PORT = PORT + 1

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp:
        udp.bind((HOST, VOICE_PORT))

        while True:
                soundData, addr = udp.recvfrom(CHUNK * CHANNELS * 10)

                if addr not in voice_connected_date_dict:
                    voice_connected_date_dict.append(addr)

                for conn in voice_connected_date_dict:
                    if conn != addr:
                        udp.sendto(soundData, conn)


if __name__ == "__main__":
    v_main()
