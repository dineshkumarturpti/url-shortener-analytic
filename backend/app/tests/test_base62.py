import pytest

from app.core import base62


class TestBase62Encoding:
    def test_encode_zero(self):
        assert base62.encode(0) == base62.ALPHABET[0]

    def test_encode_decode_round_trip(self):
        for number in [1, 42, 1000, 56800235583, 999_999_999]:
            code = base62.encode(number)
            assert base62.decode(code) == number

    def test_encode_is_deterministic(self):
        assert base62.encode(123456) == base62.encode(123456)

    def test_encode_negative_raises(self):
        with pytest.raises(ValueError):
            base62.encode(-1)

    def test_decode_invalid_character_raises(self):
        with pytest.raises(ValueError):
            base62.decode("!!!not-valid!!!")

    def test_larger_ids_produce_longer_or_equal_codes(self):
        short_code = base62.encode(10)
        long_code = base62.encode(10_000_000_000)
        assert len(long_code) >= len(short_code)


class TestShortCodeConversion:
    def test_id_to_short_code_round_trip(self):
        for row_id in [1, 2, 100, 999999]:
            code = base62.id_to_short_code(row_id)
            assert base62.short_code_to_id(code) == row_id

    def test_id_offset_avoids_tiny_codes_for_early_rows(self):
        # Row id 1 should not encode to a single trivial character thanks to
        # the configured offset -- this guards against accidental collisions
        # with reserved routes like "/health".
        code = base62.id_to_short_code(1)
        assert len(code) >= 3
