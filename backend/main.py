import os
import sys
from pathlib import Path
from typing import List
from fastapi import FastAPI, BackgroundTasks, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Ensure backend root is on PYTHONPATH
sys.path.append(str(Path(__file__).parent))

from config import settings
from database import SessionLocal, VerifiedEntityRecord, get_db
from schemas import WebhookPayload, VerificationResult, RawInputEntity
from services.retriever import GroundingRetriever
from services.verifier import VerificationEngine

app = FastAPI(
    title="Levee Verification API",
    description="REST service for automated EdTech concept verification with grounding and human-in-the-loop review",
    version="1.0.0"
)

# Enable CORS for Chrome Extension & Web Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def process_and_persist_entity(payload: WebhookPayload, tavily_key: str, model_name: str):
    """Background worker executing web grounding and verification."""
    entity = RawInputEntity(
        entity_id=payload.entity_id,
        subject=payload.subject,
        grade_level=payload.grade_level,
        concept_name=payload.concept_name,
        unverified_definition=payload.unverified_definition
    )

    retriever = GroundingRetriever(tavily_api_key=tavily_key)
    verifier = VerificationEngine(model=model_name)

    query = f"{entity.concept_name} {entity.subject} {entity.grade_level} definition"
    search_results = retriever.search_internet(query=query, max_results=3)
    result = verifier.verify_entity(entity, search_results)

    db: Session = SessionLocal()
    try:
        record = VerifiedEntityRecord(
            entity_id=result.entity_id,
            concept_name=result.concept_name,
            verified_definition=result.verified_definition,
            confidence_score=result.confidence_score,
            needs_human_review=result.needs_human_review,
            citations=[c.model_dump() for c in result.citations]
        )
        db.merge(record)
        db.commit()
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "EdTech Verifier Backend"}

@app.post("/api/v1/verify-entity", status_code=status.HTTP_202_ACCEPTED)
async def verify_entity_webhook(
    payload: WebhookPayload,
    background_tasks: BackgroundTasks
):
    """Inbound webhook triggered by browser plugin, Fable, or batch scripts."""
    background_tasks.add_task(
        process_and_persist_entity,
        payload,
        settings.TAVILY_API_KEY,
        settings.LLM_MODEL
    )
    return {
        "status": "accepted",
        "entity_id": payload.entity_id,
        "message": "Verification pipeline scheduled."
    }

@app.get("/api/v1/review-queue")
async def get_review_queue(db: Session = Depends(get_db)):
    """Returns records requiring human review."""
    flagged = db.query(VerifiedEntityRecord).filter(
        VerifiedEntityRecord.needs_human_review == True
    ).all()
    return flagged

@app.post("/api/v1/review-queue/{entity_id}/resolve")
async def resolve_review_item(
    entity_id: str,
    approved_definition: str,
    db: Session = Depends(get_db)
):
    """Allows human reviewers to approve or edit low-confidence records."""
    record = db.query(VerifiedEntityRecord).filter(
        VerifiedEntityRecord.entity_id == entity_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Entity not found")

    record.verified_definition = approved_definition
    record.needs_human_review = False
    db.commit()
    return {"status": "resolved", "entity_id": entity_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
