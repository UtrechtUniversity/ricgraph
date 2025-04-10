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
# This script harvests UU sources.
#
# You may want to start this script as follows:
# [name of this script] | tee output.txt
# In this case, output is written both to the terminal and to
# file 'output.txt'.
#
# Original version Rik D.T. Janssen, April 2025.
#
# ########################################################################

harvest_script_with_uustaff=batch_harvest_uu_with_uustaff.sh
cp -f batch_harvest_organization.sh $harvest_script_with_uustaff

# Insert harvest of UU staff pages in the batch_harvest_organization.sh script,
# after the harvest of Pure.
sed -i ':a;N;$!ba;s|# ##### #### ### ##|echo "Harvesting UU staff pages."\
PYTHONPATH=$python_path $python_cmd harvest_uustaffpages_to_ricgraph.py --empty_ricgraph no\
exit_code=$?\
if [ "$exit_code" = "0" ] ; then\
  echo "Done with harvesting UU staff pages."\
else\
  echo "===>>> $0: error while harvesting UU staff pages: '\''$exit_code'\''."\
  exit $exit_code\
fi|g' $harvest_script_with_uustaff

./$harvest_script_with_uustaff --organization UU --empty_ricgraph yes

