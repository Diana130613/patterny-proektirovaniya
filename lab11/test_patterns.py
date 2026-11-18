
import unittest
import importlib.util
import tkinter as tk
from unittest.mock import patch
from matrix import Matrix
from facade import CalculatorFacade
from validation import CalculationRequest, validation_chain

HAS_SESSION = importlib.util.find_spec('memento') is not None
HAS_EVENTS = importlib.util.find_spec('events') is not None
HAS_STRATEGY = importlib.util.find_spec('algorithms') is not None
HAS_MVP = importlib.util.find_spec('presenter') is not None


class ChainTests(unittest.TestCase):
    def test_all_operations(self):
        facade = CalculatorFacade()
        expected = {'A + B': [[6,8],[10,12]], 'A - B': [[-4,-4],[-4,-4]],
                    'A × B': [[19,22],[43,50]], 'A × число': [[2,4],[6,8]],
                    '(A + B) × A': [[30,44],[46,68]]}
        for operation, data in expected.items():
            with self.subTest(operation=operation):
                self.assertEqual(facade.calculate('1 2\n3 4', '5 6\n7 8', operation, '2').data, data)

    def test_stops_at_first_error(self):
        request = CalculationRequest('x', '', 'A + B')
        with self.assertRaises(ValueError):
            validation_chain().handle(request)
        self.assertEqual(request.checks, ['OperationHandler'])

    def test_scalar_ignores_unused_b(self):
        self.assertEqual(CalculatorFacade().calculate('1,5', 'x', 'A × число', '2').data, [[3]])

    def test_invalid_inputs(self):
        cases = [('', '1', 'A + B', ''), ('1 2\n3', '1', 'A + B', ''),
                 ('nan', '1', 'A + B', ''), ('1', '1', 'A × число', 'inf'),
                 ('1 2', '1', 'A + B', ''), ('1 2', '1 2', 'A × B', ''),
                 ('1', '1', '?', ''), ('1 2', '1 2', '(A + B) × A', '')]
        for args in cases:
            with self.subTest(args=args), self.assertRaises(ValueError):
                CalculatorFacade().calculate(*args)

    def test_chain_passes_to_extension(self):
        from validation import Handler
        class Audit(Handler):
            def check(self, request):
                request.scalar_text = 'checked'
        chain = validation_chain()
        tail = chain
        while tail.next:
            tail = tail.next
        tail.set_next(Audit())
        request = chain.handle(CalculationRequest('1', '2', 'A + B'))
        self.assertEqual(request.scalar_text, 'checked')
        self.assertEqual(request.checks[-1], 'Audit')


@unittest.skipUnless(HAS_SESSION, 'starting at lab 9')
class SnapshotTests(unittest.TestCase):
    def test_isolation_and_restore(self):
        from memento import CalculatorSession, SnapshotHistory
        session = CalculatorSession()
        session.result = Matrix([[6,8],[10,12]])
        history = SnapshotHistory(session)
        history.save()
        session.result.data[0][0] = 99
        session.a_text = '99'
        history.restore()
        self.assertEqual(session.a_text, '1 2\n3 4')
        self.assertEqual(session.result.data[0][0], 6)
        session.result.data[0][0] = 88
        history.restore()
        self.assertEqual(session.result.data[0][0], 6)

    def test_missing_and_empty_snapshot(self):
        from memento import CalculatorSession, SnapshotHistory
        session = CalculatorSession()
        history = SnapshotHistory(session)
        with self.assertRaises(ValueError):
            history.restore()
        history.save()
        session.result = Matrix([[1]])
        history.restore()
        self.assertIsNone(session.result)


