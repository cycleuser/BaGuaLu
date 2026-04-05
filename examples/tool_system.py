"""Example: Tool system usage.

This example demonstrates how to:
1. Create custom tools
2. Register tools in the tool registry
3. Use tools in agents and skills
4. Validate tool inputs with Pydantic
5. Handle tool execution results
"""

import asyncio
from pathlib import Path

from pydantic import BaseModel, Field

from bagualu.tools import BaseTool, ToolExecutionContext, ToolRegistry, ToolResult


class FileReadInput(BaseModel):
    """Input schema for file read tool."""

    file_path: str = Field(description="Path to the file to read")
    encoding: str = Field(default="utf-8", description="File encoding")


class FileWriteInput(BaseModel):
    """Input schema for file write tool."""

    file_path: str = Field(description="Path to the file to write")
    content: str = Field(description="Content to write")
    encoding: str = Field(default="utf-8", description="File encoding")


class FileReadTool(BaseTool):
    """Tool for reading files."""

    name = "file_read"
    description = "Read content from a file"
    input_model = FileReadInput

    async def execute(
        self,
        arguments: dict[str, any],
        context: ToolExecutionContext,
    ) -> ToolResult:
        """Execute file read operation."""
        validated = self.validate_input(arguments)
        if not validated:
            return ToolResult(
                output=None,
                error="Invalid input for file_read tool",
            )

        file_path = Path(validated.file_path)

        if not file_path.exists():
            return ToolResult(
                output=None,
                error=f"File not found: {file_path}",
            )

        try:
            content = file_path.read_text(encoding=validated.encoding)
            return ToolResult(
                output=content,
                metadata={
                    "file_path": str(file_path),
                    "encoding": validated.encoding,
                    "size": len(content),
                },
            )
        except Exception as e:
            return ToolResult(
                output=None,
                error=f"Failed to read file: {e}",
            )


class FileWriteTool(BaseTool):
    """Tool for writing files."""

    name = "file_write"
    description = "Write content to a file"
    input_model = FileWriteInput

    async def execute(
        self,
        arguments: dict[str, any],
        context: ToolExecutionContext,
    ) -> ToolResult:
        """Execute file write operation."""
        validated = self.validate_input(arguments)
        if not validated:
            return ToolResult(
                output=None,
                error="Invalid input for file_write tool",
            )

        file_path = Path(validated.file_path)

        try:
            file_path.write_text(validated.content, encoding=validated.encoding)
            return ToolResult(
                output=f"Successfully wrote to {file_path}",
                metadata={
                    "file_path": str(file_path),
                    "encoding": validated.encoding,
                    "size": len(validated.content),
                },
            )
        except Exception as e:
            return ToolResult(
                output=None,
                error=f"Failed to write file: {e}",
            )


