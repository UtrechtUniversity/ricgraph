# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
# 
# Copyright (c) 2026 Rik D.T. Janssen
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
# This script renames URLs in the DUT harvest.
# For DUT, we harvest from pure.tudelft.nl, but the links to the
# portal in that instance point to research.tudelft.nl.
# This script renames those links in the url_main, url_other,
# and url_asset properties of nodes.
#
# Original version Rik D.T. Janssen, November 2026.
#
# ########################################################################
#
# Usage
# rename_dut_urls.py [options]
#
# Options:
#   --are_you_sure <yes>
#           Safety check since the script will rename items in Ricgraph.
#           'yes': This script will run.
#           any other value: This script will not run.
#           If this option is not present, the script will prompt the user
#           whether to run the script.
#
# ########################################################################

import sys
import ricgraph as rcg

OLD_URL = 'https://pure.tudelft.nl/'
NEW_URL = 'https://research.tudelft.nl/'
RICGRAPH_URL_PROPERTIES = ['url_main', 'url_other', 'url_asset']

# ############################################
# ################### main ###################
# ############################################
rcg.print_commandline_arguments(argument_list=sys.argv)

print('This script will rename DUT URLs in Ricgraph, but only')
print('for the node properties "' + str(RICGRAPH_URL_PROPERTIES) + '".')
print('Strings matching "' + OLD_URL + '" will be renamed to')
print('"' + NEW_URL + '.')
print('If there are no matches, nothing will be changed.')

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

print('\nPreparing graph, starting script at ' + rcg.timestamp() + '...\n')
graph = rcg.open_ricgraph()

total_nr_nodes_changed = 0

for property_name in RICGRAPH_URL_PROPERTIES:
    print('Processing changes for property "' + property_name + '"...')
    time_stamp = rcg.datetimestamp()
    history_line = time_stamp + ': '
    history_line += rcg.create_history_line(property_name=property_name,
                                            old_value=OLD_URL,
                                            new_value=NEW_URL)

    cypher_query = 'MATCH (node:RicgraphNode) '
    # Make sure every property_name is a list.
    cypher_query += 'WITH node, '
    cypher_query += ' CASE '
    cypher_query += '     WHEN node[$url_property] IS :: LIST<STRING> NOT NULL '
    cypher_query += '     THEN node[$url_property] '
    cypher_query += '     ELSE [] '
    cypher_query += ' END AS urls '
    cypher_query += 'WHERE any(url IN urls WHERE url CONTAINS $old_url) '
    # Now for every element in 'urls', if it matches, change it.
    cypher_query += 'SET node[$url_property] = [ '
    cypher_query += '    url IN urls | '
    cypher_query += '    replace(url, $old_url, $new_url) '
    cypher_query += '], '
    # Add a message to _history.
    cypher_query += 'node._history = coalesce(node._history, []) + [$history_line] '
    # Return the number of nodes changed. Note that each node may have
    # more than one URL that has to be changed.
    cypher_query += 'RETURN count(*) AS nodes_changed'

    records, _, _ = graph.execute_query(query_=cypher_query,
                                        url_property=property_name,
                                        old_url=OLD_URL,
                                        new_url=NEW_URL,
                                        history_line=history_line,
                                        database_=rcg.ricgraph_databasename())

    nr_nodes_changed = records[0]["nodes_changed"]
    total_nr_nodes_changed += nr_nodes_changed
    print('   ' + str(nr_nodes_changed) + ' nodes have changed.\n')

print('Total number of nodes changed is ' + str(total_nr_nodes_changed) + '.')
print('Note that a node may have more than one URL that has changed.\n')
print('Script finished at ' + rcg.timestamp() + '...\n')
