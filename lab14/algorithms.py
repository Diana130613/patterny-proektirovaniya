from abc import ABC, abstractmethod
from matrix import Matrix
from calculator import CalculationService


class MultiplicationStrategy(ABC):
    @abstractmethod
    def multiply(self, a, b):
        pass


class StandardMultiplication(MultiplicationStrategy):
    def multiply(self, a, b):
        return a.multiply(b)


class TransposedMultiplication(MultiplicationStrategy):
    def multiply(self, a, b):
        if a.columns != b.rows:
            raise ValueError("Несовместимые размеры матриц.")
        columns = list(zip(*b.data))
        return Matrix([[sum(x * y for x, y in zip(row, column))
                        for column in columns] for row in a.data])


class OperationTemplate(ABC):
    def execute(self, a, b):
        self.validate(a, b)
        result = self.compute(a, b)
        self.validate_result(result)
        return result

    @abstractmethod
    def validate(self, a, b):
        pass

    @abstractmethod
    def compute(self, a, b):
        pass

    def validate_result(self, result):
        if not isinstance(result, Matrix):
            raise ValueError("Операция должна вернуть матрицу.")


class AddOperation(OperationTemplate):
    def validate(self, a, b):
        a.check_same_size(b)

    def compute(self, a, b):
        return a.add(b)


class MultiplyOperation(OperationTemplate):
    def __init__(self, strategy):
        self.strategy = strategy

    def validate(self, a, b):
        if a.columns != b.rows:
            raise ValueError("Несовместимые размеры матриц.")

    def compute(self, a, b):
        return self.strategy.multiply(a, b)


class StrategyCalculator(CalculationService):
    def __init__(self, strategy=None):
        self.strategy = strategy if strategy is not None else StandardMultiplication()

    def calculate(self, a, b, operation, scalar=None):
        if operation == "A + B":
            return AddOperation().execute(a, b)
        if operation == "A × B":
            return MultiplyOperation(self.strategy).execute(a, b)
        if operation == "(A + B) × A":
            total = AddOperation().execute(a, b)
            return MultiplyOperation(self.strategy).execute(total, a)
        return super().calculate(a, b, operation, scalar)
