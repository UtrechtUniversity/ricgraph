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
# This script harvests the Research Software Directory and Yoda for the UU.
# Since these do not need a REST API key, they are very suitable for a 
# demo harvest script that anyone can run.
#
# You may want to start this script as follows:
# [name of this script] | tee output.txt
# In this case, output is written both to the terminal and to
# file 'output.txt'.
# Or use the Makefile and type:
# make bash_script=harvest_multiple_sources/multiple_harvest_demo.sh run_bash_script
#
# Original version Rik D.T. Janssen, April 2025.
#
# ########################################################################

./multiple_harvest_organization_rsd_yoda.sh --organization UU --empty_ricgraph yes
