"""FastAPI application for impact analysis service."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .graph import analysis_graph
from .models.schema import AnalysisRequest, AnalysisResult
from .nodes.analysis_nodes import AnalysisState

app = FastAPI(
    title="Agentic Coding Assistant",
    description="Impact analysis service with SPEED and PRECISION modes",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Agentic Coding Assistant",
        "version": "0.1.0",
        "description": "Impact analysis service with SPEED and PRECISION modes",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/analyze", response_model=AnalysisResult)
async def analyze_impact(request: AnalysisRequest) -> AnalysisResult:
    """Perform impact analysis.

    Args:
        request: Analysis request with mode, file path, and symbol name

    Returns:
        Analysis result with dependencies and metadata

    Raises:
        HTTPException: If analysis fails
    """
    try:
        # Create initial state
        initial_state: AnalysisState = {
            "request": request,
            "result": None,
            "should_fallback": False,
            "error_count": 0,
        }

        # Run the workflow
        final_state = analysis_graph.invoke(initial_state)

        # Extract result
        result = final_state.get("result")

        if not result:
            raise HTTPException(
                status_code=500,
                detail="Analysis workflow did not produce a result",
            )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}",
        )


@app.get("/modes")
async def get_available_modes():
    """Get available analysis modes and their status.

    Returns:
        Dictionary of modes and their availability
    """
    from .analyzers import PrecisionAnalyzer, SpeedAnalyzer

    speed = SpeedAnalyzer()
    precision = PrecisionAnalyzer()

    return {
        "modes": {
            "SPEED": {
                "available": speed.is_available(),
                "description": "Fast static analysis using Tree-sitter",
                "typical_time": "< 5 seconds for 10k lines",
            },
            "PRECISION": {
                "available": precision.is_available(),
                "description": "Precise analysis using LSP (Pyright)",
                "typical_time": "10-30 seconds depending on project size",
            },
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
