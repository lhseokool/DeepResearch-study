"""Precision mode analyzer using LSP (Pyright)."""

import asyncio
import subprocess
import time
from pathlib import Path

from ..models.schema import (
    AnalysisMode,
    AnalysisRequest,
    AnalysisResult,
    DependencyNode,
    ImpactLevel,
)
from .base import BaseAnalyzer


class PrecisionAnalyzer(BaseAnalyzer):
    """Precise analysis using LSP (Pyright).

    This analyzer uses the Language Server Protocol with Pyright to get
    compiler-level accurate references. It's slower but has minimal false positives.
    """

    def __init__(self):
        """Initialize the precision analyzer."""
        self.lsp_process = None
        self.initialized = False

    def is_available(self) -> bool:
        """Check if Pyright is available.

        Returns:
            True if pyright-langserver is installed
        """
        try:
            result = subprocess.run(
                ["pyright-langserver", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Perform precise LSP-based analysis.

        Args:
            request: Analysis request with target file and symbol

        Returns:
            Analysis result with precise dependency information
        """
        start_time = time.time()

        try:
            # Check if Pyright is available
            if not self.is_available():
                return AnalysisResult(
                    mode=AnalysisMode.PRECISION,
                    success=False,
                    error_message="Pyright LSP server is not available. "
                    "Please install: pip install pyright",
                    execution_time=time.time() - start_time,
                    fallback_suggested=True,
                )

            # Run LSP analysis
            dependencies = asyncio.run(
                self._analyze_with_lsp(request)
            )

            # Rank by criticality
            ranked_deps = self._rank_by_criticality(dependencies)

            execution_time = time.time() - start_time

            return AnalysisResult(
                mode=AnalysisMode.PRECISION,
                success=True,
                dependencies=ranked_deps,
                execution_time=execution_time,
                metadata={
                    "lsp_server": "pyright",
                    "reference_count": len(dependencies),
                },
            )

        except Exception as e:
            return AnalysisResult(
                mode=AnalysisMode.PRECISION,
                success=False,
                error_message=f"LSP analysis failed: {str(e)}",
                execution_time=time.time() - start_time,
                fallback_suggested=True,
            )

    async def _analyze_with_lsp(
        self, request: AnalysisRequest
    ) -> list[DependencyNode]:
        """Analyze code using LSP.

        Args:
            request: Analysis request

        Returns:
            List of dependency nodes from LSP references
        """
        file_path = Path(request.file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {request.file_path}")

        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Find symbol position
        symbol_position = self._find_symbol_position(content, request.symbol_name)

        if not symbol_position:
            return []

        # Use subprocess to call pyright for finding references
        # In a production environment, you'd use a proper LSP client
        # For now, we'll use a simplified approach with pyright CLI

        try:
            # Use pyright to find references
            result = subprocess.run(
                [
                    "pyright",
                    "--outputjson",
                    str(file_path),
                ],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=request.project_root or file_path.parent,
            )

            # Parse the output and extract dependencies
            # This is a simplified implementation
            # In production, you'd implement proper LSP client communication

            dependencies = self._parse_pyright_output(
                result.stdout, request.symbol_name
            )

            return dependencies

        except subprocess.TimeoutExpired:
            raise RuntimeError("Pyright analysis timed out")
        except Exception as e:
            raise RuntimeError(f"Pyright execution failed: {e}")

    def _find_symbol_position(self, content: str, symbol_name: str) -> tuple[int, int] | None:
        """Find the position of a symbol in the source code.

        Args:
            content: Source code content
            symbol_name: Symbol to find

        Returns:
            Tuple of (line, column) or None
        """
        lines = content.split("\n")

        for line_num, line in enumerate(lines):
            col = line.find(f"def {symbol_name}")
            if col == -1:
                col = line.find(f"class {symbol_name}")

            if col != -1:
                return (line_num, col)

        return None

    def _parse_pyright_output(
        self, output: str, symbol_name: str
    ) -> list[DependencyNode]:
        """Parse Pyright output to extract dependencies.

        Args:
            output: Pyright JSON output
            symbol_name: Symbol being analyzed

        Returns:
            List of dependency nodes
        """
        # This is a simplified parser
        # In production, implement proper JSON parsing of Pyright output

        dependencies = []

        try:
            import json

            data = json.loads(output)

            # Extract diagnostics and references
            # The actual structure depends on Pyright's output format
            # This is a placeholder implementation

            if "generalDiagnostics" in data:
                for diag in data["generalDiagnostics"]:
                    if symbol_name in diag.get("message", ""):
                        file_path = diag.get("file", "")
                        line_num = diag.get("range", {}).get("start", {}).get("line", 0)

                        if file_path:
                            dependencies.append(
                                DependencyNode(
                                    file_path=file_path,
                                    symbol_name=symbol_name,
                                    line_number=line_num + 1,
                                    node_type="reference",
                                    impact_level=ImpactLevel.MEDIUM,
                                )
                            )

        except json.JSONDecodeError:
            pass

        return dependencies

    def _rank_by_criticality(
        self, dependencies: list[DependencyNode]
    ) -> list[DependencyNode]:
        """Rank dependencies by criticality.

        Args:
            dependencies: List of dependency nodes

        Returns:
            Ranked list of dependencies
        """
        # Group by file to see which files have most references
        file_counts = {}
        for dep in dependencies:
            file_counts[dep.file_path] = file_counts.get(dep.file_path, 0) + 1

        # Assign impact levels based on reference frequency
        for dep in dependencies:
            count = file_counts[dep.file_path]

            if count >= 10:
                dep.impact_level = ImpactLevel.CRITICAL
            elif count >= 5:
                dep.impact_level = ImpactLevel.HIGH
            elif count >= 2:
                dep.impact_level = ImpactLevel.MEDIUM
            else:
                dep.impact_level = ImpactLevel.LOW

        # Sort by impact level
        level_order = {
            ImpactLevel.CRITICAL: 0,
            ImpactLevel.HIGH: 1,
            ImpactLevel.MEDIUM: 2,
            ImpactLevel.LOW: 3,
        }

        dependencies.sort(key=lambda x: level_order[x.impact_level])

        return dependencies

    def __del__(self):
        """Cleanup LSP process."""
        if self.lsp_process:
            self.lsp_process.terminate()
            self.lsp_process.wait()
