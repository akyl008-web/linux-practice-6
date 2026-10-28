#!/usr/bin/env python3
"""ПР-6, вариант B, задание 3. Барьер на условной переменной: 4 потока, задача в три фазы.
Проверка: ни один поток не начинает фазу k+1, пока все не закончили фазу k."""
import random
import sys
import threading
import time

THREADS = 4
PHASES = 3


class Barrier:
    def __init__(self, n):
        self.n = n
        self.waiting = 0
        self.generation = 0  # номер «поколения»: позволяет использовать барьер повторно
        self.cond = threading.Condition()

    def wait(self):
        with self.cond:
            gen = self.generation
            self.waiting += 1
            if self.waiting == self.n:  # пришёл последний — открываем барьер
                self.generation += 1
                self.waiting = 0
                self.cond.notify_all()
            else:
                while gen == self.generation:  # while: защита от ложных пробуждений
                    self.cond.wait()


log = []
log_lock = threading.Lock()


def record(event, phase, k):
    with log_lock:
        log.append((event, phase, k))
        print(f"  поток {k}: {'начал' if event == 'start' else 'закончил'} фазу {phase}", flush=True)


def worker(k, barrier):
    for phase in range(1, PHASES + 1):
        record("start", phase, k)
        time.sleep(random.uniform(0.01, 0.1))  # «работа» разной длительности
        record("end", phase, k)
        barrier.wait()


def main():
    barrier = Barrier(THREADS)
    threads = [threading.Thread(target=worker, args=(k, barrier)) for k in range(THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # инвариант: все «закончил фазу p» стоят в журнале раньше любого «начал фазу p+1»
    ok = True
    for phase in range(1, PHASES):
        last_end = max(i for i, (e, p, _) in enumerate(log) if e == "end" and p == phase)
        first_next = min(i for i, (e, p, _) in enumerate(log) if e == "start" and p == phase + 1)
        good = last_end < first_next
        ok = ok and good
        print(f"Фаза {phase} → {phase + 1}: последнее завершение — запись #{last_end}, "
              f"первое начало следующей — запись #{first_next}: {'OK' if good else 'НАРУШЕНИЕ'}")
    print(f"Результат: {'OK' if ok else 'ОШИБКА'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()