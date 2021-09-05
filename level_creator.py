from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import cv2
import math
import solver

window = Tk()
window.title("Level Creator")

size = 64
width = 5
height = 5


def createLevel(s=size, w=width, h=height):
    global size, width, height, horiz, vert, level, player, cop
    player = (-1, -1)
    cop = (-1, -1)
    size, width, height = s, w, h
    horiz = np.zeros((height + 1, width), dtype=bool)
    horiz[0] = horiz[height] = 1
    vert = np.zeros((height, width + 1), dtype=bool)
    vert[:, 0] = vert[:, width] = 1
    level = (vert, horiz)
    return level


createLevel()


def newLevel():
    split = sizeEntry.get().split('x')
    createLevel(w=int(split[0]), h=int(split[1]))
    redrawImage()


def blankImage():
    # return np.full((size*height+1, size*width+1, 3), 255, dtype=np.uint8)
    return np.fromfunction(
        lambda x, y, z:
        255 - 50 * (x // size % 2 ^ y // size % 2),
        (size * height + 1, size * width + 1, 3), dtype=np.uint8)


def drawWalls(image, s=16, t=4):
    for (y, x), z in np.ndenumerate(horiz):
        if z:
            cv2.line(image, (s * x, s * y), (s * x + s, s * y), color=0, thickness=t)
    for (y, x), z in np.ndenumerate(vert):
        if z:
            cv2.line(image, (s * x, s * y), (s * x, s * y + s), color=0, thickness=t)
    return image


def redrawImage():
    levelImage = blankImage()
    drawWalls(levelImage, size)
    if player != (-1, -1):
        cv2.circle(levelImage, (size * player[0] + size // 2, size * player[1] + size // 2),
                   size * 2 // 5, (0, 255, 0), -1)
    if cop != (-1, -1):
        cv2.circle(levelImage, (size * cop[0] + size // 2, size * cop[1] + size // 2),
                   size * 2 // 5, (0, 0, 255), -1)
    photo = ImageTk.PhotoImage(Image.fromarray(levelImage))
    lbl.configure(image=photo)
    lbl.image = photo


def onClick(event):
    lbl.focus_set()
    x, y = event.x, event.y
    x1, y1 = x / size, y / size
    s = math.floor(x1 + y1)
    d = math.floor(y1 - x1)
    w = (s + d) % 2
    r = (s + d + 1) // 2
    c = (s - d) // 2
    level[w][r, c] ^= True
    redrawImage()


def clamp(x, minimum, maximum):
    return min(max(x, minimum), maximum)


def setPlayer(event):
    global player
    player = clamp(event.x // size, 0, width - 1), clamp(event.y // size, 0, height - 1)
    redrawImage()


def setCop(event):
    global cop
    cop = clamp(event.x // size, 0, width - 1), clamp(event.y // size, 0, height - 1)
    redrawImage()


def solve():
    solver.dim = (width, height)
    solver.horizontal, solver.vertical = horiz, vert
    # solver.player, solver.cop = player, cop
    if player != (-1, -1) and cop != (-1, -1):
        s = solver.solve(player, cop, True)
        solver.visualizeSolutions(s)


def openFile():
    global width, height, horiz, vert, level, player, cop
    chosen = filedialog.askopenfilename(filetypes=(('Text files', '.txt'), ("Prison files", '.prison')))
    if chosen:
        if chosen.endswith('.txt'):
            file = open(chosen)
            w, h = map(int, file.readline().strip().split('x'))
            newHoriz = np.zeros((h + 1, w), dtype=bool)
            newVert = np.zeros((h, w + 1), dtype=bool)
            newLevel = (newVert, newHoriz)
            px, py = map(int, file.readline().strip().split(','))
            cx, cy = map(int, file.readline().strip().split(','))
            nCharacters = (2 * w + 2) * h
            lines = np.array(file.readlines(nCharacters), dtype=f'S{2 * w + 1}')
            lines = lines.view('S1').reshape((h + 1, 2 * w + 1))
            for (y, x), z in np.ndenumerate(lines):
                if z != b' ':
                    which = x % 2
                    r, c = y - 1 + which, x // 2
                    newLevel[which][r, c] = True
            width, height, horiz, vert, level, player, cop = \
                w, h, newHoriz, newVert, newLevel, (px, py), (cx, cy)
            redrawImage()
        else:
            file = open(chosen, mode='rb')
            help(file)
        file.close()
    # print(open(chosen).readlines())
    # print(chosen)
    pass


def saveFile():
    chosen = filedialog.asksaveasfilename(
        filetypes=(('Text files', '.txt'), ("Prison files", '.prison')),
        defaultextension='.txt',
        initialfile='Untitled.txt')
    if chosen:
        if chosen.endswith('.txt'):
            file = open(chosen, mode='w')
            file.write(f"{width}x{height}\n")
            file.write(f"{player[0]},{player[1]}\n")
            file.write(f"{cop[0]},{cop[1]}\n")
            lines = np.full((height + 1, 2 * width + 1), ' ', dtype='S1')
            for (y, x), z in np.ndenumerate(horiz):
                if z:
                    lines[y, 2 * x + 1] = '_'
            for (y, x), z in np.ndenumerate(vert):
                if z:
                    lines[y + 1, 2 * x] = '|'
            file.writelines(b'\n'.join(lines).decode('utf-8'))
        else:
            file = open(chosen, mode='wb')
            file.write(width.to_bytes(1, 'big'))
            file.write(height.to_bytes(1, 'big'))
            area = width * height
            horizNum = sum(x << i for i, x in enumerate(horiz.ravel()))
            vertNum = sum(x << i for i, x in enumerate(vert.ravel()))
            file.write(horizNum.to_bytes(area, 'big'))
            file.write(vertNum.to_bytes(area, 'big'))
            help(file)
        file.close()


def flipud():
    global vert, horiz, level, player, cop
    vert = np.flipud(vert)
    horiz = np.flipud(horiz)
    level = (vert, horiz)
    if player != (-1, -1):
        player = player[0], height - player[1] - 1
    if cop != (-1, -1):
        cop = cop[0], height - cop[1] - 1
    redrawImage()


def fliplr():
    global vert, horiz, level, player, cop
    vert = np.fliplr(vert)
    horiz = np.fliplr(horiz)
    level = (vert, horiz)
    if player != (-1, -1):
        player = width - player[0] - 1, player[1]
    if cop != (-1, -1):
        cop = width - cop[0] - 1, cop[1]
    redrawImage()


if __name__ == '__main__':
    lbl = Label(window)
    redrawImage()
    lbl.grid(row=0, column=0, rowspan=7, columnspan=7)
    lbl.bind('<Button-1>', onClick)
    lbl.bind('<Button-2>', setPlayer)
    lbl.bind('<Button-3>', setCop)
    lbl.bind('p', setPlayer)
    lbl.bind('c', setCop)
    # lbl.bind('<B1-Motion>', onClick)
    # window.pack()
    # lbl.pack()
    # window.geometry("320x320")
    sizeEntry = Entry(window, width=5)
    sizeEntry.insert(0, '5x5')
    sizeEntry.grid(row=7, column=0, sticky=E)
    newBtn = Button(window, text='Create New Level', command=newLevel)
    newBtn.grid(row=7, column=1, sticky=W)
    solveBtn = Button(window, text='Solve!', command=solve)
    solveBtn.grid(row=7, column=2)
    saveBtn = Button(window, text='Save', command=saveFile)
    saveBtn.grid(row=7, column=3)
    openBtn = Button(window, text='Open', command=openFile)
    openBtn.grid(row=7, column=4)
    fliplrBtn = Button(window, text='Flip ⬌', command=fliplr)
    fliplrBtn.grid(row=7, column=5)
    flipudBtn = Button(window, text='Flip ⬍', command=flipud)
    flipudBtn.grid(row=7, column=6)
    # window.tk_focusFollowsMouse()
    window.resizable(0, 0)
    window.mainloop()
