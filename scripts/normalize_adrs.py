#!/usr/bin/env python3
"""Normalize ADR markdown files in docs/ADR to canonical template order.

This script reorders and inserts missing template sections for each
markdown file under docs/ADR. It preserves section contents where
possible and inserts sensible defaults for missing fields.

Usage: .venv\Scripts\python.exe scripts\normalize_adrs.py
"""
from pathlib import Path
import re
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
ADR_DIR = ROOT / 'docs' / 'ADR'
TEMPLATE = [
    'Status',
    'Date',
    'Intellectual property rights',
    'Privacy and confidentiality',
    'Context',
    'Decision',
    'Consequences',
    'Testing',
    'References',
]

DEFAULT_IP = 'Repository authorship and licensing: see project LICENSE; contact maintainers for clarification.'
DEFAULT_PRIVACY = 'This ADR contains no personal data. Implementers must follow the repository privacy and confidentiality policies, avoid committing secrets, and document any sensitive data handling in implementation steps.'

hdr_re = re.compile(r'(?m)^##\s+(.+)$')


def read_sections(text):
    # Find title
    title = None
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith('# '):
            title = ln.strip()
            break
    # Find headers and their positions
    sections = {}
    matches = list(hdr_re.finditer(text))
    if matches:
        for idx, m in enumerate(matches):
            name = m.group(1).strip()
            start = m.end()
            end = matches[idx+1].start() if idx+1 < len(matches) else len(text)
            content = text[start:end].strip()
            sections[name] = content
    else:
        # No '##' headers - attempt to sniff inline fields
        body = text
        # inline status/date lines like 'Date: 2026-03-30' or 'Status: Accepted'
        for field in ['Status', 'Date']:
            m = re.search(r'(?m)^' + field + r':\s*(.+)$', text)
            if m:
                sections[field] = m.group(1).strip()
        # remaining body as Context
        sections['Context'] = body.strip()
    return title or '', sections


def build_content(title, sections):
    out = []
    if title:
        out.append(title)
        out.append('')
    today = date.today().isoformat()
    for sec in TEMPLATE:
        out.append(f'## {sec}')
        val = sections.get(sec)
        if not val:
            if sec == 'Status':
                val = sections.get('Status', 'Proposed')
            elif sec == 'Date':
                val = sections.get('Date', today)
            elif sec == 'Intellectual property rights':
                val = sections.get('Intellectual property rights', DEFAULT_IP)
            elif sec == 'Privacy and confidentiality':
                val = sections.get('Privacy and confidentiality', DEFAULT_PRIVACY)
            elif sec == 'References':
                # Collect migrated lines if any
                migrated = sections.get('Migrated from') or sections.get('Migrated') or ''
                if migrated:
                    val = migrated
                else:
                    # If file had a bottom '---' migration note, try to capture
                    val = sections.get('References', '')
            else:
                val = sections.get(sec, '')
        out.append(val.strip())
        out.append('')
    return '\n'.join(out).rstrip() + '\n'


def normalize_file(path: Path):
    text = path.read_text(encoding='utf-8')
    title, sections = read_sections(text)
    # Attempt to capture 'Migrated from' lines into sections
    m = re.search(r'(?ms)^---\s*(.*?)\n\Z', text)
    if m:
        tail = m.group(1).strip()
        if 'Migrated from' in tail or 'Automated migration' in tail:
            sections.setdefault('References', tail)
    # Also capture explicit 'Migrated from' lines elsewhere
    mig = re.search(r'(?m)Migrated from\s*\n?`?([^`\n]+)`?', text)
    if mig:
        sections.setdefault('References', mig.group(1).strip())
    new = build_content(title, sections)
    if new != text:
        backup = path.with_suffix(path.suffix + '.bak')
        path.rename(backup)
        path.write_text(new, encoding='utf-8')
        return True, str(backup.name)
    return False, ''


def main():
    adr_files = sorted(ADR_DIR.glob('*.md'))
    modified = []
    for p in adr_files:
        changed, bak = normalize_file(p)
        if changed:
            modified.append((p.name, bak))
    print('Normalization complete.')
    if modified:
        print('Modified files:')
        for name, bak in modified:
            print(f'- {name} (backup created: {bak})')
    else:
        print('No changes required; all ADRs match template order.')


if __name__ == '__main__':
    main()
