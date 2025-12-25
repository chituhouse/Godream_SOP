#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _parse_iso(ts: str | None) -> str:
    if not ts:
        return ""
    try:
        # Example: 2025-12-25T03:36:26.464Z
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ts)


def _extract_text_from_message(message: Any, include_tool_results: bool) -> str:
    # Claude Code JSONL "message" shape varies a bit.
    if isinstance(message, dict):
        content = message.get("content")
    else:
        content = None

    if isinstance(content, str):
        return content

    if not isinstance(content, list):
        return ""

    parts: list[str] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        t = item.get("type")
        if t == "text":
            text = item.get("text")
            if isinstance(text, str) and text.strip():
                parts.append(text)
        elif include_tool_results and t == "tool_result":
            # tool_result.content can be str or list-of-dicts (Claude tool schema)
            tool_content = item.get("content")
            if isinstance(tool_content, str) and tool_content.strip():
                parts.append(tool_content)
            elif isinstance(tool_content, list):
                for sub in tool_content:
                    if isinstance(sub, dict) and isinstance(sub.get("text"), str):
                        parts.append(sub["text"])
    return "\n".join(parts).strip()


def jsonl_to_markdown(
    input_path: Path,
    output_path: Path,
    include_tool_results: bool,
) -> None:
    lines: list[str] = []
    lines.append(f"# Claude Code Transcript: {input_path.name}")
    lines.append("")

    with input_path.open("r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            obj = json.loads(raw)
            msg_type = obj.get("type")
            if msg_type not in {"user", "assistant", "system"}:
                continue

            ts = _parse_iso(obj.get("timestamp"))
            message = obj.get("message")
            text = _extract_text_from_message(message, include_tool_results=include_tool_results)
            if not text:
                continue

            role = msg_type.upper()
            lines.append(f"## [{ts}] {role}" if ts else f"## {role}")
            lines.append("")
            lines.append(text.rstrip())
            lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert Claude Code JSONL to readable Markdown.")
    parser.add_argument("input", type=Path, help="Path to Claude Code .jsonl file")
    parser.add_argument("output", type=Path, help="Output markdown path")
    parser.add_argument(
        "--include-tool-results",
        action="store_true",
        help="Include tool_result payloads (can be very verbose).",
    )
    args = parser.parse_args()

    jsonl_to_markdown(
        input_path=args.input,
        output_path=args.output,
        include_tool_results=bool(args.include_tool_results),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
