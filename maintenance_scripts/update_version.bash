#!/bin/bash
# ###############################################################
# Script to propagate a new version number to various files.
#
# Rik D.T. Janssen, November 2024.
# ###############################################################

# Future extension:
# Read the new version from an environment variable or from a VERSION file
# NEW_VERSION=${1:-$(cat VERSION)}

# Get the new version from the user
read -p "Specify the new version number: " new_version
if [ -z "$new_version" ]; then
    echo "You have not specified a version number, exiting."
    exit 1
else
    echo "The new version number is: $new_version."
fi

cd ..
current_date=$(date '+%Y-%m-%d')

# Future extension:
# Update setup.py
#echo "Updating setup.py..."
#sed -i "s/version='.*'/version='${new_version}'/" setup.py

# Update ricgraph/__init__.py
echo "Updating ricgraph/__init__.py..."
sed -i "s/__version__ = '.*'/__version__ = '${new_version}'/" ricgraph/__init__.py

# Update CITATION.cff
echo "Updating CITATION.cff..."
sed -i "s/^version: .*/version: \"${new_version}\"/" CITATION.cff
sed -i "s/date-released: .*/date-released: \"${current_date}\"/" CITATION.cff

# Update Makefile
echo "Updating Makefile..."
sed -i "s/ricgraph_version := .*/ricgraph_version := ${new_version}/" Makefile

echo "Done."
