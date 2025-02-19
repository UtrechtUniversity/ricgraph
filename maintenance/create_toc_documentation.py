# ############################################################
# Perplexity.ai has generated this script on October 18, 2024.
# It creates the table of contents for the Ricgraph documentation.
#
# Modified slightly by Rik D.T. Janssen, October 2024.
# Note that the script does a chdir in main().
# ############################################################

import os
import re
import urllib.parse

toc_file = 'docs/ricgraph_toc_documentation.md'


def extract_headings(file_path):
    headings = []
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        pattern = r'^(#{1,6})\s+(.+)$'
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            level = len(match.group(1))
            text = match.group(2)
            headings.append((level, text, os.path.relpath(file_path)))
    return headings


def generate_toc():
    all_headings = []
    
    # Process README.md in the root
    if os.path.exists('README.md'):
        all_headings.extend(extract_headings('README.md'))
    
    # Process .md files in the docs directory
    if os.path.exists('docs'):
        for root, _, files in os.walk('docs'):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    all_headings.extend(extract_headings(file_path))
    
    # Generate TOC
    toc = ["# Table of contents Ricgraph documentation\n"]
    toc.append(f"This table of contents has been generated automatically.\n\n")
    for level, text, file_path in all_headings:
        indent = "  " * (level - 1)
        link = create_github_anchor(text)
        encoded_file_path = urllib.parse.quote(file_path)
        # RDTJ Oct. 18, 2024, hack.
        # toc.append(f"{indent}- [{text}]({encoded_file_path}#{link})\n")
        toc.append(f"{indent}- [{text}](../{encoded_file_path}#{link})\n")
    
    return ''.join(toc)


def create_github_anchor(text):
    # Convert to lowercase
    anchor = text.lower()
    # Replace spaces with hyphens
    anchor = anchor.replace(' ', '-')
    # Remove any character that is not alphanumeric, hyphen, or underscore
    anchor = re.sub(r'[^\w-]', '', anchor)
    return anchor


def write_toc(toc):
    with open(toc_file, 'w', encoding='utf-8') as file:
        file.write(toc)
    print(f"Table of Contents has been written to {toc_file}")


if __name__ == "__main__":
    os.chdir('..')
    maintoc = generate_toc()
    write_toc(maintoc)
