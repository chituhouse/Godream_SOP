#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ConversationMeta:
    source: str
    relpath: str
    size_bytes: int
    start_ts: str | None = None
    end_ts: str | None = None
    slug: str | None = None
    session_id: str | None = None
    user_messages: int | None = None
    assistant_messages: int | None = None


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def _read_jsonl_meta(path: Path) -> dict[str, Any]:
    start_ts: str | None = None
    end_ts: str | None = None
    slug: str | None = None
    session_id: str | None = None
    user = 0
    assistant = 0

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            t = obj.get("type")
            if t == "user":
                user += 1
            elif t == "assistant":
                assistant += 1
            else:
                continue

            ts = obj.get("timestamp")
            if isinstance(ts, str) and ts:
                if start_ts is None:
                    start_ts = ts
                    slug = obj.get("slug") if isinstance(obj.get("slug"), str) else None
                    session_id = obj.get("sessionId") if isinstance(obj.get("sessionId"), str) else None
                end_ts = ts

    return {
        "start_ts": start_ts,
        "end_ts": end_ts,
        "slug": slug,
        "session_id": session_id,
        "user_messages": user,
        "assistant_messages": assistant,
    }


_CODEX_NAME_RE = re.compile(r"^rollout-(\d{4}-\d{2}-\d{2})T(\d{2})-(\d{2})-(\d{2})-")
_SERENA_NAME_RE = re.compile(r"^mcp_(\d{8})-(\d{6})")


def _parse_from_filename(path: Path) -> dict[str, Any]:
    name = path.name
    if m := _CODEX_NAME_RE.match(name):
        date_s, hh, mm, ss = m.groups()
        return {"start_ts": f"{date_s}T{hh}:{mm}:{ss}Z", "end_ts": None}
    if m := _SERENA_NAME_RE.match(name):
        ymd, hms = m.groups()
        return {
            "start_ts": f"{ymd[0:4]}-{ymd[4:6]}-{ymd[6:8]}T{hms[0:2]}:{hms[2:4]}:{hms[4:6]}Z",
            "end_ts": None,
        }
    return {}


def build_index(repo_root: Path) -> list[ConversationMeta]:
    conv_root = repo_root / "conversations"
    metas: list[ConversationMeta] = []

    for path in sorted(conv_root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_root).as_posix()
        size = path.stat().st_size

        parts = rel.split("/", 2)
        source = parts[1] if len(parts) > 1 else "unknown"

        meta_kwargs: dict[str, Any] = {}
        if source == "claude" and path.suffix.lower() == ".jsonl":
            meta_kwargs.update(_read_jsonl_meta(path))
        elif source == "codex" and path.suffix.lower() == ".jsonl":
            meta_kwargs.update(_parse_from_filename(path))
        elif source == "serena":
            meta_kwargs.update(_parse_from_filename(path))

        metas.append(
            ConversationMeta(
                source=source,
                relpath=rel,
                size_bytes=size,
                start_ts=meta_kwargs.get("start_ts"),
                end_ts=meta_kwargs.get("end_ts"),
                slug=meta_kwargs.get("slug"),
                session_id=meta_kwargs.get("session_id"),
                user_messages=meta_kwargs.get("user_messages"),
                assistant_messages=meta_kwargs.get("assistant_messages"),
            )
        )

    def sort_key(m: ConversationMeta) -> tuple[float, str]:
        dt = _parse_iso(m.start_ts)
        return ((dt.timestamp() if dt else float("inf")), m.relpath)

    metas.sort(key=sort_key)
    return metas


def write_outputs(repo_root: Path, metas: list[ConversationMeta]) -> None:
    out_dir = repo_root / "sop" / "conversations"
    out_dir.mkdir(parents=True, exist_ok=True)

    index_json = out_dir / "index.json"
    index_md = out_dir / "index.md"

    index_json.write_text(json.dumps([asdict(m) for m in metas], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines: list[str] = []
    lines.append("# 对话记录索引（自动生成）")
    lines.append("")
    lines.append("说明：本索引用于“先查索引 → 再回看原始对话取证”，避免在海量对话里盲翻。")
    lines.append("")
    lines.append(f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- 源数据目录：`conversations/`")
    lines.append(f"- 机器可读索引：`{index_json.relative_to(repo_root).as_posix()}`")
    lines.append("")

    def fmt_ts(ts: str | None) -> str:
        if not ts:
            return "-"
        dt = _parse_iso(ts)
        return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else ts

    lines.append("## 按时间线（Top 50）")
    lines.append("")
    lines.append("| 时间 | 来源 | 文件 | 备注 |")
    lines.append("|---|---|---|---|")
    for m in metas[:50]:
        note = []
        if m.slug:
            note.append(f"slug={m.slug}")
        if m.user_messages is not None and m.assistant_messages is not None:
            note.append(f"u/a={m.user_messages}/{m.assistant_messages}")
        lines.append(f"| {fmt_ts(m.start_ts)} | {m.source} | `{m.relpath}` | {'; '.join(note) if note else '-'} |")
    lines.append("")
    lines.append("## 使用建议")
    lines.append("")
    lines.append("1) 先用关键词在仓库内搜索（如：`NAS`、`相对路径`、`SQLite`、`PySide6`）。")
    lines.append("2) 找到相关 session 后，回看原始 jsonl 或 `readable/` 的可读导出。")
    lines.append("3) 把关键结论回写到 `marketing/00_对外口径真源.md` 或对应 SOP/ADR，避免口径漂移。")
    lines.append("")

    index_md.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build conversation index for Godream_SOP.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    metas = build_index(repo_root)
    write_outputs(repo_root, metas)
    print(f"indexed {len(metas)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
