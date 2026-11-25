"""Фабричный метод: общий сценарий использует переопределяемое создание."""

from abc import ABC, abstractmethod
from matrix import Matrix


class MatrixCreator(ABC):
    def prepare(self):
        matrix = self.create_matrix()
        # Общая операция над продуктом не зависит от его источника.
        return matrix, f"{matrix.rows} × {matrix.columns}"

    @abstractmethod
    def create_matrix(self) -> Matrix:
        pass


class TextMatrixCreator(MatrixCreator):
    def __init__(self, text):
        self.text = text

    def create_matrix(self) -> Matrix:
        return Matrix.from_text(self.text)


class FileMatrixCreator(MatrixCreator):
    def __init__(self, path):
        self.path = path

    def create_matrix(self) -> Matrix:
        return Matrix.load(self.path)