async def main() -> None:
    """Demonstrate tool system capabilities."""

    print("=" * 60)
    print("BaGuaLu Tool System Example")
    print("=" * 60)

    print("\n1. Understanding the Tool System")
    print("-" * 60)
    print("BaGuaLu tools provide:")
    print("  • Structured input validation (Pydantic)")
    print("  • Self-describing JSON schemas")
    print("  • Execution context tracking")
    print("  • Error handling and recovery")
    print("  • Metadata collection")

    print("\n2. Creating Custom Tools")
    print("-" * 60)
    print("Tools extend BaseTool and implement execute():")
    print()
    print("  class MyTool(BaseTool):")
    print("      name = 'my_tool'")
    print("      description = 'My custom tool'")
    print("      input_model = MyInputSchema  # Optional")
    print()
    print("      async def execute(self, arguments, context):")
    print("          # Validate input")
    print("          validated = self.validate_input(arguments)")
    print("          if not validated:")
    print("              return ToolResult(output=None, error='Invalid input')")
    print()
    print("          # Execute tool logic")
    print("          result = do_something(validated)")
    print()
    print("          # Return result")
    print("          return ToolResult(output=result, metadata={...})")

    print("\n3. Tool Registry")
    print("-" * 60)
    registry = ToolRegistry()

    read_tool = FileReadTool()
    write_tool = FileWriteTool()

    registry.register(read_tool)
    registry.register(write_tool)

    print("Registered tools:")
    for tool_name in registry.list_tools():
        print(f"  • {tool_name}")

    print("\n4. Tool Schemas")
    print("-" * 60)
    print("Tools automatically generate JSON schemas:")

    schemas = registry.get_all_schemas()
    for schema in schemas:
        print(f"\nTool: {schema['name']}")
        print(f"Description: {schema['description']}")
        if "input_schema" in schema:
            print("Input schema:")
            print(f"  {schema['input_schema']}")

    print("\n5. Executing Tools")
    print("-" * 60)

    context = ToolExecutionContext(
        agent_id="demo-agent",
        session_id="demo-session",
    )

    print("\n5.1. Write a file:")
    write_result = await registry.execute_tool(
        tool_name="file_write",
        arguments={
            "file_path": "/tmp/demo.txt",
            "content": "Hello from BaGuaLu tools!",
        },
        context=context,
    )

    if write_result.is_success():
        print(f"  ✓ {write_result.output}")
        print(f"  Metadata: {write_result.metadata}")
    else:
        print(f"  ✗ Error: {write_result.error}")

    print("\n5.2. Read the file:")
    read_result = await registry.execute_tool(
        tool_name="file_read",
        arguments={"file_path": "/tmp/demo.txt"},
        context=context,
    )

    if read_result.is_success():
        print(f"  ✓ Content: {read_result.output}")
        print(f"  Metadata: {read_result.metadata}")
    else:
        print(f"  ✗ Error: {read_result.error}")

    print("\n6. Input Validation")
    print("-" * 60)
    print("Pydantic models validate tool inputs:")

    invalid_result = await registry.execute_tool(
        tool_name="file_read",
        arguments={"invalid_param": "value"},
        context=context,
    )

    print(f"Invalid input result: {invalid_result.error}")

    print("\n7. Using Tools in Agents")
    print("-" * 60)
    print("Agents can use registered tools:")
    print()
    print("  core = BaGuaLuCore()")
    print("  await core.initialize()")
    print()
    print("  # Deploy agent with tools")
    print("  agent_id = await core.deploy_agent(")
    print("      name='file-processor',")
    print("      role='executor',")
    print("      tools=['file_read', 'file_write'],")
    print("  )")
    print()
    print("  # Execute task using tools")
    print("  result = await core.cluster.execute_with_agent(")
    print("      agent_id=agent_id,")
    print("      instruction='Read and process files',")
    print("      inputs={'files': ['file1.txt', 'file2.txt']},")
    print("  )")

    print("\n8. Using Tools in Skills")
    print("-" * 60)
    print("Skills can integrate tools:")
    print()
    print("In SKILL.md:")
    print("  ## Tools")
    print("  - file_read: Read files for analysis")
    print("  - file_write: Write processed results")
    print()
    print("In skill implementation:")
    print("  # Skill uses registered tools")
    print("  content = await tools.execute('file_read', {'file_path': file})")
    print("  processed = process_content(content)")
    print("  await tools.execute('file_write', {'file_path': output, 'content': processed})")

    print("\n9. Tool Error Handling")
    print("-" * 60)
    print("Tools handle errors gracefully:")
    print()
    print("  # File not found")
    print("  result = await registry.execute_tool(")
    print("      'file_read', {'file_path': '/nonexistent.txt'}, context")
    print("  )")
    print("  if not result.is_success():")
    print("      print(f'Error: {result.error}')")
    print("      # Handle error: retry, skip, notify, etc.")

    print("\n10. Built-in Tools")
    print("-" * 60)
    print("BaGuaLu provides built-in tools:")
    print("  • file_operations - File read/write")
    print("  • web_search - Search the web")
    print("  • code_analysis - Analyze code")
    print("  • test_runner - Execute tests")
    print("  • git_operations - Git commands")
    print()
    print("Register built-in tools:")
    print("  from bagualu.tools.builtin import register_builtin_tools")
    print("  register_builtin_tools(registry)")

    print("\n11. Best Practices")
    print("-" * 60)
    print("✓ Define clear input schemas with Pydantic")
    print("✓ Return detailed metadata for debugging")
    print("✓ Handle errors gracefully in execute()")
    print("✓ Use ToolExecutionContext for tracking")
    print("✓ Document tool usage in skills")
    print("✓ Test tools independently")
    print("✓ Consider permissions and security")

    print("\n" + "=" * 60)
    print("Tool system example completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
