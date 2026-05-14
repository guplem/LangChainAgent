"""Entry point for `python -m mathagent` and the `mathagent` console script.

This module is intentionally the only place that loads .env files. Importing
`mathagent` as a library does NOT trigger any auto-load, so tests, notebooks,
and library users see the unmodified os.environ.

Precedence (canonical):

    shell exports > .env.local > .env

Implemented by loading `.env.local` first and `.env` second, both with
`override=False`: each call only sets variables that are not already in
os.environ. So an earlier-loaded `.env.local` value wins over the same key
in `.env`, and a shell export wins over both.
"""

from dotenv import load_dotenv

from mathagent.repl import run


def main() -> None:
    # Load .env.local first so its secrets stick before .env fills the gaps.
    # Missing files are silent no-ops; load_dotenv returns False but does not raise.
    load_dotenv(".env.local", override=False)
    load_dotenv(".env", override=False)
    run()


if __name__ == "__main__":
    main()
