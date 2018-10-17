"""
Extends threading.Thread giving access to a Thread object which will accept
A thread_id, thread name, and a function at the time of instantiation. The
function will be called when the threads start() method is called.
"""

import multiprocessing


class Thread(threading.Thread):
    def __init__(self, thread_id, name, func):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name

        # the function that should be run in the thread.
        self.func = func

    def run(self):
        return self.func()