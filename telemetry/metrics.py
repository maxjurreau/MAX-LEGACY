"""
Simple metrics collector. Replace with real backend (Prometheus Pushgateway, Cloud Monitoring).
"""

import threading
from collections import defaultdict

class Metrics:
    def __init__(self):
        self._lock = threading.Lock()
        self._counters = defaultdict(int)

    def increment(self, name: str, amount: int = 1):
        with self._lock:
            self._counters[name] += amount

    def get(self, name: str):
        with self._lock:
            return self._counters.get(name, 0)

    def snapshot(self):
        with self._lock:
            return dict(self._counters)
