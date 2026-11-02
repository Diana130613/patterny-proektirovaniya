import tempfile
import unittest
from pathlib import Path

from matrix import Matrix
from expressions import MatrixExpression, MatrixValue, MatrixOperation
from formatters import (MatrixFormatter, PlainFormatter, FormatterDecorator,
                        RowNumbersFormatter, SizeFormatter)


class CompositeTests(unittest.TestCase):
    def setUp(self):
        self.a = MatrixValue(Matrix([[1, 2], [3, 4]]))
        self.b = MatrixValue(Matrix([[5, 6], [7, 8]]))

    def test_leaf(self):
        self.assertEqual(self.a.evaluate().data, [[1, 2], [3, 4]])

    def test_basic_operations(self):
        for symbol, expected in (("+", [[6, 8], [10, 12]]),
                                 ("-", [[-4, -4], [-4, -4]]),
                                 ("*", [[19, 22], [43, 50]])):
            with self.subTest(operation=symbol):
                self.assertEqual(MatrixOperation(self.a, self.b, symbol)
                                 .evaluate().data, expected)

    def test_nested_expression(self):
        total = MatrixOperation(self.a, self.b, "+")
        expression = MatrixOperation(total, self.a, "*")
        self.assertEqual(expression.evaluate().data, [[30, 44], [46, 68]])
        self.assertEqual(self.a.evaluate().data, [[1, 2], [3, 4]])

    def test_two_nested_branches(self):
        left = MatrixOperation(self.a, self.b, "+")
        right = MatrixOperation(self.b, self.a, "-")
        result = MatrixOperation(left, right, "*").evaluate()
        self.assertEqual(result.data, [[56, 56], [88, 88]])

    def test_bad_dimensions(self):
        short = MatrixValue(Matrix([[1, 2, 3]]))
        expression = MatrixOperation(MatrixOperation(self.a, short, "+"), self.b, "*")
        with self.assertRaises(ValueError):
            expression.evaluate()

    def test_abstract_component_and_unknown_operation(self):
        with self.assertRaises(TypeError):
            MatrixExpression()
        with self.assertRaises(ValueError):
            MatrixOperation(self.a, self.b, "/")


class DecoratorTests(unittest.TestCase):
    def setUp(self):
        self.matrix = Matrix([[30, 44], [46, 68]])

    def test_plain_and_forwarding(self):
        plain = PlainFormatter(3)
        self.assertEqual(plain.format(self.matrix), "30 44\n46 68")
        self.assertEqual(FormatterDecorator(plain).format(self.matrix),
                         plain.format(self.matrix))

    def test_single_decorators(self):
        plain = PlainFormatter(3)
        self.assertEqual(RowNumbersFormatter(plain).format(self.matrix),
                         "1: 30 44\n2: 46 68")
        self.assertEqual(SizeFormatter(plain).format(self.matrix),
                         "Размер: 2 × 2\n30 44\n46 68")

    def test_combined_decorators(self):
        formatter = SizeFormatter(RowNumbersFormatter(PlainFormatter(3)))
        self.assertEqual(formatter.format(self.matrix),
                         "Размер: 2 × 2\n1: 30 44\n2: 46 68")

    def test_order_is_preserved(self):
        formatter = RowNumbersFormatter(SizeFormatter(PlainFormatter(3)))
        self.assertEqual(formatter.format(self.matrix),
                         "1: Размер: 2 × 2\n2: 30 44\n3: 46 68")

    def test_raw_file_and_matrix_unchanged(self):
        SizeFormatter(RowNumbersFormatter(PlainFormatter(0))).format(self.matrix)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "result.txt"
            self.matrix.save(path)
            self.assertEqual(Matrix.load(path).data, [[30, 44], [46, 68]])
            self.assertNotIn("Размер", path.read_text(encoding="utf-8"))

    def test_precision_and_abstract_formatter(self):
        formatter = RowNumbersFormatter(PlainFormatter(2))
        self.assertEqual(formatter.format(Matrix([[1.234, -0.001]])), "1: 1.23 0")
        with self.assertRaises(TypeError):
            MatrixFormatter()


if __name__ == "__main__":
    unittest.main()
