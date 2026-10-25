import tempfile
import unittest
from pathlib import Path

from adapters import CsvTableReader, CsvMatrixAdapter, TextMatrixReader
from matrix import Matrix
from portraits import ColorCellRenderer, TextCellRenderer, SignPortrait
from settings import AppSettings


class RecordingCanvas:
    def __init__(self):
        self.rectangles = []
        self.labels = []
        self.region = None

    def delete(self, tag):
        self.rectangles.clear()
        self.labels.clear()

    def configure(self, **kwargs):
        self.region = kwargs["scrollregion"]

    def create_rectangle(self, *bounds, **style):
        self.rectangles.append((bounds, style))

    def create_text(self, *position, **style):
        self.labels.append((position, style))


class AdapterTests(unittest.TestCase):
    def read_csv(self, text):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "matrix.csv"
            path.write_text(text, encoding="utf-8-sig")
            return CsvMatrixAdapter(CsvTableReader()).read(path)

    def test_csv_decimals_and_quotes(self):
        matrix = self.read_csv('"1,5";-2\n0;3\n')
        self.assertEqual(matrix.data, [[1.5, -2], [0, 3]])

    def test_blank_rows(self):
        self.assertEqual(self.read_csv('\n1;2\n\n3;4\n').data,
                         [[1, 2], [3, 4]])

    def test_bad_csv(self):
        for text in ('', '1;2\n3', '1;x', '1;nan'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.read_csv(text)

    def test_text_reader(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "matrix.txt"
            Matrix([[1, -2], [0, 3]]).save(path)
            self.assertEqual(TextMatrixReader().read(path).data,
                             [[1, -2], [0, 3]])


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.settings = AppSettings.DEFAULTS.copy()
        self.canvas = RecordingCanvas()
        self.matrix = Matrix([[1, -2, 0]])

    def test_color_renderer(self):
        renderer = ColorCellRenderer(self.canvas, self.settings)
        SignPortrait(renderer, self.settings).draw(self.matrix)
        colors = [style["fill"] for _, style in self.canvas.rectangles]
        self.assertEqual(colors, [self.settings[k] for k in
                         ("positive_color", "negative_color", "zero_color")])
        self.assertEqual(self.canvas.region, (0, 0, 90, 30))
        self.assertEqual(self.canvas.labels, [])

    def test_renderer_replacement(self):
        portrait = SignPortrait(ColorCellRenderer(self.canvas, self.settings),
                                self.settings)
        portrait.draw(self.matrix)
        portrait.renderer = TextCellRenderer(self.canvas, self.settings)
        portrait.draw(self.matrix)
        self.assertEqual([style["text"] for _, style in self.canvas.labels],
                         ["+", "−", "0"])
        self.assertEqual(len(self.canvas.rectangles), 3)

    def test_no_grid(self):
        self.settings["show_grid"] = False
        renderer = ColorCellRenderer(self.canvas, self.settings)
        SignPortrait(renderer, self.settings).draw(self.matrix)
        self.assertTrue(all(style["outline"] == ""
                            for _, style in self.canvas.rectangles))

    def test_cell_coordinates(self):
        self.settings["cell_size"] = 20
        renderer = TextCellRenderer(self.canvas, self.settings)
        SignPortrait(renderer, self.settings).draw(Matrix([[0], [1]]))
        self.assertEqual(self.canvas.rectangles[1][0], (0, 20, 20, 40))
        self.assertEqual(self.canvas.region, (0, 0, 20, 40))


if __name__ == "__main__":
    unittest.main()
