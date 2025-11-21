"""Prompt templates for LLM interactions."""

from .orchestrator import format_orchestrator_prompt

PLANNING_PROMPT = """
You are an expert code analyst planning an impact analysis task.

Task Details:
- Mode: {mode}
- Target File: {file_path}
- Symbol: {symbol_name}
- Max Depth: {max_depth}

Create a brief analysis plan considering:
1. Is the selected mode appropriate for this task?
2. What are potential challenges (e.g., dynamic typing, complex dependencies)?
3. Should we prepare for fallback to SPEED mode?

Provide a concise 2-3 sentence plan.
"""

FALLBACK_DECISION_PROMPT = """
The PRECISION mode analysis has failed with the following error:
{error_message}

Should we fallback to SPEED mode?

Consider:
- SPEED mode is faster but may have false positives
- SPEED mode doesn't require build environment
- The analysis will complete but with less precision

Recommend: yes or no
"""

RESULT_SUMMARY_PROMPT = """
Summarize the following impact analysis results in natural language:

Mode: {mode}
Success: {success}
Dependencies Found: {dep_count}
Execution Time: {execution_time}s

Dependencies:
{dependencies}

Provide a brief, user-friendly summary.
"""

__all__ = [
    "format_orchestrator_prompt",
    "PLANNING_PROMPT",
    "FALLBACK_DECISION_PROMPT",
    "RESULT_SUMMARY_PROMPT",
]
