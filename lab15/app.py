import sqlite3
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from journal_model import EventCalculatorModel
from presenter import CalculatorPresenter
from view import CalculatorView
from repository import SqliteSessionRepository


def create_app(root, data_dir=None):
    directory = Path(data_dir) if data_dir is not None else Path(__file__).parent
    model = EventCalculatorModel(directory / "events.jsonl")
    model.repository = SqliteSessionRepository(directory / "sessions.db")
    view = CalculatorView(root)
    presenter = CalculatorPresenter(model, view)
    view.presenter = presenter
    presenter.start()
    presenter.enable_background()
    return view


if __name__ == "__main__":
    root = tk.Tk()
    try:
        create_app(root)
    except (OSError, ValueError, sqlite3.Error) as error:
        messagebox.showerror("Ошибка запуска", str(error), parent=root)
        root.destroy()
    else:
        root.mainloop()
