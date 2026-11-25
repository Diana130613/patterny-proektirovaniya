from concurrent.futures import ThreadPoolExecutor


class BackgroundCalculator:
    def __init__(self, calculator):
        self.calculator = calculator
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.pending = None

    def submit(self, request):
        if self.pending is not None and not self.pending.done():
            raise ValueError("Вычисление уже выполняется.")
        self.pending = self.pool.submit(self.calculator.calculate, *request)
        return self.pending

    def close(self):
        self.pool.shutdown(wait=False, cancel_futures=True)
