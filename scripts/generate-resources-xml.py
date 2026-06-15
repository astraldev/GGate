#!/usr/bin/env python3
import os
import glob
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Generate GResource XML file dynamically")
    parser.add_argument("--prefix", required=True, help="GResource prefix")
    parser.add_argument("--output", required=True, help="Output XML file path")
    parser.add_argument("--source-dir", required=True, help="Source data/images directory")
    args = parser.parse_args()

    # Base directory is data/images
    images_dir = os.path.abspath(args.source_dir)
    # Project data dir is parent of images_dir (which is data/)
    data_dir = os.path.dirname(images_dir)

    comp_files = sorted(glob.glob(os.path.join(images_dir, "components", "*.svg")))
    act_files = sorted(glob.glob(os.path.join(images_dir, "actions", "*.svg")))
    theme_files = sorted(glob.glob(os.path.join(data_dir, "themes", "*.json")))

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<gresources>')
    lines.append(f'  <gresource prefix="{args.prefix}">')

    # Add components and actions (relative to images_dir)
    for f in comp_files:
        rel = os.path.relpath(f, images_dir).replace("\\", "/")
        lines.append(f'    <file preprocess="xml-stripblanks">{rel}</file>')
    for f in act_files:
        rel = os.path.relpath(f, images_dir).replace("\\", "/")
        lines.append(f'    <file preprocess="xml-stripblanks">{rel}</file>')

    # Add themes (alias is basename, path relative to images_dir)
    for f in theme_files:
        rel = os.path.relpath(f, images_dir).replace("\\", "/")
        basename = os.path.basename(f)
        lines.append(f'    <file alias="themes/{basename}">{rel}</file>')

    lines.append('  </gresource>')
    lines.append('</gresources>')

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

if __name__ == "__main__":
    main()
