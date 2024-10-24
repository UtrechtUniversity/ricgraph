# ############################################################
# Perplexity.ai has generated this script on October 10, 2024.
# It checks for broken internal links in .md files.
# But it does not check links to anchors correctly.
# This is a future extension.
#
# Modified slightly by Rik D.T. Janssen, October 2024.
# ############################################################

import os
import re
from pathlib import Path

ROOT_PATH = '..'

def check_md_links(repo_path):
    md_files = list(Path(repo_path).rglob('*.md'))
    md_file_paths = {file.resolve().as_posix() for file in md_files}

    broken_links = []

    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as file:
            content = file.readlines()

        for line_num, line in enumerate(content, 1):
            links = re.findall(r'\[.*?\]\((.*?\.md)\)', line)
            
            for link in links:
                if link.startswith('http'):
                    continue  # Skip external links

                linked_file_path = (md_file.parent / link).resolve().as_posix()

                if linked_file_path not in md_file_paths:
                    broken_links.append((md_file.as_posix(), link, line_num))

    return broken_links

if __name__ == "__main__":
    repo_path = ROOT_PATH
    # repo_path = os.getcwd()

    broken_links = check_md_links(repo_path)

    if broken_links:
        print("Broken links found:")
        for file_path, link, line_number in broken_links:
            print(f"In {file_path} (line {line_number}): {link}")
    else:
        print("No broken links found between .md files.")

    print("Note that this script does not test for missing anchors yet.")

