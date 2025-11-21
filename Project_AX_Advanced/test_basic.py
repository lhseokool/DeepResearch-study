"""Basic functionality test without LLM."""

from pathlib import Path

from agentic_coding_assistant.analyzers import SpeedAnalyzer
from agentic_coding_assistant.models.schema import AnalysisMode, AnalysisRequest

# Create test file
test_file = Path("test_sample.py")
test_file.write_text("""
def helper():
    return "help"

def main():
    return helper()

def another():
    main()
""")

try:
    print("🧪 Testing SPEED Mode (without LLM)...")
    
    # Test SpeedAnalyzer directly
    analyzer = SpeedAnalyzer()
    
    request = AnalysisRequest(
        mode=AnalysisMode.SPEED,
        file_path=str(test_file.absolute()),
        symbol_name="helper",
        max_depth=2,
    )
    
    result = analyzer.analyze(request)
    
    print(f"\n✓ Analysis completed!")
    print(f"  Success: {result.success}")
    print(f"  Mode: {result.mode.value}")
    print(f"  Execution Time: {result.execution_time:.3f}s")
    print(f"  Dependencies Found: {len(result.dependencies)}")
    
    if result.dependencies:
        print("\n  Dependencies:")
        for dep in result.dependencies:
            print(f"    - {dep.symbol_name} ({dep.impact_level.value})")
    
    print(f"\n  Metadata:")
    for key, value in result.metadata.items():
        print(f"    {key}: {value}")
    
    print("\n✅ Test passed!")
    
finally:
    # Cleanup
    if test_file.exists():
        test_file.unlink()
