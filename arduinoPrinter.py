from escpos.printer import File, Dummy
import popen2
import time
from PIL import Image
import pygame
import serial

notes = {'C1': 0, 'D1': 1, 'E1': 2, 'F1': 3, 'G1': 4, 'A1': 5, 'B1': 6,
         'C2': 7, 'D2': 8, 'E2': 9, 'F2': 10, 'G2': 11, 'A2': 12, 'B2': 13,
         'C3': 14}

col_lead = 10
col_width = 16
col_num = 14
col_end = 290
row_height = 32
row_height_half = row_height / 2


class Receipt:

    def __init__(self, uid, pid):
        self.p = Dummy()

        self.qanswered = 0
        self.id = uid
        self.pid = pid

    def startRecording(self):
        self.start_time = time.time()
        self.sequence = []
        self.chord = []

    def recordNote(self, note):
        curr_time = time.time()
        if curr_time < self.start_time + 0.125:
            self.chord.append(note)
        else:
            self.sequence.append(self.chord)
            self.chord = [note]
            num_rest = (curr_time - (self.start_time + 0.125)) / 0.125
            for r in xrange(int(num_rest)):
                self.sequence.append(None)
            self.start_time = self.start_time + (num_rest + 1) * 0.125

    def endRecording(self):
        self.sequence.append(self.chord)
        self.addSequence(self.sequence, True)

    def startFreeRecording(self):
        self.sequence = []

    def recordFreeNote(self, note):
        self.sequence.append((note, time.time()))

    def endFreeRecording(self):
        self.addFreeSequence(self.sequence)

    def saveToText(self, fn):
        f = File(fn)
        f._raw(self.p.output)
        f.cut()

    def addFreeSequence(self, sequence):
        seq_len = len(sequence)
        if seq_len != 0:
            self.createFreeSequence(sequence[0][1] - 0.5,
                                    sequence[seq_len - 1][1] + 0.5,
                                    sequence)
            self.p.image("line.ppm")

    def addSequence(self, notes_list, half=False):
        for n in notes_list:
            if n is None:
                self.addRest(half)
            else:
                self.addChord(n, half)

    def addChord(self, notes, half=False):
        if half:
            self.createChordHalf(notes)
        else:
            self.createChord(notes)
        self.p.image("line.ppm")

    def addRest(self, half=False):
        if half:
            self.p.image("empty_half.ppm")
        else:
            self.p.image("empty.ppm")

    def createFreeSequence(self, start_time, end_time, sequence):
        width = col_end + 1
        height = int(row_height * (end_time - start_time) / 0.25)

        img = Image.new('RGB', (width, height), "white")
        pixels = img.load()

        for n, t in sequence:
            x_cent = self.getXForNote(n)
            y_cent = int(row_height * (t - start_time) / 0.25)
            for i in xrange(x_cent - 5, x_cent + 5):
                for j in xrange(y_cent - 5, y_cent + 5):
                    pixels[i, j] = (0, 0, 0)

        for j in xrange(height):
            pixels[col_end, j] = (0, 0, 0)

        img.save('line.ppm')

    def createChord(self, notes):
        width = col_end + 1
        height = row_height

        img = Image.new('RGB', (width, height), "white")
        pixels = img.load()

        for n in notes:
            i_cent = self.getXForNote(n)
            for i in xrange(i_cent - 5, i_cent + 5):
                for j in xrange(row_height / 2 - 5, row_height / 2 + 5):
                    pixels[i, j] = (0, 0, 0)

        for j in xrange(height):
            pixels[col_end, j] = (0, 0, 0)

        img.save('line.ppm')

    def createChordHalf(self, notes):
        width = col_end + 1
        height = row_height_half

        img = Image.new('RGB', (width, height), "white")
        pixels = img.load()

        for n in notes:
            i_cent = self.getXForNote(n)
            for i in xrange(i_cent - 5, i_cent + 5):
                for j in xrange(row_height_half / 2 - 5,
                                row_height_half / 2 + 5):
                    pixels[i, j] = (0, 0, 0)

        for j in xrange(height):
            pixels[col_end, j] = (0, 0, 0)

        img.save('line.ppm')

    def resetRest(self):
        img = Image.new('RGB', (col_end + 1, row_height), "white")
        pixels = img.load()

        for j in xrange(row_height):
            pixels[col_end, j] = (0, 0, 0)

        img.save('empty.ppm')

        img = Image.new('RGB', (col_end + 1, row_height_half), "white")
        pixels = img.load()

        for j in xrange(row_height_half):
            pixels[col_end, j] = (0, 0, 0)

        img.save('empty_half.ppm')

    def getXForNote(self, note):
        return col_lead + col_width * note


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
        arduino = serial.Serial("/dev/cu.usbmodem1411", 9600, timeout=1)
    except:
        print("Please check the arduino port")
        return

    pygame.mixer.init(frequency=0, size=8, channels=1)
    pygame.mixer.set_num_channels(15)

    r = None
    quit = False
    recording = False

    while not quit:
        if arduino.in_waiting:
            line = arduino.readline().decode().strip()
            if line == 'QUIT':                     # quit
                quit = True
                if recording:
                    r.endFreeRecording()
                    print('\nrecording end')
                    r.saveToText("out.txt")
                    popen2.popen4("lpr -P Printer_USB_Thermal_Printer " +
                                  "-o raw out.txt")
            elif line == 'RECORD':                   # toggle record
                recording = not recording
                if recording:
                    r = Receipt(239, 23)
                    r.startFreeRecording()
                    print('recording start')
                else:
                    r.endFreeRecording()
                    print('\nrecording end')
                    r.saveToText("out.txt")
                    popen2.popen4("lpr -P Printer_USB_Thermal_Printer " +
                                  "-o raw out.txt")
            elif len(line) > 0:
                onKeyEvent(r, recording, notes[line], notes[line], line)


if __name__ == "__main__":
    main()
