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
# This file is an demo to show how to run Ricgraph harvest scripts
# in a batch. It harvests Yoda and Research Software Directory of UU,
# since they do not need a REST API key.
#
# You may want to start this script as follows:
# [name of this script] | tee output.txt
# In this case, output is written both to the terminal and to
# file 'output.txt'.
#
# Original version Rik D.T. Janssen, April 2025.
#
# ########################################################################

./batch_harvest_organization_rsd_yoda.sh --organization UU --empty_ricgraph yes
