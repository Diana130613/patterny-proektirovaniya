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

    def calculate_synchronously(self):
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

    def enable_background(self):
        from background import BackgroundCalculator
        self.worker = BackgroundCalculator(self.model.facade)
        self.pending = None
        self.closed = False
        self.poll_id = None
        self.ticks = 0
        self.view.root.protocol("WM_DELETE_WINDOW", self.close)

    def calculate(self):
        from events import BusyState
        if self.pending is not None:
            return
        request = tuple(self.view.get_request())
        try:
            self.pending = self.worker.submit(request)
        except (ValueError, RuntimeError) as error:
            self.view.show_error(str(error))
            return
        self.request = request
        self.ticks = 0
        self.model.context.transition(BusyState(), "Фоновое вычисление")
        self.view.set_busy(True)
        self.poll_id = self.view.root.after(50, self.poll_result)

    def poll_result(self):
        from events import ReadyState, ErrorState
        if self.closed:
            return
        self.ticks += 1
        self.view.background_status.set(
            f"Интерфейс отвечает; проверок готовности: {self.ticks}")
        if not self.pending.done():
            self.poll_id = self.view.root.after(50, self.poll_result)
            return
        try:
            result = self.pending.result()
            self.model.commit_result(self.request, result)
        except (ValueError, OverflowError, OSError) as error:
            self.model.context.transition(ErrorState(), str(error))
            self.view.set_busy(False)
            self.view.background_status.set("Фоновая задача завершилась ошибкой")
            self.view.show_error(str(error))
        else:
            self.model.context.transition(ReadyState(), "Фоновое вычисление завершено")
            self.view.set_busy(False)
            self.refresh_result()
            self.view.select_result()
            self.show_portrait()
            self.view.show_journal_count(self.model.projection.count)
            self.view.background_status.set("Результат Future получен")
        finally:
            self.pending = None
            self.poll_id = None

    def close(self):
        self.closed = True
        if self.poll_id is not None:
            self.view.root.after_cancel(self.poll_id)
        self.worker.close()
        self.view.root.destroy()
