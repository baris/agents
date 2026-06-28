import json
import os

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    telegram_bot_token: str = Field(default="", validation_alias="TELEGRAM_BOT_TOKEN")
    whitelisted_user_id: int = Field(default=0, validation_alias="WHITELISTED_USER_ID")
    use_topics: bool = Field(default=True, validation_alias="USE_TOPICS")
    topic_mappings_file: str = Field(
        default="topic_mappings.json", validation_alias="TOPIC_MAPPINGS_FILE"
    )
    default_workspace_dir: str = Field(
        default="/Users/tbmetin/repos/agents", validation_alias="DEFAULT_WORKSPACE_DIR"
    )

    # Dictionary containing mapped topic IDs to directory paths
    topic_mappings: dict[int, str] = Field(default_factory=dict)

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", populate_by_name=True
    )

    @field_validator("telegram_bot_token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        if not v:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")
        return v

    @field_validator("whitelisted_user_id")
    @classmethod
    def validate_user_id(cls, v: int) -> int:
        if v == 0:
            raise ValueError("WHITELISTED_USER_ID environment variable is not set or invalid")
        return v

    @field_validator("default_workspace_dir")
    @classmethod
    def validate_workspace_dir(cls, v: str) -> str:
        expanded_path = os.path.abspath(os.path.expanduser(v))
        if not os.path.isdir(expanded_path):
            # We don't crash here if it doesn't exist yet, but we ensure it can be created
            pass
        return expanded_path

    def load_mappings(self) -> None:
        """Loads and parses topic_mappings_file if use_topics is True."""
        if not self.use_topics:
            return

        if not os.path.exists(self.topic_mappings_file):
            return

        try:
            with open(self.topic_mappings_file) as f:
                data = json.load(f)
                self.topic_mappings = {
                    int(k): os.path.abspath(os.path.expanduser(str(v))) for k, v in data.items()
                }
        except Exception as e:
            raise ValueError(f"Failed to parse topic mappings file: {e}") from e


def load_settings() -> Settings:
    """Utility factory to load and prepare application settings."""
    settings = Settings()
    settings.load_mappings()
    return settings
