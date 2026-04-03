# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.5.0] - 2026-04-03

### Added

- **Guard command** — pre-push dependency security scanner (`firsttoknow guard`)
  - CVE/vulnerability scanning via [OSV.dev](https://osv.dev) for new dependencies
  - License change detection between package versions
  - AI-powered code review of git diff (`--review` flag)
  - Pre-push git hook integration via pre-commit (`--init` flag)
  - Movie-themed grading system: Blockbuster → Superhit → Hit → Average → Flop → Disaster
  - Typosquatting detection for new dependencies (compares against ~100 popular PyPI + npm packages)
- **GitHub releases tool** — `fetch_github_releases` fetches latest releases and changelogs for tracked GitHub repos
- **Briefing now covers GitHub repos** — tracked repos get release summaries with changelog highlights
- `firsttoknow-guard` entry point for use as a pre-commit hook
- 267 tests (up from 130)

### Changed

- `fetch_github_trending` now uses authenticated GitHub API headers (GITHUB_TOKEN) to avoid rate limits
- Briefing instruction updated with GitHub Releases section and 9 tools (was 8)
- CLI `brief` command now includes tracked GitHub repos in agent message

### Fixed

- Removed `pytest` from production dependencies (was accidentally included — now dev-only)
- Synced package version across pyproject.toml and `__init__.py`

## [0.4.1] - 2026-04-03

### Added

- **License change detection** — alerts when a tracked package changes its license between versions (legal risk for commercial use)
- **Colorized markdown briefing output** with ASCII logo banner
- **Demo GIF** and real-world screenshots in README
- **Groq and DeepSeek** added to supported LLM providers in `.env.example`
- **14 GitHub topics** and PyPI keywords for discoverability

### Changed

- README rewritten with hero GIF, scan/status screenshot, and real-world proof section
- Social preview image for better link sharing on Twitter/LinkedIn/Slack
- Author branding ("Built by Dinesh Karakambaka") added to README and social preview

## [0.4.0] - 2026-03-31

### Added

- **npm package support** — track npm packages (`--npm` flag), scan `package.json`, fetch releases from npm registry
- **CVE/OSV vulnerability alerts** — check all tracked packages (PyPI + npm) for known security vulnerabilities via [osv.dev](https://osv.dev). Flagged as 🔴 CRITICAL with severity (CRITICAL/HIGH/MEDIUM/LOW) and CVE IDs
- **Live spinner with dynamic tool status** — animated spinner during briefings shows exactly what the agent is doing in real-time ("Checking PyPI...", "Scanning for vulnerabilities...", "Fetching GitHub trending repos...")
- `scan` command now detects `package.json` and tracks npm dependencies
- 8 new tests (122 total)

### Changed

- `scan_project` now returns source file name alongside dependencies (fixes ecosystem detection bug)
- Deduplicated error handling across all 7 tools into shared `_error_response` helper
- Rewrote noise suppression as proper context manager (fixes resource leak)
- Agent instructions updated for npm tools and vulnerability checking

## [0.3.0] - 2026-03-31

### Changed

- **Renamed project from LastToKnow to FirstToKnow** — aspirational > self-deprecating
- Renamed all imports, CLI commands, config dir (`~/.firsttoknow/`), env var (`FIRSTTOKNOW_MODEL`)
- Agent now produces real summaries (2-3 sentences per item) instead of just headlines
- Every item includes a `[Read more]` link for optional deep-dive

## [0.2.0] - 2026-03-31

### Added

- Dev.to tool: fetch popular articles by tag (`fetch_devto_articles`)
- Reddit tool: fetch hot posts from any subreddit (`fetch_reddit_posts`)
- Agent now uses 5 data sources (PyPI, GitHub, Hacker News, Dev.to, Reddit)
- Structured briefing output with sections: 📦 Package Updates, 🔥 Trending Repos, 📰 News & Discussions, 💡 TL;DR
- 8 new tests for Dev.to and Reddit tools (89 total)

### Changed

- Rewrote agent instructions for structured, sectioned output
- Agent now calls at least 3 different tools per briefing
- README commands now include `uv run` prefix

## [0.1.0] - 2026-03-31

### Added

- CLI with Typer: `track`, `untrack`, `list`, `brief`, `scan`, `status`, `config`
- ADK agent with LiteLLM backbone for AI-powered briefings
- 3 tool functions: PyPI releases, GitHub trending, Hacker News top stories
- Dependency scanner: auto-detect from `pyproject.toml` / `requirements.txt`
- Rich terminal output: panels, tables, colored text
- Config management with JSON persistence (`~/.firsttoknow/`)
- `.env` support via python-dotenv for API keys
- Works with any LLM provider: Azure OpenAI, OpenAI, Gemini, Claude, Ollama
- System prompt with priority levels: 🔴 Critical / 🟡 Important / 🟢 FYI
- 81 tests with full coverage across CLI, agents, config, scanner, and models
