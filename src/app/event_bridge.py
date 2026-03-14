from collections import defaultdict


class EventBridge:

    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, event_name, callback):
        self._subscribers[event_name].append(callback)

    def emit(self, event_name, *args, **kwargs):
        for callback in self._subscribers[event_name]:
            callback(*args, **kwargs)


event_bridge = EventBridge()
