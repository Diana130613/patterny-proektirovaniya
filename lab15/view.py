import tkinter as tk
from tkinter import ttk
from base_view import BaseCalculatorView


class CalculatorView(BaseCalculatorView):
    def __init__(self, root):
        super().__init__(root)
        root.title("Лабораторная 15 · Матричный калькулятор · Вариант 6")
        root.geometry("1100x920")
        self.extra = ttk.Frame(root, padding=(12, 4, 12, 10))
        self.extra.pack(fill="x", side="bottom", before=root.winfo_children()[0])
        self.journal_status = tk.StringVar(value="Журнал: 0 событий")
        row = ttk.Frame(self.extra)
        row.pack(fill="x")
        self.button(row, "Восстановить из журнала", "replay")
        self.button(row, "История событий", "show_history")
        ttk.Label(row, textvariable=self.journal_status).pack(side="left", padx=8)
        row = ttk.Frame(self.extra)
        row.pack(fill="x", pady=5)
        ttk.Label(row, text="Название: ").pack(side="left")
        self.session_name = ttk.Entry(row, width=18)
        self.session_name.insert(0, "Мой расчёт")
        self.session_name.pack(side="left")
        self.button(row, "В базу", "save_database")
        self.saved_sessions = ttk.Combobox(row, state="readonly", width=25)
        self.saved_sessions.pack(side="left", padx=5)
        self.button(row, "Загрузить", "load_database")
        self.button(row, "Удалить", "delete_database")
        self.database_ids = {}
        row = ttk.Frame(self.extra)
        row.pack(fill="x")
        self.progress = ttk.Progressbar(row, mode="indeterminate", length=180)
        self.progress.pack(side="left")
        self.background_status = tk.StringVar(value="Фоновых задач нет")
        ttk.Label(row, textvariable=self.background_status).pack(side="left", padx=8)
        self.disabled_widgets = []

    def show_journal_count(self, count):
        self.journal_status.set(f"Журнал: {count} событий")

    def show_events(self, events):
        window = tk.Toplevel(self.root)
        window.title("История событий")
        window.geometry("700x350")
        text = tk.Text(window, wrap="word", font=("Consolas", 11))
        text.pack(fill="both", expand=True)
        for event in events:
            payload = event["payload"]
            request = payload.get("request")
            operation = request[2] if request else ""
            text.insert("end", f'{event["sequence"]}. {event["kind"]} {operation}\n')
        text.configure(state="disabled")

    def update_saved_sessions(self, items, selected=None):
        self.database_ids = {f"{key}: {name}": key for key, name in items}
        self.saved_sessions.configure(values=list(self.database_ids))
        choice = next((label for label, key in self.database_ids.items()
                       if key == selected), "")
        self.saved_sessions.set(choice)

    def selected_session_id(self):
        key = self.database_ids.get(self.saved_sessions.get())
        if key is None:
            raise ValueError("Выберите сохранённый сеанс.")
        return key

    def set_busy(self, busy):
        if busy:
            self.disabled_widgets = []
            def visit(parent):
                for widget in parent.winfo_children():
                    if isinstance(widget, (ttk.Button, ttk.Entry, ttk.Combobox,
                                           ttk.Checkbutton, tk.Text)):
                        self.disabled_widgets.append((widget, widget.cget("state")))
                        widget.configure(state="disabled")
                    visit(widget)
            visit(self.root)
            self.progress.start(12)
        else:
            self.progress.stop()
            for widget, state in self.disabled_widgets:
                widget.configure(state=state)
            self.disabled_widgets = []
