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
# Ricgraph Explorer constants section.
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, January 2023.
# Extended Rik D.T. Janssen, February, September 2023 to May 2025.
#
# ########################################################################


from ricgraph import get_ricgraph_version


# Ricgraph Explorer is also a "discoverer". This parameter gives the
# default mode. Possibilities are:
# - details_view: show all the details.
# - person_view: show a person card, limit details (e.g. do not show _history & _source)
# Should be this:
# DEFAULT_DISCOVERER_MODE = 'person_view'
# But for development, this one is easier:
DEFAULT_DISCOVERER_MODE = 'details_view'

# You can search in two different ways in Ricgraph Explorer. This parameter
# gives the default mode. Possibilities are:
# exact_match: do a search on exact match, we call it 'advanced search'.
# value_search: do a broad search on field 'value'.
DEFAULT_SEARCH_MODE = 'value_search'

# Minimum length of a value in a search field (in characters).
SEARCH_STRING_MIN_LENGTH = 2

# Ricgraph Explorer shows tables. You can specify which columns you need.
# You do this by making a list of one or more fields in a Ricgraph node.
# There are some predefined lists.
DETAIL_COLUMNS = ['name', 'category', 'value', 'comment', 'year',
                  'url_main', 'url_other', '_source', '_history']
RESEARCH_OUTPUT_COLUMNS = ['name', 'category', 'value', 'comment',
                           'year', 'url_main', 'url_other']
ORGANIZATION_COLUMNS = ['name', 'value', 'comment', 'url_main']
ID_COLUMNS = ['name', 'value', 'comment', 'url_main']

# When we do a query, we return at most this number of nodes.
MAX_ITEMS = 250

# If we render a table, we return at most this number of rows in that table.
MAX_ROWS_IN_TABLE = 250

# If we export a table, we export at most this number of rows in that table.
MAX_ROWS_TO_EXPORT = 250

# It is possible to find enrichments for all nodes in Ricgraph. However, that
# will take a long time. This is the maximum number of nodes Ricgraph Explorer
# is going to enrich in find_enrich_candidates().
MAX_NR_NODES_TO_ENRICH = 20

# The location of the privacy statement and privacy measures file, if present.
# If one or both exist, they should be in the 'static' folder.
# A link is generated to this file, so it should be comprehensible to a browser.
PRIVACY_STATEMENT_FILE = 'privacy_statement.pdf'
PRIVACY_MEASURES_FILE = 'privacy_measures.pdf'

# The location of the home page intro text, if present.
# If it exists, it should be in the 'static' folder.
# It is included on the home page without further processing, expected to be in html format.
HOMEPAGE_INTRO_FILE = 'homepage_intro.html'

# These are all the 'view_mode's that are allowed.
VIEW_MODE_ALL = ['view_regular_table_personal',
                 'view_regular_table_organizations',
                 'view_regular_table_persons_of_org',
                 'view_regular_table_category',
                 'view_regular_table_overlap',
                 'view_regular_table_overlap_records',
                 'view_unspecified_table_resouts',
                 'view_unspecified_table_everything',
                 'view_unspecified_table_everything_except_ids',
                 'view_unspecified_table_organizations',
                 'view_regular_table_person_share_resouts',
                 'view_regular_table_person_enrich_source_system',
                 'view_regular_table_person_organization_collaborations',
                 'view_regular_table_organization_addinfo',
                 ]


# ########################################################################
# HTML button constants.
# ########################################################################
# The html 'width' of input fields or 'min-width' of buttons.
field_button_width = '30em'
# The style for the buttons, note the space before and after the text.
button_style = ' w3-button uu-yellow w3-round-large w3-mobile '
# A button with a black line around it.
button_style_border = button_style + ' w3-border rj-border-black '
# Restrict the width of a button. Use 'min-width' to make sure the text fits.
button_width = ' style="min-width:' + field_button_width + ';" '


