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
# Research result related constants.
# ########################################################################

# ########################################################################
# Research result types used in Ricgraph.
# In Ricgraph, we use the general wording "research result" for anything
# that may be in any way the result of some research activity, direct
# or indirect.
# That means, that e.g. press media items, on which a researcher may
# not have any influence (e.g. an article in a newspaper) are also
# considered to be research results.
#
# Harvested sources most often have a type for a research result.
# In a harvest script for a certain source, you specify a mapping
# from the names used in the source you harvest, to the values below.
# This ensures that Ricgraph uses the same wording for types of
# research results harvested from different sources.
#
# An example mapping may look like this:
# mapping = {
#    'book': RESEARCHRESULT_CATEGORY_BOOK,
#    'data set': RESEARCHRESULT_CATEGORY_DATASET,
#    'software': RESEARCHRESULT_CATEGORY_SOFTWARE
# }
#
# Call the function lookup_researchresult_category() to do this mapping.
# If you add a type, also add it to RESEARCHRESULT_CATEGORY_ALL.
# If you add a type that is a publication, also add it to RESEARCHRESULT_CATEGORY_PUBLICATION.
#
# RESEARCHRESULT_CATEGORY_* are used in the Ricgraph 'category' field.
#
# This list is inspired by the Strategy Evaluation Protocol 2021-2027
# https://www.universiteitenvannederland.nl/files/documenten/Domeinen/Onderzoek/SEP_2021-2027.pdf,
# Appendix E2.
RESEARCHRESULT_CATEGORY_ABSTRACT = 'abstract'
RESEARCHRESULT_CATEGORY_ARTEFACT = 'artefact'
RESEARCHRESULT_CATEGORY_BOOK = 'book'
RESEARCHRESULT_CATEGORY_BOOKCHAPTER = 'book chapter'
RESEARCHRESULT_CATEGORY_CONFERENCE_ARTICLE = 'conference article'
RESEARCHRESULT_CATEGORY_DATASET = 'data set'
RESEARCHRESULT_CATEGORY_DESIGN = 'design'
RESEARCHRESULT_CATEGORY_DIGITAL_VISUAL_PRODUCT = 'digital or visual product'
RESEARCHRESULT_CATEGORY_EDITORIAL = 'editorial'
RESEARCHRESULT_CATEGORY_ENTRY = 'entry for encyclopedia or dictionary'
RESEARCHRESULT_CATEGORY_EXHIBITION_PERFORMANCE = 'exhibition or performance'
RESEARCHRESULT_CATEGORY_JOURNAL_ARTICLE = 'journal article'
RESEARCHRESULT_CATEGORY_LETTER = 'letter to the editor'
RESEARCHRESULT_CATEGORY_MEMORANDUM = 'memorandum'
RESEARCHRESULT_CATEGORY_METHOD_DESCRIPTION = 'method description'
RESEARCHRESULT_CATEGORY_MODEL = 'model'
RESEARCHRESULT_CATEGORY_OTHER_CONTRIBUTION = 'other contribution'
RESEARCHRESULT_CATEGORY_PATENT = 'patent'
RESEARCHRESULT_CATEGORY_PHDTHESIS = 'PhD thesis'
RESEARCHRESULT_CATEGORY_POSTER = 'poster'
RESEARCHRESULT_CATEGORY_PREPRINT = 'preprint'
RESEARCHRESULT_CATEGORY_PRESENTATION = 'presentation'
RESEARCHRESULT_CATEGORY_PRESS_MEDIA = 'press media'
RESEARCHRESULT_CATEGORY_REGISTERED_REPORT = 'registered report'
RESEARCHRESULT_CATEGORY_REPORT = 'report'
RESEARCHRESULT_CATEGORY_RETRACTION = 'retraction'
RESEARCHRESULT_CATEGORY_REVIEW = 'review'
RESEARCHRESULT_CATEGORY_SOFTWARE = 'software'
RESEARCHRESULT_CATEGORY_THESIS = 'thesis'
RESEARCHRESULT_CATEGORY_WEBSITE = 'website or web publication'


