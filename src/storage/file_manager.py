import re
import time
from pathlib import Path
from urllib.parse import urlsplit

from contracts.storage_contracts import ResolvedFile
from ffmpeg_engine import FfmpegEngine
from path_builder import PathBuilder

URI_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:\/\/")

MIME_TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "webp": "image/webp",
    "mp4": "video/mp4",
    "ts": "video/mp2t",
    "m3u8": "application/vnd.apple.mpegurl",
    "webm": "video/webm",
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
}


class FileManager:
    def __init__(self, ffmpeg_engine: FfmpegEngine):
        self._ffmpeg_engine = ffmpeg_engine
        self._default_directory = "downloads"
        self._path_builder = PathBuilder()

    def _needs_remux(extension: str | None = None, isFmp4: bool | None = None) -> bool:
        return isFmp4 or (extension or "").lower() == "ts"

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
                if re.search(r"^[^/?#]+\.[a-z0-9]{2,10}$", segment, re.I)
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
