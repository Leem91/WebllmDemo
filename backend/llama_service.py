import os
import json
import threading

try:
    from llama_cpp import Llama
    _LLAMA_AVAILABLE = True
    _LLAMA_IMPORT_ERROR = None
except Exception as _e:
    Llama = None
    _LLAMA_AVAILABLE = False
    _LLAMA_IMPORT_ERROR = str(_e)


class LlamaService:
    def __init__(self):
        self.model_path = os.getenv("LLAMA_MODEL_PATH", os.path.join(os.path.dirname(__file__), "models", "llama-3.2-1b-q4.bin"))
        self._model = None
        self._lock = threading.Lock()
        self._loaded = False

    def ensure_loaded(self):
        if self._loaded:
            return
        if not _LLAMA_AVAILABLE:
            raise RuntimeError("llama_cpp (llama-cpp-python) is not installed: " + str(_LLAMA_IMPORT_ERROR))
        if not self.model_path or not os.path.exists(self.model_path):
            raise RuntimeError(f"LLAMA model file not found at: {self.model_path}")
        # Load model (may be large); keep simple and rely on llama-cpp-python
        # n_ctx can be tuned via LLAMA_N_CTX env var
        n_ctx = int(os.getenv("LLAMA_N_CTX", "2048"))
        self._model = Llama(model_path=self.model_path, n_ctx=n_ctx)
        self._loaded = True

    def _messages_to_prompt(self, messages):
        if not messages:
            return ""
        parts = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                parts.append(f"System: {content}")
            elif role == "assistant":
                parts.append(f"Assistant: {content}")
            else:
                parts.append(f"User: {content}")
        return "\n".join(parts) + "\n"

    def stream_chat(self, messages, max_tokens=512, temperature=0.2):
        """
        Returns a generator yielding bytes in SSE (Server-Sent Events) "data: ...\n\n" format.
        Each event payload is a JSON object similar to OpenAI stream chunks: {"choices":[{"delta":{"content":"..."}}]}
        """
        self.ensure_loaded()
        prompt = self._messages_to_prompt(messages)

        # llama-cpp-python exposes a streaming generator via create(..., stream=True)
        try:
            gen = self._model.create(prompt=prompt, max_tokens=max_tokens, temperature=temperature, stream=True)
        except Exception:
            # Some versions expose create_completion
            try:
                gen = self._model.create_completion(prompt=prompt, max_tokens=max_tokens, temperature=temperature, stream=True)
            except Exception as e:
                raise RuntimeError("Model streaming failed: " + str(e))

        for chunk in gen:
            text = ""
            try:
                if isinstance(chunk, dict):
                    # Common shape: {'choices':[{'text': '...'}]} or choices.deltas
                    ch = chunk.get("choices", [])[0]
                    text = ch.get("text") or ch.get("delta", {}).get("content", "") or ""
                else:
                    text = str(chunk)
            except Exception:
                text = str(chunk)

            # Emit SSE event
            try:
                data_obj = {"choices": [{"delta": {"content": text}}]}
                out = "data: " + json.dumps(data_obj, ensure_ascii=False) + "\n\n"
                yield out.encode("utf-8")
            except Exception:
                yield ("data: " + text + "\n\n").encode("utf-8")

    def get_status(self):
        return {
            "available": bool(_LLAMA_AVAILABLE),
            "model_path": self.model_path,
            "loaded": bool(self._loaded),
            "import_error": _LLAMA_IMPORT_ERROR if not _LLAMA_AVAILABLE else None,
        }


_service = LlamaService()


def stream_chat(messages, max_tokens=512, temperature=0.2):
    return _service.stream_chat(messages, max_tokens=max_tokens, temperature=temperature)


def get_status():
    return _service.get_status()


def preload():
    _service.ensure_loaded()
