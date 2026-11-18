from memento import CalculatorSession, SnapshotHistory


class CalculatorMediator:
    def __init__(self, view):
        self.view = view
        self.session = CalculatorSession()
        self.history = SnapshotHistory(self.session)

    def notify(self, event):
        if event == "operation_changed":
            enabled = self.view.operation.get() == "A × число"
            self.view.scalar.configure(state="normal" if enabled else "disabled")
        elif event == "save_session":
            session = self.session
            session.a_text = self.view.a_text.get("1.0", "end-1c")
            session.b_text = self.view.b_text.get("1.0", "end-1c")
            session.operation = self.view.operation.get()
            session.scalar_text = self.view.scalar.get()
            session.result = self.view.result
            self.history.save()
            self.view.session_status.set("Сеанс сохранён")
        elif event == "restore_session":
            self.history.restore()
            session = self.session
            for widget, text in ((self.view.a_text, session.a_text),
                                 (self.view.b_text, session.b_text)):
                widget.delete("1.0", "end")
                widget.insert("1.0", text)
            self.view.operation.set(session.operation)
            self.view.scalar.configure(state="normal")
            self.view.scalar.delete(0, "end")
            self.view.scalar.insert(0, session.scalar_text)
            self.view.store.set_result(session.result)
            self.view.result = self.view.store.result
            self.view.history.commands.clear()
            self.view.update_result_text()
            if self.view.result is None:
                self.view.canvas.delete("all")
            else:
                self.view.portrait_source.set("Результат")
                self.view.show_portrait()
            self.notify("operation_changed")
            self.view.session_status.set("Сеанс восстановлен")
