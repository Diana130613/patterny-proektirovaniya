import sqlite3
from base_presenter import BaseCalculatorPresenter


class CalculatorPresenter(BaseCalculatorPresenter):
    def start(self):
        super().start()
        if self.model.projection.count:
            self.view.set_request(self.model.projection.request)
            self.operation_changed()
            self.refresh_result()
            self.view.select_result()
            self.show_portrait()
            self.view.show_status("Сеанс восстановлен из журнала")
        self.view.show_journal_count(self.model.projection.count)

    def calculate(self):
        try:
            super().calculate()
        except OSError as error:
            self.view.show_error(str(error))
        self.view.show_journal_count(self.model.projection.count)

    def undo(self):
        try:
            super().undo()
        except (OSError, ValueError) as error:
            self.view.show_error(str(error))
        self.view.show_journal_count(self.model.projection.count)

    def restore_session(self):
        try:
            super().restore_session()
        except OSError as error:
            self.view.show_error(str(error))
        self.view.show_journal_count(self.model.projection.count)

    def replay(self):
        try:
            self.view.set_request(self.model.replay())
            self.operation_changed()
            self.refresh_result()
            self.view.select_result()
            self.show_portrait()
            self.view.show_journal_count(self.model.projection.count)
            self.view.show_status("Сеанс восстановлен из журнала")
        except (OSError, ValueError) as error:
            self.view.show_error(str(error))

    def show_history(self):
        try:
            self.view.show_events(self.model.events.read_all())
        except (OSError, ValueError) as error:
            self.view.show_error(str(error))
