"""Reading credentials out of a file.

Deliberately not python-dotenv. This is twenty lines, and a credential loader is
a poor place to acquire a dependency — one that has to be present before the
program can start, and that reads secrets on the way past.

Two rules, both about not surprising anyone:

* **the shell wins.** A value already in the environment is never overwritten by
  a file. Whoever exported it meant it.
* **an empty value is not a value.** Placeholder lines like ``OPENAI_API_KEY=``
  are extremely common in shared env files, and treating one as a real setting
  would mask a genuine variable with an empty string.
"""
from __future__ import annotations

import os
from pathlib import Path

#: Where the package itself lives, for the case of running from elsewhere.
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def candidates() -> tuple[Path, ...]:
    """Where to look, in order. Computed per call, not at import.

    ``Path.cwd()`` frozen at import time is the current directory of whatever
    process happened to import the module first — which is not necessarily the
    directory anyone is working in.
    """
    return (Path.cwd() / ".env", PROJECT_ROOT / ".env")


def load_env(path: Path | str, required: bool = True) -> bool:
    """Read ``KEY=value`` lines into the environment. Returns whether it read one."""
    path = Path(path).expanduser()
    if not path.exists():
        if required:
            raise FileNotFoundError(f"no such env file: {path}")
        return False

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip("\"'")
        if value and key not in os.environ:
            os.environ[key] = value
    return True


def find_env(extra: tuple[Path, ...] | None = None) -> Path | None:
    """The first ``.env`` worth loading, or ``None``."""
    for candidate in (candidates() if extra is None else extra):
        if candidate.exists():
            return candidate
    return None