# ########################################################################
# The HTML stylesheet.
# ########################################################################
stylesheet = '<style>'
# Scrollbar colors, see https://www.w3schools.com/howto/howto_css_custom_scrollbar.asp.
# Note that this is not supported in Firefox.
# Scrollbar width.
stylesheet += '::-webkit-scrollbar {width:10px;}'
# Scrollbar track.
stylesheet += '::-webkit-scrollbar-track {background-color:#e1e1e1;}'
# Scrollbar handle.
stylesheet += '::-webkit-scrollbar-thumb {background-color:#999;}'
# Scrollbar handle on hover.
stylesheet += '::-webkit-scrollbar-thumb:hover {background-color:#555;}'

stylesheet += '.w3-container {padding:16px;}'
# Note: #ffcd00 is 'uu-yellow' below.
stylesheet += '.w3-check {width:15px; height:15px; position:relative; top:3px; accent-color:#ffcd00;}'
stylesheet += '.w3-radio {accent-color: #ffcd00;}'
# Restrict the width of the input fields.
stylesheet += '.w3-input {width:' + field_button_width + ';}'
# Define UU colors. We do not need to define "black" and "white" (they do exist).
# See https://www.uu.nl/organisatie/huisstijl/huisstijlelementen/kleur.
stylesheet += '.uu-yellow, .uu-hover-yellow:hover '
stylesheet += '{color:#000!important; background-color:#ffcd00!important;}'
stylesheet += '.uu-red, .uu-hover-red:hover '
stylesheet += '{color:#000!important; background-color:#c00a35!important;}'
stylesheet += '.uu-orange, .uu-hover-orange:hover '
stylesheet += '{color:#000!important; background-color:#f3965e!important;}'
stylesheet += '.uu-blue, .uu-hover-blue:hover '
stylesheet += '{color:#000!important; background-color:#5287c6!important;}'
stylesheet += '.rj-gray, .rj-hover-gray:hover '
stylesheet += '{color:#000!important; background-color:#cecece!important;}'
stylesheet += '.rj-border-black, .rj-hover-border-black:hover {border-color:#000!important;}'
stylesheet += 'body {background-color:white;}'
stylesheet += 'body, h1, h2, h3, h4, h5, h6 {font-family:"Open Sans",sans-serif;}'
stylesheet += 'ul {padding-left:2em; margin:0px}'
stylesheet += 'a:link, a:visited {color:blue;}'
stylesheet += 'a:hover {color:darkblue;}'
stylesheet += 'table {font-size:85%;}'
stylesheet += 'table, th, td {border-collapse:collapse; border:1px solid black}'
stylesheet += 'th {text-align:left;}'
# Style for tabbed html table header.
stylesheet += '.tablink {font-size:85%;}'
# Style for faceted box.
stylesheet += '.facetedform {font-size:90%;}'
# For table sorting. \u00a0 is a non-breaking space.
stylesheet += 'table.sortable th:not(.sorttable_sorted):not(.sorttable_sorted_reverse)'
stylesheet += ':not(.sorttable_nosort):after{content:"\u00a0\u25b4\u00a0\u25be"}'

# In Firefox, dropdown lists do not have a downward triangle, as Brave, Chrome and Edge have.
# To give the user a clue that there is a dropdown list, we show additional text.
# This is done as follows:
# <div class="firefox-only">Click twice to get a dropdown list.</div>
# We need the following css to make this happen:
# To hide by default in any browser.
stylesheet += '.firefox-only {display: none;}'
# To show only in Firefox.
stylesheet += '@-moz-document url-prefix() {.firefox-only'
stylesheet += '{display:block; font-size:80%; font-style:italic;}}'
# End of Firefox dropdown list css.

stylesheet += '</style>'


# ########################################################################
# The HTML preamble
# ########################################################################
html_preamble = '<meta charset="utf-8">'
html_preamble += '<meta name="author" content="Rik D.T. Janssen">'
html_preamble += '<meta name="description" content="Ricgraph - Research in context graph">'
html_preamble += '<meta name="keywords" content="Ricgraph, Ricgraph Explorer, Ricgraph REST API">'
html_preamble += '<meta name="viewport" content="width=device-width, initial-scale=1">'
# The W3.css style file is at https://www.w3schools.com/w3css/4/w3.css. I use the "pro" version.
# The pro version is identical to the standard version except for it has no colors defined.
html_preamble += '<link rel="stylesheet" href="/static/w3pro.css">'
html_preamble += '<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Open+Sans">'


