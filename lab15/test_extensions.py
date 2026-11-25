import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import threading
import time
import importlib.util
import tkinter as tk
from journal_model import EventCalculatorModel
from event_store import EventStore
from matrix import Matrix

REQUEST=('1 2\n3 4','5 6\n7 8','A + B','2')
HAS_REPO=importlib.util.find_spec('repository') is not None
HAS_BACKGROUND=importlib.util.find_spec('background') is not None


class JournalTests(unittest.TestCase):
    def test_replay_and_undo_survive_restart(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'events.jsonl'
            model=EventCalculatorModel(path)
            model.calculate(REQUEST)
            model.calculate((*REQUEST[:2],'A - B','2'))
            restored=EventCalculatorModel(path)
            self.assertEqual(restored.store.result.data,[[-4,-4],[-4,-4]])
            self.assertTrue(restored.history.undo())
            self.assertEqual(restored.store.result.data,[[6,8],[10,12]])
            again=EventCalculatorModel(path)
            self.assertEqual(again.store.result.data,[[6,8],[10,12]])
            self.assertTrue(again.history.undo())
            self.assertIsNone(again.store.result)
            self.assertFalse(again.history.undo())
            self.assertEqual(len(EventStore(path).read_all()),4)

    def test_invalid_calculation_and_write_failure(self):
        with TemporaryDirectory() as directory:
            model=EventCalculatorModel(Path(directory)/'events.jsonl')
            model.calculate(REQUEST)
            with self.assertRaises(ValueError):
                model.calculate(('x',*REQUEST[1:]))
            self.assertEqual(model.projection.count,1)
            self.assertEqual(model.context.state.name,'Ошибка')
            with patch.object(model.events,'append',side_effect=OSError('read only')):
                with self.assertRaises(OSError):
                    model.calculate((*REQUEST[:2],'A - B','2'))
            self.assertEqual(model.store.result.data,[[6,8],[10,12]])
            self.assertEqual(model.projection.count,1)

    def test_session_restore_is_an_event(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'events.jsonl'
            model=EventCalculatorModel(path)
            model.calculate(REQUEST)
            model.save_session(REQUEST)
            model.calculate((*REQUEST[:2],'A × B','2'))
            model.restore_session()
            again=EventCalculatorModel(path)
            self.assertEqual(again.projection.request,REQUEST)
            self.assertEqual(again.store.result.data,[[6,8],[10,12]])
            self.assertFalse(again.history.undo())

    def test_corrupt_log_is_reported(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'events.jsonl'
            path.write_text('{unfinished',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'строке 1'):
                EventCalculatorModel(path)


@unittest.skipUnless(HAS_REPO,'Repository starts at lab 14')
class RepositoryTests(unittest.TestCase):
    def test_database_restart_and_delete(self):
        from repository import SqliteSessionRepository
        from memento import CalculatorSession
        with TemporaryDirectory() as directory:
            path=Path(directory)/'sessions.db'
            session=CalculatorSession()
            session.result=Matrix([[1,-2],[0,3]])
            first=SqliteSessionRepository(path)
            name="Расчёт '); DROP TABLE sessions;--"
            key=first.save(name,session.save())
            second=SqliteSessionRepository(path)
            self.assertEqual(second.list_all(),[(key,name)])
            snapshot=second.get(key)
            self.assertEqual(snapshot.result,((1.,-2.),(0.,3.)))
            self.assertTrue(second.delete(key))
            self.assertFalse(second.delete(key))
            with self.assertRaises(ValueError):second.get(key)
            with self.assertRaises(ValueError):second.save(' ',snapshot)


@unittest.skipUnless(HAS_BACKGROUND,'Thread pool starts at lab 15')
class BackgroundTests(unittest.TestCase):
    def test_worker_thread_and_duplicate_submission(self):
        from background import BackgroundCalculator
        started=threading.Event();release=threading.Event();ids=[]
        class Calculator:
            def calculate(self,*request):
                ids.append(threading.get_ident());started.set()
                release.wait(3)
                return Matrix([[7]])
        worker=BackgroundCalculator(Calculator())
        try:
            future=worker.submit(REQUEST)
            self.assertTrue(started.wait(2))
            self.assertNotEqual(ids[0],threading.get_ident())
            with self.assertRaises(ValueError):worker.submit(REQUEST)
            release.set()
            self.assertEqual(future.result(timeout=3).data,[[7]])
        finally:
            release.set();worker.close()


class GuiTests(unittest.TestCase):
    def test_actions_and_background_completion(self):
        from app import create_app
        with TemporaryDirectory() as directory:
            root=tk.Tk();root.withdraw()
            app=create_app(root,directory)
            presenter=app.presenter
            try:
                if HAS_BACKGROUND:
                    started=threading.Event();release=threading.Event()
                    original=presenter.model.facade.calculate
                    def delayed(*args):
                        started.set();release.wait(3)
                        return original(*args)
                    with patch.object(presenter.model.facade,'calculate',side_effect=delayed):
                        presenter.calculate()
                        self.assertTrue(started.wait(2))
                        for _ in range(5):root.update();time.sleep(.025)
                        self.assertGreater(presenter.ticks,0)
                        self.assertIsNotNone(presenter.pending)
                        self.assertEqual(str(app.operation.cget('state')),'disabled')
                        release.set()
                        deadline=time.monotonic()+4
                        while presenter.pending is not None and time.monotonic()<deadline:
                            root.update();time.sleep(.01)
                        self.assertIsNone(presenter.pending)
                else:presenter.calculate()
                self.assertEqual(presenter.model.store.result.data,[[6,8],[10,12]])
                presenter.undo()
                self.assertIsNone(presenter.model.store.result)
                presenter.replay()
                self.assertIsNone(presenter.model.store.result)
                if HAS_REPO:
                    presenter.save_database()
                    self.assertEqual(len(presenter.model.repository.list_all()),1)
                    app.a_text.delete('1.0','end');app.a_text.insert('1.0','9')
                    presenter.load_database()
                    self.assertEqual(app.a_text.get('1.0','end-1c'),'1 2\n3 4')
                if HAS_BACKGROUND:
                    app.a_text.delete('1.0','end');app.a_text.insert('1.0','x')
                    with patch.object(app,'show_error') as error:
                        presenter.calculate()
                        deadline=time.monotonic()+4
                        while presenter.pending is not None and time.monotonic()<deadline:
                            root.update();time.sleep(.01)
                        self.assertEqual(error.call_count,1)
                    self.assertIsNone(presenter.model.store.result)
                    self.assertEqual(str(app.operation.cget('state')),'readonly')
            finally:
                if HAS_BACKGROUND:presenter.close()
                else:root.destroy()


if __name__=='__main__':unittest.main(verbosity=2)
