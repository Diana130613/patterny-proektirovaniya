from validation import CalculationRequest, validation_chain
from matrix import Matrix
from creators import TextMatrixCreator
from adapters import TextMatrixReader, CsvTableReader, CsvMatrixAdapter
from calculator import CalculationService


class CalculatorFacade:
    def __init__(self, calculator=None):
        self.calculator = (calculator if calculator is not None
                           else CalculationService())

    def calculate(self, a_text, b_text, operation, scalar_text=""):
        request = CalculationRequest(a_text, b_text, operation, scalar_text)
        self.last_request = request
        validation_chain().handle(request)
        return self.calculator.calculate(
            request.a, request.b, request.operation, request.scalar)

    def load(self, path):
        if str(path).lower().endswith(".csv"):
            reader = CsvMatrixAdapter(CsvTableReader())
        else:
            reader = TextMatrixReader()
        return reader.read(path)

    def save(self, matrix, path):
        matrix.save(path)
