from algorithms import StrategyCalculator, StandardMultiplication, TransposedMultiplication
from proxy import CachedCalculator
from facade import CalculatorFacade
from commands import ResultStore, CommandHistory, CalculateCommand
from memento import CalculatorSession, SnapshotHistory
from events import CalculationContext
from settings import AppSettings


class CalculatorModel:
    def __init__(self):
        self.engine = StrategyCalculator()
        self.calculator = CachedCalculator(self.engine)
        self.facade = CalculatorFacade(self.calculator)
        self.store = ResultStore()
        self.history = CommandHistory()
        self.session = CalculatorSession()
        self.snapshots = SnapshotHistory(self.session)
        self.context = CalculationContext()
        self.settings = AppSettings()
        self.prototype = None

    def calculate(self, request):
        command = CalculateCommand(self.facade, self.store, *request)
        def action():
            self.history.execute(command)
            return self.store.result
        return self.context.calculate(action)

    def set_strategy(self, name):
        self.engine.strategy = (StandardMultiplication() if name == "Обычный"
                                else TransposedMultiplication())
        self.calculator.clear()

    def save_session(self, request):
        session = self.session
        session.a_text, session.b_text, session.operation, session.scalar_text = request
        session.result = self.store.result
        self.snapshots.save()

    def restore_session(self):
        self.snapshots.restore()
        self.store.set_result(self.session.result)
        self.history.commands.clear()
        return (self.session.a_text, self.session.b_text,
                self.session.operation, self.session.scalar_text)
