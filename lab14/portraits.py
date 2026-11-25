from abc import ABC, abstractmethod
from cell_styles import CellStyleFactory


class PortraitRenderer(ABC):
    def __init__(self, canvas, settings):
        self.canvas = canvas
        self.settings = settings

    def begin(self, rows, columns):
        size = self.settings["cell_size"]
        self.canvas.delete("all")
        self.canvas.configure(scrollregion=(0, 0, columns * size, rows * size))

    @abstractmethod
    def draw_cell(self, row, column, color, label):
        pass

    def bounds(self, row, column):
        size = self.settings["cell_size"]
        return (column * size, row * size,
                (column + 1) * size, (row + 1) * size)


class ColorCellRenderer(PortraitRenderer):
    def draw_cell(self, row, column, color, label):
        outline = "#777777" if self.settings["show_grid"] else ""
        self.canvas.create_rectangle(*self.bounds(row, column),
                                     fill=color, outline=outline)


class TextCellRenderer(PortraitRenderer):
    def draw_cell(self, row, column, color, label):
        x1, y1, x2, y2 = self.bounds(row, column)
        outline = "#777777" if self.settings["show_grid"] else ""
        self.canvas.create_rectangle(x1, y1, x2, y2,
                                     fill="white", outline=outline)
        font_size = min(self.settings["font_size"],
                        max(6, self.settings["cell_size"] // 2))
        self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2,
                                text=label, fill="black",
                                font=("Consolas", font_size))


class MatrixPortrait(ABC):
    def __init__(self, renderer, settings):
        self.renderer = renderer
        self.settings = settings

    def draw(self, matrix):
        self.renderer.begin(matrix.rows, matrix.columns)
        for i, row in enumerate(matrix.data):
            for j, value in enumerate(row):
                color, label = self.describe(value)
                self.renderer.draw_cell(i, j, color, label)

    @abstractmethod
    def describe(self, value):
        pass


class SignPortrait(MatrixPortrait):
    def __init__(self, renderer, settings, styles=None):
        super().__init__(renderer, settings)
        self.styles = styles if styles is not None else CellStyleFactory()

    def describe(self, value):
        style = self.styles.get(value, self.settings)
        return style.color, style.label

    def draw(self, matrix):
        self.renderer.begin(matrix.rows, matrix.columns)
        for row, values in enumerate(matrix.data):
            for column, value in enumerate(values):
                style = self.styles.get(value, self.settings)
                style.draw(self.renderer, row, column)
