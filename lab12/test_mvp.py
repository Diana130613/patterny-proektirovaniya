import unittest
from model import CalculatorModel
from presenter import CalculatorPresenter


class FakeView:
    def __init__(self):
        self.request = ('1 2\n3 4', '5 6\n7 8', 'A + B', '2')
        self.errors = []
        self.source = 'A'
        self.text = ''

    def get_request(self): return self.request
    def set_request(self, request): self.request = request
    def get_format_options(self): return False, False
    def get_portrait_options(self): return self.source, 'Цветные клетки'
    def select_result(self): self.source = 'Результат'
    def show_result(self, text, statistics): self.text = text
    def show_error(self, message): self.errors.append(message)
    def show_status(self, message): self.status = message
    def enable_scalar(self, enabled): self.scalar_enabled = enabled
    def draw_portrait(self, matrix, mode, settings): self.matrix = matrix


class PresenterTests(unittest.TestCase):
    def setUp(self):
        self.view = FakeView()
        self.model = CalculatorModel()
        self.presenter = CalculatorPresenter(self.model, self.view)

    def test_calculation_and_undo_without_window(self):
        self.presenter.calculate()
        self.assertEqual(self.view.text, '6 8\n10 12')
        self.view.request = (*self.view.request[:2], 'A - B', '2')
        self.presenter.calculate()
        self.presenter.undo()
        self.assertEqual(self.view.text, '6 8\n10 12')
        self.assertEqual(self.model.context.result.data, [[6,8],[10,12]])

    def test_error_preserves_result(self):
        self.presenter.calculate()
        self.view.request = ('x', '1', 'A + B', '')
        self.presenter.calculate()
        self.assertEqual(len(self.view.errors), 1)
        self.assertEqual(self.view.text, '6 8\n10 12')

    def test_snapshot_restores_fields_and_result(self):
        self.presenter.calculate()
        self.presenter.save_session()
        original = self.view.request
        self.view.request = ('9', '1', 'A × число', '3')
        self.presenter.calculate()
        self.presenter.restore_session()
        self.assertEqual(self.view.request, original)
        self.assertEqual(self.view.text, '6 8\n10 12')
        self.assertEqual(self.model.history.commands, [])
        self.assertFalse(self.view.scalar_enabled)


if __name__ == '__main__':
    unittest.main(verbosity=2)
