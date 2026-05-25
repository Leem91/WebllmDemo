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
        This implementation is more tolerant of different chunk shapes (bytes, str, dict) produced by llama-cpp-python.
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
                if isinstance(chunk, (bytes, bytearray)):
                    text = chunk.decode("utf-8", errors="ignore")
                elif isinstance(chunk, str):
                    text = chunk
                elif isinstance(chunk, dict):
                    # Support shapes like {'choices':[{'text':...}]} or {'choices':[{'delta':{'content':...}}]}
                    ch = chunk.get("choices")
                    if ch and isinstance(ch, list) and len(ch) > 0:
                        first = ch[0]
                        if isinstance(first, dict):
                            text = first.get("text") or first.get("delta", {}).get("content") or first.get("content") or ""
                        else:
                            text = str(first)
                    else:
                        # Fallback: stringify the dict
                        text = json.dumps(chunk, ensure_ascii=False)
                else:
                    text = str(chunk)
            except Exception:
                try:
                    text = str(chunk)
                except Exception:
                    text = ""

            if not text:
                # skip empty tokens
                continue

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