# ########################################################################
# This is a special research result type allowing to select all publication
# types.
RESEARCHRESULT_CATEGORY_PUBLICATION_ALL = 'publication_all'


# If you add something here, you may also want to add it to
# one or more of
# RESEARCHRESULT_CATEGORY_PUBLICATION,
# RESEARCHRESULT_CATEGORY_RESEARCH_MATERIAL,
# RESEARCHRESULT_CATEGORY_REPORTING_MATERIAL,
# RESEARCHRESULT_CATEGORY_ENGAGEMENT_MATERIAL.
RESEARCHRESULT_CATEGORY_ALL = \
    [RESEARCHRESULT_CATEGORY_ABSTRACT,
     RESEARCHRESULT_CATEGORY_ARTEFACT,
     RESEARCHRESULT_CATEGORY_BOOK,
     RESEARCHRESULT_CATEGORY_BOOKCHAPTER,
     RESEARCHRESULT_CATEGORY_CONFERENCE_ARTICLE,
     RESEARCHRESULT_CATEGORY_DATASET,
     RESEARCHRESULT_CATEGORY_DESIGN,
     RESEARCHRESULT_CATEGORY_DIGITAL_VISUAL_PRODUCT,
     RESEARCHRESULT_CATEGORY_EDITORIAL,
     RESEARCHRESULT_CATEGORY_ENTRY,
     RESEARCHRESULT_CATEGORY_EXHIBITION_PERFORMANCE,
     RESEARCHRESULT_CATEGORY_JOURNAL_ARTICLE,
     RESEARCHRESULT_CATEGORY_LETTER,
     RESEARCHRESULT_CATEGORY_MEMORANDUM,
     RESEARCHRESULT_CATEGORY_METHOD_DESCRIPTION,
     RESEARCHRESULT_CATEGORY_MODEL,
     RESEARCHRESULT_CATEGORY_OTHER_CONTRIBUTION,
     RESEARCHRESULT_CATEGORY_PATENT,
     RESEARCHRESULT_CATEGORY_PHDTHESIS,
     RESEARCHRESULT_CATEGORY_POSTER,
     RESEARCHRESULT_CATEGORY_PREPRINT,
     RESEARCHRESULT_CATEGORY_PRESENTATION,
     RESEARCHRESULT_CATEGORY_PRESS_MEDIA,
     RESEARCHRESULT_CATEGORY_REGISTERED_REPORT,
     RESEARCHRESULT_CATEGORY_REPORT,
     RESEARCHRESULT_CATEGORY_RETRACTION,
     RESEARCHRESULT_CATEGORY_REVIEW,
     RESEARCHRESULT_CATEGORY_SOFTWARE,
     RESEARCHRESULT_CATEGORY_THESIS,
     RESEARCHRESULT_CATEGORY_WEBSITE]

# A resout_type_all is defined in initialize_ricgraph_explorer().
# These are elements of RESEARCHRESULT_CATEGORY_ALL that are present in your Ricgraph.
# I.e., those have been harvested from the source systems that you chose to harvest.

RESEARCHRESULT_CATEGORY_PUBLICATION = \
    [RESEARCHRESULT_CATEGORY_ABSTRACT,
     RESEARCHRESULT_CATEGORY_BOOK,
     RESEARCHRESULT_CATEGORY_BOOKCHAPTER,
     RESEARCHRESULT_CATEGORY_CONFERENCE_ARTICLE,
     RESEARCHRESULT_CATEGORY_EDITORIAL,
     RESEARCHRESULT_CATEGORY_ENTRY,
     RESEARCHRESULT_CATEGORY_JOURNAL_ARTICLE,
     RESEARCHRESULT_CATEGORY_LETTER,
     RESEARCHRESULT_CATEGORY_MEMORANDUM,
     RESEARCHRESULT_CATEGORY_METHOD_DESCRIPTION,
     RESEARCHRESULT_CATEGORY_PATENT,
     RESEARCHRESULT_CATEGORY_PHDTHESIS,
     RESEARCHRESULT_CATEGORY_POSTER,
     RESEARCHRESULT_CATEGORY_PREPRINT,
     RESEARCHRESULT_CATEGORY_PRESENTATION,
     RESEARCHRESULT_CATEGORY_REGISTERED_REPORT,
     RESEARCHRESULT_CATEGORY_REPORT,
     RESEARCHRESULT_CATEGORY_RETRACTION,
     RESEARCHRESULT_CATEGORY_REVIEW,
     RESEARCHRESULT_CATEGORY_THESIS]

