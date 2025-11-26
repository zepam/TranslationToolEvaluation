<!--
AI Assistant instructions for this repository.
This file was generated automatically because no existing agent-instruction files were found.
Update with project-specific examples when source files are available.
-->
# Copilot / AI Agent Instructions — TranslationToolEvaluation

Purpose
- Help an AI coding agent quickly become productive in this repository. If you see placeholders below, the repo currently lacks discoverable project files; replace placeholders with real paths and examples.

Getting started (explore)
- Run a fast repo scan for language and build manifests: search for `package.json`, `pyproject.toml`, `requirements.txt`, `setup.py`, `go.mod`, `Cargo.toml`, `pom.xml`, `Makefile`, `Dockerfile`.
- If none are present, report back: "no build manifests found" and list top-level files and directories.
- Identify tests by searching for `tests/`, `spec/`, `*_test.go`, `pytest.ini`, or a `test` script in `package.json`.

Big-picture analysis checklist
- Find the entrypoints/binaries (web server, CLI, lambda handlers). Look for `src/`, `cmd/`, `app/`, or `main()` functions.
- Identify major components and boundaries: e.g., frontend vs backend, worker queues, data storage layers. Map where configuration lives (env vars, `config/`, `*.env`).
- Record external integrations (APIs, databases, message brokers). Look for connection strings, SDK imports, or client libraries.

Developer workflows (what to document here)
- Build: note the exact command to build the project (examples: `npm install && npm run build`, `python -m build`, `cargo build --release`). If absent, state that no build script was found.
- Tests: add the command to run the test suite (examples: `pytest`, `npm test`, `go test ./...`). Include how to run a single test file or a failing test locally.
- Lint / format: list linters or formatters in use (ESLint, black, gofmt) and the commands to run them.
- Debugging: where to set breakpoints and any special runtime flags (e.g., `node --inspect`, `python -m debugpy --listen`).

Project-specific conventions to look for
- Coding style: check for `.editorconfig`, `pyproject.toml`, `.eslintrc`, or `rustfmt.toml` and prefer those rules.
- Error handling: note if functions return error objects, exceptions, or use sentinel values; cite a concrete file and function once available.
- Config patterns: prefer environment variables, YAML/JSON config files, or a config package — record which.

Integration notes
- Authentication: search for OAuth/OIDC clients, API keys or `auth` packages.
- Storage: search for `postgres`, `mongodb`, `redis`, `s3` in the code or Docker-compose.
- CI/CD: look for `.github/workflows/`, `circleci/`, `Jenkinsfile`. If present, extract build/test/deploy steps.

How to update this file (merge guidance)
- If `.github/copilot-instructions.md` already exists, preserve custom sections. Add or update only verifiable information discovered by scanning files.
- When adding examples, use exact file paths and short code snippets (3–6 lines) demonstrating the pattern.

When you cannot find information
- Be explicit: state which files were searched and what was (not) found.
- Provide safe, minimal suggestions (e.g., "Add a `Makefile` with build/test targets") and ask the human for missing credentials or environment details.

Feedback
- After following these instructions, ask the repo owner for two quick confirmations: the correct build command and the primary entrypoint file.

— End of template —
