"""Матричный калькулятор. Запуск: python app.py"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser

from matrix import Matrix
from settings import AppSettings
from creators import TextMatrixCreator
from adapters import TextMatrixReader, CsvTableReader, CsvMatrixAdapter
from portraits import SignPortrait, ColorCellRenderer, TextCellRenderer


class MatrixCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.settings = AppSettings()
        self.result = None
        self.prototype = None
        root.title("Лабораторная 3 · Матричный калькулятор · Вариант 6")
        root.geometry("1000x720")
        root.minsize(780, 600)
        try:
            self.settings.load()
        except (OSError, ValueError, TypeError) as error:
            messagebox.showwarning("Настройки", str(error), parent=root)

        main = ttk.Frame(root, padding=12)
        main.pack(fill="both", expand=True)
        ttk.Label(main, text="Матричный калькулятор",
                  font=("Arial", 18, "bold")).pack(anchor="w")
        ttk.Label(main, text="Элементы разделяйте пробелами, строки — Enter. "
                  "Дробные числа можно вводить с точкой или запятой.").pack(anchor="w", pady=6)
        inputs = ttk.Frame(main)
        inputs.pack(fill="x")
        self.a_text = self.matrix_field(inputs, "Матрица A", "1 2\n3 4")
        self.b_text = self.matrix_field(inputs, "Матрица B", "5 6\n7 8")

        copies = ttk.Frame(main)
        copies.pack(fill="x", pady=4)
        ttk.Button(copies, text="Запомнить A как образец",
                   command=self.remember_prototype).pack(side="left")
        ttk.Button(copies, text="Копия образца в B",
                   command=self.restore_prototype).pack(side="left", padx=8)

        commands = ttk.Frame(main)
        commands.pack(fill="x", pady=10)
        self.operation = ttk.Combobox(commands, state="readonly", width=12,
                                     values=["A + B", "A - B", "A × число", "A × B"])
        self.operation.current(0)
        self.operation.pack(side="left")
        ttk.Label(commands, text="  Число: ").pack(side="left")
        self.scalar = ttk.Entry(commands, width=10)
        self.scalar.insert(0, "2")
        self.scalar.pack(side="left")
        ttk.Button(commands, text="Вычислить", command=self.calculate).pack(side="left", padx=8)
        ttk.Button(commands, text="Настройки", command=self.open_settings).pack(side="right")

        output = ttk.LabelFrame(main, text="Результат", padding=6)
        output.pack(fill="x")
        self.result_text = tk.Text(output, height=5, wrap="none", state="disabled")
        self.result_text.pack(fill="x")
        result_scroll = ttk.Scrollbar(output, orient="horizontal", command=self.result_text.xview)
        result_scroll.pack(fill="x")
        self.result_text.configure(xscrollcommand=result_scroll.set)
        ttk.Button(output, text="Сохранить результат в файл",
                   command=self.save_result).pack(anchor="w", pady=4)

        portrait_bar = ttk.Frame(main)
        portrait_bar.pack(fill="x", pady=(10, 4))
        ttk.Label(portrait_bar, text="Портрет матрицы: ").pack(side="left")
        self.portrait_source = ttk.Combobox(portrait_bar, state="readonly",
                                          values=["A", "B", "Результат"], width=12)
        self.portrait_source.current(0)
        self.portrait_source.pack(side="left")
        ttk.Button(portrait_bar, text="Показать",
                   command=self.show_portrait).pack(side="left", padx=8)
        self.portrait_mode = ttk.Combobox(portrait_bar, state="readonly",
                                         values=["Цветные клетки", "Знаки"], width=16)
        self.portrait_mode.current(0)
        self.portrait_mode.pack(side="left")
        self.portrait_mode.bind("<<ComboboxSelected>>", lambda event: self.show_portrait())
        area = ttk.Frame(main)
        area.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(area, background="#eeeeee", highlightthickness=0)
        horizontal = ttk.Scrollbar(area, orient="horizontal", command=self.canvas.xview)
        vertical = ttk.Scrollbar(area, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=horizontal.set, yscrollcommand=vertical.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        area.rowconfigure(0, weight=1)
        area.columnconfigure(0, weight=1)
        self.apply_settings()
        self.show_portrait()

    def matrix_field(self, parent, title, sample):
        frame = ttk.LabelFrame(parent, text=title, padding=6)
        frame.pack(side="left", fill="both", expand=True, padx=3)
        text = tk.Text(frame, width=30, height=6, wrap="none")
        text.insert("1.0", sample)
        text.pack(fill="both", expand=True)
        scroll = ttk.Scrollbar(frame, orient="horizontal", command=text.xview)
        scroll.pack(fill="x")
        text.configure(xscrollcommand=scroll.set)
        ttk.Button(frame, text="Загрузить из файла",
                   command=lambda: self.load_matrix(text)).pack(anchor="w", pady=4)
        return text

    def read_matrix(self, text):
        creator = TextMatrixCreator(text.get("1.0", "end"))
        matrix, _ = creator.prepare()
        return matrix

    def remember_prototype(self):
        try:
            self.prototype = self.read_matrix(self.a_text).clone()
        except ValueError as error:
            self.error(error)

    def restore_prototype(self):
        if self.prototype is None:
            self.error("Сначала запомните матрицу A как образец.")
            return
        matrix = self.prototype.clone()
        self.b_text.delete("1.0", "end")
        self.b_text.insert("1.0", matrix.to_text())
        self.portrait_source.set("B")
        self.show_portrait()

    def error(self, error):
        messagebox.showerror("Ошибка", str(error), parent=self.root)

    def load_matrix(self, text):
        path = filedialog.askopenfilename(parent=self.root,
            filetypes=[("Матрицы TXT и CSV", "*.txt *.csv"),
                       ("Текстовые файлы", "*.txt"), ("Таблицы CSV", "*.csv")])
        if not path:
            return
        try:
            if path.lower().endswith(".csv"):
                reader = CsvMatrixAdapter(CsvTableReader())
            else:
                reader = TextMatrixReader()
            matrix = reader.read(path)
            text.delete("1.0", "end")
            text.insert("1.0", matrix.to_text())
            self.show_portrait()
        except (ValueError, OSError) as error:
            self.error(error)

    def calculate(self):
        try:
            a = self.read_matrix(self.a_text)
            operation = self.operation.get()
            if operation == "A × число":
                result = a.multiply_by_number(Matrix.number(self.scalar.get()))
            else:
                b = self.read_matrix(self.b_text)
                if operation == "A + B":
                    result = a.add(b)
                elif operation == "A - B":
                    result = a.subtract(b)
                else:
                    result = a.multiply(b)
            self.result = result
            self.update_result_text()
            self.portrait_source.set("Результат")
            self.show_portrait()
        except (ValueError, OverflowError) as error:
            # После ошибки предыдущий результат не должен выглядеть новым.
            self.result = None
            self.update_result_text()
            self.canvas.delete("all")
            self.error(error)

    def update_result_text(self):
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        if self.result:
            self.result_text.insert("1.0", self.result.to_text(
                self.settings.values["decimal_places"]))
        self.result_text.configure(state="disabled")

    def save_result(self):
        if self.result is None:
            messagebox.showinfo("Результат", "Сначала выполните вычисление.", parent=self.root)
            return
        path = filedialog.asksaveasfilename(parent=self.root, defaultextension=".txt",
                                          filetypes=[("Текстовые файлы", "*.txt")])
        if path:
            try:
                self.result.save(path)
            except OSError as error:
                self.error(error)

    def show_portrait(self):
        try:
            source = self.portrait_source.get()
            if source == "Результат":
                matrix = self.result
                if matrix is None:
                    raise ValueError("Сначала выполните вычисление.")
            else:
                matrix = self.read_matrix(self.a_text if source == "A" else self.b_text)
            settings = self.settings.values
            renderer_class = (TextCellRenderer if self.portrait_mode.get() == "Знаки"
                              else ColorCellRenderer)
            renderer = renderer_class(self.canvas, settings)
            portrait = SignPortrait(renderer, settings)
            portrait.draw(matrix)
        except ValueError as error:
            self.canvas.delete("all")
            self.error(error)

    def apply_settings(self):
        font = ("Consolas", self.settings.values["font_size"])
        for text in (self.a_text, self.b_text, self.result_text):
            text.configure(font=font)
        self.update_result_text()

    def open_settings(self):
        window = tk.Toplevel(self.root)
        window.title("Настройки — единственный объект AppSettings")
        window.resizable(False, False)
        window.transient(self.root)
        window.grab_set()
        frame = ttk.Frame(window, padding=16)
        frame.pack()
        variables = {}
        labels = {"decimal_places": "Знаков после запятой (0–10)",
                  "font_size": "Размер шрифта (8–24)",
                  "cell_size": "Размер клетки (10–60)", "show_grid": "Показывать сетку",
                  "positive_color": "Цвет положительных элементов",
                  "negative_color": "Цвет отрицательных элементов",
                  "zero_color": "Цвет нулевых элементов"}
        for row, (key, label) in enumerate(labels.items()):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=5)
            value = self.settings.values[key]
            if key == "show_grid":
                variable = tk.BooleanVar(value=value)
                ttk.Checkbutton(frame, variable=variable).grid(row=row, column=1)
            else:
                variable = tk.StringVar(value=str(value))
                ttk.Entry(frame, textvariable=variable, width=14).grid(row=row, column=1)
                if key.endswith("color"):
                    def choose_color(var=variable):
                        color = colorchooser.askcolor(parent=window, color=var.get())[1]
                        if color:
                            var.set(color)
                    ttk.Button(frame, text="Цвет", command=choose_color).grid(row=row, column=2)
            variables[key] = variable

        def save():
            try:
                values = {key: var.get() for key, var in variables.items()}
                for key in ("decimal_places", "font_size", "cell_size"):
                    values[key] = int(values[key])
                self.settings.save(values)
                self.apply_settings()
                self.show_portrait()
                window.destroy()
            except (ValueError, OSError) as error:
                messagebox.showerror("Настройки", str(error), parent=window)
        ttk.Button(frame, text="Сохранить", command=save).grid(row=7, column=0, pady=12)
        ttk.Button(frame, text="Отмена", command=window.destroy).grid(row=7, column=1)


if __name__ == "__main__":
    root = tk.Tk()
    MatrixCalculatorApp(root)
    root.mainloop()
