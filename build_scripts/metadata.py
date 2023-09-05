from datetime import datetime
import pathlib
import re

description = "A logic gate simulator for linux developed with Gtk and python."
url = "https://github.com/astraldev/GGate"
revision = "stable"
version = '4.0.0'
package = "ggate"
package_name = "GGate"
email = 'ekureedem480@gmail.com'
full_name = 'Ekure Edem'
section = "science"
date = datetime.now()
base_dir = pathlib.Path(__file__).parent.parent
license = f"{base_dir}/COPYING"
day_names = [
    "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"
]
month_names = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]


def _parse_changelog(text):
    changelog_entries = []
    current_entry = None

    for line in text.splitlines():
        line = line.strip()
        # Check if the line matches the date and version pattern
        if re.match(r'\d{4}-\d{2}-\d{2}: version \d+\.\d+(\.\d+(-[a-zA-Z\d]+)?)?$', line):
            if current_entry:
                changelog_entries.append(current_entry)
            date_str, version_str = line.split(': version ')
            date = datetime.strptime(date_str, '%Y-%m-%d')
            current_entry = {
                'date': date.strftime(f"{day_names[date.weekday()]}, %d {month_names[date.month]} %Y %H:%M:%S %z"),
                'version': version_str,
                'changes': []
            }
        elif current_entry and line.startswith('* '):
            current_entry['changes'].append(line[2:])

    if current_entry:
        changelog_entries.append(current_entry)

    return changelog_entries


def get_changelog(file):
    changelog_entries = _parse_changelog(file.read())
    text = f'{package} ({version}{"" if not revision else "-"+revision}) all; urgency=medium\n'
    for entry in changelog_entries:
        for change in entry['changes']:
            text += f"  * {change}\n"
        if version.find('3.') != -1:
            text += f'\n -- {full_name} <{email}>  {entry["date"]}'
        else:
            text += f'\n -- Koichi Akabe <vbkaisetsu@gmail.com>  {entry["date"]}\n'
    return text.strip()


def parse_control_text(control_text: str):
    control_dict = {}
    for line in control_text.splitlines():
        if not line.strip():
            continue  # Skip empty lines
        try:
            key, value = line.split(':', 1)
        except ValueError:
            key = list(control_dict.keys())[-1]
            control_dict[key] += line
            continue
        key = key.strip()
        value = value.strip()
        # Check if we encounter a new section
        control_dict[key] = value
    return control_dict


def split_text_by_length(text, max_length):
    text_chunks = []
    # Split the text into words
    words = text.split()
    # Initialize the current chunk and its length
    current_chunk = ""
    current_length = 0
    for word in words:
        # If adding the current word to the chunk doesn't exceed the maximum length, add it
        if current_length + len(word) + len(current_chunk) <= max_length:
            if current_chunk:
                current_chunk += " "  # Add a space between words if the chunk is not empty
            current_chunk += word
            current_length += len(word)
        else:
            # If adding the word exceeds the maximum length, start a new chunk
            text_chunks.append(current_chunk)
            current_chunk = word
            current_length = len(word)
    # Append the last chunk (if any)
    if current_chunk:
        text_chunks.append(current_chunk)

    return text_chunks

def get_copyright_file(text: str):
    text = text.replace("Source: <url://example.com>", f"Source: {url}.git")
    text = text.replace("Upstream-Contact: <preferred name and address to reach the upstream project>", f"Upstream-Contact: {url}")
    return text

def get_control_file(text):
    key_value_pair = parse_control_text(text)
    key_value_pair["Section"] = "science"
    key_value_pair["Description"] = description
    key_value_pair["Homepage"] = url
    key_value_pair["Architecture"] = "amd64"
    key_value_pair["Build-Depends"] += ", python3-gi, python3-gi-cairo"
    res = ""
    for (key, value) in key_value_pair.items():
        if key == "Package":
            key = f"\n{key}"
        res += f"{key}: "
        split_text = split_text_by_length(value, 150)
        res += split_text[0]
        for text in split_text[1:]:
            res += f"\n  {text}"
        res += "\n"
    return res


parsed_changelog = get_changelog(open(f"{base_dir}/NEWS"))
readme_debian = f"""Package: {package}
Version: {version}
Date: {date}

Description
-----------
{package_name} (fork of GLogic)

A logic gate simulator for linux developed with Gtk and python.

Requirements
------------

This application requires any linux environment on which **GTK4** is installed.

Installation
------------
To install {package_name}, clone the [github repository]({url}) and run `./install.sh`

Features
--------

* Includes Tri State Buffer
* LED and 7 segment for state viewing
* Easy to understand UI and accessible shortcuts
* Contains all logic gates with appropriate diagrams and alternative (IEC, MIL/ANSI)
* Supports Simulation and Timing Diagrams
* Support exporting of drawings and timing diagrams.
* Variable component properties
* Contains all types Flip Flop
* Has display contents like LED, 7 Segments etc
* File handling support

Check out the latest changelog on {package_name} [here.]({url}/blob/main/NEWS) and [future plans]({url}/blob/main/TODO)

Contact
-------
For any issues or questions, please contact the package maintainer at [ekureedem480@gmail.com](mailto:ekureedem480@gmail.com) or file an [issue on github](https://github.com/astraldev/GGate/issues/new)

License
-------
This package is distributed under the GNU General Public License v3.

    -- {full_name} <{email}>  {date}
"""
