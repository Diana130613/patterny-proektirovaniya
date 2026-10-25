import tempfile
import unittest
from pathlib import Path

from matrix import Matrix
from creators import MatrixCreator, TextMatrixCreator, FileMatrixCreator


class PatternTests(unittest.TestCase):
    def test_abstract_creator(self):
        with self.assertRaises(TypeError):
            MatrixCreator()

    def test_text_creator(self):
        matrix, size = TextMatrixCreator("1 2\n3 4").prepare()
        self.assertEqual(matrix.data, [[1, 2], [3, 4]])
        self.assertEqual(size, "2 × 2")

    def test_file_creator(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "matrix.txt"
            Matrix([[1, 2], [3, 4]]).save(path)
            matrix, size = FileMatrixCreator(path).prepare()
            self.assertEqual(matrix.data, [[1, 2], [3, 4]])
            self.assertEqual(size, "2 × 2")

    def test_clone_is_independent(self):
        original = Matrix([[1, 2], [3, 4]])
        copy = original.clone()
        self.assertIsNot(original, copy)
        self.assertIsNot(original.data, copy.data)
        self.assertIsNot(original.data[0], copy.data[0])
        copy.data[0][0] = 99
        self.assertEqual(original.data[0][0], 1)

    def test_multiple_clones(self):
        prototype = Matrix([[1]])
        first, second = prototype.clone(), prototype.clone()
        first.data[0][0] = 99
        self.assertEqual(second.data, [[1]])
        self.assertEqual(prototype.data, [[1]])

    def test_bad_sources(self):
        with self.assertRaises(ValueError):
            TextMatrixCreator("1 2\n3").prepare()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.txt"
            path.write_text("2 2\n1 2", encoding="utf-8")
            with self.assertRaises(ValueError):
                FileMatrixCreator(path).prepare()


if __name__ == "__main__":
    unittest.main()