@unittest.skipUnless(HAS_EVENTS, 'starting at lab 10')
class EventTests(unittest.TestCase):
    def test_notifications_and_recovery(self):
        from events import CalculationContext
        context = CalculationContext()
        received, second = [], []
        context.subscribe(received.append)
        context.subscribe(second.append)
        context.calculate(lambda: Matrix([[6]]))
        def fail():
            raise ValueError('bad input')
        with self.assertRaises(ValueError):
            context.calculate(fail)
        self.assertEqual(context.result.data, [[6]])
        context.calculate(lambda: Matrix([[8]]))
        self.assertEqual([e.state for e in received],
            ['Вычисление', 'Готов', 'Вычисление', 'Ошибка', 'Вычисление', 'Готов'])
        self.assertEqual(len(second), 6)
        context.unsubscribe(second.append)
        context.calculate(lambda: Matrix([[1]]))
        self.assertEqual(len(second), 6)

    def test_busy_rejects_nested_request(self):
        from events import CalculationContext
        context = CalculationContext()
        def action():
            with self.assertRaisesRegex(ValueError, 'уже выполняется'):
                context.calculate(lambda: Matrix([[9]]))
            return Matrix([[1]])
        self.assertEqual(context.calculate(action).data, [[1]])


@unittest.skipUnless(HAS_STRATEGY, 'starting at lab 11')
class StrategyTests(unittest.TestCase):
    def test_rectangular_and_zero(self):
        from algorithms import StandardMultiplication, TransposedMultiplication
        a = Matrix([[1,2,3],[-1,0,2]])
        b = Matrix([[1,0],[0,1],[2,-1]])
        for strategy in (StandardMultiplication(), TransposedMultiplication()):
            self.assertEqual(strategy.multiply(a,b).data, [[7,-1],[3,-2]])
            self.assertEqual(strategy.multiply(Matrix([[0]]),Matrix([[8]])).data, [[0]])

    def test_template_order(self):
        from algorithms import OperationTemplate
        calls = []
        class Sample(OperationTemplate):
            def validate(self,a,b): calls.append('validate')
            def compute(self,a,b):
                calls.append('compute')
                return Matrix([[1]])
            def validate_result(self,result): calls.append('result')
        Sample().execute(None,None)
        self.assertEqual(calls, ['validate','compute','result'])


class GuiTests(unittest.TestCase):
    def test_workflow(self):
        root = tk.Tk()
        root.withdraw()
        try:
            if HAS_MVP:
                from app import create_app
                app = create_app(root)
                calculate, undo = app.presenter.calculate, app.presenter.undo
                get_result = lambda: app.presenter.model.store.result
                error_target = 'view.messagebox.showerror'
            else:
                from app import MatrixCalculatorApp
                app = MatrixCalculatorApp(root)
                calculate, undo = app.calculate, app.undo
                get_result = lambda: app.result
                error_target = 'base_app.messagebox.showerror'
            app.operation.set('A + B')
            calculate()
            self.assertEqual(get_result().data, [[6,8],[10,12]])
            app.operation.set('A - B')
            calculate()
            undo()
            self.assertEqual(get_result().data, [[6,8],[10,12]])
            app.a_text.delete('1.0', 'end')
            app.a_text.insert('1.0', 'x')
            with patch(error_target) as error:
                calculate()
                self.assertEqual(error.call_count, 1)
            self.assertEqual(get_result().data, [[6,8],[10,12]])
            app.a_text.delete('1.0', 'end')
            app.a_text.insert('1.0', '1 2\n3 4')
            if HAS_SESSION:
                if HAS_MVP:
                    app.presenter.save_session()
                else:
                    app.session_action('save_session')
                app.a_text.delete('1.0', 'end')
                app.a_text.insert('1.0', '99')
                if HAS_MVP:
                    app.presenter.restore_session()
                else:
                    app.session_action('restore_session')
                self.assertEqual(app.a_text.get('1.0', 'end-1c'), '1 2\n3 4')
                self.assertEqual(get_result().data, [[6,8],[10,12]])
                if not HAS_MVP:
                    app.operation.set('A × число')
                    app.mediator.notify('operation_changed')
                    self.assertEqual(str(app.scalar.cget('state')), 'normal')
            if HAS_STRATEGY:
                app.operation.set('A × B')
                app.algorithm.current(1)
                if HAS_MVP:
                    app.presenter.change_strategy(app.algorithm.get())
                else:
                    app.change_strategy()
                calculate()
                self.assertEqual(get_result().data, [[19,22],[43,50]])
            root.update_idletasks()
        finally:
            root.destroy()


if __name__ == '__main__':
    unittest.main(verbosity=2)
