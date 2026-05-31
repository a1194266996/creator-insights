from __future__ import annotations

import json
import urllib.request


def send_feishu_text(webhook_url: str, text: str, timeout_seconds: int = 20) -> None:
    if not webhook_url:
        raise ValueError("FEISHU_WEBHOOK_URL is not configured")

    payload = {
        "msg_type": "text",
        "content": {"text": text},
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        body = response.read().decode("utf-8", errors="replace")
        if response.status >= 300:
            raise RuntimeError(f"Feishu webhook failed: HTTP {response.status} {body}")
