#!/usr/bin/env python3
"""Check the lightweight Design trace matrix and referenced page documents."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SOURCE_RE = re.compile(
    r"\b(?:REQ-F\d{2,3}-\d{2,3}|AC-F\d{2,3}-\d{2,3}|NFR-\d{3}|"
    r"REPRO-\d{2,3}|CUR-\d{2,3}|EXP-\d{2,3}|UNCH-\d{2,3}|CON-\d{2,3}|"
    r"TASK-\d{2,3}|DONE-\d{2,3}|RISK-\d{2,3})\b"
)
HEADING_SOURCE_RE = re.compile(
    r"^###\s+((?:REQ-F\d{2,3}-\d{2,3}|AC-F\d{2,3}-\d{2,3}|NFR-\d{3}|"
    r"REPRO-\d{2,3}|CUR-\d{2,3}|EXP-\d{2,3}|UNCH-\d{2,3}|CON-\d{2,3}))\b",
    re.MULTILINE,
)
DESIGN_RE = re.compile(
    r"\b(?:PAGE(?:-F\d{2,3}-\d{2,3}|-\d{2,3})|CMP(?:-F\d{2,3}-\d{2,3}|-\d{2,3})|"
    r"API(?:-F\d{2,3}-\d{2,3}|-\d{2,3})|DATA(?:-F\d{2,3}-\d{2,3}|-\d{2,3})|"
    r"SEQ(?:-F\d{2,3}-\d{2,3}|-\d{2,3})|DEC-\d{3}|FIX-BUG-\d{3})\b"
)
PAGE_RE = re.compile(r"\bPAGE(?:-F\d{2,3}-\d{2,3}|-\d{2,3})\b")
PLACEHOLDER_RE = re.compile(r"\b(?:TBD|TODO|TBC|missing|placeholder)\b|待定|缺失|占位", re.I)
PAGE_SECTIONS = tuple(f"## {index}." for index in range(1, 11))


def field(text: str, name: str) -> str | None:
    match = re.search(rf"^-\s*{re.escape(name)}\s*:\s*(.+?)\s*$", text, re.MULTILINE | re.I)
    return match.group(1).strip().strip("`") if match else None


def table_rows(text: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        values = [value.strip().strip("`") for value in line.strip().strip("|").split("|")]
        if len(values) != 7 or values[0].lower() == "source id":
            continue
        if all(re.fullmatch(r":?-+:?", value) for value in values):
            continue
        if SOURCE_RE.fullmatch(values[0]):
            result[values[0]] = values
    return result


def source_blocks(text: str) -> dict[str, str]:
    matches = list(HEADING_SOURCE_RE.finditer(text))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[match.start() : end]
        if not re.search(r"^-\s*Status:\s*retired\s*$", block, re.MULTILINE | re.I):
            blocks[match.group(1)] = block
    return blocks


def source_inventory(source_path: Path) -> tuple[set[str], set[str], str, list[str]]:
    text = source_path.read_text(encoding="utf-8")
    errors: list[str] = []
    if source_path.name == "requirements.md":
        blocks = source_blocks(text)
        if not blocks:
            errors.append("requirements.md 没有合法的 REQ/AC/NFR 标题")
        requirements = {key for key in blocks if key.startswith("REQ-")}
        mvp = {key for key, block in blocks.items() if key.startswith("REQ-") and "MVP" in (field(block, "Stage") or "").upper()}
        for key, block in blocks.items():
            if key.startswith("AC-") and field(block, "Parent") in mvp:
                mvp.add(key)
            if key.startswith("NFR-"):
                applies = set(SOURCE_RE.findall(field(block, "Applies-to") or ""))
                if not applies or applies & mvp:
                    mvp.add(key)
        for key, block in blocks.items():
            if key.startswith("REQ-") and not field(block, "Stage"):
                errors.append(f"{key} 缺少 Stage")
            if key.startswith("AC-") and field(block, "Parent") not in requirements:
                errors.append(f"{key} 的 Parent 不是 active REQ")
        return set(blocks), mvp, "standard", errors
    if source_path.name == "bugfix.md":
        blocks = source_blocks(text)
        if not blocks:
            errors.append("bugfix.md 没有合法的 Bugfix source 标题")
        return set(blocks), set(blocks), "bugfix", errors
    quick_sources = set(SOURCE_RE.findall(text)) & {key for key in SOURCE_RE.findall(text) if key.startswith(("TASK-", "DONE-", "RISK-"))}
    if not quick_sources:
        errors.append("quick 产品草图没有找到 TASK/DONE/RISK source ID")
    return quick_sources, quick_sources, "quick", errors


def artifact_paths(value: str) -> list[Path]:
    paths: list[Path] = []
    for raw in re.split(r"[;,]", value):
        raw = raw.strip().strip("`").strip()
        for token in raw.split():
            token = token.strip("`\"'")
            if token.startswith("output/"):
                token = token.removeprefix("output/")
            if token.startswith("pages/") and token.lower().endswith((".md", ".html")):
                paths.append(Path(token))
    return paths


def check_page(path: Path, expected_page: str, errors: list[str]) -> None:
    if not path.is_file():
        errors.append(f"页面产物不存在: {path}")
        return
    if path.suffix.lower() != ".md":
        return
    text = path.read_text(encoding="utf-8")
    for section in PAGE_SECTIONS:
        if not re.search(rf"^{re.escape(section)}", text, re.MULTILINE):
            errors.append(f"{path.name} 缺少页面章节: {section}")
    if not re.search(rf"页面 ID\s*\|\s*`?{re.escape(expected_page)}`?", text):
        errors.append(f"{path.name} 的页面 ID 与 {expected_page} 不一致")
    source_match = re.search(r"Source IDs\s*\|\s*([^|]+)", text)
    if not source_match or not SOURCE_RE.search(source_match.group(1)):
        errors.append(f"{path.name} 缺少可追踪的 Source IDs")


def main() -> int:
    parser = argparse.ArgumentParser(description="检查 Design 追溯矩阵和页面施工图")
    parser.add_argument("output", type=Path, help="项目 output 目录")
    args = parser.parse_args()
    output = args.output
    trace_path = output / "设计追溯矩阵.md"
    if not trace_path.is_file():
        print(f"❌ 文件不存在: {trace_path}")
        return 2

    source_candidates = [output / name for name in ("requirements.md", "bugfix.md", "产品草图.md")]
    source_path = next((path for path in source_candidates if path.is_file()), None)
    if source_path is None:
        print("❌ 找不到 requirements.md、bugfix.md 或 产品草图.md")
        return 2

    sources, mvp_sources, mode, errors = source_inventory(source_path)
    rows = table_rows(trace_path.read_text(encoding="utf-8"))
    checked_page_paths: set[Path] = set()
    if not rows:
        errors.append("设计追溯矩阵没有合法的七列表格数据行")
    trace_text = trace_path.read_text(encoding="utf-8")
    for source in sorted(sources):
        if source not in rows:
            errors.append(f"缺少 Source 行: {source}")
            continue
        source_id, revision, design_ids, artifact, invariant, verification, status = rows[source]
        if not DESIGN_RE.search(design_ids):
            errors.append(f"{source} 缺少合法 Design ID")
        for label, value in (("Artifact", artifact), ("Error/Invariant", invariant), ("Verification Surface", verification)):
            if not value or value == "-" or PLACEHOLDER_RE.search(value):
                errors.append(f"{source} 的 {label} 未完成")
        normalized_status = status.strip().lower()
        allowed = {"covered", "preserved"} if source in mvp_sources else {"covered", "preserved", "planned"}
        if normalized_status not in allowed:
            errors.append(f"{source} 状态不合法: {status}")
        if normalized_status == "planned":
            if not any(name in artifact for name in ("页面清单.md", "设计决策蓝图.md", "技术方案.md")):
                errors.append(f"{source} 的 planned Artifact 必须指向页面清单/蓝图/技术方案骨架")
            if re.search(r"pages[/\\].+\.(?:md|html)\b", artifact, re.I):
                errors.append(f"{source} 为 planned，不得伪造已生成的页面文件")
            continue
        pages = sorted(set(PAGE_RE.findall(design_ids)))
        if pages:
            paths = artifact_paths(artifact)
            md_paths = [path for path in paths if path.suffix.lower() == ".md"]
            html_paths = [path for path in paths if path.suffix.lower() == ".html"]
            if not md_paths:
                errors.append(f"{source} 的 PAGE 设计缺少 pages/*.md Artifact")
            if mode == "standard" and not html_paths:
                errors.append(f"{source} 的 standard PAGE 设计缺少 pages/*.html Artifact")
            for page_id in pages:
                for path in md_paths:
                    resolved = output / path
                    if resolved not in checked_page_paths:
                        check_page(resolved, page_id, errors)
                        checked_page_paths.add(resolved)
                if mode == "standard":
                    for path in html_paths:
                        html_path = output / path
                        if not html_path.is_file():
                            errors.append(f"页面产物不存在: {html_path}")
                        elif not re.search(
                            rf'''page-id["']?\s*[:=]\s*["']{re.escape(page_id)}["']''',
                            html_path.read_text(encoding="utf-8"),
                            re.I,
                        ):
                            errors.append(f"{html_path.name} 缺少 {page_id} 的 page-id 元信息")

    extra = sorted(set(rows) - sources)
    if extra:
        errors.append("矩阵包含未定义或 retired Source: " + ", ".join(extra))
    if errors:
        print(f"❌ Design 追溯校验失败（{len(errors)}）")
        for error in errors:
            print(f"  - {error}")
        return 2
    print(f"✅ Design 追溯校验通过：{len(mvp_sources)} 个核心 Source / {len(rows)} 条矩阵记录 / {mode} 模式")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
