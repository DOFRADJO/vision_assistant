"""Entry point for Vision Assistant desktop execution."""
from __future__ import annotations

from app.desktop.desktop_app import DesktopApp


def main() -> None:
    app = DesktopApp()
    app.run()


if __name__ == "__main__":
    main()
