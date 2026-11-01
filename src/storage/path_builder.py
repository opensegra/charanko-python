import posixpath
import re
from pathlib import Path


class PathBuilder:
    @staticmethod
    def relative_path(filename: str, folder: str | None = None) -> str:
        return str(Path(folder) / filename) if folder else filename

    @staticmethod
    def join(*segments: str) -> str:
        return posixpath.join(*(segment for segment in segments if segment))

    @staticmethod
    def safe_name(name: str | None = None) -> str:
        return re.sub(r"[^a-zA-Z0-9]", "_", name or "unknown")
