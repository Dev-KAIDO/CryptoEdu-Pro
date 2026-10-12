import time
import unittest

from core.app_state import AppState
from core.controller import CryptoController


class TestCryptoController(unittest.TestCase):
    def wait_for_result(self, controller):
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            results = controller.poll_results()
            if results:
                return results[0]
            time.sleep(0.005)
        self.fail("controller did not return a result")

    def test_submit_and_collect_result(self):
        state = AppState()
        controller = CryptoController(state)
        try:
            job_id = controller.submit("Caesar", "ABC", ("3",), "encrypt", "AR")
            self.assertEqual(job_id, 1)
            self.assertTrue(state.crypto_busy)
            result = self.wait_for_result(controller)
            self.assertEqual(result.job_id, job_id)
            self.assertEqual(result.future.result(), "DEF")
            self.assertTrue(controller.mark_finished(job_id))
            self.assertFalse(state.crypto_busy)
        finally:
            controller.close()

    def test_only_one_operation_can_run(self):
        state = AppState()
        controller = CryptoController(state)
        try:
            self.assertEqual(controller.submit("Caesar", "ABC", ("3",), "encrypt", "AR"), 1)
            self.assertIsNone(controller.submit("Caesar", "ABC", ("3",), "encrypt", "AR"))
            result = self.wait_for_result(controller)
            controller.mark_finished(result.job_id)
        finally:
            controller.close()

    def test_cancel_invalidates_late_result(self):
        state = AppState()
        controller = CryptoController(state)
        try:
            job_id = controller.submit("Caesar", "ABC", ("3",), "encrypt", "AR")
            controller.cancel_current()
            self.assertFalse(controller.is_current(job_id))
            self.assertFalse(state.crypto_busy)
        finally:
            controller.close()


if __name__ == "__main__":
    unittest.main()
