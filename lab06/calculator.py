from abc import ABC, abstractmethod

from expressions import MatrixValue, MatrixOperation


class MatrixCalculator(ABC):
    @abstractmethod
    def calculate(self, a, b, operation, scalar=None):
        pass


class CalculationService(MatrixCalculator):
    def calculate(self, a, b, operation, scalar=None):
        if operation == "A × число":
            return a.multiply_by_number(scalar)
        if operation == "(A + B) × A":
            total = MatrixOperation(MatrixValue(a), MatrixValue(b), "+")
            expression = MatrixOperation(total, MatrixValue(a), "*")
        else:
            symbols = {"A + B": "+", "A - B": "-", "A × B": "*"}
            if operation not in symbols:
                raise ValueError("Неизвестная операция.")
            expression = MatrixOperation(
                MatrixValue(a), MatrixValue(b), symbols[operation])
        return expression.evaluate()
