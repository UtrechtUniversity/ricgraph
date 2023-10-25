# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License, Copyright (c) 2023 Rik D.T. Janssen
#
# ########################################################################
#
# This file is an example to show how to run Ricgraph harvest scripts 
# in a batch. Choose one of the available batch orders, or create your own
# batch order.
#
# A best practise is to start the harvest with that harvest script of which
# you expect the most data.
#
# You can also add calls to Ricgraph to modify the graph that is
# harvested, specific for your organization.
# You can do this e.g. in between the different
# calls to the harvest scripts, or for post processing.
# For example, the Utrecht University Pure uses organization name
# 'University: Universiteit Utrecht', while this same organization
# is called 'Utrecht University' in OpenAlex. If you rename the node
# [name='ORGANIZATION_NAME', value='University: Universiteit Utrecht'],
# to
# [name='ORGANIZATION_NAME', value='Utrecht University']
# after the Pure harvest and before the OpenAlex harvest,
# records harvested using the OpenAlex harvest will be connected to this
# already existing node, preventing the creation of another.
# This ensures a more concise graph.
#
# Original version Rik D.T. Janssen, April 2023.
# Updated version October 2023.
#
# ########################################################################

import os
import ricgraph as rcg


# ###########################################################
# Batch order 1: Preferred batch order for Utrecht University
# ###########################################################
status = os.system('python harvest_pure_to_ricgraph.py --empty_ricgraph yes --organization UU')
if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)

# Change the value of the node representing Utrecht University. For explanation see above.
graph = rcg.open_ricgraph()
if graph is None:
    print('Ricgraph could not be opened in batch_harvest.py.')
    exit(2)
node = rcg.update_node_value(name='ORGANIZATION_NAME',
                             old_value='University: Universiteit Utrecht',
                             new_value='Utrecht University')
if node is None:
    print('Update of node failed in batch_harvest.py.')
    exit(2)
rcg.close_ricgraph()

status = os.system('python harvest_yoda_datacite_to_ricgraph.py --empty_ricgraph no')
if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
status = os.system('python harvest_rsd_to_ricgraph.py --empty_ricgraph no --organization UU')
if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
status = os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization UU')
if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
status = os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization UMCU')
if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)

status = os.system('python harvest_uustaffpages_to_ricgraph.py --empty_ricgraph no')
if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)

# status = os.system('python harvest_pure_to_ricgraph.py --empty_ricgraph no --organization VU --harvest_projects yes')
# if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)

# ###########################################################
# Batch order 2: If you'd like to harvest OpenAlex
# ###########################################################
#status = os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph yes --organization UU')
#if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
#status = os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization UMCU')
#if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
#status = os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization DUT')
#if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
#status = os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization EUR')
#if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
#status = os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization EUT')
#if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
#status = os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization UG')
#if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
#status = os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization VU')
#if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)


# ###########################################################
# Batch order 3: If you'd like to harvest the Research Software Directory
# ###########################################################
#status = os.system('python harvest_rsd_to_ricgraph.py --empty_ricgraph yes --organization UU')
#if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
#status = os.system('python harvest_rsd_to_ricgraph.py --empty_ricgraph no --organization UMCU')
#if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
#status = os.system('python harvest_rsd_to_ricgraph.py --empty_ricgraph no --organization DUT')
#if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
#status = os.system('python harvest_rsd_to_ricgraph.py --empty_ricgraph no --organization EUR')
#if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
#status = os.system('python harvest_rsd_to_ricgraph.py --empty_ricgraph no --organization EUT')
#if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
#status = os.system('python harvest_rsd_to_ricgraph.py --empty_ricgraph no --organization UG')
#if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
#status = os.system('python harvest_rsd_to_ricgraph.py --empty_ricgraph no --organization VU')
#if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)

