from collections import OrderedDict

from calculator import MatrixCalculator, CalculationService


class CachedCalculator(MatrixCalculator):
    def __init__(self, calculator=None, capacity=20):
        if capacity < 1:
            raise ValueError("Размер кэша должен быть положительным.")
        self.calculator = (calculator if calculator is not None
                           else CalculationService())
        self.capacity = capacity
        self.cache = OrderedDict()
        self.last_hit = False

    def calculate(self, a, b, operation, scalar=None):
        self.last_hit = False
        left = tuple(tuple(row) for row in a.data)
        if operation == "A × число":
            right = None
        else:
            right = tuple(tuple(row) for row in b.data)
            scalar = None
        key = (left, right, operation, scalar)
        if key in self.cache:
            self.last_hit = True
            self.cache.move_to_end(key)
            return self.cache[key].clone()
        result = self.calculator.calculate(a, b, operation, scalar)
        self.cache[key] = result.clone()
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
        return result

    def clear(self):
        self.cache.clear()
        self.last_hit = False
