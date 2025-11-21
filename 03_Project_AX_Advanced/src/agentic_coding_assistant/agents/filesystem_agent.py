"""FileSystem Agent using DeepAgents Library with create_deep_agent.

FR-FS-01: Contextual Exploration
FR-FS-02: Pattern-based Search
FR-FS-03: Precise Code Modification
FR-FS-04: Large Output Handling

This agent uses create_deep_agent to leverage DeepAgent patterns:
- Planning: Automatic task decomposition
- FileSystem: Built-in FileSystemBackend tools (ls, read_file, glob, grep, edit_file, write_file)
- SubAgent: Can spawn specialized agents for complex tasks
"""

from pathlib import Path
from typing import Any, Callable

from deepagents import create_deep_agent
from langchain_core.messages import HumanMessage


# System prompt for FileSystem Agent
FILESYSTEM_AGENT_PROMPT = """You are an expert filesystem agent specialized in code exploration and manipulation.

Note: You are using OpenRouter API with multiple model providers available.

Your capabilities:
1. **Contextual Exploration (FR-FS-01)**: Understand project structure and provide insights
2. **Pattern Search (FR-FS-02)**: Find files and code patterns efficiently
3. **Precise Modification (FR-FS-03)**: Edit code with exact string replacement
4. **Large Output Handling (FR-FS-04)**: Summarize large files and save to disk

You have access to these filesystem tools (automatically provided by FileSystemBackend):
- `ls`: List directory contents
- `read_file`: Read file contents
- `glob`: Pattern-based file search (e.g., "**/*.py")
- `grep`: Search string in files
- `edit_file`: Precise string replacement in files
- `write_file`: Create new files

When exploring:
1. Start with `ls` to understand structure
2. Use `glob` or `grep` to find relevant files
3. Use `read_file` to examine contents
4. Provide clear, actionable insights

When modifying:
1. Always verify file exists first
2. Use exact string matching for `edit_file`
3. Create backups for critical changes
4. Report success/failure clearly

For large outputs (>4000 tokens):
1. Save to file using `write_file`
2. Provide concise summary
3. Include file path in response
"""


