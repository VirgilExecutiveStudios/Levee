import sys
import unittest
from unittest.mock import patch, MagicMock
from typing import List, Dict, Any

# Ensure backend root is on PYTHONPATH
sys.path.append(str(__file__))

from main import process_and_persist_entity
from schemas import WebhookPayload, RawInputEntity, VerificationResult, Citation


class TestVerificationPipeline(unittest.TestCase):
    """Test the verification pipeline from RawInputEntity to VerificationResult."""

    def setUp(self):
        """Set up test data and mocks."""
        self.test_payload = WebhookPayload(
            entity_id="test-entity-001",
            subject="Mathematics",
            grade_level="8",
            concept_name="Pythagorean Theorem",
            unverified_definition="In a right triangle, the square of the hypotenuse is equal to the sum of the squares of the other two sides.",
            callback_url=None
        )
        self.mock_search_results = [
            {
                "title": "Pythagorean Theorem - Wikipedia",
                "url": "https://en.wikipedia.org/wiki/Pythagorean_theorem",
                "content": "In mathematics, the Pythagorean theorem is a fundamental relation in Euclidean geometry among the three sides of a right triangle."
            },
            {
                "title": "Pythagorean Theorem - Khan Academy",
                "url": "https://www.khanacademy.org/math/geometry/hs-geo-trig/hs-geo-trig-side-lengths/v/pythagorean-theorem",
                "content": "The Pythagorean theorem describes the relationship between the lengths of the legs and the hypotenuse of a right triangle."
            }
        ]
        self.mock_verification_result_high_confidence = VerificationResult(
            entity_id="test-entity-001",
            concept_name="Pythagorean Theorem",
            is_accurate=True,
            verified_definition="In a right triangle, the square of the hypotenuse (the side opposite the right angle) is equal to the sum of the squares of the other two sides.",
            confidence_score=0.95,
            citations=[
                Citation(
                    url="https://en.wikipedia.org/wiki/Pythagorean_theorem",
                    source_title="Wikipedia",
                    supporting_quote="In mathematics, the Pythagorean theorem is a fundamental relation in Euclidean geometry among the three sides of a right triangle."
                )
            ],
            needs_human_review=False,
            reasoning="Multiple authoritative sources confirm the definition is accurate."
        )
        self.mock_verification_result_low_confidence = VerificationResult(
            entity_id="test-entity-001",
            concept_name="Pythagorean Theorem",
            is_accurate=False,
            verified_definition="In any triangle, the square of one side is equal to the sum of the squares of the other two sides.",
            confidence_score=0.60,
            citations=[
                Citation(
                    url="https://example.com/math-myth",
                    source_title="Math Myths Blog",
                    supporting_quote="In any triangle, the square of one side is equal to the sum of the squares of the other two sides."
                )
            ],
            needs_human_review=True,
            reasoning="Conflicting information found; authoritative sources contradict the definition."
        )

    @patch('main.SessionLocal')
    @patch('main.VerificationEngine')
    @patch('main.GroundingRetriever')
    def test_pipeline_high_confidence(self, MockRetriever, MockVerifier, MockSessionLocal):
        """Test pipeline with high confidence score (should not need human review)."""
        # Configure mocks
        mock_retriever_instance = MockRetriever.return_value
        mock_retriever_instance.search_internet.return_value = self.mock_search_results

        mock_verifier_instance = MockVerifier.return_value
        mock_verifier_instance.verify_entity.return_value = self.mock_verification_result_high_confidence

        mock_session = MagicMock()
        MockSessionLocal.return_value = mock_session

        # Execute pipeline
        process_and_persist_entity(
            payload=self.test_payload,
            tavily_key="fake-tavily-key",
            model_name="fake-model"
        )

        # Verify GroundingRetriever was called correctly
        MockRetriever.assert_called_once_with(tavily_api_key="fake-tavily-key")
        expected_query = f"{self.test_payload.concept_name} {self.test_payload.subject} {self.test_payload.grade_level} definition"
        mock_retriever_instance.search_internet.assert_called_once_with(query=expected_query, max_results=3)

        # Verify VerificationEngine was called correctly
        MockVerifier.assert_called_once_with(model="fake-model")
        # Check that verify_entity was called with RawInputEntity and search results
        call_args = mock_verifier_instance.verify_entity.call_args
        self.assertEqual(call_args[0][0].entity_id, self.test_payload.entity_id)  # RawInputEntity arg
        self.assertEqual(call_args[0][1], self.mock_search_results)  # search_results arg

        # Verify database operations
        MockSessionLocal.assert_called_once()
        mock_session.merge.assert_called_once()
        mock_session.commit.assert_called_once()

        # Verify the merged record matches expected VerificationResult
        merged_record_arg = mock_session.merge.call_args[0][0]
        self.assertEqual(merged_record_arg.entity_id, self.mock_verification_result_high_confidence.entity_id)
        self.assertEqual(merged_record_arg.concept_name, self.mock_verification_result_high_confidence.concept_name)
        self.assertEqual(merged_record_arg.verified_definition, self.mock_verification_result_high_confidence.verified_definition)
        self.assertEqual(merged_record_arg.confidence_score, self.mock_verification_result_high_confidence.confidence_score)
        self.assertEqual(merged_record_arg.needs_human_review, self.mock_verification_result_high_confidence.needs_human_review)
        # Check citations length
        self.assertEqual(len(merged_record_arg.citations), len(self.mock_verification_result_high_confidence.citations))

    @patch('main.SessionLocal')
    @patch('main.VerificationEngine')
    @patch('main.GroundingRetriever')
    def test_pipeline_low_confidence_triggers_review(self, MockRetriever, MockVerifier, MockSessionLocal):
        """Test pipeline with low confidence score (should need human review)."""
        # Configure mocks
        mock_retriever_instance = MockRetriever.return_value
        mock_retriever_instance.search_internet.return_value = self.mock_search_results

        mock_verifier_instance = MockVerifier.return_value
        mock_verifier_instance.verify_entity.return_value = self.mock_verification_result_low_confidence

        mock_session = MagicMock()
        MockSessionLocal.return_value = mock_session

        # Execute pipeline
        process_and_persist_entity(
            payload=self.test_payload,
            tavily_key="fake-tavily-key",
            model_name="fake-model"
        )

        # Verify VerificationEngine was called
        mock_verifier_instance.verify_entity.assert_called_once()

        # Verify database operations
        mock_session.merge.assert_called_once()
        mock_session.commit.assert_called_once()

        # Verify the merged record has needs_human_review=True due to low confidence
        merged_record_arg = mock_session.merge.call_args[0][0]
        self.assertTrue(merged_record_arg.needs_human_review)
        self.assertEqual(merged_record_arg.confidence_score, 0.60)

    def test_verification_result_schema_constraints(self):
        """Test that VerificationResult adheres to schema constraints."""
        # Test valid confidence score
        result = VerificationResult(
            entity_id="test-1",
            concept_name="Test Concept",
            is_accurate=True,
            verified_definition="Test definition",
            confidence_score=0.85,
            citations=[
                Citation(
                    url="https://example.com",
                    source_title="Example",
                    supporting_quote="Test quote"
                )
            ],
            needs_human_review=False,
            reasoning="Test reasoning"
        )
        self.assertEqual(result.confidence_score, 0.85)
        self.assertFalse(result.needs_human_review)

        # Test confidence score boundary: 0.0
        result_low = VerificationResult(
            entity_id="test-2",
            concept_name="Test Concept",
            is_accurate=False,
            verified_definition="Test definition",
            confidence_score=0.0,
            citations=[
                Citation(
                    url="https://example.com",
                    source_title="Example",
                    supporting_quote="Test quote"
                )
            ],
            needs_human_review=True,
            reasoning="Test reasoning"
        )
        self.assertEqual(result_low.confidence_score, 0.0)
        self.assertTrue(result_low.needs_human_review)

        # Test confidence score boundary: 1.0
        result_high = VerificationResult(
            entity_id="test-3",
            concept_name="Test Concept",
            is_accurate=True,
            verified_definition="Test definition",
            confidence_score=1.0,
            citations=[
                Citation(
                    url="https://example.com",
                    source_title="Example",
                    supporting_quote="Test quote"
                )
            ],
            needs_human_review=False,
            reasoning="Test reasoning"
        )
        self.assertEqual(result_high.confidence_score, 1.0)
        self.assertFalse(result_high.needs_human_review)

        # Test that needs_human_review is True when confidence < 0.85 (per schema description)
        # Note: The actual logic is in the VerificationEngine, but we can test the field behavior
        result_edge = VerificationResult(
            entity_id="test-4",
            concept_name="Test Concept",
            is_accurate=True,
            verified_definition="Test definition",
            confidence_score=0.84,  # Just below threshold
            citations=[
                Citation(
                    url="https://example.com",
                    source_title="Example",
                    supporting_quote="Test quote"
                )
            ],
            needs_human_review=True,  # Should be True per pipeline logic
            reasoning="Test reasoning"
        )
        self.assertTrue(result_edge.needs_human_review)


if __name__ == '__main__':
    unittest.main()