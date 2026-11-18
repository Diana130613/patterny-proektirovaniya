from dataclasses import dataclass, field
from matrix import Matrix


@dataclass
class CalculationRequest:
    a_text: str
    b_text: str
    operation: str
    scalar_text: str = ""
    a: object = None
    b: object = None
    scalar: object = None
    checks: list = field(default_factory=list)


class Handler:
    def __init__(self):
        self.next = None

    def set_next(self, handler):
        self.next = handler
        return handler

    def handle(self, request):
        self.check(request)
        request.checks.append(type(self).__name__)
        if self.next is not None:
            return self.next.handle(request)
        return request


    def check(self, request):
        raise NotImplementedError


class OperationHandler(Handler):
    def check(self, request):
        if request.operation not in (
                "A + B", "A - B", "A × B", "A × число", "(A + B) × A"):
            raise ValueError("Неизвестная операция.")


class MatrixInputHandler(Handler):
    def check(self, request):
        request.a = Matrix.from_text(request.a_text)
        if request.operation != "A × число":
            request.b = Matrix.from_text(request.b_text)


class ScalarHandler(Handler):
    def check(self, request):
        if request.operation == "A × число":
            request.scalar = Matrix.number(request.scalar_text)


class DimensionsHandler(Handler):
    def check(self, request):
        a, b, operation = request.a, request.b, request.operation
        if operation in ("A + B", "A - B", "(A + B) × A"):
            a.check_same_size(b)
        if operation in ("A × B", "(A + B) × A"):
            right = a if operation == "(A + B) × A" else b
            if a.columns != right.rows:
                raise ValueError("Число столбцов A должно равняться числу строк B.")


def validation_chain():
    first = OperationHandler()
    first.set_next(MatrixInputHandler()).set_next(ScalarHandler()).set_next(
        DimensionsHandler())
    return first
