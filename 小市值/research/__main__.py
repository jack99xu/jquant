"""python -m research 入口。"""
import sys

from research import cli


def main() -> int:
    return cli.main()


if __name__ == "__main__":
    sys.exit(main())