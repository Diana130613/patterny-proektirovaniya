from matrix import Matrix


class CalculatorProjection:
    def __init__(self):
        self.request = ("1 2\n3 4", "5 6\n7 8", "A + B", "2")
        self.result = None
        self.previous_results = []
        self.count = 0

    def apply(self, event):
        kind = event.get("kind")
        payload = event.get("payload")
        if not isinstance(payload, dict):
            raise ValueError("Неверные данные события.")
        if kind in ("calculated", "session_restored"):
            request = payload.get("request")
            if (not isinstance(request, (list, tuple)) or len(request) != 4
                    or any(not isinstance(value, str) for value in request)):
                raise ValueError("Неверный запрос в событии.")
            data = payload.get("result")
            result = None if data is None else Matrix(data)
            if kind == "calculated":
                if result is None:
                    raise ValueError("Вычисление должно содержать результат.")
                self.previous_results.append(
                    None if self.result is None else self.result.clone())
            else:
                self.previous_results.clear()
            self.request = tuple(request)
            self.result = result
        elif kind == "undone":
            if not self.previous_results:
                raise ValueError("В журнале нет вычисления для отмены.")
            self.result = self.previous_results.pop()
        else:
            raise ValueError("Неизвестный тип события.")
        self.count += 1
