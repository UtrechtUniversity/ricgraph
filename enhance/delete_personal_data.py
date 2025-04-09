# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
# 
# Copyright (c) 2025 Rik D.T. Janssen
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# ########################################################################
#
# Delete all personal data of one or more persons from Ricgraph.
# These persons are listed in a csv file.
#
# Original version Rik D.T. Janssen, January 2025.
#
# ########################################################################
#
# Usage
# delete_personal_data.py [options]
#
# Options:
#   --filename <filename>
#           Specifies a csv file that has columns 'name' and 'value'.
#           Every row in this file contains a personal identifier of
#           a person whose personal data needs to be deleted from Ricgraph.
#   --are_you_sure <yes>
#           Safety check since the script will delete items from Ricgraph.
#           'yes': This script will run.
#           any other value: This script will not run.
#           If this option is not present, the script will prompt the user
#           whether to run the script.
#
# ########################################################################

import os.path
import sys
import ricgraph as rcg


# ############################################
# ################### main ###################
# ############################################
rcg.print_commandline_arguments(argument_list=sys.argv)

print('This script will delete from Ricgraph all personal data of one or more persons')
print('that are listed in the input file.')
are_you_sure = rcg.get_commandline_argument(argument='--are_you_sure',
                                            argument_list=sys.argv)
if are_you_sure == '':
    are_you_sure = input('Are you sure you want to run this script? Type "yes" to continue: ')
    if are_you_sure != 'yes':
        print('Exiting this script.')
        exit(1)
elif are_you_sure != 'yes':
    print('It appears from the command line that you are not sure to run this script. Exiting.')
    exit(1)

filename = rcg.get_commandline_argument(argument='--filename',
                                                 argument_list=sys.argv)
if filename == '':
    print('\nYou need to specify a filename. This filename contains')
    print('the persons whose personal data will be deleted from Ricgraph.')
    print('If you enter an empty value, this script will exit.')
    filename = input('Please specify this filename: ')
    if filename == '':
        print('Exiting.\n')
        exit(1)

if not os.path.isfile(path=filename):
    print('Error: filename "' + filename + '" not found, exiting.')
    exit(1)

print('Filename used: "' + filename + '".')

print('\nPreparing graph, starting script at ' + rcg.timestamp() + '...\n')
graph = rcg.open_ricgraph()

# Import all values as string.
personal_ids = rcg.read_dataframe_from_csv(filename=filename, datatype=str)

# Make sure every column we expect is in personal_ids.
for prop in rcg.RICGRAPH_PROPERTIES_STANDARD:
    if prop == 'category':
        continue
    if prop not in personal_ids.columns:
        print('\nError: property "' + prop + '" not found in file "' + filename + '".')
        print('Exiting.\n')
        exit(1)

if personal_ids['name'].str.contains('person-root').any():
    # The first part creates a boolean Series indicating whether each cell
    # contains 'person-root'. '.any()' checks if any of those boolean values are True.
    print('Error: At least one of the personal ids to be deleted is identified by')
    print('a "person-root" value in the input file.')
    print('This is not possible since person-root UUIDs will change after a reharvest.')
    print('Remove this id and identify this person by another personal id. Exiting.')
    exit(1)

nodes_deleted = 0
personal_ids_found = 0
for personal_id in personal_ids.itertuples():
    print('\nFinding person with personal id [' + personal_id.name + ', ' + personal_id.value + '].')
    node = rcg.read_node(name=personal_id.name, value=personal_id.value)
    if node is None:
        print('  Personal id not found, skipping.')
        continue

    personal_ids_found += 1
    personroot = rcg.get_personroot_node(node=node)
    if personroot is None:
        print('  Found. This personal id does not have a person-root node, deleting node.\n')
        rcg.delete_node(node=node)
        nodes_deleted += 1
        continue

    print('  Found. Its "person-root" node is [' + personroot['name'] + ', ' + personroot['value'] + '].')
    print('  Deleting neighbors of this "person-root" node containing personal data:')
    neighbors = rcg.get_all_neighbor_nodes(node=personroot, category_want='person')

    for neighbor in neighbors:
        rcg.delete_node(node=neighbor)
        nodes_deleted += 1
        print('    Deleted personal id [' + neighbor['name'] + ', ' + neighbor['value'] + '].')

    print('  Cleaning _history of this "person-root" node, since it may contain personal data:')
    time_stamp = rcg.datetimestamp()
    node_properties = {'_history': [time_stamp + ': Cleaned _history due to delete of personal data request.']}
    rcg.cypher_update_node_properties(node_element_id=personroot.element_id,
                                      node_properties=node_properties)
    print('    Cleaned _history.')

print('\nDone at ' + rcg.timestamp() + '.')
rcg.close_ricgraph()

print('Summary')
print('File "' + filename + '" has ' + str(len(personal_ids)) + ' personal identifiers')
print('identifying persons to be deleted from Ricgraph.')
if personal_ids_found == len(personal_ids):
    print('From these, all have been found.')
else:
    print('From these, only ' + str(personal_ids_found) + ' could be found.')

print('In total, ' + str(nodes_deleted) + ' nodes containing personal identifiers have been deleted.')
