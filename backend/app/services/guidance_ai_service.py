"""
Gemini-powered personalized patient and caregiver guidance generation.

This service receives an existing AI report analysis and asks Gemini to
generate safe, structured guidance for either the patient or caregiver.
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


# ---------------------------------------------------------------------------
# Patient guidance response format
# ---------------------------------------------------------------------------

_PATIENT_GUIDANCE_SCHEMA = """
Return ONLY one valid JSON object with exactly these keys:

{
  "overview": "short patient-friendly overview or null",
  "immediate_actions": [
    "action 1",
    "action 2"
  ],
  "questions_for_doctor": [
    "question 1",
    "question 2"
  ],
  "medication_guidance": [
    "guidance item"
  ],
  "nutrition_guidance": [
    "guidance item"
  ],
  "activity_guidance": [
    "guidance item"
  ],
  "warning_signs": [
    "warning sign"
  ],
  "follow_up_plan": [
    "follow-up item"
  ],
  "emotional_support": [
    "support suggestion"
  ],
  "disclaimer": "medical safety disclaimer"
}

Rules:

1. Use simple, patient-friendly language.
2. Use only information supported by the supplied report analysis.
3. Do not make a diagnosis.
4. Do not prescribe or change medicines.
5. Do not invent treatments, findings, stages, or test results.
6. Encourage consultation with a qualified healthcare professional.
7. For urgent warning signs, advise contacting emergency services or a doctor.
8. Use empty lists when array information is unavailable.
9. Use null when a text field cannot be determined.
10. Do not include markdown fences.
11. Do not add text outside the JSON object.
"""


# ---------------------------------------------------------------------------
# Caregiver guidance response format
# ---------------------------------------------------------------------------

_CAREGIVER_GUIDANCE_SCHEMA = """
Return ONLY one valid JSON object with exactly these keys:

{
  "overview": "short caregiver-friendly overview or null",
  "daily_support": [
    "support action"
  ],
  "medication_support": [
    "support action"
  ],
  "appointment_support": [
    "support action"
  ],
  "nutrition_support": [
    "support action"
  ],
  "mobility_support": [
    "support action"
  ],
  "emotional_support": [
    "support action"
  ],
  "warning_signs": [
    "warning sign"
  ],
  "caregiver_wellbeing": [
    "caregiver self-care suggestion"
  ],
  "disclaimer": "medical safety disclaimer"
}

Rules:

