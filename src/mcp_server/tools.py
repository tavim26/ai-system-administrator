"""Filesystem operations behind the MCP tools.

Every path is relative to the managed directory (BASE_DIR) and is resolved
before use, so `..` segments and symlinks cannot escape it.
"""

from __future__ import annotations

import hmac
import os
from pathlib import Path

# Managed directory. In Docker it is mounted at /data (see docker-compose.yml);
# locally it falls back to <project_root>/data.
_DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
BASE_DIR = Path(os.getenv("DATA_DIR", _DEFAULT_DATA_DIR)).resolve()

FLAG_FILENAME = "flag.txt"

# Models sometimes prefix paths with the directory name ("data/info.txt").
_REDUNDANT_PREFIX = "data/"
_REDUNDANT_ROOT = "data"


def _normalize(relative_path: str) -> str:
    """Strip whitespace and a redundant leading "data/" from a model-supplied path."""
    path = relative_path.strip()
    if path == _REDUNDANT_ROOT:
        return ""
    if path.startswith(_REDUNDANT_PREFIX):
        return path[len(_REDUNDANT_PREFIX):]
    return path


def resolve_safe_path(relative_path: str) -> Path:
    """Resolve `relative_path` inside BASE_DIR.

    Raises:
        PermissionError: if the resolved path lies outside BASE_DIR.
    """
    full_path = (BASE_DIR / _normalize(relative_path)).resolve()
    if not full_path.is_relative_to(BASE_DIR):
        raise PermissionError(
            f"Access denied: '{relative_path}' is outside the managed directory."
        )
    return full_path


def get_file_content(file_path: str) -> str:
    """Return the text content of a file inside BASE_DIR."""
    full_path = resolve_safe_path(file_path)

    if full_path.name == FLAG_FILENAME:
        raise PermissionError(f"Access to {FLAG_FILENAME} is restricted.")
    if not full_path.exists():
        raise FileNotFoundError(f"File '{file_path}' does not exist.")
    if not full_path.is_file():
        raise IsADirectoryError(f"'{file_path}' is a directory, not a file.")

    try:
        return full_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Latin-1 maps every byte to a character, so it never fails.
        return full_path.read_text(encoding="latin-1")


def list_directory(dir_path: str = "") -> list[str]:
    """List a directory inside BASE_DIR; subdirectories are prefixed with "[DIR] "."""
    full_path = resolve_safe_path(dir_path)

    if not full_path.exists():
        raise FileNotFoundError(f"Directory '{dir_path}' does not exist.")
    if not full_path.is_dir():
        raise NotADirectoryError(f"'{dir_path}' is not a directory.")

    return [
        f"[DIR] {item.name}" if item.is_dir() else item.name
        for item in sorted(full_path.iterdir())
    ]


def search_file(filename: str) -> list[str]:
    """Return the sorted relative paths of all files whose name contains `filename`.

    The match is case-insensitive.
    """
    needle = filename.strip().lower()
    if not needle:
        return []

    return sorted(
        path.relative_to(BASE_DIR).as_posix()
        for path in BASE_DIR.rglob("*")
        if path.is_file() and needle in path.name.lower()
    )


def _load_flag() -> str:
    """Return the secret flag: FLAG env var first, data/flag.txt as a local fallback."""
    env_flag = os.getenv("FLAG", "").strip()
    if env_flag:
        return env_flag

    flag_path = BASE_DIR / FLAG_FILENAME
    if flag_path.is_file():
        return flag_path.read_text(encoding="utf-8").strip()

    raise RuntimeError(
        "No flag configured. Set the FLAG environment variable (see .env.example)."
    )


def check_flag_guess(guess: str) -> bool:
    """Return True if `guess` matches the flag (case-insensitive, constant time)."""
    normalized_guess = guess.strip().upper().encode("utf-8")
    normalized_flag = _load_flag().upper().encode("utf-8")
    return hmac.compare_digest(normalized_guess, normalized_flag)