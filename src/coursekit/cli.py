import argparse
import json

from coursekit.day1_rag import RAGSystem
from coursekit.day2_graph import AdaptiveRAG


def main() -> None:
    parser = argparse.ArgumentParser(description="Five-day course CLI")
    parser.add_argument("day", choices=["day1", "day2", "day3", "day4", "day5", "eval"])
    parser.add_argument("question", nargs="?", default="")
    args = parser.parse_args()
    if args.day == "day1":
        result = RAGSystem().ask(args.question)
        print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
        return
    if args.day == "day2":
        result = AdaptiveRAG().ask(args.question)
        print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
        return
    raise SystemExit(f"{args.day} is not implemented on this branch. Open labs/{args.day}.md")


if __name__ == "__main__":
    main()
