"""Allow ``python -m cortex`` to invoke the CLI."""

from .cli.main import main
import sys

if __name__ == "__main__":
    sys.exit(main())
