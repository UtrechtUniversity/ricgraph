#!/bin/bash
# ###############################################################
# Script to create both the toc and the index documentation
# files.
#
# Rik D.T. Janssen, November 2025.
# ###############################################################

# We need to run twice for being sure new sections are also in the index.
../venv/bin/python3 create_toc_documentation.py
../venv/bin/python3 create_index_documentation.py
../venv/bin/python3 create_toc_documentation.py
../venv/bin/python3 create_index_documentation.py

