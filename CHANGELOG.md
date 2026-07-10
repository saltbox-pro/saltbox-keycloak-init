# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Fixed

---

## [0.3.0] - 2026-07-10

### Added

- Login theme and internationalization support applied during realm creation: `KEYCLOAK_LOGIN_THEME`,
  `KEYCLOAK_SUPPORTED_LOCALES`, and `KEYCLOAK_DEFAULT_LOCALE` env vars.
- CI `bump-version` stage for automated version file updates via shared `set-version` CI template.

### Changed

- Switched CI lint toolchain from pip to uv (`uv sync` / `uv run`); added APK and uv layer caching.
- Simplified CI build pipeline: merged separate tag/branch build jobs into a single `Build Keycloak Init image` job.
- Moved lint tool declarations from `[project.optional-dependencies]` to `[dependency-groups]` in `pyproject.toml`.

### Removed

- Unused login theme asset files.

---

## [0.2.0]

### Added

- Brute Force detection with configurable parameters (`KEYCLOAK_BF_MAX_FAILURE_WAIT_SC`,
  `KEYCLOAK_BF_WAIT_INCREMENT_SC`, `KEYCLOAK_BF_MIN_QUICK_LOGIN_WAIT_SC`,
  `KEYCLOAK_BF_QUICK_LOGIN_CHECK_MSC`, `KEYCLOAK_BF_MAX_DELTA_TIME_SC`,
  `KEYCLOAK_BF_FAILURE_FACTOR` env vars).
- Retry policy for Keycloak initialization attempts.
- CI lint job (mypy, ruff) via GitLab CI pipeline.
- `client.d/` JSON-based configuration for Keycloak clients (Grafana, saltbox-core).

### Changed

- Drop `pydantic`/`pydantic-settings` dependency; replaced with lightweight custom
  `Settings` class reading env vars and Docker secrets directly.
- Rename `GRAFANA_CLIENT` environment variable to `KEYCLOAK_CLIENT_GRAFANA`.
- Refactor code style: single quotes, improved type annotations across all modules.
- `Dockerfile`: simplified by removing multi-stage builder.
- Logging: add datetime format to log formatter.
- `pyproject.toml`: add `package-data` section for `client.d/` JSON files.

### Fixed

- Docker secret extraction in `config.py`.
- Initialization of Salt.Box entities incorrectly applied to master realm instead of
  target realm.
- `SecretsUsedInArgOrEnv` linting error in `Dockerfile`.
- mypy type errors.

### Removed

- `DEFAULT_QUICK_LOGIN_CHECK_TIME` variable.
- Builder stage from `Dockerfile`.
- `--prefix` flag from pip install in `Dockerfile`.
- `pydantic` and `pydantic-settings` from dependencies.