# A resout_type_pub is defined in initialize_ricgraph_explorer().
# These are elements of RESEARCHRESULT_CATEGORY_PUBLICATION that are present in your Ricgraph.
# I.e., those have been harvested from the source systems that you chose to harvest.


# ########################################################################
# Research result types related to open science monitoring.
RESEARCHRESULT_CATEGORY_RESEARCH_MATERIAL = \
    [RESEARCHRESULT_CATEGORY_DATASET,
     RESEARCHRESULT_CATEGORY_SOFTWARE]

RESEARCHRESULT_CATEGORY_REPORTING_MATERIAL = \
    [RESEARCHRESULT_CATEGORY_ABSTRACT,
     RESEARCHRESULT_CATEGORY_ARTEFACT,
     RESEARCHRESULT_CATEGORY_BOOK,
     RESEARCHRESULT_CATEGORY_BOOKCHAPTER,
     RESEARCHRESULT_CATEGORY_CONFERENCE_ARTICLE,
     RESEARCHRESULT_CATEGORY_DESIGN,
     RESEARCHRESULT_CATEGORY_EDITORIAL,
     RESEARCHRESULT_CATEGORY_ENTRY,
     RESEARCHRESULT_CATEGORY_JOURNAL_ARTICLE,
     RESEARCHRESULT_CATEGORY_LETTER,
     RESEARCHRESULT_CATEGORY_MEMORANDUM,
     RESEARCHRESULT_CATEGORY_METHOD_DESCRIPTION,
     RESEARCHRESULT_CATEGORY_OTHER_CONTRIBUTION,
     RESEARCHRESULT_CATEGORY_PHDTHESIS,
     RESEARCHRESULT_CATEGORY_POSTER,
     RESEARCHRESULT_CATEGORY_PREPRINT,
     RESEARCHRESULT_CATEGORY_PRESENTATION,
     RESEARCHRESULT_CATEGORY_REGISTERED_REPORT,
     RESEARCHRESULT_CATEGORY_REPORT,
     RESEARCHRESULT_CATEGORY_RETRACTION,
     RESEARCHRESULT_CATEGORY_REVIEW,
     RESEARCHRESULT_CATEGORY_THESIS]

RESEARCHRESULT_CATEGORY_ENGAGEMENT_MATERIAL = \
    [RESEARCHRESULT_CATEGORY_DIGITAL_VISUAL_PRODUCT,
     RESEARCHRESULT_CATEGORY_EXHIBITION_PERFORMANCE,
     RESEARCHRESULT_CATEGORY_MODEL,
     RESEARCHRESULT_CATEGORY_PATENT,
     RESEARCHRESULT_CATEGORY_PRESS_MEDIA,
     RESEARCHRESULT_CATEGORY_WEBSITE]


# ########################################################################
# Organization related constants.
# ########################################################################
ORGANIZATION_CATEGORY_ORGANISATION = 'organization'
ORGANIZATION_CATEGORY_ALL = \
    [ORGANIZATION_CATEGORY_ORGANISATION]


# ########################################################################
# Person related constants.
# ########################################################################
PERSON_CATEGORY_PERSON = 'person'
PERSON_CATEGORY_ALL = \
    [PERSON_CATEGORY_PERSON]


# ########################################################################
# Competence related constants.
# ########################################################################
COMPETENCE_CATEGORY_COMPETENCE= 'competence'
COMPETENCE_CATEGORY_ALL = \
    [COMPETENCE_CATEGORY_COMPETENCE]


# ########################################################################
# Project related constants.
# ########################################################################
PROJECT_CATEGORY_PROJECT = 'project'
PROJECT_CATEGORY_ALL = \
    [PROJECT_CATEGORY_PROJECT]
