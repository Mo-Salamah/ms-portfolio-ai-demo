"""
Base Agent Class for MS Portfolio AI Agent Demo

This module provides the base class for all agents with common
Claude API interaction patterns.
"""

import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AgentResponse(BaseModel):
    """
    Structured response from any agent.
    """
    content: str = Field(description="Main response content")
    thinking: Optional[str] = Field(default=None, description="Agent reasoning trace")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional info")
    agent_name: str = Field(description="Name of the agent that generated this response")
    agent_name_en: Optional[str] = Field(default=None, description="English name of the agent")


class BaseAgent(ABC):
    """
    Abstract base class for all agents.

    Provides common functionality for Claude API interaction,
    including message building, API calls, and response parsing.
    """

    def __init__(
        self,
        name: str,
        name_en: str,
        description: str,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 4096,
        temperature: float = 0.7
    ):
        """
        Initialize the base agent.

        Args:
            name: Agent name
            name_en: Agent name in English
            description: Agent description
            model: Claude model to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
        """
        self.name = name
        self.name_en = name_en
        self.description = description
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Initialize Anthropic client
        # Try Streamlit secrets first (for cloud deployment), then env var
        api_key = None
        try:
            import streamlit as st
            api_key = st.secrets.get("ANTHROPIC_API_KEY")
        except Exception:
            pass

        if not api_key:
            api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in secrets or environment variables")
        self.client = Anthropic(api_key=api_key)

        # Thinking log for UI display
        self._thinking_log: List[str] = []

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Return the agent-specific system prompt.
        Must be implemented by subclasses.
        """
        pass

    def _log_thinking(self, thought: str):
        """
        Capture reasoning for UI display.

        Args:
            thought: A reasoning step to log
        """
        self._thinking_log.append(thought)

    def _clear_thinking(self):
        """Clear the thinking log for a new request."""
        self._thinking_log = []

    def _get_thinking_trace(self) -> str:
        """Get the full thinking trace as a formatted string."""
        if not self._thinking_log:
            return ""
        return "\n".join([f"- {thought}" for thought in self._thinking_log])

    def _build_messages(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Construct message list for API call.

        Args:
            user_message: The user's input message
            context: Optional context dict to include
            conversation_history: Optional list of previous messages

        Returns:
            List of message dicts for the API
        """
        messages = []

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Build the current user message with optional context
        content = user_message
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            content = f"""Context:
{context_str}

Request:
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
        """
        Main entry point for agent invocation.

        Args:
            user_message: The user's input message
            context: Optional context dictionary
            conversation_history: Optional previous messages

        Returns:
            AgentResponse with content, thinking, and metadata
        """
        # Clear thinking log for new request
        self._clear_thinking()

        # Log initial thinking
        self._log_thinking(f"Received request: {user_message[:100]}...")

        # Build messages
        messages = self._build_messages(user_message, context, conversation_history)
        self._log_thinking("Messages prepared for model")

        # Get system prompt
        system_prompt = self.get_system_prompt()
        self._log_thinking("System instructions loaded")

        try:
            # Call Claude API
            self._log_thinking("Calling Claude model...")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=messages
            )

            # Extract response content
            response_text = response.content[0].text
            self._log_thinking("Response received successfully")

            # Build metadata
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
            self._log_thinking(f"Error occurred: {str(e)}")

            return AgentResponse(
                content=f"Sorry, an error occurred while processing your request: {str(e)}",
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
        """
        Invoke the agent with specific output format instructions.

        Args:
            user_message: The user's input message
            output_instructions: Instructions for output format
            context: Optional context dictionary

        Returns:
            AgentResponse with structured content
        """
        enhanced_message = f"""{user_message}

Please provide your response in the following format:
{output_instructions}"""

        return self.invoke(enhanced_message, context)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', model='{self.model}')"
