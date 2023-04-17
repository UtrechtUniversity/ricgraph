# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License, Copyright (c) 2023 Rik D.T. Janssen
#
# ########################################################################
#
# This file is an example to show how to run Ricgraph harvest scripts 
# in a batch. Choose one of the available batch orders, or create your own
# batch order.
#
# A best practise is to start the harvest with that harvest script of which
# you expect the most data.
#
# Original version Rik D.T. Janssen, April 2023.
#
# ########################################################################

import os


# ###########################################################
# Batch order 1: Preferred batch order for Utrecht University
# ###########################################################
os.system('python harvest_pure_to_ricgraph.py --empty_ricgraph yes --organization UU')
os.system('python harvest_yoda_datacite_to_ricgraph.py --empty_ricgraph no')
os.system('python harvest_rsd_to_ricgraph.py --empty_ricgraph no --organization UU')
os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization UU')
os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization UMCU')
os.system('python harvest_uustaffpages_to_ricgraph.py --empty_ricgraph no')


# ###########################################################
# Batch order 2: If you'd like to harvest OpenAlex
# ###########################################################
#os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph yes --organization UU')
#os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization UMCU')
#os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization DUT')
#os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization EUR')
#os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization EUT')
#os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization UG')
#os.system('python harvest_openalex_to_ricgraph.py --empty_ricgraph no --organization VU')


# ###########################################################
# Batch order 3: If you'd like to harvest the Research Software Directory
# ###########################################################
#os.system('python harvest_rsd_to_ricgraph.py --empty_ricgraph yes --organization UU')
#os.system('python harvest_rsd_to_ricgraph.py --empty_ricgraph no --organization UMCU')
#os.system('python harvest_rsd_to_ricgraph.py --empty_ricgraph no --organization DUT')
#os.system('python harvest_rsd_to_ricgraph.py --empty_ricgraph no --organization EUR')
#os.system('python harvest_rsd_to_ricgraph.py --empty_ricgraph no --organization EUT')
#os.system('python harvest_rsd_to_ricgraph.py --empty_ricgraph no --organization UG')
#os.system('python harvest_rsd_to_ricgraph.py --empty_ricgraph no --organization VU')
