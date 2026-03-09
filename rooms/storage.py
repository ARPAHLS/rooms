import json
import os
from typing import List, Dict

def save_transcript(history: List[Dict[str, str]], filepath: str, format: str = "markdown"):
    """
    Save the conversation history to the specified filepath.
    Format can be 'markdown' or 'json'.
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    
    if format == "json":
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4)
    else:
        # Default to markdown
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# Room Session Transcript\n\n")
            for msg in history:
                role = msg["role"]
                content = msg["content"]
                if role == "system":
                    f.write(f"--- \n> **System**: {content}\n\n")
                else:
                    f.write(f"### {role.capitalize()}\n\n{content}\n\n")
