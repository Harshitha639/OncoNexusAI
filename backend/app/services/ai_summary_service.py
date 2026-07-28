"""
AI report summarization via the Gemini API.

Takes OCR-extracted medical report text and asks Gemini to return one
structured JSON object containing patient-friendly and clinical summaries,
findings, cancer details, biomarkers, abnormal values, recommendations,
follow-up suggestions, risk indicators, and a risk score.
"""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.logging import get_logger
from app.exceptions.base import ServiceUnavailableException

logger = get_logger(__name__)


_RESPONSE_SCHEMA_HINT = """
Return ONLY one valid JSON object.

Use exactly these keys:

{
  "patient_friendly_summary": "plain-language summary or null",
  "medical_summary": "clinical summary or null",
  "important_findings": [
    "finding 1",
    "finding 2"
  ],
  "cancer_type": "identified cancer type or null",
  "cancer_stage": "identified cancer stage or null",
  "biomarkers": [
    {
      "name": "biomarker name",
      "value": "reported value",
      "reference_range": "reference range or null"
    }
  ],
  "abnormal_values": [
    {
      "name": "test name",
      "value": "reported value",
      "reference_range": "reference range or null",
      "severity": "low, high, or critical"
    }
  ],
  "recommendations": "patient-safe recommendations or null",
  "follow_up_suggestions": "follow-up actions and timeline or null",
  "risk_indicators": [
    "risk indicator 1",
    "risk indicator 2"
  ],
  "risk_score": 0
}

Rules:

1. risk_score must be between 0 and 100, or null.
2. Use null when a value cannot be determined.
3. Use an empty list for missing array fields.
4. Do not invent diagnoses, stages, findings, values, or treatments.
5. Do not include markdown code fences.
6. Do not include commentary outside the JSON object.
"""


_SYSTEM_INSTRUCTION = (
    "You are a clinical oncology report summarisation assistant for a "
    "cancer-care support platform. Extract only information explicitly "
    "supported by the supplied report. Do not make a definitive diagnosis, "
    "do not invent findings, and do not replace professional medical advice."
)


def _build_prompt(report_text: str) -> str:
    """Build the structured Gemini prompt."""

    return (
        f"{_SYSTEM_INSTRUCTION}\n\n"
        "Analyse the following OCR-extracted medical report and return the "
        "requested structured information.\n\n"
        f"{_RESPONSE_SCHEMA_HINT}\n\n"
        "--- REPORT TEXT START ---\n"
        f"{report_text.strip()}\n"
        "--- REPORT TEXT END ---"
    )


def _extract_json(raw_text: str) -> dict[str, Any]:
    """Extract and validate a JSON object from Gemini's response."""

    cleaned = raw_text.strip()

    cleaned = re.sub(
        r"^```(?:json)?",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip()

    cleaned = re.sub(
        r"```$",
        "",
        cleaned,
    ).strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)

        if match is None:
            raise

        parsed = json.loads(match.group(0))

    if not isinstance(parsed, dict):
        raise ValueError("Gemini response must be a JSON object.")

    return parsed


def _ensure_list(value: Any) -> list[Any]:
    """Return the value when it is a list; otherwise return an empty list."""

    return value if isinstance(value, list) else []


class AiSummaryService:
    """Gemini-based structured report summarisation service."""

    def __init__(self) -> None:
        self._client: genai.Client | None = None

        if settings.GEMINI_API_KEY:
            self._client = genai.Client(
                api_key=settings.GEMINI_API_KEY,
            )
        else:
            logger.warning(
                "GEMINI_API_KEY is not configured. "
                "AI summary generation will remain unavailable."
            )

    async def generate_summary(self, report_text: str) -> dict[str, Any]:
        """Generate and normalise a structured medical-report summary."""

        if self._client is None:
            raise ServiceUnavailableException(
                message=(
                    "AI summary generation is not configured on this server."
                )
            )

        if not report_text or not report_text.strip():
            raise ServiceUnavailableException(
                message="The extracted report text is empty."
            )

        prompt = _build_prompt(report_text)

        try:
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                ),
            )

            raw_text = response.text

            if not raw_text or not raw_text.strip():
                raise ValueError("Gemini returned an empty response.")

        except Exception as exc:
            logger.exception(
                "Gemini API call failed. Model=%s Error=%s",
                settings.GEMINI_MODEL,
                exc,
            )

            raise ServiceUnavailableException(
                message=(
                    "AI summary generation failed. "
                    "Please check the Gemini API configuration and try again."
                )
            ) from exc

        try:
            parsed = _extract_json(raw_text)

        except (
            json.JSONDecodeError,
            AttributeError,
            TypeError,
            ValueError,
        ) as exc:
            logger.exception(
                "Failed to parse Gemini response as JSON. Error=%s",
                exc,
            )

            raise ServiceUnavailableException(
                message=(
                    "AI summary generation returned an unexpected response."
                )
            ) from exc

        return self._normalize(parsed)

    @staticmethod
    def _normalize(parsed: dict[str, Any]) -> dict[str, Any]:
        """Convert Gemini output into safe database-compatible values."""

        risk_score = parsed.get("risk_score")

        if risk_score is not None:
            try:
                risk_score = float(risk_score)
                risk_score = max(0.0, min(100.0, risk_score))
            except (TypeError, ValueError):
                risk_score = None

        return {
            "patient_friendly_summary": parsed.get(
                "patient_friendly_summary"
            ),
            "medical_summary": parsed.get("medical_summary"),
            "important_findings": _ensure_list(
                parsed.get("important_findings")
            ),
            "cancer_type": parsed.get("cancer_type"),
            "cancer_stage": parsed.get("cancer_stage"),
            "biomarkers": _ensure_list(
                parsed.get("biomarkers")
            ),
            "abnormal_values": _ensure_list(
                parsed.get("abnormal_values")
            ),
            "recommendations": parsed.get("recommendations"),
            "follow_up_suggestions": parsed.get(
                "follow_up_suggestions"
            ),
            "risk_indicators": _ensure_list(
                parsed.get("risk_indicators")
            ),
            "risk_score": risk_score,
        }