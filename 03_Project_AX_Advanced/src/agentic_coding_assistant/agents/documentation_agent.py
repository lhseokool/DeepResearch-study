"""Documentation Synchronization Agent.

FR-DS-01: Automatically detect and update documentation when code changes.
"""

import ast
import re
import difflib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from langchain_core.messages import HumanMessage

from ..utils.openrouter_llm import create_openrouter_llm


@dataclass
class DocumentationUpdate:
    """Proposed documentation update."""

    doc_type: str  # docstring, readme, swagger, etc.
    file_path: str
    current_content: str
    proposed_content: str
    reason: str


class DocumentationAgent:
    """Agent for automatic documentation synchronization.
    
    When code changes, this agent:
    1. Detects affected documentation (Docstring, README, Swagger)
    2. Generates update proposals
    3. Applies updates or requests human approval
    """

    def __init__(
        self,
        model: str = "openai/gpt-4.1",
        temperature: float = 0,
    ):
        """Initialize Documentation Agent.

        Args:
            model: LLM model name (OpenRouter format: provider/model)
            temperature: Temperature for LLM
        """
        self.llm = create_openrouter_llm(model=model, temperature=temperature)

    def analyze_code_changes(
        self,
        old_code: str,
        new_code: str,
        file_path: str,
    ) -> dict[str, Any]:
        """Analyze what changed in the code.

        Args:
            old_code: Original code
            new_code: Modified code
            file_path: Path to the file

        Returns:
            Analysis of changes
        """
        changes = {
            "file_path": file_path,
            "functions_changed": [],
            "classes_changed": [],
            "imports_changed": [],
            "docstrings_changed": [],
        }
        
        try:
            old_tree = ast.parse(old_code)
            new_tree = ast.parse(new_code)
            
            old_functions = {
                node.name: ast.get_docstring(node)
                for node in ast.walk(old_tree)
                if isinstance(node, ast.FunctionDef)
            }
            new_functions = {
                node.name: ast.get_docstring(node)
                for node in ast.walk(new_tree)
                if isinstance(node, ast.FunctionDef)
            }
            
            # Detect function changes
            for func_name, old_doc in old_functions.items():
                if func_name in new_functions:
                    if new_functions[func_name] != old_doc:
                        changes["functions_changed"].append(func_name)
                        changes["docstrings_changed"].append({
                            "function": func_name,
                            "old_docstring": old_doc,
                            "new_docstring": new_functions[func_name],
                        })
            
            # Detect new functions
            for func_name in new_functions:
                if func_name not in old_functions:
                    changes["functions_changed"].append(func_name)
            
            # Detect class changes
            old_classes = {
                node.name for node in ast.walk(old_tree)
                if isinstance(node, ast.ClassDef)
            }
            new_classes = {
                node.name for node in ast.walk(new_tree)
                if isinstance(node, ast.ClassDef)
            }
            changes["classes_changed"] = list(new_classes - old_classes)
            
        except SyntaxError:
            changes["error"] = "Failed to parse code"
        
        return changes

    async def detect_documentation_needs(
        self,
        code_changes: dict[str, Any],
        project_root: Path,
    ) -> list[DocumentationUpdate]:
        """FR-DS-01: Detect which documentation needs updating.

        Args:
            code_changes: Analysis of code changes
            project_root: Root directory of project

        Returns:
            List of required documentation updates
        """
        updates: list[DocumentationUpdate] = []
        file_path = code_changes["file_path"]
        
        # 1. Check docstrings
        if code_changes["docstrings_changed"]:
            for change in code_changes["docstrings_changed"]:
                if not change["new_docstring"]:
                    updates.append(DocumentationUpdate(
                        doc_type="docstring",
                        file_path=file_path,
                        current_content=change["old_docstring"] or "",
                        proposed_content="",  # To be generated
                        reason=f"Function '{change['function']}' missing docstring",
                    ))
        
        # 2. Check README
        readme_path = project_root / "README.md"
        if readme_path.exists() and (
            code_changes["functions_changed"] or code_changes["classes_changed"]
        ):
            current_readme = readme_path.read_text()
            
            # Check if changed functions/classes are mentioned in README
            needs_readme_update = False
            for func in code_changes["functions_changed"]:
                if func in current_readme:
                    needs_readme_update = True
                    break
            
            if needs_readme_update:
                updates.append(DocumentationUpdate(
                    doc_type="readme",
                    file_path=str(readme_path),
                    current_content=current_readme,
                    proposed_content="",  # To be generated
                    reason="Changed functions/classes mentioned in README",
                ))
        
        # 3. Check Swagger/API documentation
        if self._is_api_file(file_path):
            api_doc_path = project_root / "docs" / "api.md"
            if api_doc_path.exists():
                updates.append(DocumentationUpdate(
                    doc_type="swagger",
                    file_path=str(api_doc_path),
                    current_content=api_doc_path.read_text(),
                    proposed_content="",  # To be generated
                    reason="API endpoints changed",
                ))
        
        return updates

    def _is_api_file(self, file_path: str) -> bool:
        """Check if file contains API definitions.

        Args:
            file_path: Path to check

        Returns:
            True if file appears to be API-related
        """
        api_patterns = ["api", "route", "endpoint", "views"]
        return any(pattern in file_path.lower() for pattern in api_patterns)

    async def generate_docstring(
        self,
        function_code: str,
        function_name: str,
        style: str = "google",
    ) -> str:
        """Generate docstring for a function.

        Args:
            function_code: Function source code
            function_name: Name of the function
            style: Docstring style (google, numpy, sphinx)

        Returns:
            Generated docstring
        """
        system_prompt = f"""You are an expert at writing clear, comprehensive {style}-style docstrings.

Generate a docstring that includes:
- Brief description
- Args section
- Returns section
- Raises section (if applicable)
- Example usage (if helpful)

Return ONLY the docstring content without quotes or formatting."""

        user_prompt = f"""
## Function Code
```python
{function_code}
```

## Function Name
{function_name}

## Task
Generate a {style}-style docstring for this function.
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        
        response = self.llm.invoke(messages)
        return response.content.strip()

    async def update_readme(
        self,
        current_readme: str,
        code_changes: dict[str, Any],
    ) -> str:
        """Generate updated README content.

        Args:
            current_readme: Current README content
            code_changes: Analysis of code changes

        Returns:
            Updated README content
        """
        system_prompt = """You are an expert at writing clear, user-friendly documentation.
