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
# Rename organizations.
# The organizations are listed in a csv file in the format.
# "old organization name","new organization name"
#
# Original version Rik D.T. Janssen, April 2025.
#
# ########################################################################
#
# Usage
# rename_orgs.py [options]
#
# Options:
#   --filename <filename>
#           Specifies a csv file that has columns 'orgname_old'
#           and 'orgname_new'.
#           Every row in this file contains an organization name
#           that has to be renamed to a new organization name.
#
#   --are_you_sure <yes>
#           Safety check since the script will modify Ricgraph.
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

print('This script will rename organizations in Ricgraph')
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
    print('the organizations that have to be renamed in Ricgraph.')
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
organizations = rcg.read_dataframe_from_csv(filename=filename, datatype=str)
for org in organizations.itertuples():
    orgname_old = org.orgname_old
    orgname_new = org.orgname_new
    print('Start rename at ' + rcg.timestamp(seconds=True)
          + ' from "' + orgname_old + '" to: "' + orgname_new + '".')
    node = rcg.update_node_value(name='ORGANIZATION_NAME',
                                 old_value=orgname_old,
                                 new_value=orgname_new)
    if node is None:
        print('    ----> Warning: failed rename at ' + rcg.timestamp(seconds=True) + '.')
        # Do not exit, continue.
    else:
        print('    Finished rename at ' + rcg.timestamp(seconds=True) + '.')

print('\nDone at ' + rcg.timestamp() + '.')
rcg.close_ricgraph()
