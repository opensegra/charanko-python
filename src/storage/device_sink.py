import asyncio
from pathlib import Path

from contracts.media_types import MIME_TYPES
from contracts.storage_contracts import MediaHints, StoredFile, TranscodeOptions
from storage.file_manager import FileManager, ResolvedFile


class DeviceSink:
    def __init__(
        self,
        final_path: Path,
        file_manager: FileManager,
        transcode: TranscodeOptions | None = None,
    ) -> None:
        self._final_path = final_path
        self._part_path = Path(f"{final_path}.part")
        self._file_manager = file_manager
        self._transcode = transcode
        self._stream = self._part_path.open("wb")

    async def write(self, data: bytes) -> None:
        await asyncio.to_thread(self._stream.write, data)

    async def finalize(
        self, file: ResolvedFile, headers: dict[str, str], is_fmp4: bool | None = None
    ) -> StoredFile:

        await asyncio.to_thread(self._stream.flush)
        await asyncio.to_thread(self._stream.close)

        await asyncio.to_thread(self._part_path.replace, self._final_path)

        finalized = await self._file_manager.finalize_file(
            str(self._final_path),
            self._transcode,
            is_fmp4,
            MediaHints(
                extension=file.extension,
                mime_type=(
                    MIME_TYPES.get(file.extension)
                    or headers.get("content-type", "").split(";")[0].strip()
                    or None
                ),
            ),
        )

        stats = await asyncio.to_thread(Path(finalized.path).stat)

        return StoredFile(
            path=finalized.path,
            original_filename=finalized.filename,
            extended_filename=finalized.filename,
            mime_type=finalized.mime_type,
            is_fmp4=is_fmp4,
            extension=finalized.extension,
            size_bytes=stats.st_size,
        )

    async def cleanup(self) -> None:
        if not self._stream.closed:
            await asyncio.to_thread(self._stream.close)

        await asyncio.to_thread(self._part_path.unlink, missing_ok=True)
