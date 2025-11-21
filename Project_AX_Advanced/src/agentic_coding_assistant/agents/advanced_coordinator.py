"""Advanced Coordinator integrating all DeepAgent capabilities.

Integrates:
- FileSystem Agent (FR-FS-01 to FR-FS-04)
- Self-Healing Agent (FR-AC-01 to FR-AC-03)
- Documentation Agent (FR-DS-01)
- Impact Analysis Coordinator (existing)
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph

from ..configuration import DeepAgentConfiguration
from ..subagents import (
    create_analyzer_subagent,
    create_documenter_subagent,
    create_refactorer_subagent,
)
from ..utils.openrouter_llm import create_openrouter_llm
from ..utils.workspace import get_agent_workspace
from .documentation_agent import DocumentationAgent
from .filesystem_agent import FileSystemAgent
from .self_healing_agent import SelfHealingAgent


class AdvancedCoordinator:
    """Advanced coordinator using all DeepAgent patterns.
    
    Orchestrates:
    1. Impact Analysis (existing functionality)
    2. File System Exploration (FR-FS)
    3. Self-Healing Code Generation (FR-AC)
    4. Documentation Synchronization (FR-DS)
    """

    def __init__(
        self,
        project_root: str | Path,
        model: str = "openai/gpt-4.1",
        temperature: float = 0,
    ):
        """Initialize Advanced Coordinator.

        Args:
            project_root: Root directory of the project
            model: LLM model name (OpenRouter format: provider/model)
            temperature: Temperature for LLM
        """
        self.project_root = Path(project_root).resolve()
        self.llm = create_openrouter_llm(model=model, temperature=temperature)
        
        # Initialize specialized agents
        self.fs_agent = FileSystemAgent(
            work_dir=self.project_root,
            model=model,
            temperature=temperature,
        )
        self.healing_agent = SelfHealingAgent(
            model=model,
            temperature=temperature,
            work_dir=self.project_root,
        )
        self.doc_agent = DocumentationAgent(
            model=model,
            temperature=temperature,
        )

    def explore_project(self, target_path: str | None = None) -> dict[str, Any]:
        """FR-FS-01: Explore project structure and context.

        Args:
            target_path: Optional specific path to explore

        Returns:
            Project context information
        """
        return self.fs_agent.explore_context(target_path)

    def search_code(
        self,
        pattern: str | None = None,
        query: str | None = None,
        extension: str | None = None,
    ) -> dict[str, Any]:
        """FR-FS-02: Search code using patterns or grep.

        Args:
            pattern: Glob pattern (e.g., "**/*.py")
            query: String to search for
            extension: File extension filter

        Returns:
            Search results
        """
        return self.fs_agent.pattern_search(pattern, query, extension)

    def modify_code_precise(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
    ) -> dict[str, Any]:
        """FR-FS-03: Precisely modify code with string replacement.

        Args:
            file_path: Path to file
            old_string: String to replace
            new_string: Replacement string

        Returns:
            Modification result
        """
        return self.fs_agent.modify_code(file_path, old_string, new_string)

    async def refactor_with_healing(
        self,
        code: str,
        file_path: str | Path,
        related_docs: str | None = None,
        human_callback: Callable[[str], bool] | None = None,
    ) -> dict[str, Any]:
        """FR-AC-01, FR-AC-02, FR-AC-03: Complete refactoring workflow.
        
        Workflow:
        1. Apply self-healing loop (max 3 retries)
        2. Generate unit tests
        3. Run tests and verify
        4. Request human approval if needed

        Args:
            code: Code to refactor
            file_path: Path to code file
            related_docs: Optional documentation
            human_callback: Optional callback for human-in-the-loop

        Returns:
            Complete refactoring result
        """
        print("🚀 Starting refactoring with self-healing...")
        
        # Execute refactoring with tests
        result = await self.healing_agent.refactor_with_tests(
            code=code,
            file_path=file_path,
            related_docs=related_docs,
        )
        
        # If healing failed, request human intervention
        if not result["success"] and human_callback:
            user_decision = human_callback(
                f"Self-healing failed after {result.get('attempts', 0)} attempts.\n"
                f"Last error: {result.get('last_error')}\n"
                f"Continue with partially healed code? (yes/no)"
            )
            
            result["human_intervened"] = True
            result["human_decision"] = user_decision
        
        return result

    async def synchronize_documentation(
        self,
        old_code: str,
        new_code: str,
        file_path: str,
        auto_apply: bool = False,
    ) -> dict[str, Any]:
        """FR-DS-01: Synchronize documentation with code changes.

        Args:
            old_code: Original code
            new_code: Modified code
            file_path: Path to changed file
            auto_apply: Whether to automatically apply updates

        Returns:
            Documentation synchronization result
        """
        return await self.doc_agent.synchronize_documentation(
            old_code=old_code,
            new_code=new_code,
            file_path=file_path,
            project_root=self.project_root,
            auto_apply=auto_apply,
        )

    async def handle_large_file(
        self,
        file_path: str,
        human_callback: Callable[[str], bool] | None = None,
    ) -> dict[str, Any]:
        """FR-FS-04: Handle large file with human-in-the-loop.

        Args:
            file_path: Path to large file
            human_callback: Callback for human approval

        Returns:
            File handling result
        """
        # Read file with automatic size detection
        result = await self.fs_agent.read_file_safe(file_path)
        
        # If large file detected and human callback provided
        if result.get("human_in_loop_required") and human_callback:
            user_decision = human_callback(
                f"Large file detected ({result['tokens']} tokens).\n"
                f"Saved to: {result['saved_to']}\n"
                f"Summary: {result['summary']}\n\n"
                f"Process full file? (yes/no)"
            )
            
            result["human_decision"] = user_decision
            
            if user_decision:
                # Read full file if user approves
                full_content = await self.fs_agent.fs_backend.read_file(file_path)
                result["full_content"] = full_content
        
        return result

    async def complete_workflow(
        self,
        user_request: str,
        target_files: list[str] | None = None,
        human_callback: Callable[[str], bool] | None = None,
    ) -> dict[str, Any]:
        """Complete end-to-end workflow.
        
        Workflow:
        1. Explore project context (FR-FS-01)
        2. Search and identify target files (FR-FS-02)
        3. Generate and heal code (FR-AC-01, FR-AC-02)
        4. Generate tests (FR-AC-03)
        5. Synchronize documentation (FR-DS-01)
        6. Handle large outputs (FR-FS-04)

        Args:
            user_request: User's refactoring request
            target_files: Optional list of target files
            human_callback: Optional human-in-the-loop callback

        Returns:
            Complete workflow result
        """
        workflow_result = {
            "request": user_request,
            "steps": [],
        }
        
        # Step 1: Explore context
        print("\n📂 Step 1: Exploring project context...")
        context = await self.explore_project()
        workflow_result["steps"].append({
            "name": "explore_context",
            "result": context,
        })
        
        # Step 2: Identify target files
        print("\n🔍 Step 2: Identifying target files...")
        if not target_files:
            # Use LLM to determine which files to modify
            search_result = await self.search_code(pattern="**/*.py")
            target_files = search_result.get("glob_results", [])[:5]  # Limit to 5 files
        
        workflow_result["target_files"] = target_files
        
        # Step 3-5: Process each file
        processed_files = []
        for file_path in target_files:
            print(f"\n⚙️  Processing: {file_path}")
            
            # Read original code
            file_result = await self.fs_agent.read_file_safe(str(file_path))
            
            if file_result.get("type") == "large_file":
                # Handle large file with human approval
                large_file_result = await self.handle_large_file(
                    file_path=str(file_path),
                    human_callback=human_callback,
                )
                
                if not large_file_result.get("human_decision", False):
                    print(f"⏭️  Skipping large file: {file_path}")
                    continue
                
                original_code = large_file_result.get("full_content", "")
            else:
                original_code = file_result.get("content", "")
            
            # Generate modified code (simplified - in practice, use LLM)
            # This would normally involve analyzing user_request and generating new code
            modified_code = original_code  # Placeholder
            
            # Apply self-healing
            healing_result = await self.refactor_with_healing(
                code=modified_code,
                file_path=file_path,
                human_callback=human_callback,
            )
            
            # Synchronize documentation
            if healing_result["success"]:
                doc_result = await self.synchronize_documentation(
                    old_code=original_code,
                    new_code=healing_result["code"],
                    file_path=str(file_path),
                    auto_apply=False,  # Always request human approval for docs
                )
                
                processed_files.append({
                    "file": str(file_path),
                    "healing": healing_result,
                    "documentation": doc_result,
                })
        
        workflow_result["processed_files"] = processed_files
        workflow_result["success"] = len(processed_files) > 0
        
        return workflow_result

    async def create_deep_advanced_coordinator(
        self,
        tools: list[Any],
        *,
        config: Optional[RunnableConfig] = None,
        checkpointer=None,
    ) -> CompiledStateGraph:
        """Create a DeepAgent-based advanced coordinator.

        This creates a comprehensive coordinator with all sub-agents:
        - Analyzer: Code analysis and impact detection
        - Refactorer: Code refactoring with self-healing
        - Documenter: Documentation synchronization

        Args:
            tools: List of tool objects
            config: Optional runtime configuration
            checkpointer: Checkpointer for session persistence (default: MemorySaver)

        Returns:
            Compiled LangGraph agent ready for execution
        """
        from langgraph.checkpoint.memory import MemorySaver

        # Default checkpointer
        if checkpointer is None:
            checkpointer = MemorySaver()

        # Get current date for prompts
        now = datetime.now()
        date = f"{now:%a} {now:%b} {now.day}, {now:%Y}"

        # Create sub-agent configurations
        analyzer_config = create_analyzer_subagent(tools=tools, date=date)
        refactorer_config = create_refactorer_subagent(tools=tools, date=date)
        documenter_config = create_documenter_subagent(date=date)

        # Sub-agents list
        subagents = [analyzer_config, refactorer_config, documenter_config]

        # Orchestrator system prompt
        orchestrator_prompt = f"""You are an advanced coding assistant coordinator.