1. Use clear and supportive language.
2. Use only information supported by the supplied report analysis.
3. Do not make a diagnosis.
4. Do not prescribe or change medicines.
5. Do not invent treatment instructions.
6. Do not recommend unsafe physical assistance.
7. Encourage consultation with qualified healthcare professionals.
8. Use empty lists when array information is unavailable.
9. Use null when a text field cannot be determined.
10. Do not include markdown fences.
11. Do not add text outside the JSON object.
"""


def _extract_json(raw_text: str) -> dict[str, Any]:
    """
    Extract a JSON object from Gemini's response.

    Gemini is instructed to return only JSON, but this function also removes
    markdown fences in case the model includes them.
    """

    if not raw_text or not raw_text.strip():
        raise ValueError("Gemini returned an empty response.")

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
        match = re.search(
            r"\{.*\}",
            cleaned,
            re.DOTALL,
        )

        if match is None:
            raise

        parsed = json.loads(match.group(0))

    if not isinstance(parsed, dict):
        raise ValueError(
            "Gemini guidance response must be a JSON object."
        )

    return parsed


def _ensure_list(value: Any) -> list[Any]:
    """Return the value only when it is a list."""

    if isinstance(value, list):
        return value

    return []


def _object_to_json_text(value: Any) -> str:
    """
    Convert dictionaries, Pydantic schemas, or ORM objects into JSON text.
    """

    if value is None:
        return "{}"

    if isinstance(value, dict):
        payload = value

    elif hasattr(value, "model_dump"):
        payload = value.model_dump(
            mode="json",
        )

    elif hasattr(value, "__dict__"):
        payload = {
            key: item
            for key, item in vars(value).items()
            if not key.startswith("_")
        }

    else:
        payload = {
            "value": str(value),
        }

    return json.dumps(
        payload,
        ensure_ascii=False,
        default=str,
        indent=2,
    )


class GuidanceAiService:
    """
    Gemini service for patient and caregiver guidance generation.
    """

    def __init__(self) -> None:
        self._client: genai.Client | None = None

        if settings.GEMINI_API_KEY:
            self._client = genai.Client(
                api_key=settings.GEMINI_API_KEY,
            )

        else:
            logger.warning(
                "GEMINI_API_KEY is not configured. "
                "AI guidance generation is unavailable."
            )

    async def generate_personalized_guidance(
        self,
        analysis_fields: Any,
        patient_profile: Any | None = None,
    ) -> dict[str, Any]:
        """
        Generate personalized patient guidance.

        This method name is required because GuidanceService calls:

        generate_personalized_guidance(...)
        """

        prompt = (
            "You are a clinical oncology patient-support assistant.\n\n"
            "Create safe, personalized, patient-friendly guidance using only "
            "the supplied report analysis and optional patient profile.\n\n"
            f"{_PATIENT_GUIDANCE_SCHEMA}\n\n"
            "----- REPORT ANALYSIS START -----\n"
            f"{_object_to_json_text(analysis_fields)}\n"
            "----- REPORT ANALYSIS END -----\n\n"
            "----- PATIENT PROFILE START -----\n"
            f"{_object_to_json_text(patient_profile)}\n"
            "----- PATIENT PROFILE END -----"
        )

        parsed = await self._generate_json(
            prompt=prompt,
            guidance_type="personalized patient",
        )

        return self._normalize_patient_guidance(parsed)

    async def generate_patient_guidance(
        self,
        analysis: Any,
        patient_profile: Any | None = None,
    ) -> dict[str, Any]:
        """
        Alias for generate_personalized_guidance.

        This allows both method names to work.
        """

        return await self.generate_personalized_guidance(
            analysis_fields=analysis,
            patient_profile=patient_profile,
        )

    async def generate_caregiver_guidance(
        self,
        analysis_fields: Any,
        patient_profile: Any | None = None,
    ) -> dict[str, Any]:
        """Generate structured caregiver-support guidance."""

        prompt = (
            "You are a clinical oncology caregiver-support assistant.\n\n"
            "Create safe, practical, and supportive caregiver guidance using "
            "only the supplied report analysis and optional patient profile.\n\n"
            f"{_CAREGIVER_GUIDANCE_SCHEMA}\n\n"
            "----- REPORT ANALYSIS START -----\n"
            f"{_object_to_json_text(analysis_fields)}\n"
            "----- REPORT ANALYSIS END -----\n\n"
            "----- PATIENT PROFILE START -----\n"
            f"{_object_to_json_text(patient_profile)}\n"
            "----- PATIENT PROFILE END -----"
        )

        parsed = await self._generate_json(
            prompt=prompt,
            guidance_type="caregiver",
        )

        return self._normalize_caregiver_guidance(parsed)

    async def _generate_json(
        self,
        prompt: str,
        guidance_type: str,
    ) -> dict[str, Any]:
        """Send the prompt to Gemini and parse its JSON response."""

        if self._client is None:
            raise ServiceUnavailableException(
                message=(
                    "AI guidance generation is not configured "
                    "on this server."
                )
            )

        try:
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )

            raw_text = response.text

            if not raw_text or not raw_text.strip():
                raise ValueError(
                    "Gemini returned an empty guidance response."
                )

        except Exception as exc:
            logger.exception(
                "Gemini %s guidance generation failed. Model=%s",
                guidance_type,
                settings.GEMINI_MODEL,
            )

            raise ServiceUnavailableException(
                message=(
                    "AI guidance generation failed. "
                    "Please try again later."
                )
            ) from exc

        try:
            return _extract_json(raw_text)

        except (
            json.JSONDecodeError,
            AttributeError,
            TypeError,
            ValueError,
        ) as exc:
            logger.exception(
                "Failed to parse Gemini %s guidance response.",
                guidance_type,
            )

            raise ServiceUnavailableException(
                message=(
                    "AI guidance generation returned "
                    "an unexpected response."
                )
            ) from exc

    @staticmethod
    def _normalize_patient_guidance(
        parsed: dict[str, Any],
    ) -> dict[str, Any]:
        """Convert patient guidance into safe expected values."""

        return {
            "overview": parsed.get("overview"),
            "immediate_actions": _ensure_list(
                parsed.get("immediate_actions")
            ),
            "questions_for_doctor": _ensure_list(
                parsed.get("questions_for_doctor")
            ),
            "medication_guidance": _ensure_list(
                parsed.get("medication_guidance")
            ),
            "nutrition_guidance": _ensure_list(
                parsed.get("nutrition_guidance")
            ),
            "activity_guidance": _ensure_list(
                parsed.get("activity_guidance")
            ),
            "warning_signs": _ensure_list(
                parsed.get("warning_signs")
            ),
            "follow_up_plan": _ensure_list(
                parsed.get("follow_up_plan")
            ),
            "emotional_support": _ensure_list(
                parsed.get("emotional_support")
            ),
            "disclaimer": (
                parsed.get("disclaimer")
                or (
                    "This guidance is for educational support only and "
                    "does not replace advice from a qualified healthcare "
                    "professional."
                )
            ),
        }

    @staticmethod
    def _normalize_caregiver_guidance(
        parsed: dict[str, Any],
    ) -> dict[str, Any]:
        """Convert caregiver guidance into safe expected values."""

        return {
            "overview": parsed.get("overview"),
            "daily_support": _ensure_list(
                parsed.get("daily_support")
            ),
            "medication_support": _ensure_list(
                parsed.get("medication_support")
            ),
            "appointment_support": _ensure_list(
                parsed.get("appointment_support")
            ),
            "nutrition_support": _ensure_list(
                parsed.get("nutrition_support")
            ),
            "mobility_support": _ensure_list(
                parsed.get("mobility_support")
            ),
            "emotional_support": _ensure_list(
                parsed.get("emotional_support")
            ),
            "warning_signs": _ensure_list(
                parsed.get("warning_signs")
            ),
            "caregiver_wellbeing": _ensure_list(
                parsed.get("caregiver_wellbeing")
            ),
            "disclaimer": (
                parsed.get("disclaimer")
                or (
                    "This guidance is for educational support only and "
                    "does not replace advice from a qualified healthcare "
                    "professional."
                )
            ),
        }