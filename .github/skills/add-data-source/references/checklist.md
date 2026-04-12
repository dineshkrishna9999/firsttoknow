# Add Data Source — Implementation Checklist

Copy this checklist when adding any new data source. Check off each item in order.

## Pre-flight

- [ ] I know the API endpoint URL and whether it requires auth (e.g. API key, OAuth)
- [ ] I've checked the API rate limits (free tier usually fine for `_TIMEOUT = 10`)
- [ ] The API returns JSON (if it returns XML or HTML, this pattern does not apply)

## Implementation

- [ ] **Method written** in `FirstToKnowTools` in `src/firsttoknow/agents/_tools.py`
  - [ ] Method name is `fetch_<source>_<things>` (snake_case)
  - [ ] Returns `str` (a JSON string)
  - [ ] Uses `httpx.get(..., timeout=_TIMEOUT)`
  - [ ] Entire body is wrapped in `try/except Exception as exc`
  - [ ] Failure path returns `_error_response("<context>", exc)` — not `raise`
  - [ ] Docstring is one clear sentence (the LLM reads this to understand the tool)
  - [ ] Output JSON keys are descriptive (e.g. `"questions"`, `"posts"` not `"data"`, `"result"`)

- [ ] **Registered** in `FirstToKnowTools.get_tools()` as `FunctionTool(self.fetch_...)`

- [ ] **Briefing instruction updated** in `src/firsttoknow/agents/instructions/briefing.py`
  - [ ] Row added to the tools table at the top of `BRIEFING_INSTRUCTION`
  - [ ] Numbered step added in "How to run a briefing" section telling the agent WHEN to call it

- [ ] **Tests written** in `tests/test_agents/test_tools.py`
  - [ ] Happy path: mocked response → assert expected JSON keys exist
  - [ ] Failure path: `side_effect=Exception(...)` → assert `"error"` in result
  - [ ] Test class name: `TestFetch<SourceName>`
  - [ ] Test method names: `test_fetch_<method>_<scenario>`

## Verification

- [ ] `uv run pytest tests/test_agents/test_tools.py -v` — all new tests pass
- [ ] `uv run poe lint` — no ruff or bandit issues
- [ ] `uv run firsttoknow brief --model <model>` — agent calls the new tool in its output

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Forgot to add to `get_tools()` | Agent has no access to the tool at all |
| Updated `get_tools()` but not `BRIEFING_INSTRUCTION` | Agent can call the tool but never does |
| `return data` instead of `return json.dumps(data)` | ADK crashes — tool must return `str` |
| No `timeout=_TIMEOUT` | Bandit S113 lint error; also hangs forever on slow APIs |
| `raise` instead of `_error_response` | Agent crashes instead of gracefully reporting error |
