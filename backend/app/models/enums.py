"""Shared enumerations used across ORM models and schemas."""

import enum


class RoleName(str, enum.Enum):
    """Fixed set of platform roles. Stored as the `roles.name` value."""

    PATIENT = "patient"
    DOCTOR = "doctor"
    CAREGIVER = "caregiver"
    ADMIN = "admin"


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class BloodGroup(str, enum.Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    UNKNOWN = "unknown"


class SmokingStatus(str, enum.Enum):
    NEVER = "never"
    FORMER = "former"
    CURRENT = "current"


class AlcoholConsumption(str, enum.Enum):
    NEVER = "never"
    OCCASIONAL = "occasional"
    REGULAR = "regular"
    FREQUENT = "frequent"


class ReportFileType(str, enum.Enum):
    PDF = "pdf"
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"


class OcrStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AiSummaryStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class NotificationType(str, enum.Enum):
    APPOINTMENT_REMINDER = "appointment_reminder"
    MEDICATION_REMINDER = "medication_reminder"
    REPORT_UPLOAD_SUCCESS = "report_upload_success"
    GENERAL = "general"
