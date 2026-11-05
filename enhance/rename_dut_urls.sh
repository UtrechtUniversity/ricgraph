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
# This script renames URLs in the DUT harvest.
# It is a wrapper for the python script rename_dut_urls.py.
# For command line options, read the comments in file
# ../library/get_cmdline_args.sh.
#
# Original version Rik D.T. Janssen, November 2026.
#
# ########################################################################


rename_dut_urls () {
  echo "Renaming URLs for organization DUT in Ricgraph."

  PYTHONPATH=$python_path $python_cmd ./rename_dut_urls.py --are_you_sure yes
  exit_code=$?
  if [ "$exit_code" = "0" ] ; then
    echo "Done with renaming URLs for organization DUT in Ricgraph."
  else
    echo "--> $0: error while renaming URLs for organization DUT in Ricgraph, status: '$exit_code'."
    exit $exit_code
  fi
}


echo "This script renames URLs for organization DUT in Ricgraph."
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

rename_dut_urls
