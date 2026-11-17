from dataclasses import dataclass, field
from types.error_codes import ErrorCode
from typing import Any


@dataclass
class ExceptionOptions:
    context: dict[str, Any] = field(default_factory=dict)
    cause: BaseException | None = None


@dataclass
class ExceptionPayload:
    code: ErrorCode
    message: str
    context: dict[str, Any] = field(default_factory=dict)
    cause: BaseException | None = None


@dataclass
class ExceptionOutput(ExceptionPayload):
    name: str
