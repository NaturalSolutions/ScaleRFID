#!venv/bin/python3

from datetime import datetime


class KillSwitch:
    _STATES = [False, 'PENDING1', 'PENDING2', 'ACTIVATED']

    def __init__(self, key_code=30, threshold=.500):
        self.state = self._STATES[0]
        self.key_code = key_code
        self.threshold = threshold
        self._last = datetime.now().timestamp()
        self._delta = 0

    @property
    def activated(self):
        return self._STATES.index(self.state) == len(self._STATES) - 1

    @property
    def pending(self):
        # return self.state.startswith('PENDING')
        return 0 < self._STATES.index(self.state) < len(self._STATES) - 1

    def increment(self):
        self.state = self._STATES[self._STATES.index(self.state) + 1]

    def register(self, ts):
        self._delta = ts - self._last
        if (self._delta < self.threshold):
            self.increment()
        else:
            self.state = self._STATES[0]
        self._last = ts
