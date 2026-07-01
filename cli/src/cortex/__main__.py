"""Allow ``python -m cortex`` to invoke the CLI."""

from .cli.main_e3 import main
import sys

if __name__ == "__main__":
    sys.exit(main())
