#!/usr/bin/env python3
"""ПР-6, вариант B. Общая часть: кольцевой буфер и тест «производитель–потребитель».
3 производителя, 2 потребителя, 1000 элементов, буфер на 5 элементов."""
import sys
import threading

SIZE = 5
N_ITEMS = 1000
PRODUCERS = 3
CONSUMERS = 2
STOP = -1     # «ядовитая пилюля»: сигнал потребителю завершиться
TIMEOUT = 10  # секунд; если дольше — считаем, что программа зависла


class RingBuffer:
    """Кольцевой буфер БЕЗ синхронизации. Проверяет инварианты и записывает нарушения.
    Вызывается только из-под блокировки обёрток (SemBuffer, CondBuffer)."""

    def __init__(self, size, violations):
        self.slots = [None] * size
        self.size = size
        self.head = self.tail = self.count = 0
        self.violations = violations

    def put(self, item):
        if self.count >= self.size:
            self.violations.append(f"переполнение: в буфере уже {self.count}, кладём {item}")
        self.slots[self.tail] = item
        self.tail = (self.tail + 1) % self.size
        self.count += 1

    def get(self):
        if self.count <= 0:
            self.violations.append(f"чтение из пустого буфера: count = {self.count}")
        item = self.slots[self.head]
        self.slots[self.head] = None
        self.head = (self.head + 1) % self.size
        self.count -= 1
        return item


def run_test(make_buffer, title):
    """3 производителя и 2 потребителя. Проверяет: каждый элемент потреблён ровно один раз,
    буфер не переполнялся и не читался пустым. Возвращает True, если нарушений нет."""
    sys.setswitchinterval(1e-5)  # частые переключения потоков — гонки проявляются чаще
    violations = []
    buf = make_buffer(SIZE, violations)
    consumed = [[] for _ in range(CONSUMERS)]

    def producer(k):
        for item in range(k, N_ITEMS, PRODUCERS):
            buf.put(item)

    def consumer(k):
        while True:
            item = buf.get()
            if item == STOP:
                return
            if item is None:
                violations.append("потребитель получил пустой слот")
                continue
            consumed[k].append(item)

    def send_stops():
        for _ in range(CONSUMERS):
            buf.put(STOP)

    producers = [threading.Thread(target=producer, args=(k,), daemon=True) for k in range(PRODUCERS)]
    consumers = [threading.Thread(target=consumer, args=(k,), daemon=True) for k in range(CONSUMERS)]
    for t in producers + consumers:
        t.start()
    for t in producers:
        t.join(TIMEOUT)
    # пилюли кладёт отдельный поток, чтобы главный поток не завис на заполненном буфере
    threading.Thread(target=send_stops, daemon=True).start()
    for t in consumers:
        t.join(TIMEOUT)
    hung = any(t.is_alive() for t in producers + consumers)

    items = [x for part in consumed for x in part]
    duplicates = len(items) - len(set(items))
    missing = N_ITEMS - len(set(items) & set(range(N_ITEMS)))
    ok = not (violations or duplicates or missing or hung)
    print(title)
    print(f"  потреблено: {len(items)} из {N_ITEMS} (по потребителям: {[len(c) for c in consumed]})")
    print(f"  дубликатов: {duplicates}, потеряно: {missing}, нарушений буфера: {len(violations)}"
          + (", ЗАВИСАНИЕ" if hung else ""))
    for v in violations[:5]:
        print(f"    нарушение: {v}")
    print(f"  результат: {'OK' if ok else 'ОШИБКА'}", flush=True)
    return ok