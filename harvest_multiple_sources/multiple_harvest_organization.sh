#!/bin/bash
# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License, Copyright (c) 2025 - 2026 Rik D.T. Janssen
#
# ########################################################################
#
# This bash script is a wrapper around the Ricgraph harvest scripts.
# For command line options, read the comments in file
# ../library/get_cmdline_args.sh.
# This script harvests the following sources for Ricgraph:
# - Pure, OpenAlex, and Research Software Directory;
# - Yoda (but only if there is a set name for Yoda in ricgraph.ini);
# - UU staff pages (but only if organization is UU and you have
#   the correct settings in ricgraph.ini).
#
# A best practise is to start the harvest with that harvest script of which
# you expect the most data.
#
# You can run this script as follows:
# - In directory .../ricgraph:
#   make run_bash_script bash_script=harvest_multiple_sources/multiple_harvest_organization.sh \
#    cmd_args="--organization UU --empty_ricgraph yes"
#   This does a 'tee', like in: "[name of this script] | tee output.txt".
#   Output will be written both to the terminal and to file 'output.txt'.
# - In directory .../ricgraph/harvest_multiple_sources:
#   ./multiple_harvest_organization.sh --organization UU --empty_ricgraph yes
#
# Original version Rik D.T. Janssen, April 2025.
# Updated Rik D.T. Janssen, February 2026.
#
# ########################################################################


harvest_pure() {
  echo "Harvesting Pure for organization '$organization', first year: '$year_first', last year: '$year_last'."
  echo "Emptying Ricgraph: '$empty_ricgraph'."
  PYTHONPATH=$python_path $python_cmd harvest_pure_to_ricgraph.py --empty_ricgraph "$empty_ricgraph" --organization "$organization" --harvest_projects no --year_first "$year_first" --year_last "$year_last"
  exit_code=$?
  if [ "$exit_code" = "0" ] ; then
    echo "Done with harvesting Pure-$organization."
  else
    echo "--> $0: error while harvesting Pure-$organization, status: '$exit_code'."
    exit $exit_code
  fi
  echo ""
}


harvest_openalex() {
  echo "Harvesting OpenAlex for organization '$organization', first year: '$year_first', last year: '$year_last'."
  PYTHONPATH=$python_path $python_cmd harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization "$organization" --year_first "$year_first" --year_last "$year_last"
  exit_code=$?
  if [ "$exit_code" = "0" ] ; then
    echo "Done with harvesting OpenAlex-$organization."
  else
    echo "--> $0: error while harvesting OpenAlex-$organization, status: '$exit_code'."
    exit $exit_code
  fi
  echo ""
}


harvest_rsd () {
  echo "Harvesting Research Software Directory for organization '$organization'."
  PYTHONPATH=$python_path $python_cmd harvest_rsd_to_ricgraph.py --empty_ricgraph no --organization "$organization"
  exit_code=$?
  if [ "$exit_code" = "0" ] ; then
    echo "Done with harvesting Research Software Directory-$organization."
  else
    echo "--> $0: error while harvesting Research Software Directory-$organization, status: '$exit_code'."
    exit $exit_code
  fi
  echo ""
}


harvest_yoda() {
  # Now check if this organization has a value for the Yoda set to be harvested.
  # E.g., for UU, this key in ricgraph.ini is called "yoda_set_UU".
  # If the key does not exist, or if it has no value, Yoda is not harvested.
  yoda_set_name=yoda_set_$organization
  if grep -q "^$yoda_set_name" ../ricgraph.ini; then
    value=$(grep "^$yoda_set_name" ../ricgraph.ini | cut -d '=' -f 2 | xargs)
    if [[ -n "$value" ]]; then
      echo "Continuing harvesting organization '$organization': Yoda."
    else
      # The key has no value.
      echo "Skipping harvesting Yoda, no value for Yoda set in ricgraph.ini file."
      echo "This is to be expected if your organization does not use the Yoda data repository."
      echo "Done with harvesting."
      exit 0
    fi
  else
    # The key does not exist.
    echo "Skipping harvesting Yoda, key for Yoda in ricgraph.ini file does not exist."
    echo "This is to be expected if your organization does not use the Yoda data repository."
    echo "Done with harvesting."
    exit 0
  fi

  echo "Harvesting Yoda for organization '$organization'."
  PYTHONPATH=$python_path $python_cmd harvest_yoda_datacite_to_ricgraph.py --empty_ricgraph no --organization "$organization"
  exit_code=$?
  if [ "$exit_code" = "0" ] ; then
    echo "Done with harvesting Yoda-$organization."
  else
    echo "--> $0: error while harvesting Yoda-$organization, status: '$exit_code'."
    exit $exit_code
  fi
  echo ""
}


harvest_uustaffpages() {
  echo "Harvesting UU staff pages."
  PYTHONPATH=$python_path $python_cmd harvest_uustaffpages_to_ricgraph.py --empty_ricgraph no
  exit_code=$?
  if [ "$exit_code" = "0" ] ; then
    echo "Done with harvesting UU staff pages."
  else
    echo "--> $0: error while harvesting UU staff pages, status: '$exit_code'."
    exit $exit_code
  fi
  echo ""
}


echo "This script harvests Pure, OpenAlex, and the Research Software Directory."
echo "It also harvests Yoda if your organization uses it,"
echo "and UU staff pages if your organization is UU."

# The following script returns $python_cmd, $python_path,
# $organization, $empty_ricgraph, $year_first, and $year_last.
source ../library/get_cmdline_args.sh

cd ../harvest || exit 1

harvest_pure

if [ "$organization" = "UU" ] ; then
  harvest_uustaffpages
fi

harvest_openalex

harvest_rsd

harvest_yoda

echo "Done with harvesting."
