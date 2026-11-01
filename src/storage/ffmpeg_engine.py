import asyncio
from pathlib import Path

from contracts.storage_contracts import FinalizedMedia, RemuxPipe, TranscodeOptions

MISSING_FFMPEG = (
    "ffmpeg executable was not found.Install ffmpeg or pass transcode.ffmpeg_path."
)


class FfmpegEngine:
    """Remuxes or transcodes media using Ffmpeg"""

    @property
    def binary(self) -> str:
        """Returns the ffmpeg executable available on the system"""
        return self._find_ffmpeg()

    def _find_ffmpeg(self) -> str:
        from shutil import which

        binary = which("ffmpeg")

        if binary is None:
            raise FileNotFoundError(MISSING_FFMPEG)

        return binary

    def _binary_for(self, options: TranscodeOptions | None = None) -> str:
        return options.ffmpeg_path if options and options.ffmpeg_path else self.binary

    @staticmethod
    def _codec_args(
        video_codec: str | None = None,
        audio_codec: str | None = None,
        crf: str | None = None,
        preset: str | None = None,
    ) -> list[str]:
        args = ["-c:v", video_codec or "copy"]

        if video_codec == "libx264":
            args.extend(["-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2"])

        args.extend(["-c:a", audio_codec or "copy"])

        encoding = bool(video_codec) and video_codec != "copy"
        if encoding and crf is not None:
            args.extend(["-crf", str(crf)])

        if encoding and preset:
            args.extend("-preset", preset)

        return args

    async def remux_stream(self, options: TranscodeOptions | None = None) -> RemuxPipe:
        options = options or TranscodeOptions()

        codec_args = [
            "-c:v",
            options.video_codec or "copy",
            "-c:a",
            options.audio_codec or "copy",
            "-movflags",
            "frag_keyframe+empty_moov+default_base_moof",
        ]

        args = options.ffmpeg_args or [
            "-loglevel",
            "error",
            "-i",
            "pipe:0",
            *codec_args,
            "-f",
            "mp4",
            "pipe:1",
        ]

        binary = self._binary_for(options)

        process = await asyncio.create_subprocess_exec(
            binary,
            *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        assert process.stdin is not None
        assert process.stdout is not None
        assert process.stderr is not None

        async def monitor() -> None:
            stderr_tail = bytearray()

            async def collect_stderr() -> None:
                while chunk := await process.stderr.read(4096):
                    stderr_tail.extend(chunk)

                    if len(stderr_tail) > 2000:
                        del stderr_tail[:-2000]

            stderr_task = asyncio.create_task(collect_stderr())

            try:
                return_code = await process.wait()
                await stderr_task

                if return_code != 0:
                    stderr_text = stderr_tail.decode(errors="replace").strip()
                    raise RuntimeError(
                        f"ffmpeg exited with code {return_code}: {stderr_text}"
                    )

            except BaseException:
                if process.return_code is None:
                    process.kill()
                    await process.wait()

                if not stderr_task.done():
                    stderr_task.cancel()
                    await asyncio.gather(stderr_task, return_exceptions=True)
                raise

        done = asyncio.create_task(monitor())

        return RemuxPipe(input=process.stdin, output=process.stdout, done=done)

    async def finalize_media(self, options: TranscodeOptions) -> FinalizedMedia:
        if not options.input_path:
            raise ValueError("Input path is required for finalizing media")

        input_path = Path(options.input_path)
        output_filename = f"{input_path.stem}_final.{options.output_extension}"
        output_path = input_path.parent / output_filename

        args = options.ffmpeg_args or [
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(input_path),
            *self._codec_args(
                options.video_codec, options.audio_codec, options.crf, options.preset
            ),
            "-movflags",
            "+faststart",
            str(output_path),
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                self._binary_for(options),
                *args,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.DEVNULL,
            )

            _, stderr = await process.communicate()

            if process.returncode != 0:
                raise RuntimeError(stderr.decode(errors="replace").strip())

            if options.delete_input:
                await asyncio.to_thread(input_path.unlink)

            return FinalizedMedia(
                path=str(output_path),
                extension=options.output_extension,
                filename=output_filename,
                mime_type=f"video/{options.output_extension}",
            )
        except FileNotFoundError as error:
            raise RuntimeError(f"Failed to finalize media {MISSING_FFMPEG}") from error
        except Exception as error:
            raise RuntimeError(f"Failed to finalize media {error}") from error
