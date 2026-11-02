import unittest

from commands import ResultStore, CalculateCommand, CommandHistory
from facade import CalculatorFacade
from matrix import Matrix
from iterators import sign_counts


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.store = ResultStore()
        self.history = CommandHistory()
        self.facade = CalculatorFacade()

    def command(self, a="1 2", b="3 4", op="A + B"):
        return CalculateCommand(self.facade, self.store, a, b, op)

    def test_execute_and_multiple_undo(self):
        self.history.execute(self.command())
        self.assertEqual(self.store.result.data, [[4, 6]])
        self.history.execute(self.command(op="A - B"))
        self.assertEqual(self.store.result.data, [[-2, -2]])
        self.assertTrue(self.history.undo())
        self.assertEqual(self.store.result.data, [[4, 6]])
        self.assertTrue(self.history.undo())
        self.assertIsNone(self.store.result)
        self.assertFalse(self.history.undo())

    def test_error_does_not_enter_history_or_change_result(self):
        self.history.execute(self.command())
        with self.assertRaises(ValueError):
            self.history.execute(self.command("1 2", "1"))
        self.assertEqual(len(self.history.commands), 1)
        self.assertEqual(self.store.result.data, [[4, 6]])

    def test_previous_result_is_independent(self):
        original = Matrix([[8]])
        self.store.set_result(original)
        original.data[0][0] = 99
        self.history.execute(self.command())
        self.store.result.data[0][0] = 77
        self.history.undo()
        self.assertEqual(self.store.result.data, [[8]])

    def test_new_calculation_after_undo(self):
        self.history.execute(self.command())
        self.history.execute(self.command(op="A - B"))
        self.history.undo()
        self.history.execute(self.command("2", "3"))
        self.assertEqual(self.store.result.data, [[5]])
        self.history.undo()
        self.assertEqual(self.store.result.data, [[4, 6]])


class IteratorTests(unittest.TestCase):
    def test_row_major_and_coordinates(self):
        matrix = Matrix([[1, -2, 0], [3, 4, -5]])
        self.assertEqual(list(matrix), [
            (0, 0, 1), (0, 1, -2), (0, 2, 0),
            (1, 0, 3), (1, 1, 4), (1, 2, -5)])
        self.assertEqual(sign_counts(matrix), (3, 2, 1))

    def test_independent_and_nested_iterators(self):
        matrix = Matrix([[1, 2]])
        first, second = iter(matrix), iter(matrix)
        self.assertIs(iter(first), first)
        self.assertEqual(next(first), next(second))
        self.assertEqual(len([(a, b) for a in matrix for b in matrix]), 4)
        self.assertEqual(list(matrix), list(matrix))

    def test_single_cell_and_exhaustion(self):
        iterator = iter(Matrix([[0]]))
        self.assertEqual(next(iterator), (0, 0, 0))
        for _ in range(2):
            with self.assertRaises(StopIteration):
                next(iterator)

    def test_column_and_sign_counts(self):
        matrix = Matrix([[-1], [0], [2]])
        self.assertEqual(list(matrix), [(0, 0, -1), (1, 0, 0), (2, 0, 2)])
        self.assertEqual(sign_counts(matrix), (1, 1, 1))


if __name__ == "__main__":
    unittest.main()
