"""Матрица, четыре операции и чтение/запись текстовых файлов."""

import math
from pathlib import Path


class Matrix:
    def __init__(self, data):
        if not data or not data[0]:
            raise ValueError("Матрица не должна быть пустой.")
        self.rows = len(data)
        self.columns = len(data[0])
        if self.rows > 100 or self.columns > 100:
            raise ValueError("Максимальный размер матрицы — 100 × 100.")
        if any(len(row) != self.columns for row in data):
            raise ValueError("Во всех строках должно быть одинаковое число элементов.")
        self.data = [[float(value) for value in row] for row in data]
        if any(not math.isfinite(value) for row in self.data for value in row):
            raise ValueError("Допустимы только конечные числа.")

    @staticmethod
    def number(text):
        try:
            value = float(text.strip().replace(",", "."))
        except ValueError:
            raise ValueError(f"Неверное число: {text}") from None
        if not math.isfinite(value):
            raise ValueError("Допустимы только конечные числа.")
        return value

    @classmethod
    def from_text(cls, text):
        lines = [line for line in text.splitlines() if line.strip()]
        data = [[cls.number(value) for value in line.split()] for line in lines]
        return cls(data)

    def to_text(self, decimal_places=None):
        def format_number(value):
            if decimal_places is None:
                return repr(value)  # Полная точность для файлов и исходных данных.
            text = f"{value:.{decimal_places}f}"
            if decimal_places:
                text = text.rstrip("0").rstrip(".")
            return "0" if text == "-0" else text
        return "\n".join(" ".join(format_number(value) for value in row)
                         for row in self.data)

    def add(self, other):
        self.check_same_size(other)
        return Matrix([[self.data[i][j] + other.data[i][j]
                        for j in range(self.columns)] for i in range(self.rows)])

    def subtract(self, other):
        self.check_same_size(other)
        return Matrix([[self.data[i][j] - other.data[i][j]
                        for j in range(self.columns)] for i in range(self.rows)])

    def check_same_size(self, other):
        if self.rows != other.rows or self.columns != other.columns:
            raise ValueError("Для сложения и вычитания размеры матриц должны совпадать.")

    def multiply_by_number(self, number):
        return Matrix([[value * number for value in row] for row in self.data])

    def multiply(self, other):
        if self.columns != other.rows:
            raise ValueError("Число столбцов A должно равняться числу строк B.")
        # Элемент результата: сумма произведений строки A на столбец B.
        return Matrix([[sum(self.data[i][k] * other.data[k][j]
                            for k in range(self.columns))
                        for j in range(other.columns)] for i in range(self.rows)])

    @classmethod
    def load(cls, path):
        # utf-8-sig позволяет читать UTF-8 как с BOM, так и без него.
        tokens = Path(path).read_text(encoding="utf-8-sig").split()
        try:
            rows, columns = int(tokens[0]), int(tokens[1])
        except (ValueError, IndexError):
            raise ValueError("В начале файла нужны два целых числа: строки и столбцы.") from None
        if not 1 <= rows <= 100 or not 1 <= columns <= 100:
            raise ValueError("Размер матрицы должен быть от 1 до 100.")
        if len(tokens) != 2 + rows * columns:
            raise ValueError("Количество чисел не соответствует размерам матрицы.")
        data = [[cls.number(tokens[2 + i * columns + j]) for j in range(columns)]
                for i in range(rows)]
        return cls(data)

    def save(self, path):
        text = f"{self.rows} {self.columns}\n{self.to_text()}\n"
        Path(path).write_text(text, encoding="utf-8")
