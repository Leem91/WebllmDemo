import httpx
import json
import time


def test_llm_streaming():
    """Smoke test that posts to /api/llm and confirms streaming chunks arrive.
    Requires backend running (CI starts it before this test)."""
    url = "http://127.0.0.1:8000/api/llm"
    payload = {"messages": [{"role": "user", "content": "Hello, run a quick analysis"}]}

    with httpx.Client(timeout=30.0) as client:
        with client.stream("POST", url, json=payload, timeout=30.0) as resp:
            assert resp.status_code == 200
            collected = ""
            # read streaming bytes
            for chunk in resp.iter_bytes():
                if not chunk:
                    continue
                try:
                    s = chunk.decode("utf-8", errors="ignore")
                except Exception:
                    s = str(chunk)
                collected += s
                # stop early if we see end marker (used by mock_llama)
                if "<end>" in collected or "MockLLM" in collected:
                    break
            assert collected, "No streaming content received"
            assert ("MockLLM" in collected) or ("choices" in collected) or ("data:" in collected)
