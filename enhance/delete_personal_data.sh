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

  PYTHONPATH=$python_path $python_cmd ./delete_pers_data.py --filename "$pers_to_delete_file" --are_you_sure yes
  exit_code=$?
  if [ "$exit_code" = "0" ] ; then
    echo "Done with deleting personal data for organization $organization."
  else
    echo "--> $0: error while deleting personal data for organization $organization, status: '$exit_code'."
    exit $exit_code
  fi
}


echo "This script deletes personal data based on a file."
echo "To run it, you should at least specify '--organization'"
echo "and '--are_you_sure yes'."
echo ""

# The following script returns $python_cmd, $python_path,
# $organization, and $are_you_sure.
source ../library/get_cmdline_args.sh

if [ "$are_you_sure" != "yes" ]; then
  echo "You have not specified the command line"
  echo "parameter '--are_you_sure yes', or you have set it to 'no'."
  echo "You need to set it to 'yes', otherwise this script will not run."
  exit 1
fi

delete_personal_data
