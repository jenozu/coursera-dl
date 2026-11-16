"""Launcher (roadmap 5.1, 8.2): start the server on 127.0.0.1 and open the browser."""

from __future__ import annotations

import sys


def main() -> int:
    try:
        from coursera_app.main import create_app  # noqa: F401
    except ImportError as exc:  # pragma: no cover
        print(f"Cannot start: {exc}. Run scripts/setup.ps1 first.")
        return 1
    print("The new FastAPI app is not built yet (milestone M5). Use the Streamlit app for now:")
    print("  streamlit run app.py --server.address 127.0.0.1")
    return 1


if __name__ == "__main__":
    sys.exit(main())
