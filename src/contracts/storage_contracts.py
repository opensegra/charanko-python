import asyncio
from dataclasses import dataclass
from typing import Literal


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
class RemuxPipe:
    input: asyncio.StreamWriter
    output: asyncio.StreamReader
    done: asyncio.Task[None]
