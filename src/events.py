"""A module for event handling

Objects register themselves to arbitrary string event names, which they pass callback functions to.
"""
from collections import defaultdict

__event_listeners = defaultdict(list)

def listen_to_event(eventname, callback):
    """Register an object to listen to an event

    eventname: A string identifying the event to listen for
    callback: A function to be called on listening_object when the event fires
    """
    __event_listeners[eventname].append(callback)

def trigger_event(eventname, *args, **kwargs):
    """Call all the registered callbacks that are listening to eventname"""
    for callback in __event_listeners[eventname]:
        callback(*args, **kwargs)
