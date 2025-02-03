# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License, Copyright (c) 2024 Rik D.T. Janssen
#
# ########################################################################
#
# This file is an example to show how to run Ricgraph harvest scripts 
# in a batch. For a more extensive example, see batch_harvest_uu.py.
#
# You may want to start this script as follows:
# [name of this Python file] | tee output.txt
# In this case, output is written both to the terminal and to
# file 'output.txt'.
#
#
# A best practise is to start the harvest with that harvest script of which
# you expect the most data.
# You can also add calls to Ricgraph to modify the graph that is
# harvested, specific for your organization.
# For an example, see batch_harvest_uu.py.
#
# Original version Rik D.T. Janssen, October 2024.
#
# ########################################################################

import os
import sys
# Might be necessary in case you extend this script with Ricgraph calls.
# For an example, see batch_harvest_uu.py.
# import ricgraph as rcg

# Get the name of the Python executable that is executing this script.
PYTHON_CMD = sys.executable


# ###########################################################
# For these two sources you don't need an API key.
# ###########################################################
print('')
print('This script is called by Python interpreter: ' + PYTHON_CMD + '.')
print('It will also be used for the Ricgraph harvest scripts to be called from this script.')
print('')

status = os.system(PYTHON_CMD + ' harvest_yoda_datacite_to_ricgraph.py --empty_ricgraph yes --organization UU')
if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
status = os.system(PYTHON_CMD + ' harvest_rsd_to_ricgraph.py --empty_ricgraph no --organization UU')
if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
