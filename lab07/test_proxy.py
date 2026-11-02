import unittest

from calculator import CalculationService
from facade import CalculatorFacade
from matrix import Matrix
from proxy import CachedCalculator


class CountingCalculator(CalculationService):
    def __init__(self):
        self.calls = 0

    def calculate(self, *args):
        self.calls += 1
        return super().calculate(*args)


class ProxyTests(unittest.TestCase):
    def setUp(self):
        self.service = CountingCalculator()
        self.proxy = CachedCalculator(self.service, capacity=2)
        self.facade = CalculatorFacade(self.proxy)

    def calc(self, a="1 2", b="3 4", op="A + B", scalar=""):
        return self.facade.calculate(a, b, op, scalar)

    def test_repeat_calls_service_once(self):
        first = self.calc()
        self.assertFalse(self.proxy.last_hit)
        second = self.calc("1.0 2,0", "3.0 4.0")
        self.assertTrue(self.proxy.last_hit)
        self.assertEqual(first.data, second.data)
        self.assertEqual(self.service.calls, 1)

    def test_cache_is_protected_from_mutation(self):
        self.calc().data[0][0] = 99
        cached = self.calc()
        self.assertEqual(cached.data, [[4, 6]])
        cached.data[0][0] = 88
        self.assertEqual(self.calc().data, [[4, 6]])

    def test_key_includes_values_operation_scalar_and_shape(self):
        for a, b, op, scalar in [
            ("1", "2", "A + B", ""),
            ("2", "2", "A + B", ""),
            ("2", "2", "A - B", ""),
            ("2", "", "A × число", "2"),
            ("2", "", "A × число", "3"),
            ("1 2", "3 4", "A + B", ""),
            ("1\n2", "3\n4", "A + B", "")]:
            self.calc(a, b, op, scalar)
            self.assertFalse(self.proxy.last_hit)
        self.assertEqual(self.service.calls, 7)

    def test_input_mutation_changes_key(self):
        a, b = Matrix([[1]]), Matrix([[2]])
        self.proxy.calculate(a, b, "A + B")
        a.data[0][0] = 3
        self.assertEqual(self.proxy.calculate(a, b, "A + B").data, [[5]])
        self.assertEqual(self.service.calls, 2)

    def test_lru_eviction_and_clear(self):
        self.calc("1", "1")
        self.calc("2", "2")
        self.calc("1", "1")
        self.calc("3", "3")
        self.calc("2", "2")
        self.assertFalse(self.proxy.last_hit)
        self.assertEqual(self.service.calls, 4)
        self.assertEqual(len(self.proxy.cache), 2)
        self.proxy.clear()
        self.assertFalse(self.proxy.cache)
        self.calc("2", "2")
        self.assertEqual(self.service.calls, 5)

    def test_error_is_not_cached(self):
        for _ in range(2):
            with self.assertRaises(ValueError):
                self.calc("1 2", "1")
        self.assertEqual(self.service.calls, 2)
        self.assertFalse(self.proxy.cache)
        self.assertFalse(self.proxy.last_hit)

    def test_capacity_validation(self):
        with self.assertRaises(ValueError):
            CachedCalculator(capacity=0)


if __name__ == "__main__":
    unittest.main()
