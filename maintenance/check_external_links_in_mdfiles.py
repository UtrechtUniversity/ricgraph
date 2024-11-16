# ############################################################
# Perplexity.ai has generated this script on October 10, 2024.
# It checks for broken external links in .md files.
#
# Modified slightly by Rik D.T. Janssen, October 2024.
# ############################################################

import re
import requests
from pathlib import Path

ROOT_PATH = '..'

def check_links(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Extract external URLs from markdown links
    urls = re.findall(r'\[.*?\]\((http[s]?://\S+)\)', content)

    for url in urls:
        try:
            response = requests.head(url, allow_redirects=True, timeout=5)
            # Check if the response indicates a potential Cloudflare block or valid response
            if response.status_code == 403 or response.status_code == 1020:
                print(f"Ignoring potential Cloudflare block for: {url} - Status: {response.status_code}")
            elif response.status_code >= 400:
                print(f"Broken link: {url} - Status: {response.status_code}")
            #else:
            #    print(f"Valid link: {url} - Status: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error checking: {url} - Exception: {str(e)}")

if __name__ == "__main__":
    markdown_files = Path(ROOT_PATH).rglob('*.md')
    for file in markdown_files:
        print("")
        print(f"Checking links in {file}...")
        check_links(file)

