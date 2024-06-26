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
# Updated Rik D.T. Janssen, February 2023.
#
# ########################################################################


import ricgraph as rcg


# ############################################
# ################### main ###################
# ############################################
print('\nPreparing graph...')
graph = rcg.open_ricgraph()

for pid_type in ('DAI', 'EMPLOYEE_ID', 'ISNI', 'ORCID', 'SCOPUS_AUTHOR_ID'):
    print('-----------------------------------------------------------------------------')
    print('Testing for multiple occurrences of PID: ' + pid_type)
    result = rcg.read_all_nodes(name=pid_type)

    for node in result:
        neighbors_nodes = rcg.get_all_neighbor_nodes(node=node)
        number_of_edges = len(neighbors_nodes)
        if number_of_edges > 1:
            print('---------------')
            print('From node with name: ' + node['name'] + ', value: ' + node['value']
                  + ' (' + node['url_main']
                  + '),\nthere are ' + str(number_of_edges) + ' outgoing edges, to nodes:')
            for neighbor in neighbors_nodes:
                if node == neighbor:
                    continue
                personroot_node = rcg.get_personroot_node(neighbor)
                fullname_nodes = rcg.get_all_neighbor_nodes(node=personroot_node,
                                                            name_want='FULL_NAME')
                if len(fullname_nodes) == 0:
                    res = '[no FULL_NAME found]'
                else:
                    res = fullname_nodes[0]['value']
                print('- name: ' + neighbor['name'] + ', value: ' + neighbor['value']
                      + '. This node\n  is connected to a node with FULL_NAME: ' + res + '.')

rcg.close_ricgraph()
