#!/usr/bin/env python3
"""Validate standard Design HTML identity, paired docs, tokens, and local links."""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


PAGE_ID_RE = re.compile(r"^PAGE(?:-F\d{2,3}-\d{2,3}|-\d{2,3})$")
PLACEHOLDER_RE = re.compile(r"\{\{|\}\}|\b(?:TODO|TBD|TBC|placeholder)\b|待定|缺失|占位", re.I)
LOCAL_JS_RE = re.compile(
    r"(?:location(?:\.href|\.assign)?|window\.location(?:\.href|\.assign)?)\s*=\s*['\"]([^'\"]+)['\"]",
    re.I,
)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.page_id: str | None = None
        self.links: list[str] = []
        self.onclick_values: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "meta" and values.get("name", "").lower() == "page-id":
            self.page_id = values.get("content", "").strip()
        href = values.get("href")
        if href:
            self.links.append(href.strip())
        onclick = values.get("onclick")
        if onclick:
            self.onclick_values.append(onclick)


def local_target(raw: str) -> str | None:
    value = raw.strip().strip("`\"'")
    if not value or value.startswith(("#", "/", "//")):
        return None
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        return None
    path = parsed.path
    return path if path.lower().endswith((".html", ".htm")) else None


def check_file(path: Path, output: Path, standard: bool, errors: list[str]) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"无法读取 {path}: {exc}")
        return
    parser = PageParser()
    try:
        parser.feed(text)
    except Exception as exc:  # HTMLParser is deliberately tolerant, but report malformed input.
        errors.append(f"HTML 解析失败 {path.name}: {exc}")
        return
    if not parser.page_id or not PAGE_ID_RE.fullmatch(parser.page_id):
        errors.append(f"{path.name} 缺少合法 page-id 元信息")
    md_path = path.with_suffix(".md")
    if not md_path.is_file():
        errors.append(f"{path.name} 缺少同名页面 MD: {md_path.name}")
    else:
        md_text = md_path.read_text(encoding="utf-8")
        md_id = re.search(r"页面 ID\s*\|\s*`?(PAGE(?:-F\d{2,3}-\d{2,3}|-\d{2,3}))`?", md_text)
        if not md_id or md_id.group(1) != parser.page_id:
            errors.append(f"{path.name} 与同名 MD 的 PAGE ID 不一致")
    if PLACEHOLDER_RE.search(text):
        errors.append(f"{path.name} 含有占位文本")
    if standard:
        for token in ("--bg", "--fg", "--accent", "--font-body", "--space-"):
            if token not in text:
                errors.append(f"{path.name} 缺少设计 Token: {token}")
        if ("animation" in text or "transition" in text) and "prefers-reduced-motion" not in text:
            errors.append(f"{path.name} 使用动效但缺少 prefers-reduced-motion 降级")
    targets = list(parser.links)
    for onclick in parser.onclick_values:
        targets.extend(LOCAL_JS_RE.findall(onclick))
    seen: set[str] = set()
    for raw in targets:
        target = local_target(raw)
        if target is None or target in seen:
            continue
        seen.add(target)
        target_path = (path.parent / target).resolve()
        if not target_path.is_file() or output.resolve() not in target_path.parents:
            errors.append(f"{path.name} 的本地跳转目标不存在或越界: {raw}")


def main() -> int:
    parser = argparse.ArgumentParser(description="检查 Design HTML 交付契约与本地链接")
    parser.add_argument("output", type=Path, help="项目 output 目录")
    parser.add_argument("--standard", action="store_true", help="启用标准 HTML/Token/动效门禁")
    args = parser.parse_args()
    pages = args.output / "pages"
    if not pages.is_dir():
        print(f"❌ 页面目录不存在: {pages}")
        return 2
    html_files = sorted(pages.glob("*.html"))
    if args.standard and not html_files:
        print("❌ standard 模式至少需要一个 pages/*.html")
        return 2
    errors: list[str] = []
    for path in html_files:
        check_file(path, args.output, args.standard, errors)
    if errors:
        print(f"❌ HTML 交付校验失败（{len(errors)}）")
        for error in errors:
            print(f"  - {error}")
        return 2
    print(f"✅ HTML 交付校验通过：{len(html_files)} 个页面，standard={str(args.standard).lower()}，本地链接无断链")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
