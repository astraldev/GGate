#!/usr/bin/env python3
# Generate multi-entry debian/changelog from meson.build version and CHANGELOG.md.
import os
import re
import sys
import datetime
import email.utils

VERSION_PATTERNS = [
    re.compile(r"[Bb]ump version to (\d+\.\d+(?:\.\d+)?)"),
    re.compile(r"[Rr]elease version (\d+\.\d+(?:\.\d+)?)"),
    re.compile(r"[Bb]ump to (\d+\.\d+(?:\.\d+)?)"),
    re.compile(r"(?:^|\s)[vV](\d+\.\d+(?:\.\d+)?)")
]

class Section:
    def __init__(self, date_str, author):
        # Section attributes
        self.date_str = date_str
        self.author = author
        self.bullets = []
        self.explicit_version = None
        self.version = None

def get_meson_version(meson_path):
    # Extract version from meson.build
    with open(meson_path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"version\s*:\s*'([0-9][^']*)'", content)
    if match:
        return match.group(1)
    return "0.0.0"

def extract_version(line):
    # Find explicit version in a line
    for pattern in VERSION_PATTERNS:
        match = pattern.search(line)
        if match:
            return match.group(1)
    return None

def parse_header(line):
    # Parse header fields
    content = line[2:].strip()
    parts = content.split(None, 1)
    if len(parts) < 2:
        return None, None
    return parts[0], parts[1].strip()

def parse_changelog(changelog_path):
    # Parse changelog sections
    sections = []
    current_section = None
    with open(changelog_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("## "):
                date_str, author = parse_header(line)
                if date_str:
                    current_section = Section(date_str, author)
                    sections.append(current_section)
            elif current_section is not None:
                stripped = line.strip()
                if stripped:
                    current_section.bullets.append(stripped)
                    ver = extract_version(stripped)
                    if ver and current_section.explicit_version is None:
                        current_section.explicit_version = ver
    return sections

def resolve_versions(sections, meson_version):
    # Assign versions to stanzas
    if not sections:
        return
    
    sections[0].version = meson_version
    for i in range(1, len(sections)):
        if sections[i].explicit_version:
            sections[i].version = sections[i].explicit_version
            
    is_anchor = [s.version is not None for s in sections]
    
    for i in range(len(sections)):
        if not is_anchor[i]:
            ref_ver = "0"
            for j in range(i - 1, -1, -1):
                if is_anchor[j]:
                    ref_ver = sections[j].version
                    break
            
            a = i
            while a > 0 and not is_anchor[a - 1]:
                a -= 1
            b = i
            while b < len(sections) - 1 and not is_anchor[b + 1]:
                b += 1
                
            n_val = b - i + 1
            sections[i].version = f"{ref_ver}~dev{n_val}"

def format_rfc2822_date(date_str):
    # Format date as RFC-2822
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").astimezone()
        return email.utils.format_datetime(dt)
    except Exception:
        return email.utils.formatdate(localtime=True)

def generate_changelog(sections):
    # Print formatted stanzas to stdout
    for i, sec in enumerate(sections):
        rfc_date = format_rfc2822_date(sec.date_str)
        print(f"ggate ({sec.version}-1) unstable; urgency=medium\n")
        for bullet in sec.bullets:
            print(f"  * {bullet}")
        print(f"\n -- {sec.author}  {rfc_date}")
        if i < len(sections) - 1:
            print()

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    meson_path = os.path.join(root, "meson.build")
    changelog_path = os.path.join(root, "CHANGELOG.md")
    
    meson_version = get_meson_version(meson_path)
    sections = parse_changelog(changelog_path)
    resolve_versions(sections, meson_version)
    generate_changelog(sections)

if __name__ == "__main__":
    main()
