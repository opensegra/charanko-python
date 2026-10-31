import re
from urllib.parse import urlsplit, urlunsplit


class KvsResolver:
    """Deciphers KVS function/N/ media URLs with the site's license code."""

    @staticmethod
    def resolve(url: str, license_code: str | None = None) -> str:
        """Returns the playable URL or the original URL if it isn't a KVS URL."""

        match = re.match(r"^function/\d+/(.+)$", url, re.IGNORECASE)

        if not match or not license_code:
            return url

        parsed = urlsplit(match.group(1))
        segments = parsed.path.split("/")
        token = segments[3] if len(segments) > 3 else None

        if not token or len(token) < 32:
            return urlunsplit(parsed)

        segments[3] = KvsResolver._decipher(token[:32], license_code) + token[32:]

        new_path = "/".join(segments)

        return urlunsplit(
            (
                parsed.scheme,
                parsed.netloc,
                new_path,
                parsed.query,
                parsed.fragment,
            )
        )

    @staticmethod
    def _seeds(license_code: str) -> list[int]:
        normalized = license_code.replace("$", "")

        digits = [int(char) for char in normalized]
        non_zero = normalized.replace("0", "1")

        midpoint = len(non_zero) // 2
        left = int(non_zero[: midpoint + 1])
        right = int(non_zero[midpoint:])

        seed = str(4 * abs(left - right))[: midpoint + 1]

        seeds = []

        for index, digit in enumerate(seed):
            value = int(digit)

            for offset in range(4):
                seeds.append((digits[index + offset] + value) % 10)

        return seeds

    @staticmethod
    def _decipher(hash_value: str, license_code: str) -> str:
        seeds = KvsResolver._seeds(license_code)
        chars = list(hash_value)

        offset = 0
        char_length = len(chars)

        for index in range(char_length - 1, -1, -1):
            offset += seeds[index]

            target = (index + offset) % char_length

            chars[index], chars[target] = chars[target], chars[index]

        return "".join(chars)
