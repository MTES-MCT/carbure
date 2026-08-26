from enum import StrEnum
from typing import TypedDict


class Severity(StrEnum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class ConsistencyCheck(TypedDict):
    code: str
    level: Severity
    message: str
