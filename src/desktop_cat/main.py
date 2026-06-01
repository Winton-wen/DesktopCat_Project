from .sprite_app import DesktopCatApp


def main() -> int:
    app = DesktopCatApp()
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
