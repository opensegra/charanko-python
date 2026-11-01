import asyncio
from dataclasses import dataclass
from typing import Literal

from media_types import OutputType


@dataclass
class FinalizedMedia:
    path: str
    filename: str
    extension: str
    mime_type: str


TranscodePreset = Literal[
    "ultrafast", "superfast", "veryfast", "faster", "fast", "slow"
]


@dataclass
class ResolvedFile:
    original_filename: str
    extension: str
    extended_filename: str


@dataclass
class TranscodeOptions:
    input_path: str | None = None
    ffmpeg_path: str | None = None
    delete_input: bool | None = None
    ffmpeg_args: list[str] | None = None
    output_extension: str | None = None
    preset: TranscodePreset | None = None
    crf: int | None = None
    video_codec: str | None = None
    audio_codec: str | None = None


@dataclass
class MediaHints:
    extension: str | None = None
    mime_type: str | None = None


@dataclass
class RemuxPipe:
    input: asyncio.StreamWriter
    output: asyncio.StreamReader
    done: asyncio.Task[None]


@dataclass
class StreamSink(RemuxPipe):
    extension: str
    mime_type: str
    filename: str


@dataclass
class StoredFile:
    original_filename: str
    extension: str
    extended_filename: str
    mime_type: str
    size_bytes: int
    path: str
    is_fmp4: bool | None = None


@dataclass
class SinkOptions:
    type: OutputType
    transcode: TranscodeOptions | None = None
    directory_path: str | None = None
    filename: str
    folder: str | None = None
