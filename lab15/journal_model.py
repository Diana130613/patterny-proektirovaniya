from copy import deepcopy
from pathlib import Path
from model import CalculatorModel
from event_store import EventStore
from projection import CalculatorProjection


class EventHistory:
    def __init__(self, model):
        self.model = model

    def undo(self):
        if not self.model.projection.previous_results:
            return False
        self.model.record("undone", {})
        return True


class EventCalculatorModel(CalculatorModel):
    def __init__(self, path=None):
        super().__init__()
        self.events = EventStore(path if path is not None else
                                 Path(__file__).with_name("events.jsonl"))
        self.projection = CalculatorProjection()
        self.history = EventHistory(self)
        self.replay()

    def sync_result(self):
        self.store.set_result(self.projection.result)
        result = self.store.result
        self.context.result = None if result is None else result.clone()

    def replay(self):
        projection = CalculatorProjection()
        for event in self.events.read_all():
            projection.apply(event)
        self.projection = projection
        self.sync_result()
        return projection.request

    def record(self, kind, payload):
        candidate = deepcopy(self.projection)
        candidate.apply({"kind": kind, "payload": payload})
        self.events.append(kind, payload)
        self.projection = candidate
        self.sync_result()

    def commit_result(self, request, result):
        self.record("calculated", {
            "request": list(request), "result": result.data})
        return self.store.result

    def calculate(self, request):
        def action():
            result = self.facade.calculate(*request)
            return self.commit_result(request, result)
        return self.context.calculate(action)

    def restore_session(self):
        snapshot = self.snapshots.snapshot
        if snapshot is None:
            raise ValueError("Сначала сохраните сеанс.")
        request = (snapshot.a_text, snapshot.b_text,
                   snapshot.operation, snapshot.scalar_text)
        self.record("session_restored", {
            "request": list(request), "result": snapshot.result})
        return request
