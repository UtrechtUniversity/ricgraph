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
# This script deletes all EMPLOYEE_ID nodes from Ricgraph.
#
# Original version Rik D.T. Janssen, July 2026.
#
# ########################################################################
#
# Usage
# delete_emplid.py [options]
#
# Options:
#   --are_you_sure <yes>
#           Safety check since the script will delete items from Ricgraph.
#           'yes': This script will run.
#           any other value: This script will not run.
#           If this option is not present, the script will prompt the user
#           whether to run the script.
#
# ########################################################################

import sys
import ricgraph as rcg


# ############################################
# ################### main ###################
# ############################################
rcg.print_commandline_arguments(argument_list=sys.argv)

print('This script will delete all EMPLOYEE_ID nodes from Ricgraph.')
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

nodes_with_employeeid = rcg.read_all_nodes(name='EMPLOYEE_ID',
                                           name_is_exact_match=True)
if len(nodes_with_employeeid) == 0:
    print('Your Ricgraph does not have any EMPLOYEE_ID nodes, nothing to be done.')
    exit(0)

print('There are ' + str(len(nodes_with_employeeid)) + ' EMPLOYEE_ID nodes ('
      + rcg.timestamp() + '), deleting node:')
count = 0
for node in nodes_with_employeeid:
    count = rcg.print_progress(count=count, interval=100)
    rcg.delete_node(node=node)

rcg.print_progress(count=count, now=True)
