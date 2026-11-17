from typing import Any

from charanko_exception import CharankoException
from contracts.exception_contracts import ErrorCode, ExceptionOptions, ExceptionPayload


class DownloadException(CharankoException):
    def __init__(self, url: str, reason: str, options: ExceptionOptions):
        self.url: str = url
        self.reason: str = reason
        options = options or ExceptionOptions()

        context: dict[str, Any] = {"url": self.url, **options.context}

        super().__init__(
            ExceptionPayload(
                cause=options.cause,
                code=ErrorCode.DOWNLOAD_FAILED,
                message=self._build_message(url, reason),
                context=context,
            )
        )

    @staticmethod
    def _build_message(url: str, reason: str) -> str:
        return f"Download failed for {url}: {reason}"
