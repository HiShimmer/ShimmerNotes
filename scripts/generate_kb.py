from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
TAGS_DIR = DOCS / "tags"

EXCLUDE_DIRS = {"tags"}
EXCLUDE_FILES = {"_sidebar.md", "_navbar.md", "_coverpage.md"}

TAG_LINE_RE = re.compile(r"^(Tags|标签)\s*:\s*(.+)$", re.IGNORECASE)


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
