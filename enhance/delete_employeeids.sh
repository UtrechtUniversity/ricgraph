#!/bin/bash
# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License, Copyright (c) 2026 Rik D.T. Janssen
#
# ########################################################################
#
# This script deletes all EMPLOYEE_ID nodes from Ricgraph.
# It is a wrapper for the python script delete_emplids.py.
# For command line options, read the comments in file
# ../library/get_cmdline_args.sh.
#
# Original version Rik D.T. Janssen, July 2026.
#
# ########################################################################


delete_employeeids () {
  echo "Deleting all EMPLOYEE_ID nodes from Ricgraph."

  PYTHONPATH=$python_path $python_cmd ./delete_emplids.py --are_you_sure yes
  exit_code=$?
  if [ "$exit_code" = "0" ] ; then
    echo "Done with deleting all EMPLOYEE_ID nodes from Ricgraph."
  else
    echo "--> $0: error while deleting all EMPLOYEE_ID nodes from Ricgraph, status: '$exit_code'."
    exit $exit_code
  fi
}


echo "This script deletes all EMPLOYEE_ID nodes from Ricgraph."
echo "To run it, you should at least specify '--are_you_sure yes'."
echo ""

# The following script returns $python_cmd, $python_path,
# $organization, and $are_you_sure.
# We need to specify '--organization' otherwise the script exits.
# If we do this, we also need to pass the parameters to this script with $@.
source ../library/get_cmdline_args.sh "$@" --organization DOES_NOT_MATTER

if [ "$are_you_sure" != "yes" ]; then
  echo "You have not specified the command line"
  echo "parameter '--are_you_sure yes', or you have set it to 'no'."
  echo "You need to set it to 'yes', otherwise this script will not run."
  exit 1
fi

delete_employeeids
