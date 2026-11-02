from matrix import Matrix
from creators import TextMatrixCreator
from adapters import TextMatrixReader, CsvTableReader, CsvMatrixAdapter
from calculator import CalculationService


class CalculatorFacade:
    def __init__(self, calculator=None):
        self.calculator = (calculator if calculator is not None
                           else CalculationService())

    def calculate(self, a_text, b_text, operation, scalar_text=""):
        a, _ = TextMatrixCreator(a_text).prepare()
        b = None
        scalar = None
        if operation == "A × число":
            scalar = Matrix.number(scalar_text)
        else:
            b, _ = TextMatrixCreator(b_text).prepare()
        return self.calculator.calculate(a, b, operation, scalar)

    def load(self, path):
        if str(path).lower().endswith(".csv"):
            reader = CsvMatrixAdapter(CsvTableReader())
        else:
            reader = TextMatrixReader()
        return reader.read(path)

    def save(self, matrix, path):
        matrix.save(path)
