# Tool Function Pattern

Reference for the exact pattern every data source tool must follow in `src/firsttoknow/agents/_tools.py`.

## Production Tool Pattern

Here is `fetch_hackernews_top` — the simplest complete example from the real codebase:

```python
def fetch_hackernews_top(self, query: str = "AI", limit: int = 10) -> str:
    """Fetch top Hacker News stories matching a query.

    Args:
        query: Search term to filter stories (e.g. "AI", "python", "LLM").
        limit: Maximum number of stories to return (default 10).

    Returns:
        JSON string with a list of stories (title, url, points, comments).
    """
    params: dict[str, str | int] = {
        "query": query,
        "tags": "story",
        "hitsPerPage": limit,
    }
    try:
        resp = httpx.get("https://hn.algolia.com/api/v1/search", params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        stories = [
            {
                "title": hit["title"],
                "url": hit.get("url", f"https://news.ycombinator.com/item?id={hit['objectID']}"),
                "points": hit.get("points", 0),
                "comments": hit.get("num_comments", 0),
            }
            for hit in data.get("hits", [])
        ]
        return json.dumps({"stories": stories, "query": query})
    except Exception as exc:
        return _error_response(f"HN fetch failed for query '{query}'", exc)
```

## Non-negotiable Rules

| Rule | Right | Wrong |
|------|-------|-------|
| Return type | `str` (JSON string always) | `dict`, `list`, `None` |
| HTTP timeout | `timeout=_TIMEOUT` (the `_TIMEOUT = 10` constant) | `timeout=5`, no timeout |
| Error handling | `return _error_response(context, exc)` | `raise`, `return None`, `print()` |
| HTTP client | `httpx.get(...)` | `requests.get(...)`, `urllib` |
| JSON success | `return json.dumps({...})` | `return str(data)`, `return data` |

## Registration in `get_tools()`

```python
def get_tools(self) -> list[FunctionTool]:
    """Return all tools as FunctionTool instances for ADK."""
    return [
        FunctionTool(self.fetch_pypi_releases),
        FunctionTool(self.fetch_npm_releases),
        FunctionTool(self.check_vulnerabilities),
        FunctionTool(self.check_license_change),
        FunctionTool(self.fetch_github_trending),
        FunctionTool(self.fetch_github_releases),
        FunctionTool(self.fetch_hackernews_top),
        FunctionTool(self.fetch_devto_articles),
        FunctionTool(self.fetch_reddit_posts),
        # ← your new FunctionTool goes here
    ]
```

## Test Skeleton

Paste this into `tests/test_agents/test_tools.py` and fill in the blanks:

```python
class TestFetch<SourceName>:
    """Tests for the <source name> fetcher."""

    def setup_method(self) -> None:
        self.tools = FirstToKnowTools()

    def test_fetch_<method_name>_returns_expected_keys(self) -> None:
        mock_api_response = {
            # ← paste a realistic response from the real API here
        }
        with patch("firsttoknow.agents._tools.httpx.get", return_value=_mock_response(mock_api_response)):
            result = json.loads(self.tools.fetch_<method_name>("<param>"))

        assert "<top_level_key>" in result          # e.g. "stories", "questions", "posts"
        assert isinstance(result["<key>"], list)

    def test_fetch_<method_name>_returns_error_on_failure(self) -> None:
        with patch("firsttoknow.agents._tools.httpx.get", side_effect=Exception("timeout")):
            result = json.loads(self.tools.fetch_<method_name>("<param>"))

        assert "error" in result
        assert "timeout" in result["error"]
```

Where `_mock_response` is the helper already at the top of the test file:

```python
def _mock_response(data: dict | list) -> MagicMock:
    mock = MagicMock()
    mock.json.return_value = data
    mock.raise_for_status.return_value = None
    return mock
```
