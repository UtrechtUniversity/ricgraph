# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
#
# Copyright (c) 2023 - 2026 Rik D.T. Janssen
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
# Updated Rik D.T. Janssen, January to June 2025, March 2026.
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
# A cache entry is approx. 20 - 30 bytes. 30 x 2000000 ~ 60MB.
MAX_NODES_CACHE_KEY_ID = 2000000

# In merge_two_nodes(node_merge_from, node_merge_to), we are constructing a list of
# all the nodes that are to be merged with node_merge_to, to add to property _history
# in that node. This value restricts the length of that list (to prevent property
# values that are too long).
MAX_NR_HISTORYITEMS_TO_ADD = 50

# The maximum length of the organization abbreviation.
MAX_ORG_ABBREVIATION_LENGTH = 4


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
#    'book': ROCATEGORY_BOOK,
#    'data set': ROCATEGORY_DATASET,
#    'software': ROCATEGORY_SOFTWARE
# }
#
# Call the function lookup_resout_category() to do this mapping.
# If you add a type, also add it to ROCATEGORY_ALL.
# If you add a type that is a publication, also add it to ROCATEGORY_PUBLICATION.
#
# ROCATEGORY_* are used in the Ricgraph 'category' field.
#
# This list is inspired by the Strategy Evaluation Protocol 2021-2027
# https://www.universiteitenvannederland.nl/files/documenten/Domeinen/Onderzoek/SEP_2021-2027.pdf,
# Appendix E2.
ROCATEGORY_ABSTRACT = 'abstract'
ROCATEGORY_ARTEFACT = 'artefact'
ROCATEGORY_BOOK = 'book'
ROCATEGORY_BOOKCHAPTER = 'book chapter'
ROCATEGORY_CONFERENCE_ARTICLE = 'conference article'
ROCATEGORY_DATASET = 'data set'
ROCATEGORY_DESIGN = 'design'
ROCATEGORY_DIGITAL_VISUAL_PRODUCT = 'digital or visual product'
ROCATEGORY_EDITORIAL = 'editorial'
ROCATEGORY_ENTRY = 'entry for encyclopedia or dictionary'
ROCATEGORY_EXHIBITION_PERFORMANCE = 'exhibition or performance'
ROCATEGORY_JOURNAL_ARTICLE = 'journal article'
ROCATEGORY_LETTER = 'letter to the editor'
ROCATEGORY_MEMORANDUM = 'memorandum'
ROCATEGORY_METHOD_DESCRIPTION = 'method description'
ROCATEGORY_MODEL = 'model'
ROCATEGORY_OTHER_CONTRIBUTION = 'other contribution'
ROCATEGORY_PATENT = 'patent'
ROCATEGORY_PHDTHESIS = 'PhD thesis'
ROCATEGORY_POSTER = 'poster'
ROCATEGORY_PREPRINT = 'preprint'
ROCATEGORY_PRESENTATION = 'presentation'
ROCATEGORY_REGISTERED_REPORT = 'registered report'
ROCATEGORY_REPORT = 'report'
ROCATEGORY_RETRACTION = 'retraction'
ROCATEGORY_REVIEW = 'review'
ROCATEGORY_SOFTWARE = 'software'
ROCATEGORY_THESIS = 'thesis'
ROCATEGORY_WEBSITE = 'website or web publication'

# ########################################################################
# This is a special research output type allowing to select all publication
# types.
ROCATEGORY_PUBLICATION_ALL = 'publication_all'


ROCATEGORY_ALL = [ROCATEGORY_ABSTRACT,
                  ROCATEGORY_ARTEFACT,
                  ROCATEGORY_BOOK,
                  ROCATEGORY_BOOKCHAPTER,
                  ROCATEGORY_CONFERENCE_ARTICLE,
                  ROCATEGORY_DATASET,
                  ROCATEGORY_DESIGN,
                  ROCATEGORY_DIGITAL_VISUAL_PRODUCT,
                  ROCATEGORY_EDITORIAL,
                  ROCATEGORY_ENTRY,
                  ROCATEGORY_EXHIBITION_PERFORMANCE,
                  ROCATEGORY_JOURNAL_ARTICLE,
                  ROCATEGORY_LETTER,
                  ROCATEGORY_MEMORANDUM,
                  ROCATEGORY_METHOD_DESCRIPTION,
                  ROCATEGORY_MODEL,
                  ROCATEGORY_OTHER_CONTRIBUTION,
                  ROCATEGORY_PATENT,
                  ROCATEGORY_PHDTHESIS,
                  ROCATEGORY_POSTER,
                  ROCATEGORY_PREPRINT,
                  ROCATEGORY_PRESENTATION,
                  ROCATEGORY_REGISTERED_REPORT,
                  ROCATEGORY_REPORT,
                  ROCATEGORY_RETRACTION,
                  ROCATEGORY_REVIEW,
                  ROCATEGORY_SOFTWARE,
                  ROCATEGORY_THESIS,
                  ROCATEGORY_WEBSITE]

