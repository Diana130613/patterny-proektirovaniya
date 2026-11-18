from dataclasses import dataclass


@dataclass(frozen=True)
class CellStyle:
    color: str
    label: str

    def draw(self, renderer, row, column):
        renderer.draw_cell(row, column, self.color, self.label)


class CellStyleFactory:
    def __init__(self):
        self._styles = {}

    def get(self, value, settings):
        if value > 0:
            key = (settings["positive_color"], "+")
        elif value < 0:
            key = (settings["negative_color"], "−")
        else:
            key = (settings["zero_color"], "0")
        if key not in self._styles:
            self._styles[key] = CellStyle(*key)
        return self._styles[key]

    def clear(self):
        self._styles.clear()
