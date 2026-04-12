---
name: add-data-source
description: 'Use when adding a new API data source to FirstToKnow — e.g. Stack Overflow, Product Hunt, Mastodon, Discord, Lobsters, or any new feed. Covers writing the tool function, registering it, updating the agent briefing instruction, and writing tests. Follow every step in order.'
argument-hint: 'Name of the data source to add (e.g. "Stack Overflow", "Product Hunt")'
---

# Add a New Data Source to FirstToKnow

## What This Skill Does

Guides you through adding a new external API data source to FirstToKnow in exactly the right order, using the correct patterns. Every data source in this project follows the same 5-step workflow. Skipping or reordering steps causes the agent to not know about the new tool.

## When to Use

- "Add Stack Overflow as a data source"
- "I want to track Product Hunt trending posts"
- "Add Mastodon / Lobsters / Discord / any new feed"
- "The TODO.md mentions Discord — let's add it"

## Step-by-Step Procedure

### Step 1 — Write the tool method in `_tools.py`

Open [`src/firsttoknow/agents/_tools.py`](../../../src/firsttoknow/agents/_tools.py).

Add a new method inside the `FirstToKnowTools` class. Follow the **exact** pattern in [references/tool-pattern.md](./references/tool-pattern.md) — no deviations. Key rules:

- Method name: `fetch_<source_name>` (e.g. `fetch_stackoverflow_questions`)
- Return type: `str` (always a JSON string)
- Must call `httpx.get()` with `timeout=_TIMEOUT`
- Must wrap everything in `try/except Exception` and call `_error_response()` on failure
- The docstring is what the LLM sees — make it one clear sentence

Example skeleton:
```python
def fetch_stackoverflow_questions(self, tag: str = "python", limit: int = 10) -> str:
    """Fetch hot questions from Stack Overflow by tag."""
    url = "https://api.stackexchange.com/2.3/questions"
    params = {"order": "desc", "sort": "hot", "tagged": tag, "site": "stackoverflow", "pagesize": limit}
    try:
        resp = httpx.get(url, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        questions = [
            {"title": q["title"], "url": q["link"], "score": q["score"], "answers": q["answer_count"]}
            for q in data.get("items", [])[:limit]
        ]
        return json.dumps({"questions": questions, "tag": tag})
    except Exception as exc:
        return _error_response(f"Stack Overflow fetch failed for tag '{tag}'", exc)
```

### Step 2 — Register the tool in `get_tools()`

In the same file, find the `get_tools()` method at the bottom of `FirstToKnowTools`. Add a `FunctionTool` for your new method:

```python
def get_tools(self) -> list[FunctionTool]:
    return [
        FunctionTool(self.fetch_pypi_releases),
        # ... existing tools ...
        FunctionTool(self.fetch_stackoverflow_questions),  # ← add here
    ]
```

Without this, the ADK agent cannot see or call the new tool.

### Step 3 — Update the briefing instruction

Open [`src/firsttoknow/agents/instructions/briefing.py`](../../../src/firsttoknow/agents/instructions/briefing.py).

There are two places to update inside `BRIEFING_INSTRUCTION`:

**3a.** Add a row to the tools table:
```
| `fetch_stackoverflow_questions` | Fetch hot Stack Overflow questions by tag |
```

**3b.** Add a numbered step in "How to run a briefing":
```
7. **Stack Overflow** — call `fetch_stackoverflow_questions` for relevant tags \
(e.g. "python", "ai", "llm"). Surface questions with high scores and activity.
```

Without this, the agent has access to the tool but doesn't know when to call it.

### Step 4 — Write tests

Open [`tests/test_agents/test_tools.py`](../../../tests/test_agents/test_tools.py).

Add a test class following the existing pattern. See [references/tool-pattern.md](./references/tool-pattern.md) for the test skeleton. You need at minimum:

1. `test_<method_name>_returns_expected_keys` — happy path, mock `httpx.get`, assert JSON keys exist
2. `test_<method_name>_returns_error_on_failure` — mock `httpx.get` to raise `Exception`, assert `"error"` in result

### Step 5 — Verify

```bash
uv run pytest tests/test_agents/test_tools.py -v   # new tests pass
uv run poe lint                                     # no ruff/bandit issues
uv run firsttoknow brief --model <your-model>       # agent actually calls the new tool
```

## Reference Files

- [Tool function pattern + test skeleton](./references/tool-pattern.md)
- [Full implementation checklist](./references/checklist.md)
