"""Проверка существенных требований. Запуск: python -m unittest -v"""

import tempfile
import unittest
from pathlib import Path

from matrix import Matrix
from settings import AppSettings


class MatrixTests(unittest.TestCase):
    def setUp(self):
        self.a = Matrix([[1, 2], [3, 4]])
        self.b = Matrix([[5, 6], [7, 8]])

    def test_four_operations(self):
        self.assertEqual(self.a.add(self.b).data, [[6, 8], [10, 12]])
        self.assertEqual(self.a.subtract(self.b).data, [[-4, -4], [-4, -4]])
        self.assertEqual(self.a.multiply_by_number(2).data, [[2, 4], [6, 8]])
        self.assertEqual(self.a.multiply(self.b).data, [[19, 22], [43, 50]])

    def test_rectangular_multiplication(self):
        a = Matrix([[1, 2, 3], [4, 5, 6]])
        b = Matrix([[1], [2], [3]])
        self.assertEqual(a.multiply(b).data, [[14], [32]])

    def test_wrong_dimensions(self):
        for operation in (self.a.add, self.a.subtract, self.a.multiply):
            with self.assertRaises(ValueError):
                operation(Matrix([[1, 2, 3]]))

    def test_text_and_decimals(self):
        matrix = Matrix.from_text("1,5 -2.25\n0 3")
        self.assertEqual(matrix.data, [[1.5, -2.25], [0, 3]])
        self.assertEqual(matrix.to_text(1), "1.5 -2.2\n0 3")
        self.assertEqual(Matrix([[-0.001]]).to_text(2), "0")

    def test_invalid_numbers_and_rows(self):
        for text in ("", "1 2\n3", "NaN", "inf", "abc"):
            with self.assertRaises(ValueError):
                Matrix.from_text(text)
        with self.assertRaises(ValueError):
            Matrix([[1e308]]).multiply_by_number(2)

    def test_file_roundtrip_preserves_precision(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "result.txt"
            original = Matrix([[1.123456789012345, -2], [0, 3]])
            original.save(path)
            self.assertEqual(Matrix.load(path).data, original.data)
            path.write_text("2 2\n1 2\n3", encoding="utf-8-sig")
            with self.assertRaises(ValueError):
                Matrix.load(path)

    def test_example_files(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "matrix.txt"
            for text, expected in (("2 2\n1 2\n3 4", self.a.data),
                                   ("2 2\n5 6\n7 8", self.b.data)):
                path.write_text(text, encoding="utf-8-sig")
                self.assertEqual(Matrix.load(path).data, expected)


class SettingsTests(unittest.TestCase):
    def test_singleton_and_shared_state(self):
        a, b = AppSettings(), AppSettings()
        self.assertIs(a, b)
        old = a.values.copy()
        try:
            a.values["font_size"] = 15
            self.assertEqual(b.values["font_size"], 15)
        finally:
            a.values = old

    def test_seven_settings_save_and_load(self):
        settings = AppSettings()
        old_path, old_values = settings.FILE, settings.values.copy()
        try:
            with tempfile.TemporaryDirectory() as folder:
                settings.FILE = Path(folder) / "settings.json"
                values = settings.DEFAULTS.copy()
                values["cell_size"] = 40
                settings.save(values)
                settings.values = settings.DEFAULTS.copy()
                settings.load()
                self.assertEqual(settings.values, values)
                self.assertEqual(len(settings.values), 7)
        finally:
            settings.FILE, settings.values = old_path, old_values

    def test_invalid_settings(self):
        settings = AppSettings()
        for key, value in (("font_size", 100), ("decimal_places", -1),
                           ("show_grid", "yes"), ("positive_color", "red")):
            values = settings.DEFAULTS.copy()
            values[key] = value
            with self.assertRaises(ValueError):
                settings.validate(values)


if __name__ == "__main__":
    unittest.main()
