#!/usr/bin/env python3
"""ПР-6, вариант B, задание 1а. Ограниченный буфер на двух семафорах и мьютексе."""
import sys
import threading

from ring import RingBuffer, run_test


class SemBuffer:
    def __init__(self, size, violations):
        self.ring = RingBuffer(size, violations)
        self.empty = threading.Semaphore(size)  # число свободных мест
        self.full = threading.Semaphore(0)      # число занятых мест
        self.mutex = threading.Lock()           # защищает сам буфер (head, tail, count)

    def put(self, item):
        self.empty.acquire()   # ждём свободное место
        with self.mutex:
            self.ring.put(item)
        self.full.release()    # стало на один элемент больше

    def get(self):
        self.full.acquire()    # ждём элемент
        with self.mutex:
            item = self.ring.get()
        self.empty.release()   # освободилось место
        return item


if __name__ == "__main__":
    results = [run_test(SemBuffer, f"Семафоры + мьютекс, прогон {i}") for i in range(1, 4)]
    sys.exit(0 if all(results) else 1)