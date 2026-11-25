from dataclasses import dataclass
from matrix import Matrix


@dataclass(frozen=True)
class SessionSnapshot:
    a_text: str
    b_text: str
    operation: str
    scalar_text: str
    result: object


class CalculatorSession:
    def __init__(self):
        self.a_text = "1 2\n3 4"
        self.b_text = "5 6\n7 8"
        self.operation = "A + B"
        self.scalar_text = "2"
        self.result = None

    def save(self):
        data = (None if self.result is None else
                tuple(tuple(row) for row in self.result.data))
        return SessionSnapshot(self.a_text, self.b_text,
                               self.operation, self.scalar_text, data)

    def restore(self, snapshot):
        self.a_text, self.b_text = snapshot.a_text, snapshot.b_text
        self.operation, self.scalar_text = snapshot.operation, snapshot.scalar_text
        self.result = None if snapshot.result is None else Matrix(snapshot.result)


class SnapshotHistory:
    def __init__(self, session):
        self.session = session
        self.snapshot = None

    def save(self):
        self.snapshot = self.session.save()

    def restore(self):
        if self.snapshot is None:
            raise ValueError("Сначала сохраните сеанс.")
        self.session.restore(self.snapshot)
