# FirstToKnow — Project Guidelines

## What This Project Is

**FirstToKnow** is an AI-powered CLI tool that watches a developer's tech stack and delivers a prioritized daily briefing (CVEs, breaking changes, trending repos, HN/Reddit discussions) from the terminal. One command: `uv run firsttoknow brief`.

## Architecture

```
CLI (Typer)  →  Config (JSON at ~/.firsttoknow/)  →  Agent (Google ADK + LiteLLM)
                                                               ↓
                                                    Tools (httpx API calls)
                                                               ↓
                                                    Renderer (Rich terminal UI)
```

Key source files:
- `src/firsttoknow/cli.py` — all CLI commands (Typer app)
- `src/firsttoknow/config.py` — `FirstToKnowConfig`, tracks items in `~/.firsttoknow/tracked.json`
- `src/firsttoknow/models.py` — `ItemType`, `Severity`, `GuardFinding`, `GuardReport`, `TrackedItem`
- `src/firsttoknow/agents/agent.py` — `FirstToKnowAgent` (Google ADK `LlmAgent`), `run_agent()`
- `src/firsttoknow/agents/_tools.py` — `FirstToKnowTools` class; each method calls one external API and returns a JSON string
- `src/firsttoknow/agents/instructions/briefing.py` — `BRIEFING_INSTRUCTION` constant passed to the agent
- `src/firsttoknow/renderer.py` — all Rich terminal output (`render_briefing`, `render_guard_report`, etc.)
- `src/firsttoknow/guard.py` — pre-push dependency scanner (CVE + license + typosquat) — does NOT use LLM
- `src/firsttoknow/scanner.py` — reads `pyproject.toml` / `package.json` / `requirements.txt`, returns `ScannedDep` list
- `src/firsttoknow/typosquat.py` — `check_typosquat()`, curated list of ~100 popular PyPI + npm packages

## Build & Test

```bash
uv run poe fmt          # ruff format
uv run poe lint         # ruff check
uv run pytest           # run all tests
uv run firsttoknow --help
```

## Code Conventions

- **`from __future__ import annotations`** at the top of every module — always
- **Type hints on all function signatures** — no bare `def f(x):`
- **`pathlib.Path` over `os.path`** — always
- **`StrEnum` over raw strings** for enumerations (see `models.py`)
- **`dataclass` for data models** — not dicts, not namedtuples (see `models.py`)
- **Line length 120** — configured in `pyproject.toml`, enforced by ruff
- **`TYPE_CHECKING` guard for import-time-only imports** — see existing modules for examples

## Tool Function Pattern

Every agent tool in `_tools.py` follows this exact pattern — do not deviate:

```python
def fetch_something(self, param: str) -> str:
    """One-line description for the LLM to understand this tool."""
    try:
        resp = httpx.get(url, timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return json.dumps({"key": data["key"]})
    except Exception as exc:
        return _error_response("fetch_something", exc)
```

Rules:
1. Always return a JSON string (success or error)
2. Always use `_TIMEOUT = 10` for httpx calls
3. Always use `_error_response(context, exc)` on failure — never raise
4. Register the method in `FirstToKnowTools.get_tools()` as a `FunctionTool`
5. Update `BRIEFING_INSTRUCTION` in `agents/instructions/briefing.py` to tell the agent when to call it

## Testing Conventions

- **Mock HTTP with `monkeypatch`** — not `unittest.mock.patch`. See `tests/test_agents/test_tools.py` for examples.
- **Test naming:** `test_<function_name>_<scenario>` (e.g. `test_fetch_pypi_releases_returns_json`)
- **Config tests:** use `tmp_path` fixture for isolated `~/.firsttoknow/` directories
- **Tool tests:** mock `httpx.get` via `monkeypatch`, assert on JSON keys — not full string equality

## Security

- `S` (bandit) rules are enabled in ruff — fix bandit warnings, do not suppress with `noqa`
- Never hardcode API keys — use `os.environ.get()` or `python-dotenv`
- `subprocess.run` calls must include `timeout=` and avoid `shell=True` (see `guard.py`)
- `httpx` calls must include `timeout=_TIMEOUT`

## Architecture Decision Comments

This codebase uses **teaching-style comments** explaining *why* decisions were made, not just *what* the code does. When adding new code, follow the same pattern — if you make a non-obvious choice (e.g. using subprocess over a library, or not using an LLM), write a short "Why?" explanation as a docstring or inline comment. See `guard.py` for examples.
