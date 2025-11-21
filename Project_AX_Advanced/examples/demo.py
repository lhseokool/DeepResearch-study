"""Demo script for impact analysis."""

import os
from pathlib import Path

from dotenv import load_dotenv

from agentic_coding_assistant import (
    AnalysisMode,
    AnalysisRequest,
    ImpactAnalysisCoordinator,
)

# Load environment variables
load_dotenv()


def demo_speed_mode():
    """Demonstrate SPEED mode analysis."""
    print("\n" + "=" * 60)
    print("DEMO: SPEED Mode Analysis")
    print("=" * 60 + "\n")

    # Create sample file
    sample_file = Path("sample_code.py")
    sample_file.write_text("""
def calculate_sum(a, b):
    return a + b

def calculate_product(a, b):
    return a * b

def process_numbers(x, y):
    sum_result = calculate_sum(x, y)
    product_result = calculate_product(x, y)
    return sum_result, product_result

def main():
    result = process_numbers(5, 10)
    print(f"Results: {result}")
""")

    try:
        # Create coordinator
        coordinator = ImpactAnalysisCoordinator()

        # Analyze calculate_sum function
        request = AnalysisRequest(
            mode=AnalysisMode.SPEED,
            file_path=str(sample_file.absolute()),
            symbol_name="calculate_sum",
            max_depth=3,
        )

        print(f"Analyzing: calculate_sum")
        print(f"File: {sample_file}")
        print(f"Mode: SPEED\n")

        result = coordinator.analyze(request)

        print(f"Success: {result.success}")
        print(f"Execution Time: {result.execution_time:.3f}s")
        print(f"Dependencies Found: {len(result.dependencies)}")

        if result.dependencies:
            print("\nDependencies:")
            for dep in result.dependencies:
                print(f"  - {dep.symbol_name} ({dep.impact_level.value})")

        print("\nMetadata:")
        for key, value in result.metadata.items():
            print(f"  {key}: {value}")

    finally:
        # Cleanup
        if sample_file.exists():
            sample_file.unlink()


def demo_precision_mode():
    """Demonstrate PRECISION mode analysis with fallback."""
    print("\n" + "=" * 60)
    print("DEMO: PRECISION Mode Analysis (with fallback)")
    print("=" * 60 + "\n")

    # Create sample file
    sample_file = Path("sample_code.py")
    sample_file.write_text("""
def helper():
    return "help"

def main():
    return helper()
""")

    try:
        coordinator = ImpactAnalysisCoordinator()

        request = AnalysisRequest(
            mode=AnalysisMode.PRECISION,
            file_path=str(sample_file.absolute()),
            symbol_name="helper",
        )

        print(f"Analyzing: helper")
        print(f"Mode: PRECISION\n")

        result = coordinator.analyze(request)

        print(f"Success: {result.success}")
        print(f"Execution Time: {result.execution_time:.3f}s")
        print(f"Mode Used: {result.mode.value}")

        if result.fallback_suggested:
            print("\n⚠️  Fallback to SPEED mode was suggested")

        if "fallback_executed" in result.metadata:
            print("✓ Fallback was automatically executed")

    finally:
        if sample_file.exists():
            sample_file.unlink()


def demo_human_in_loop():
    """Demonstrate human-in-the-loop fallback."""
    print("\n" + "=" * 60)
    print("DEMO: Human-in-the-Loop")
    print("=" * 60 + "\n")

    sample_file = Path("sample_code.py")
    sample_file.write_text("""
def test():
    pass
""")

    try:
        coordinator = ImpactAnalysisCoordinator()

        # Mock human input - always approve fallback
        def mock_human_input(message):
            print(f"\n[Human Input Required]")
            print(message)
            print("[Auto-approving for demo]")
            return True

        request = AnalysisRequest(
            mode=AnalysisMode.PRECISION,
            file_path=str(sample_file.absolute()),
            symbol_name="test",
        )

        result = coordinator.analyze_with_human_in_loop(
            request, mock_human_input
        )

        print(f"\nResult: {result.success}")
        print(f"Mode Used: {result.mode.value}")

        if "human_approved_fallback" in result.metadata:
            print("✓ Human approved fallback to SPEED mode")

    finally:
        if sample_file.exists():
            sample_file.unlink()


def main():
    """Run all demos."""
    print("\n🚀 Agentic Coding Assistant - Demo")
    print("=" * 60)

    demo_speed_mode()
    demo_precision_mode()
    demo_human_in_loop()

    print("\n" + "=" * 60)
    print("✓ Demo completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
