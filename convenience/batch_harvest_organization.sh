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
# This script harvests three sources for Ricgraph:
# Pure, OpenAlex, and the Research Software Directory.
# If there is a set name for Yoda in ricgraph.ini, Yoda
# will also be harvested.
#
# A best practise is to start the harvest with that harvest script of which
# you expect the most data.
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

echo "Batch harvesting organization '$organization': Pure and OpenAlex."

echo "Harvesting Pure for organization '$organization'."
PYTHONPATH=$python_path $python_cmd harvest_pure_to_ricgraph.py --empty_ricgraph "$empty_ricgraph" --organization "$organization" --harvest_projects yes
exit_code=$?
if [ "$exit_code" = "0" ] ; then
  echo "Done with harvesting Pure-$organization."
else
  echo "===>>> $0: error while harvesting Pure-$organization, status: '$exit_code'."
  exit $exit_code
fi

# Do not remove or modify the next line, file batch_harvest_uu.sh may modify it.
# ##### #### ### ##
# Do not remove or modify the line above.

echo "Harvesting OpenAlex for organization '$organization'."
PYTHONPATH=$python_path $python_cmd harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization "$organization"
exit_code=$?
if [ "$exit_code" = "0" ] ; then
  echo "Done with harvesting OpenAlex-$organization."
else
  echo "===>>> $0: error while harvesting OpenAlex-$organization, status: '$exit_code'."
  exit $exit_code
fi

# If 'organization' does not have Yoda, it will not be harvested.
../convenience/batch_harvest_organization_rsd_yoda.sh --organization "$organization" --empty_ricgraph no
