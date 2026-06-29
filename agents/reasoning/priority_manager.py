"""Priority ranking for reasoning messages."""
from __future__ import annotations

from typing import Dict, List


def sort_messages(messages: List[Dict[str, object]]) -> List[Dict[str, object]]:
    return sorted(messages, key=lambda item: (-(int(item.get("priority", 1))), item.get("message", "")))
