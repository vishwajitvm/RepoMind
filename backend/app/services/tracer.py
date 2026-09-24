import os
import sys
import json
import logging
import time
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)


def _install_tracenest_formatter_hook():
    """
    Hooks TraceNest log formatter to inject top-level 'logger' and 'module' fields.
    This allows the TraceNest UI table to display the actual component name
    (e.g., 'indexer', 'llm', 'retrieval', 'mcp') instead of '—'.
    """
    try:
        import tracenest.logger
        mod = sys.modules.get("tracenest.logger")
        if mod and hasattr(mod, "format_log") and not getattr(mod, "_repomind_hooked", False):
            orig_format_log = mod.format_log

            def repomind_format_log(*, level, message, metadata=None, **kwargs):
                raw = orig_format_log(level=level, message=message, metadata=metadata, **kwargs)
                if not raw:
                    return raw
                try:
                    data = json.loads(raw)
                    comp = None
                    if metadata and isinstance(metadata, dict):
                        comp = metadata.get("logger") or metadata.get("component")
                    if not comp:
                        comp = data.get("meta", {}).get("logger") or data.get("meta", {}).get("component") or "repomind"
                    data["logger"] = comp
                    data["module"] = comp
                    return json.dumps(data, ensure_ascii=False)
                except Exception:
                    return raw

            mod.format_log = repomind_format_log
            mod._repomind_hooked = True
    except Exception as e:
        logger.debug(f"TraceNest formatter hook notice: {e}")


class ObservabilityTracer:
    """
    Best-effort tracer integrating TraceNest and LangSmith.
    Captures descriptive execution traces, tool calls, latencies, and fallback events.
    Guarantees that telemetry failures never break application flow.
    """

    def __init__(self):
        self._init_langsmith()
        self._init_tracenest()
        _install_tracenest_formatter_hook()

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
        self.tracenest_logger = None
        try:
            from tracenest.logger import logger as tl
            self.tracenest_logger = tl
            logger.info("TraceNest logger initialized")
        except Exception as e:
            logger.warning(f"TraceNest logger initialization skipped: {e}")

    def log_event(
        self,
        event_name: str,
        message_or_payload: Any = None,
        *,
        message: Optional[str] = None,
        logger_name: Optional[str] = None,
        level: str = "INFO",
        trace_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        **extra_payload
    ):
        """
        Safely record a descriptive event to TraceNest and structured logger.
        
        Args:
            event_name: machine-readable identifier (e.g. 'indexing_started')
            message_or_payload: human-readable message string OR dict payload for backwards compatibility
            message: explicit human-readable event message
            logger_name: component name (e.g. 'indexer', 'llm', 'retrieval', 'mcp', 'api')
            level: 'INFO', 'WARNING', 'ERROR', or 'DEBUG'
            trace_id: correlation / execution ID
            payload: additional structured metadata dict
            **extra_payload: additional key-value metadata pairs
        """
        final_payload: Dict[str, Any] = {}
        final_message: str = ""

        if isinstance(message_or_payload, str):
            final_message = message_or_payload
        elif isinstance(message_or_payload, dict):
            final_payload.update(message_or_payload)

        if message:
            final_message = message
        elif not final_message:
            final_message = event_name.replace("_", " ").capitalize()

        if payload and isinstance(payload, dict):
            final_payload.update(payload)

        if extra_payload:
            final_payload.update(extra_payload)

        # Infer logger_name if not provided
        comp = logger_name or final_payload.get("logger") or final_payload.get("component")
        if not comp:
            if "index" in event_name or "file" in event_name:
                comp = "indexer"
            elif "parse" in event_name:
                comp = "parser"
            elif "embed" in event_name:
                comp = "embedding"
            elif "qdrant" in event_name:
                comp = "qdrant"
            elif "retriev" in event_name:
                comp = "retrieval"
            elif "mcp" in event_name:
                comp = "mcp"
            elif "llm" in event_name or "model" in event_name:
                comp = "llm"
            elif "graph" in event_name:
                comp = "langgraph"
            elif "repo" in event_name:
                comp = "repository"
            elif "chat" in event_name:
                comp = "chat"
            elif "trace" in event_name:
                comp = "observability"
            else:
                comp = "repomind"

        # Sanitize any accidental secrets
        safe_payload: Dict[str, Any] = {
            "event": event_name,
            "logger": comp,
            "component": comp
        }

        for k, v in final_payload.items():
            if k in {"event", "logger", "component"}:
                continue
            if any(secret_term in str(k).lower() for secret_term in ("key", "token", "password", "secret", "auth", "credential")):
                safe_payload[k] = "[REDACTED]"
            else:
                if isinstance(v, (str, int, float, bool, list, dict)) or v is None:
                    safe_payload[k] = v
                else:
                    safe_payload[k] = str(v)

        lvl = level.upper()
        if lvl not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            lvl = "INFO"

        # Structured standard console log
        std_fn = getattr(logger, lvl.lower(), logger.info)
        std_fn(f"[{comp.upper()}] {final_message} | {safe_payload}")

        # Best-effort TraceNest structured logging
        if self.tracenest_logger:
            try:
                log_fn = getattr(self.tracenest_logger, lvl.lower(), self.tracenest_logger.info)
                log_fn(final_message, trace_id=trace_id, **safe_payload)
            except Exception as e:
                logger.debug(f"TraceNest logging failed: {e}")


tracer = ObservabilityTracer()
