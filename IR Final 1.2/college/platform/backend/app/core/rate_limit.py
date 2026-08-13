"""Rate limiting middleware."""

import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import HTTPException, Request


class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.limit = requests_per_minute
        self._requests: Dict[str, list] = defaultdict(list)

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def check(self, request: Request) -> None:
        key = self._client_key(request)
        now = time.time()
        window_start = now - 60
        self._requests[key] = [t for t in self._requests[key] if t > window_start]
        if len(self._requests[key]) >= self.limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in 1 minute.")
        self._requests[key].append(now)
