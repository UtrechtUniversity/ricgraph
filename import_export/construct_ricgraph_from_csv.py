# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
# 
# Copyright (c) 2024 Rik D.T. Janssen
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
# Construct a Ricgraph from a csv file.
# Nodes and edges are inserted with Ricgraph calls. That means,
# that nodes are inserted in pairs. If a node is not connected to another
# node, it will not be created. This is due to the way Ricgraph works.
# This script is different compared to ricgraph_export_raw_to_csv.py and
# ricgraph_import_raw_from_csv.py, since these export/import with Cypher
# calls.
#
# Original version Rik D.T. Janssen, October 2024.
#
# ########################################################################
#
# Usage
# construct_ricgraph_from_csv.py [options]
#
# Options:
#   --empty_ricgraph <yes|no>
#           'yes': Ricgraph will be emptied before importing.
#           'no': Ricgraph will not be emptied before importing.
#           If this option is not present, the script will prompt the user
#           what to do.
#   --filename <filename>
#           Import nodes and edges from a csv file starting with <filename>.
#
# ########################################################################

import os.path
import sys
import numpy
import ricgraph as rcg


# Extension of nodes and edges filename.
FILENAME_NODES_EXTENSION = '-nodes.csv'
FILENAME_EDGES_EXTENSION = '-edges.csv'


# ############################################
# ################### main ###################
# ############################################
rcg.print_commandline_arguments(argument_list=sys.argv)

print('\nYou need to specify a filename. This name will be used for')
print('importing the nodes and edges.')
print('If you enter an empty value, this script will exit.')
filename = rcg.get_commandline_argument_filename(argument_list=sys.argv)
if filename == '':
    print('Exiting.\n')
    exit(1)

filename_nodes = filename + FILENAME_NODES_EXTENSION
filename_edges = filename + FILENAME_EDGES_EXTENSION

if not os.path.isfile(path=filename_nodes):
    print('Error: import filename for nodes "' + filename_nodes + '" not found, exiting.')
    exit(1)
if not os.path.isfile(path=filename_edges):
    print('Error: import filename for edges "' + filename_edges + '" not found, exiting.')
    exit(1)

print('Filename used for nodes: "' + filename_nodes + '", for edges: "'
      + filename_edges + '".')

print('\nPreparing graph...')
graph = rcg.open_ricgraph()

empty_graph = rcg.get_commandline_argument_empty_ricgraph(argument_list=sys.argv)
if empty_graph == 'yes' or empty_graph == 'no':
    rcg.empty_ricgraph(answer=empty_graph)
else:
    print('Exiting.\n')
    exit(1)

# Import all values as string (i.e., also the year which might otherwise be read as an int).
df_nodes = rcg.read_dataframe_from_csv(filename=filename_nodes, datatype=str)
df_edges = rcg.read_dataframe_from_csv(filename=filename_edges, datatype=str)

all_properties = list(rcg.get_ricgraph_properties_standard() + rcg.get_ricgraph_properties_additional())

# We don't do the hidden properties (they will be created by Ricgraph), nor these.
all_properties.remove('source_event')
all_properties.remove('history_event')

# Make sure every column we expect is in df_nodes.
for prop in all_properties:
    if prop not in df_nodes.columns:
        df_nodes[prop] = numpy.nan

# And remove columns we do not need.
df_nodes = df_nodes[['name', 'category', 'value',
                     'comment', 'year', 'url_main', 'url_other']]
# Cleanup.
# dropna(how='all'): drop row if all row values contain NaN
df_nodes.dropna(axis=0, how='all', inplace=True)
df_nodes.drop_duplicates(keep='first', inplace=True, ignore_index=True)
df_nodes.fillna(value='', inplace=True)

df_edges.dropna(axis=0, how='all', inplace=True)
df_edges.drop_duplicates(keep='first', inplace=True, ignore_index=True)
df_edges.fillna(value='', inplace=True)

if df_nodes['name'].str.contains('person-root').any():
    # The first part creates a boolean Series indicating whether each cell
    # contains 'person-root'. '.any()' checks if any of those boolean values are True.
    print('Error: one or more of the nodes to import in file "' + filename_nodes
          + '" has name "person-root" which is not allowed, exiting.')
    exit(1)

if df_edges['name_from'].str.contains('person-root').any() \
        or df_edges['name_from'].str.contains('person-root').any():
    print('Error: one or more of the edges to import in file "' + filename_edges
          + '" has name "person-root" which is not allowed, exiting.')
    exit(1)

# Merge edges with nodes to get details for name_from and value_from
merged = df_edges.merge(df_nodes, left_on=['name_from', 'value_from'], right_on=['name', 'value'], how='left')
merged.rename(columns={'name_from': 'name1',
                       'category': 'category1',
                       'value_from': 'value1',
                       'comment': 'comment1',
                       'year': 'year1',
                       'url_main': 'url_main1',
                       'url_other': 'url_other1'}, inplace=True)

merged = merged[['name_to', 'value_to',
                 'name1', 'category1', 'value1',
                 'comment1', 'year1', 'url_main1', 'url_other1']]

# Merge again to get details for name2 and value2
result = merged.merge(df_nodes, left_on=['name_to', 'value_to'], right_on=['name', 'value'], how='left')
result.rename(columns={'name_to': 'name2',
                       'category': 'category2',
                       'value_to': 'value2',
                       'comment': 'comment2',
                       'year': 'year2',
                       'url_main': 'url_main2',
                       'url_other': 'url_other2'}, inplace=True)

# Select relevant columns for the final result DataFrame
result = result[['name1', 'category1', 'value1',
                 'comment1', 'year1', 'url_main1', 'url_other1',
                 'name2', 'category2', 'value2',
                 'comment2', 'year2', 'url_main2', 'url_other2']]

print('There are ' + str(len(df_nodes)) + ' nodes and ' + str(len(df_edges)) + ' edges in the import files.')
print('This results in ' + str(len(result)) + ' nodepairs to be inserted in Ricgraph.\n')
print('The following nodepairs will be inserted in Ricgraph at ' + rcg.timestamp() + ':')
print(result)
rcg.create_nodepairs_and_edges_df(left_and_right_nodepairs=result)
print('\nDone at ' + rcg.timestamp() + '.\n')

rcg.close_ricgraph()
