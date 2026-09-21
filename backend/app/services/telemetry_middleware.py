import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.tracer import tracer


class RepoMindHTTPTelemetryMiddleware(BaseHTTPMiddleware):
    """
    Descriptive request telemetry middleware for RepoMind.
    Produces high-signal, operation-specific messages instead of generic 'HTTP request completed'.
    Excludes polling, static UI, and documentation endpoints to eliminate log noise.
    """

    EXCLUDED_PREFIXES = (
        "/tracenest",
        "/docs",
        "/openapi.json",
        "/health",
        "/favicon.ico",
        "/styles.css",
        "/app.js",
    )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path

        # Ignore noisy paths: TraceNest UI, static assets, docs, health polling
        if any(path == p or path.startswith(f"{p}/") for p in self.EXCLUDED_PREFIXES):
            return await call_next(request)

        start_time = time.perf_counter()
        trace_id = request.headers.get("x-trace-id") or uuid.uuid4().hex

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Formulate descriptive operation-specific message
            msg = self._format_message(request.method, path, response.status_code)
            level = "INFO"
            if response.status_code >= 500:
                level = "ERROR"
            elif response.status_code >= 400:
                level = "WARNING"

            tracer.log_event(
                event_name="http_request_completed",
                message=msg,
                logger_name="api",
                level=level,
                trace_id=trace_id,
                method=request.method,
                path=path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
                client=request.client.host if request.client else None
            )
            return response

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            msg = f"{request.method} {path} failed — {type(exc).__name__}: {str(exc)}"
            tracer.log_event(
                event_name="http_request_failed",
                message=msg,
                logger_name="api",
                level="ERROR",
                trace_id=trace_id,
                method=request.method,
                path=path,
                duration_ms=round(duration_ms, 2),
                client=request.client.host if request.client else None,
                error=str(exc)
            )
            raise

    def _format_message(self, method: str, path: str, status_code: int) -> str:
        # Route-specific human-readable messages
        if path == "/api/repositories":
            if method == "POST":
                return "POST /api/repositories completed — repository registered" if status_code < 400 else f"POST /api/repositories failed — {status_code}"
            elif method == "GET":
                return "GET /api/repositories completed — listed repositories"

        if "/index" in path and method == "POST":
            return f"POST {path} completed — indexing job queued" if status_code < 400 else f"POST {path} failed — {status_code}"

        if "/status" in path and method == "GET":
            return f"GET {path} completed — indexing status checked"

        if path == "/api/chat" and method == "POST":
            return "POST /api/chat completed — intelligence response generated" if status_code < 400 else f"POST /api/chat failed — {status_code}"

        if path.startswith("/api/executions/") and method == "GET":
            return f"GET {path} completed — execution trace retrieved"

        if path.startswith("/api/repositories/") and method == "GET":
            return f"GET {path} completed — repository details fetched"

        # General descriptive fallback
        action = "completed" if status_code < 400 else "failed"
        return f"{method} {path} {action} — {status_code}"
