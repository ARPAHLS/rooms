import csv
import json
import os
from typing import List, Dict, Any


def slugify_topic(topic: str, max_words: int = 5) -> str:
    """Create a short filename-safe title from a potentially long topic."""
    # Take first N words, strip odd characters
    words = topic.strip().split()[:max_words]
    slug = "_".join(w.lower() for w in words)
    slug = "".join(c if c.isalnum() or c == "_" else "" for c in slug)
    return slug or "session"


def save_transcript(history: List[Dict[str, Any]], filepath: str, format: str = "markdown"):
    """
    Save the conversation history to filepath.
    Format: 'markdown' or 'csv'.
    history entries may include: role, content, timestamp, color.
    """
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    # Filter out system bootstrap messages from saved output
    public_history = [m for m in history if m["role"] != "system"]

    if format == "csv":
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Speaker", "Message"])
            for msg in public_history:
                if msg.get("role") == "skill":
                    payload = {
                        "event_type": msg.get("event_type", "skill_execution"),
                        "agent": msg.get("agent", ""),
                        "tool_name": msg.get("tool_name", ""),
                        "status": msg.get("status", ""),
                        "arguments": msg.get("arguments", {}),
                        "result": msg.get("result", {}),
                    }
                    message = json.dumps(payload, ensure_ascii=True, separators=(",", ":"))
                else:
                    message = msg.get("content", "").replace("\n", " ")
                writer.writerow([
                    msg.get("timestamp", ""),
                    msg.get("role", ""),
                    message
                ])
    else:
        # Markdown
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# Room Session Transcript\n\n")
            for msg in public_history:
                role = msg.get("role", "Unknown")
                content = msg.get("content", "")
                ts = msg.get("timestamp", "")
                ts_str = f" _{ts}_" if ts else ""
                if role == "skill":
                    content = (
                        f"- agent: {msg.get('agent', '')}\n"
                        f"- tool: {msg.get('tool_name', '')}\n"
                        f"- status: {msg.get('status', '')}\n"
                        f"- arguments: `{json.dumps(msg.get('arguments', {}), ensure_ascii=True)}`\n"
                        f"- result: `{json.dumps(msg.get('result', {}), ensure_ascii=True)}`"
                    )
                    role = "skill event"
                f.write(f"### {role.strip().capitalize()}{ts_str}\n\n{content}\n\n---\n\n")
