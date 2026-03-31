"""Tests for the FirstToKnow renderer."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from firsttoknow.renderer import _TOOL_STATUS, render_briefing_spinner


class TestRenderBriefingSpinner:
    """Tests for the briefing spinner context manager."""

    def test_yields_callable(self) -> None:
        """The context manager should yield a callable."""
        with patch("firsttoknow.renderer.console") as mock_console:
            mock_console.status.return_value.__enter__ = MagicMock()
            mock_console.status.return_value.__exit__ = MagicMock(return_value=False)
            with render_briefing_spinner() as on_tool_call:
                assert callable(on_tool_call)

    def test_callback_updates_status(self) -> None:
        """Calling the callback should update the spinner status text."""
        mock_status = MagicMock()
        with patch("firsttoknow.renderer.console") as mock_console:
            mock_console.status.return_value.__enter__ = MagicMock(return_value=mock_status)
            mock_console.status.return_value.__exit__ = MagicMock(return_value=False)
            with render_briefing_spinner() as on_tool_call:
                on_tool_call("fetch_pypi_releases")
                mock_status.update.assert_called_with("[bold green]Checking PyPI...")

    def test_callback_handles_unknown_tool(self) -> None:
        """Unknown tool names should show a generic message."""
        mock_status = MagicMock()
        with patch("firsttoknow.renderer.console") as mock_console:
            mock_console.status.return_value.__enter__ = MagicMock(return_value=mock_status)
            mock_console.status.return_value.__exit__ = MagicMock(return_value=False)
            with render_briefing_spinner() as on_tool_call:
                on_tool_call("some_unknown_tool")
                mock_status.update.assert_called_with("[bold green]Running some_unknown_tool...")

    def test_all_tools_have_status_labels(self) -> None:
        """Every known tool should have a human-friendly status label."""
        expected_tools = {
            "fetch_pypi_releases",
            "fetch_npm_releases",
            "check_vulnerabilities",
            "fetch_github_trending",
            "fetch_hackernews_top",
            "fetch_devto_articles",
            "fetch_reddit_posts",
        }
        assert set(_TOOL_STATUS.keys()) == expected_tools
