from __future__ import annotations

import os
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
TAGS_DIR = DOCS / "tags"

EXCLUDE_DIRS = {"tags"}
EXCLUDE_FILES = {"_sidebar.md", "_navbar.md", "_coverpage.md"}

BACKLINKS_START = "<!-- backlinks:start -->"
BACKLINKS_END = "<!-- backlinks:end -->"

TAG_LINE_RE = re.compile(r"^(Tags|标签)\s*:\s*(.+)$", re.IGNORECASE)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def iter_pages() -> list[Path]:
    pages: list[Path] = []
    for path in DOCS.rglob("*.md"):
        rel = path.relative_to(DOCS)
        if rel.parts and rel.parts[0] in EXCLUDE_DIRS:
            continue
        if path.name in EXCLUDE_FILES:
            continue
        pages.append(path)
    return pages


def extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def parse_tags(text: str) -> list[str]:
    for line in text.splitlines():
        match = TAG_LINE_RE.match(line.strip())
        if not match:
            continue
        raw = match.group(2).strip()
        if not raw:
            return []
        parts = re.split(r"[,\uFF0C;/|]+", raw)
        tags: list[str] = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if re.search(r"\s", part):
                tags.extend([p for p in re.split(r"\s+", part) if p])
            else:
                tags.append(part)
        return tags
    return []


def slugify(tag: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", tag.lower()).strip("-")
    if not slug:
        slug = f"tag-{abs(hash(tag)) % 100000}"
    return slug


def parse_links(text: str, source_path: Path) -> list[Path]:
    links: list[Path] = []
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip()
        if not target:
            continue
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        target = target.split("#", 1)[0].split("?", 1)[0]
        if not target.endswith(".md"):
            continue
        if target.startswith("/"):
            target_path = (DOCS / target.lstrip("/")).resolve()
        else:
            target_path = (source_path.parent / target).resolve()
        try:
            target_path.relative_to(DOCS)
        except ValueError:
            continue
        if target_path.exists():
            links.append(target_path)
    return links


def render_backlinks(
    page_path: Path,
    backlinks: list[Path],
    titles: dict[Path, str],
) -> str:
    lines = [BACKLINKS_START, "## Backlinks"]
    if backlinks:
        for src in backlinks:
            title = titles.get(src, src.stem)
            rel_link = os.path.relpath(src, page_path.parent).replace("\\", "/")
            lines.append(f"- [{title}]({rel_link})")
    else:
        lines.append("- 暂无")
    lines.append(BACKLINKS_END)
    return "\n".join(lines)


def update_backlinks_section(page_path: Path, block: str) -> None:
    text = page_path.read_text(encoding="utf-8")
    if BACKLINKS_START in text and BACKLINKS_END in text:
        pattern = re.compile(
            rf"{re.escape(BACKLINKS_START)}.*?{re.escape(BACKLINKS_END)}",
            re.S,
        )
        new_text = pattern.sub(block, text)
    else:
        new_text = text.rstrip() + "\n\n" + block + "\n"
    if new_text != text:
        page_path.write_text(new_text, encoding="utf-8")


def render_tags_index(tag_map: dict[str, list[Path]], tag_display: dict[str, str]) -> str:
    lines = ["# 标签", ""]
    if not tag_map:
        lines.append("暂无标签。")
        return "\n".join(lines) + "\n"
    for slug in sorted(tag_map.keys()):
        display = tag_display[slug]
        count = len(tag_map[slug])
        lines.append(f"- [{display}]({slug}.md) ({count})")
    return "\n".join(lines) + "\n"


def render_tag_page(
    slug: str,
    display: str,
    pages: list[Path],
    titles: dict[Path, str],
) -> str:
    lines = [f"# 标签：{display}", "", "- [返回标签索引](index.md)", ""]
    for page in pages:
        title = titles.get(page, page.stem)
        rel_link = os.path.relpath(page, TAGS_DIR).replace("\\", "/")
        lines.append(f"- [{title}]({rel_link})")
    return "\n".join(lines) + "\n"


def main() -> None:
    pages = iter_pages()
    titles: dict[Path, str] = {}
    tags_by_page: dict[Path, list[str]] = {}

    for page in pages:
        text = page.read_text(encoding="utf-8")
        titles[page] = extract_title(text, page.stem)
        tags_by_page[page] = parse_tags(text)

    incoming: dict[Path, set[Path]] = defaultdict(set)
    for page in pages:
        text = page.read_text(encoding="utf-8")
        for target in parse_links(text, page):
            if target in pages:
                incoming[target].add(page)

    for page in pages:
        backlinks = sorted(incoming.get(page, set()), key=lambda p: titles.get(p, p.stem))
        block = render_backlinks(page, backlinks, titles)
        update_backlinks_section(page, block)

    tag_map: dict[str, list[Path]] = defaultdict(list)
    tag_display: dict[str, str] = {}
    for page in pages:
        for tag in tags_by_page[page]:
            slug = slugify(tag)
            tag_map[slug].append(page)
            tag_display.setdefault(slug, tag)

    TAGS_DIR.mkdir(parents=True, exist_ok=True)
    (TAGS_DIR / "index.md").write_text(
        render_tags_index(tag_map, tag_display), encoding="utf-8"
    )

    existing_tag_pages = {p.stem for p in TAGS_DIR.glob("*.md") if p.name != "index.md"}
    for slug in existing_tag_pages:
        if slug not in tag_map:
            (TAGS_DIR / f"{slug}.md").unlink()

    for slug, pages_list in tag_map.items():
        sorted_pages = sorted(pages_list, key=lambda p: titles.get(p, p.stem))
        content = render_tag_page(slug, tag_display[slug], sorted_pages, titles)
        (TAGS_DIR / f"{slug}.md").write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
