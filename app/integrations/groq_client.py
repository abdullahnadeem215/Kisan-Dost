"""
Groq LLM Client integration with fallback support, OpenAI-compatible tool calling, and structured JSON parsing.
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from config.settings import settings

logger = logging.getLogger(__name__)

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class GroqClient:
    """
    Wrapper around Groq API to provide structured inference and tool execution
    with grounding guarantees for OpenAI Agents SDK.
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

    def chat_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: str = "auto",
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        Invokes Groq chat completions with OpenAI-compatible tool definitions.
        Returns the assistant message content and any tool_calls requested by the model.
        """
        if not self.is_configured():
            return {
                "success": False,
                "content": None,
                "tool_calls": [],
                "error": "Groq API key not configured.",
                "is_fallback": True
            }

        try:
            kwargs: Dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = tool_choice

            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message
            content = message.content or ""

            tool_calls_parsed: List[Dict[str, Any]] = []
            if hasattr(message, "tool_calls") and message.tool_calls:
                for tc in message.tool_calls:
                    fn_args = {}
                    if hasattr(tc.function, "arguments") and tc.function.arguments:
                        try:
                            fn_args = json.loads(tc.function.arguments)
                        except Exception:
                            fn_args = {}
                    tool_calls_parsed.append({
                        "id": getattr(tc, "id", f"call_{len(tool_calls_parsed)}"),
                        "name": tc.function.name,
                        "arguments": fn_args
                    })

            return {
                "success": True,
                "content": content,
                "tool_calls": tool_calls_parsed,
                "is_fallback": False
            }
        except Exception as e:
            logger.error(f"Groq chat_with_tools error: {e}")
            return {
                "success": False,
                "content": None,
                "tool_calls": [],
                "error": str(e),
                "is_fallback": True
            }
