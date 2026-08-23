import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Five-day course CLI")
    parser.add_argument("day", choices=["day1", "day2", "day3", "day4", "day5", "eval"])
    parser.add_argument("question", nargs="?", default="")
    args = parser.parse_args()
    raise SystemExit(f"{args.day} is not implemented on this start branch. Open labs/{args.day}.md")

