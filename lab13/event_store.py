import json
import os
from pathlib import Path


class EventStore:
    def __init__(self, path):
        self.path = Path(path)

    def read_all(self):
        if not self.path.exists():
            return []
        events = []
        for number, line in enumerate(
                self.path.read_text(encoding="utf-8").splitlines(), 1):
            try:
                event = json.loads(line)
                if not isinstance(event, dict) or event.get("sequence") != number:
                    raise ValueError("Нарушен порядок событий.")
                events.append(event)
            except (ValueError, TypeError) as error:
                raise ValueError(f"Ошибка журнала в строке {number}: {error}") from error
        return events

    def append(self, kind, payload):
        events = self.read_all()
        event = {"sequence": len(events) + 1, "kind": kind,
                 "payload": payload}
        text = json.dumps(event, ensure_ascii=False, allow_nan=False)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(text + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        return event
