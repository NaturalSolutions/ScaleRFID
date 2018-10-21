#!venv/bin/python3

# import os
import tty
import sys
import termios


class _Getch:
    """Gets a single character from standard input.
    Does not echo to the screen."""

    def __init__(self):
        self.impl = _GetchUnix()

    def __call__(self):
        return self.impl()


class _GetchUnix:
    def __call__(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)[0]
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


if __name__ == '__main__':
    # readchar = _GetchUnix()
    #
    # c1 = 0
    # while c1 != chr(27):  # ESC
    #     c1 = readchar()
    #     print(len(c1))
    #     print(ord(c1))
    #     # if ord(c1) != 0x1b:
    #     print(c1)
    #     if c1 == 'd':
    #         break
    #     print(r"You pressed {}".format(c1))
    #     # c2 = readchar()
    #     # if ord(c2) != 0x5b:
    #     #     print("You pressed", c1 + c2)
    #     # c3 = readchar()
    #     # if ord(c3) != 0x33:
    #     #     print("You pressed", c1 + c2 + c3)
    #     # c4 = readchar()
    #     # print("You pressed", c1 + c2 + c3 + c4)
