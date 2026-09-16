"""Google Gemini API wrapper (free tier)."""
import os
from typing import Optional


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY", "").strip()
        self.model_name = model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self._client = None
        self.available = False
        self._init()

    def _init(self):
        if not self.api_key or self.api_key.startswith("your_"):
            print("[INFO] GOOGLE_API_KEY not set. LLM features disabled.")
            return
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self.model_name)
            self.available = True
            print(f"[INFO] Gemini client ready (model={self.model_name}).")
        except Exception as e:
            print(f"[WARN] Failed to init Gemini: {e}")
            self.available = False

    def generate(self, prompt: str) -> Optional[str]:
        if not self.available:
            return None
        try:
            response = self._client.generate_content(prompt)
            return getattr(response, "text", None)
        except Exception as e:
            print(f"[WARN] Gemini generation failed: {e}")
            return None