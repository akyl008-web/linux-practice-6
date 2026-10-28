#!/usr/bin/env python3
"""ПР-6, вариант B, задание 1б. Ограниченный буфер на мьютексе и условной переменной."""
import sys
import threading

from ring import RingBuffer, run_test


class CondBuffer:
    def __init__(self, size, violations):
        self.ring = RingBuffer(size, violations)
        self.cond = threading.Condition()  # Condition содержит мьютекс внутри

    def put(self, item):
        with self.cond:
            while self.ring.count == self.ring.size:  # пока буфер полон — ждём
                self.cond.wait()
            self.ring.put(item)
            self.cond.notify_all()  # одна переменная на «полон» и «пуст» → будим всех

    def get(self):
        with self.cond:
            while self.ring.count == 0:  # пока буфер пуст — ждём
                self.cond.wait()
            item = self.ring.get()
            self.cond.notify_all()
            return item


if __name__ == "__main__":
    results = [run_test(CondBuffer, f"Мьютекс + условная переменная (while), прогон {i}") for i in range(1, 4)]
    sys.exit(0 if all(results) else 1)