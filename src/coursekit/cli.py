import argparse
import json
from pathlib import Path

from coursekit.config import resolve_data_dir
from coursekit.day1_rag import RAGSystem
from coursekit.day2_graph import AdaptiveRAG
from coursekit.day3_agent import AgentHarness
from coursekit.day4_multiagent import SearchAndVerifySystem
from coursekit.day5_system import OperationalSystem
from coursekit.project import validate_project


def main() -> None:
    parser = argparse.ArgumentParser(description="Five-day course CLI")
    parser.add_argument(
        "day", choices=["day1", "day2", "day3", "day4", "day5", "eval", "project-check"]
    )
    parser.add_argument("question", nargs="?", default="")
    parser.add_argument("--data-dir", default=None)
    args = parser.parse_args()
    data_dir = resolve_data_dir(args.data_dir)
    document_dir = Path(data_dir) / "documents"
    if args.day == "project-check":
        result = validate_project(data_dir)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if not result["valid"]:
            raise SystemExit(1)
        return
    if args.day == "day1":
        result = RAGSystem(document_dir=document_dir).ask(args.question)
        print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
        return
    if args.day == "day2":
        result = AdaptiveRAG(document_dir=document_dir).ask(args.question)
        print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
        return
    if args.day == "day3":
        result = AgentHarness(data_dir=data_dir).run(args.question)
        print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
        return
    if args.day == "day4":
        result = SearchAndVerifySystem(data_dir=data_dir).run(args.question)
        print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
        return
    if args.day == "day5":
        result = OperationalSystem(data_dir=data_dir).run(args.question)
        print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
        return
    if args.day == "eval":
        result = OperationalSystem(data_dir=data_dir).evaluate()
        print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
        return
    raise SystemExit(f"{args.day} is not implemented on this branch. Open labs/{args.day}.md")


if __name__ == "__main__":
    main()
