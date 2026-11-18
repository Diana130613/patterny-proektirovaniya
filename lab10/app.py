import tkinter as tk
from tkinter import ttk
from base_app import MatrixCalculatorApp as BaseApp
from lab9_app import MatrixCalculatorApp as SessionApp
from events import CalculationContext



class MatrixCalculatorApp(SessionApp):
    def __init__(self, root):
        super().__init__(root)
        root.title("Лабораторная 10 · Матричный калькулятор · Вариант 6")
        root.geometry("1080x850")
        self.extra = ttk.Frame(root, padding=(12, 4, 12, 10))
        self.extra.pack(fill="x", side="bottom", before=root.winfo_children()[0])
        self.context = CalculationContext()
        self.event_status = tk.StringVar(value="Готов")
        self.event_log = tk.StringVar(value="Уведомлений: 0")
        self.event_count = 0
        self.context.subscribe(self.show_state)
        self.context.subscribe(self.count_event)
        ttk.Label(self.extra, textvariable=self.event_status).pack(anchor="w")
        ttk.Label(self.extra, textvariable=self.event_log).pack(anchor="w")

    def undo(self):
        super().undo()
        result = self.store.result
        self.context.result = None if result is None else result.clone()

    def session_action(self, event):
        super().session_action(event)
        result = self.store.result
        self.context.result = None if result is None else result.clone()

    def show_state(self, event):
        self.event_status.set(event.state + ": " + event.message)
        self.root.update_idletasks()

    def count_event(self, event):
        self.event_count += 1
        self.event_log.set(f"Уведомлений: {self.event_count}; последнее: {event.state}")

    def calculate(self):
        def action():
            from commands import CalculateCommand
            command = CalculateCommand(self.facade, self.store,
                self.a_text.get("1.0", "end"), self.b_text.get("1.0", "end"),
                self.operation.get(), self.scalar.get())
            self.history.execute(command)
            return self.store.result
        try:
            self.result = self.context.calculate(action)
            self.cache_status.set("Результат из кэша" if self.calculator.last_hit else "Результат вычислен")
            self.update_result_text()
            self.portrait_source.set("Результат")
            self.show_portrait()
        except (ValueError, OverflowError) as error:
            self.error(error)



if __name__ == "__main__":
    root = tk.Tk()
    MatrixCalculatorApp(root)
    root.mainloop()
