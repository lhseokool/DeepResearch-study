"""CLI for impact analysis."""

import argparse
import json
import sys
from pathlib import Path

from .agents.coordinator import ImpactAnalysisCoordinator
from .models.schema import AnalysisMode, AnalysisRequest


def human_input_callback(message: str) -> bool:
    """Callback for human input.

    Args:
        message: Message to display to user

    Returns:
        True if user agrees, False otherwise
    """
    print(f"\n{message}")
    response = input("Your choice: ").strip().lower()
    return response in ["yes", "y", "true", "1"]


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Agentic Coding Assistant - Impact Analysis"
    )

    parser.add_argument(
        "--file",
        "-f",
        required=True,
        help="File path to analyze",
    )

    parser.add_argument(
        "--symbol",
        "-s",
        required=True,
        help="Symbol name (function, class) to analyze",
    )

    parser.add_argument(
        "--mode",
        "-m",
        choices=["SPEED", "PRECISION"],
        default="SPEED",
        help="Analysis mode (default: SPEED)",
    )

    parser.add_argument(
        "--project-root",
        "-p",
        help="Project root directory",
    )

    parser.add_argument(
        "--max-depth",
        "-d",
        type=int,
        default=3,
        help="Maximum dependency depth (default: 3)",
    )

    parser.add_argument(
        "--human-in-loop",
        "-l",
        action="store_true",
        help="Enable human-in-the-loop for fallback decisions",
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (JSON format)",
    )

    args = parser.parse_args()

    # Validate file exists
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Create analysis request
    request = AnalysisRequest(
        mode=AnalysisMode(args.mode),
        file_path=str(file_path.absolute()),
        symbol_name=args.symbol,
        project_root=args.project_root,
        max_depth=args.max_depth,
    )

    # Create coordinator
    coordinator = ImpactAnalysisCoordinator()

    # Execute analysis
    print(f"\n🔍 Analyzing: {args.symbol} in {file_path.name}")
    print(f"📊 Mode: {args.mode}")
    print(f"🎯 Max Depth: {args.max_depth}\n")

    if args.human_in_loop:
        result = coordinator.analyze_with_human_in_loop(
            request, human_input_callback
        )
    else:
        result = coordinator.analyze(request)

    # Display results
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)

    print(f"\n✓ Success: {result.success}")
    print(f"⏱️  Execution Time: {result.execution_time:.2f}s")
    print(f"📁 Mode Used: {result.mode.value}")

    if result.error_message:
        print(f"\n❌ Error: {result.error_message}")

    if result.dependencies:
        print(f"\n📋 Dependencies Found: {len(result.dependencies)}")
        print("\n" + "-" * 60)

        for i, dep in enumerate(result.dependencies, 1):
            print(f"\n{i}. {dep.symbol_name}")
            print(f"   📄 File: {dep.file_path}")
            print(f"   📍 Line: {dep.line_number or 'N/A'}")
            print(f"   🏷️  Type: {dep.node_type}")
            print(f"   ⚠️  Impact: {dep.impact_level.value}")

    else:
        print("\n📋 No dependencies found")

    if result.metadata:
        print("\n" + "-" * 60)
        print("Metadata:")
        for key, value in result.metadata.items():
            print(f"  {key}: {value}")

    print("\n" + "=" * 60 + "\n")

    # Save to file if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(result.model_dump(), f, indent=2, default=str)
        print(f"💾 Results saved to: {output_path}")

    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
