import csv
import os
from typing import List, Dict


def slugify_topic(topic: str, max_words: int = 5) -> str:
    """Create a short filename-safe title from a potentially long topic."""
    # Take first N words, strip odd characters
    words = topic.strip().split()[:max_words]
    slug = "_".join(w.lower() for w in words)
    slug = "".join(c if c.isalnum() or c == "_" else "" for c in slug)
    return slug or "session"


def save_transcript(history: List[Dict[str, str]], filepath: str, format: str = "markdown"):
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
                writer.writerow([
                    msg.get("timestamp", ""),
                    msg.get("role", ""),
                    msg.get("content", "").replace("\n", " ")
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
                f.write(f"### {role.strip().capitalize()}{ts_str}\n\n{content}\n\n---\n\n")
