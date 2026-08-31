from __future__ import annotations

import argparse
import json

from glancepath.parser.scanner import scan_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="glancepath")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Scan a Python repository")
    scan.add_argument("path", nargs="?", default=".")
    scan.add_argument("--json", action="store_true", dest="as_json")

    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "scan":
        graph = scan_repository(args.path)
        if args.as_json:
            print(json.dumps(graph.to_dict(), indent=2))
            return

        print(f"Scanned {len(graph.nodes)} nodes and {len(graph.edges)} edges")
        for node in graph.nodes.values():
            print(f"{node.kind}: {node.id} ({node.file}:{node.start_line})")


if __name__ == "__main__":
    main()
