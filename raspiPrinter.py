import time
from PIL import Image
import pygame
import serial
from Adafruit_Thermal import *
from Queue import Queue
from threading import Thread

notes = {'C1': 0, 'D1': 1, 'E1': 2, 'F1': 3, 'G1': 4, 'A1': 5, 'B1': 6,
         'C2': 7, 'D2': 8, 'E2': 9, 'F2': 10, 'G2': 11, 'A2': 12, 'B2': 13,
         'C3': 14}

col_lead = 10
col_width = 16
col_num = 14
col_end = 290
row_height = 32
row_height_half = row_height / 2

imgQueue = Queue()


def printerThread():
    global imgQueue

    printer = Adafruit_Thermal("/dev/ttyUSB0", 9600, timeout=5)

    while True:
        img = imgQueue.get()

        if not img:
            printer.feed(2)
        else:
            printer.printImage(img)


def imageThread(sequence):
    global imgQueue

    curr = {}
    curr_row = 0

    (note, timestamp) = sequence.get()

    start_time = timestamp - 0.5

    while note != -1:

        while curr_row < int(row_height * (timestamp - start_time) / 0.25) - 5:
            img = Image.new('RGB', (col_end + 1, 1), "white")
            pixels = img.load()

            for n in curr:
                row = int(row_height * (curr[n] - start_time) / 0.25)
                if curr_row in range(row - 5, row + 5):
                    x_cent = col_lead + col_width * n
                    for i in xrange(x_cent - 5, x_cent + 5):
                        pixels[i, 0] = (0, 0, 0)

            pixels[col_end, 0] = (0, 0, 0)

            imgQueue.put(img)

            curr_row += 1

        curr[note] = timestamp

        (note, timestamp) = sequence.get()

    while curr_row < int(row_height * (timestamp + 0.5 - start_time) / 0.25) + 5:
        img = Image.new('RGB', (col_end + 1, 1), "white")
        pixels = img.load()

        for n in curr:
            row = int(row_height * (curr[n] - start_time) / 0.25)
            if curr_row in range(row - 5, row + 5):
                x_cent = col_lead + col_width * n
                for i in xrange(x_cent - 5, x_cent + 5):
                    pixels[i, 0] = (0, 0, 0)

        pixels[col_end, 0] = (0, 0, 0)

        imgQueue.put(img)

        curr_row += 1

    imgQueue.put(None)


class Receipt:

    def startFreeRecording(self):
        self.sequence = Queue()
        self.thread = Thread(target=imageThread, args=(self.sequence,))
        self.thread.start()

    def recordFreeNote(self, note):
        self.sequence.put((note, time.time()))

    def endFreeRecording(self):
        self.sequence.put((-1, time.time()))
        self.thread.join()


def onKeyEvent(r, recording, note, channel, note_str):
    if recording:
        print note_str,
        r.recordFreeNote(note)
    pygame.mixer.Channel(channel).stop()
    pygame.mixer.Channel(channel).play(pygame.mixer.Sound('notes/note_' +
                                                          note_str +
                                                          '.wav'))


def main():
    try:
        arduino = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
    except:
        print("Please check the arduino port")
        return

    pygame.mixer.init(frequency=0, size=8, channels=1)
    pygame.mixer.set_num_channels(15)

    r = None
    quit = False
    recording = False

    printer = Thread(target=printerThread)
    printer.start()

    while not quit:
        if arduino.in_waiting:
            line = arduino.readline().decode().strip()
            if line == 'RECORDON':                   # toggle record
                recording = True
                r = Receipt()
                r.startFreeRecording()
                print('recording start')
            elif line == 'RECORDOFF':
                if recording:
                    recording = False
                    r.endFreeRecording()
                    print('\nrecording end')
            elif len(line) > 0:
                onKeyEvent(r, recording, notes[line], notes[line], line)


if __name__ == "__main__":
    main()
