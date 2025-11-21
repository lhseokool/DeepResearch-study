"""Base Agent class for common functionality.

Provides common LLM initialization and utilities for all agents.
"""

from pathlib import Path

from langchain_openai import ChatOpenAI


class BaseAgent:
    """Base class for all agents with common LLM initialization."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0,
    ):
        """Initialize base agent.

        Args:
            model: LLM model name
            temperature: Temperature for LLM
        """
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.model = model
        self.temperature = temperature

    def _get_llm_config(self) -> dict:
        """Get LLM configuration.

        Returns:
            Dictionary with model and temperature
        """
        return {
            "model": self.model,
            "temperature": self.temperature,
        }
