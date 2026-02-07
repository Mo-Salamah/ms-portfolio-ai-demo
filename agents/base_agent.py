"""
الوكيل الأساسي — منصة الذكاء الاصطناعي للمحفظة (أ)
"""

import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class AgentResponse(BaseModel):
    """Structured response from any agent."""
    content: str = Field(description="Main response content")
    thinking: Optional[str] = Field(default=None, description="Agent reasoning trace")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional info")
    agent_name: str = Field(description="Name of the agent")
    agent_name_en: Optional[str] = Field(default=None, description="Agent name for display")


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(
        self,
        name: str,
        name_en: str,
        description: str,
        model: str = "claude-opus-4-6",
        max_tokens: int = 4096,
        temperature: float = 0.7
    ):
        self.name = name
        self.name_en = name_en
        self.description = description
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

        api_key = None
        try:
            import streamlit as st
            api_key = st.secrets.get("ANTHROPIC_API_KEY")
        except Exception:
            pass

        if not api_key:
            api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")
        self.client = Anthropic(api_key=api_key)

        self._thinking_log: List[str] = []

    @abstractmethod
    def get_system_prompt(self) -> str:
        pass

    def _log_thinking(self, thought: str):
        self._thinking_log.append(thought)

    def _clear_thinking(self):
        self._thinking_log = []

    def _get_thinking_trace(self) -> str:
        if not self._thinking_log:
            return ""
        return "\n".join([f"- {thought}" for thought in self._thinking_log])

    def _build_messages(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> List[Dict]:
        messages = []

        if conversation_history:
            messages.extend(conversation_history)

        content = user_message
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            content = f"""السياق:
{context_str}

الطلب:
{user_message}"""

        messages.append({
            "role": "user",
            "content": content
        })

        return messages

    def invoke(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AgentResponse:
        self._clear_thinking()
        self._log_thinking(f"استلام الطلب: {user_message[:100]}...")

        messages = self._build_messages(user_message, context, conversation_history)
        self._log_thinking("تجهيز الرسائل")

        system_prompt = self.get_system_prompt()
        self._log_thinking("تحميل تعليمات النظام")

        try:
            self._log_thinking("استدعاء النموذج...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=messages
            )

            response_text = response.content[0].text
            self._log_thinking("تم استلام الرد")

            metadata = {
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "stop_reason": response.stop_reason,
            }

            return AgentResponse(
                content=response_text,
                thinking=self._get_thinking_trace(),
                metadata=metadata,
                agent_name=self.name,
                agent_name_en=self.name_en
            )

        except Exception as e:
            self._log_thinking(f"حدث خطأ: {str(e)}")

            return AgentResponse(
                content=f"حدث خطأ أثناء معالجة الطلب: {str(e)}",
                thinking=self._get_thinking_trace(),
                metadata={"error": str(e)},
                agent_name=self.name,
                agent_name_en=self.name_en
            )

    def invoke_with_structured_output(
        self,
        user_message: str,
        output_instructions: str,
        context: Optional[Dict] = None
    ) -> AgentResponse:
        enhanced_message = f"""{user_message}

يرجى تقديم الرد بالصيغة التالية:
{output_instructions}"""

        return self.invoke(enhanced_message, context)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', model='{self.model}')"
