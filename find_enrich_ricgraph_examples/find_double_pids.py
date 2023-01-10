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
# With this code, you can check if there are any personal identifiers that are
# pointing to two or more different persons.
# There are no parameters to set.
#
# Original version Rik D.T. Janssen, December 2022.
#
# ########################################################################


import py2neo
import ricgraph as rcg


def get_full_name(start_node: py2neo.Node) -> str:
    """Get the name (property FULL_NAME) from a node connected to the 'start_node'.

    :param start_node: node to start from.
    :return: name found.
    """
    name_found = ''
    if start_node['name'] == 'FULL_NAME':
        # This should not happen
        name_found = start_node['value']
        print('get_full_name(): not expected, this node has a neighbor which is not a person-root (value: '
              + name_found + ').')
        return name_found

    for ledge in graph.match((start_node,), r_type='LINKS_TO'):
        end_node = ledge.end_node
        if end_node['name'] == 'person-root':
            # Go one step further
            for edge_from_person_root in graph.match((end_node,), r_type='LINKS_TO'):
                if ledge == edge_from_person_root:
                    # Prevent backtracking
                    continue
                if edge_from_person_root.end_node['name'] == 'FULL_NAME':
                    name_found = edge_from_person_root.end_node['value']

        if end_node['name'] == 'FULL_NAME':
            name_found = end_node['value']
    return name_found


# ############################################
# ################### main ###################
# ############################################
print('\nPreparing graph...')
graph = rcg.open_ricgraph()

for pid_type in ('DAI', 'EMPLOYEE_ID', 'ISNI', 'ORCID', 'SCOPUS_AUTHOR_ID'):
    print('-----------------------------------------------------------------------------')
    print('Testing for multiple occurrences of PID: ' + pid_type)
    result = rcg.read_all_nodes(name=pid_type, category='', value='')

    for node in result:
        number_of_edges = len(graph.match((node,), r_type='LINKS_TO'))
        if number_of_edges > 1:
            print('---------------')
            print('From node with name: ' + node['name'] + ', value: ' + node['value']
                  + ' (' + node['url_main']
                  + '), there are ' + str(number_of_edges) + ' outgoing edges, to nodes:')
            for edge in graph.match((node,), r_type='LINKS_TO'):
                next_node = edge.end_node
                if node == next_node:
                    continue
                res = get_full_name(next_node)
                if res == '':
                    res = '[no FULL_NAME found]'
                print('- name: ' + next_node['name'] + ', value: ' + next_node['value']
                      + '. This node is connected to a node with FULL_NAME: ' + res + '.')

rcg.close_ricgraph()
