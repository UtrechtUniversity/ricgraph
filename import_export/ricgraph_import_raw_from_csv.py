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
# Import nodes and edges from a csv file.
# This is a "raw" import, because person-root nodes are also imported, as
# are the connections between e.g. an ORCID node and its person-root node.
# When you import, all nodes and edges
# will be inserted directly in the graph database backend using a Cypher
# query. That means that no checking is done at all if the resulting nodes
# and edges conform to the Ricgraph model. This may result in a graph
# not consistent with the Ricgraph model. Due to this, Ricgraph Explorer
# may not work as expected.
#
# If you import a large number of nodes or edges, this script may crash due
# to shortage of memory. In that case, you may want to set the limit
# MAX_NR_ITEMS_TO_IMPORT.
#
# This script forms a pair with ricgraph_export_raw_to_csv.py.
#
# Original version Rik D.T. Janssen, October 2024.
#
# ########################################################################
#
# Usage
# ricgraph_import_raw_from_csv.py [options]
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
import ast


MAX_NR_ITEMS_TO_IMPORT = 0               # 0 = all records

# Extension of nodes and edges filename.
FILENAME_NODES_EXTENSION = '-nodes.csv'
FILENAME_EDGES_EXTENSION = '-edges.csv'


def convert_string_to_list(cell):
    """
    Function to convert a string to a list if it starts with '['.

    :param cell: A cell in a dataframe.
    :return: Either the list, or the original value.
    """
    if isinstance(cell, str) and cell.startswith('['):
        try:
            return ast.literal_eval(cell)
        except (ValueError, SyntaxError):
            return cell
    return cell


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

print('If you import a large number of nodes or edges, this script may crash due to')
print('shortage of memory. In that case, you may want to set a limit in this script.\n')

# Import all values as string (i.e., also the year which might otherwise be read as an int).
df_nodes = rcg.read_dataframe_from_csv(filename=filename_nodes, datatype=str)
df_edges = rcg.read_dataframe_from_csv(filename=filename_edges, datatype=str)

all_properties = list(rcg.RICGRAPH_PROPERTIES_STANDARD
                      + rcg.RICGRAPH_PROPERTIES_ADDITIONAL
                      + rcg.RICGRAPH_PROPERTIES_HIDDEN)
# Don't do these.
all_properties.remove('source_event')
all_properties.remove('history_event')

if MAX_NR_ITEMS_TO_IMPORT == 0:
    max_items = rcg.A_LARGE_NUMBER
else:
    max_items = MAX_NR_ITEMS_TO_IMPORT

# Make sure every column we expect is in df_nodes.
for prop in all_properties:
    if prop not in df_nodes.columns:
        df_nodes[prop] = numpy.nan

# Cleanup.
# dropna(how='all'): drop row if all row values contain NaN
df_nodes.dropna(axis=0, how='all', inplace=True)
df_nodes.drop_duplicates(keep='first', inplace=True, ignore_index=True)
df_nodes.fillna(value='', inplace=True)
df_nodes = df_nodes.map(convert_string_to_list)

df_edges.dropna(axis=0, how='all', inplace=True)
df_edges.drop_duplicates(keep='first', inplace=True, ignore_index=True)
df_edges.fillna(value='', inplace=True)

# Construct Cypher query to import all nodes.
prop_string = '{'
prop_string += ', '.join(str(prop + ': $' + prop) for prop in all_properties)
prop_string += '}'
cypher_query = 'MERGE (node:RicgraphNode ' + prop_string + ') RETURN node'
count = 0
if int(MAX_NR_ITEMS_TO_IMPORT) > 0:
    print('Importing ' + str(MAX_NR_ITEMS_TO_IMPORT) + ' nodes...')
else:
    print('Importing ' + str(len(df_nodes)) + ' nodes...')
for index, row in df_nodes.iterrows():
    if count >= max_items:
        break
    count += 1
    if count % 500 == 0:
        print(count, ' ', end='', flush=True)
    if count % 5000 == 0:
        print('\n', end='', flush=True)
    graph.execute_query(query_=cypher_query,
                        name=row['name'],
                        category=row['category'],
                        value=row['value'],
                        _key=row['_key'],
                        comment=row['comment'],
                        year=row['year'],
                        url_main=row['url_main'],
                        url_other=row['url_other'],
                        _source=row['_source'],
                        _history=row['_history'],
                        database_=rcg.ricgraph_databasename())
print(count, ' Done.\n\n', end='', flush=True)

# Construct Cypher query to import all edges.
cypher_query = 'MATCH (left_node:RicgraphNode {name: $left_name, value: $left_value}) '
cypher_query += 'MATCH (right_node:RicgraphNode {name: $right_name, value: $right_value}) '
cypher_query += 'MERGE (left_node)-[:LINKS_TO]->(right_node) '
cypher_query += 'MERGE (left_node)<-[:LINKS_TO]-(right_node) '
count = 0
if int(MAX_NR_ITEMS_TO_IMPORT) > 0:
    print('Importing ' + str(MAX_NR_ITEMS_TO_IMPORT) + ' edges...')
else:
    print('Importing ' + str(len(df_edges)) + ' edges...')
for index, row in df_edges.iterrows():
    if count >= max_items:
        break
    count += 1
    if count % 500 == 0:
        print(count, ' ', end='', flush=True)
    if count % 5000 == 0:
        print('\n', end='', flush=True)
    graph.execute_query(query_=cypher_query,
                        left_name=row['name_from'],
                        left_value=row['value_from'],
                        right_name=row['name_to'],
                        right_value=row['value_to'],
                        database_=rcg.ricgraph_databasename())
print(count, ' Done.\n\n', end='', flush=True)

rcg.close_ricgraph()
