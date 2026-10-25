import csv
from abc import ABC, abstractmethod
from pathlib import Path

from matrix import Matrix


class MatrixReader(ABC):
    @abstractmethod
    def read(self, path) -> Matrix:
        pass


class TextMatrixReader(MatrixReader):
    def read(self, path) -> Matrix:
        return Matrix.load(path)


class CsvTableReader:
    def load_rows(self, path):
        with Path(path).open(encoding="utf-8-sig", newline="") as file:
            rows = list(csv.reader(file, delimiter=";"))
        return [row for row in rows if any(cell.strip() for cell in row)]


class CsvMatrixAdapter(MatrixReader):
    def __init__(self, reader):
        self.reader = reader

    def read(self, path) -> Matrix:
        rows = self.reader.load_rows(path)
        data = [[Matrix.number(cell) for cell in row] for row in rows]
        return Matrix(data)
