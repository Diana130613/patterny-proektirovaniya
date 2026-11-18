import tkinter as tk
from tkinter import ttk
from base_app import MatrixCalculatorApp as BaseApp



class MatrixCalculatorApp(BaseApp):
    def __init__(self, root):
        super().__init__(root)
        root.title("Лабораторная 8 · Матричный калькулятор · Вариант 6")
        root.geometry("1080x850")
        self.extra = ttk.Frame(root, padding=(12, 4, 12, 10))
        self.extra.pack(fill="x", side="bottom", before=root.winfo_children()[0])
        ttk.Label(self.extra, text="Проверки: операция → ввод матриц → число → размеры").pack(anchor="w")



if __name__ == "__main__":
    root = tk.Tk()
    MatrixCalculatorApp(root)
    root.mainloop()
