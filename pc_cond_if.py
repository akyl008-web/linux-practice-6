#!/usr/bin/env python3
"""ПР-6, вариант B, задание 4. ОШИБОЧНАЯ версия: if вместо while вокруг wait.
После пробуждения условие не проверяется заново — буфер переполняется / читается пустым."""
import sys
import threading

from ring import RingBuffer, run_test

RUNS = 5


class CondBufferIf:
    def __init__(self, size, violations):
        self.ring = RingBuffer(size, violations)
        self.cond = threading.Condition()

    def put(self, item):
        with self.cond:
            if self.ring.count == self.ring.size:  # ОШИБКА: должно быть while
                self.cond.wait()
            self.ring.put(item)
            self.cond.notify_all()

    def get(self):
        with self.cond:
            if self.ring.count == 0:  # ОШИБКА: должно быть while
                self.cond.wait()
            item = self.ring.get()
            self.cond.notify_all()
            return item


if __name__ == "__main__":
    results = [run_test(CondBufferIf, f"if вместо while, прогон {i}") for i in range(1, RUNS + 1)]
    print(f"\nОшибки в {results.count(False)} из {RUNS} прогонов")
    sys.exit(0 if all(results) else 1)