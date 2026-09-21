import os
import logging
import time
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class ObservabilityTracer:
    """
    Best-effort tracer integrating TraceNest and LangSmith.
    Captures execution traces, tool calls, latencies, and fallback events.
    Guarantees that telemetry failures never break application flow.
    """

    def __init__(self):
        self._init_langsmith()
        self._init_tracenest()

    def _init_langsmith(self):
        if settings.LANGSMITH_API_KEY:
            try:
                os.environ["LANGCHAIN_TRACING_V2"] = "true"
                os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
                os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
                logger.info(f"LangSmith tracing enabled for project '{settings.LANGSMITH_PROJECT}'")
            except Exception as e:
                logger.warning(f"Failed to initialize LangSmith: {e}")
        else:
            os.environ["LANGCHAIN_TRACING_V2"] = "false"

    def _init_tracenest(self):
        self.tracenest_client = None
        if settings.TRACENEST_API_KEY:
            try:
                import tracenest
                # TraceNest best effort initialization
                self.tracenest_client = tracenest
                logger.info("TraceNest client initialized")
            except Exception as e:
                logger.warning(f"TraceNest initialization skipped: {e}")

    def log_event(self, event_name: str, payload: Dict[str, Any]):
        """Safely record an event to TraceNest and structured logger."""
        # Sanitize any accidental secrets
        safe_payload = {}
        for k, v in payload.items():
            if any(secret_term in k.lower() for secret_term in ("key", "token", "password", "secret", "auth")):
                safe_payload[k] = "[REDACTED]"
            else:
                safe_payload[k] = v

        logger.info(f"[TRACE] {event_name}: {safe_payload}")

        if self.tracenest_client:
            try:
                # Best-effort TraceNest track
                if hasattr(self.tracenest_client, "track"):
                    self.tracenest_client.track(event_name, safe_payload)
            except Exception as e:
                logger.debug(f"TraceNest logging failed: {e}")


tracer = ObservabilityTracer()
