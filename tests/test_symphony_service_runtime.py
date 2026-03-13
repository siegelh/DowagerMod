from __future__ import annotations

import logging
import tempfile
import unittest
from pathlib import Path

from symphony.server import SymphonyServer
from symphony.service_runtime import ServiceRuntime


class FakeService:
    def __init__(self, runtime: ServiceRuntime):
        self._runtime = runtime
        self.calls = 0

    def run_once(self, **_kwargs):
        self.calls += 1
        self._runtime.request_stop()
        return None


class ServiceRuntimeTests(unittest.TestCase):
    def test_read_status_without_worker_returns_stopped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = ServiceRuntime(Path(tmp))
            status = runtime.read_status()

        self.assertFalse(status.is_running)
        self.assertEqual(status.payload["state"], "stopped")

    def test_stop_request_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = ServiceRuntime(Path(tmp))
            self.assertFalse(runtime.is_stop_requested())
            runtime.request_stop()
            self.assertTrue(runtime.is_stop_requested())
            runtime.clear_stop_request()
            self.assertFalse(runtime.is_stop_requested())

    def test_server_writes_running_status_and_stops_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = ServiceRuntime(Path(tmp))
            service = FakeService(runtime)
            logger = logging.getLogger("test-symphony-server")
            logger.handlers.clear()
            server = SymphonyServer(
                service=service,
                runtime=runtime,
                logger=logger,
                poll_interval_seconds=5,
                error_backoff_seconds=5,
            )

            exit_code = server.serve_forever()
            status = runtime.read_status()

        self.assertEqual(exit_code, 0)
        self.assertEqual(service.calls, 1)
        self.assertFalse(status.is_running)
        self.assertEqual(status.payload["state"], "stopped")
        self.assertNotIn("current_job_name", status.payload)


if __name__ == "__main__":
    unittest.main()
