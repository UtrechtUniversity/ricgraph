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
# This bash script is a wrapper around the Ricgraph harvest scripts.
# For command line options, read the comments in file
# ../library/get_cmdline_args.sh.
# This script harvests the following sources for Ricgraph:
# - in this script: Pure and OpenAlex;
# - by calling another script: the Research Software Directory
#   and Yoda (but only if there is a set name for Yoda in ricgraph.ini).
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


harvest_pure() {
  echo "Harvesting Pure for organization '$organization', first year: '$year_first', last year: '$year_last'."
  PYTHONPATH=$python_path $python_cmd harvest_pure_to_ricgraph.py --empty_ricgraph "$empty_ricgraph" --organization "$organization" --harvest_projects no --year_first "$year_first" --year_last "$year_last"
  exit_code=$?
  if [ "$exit_code" = "0" ] ; then
    echo "Done with harvesting Pure-$organization."
  else
    echo "--> $0: error while harvesting Pure-$organization, status: '$exit_code'."
    exit $exit_code
  fi
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
}


harvest_rsd_yoda_wrapper() {
  # If 'organization' does not have Yoda, it will not be harvested.
  # Note, we are in directory harvest.
  ../harvest_multiple_sources/multiple_harvest_organization_rsd_yoda.sh --organization "$organization" --empty_ricgraph no
  exit_code=$?
  if [ "$exit_code" != "0" ] ; then
    echo "--> $0: error while harvesting RSD and Yoda for $organization, status: '$exit_code'."
    exit $exit_code
  fi
}


echo "This script harvests Pure, OpenAlex, the Research Software Directory, and Yoda."

# The following script returns $python_cmd, $python_path,
# $organization, and $empty_ricgraph.
source ../library/get_cmdline_args.sh

cd ../harvest || exit 1

harvest_pure

# Do not remove or modify the next line, file multiple_harvest_uu.sh may modify it.
# ##### #### ### ##
# Do not remove or modify the line above.

harvest_openalex

harvest_rsd_yoda_wrapper
