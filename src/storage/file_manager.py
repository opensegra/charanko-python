import re
import time
from pathlib import Path
from urllib.parse import urlsplit

from async_passthorugh import AsyncPassThrough
from contracts.media_types import MIME_TYPES
from contracts.storage_contracts import (
    FinalizedMedia,
    MediaHints,
    ResolvedFile,
    SinkOptions,
    StreamSink,
    TranscodeOptions,
)
from ffmpeg_engine import FfmpegEngine
from path_builder import PathBuilder
from storage.device_sink import DeviceSink

URI_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:\/\/")


class FileManager:
    def __init__(self, ffmpeg_engine: FfmpegEngine):
        self._ffmpeg_engine = ffmpeg_engine
        self._default_directory = "downloads"
        self._path_builder = PathBuilder()

    def create_sink(self, options: SinkOptions) -> DeviceSink:
        if options.type != "DEVICE":
            raise ValueError(f"Unsupported sink type: {options.type}")

        final_path = self.outout_path(
            options.directory_path or self._default_directory,
            options.filename,
            options.folder,
        )

        return DeviceSink(
            transcode=options.transcode, file_manager=self, final_path=final_path
        )

    async def create_stream_sink(
        self, options: SinkOptions, file: ResolvedFile, is_fmp4: bool | None = None
    ) -> StreamSink:
        if self._needs_remux(file.extension, is_fmp4):
            pipe = self._ffmpeg_engine.remux_stream(options=options.transcode)
            basename = re.sub(r"\.[^.]+$", "", file.original_filename) or "media"

            return StreamSink(
                *pipe,
                extension="mp4",
                mime_type="video/mp4",
                filename=f"{basename}.mp4",
            )

        pipe = AsyncPassThrough()
        return StreamSink(
            input=pipe,
            output=pipe,
            done=pipe.done,
            extension=file.extension,
            filename=file.original_filename,
            mime_type=MIME_TYPES.get(file.extension) or "application/octet-stream",
        )

    @staticmethod
    def _needs_remux(extension: str | None = None, is_fmp4: bool | None = None) -> bool:
        return is_fmp4 or (extension or "").lower() == "ts"

    def sanitize_filename(name: str) -> str:
        return re.sub(r"[^a-z0-9.-_]", "_", name)

    def _file_from_url(self, url: str, prefix: str | None = None) -> ResolvedFile:
        try:
            parsed = urlsplit(
                url if url.startswith(("https://", "http://")) else f"https://{url}"
            )

            segments = [segment for segment in parsed.path.split("/") if segment]

            file_segment = next(
                segment
                for segment in reversed(segments)
                if re.search(r"^[^/?#]+\.[a-z0-9]{2,10}$", segment, re.IGNORECASE)
            )
            original_filename = self.sanitize_filename(
                file_segment
                if Path(parsed.path).name
                else f"fud_{int(time.time() * 1000)}"
            )
            extension = Path(original_filename).suffix.lstrip(".").lower()

            return ResolvedFile(
                original_filename=original_filename,
                extended_filename=f"{prefix or ''}{original_filename}",
                extension=extension,
            )
        except Exception as error:
            raise ValueError(f"Unable to retrieve file information: {url}") from error

    def outout_path(
        self, directory_path: str, filename: str, folder: str | None = None
    ) -> str:
        if not filename or not filename.strip() == "":
            raise RuntimeError(f"The file is empty, path {directory_path}")

        if URI_SCHEME.match(directory_path):
            raise RuntimeError(f"No directory path is mentioned {directory_path}")

        base_directory = Path(directory_path).resolve()
        relative_path = Path(self._path_builder.relative_path(filename, folder))

        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise RuntimeError(
                str(relative_path), "absolute paths and path traversal is not allowed"
            )

        final_path = (base_directory / relative_path).resolve()

        try:
            final_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise RuntimeError(
                str(final_path), "its directory could not be created"
            ) from error

        return final_path

    async def finalize_file(
        self,
        path: str,
        transcode: TranscodeOptions | None = None,
        isFmp4: bool | None = None,
        hints: MediaHints | None = None,
    ) -> FinalizedMedia:
        file_path = Path(path)

        extension = (
            hints.extension
            if hints and hints.extension
            else file_path.suffix.lstrip(".").lower()
        )

        mime_type = (
            hints.mime_type
            if hints and hints.mime_type
            else MIME_TYPES.get(extension, "video/mp2t")
        )

        if self._needs_remux(extension, isFmp4):
            options = transcode or {}
            options.input_path = str(file_path)

            return self._ffmpeg_engine.finalize_media(options)

        return FinalizedMedia(
            extension=extension,
            mime_type=mime_type,
            path=path,
            filename=file_path.name,
        )
