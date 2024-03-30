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
# Count the organizations of persons who have contributed to all nodes of a
# specified category (e.g., 'data set' or 'software').
# Both a histogram and a collaboration table will be
# computed and written to a file. The filenames are predefined, see below.
# The histogram contains the count of organizations of all nodes of the
# specified category.
# The collaboration table contains the count of organizations who have worked
# together on all nodes of the specified category.
#
# Original version Rik D.T. Janssen, February 2024.
#
# ########################################################################
#
# Usage
# count_organizations_contributed_to_category.py [options]
#
# Options:
#   --sort_organization <organization name>
#           Sort the collaboration table on this organization name.
#           If the name has one or more spaces, enclose it with "...".
#           If this option is not present, the script will prompt the user
#           for a name.
#   --category <category>
#           Compute histogram and collaboration table for given category.
#           If the name has one or more spaces, enclose it with "...".
#           If this option is not present, the script will prompt the user
#           for a name.
#
# ########################################################################


import sys
import pandas
import ricgraph as rcg

# The maximum number of nodes to process.
MAX_NR_NODES = rcg.A_LARGE_NUMBER      # Do for all nodes found


# ############################################
# ################### main ###################
# ############################################
print('\nPreparing graph...')
rcg.open_ricgraph()

rcg.print_commandline_arguments(argument_list=sys.argv)

sort_organization = rcg.get_commandline_argument(argument='--sort_organization',
                                                 argument_list=sys.argv)
if sort_organization == '':
    print('\nYou need to specify an organization name. This name will be used to sort')
    print('the collaboration table.')
    print('If you enter an empty value, this script will exit.')
    sort_organization = input('Please specify this organization name: ')
    if sort_organization == '':
        print('Exiting.\n')
        exit(1)

category_all = rcg.read_all_values_of_property('category')
if len(category_all) == 0 :
    print('Error in obtaining list with all property values for property "category".')
    exit(2)

category_wanted = rcg.get_commandline_argument(argument='--category',
                                               argument_list=sys.argv)
if category_wanted == '':
    print('\nThis script collects the organizations of persons who have contributed to nodes')
    print('of a specified category, and writes a histogram and a collaboration table of')
    print('these organizations to a csv file. You may want to visualize the results using e.g. Excel.\n')
    print('Choose one of these categories:')
    print(str(category_all))
    category_wanted = input('Please specify a category: ')
    if category_wanted == '':
        print('Error, you have not specified a category, exiting.\n')
        exit(1)

if category_wanted not in category_all:
    print('Error, category "' + category_wanted + '" is not a valid category.')
    print('Exiting.\n')
    exit(1)

nodes = rcg.read_all_nodes(category=category_wanted)
if len(nodes) == 0:
    print('Nothing found for category "' + category_wanted + '".')
    exit(1)

histogram_filename = category_wanted.replace(' ', '_') + '_histogram_'
histogram_filename += str(len(nodes)) + '_items' + '.csv'
collaborations_filename = category_wanted.replace(' ', '_') + '_collaborations_'
collaborations_filename += str(len(nodes)) + '_items' + '.csv'
histogram = {}
collaborations = rcg.create_multidimensional_dict(2, int)

# Collect the organizations of persons who have contributed to a node with category 'category_wanted'.
# For one node of a category, every organization is only counted once.
# We use a set to collect organizations since it does not allow duplicates.
print('\nThere are ' + str(len(nodes)) + ' nodes of category "' + category_wanted + '".')
nr_nodes_processed = 0
print('Processing node: ', end='', flush=True)
for node in nodes:
    if nr_nodes_processed >= MAX_NR_NODES:
        break
    nr_nodes_processed += 1
    if nr_nodes_processed % 25 == 0:
        print(nr_nodes_processed, ' ', end='', flush=True)
    if nr_nodes_processed % 500 == 0:
        print('\n', end='', flush=True)

    node_in_organizations = set()
    personroots = rcg.get_all_personroot_nodes(node=node)
    for personroot in personroots:
        organizations = rcg.get_all_neighbor_nodes(node=personroot, category_want='organization')
        for organization in organizations:
            node_in_organizations.add(organization['value'])

    for organization in node_in_organizations:
        if organization not in histogram:
            histogram[organization] = 1
        else:
            histogram[organization] += 1
        for collab_organization in node_in_organizations:
            # Note: also count collaborations with the same organization,
            # i.e. organization == collab_organization, because
            # it makes sorting the collaboration table look better.
            collaborations[organization][collab_organization] += 1

print(nr_nodes_processed, '\n', end='', flush=True)

if sort_organization not in histogram:
    print('\n\nError, the organization "' + sort_organization + '" for sorting the collaboration table')
    print('does not exist.')
    print('Exiting.\n')
    exit(1)

count_of = ' count of ' + category_wanted + ' (total ' + str(len(nodes)) + ' items)'
histogram_df = pandas.DataFrame(histogram.items(), columns=['organization', 'nr_nodes_processed'])
histogram_df.sort_values(by='nr_nodes_processed', ascending=False, inplace=True, ignore_index=True)
histogram_df.rename(columns={'nr_nodes_processed': 'histogram' + count_of}, inplace=True)
print(histogram_df)
rcg.write_dataframe_to_csv(filename=histogram_filename, df=histogram_df)

collaborations_df = pandas.DataFrame(collaborations)
collaborations_df.fillna(value=0, inplace=True)
collaborations_df = collaborations_df.astype(int)
collaborations_df.sort_values(by=sort_organization,
                              axis='columns',
                              ascending=False,
                              inplace=True)
collaborations_df.reset_index(inplace=True)
collaborations_df.rename(columns={'index': 'collaboration' + count_of}, inplace=True)
collaborations_df.sort_values(by=sort_organization,
                              axis='index',
                              ascending=False,
                              inplace=True,
                              ignore_index=True)
print(collaborations_df)
rcg.write_dataframe_to_csv(filename=collaborations_filename, df=collaborations_df)

rcg.close_ricgraph()
