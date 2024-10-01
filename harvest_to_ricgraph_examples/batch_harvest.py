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
import ricgraph as rcg


# ###########################################################
# For these two sources you don't need an API key.
# ###########################################################
status = os.system('python harvest_yoda_datacite_to_ricgraph.py --empty_ricgraph yes')
if status != 0: print('===>>> batch_harvest_uu.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
status = os.system('python harvest_rsd_to_ricgraph.py --empty_ricgraph no --organization UU')
if status != 0: print('===>>> batch_harvest_uu.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
