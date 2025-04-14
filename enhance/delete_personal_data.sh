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
# This script deletes all personal data of one or more persons from Ricgraph.
# These persons are listed in a csv file.
# It is a wrapper for the python script delete_pers_data.py.
# For command line options, read the comments in file
# ../library/get_cmdline_args.sh.
#
# Original version Rik D.T. Janssen, April 2025.
#
# ########################################################################


delete_personal_data () {
  pers_to_delete_file=pers_to_delete_$organization.csv
  echo "Batch deleting personal data for organization '$organization', using"
  echo "file '$pers_to_delete_file' that tells what personal data to rename."

  PYTHONPATH=$python_path $python_cmd ./rename_orgs.py --filename "$pers_to_delete_file" --are_you_sure yes
  exit_code=$?
  if [ "$exit_code" = "0" ] ; then
    echo "Done with deleting personal data for organization $organization."
  else
    echo "--> $0: error while deleting personal data for organization $organization, status: '$exit_code'."
    exit $exit_code
  fi
}


echo "This script delete personal data based on a file."

# The following script returns $python_cmd, $python_path,
# $organization, and $empty_ricgraph.
source ../library/get_cmdline_args.sh

delete_personal_data
