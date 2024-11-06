#!/bin/bash
# ###############################################################
# Script to propagate a new version number to various files.
#
# Rik D.T. Janssen, November 2024.
# ###############################################################

expected_run_directory="maintenance_scripts"

echo "This script propagates a new version number to a number of files."
if echo -n "Are you sure you want to proceed? [y/N] " && read ans && ! [ "${ans:-N}" = "y" ]; then
    echo "Script aborted."
    echo ""
    exit 1
fi

current_dir=$(pwd)
dir_name=$(basename "$current_dir")
if [ "$dir_name" != "$expected_run_directory" ]; then
    echo ""
    echo "Error, this script is expected to run from directory \"$expected_run_directory\","
    echo "but it is run from directory \"$current_dir\"."
    echo "Please change directory. Exiting."
    echo ""
    exit 1
fi

# Get the new version from the user
echo ""
read -p "Specify the new version number: " new_version
if [ -z "$new_version" ]; then
    echo "You have not specified a version number, exiting."
    echo ""
    exit 1
else
    echo "The new version number is: $new_version."
    echo ""
fi

# Possible future extension:
# Read the new version from an environment variable or from a VERSION file
# NEW_VERSION=${1:-$(cat VERSION)}

cd ..

# Possible future extension:
# Update setup.py
#echo "Updating setup.py..."
#sed -i "s/version='.*'/version='${new_version}'/" setup.py

# Update ricgraph/__init__.py
echo "Updating ricgraph/__init__.py..."
sed -i "s/__version__ = '.*'/__version__ = '${new_version}'/" ricgraph/__init__.py

# Update CITATION.cff
current_date=$(date '+%Y-%m-%d')
echo "Updating CITATION.cff..."
sed -i "s/^version: .*/version: \"${new_version}\"/" CITATION.cff
sed -i "s/date-released: .*/date-released: \"${current_date}\"/" CITATION.cff

# Update Makefile
echo "Updating Makefile..."
sed -i "s/ricgraph_version := .*/ricgraph_version := ${new_version}/" Makefile

echo "Done."
