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
# This script simplifies running Ricgraph harvest scripts by 
# calling a bash script that is a wrapper around these harvest scripts.
# This script harvests various UU sources.
# Compared to multiple_harvest_organization.sh, it creates a copy of it, 
# inserts the python script to harvest the UU staff pages in that copy, 
# and then runs that copy bash script.
# This is done to prevent code duplication.
#
# You may want to start this script as follows:
# [name of this script] | tee output.txt
# In this case, output is written both to the terminal and to
# file 'output.txt'.
# Or use the Makefile and type:
# make bash_script=harvest_multiple_sources/multiple_harvest_uu.sh run_bash_script
#
# Original version Rik D.T. Janssen, April 2025.
#
# ########################################################################


exit_on_error() {
  exit_code=$1
  if [ "$exit_code" != "0" ] ; then
    echo ""
    echo "$0: an error occurred in a previous script."
    echo "Read above for more information, status: '$exit_code'. Exiting."
    echo ""
    exit "$exit_code"
  fi
}


insert_uuharvest_in_multiple_harvest_organization_script() {
  cp -f multiple_harvest_organization.sh $multiple_harvest_script_with_uustaff

  # Insert a message that it is a generated script.
  sed -i 's|#!/bin/bash|#!/bin/bash\
#\
# NOTE: THIS IS A GENERATED FILE.\
# It is created by script multiple_harvest_uu.sh.\
# You can remove it at will, it will be recreated by that script.\
# Also, do not modify it, since any changes will be overwritten.\
#|g' $multiple_harvest_script_with_uustaff

  # Insert harvest of UU staff pages in the multiple_harvest_organization.sh
  # script, after the harvest of Pure.
  sed -i ':a;N;$!ba;s|# ##### #### ### ##|echo "Harvesting UU staff pages."\
PYTHONPATH=$python_path $python_cmd harvest_uustaffpages_to_ricgraph.py --empty_ricgraph no\
exit_code=$?\
if [ "$exit_code" = "0" ] ; then\
  echo "Done with harvesting UU staff pages."\
else\
  echo "--> $0: error while harvesting UU staff pages: '\''$exit_code'\''."\
  exit $exit_code\
fi|g' $multiple_harvest_script_with_uustaff
}


echo "This script harvests a number of sources for Ricgraph from the UU."

multiple_harvest_script_with_uustaff=multiple_harvest_uu_uustaff_generated.sh

insert_uuharvest_in_multiple_harvest_organization_script
exit_on_error $?

./$multiple_harvest_script_with_uustaff --organization UU --empty_ricgraph yes
exit_on_error $?
