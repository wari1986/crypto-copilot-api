from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.analysis import analysis_agent

router = APIRouter(prefix="/llm", tags=["LLM"])


@router.post("/analyze")
async def analyze_market() -> dict[str, str]:
    """Run the analysis agent immediately and return its output."""
    result = await analysis_agent.run()
    return {"analysis": result}


@router.get("/analysis")
async def latest_analysis() -> dict[str, str]:
    """Return the most recent market analysis."""
    result = analysis_agent.latest()
    if result is None:
        raise HTTPException(status_code=404, detail="No analysis available")
    return {"analysis": result}
