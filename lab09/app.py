import tkinter as tk
from tkinter import ttk
from base_app import MatrixCalculatorApp as BaseApp
from mediator import CalculatorMediator


class MatrixCalculatorApp(BaseApp):
    def __init__(self, root):
        super().__init__(root)
        root.title("Лабораторная 9 · Матричный калькулятор · Вариант 6")
        root.geometry("1080x850")
        self.extra = ttk.Frame(root, padding=(12, 4, 12, 10))
        self.extra.pack(fill="x", side="bottom", before=root.winfo_children()[0])
        self.mediator = CalculatorMediator(self)
        self.session_status = tk.StringVar(value="Сеанс не сохранён")
        ttk.Button(self.extra, text="Сохранить сеанс", command=lambda: self.session_action("save_session")).pack(side="left")
        ttk.Button(self.extra, text="Восстановить сеанс", command=lambda: self.session_action("restore_session")).pack(side="left", padx=8)
        ttk.Label(self.extra, textvariable=self.session_status).pack(side="left")
        self.operation.bind("<<ComboboxSelected>>", lambda e: self.mediator.notify("operation_changed"))
        self.mediator.notify("operation_changed")

    def session_action(self, event):
        try:
            self.mediator.notify(event)
        except ValueError as error:
            self.error(error)



if __name__ == "__main__":
    root = tk.Tk()
    MatrixCalculatorApp(root)
    root.mainloop()
