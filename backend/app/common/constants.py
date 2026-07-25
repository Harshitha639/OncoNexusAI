"""Application-wide constants. Avoid duplicating magic strings/numbers elsewhere."""

from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class ApiTags(str, Enum):
    """Tags used to group endpoints in the OpenAPI/Swagger docs."""

    HEALTH = "Health"
    AUTH = "Authentication"
    USERS = "Users"
    PATIENTS = "Patients"
    REPORTS = "Medical Reports"
    RISK_ASSESSMENT = "Risk Assessment"
    AGENTS = "AI Agents"
    REHABILITATION = "Rehabilitation"


class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    FAIL = "fail"


DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
