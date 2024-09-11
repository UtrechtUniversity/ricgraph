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
# in a batch. 
#
# You may want to start this script as follows:
# [name of this Python file] | tee output.txt
# In this case, output is written both to the terminal and to 
# file 'output.txt'.
#
# Original version Rik D.T. Janssen, April 2023.
# Updated version September 2024 for Delft University of Technology
#
# ########################################################################

import os
import ricgraph as rcg

rename_nodes_first_group = {
    'University: Delft University of Technology': 'Delft University of Technology',
}


def rename_nodes(name: str, rename_table: dict):
    for old_value in rename_table:
        new_value = rename_table[old_value]
        print('batch_harvest_tud.py/rename_nodes(): Updating node name: "' + name + '" value from: "' + old_value + '" to: "' + new_value + '".')
        node = rcg.update_node_value(name=name, old_value=old_value, new_value=new_value)
        if node is None:
            print('----> Error: update of value: "' + old_value + '" to: "' + new_value + '" failed.')
            exit(2)

    return

# ###########################################################
# Batch order for Delft University of Technology
# ###########################################################
status = os.system('../bin/python harvest_pure_to_ricgraph.py --empty_ricgraph yes --organization DUT --harvest_projects yes')
if status != 0: print('===>>> batch_harvest_tud.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)

# Change the 'value' of some nodes, so they will have the same name as nodes in following harvests.
graph = rcg.open_ricgraph()
if graph is None:
    print('Ricgraph could not be opened in batch_harvest_tud.py.')
    exit(2)
rename_nodes(name='ORGANIZATION_NAME', rename_table=rename_nodes_first_group)
rcg.close_ricgraph()

status = os.system('../bin/python harvest_rsd_to_ricgraph.py --empty_ricgraph no --organization DUT')
if status != 0: print('===>>> batch_harvest_tud.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)
status = os.system('../bin/python harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization DUT')
if status != 0: print('===>>> batch_harvest_tud.py: error while executing previous script, status: ' + str(status) + '.'); exit(status)