# ########################################################################
# The HTML page header.
# ########################################################################
page_header = '<header class="w3-container uu-yellow">'
page_header += '<div class="w3-bar uu-yellow">'
page_header += '<a href="javascript:history.back()" class="w3-bar-item" style="font-size:80%; padding-top:0px;'
page_header += 'padding-bottom:0px; padding-right:0px; writing-mode:vertical-rl; transform:rotate(180deg);">Go back</a>'
page_header += '<div class="w3-bar-item w3-mobile" style="padding-left:0em; padding-right:2em;">'
page_header += '<a href="/" style="text-decoration:none; color:#000000; font-size:130%;">'
page_header += '<img src="/static/uu_logo_small.png" height="30" style="padding-right:2em;">'
page_header += '<img src="/static/ricgraph_logo.png" height="30" style="padding-right:0.5em;">Explorer</a>'
page_header += '</div>'
page_header += '<a href="/" class="w3-bar-item'
page_header += button_style_border + '" style="min-width:10em;">Home</a>'
page_header += '<a href="/searchpage/?search_mode=value_search" class="w3-bar-item'
page_header += button_style_border + '" style="min-width:10em;">Broad search</a>'
page_header += '<a href="/searchpage/?search_mode=exact_match" class="w3-bar-item'
page_header += button_style_border + '" style="min-width:10em;">Advanced search</a>'
page_header += '<a href="/restapidocpage/" class="w3-bar-item'
page_header += button_style_border + '" style="min-width:10em;margin-left:2em;">REST API doc</a>'
page_header += '</div>'
page_header += '</header>'


# ########################################################################
# The HTML page footer.
# ########################################################################
page_footer_general = 'For more information about Ricgraph, Ricgraph Explorer, and the Ricgraph REST API, '
page_footer_general += 'please read the reference publication '
page_footer_general += '<a href="https://doi.org/10.1016/j.softx.2024.101736">'
page_footer_general += 'https://doi.org/10.1016/j.softx.2024.101736</a>, '
page_footer_general += 'visit the website <a href=https://www.ricgraph.eu>www.ricgraph.eu</a>, '
page_footer_general += 'or go to the GitHub repository '
page_footer_general += '<a href=https://github.com/UtrechtUniversity/ricgraph>'
page_footer_general += 'https://github.com/UtrechtUniversity/ricgraph</a>. '
page_footer_general += 'This site uses Ricgraph version ' + get_ricgraph_version() + '.'

page_footer_development = '<footer class="w3-container rj-gray" style="font-size:80%">'
page_footer_development += 'You are using Ricgraph Explorer in development mode. '
page_footer_development += 'Do only use this for research use, not for production use. '
page_footer_development += page_footer_general
page_footer_development += '</footer>'

page_footer_wsgi = '<footer class="w3-container rj-gray" style="font-size:80%">'
page_footer_wsgi += 'You are using Ricgraph Explorer with a '
page_footer_wsgi += 'WSGI Gunicorn server using Uvicorn for ASGI applications. '
page_footer_wsgi += page_footer_general
page_footer_wsgi += '</footer>'


# ########################################################################
# The first part of the HTML page, up to stylesheet and page_header.
# ########################################################################
html_body_start = '<!DOCTYPE html>'
html_body_start += '<html>'
html_body_start += '<head>'
html_body_start += html_preamble
html_body_start += stylesheet
html_body_start += '<title>Ricgraph Explorer</title>'
# Define two global JavaScript arrays to be used in get_regular_table().
html_body_start += '<script>let currentPage = []; let totalPages = [];</script>'
html_body_start += '</head>'
html_body_start += '<body>'
html_body_start += page_header


# ########################################################################
# The last part of the HTML page, from page_footer (not included) to script inclusion.
# ########################################################################
html_body_end = '<script src="/static/ricgraph_sorttable.js"></script>'
# Required for the Observable D3 and Observable Plot framework for data visualization,
# https://d3js.org and https://observablehq.com/plot.
html_body_end += '<script src="/static/d3.min.js"></script>'
html_body_end += '<script src="/static/plot.min.js"></script>'
html_body_end += '</body>'
html_body_end += '</html>'
