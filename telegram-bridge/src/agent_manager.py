import asyncio
import os
from collections.abc import AsyncGenerator, Callable, Awaitable
from typing import Any

from google.antigravity import Agent, LocalAgentConfig
from google.antigravity.hooks import policy

from src.logger import get_logger

logger = get_logger("agent_manager")


class AgentSession:
    def __init__(
        self,
        topic_id: int | None,
        workspace_dir: str,
        approval_callback: Callable[[int | None, Any], Awaitable[bool]],
    ) -> None:
        self.topic_id = topic_id
        self.workspace_dir = workspace_dir
        self.approval_callback = approval_callback
        self.agent: Agent | None = None
        self.auto_accept = False
        self.is_running = False

    def __deepcopy__(self, memo: dict[int, Any]) -> "AgentSession":
        # Return self to prevent deep copying the session, which contains non-picklable bot references.
        return self

    def _create_policies(self) -> list[Any]:
        """Creates the set of workspace restrictions and confirmation hooks."""
        # Restrict agent file operations strictly to the mapped topic workspace
        policies = [
            policy.workspace_only([self.workspace_dir]),
            policy.confirm_run_command(handler=self.handle_approval),
            policy.ask_user("create_file", handler=self.handle_approval),
            policy.ask_user("edit_file", handler=self.handle_approval),
        ]
        return policies

    async def init_agent(self) -> None:
        """Initializes and starts the underlying Antigravity Agent context."""
        if self.agent:
            return

        # Ensure workspace directory exists
        os.makedirs(self.workspace_dir, exist_ok=True)

        config = LocalAgentConfig(
            workspaces=[self.workspace_dir],
            policies=self._create_policies(),
            app_data_dir=os.path.abspath(os.path.join(self.workspace_dir, ".antigravity_brain")),
        )
        self.agent = Agent(config=config)
        await self.agent.__aenter__()
        logger.info(
            "Initialized AgentSession",
            extra={"topic_id": self.topic_id, "workspace_dir": self.workspace_dir},
        )

    async def handle_approval(self, tool_call: Any) -> bool:
        """SDK policy hook called before execution of sensitive tools."""
        if self.auto_accept:
            logger.info("Auto-accepting tool execution", extra={"tool_call": str(tool_call)})
            return True

        logger.info(
            "Intercepted tool call, requesting Telegram approval",
            extra={"topic_id": self.topic_id, "tool_call": str(tool_call)},
        )
        # Trigger the Telegram bot controller's prompt and wait for the response
        return await self.approval_callback(self.topic_id, tool_call)

    async def chat(self, prompt: str) -> AsyncGenerator[tuple[str, str], None]:
        """Runs a chat turn on the agent, yielding thoughts and response text."""
        if not self.agent:
            await self.init_agent()

        assert self.agent is not None
        self.is_running = True
        try:
            response = await self.agent.chat(prompt)

            # Stream reasoning/thoughts if supported
            if hasattr(response, "thoughts") and response.thoughts:
                async for thought in response.thoughts:
                    yield "thought", thought

            # Stream final response tokens
            async for token in response:
                yield "text", token
        finally:
            self.is_running = False

    async def close(self) -> None:
        """Cleans up the Agent instance on teardown."""
        if self.agent:
            try:
                await self.agent.__aexit__(None, None, None)
            except Exception as e:
                logger.error("Error closing agent session", extra={"error": str(e)}, exc_info=True)
            self.agent = None


class AgentManager:
    def __init__(
        self,
        default_workspace: str,
        topic_mappings: dict[int, str],
        approval_callback: Callable[[int | None, Any], Awaitable[bool]],
    ) -> None:
        self.default_workspace = default_workspace
        self.topic_mappings = topic_mappings
        self.approval_callback = approval_callback
        self.sessions: dict[int | None, AgentSession] = {}

    def get_session(self, topic_id: int | None) -> AgentSession:
        """Retrieves or spins up an AgentSession for a specific Topic ID."""
        if topic_id in self.sessions:
            return self.sessions[topic_id]

        workspace_dir = self.topic_mappings.get(topic_id or 0, self.default_workspace)
        session = AgentSession(
            topic_id=topic_id, workspace_dir=workspace_dir, approval_callback=self.approval_callback
        )
        self.sessions[topic_id] = session
        return session

    async def close_all(self) -> None:
        """Closes all active agent sessions during teardown."""
        for session in list(self.sessions.values()):
            await session.close()
        self.sessions.clear()
