import os
import json
import logging
from typing import List, Dict, Any, Optional
from litellm import completion
from schemas import RawInputEntity, VerificationResult, Citation

logger = logging.getLogger(__name__)

class VerificationEngine:
    """Multi-provider LLM verification engine supporting Claude, OpenAI, and local models."""
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.model = model or os.getenv("DEFAULT_VERIFIER_MODEL", "claude-3-5-sonnet-20240620")
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
            os.environ["OPENAI_API_KEY"] = api_key

    def verify_entity(self, entity: RawInputEntity, search_results: List[Dict[str, Any]]) -> VerificationResult:
        context_str = json.dumps(search_results, indent=2)

        prompt = f"""
        You are an expert EdTech content verifier.
        Evaluate the following educational claim against the provided web sources:

        Entity ID: {entity.entity_id}
        Subject: {entity.subject}
        Grade Level: {entity.grade_level}
        Concept Name: {entity.concept_name}
        Original Claim: {entity.unverified_definition}

        Web Sources:
        {context_str}

        Task:
        1. Determine if the original claim is accurate (is_accurate: true/false).
        2. Provide the authoritative, verified definition.
        3. Compute a confidence score from 0.0 to 1.0 based on source authority and agreement.
        4. Extract up to 2 citations with url, source_title, and supporting_quote.
        5. Set needs_human_review = true if confidence_score < 0.85 or sources are contradictory.
        6. Provide brief internal reasoning.

        Output MUST be a valid JSON object matching this schema:
        {{
            "entity_id": "{entity.entity_id}",
            "concept_name": "{entity.concept_name}",
            "is_accurate": true,
            "verified_definition": "...",
            "confidence_score": 0.95,
            "citations": [
                {{"url": "...", "source_title": "...", "supporting_quote": "..."}}
            ],
            "needs_human_review": false,
            "reasoning": "..."
        }}
        """

        try:
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            raw_content = response.choices[0].message.content
            raw_data = json.loads(raw_content.replace("```json", "").replace("```", ""))

            # Ensure required fields
            raw_data["entity_id"] = raw_data.get("entity_id", entity.entity_id)
            raw_data["concept_name"] = raw_data.get("concept_name", entity.concept_name)

            return VerificationResult(**raw_data)
        except Exception as e:
            logger.error(f"VerificationEngine failed: {e}")
            return VerificationResult(
                entity_id=entity.entity_id,
                concept_name=entity.concept_name,
                is_accurate=False,
                verified_definition=entity.unverified_definition or "Verification failed.",
                confidence_score=0.0,
                citations=[],
                needs_human_review=True,
                reasoning=f"Verification failed with error: {str(e)}"
            )
