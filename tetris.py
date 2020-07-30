from enum import IntEnum
from random import randrange


class Grid:
    """ stuff not falling """
    def __init__(self, w=10, h=20):
        self.rows = [[0 for _ in range(w)] for _ in range(h)]
        self.w = w
        self.h = h

    def get(self, x: int, y: int):
        return self.rows[y][x]

    def set(self, x: int, y: int, value: int):
        self.rows[y][x] = value

    def get_full_rows(self):
        full_rows = []
        for i, row in enumerate(self.rows):
            if 0 not in row:
                full_rows.append(i)
        return full_rows

    def disappear_rows(self, full_rows: list):
        """ pre: full_rows is sorted """
        row = self.h - 1
        count_dis_below = 0  # how many disappearing rows below row
        full_rows_i = len(full_rows) - 1
        while row >= 0:
            if full_rows_i >= 0 and full_rows[full_rows_i] > row:
                count_dis_below += 1
                full_rows_i -= 1
            # move this row down in the amount of count_dis_below
            self.rows[row + count_dis_below] = self.rows[row]
            row -= 1
        # add blank rows at the top
        while row < len(full_rows) - 1:
            row += 1
            self.rows[row] = [0 for _ in range(self.w)]

    def __repr__(self):
        to_return = ""
        for row in self.rows:
            to_return += "[ "
            for col in row:
                if col == 0:
                    to_return += " "
                else:
                    to_return += str(col)
                to_return += " "
            to_return += "]\n"
        return to_return


class Faller:
    class Shape(IntEnum):
        T = 0
        L = 1
        J = 2
        I = 3
        S = 4
        Z = 5
        O = 6
        COUNT = 7  # also the null placeholder

    BLOCKS = {
        Shape.T: (
            ((0, 0), (1, 0), (2, 0), (1, 1)),
            ((0, 0), (0, 1), (1, 1), (0, 2)),
            ((1, 0), (0, 1), (1, 1), (2, 1)),
            ((1, 0), (0, 1), (1, 1), (1, 2))
        ),
        Shape.L: (
            ((0, 0), (1, 0), (2, 0), (0, 1)),
            ((0, 0), (0, 1), (0, 2), (1, 2)),
            ((2, 0), (0, 1), (1, 1), (2, 1)),
            ((0, 0), (1, 0), (1, 1), (1, 2))
        ),
        Shape.J: (
            ((0, 0), (1, 0), (2, 0), (2, 1)),
            ((0, 0), (0, 1), (0, 2), (1, 0)),
            ((0, 0), (0, 1), (1, 1), (2, 1)),
            ((0, 2), (1, 0), (1, 1), (1, 2))
        ),
        Shape.I: (
            ((-1, 0), (0, 0), (1, 0), (2, 0)),
            ((0, -1), (0, 0), (0, 1), (0, 2))
        ),
        Shape.S: (
            ((1, 0), (2, 0), (0, 1), (1, 1)),
            ((0, 0), (0, 1), (1, 1), (1, 2))
        ),
        Shape.Z: (
            ((0, 0), (1, 0), (1, 1), (2, 1)),
            ((1, 0), (0, 1), (1, 1), (0, 2))
        ),
        Shape.O: (
            ((0, 0), (1, 0), (0, 1), (1, 1)),
        )
    }

    def __init__(self, shape: "Faller.Shape", x: int):
        self.shape = shape
        self.rotation = 0  # 90 deg anticlockwise, 0 and 2 are shorter
        self.x = x
        self.y = 0

    def get_blocks(self, d_clockwise=0):
        """ d_clockwise is the change in rotation """
        fbs = Faller.BLOCKS[self.shape]
        rotation = (self.rotation - d_clockwise) % 4
        return fbs[rotation % len(fbs)]

    def can_fall(self, grid: Grid):
        for block in self.get_blocks():
            y_to_check = self.y + block[1] + 1
            if y_to_check >= grid.h:
                return False
            if grid.get(self.x + block[0], y_to_check):
                return False
        return True

    def stop(self, grid: Grid):
        for block in self.get_blocks():
            grid.set(self.x + block[0], self.y + block[1], self.shape + 1)

    def move_x(self, grid: Grid, dx: int):
        if self.shape == Faller.Shape.COUNT:
            return False
        can_move = True
        for block in self.get_blocks():
            x_to_check = self.x + block[0] + dx
            if x_to_check < 0 or x_to_check >= grid.w:
                can_move = False
                break
            if grid.get(x_to_check, self.y + block[1]):
                can_move = False
        if can_move:
            self.x += dx
        return can_move

    def rotate(self, grid: Grid, d_clockwise: int):
        if self.shape == Faller.Shape.COUNT:
            return False
        can_rotate = True
        for block in self.get_blocks(d_clockwise):
            x_to_check = self.x + block[0]
            y_to_check = self.y + block[1]
            if x_to_check < 0 or x_to_check >= grid.w or\
                    y_to_check < 0 or y_to_check >= grid.h:
                can_rotate = False
                break
            if grid.get(x_to_check, y_to_check):
                can_rotate = False
        if can_rotate:
            self.rotation = (self.rotation - d_clockwise) % 4
        return can_rotate


class Tetris:
    """ the game without any timing """
    def __init__(self):
        self.grid = Grid()
        self.faller = Faller(Faller.Shape.COUNT, self.grid.w // 2 - 1)
        self.next_shape = Faller.Shape(randrange(Faller.Shape.COUNT))
        self.lose = False
        self.full_rows = []

    def fall(self) -> bool:
        """ returns whether new piece enters the field """
        if self.faller.shape == Faller.Shape.COUNT:  # if shape is null
            self.grid.disappear_rows(self.full_rows)
            self.faller.shape = self.next_shape
            self.next_shape = Faller.Shape(randrange(Faller.Shape.COUNT))
            self.faller.rotation = 0
            self.faller.x = self.grid.w // 2 - 1
            self.faller.y = -1
            self.lose = not self.faller.can_fall(self.grid)
            self.faller.y = 0
            if self.lose:
                self.faller.stop(self.grid)
            return True
        else:  # shape is not null
            if self.faller.can_fall(self.grid):
                self.faller.y += 1
            else:
                self.faller.stop(self.grid)
                self.full_rows = self.grid.get_full_rows()
                self.faller.shape = Faller.Shape.COUNT  # null
            return False

    def move(self, dx: int):
        return self.faller.move_x(self.grid, dx)

    def rotate(self, d_clockwise: int):
        return self.faller.rotate(self.grid, d_clockwise)


def test_disappear_rows():
    t = Tetris()
    t.next_shape = Faller.Shape.I
    t.fall()
    t.move(-3)
    print(t.grid)
    for _ in range(20):
        t.fall()
    print(t.grid)
    t.next_shape = Faller.Shape.I
    t.fall()
    t.move(1)
    for _ in range(20):
        t.fall()
    print(t.grid)
    t.next_shape = Faller.Shape.O
    t.fall()
    t.move(4)
    for _ in range(19):
        t.fall()
    print(t.grid)
    t.fall()
    print(t.grid)


def fall_test():
    t = Tetris()
    while not t.lose:
        t.fall()
    print(t.grid)


if __name__ == "__main__":
    fall_test()
    test_disappear_rows()
