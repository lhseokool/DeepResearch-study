"""Self-Healing Agent for autonomous code generation and recovery.

FR-AC-01: Refactoring Execution
FR-AC-02: Self-Healing Loop (Max 3 retries)
FR-AC-03: Test Generation
"""

import asyncio
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from deepagents.backends import FileSystemBackend
from langchain_core.messages import HumanMessage

from ..utils.openrouter_llm import create_openrouter_llm


class ErrorType(Enum):
    """Error type classification."""

    SYNTAX_ERROR = "syntax_error"
    IMPORT_ERROR = "import_error"
    TYPE_ERROR = "type_error"
    NAME_ERROR = "name_error"
    ATTRIBUTE_ERROR = "attribute_error"
    TEST_FAILURE = "test_failure"
    RUNTIME_ERROR = "runtime_error"
    UNKNOWN = "unknown"


@dataclass
class ExecutionResult:
    """Result of code execution."""

    success: bool
    output: str
    error: str | None
    error_type: ErrorType | None
    exit_code: int


@dataclass
class HealingAttempt:
    """Single healing attempt record."""

    attempt_number: int
    error_context: str
    patch_generated: str
    result: ExecutionResult


class SelfHealingAgent:
    """Agent for autonomous code generation and self-healing.
    
    Process Flow:
    1. Execute: Compile or run tests on generated code
    2. Analyze: Parse error messages and classify error types
    3. Prompting: Send Original Code + Error Log + Related Docs to LLM
    4. Patch: Apply LLM-generated modifications (Diff)
    5. Retry: Increment retry count and retry (Max 3 times)
    """

    MAX_RETRIES = 3

    def __init__(
        self,
        model: str = "openai/gpt-4.1",
        temperature: float = 0,
        work_dir: str | Path | None = None,
    ):
        """Initialize Self-Healing Agent.

        Args:
            model: LLM model name (OpenRouter format: provider/model)
            temperature: Temperature for LLM
            work_dir: Working directory for file operations
        """
        self.llm = create_openrouter_llm(model=model, temperature=temperature)
        self.work_dir = Path(work_dir) if work_dir else Path.cwd()
        self.healing_history: list[HealingAttempt] = []

    async def execute_code(
        self,
        code: str,
        file_path: str | Path,
        test_command: str | None = None,
    ) -> ExecutionResult:
        """Execute: Compile or run tests on generated code.

        Args:
            code: Code to execute
            file_path: Path to save code file
            test_command: Optional test command (e.g., "pytest test_file.py")

        Returns:
            Execution result
        """
        file_path = Path(file_path)
        
        # Write code to file
        file_path.write_text(code)
        
        # Determine execution command
        if test_command:
            command = test_command
        else:
            # Default: try to compile/lint the code
            command = f"python -m py_compile {file_path}"
        
        # Execute command
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.work_dir,
                timeout=30,
            )
            
            success = result.returncode == 0
            error = result.stderr if not success else None
            error_type = self._classify_error(result.stderr) if error else None
            
            return ExecutionResult(
                success=success,
                output=result.stdout,
                error=error,
                error_type=error_type,
                exit_code=result.returncode,
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                output="",
                error="Execution timeout (30s)",
                error_type=ErrorType.RUNTIME_ERROR,
                exit_code=-1,
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                error_type=ErrorType.UNKNOWN,
                exit_code=-1,
            )

    def _classify_error(self, error_message: str) -> ErrorType:
        """Analyze: Parse error messages and classify error type.

        Args:
            error_message: Error message from execution

        Returns:
            Classified error type
        """
        if not error_message:
            return ErrorType.UNKNOWN
        
        error_lower = error_message.lower()
        
        # Classification patterns
        patterns = {
            ErrorType.SYNTAX_ERROR: [r"syntaxerror", r"invalid syntax"],
            ErrorType.IMPORT_ERROR: [r"importerror", r"modulenotfounderror", r"no module named"],
            ErrorType.TYPE_ERROR: [r"typeerror"],
            ErrorType.NAME_ERROR: [r"nameerror", r"name .* is not defined"],
            ErrorType.ATTRIBUTE_ERROR: [r"attributeerror"],
            ErrorType.TEST_FAILURE: [r"failed", r"assertion", r"assertionerror"],
        }
        
        for error_type, patterns_list in patterns.items():
            for pattern in patterns_list:
                if re.search(pattern, error_lower):
                    return error_type
        
        return ErrorType.UNKNOWN

    async def generate_patch(
        self,
        original_code: str,
        error_log: str,
        error_type: ErrorType,
        related_docs: str | None = None,
        attempt_number: int = 1,
    ) -> str:
        """Prompting: Generate patch using LLM.

        Args:
            original_code: Original code that failed
            error_log: Error message from execution
            error_type: Classified error type
            related_docs: Optional related documentation
            attempt_number: Current attempt number

        Returns:
            Patched code
        """
        system_prompt = """You are an expert Python developer specialized in debugging and fixing code.
Your task is to analyze error logs and generate corrected code.

IMPORTANT:
- Return ONLY the complete corrected code
- Do NOT include explanations or markdown code blocks
- Preserve the original structure and intent
- Fix only what is necessary to resolve the error"""

        user_prompt = f"""
## Original Code
```python
{original_code}
```

## Error Type
{error_type.value}

## Error Log
```
{error_log}
```

## Attempt Number
{attempt_number} of {self.MAX_RETRIES}

## Related Documentation
{related_docs or "No additional documentation provided"}

## Task
Fix the code to resolve the error. Return ONLY the corrected code without any explanation or markdown formatting.
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        
        response = self.llm.invoke(messages)
        
        # Extract code from response (handle potential markdown wrapping)
        patched_code = response.content.strip()
        
        # Remove markdown code blocks if present
        if patched_code.startswith("```python"):
            patched_code = re.sub(r"^```python\n", "", patched_code)
            patched_code = re.sub(r"\n```$", "", patched_code)
        elif patched_code.startswith("```"):
            patched_code = re.sub(r"^```\n", "", patched_code)
            patched_code = re.sub(r"\n```$", "", patched_code)
        
        return patched_code

    async def self_heal(
        self,
        code: str,
        file_path: str | Path,
        test_command: str | None = None,
        related_docs: str | None = None,
    ) -> dict[str, Any]:
        """FR-AC-02: Self-Healing Loop.
        
        Automatically attempt to fix code errors up to MAX_RETRIES times.

        Args:
            code: Initial code to heal
            file_path: Path to save code file
            test_command: Optional test command
            related_docs: Optional related documentation

        Returns:
            Healing result with final code and attempt history
        """
        self.healing_history = []
        current_code = code
        
        # Initial execution
        result = await self.execute_code(current_code, file_path, test_command)
        
        if result.success:
            return {
                "success": True,
                "final_code": current_code,
                "attempts": 0,
                "message": "Code executed successfully on first attempt",
            }
        
        # Self-healing loop
        for attempt in range(1, self.MAX_RETRIES + 1):
            print(f"\n🔄 Healing attempt {attempt}/{self.MAX_RETRIES}")
            print(f"Error: {result.error_type.value if result.error_type else 'unknown'}")
            
            # Generate patch
            patched_code = await self.generate_patch(
                original_code=current_code,
                error_log=result.error or "",
                error_type=result.error_type or ErrorType.UNKNOWN,
                related_docs=related_docs,
                attempt_number=attempt,
            )
            
            # Record attempt
            healing_attempt = HealingAttempt(
                attempt_number=attempt,
                error_context=result.error or "",
                patch_generated=patched_code,
                result=result,
            )
            self.healing_history.append(healing_attempt)
            
            # Update current code and retry
            current_code = patched_code
            result = await self.execute_code(current_code, file_path, test_command)
            
            if result.success:
                return {
                    "success": True,
                    "final_code": current_code,
                    "attempts": attempt,
                    "history": self.healing_history,
                    "message": f"Code healed successfully after {attempt} attempt(s)",
                }
        
        # Max retries reached without success
        return {
            "success": False,
            "final_code": current_code,
            "attempts": self.MAX_RETRIES,
            "history": self.healing_history,
            "message": f"Failed to heal code after {self.MAX_RETRIES} attempts",
            "last_error": result.error,
        }

    async def generate_unit_tests(
        self,
        code: str,
        file_path: str | Path,
        framework: str = "pytest",
    ) -> str:
        """FR-AC-03: Test Generation.
        
        Automatically generate unit tests for modified code.

        Args:
            code: Code to generate tests for
            file_path: Original code file path
            framework: Testing framework (pytest, unittest)

        Returns:
            Generated test code
        """
        system_prompt = """You are an expert in writing comprehensive unit tests.
