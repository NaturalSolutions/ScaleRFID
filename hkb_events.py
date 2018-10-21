#!venv/bin/python3

from event_dispatcher import Event, EventDispatcher


dispatcher = EventDispatcher()


def dispatch(event):
    _type = list(event.keys())[0]
    interfaced = Event(_type, event[_type])
    dispatcher.dispatch_event(interfaced)


def inputEvent(func):
    # if len(func.__qualname__.split('.')) > 1:
    #         def calling(self, *args, **kwargs):
    dispatcher.add_listener('inputEvent', func)
    return
