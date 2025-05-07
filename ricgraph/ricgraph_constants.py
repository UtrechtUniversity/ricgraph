# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
#
# Copyright (c) 2023 - 2025 Rik D.T. Janssen
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
# Ricgraph constants.
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, December 2022.
# Updated Rik D.T. Janssen, February, March, September to December 2023.
# Updated Rik D.T. Janssen, February to June, September to December  2024.
# Updated Rik D.T. Janssen, January to June 2025.
#
# ########################################################################


RICGRAPH_INI_FILENAME = 'ricgraph.ini'

# This one separates value & name in property _key of a node.
RICGRAPH_KEY_SEPARATOR = '|'
# If we find RICGRAPH_KEY_SEPARATOR in a string, replace it with this one.
RICGRAPH_KEY_SEPARATOR_REPLACEMENT = '_'

# For a non-unique 'value' field, this one separates 'value' & the
# unique string to concatenate. It may not be RICGRAPH_KEY_SEPARATOR.
RICGRAPH_VALUE_SEPARATOR = '#'
# If we find RICGRAPH_VALUE_SEPARATOR in 'value', replace it with this one.
RICGRAPH_VALUE_SEPARATOR_REPLACEMENT = '_'

# Used for some loop iterations, in case no max iteration for such a loop is specified.
A_LARGE_NUMBER = 9999999999

# For the REST API, we need to return an HTTP response status code. These are
# listed on https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml.
# For Ricgraph, we only use one HTTP response status code:
# https://www.rfc-editor.org/rfc/rfc9110.html#name-200-ok.
HTTP_RESPONSE_OK = 200
# We use these if an item cannot be found. They should be in the 2xx series
# since we still return a valid HTTP response. These are in the "unassigned" range,
# which may be freely used.
HTTP_RESPONSE_NOTHING_FOUND = 250
HTTP_RESPONSE_INVALID_SEARCH = 251

# The dict '_nodes_cache_key_id' is used to cache IDs to nodes. This is the cache size.
# The dict itself is defined in ricgraph_cache.py.
# This dict will be emptied if it reaches this number of elements.
MAX_NODES_CACHE_KEY_ID = 100000

# The dict '_nodes_cache_nodelink' is used to be able to pass nodes (i.e. links to Node)
# between the pages of Ricgraph Explorer.
# The dict itself is defined in ricgraph_cache.py.
# This dict will be emptied if it reaches this number of elements.
MAX_NODES_CACHE_NODELINK = 100000

# In merge_two_nodes(node_merge_from, node_merge_to), we are constructing a list of
# all the nodes that are to be merged with node_merge_to, to add to property _history
# in that node. This value restricts the length of that list (to prevent property
# values that are too long).
MAX_NR_HISTORYITEMS_TO_ADD = 50


# ########################################################################
# Research output types used in Ricgraph.
# Harvested sources most often have a type for a research output.
# In a harvest script for a certain source, you specify a mapping
# from the names used in the source you harvest, to the values below.
# This ensures that Ricgraph uses the same wording for types of
# research outputs harvested from different sources.
#
# An example mapping may look like this:
# mapping = {
#    'book': ROTYPE_BOOK,
#    'data set': ROTYPE_DATASET,
#    'software': ROTYPE_SOFTWARE
# }
#
# Call the function lookup_resout_type() to do this mapping.
# If you add a type, also add it to ROTYPE_ALL.
#
# This list is inspired by the Strategy Evaluation Protocol 2021-2027
# https://www.universiteitenvannederland.nl/files/documenten/Domeinen/Onderzoek/SEP_2021-2027.pdf,
# Appendix E2.
ROTYPE_ABSTRACT = 'abstract'
ROTYPE_BOOK = 'book'
ROTYPE_BOOKCHAPTER = 'book chapter'
ROTYPE_CONFERENCE_ARTICLE = 'conference article'
ROTYPE_DATASET = 'data set'
ROTYPE_DESIGN = 'design'
ROTYPE_DIGITAL_VISUAL_PRODUCT = 'digital or visual product'
ROTYPE_EDITORIAL = 'editorial'
ROTYPE_ENTRY = 'entry for encyclopedia or dictionary'
ROTYPE_EXHIBITION_PERFORMANCE = 'exhibition or performance'
ROTYPE_JOURNAL_ARTICLE = 'journal article'
ROTYPE_LETTER = 'letter to the editor'
ROTYPE_MEMORANDUM = 'memorandum'
ROTYPE_METHOD_DESCRIPTION = 'method description'
ROTYPE_MODEL = 'model'
ROTYPE_OTHER_CONTRIBUTION = 'other contribution'
ROTYPE_PATENT = 'patent'
ROTYPE_PHDTHESIS = 'PhD thesis'
ROTYPE_POSTER = 'poster'
ROTYPE_PREPRINT = 'preprint'
ROTYPE_PRESENTATION = 'presentation'
ROTYPE_REGISTERED_REPORT = 'registered report'
ROTYPE_REPORT = 'report'
ROTYPE_RETRACTION = 'retraction'
ROTYPE_REVIEW = 'review'
ROTYPE_SOFTWARE = 'software'
ROTYPE_THESIS = 'thesis'
ROTYPE_WEBSITE = 'website or web publication'

ROTYPE_ALL = [ROTYPE_ABSTRACT,
              ROTYPE_BOOK,
              ROTYPE_BOOKCHAPTER,
              ROTYPE_CONFERENCE_ARTICLE,
              ROTYPE_DATASET,
              ROTYPE_DESIGN,
              ROTYPE_DIGITAL_VISUAL_PRODUCT,
              ROTYPE_EDITORIAL,
              ROTYPE_ENTRY,
              ROTYPE_EXHIBITION_PERFORMANCE,
              ROTYPE_JOURNAL_ARTICLE,
              ROTYPE_LETTER,
              ROTYPE_MEMORANDUM,
              ROTYPE_METHOD_DESCRIPTION,
              ROTYPE_MODEL,
              ROTYPE_OTHER_CONTRIBUTION,
              ROTYPE_PATENT,
              ROTYPE_PHDTHESIS,
              ROTYPE_POSTER,
              ROTYPE_PREPRINT,
              ROTYPE_PRESENTATION,
              ROTYPE_REGISTERED_REPORT,
              ROTYPE_REPORT,
              ROTYPE_RETRACTION,
              ROTYPE_REVIEW,
              ROTYPE_SOFTWARE,
              ROTYPE_THESIS,
              ROTYPE_WEBSITE]
