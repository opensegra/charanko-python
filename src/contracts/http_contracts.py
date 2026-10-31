from dataclasses import dataclass
from typing import Literal


@dataclass
class HttpAgentOptions:
    user_agent: str | None = None
    enable_sni_spoofing: bool | None = None
    proxy: str | None = None
    dispatcher: str | None = None


@dataclass
class ProxyOptions:
    type: Literal["http", "https", "socks4", "socks5"]
    host: str
    port: int
    username: str | None = None
    password: str | None = None


@dataclass
class HttpOptions(HttpAgentOptions):
    signal: object | None = None
    headers: dict[str, str] | None = None
    timeout_ms: int | None = None
    retries: int | None = None
    referrer: str | None = None
    forma_data: dict[str, str] | None = None
