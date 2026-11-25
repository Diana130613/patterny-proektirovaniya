from abc import ABC, abstractmethod


class MatrixExpression(ABC):
    @abstractmethod
    def evaluate(self):
        pass


class MatrixValue(MatrixExpression):
    def __init__(self, matrix):
        self.matrix = matrix

    def evaluate(self):
        return self.matrix


class MatrixOperation(MatrixExpression):
    def __init__(self, left, right, operation):
        if operation not in ("+", "-", "*"):
            raise ValueError("Неизвестная операция.")
        self.left = left
        self.right = right
        self.operation = operation

    def evaluate(self):
        left = self.left.evaluate()
        right = self.right.evaluate()
        if self.operation == "+":
            return left.add(right)
        if self.operation == "-":
            return left.subtract(right)
        return left.multiply(right)