Update the README to reflect code changes while preserving the overall structure and style.

Focus on:
- Updating API references
- Modifying examples if needed
- Keeping the tone consistent
- Preserving existing sections that are still relevant"""

        user_prompt = f"""
## Current README
```markdown
{current_readme}
```

## Code Changes
- Functions changed: {', '.join(code_changes['functions_changed'])}
- Classes changed: {', '.join(code_changes['classes_changed'])}

## Task
Update the README to reflect these code changes.
Return the complete updated README.
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        
        response = self.llm.invoke(messages)
        return response.content.strip()

    async def update_api_documentation(
        self,
        current_doc: str,
        code_changes: dict[str, Any],
    ) -> str:
        """Generate updated API documentation.

        Args:
            current_doc: Current API documentation
            code_changes: Analysis of code changes

        Returns:
            Updated API documentation
        """
        system_prompt = """You are an expert at writing API documentation in OpenAPI/Swagger format.
Update the documentation to reflect API changes while maintaining proper formatting."""

        user_prompt = f"""
## Current API Documentation
```
{current_doc}
```

## Code Changes
- Functions changed: {', '.join(code_changes['functions_changed'])}
- Classes changed: {', '.join(code_changes['classes_changed'])}

## Task
Update the API documentation to reflect these changes.
Include request/response schemas, endpoints, and examples.
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        
        response = self.llm.invoke(messages)
        return response.content.strip()

    async def synchronize_documentation(
        self,
        old_code: str,
        new_code: str,
        file_path: str,
        project_root: Path,
        auto_apply: bool = False,
    ) -> dict[str, Any]:
        """FR-DS-01: Main documentation synchronization workflow.

        Args:
            old_code: Original code
            new_code: Modified code
            file_path: Path to the changed file
            project_root: Project root directory
            auto_apply: Whether to automatically apply updates

        Returns:
            Synchronization result with proposed updates
        """
        # 1. Analyze code changes
        changes = self.analyze_code_changes(old_code, new_code, file_path)
        
        # 2. Detect documentation needs
        updates_needed = await self.detect_documentation_needs(changes, project_root)
        
        if not updates_needed:
            return {
                "success": True,
                "updates_needed": 0,
                "message": "No documentation updates required",
            }
        
        # 3. Generate update proposals
        proposed_updates = []
        
        for update in updates_needed:
            if update.doc_type == "docstring":
                # Generate docstring
                proposed_content = await self.generate_docstring(
                    function_code=new_code,
                    function_name=update.file_path,  # Simplified
                )
                update.proposed_content = proposed_content
                
            elif update.doc_type == "readme":
                # Update README
                proposed_content = await self.update_readme(
                    current_readme=update.current_content,
                    code_changes=changes,
                )
                update.proposed_content = proposed_content
                
            elif update.doc_type == "swagger":
                # Update API documentation
                proposed_content = await self.update_api_documentation(
                    current_doc=update.current_content,
                    code_changes=changes,
                )
                update.proposed_content = proposed_content
            
            proposed_updates.append({
                "type": update.doc_type,
                "file": update.file_path,
                "reason": update.reason,
                "current_preview": update.current_content[:200] + "...",
                "proposed_preview": update.proposed_content[:200] + "...",
                "full_proposed": update.proposed_content,
            })
        
        # 4. Apply updates if auto_apply is True
        applied_updates = []
        if auto_apply:
            for i, update in enumerate(updates_needed):
                try:
                    file_path = Path(update.file_path)
                    if update.doc_type == "docstring":
                        # Update docstring in code file
                        # This is simplified - in practice, use AST manipulation
                        pass
                    else:
                        # Update external documentation file
                        file_path.write_text(update.proposed_content)
                    
                    applied_updates.append(proposed_updates[i])
                except Exception as e:
                    proposed_updates[i]["error"] = str(e)
        
        return {
            "success": True,
            "updates_needed": len(updates_needed),
            "proposed_updates": proposed_updates,
            "applied_updates": applied_updates if auto_apply else [],
            "auto_applied": auto_apply,
            "message": f"Generated {len(proposed_updates)} documentation update(s)",
        }
