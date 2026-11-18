from abc import ABC, abstractmethod


class MatrixFormatter(ABC):
    @abstractmethod
    def format(self, matrix):
        pass


class PlainFormatter(MatrixFormatter):
    def __init__(self, decimal_places):
        self.decimal_places = decimal_places

    def format(self, matrix):
        return matrix.to_text(self.decimal_places)


class FormatterDecorator(MatrixFormatter):
    def __init__(self, formatter):
        self.formatter = formatter

    def format(self, matrix):
        return self.formatter.format(matrix)


class RowNumbersFormatter(FormatterDecorator):
    def format(self, matrix):
        text = self.formatter.format(matrix)
        return "\n".join(f"{i}: {line}"
                         for i, line in enumerate(text.splitlines(), 1))


class SizeFormatter(FormatterDecorator):
    def format(self, matrix):
        text = self.formatter.format(matrix)
        return f"Размер: {matrix.rows} × {matrix.columns}\n{text}"
