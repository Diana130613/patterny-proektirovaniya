import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from portraits import SignPortrait, ColorCellRenderer, TextCellRenderer
from cell_styles import CellStyleFactory


class BaseCalculatorView:
    def __init__(self, root):
        self.root, self.presenter = root, None
        self.styles = CellStyleFactory()
        self.current_settings = {}
        root.title("Лабораторная 12 · Матричный калькулятор · Вариант 6")
        root.geometry("1080x850")
        root.minsize(950, 800)
        main = ttk.Frame(root, padding=12)
        main.pack(fill="both", expand=True)
        ttk.Label(main, text="Матричный калькулятор", font=("Arial", 18, "bold")).pack(anchor="w")
        ttk.Label(main, text="Элементы разделяйте пробелами, строки – Enter. Дробные числа: точка или запятая.").pack(anchor="w", pady=6)
        inputs = ttk.Frame(main)
        inputs.pack(fill="x")
        self.a_text = self.matrix_field(inputs, "A", "1 2\n3 4")
        self.b_text = self.matrix_field(inputs, "B", "5 6\n7 8")
        bar = ttk.Frame(main)
        bar.pack(fill="x", pady=5)
        self.button(bar, "Запомнить A как образец", "remember")
        self.button(bar, "Копия образца в B", "restore_prototype")
        bar = ttk.Frame(main)
        bar.pack(fill="x", pady=8)
        self.operation = ttk.Combobox(bar, state="readonly", width=18,
            values=["A + B", "A - B", "A × число", "A × B", "(A + B) × A"])
        self.operation.current(0)
        self.operation.pack(side="left")
        self.operation.bind("<<ComboboxSelected>>", lambda e: self.presenter.operation_changed())
        ttk.Label(bar, text=" Число: ").pack(side="left")
        self.scalar = ttk.Entry(bar, width=10)
        self.scalar.insert(0, "2")
        self.scalar.pack(side="left")
        self.button(bar, "Вычислить", "calculate")
        self.button(bar, "Отменить", "undo")
        ttk.Button(bar, text="Настройки", command=self.open_settings).pack(side="right")
        output = ttk.LabelFrame(main, text="Результат", padding=6)
        output.pack(fill="x")
        self.row_numbers, self.show_size = tk.BooleanVar(), tk.BooleanVar()
        formatting = ttk.Frame(output)
        formatting.pack(fill="x")
        for text, variable in (("Номера строк", self.row_numbers), ("Размер матрицы", self.show_size)):
            ttk.Checkbutton(formatting, text=text, variable=variable,
                command=lambda: self.presenter.refresh_result()).pack(side="left", padx=3)
        self.button(formatting, "Очистить кэш", "clear_cache")
        self.statistics = tk.StringVar(value="Нет результата")
        ttk.Label(output, textvariable=self.statistics).pack(anchor="w")
        self.result_text = tk.Text(output, height=5, state="disabled", wrap="none")
        self.result_text.pack(fill="x")
        scroll = ttk.Scrollbar(output, orient="horizontal", command=self.result_text.xview)
        scroll.pack(fill="x")
        self.result_text.configure(xscrollcommand=scroll.set)
        ttk.Button(output, text="Сохранить результат в файл", command=self.choose_save).pack(anchor="w", pady=4)
        bar = ttk.Frame(main)
        bar.pack(fill="x", pady=8)
        self.button(bar, "Сохранить сеанс", "save_session")
        self.button(bar, "Восстановить сеанс", "restore_session")
        ttk.Label(bar, text="Алгоритм: ").pack(side="left")
        self.algorithm = ttk.Combobox(bar, state="readonly", width=25,
            values=["Обычный", "С транспонированием B"])
        self.algorithm.current(0)
        self.algorithm.pack(side="left")
        self.algorithm.bind("<<ComboboxSelected>>", lambda e: self.presenter.change_strategy(self.algorithm.get()))
        self.status = tk.StringVar(value="Готов")
        ttk.Label(main, textvariable=self.status, wraplength=1000).pack(anchor="w", pady=4)
        bar = ttk.Frame(main)
        bar.pack(fill="x", pady=5)
        ttk.Label(bar, text="Портрет матрицы: ").pack(side="left")
        self.portrait_source = ttk.Combobox(bar, values=["A", "B", "Результат"], state="readonly", width=12)
        self.portrait_source.current(0)
        self.portrait_source.pack(side="left")
        self.button(bar, "Показать", "show_portrait")
        self.portrait_mode = ttk.Combobox(bar, values=["Цветные клетки", "Знаки"], state="readonly", width=18)
        self.portrait_mode.current(0)
        self.portrait_mode.pack(side="left")
        self.portrait_mode.bind("<<ComboboxSelected>>", lambda e: self.presenter.show_portrait())
        area = ttk.Frame(main)
        area.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(area, background="#eeeeee", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(area, orient="vertical", command=self.canvas.yview)
        horizontal = ttk.Scrollbar(area, orient="horizontal", command=self.canvas.xview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(xscrollcommand=horizontal.set, yscrollcommand=vertical.set)
        area.rowconfigure(0, weight=1)
        area.columnconfigure(0, weight=1)

    def button(self, parent, text, method):
        ttk.Button(parent, text=text, command=lambda: getattr(self.presenter, method)()).pack(side="left", padx=4)

    def matrix_field(self, parent, name, sample):
        frame = ttk.LabelFrame(parent, text="Матрица " + name, padding=6)
        frame.pack(side="left", fill="both", expand=True, padx=3)
        text = tk.Text(frame, height=6, width=30, wrap="none")
        text.insert("1.0", sample)
        text.pack(fill="both", expand=True)
        scroll = ttk.Scrollbar(frame, orient="horizontal", command=text.xview)
        scroll.pack(fill="x")
        text.configure(xscrollcommand=scroll.set)
        ttk.Button(frame, text="Загрузить из файла", command=lambda: self.choose_load(name)).pack(anchor="w", pady=4)
        return text

    def get_request(self):
        return (self.a_text.get("1.0", "end-1c"), self.b_text.get("1.0", "end-1c"),
                self.operation.get(), self.scalar.get())

    def set_request(self, request):
        self.set_matrix_text("A", request[0])
        self.set_matrix_text("B", request[1])
        self.operation.set(request[2])
        self.scalar.configure(state="normal")
        self.scalar.delete(0, "end")
        self.scalar.insert(0, request[3])

    def set_matrix_text(self, field, text):
        widget = self.a_text if field == "A" else self.b_text
        widget.delete("1.0", "end")
        widget.insert("1.0", text)

    def enable_scalar(self, enabled):
        self.scalar.configure(state="normal" if enabled else "disabled")

    def get_format_options(self):
        return self.row_numbers.get(), self.show_size.get()

    def get_portrait_options(self):
        return self.portrait_source.get(), self.portrait_mode.get()

    def select_result(self):
        self.portrait_source.set("Результат")

    def show_result(self, text, statistics):
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
        self.result_text.configure(state="disabled")
        self.statistics.set(statistics)

    def show_status(self, message):
        self.status.set(message)
        self.root.update_idletasks()

    def show_error(self, message):
        messagebox.showerror("Ошибка", message, parent=self.root)

    def draw_portrait(self, matrix, mode, settings):
        self.canvas.delete("all")
        if matrix is not None:
            renderer = TextCellRenderer if mode == "Знаки" else ColorCellRenderer
            SignPortrait(renderer(self.canvas, settings), settings, self.styles).draw(matrix)

    def apply_settings(self, settings):
        self.current_settings = settings.copy()
        self.styles.clear()
        for widget in (self.a_text, self.b_text, self.result_text):
            widget.configure(font=("Consolas", settings["font_size"]))

    def choose_load(self, field):
        path = filedialog.askopenfilename(parent=self.root, filetypes=[("Матрицы", "*.txt *.csv")])
        if path:
            self.presenter.load(field, path)

    def choose_save(self):
        path = filedialog.asksaveasfilename(parent=self.root, defaultextension=".txt",
            filetypes=[("Матрицы TXT", "*.txt")])
        if path:
            self.presenter.save(path)

    def open_settings(self):
        window = tk.Toplevel(self.root)
        window.title("Настройки")
        window.transient(self.root)
        window.grab_set()
        frame = ttk.Frame(window, padding=16)
        frame.pack()
        variables = {}
        labels = {"decimal_places": "Знаков после запятой (0–10)", "font_size": "Размер шрифта (8–24)",
                  "cell_size": "Размер клетки (10–60)", "show_grid": "Показывать сетку",
                  "positive_color": "Цвет положительных", "negative_color": "Цвет отрицательных", "zero_color": "Цвет нулей"}
        for row, (key, label) in enumerate(labels.items()):
            value = self.current_settings[key]
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=4)
            variable = tk.BooleanVar(value=value) if key == "show_grid" else tk.StringVar(value=str(value))
            variables[key] = variable
            widget = ttk.Checkbutton(frame, variable=variable) if key == "show_grid" else ttk.Entry(frame, textvariable=variable)
            widget.grid(row=row, column=1)
            if key.endswith("color"):
                def choose(var=variable):
                    color = colorchooser.askcolor(parent=window, color=var.get())[1]
                    if color:
                        var.set(color)
                ttk.Button(frame, text="Цвет", command=choose).grid(row=row, column=2)
        def save():
            try:
                values = {key: var.get() for key, var in variables.items()}
                for key in ("decimal_places", "font_size", "cell_size"):
                    values[key] = int(values[key])
                if self.presenter.save_settings(values):
                    window.destroy()
            except ValueError:
                self.show_error("Настройки размеров и точности должны быть целыми числами.")
        ttk.Button(frame, text="Сохранить", command=save).grid(row=7, column=0, pady=8)
        ttk.Button(frame, text="Отмена", command=window.destroy).grid(row=7, column=1)
