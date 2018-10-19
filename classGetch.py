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
        # old_settings = termios.tcgetattr(sys.stdin)
        # new_settings = termios.tcgetattr(sys.stdin)
        # # lflags
        # new_settings[3] = new_settings[3] & ~(termios.ECHO | termios.ICANON)
        # new_settings[6][termios.VMIN] = 0   # cc
        # new_settings[6][termios.VTIME] = 0  # cc
        # termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new_settings)
        # ch = os.read(sys.stdin.fileno(), 1)
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
