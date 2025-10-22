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
# This script collects collaborations within and between (sub-)organizations
# in Ricgraph. You can choose between two types of diagrams: Chord diagrams
# and Sankey diagrams.
#
# This script is a batch example script, so you can adapt it for your own
# situation by writing the exact function calls to obtain the collaborations.
# To be able to use this script, it is necessary to have
# organization hierarchies. If you don't have these, you can still use it,
# but you will only be able to get collaborations between top-level organizations.
#
# This script assumes organization hierarchies for:
# - Utrecht University, the Netherlands - UU;
# - Vrije Universiteit Amsterdam, the Netherlands - VUA;
# - Delft University of Technology, the Netherlands - DUT.
#
# If you have these, and run this script, you will get organization
# collaborations between:
# - UU Faculty and VUA Faculty, in a Sankey diagram;
# - UU Faculty, VUA Faculty, and DUT Faculty, in a Chord diagram;
# - UU Faculty and UU Faculty, in a Sankey diagram.
#
# For more information about collaborations and Ricgraph, please read
# Rik D.T. Janssen (2025). Utilizing Ricgraph to gain insights into
# research collaborations across institutions, at every organizational
# level. [preprint]. https://doi.org/10.2139/ssrn.5524439.
#
# Original version Rik D.T. Janssen, October 2025.
#
# ########################################################################
#
# Usage:
# organization_collaborations_batch.py
#   No command line options.
#
# For this script to work, copy it to directory ../ricgraph_explorer.
# Then run it in that directory.
# The files produced by this script will be placed in directory 'output_dir'.
# Note that running this script takes a while (as in: 5-15 minutes), since
# it does a time expensive large query in the graph database backend.
#
# ########################################################################


import ricgraph as rcg
from ricgraph_explorer import initialize_ricgraph_explorer, ricgraph_explorer
from ricgraph_explorer_datavis import collabs_org_with_org, collabs_three_orgs_chord


output_dir = 'collabs/'


# ################### main ###################
print('\nPreparing graph...')
graph = rcg.open_ricgraph()
initialize_ricgraph_explorer(ricgraph_explorer_app=ricgraph_explorer)

orgs_with_hierarchies = rcg.get_configfile_key_organizations_with_hierarchies()
if orgs_with_hierarchies is None or orgs_with_hierarchies.empty:
    print('No organizations with hierarchies found, continuing.\n')

# Get organization collaborations between:
# - UU Faculty and VUA Faculty, in a Sankey diagram.
collabs_org_with_org(orgs_with_hierarchies=orgs_with_hierarchies,
                     start_organizations='UU Faculty',
                     collab_organizations='VUA Faculty',
                     research_result_category=rcg.ROTYPE_PUBLICATION,
                     filename=output_dir + 'uufac-vuafac')

# Get organization collaborations between:
# - UU Faculty, VUA Faculty, and DUT Faculty, in a Chord diagram.
collabs_three_orgs_chord(first_org='UU Faculty',
                         second_org='VUA Faculty',
                         third_org='DUT Faculty',
                         research_result_category=rcg.ROTYPE_PUBLICATION,
                         filename=output_dir + 'uufac-vuafac-dutfac')

# Get organization collaborations between:
# - UU Faculty and UU Faculty, in a Sankey diagram.
collabs_org_with_org(orgs_with_hierarchies=orgs_with_hierarchies,
                     start_organizations='UU Faculty',
                     collab_organizations='UU Faculty',
                     research_result_category=rcg.ROTYPE_PUBLICATION,
                     filename=output_dir + 'uufac-uufac')

rcg.close_ricgraph()
