import json
import os
import tempfile

import pytest

from src.config import Settings


def test_settings_validation() -> None:
    """Verifies that Settings parses environment inputs correctly."""
    settings = Settings(
        telegram_bot_token="abc:123",
        whitelisted_user_id=987654321,
        use_topics=True,
        default_workspace_dir="/tmp/test_workspace",
    )
    assert settings.telegram_bot_token == "abc:123"
    assert settings.whitelisted_user_id == 987654321
    assert settings.use_topics is True
    assert settings.default_workspace_dir == "/tmp/test_workspace"


def test_topic_mappings_loading() -> None:
    """Verifies topic_mappings.json loading and mapping expansion."""
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        json.dump({"100": "/tmp/subdir_a", "200": "~/subdir_b"}, f)
        temp_filename = f.name

    try:
        settings = Settings(
            telegram_bot_token="abc:123",
            whitelisted_user_id=987654321,
            use_topics=True,
            topic_mappings_file=temp_filename,
            default_workspace_dir="/tmp/test_workspace",
        )
        settings.load_mappings()

        assert 100 in settings.topic_mappings
        assert settings.topic_mappings[100] == "/tmp/subdir_a"
        assert 200 in settings.topic_mappings
        # Path expansion should occur
        expected_expanded = os.path.abspath(os.path.expanduser("~/subdir_b"))
        assert settings.topic_mappings[200] == expected_expanded
    finally:
        os.unlink(temp_filename)


def test_settings_invalid_token() -> None:
    """Verifies that validation fails if the bot token is empty."""
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        Settings(
            telegram_bot_token="",
            whitelisted_user_id=12345,
            default_workspace_dir="/tmp/test_workspace",
        )


def test_settings_invalid_user_id() -> None:
    """Verifies that validation fails if whitelisted_user_id is 0."""
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        Settings(
            telegram_bot_token="abc:123",
            whitelisted_user_id=0,
            default_workspace_dir="/tmp/test_workspace",
        )

