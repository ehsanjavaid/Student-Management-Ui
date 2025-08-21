from __future__ import annotations

try:
    from .database import init_database
    from .config import load_settings
except ImportError:  # Running as a script without package context
    from database import init_database
    from config import load_settings


def main() -> None:
    init_database()
    try:
        from .ui.main_window import StudentManagementApp
    except ImportError:  # Running as a script without package context
        from ui.main_window import StudentManagementApp

    settings = load_settings()
    theme = settings.get("theme", "flatly")

    app = StudentManagementApp(theme_name=theme)
    app.mainloop()


if __name__ == "__main__":
    main()

