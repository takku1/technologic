#!/usr/bin/env python3
"""Measure the original and compiled prompts, excluding audit-only artifacts."""
import argparse
import json
from pathlib import Path
import sys

WREN = Path(__file__).resolve().parents[1]


def measure(encoder):
    files = {"original": WREN.parent / "skills/technologic/SKILL.md",
             "compiled": WREN / "skills/technologic-logic/SKILL.md"}
    sizes = {}
    for name, path in files.items():
        raw = path.read_bytes()
        text = raw.decode("utf-8-sig")
        sizes[name] = {"lines": len(text.splitlines()), "bytes": len(raw),
                       "tokens": len(encoder.encode(text))}
    original, compiled = sizes["original"]["tokens"], sizes["compiled"]["tokens"]
    return {"tokenizer": encoder.name, "files": sizes,
            "tokens_saved": original - compiled,
            "reduction_percent": round(100 * (original - compiled) / original, 2)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tokenizer", default="cl100k_base")
    args = parser.parse_args(argv)
    try:
        import tiktoken
        report = measure(tiktoken.get_encoding(args.tokenizer))
    except (ImportError, OSError, ValueError) as error:
        print(f"context measurement requires tiktoken and its vocabulary: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0 if report["tokens_saved"] > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
