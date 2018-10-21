#!venv/bin/python3


class Event(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data


class EventDispatcher(object):
    def __init__(self):
        self.events = {}

    def has_listener(self, event_name, listener):
        if event_name in self.events.keys():
            return listener in self.events[event_name]
        else:
            return False

    def add_listener(self, event_name, listener):
        if not self.has_listener(event_name, listener):
            listeners = self.events.get(event_name, [])
            listeners.append(listener)
            self.events[event_name] = listeners

    def remove_listener(self, event_name, listener):
        if self.has_listener(event_name, listener):
            listeners = self.events[event_name]
            if len(listeners) == 1:
                del self.events[event_name]
            else:
                listeners.remove(listener)
                self.events[event_name] = listeners

    def dispatch_event(self, event):
        if event.name in self.events.keys():
            listeners = self.events[event.name]
            for listener in listeners:
                listener(event)

    def __del__(self):
        self.events = None
