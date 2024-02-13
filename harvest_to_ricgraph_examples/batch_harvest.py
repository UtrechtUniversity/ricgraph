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
# batch order. 'Batch order 1' is specifically created for harvesting Utrecht
# University sources. Please adapt for your own situation, for example use
# 'Batch order 2' or 'Batch order 3'.
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

rename_nodes_first_group = {
    'University: Universiteit Utrecht': 'Utrecht University',
    'UU Faculty: Faculteit Betawetenschappen': 'Science',
    'UU Faculty: Faculteit Diergeneeskunde': 'Veterinary Medicine',
    'UU Faculty: Faculteit Geesteswetenschappen': 'Humanities',
    'UU Faculty: Faculteit Geowetenschappen': 'Geosciences',
    'UU Faculty: Faculteit REBO': 'Law, Economics and Governance',
    'UU Faculty: Faculteit Sociale Wetenschappen': 'Social and Behavioural Sciences',
    'UU Faculty: University College Utrecht': 'University College Utrecht',
    'UU Faculties / Services: Utrecht University Library': 'Utrecht University Library',
    'UU Faculties / Services: Corporate Offices': 'University Corporate Offices',
}

rename_nodes_second_group = {
    'Science': 'UU Faculty: Science',
    'Veterinary Medicine': 'UU Faculty: Veterinary Medicine',
    'Humanities': 'UU Faculty: Humanities',
    'Geosciences': 'UU Faculty: Geosciences',
    'Law, Economics and Governance': 'UU Faculty: Law, Economics and Governance',
    'Social and Behavioural Sciences': 'UU Faculty: Social and Behavioural Sciences',
    'University College Utrecht': 'UU Faculty: University College Utrecht',
    'Utrecht University Library': 'UU Faculties/Services: Utrecht University Library',
    'University Corporate Offices': 'UU Faculties/Services: University Corporate Offices',
    'Medicine': 'University Medical Center Utrecht',
}


def rename_nodes(name: str, rename_table: dict):
    for old_value in rename_table:
        new_value = rename_table[old_value]
        print('batch_harvest.py/rename_nodes(): Updating node name: "' + name + '" value from: "' + old_value + '" to: "' + new_value + '".')
        node = rcg.update_node_value(name=name, old_value=old_value, new_value=new_value)
        if node is None:
            print('----> Error: update of value: "' + old_value + '" to: "' + new_value + '" failed.')
            exit(2)

    return


# ###########################################################
# Batch order 1: Preferred batch order for Utrecht University
# ###########################################################
status = os.system('python harvest_pure_to_ricgraph.py --empty_ricgraph yes --organization UU --harvest_projects yes')
if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)

# Change the 'value' of some nodes, so they will have the same name as nodes in following harvests.
graph = rcg.open_ricgraph()
if graph is None:
    print('Ricgraph could not be opened in batch_harvest.py.')
    exit(2)
rename_nodes(name='ORGANIZATION_NAME', rename_table=rename_nodes_first_group)
rcg.close_ricgraph()

status = os.system('python harvest_uustaffpages_to_ricgraph.py --empty_ricgraph no')
if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)

graph = rcg.open_ricgraph()
if graph is None:
    print('Ricgraph could not be opened in batch_harvest.py.')
    exit(2)
rename_nodes(name='ORGANIZATION_NAME', rename_table=rename_nodes_second_group)
rcg.close_ricgraph()

status = os.system('python harvest_yoda_datacite_to_ricgraph.py --empty_ricgraph no')
if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
status = os.system('python harvest_rsd_to_ricgraph.py --empty_ricgraph no --organization UU')
if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
status = os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization UU')
if status != 0: print('===>>> batch_harvest.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
status = os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization UMCU')
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

