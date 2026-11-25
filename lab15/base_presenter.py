from matrix import Matrix
from iterators import sign_counts
from formatters import PlainFormatter, RowNumbersFormatter, SizeFormatter


class BaseCalculatorPresenter:
    def __init__(self, model, view):
        self.model, self.view = model, view
        self.event_count = 0
        model.context.subscribe(self.on_event)

    def start(self):
        try:
            self.model.settings.load()
        except (ValueError, OSError, TypeError) as error:
            self.view.show_error(str(error))
        self.view.apply_settings(self.model.settings.values)
        self.operation_changed()
        self.show_portrait()

    def on_event(self, event):
        self.event_count += 1
        self.view.show_status(f"{event.state}: {event.message}; уведомлений: {self.event_count}")

    def calculate(self):
        try:
            self.model.calculate(self.view.get_request())
            self.refresh_result()
            self.view.select_result()
            self.show_portrait()
        except (ValueError, OverflowError) as error:
            self.view.show_error(str(error))

    def refresh_result(self):
        result = self.model.store.result
        if result is None:
            self.view.show_result("", "Нет результата")
            return
        formatter = PlainFormatter(self.model.settings.values["decimal_places"])
        rows, size = self.view.get_format_options()
        if rows:
            formatter = RowNumbersFormatter(formatter)
        if size:
            formatter = SizeFormatter(formatter)
        p, n, z = sign_counts(result)
        self.view.show_result(formatter.format(result),
            f"Положительных: {p}; отрицательных: {n}; нулей: {z}")

    def undo(self):
        if self.model.history.undo():
            result = self.model.store.result
            self.model.context.result = None if result is None else result.clone()
            self.refresh_result()
            self.view.select_result()
            self.show_portrait()
            self.view.show_status("Вычисление отменено")
        else:
            self.view.show_status("Нет вычислений для отмены")

    def save_session(self):
        self.model.save_session(self.view.get_request())
        self.view.show_status("Сеанс сохранён")

    def restore_session(self):
        try:
            self.view.set_request(self.model.restore_session())
            result = self.model.store.result
            self.model.context.result = None if result is None else result.clone()
            self.operation_changed()
            self.refresh_result()
            self.view.select_result()
            self.show_portrait()
            self.view.show_status("Сеанс восстановлен")
        except ValueError as error:
            self.view.show_error(str(error))

    def operation_changed(self):
        self.view.enable_scalar(self.view.get_request()[2] == "A × число")

    def change_strategy(self, name):
        self.model.set_strategy(name)
        self.view.show_status("Алгоритм изменён, кэш очищен")

    def clear_cache(self):
        self.model.calculator.clear()
        self.view.show_status("Кэш очищен")

    def show_portrait(self):
        source, mode = self.view.get_portrait_options()
        try:
            matrix = (self.model.store.result if source == "Результат" else
                      Matrix.from_text(self.view.get_request()[0 if source == "A" else 1]))
            self.view.draw_portrait(matrix, mode, self.model.settings.values)
        except ValueError as error:
            self.view.show_error(str(error))

    def load(self, field, path):
        try:
            matrix = self.model.facade.load(path)
            self.view.set_matrix_text(field, matrix.to_text())
        except (OSError, ValueError) as error:
            self.view.show_error(str(error))

    def save(self, path):
        if self.model.store.result is None:
            self.view.show_error("Сначала выполните вычисление.")
            return
        try:
            self.model.facade.save(self.model.store.result, path)
        except OSError as error:
            self.view.show_error(str(error))

    def remember(self):
        try:
            self.model.prototype = Matrix.from_text(self.view.get_request()[0]).clone()
            self.view.show_status("Образец A сохранён")
        except ValueError as error:
            self.view.show_error(str(error))

    def restore_prototype(self):
        if self.model.prototype is None:
            self.view.show_error("Сначала запомните матрицу A как образец.")
        else:
            self.view.set_matrix_text("B", self.model.prototype.clone().to_text())

    def save_settings(self, values):
        try:
            self.model.settings.save(values)
            self.view.apply_settings(self.model.settings.values)
            self.refresh_result()
            self.show_portrait()
            return True
        except (OSError, ValueError) as error:
            self.view.show_error(str(error))
            return False
