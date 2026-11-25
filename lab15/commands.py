from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass


class ResultStore:
    def __init__(self):
        self.result = None

    def set_result(self, matrix):
        self.result = None if matrix is None else matrix.clone()


class CalculateCommand(Command):
    def __init__(self, facade, store, a, b, operation, scalar=""):
        self.facade = facade
        self.store = store
        self.request = (a, b, operation, scalar)
        self.previous = None

    def execute(self):
        result = self.facade.calculate(*self.request)
        old = self.store.result
        self.previous = None if old is None else old.clone()
        self.store.set_result(result)

    def undo(self):
        self.store.set_result(self.previous)


class CommandHistory:
    def __init__(self):
        self.commands = []

    def execute(self, command):
        command.execute()
        self.commands.append(command)

    def undo(self):
        if not self.commands:
            return False
        self.commands[-1].undo()
        self.commands.pop()
        return True
