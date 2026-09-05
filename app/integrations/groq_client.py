"""
Groq LLM Client integration with fallback support and structured JSON response parsing.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from config.settings import settings

logger = logging.getLogger(__name__)

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class GroqClient:
    """
    Wrapper around Groq API to provide structured inference with grounding guarantees.
    """
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.groq_api_key or os.getenv("GROQ_API_KEY")
        self.model = model or settings.groq_model
        self.client = None
        
        if GROQ_AVAILABLE and self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")

    def is_configured(self) -> bool:
        return self.client is not None

    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        json_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Generate completion using Groq LLM API.
        Returns response content along with execution metadata.
        """
        if not self.is_configured():
            logger.info("Groq API key not configured or client unavailable. Returning fallback mock structure.")
            return {
                "success": False,
                "content": None,
                "error": "Groq API key not configured.",
                "is_fallback": True
            }

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content

            if json_mode:
                parsed = json.loads(content)
                return {"success": True, "content": parsed, "is_fallback": False}

            return {"success": True, "content": content, "is_fallback": False}

        except Exception as e:
            logger.error(f"Groq API call error: {e}")
            return {
                "success": False,
                "content": None,
                "error": str(e),
                "is_fallback": True
            }
