from dataclasses import dataclass

from http_contracts import HttpOptions
from media_types import OutputType


@dataclass
class DownloadContract:
    url: str
    referrer: str | None
    folder: str | None
    licenseCode: str | None


@dataclass
class DownloadOptions(HttpOptions):
    output_type: OutputType
