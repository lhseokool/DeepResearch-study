"""Speed mode analyzer using Tree-sitter and NetworkX."""

import time
from pathlib import Path

import networkx as nx
from tree_sitter import Language, Parser
from tree_sitter_python import language

from ..models.schema import (
    AnalysisMode,
    AnalysisRequest,
    AnalysisResult,
    DependencyNode,
    ImpactLevel,
)
from .base import BaseAnalyzer


class SpeedAnalyzer(BaseAnalyzer):
    """Fast static analysis using Tree-sitter and NetworkX.

    This analyzer parses code into AST using Tree-sitter and builds a dependency
    graph using NetworkX. It's fast but may have false positives with dynamic typing.
    """

    def __init__(self):
        """Initialize the speed analyzer."""
        self.parser = Parser(Language(language()))
        self.dependency_graph = nx.DiGraph()

    def is_available(self) -> bool:
        """Check if speed analyzer is available.

        Returns:
            Always True as Tree-sitter doesn't require build environment
        """
        return True

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Perform fast static analysis.

        Args:
            request: Analysis request with target file and symbol

        Returns:
            Analysis result with dependency information
        """
        start_time = time.time()

        try:
            # Read the target file
            file_path = Path(request.file_path)
            if not file_path.exists():
                return AnalysisResult(
                    mode=AnalysisMode.SPEED,
                    success=False,
                    error_message=f"File not found: {request.file_path}",
                    execution_time=time.time() - start_time,
                )

            # Parse the file and build dependency graph
            self._build_dependency_graph(file_path, request.project_root)

            # Find dependencies of the target symbol
            dependencies = self._find_dependencies(
                request.file_path, request.symbol_name, request.max_depth
            )

            # Rank by criticality
            ranked_deps = self._rank_by_criticality(dependencies)

            execution_time = time.time() - start_time

            return AnalysisResult(
                mode=AnalysisMode.SPEED,
                success=True,
                dependencies=ranked_deps,
                execution_time=execution_time,
                metadata={
                    "total_nodes": self.dependency_graph.number_of_nodes(),
                    "total_edges": self.dependency_graph.number_of_edges(),
                    "max_depth": request.max_depth,
                },
            )

        except Exception as e:
            return AnalysisResult(
                mode=AnalysisMode.SPEED,
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time,
            )

    def _build_dependency_graph(
        self, file_path: Path, project_root: str | None
    ) -> None:
        """Build dependency graph from Python files.

        Args:
            file_path: Target file path
            project_root: Project root directory
        """
        # Determine project root
        root = Path(project_root) if project_root else file_path.parent

        # Parse all Python files in the project
        python_files = list(root.rglob("*.py"))

        for py_file in python_files:
            self._parse_file(py_file)

    def _parse_file(self, file_path: Path) -> None:
        """Parse a single Python file and extract dependencies.

        Args:
            file_path: Path to Python file
        """
        try:
            with open(file_path, "rb") as f:
                code = f.read()

            tree = self.parser.parse(code)
            self._extract_symbols(tree.root_node, str(file_path), code)

        except Exception:
            # Skip files that can't be parsed
            pass

    def _extract_symbols(self, node, file_path: str, code: bytes) -> None:
        """Extract symbols and their dependencies from AST node.

        Args:
            node: Tree-sitter AST node
            file_path: File path
            code: Source code bytes
        """
        if node.type == "function_definition":
            func_name = self._get_function_name(node)
            if func_name:
                node_id = f"{file_path}::{func_name}"
                self.dependency_graph.add_node(
                    node_id,
                    file_path=file_path,
                    symbol_name=func_name,
                    line_number=node.start_point[0] + 1,
                    node_type="function",
                )

                # Extract function calls within this function
                self._extract_calls(node, node_id, file_path)

        elif node.type == "class_definition":
            class_name = self._get_class_name(node)
            if class_name:
                node_id = f"{file_path}::{class_name}"
                self.dependency_graph.add_node(
                    node_id,
                    file_path=file_path,
                    symbol_name=class_name,
                    line_number=node.start_point[0] + 1,
                    node_type="class",
                )

        # Recursively process child nodes
        for child in node.children:
            self._extract_symbols(child, file_path, code)

    def _get_function_name(self, node) -> str | None:
        """Get function name from function definition node.

        Args:
            node: Function definition node

        Returns:
            Function name or None
        """
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode("utf-8")
        return None

    def _get_class_name(self, node) -> str | None:
        """Get class name from class definition node.

        Args:
            node: Class definition node

        Returns:
            Class name or None
        """
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode("utf-8")
        return None

    def _extract_calls(self, node, caller_id: str, file_path: str) -> None:
        """Extract function calls from a node.

        Args:
            node: AST node to search for calls
            caller_id: ID of the calling function
            file_path: Current file path
        """
        if node.type == "call":
            callee_name = self._get_call_name(node)
            if callee_name:
                # Create edges to all potential callees with this name
                for node_id in self.dependency_graph.nodes():
                    node_data = self.dependency_graph.nodes[node_id]
                    if node_data.get("symbol_name") == callee_name:
                        self.dependency_graph.add_edge(caller_id, node_id)

        for child in node.children:
            self._extract_calls(child, caller_id, file_path)

    def _get_call_name(self, node) -> str | None:
        """Get function/method name from call node.

        Args:
            node: Call node

        Returns:
            Function name or None
        """
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode("utf-8")
            elif child.type == "attribute":
                # For method calls like obj.method()
                for subchild in child.children:
                    if subchild.type == "identifier" and subchild != child.children[0]:
                        return subchild.text.decode("utf-8")
        return None

    def _find_dependencies(
        self, file_path: str, symbol_name: str, max_depth: int
    ) -> list[DependencyNode]:
        """Find all dependencies of a symbol.

        Args:
            file_path: File path containing the symbol
            symbol_name: Symbol to analyze
            max_depth: Maximum depth to traverse

        Returns:
            List of dependency nodes
        """
        source_id = f"{file_path}::{symbol_name}"

        if source_id not in self.dependency_graph:
            return []

        dependencies = []

        # Use BFS to find dependencies within max_depth
        visited = {source_id}
        queue = [(source_id, 0)]

        while queue:
            current_id, depth = queue.pop(0)

            if depth >= max_depth:
                continue

            # Get all nodes that depend on current node (reverse dependencies)
            for predecessor in self.dependency_graph.predecessors(current_id):
                if predecessor not in visited:
                    visited.add(predecessor)
                    queue.append((predecessor, depth + 1))

                    node_data = self.dependency_graph.nodes[predecessor]
                    dependencies.append(
                        DependencyNode(
                            file_path=node_data["file_path"],
                            symbol_name=node_data["symbol_name"],
                            line_number=node_data.get("line_number"),
                            node_type=node_data["node_type"],
                            impact_level=ImpactLevel.MEDIUM,  # Will be ranked later
                        )
                    )

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
        # Calculate criticality based on:
        # 1. Number of incoming edges (how many things depend on it)
        # 2. Number of outgoing edges (how many things it depends on)

        for dep in dependencies:
            node_id = f"{dep.file_path}::{dep.symbol_name}"

            if node_id in self.dependency_graph:
                in_degree = self.dependency_graph.in_degree(node_id)
                out_degree = self.dependency_graph.out_degree(node_id)

                # Higher in-degree means more critical
                if in_degree >= 5:
                    dep.impact_level = ImpactLevel.CRITICAL
                elif in_degree >= 3:
                    dep.impact_level = ImpactLevel.HIGH
                elif in_degree >= 1:
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