class FileSystemAgent:
    """Agent for deep filesystem exploration using create_deep_agent.
    
    Uses DeepAgents Library's create_deep_agent with built-in FileSystemBackend.
    This provides automatic Planning, FileSystem context management, and SubAgent capabilities.
    """

    def __init__(
        self,
        work_dir: str | Path,
        model: str = "gpt-4o-mini",
        temperature: float = 0,
        max_token_output: int = 4000,
        additional_tools: list[Callable] | None = None,
    ):
        """Initialize FileSystem Agent using create_deep_agent.

        Args:
            work_dir: Working directory path (execution path)
            model: LLM model name
            temperature: Temperature for LLM
            max_token_output: Maximum token output for large files
            additional_tools: Optional additional custom tools
        """
        self.work_dir = Path(work_dir).resolve()
        self.max_token_output = max_token_output
        
        # Create deep agent with FileSystemBackend (automatically included)
        # The FileSystemBackend tools are added automatically when using create_deep_agent
        # Note: create_deep_agent uses the model parameter directly (OpenRouter format)
        self.agent = create_deep_agent(
            system_prompt=FILESYSTEM_AGENT_PROMPT,
            model=model,  # OpenRouter format: provider/model (e.g., openai/gpt-4.1-mini)
            tools=additional_tools or [],  # Custom tools if needed
            # FileSystemBackend is automatically included by create_deep_agent
        )
        
        # Store config for backward compatibility
        self.model = model
        self.temperature = temperature

    def explore_context(self, target_path: str | None = None) -> dict[str, Any]:
        """FR-FS-01: Contextual Exploration.
        
        Explore directory structure to understand development context.

        Args:
            target_path: Optional specific path to explore

        Returns:
            Context information dictionary
        """
        path = target_path or "."
        
        # Use DeepAgent to explore and provide insights
        prompt = f"""
        Explore the directory at path: {path}
        
        Tasks:
        1. List the directory structure using `ls`
        2. Identify:
           - Project type (web, library, script, etc.)
           - Key configuration files (pyproject.toml, setup.py, etc.)
           - Source code structure
           - Test directories
           - Documentation files
        3. Provide actionable insights about the project
        
        Return a structured analysis.
        """
        
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": prompt}]
        })
        
        # Extract response from agent
        response_content = result["messages"][-1].content
        
        return {
            "path": path,
            "insights": response_content,
            "agent_used": "create_deep_agent",
        }

    def pattern_search(
        self,
        pattern: str | None = None,
        query: str | None = None,
        extension: str | None = None,
    ) -> dict[str, Any]:
        """FR-FS-02: Pattern-based Search.
        
        Search files using glob patterns or grep for string matching.

        Args:
            pattern: Glob pattern (e.g., "**/*.py")
            query: String to search for (grep)
            extension: File extension filter

        Returns:
            Search results
        """
        # Build search instructions for DeepAgent
        search_tasks = []
        if pattern:
            search_tasks.append(f"- Use `glob` to find files matching: {pattern}")
        if query:
            ext_filter = f" (filter by *.{extension})" if extension else ""
            search_tasks.append(f"- Use `grep` to search for: \"{query}\"{ext_filter}")
        
        if not search_tasks:
            return {"error": "No search criteria provided"}
        
        prompt = f"""
        Search the codebase:
        
        {chr(10).join(search_tasks)}
        
        Then analyze the results:
        1. Total files found
        2. Key patterns or commonalities
        3. Most relevant files to modify
        4. Suggested next steps
        
        Provide a clear summary.
        """
        
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": prompt}]
        })
        
        return {
            "search_criteria": {"pattern": pattern, "query": query, "extension": extension},
            "results": result["messages"][-1].content,
            "agent_used": "create_deep_agent",
        }

    def modify_code(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
    ) -> dict[str, Any]:
        """FR-FS-03: Precise Code Modification.
        
        Edit file with precise string replacement.

        Args:
            file_path: Path to file
            old_string: String to replace
            new_string: Replacement string

        Returns:
            Modification result
        """
        prompt = f"""
        Modify the file: {file_path}
        
        Use `edit_file` to replace:
        OLD: {old_string[:100]}{'...' if len(old_string) > 100 else ''}
        NEW: {new_string[:100]}{'...' if len(new_string) > 100 else ''}
        
        Report success or failure.
        """
        
        try:
            result = self.agent.invoke({
                "messages": [{"role": "user", "content": prompt}]
            })
            
            return {
                "success": True,
                "file": file_path,
                "message": result["messages"][-1].content,
                "agent_used": "create_deep_agent",
            }
        except Exception as e:
            return {
                "success": False,
                "file": file_path,
                "error": str(e),
            }

    def create_file(
        self,
        file_path: str,
        content: str,
    ) -> dict[str, Any]:
        """Create new file.

        Args:
            file_path: Path for new file
            content: File content

        Returns:
            Creation result
        """
        prompt = f"""
        Create a new file: {file_path}
        
        Use `write_file` with this content:
        {content[:200]}{'...' if len(content) > 200 else ''}
        
        Report success or failure.
        """
        
        try:
            result = self.agent.invoke({
                "messages": [{"role": "user", "content": prompt}]
            })
            
            return {
                "success": True,
                "file": file_path,
                "message": result["messages"][-1].content,
                "agent_used": "create_deep_agent",
            }
        except Exception as e:
            return {
                "success": False,
                "file": file_path,
                "error": str(e),
            }

    def handle_large_output(
        self,
        content: str,
        output_path: str | None = None,
    ) -> dict[str, Any]:
        """FR-FS-04: Large Output Handling.
        
        Handle large files by saving to filesystem and summarizing.

        Args:
            content: Large content to handle
            output_path: Optional path to save content

        Returns:
            Handling result with summary
        """
        # Check if content exceeds token limit
        estimated_tokens = len(content.split())
        
        if estimated_tokens > self.max_token_output:
            # Save to file using DeepAgent
            if not output_path:
                output_path = f"large_output_{hash(content)}.txt"
            
            prompt = f"""
            This content is too large ({estimated_tokens} tokens > {self.max_token_output}).
            
            Tasks:
            1. Save the full content to file: {output_path} using `write_file`
            2. Provide a concise summary highlighting:
               - Main purpose
               - Key sections
               - Important findings
            
            Content preview:
            {content[:1000]}...
            """
            
            result = self.agent.invoke({
                "messages": [{"role": "user", "content": prompt}]
            })
            
            return {
                "large_output": True,
                "saved_to": output_path,
                "summary": result["messages"][-1].content,
                "estimated_tokens": estimated_tokens,
                "agent_used": "create_deep_agent",
            }
        else:
            return {
                "large_output": False,
                "content": content,
                "estimated_tokens": estimated_tokens,
            }

    def read_file_safe(self, file_path: str) -> dict[str, Any]:
        """Read file with automatic large output handling.

        Args:
            file_path: Path to file

        Returns:
            File content or summary if too large
        """
        prompt = f"""
        Read the file: {file_path} using `read_file`
        
        If the file is large (>4000 tokens):
        1. Save to a temporary file
        2. Provide a summary
        
        Otherwise, return the content.
        """
        
        try:
            result = self.agent.invoke({
                "messages": [{"role": "user", "content": prompt}]
            })
            
            response_content = result["messages"][-1].content
            
            # Check if it's large output
            estimated_tokens = len(response_content.split())
            if estimated_tokens > self.max_token_output:
                return self.handle_large_output(response_content)
            
            return {
                "success": True,
                "file": file_path,
                "content": response_content,
                "agent_used": "create_deep_agent",
            }
        except Exception as e:
            return {
                "success": False,
                "file": file_path,
                "error": str(e),
            }
