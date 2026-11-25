from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass(frozen=True)
class CalculationEvent:
    state: str
    message: str
    result: object = None


class Observable:
    def __init__(self):
        self.observers = []

    def subscribe(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def unsubscribe(self, observer):
        self.observers.remove(observer)

    def publish(self, event):
        for observer in tuple(self.observers):
            observer(event)


class CalculationState(ABC):
    @abstractmethod
    def calculate(self, context, action):
        pass


class ReadyState(CalculationState):
    name = "Готов"

    def calculate(self, context, action):
        context.transition(BusyState(), "Выполняется вычисление")
        try:
            result = action()
        except (ValueError, OverflowError) as error:
            context.transition(ErrorState(), str(error))
            raise
        context.result = result.clone()
        context.transition(ReadyState(), "Вычисление завершено")
        return result


class BusyState(CalculationState):
    name = "Вычисление"

    def calculate(self, context, action):
        raise ValueError("Вычисление уже выполняется.")


class ErrorState(ReadyState):
    name = "Ошибка"


class CalculationContext(Observable):
    def __init__(self):
        super().__init__()
        self.state = ReadyState()
        self.result = None

    def transition(self, state, message):
        self.state = state
        result = None if self.result is None else self.result.clone()
        self.publish(CalculationEvent(state.name, message, result))

    def calculate(self, action):
        return self.state.calculate(self, action)
