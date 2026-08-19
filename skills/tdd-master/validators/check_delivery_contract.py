#!/usr/bin/env python3
"""Check the lightweight TDD contract and, optionally, its result ledger.

This validator intentionally uses only the Python standard library so it can run
in a fresh project environment without adding a test framework or YAML package.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import struct
import sys
from pathlib import Path


TEST_ID = r"(?:SMOKE|FLOW|RULE|DESIGN)-\d{2,3}|BUG-(?:REPRO|FIX|REG|RULE)-\d{2,3}"
SOURCE_ID = r"(?:REQ|AC|NFR|TASK|DONE|RISK|PAGE|CMP|API|DATA|SEQ|DEC|FIX|REPRO|CUR|EXP|UNCH|CON)(?:-[A-Z0-9]+)+"
TEST_ID_RE = re.compile(rf"^{TEST_ID}$")
SOURCE_ID_RE = re.compile(rf"\b{SOURCE_ID}\b")
PAGE_ID_RE = re.compile(r"\bPAGE(?:-[A-Z0-9]+)+\b")
PLACEHOLDER_RE = re.compile(r"\b(?:TBD|TODO|TBC|placeholder|missing)\b|待定|缺失|占位", re.I)
SEPARATOR_RE = re.compile(r"^:?-{3,}:?$")

CONTRACT_SECTIONS = (
    "## 0.",
    "## 1.",
    "## 2.",
    "## 3.",
    "## 4.",
    "## 5.",
    "## 6.",
)


def cells(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def rows(text: str, width: int, id_re: re.Pattern[str]) -> list[list[str]]:
    result: list[list[str]] = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        values = cells(line)
        if len(values) != width or all(SEPARATOR_RE.fullmatch(value) for value in values):
            continue
        candidate = values[0].strip("`")
        if id_re.fullmatch(candidate):
            values[0] = candidate
            result.append(values)
    return result


def field(text: str, name: str) -> str | None:
    match = re.search(
        rf"^-\s*{re.escape(name)}\s*:\s*(.+?)\s*$",
        text,
        re.MULTILINE | re.IGNORECASE,
    )
    return match.group(1).strip().strip("`") if match else None


def invalid(value: str | None, allow_dash: bool = False) -> bool:
    value = (value or "").strip().strip("`")
    if not value or PLACEHOLDER_RE.search(value):
        return True
    return value == "-" and not allow_dash


def structured_fields(value: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for part in re.split(r"[;；]", value.strip().strip("`")):
        key, separator, detail = part.partition("=")
        if separator:
            result[key.strip().lower()] = detail.strip().strip("`")
    return result


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def png_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", data[16:24])
    return (width, height) if width and height else None


def check_contract(output: Path) -> tuple[list[str], Path, list[list[str]]]:
    contract_path = output / "tests" / "TDD验收契约.md"
    errors: list[str] = []
    if not contract_path.is_file():
        return [f"文件不存在: {contract_path}"], contract_path, []

    text = contract_path.read_text(encoding="utf-8")
    for section in CONTRACT_SECTIONS:
        if not re.search(rf"^{re.escape(section)}", text, re.MULTILINE):
            errors.append(f"契约缺少章节前缀: {section}")

    work_type = field(text, "work_type")
    delivery_mode = field(text, "delivery_mode")
    workflow_mode = field(text, "workflow_mode")
    source_contract = field(text, "source_contract")
    for name, value, allowed in (
        ("work_type", work_type, {"feature", "bugfix"}),
        ("delivery_mode", delivery_mode, {"quick", "standard"}),
        ("workflow_mode", workflow_mode, {"standard", "tech-constrained"}),
        ("source_contract", source_contract, {"产品草图.md", "requirements.md", "bugfix.md"}),
    ):
        if value not in allowed:
            errors.append(f"{name} 无效或缺失: {value or '<empty>'}")

    if source_contract == "requirements.md" and work_type != "feature":
        errors.append("requirements.md 必须对应 work_type=feature")
    if source_contract == "bugfix.md" and work_type != "bugfix":
        errors.append("bugfix.md 必须对应 work_type=bugfix")
    if invalid(field(text, "source_revision")):
        errors.append("source_revision 无效或缺失")
    if invalid(field(text, "generated_from")):
        errors.append("generated_from 无效或缺失")

    contract_rows = rows(text, 6, TEST_ID_RE)
    if not contract_rows:
        errors.append("契约没有合法的六列表格验收行")
        return errors, contract_path, contract_rows

    ids = [row[0] for row in contract_rows]
    duplicates = sorted({test_id for test_id in ids if ids.count(test_id) > 1})
    if duplicates:
        errors.append("验收 ID 重复: " + ", ".join(duplicates))
    if not any(test_id.startswith("SMOKE-") for test_id in ids):
        errors.append("缺少 SMOKE 冒烟门禁")
    if work_type == "feature" and not any(test_id.startswith("FLOW-") for test_id in ids):
        errors.append("Feature 缺少 FLOW 核心用户旅程")
    if work_type == "bugfix":
        for prefix, label in (("BUG-REPRO-", "复现"), ("BUG-FIX-", "修复"), ("BUG-REG-", "回归")):
            if not any(test_id.startswith(prefix) for test_id in ids):
                errors.append(f"Bugfix 缺少{label}验收")

    for test_id, source_cell, design_cell, scenario, expected, method in contract_rows:
        if invalid(source_cell):
            if not test_id.startswith("SMOKE-"):
                errors.append(f"{test_id} 缺少 Source ID 或 design-derived 来源")
        elif not re.search(r"design-derived", source_cell, re.I) and not SOURCE_ID_RE.search(source_cell):
            errors.append(f"{test_id} 缺少可识别的 Source ID")
        if test_id.startswith("DESIGN-") and not PAGE_ID_RE.search(design_cell):
            errors.append(f"{test_id} 缺少 PAGE ID")
        if invalid(design_cell, allow_dash=test_id.startswith("SMOKE-")):
            errors.append(f"{test_id} 的 Design IDs/产物为空或仍是占位内容")
        for label, value in (("场景与操作", scenario), ("可观察通过标准", expected), ("验证方式", method)):
            if invalid(value):
                errors.append(f"{test_id} 的{label}为空或仍是占位内容")

    return errors, contract_path, contract_rows


def check_result(output: Path, contract_path: Path, contract_rows: list[list[str]]) -> list[str]:
    result_path = output / "tests" / "TDD验收结果.md"
    if not result_path.is_file():
        return [f"文件不存在: {result_path}"]
    text = result_path.read_text(encoding="utf-8")
    errors: list[str] = []
    if field(text, "contract_sha256") != sha256(contract_path):
        errors.append("contract_sha256 与当前 TDD 验收契约不一致")
    started = field(text, "run_started_at")
    if invalid(started) or not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", started or ""):
        errors.append("run_started_at 不是有效 ISO 8601 时间")

    result_rows = rows(text, 4, TEST_ID_RE)
    if not result_rows:
        return errors + ["TDD验收结果没有合法的四列表格结果行"]
    contract_ids = [row[0] for row in contract_rows]
    result_ids = [row[0] for row in result_rows]
    if len(result_ids) != len(set(result_ids)):
        errors.append("TDD验收结果 ID 重复")
    if set(result_ids) != set(contract_ids):
        missing = sorted(set(contract_ids) - set(result_ids))
        extra = sorted(set(result_ids) - set(contract_ids))
        if missing:
            errors.append("TDD验收结果漏项: " + ", ".join(missing))
        if extra:
            errors.append("TDD验收结果包含契约外 ID: " + ", ".join(extra))

    contract_by_id = {row[0]: row for row in contract_rows}
    for test_id, status, action, evidence in result_rows:
        normalized_status = status.strip("`").lower()
        if normalized_status != "pass":
            errors.append(f"{test_id} 尚未通过: {status}")
        if invalid(action):
            errors.append(f"{test_id} 缺少本轮实际验证动作")
        if invalid(evidence):
            errors.append(f"{test_id} 缺少本轮验证证据")
        if test_id.startswith("DESIGN-") and test_id in contract_by_id:
            if not (re.search(r"baseline", action, re.I) and re.search(r"actual", action, re.I)):
                errors.append(f"{test_id} 的验证动作没有说明查看 baseline 和 actual")
            details = structured_fields(evidence)
            for key in ("baseline", "actual", "reviewer", "review", "blocking"):
                if invalid(details.get(key)):
                    errors.append(f"{test_id} 缺少视觉证据字段: {key}")
            if details.get("reviewer", "").lower() != "independent-visual":
                errors.append(f"{test_id} 必须由 independent-visual 独立复核")
            if details.get("review", "").lower() != "pass":
                errors.append(f"{test_id} 的视觉复核未通过")
            if details.get("blocking") != "0":
                errors.append(f"{test_id} 仍有阻塞视觉差异")
            image_sizes: list[tuple[str, tuple[int, int] | None]] = []
            for key in ("baseline", "actual"):
                raw_path = details.get(key, "").strip("`\"'")
                relative = Path(raw_path.removeprefix("output/"))
                if (
                    relative.is_absolute()
                    or ".." in relative.parts
                    or relative.parts[:2] != ("tests", "visual")
                    or relative.suffix.lower() != ".png"
                ):
                    errors.append(f"{test_id} 的 {key} 必须是 output/tests/visual/ 下的 PNG")
                    continue
                image_path = output / relative
                if not image_path.is_file():
                    errors.append(f"{test_id} 的 {key} 截图不存在: {relative}")
                    continue
                image_sizes.append((key, png_dimensions(image_path)))
            if len(image_sizes) == 2:
                if details.get("baseline") == details.get("actual"):
                    errors.append(f"{test_id} 的 baseline 与 actual 不能是同一文件")
                if any(size is None for _, size in image_sizes):
                    errors.append(f"{test_id} 的视觉证据不是有效 PNG")
                elif image_sizes[0][1] != image_sizes[1][1]:
                    errors.append(f"{test_id} 的 baseline 与 actual 尺寸不一致")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="检查轻量 TDD 验收契约与结果台账")
    parser.add_argument("output", type=Path, help="项目 output 目录")
    parser.add_argument("--result", action="store_true", help="同时检查 TDD验收结果.md")
    args = parser.parse_args()

    errors, contract_path, contract_rows = check_contract(args.output)
    if args.result and contract_rows:
        errors.extend(check_result(args.output, contract_path, contract_rows))
    if errors:
        print(f"❌ TDD 交付校验失败（{len(errors)}）")
        for error in errors:
            print(f"  - {error}")
        return 2
    suffix = "，结果台账全部通过" if args.result else ""
    print(f"✅ TDD 交付校验通过：{len(contract_rows)} 条验收项{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