# A resout_type_all is defined in initialize_ricgraph_explorer().
# These are elements of ROCATEGORY_ALL that are present in your Ricgraph.
# I.e., those have been harvested from the source systems that you chose to harvest.

ROCATEGORY_PUBLICATION = [ROCATEGORY_ABSTRACT,
                          ROCATEGORY_BOOK,
                          ROCATEGORY_BOOKCHAPTER,
                          ROCATEGORY_CONFERENCE_ARTICLE,
                          ROCATEGORY_EDITORIAL,
                          ROCATEGORY_ENTRY,
                          ROCATEGORY_JOURNAL_ARTICLE,
                          ROCATEGORY_LETTER,
                          ROCATEGORY_MEMORANDUM,
                          ROCATEGORY_METHOD_DESCRIPTION,
                          ROCATEGORY_PATENT,
                          ROCATEGORY_PHDTHESIS,
                          ROCATEGORY_POSTER,
                          ROCATEGORY_PREPRINT,
                          ROCATEGORY_PRESENTATION,
                          ROCATEGORY_REGISTERED_REPORT,
                          ROCATEGORY_REPORT,
                          ROCATEGORY_RETRACTION,
                          ROCATEGORY_REVIEW,
                          ROCATEGORY_THESIS]

# A resout_type_pub is defined in initialize_ricgraph_explorer().
# These are elements of ROCATEGORY_PUBLICATION that are present in your Ricgraph.
# I.e., those have been harvested from the source systems that you chose to harvest.


# ########################################################################
# Other types used in Ricgraph.
CATEGORY_PRESS_MEDIA = 'press media'


# ########################################################################
# Types related to open science monitoring.
ROCATEGORY_RESEARCH_MATERIAL = [ROCATEGORY_DATASET,
                                ROCATEGORY_SOFTWARE]

ROCATEGORY_REPORTING_MATERIAL = [ROCATEGORY_ABSTRACT,
                                 ROCATEGORY_ARTEFACT,
                                 ROCATEGORY_BOOK,
                                 ROCATEGORY_BOOKCHAPTER,
                                 ROCATEGORY_CONFERENCE_ARTICLE,
                                 ROCATEGORY_DESIGN,
                                 ROCATEGORY_EDITORIAL,
                                 ROCATEGORY_ENTRY,
                                 ROCATEGORY_JOURNAL_ARTICLE,
                                 ROCATEGORY_LETTER,
                                 ROCATEGORY_MEMORANDUM,
                                 ROCATEGORY_METHOD_DESCRIPTION,
                                 ROCATEGORY_OTHER_CONTRIBUTION,
                                 ROCATEGORY_PHDTHESIS,
                                 ROCATEGORY_POSTER,
                                 ROCATEGORY_PREPRINT,
                                 ROCATEGORY_PRESENTATION,
                                 ROCATEGORY_REGISTERED_REPORT,
                                 ROCATEGORY_REPORT,
                                 ROCATEGORY_RETRACTION,
                                 ROCATEGORY_REVIEW,
                                 ROCATEGORY_THESIS]

ROCATEGORY_ENGAGEMENT_MATERIAL = [ROCATEGORY_DIGITAL_VISUAL_PRODUCT,
                                  ROCATEGORY_EXHIBITION_PERFORMANCE,
                                  ROCATEGORY_MODEL,
                                  ROCATEGORY_PATENT,
                                  CATEGORY_PRESS_MEDIA,
                                  ROCATEGORY_WEBSITE]
