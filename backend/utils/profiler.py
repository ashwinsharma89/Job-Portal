import time
from contextlib import contextmanager
import json
from typing import Dict, Any

class RequestProfiler:
    def __init__(self):
        self.timings: Dict[str, float] = {}
        self.meta: Dict[str, Any] = {}
        self.start_time = time.time()

    @contextmanager
    def measure(self, name: str):
        """Context manager to measure time of a block."""
        t0 = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - t0) * 1000
            self.timings[name] = round(duration_ms, 2)

    def set_meta(self, key: str, value: Any):
        """Set logical metric (counts, cache status, etc)."""
        self.meta[key] = value

    def get_header_json(self) -> str:
        """Return JSON string for X-Debug-Info header."""
        total_ms = (time.time() - self.start_time) * 1000
        self.timings['total'] = round(total_ms, 2)
        
        data = {
            "timing": self.timings,
            "meta": self.meta
        }
        return json.dumps(data)

# Global context var could be used, but for simplicity we'll attach to request state 
# or pass it down. For FastAPI, request.state is best.
