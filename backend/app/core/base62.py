"""
Base62 encoding for short URL codes.

Why Base62 instead of a raw incrementing ID or a UUID?
- A raw integer ID (e.g. "125000") is short but looks unprofessional and leaks
  how many URLs have been created (business-metric leakage).
- A UUID (e.g. "550e8400-e29b-41d4-a716-446655440000") is safe but far too long
  for a "short" URL.
- Base62 (0-9, a-z, A-Z = 62 symbols) gives us the shortest possible
  representation of an integer ID while staying URL-safe (no encoding needed,
  unlike Base64 which introduces +, /, = characters).

With 6 characters of Base62 we get 62^6 ≈ 56.8 billion unique codes, which is
more than enough headroom for a portfolio-scale (or honestly mid-size
production) service before we'd need to move to 7 characters.
"""

from app.core.config import settings

ALPHABET = settings.base62_alphabet
BASE = len(ALPHABET)
CHAR_TO_INDEX = {char: index for index, char in enumerate(ALPHABET)}


def encode(number: int) -> str:
    """Encode a non-negative integer into a Base62 string."""
    if number < 0:
        raise ValueError("Cannot Base62-encode a negative number")

    if number == 0:
        return ALPHABET[0]

    digits = []
    while number > 0:
        number, remainder = divmod(number, BASE)
        digits.append(ALPHABET[remainder])

    return "".join(reversed(digits))


def decode(code: str) -> int:
    """Decode a Base62 string back into its integer value."""
    number = 0
    for char in code:
        if char not in CHAR_TO_INDEX:
            raise ValueError(f"Invalid Base62 character: {char!r}")
        number = number * BASE + CHAR_TO_INDEX[char]
    return number


def id_to_short_code(row_id: int) -> str:
    """
    Convert a database row id into the public-facing short code.

    We add `settings.id_offset` before encoding so early IDs don't produce
    single-character codes (row 1 -> "1"), and so the produced codes look
    consistent in length as the table grows.
    """
    return encode(row_id + settings.id_offset)


def short_code_to_id(code: str) -> int:
    """Reverse of `id_to_short_code`."""
    return decode(code) - settings.id_offset
