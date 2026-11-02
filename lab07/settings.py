"""Один объект настроек для всех частей приложения — паттерн Одиночка."""

import json
from pathlib import Path


class AppSettings:
    _instance = None
    FILE = Path(__file__).with_name("settings.json")
    DEFAULTS = {
        "decimal_places": 3,
        "font_size": 12,
        "cell_size": 30,
        "show_grid": True,
        "positive_color": "#90ee90",
        "negative_color": "#f08080",
        "zero_color": "#ffffff",
    }

    def __new__(cls):
        # Первый вызов создаёт объект, последующие возвращают тот же объект.
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.values = cls.DEFAULTS.copy()
        return cls._instance

    def load(self):
        if self.FILE.exists():
            with self.FILE.open(encoding="utf-8") as file:
                values = json.load(file)
            self.validate(values)
            self.values = values

    def validate(self, values):
        if not isinstance(values, dict) or set(values) != set(self.DEFAULTS):
            raise ValueError("В файле настроек должен быть набор из 7 параметров.")
        limits = {"decimal_places": (0, 10), "font_size": (8, 24),
                  "cell_size": (10, 60)}
        for key, (minimum, maximum) in limits.items():
            value = values[key]
            if type(value) is not int or not minimum <= value <= maximum:
                raise ValueError(f"{key}: допустимы целые числа {minimum}–{maximum}.")
        if type(values["show_grid"]) is not bool:
            raise ValueError("Показ сетки должен быть логическим значением.")
        for key in ("positive_color", "negative_color", "zero_color"):
            color = values[key]
            if not isinstance(color, str) or len(color) != 7 or color[0] != "#":
                raise ValueError("Цвет задаётся в формате #RRGGBB.")
            try:
                int(color[1:], 16)
            except ValueError:
                raise ValueError("Цвет задаётся в формате #RRGGBB.") from None

    def save(self, values):
        self.validate(values)
        # Сначала записываем файл. Если запись не удалась, настройки не меняются.
        with self.FILE.open("w", encoding="utf-8") as file:
            json.dump(values, file, ensure_ascii=False, indent=2)
        self.values = values.copy()
