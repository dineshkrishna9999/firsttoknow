"""Tests for the agent runner (callback mechanism)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from firsttoknow.agents.agent import _run_agent_inner


def _make_event(*, text: str | None = None, function_call_name: str | None = None) -> MagicMock:
    """Build a mock ADK event with optional text and/or function_call parts."""
    parts = []

    if function_call_name:
        fc_part = MagicMock()
        fc_part.text = None
        fc_part.function_call = MagicMock()
        fc_part.function_call.name = function_call_name
        parts.append(fc_part)

    if text:
        text_part = MagicMock()
        text_part.text = text
        text_part.function_call = None
        parts.append(text_part)

    event = MagicMock()
    event.content = MagicMock()
    event.content.parts = parts
    return event


class TestOnToolCallCallback:
    """Tests for the on_tool_call callback in _run_agent_inner."""

    @patch("firsttoknow.agents.agent.Runner")
    @patch("firsttoknow.agents.agent.InMemorySessionService")
    @patch("firsttoknow.agents.agent.FirstToKnowAgent")
    @patch("firsttoknow.agents.agent.LiteLlm")
    def test_callback_receives_tool_names(
        self,
        mock_litellm: MagicMock,
        mock_agent: MagicMock,
        mock_session: MagicMock,
        mock_runner_cls: MagicMock,
    ) -> None:
        """Callback should be called with tool names when function_call events arrive."""
        events = [
            _make_event(function_call_name="fetch_pypi_releases"),
            _make_event(function_call_name="check_vulnerabilities"),
            _make_event(text="Here is your briefing."),
        ]
        mock_runner_cls.return_value.run.return_value = events

        callback = MagicMock()
        result = _run_agent_inner("gpt-4o", "brief me", on_tool_call=callback)

        assert result == "Here is your briefing."
        assert callback.call_count == 2
        callback.assert_any_call("fetch_pypi_releases")
        callback.assert_any_call("check_vulnerabilities")

    @patch("firsttoknow.agents.agent.Runner")
    @patch("firsttoknow.agents.agent.InMemorySessionService")
    @patch("firsttoknow.agents.agent.FirstToKnowAgent")
    @patch("firsttoknow.agents.agent.LiteLlm")
    def test_no_callback_does_not_crash(
        self,
        mock_litellm: MagicMock,
        mock_agent: MagicMock,
        mock_session: MagicMock,
        mock_runner_cls: MagicMock,
    ) -> None:
        """Default (no callback) should work without errors."""
        events = [
            _make_event(function_call_name="fetch_pypi_releases"),
            _make_event(text="Here is your briefing."),
        ]
        mock_runner_cls.return_value.run.return_value = events

        result = _run_agent_inner("gpt-4o", "brief me")
        assert result == "Here is your briefing."

    @patch("firsttoknow.agents.agent.Runner")
    @patch("firsttoknow.agents.agent.InMemorySessionService")
    @patch("firsttoknow.agents.agent.FirstToKnowAgent")
    @patch("firsttoknow.agents.agent.LiteLlm")
    def test_text_response_captured_with_callback(
        self,
        mock_litellm: MagicMock,
        mock_agent: MagicMock,
        mock_session: MagicMock,
        mock_runner_cls: MagicMock,
    ) -> None:
        """Text response should be returned even when callback is active."""
        events = [
            _make_event(function_call_name="fetch_github_trending"),
            _make_event(text="Partial response"),
            _make_event(text="Final briefing."),
        ]
        mock_runner_cls.return_value.run.return_value = events

        callback = MagicMock()
        result = _run_agent_inner("gpt-4o", "brief me", on_tool_call=callback)

        # Should get the last text response
        assert result == "Final briefing."
        callback.assert_called_once_with("fetch_github_trending")

    @patch("firsttoknow.agents.agent.Runner")
    @patch("firsttoknow.agents.agent.InMemorySessionService")
    @patch("firsttoknow.agents.agent.FirstToKnowAgent")
    @patch("firsttoknow.agents.agent.LiteLlm")
    def test_mixed_event_with_both_tool_and_text(
        self,
        mock_litellm: MagicMock,
        mock_agent: MagicMock,
        mock_session: MagicMock,
        mock_runner_cls: MagicMock,
    ) -> None:
        """An event with both function_call and text parts should trigger both."""
        # Build a single event that has both a function_call part and a text part
        fc_part = MagicMock()
        fc_part.text = None
        fc_part.function_call = MagicMock()
        fc_part.function_call.name = "fetch_npm_releases"

        text_part = MagicMock()
        text_part.text = "Done."
        text_part.function_call = None

        event = MagicMock()
        event.content = MagicMock()
        event.content.parts = [fc_part, text_part]

        mock_runner_cls.return_value.run.return_value = [event]

        callback = MagicMock()
        result = _run_agent_inner("gpt-4o", "brief me", on_tool_call=callback)

        assert result == "Done."
        callback.assert_called_once_with("fetch_npm_releases")
