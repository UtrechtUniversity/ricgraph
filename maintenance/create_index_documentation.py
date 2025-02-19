# ############################################################
# Perplexity.ai has generated this script on October 18, 2024.
# It creates the index for the Ricgraph documentation in a file.
#
# Modified slightly by Rik D.T. Janssen, October 2024.
# Note that the script does a chdir in main().
# ############################################################

import os
import re
from collections import defaultdict
from urllib.parse import quote

index_file = 'docs/ricgraph_index_documentation.md'


def sanitize_filename(filename):
    return quote(filename)


def sanitize_anchor(text):
    # Remove any non-alphanumeric characters (except hyphen and underscore)
    # and convert spaces to hyphens
    return re.sub(r'[^\w\-]', '', text.lower().replace(' ', '-'))


def extract_headings(file_path):
    headings = []
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        pattern = r'^(#{1,6})\s+(.+)$'
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            level = len(match.group(1))
            text = match.group(2)
            headings.append((text, level, os.path.relpath(file_path)))
    return headings


def generate_sorted_index():
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
    
    # Sort headings alphabetically
    all_headings.sort(key=lambda x: x[0].lower())
    
    # Group headings by first letter
    grouped_headings = defaultdict(list)
    for text, level, file_path in all_headings:
        first_letter = text[0].upper()
        grouped_headings[first_letter].append((text, level, file_path))
    
    # Generate sorted index
    index = ["# Index Ricgraph documentation\n"]
    index.append(f"This index has been generated automatically.\n")
    for letter in sorted(grouped_headings.keys()):
        # index.append(f"\n## {letter}\n")
        index.append(f"\n__{letter}__\n\n")
        for text, level, file_path in grouped_headings[letter]:
            sanitized_file_path = sanitize_filename(file_path)
            sanitized_anchor = sanitize_anchor(text)
            # RDTJ Oct. 18, 2024, hack.
            # index.append(f"- [{text}]({sanitized_file_path}#{sanitized_anchor})\n")
            index.append(f"- [{text}](../{sanitized_file_path}#{sanitized_anchor})\n")
    
    return ''.join(index)


def write_index(index):
    with open(index_file, 'w', encoding='utf-8') as file:
        file.write(index)
    print(f"Index has been written to {index_file}")


if __name__ == "__main__":
    os.chdir('..')
    sorted_index = generate_sorted_index()
    write_index(sorted_index)
