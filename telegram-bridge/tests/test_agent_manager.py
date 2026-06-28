import asyncio
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.agent_manager import AgentManager, AgentSession


@pytest.mark.asyncio
async def test_agent_manager_scoping() -> None:
    """Verifies that AgentManager routes workspace paths based on Topic IDs."""
    topic_mappings = {123: "/tmp/workspace_a", 456: "/tmp/workspace_b"}

    # Dummy approval callback
    async def dummy_approval(topic_id: int | None, tool_call: Any) -> bool:
        return True

    manager = AgentManager(
        default_workspace="/tmp/default_workspace",
        topic_mappings=topic_mappings,
        approval_callback=dummy_approval,
    )

    # Scoped to mapped workspace
    session_a = manager.get_session(123)
    assert session_a.workspace_dir == "/tmp/workspace_a"

    # Scoped to default workspace
    session_default = manager.get_session(999)
    assert session_default.workspace_dir == "/tmp/default_workspace"

    # Scoped to default workspace (no topic)
    session_none = manager.get_session(None)
    assert session_none.workspace_dir == "/tmp/default_workspace"


@pytest.mark.asyncio
async def test_agent_session_approval() -> None:
    """Verifies that approval callback behaves properly and handles auto-accept."""
    future: asyncio.Future[bool] = asyncio.Future()
    future.set_result(True)

    approval_mock = MagicMock(return_value=future)

    session = AgentSession(
        topic_id=123, workspace_dir="/tmp/test_workspace", approval_callback=approval_mock
    )

    # Test autoaccept False triggers Telegram prompt callback
    tool_call = MagicMock()
    result = await session.handle_approval(tool_call)
    assert result is True
    approval_mock.assert_called_once_with(123, tool_call)

    # Test autoaccept True immediately returns True without calling Telegram prompt callback
    approval_mock.reset_mock()
    session.auto_accept = True
    result_auto = await session.handle_approval(tool_call)
    assert result_auto is True
    approval_mock.assert_not_called()


@pytest.mark.asyncio
async def test_agent_session_chat_streaming() -> None:
    """Verifies that chat streams thoughts and text correctly."""
    session = AgentSession(
        topic_id=123, workspace_dir="/tmp/test_workspace", approval_callback=AsyncMock()
    )

    mock_agent = MagicMock()
    mock_response = MagicMock()

    # Mock thoughts stream
    async def mock_thoughts(*args: Any, **kwargs: Any) -> AsyncGenerator[str, None]:
        yield "thought1"
        yield "thought2"

    # Mock response tokens stream
    async def mock_tokens(*args: Any, **kwargs: Any) -> AsyncGenerator[str, None]:
        yield "token1"
        yield "token2"

    mock_response.thoughts = mock_thoughts()
    mock_response.__aiter__ = mock_tokens
    mock_agent.chat = AsyncMock(return_value=mock_response)
    session.agent = mock_agent

    streamed_chunks = []
    async for chunk_type, content in session.chat("Hello"):
        streamed_chunks.append((chunk_type, content))

    assert streamed_chunks == [
        ("thought", "thought1"),
        ("thought", "thought2"),
        ("text", "token1"),
        ("text", "token2"),
    ]
