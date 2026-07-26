"""
AI report summarization via the Gemini API.

Takes the OCR-extracted text of a medical report and asks Gemini to
return a single structured JSON object covering every field the product
requires (patient-friendly summary, medical summary, findings, cancer
type/stage, biomarkers, abnormal values, recommendations, follow-up
suggestions, risk indicators, and a 0-100 risk score). The raw model
call is isolated here so the rest of the app never talks to Gemini
directly.
"""

import json
import re

from app.core.config import settings
from app.core.logging import get_logger
from app.exceptions.base import ServiceUnavailableException

logger = get_logger(__name__)

_RESPONSE_SCHEMA_HINT = """
Respond with ONLY a single valid JSON object (no markdown fences, no commentary)
with exactly these keys:

{
  "patient_friendly_summary": "<plain-language summary a non-medical patient can understand>",
  "medical_summary": "<clinical summary using standard medical terminology>",
  "important_findings": ["<finding 1>", "<finding 2>", "..."],
  "cancer_type": "<cancer type if identifiable, else null>",
  "cancer_stage": "<cancer stage if identifiable, else null>",
  "biomarkers": [{"name": "<biomarker>", "value": "<value>", "reference_range": "<range or null>"}],
  "abnormal_values": [{"name": "<test name>", "value": "<value>", "reference_range": "<range or null>", "severity": "<low|high|critical>"}],
  "recommendations": "<actionable recommendations for the patient>",
  "follow_up_suggestions": "<suggested follow-up actions/tests/timeline>",
  "risk_indicators": ["<risk indicator 1>", "<risk indicator 2>", "..."],
  "risk_score": <number between 0 and 100 representing overall risk, or null if not determinable>
}

If a field cannot be determined from the report text, use null (or an empty
list for array fields) rather than guessing.
"""

_SYSTEM_INSTRUCTION = (
    "You are a clinical oncology assistant helping summarize medical reports "
    "for a cancer care platform. You are careful, precise, and never invent "
    "findings that are not supported by the report text."
)


def _build_prompt(report_text: str) -> str:
    return (
        f"{_SYSTEM_INSTRUCTION}\n\n"
        f"Analyze the following medical report text and extract structured "
        f"information.\n\n{_RESPONSE_SCHEMA_HINT}\n\n"
        f"--- REPORT TEXT START ---\n{report_text}\n--- REPORT TEXT END ---"
    )


def _extract_json(raw_text: str) -> dict:
    """Best-effort extraction of a JSON object from the model's raw response."""
    cleaned = raw_text.strip()
    # Strip markdown code fences if the model added them despite instructions.
    cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


class AiSummaryService:
    """Thin wrapper around the Gemini API for structured report summarization."""

    def __init__(self) -> None:
        if not settings.GEMINI_API_KEY:
            logger.warning(
                "GEMINI_API_KEY is not configured — AI summary generation will fail "
                "until it is set."
            )

    def _get_model(self):
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        return genai.GenerativeModel(settings.GEMINI_MODEL)

    async def generate_summary(self, report_text: str) -> dict:
        """Call Gemini and return the parsed structured analysis dict.

        Raises `ServiceUnavailableException` if the API call fails or the
        response cannot be parsed as the expected JSON structure.
        """
        if not settings.GEMINI_API_KEY:
            raise ServiceUnavailableException(
                message="AI summary generation is not configured on this server."
            )

        prompt = _build_prompt(report_text)

        try:
            model = self._get_model()
            response = await model.generate_content_async(
                prompt,
                generation_config={"temperature": 0.2, "response_mime_type": "application/json"},
            )
            raw_text = response.text
        except Exception as exc:  # noqa: BLE001 — any Gemini SDK failure
            logger.error("Gemini API call failed: %s", exc)
            raise ServiceUnavailableException(
                message="AI summary generation failed. Please try again later."
            ) from exc

        try:
            parsed = _extract_json(raw_text)
        except (json.JSONDecodeError, AttributeError) as exc:
            logger.error("Failed to parse Gemini response as JSON: %s", exc)
            raise ServiceUnavailableException(
                message="AI summary generation returned an unexpected response."
            ) from exc

        return self._normalize(parsed)

    @staticmethod
    def _normalize(parsed: dict) -> dict:
        """Coerce the parsed payload into safe, expected types/defaults."""
        risk_score = parsed.get("risk_score")
        if risk_score is not None:
            try:
                risk_score = max(0.0, min(100.0, float(risk_score)))
            except (TypeError, ValueError):
                risk_score = None

        return {
            "patient_friendly_summary": parsed.get("patient_friendly_summary"),
            "medical_summary": parsed.get("medical_summary"),
            "important_findings": parsed.get("important_findings") or [],
            "cancer_type": parsed.get("cancer_type"),
            "cancer_stage": parsed.get("cancer_stage"),
            "biomarkers": parsed.get("biomarkers") or [],
            "abnormal_values": parsed.get("abnormal_values") or [],
            "recommendations": parsed.get("recommendations"),
            "follow_up_suggestions": parsed.get("follow_up_suggestions"),
            "risk_indicators": parsed.get("risk_indicators") or [],
            "risk_score": risk_score,
        }
