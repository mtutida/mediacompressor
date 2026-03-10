class InteractionEventBridge:
    """Global event bridge between Scheduler, InteractionModel and UI"""

    def __init__(self):
        self._listeners = []

    def subscribe(self, callback):
        if callback not in self._listeners:
            self._listeners.append(callback)

    def unsubscribe(self, callback):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def emit(self, event_type, payload):
        for cb in list(self._listeners):
            try:
                cb(event_type, payload)
            except Exception:
                pass


# global singleton bridge
event_bridge = InteractionEventBridge()
