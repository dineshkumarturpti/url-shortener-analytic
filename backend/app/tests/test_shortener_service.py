from app.db import redis_client
from app.services import shortener


class TestCreateShortUrl:
    def test_creates_row_with_generated_short_code(self, db_session):
        url_row = shortener.create_short_url(db_session, long_url="https://example.com/a/long/path")

        assert url_row.id is not None
        assert url_row.short_code != ""
        assert url_row.long_url == "https://example.com/a/long/path"

    def test_two_urls_get_different_short_codes(self, db_session):
        first = shortener.create_short_url(db_session, long_url="https://example.com/one")
        second = shortener.create_short_url(db_session, long_url="https://example.com/two")

        assert first.short_code != second.short_code

    def test_creation_warms_the_cache(self, db_session):
        url_row = shortener.create_short_url(db_session, long_url="https://example.com/warm")

        cached_value = redis_client.get_cached_url(url_row.short_code)
        assert cached_value == "https://example.com/warm"


class TestResolveShortCode:
    def test_resolves_from_cache_without_hitting_db_again(self, db_session):
        url_row = shortener.create_short_url(db_session, long_url="https://example.com/cached")

        # Simulate the DB being unavailable by deleting the row directly --
        # resolution should still succeed purely from the cache.
        db_session.delete(url_row)
        db_session.commit()

        resolved = shortener.resolve_short_code(db_session, url_row.short_code)
        assert resolved == "https://example.com/cached"

    def test_resolves_from_db_on_cache_miss_and_repopulates_cache(self, db_session):
        url_row = shortener.create_short_url(db_session, long_url="https://example.com/miss")
        redis_client.invalidate_cached_url(url_row.short_code)

        assert redis_client.get_cached_url(url_row.short_code) is None

        resolved = shortener.resolve_short_code(db_session, url_row.short_code)
        assert resolved == "https://example.com/miss"
        # Cache should now be repopulated (cache-aside pattern).
        assert redis_client.get_cached_url(url_row.short_code) == "https://example.com/miss"

    def test_unknown_short_code_returns_none(self, db_session):
        assert shortener.resolve_short_code(db_session, "doesnotexist") is None


class TestAnalyticsIntegration:
    def test_click_is_recorded_and_counted(self, db_session):
        from app.services import analytics

        url_row = shortener.create_short_url(db_session, long_url="https://example.com/tracked")
        analytics.record_click(db_session, url_id=url_row.id, referrer="https://google.com", user_agent="pytest")
        analytics.record_click(db_session, url_id=url_row.id, referrer=None, user_agent="pytest")

        assert analytics.get_total_clicks(db_session, url_row.id) == 2
        recent = analytics.get_recent_clicks(db_session, url_row.id)
        assert len(recent) == 2
