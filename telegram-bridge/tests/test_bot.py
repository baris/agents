import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from telegram import CallbackQuery, Message, Update, User

from src.bot import TelegramBridgeBot
from src.config import Settings


def create_settings() -> Settings:
    return Settings(
        telegram_bot_token="abc:123",
        whitelisted_user_id=12345,
        use_topics=True,
        default_workspace_dir="/tmp/test_workspace",
    )


def test_authorization_check() -> None:
    """Verifies that only whitelisted user IDs are authorized."""
    settings = create_settings()
    bot = TelegramBridgeBot(settings)

    # Authorized user
    update_auth = MagicMock(spec=Update)
    user_auth = MagicMock(spec=User)
    user_auth.id = 12345
    update_auth.effective_user = user_auth
    assert bot._is_authorized(update_auth) is True

    # Unauthorized user
    update_unauth = MagicMock(spec=Update)
    user_unauth = MagicMock(spec=User)
    user_unauth.id = 99999
    update_unauth.effective_user = user_unauth
    assert bot._is_authorized(update_unauth) is False


@pytest.mark.asyncio
async def test_autoaccept_command() -> None:
    """Verifies the /autoaccept command toggles session auto_accept."""
    settings = create_settings()
    bot = TelegramBridgeBot(settings)

    # Mock dependencies
    bot.agent_manager = MagicMock()
    mock_session = MagicMock()
    mock_session.auto_accept = False
    bot.agent_manager.get_session.return_value = mock_session

    # Prepare Update
    update = MagicMock(spec=Update)
    user = MagicMock(spec=User)
    user.id = 12345
    update.effective_user = user
    message = MagicMock(spec=Message)
    message.message_thread_id = 99
    update.message = message

    # Call handler
    context = MagicMock()
    await bot.handle_autoaccept(update, context)

    # Should toggle session status
    assert mock_session.auto_accept is True
    message.reply_text.assert_called_once()
    assert "ENABLED" in message.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_callback_resolution() -> None:
    """Verifies that callback query clicks resolve the corresponding future."""
    settings = create_settings()
    bot = TelegramBridgeBot(settings)

    # Setup pending approval
    future: asyncio.Future[bool] = asyncio.Future()
    bot.pending_approvals["future_123"] = future

    # Prepare Callback Query Update
    update = MagicMock(spec=Update)
    user = MagicMock(spec=User)
    user.id = 12345
    update.effective_user = user

    query = MagicMock(spec=CallbackQuery)
    query.data = "approve:future_123"
    update.callback_query = query

    # Call handler
    context = MagicMock()
    await bot.handle_callback(update, context)

    # The future should resolve with True (approved)
    assert future.done()
    assert future.result() is True
    query.edit_message_text.assert_called_once()


@pytest.mark.asyncio
async def test_handle_workspace_command() -> None:
    """Verifies the /workspace command views and changes workspace path."""
    settings = create_settings()
    bot = TelegramBridgeBot(settings)
    bot.agent_manager = MagicMock()

    mock_session = MagicMock()
    mock_session.workspace_dir = "/old/path"
    mock_session.is_running = False
    mock_session.close = AsyncMock()
    bot.agent_manager.get_session.return_value = mock_session
    bot.agent_manager.topic_mappings = {}

    # Case 1: View path
    update = MagicMock(spec=Update)
    user = MagicMock(spec=User)
    user.id = 12345
    update.effective_user = user
    message = MagicMock(spec=Message)
    message.text = "/workspace"
    message.message_thread_id = 123
    update.message = message

    await bot.handle_workspace(update, MagicMock())
    message.reply_text.assert_called_with(
        "Current workspace: `/old/path`\n\nTo change it, use: `/workspace <absolute_path>`",
        parse_mode="Markdown",
        message_thread_id=123,
    )

    # Case 2: Change path
    message.text = "/workspace /new/path"
    await bot.handle_workspace(update, MagicMock())
    assert mock_session.workspace_dir == "/new/path"
    assert bot.agent_manager.topic_mappings[123] == "/new/path"
    assert "Workspace updated to" in message.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_dynamic_chat_id_routing() -> None:
    """Verifies that incoming prompts update the session chat_id for approval routing."""
    settings = create_settings()
    bot = TelegramBridgeBot(settings)
    bot.agent_manager = MagicMock()

    mock_session = MagicMock()
    mock_session.is_running = False
    bot.agent_manager.get_session.return_value = mock_session

    update = MagicMock(spec=Update)
    user = MagicMock(spec=User)
    user.id = 12345
    update.effective_user = user
    
    # Setup mock chat
    chat = MagicMock()
    chat.id = 99999
    update.effective_chat = chat

    message = MagicMock(spec=Message)
    message.text = "Hello world"
    message.message_thread_id = 456
    update.message = message

    await bot.handle_message(update, MagicMock())
    # Should store the chat ID in the session
    assert mock_session.chat_id == 99999

