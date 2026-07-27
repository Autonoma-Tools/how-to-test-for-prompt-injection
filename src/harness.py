"""
Harness for running a red-team payload against the app under test.

The harness's only job is delivery and capture: build the right input shape
for a payload's vector, send it to the app, and return a structured result.
It never judges pass or fail, that is assertions.py's job.
"""

from __future__ import annotations

import glob
from dataclasses import dataclass, field
from typing import Any

import yaml

DEFAULT_USER_MESSAGE = "What's the status of my order #4821?"


@dataclass
class RedTeamResult:
    payload_id: str
    response_text: str
    tool_calls: list[dict] = field(default_factory=list)
    system_prompt_used: str = ""


def load_corpus(*paths: str) -> list[dict]:
    """Load and flatten one or more payload YAML files (or glob patterns)
    into a single list of payload dicts."""
    payloads: list[dict] = []
    for pattern in paths:
        for path in sorted(glob.glob(pattern)):
            with open(path, "r", encoding="utf-8") as handle:
                loaded = yaml.safe_load(handle) or []
                payloads.extend(loaded)
    return payloads


def build_delivery(payload: dict) -> tuple[str, list[dict]]:
    """Build the (user_message, context_snippets) pair the app under test
    should receive for this payload, based on its vector.

    Direct-class payloads (and jailbreak / leak / exfiltration payloads,
    which are also user-message-vector) are sent as the literal user turn.
    Indirect-class payloads are wrapped inside a synthetic snippet of the
    carrier type they specify, and the harness sends an ordinary, unrelated
    question as the actual user message, so the scenario looks like real
    traffic rather than an obvious test fixture.
    """
    vector = payload["vector"]

    if vector == "user_message":
        return payload["payload"], []

    carrier = payload.get("carrier", "retrieved_content")
    context_snippets = [
        {
            "type": vector,
            "carrier": carrier,
            "content": payload["payload"],
        }
    ]
    user_message = payload.get("base_user_message", DEFAULT_USER_MESSAGE)
    return user_message, context_snippets


def run_payload(app_client: Any, payload: dict, system_prompt: str) -> RedTeamResult:
    """Deliver a single payload to the app under test and capture the
    result. `app_client` is expected to expose a `.chat(system_prompt,
    user_message, context_snippets=None) -> dict` method returning at least
    {"text": str, "tool_calls": list[dict]}. Point it at a real client that
    talks to your app's preview or staging environment; the fake client in
    tests/test_red_team.py exists only to make this repo runnable out of the
    box.
    """
    user_message, context_snippets = build_delivery(payload)
    raw = app_client.chat(system_prompt, user_message, context_snippets=context_snippets)
    return RedTeamResult(
        payload_id=payload["id"],
        response_text=raw.get("text", ""),
        tool_calls=raw.get("tool_calls", []),
        system_prompt_used=system_prompt,
    )
