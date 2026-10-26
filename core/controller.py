"""Application controller for asynchronous cryptographic operations."""

from __future__ import annotations

import queue
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass

from .app_state import AppState
from .service import CryptoOperationService


@dataclass(frozen=True)
class CryptoResult:
    """Result envelope passed from the worker back to the UI thread."""

    job_id: int
    cipher: str
    text: str
    keys: tuple[str, ...]
    operation: str
    future: Future


class CryptoController:
    """Own operation lifecycle, worker execution, cancellation and results."""

    def __init__(self, state: AppState, service=CryptoOperationService):
        self.state = state
        self.service = service
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="crypto")
        self._results: queue.Queue[CryptoResult] = queue.Queue()

    def submit(self, cipher, text, keys, operation, lang):
        """Submit one operation and return its monotonically increasing job id."""
        if self.state.crypto_busy or self.state.closing:
            return None
        self.state.crypto_busy = True
        self.state.crypto_job_id += 1
        job_id = self.state.crypto_job_id
        future = self.executor.submit(self.service.execute, cipher, text, keys, operation, lang)
        future.add_done_callback(self._enqueue_result(job_id, cipher, text, keys, operation))
        return job_id

    def _enqueue_result(self, job_id, cipher, text, keys, operation):
        def callback(future):
            if not self.state.closing:
                self._results.put(CryptoResult(job_id, cipher, text, keys, operation, future))

        return callback

    def poll_results(self):
        """Drain completed worker results; safe to call from the UI thread."""
        results = []
        while True:
            try:
                results.append(self._results.get_nowait())
            except queue.Empty:
                return results

    def is_current(self, job_id):
        return not self.state.closing and job_id == self.state.crypto_job_id

    def mark_finished(self, job_id):
        if self.is_current(job_id):
            self.state.crypto_busy = False
            return True
        return False

    def cancel_current(self):
        """Invalidate the current result without touching Tkinter widgets."""
        self.state.crypto_job_id += 1
        self.state.crypto_busy = False

    def close(self):
        self.state.closing = True
        self.cancel_current()
        self.executor.shutdown(wait=False, cancel_futures=True)
