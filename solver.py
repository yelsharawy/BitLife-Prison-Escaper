import cv2
import numpy as np


def drawWalls(image, s=16, t=1):
    for (y, x), z in np.ndenumerate(horizontal):
        if z:
            image = cv2.line(image, (s * x, s * y), (s * x + s, s * y), color=0, thickness=t)
    for (y, x), z in np.ndenumerate(vertical):
        if z:
            image = cv2.line(image, (s * x, s * y), (s * x, s * y + s), color=0, thickness=t)
    return image


def wallLeft(pos):
    return vertical.T[pos]


def wallTop(pos):
    return horizontal.T[pos]


def wallRight(pos):
    return vertical.T[pos[0] + 1, pos[1]]


def wallBottom(pos):
    return horizontal.T[pos[0], pos[1] + 1]


def moveCop(player, cop):
    if cop[0] < player[0] and not wallRight(cop):
        return cop[0] + 1, cop[1]
    if cop[0] > player[0] and not wallLeft(cop):
        return cop[0] - 1, cop[1]
    if cop[1] < player[1] and not wallBottom(cop):
        return cop[0], cop[1] + 1
    if cop[1] > player[1] and not wallTop(cop):
        return cop[0], cop[1] - 1
    return cop


class State():

    def __init__(self, player, cop, prev=None):
        self.player = player
        self.cop = cop
        self.tpl = (player, cop)
        self.prev = prev or []

    def nextStates(self):
        player, cop = self.tpl
        output = set()
        nextChain = self.prev + [self.tpl]

        def addMove(newPlayer):
            output.add(State(newPlayer, moveCop(newPlayer, moveCop(newPlayer, cop)), nextChain))

        if not wallLeft(player):
            addMove((player[0] - 1, player[1]))
        if not wallRight(player):
            addMove((player[0] + 1, player[1]))
        if not wallTop(player):
            addMove((player[0], player[1] - 1))
        if not wallBottom(player):
            addMove((player[0], player[1] + 1))
        return output

    def __hash__(self):
        return hash(self.tpl)

    def __eq__(self, other):
        return self.tpl == other.tpl

    def __str__(self):
        return f"{str(self.tpl)}, {len(self.prev)} moves"


def inMap(pos):
    return 0 <= pos[0] < dim[0] and 0 <= pos[1] < dim[1]


def getWallImage(squareSize, thickness):
    # np.ones((squareSize*dim[1]+(thickness+1)//2, squareSize*dim[0]+(thickness+1)//2, 3))
    image = \
        np.fromfunction(
            lambda x, y, z:
            1 - 0.2 * (x // squareSize % 2 ^ y // squareSize % 2),
            (squareSize * dim[1] + 1, squareSize * dim[0] + 1, 3), dtype=np.uint8)
    image = drawWalls(image, squareSize, thickness)
    return image


def solve(player, cop, getAll=False):
    doneStates = set()
    solutions = []
    states = {State(player, cop)}
    i = 0
    while getAll or len(solutions) == 0 and len(states) > 0:
        nextMoves = tuple(x.nextStates()
                          for x in states
                          if x.player != x.cop)
        if len(nextMoves) == 0:
            break
        states, doneStates = set.union(*nextMoves), \
                             doneStates | states
        solutions.extend(x for x in states if not inMap(x.player))
        states.difference_update(solutions, doneStates)
    return solutions


def visualizeSolutions(solutions, cColor=(1, 0, 0), pColor=(0, 1, 0), squareSize=32, wallThickness=2):
    for a in solutions:
        name = str(a)
        for state in a.prev:
            pPos = state[0]
            cPos = state[1]
            special = getWallImage(squareSize, wallThickness)
            cv2.circle(special, (squareSize * pPos[0] + squareSize // 2, squareSize * pPos[1] + squareSize // 2),
                       squareSize * 2 // 5, pColor, -1)
            cv2.circle(special, (squareSize * cPos[0] + squareSize // 2, squareSize * cPos[1] + squareSize // 2),
                       squareSize * 2 // 5, cColor, -1)
            cv2.imshow(name, special)
            k = cv2.waitKey(1500)
            del special
            if k == 27:
                break
        cv2.destroyAllWindows()


if __name__ == '__main__':
    dim = (6, 6)

    horizontal = np.array(dtype=bool, object=
    [[1, 1, 1, 1, 1, 1],
     [1, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, 0, 1, 0, 0, 0],
     [1, 1, 1, 1, 1, 1]])
    vertical = np.array(dtype=bool, object=
    [[1, 0, 1, 1, 0, 0, 1],
     [1, 1, 0, 0, 0, 0, 1],
     [1, 0, 0, 1, 1, 1, 1],
     [1, 0, 0, 0, 0, 1, 1],
     [1, 0, 0, 1, 0, 0, 1],
     [1, 0, 0, 0, 1, 0, 0]])
    s = solve((2, 3), (5, 3), True)
    visualizeSolutions(s)
