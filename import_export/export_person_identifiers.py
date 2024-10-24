# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
# 
# Copyright (c) 2023 Rik D.T. Janssen
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
# This file contains example code for Ricgraph.
#
# With this code, you can export all "person" nodes in Ricgraph to a csv file.
# You can set some parameters in the code following the "import" statements below.
#
# Original version Rik D.T. Janssen, April 2023.
#
# ########################################################################


import pandas
import ricgraph as rcg

EXPORT_FILENAME = 'ricgraph_export_person_identifiers.csv'
EXPORT_MAX_RECS = 0                   # 0 = all records


# ############################################
# ################### main ###################
# ############################################
print('\nPreparing graph...')
graph = rcg.open_ricgraph()

all_personroot_nodes = rcg.read_all_nodes(name='person-root')
if len(all_personroot_nodes) == 0:
    print('No person-root nodes found, exiting.')
    exit(0)

result = pandas.DataFrame()
chunk = []                              # list of dictionaries
all_records = 9999999999                # a large number
if EXPORT_MAX_RECS == 0:
    print('There are ' + str(len(all_personroot_nodes)) + ' person-root nodes.')
    max_nodes_to_export = all_records
else:
    max_nodes_to_export = EXPORT_MAX_RECS
    print('There are ' + str(len(all_personroot_nodes)) + ' person-root nodes, '
          + 'exporting at most ' + str(max_nodes_to_export) + ' nodes.')

print('Exporting record: 0  ', end='', flush=True)
count = 0
for personroot_node in all_personroot_nodes:
    if count >= max_nodes_to_export:
        break

    count += 1
    if count % 100 == 0:
        print(count, ' ', end='', flush=True)
    if count % 2000 == 0:
        print('\n', end='', flush=True)

    neighbors = rcg.get_all_neighbor_nodes(personroot_node, category_want='person')
    if len(neighbors) == 0:
        continue

    for node in neighbors:
        if node == personroot_node:
            continue

        line = {}
        line['person-root'] = str(personroot_node['value'])
        line[node['name']] = str(node['value'])
        line['_source'] = ','.join([str(source) for source in node['_source']])
        chunk.append(line)

print(count, '\n', end='', flush=True)

chunk_df = pandas.DataFrame(chunk)
result = pandas.concat([result, chunk_df], ignore_index=True)
# dropna(how='all'): drop row if all row values contain NaN
result.dropna(axis=0, how='all', inplace=True)
result.drop_duplicates(keep='first', inplace=True, ignore_index=True)
rcg.write_dataframe_to_csv(filename=EXPORT_FILENAME, df=result)

rcg.close_ricgraph()
