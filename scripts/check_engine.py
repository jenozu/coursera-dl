"""Print the installed dl_coursera version and verify the functions the adapter relies on.

Roadmap 8.4. Exit code 1 if anything required is missing.
"""

from __future__ import annotations

import inspect
import sys
from importlib import metadata

REQUIRED = ("crawl", "gather_dl_tasks")


def main() -> int:
    try:
        version = metadata.version("dl_coursera")
    except metadata.PackageNotFoundError:
        print("dl_coursera is not installed")
        return 1

    print(f"dl_coursera {version}")
    try:
        import dl_coursera_run as engine
    except ImportError as exc:
        print(f"cannot import dl_coursera_run: {exc}")
        return 1

    missing = [name for name in REQUIRED if not callable(getattr(engine, name, None))]
    for name in REQUIRED:
        func = getattr(engine, name, None)
        if callable(func):
            print(f"  {name}{inspect.signature(func)}")
    if missing:
        print("missing:", ", ".join(missing))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
