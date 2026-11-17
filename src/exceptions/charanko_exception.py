from types.error_codes import ErrorCode
from typing import Any

from contracts.exception_contracts import ExceptionOutput, ExceptionPayload


class CharankoException(Exception):
    """Base for every charanko exception"""

    def __init__(self, payload: ExceptionPayload):
        super().__init__(payload.message)

        self.code: ErrorCode = payload.code
        self.context: dict[str, Any] = payload.context
        self.cause: BaseException | None = payload.cause

        if self.cause is None:
            self.__cause__ = self.cause

    @property
    def name(self) -> str:
        return type(self).__name__

    def to_dict(self) -> ExceptionOutput:
        return ExceptionOutput(
            cause=str(self.cause) if self.cause is not None else None,
            context=self.context,
            code=self.code.value,
            message=str(self),
            name=self.name,
        )

    def __str__(self):
        return super().__str__()
