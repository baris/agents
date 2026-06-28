import asyncio
import json
import os
import uuid
from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.agent_manager import AgentManager, AgentSession
from src.config import Settings
from src.logger import get_logger

logger = get_logger("bot")

# Track running tasks at module level to avoid deep copy pickling errors
# inside pydantic/deepcopy hooks.
RUNNING_TASKS: dict[int | None, asyncio.Task[Any]] = {}


class TelegramBridgeBot:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.agent_manager: AgentManager | None = None
        self.application: Application[Any, Any, Any, Any, Any, Any] | None = None
        self.pending_approvals: dict[str, asyncio.Future[bool]] = {}

    def _is_authorized(self, update: Update) -> bool:
        """Checks if the incoming message is from the whitelisted user ID."""
        user = update.effective_user
        if not user or user.id != self.settings.whitelisted_user_id:
            logger.warning(
                "Unauthorized access attempt",
                extra={
                    "user_id": user.id if user else None,
                    "username": user.username if user else None,
                },
            )
            return False
        return True

    async def start(self) -> None:
        """Starts the Telegram bot application loop."""
        self.agent_manager = AgentManager(
            default_workspace=self.settings.default_workspace_dir,
            topic_mappings=self.settings.topic_mappings,
            approval_callback=self.request_approval,
        )

        self.application = Application.builder().token(self.settings.telegram_bot_token).build()
        self._register_handlers()

        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()  # type: ignore[union-attr]
        logger.info("Telegram Bot started polling")

    def _register_handlers(self) -> None:
        """Registers all command, message, and callback handlers on the application."""
        assert self.application is not None
        self.application.add_handler(CommandHandler("start", self.handle_start))
        self.application.add_handler(CommandHandler("ask", self.handle_ask))
        self.application.add_handler(CommandHandler("status", self.handle_status))
        self.application.add_handler(CommandHandler("autoaccept", self.handle_autoaccept))
        self.application.add_handler(CommandHandler("cancel", self.handle_cancel))
        self.application.add_handler(CommandHandler("stop", self.handle_cancel))
        self.application.add_handler(CommandHandler("workspace", self.handle_workspace))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        # Handle plain text messages (back-and-forth chat)
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

    async def stop(self) -> None:
        """Stops the bot updater, application, and closes agent sessions."""
        if self.application:
            await self.application.updater.stop()  # type: ignore[union-attr]
            await self.application.stop()
            await self.application.shutdown()
        if self.agent_manager:
            await self.agent_manager.close_all()
        logger.info("Telegram Bot stopped")

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Greets the user and displays bot capabilities."""
        message = update.message
        if not message or not self._is_authorized(update):
            return
        await message.reply_text(
            "Welcome to the Antigravity 2.0 Remote Control Bridge!\n\n"
            "Commands:\n"
            "• `/ask <prompt>` or just send a plain text message - Run a turn on the agent\n"
            "• `/status` - View agent execution status and docs/TODO.md task queue\n"
            "• `/workspace [path]` - View or change active workspace directory\n"
            "• `/autoaccept` - Toggle auto-approval of all intercepted tools\n"
            "• `/cancel` or `/stop` - Abort the currently running agent execution",
            parse_mode="Markdown",
            message_thread_id=message.message_thread_id,
        )

    async def handle_ask(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Routes prompt payloads to the active agent session for the topic thread."""
        message = update.message
        if not message or not message.text or not self._is_authorized(update):
            return

        parts = message.text.split(" ", 1)
        if len(parts) < 2:
            await message.reply_text(
                "Please provide a prompt. Usage: `/ask <prompt>`",
                message_thread_id=message.message_thread_id,
            )
            return

        prompt = parts[1]
        thread_id = message.message_thread_id
        assert self.agent_manager is not None
        session = self.agent_manager.get_session(thread_id)
        session.chat_id = update.effective_chat.id if update.effective_chat else None

        if session.is_running:
            await message.reply_text(
                "An execution is already running for this workspace.",
                message_thread_id=thread_id,
            )
            return

        task = asyncio.create_task(
            self._process_and_stream_response(update, session, prompt, thread_id)
        )
        RUNNING_TASKS[thread_id] = task
        task.add_done_callback(lambda t: RUNNING_TASKS.pop(thread_id, None))

    async def _process_and_stream_response(
        self, update: Update, session: AgentSession, prompt: str, thread_id: int | None
    ) -> None:
        """Processes agent turn and streams formatted output chunk-by-chunk to avoid rate limits."""
        message = update.message
        if not message:
            return
        # Send placeholder message
        msg = await message.reply_text("Starting agent turn...", message_thread_id=thread_id)

        current_type = ""
        buffer = ""
        last_edit_time = 0.0

        async for chunk_type, token in session.chat(prompt):
            if chunk_type != current_type:
                # Flush the header block transition
                prefix = (
                    "\n\n🧠 *Thought Process*:\n"
                    if chunk_type == "thought"
                    else "\n\n🤖 *Agent Output*:\n"
                )
                buffer += prefix
                current_type = chunk_type

            buffer += token
            # Rate limit edits to once per 1.5 seconds to avoid Telegram API blocks
            now = asyncio.get_event_loop().time()
            if now - last_edit_time > 1.5:
                try:
                    await msg.edit_text(buffer[:4000], parse_mode="Markdown")
                    last_edit_time = now
                except Exception as e:
                    logger.debug("Failed to edit Telegram message chunk: %s", e)

        # Final flush
        try:
            await msg.edit_text(buffer[:4000], parse_mode="Markdown")
        except Exception as e:
            logger.error("Failed to edit Telegram message final flush: %s", e)

    async def request_approval(self, topic_id: int | None, tool_call: Any) -> bool:
        """Pushes a confirmation request card with buttons to Telegram and awaits response."""
        future_id = str(uuid.uuid4())
        future: asyncio.Future[bool] = asyncio.Future()
        self.pending_approvals[future_id] = future

        # Format details of the intercepted tool call
        name = getattr(tool_call, "name", str(tool_call))
        args = getattr(tool_call, "arguments", {})
        details = f"🔧 *Tool Execution Request*\n\n*Tool:* `{name}`\n"
        if args:
            details += f"*Arguments:*\n`{args}`\n"

        # Check path containment for shell execution to raise warnings for out-of-workspace activity
        if name == "run_command":
            cmd = args.get("CommandLine", "")
            cwd = args.get("Cwd", "")
            assert self.agent_manager is not None
            session = self.agent_manager.get_session(topic_id)
            workspace = os.path.abspath(session.workspace_dir)

            is_outside = False
            if cwd:
                abs_cwd = os.path.abspath(os.path.expanduser(cwd))
                if not abs_cwd.startswith(workspace):
                    is_outside = True

            # Simple token checking to catch absolute path or traversal traversal escapes
            for word in cmd.split():
                if os.path.isabs(word):
                    abs_word = os.path.abspath(word)
                    if not abs_word.startswith(workspace):
                        is_outside = True
                        break
                elif ".." in word:
                    is_outside = True
                    break

            if is_outside:
                details += (
                    "\n⚠️ *WARNING:* Command targets locations outside the active workspace!\n"
                )

        keyboard = [
            [
                InlineKeyboardButton("Approve ✅", callback_data=f"approve:{future_id}"),
                InlineKeyboardButton("Reject ❌", callback_data=f"reject:{future_id}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Resolve target chat ID dynamically based on the session or fallback whitelist
        assert self.agent_manager is not None
        session = self.agent_manager.get_session(topic_id)
        chat_id = session.chat_id or self.settings.whitelisted_user_id

        await self.application.bot.send_message(  # type: ignore[union-attr]
            chat_id=chat_id,
            text=details,
            reply_markup=reply_markup,
            parse_mode="Markdown",
            message_thread_id=topic_id,
        )

        try:
            return await future
        finally:
            self.pending_approvals.pop(future_id, None)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Processes the button interaction from the whitelisted user."""
        if not self._is_authorized(update) or not update.callback_query:
            return

        query = update.callback_query
        await query.answer()

        data = query.data
        if not data or ":" not in data:
            return

        decision, future_id = data.split(":", 1)
        future = self.pending_approvals.get(future_id)
        if not future or future.done():
            await query.edit_message_text("This request has expired or already been handled.")
            return

        approved = decision == "approve"
        future.set_result(approved)

        status_text = "Approved ✅" if approved else "Rejected ❌"
        message = query.message
        if not message or not isinstance(message, Message):
            await query.edit_message_text(f"Decision: {status_text}")
            return

        await query.edit_message_text(
            f"{message.text}\n\n*Decision:* {status_text}", parse_mode="Markdown"
        )

    async def handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Retrieves and displays the parsed task queue from the workspace docs/TODO.md."""
        message = update.message
        if not message or not self._is_authorized(update):
            return

        thread_id = message.message_thread_id
        assert self.agent_manager is not None
        session = self.agent_manager.get_session(thread_id)

        # Fetch status of agent
        status_text = (
            f"🔄 *Bridge Session Status*\n"
            f"*Workspace:* `{session.workspace_dir}`\n"
            f"*State:* `{'Busy 🤖' if session.is_running else 'Idle 💤'}`\n"
            f"*Auto-Accept:* `{'Enabled' if session.auto_accept else 'Disabled'}`\n\n"
        )

        # Read TODO.md if it exists
        todo_path = os.path.join(session.workspace_dir, "docs/TODO.md")
        if os.path.exists(todo_path):
            try:
                with open(todo_path) as f:
                    todo_content = f.read()
                # Extract first 15 lines of TODO list
                lines = todo_content.split("\n")[:18]
                status_text += "*Active Task Queue:*\n```markdown\n" + "\n".join(lines) + "\n```"
            except Exception as e:
                status_text += f"_Failed to read TODO.md file: {e}_"
        else:
            status_text += "_No docs/TODO.md file found in the workspace root._"

        await message.reply_text(status_text, parse_mode="Markdown", message_thread_id=thread_id)

    async def handle_autoaccept(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Toggles the auto-accept state flag for the active workspace session."""
        message = update.message
        if not message or not self._is_authorized(update):
            return

        thread_id = message.message_thread_id
        assert self.agent_manager is not None
        session = self.agent_manager.get_session(thread_id)
        session.auto_accept = not session.auto_accept

        state_str = "ENABLED" if session.auto_accept else "DISABLED"
        await message.reply_text(
            f"Auto-Accept is now *{state_str}* for this session. "
            f"The bot will bypass manual confirmations.",
            parse_mode="Markdown",
            message_thread_id=thread_id,
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Processes plain text messages as agent prompt inputs."""
        message = update.message
        if not message or not message.text or not self._is_authorized(update):
            return

        thread_id = message.message_thread_id
        assert self.agent_manager is not None
        session = self.agent_manager.get_session(thread_id)
        session.chat_id = update.effective_chat.id if update.effective_chat else None

        if session.is_running:
            await message.reply_text(
                "An execution is already running for this workspace.",
                message_thread_id=thread_id,
            )
            return

        task = asyncio.create_task(
            self._process_and_stream_response(update, session, message.text, thread_id)
        )
        RUNNING_TASKS[thread_id] = task
        task.add_done_callback(lambda t: RUNNING_TASKS.pop(thread_id, None))

    async def handle_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Cancels any active agent execution for the current thread/workspace."""
        message = update.message
        if not message or not self._is_authorized(update):
            return

        thread_id = message.message_thread_id
        task = RUNNING_TASKS.get(thread_id)
        if not task or task.done():
            await message.reply_text(
                "No agent execution is currently running in this workspace.",
                message_thread_id=thread_id,
            )
            return

        task.cancel()
        await message.reply_text(
            "Agent execution cancelled. 🛑",
            message_thread_id=thread_id,
        )

    async def handle_workspace(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Changes the workspace directory for the current thread/workspace session."""
        message = update.message
        if not message or not message.text or not self._is_authorized(update):
            return

        thread_id = message.message_thread_id
        parts = message.text.split(" ", 1)
        if len(parts) < 2:
            assert self.agent_manager is not None
            session = self.agent_manager.get_session(thread_id)
            await message.reply_text(
                f"Current workspace: `{session.workspace_dir}`\n\n"
                f"To change it, use: `/workspace <absolute_path>`",
                parse_mode="Markdown",
                message_thread_id=thread_id,
            )
            return

        new_path = parts[1].strip()
        if not os.path.isabs(new_path):
            await message.reply_text(
                "Error: Please provide an absolute path.",
                message_thread_id=thread_id,
            )
            return

        assert self.agent_manager is not None
        session = self.agent_manager.get_session(thread_id)
        if session.is_running:
            await message.reply_text(
                "Cannot change workspace while the agent is running.",
                message_thread_id=thread_id,
            )
            return

        await session.close()
        session.workspace_dir = new_path
        self.agent_manager.topic_mappings[thread_id or 0] = new_path

        try:
            mappings_path = self.settings.topic_mappings_file
            serialized_mappings = {str(k): v for k, v in self.agent_manager.topic_mappings.items()}
            with open(mappings_path, "w") as f:
                json.dump(serialized_mappings, f, indent=2)
        except (OSError, TypeError) as e:
            logger.error("Failed to persist new workspace mapping to file: %s", e)

        await message.reply_text(
            f"Workspace updated to: `{new_path}`\n\nThe mapping has been persisted.",
            parse_mode="Markdown",
            message_thread_id=thread_id,
        )
