try:
    from .main import main
except ImportError:  # Running as a script without package context
    from main import main


if __name__ == "__main__":
    main()


