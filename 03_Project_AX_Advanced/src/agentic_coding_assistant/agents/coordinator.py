"""DeepAgent-based coordinator for impact analysis.

This module implements the DeepAgent pattern with:
- Planning: Decide which analysis mode to use
- FileSystem: Access and analyze code files
- SubAgent: Delegate to SPEED or PRECISION analyzers
"""

from datetime import datetime
from typing import Any, Optional

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph

from ..analyzers import PrecisionAnalyzer, SpeedAnalyzer
from ..configuration import DeepAgentConfiguration
from ..models.schema import AnalysisMode, AnalysisRequest, AnalysisResult
from ..subagents import create_analyzer_subagent
from ..utils.openrouter_llm import create_openrouter_llm
from ..utils.workspace import get_agent_workspace


def get_today_str() -> str:
    """Format current date for prompts.

    Returns:
        Human-readable date string like 'Mon Jan 15, 2024'
    """
    now = datetime.now()
    return f"{now:%a} {now:%b} {now.day}, {now:%Y}"


class ImpactAnalysisCoordinator:
    """Coordinator using DeepAgent pattern for impact analysis.

    Implements:
    - Planning: Creates analysis plan based on mode selection
    - FileSystem: Accesses code files for analysis
    - SubAgent: Delegates to appropriate analyzer
    """

    def __init__(
        self,
        model: str = "openai/gpt-4.1-mini",
        temperature: float = 0,
        project_root: Optional[str] = None,
    ):
        """Initialize the coordinator.

        Args:
            model: LLM model name (OpenRouter format: provider/model)
            temperature: Temperature for LLM
            project_root: Root directory of the project to analyze
        """
        self.llm = create_openrouter_llm(model=model, temperature=temperature)
        self.speed_analyzer = SpeedAnalyzer()
        self.precision_analyzer = PrecisionAnalyzer()
        self.project_root = project_root
        self.model = model

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Coordinate impact analysis using DeepAgent pattern.

        Args:
            request: Analysis request

        Returns:
            Analysis result
        """
        # Step 1: Planning - decide on analysis strategy
        plan = self._create_plan(request)

        # Step 2: FileSystem - verify file access
        if not self._verify_file_access(request.file_path):
            return AnalysisResult(
                mode=request.mode,
                success=False,
                error_message=f"Cannot access file: {request.file_path}",
                execution_time=0.0,
            )

        # Step 3: SubAgent - delegate to appropriate analyzer
        result = self._execute_with_subagent(request, plan)

        # Step 4: Handle fallback if needed
        if result.fallback_suggested and request.mode == AnalysisMode.PRECISION:
            fallback_request = AnalysisRequest(
                mode=AnalysisMode.SPEED,
                file_path=request.file_path,
                symbol_name=request.symbol_name,
                project_root=request.project_root,
                max_depth=request.max_depth,
            )
            result = self._execute_with_subagent(fallback_request, plan)
            result.metadata["fallback_executed"] = True

        return result

    def _create_plan(self, request: AnalysisRequest) -> dict[str, Any]:
        """Create analysis plan using Planning pattern.

        Args:
            request: Analysis request

        Returns:
            Plan dictionary with strategy
        """
        # Use LLM to create analysis plan
        planning_prompt = f"""
        Create an analysis plan for impact analysis:
        
        Mode: {request.mode.value}
        File: {request.file_path}
        Symbol: {request.symbol_name}
        Max Depth: {request.max_depth}
        
        Determine:
        1. Is the mode appropriate for this analysis?
        2. What are the potential challenges?
        3. Should we consider fallback?
        
        Return a brief plan.
        """

        response = self.llm.invoke([HumanMessage(content=planning_prompt)])

        plan = {
            "mode": request.mode,
            "strategy": response.content,
            "fallback_ready": request.mode == AnalysisMode.PRECISION,
        }

        return plan

    def _verify_file_access(self, file_path: str) -> bool:
        """Verify file access using FileSystem pattern.

        Args:
            file_path: Path to verify

        Returns:
            True if file is accessible
        """
        from pathlib import Path

        try:
            path = Path(file_path)
            return path.exists() and path.is_file()
        except Exception:
            return False

    def _execute_with_subagent(
        self, request: AnalysisRequest, plan: dict[str, Any]
    ) -> AnalysisResult:
        """Execute analysis using SubAgent pattern.

        Args:
            request: Analysis request
            plan: Analysis plan

        Returns:
            Analysis result
        """
        if request.mode == AnalysisMode.SPEED:
            return self.speed_analyzer.analyze(request)
        elif request.mode == AnalysisMode.PRECISION:
            # Check if precision analyzer is available
            if not self.precision_analyzer.is_available():
                result = AnalysisResult(
                    mode=AnalysisMode.PRECISION,
                    success=False,
                    error_message="Precision analyzer not available",
                    execution_time=0.0,
                    fallback_suggested=True,
                )
                return result

            return self.precision_analyzer.analyze(request)
        else:
            return AnalysisResult(
                mode=request.mode,
                success=False,
                error_message=f"Unknown mode: {request.mode}",
                execution_time=0.0,
            )

    def analyze_with_human_in_loop(
        self, request: AnalysisRequest, human_input_callback=None
    ) -> AnalysisResult:
        """Analyze with human-in-the-loop capability.

        Args:
            request: Analysis request
            human_input_callback: Callback function for human input

        Returns:
            Analysis result with potential human intervention
        """
        # First attempt with requested mode
        result = self.analyze(request)

        # If failed and fallback suggested, ask human
        if not result.success and result.fallback_suggested:
            should_fallback = True

            if human_input_callback:
                should_fallback = human_input_callback(
                    f"Analysis failed: {result.error_message}\n"
                    f"Switch to SPEED mode? (yes/no)"
                )

            if should_fallback:
                fallback_request = AnalysisRequest(
                    mode=AnalysisMode.SPEED,
                    file_path=request.file_path,
                    symbol_name=request.symbol_name,
                    project_root=request.project_root,
                    max_depth=request.max_depth,
                )
                result = self.analyze(fallback_request)
                result.metadata["human_approved_fallback"] = True

        return result

    async def create_deep_coordinator(
        self,
        tools: list[Any],
        *,
        config: Optional[RunnableConfig] = None,
        checkpointer=None,
    ) -> CompiledStateGraph:
        """Create a DeepAgent-based coordinator for impact analysis.

        Args:
            tools: List of tool objects for analysis
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
        date = get_today_str()

        # Create analyzer sub-agent configuration
        analyzer_config = create_analyzer_subagent(
            tools=tools,
            date=date,
        )

        # Sub-agents list
        subagents = [analyzer_config]

        # Orchestrator system prompt
        orchestrator_prompt = f"""You are an intelligent code analysis coordinator.

Your role is to:
1. Understand user requests for code analysis and impact assessment
2. Delegate analysis tasks to specialized analyzer sub-agents
3. Coordinate multiple analyzers for comprehensive analysis
4. Synthesize results into actionable insights

You can delegate to the following sub-agents:
- analyzer: For deep code analysis and impact detection

Current date: {date}
Project root: {self.project_root or 'Not specified'}

Use the analyzer sub-agent to perform detailed code analysis when needed.
Provide clear, actionable insights based on the analysis results.
"""

        # Create DeepAgent
        agent = create_deep_agent(
            model=self.model,
            tools=tools,
            system_prompt=orchestrator_prompt,
            subagents=subagents,
            backend=lambda rt: FilesystemBackend(
                root_dir=get_agent_workspace("coordinator"),
                virtual_mode=True,
            ),
            checkpointer=checkpointer,
            name="ImpactAnalysisCoordinator",
            debug=True,
        )

        return agent
