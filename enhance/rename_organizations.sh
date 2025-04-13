#!/bin/bash
# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License, Copyright (c) 2025 Rik D.T. Janssen
#
# ########################################################################
#
# This script renames organizations, using a file containing
# the (sub-)organizations to rename.
# It is a wrapper for the python script rename_orgs.py.
# For command line options, read the comments in file
# ../library/get_cmdline_args.sh.
#
# Original version Rik D.T. Janssen, April 2025.
#
# ########################################################################


rename_organizations () {
  rename_orgs_file=orgs_to_rename_$organization.csv
  echo "Batch renaming organizations for organization '$organization', using"
  echo "file '$rename_orgs_file' that tells what to rename."

  PYTHONPATH=$python_path $python_cmd ./rename_orgs.py --filename "$rename_orgs_file" --are_you_sure yes
  exit_code=$?
  if [ "$exit_code" = "0" ] ; then
    echo "Done with renaming organizations for organization $organization."
  else
    echo "--> $0: error while renaming organizations for organization $organization, status: '$exit_code'."
    exit $exit_code
  fi
}


echo "This script renames organizations based on a file."

# The following script returns $python_cmd, $python_path,
# $organization, and $empty_ricgraph.
source ../library/get_cmdline_args.sh

rename_organizations

exit 0
