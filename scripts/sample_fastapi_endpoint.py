#!/usr/bin/env python3
"""Sample FastAPI endpoint for AI inference with schema validation."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="AI Inference API", version="1.0.0")

class InferenceRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 100
    temperature: Optional[float] = 0.7

class InferenceResponse(BaseModel):
    response: str
    tokens_used: int
    confidence: float

@app.post("/inference", response_model=InferenceResponse)
async def perform_inference(request: InferenceRequest) -> InferenceResponse:
    """Mock AI inference endpoint with schema validation."""
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    # Mock response - replace with actual model call
    mock_response = f"Processed: {request.prompt[:50]}..."
    tokens_used = len(request.prompt.split()) + request.max_tokens
    confidence = 0.85

    return InferenceResponse(
        response=mock_response,
        tokens_used=tokens_used,
        confidence=confidence
    )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
