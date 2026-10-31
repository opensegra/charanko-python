from enum import StrEnum


class VideoQuality(StrEnum):
    P144 = "144p"
    P240 = "240p"
    P360 = "360P"
    P480 = "480P"
    P720 = "720P"
    P1080 = "1080P"
    P1440 = "1440p"
    P2160 = "2160p"
    P4320 = "4320p"
    UNKNOWN = "unknown"


class VideoCodec(StrEnum):
    H264 = "h264"
    AV1 = "av1"


class VideoFormat(StrEnum):
    HLS = "hls"
    MP4 = "mp4"


class OutputType(StrEnum):
    DEVICE = "DEVICE"
    JSON = "JSON"
    STREAM = "STREAM"
    RETURN = "RETURN"
