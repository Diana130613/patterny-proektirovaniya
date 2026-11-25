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
        self.view.update_saved_sessions(self.model.repository.list_all())

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

    def save_database(self):
        try:
            self.model.save_session(self.view.get_request())
            key = self.model.repository.save(
                self.view.session_name.get(), self.model.snapshots.snapshot)
            self.view.update_saved_sessions(self.model.repository.list_all(), key)
            self.view.show_status("Сеанс сохранён в базе данных")
        except (OSError, ValueError, sqlite3.Error) as error:
            self.view.show_error(str(error))

    def load_database(self):
        try:
            key = self.view.selected_session_id()
            self.model.snapshots.snapshot = self.model.repository.get(key)
            self.restore_session()
            self.view.show_status("Сеанс загружен из базы данных")
        except (OSError, ValueError, sqlite3.Error) as error:
            self.view.show_error(str(error))

    def delete_database(self):
        try:
            key = self.view.selected_session_id()
            self.model.repository.delete(key)
            self.view.update_saved_sessions(self.model.repository.list_all())
            self.view.show_status("Сеанс удалён из базы данных")
        except (OSError, ValueError, sqlite3.Error) as error:
            self.view.show_error(str(error))
