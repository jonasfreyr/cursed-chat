import pyaudio
import socket
from threading import Thread

out_frames = []
in_frames = []

voice_port_receiving = 65432
voice_port_sending = 65433

def udpStream(udp):
    while True:
        if len(out_frames) > 0:
            udp.sendto(out_frames.pop(0), ("34.121.32.86", voice_port_sending))

    udp.close()


def receive_voice_data(udp):
    while True:
        soundData, addr = udp.recvfrom(CHUNK * CHANNELS * 10)
        in_frames.append(soundData)


def record(stream, CHUNK):
    while True:
        out_frames.append(stream.read(CHUNK))


def play(stream, CHUNK):
    BUFFER = 10
    while True:
            if len(in_frames) >= BUFFER:
                while len(in_frames) != 0:
                    stream.write(in_frames.pop(0), CHUNK)


if __name__ == "__main__":
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 96000

    p = pyaudio.PyAudio()

    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(('', voice_port_receiving))

    stream_output = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK,
                    )

    stream_input = p.open(format = FORMAT,
                    channels = CHANNELS,
                    rate = RATE,
                    input = True,
                    frames_per_buffer = CHUNK,
                    )

    record_thread = Thread(target=record, args=(stream_input, CHUNK,))
    send_thread = Thread(target=udpStream, args=(udp, ))

    receive_thread = Thread(target=receive_voice_data, args=(udp, ))
    play_thread = Thread(target=play, args=(stream_output, CHUNK,))

    record_thread.setDaemon(True)
    send_thread.setDaemon(True)

    receive_thread.setDaemon(True)
    play_thread.setDaemon(True)

    record_thread.start()
    send_thread.start()
    receive_thread.start()
    play_thread.start()

    receive_thread.join()
    send_thread.join()
    receive_thread.join()
    play_thread.join()
