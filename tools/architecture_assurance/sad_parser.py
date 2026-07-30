"""Parse Better Tomorrow arc42 SAD declarations without fabricating bindings."""

from __future__ import annotations

from dataclasses import dataclass
import re


_SECTION = re.compile(r"(?m)^##\s+(?P<number>\d+)\.\s+(?P<title>.+?)\s*$")
_DECISION = re.compile(
    r"(?ms)^###\s+(?P<id>D\d+|MVP\d+-\d+|ADR-\d+):\s*(?P<title>.+?)\n"
    r"(?P<body>.*?)(?=^###\s+(?:D\d+|MVP\d+-\d+|ADR-\d+):|\Z)"
)
_STATUS = re.compile(r"(?m)^\*\*Status:\*\*\s*(?P<status>.+?)\s*$")
_TABLE_ROW = re.compile(r"(?m)^\|\s*(?P<block>[^|\n]+?)\s*\|\s*(?P<path>[^|\n]+?)\s*\|")
_MERMAID_NODE = re.compile(
    r'(?m)^\s*[A-Za-z][A-Za-z0-9_]*\["(?P<label>[^"]+)"\]'
)
_CODE = re.compile(r"`(?P<value>[^`\r\n]+)`")
_MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\((?P<target>[^)#]+)(?:#[^)]+)?\)")
_PATHISH = re.compile(
    r"(?i)(?:^|[\s(])(?P<path>[A-Za-z0-9_' -]+(?:/[A-Za-z0-9_.?*' -]+)+"
    r"\.(?:py|sql|ya?ml|json|html|js|css|toml|ini|md))(?=$|[\s),.;])"
)


@dataclass(frozen=True)
class Declaration:
    id: str
    title: str
    status: str
    evidence_paths: tuple[str, ...]


@dataclass(frozen=True)
class SadDocument:
    blocks: tuple[Declaration, ...]
    decisions: tuple[Declaration, ...]
    section_numbers: tuple[int, ...]


def _slug(value: str) -> str:
    text = re.sub(r"<br\s*/?>.*", "", value, flags=re.I)
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text or "unnamed"


def _section_text(markdown: str, number: int) -> str:
    matches = list(_SECTION.finditer(markdown))
    for index, match in enumerate(matches):
        if int(match.group("number")) != number:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        return markdown[match.end() : end]
    return ""


def evidence_paths(text: str) -> tuple[str, ...]:
    candidates: list[str] = []
    candidates.extend(
        match.group("target").strip().replace("\\", "/")
        for match in _MARKDOWN_LINK.finditer(text)
        if "://" not in match.group("target")
    )
    for match in _CODE.finditer(text):
        value = match.group("value").strip().replace("\\", "/")
        if "/" in value or "." in value:
            candidates.append(value)
    candidates.extend(
        match.group("path").strip().replace("\\", "/")
        for match in _PATHISH.finditer(text)
    )
    return tuple(dict.fromkeys(candidates))


def _parse_blocks(section: str) -> tuple[Declaration, ...]:
    blocks: dict[str, Declaration] = {}
    for match in _TABLE_ROW.finditer(section):
        title = match.group("block").strip()
        path_cell = match.group("path").strip()
        if (
            title.lower() in {"block", "layer", "artifact", "area", "mvp wave"}
            or path_cell.lower()
            in {
                "path",
                "location",
                "primary artifact",
                "source",
                "implementation",
                "canonical evidence",
                "protects",
            }
            or set(title) == {"-"}
            or set(path_cell) == {"-"}
        ):
            continue
        block_id = f"B-{_slug(title)}"
        blocks[block_id] = Declaration(
            id=block_id,
            title=title,
            status="Implemented",
            evidence_paths=evidence_paths(path_cell),
        )
    for match in _MERMAID_NODE.finditer(section):
        title = match.group("label").strip()
        block_id = f"B-{_slug(title)}"
        blocks.setdefault(
            block_id,
            Declaration(
                id=block_id,
                title=title,
                status="Implemented",
                evidence_paths=evidence_paths(title),
            ),
        )
    return tuple(blocks[key] for key in sorted(blocks))


def parse_sad(markdown: str) -> SadDocument:
    sections = tuple(
        sorted({int(match.group("number")) for match in _SECTION.finditer(markdown)})
    )
    blocks = _parse_blocks(_section_text(markdown, 5))
    decisions: list[Declaration] = []
    decision_section = _section_text(markdown, 9)
    for match in _DECISION.finditer(decision_section):
        body = match.group("body")
        status_match = _STATUS.search(body)
        decisions.append(
            Declaration(
                id=match.group("id"),
                title=match.group("title").strip(),
                status=(
                    status_match.group("status").strip()
                    if status_match
                    else "Unknown"
                ),
                evidence_paths=evidence_paths(body),
            )
        )
    decisions.sort(key=lambda item: item.id)
    return SadDocument(
        blocks=blocks,
        decisions=tuple(decisions),
        section_numbers=sections,
    )