Your role is to orchestrate a complete development workflow:
1. Analyze code for impact and dependencies (use analyzer sub-agent)
2. Refactor code with self-healing and testing (use refactorer sub-agent)
3. Synchronize documentation with code changes (use documenter sub-agent)

Available sub-agents:
- analyzer: Deep code analysis and impact detection
- refactorer: Code refactoring with automated testing and self-healing
- documenter: Documentation synchronization and updates

Current date: {date}
Project root: {self.project_root}

Coordinate these sub-agents to provide comprehensive coding assistance.
Always ensure code quality through testing and maintain documentation accuracy.
"""

        # Create DeepAgent
        agent = create_deep_agent(
            model=self.llm.model_name if hasattr(self.llm, 'model_name') else "openai:gpt-4.1",
            tools=tools,
            system_prompt=orchestrator_prompt,
            subagents=subagents,
            backend=lambda rt: FilesystemBackend(
                root_dir=get_agent_workspace("advanced_coordinator"),
                virtual_mode=True,
            ),
            checkpointer=checkpointer,
            name="AdvancedCoordinator",
            debug=True,
        )

        return agent


async def demo_advanced_coordinator():
    """Demo function showing complete workflow."""
    coordinator = AdvancedCoordinator(
        project_root="/Users/hseokool/Desktop/src/project-ax-advanced",
    )
    
    # Example: Explore project
    context = await coordinator.explore_project()
    print("Project Context:", context)
    
    # Example: Search for Python files
    search_result = await coordinator.search_code(pattern="**/*.py")
    print("\nPython Files:", search_result)
    
    # Example: Generate and heal code
    sample_code = '''
def calculate_sum(a, b):
    return a + b  # Missing type hints and docstring
'''
    
    healing_result = await coordinator.refactor_with_healing(
        code=sample_code,
        file_path="sample_function.py",
    )
    print("\nHealing Result:", healing_result)


if __name__ == "__main__":
    asyncio.run(demo_advanced_coordinator())
