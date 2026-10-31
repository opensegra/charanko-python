import posixpath
import re
from pathlib import Path


class PathBuilder:
    def relative_path(filename: str, folder: str | None = None) -> str:
        return str(Path(folder) / filename) if folder else filename

    def join(*segments: list[str]) -> str:
        return posixpath.join(*(segment for segment in segments if segment))

    def safe_name(name: str | None = None) -> str:
        return re.sub(r"[^a-zA-Z0-9]", "_", name or "unknown")
