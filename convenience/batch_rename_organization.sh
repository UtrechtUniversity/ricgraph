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
#
# Original version Rik D.T. Janssen, April 2025.
#
# ########################################################################

# The following script returns $python_cmd, $python_path,
# $organization, and $empty_ricgraph.
source ./get_cmdline_args.sh

rename_orgs_file=$(pwd)/orgs_to_rename_$organization.csv
echo "Batch renaming organizations for organization '$organization', using"
echo "file '$rename_orgs_file'"
echo "that tells what to rename."

PYTHONPATH=$python_path $python_cmd ../enhance/rename_orgs.py --filename "$rename_orgs_file" --are_you_sure yes
exit_code=$?
if [ "$exit_code" = "0" ] ; then
  echo "Done with renaming organizations for organization $organization."
else
  echo "===>>> $0: error while renaming organizations for organization $organization, status: '$exit_code'."
  exit $exit_code
fi
