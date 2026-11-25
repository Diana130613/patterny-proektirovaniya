import tkinter as tk
from tkinter import ttk
from base_view import BaseCalculatorView


class CalculatorView(BaseCalculatorView):
    def __init__(self, root):
        super().__init__(root)
        root.title("Лабораторная 13 · Матричный калькулятор · Вариант 6")
        root.geometry("1100x920")
        self.extra = ttk.Frame(root, padding=(12, 4, 12, 10))
        self.extra.pack(fill="x", side="bottom", before=root.winfo_children()[0])
        self.journal_status = tk.StringVar(value="Журнал: 0 событий")
        row = ttk.Frame(self.extra)
        row.pack(fill="x")
        self.button(row, "Восстановить из журнала", "replay")
        self.button(row, "История событий", "show_history")
        ttk.Label(row, textvariable=self.journal_status).pack(side="left", padx=8)

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
