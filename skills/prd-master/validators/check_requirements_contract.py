#!/usr/bin/env python3
"""Validate the compact standard requirements contract without third-party packages."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ID_RE = re.compile(
    r"^(?:US-F\d{2,3}-\d{2,3}|REQ-F\d{2,3}-\d{2,3}|"
    r"AC-F\d{2,3}-\d{2,3}|NFR-\d{3})$"
)
REQ_RE = re.compile(r"REQ-F\d{2,3}-\d{2,3}")
PLACEHOLDER_RE = re.compile(r"\{\{|\}\}|\b(?:TBD|TODO|TBC|placeholder|missing)\b|待定|缺失|占位", re.I)
REQUIRED_SECTIONS = (
    "## Metadata",
    "## External capability configuration",
    "## Capability prerequisites",
    "## Non-functional requirements",
)


def field(text: str, name: str) -> str | None:
    match = re.search(
        rf"^-\s*{re.escape(name)}\s*:\s*(.+?)\s*$",
        text,
        re.MULTILINE | re.IGNORECASE,
    )
    return match.group(1).strip().strip("`") if match else None


def invalid(value: str | None) -> bool:
    value = (value or "").strip().strip("`")
    return not value or value == "-" or bool(PLACEHOLDER_RE.search(value))


def blocks(text: str) -> tuple[dict[str, str], list[str]]:
    matches = list(
        re.finditer(
            r"^###\s+((?:US-F\d{2,3}-\d{2,3}|REQ-F\d{2,3}-\d{2,3}|"
            r"AC-F\d{2,3}-\d{2,3}|NFR-\d{3}))\b",
            text,
            re.MULTILINE,
        )
    )
    result: dict[str, str] = {}
    errors: list[str] = []
    for index, match in enumerate(matches):
        identifier = match.group(1)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        if identifier in result:
            errors.append(f"重复定义 ID: {identifier}")
        result[identifier] = text[match.start() : end]
    return result, errors


def table_rows(text: str, heading: str, width: int) -> list[list[str]]:
    if heading not in text:
        return []
    section = text.split(heading, 1)[1]
    section = re.split(r"\n##\s+", section, maxsplit=1)[0]
    rows: list[list[str]] = []
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        values = [value.strip().strip("`") for value in line.strip().strip("|").split("|")]
        if len(values) != width or values[0].lower() in {"capability", "prerequisite"}:
            continue
        if all(re.fullmatch(r":?-+:?", value) for value in values):
            continue
        rows.append(values)
    return rows


def validate_tables(text: str, reqs: set[str], errors: list[str]) -> None:
    external_heading = "## External capability configuration"
    external = table_rows(text, external_heading, 8)
    if not external:
        errors.append("External capability configuration 没有合法责任行")
    elif any(row[0].lower() == "none" for row in external):
        if len(external) != 1 or external[0][1:] != ["-"] * 7:
            errors.append("没有外部能力时只能保留一行 none，其他列必须为 -")
    else:
        for row in external:
            capability, owner, actor, surface, scope, lifecycle, stage, requirement_ids = row
            label = f"外部能力 {capability}"
            for name, value in (("Credential owner", owner), ("Configuration actor", actor), ("Surface", surface), ("Scope", scope), ("Lifecycle", lifecycle), ("Stage", stage)):
                if invalid(value):
                    errors.append(f"{label} 缺少 {name}")
            referenced = set(REQ_RE.findall(requirement_ids))
            unknown = sorted(referenced - reqs)
            if unknown:
                errors.append(f"{label} 引用未定义需求: {', '.join(unknown)}")

    prerequisites = table_rows(text, "## Capability prerequisites", 7)
    if not prerequisites:
        errors.append("Capability prerequisites 没有合法责任行")
    elif any(row[0].lower() == "none" for row in prerequisites):
        if len(prerequisites) != 1 or prerequisites[0][1:] != ["-"] * 6:
            errors.append("没有方案前置能力时只能保留一行 none，其他列必须为 -")
    else:
        for row in prerequisites:
            prerequisite, status, owner, evidence, fallback, stage, requirement_ids = row
            label = f"方案前置能力 {prerequisite}"
            if status not in {"ready", "committed"}:
                errors.append(f"{label} 的 Status 必须为 ready 或 committed")
            for name, value in (("Owner", owner), ("Evidence or deadline", evidence), ("Fallback", fallback), ("Stage", stage)):
                if invalid(value):
                    errors.append(f"{label} 缺少 {name}")
            referenced = set(REQ_RE.findall(requirement_ids))
            if not referenced:
                errors.append(f"{label} 必须关联至少一个 REQ")
            unknown = sorted(referenced - reqs)
            if unknown:
                errors.append(f"{label} 引用未定义需求: {', '.join(unknown)}")


def validate_contract(text: str) -> list[str]:
    errors: list[str] = []
    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"缺少章节: {section}")

    if field(text, "work_type") != "feature":
        errors.append("requirements.md 的 work_type 必须为 feature")
    if field(text, "delivery_mode") not in {"standard", "quick"}:
        errors.append("delivery_mode 必须为 standard 或 quick")
    if field(text, "workflow_mode") not in {"standard", "tech-constrained"}:
        errors.append("workflow_mode 必须为 standard 或 tech-constrained")
    for name in ("source_revision", "source_prd", "status"):
        if invalid(field(text, name)):
            errors.append(f"Metadata 缺少有效 {name}")

    items, block_errors = blocks(text)
    errors.extend(block_errors)
    if not any(key.startswith("US-") for key in items):
        errors.append("缺少 US 用户故事")
    if not any(key.startswith("REQ-") for key in items):
        errors.append("缺少 REQ 行为需求")
    if not any(key.startswith("AC-") for key in items):
        errors.append("缺少 AC 可观察结果")

    stories = {key for key in items if key.startswith("US-")}
    reqs = {key for key in items if key.startswith("REQ-")}
    acs = {key for key in items if key.startswith("AC-")}
    for story in sorted(stories):
        for name in ("Role", "Goal"):
            match = re.search(rf"^-\s*{name}:\s*(.+?)\s*$", items[story], re.MULTILINE)
            if not match or invalid(match.group(1)):
                errors.append(f"{story} 缺少有效 {name}")
    for req in sorted(reqs):
        match = re.search(r"^-\s*Story:\s*(US-F\d{2,3}-\d{2,3})\s*$", items[req], re.MULTILINE)
        if not match:
            errors.append(f"{req} 缺少合法 Story")
        elif match.group(1) not in stories:
            errors.append(f"{req} 引用未定义用户故事 {match.group(1)}")
    referenced_reqs: set[str] = set()
    for ac in sorted(acs):
        block = items[ac]
        parent = re.search(r"^-\s*Parent:\s*(REQ-F\d{2,3}-\d{2,3})\s*$", block, re.MULTILINE)
        if not parent:
            errors.append(f"{ac} 缺少合法 Parent")
        else:
            referenced_reqs.add(parent.group(1))
            if parent.group(1) not in reqs:
                errors.append(f"{ac} 引用未定义需求 {parent.group(1)}")
        priority = re.search(r"^-\s*Priority:\s*(P[0-2])\s*$", block, re.MULTILINE)
        if not priority:
            errors.append(f"{ac} 缺少 P0/P1/P2 Priority")
        if not re.search(r"\bWHEN\b[\s\S]+\bTHE SYSTEM SHALL\b", block):
            errors.append(f"{ac} 缺少 WHEN ... THE SYSTEM SHALL ... EARS 行为")
    for req in sorted(reqs - referenced_reqs):
        errors.append(f"{req} 没有任何 AC 覆盖")

    for nfr, block in ((key, value) for key, value in items.items() if key.startswith("NFR-")):
        applies = set(REQ_RE.findall(field(block, "Applies-to") or ""))
        if not applies or not applies <= reqs:
            errors.append(f"{nfr} 的 Applies-to 必须引用已定义 REQ")
        if invalid(field(block, "Measure")):
            errors.append(f"{nfr} 缺少可验证 Measure")
    validate_tables(text, reqs, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="检查轻量 PRD requirements.md 契约")
    parser.add_argument("contract", type=Path, help="requirements.md 路径")
    parser.add_argument("--analysis", type=Path, help="可选 requirements-analysis.md 路径")
    args = parser.parse_args()
    if not args.contract.is_file():
        print(f"❌ 文件不存在: {args.contract}")
        return 2
    text = args.contract.read_text(encoding="utf-8")
    errors = validate_contract(text)
    if args.analysis:
        if not args.analysis.is_file():
            errors.append(f"分析文件不存在: {args.analysis}")
        else:
            analysis = args.analysis.read_text(encoding="utf-8")
            for label in ("P0 unresolved: 0", "P1 unresolved: 0"):
                if label not in analysis:
                    errors.append(f"正确性分析缺少清零汇总: {label}")
    if errors:
        print(f"❌ 需求契约校验失败（{len(errors)}）")
        for error in errors:
            print(f"  - {error}")
        return 2
    print("✅ 需求契约校验通过：Metadata、US/REQ/AC/NFR、外部能力和前置能力均可追踪")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