Generate high-quality test code that covers:
- Happy path scenarios
- Edge cases
- Error conditions
- Boundary values

Use best practices for the specified testing framework."""

        user_prompt = f"""
## Code to Test
```python
{code}
```

## Testing Framework
{framework}

## File Path
{file_path}

## Task
Generate comprehensive unit tests for this code.
Return ONLY the complete test code without explanations or markdown formatting.
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        
        response = self.llm.invoke(messages)
        test_code = response.content.strip()
        
        # Clean up markdown if present
        if test_code.startswith("```python"):
            test_code = re.sub(r"^```python\n", "", test_code)
            test_code = re.sub(r"\n```$", "", test_code)
        elif test_code.startswith("```"):
            test_code = re.sub(r"^```\n", "", test_code)
            test_code = re.sub(r"\n```$", "", test_code)
        
        return test_code

    async def refactor_with_tests(
        self,
        code: str,
        file_path: str | Path,
        related_docs: str | None = None,
    ) -> dict[str, Any]:
        """FR-AC-01: Refactoring Execution with automatic test generation.

        Args:
            code: Code to refactor
            file_path: Path to code file
            related_docs: Optional related documentation

        Returns:
            Refactoring result with code and tests
        """
        # First, ensure code works
        healing_result = await self.self_heal(
            code=code,
            file_path=file_path,
            related_docs=related_docs,
        )
        
        if not healing_result["success"]:
            return healing_result
        
        # Generate tests for working code
        test_code = await self.generate_unit_tests(
            code=healing_result["final_code"],
            file_path=file_path,
        )
        
        # Save test file
        test_file_path = Path(file_path).parent / f"test_{Path(file_path).name}"
        test_file_path.write_text(test_code)
        
        # Run tests
        test_result = await self.execute_code(
            code=test_code,
            file_path=test_file_path,
            test_command=f"pytest {test_file_path} -v",
        )
        
        return {
            "success": healing_result["success"],
            "code": healing_result["final_code"],
            "tests": test_code,
            "test_file": str(test_file_path),
            "test_passed": test_result.success,
            "healing_attempts": healing_result.get("attempts", 0),
        }
