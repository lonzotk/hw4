from contextvars import ContextVar
from datetime import datetime, timezone
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = PROJECT_ROOT / "output" / "audit_trail.json"
CURRENT_AUDIT: ContextVar[dict | None] = ContextVar("current_audit", default=None)


def ensure_audit_file() -> None:
    """Create the project-level audit file without replacing existing entries."""
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not AUDIT_PATH.exists():
        AUDIT_PATH.write_text("[]\n", encoding="utf-8")


def safe(value):
    text = str(value)
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[REDACTED_EMAIL]", text)
    text = re.sub(r"(?i)(password|hash|api[_-]?key|token|secret|authorization)\s*[:=]\s*[^,;\s]+", r"\1=[REDACTED]", text)
    return text[:500]


def begin_audit(message: str) -> dict:
    record = {"started_at": datetime.now(timezone.utc).isoformat(), "steps": [], "message": safe(message)}
    CURRENT_AUDIT.set(record)
    record_step("agent", {"action": "start"}, "Agent run started")
    return record


def record_step(tool_name: str, inputs, result: str, stopped_because: str | None = None) -> None:
    record = CURRENT_AUDIT.get()
    if record is None:
        return
    step = {"time": datetime.now(timezone.utc).isoformat(), "tool": tool_name, "inputs": safe(inputs), "result": safe(result)}
    if stopped_because:
        step["stopped_because"] = safe(stopped_because)
    record["steps"].append(step)


def finish_audit(record: dict, reason: str) -> None:
    record["finished_at"] = datetime.now(timezone.utc).isoformat()
    record["stopped_because"] = safe(reason)
    ensure_audit_file()
    try:
        existing = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
        if not isinstance(existing, list):
            raise ValueError("audit trail must contain a JSON list")
    except (OSError, json.JSONDecodeError):
        raise RuntimeError(f"Cannot append safely to {AUDIT_PATH}; existing audit data was not replaced.")
    existing.append(record)
    AUDIT_PATH.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


ensure_audit_file()
