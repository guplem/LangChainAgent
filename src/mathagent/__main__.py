"""Entry point for `python -m mathagent` and the `mathagent` console script."""

from mathagent.repl import run


def main() -> None:
    run()


if __name__ == "__main__":
    main()
