from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional

class RawInputEntity(BaseModel):
    """Initial data structure extracted from source files or web extension."""
    entity_id: str
    subject: str
    grade_level: str
    concept_name: str
    unverified_definition: Optional[str] = None
    source_metadata: Optional[dict] = Field(default_factory=dict)

class Citation(BaseModel):
    url: str = Field(description="Exact URL where the supporting fact was found")
    source_title: str = Field(description="Title or domain of the source")
    supporting_quote: str = Field(description="Direct verbatim quote from the text that proves the claim")

class VerificationResult(BaseModel):
    entity_id: str
    concept_name: str
    is_accurate: bool = Field(description="True if original input was completely accurate")
    verified_definition: str = Field(description="The authoritative, verified definition")
    confidence_score: float = Field(
        ge=0.0, le=1.0,
        description="Score from 0.0 to 1.0 based on source authority and agreement"
    )
    citations: List[Citation]
    needs_human_review: bool = Field(
        default=False,
        description="Flagged as True if confidence_score < 0.85 or contradictory sources exist"
    )
    reasoning: str = Field(description="Brief internal explanation of the evaluation")

class WebhookPayload(BaseModel):
    entity_id: str
    subject: str
    grade_level: str
    concept_name: str
    unverified_definition: Optional[str] = None
    callback_url: Optional[str] = None
