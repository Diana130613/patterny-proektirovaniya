import tkinter as tk
from model import CalculatorModel
from presenter import CalculatorPresenter
from view import CalculatorView


def create_app(root):
    view = CalculatorView(root)
    presenter = CalculatorPresenter(CalculatorModel(), view)
    view.presenter = presenter
    presenter.start()
    return view


if __name__ == "__main__":
    root = tk.Tk()
    create_app(root)
    root.mainloop()
