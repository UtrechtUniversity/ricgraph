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
# This script harvests two sources for Ricgraph:
# Research Software Directory and Yoda.
#
# You may want to start this script as follows:
# [name of this script] | tee output.txt
# In this case, output is written both to the terminal and to 
# file 'output.txt'.
#
# Original version Rik D.T. Janssen, April 2025.
#
# ########################################################################

# The following script returns $python_cmd, $python_path,
# $organization, and $empty_ricgraph.
source ./get_cmdline_args.sh

cd ../harvest || exit 1

echo "Batch harvesting organization '$organization': Research Software Directory."

echo "Harvesting Research Software Directory for organization '$organization'."
PYTHONPATH=$python_path $python_cmd harvest_rsd_to_ricgraph.py --empty_ricgraph "$empty_ricgraph" --organization "$organization"
exit_code=$?
if [ "$exit_code" = "0" ] ; then
  echo "Done with harvesting Research Software Directory-$organization."
else
  echo "===>>> $0: error while harvesting Research Software Directory-$organization, status: '$exit_code'."
  exit $exit_code
fi

# Now check if this organization has a value for the Yoda set to be harvested.
# E.g., for UU, this key in ricgraph.ini is called "yoda_set_UU".
# If the key does not exist, or if it has no value, Yoda is not harvested.
yoda_set_name=yoda_set_$organization
if grep -q "^$yoda_set_name" ../ricgraph.ini; then
  value=$(grep "^$yoda_set_name" ../ricgraph.ini | cut -d '=' -f 2 | xargs)
  if [[ -n "$value" ]]; then
    echo "Batch harvesting organization '$organization': Yoda."
  else
    # Ready with harvesting, key has no value.
    echo "Done with harvesting."
    exit 0
  fi
else
  # Ready with harvesting, key does not exist.
  echo "Done with harvesting."
  exit 0
fi

echo "Harvesting Yoda for organization '$organization'."
PYTHONPATH=$python_path $python_cmd harvest_yoda_datacite_to_ricgraph.py --empty_ricgraph no --organization "$organization"
exit_code=$?
if [ "$exit_code" = "0" ] ; then
  echo "Done with harvesting Yoda-$organization."
else
  echo "===>>> $0: error while harvesting Yoda-$organization, status: '$exit_code'."
  exit $exit_code
fi

echo "Done with harvesting."
