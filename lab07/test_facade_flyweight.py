import tempfile
import unittest
from pathlib import Path
from dataclasses import FrozenInstanceError

from facade import CalculatorFacade
from cell_styles import CellStyleFactory
from settings import AppSettings
from test_structural import RecordingCanvas
from portraits import SignPortrait, ColorCellRenderer
from matrix import Matrix


class FacadeTests(unittest.TestCase):
    def setUp(self):
        self.facade = CalculatorFacade()

    def test_operations(self):
        for op, expected in [
            ("A + B", [[6, 8], [10, 12]]),
            ("A - B", [[-4, -4], [-4, -4]]),
            ("A × B", [[19, 22], [43, 50]]),
            ("(A + B) × A", [[30, 44], [46, 68]])]:
            with self.subTest(op=op):
                result = self.facade.calculate("1 2\n3 4", "5 6\n7 8", op)
                self.assertEqual(result.data, expected)

    def test_scalar_ignores_unused_matrix(self):
        result = self.facade.calculate("1,5 -2", "ошибка", "A × число", "2")
        self.assertEqual(result.data, [[3, -4]])

    def test_invalid_input(self):
        for a, b, op in [("x", "1", "A + B"),
                         ("1 2", "1", "A + B"), ("1", "2", "?")]:
            with self.subTest(op=op), self.assertRaises(ValueError):
                self.facade.calculate(a, b, op)

    def test_file_formats(self):
        with tempfile.TemporaryDirectory() as folder:
            txt = Path(folder) / "m.txt"
            csv = Path(folder) / "m.CSV"
            matrix = Matrix([[1.25, -2]])
            self.facade.save(matrix, txt)
            self.assertEqual(self.facade.load(txt).data, matrix.data)
            csv.write_text("1,25;-2", encoding="utf-8")
            self.assertEqual(self.facade.load(csv).data, matrix.data)


class FlyweightTests(unittest.TestCase):
    def setUp(self):
        self.styles = CellStyleFactory()
        self.settings = AppSettings.DEFAULTS.copy()

    def test_sharing_and_distinct_signs(self):
        plus = self.styles.get(1, self.settings)
        self.assertIs(plus, self.styles.get(100, self.settings))
        self.assertIsNot(plus, self.styles.get(-1, self.settings))
        with self.assertRaises(FrozenInstanceError):
            plus.color = "#000000"

    def test_settings_change_and_clear(self):
        old = self.styles.get(1, self.settings)
        self.settings["positive_color"] = "#123456"
        new = self.styles.get(1, self.settings)
        self.assertEqual(new.color, "#123456")
        self.assertIsNot(old, new)
        self.styles.clear()
        self.assertIsNot(new, self.styles.get(1, self.settings))

    def test_shared_styles_keep_coordinates_separate(self):
        canvas = RecordingCanvas()
        renderer = ColorCellRenderer(canvas, self.settings)
        portrait = SignPortrait(renderer, self.settings, self.styles)
        portrait.draw(Matrix([[1, 2, 0], [-1, -2, 0]]))
        self.assertEqual(len(self.styles._styles), 3)
        self.assertEqual(len(canvas.rectangles), 6)
        self.assertEqual(canvas.rectangles[-1][0], (60, 30, 90, 60))


if __name__ == "__main__":
    unittest.main()
