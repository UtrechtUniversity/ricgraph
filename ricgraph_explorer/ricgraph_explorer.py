# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
#
# Copyright (c) 2023, 2024 Rik D.T. Janssen
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
# This file is Ricgraph Explorer, a web based tool to access nodes in
# Ricgraph.
# The purpose is to illustrate how web based access using Flask can be done.
# To keep it simple, everything is contained in this file (except for
# some static files, which are in ../static).
#
# Please note that this code is meant for research purposes,
# not for production use. That means, this code has not been hardened for
# "the outside world". Be careful if you expose it to the outside world.
# At least use a web server such as Apache combined with a WSGI server.
# Please read the documentation to learn how to do that, and to find
# example configuration files.
#
# Original version Rik D.T. Janssen, January 2023.
# Extended Rik D.T. Janssen, February, September 2023 to December 2024.
#
# ########################################################################
#
# For table sorting. Ricgraph Explorer uses sorttable.js.
# It is copied from https://www.kryogenix.org/code/browser/sorttable
# on February 1, 2023. At that link, you'll find a how-to. It is licensed under X11-MIT.
# It is renamed to ricgraph_sorttable.js since it has a small modification
# related to case-insensitive sorting. The script is included in html_body_end.
#
# ##############################################################################
#
# Ricgraph Explorer uses W3.CSS, a modern, responsive, mobile first CSS framework.
# See https://www.w3schools.com/w3css/default.asp.
#
# ##############################################################################
#
# Explanation why sometimes Cypher queries are used.
# In some cases, Ricgraph Explorer uses a Cypher query instead of function calls
# that go from node to edges to neighbor nodes and so on.
# Sometimes, these calls can be slow, especially if:
# - the start node has a large number of neighbors (this may be the case with
#   top level organization nodes, e.g. with 'Utrecht University'), AND
# - the node type you'd want to find (in name_list and/or category_list) has
#   only a few matching nodes in Ricgraph (e.g. there are only a few 'competence'
#   or 'patent' nodes).
#
# I assume Cypher is faster because Python is an interpreted language, so loops
# may be a bit slow. In case a loop runs over a large number of nodes or edges,
# many calls to the graph database backend are done, which may take a lot of time.
# A cypher query is one call to the graph database backend. Also, there are
# many query optimizations in that backend, and the backend is a compiled application.
#
# ##############################################################################

import random
import string
import json
import os
import sys
import urllib.parse
import uuid
from typing import Union, Tuple
from math import ceil, floor
from neo4j.graph import Node
import connexion.options
from flask import request, url_for, send_from_directory, current_app
from markupsafe import escape
import ricgraph as rcg

# We don't show the Swagger REST API page, we use RapiDoc for that (see restapidocpage()
# endpoint below). 'swagger_ui_options' is taken from
# https://connexion.readthedocs.io/en/latest/swagger_ui.html#connexion.options.SwaggerUIOptions.
# 'swagger_ui_config' options are on this page:
# https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration
swagger_ui_options = connexion.options.SwaggerUIOptions(swagger_ui=False)
ricgraph_explorer = connexion.FlaskApp(import_name=__name__,
                                       specification_dir='./static/',
                                       swagger_ui_options=swagger_ui_options)
ricgraph_explorer.add_api(specification='openapi.yaml',
                          swagger_ui_options=swagger_ui_options)


# ########################################################################
# Start of constants section
# ########################################################################

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

# Miniumum length of a value in a search field (in characters).
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
MAX_ITEMS = '250'

# If we render a table, we return at most this number of rows in that table.
MAX_ROWS_IN_TABLE = '250'

# If we search for neighbors of an 'organization' node, in the first filter
# in filterorganization(), we restrict it to return at most this number of nodes.
MAX_ORGANIZATION_NODES_TO_RETURN = 4 * MAX_ROWS_IN_TABLE

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

# The dict 'nodes_cache' is used to be able to pass nodes (i.e. links to Node)
# between the pages of this application. If we would not do this, we would need
# to search the node again every time we go to a new page. Then we would
# lose the advantage of using a graph.
# I could have used rcg.read_node() with @ricgraph_lru_cache, but I'd prefer to be
# able to store any node in the cache at the moment I prefer, as is done
# in function get_regular_table()).
# This dict has the format: [Ricgraph _key]: [Node link]
nodes_cache = {}

# These will be defined in initialize_ricgraph_explorer()
global graph
global name_all, name_personal_all, category_all, source_all, resout_types_all
global name_all_datalist, category_all_datalist, source_all_datalist, resout_types_all_datalist
global personal_types_all, remainder_types_all
global privacy_statement_link, privacy_measures_link
global homepage_intro_html
global page_footer

# The html 'width' of input fields or 'min-width' of buttons.
field_button_width = '30em'
# The style for the buttons, note the space before and after the text.
button_style = ' w3-button uu-yellow w3-round-large w3-mobile '
# A button with a black line around it.
button_style_border = button_style + ' w3-border rj-border-black '
# Restrict the width of a button. Use 'min-width' to make sure the text fits.
button_width = ' style="min-width:' + field_button_width + ';" '

# The html stylesheet.
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

# The html preamble
html_preamble = '<meta charset="utf-8">'
html_preamble += '<meta name="author" content="Rik D.T. Janssen">'
html_preamble += '<meta name="description" content="Ricgraph - Research in context graph">'
html_preamble += '<meta name="keywords" content="Ricgraph, Ricgraph Explorer, Ricgraph REST API">'
html_preamble += '<meta name="viewport" content="width=device-width, initial-scale=1">'
# The W3.css style file is at https://www.w3schools.com/w3css/4/w3.css. I use the "pro" version.
# The pro version is identical to the standard version except for it has no colors defined.
html_preamble += '<link rel="stylesheet" href="/static/w3pro.css">'
html_preamble += '<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Open+Sans">'

# The html page header.
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

# The html page footer.
page_footer_general = 'For more information about Ricgraph, Ricgraph Explorer, and the Ricgraph REST API, '
page_footer_general += 'please read the reference publication '
page_footer_general += '<a href="https://doi.org/10.1016/j.softx.2024.101736">'
page_footer_general += 'https://doi.org/10.1016/j.softx.2024.101736</a>, '
page_footer_general += 'visit the website <a href=https://www.ricgraph.eu>www.ricgraph.eu</a>, '
page_footer_general += 'or go to the GitHub repository '
page_footer_general += '<a href=https://github.com/UtrechtUniversity/ricgraph>'
page_footer_general += 'https://github.com/UtrechtUniversity/ricgraph</a>. '
page_footer_general += 'This site uses Ricgraph version ' + rcg.get_ricgraph_version() + '.'

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

# The first part of the html page, up to stylesheet and page_header.
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

# The last part of the html page, from page_footer (not included) to script inclusion.
html_body_end = '<script src="/static/ricgraph_sorttable.js"></script>'
# Required for the Observable D3 and Observable Plot framework for data visualization,
# https://d3js.org and https://observablehq.com/plot.
html_body_end += '<script src="/static/d3.min.js"></script>'
html_body_end += '<script src="/static/plot.min.js"></script>'
html_body_end += '</body>'
html_body_end += '</html>'


# ##############################################################################
# Favicon
# ##############################################################################
@ricgraph_explorer.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(ricgraph_explorer.app.root_path, 'static'),
                               path='favicon.ico',
                               mimetype='image/png')


# ##############################################################################
# Entry functions.
# Ricgraph Explorer has these web pages:
# 1. homepage.
# 2. searchpage:
# 2a. if there is more than one result: select a node from a list of nodes,
#     go to optionspage.
# 2b. if there is just one result: go to optionspage.
# 3. optionspage, this page depends on the node type found.
# 3. resultspage, this page depends on what the user would like to see.
# 4. restapidocpage, this page shows the documentation of the REST API.
# ##############################################################################
@ricgraph_explorer.route(rule='/')
def homepage() -> str:
    """Ricgraph Explorer entry, the home page, when you access '/'.

    :return: html to be rendered.
    """
    global html_body_start, html_body_end, page_footer
    global source_all, category_all
    global homepage_intro_html

    get_all_globals_from_app_context()
    html = html_body_start
    html += get_html_for_cardstart()
    html += '<h3>Ricgraph - Research in context graph</h3>'
    html += 'Ricgraph, also known as Research in context graph, enables the exploration of researchers, '
    html += 'teams, their results, '
    html += 'collaborations, skills, projects, and the relations between these items. '
    html += 'Ricgraph can store many types of items into a single graph (network). '
    html += 'These items can be obtained from various systems and from '
    html += 'multiple organizations. '
    html += 'Ricgraph facilitates reasoning about these '
    html += 'items because it infers new relations between items, '
    html += 'relations that are not present in any of the separate source systems. '
    html += 'It is flexible and extensible, and can be adapted to new application areas. '

    html += '<p/>'
    html += homepage_intro_html
    html += '<p/>'

    html += 'You can use Ricgraph Explorer to explore Ricgraph. '
    html += 'There are various methods to start exploring:'
    html += '<p/>'
    html += create_html_form(destination='searchpage',
                             button_text='search for a person',
                             hidden_fields={'search_mode': 'value_search',
                                            'name': 'FULL_NAME'
                                            })
    html += '<p/>'
    html += create_html_form(destination='searchpage',
                             button_text='search for a (sub-)organization',
                             hidden_fields={'search_mode': 'value_search',
                                            'category': 'organization'
                                            })
    html += '<p/>'
    if 'competence' in category_all:
        html += create_html_form(destination='searchpage',
                                 button_text='search for a skill, expertise area or research area',
                                 hidden_fields={'search_mode': 'value_search',
                                                'category': 'competence'
                                                })
        html += '<p/>'
    html += create_html_form(destination='searchpage',
                             button_text='search for anything (broad search)',
                             hidden_fields={'search_mode': 'value_search'
                                            })
    html += '<p/>'
    html += create_html_form(destination='searchpage',
                             button_text='advanced search',
                             hidden_fields={'search_mode': 'exact_match'
                                            })
    html += '<p/>'
    html += get_html_for_cardend()

    html += get_html_for_cardstart()
    nr_nodes = rcg.ricgraph_nr_nodes()
    nr_edges = rcg.ricgraph_nr_edges()
    html += '<h4>About Ricgraph</h4>'
    html += 'More information:'
    html += '<ul>'
    html += '<li>'
    html += 'For a gentle introduction in Ricgraph, please read the reference publication: '
    html += 'Rik D.T. Janssen (2024). Ricgraph: A flexible and extensible graph to explore research in '
    html += 'context from various systems. <em>SoftwareX</em>, 26(101736). '
    html += '<a href="https://doi.org/10.1016/j.softx.2024.101736">https://doi.org/10.1016/j.softx.2024.101736</a>. '
    html += '</li>'
    html += '<li>'
    html += 'Extensive documentation, publications, videos and source code can be found in the GitHub repository '
    html += '<a href="https://github.com/UtrechtUniversity/ricgraph">'
    html += 'https://github.com/UtrechtUniversity/ricgraph</a>. '
    html += '</li>'
    html += '<li>'
    html += 'If you use or refer to Ricgraph, please cite both the reference publication '
    html += '(<a href="https://doi.org/10.1016/j.softx.2024.101736">https://doi.org/10.1016/j.softx.2024.101736</a>), '
    html += 'and the software '
    html += '(<a href="https://doi.org/10.5281/zenodo.7524314">https://doi.org/10.5281/zenodo.7524314</a>).'
    html += '</li>'
    html += '</ul>'
    html += '<br/>'
    html += 'What to find in this instance of Ricgraph:'
    html += '<ul>'
    html += '<li>'
    html += 'Items from the following source systems: '
    if len(source_all) == 0:
        html += '[no source systems harvested yet]'
    else:
        html += ', '.join([str(source) for source in source_all])
    html += '.'
    html += '</li>'
    html += '<li>'
    html += 'Types of items: '
    if len(name_all) == 0:
        html += '[no items yet]'
    else:
        html += ', '.join([str(name) for name in name_all])
    html += '.'
    html += '</li>'
    html += '<li>'
    html += 'Types of items that contain personal data: '
    if len(name_personal_all) == 0:
        html += '[no items that contain personal data yet]'
    else:
        html += ', '.join([str(name_personal) for name_personal in name_personal_all])
    html += '.'
    html += '</li>'
    html += '<li>'
    html += str(nr_nodes) + ' nodes and ' + str(nr_edges) + ' edges.'
    html += '</li>'
    html += '<li>'
    html += 'The node cache has ' + str(len(nodes_cache)) + ' elements, and its size is '
    html += str(round(sys.getsizeof(nodes_cache)/1000, 1)) + ' kB.'
    html += '</li>'
    html += '</ul>'
    html += get_html_for_cardend()
    html += page_footer + html_body_end
    return html


@ricgraph_explorer.route(rule='/searchpage/', methods=['GET'])
def searchpage() -> str:
    """Ricgraph Explorer entry, this 'page' shows the search form, both the
    exact match search form and the broad search on the 'value' field form.

    Possible parameters are:
    - discoverer_mode: the discoverer_mode to use, 'details_view' to see all details,
      or 'person_view' to have a nicer layout.
    - search_mode: the search_mode to use, 'exact_match' or 'value_search' (broad
      search on field 'value').

    returns html to parse.
    """
    global html_body_start, html_body_end, page_footer
    global name_all_datalist, category_all, category_all_datalist

    get_all_globals_from_app_context()
    name = get_url_parameter_value(parameter='name')
    category = get_url_parameter_value(parameter='category')
    search_mode = get_url_parameter_value(parameter='search_mode',
                                          allowed_values=['exact_match', 'value_search'],
                                          default_value=DEFAULT_SEARCH_MODE)
    discoverer_mode = get_url_parameter_value(parameter='discoverer_mode',
                                              allowed_values=['details_view', 'person_view'],
                                              default_value=DEFAULT_DISCOVERER_MODE)
    max_nr_items = get_url_parameter_value(parameter='max_nr_items',
                                           default_value=MAX_ITEMS)
    if not max_nr_items.isnumeric():
        # This also catches negative numbers, they contain a '-' and are not numeric.
        # See https://www.w3schools.com/python/ref_string_isnumeric.asp.
        max_nr_items = MAX_ITEMS
    max_nr_table_rows = get_url_parameter_value(parameter='max_nr_table_rows',
                                                default_value=MAX_ROWS_IN_TABLE)
    if not max_nr_table_rows.isnumeric():
        max_nr_table_rows = MAX_ROWS_IN_TABLE
    html = html_body_start
    html += get_html_for_cardstart()

    form = '<form method="get" action="/optionspage/">'
    if search_mode == 'exact_match':
        form += '<label>Search for a value in Ricgraph field <em>name</em>:</label>'
        form += '<input class="w3-input w3-border" list="name_all_datalist"'
        form += 'name=name id=name autocomplete=off>'
        form += '<div class="firefox-only">Click twice to get a dropdown list.</div>'
        form += name_all_datalist
        form += '<br/>'

        form += '<label>Search for a value in Ricgraph field <em>category</em>:</label>'
        form += '<input class="w3-input w3-border" list="category_all_datalist"'
        form += 'name=category id=category autocomplete=off>'
        form += '<div class="firefox-only">Click twice to get a dropdown list.</div>'
        form += category_all_datalist
        form += '<br/>'
    if search_mode == 'value_search' and name != '':
        form += '<input type="hidden" name="name" value=' + name + '>'
    if search_mode == 'value_search' and category != '':
        form += '<input type="hidden" name="category" value=' + category + '>'
    if search_mode == 'exact_match':
        form += '<label>Search for a value in Ricgraph field <em>value</em>:</label>'
    else:
        form += '<label>Type your search string:</label>'
    form += '<input class="w3-input w3-border" type=text name=value>'
    form += '<input type="hidden" name="search_mode" value=' + search_mode + '>'

    if search_mode == 'exact_match':
        form += 'These fields are case-sensitive and use exact match search. '
        form += 'If you enter values in more than one field, these fields are combined using AND.</br>'

    radio_person_text = ' <em>person_view</em>: only show relevant columns, '
    radio_person_text += 'results are presented in a <em>tabbed</em> format '
    radio_person_tooltip = '<img src="/static/circle_info_solid_uuyellow.svg">'
    radio_person_tooltip += '<div class="w3-text" style="margin-left:60px;">'
    radio_person_tooltip += 'This view presents results in a <em>tabbed</em> format. '
    radio_person_tooltip += 'Also, tables have less columns to reduce information overload. '
    if 'competence' in category_all:
        radio_person_tooltip += 'This view has been tailored to the Utrecht University staff pages, since some '
        radio_person_tooltip += 'of these pages also include expertise areas, research areas, skills or photos. '
        radio_person_tooltip += 'These will be presented in a different way using lists. '
    radio_person_tooltip += '</div>'

    radio_details_text = ' <em>details_view</em>: show all columns, '
    radio_details_text += 'research results are presented in a table with <em>facets</em> '
    radio_details_tooltip = '<img src="/static/circle_info_solid_uuyellow.svg">'
    radio_details_tooltip += '<div class="w3-text" style="margin-left:60px;"> '
    radio_details_tooltip += 'This view shows all columns in Ricgraph. '
    radio_details_tooltip += 'Research results are presented in a table with <em>facets</em>. '
    radio_details_tooltip += '</div>'

    form += '<br/>Please specify how you like to view your results:<br/>'
    form += '<input class="w3-radio" type="radio" name="discoverer_mode" value="person_view"'
    if discoverer_mode == 'person_view':
        form += 'checked'
    form += '>' + radio_person_text
    form += '<label class="w3-tooltip">' + radio_person_tooltip + '</label><br/>'
    form += '<input class="w3-radio" type="radio" name="discoverer_mode" value="details_view"'
    if discoverer_mode == 'details_view':
        form += 'checked'
    form += '>' + radio_details_text
    form += '<label class="w3-tooltip">' + radio_details_tooltip + '</label><br/>'

    form += '</br>'
    tooltip = '<img src="/static/circle_info_solid_uuyellow.svg">'
    tooltip += '<div class="w3-text" style="margin-left:60px;"> '
    tooltip += 'More items will take more time, since they all have to be processed. '
    tooltip += '</div>'
    form += 'You might want to specify the maximum number of items to return, '
    form += 'or 0 to return all items (the more items, the more time it will take): '
    form += '<label class="w3-tooltip">' + tooltip + '</label><br/>'
    form += '<input class="w3-input w3-border" type=text value=' + max_nr_items + ' name=max_nr_items>'

    form += '</br>'
    tooltip = '<img src="/static/circle_info_solid_uuyellow.svg">'
    tooltip += '<div class="w3-text" style="margin-left:60px;"> '
    tooltip += 'More rows will take more time, since HTML needs to be generated for every row. '
    tooltip += 'If the number of items returned is very large, and the number of rows in a table '
    tooltip += 'is also very large or 0 (i.e. all rows), your browser may crash. '
    tooltip += '</div>'
    form += 'You might want to specify the maximum number of rows in a table to return '
    form += '(the page size of the table), '
    form += 'or 0 to return all rows (the more rows, the more time it will take): '
    form += '<label class="w3-tooltip">' + tooltip + '</label><br/>'
    form += '<input class="w3-input w3-border" type=text value=' + max_nr_table_rows + ' name=max_nr_table_rows>'

    form += '<br/><input class="' + button_style + '" ' + button_width + ' type=submit value=search>'
    form += '</form>'
    html += form

    html += get_html_for_cardend()
    html += page_footer + html_body_end
    return html


@ricgraph_explorer.route(rule='/optionspage/', methods=['GET'])
def optionspage() -> str:
    """Ricgraph Explorer entry, this 'page' only uses URL parameters.
    Find nodes based on URL parameters passed.

    Possible parameters are:

    - key: key of the nodes to find. If present, this field is preferred above
      'name', 'category' or 'value'.
    - name: name of the nodes to find.
    - category: category of the nodes to find.
    - value: value of the nodes to find.
    - discoverer_mode: the discoverer_mode to use, 'details_view' to see all details,
      or 'person_view' to have a nicer layout.
    - search_mode: the search_mode to use, 'exact_match' or 'value_search' (broad
      search on field 'value').
    - extra_url_parameters: a dict containing url parameters to be passed with each
      url generated. This dict can be extended as desired.

    returns html to parse.
    """
    global html_body_start, html_body_end, page_footer, nodes_cache

    get_all_globals_from_app_context()
    search_mode = get_url_parameter_value(parameter='search_mode',
                                          allowed_values=['exact_match', 'value_search'],
                                          default_value=DEFAULT_SEARCH_MODE)
    discoverer_mode = get_url_parameter_value(parameter='discoverer_mode',
                                              allowed_values=['details_view', 'person_view'],
                                              default_value=DEFAULT_DISCOVERER_MODE)
    extra_url_parameters = {}
    max_nr_items = get_url_parameter_value(parameter='max_nr_items',
                                           default_value=MAX_ITEMS)
    if not max_nr_items.isnumeric():
        # This also catches negative numbers, they contain a '-' and are not numeric.
        # See https://www.w3schools.com/python/ref_string_isnumeric.asp.
        max_nr_items = MAX_ITEMS
    extra_url_parameters['max_nr_items'] = max_nr_items
    max_nr_table_rows = get_url_parameter_value(parameter='max_nr_table_rows',
                                                default_value=MAX_ROWS_IN_TABLE)
    if not max_nr_table_rows.isnumeric():
        max_nr_table_rows = MAX_ROWS_IN_TABLE
    extra_url_parameters['max_nr_table_rows'] = max_nr_table_rows
    html = html_body_start

    key = get_url_parameter_value(parameter='key', use_escape=False)
    if key == '':
        name = get_url_parameter_value(parameter='name')
        category = get_url_parameter_value(parameter='category')
        value = get_url_parameter_value(parameter='value', use_escape=False)
    else:
        name = ''
        category = ''
        value = ''

    if name == '' and category == '' and value == '' and key == '':
        html += get_message(message='Ricgraph Explorer could not find anything.')
        html += page_footer + html_body_end
        return html

    # First check if the node is in 'nodes_cache'.
    if key != '':
        if key in nodes_cache:
            node = nodes_cache[key]
            html += create_options_page(node=node,
                                        discoverer_mode=discoverer_mode,
                                        extra_url_parameters=extra_url_parameters)
            html += page_footer + html_body_end
            return html

    if name != '' and value != '':
        key_found = rcg.create_ricgraph_key(name=name, value=value)
        if key_found in nodes_cache:
            node = nodes_cache[key_found]
            html += create_options_page(node=node,
                                        discoverer_mode=discoverer_mode,
                                        extra_url_parameters=extra_url_parameters)
            html += page_footer + html_body_end
            return html

    # No, it is not.
    if key != '':
        result = rcg.read_all_nodes(key=key)
    elif search_mode == 'exact_match':
        result = rcg.read_all_nodes(name=name, category=category, value=value,
                                    max_nr_nodes=int(extra_url_parameters['max_nr_items']))
    else:
        if len(value) < SEARCH_STRING_MIN_LENGTH:
            html += get_message(message='The search string should be at least '
                                        + str(SEARCH_STRING_MIN_LENGTH) + ' characters.')
            html += page_footer + html_body_end
            return html
        result = rcg.read_all_nodes(name=name, category=category, value=value,
                                    value_is_exact_match=False,
                                    max_nr_nodes=int(extra_url_parameters['max_nr_items']))
    if len(result) == 0:
        # We didn't find anything.
        html += get_message(message='Ricgraph Explorer could not find anything.')
        html += page_footer + html_body_end
        return html
    if len(result) > 1:
        table_header = 'Your search resulted in more than one item. Please choose one item to continue:'
        html += get_regular_table(nodes_list=result,
                                  table_header=table_header,
                                  discoverer_mode=discoverer_mode,
                                  extra_url_parameters=extra_url_parameters)
        html += page_footer + html_body_end
        return html

    node = result[0]
    key = rcg.create_ricgraph_key(name=node['name'], value=node['value'])
    nodes_cache[key] = node
    html += create_options_page(node=node,
                                discoverer_mode=discoverer_mode,
                                extra_url_parameters=extra_url_parameters)
    html += page_footer + html_body_end
    return html


@ricgraph_explorer.route(rule='/resultspage/', methods=['GET'])
def resultspage() -> str:
    """Ricgraph Explorer entry, this 'page' only uses URL parameters.
    View the results based on the values passed.
    This function is tied to create_results_page(), where, depending on the
    value of 'view_mode', is determined what will be viewed.
    This function will only be called with one node, so we can use 'key' to find it.

    Possible parameters are:

    - view_mode: determines what will be shown in create_results_page().
      This view_mode is first set in create_options_page(), and then
      caught first in resultspage() and then in create_results_page().
    - key: key of the nodes to find.
    - name_list: either a string which indicates that we only want neighbor
      nodes where the property 'name' is equal to 'name_list'
      (e.g. 'ORCID'), or a list containing several node names, indicating
      that we want all neighbor nodes where the property 'name' equals
      one of the names in the list 'name_list' (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty (empty string), return all nodes.
    - category_list: similar to 'name_list', but now for the property 'category'.
    - discoverer_mode: the discoverer_mode to use, 'details_view' to see all details,
      or 'person_view' to have a nicer layout.
    - extra_url_parameters: a dict containing url parameters to be passed with each
      url generated. This dict can be extended as desired.

    returns html to parse.
    """
    global html_body_start, html_body_end, page_footer

    get_all_globals_from_app_context()
    view_mode = get_url_parameter_value(parameter='view_mode')
    key = get_url_parameter_value(parameter='key', use_escape=False)
    discoverer_mode = get_url_parameter_value(parameter='discoverer_mode',
                                              allowed_values=['details_view', 'person_view'],
                                              default_value=DEFAULT_DISCOVERER_MODE)
    extra_url_parameters = {}
    max_nr_items = get_url_parameter_value(parameter='max_nr_items',
                                           default_value=MAX_ITEMS)
    if not max_nr_items.isnumeric():
        # This also catches negative numbers, they contain a '-' and are not numeric.
        # See https://www.w3schools.com/python/ref_string_isnumeric.asp.
        max_nr_items = MAX_ITEMS
    extra_url_parameters['max_nr_items'] = max_nr_items
    max_nr_table_rows = get_url_parameter_value(parameter='max_nr_table_rows',
                                                default_value=MAX_ROWS_IN_TABLE)
    if not max_nr_table_rows.isnumeric():
        max_nr_table_rows = MAX_ROWS_IN_TABLE
    extra_url_parameters['max_nr_table_rows'] = max_nr_table_rows
    name_list = request.args.getlist('name_list')
    category_list = request.args.getlist('category_list')
    # HTML forms with an empty field named e.g. 'aa' will result in a URL parameter '...&aa=&...'.
    # In this case, getlist() returns [''].
    # This is undesirable behaviour, since I'd rather have an empty list. Correct for it.
    if len(name_list) == 1 and name_list[0] == '':
        name_list = []
    if len(category_list) == 1 and category_list[0] == '':
        category_list = []

    html = html_body_start

    if view_mode not in VIEW_MODE_ALL:
        html += get_message(message='Unknown view_mode: "' + view_mode + '".')
        html += page_footer + html_body_end
        return html

    if view_mode == 'view_regular_table_overlap_records':
        # Special case, we catch it here because it needs a number of parameters which
        # I do not really want to pass down all the way.
        name = get_url_parameter_value(parameter='name')
        category = get_url_parameter_value(parameter='category')
        value = get_url_parameter_value(parameter='value', use_escape=False)
        system1 = get_url_parameter_value(parameter='system1')
        system2 = get_url_parameter_value(parameter='system2')
        overlap_mode = get_url_parameter_value(parameter='overlap_mode',
                                               allowed_values=['thisnode', 'neighbornodes'],
                                               default_value='neighbornodes')
        html += find_overlap_in_source_systems_records(name=name, category=category, value=value,
                                                       system1=system1, system2=system2,
                                                       discoverer_mode=discoverer_mode,
                                                       overlap_mode=overlap_mode,
                                                       extra_url_parameters=extra_url_parameters)
        html += page_footer + html_body_end
        return html

    html += create_results_page(view_mode=view_mode,
                                key=key,
                                name_list=name_list,
                                category_list=category_list,
                                discoverer_mode=discoverer_mode,
                                extra_url_parameters=extra_url_parameters)

    html += page_footer + html_body_end
    return html


@ricgraph_explorer.route(rule='/restapidocpage/', methods=['GET'])
def restapidocpage() -> str:
    """Show the documentation for the Ricgraph REST API. Ricgraph uses RapiDoc.

    :return: html to be rendered.
    """
    # For more information, see: https://rapidocweb.com and https://github.com/rapi-doc/RapiDoc.
    # For options see: https://rapidocweb.com/api.html.
    html = '<!DOCTYPE html>'
    html += '<html>'
    html += '<head>'
    html += html_preamble
    html += '<script type="module" src="/static/rapidoc-min.js"></script>'
    html += '<title>Ricgraph REST API</title>'
    html += '</head>'
    html += """<body>
              <style>
                rapi-doc { --font-regular:"Open Sans",sans-serif; }
                rapi-doc::part(section-navbar) { /* <<< targets navigation bar */
                    background:#ffcd00;              /* uu-yellow */
                }
              </style>
              <rapi-doc
                show-header="false"
                spec-url="/static/openapi.yaml"
                nav-text-color="#000000"        /* black */
                nav-hover-text-color="#5287c6"  /* uu-blue */
                sort-endpoints-by="none"
              > 
              <div slot="nav-logo">
                <img slot="nav-logo" src="/static/ricgraph_logo.png" width="200" 
                  style="vertical-align:middle;padding-right:0.5em;">REST API</img>
                <p/>
                <a href="/">Return to Ricgraph Explorer</a>
              </div>
              </rapi-doc>
              </body>
              </html>"""
    return html


# ##############################################################################
# This is where the work is done.
# ##############################################################################

def create_options_page(node: Node,
                        discoverer_mode: str = '',
                        extra_url_parameters: dict = None) -> str:
    """This function creates the page with options to choose from, depending on the
    choice the user has made on the index page.
    The 'view_mode' that is used, is caught first in resultspage() and then
    in create_results_page().

    :param node: the node that is found and that determines the possible choices.
    :param discoverer_mode: as usual.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    global name_all_datalist, category_all_datalist, source_all_datalist
    global category_all, resout_types_all, resout_types_all_datalist

    if extra_url_parameters is None:
        extra_url_parameters = {}

    html = ''
    if node is None:
        return get_message(message='create_options_page(): Node is None. This should not happen.')

    if discoverer_mode == 'details_view':
        html += get_you_searched_for_card(key=node['_key'],
                                          discoverer_mode=discoverer_mode,
                                          extra_url_parameters=extra_url_parameters)
    key = node['_key']
    html += get_found_message(node=node,
                              discoverer_mode=discoverer_mode,
                              extra_url_parameters=extra_url_parameters)
    if node['category'] == 'organization':
        html += get_html_for_cardstart()
        html += '<h4>What would you like to see from this organization?</h4>'
        html += create_html_form(destination='resultspage',
                                 button_text='show all information related to this organization',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_unspecified_table_organizations'
                                                } | extra_url_parameters)
        html += '<p/>'

        html += create_html_form(destination='resultspage',
                                 button_text='show persons related to this organization',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'name_list': 'person-root',
                                                'view_mode': 'view_regular_table_persons_of_org'
                                                } | extra_url_parameters)
        html += get_html_for_cardend()

        html += get_html_for_cardstart()
        html += '<h4>Advanced information related to this organization</h4>'
        html += get_html_for_cardstart()
        html += '<h5>More information about persons or their results in this organization.</h5>'
        html += create_html_form(destination='resultspage',
                                 button_text='find any information from all persons in this organization',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_regular_table_organization_addinfo'
                                                } | extra_url_parameters)
        html += '<p/>'

        html += create_html_form(destination='resultspage',
                                 button_text='find research results from all persons in this organization',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'category_list': resout_types_all,
                                                'view_mode': 'view_regular_table_organization_addinfo'
                                                } | extra_url_parameters)
        html += '<p/>'

        if 'competence' in category_all:
            html += create_html_form(destination='resultspage',
                                     button_text='find skills from all persons in this organization',
                                     hidden_fields={'key': key,
                                                    'discoverer_mode': discoverer_mode,
                                                    'category_list': 'competence',
                                                    'view_mode': 'view_regular_table_organization_addinfo'
                                                    } | extra_url_parameters)
            html += '<p/>'

        html += '<br/>'

        explanation = 'By using the fields below, you can choose '
        explanation += 'what you would like to see from the persons or their results in this organization. '
        explanation += 'You can use one or both fields.'
        label_text_name = 'Search for persons or results using field <em>name</em>: '
        input_spec_name = ('list', 'name_list', 'name_all_datalist', name_all_datalist)
        label_text_category = '</br>Search for persons or results using field <em>category</em>: '
        input_spec_category = ('list', 'category_list', 'category_all_datalist', category_all_datalist)
        html += create_html_form(destination='resultspage',
                                 button_text='find specific information',
                                 explanation=explanation,
                                 input_fields={label_text_name: input_spec_name,
                                               label_text_category: input_spec_category,
                                               },
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_regular_table_organization_addinfo'
                                                } | extra_url_parameters)
        html += get_html_for_cardend()
        html += get_html_for_cardend()

    elif node['category'] == 'person':
        html += get_html_for_cardstart()
        html += '<h4>What would you like to see from this person?</h4>'

        html += create_html_form(destination='resultspage',
                                 button_text='show all information related to this person',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'category_list': remainder_types_all,
                                                'view_mode': 'view_unspecified_table_everything'
                                                } | extra_url_parameters)
        html += '<p/>'

        html += create_html_form(destination='resultspage',
                                 button_text='show personal information related to this person',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'category_list': 'person',
                                                'view_mode': 'view_regular_table_personal'
                                                } | extra_url_parameters)
        html += '<p/>'

        html += create_html_form(destination='resultspage',
                                 button_text='show organizations related to this person',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'category_list': 'organization',
                                                'view_mode': 'view_regular_table_organizations'
                                                } | extra_url_parameters)
        html += '<p/>'

        html += create_html_form(destination='resultspage',
                                 button_text='show research results related to this person',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'category_list': resout_types_all,
                                                'view_mode': 'view_unspecified_table_resouts'
                                                } | extra_url_parameters)

        # I wonder if the following button is useful, I leave it out for now.
        # html += '<p/>'
        #
        # everything_except_ids = category_all.copy()
        # everything_except_ids.remove('person')
        # html += create_html_form(destination='resultspage',
        #                          button_text='show everything except identities related to this person',
        #                          hidden_fields={'key': key,
        #                                         'discoverer_mode': discoverer_mode,
        #                                         'category_list': everything_except_ids,
        #                                         'view_mode': 'view_unspecified_table_everything_except_ids'
        #                                         } | extra_url_parameters)
        html += get_html_for_cardend()

        html += get_html_for_cardstart()
        html += '<h4>Advanced information related to this person</h4>'
        html += get_html_for_cardstart()
        html += '<h5>With whom does this person share research results?</h5>'
        html += create_html_form(destination='resultspage',
                                 button_text='find persons that share any research result types with this person',
                                 hidden_fields={'key': key,
                                                'category_list': resout_types_all,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_regular_table_person_share_resouts'
                                                } | extra_url_parameters)

        html += '<br/>'
        label_text = 'By entering a value in the field below, '
        label_text += 'you will get a list of persons who share a specific research result type with this person:'
        input_spec = ('list', 'category_list', 'resout_types_all_datalist', resout_types_all_datalist)
        html += create_html_form(destination='resultspage',
                                 button_text='find persons that share a specific research result type with this person',
                                 input_fields={label_text: input_spec},
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_regular_table_person_share_resouts'
                                                } | extra_url_parameters)

        html += get_html_for_cardend()

        html += get_html_for_cardstart()
        explanation = '<h5>With which organizations does this person collaborate?</h5>'
        explanation += 'By clicking the following button, you will get an overview '
        explanation += 'of organizations that his person collaborates with. '
        explanation += 'A person <em>X</em> from organization <em>A</em> '
        explanation += 'collaborates with a person <em>Y</em> from '
        explanation += 'organization <em>B</em> if <em>X</em> and <em>Y</em> have both contributed to '
        explanation += 'the same research result.'
        button_text = 'find organizations that this person collaborates with'
        html += create_html_form(destination='resultspage',
                                 button_text=button_text,
                                 explanation=explanation,
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_regular_table_person_organization_collaborations'
                                                } | extra_url_parameters)

        html += get_html_for_cardend()

        html += get_html_for_cardstart()
        explanation = '<h5>Improve or enhance information in one of your source systems</h5>'
        explanation += 'The process of improving or enhancing information in a source system is called "enriching" '
        explanation += 'that source system. This is only possible if you have harvested more than one source system. '
        explanation += 'By using information found in one or more other harvested systems, '
        explanation += 'information in this source system can be improved or enhanced. '
        explanation += '</br>Use the field below to enter a name of one of your source systems. '
        explanation += 'Ricgraph Explorer will show what information can be added to this source system, '
        explanation += 'based on the information harvested from other source systems. '
        label_text = 'The name of the source system you would like to enrich:'
        # Note: we misuse the field 'category_list' to pass the name of the source system.
        button_text = 'find information harvested from other source systems, '
        button_text += 'not present in this source system'
        input_spec = ('list', 'category_list', 'source_all_datalist', source_all_datalist)
        html += create_html_form(destination='resultspage',
                                 button_text=button_text,
                                 explanation=explanation,
                                 input_fields={label_text: input_spec},
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_regular_table_person_enrich_source_system'
                                                } | extra_url_parameters)
        html += get_html_for_cardend()

        html += get_html_for_cardstart()
        explanation = '<h5>More information about overlap in source systems</h5>'
        explanation += 'In case more than one source systems have been harvested, '
        explanation += 'and the information in Ricgraph for the neighbors of this node have originated '
        explanation += 'from more than one source system, you can find out from which ones.</br>'
        button_text = 'find the overlap in source systems for '
        button_text += 'the neighbor nodes of this node (this may take some time)'
        html += create_html_form(destination='resultspage',
                                 button_text=button_text,
                                 explanation=explanation,
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_regular_table_overlap'
                                                } | extra_url_parameters)
        html += get_html_for_cardend()

        html += get_html_for_cardend()

    # ###
    # Note: view_mode == 'view_regular_table_overlap_records' is caught in resultspage().
    # ###
    else:
        html = create_results_page(view_mode='view_regular_table_category',
                                   key=key,
                                   discoverer_mode=discoverer_mode,
                                   extra_url_parameters=extra_url_parameters)

    return html


def create_results_page(view_mode: str,
                        key: str,
                        name_list: list = None,
                        category_list: list = None,
                        discoverer_mode: str = '',
                        extra_url_parameters: dict = None) -> str:
    """This function creates the page with results to show to the user.
    What is produced depends on 'view_mode'.
    The 'view_mode' that is used, is first set in create_options_page(), and then
    caught first in resultspage() and then in create_results_page().

    :param view_mode: what type of page to create.
    :param key: the _key of the node that is found and that determines where we start from.
    :param name_list: a list containing several node names, indicating
      that we want all neighbor nodes where the property 'name' equals
      one of the names in the list 'name_str' (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty , return all nodes.
    :param category_list: as name_str, but for category.
    :param discoverer_mode: as usual.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    global resout_types_all, personal_types_all, remainder_types_all, nodes_cache

    if name_list is None:
        name_list = []
    # The following is not used yet.
    # name_list_str = ''
    # if len(name_list) == 1:
    #     name_list_str = name_list[0]
    if category_list is None:
        category_list = []
    # The following is not used yet.
    # category_list_str = ''
    # if len(category_list) == 1:
    #     category_list_str = category_list[0]
    if extra_url_parameters is None:
        extra_url_parameters = {}

    max_nr_items = int(extra_url_parameters['max_nr_items'])
    html = ''
    if key in nodes_cache:
        node = nodes_cache[key]
    else:
        result = rcg.read_all_nodes(key=key)
        if len(result) == 0 or len(result) > 1:
            if len(result) == 0:
                message = 'Ricgraph Explorer could not find anything. '
            else:
                message = 'Ricgraph Explorer found too many nodes. '
            message += 'This should not happen. '
            return get_message(message=message)
        nodes_cache[key] = result[0]
        node = result[0]

    if discoverer_mode == 'details_view':
        table_columns_ids = DETAIL_COLUMNS
        table_columns_org = DETAIL_COLUMNS
        table_columns_resout = DETAIL_COLUMNS
        if node is not None:
            html += get_you_searched_for_card(key=node['_key'],
                                              name_list=name_list,
                                              category_list=category_list,
                                              view_mode=view_mode,
                                              discoverer_mode=discoverer_mode,
                                              extra_url_parameters=extra_url_parameters)
    else:
        table_columns_ids = ID_COLUMNS
        table_columns_org = ORGANIZATION_COLUMNS
        table_columns_resout = RESEARCH_OUTPUT_COLUMNS

    # We need this multiple times.
    node_found = get_found_message(node=node,
                                   discoverer_mode=discoverer_mode,
                                   extra_url_parameters=extra_url_parameters)

    if view_mode == 'view_regular_table_personal':
        personroot_node = rcg.get_personroot_node(node=node)
        neighbor_nodes_personal = rcg.get_all_neighbor_nodes(node=personroot_node,
                                                             category_want=personal_types_all)
        html += node_found
        if discoverer_mode == 'details_view':
            html += get_regular_table(nodes_list=neighbor_nodes_personal,
                                      table_header='This is personal information related to this person:',
                                      table_columns=table_columns_ids,
                                      discoverer_mode=discoverer_mode,
                                      extra_url_parameters=extra_url_parameters)
        else:
            html += view_personal_information(nodes_list=neighbor_nodes_personal,
                                              discoverer_mode=discoverer_mode,
                                              extra_url_parameters=extra_url_parameters)

    elif view_mode == 'view_regular_table_organizations' \
            or view_mode == 'view_regular_table_category':
        if view_mode == 'view_regular_table_category':
            personroot_node = node
        else:
            personroot_node = rcg.get_personroot_node(node=node)
        neighbor_nodes = rcg.get_all_neighbor_nodes(node=personroot_node,
                                                    name_want=name_list,
                                                    category_want=category_list)
        if view_mode == 'view_regular_table_organizations':
            table_header = 'These are the organizations related to this person:'
            table_columns = table_columns_org
        else:
            table_header = 'This is all information related to this ' + node['category'] + ':'
            table_columns = table_columns_resout
        html += node_found
        html += get_regular_table(nodes_list=neighbor_nodes,
                                  table_header=table_header,
                                  table_columns=table_columns,
                                  discoverer_mode=discoverer_mode,
                                  extra_url_parameters=extra_url_parameters)

    elif view_mode == 'view_regular_table_persons_of_org':
        # Some organizations have a large number of neighbors, but we will only show
        # 'max_nr_items' in the table. Therefore, reduce the number of neighbors when
        # searching for persons in an organization. Don't do this for other view_modes, because
        # in that case the table shows how many items are found.
        neighbor_nodes = rcg.get_all_neighbor_nodes(node=node,
                                                    name_want=name_list,
                                                    category_want=category_list,
                                                    max_nr_neighbor_nodes=max_nr_items)
        table_header = 'These are persons related to this organization:'
        table_columns = table_columns_ids
        html += node_found
        html += get_regular_table(nodes_list=neighbor_nodes,
                                  table_header=table_header,
                                  table_columns=table_columns,
                                  discoverer_mode=discoverer_mode,
                                  extra_url_parameters=extra_url_parameters)

    elif view_mode == 'view_unspecified_table_organizations':
        # Some organizations have a large number of neighbors, but we will only show
        # 'max_nr_items' in the table. Therefore, reduce the number of neighbors when
        # searching for persons in an organization. Don't do this for other view_modes, because
        # in that case the table shows how many items are found.
        neighbor_nodes = rcg.get_all_neighbor_nodes(node=node,
                                                    name_want=name_list,
                                                    category_want=category_list,
                                                    max_nr_neighbor_nodes=max_nr_items)
        table_header = 'This is all information related to this organization:'
        html += node_found
        if discoverer_mode == 'details_view':
            html += get_faceted_table(parent_node=node,
                                      neighbor_nodes=neighbor_nodes,
                                      table_header=table_header,
                                      table_columns=table_columns_resout,
                                      view_mode=view_mode,
                                      discoverer_mode=discoverer_mode,
                                      extra_url_parameters=extra_url_parameters)
        else:
            html += get_tabbed_table(nodes_list=neighbor_nodes,
                                     table_header=table_header,
                                     table_columns=table_columns_resout,
                                     tabs_on='category',
                                     discoverer_mode=discoverer_mode,
                                     extra_url_parameters=extra_url_parameters)

    elif view_mode == 'view_unspecified_table_resouts' \
            or view_mode == 'view_unspecified_table_everything_except_ids':
        personroot_node = rcg.get_personroot_node(node=node)
        neighbor_nodes = rcg.get_all_neighbor_nodes(node=personroot_node,
                                                    name_want=name_list,
                                                    category_want=category_list)
        if view_mode == 'view_unspecified_table_resouts':
            table_header = 'These are the research results related to this person:'
        else:
            table_header = 'These are all the neighbors related to this person (without its identities):'
        html += node_found
        if discoverer_mode == 'details_view':
            html += get_faceted_table(parent_node=node,
                                      neighbor_nodes=neighbor_nodes,
                                      table_header=table_header,
                                      table_columns=table_columns_resout,
                                      view_mode=view_mode,
                                      discoverer_mode=discoverer_mode,
                                      extra_url_parameters=extra_url_parameters)
        else:
            html += get_tabbed_table(nodes_list=neighbor_nodes,
                                     table_header=table_header,
                                     table_columns=table_columns_resout,
                                     tabs_on='category',
                                     discoverer_mode=discoverer_mode,
                                     extra_url_parameters=extra_url_parameters)

    elif view_mode == 'view_unspecified_table_everything':
        personroot_node = rcg.get_personroot_node(node=node)
        html += node_found
        neighbor_nodes_personal = rcg.get_all_neighbor_nodes(node=personroot_node,
                                                             category_want=personal_types_all)
        neighbor_nodes_remainder = rcg.get_all_neighbor_nodes(node=personroot_node,
                                                              name_want=name_list,
                                                              category_want=category_list)
        if discoverer_mode == 'details_view':
            html += get_tabbed_table(nodes_list=neighbor_nodes_personal,
                                     table_header='This is personal information related to this person:',
                                     table_columns=table_columns_ids,
                                     tabs_on='name',
                                     discoverer_mode=discoverer_mode,
                                     extra_url_parameters=extra_url_parameters)
            html += get_faceted_table(parent_node=node,
                                      neighbor_nodes=neighbor_nodes_remainder,
                                      table_header='This is other information related to this person:',
                                      table_columns=table_columns_resout,
                                      view_mode=view_mode,
                                      discoverer_mode=discoverer_mode,
                                      extra_url_parameters=extra_url_parameters)
        else:
            html += view_personal_information(nodes_list=neighbor_nodes_personal,
                                              discoverer_mode=discoverer_mode,
                                              extra_url_parameters=extra_url_parameters)
            html += get_tabbed_table(nodes_list=neighbor_nodes_remainder,
                                     table_header='This is other information related to this person:',
                                     table_columns=table_columns_resout,
                                     tabs_on='category',
                                     discoverer_mode=discoverer_mode,
                                     extra_url_parameters=extra_url_parameters)

    elif view_mode == 'view_regular_table_person_share_resouts':
        # Note the hard limit.
        html += find_person_share_resouts(parent_node=node,
                                          category_want_list=category_list,
                                          category_dontwant_list=['person', 'competence', 'organization'],
                                          discoverer_mode=discoverer_mode,
                                          extra_url_parameters=extra_url_parameters)

    elif view_mode == 'view_regular_table_person_enrich_source_system':
        # Note: we misuse the field 'category_list' to pass the name of the source system
        # we would like to enrich.
        if len(category_list) == 0:
            source_system = ''
        else:
            source_system = str(category_list[0])
        html += find_enrich_candidates(parent_node=node,
                                       source_system=source_system,
                                       discoverer_mode=discoverer_mode,
                                       extra_url_parameters=extra_url_parameters)

    elif view_mode == 'view_regular_table_person_organization_collaborations':
        html += find_person_organization_collaborations(parent_node=node,
                                                        discoverer_mode=discoverer_mode,
                                                        extra_url_parameters=extra_url_parameters)

    elif view_mode == 'view_regular_table_organization_addinfo':
        # Note the hard limit.
        html += find_organization_additional_info(parent_node=node,
                                                  name_list=name_list,
                                                  category_list=category_list,
                                                  discoverer_mode=discoverer_mode,
                                                  extra_url_parameters=extra_url_parameters)
    elif view_mode == 'view_regular_table_overlap':
        html += find_overlap_in_source_systems(name=node['name'],
                                               category=node['category'],
                                               value=node['value'],
                                               discoverer_mode=discoverer_mode,
                                               overlap_mode='neighbornodes',
                                               extra_url_parameters=extra_url_parameters)

    # Note: view_mode == 'view_regular_table_overlap_records' is caught in resultspage().

    else:
        html += get_message(message='create_results_page(): Unknown view_mode "' + view_mode + '".')
    return html


def view_personal_information(nodes_list: list,
                              discoverer_mode: str = '',
                              extra_url_parameters: dict = None) -> str:
    """Create a person page of the node.
    This page shows the name variants, a photo (if present),
    and a list of competences (if present). Then a table with the other identities.
    'discover_mode' will always be 'person_view', but we still pass it for future
    extensions.

    :param nodes_list: the nodes to create a table from.
    :param discoverer_mode: the discoverer_mode to use.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    global nodes_cache

    if extra_url_parameters is None:
        extra_url_parameters = {}

    if len(nodes_list) == 0:
        return get_message('No neighbors found.')

    html = get_html_for_cardstart()
    names = []
    for node in nodes_list:
        # Add node to nodes_cache if it is not there already.
        key = node['_key']
        if key not in nodes_cache:
            nodes_cache[key] = node

        if node['name'] != 'FULL_NAME':
            continue
        key = rcg.create_ricgraph_key(name=node['name'], value=node['value'])
        item = '<a href=' + url_for('optionspage') + '?'
        item += urllib.parse.urlencode({'key': key,
                                        'discoverer_mode': discoverer_mode}
                                       | extra_url_parameters) + '>'
        item += node['value'] + '</a>'
        names.append(item)
    if len(names) == 1:
        html += '<p class="w3-xlarge">' + ', '.join(str(item) for item in names)
        # matching </p> inserted below
    elif len(names) > 1:
        html += '<p>This person has ' + str(len(names)) + ' name variants:&nbsp;'
        html += '<font class="w3-xlarge">' + ', '.join(str(item) for item in names) + '</font>'
        # matching </p> inserted below

    for node in nodes_list:
        if node['name'] != 'PHOTO_ID':
            continue
        key = rcg.create_ricgraph_key(name=node['name'], value=node['value'])
        html += '&nbsp;&nbsp;'
        html += '<a href=' + url_for('optionspage') + '?'
        html += urllib.parse.urlencode({'key': key,
                                        'discoverer_mode': discoverer_mode}
                                       | extra_url_parameters) + '>'
        html += '<img src="' + node['url_main'] + '" alt="' + node['value']
        html += '" title="' + node['value'] + '" height="100"></a>'
    html += '</p>'

    skills = []
    research_areas = []
    expertise_areas = []

    # Get the nodes of interest. Using rcg.get_all_neighbor_nodes() is not efficient.
    for node in nodes_list:
        if node['category'] != 'competence':
            continue
        key = rcg.create_ricgraph_key(name=node['name'], value=node['value'])
        item = '<a href=' + url_for('optionspage') + '?'
        item += urllib.parse.urlencode({'key': key,
                                        'discoverer_mode': discoverer_mode}
                                       | extra_url_parameters) + '>'
        item += node['value'] + '</a>'
        if node['name'] == 'SKILL':
            skills.append(item)
        if node['name'] == 'RESEARCH_AREA':
            research_areas.append(item)
        if node['name'] == 'EXPERTISE_AREA':
            expertise_areas.append(item)

    html_list = ''
    if len(skills) > 0:
        html_list += '<li>Skills: ' + ', '.join(str(item) for item in skills) + '</li>'
    if len(research_areas) > 0:
        html_list += '<li>Research areas: ' + ', '.join(str(item) for item in research_areas) + '</li>'
    if len(expertise_areas) > 0:
        html_list += '<li>Expertise areas: ' + ', '.join(str(item) for item in expertise_areas) + '</li>'
    if html_list != '':
        html += '<p/><td><ul>' + html_list + '</ul></td>'
    html += get_html_for_cardend()

    id_nodes = []
    for node in nodes_list:
        if node['category'] != 'person':
            continue
        if node['name'] != 'FULL_NAME' \
                and node['name'] != 'person-root' \
                and node['name'] != 'PHOTO_ID':
            id_nodes.append(node)
    html += get_tabbed_table(nodes_list=id_nodes,
                             table_header='These are the identities related to this person:',
                             table_columns=ID_COLUMNS,
                             tabs_on='name',
                             discoverer_mode=discoverer_mode,
                             extra_url_parameters=extra_url_parameters)
    return html


def find_person_share_resouts_cypher(parent_node: Node,
                                     category_want_list: list = None,
                                     category_dontwant_list: list = None,
                                     max_nr_items: str = MAX_ITEMS) -> list:
    """ For documentation, see find_person_share_resouts().

    :param parent_node:
    :param category_want_list:
    :param category_dontwant_list:
    :param max_nr_items:
    :return:
    """
    if category_want_list is None:
        category_want_list = []
    if category_dontwant_list is None:
        category_dontwant_list = []

    # By using the following statement we can start with both a node and its person-root node.
    personroot_node = rcg.get_personroot_node(node=parent_node)
    cypher_query = 'MATCH (startnode_personroot:RicgraphNode)-[]'
    cypher_query += '->(neighbor:RicgraphNode)-[]->(neighbor_personroot:RicgraphNode)'
    cypher_query += 'WHERE '
    if rcg.ricgraph_database() == 'neo4j':
        cypher_query += 'elementId(startnode_personroot)=$startnode_personroot_element_id AND '
    else:
        cypher_query += 'id(startnode_personroot)=toInteger($startnode_personroot_element_id) AND '
    # The following statement is really necessary for speed reasons.
    cypher_query += 'startnode_personroot.name="person-root" AND '
    if len(category_want_list) > 0:
        cypher_query += 'neighbor.category IN $category_want_list AND '
    if len(category_dontwant_list) > 0:
        cypher_query += 'NOT neighbor.category IN $category_dontwant_list AND '
    cypher_query += 'neighbor_personroot.name="person-root" AND '
    # cypher_query += 'id(neighbor_personroot)<>id(startnode_personroot) '
    if rcg.ricgraph_database() == 'neo4j':
        cypher_query += 'elementId(neighbor_personroot)<>elementId(startnode_personroot) '
    else:
        cypher_query += 'id(neighbor_personroot)<>id(startnode_personroot) '
    cypher_query += 'RETURN DISTINCT neighbor_personroot '
    if int(max_nr_items) > 0:
        cypher_query += 'LIMIT ' + max_nr_items
    # print(cypher_query)

    # Note that the RETURN (as in RETURN DISTINCT *) also has all intermediate results, such
    # as the common research results (in 'neighbor'). We don't use them at the moment.
    cypher_result, _, _ = graph.execute_query(cypher_query,
                                              startnode_personroot_element_id=personroot_node.element_id,
                                              category_want_list=category_want_list,
                                              category_dontwant_list=category_dontwant_list,
                                              database_=rcg.ricgraph_databasename())

    # Convert 'cypher_result' to a list of Node's.
    # If we happened to use 'result_transformer_=Result.data' in execute_query(), we would
    # have gotten a list of dicts, which messes up 'nodes_cache'.
    connected_persons = []
    for neighbor_node in cypher_result:
        if len(neighbor_node) == 0:
            continue
        person = neighbor_node['neighbor_personroot']
        connected_persons.append(person)

    return connected_persons


def find_person_share_resouts(parent_node: Node,
                              category_want_list: list = None,
                              category_dontwant_list: list = None,
                              discoverer_mode: str = '',
                              extra_url_parameters: dict = None) -> str:
    """Function that finds with whom a person shares research results.

    :param parent_node: the starting node for finding shared research result types.
    :param category_want_list: the category list used for selection, or [] if any category.
    :param category_dontwant_list: the category list used for selection (i.e. not these).
    :param discoverer_mode: as usual.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    if extra_url_parameters is None:
        extra_url_parameters = {}
    if category_want_list is None:
        category_want_list = []
    if category_dontwant_list is None:
        category_dontwant_list = []

    html = ''
    if parent_node['category'] != 'person':
        message = 'Unexpected result in find_person_share_resouts(): '
        message += 'You have not passed an "person" node, but a "' + parent_node['category']
        message += '" node.'
        return get_message(message=message)

    connected_persons = find_person_share_resouts_cypher(parent_node=parent_node,
                                                         category_want_list=category_want_list,
                                                         category_dontwant_list=category_dontwant_list,
                                                         max_nr_items=extra_url_parameters['max_nr_items'])
    if discoverer_mode == 'details_view':
        table_columns = DETAIL_COLUMNS
    else:
        table_columns = RESEARCH_OUTPUT_COLUMNS

    table_header = 'This is the person we start with:'
    html += get_regular_table(nodes_list=[parent_node],
                              table_header=table_header,
                              table_columns=table_columns,
                              discoverer_mode=discoverer_mode,
                              extra_url_parameters=extra_url_parameters)
    if len(connected_persons) == 0:
        if len(category_want_list) == 1:
            message = 'This person does not share research result type "' + category_want_list[0] + '" '
        else:
            message = 'This person does not share any research result types '
        message += 'with other persons.'
        return html + get_message(message=message)

    if len(category_want_list) == 1:
        table_header = 'This person shares research result type "' + category_want_list[0] + '" '
    else:
        table_header = 'This person shares various research result types '
    table_header += 'with these persons:'
    html += get_regular_table(nodes_list=connected_persons,
                              table_header=table_header,
                              table_columns=table_columns,
                              discoverer_mode=discoverer_mode,
                              extra_url_parameters=extra_url_parameters)
    return html


def find_enrich_candidates_one_person(personroot: Node,
                                      name_want: list = None,
                                      category_want: list = None,
                                      source_system: str = '') -> Tuple[list, list]:
    """This function tries to find nodes to enrich source system 'source_system'.

    :param personroot: the starting node for finding enrichments for.
    :param name_want: a list containing several node names, indicating
      that we want all neighbor nodes of the person-root node of the organization
      specified by 'key', where the property 'name' equals
      one of the names in the list 'name_want'
      (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty (empty string), return all nodes.
    :param category_want: similar to 'name_want', but now for the property 'category'.
    :param source_system: the source system to find enrichments for.
    :return: 2 lists, nodes to identify and nodes to enrich.
    """
    nodes_in_source_system = []
    nodes_not_in_source_system = []
    neighbors = rcg.get_all_neighbor_nodes(node=personroot,
                                           name_want=name_want,
                                           category_want=category_want)
    for neighbor in neighbors:
        if source_system in neighbor['_source']:
            nodes_in_source_system.append(neighbor)
            continue
        if source_system not in neighbor['_source']:
            nodes_not_in_source_system.append(neighbor)
            continue

    if len(nodes_in_source_system) == 0:
        return [], nodes_not_in_source_system

    person_nodes = []
    for node_source in nodes_in_source_system:
        if node_source['category'] == 'person':
            person_nodes.append(node_source)

    return person_nodes, nodes_not_in_source_system


def find_enrich_candidates(parent_node: Union[Node, None],
                           source_system: str,
                           discoverer_mode: str = '',
                           extra_url_parameters: dict = None) -> str:
    """This function tries to find nodes to enrich source system 'source_system'.
    It is built around 'person-root' nodes. For each person-root node (in case there are
    more than one) we check if we can enrich that node.
    In case this function is used to find _all_ enrichments in Ricgraph,
    (then parent_node = None), a hard limit is used to break from the loop, since otherwise
    it would take too much time.
    We do not use 'name', 'category' and/or 'value' to get a list of nodes
    (as in e.g. find_overlap_in_source_systems()), because
    in that case we need to do an additional step to get these 'person-root' nodes.

    :param parent_node: the starting node for finding enrichments for, or None if
      you want to find enrichments for all 'person-root' nodes in Ricgraph.
    :param source_system: the source system to find enrichments for.
    :param discoverer_mode: as usual.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    global source_all

    if extra_url_parameters is None:
        extra_url_parameters = {}

    if source_system not in source_all:
        html = get_message(message='You have not specified a valid source system "'
                                   + source_system + '".')
        return html

    html = ''
    if parent_node is None:
        personroot_list = rcg.read_all_nodes(name='person-root',
                                             max_nr_nodes=int(extra_url_parameters['max_nr_items']))
        personroot_node = None
        message = 'You have chosen to enrich <em>all</em> nodes in Ricgraph for source system "'
        message += source_system + '". '
        message += 'However, that will take a long time. '
        message += 'Ricgraph Explorer will find enrich candidates for at most '
        message += str(MAX_NR_NODES_TO_ENRICH) + ' nodes. '
        message += 'If you want to find more nodes to enrich, change the constant '
        message += '<em>MAX_NR_NODES_TO_ENRICH</em> in file <em>ricgraph_explorer.py</em>.'
        html += get_message(message=message, please_try_again=False)
    else:
        personroot_node = rcg.get_personroot_node(node=parent_node)
        personroot_list = [personroot_node]

    if discoverer_mode == 'details_view':
        table_columns = DETAIL_COLUMNS
    else:
        table_columns = RESEARCH_OUTPUT_COLUMNS

    count = 1
    something_found = False
    for personroot in personroot_list:
        if count > MAX_NR_NODES_TO_ENRICH:
            break
        person_nodes, nodes_not_in_source_system = \
            find_enrich_candidates_one_person(personroot=personroot,
                                              source_system=source_system)
        if len(nodes_not_in_source_system) == 0:
            # All neighbors are only from 'source_system', nothing to report.
            continue

        # Now we are left with a node that _is_ in 'source_system'.
        something_found = True
        count += 1
        html += get_html_for_cardstart()
        table_header = 'This item is used to determine possible enrichments of source system "'
        table_header += source_system + '":'
        html += get_regular_table(nodes_list=[personroot],
                                  table_header=table_header,
                                  table_columns=table_columns,
                                  extra_url_parameters=extra_url_parameters)

        if len(person_nodes) == 0:
            message = 'There are enrich candidates '
            message += 'to enrich source system "' + source_system
            message += '", but there are no <em>person</em> nodes to identify this item in "'
            message += source_system + '".'
            html += get_message(message=message, please_try_again=False)
        else:
            table_header = 'You can use the information in this table to find this item in source system "'
            table_header += source_system + '":'
            html += get_regular_table(nodes_list=person_nodes,
                                      table_header=table_header,
                                      table_columns=table_columns,
                                      extra_url_parameters=extra_url_parameters)

        table_header = 'You could enrich source system "' + source_system + '" '
        table_header += 'by using this information harvested from other source systems. '
        table_header += 'This information is not in source system "' + source_system + '".'
        html += get_tabbed_table(nodes_list=nodes_not_in_source_system,
                                 table_header=table_header,
                                 table_columns=table_columns,
                                 tabs_on='category',
                                 discoverer_mode=discoverer_mode,
                                 extra_url_parameters=extra_url_parameters)
        html += get_html_for_cardend()

    if something_found:
        if parent_node is not None:
            pass
            # ### This may be added in a future release.
            # This message is only useful if we have entered this function with the
            # aim to enrich one node.
            # message = 'The table above shows how you can enrich source system "'
            # message += source_system + '" based on one person node. '
            # message += '<a href=' + url_for('findenrichcandidates') + '?'
            # message += urllib.parse.urlencode({'discoverer_mode': discoverer_mode,
            #                                    'source_system': source_system}) + '>'
            # message += 'You can click here if you would like to find candidates to enrich '
            # message += 'for <em>all</em> nodes in Ricgraph</a>. '
            # message += 'Warning: this may take quite some time.'
            # html += get_message(message=message, please_try_again=False)
            # ### end.
    else:
        if parent_node is None:
            message = 'Ricgraph could not find any information in other source systems '
            message += 'to enrich source system "' + source_system + '".'
            html += get_message(message=message)
        else:
            html += get_html_for_cardstart()
            table_header = 'This item is used to determine possible enrichments of source system "'
            table_header += source_system + '":'
            html += get_regular_table(nodes_list=[personroot_node],
                                      table_header=table_header,
                                      table_columns=table_columns,
                                      extra_url_parameters=extra_url_parameters)
            html += '</br>Ricgraph could not find any information in other source systems '
            html += 'to enrich source system "' + source_system + '".'
            html += get_html_for_cardend()

    html += '</p>'

    return html


def find_person_organization_collaborations_cypher(parent_node: Node,
                                                   max_nr_items: str = MAX_ITEMS) -> Tuple[list, list]:
    """ For documentation, see find_person_organization_collaborations_cypher().

    :param parent_node:
    :param max_nr_items:
    :return:
    """
    # By using the following statement we can start with both a node and its person-root node.
    personroot_node = rcg.get_personroot_node(node=parent_node)
    cypher_query = 'MATCH (startnode_personroot:RicgraphNode)-[]'
    cypher_query += '->(neighbor:RicgraphNode)-[]->(neighbor_personroot:RicgraphNode)-[]'
    cypher_query += '->(neighbor_organization:RicgraphNode) '
    cypher_query += 'WHERE '
    if rcg.ricgraph_database() == 'neo4j':
        cypher_query += 'elementId(startnode_personroot)=$startnode_personroot_element_id AND '
    else:
        cypher_query += 'id(startnode_personroot)=toInteger($startnode_personroot_element_id) AND '
    # The following statement is really necessary for speed reasons.
    cypher_query += 'startnode_personroot.name="person-root" AND '
    cypher_query += 'neighbor.category IN $resout_types_all AND '
    cypher_query += 'neighbor_personroot.name="person-root" AND '
    if rcg.ricgraph_database() == 'neo4j':
        cypher_query += 'elementId(neighbor_personroot)<>elementId(startnode_personroot) AND '
    else:
        cypher_query += 'id(neighbor_personroot)<>id(startnode_personroot) AND '
    cypher_query += 'neighbor_organization.category="organization" '
    cypher_query += 'RETURN DISTINCT neighbor_organization '
    if int(max_nr_items) > 0:
        cypher_query += 'LIMIT ' + max_nr_items
    # print(cypher_query)
    # Note that the RETURN (as in RETURN DISTINCT *) also has all intermediate results, such
    # as the collaborating researchers (in 'neighbor_personroot') and the common research
    # results (in 'neighbor'). We don't use them at the moment.

    # Note that 'cypher_result' will contain _all_ organizations that 'parent_node'
    # collaborates with, very probably also the organizations this person works for.
    cypher_result, _, _ = graph.execute_query(cypher_query,
                                              startnode_personroot_element_id=personroot_node.element_id,
                                              resout_types_all=resout_types_all,
                                              database_=rcg.ricgraph_databasename())

    # Get the organizations from 'parent_node'.
    personroot_node = rcg.get_personroot_node(node=parent_node)
    personroot_node_organizations = rcg.get_all_neighbor_nodes(node=personroot_node,
                                                               category_want='organization')
    # Now get the organizations that 'parent_node' collaborates with, excluding
    # this person's own organizations. Note that the types of 'cypher_result'
    # and 'personroot_node_organizations' are not the same.
    personroot_node_organizations_key = []
    for organization in personroot_node_organizations:
        personroot_node_organizations_key.append(organization['_key'])

    # Convert 'cypher_result' to a list of Node's.
    # If we happened to use 'result_transformer_=Result.data' in execute_query(), we would
    # have gotten a list of dicts, which messes up 'nodes_cache'.
    collaborating_organizations = []
    for organization_node in cypher_result:
        if len(organization_node) == 0:
            continue
        organization = organization_node['neighbor_organization']
        organization_key = organization['_key']
        if organization_key not in personroot_node_organizations_key:
            collaborating_organizations.append(organization)

    return personroot_node_organizations, collaborating_organizations


def find_person_organization_collaborations(parent_node: Node,
                                            discoverer_mode: str = '',
                                            extra_url_parameters: dict = None) -> str:
    """Function that finds with which organization a person collaborates.

    A person X from organization A collaborates with a person Y from
    organization B if X and Y have both contributed to the same research result.
    All research result types are in 'resout_types_all'.
    This function does not give an overview of the persons that person X collaborates
    with (although those are determined in this function) because there is
    another function to do that.

    :param parent_node: the starting node for finding collaborating organizations.
    :param discoverer_mode: as usual.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    global graph
    global resout_types_all

    if extra_url_parameters is None:
        extra_url_parameters = {}

    html = ''
    if parent_node['category'] != 'person':
        message = 'Unexpected result in find_person_organization_collaborations(): '
        message += 'You have not passed an "person" node, but a "' + parent_node['category']
        message += '" node.'
        return get_message(message=message)

    personroot_node_organizations, collaborating_organizations = \
        find_person_organization_collaborations_cypher(parent_node=parent_node,
                                                       max_nr_items=extra_url_parameters['max_nr_items'])

    if discoverer_mode == 'details_view':
        table_columns = DETAIL_COLUMNS
    else:
        table_columns = RESEARCH_OUTPUT_COLUMNS

    table_header = 'This is the person we start with:'
    html += get_regular_table(nodes_list=[parent_node],
                              table_header=table_header,
                              table_columns=table_columns,
                              discoverer_mode=discoverer_mode,
                              extra_url_parameters=extra_url_parameters)

    if len(personroot_node_organizations) == 0:
        html += get_message(message='This person does not work at any organization.',
                            please_try_again=False)
    else:
        table_header = 'This person works at the following organizations:'
        html += get_regular_table(nodes_list=personroot_node_organizations,
                                  table_header=table_header,
                                  table_columns=table_columns,
                                  discoverer_mode=discoverer_mode,
                                  extra_url_parameters=extra_url_parameters)

    if len(collaborating_organizations) == 0:
        message = 'This person has no collaborations with other organizations.'
        return html + get_message(message=message)

    table_header = 'This person collaborates with the following organizations:'
    html += get_regular_table(nodes_list=collaborating_organizations,
                              table_header=table_header,
                              table_columns=table_columns,
                              discoverer_mode=discoverer_mode,
                              extra_url_parameters=extra_url_parameters)
    return html


def find_organization_additional_info_cypher(parent_node: Node,
                                             name_list: list = None,
                                             category_list: list = None,
                                             source_system: str = '',
                                             max_nr_items: str = MAX_ITEMS) -> list:
    """For documentation, see find_organization_additional_info().

    :param parent_node:
    :param name_list:
    :param category_list:
    :param source_system:
    :param max_nr_items:
    :return:
    """
    if name_list is None:
        name_list = []
    if category_list is None:
        category_list = []

    second_neighbor_name_list = ''
    second_neighbor_category_list = ''
    if len(name_list) > 0:
        second_neighbor_name_list = '["'
        second_neighbor_name_list += '", "'.join(str(item) for item in name_list)
        second_neighbor_name_list += '"]'
    if len(category_list) > 0:
        second_neighbor_category_list = '["'
        second_neighbor_category_list += '", "'.join(str(item) for item in category_list)
        second_neighbor_category_list += '"]'

    # Prepare and execute Cypher query.
    cypher_query = 'MATCH (node)-[]->(neighbor) '
    if rcg.ricgraph_database() == 'neo4j':
        cypher_query += 'WHERE elementId(node)=$node_element_id '
    else:
        cypher_query += 'WHERE id(node)=toInteger($node_element_id) '
    cypher_query += ' AND neighbor.name = "person-root" '

    cypher_query += 'MATCH (neighbor)-[]->(second_neighbor) '
    if len(name_list) > 0 or len(category_list) > 0 or source_system != '':
        cypher_query += 'WHERE '
    if len(name_list) > 0:
        cypher_query += 'second_neighbor.name IN ' + second_neighbor_name_list + ' '
    if len(name_list) > 0 and len(category_list) > 0:
        cypher_query += 'AND '
    if len(category_list) > 0:
        cypher_query += 'second_neighbor.category IN ' + second_neighbor_category_list + ' '
    if source_system != '':
        if len(name_list) > 0 or len(category_list) > 0:
            cypher_query += 'AND '
        cypher_query += 'NOT "' + source_system + '" IN second_neighbor._source '
    cypher_query += 'RETURN DISTINCT second_neighbor, count(second_neighbor) as count_second_neighbor '
    cypher_query += 'ORDER BY count_second_neighbor DESC '
    if int(max_nr_items) > 0:
        cypher_query += 'LIMIT ' + max_nr_items
    # print(cypher_query)
    cypher_result, _, _ = graph.execute_query(cypher_query,
                                              node_element_id=parent_node.element_id,
                                              database_=rcg.ricgraph_databasename())
    return cypher_result


def find_organization_additional_info(parent_node: Node,
                                      name_list: list = None,
                                      category_list: list = None,
                                      discoverer_mode: str = '',
                                      extra_url_parameters: dict = None) -> str:
    """Function that finds additional information connected to a (sub-)organization.

    :param parent_node: the starting node for finding additional information.
    :param name_list: the name list used for selection.
    :param category_list: the category list used for selection.
    :param discoverer_mode: as usual.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    global graph

    if extra_url_parameters is None:
        extra_url_parameters = {}

    if parent_node is None:
        message = 'Unexpected result in find_organization_additional_info(): '
        message += 'This organization cannot be found in Ricgraph.'
        return get_message(message=message)

    if parent_node['category'] != 'organization':
        message = 'Unexpected result in find_organization_additional_info(): '
        message += 'You have not passed an "organization" node, but a "' + parent_node['category']
        message += '" node in fiterorganization(). '
        return get_message(message=message)

    if name_list is None:
        name_list = []
    if category_list is None:
        category_list = []
    name_str = ''
    category_str = ''
    if len(name_list) == 1:
        name_str = name_list[0]
    if len(category_list) == 1:
        category_str = category_list[0]

    cypher_result = \
        find_organization_additional_info_cypher(parent_node=parent_node,
                                                 name_list=name_list,
                                                 category_list=category_list,
                                                 max_nr_items=extra_url_parameters['max_nr_items'])
    if len(cypher_result) == 0:
        message = 'Could not find any persons or results for this organization'
        if name_str != '' and category_str != '':
            message += ', using search terms '
            message += '"' + name_str + '" and "' + category_str + '".'
        elif name_str != '':
            message += ', using search term '
            message += '"' + name_str + '".'
        elif category_str != '':
            message += ', using search term '
            message += '"' + category_str + '".'
        else:
            message += '.'
        return get_message(message=message)

    relevant_result = []
    expertise_area_list = []
    research_area_list = []
    skill_list = []
    if 'competence' in category_list:
        we_have_competence = True
    else:
        we_have_competence = False

    for result in cypher_result:
        node = result['second_neighbor']
        relevant_result.append(node)
        if we_have_competence:
            if node['name'] == 'EXPERTISE_AREA':
                expertise_area_list.append({'name': node['value'],
                                            'value': result['count_second_neighbor']})
            elif node['name'] == 'RESEARCH_AREA':
                research_area_list.append({'name': node['value'],
                                           'value': result['count_second_neighbor']})
            elif node['name'] == 'SKILL':
                skill_list.append({'name': node['value'],
                                   'value': result['count_second_neighbor']})

    if discoverer_mode == 'details_view':
        table_columns = DETAIL_COLUMNS
    else:
        table_columns = RESEARCH_OUTPUT_COLUMNS

    html = ''
    table_header = 'This item is used for finding information about the persons '
    table_header += 'or their results of this organization:'
    html += get_regular_table(nodes_list=[parent_node],
                              table_header=table_header,
                              table_columns=table_columns,
                              discoverer_mode=discoverer_mode,
                              extra_url_parameters=extra_url_parameters)
    table_header = 'These are all the '
    if name_str != '' and category_str != '':
        table_header += '"' + name_str + '" and "' + category_str + '" '
    elif name_str != '':
        table_header += '"' + name_str + '" '
    elif category_str != '':
        table_header += '"' + category_str + '" '
    else:
        table_header += 'shared '
    table_header += 'items of this organization:'
    table_html = get_tabbed_table(nodes_list=relevant_result,
                                  table_header=table_header,
                                  table_columns=table_columns,
                                  tabs_on='category',
                                  discoverer_mode=discoverer_mode,
                                  extra_url_parameters=extra_url_parameters)

    if we_have_competence:
        histogram_html = ''
        if len(expertise_area_list) > 1:
            histogram_html += get_html_for_cardstart()
            histogram_html += get_html_for_histogram(histogram_list=expertise_area_list,
                                                     histogram_width=250,
                                                     histogram_title='Histogram of "expertise area":')
            histogram_html += get_html_for_cardend()
        if len(research_area_list) > 1:
            histogram_html += get_html_for_cardstart()
            histogram_html += get_html_for_histogram(histogram_list=research_area_list,
                                                     histogram_width=250,
                                                     histogram_title='Histogram of "research area":')
            histogram_html += get_html_for_cardend()
        if len(skill_list) > 1:
            histogram_html += get_html_for_cardstart()
            histogram_html += get_html_for_histogram(histogram_list=skill_list,
                                                     histogram_width=250,
                                                     histogram_title='Histogram of "skill":')
            histogram_html += get_html_for_cardend()

        if histogram_html == '':
            # No data for any of the histograms.
            html += table_html
        else:
            # Divide space between histogram and table.
            html += '<div class="w3-row-padding w3-stretch" >'
            html += '<div class="w3-col" style="width:23em" >'
            html += histogram_html
            html += '</div>'
            html += '<div class="w3-rest" >'
            html += table_html
            html += '</div>'
            html += '</div>'
    else:
        html += table_html

    return html


def find_overlap_in_source_systems(name: str = '', category: str = '', value: str = '',
                                   discoverer_mode: str = '',
                                   overlap_mode: str = 'neighbornodes',
                                   extra_url_parameters: dict = None) -> str:
    """Get the overlap in items from source systems.
    We do need a 'name', 'category' and/or 'value', otherwise we won't be able
    to find overlap in source systems for a list of items. That list can only be
    found using these fields, and then these fields can be passed to
    find_overlap_in_source_systems_records() to show the overlap nodes in a table.
    If we want to find overlap of only one node, these fields will result in only one item
    to be found, and the overlap will be computed of the neighbors of that node.
    This function is tightly connected to find_overlap_in_source_systems_records().

    :param name: name of the node(s) to find.
    :param category: category of the node(s) to find.
    :param value: value of the node(s) to find.
    :param discoverer_mode: the discoverer_mode to use.
    :param overlap_mode: which overlap to compute: from this node ('thisnode')
      or from the neighbors of this node ('neighbornodes').
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    if extra_url_parameters is None:
        extra_url_parameters = {}

    html = ''
    nodes = rcg.read_all_nodes(name=name, category=category, value=value)
    if len(nodes) == 0:
        # Let's try again, assuming we did a broad search instead of an exact match search.
        nodes = rcg.read_all_nodes(value=value,
                                   value_is_exact_match=False)
        if len(nodes) == 0:
            return get_message(message='Ricgraph Explorer could not find anything.')

    if overlap_mode == 'neighbornodes':
        # In this case, we would like to know the overlap of nodes neighboring the node
        # we have just found. We can only do that if we have found only one node.
        if len(nodes) > 1:
            message = 'Ricgraph Explorer found too many nodes. It cannot compute the overlap '
            message += 'of the neighbor nodes of more than one node in get_overlap_in_source_systems().'
            return get_message(message=message)

        parent_node = nodes[0]
        if parent_node['category'] == 'person':
            personroot = rcg.get_personroot_node(node=parent_node)
            if personroot is None:
                message = 'Ricgraph Explorer found no "person-root" '
                message += 'node in get_overlap_in_source_systems().'
                return get_message(message=message)
            neighbor_nodes = rcg.get_all_neighbor_nodes(node=personroot)
        else:
            neighbor_nodes = rcg.get_all_neighbor_nodes(node=parent_node)
        nodes = neighbor_nodes.copy()

    nr_total_recs = 0
    nr_recs_from_one_source = 0
    nr_recs_from_multiple_sources = 0
    recs_from_one_source = rcg.create_multidimensional_dict(1, int)
    recs_from_multiple_sources = rcg.create_multidimensional_dict(1, int)
    recs_from_multiple_sources_histogram = rcg.create_multidimensional_dict(2, int)

    # Determine the overlap in source systems.
    for node in nodes:
        sources = node['_source']
        if len(sources) == 0:
            continue
        nr_total_recs += 1
        if len(sources) == 1:
            nr_recs_from_one_source += 1
            recs_from_one_source[sources[0]] += 1
            continue
        nr_recs_from_multiple_sources += 1
        for system1 in sources:
            recs_from_multiple_sources[system1] += 1
            for system2 in sources:
                recs_from_multiple_sources_histogram[system1][system2] += 1

    if nr_total_recs == 0:
        if overlap_mode == 'neighbornodes':
            message = 'Ricgraph Explorer found no overlap in source systems for '
            message += 'the neighbors of this node. '
            message += 'This may be caused by that these neighbors are "person-root" nodes. '
            message += 'These nodes are generated by Ricgraph and do not have a source system.'
            return get_message(message=message)
        return ''

    # Now determine all the systems we have harvested from.
    all_harvested_systems = []
    for system in recs_from_one_source:
        if system not in all_harvested_systems:
            all_harvested_systems.append(system)
    for system in recs_from_multiple_sources:
        if system not in all_harvested_systems:
            all_harvested_systems.append(system)
    all_harvested_systems.sort()

    html += get_html_for_cardstart()
    html += '<h3>Your query</h3>'
    html += 'This was your query:'
    html += '<ul>'
    if name != '':
        html += '<li>name: <i>"' + str(name) + '"</i>'
    if category != '':
        html += '<li>category: <i>"' + str(category) + '"</i>'
    if value != '':
        html += '<li>value: <i>"' + str(value) + '"</i>'
    html += '</ul>'

    html += '<br/>'
    html += '<h3>Number of items in source systems</h3>'
    html += 'This table shows the number of items found in only one source or '
    html += 'found in multiple sources for your query. '
    html += 'You can click on a number to retrieve these items.'
    html += get_html_for_tablestart()
    html += '<tr class="uu-yellow">'
    html += '<th class="sorttable_nosort">Source systems</th>'
    html += '<th class="sorttable_nosort">Total items in source systems: '
    html += str(nr_total_recs)
    html += '</th>'
    html += '<th class="sorttable_nosort">Total items found in only one source: '
    html += str(nr_recs_from_one_source)
    html += ' (' + str(round(100 * nr_recs_from_one_source/nr_total_recs))
    html += '% of total ' + str(nr_total_recs) + ' items)'
    html += '</th>'
    html += '<th class="sorttable_nosort">Total items found in multiple sources: '
    html += str(nr_recs_from_multiple_sources)
    html += ' (' + str(round(100 * nr_recs_from_multiple_sources/nr_total_recs))
    html += '% of total ' + str(nr_total_recs) + ' items)'
    html += '</th>'
    html += '</tr>'

    for system in all_harvested_systems:
        html += '<tr class="item">'
        html += '<td>' + system + '</td>'
        row_total = 0
        if system in recs_from_one_source:
            row_total += recs_from_one_source[system]
        if system in recs_from_multiple_sources:
            row_total += recs_from_multiple_sources[system]

        if row_total > 0:
            html += '<td>' + str(row_total) + '</td>'
        else:
            html += '<td>0</td>'
        if system in recs_from_one_source:
            html += '<td>'
            html += '<a href="' + url_for('resultspage') + '?'
            html += urllib.parse.urlencode({'name': name, 'category': category, 'value': value,
                                            'system1': system,
                                            'system2': 'singlesource',
                                            'view_mode': 'view_regular_table_overlap_records',
                                            'discoverer_mode': discoverer_mode,
                                            'overlap_mode': overlap_mode}
                                           | extra_url_parameters)
            html += '">'
            html += str(recs_from_one_source[system])
            html += '</a>'
            html += ' (' + str(round(100 * recs_from_one_source[system]/nr_recs_from_one_source))
            html += '% of ' + str(nr_recs_from_one_source) + ' items are only in ' + system + ')'
            html += '</td>'
        else:
            html += '<td>0</td>'
        if system in recs_from_multiple_sources:
            html += '<td>'
            html += '<a href="' + url_for('resultspage') + '?'
            html += urllib.parse.urlencode({'name': name, 'category': category, 'value': value,
                                            'system1': system,
                                            'system2': 'multiplesource',
                                            'view_mode': 'view_regular_table_overlap_records',
                                            'discoverer_mode': discoverer_mode,
                                            'overlap_mode': overlap_mode}
                                           | extra_url_parameters)
            html += '">'
            html += str(recs_from_multiple_sources[system])
            html += '</a>'
            html += ' (' + str(round(100 * recs_from_multiple_sources[system]/nr_recs_from_multiple_sources))
            html += '% of ' + str(nr_recs_from_multiple_sources) + ' items are in multiple sources)'
            html += '</td>'
        else:
            html += '<td>0</td>'
    html += '</tr>'
    html += get_html_for_tableend()
    html += 'Note that the numbers in the columns "Total items in source systems" '
    html += 'and "Total items found in multiple sources" do not need '
    html += 'to count up to resp. '
    html += 'the total number of items ('
    html += str(nr_total_recs)
    html += ') and the total number of items from multiple sources ('
    html += str(nr_recs_from_multiple_sources)
    html += ') since an item in that column will originate from multiple sources, and subsequently will occur '
    html += 'in in multiple rows of that column.'

    if nr_recs_from_multiple_sources == 0:
        html += get_html_for_cardend()
        return html

    html += '<br/>'
    html += '<br/>'
    html += '<h3>Overlap in items from multiple sources</h3>'
    html += 'For the items found for your query in multiple sources, this table shows in which sources '
    html += 'they were found. '
    html += 'You can click on a number to retrieve these items. '
    html += 'The second column in this table corresponds to the last column in '
    html += 'the previous table.'

    html += get_html_for_tablestart()
    html_header2 = '<tr class="uu-yellow">'
    html_header2 += '<th class="sorttable_nosort">An item from \u25be...</th>'
    html_header2 += '<th class="sorttable_nosort">Total items found in multiple sources</th>'
    count = 0
    for second in all_harvested_systems:
        html_header2 += '<th class="sorttable_nosort">' + second + '</th>'
        count += 1
    html_header2 += '</tr>'
    html_header1 = '<tr class="uu-yellow">'
    html_header1 += '<th class="sorttable_nosort" colspan="2"></th>'
    html_header1 += '<th class="sorttable_nosort" colspan="' + str(count) + '">... was also found in \u25be</th>'
    html_header1 += '</tr>'
    html += html_header1 + html_header2

    for system1 in all_harvested_systems:
        html += '<tr class="item">'
        html += '<td>' + system1 + '</td>'
        if system1 in recs_from_multiple_sources:
            html += '<td>'
            html += '<a href="' + url_for('resultspage') + '?'
            html += urllib.parse.urlencode({'name': name, 'category': category, 'value': value,
                                            'system1': system1,
                                            'system2': 'multiplesource',
                                            'view_mode': 'view_regular_table_overlap_records',
                                            'discoverer_mode': discoverer_mode,
                                            'overlap_mode': overlap_mode}
                                           | extra_url_parameters)
            html += '">'
            html += str(recs_from_multiple_sources[system1])
            html += '</a>'
            html += '</td>'
        else:
            html += '<td>0</td>'
        for system2 in all_harvested_systems:
            if system1 == system2:
                html += '<td>&check;</td>'
                continue
            if system2 in recs_from_multiple_sources_histogram[system1]:
                html += '<td>'
                html += '<a href="' + url_for('resultspage') + '?'
                html += urllib.parse.urlencode({'name': name, 'category': category, 'value': value,
                                                'system1': system1,
                                                'system2': system2,
                                                'view_mode': 'view_regular_table_overlap_records',
                                                'discoverer_mode': discoverer_mode,
                                                'overlap_mode': overlap_mode}
                                               | extra_url_parameters)
                html += '">'
                html += str(recs_from_multiple_sources_histogram[system1][system2])
                percent = recs_from_multiple_sources_histogram[system1][system2]/recs_from_multiple_sources[system1]
                html += ' (' + str(round(100 * percent)) + '%)'
                html += '</a>'
                html += '</td>'
            else:
                html += '<td>0</td>'
        html += '</tr>'
    html += get_html_for_tableend()
    html += 'Note that the number of items in a row in column 3, 4, etc. do not need '
    html += 'to count up to the total number of items from that source (in the second column), '
    html += 'since an item in this table will originate from at least two sources, '
    html += 'and subsequently will occur multiple times on the same row.'
    html += get_html_for_cardend()

    return html


def find_overlap_in_source_systems_records(name: str = '', category: str = '', value: str = '',
                                           system1: str = '', system2: str = '',
                                           discoverer_mode: str = '',
                                           overlap_mode: str = '',
                                           extra_url_parameters: dict = None) -> str:
    """Show the overlap items in a html table.
    This function is tightly connected to find_overlap_in_source_systems().
    We do need a 'name', 'category' and/or 'value', otherwise we won't be able
    to find overlap in source systems for a list of items.

    :param name: name of the node(s) to find.
    :param category: category of the node(s) to find.
    :param value: value of the node(s) to find.
    :param system1: source system 1 used to compute the overlap.
    :param system2: source system 2 used to compute the overlap.
    :param discoverer_mode: the discoverer_mode to use.
    :param overlap_mode: which overlap to compute: from this node ('thisnode')
      or from the neighbors of this node ('neighbornodes').
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    if extra_url_parameters is None:
        extra_url_parameters = {}

    html = ''
    if system1 == '' and system2 != '':
        # swap
        system1 = system2
        system2 = ''
    if system1 == 'singlesource' or system1 == 'multiplesource':
        if system2 != '':
            # swap
            temp = system1
            system1 = system2
            system2 = temp

    result = rcg.read_all_nodes(name=name, category=category, value=value)
    if len(result) == 0:
        # Let's try again, assuming we did a broad search instead of an exact match search.
        result = rcg.read_all_nodes(value=value,
                                    value_is_exact_match=False)
        if len(result) == 0:
            # No, we really didn't find anything.
            message = 'Unexpected result in find_overlap_in_source_systems_records(): '
            message += 'This node cannot be found in Ricgraph.'
            return get_message(message=message)

    if overlap_mode == 'neighbornodes':
        # In this case, we would like to know the overlap of nodes neighboring the node
        # we have just found. We can only do that if we have found only one node.
        if len(result) > 1:
            message = 'Ricgraph Explorer found too many nodes. It cannot compute the overlap '
            message += 'of the neighbor nodes of more than one node '
            message += 'in find_overlap_in_source_systems_records().'
            return get_message(message=message)

        node = result[0]
        if node['category'] == 'person':
            personroot = rcg.get_personroot_node(node)
            if personroot is None:
                message = 'Unexpected result in find_overlap_in_source_systems_records(): '
                message += 'Ricgraph Explorer found no "person-root" node.'
                return get_message(message=message)
            neighbor_nodes = rcg.get_all_neighbor_nodes(node=personroot)
        else:
            neighbor_nodes = rcg.get_all_neighbor_nodes(node=node)
        result = neighbor_nodes.copy()

    relevant_result = []
    for node in result:
        sources = node['_source']
        if system1 == '':
            # Then system2 will also be '', see swap above.
            relevant_result.append(node)
            continue
        if system2 == '':
            if system1 in sources:
                relevant_result.append(node)
                continue
        if system2 == 'singlesource':
            if system1 in sources and len(sources) == 1:
                relevant_result.append(node)
                continue
        if system2 == 'multiplesource':
            if system1 in sources and len(sources) > 1:
                relevant_result.append(node)
                continue
        if system1 in sources and system2 in sources:
            relevant_result.append(node)

    if discoverer_mode == 'details_view':
        table_columns = DETAIL_COLUMNS
        html += get_you_searched_for_card(name=name,
                                          category=category,
                                          value=value,
                                          discoverer_mode=discoverer_mode,
                                          overlap_mode=overlap_mode,
                                          system1=system1,
                                          system2=system2,
                                          extra_url_parameters=extra_url_parameters)
    else:
        table_columns = RESEARCH_OUTPUT_COLUMNS

    html += get_regular_table(nodes_list=relevant_result,
                              table_header='These items conform to your selection:',
                              table_columns=table_columns,
                              discoverer_mode=discoverer_mode,
                              extra_url_parameters=extra_url_parameters)
    return html


# ##############################################################################
# General functions.
# ##############################################################################
def get_url_parameter_value(parameter: str,
                            allowed_values: list = None,
                            default_value: str = '',
                            use_escape: bool = True) -> str:
    """Get a URL parameter and its value.


    :param parameter: name of the URL parameter.
    :param allowed_values: allowed values of the URL parameter, if any.
    :param default_value: the default value, if any.
    :param use_escape: whether to call escape() or not for the URL parameter. We should
        do this for safety, however, we cannot always do this, because then we
        cannot search correctly in Ricgraph.
        For example, if we would use escape() for a URL parameter that contains an '&',
        such as in 'Department: Research & Data Management Services',
        that '&' will be translated to the HTML character '&amp;', which then
        will not be found in Ricgraph.
    :return: the value of the URL parameter.
    """
    if allowed_values is None:
        allowed_values = []

    if use_escape:
        value = str(escape(request.args.get(parameter, default='')))
    else:
        value = str(request.args.get(parameter, default=''))

    if value == '' and default_value != '':
        value = str(default_value)

    if len(allowed_values) > 0:
        # If 'default_value' == '', then 'value' will be '', which is what we intend.
        if value not in allowed_values:
            value = str(default_value)

    return value


def get_message(message: str, please_try_again: bool = True) -> str:
    """This function creates a html message containing 'message'.

    :param message: the message.
    :param please_try_again: if True, a link to try again will be added.
    :return: html to be rendered.
    """
    html = get_html_for_cardstart()
    html += message
    if please_try_again:
        html += '<br/><a href=' + url_for('homepage') + '>' + 'Please try again' + '</a>.'
    html += get_html_for_cardend()
    return html


def get_found_message(node: Node,
                      table_header: str = '',
                      discoverer_mode: str = '',
                      extra_url_parameters: dict = None) -> str:
    """This function creates a html table containing 'node'.

    :param node: the node to put in the table.
    :param table_header: header for the table.
    :param discoverer_mode: as usual.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    if extra_url_parameters is None:
        extra_url_parameters = {}

    if table_header == '':
        header = 'Ricgraph Explorer found item:'
    else:
        header = table_header

    html = get_regular_table(nodes_list=[node],
                             table_header=header,
                             discoverer_mode=discoverer_mode,
                             extra_url_parameters=extra_url_parameters)
    return html


def create_html_form(destination: str,
                     button_text: str,
                     explanation: str = '',
                     input_fields: dict = None,
                     hidden_fields: dict = None) -> str:
    """Creates a form according to a specification.

    'input_fields' is a dict according to this specification:
    input_fields={label_text: input_spec}. It may have more than one entry.
    'label_text' is the text for the label of the input field,
    and 'input_spec' is a list that specifies how the html for the
    input field is constructed:
    1. input_spec = ('list', <name of field>, <name of datalist>, <datalist>)
    2. input_spec = ('text', <name of field>)
    The first element of the list can only be 'list' or 'text'.

    'hidden_fields' is a dict according to this specification:
    hidden_fields={<name of hidden field>: <value of hidden field>}.
    It may have more than one entry.

    :param destination: function to go to after submitting the form.
    :param button_text: text for the button.
    :param explanation: explanation of the form (optional).
    :param input_fields: see above.
    :param hidden_fields: see above.
    :return: html for the form.
    """
    if input_fields is None:
        input_fields = {}
    if hidden_fields is None:
        hidden_fields = {}
    form = explanation
    form += '<form method="get" action="/' + destination + '/">'
    for item in input_fields:
        if input_fields[item][0] == 'list':
            if len(input_fields[item]) != 4:
                print('Wrong length for input field of type "list": ' +
                      str(len(input_fields[item])) + ', should be 4.')
                continue
            form += '<label>' + item + '</label>'
            form += '<input class="w3-input w3-border" '
            form += 'list="' + input_fields[item][2] + '" '     # 2: name of datalist
            form += 'name="' + input_fields[item][1] + '" '     # 1: name of field
            form += 'id="' + input_fields[item][1] + '" '       # 1: name of field
            form += 'autocomplete=off>'
            form += '<div class="firefox-only">Click twice to get a dropdown list.</div>'
            form += input_fields[item][3]                       # 3: datalist
        if input_fields[item][0] == 'text':
            if len(input_fields[item]) != 2:
                print('Wrong length for input field of type "text": ' +
                      str(len(input_fields[item])) + ', should be 2.')
                continue
            form += '<label>' + item + '</label>'
            form += '<input class="w3-input w3-border" '
            form += 'type="' + input_fields[item][0] + '" '     # 0: type of field ('text')
            form += 'name="' + input_fields[item][1] + '" '     # 1: name of field
            form += '>'

    for item in hidden_fields:
        if isinstance(hidden_fields[item], str):
            form += '<input type="hidden" name="' + item
            form += '" value="' + hidden_fields[item] + '">'
        elif isinstance(hidden_fields[item], list):
            # For every element in the list we add a URL param with
            # the same name and a different value.
            for value in hidden_fields[item]:
                form += '<input type="hidden" name="' + item
                form += '" value="' + value + '">'

    form += '<input class="' + button_style + '"' + button_width
    form += 'type=submit value="' + button_text + '">'
    form += '</form>'
    return form


def get_you_searched_for_card(name: str = 'None', category: str = 'None', value: str = 'None',
                              key: str = 'None',
                              name_list: list = None,
                              category_list: list = None,
                              view_mode: str = 'None',
                              discoverer_mode: str = 'None',
                              overlap_mode: str = 'None',
                              system1: str = 'None',
                              system2: str = 'None',
                              source_system: str = 'None',
                              name_filter: str = 'None',
                              category_filter: str = 'None',
                              extra_url_parameters: dict = None) -> str:
    """Get the html for the "You searched for" card.
    If you do not pass a str parameter, such as 'key', the default value will
    be 'None', which indicates that that value has not been passed.
    Its value will not be shown.
    That is different to passing a parameter 'key' with a value ''.
    Then that parameter will be shown.
    This makes it possible to pass a parameter with value '' and show that value.

    :param name: name.
    :param category: category.
    :param value: value.
    :param key: key.
    :param name_list: name_list.
    :param category_list: category_list.
    :param view_mode: view_mode.
    :param discoverer_mode: discoverer_mode.
    :param overlap_mode: overlap_mode.
    :param system1: system1.
    :param system2: system2.
    :param source_system: source_system.
    :param name_filter: name_filter.
    :param category_filter: category_filter.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    if name_list is None:
        name_list = []
    if category_list is None:
        category_list = []
    if extra_url_parameters is None:
        extra_url_parameters = {}

    html = '<details><summary class="uu-yellow" '
    # Use the same amount at both 'top' and 'margin-bottom'.
    html += 'style="position:relative; top:-3ex; text-align:right; margin-bottom:-3ex; float:right;">'
    html += 'Click for information about your search&nbsp;</summary>'
    html += get_html_for_cardstart()
    html += 'Your search consisted of these fields and values:'
    html += '<ul>'
    if name != 'None':
        html += '<li>name: <i>"' + str(name) + '"</i>'
    if category != 'None':
        html += '<li>category: <i>"' + str(category) + '"</i>'
    if value != 'None':
        html += '<li>value: <i>"' + str(value) + '"</i>'
    if key != 'None':
        html += '<li>key: <i>"' + str(key) + '"</i>'
    if len(name_list) > 0:
        html += '<li>name_list: <i>"' + str(name_list) + '"</i>'
    if len(category_list) > 0:
        html += '<li>category_list: <i>"' + str(category_list) + '"</i>'
    if view_mode != 'None':
        html += '<li>view_mode: <i>"' + str(view_mode) + '"</i>'
    if discoverer_mode != 'None':
        html += '<li>discoverer_mode: <i>"' + str(discoverer_mode) + '"</i>'
    if overlap_mode != 'None':
        html += '<li>overlap_mode: <i>"' + str(overlap_mode) + '"</i>'
    if system1 != 'None':
        html += '<li>system1: <i>"' + str(system1) + '"</i>'
    if system2 != 'None':
        html += '<li>system2: <i>"' + str(system2) + '"</i>'
    if source_system != 'None':
        html += '<li>source_system: <i>"' + str(source_system) + '"</i>'
    if name_filter != 'None':
        html += '<li>name_filter: <i>"' + str(name_filter) + '"</i>'
    if category_filter != 'None':
        html += '<li>category_filter: <i>"' + str(category_filter) + '"</i>'
    for item in extra_url_parameters:
        html += '<li>extra_url_parameters["' + item + '"]: <i>"' + extra_url_parameters[item] + '"</i>'
    html += '</ul>'
    html += get_html_for_cardend()
    html += '</details>'
    return html


def flask_check_file_exists(filename: str) -> bool:
    """Check if a file exists in the static folder.

    :param filename: The name of the file to check.
    :return: True if it exists, otherwise False.
    """
    # This function is called during app initialization.
    # We are outside the app context, because we are not in a route().
    # That means we need to get the app context.
    this_app = ricgraph_explorer.app
    file_path = os.path.join(this_app.static_folder, filename)
    if os.path.isfile(file_path):
        # The file exists in the static folder.
        return True
    else:
        # The file does not exist in the static folder.
        return False


def flask_read_file(filename: str) -> str:
    """Read the contents of a file in the static folder.

    :param filename: The name of the file to read.
    :return: the contents of the file, or '' when the file does not exist.
    """
    if not flask_check_file_exists(filename=filename):
        return ''

    # This function is called during app initialization.
    # We are outside the app context, because we are not in a route().
    # That means we need to get the app context.
    this_app = ricgraph_explorer.app
    file_path = os.path.join(this_app.static_folder, filename)
    with open(file_path, 'r') as file:
        html = file.read()
    return html


# ##############################################################################
# The HTML for the regular, tabbed and faceted tables is generated here.
# ##############################################################################
def create_table_pagination(total_pages, table_id) -> str:
    """Generates w3.css pagination controls for a table.

    :param total_pages: the total pages in the table.
    :param table_id: the id of the table.
    :return: html to be rendered.
    """
    if total_pages <= 1:
        return ''

    # Navigation buttons.
    html = f'<a href="#" onclick="showPage(1, \'{table_id}\')" class="w3-button">&laquo;</a>'
    html += f'<a href="#" onclick="showPage(currentPage[\'{table_id}\']-1, \'{table_id}\')" '
    html += 'class="w3-button">&lsaquo;</a>'

    # Page numbers with dynamic range.
    if total_pages <= 5:
        page_range = range(1, total_pages + 1)
    else:
        page_range = range(1, 6)
        html += f'<span class="ellipsis-left-{table_id}" style="display:none;">...</span>'

    for page in page_range:
        html += f'<a href="#" class="w3-button page-num-{table_id}">{page}</a>'

    if total_pages > 5:
        html += f'<span class="ellipsis-right-{table_id}" style="display:none;">...</span>'

    html += f'<a href="#" onclick="showPage(currentPage[\'{table_id}\']+1, \'{table_id}\')" '
    html += 'class="w3-button">&rsaquo;</a>'
    html += f'<a href="#" onclick="showPage({total_pages}, \'{table_id}\')" '
    html += 'class="w3-button">&raquo;</a>'
    return '<div class="w3-bar">' + html + '</div>'


def get_regular_table(nodes_list: list,
                      table_header: str = '',
                      table_columns: list = None,
                      discoverer_mode: str = '',
                      extra_url_parameters: dict = None) -> str:
    """Create a paginated html table for all nodes in the list.

    :param nodes_list: the nodes to create a table from.
    :param table_header: the html to show above the table.
    :param table_columns: a list of columns to show in the table.
    :param discoverer_mode: the discoverer_mode to use.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    if extra_url_parameters is None:
        extra_url_parameters = {}

    table_id = ''.join(random.choice(string.ascii_lowercase) for _ in range(12))
    table_html = get_regular_table_worker(nodes_list=nodes_list,
                                          table_id=table_id,
                                          table_header=table_header,
                                          table_columns=table_columns,
                                          discoverer_mode=discoverer_mode,
                                          extra_url_parameters=extra_url_parameters)

    max_nr_items = int(extra_url_parameters['max_nr_items'])
    if max_nr_items == 0:
        max_nr_items = rcg.A_LARGE_NUMBER
    len_nodes_list = min(len(nodes_list), max_nr_items)
    max_nr_table_rows = int(extra_url_parameters['max_nr_table_rows'])
    if max_nr_table_rows == 0:
        max_nr_table_rows = len_nodes_list

    javascript = f"""<script>
                 // Initialize currentPage and totalPages for all tables
                 currentPage['{table_id}'] = 1; 
                 totalPages['{table_id}'] = Math.ceil({len_nodes_list} / {max_nr_table_rows});
                 function showPage(page, tableId) {{
                     page = parseInt(page);
                     if (page < 1 || page > totalPages[tableId]) return;
             
                     // Update table visibility
                     document.querySelectorAll(`.table-${{tableId}}-page-${{currentPage[tableId]}}`)
                           .forEach(tr => tr.style.display = 'none');
                     document.querySelectorAll(`.table-${{tableId}}-page-${{page}}`)
                           .forEach(tr => tr.style.display = '');
             
                     currentPage[tableId] = page;
                     updatePagination(tableId);
                 }}
                 function updatePagination(tableId) {{
                     const buttons = document.querySelectorAll(`.page-num-${{tableId}}`);
                     const total = totalPages[tableId];
                     let start = 1;
                     if (total > 5) {{
                         if (currentPage[tableId] <= 3) {{
                             start = 1;
                         }} else if (currentPage[tableId] >= total - 2) {{
                             start = total - 4;
                         }} else {{
                             start = currentPage[tableId] - 2;
                         }}
                     }}
                     buttons.forEach((btn, index) => {{
                         const pageNum = start + index;
                         if (btn) {{
                             btn.textContent = pageNum;
                             btn.onclick = function() {{ showPage(pageNum, tableId); }};
                             btn.classList.toggle('uu-yellow', pageNum === currentPage[tableId]);
                             btn.style.display = pageNum <= total ? '' : 'none';
                         }}
                     }});
                     const ellipsisLeft = document.querySelector(`.ellipsis-left-${{tableId}}`);
                     const ellipsisRight = document.querySelector(`.ellipsis-right-${{tableId}}`);
                     if (ellipsisLeft) ellipsisLeft.style.display = start > 1 ? '' : 'none';
                     if (ellipsisRight) 
                        ellipsisRight.style.display = (start + buttons.length - 1) < total ? '' : 'none';
                     const firstButton = document.querySelector(`a[onclick="showPage(1, '${{tableId}}')"]`);
                     const prevButton = document.querySelector(`a[onclick=
                                        "showPage(currentPage['${{tableId}}']-1, '${{tableId}}')"]`);
                     const nextButton = document.querySelector(`a[onclick=
                                        "showPage(currentPage['${{tableId}}']+1, '${{tableId}}')"]`);
                     const lastButton = document.querySelector(`a[onclick="showPage(${{total}}, '${{tableId}}')"]`);
                     if (firstButton) firstButton.classList.toggle('w3-disabled', currentPage[tableId] === 1);
                     if (prevButton) prevButton.classList.toggle('w3-disabled', currentPage[tableId] === 1);
                     if (nextButton) nextButton.classList.toggle('w3-disabled', currentPage[tableId] === total);
                     if (lastButton) lastButton.classList.toggle('w3-disabled', currentPage[tableId] === total);
                 }}
                 document.addEventListener('DOMContentLoaded', () => {{
                     {f'updatePagination("{table_id}");'}
                 }});
                 </script>"""

    return javascript + table_html


def get_regular_table_worker(nodes_list: list,
                             table_id: str = '',
                             table_header: str = '',
                             table_columns: list = None,
                             discoverer_mode: str = '',
                             extra_url_parameters: dict = None) -> str:
    """Create a html table for all nodes in the list.
    Here the real work is done.

    :param nodes_list: the nodes to create a table from.
    :param table_id: the id of the table, required for pagination.
    :param table_header: the html to show above the table.
    :param table_columns: a list of columns to show in the table.
    :param discoverer_mode: the discoverer_mode to use.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    global nodes_cache

    if extra_url_parameters is None:
        extra_url_parameters = {}
    if table_columns is None:
        if discoverer_mode == 'details_view':
            table_columns = DETAIL_COLUMNS
        else:
            table_columns = RESEARCH_OUTPUT_COLUMNS
    len_nodes_list = len(nodes_list)
    if len_nodes_list == 0:
        return get_message(table_header + '</br>Nothing found.')

    max_nr_items = int(extra_url_parameters['max_nr_items'])
    if max_nr_items == 0:
        max_nr_items = rcg.A_LARGE_NUMBER

    nr_rows_in_table_message = ''
    max_nr_table_rows = int(extra_url_parameters['max_nr_table_rows'])
    if max_nr_table_rows == 0:
        max_nr_table_rows = min(len_nodes_list, max_nr_items)
    if 0 < max_nr_table_rows < len_nodes_list:
        nr_rows_in_table_message = 'There are ' + str(len_nodes_list) + ' rows in this table, showing pages of '
        nr_rows_in_table_message += str(max_nr_table_rows) + '.'
    # elif len_nodes_list == max_nr_table_rows:
    #     # Special case: we have truncated the number of search results somewhere out of efficiency reasons,
    #     # so we have no idea how many search results there are.
    #     nr_rows_in_table_message = 'This table shows the first ' + str(max_nr_table_rows) + ' rows.'
    elif len_nodes_list >= 2:
        nr_rows_in_table_message = 'There are ' + str(len_nodes_list) + ' rows in this table.'

    html = get_html_for_cardstart()
    html += '<span style="float:left;">' + table_header + '</span>'
    html += '<span style="float:right;">' + nr_rows_in_table_message + '</span>'
    html += '<div id="' + table_id + '-container">'     # <div> ends below.
    html += get_html_for_tablestart()
    html += '<thead>'
    html += get_html_for_tableheader(table_columns=table_columns)
    html += '</thead>'
    html += '<tbody>'
    for count, node in enumerate(nodes_list):
        if count >= max_nr_items:
            break
        table_page_num = floor(count / max_nr_table_rows) + 1
        html += get_html_for_tablerow(node=node,
                                      table_id=table_id,
                                      table_columns=table_columns,
                                      table_page_num=table_page_num,
                                      discoverer_mode=discoverer_mode,
                                      extra_url_parameters=extra_url_parameters)

        # Add node to nodes_cache if it is not there already.
        key = node['_key']
        if key not in nodes_cache:
            nodes_cache[key] = node

    html += '</tbody>'
    html += get_html_for_tableend()
    html += '</div>'        # Ends </div> from above '<div id="' + table_id + '-container">'.
    html += nr_rows_in_table_message

    total_pages = ceil(min(len(nodes_list), max_nr_items) / max_nr_table_rows)
    pagination_html = create_table_pagination(total_pages, table_id)
    html += '<div class="w3-center" id="' + table_id + '-pagination-container">' + pagination_html + '</div>'
    html += get_html_for_cardend()
    return html


def get_faceted_table(parent_node: Node,
                      neighbor_nodes: Union[list, None],
                      table_header: str = '',
                      table_columns: list = None,
                      view_mode: str = '',
                      discoverer_mode: str = '',
                      extra_url_parameters: dict = None) -> str:
    """Create a faceted html table for all neighbor_nodes in the list.

    :param parent_node: the parent of the nodes to construct the facets from.
    :param neighbor_nodes: the neighbor_nodes to create a table from.
    :param table_header: the html to show above the table.
    :param table_columns: a list of columns to show in the table.
    :param view_mode: which view to use.
    :param discoverer_mode: the discoverer_mode to use.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    if extra_url_parameters is None:
        extra_url_parameters = {}
    if table_columns is None:
        if discoverer_mode == 'details_view':
            table_columns = DETAIL_COLUMNS
        else:
            table_columns = RESEARCH_OUTPUT_COLUMNS
    if len(neighbor_nodes) == 0:
        return get_message(table_header + '</br>Nothing found.')

    faceted_html = get_facets_from_nodes(parent_node=parent_node,
                                         neighbor_nodes=neighbor_nodes,
                                         view_mode=view_mode,
                                         discoverer_mode=discoverer_mode,
                                         extra_url_parameters=extra_url_parameters)
    table_html = get_regular_table(nodes_list=neighbor_nodes,
                                   table_header=table_header,
                                   table_columns=table_columns,
                                   discoverer_mode=discoverer_mode,
                                   extra_url_parameters=extra_url_parameters)
    html = ''
    if faceted_html == '':
        # Faceted navigation not useful, don't show the panel.
        html += table_html
    else:
        # Divide space between facet panel and table.
        html += '<div class="w3-row-padding w3-stretch">'
        html += '<div class="w3-col" style="width:20em">'
        html += faceted_html
        html += '</div>'
        html += '<div class="w3-rest" >'
        html += table_html
        html += '</div>'
        html += '</div>'

    return html


def get_tabbed_table(nodes_list: Union[list, None],
                     table_header: str = '',
                     table_columns: list = None,
                     tabs_on: str = '',
                     discoverer_mode: str = '',
                     extra_url_parameters: dict = None) -> str:
    """Create a html table with tabs for all nodes in the list.

    :param nodes_list: the nodes to create a table from.
    :param table_header: the html to show above the table.
    :param table_columns: a list of columns to show in the table.
    :param tabs_on: the name of the field in Ricgraph you'd like to have tabs on.
    :param discoverer_mode: the discoverer_mode to use.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """

    table_id = ''.join(random.choice(string.ascii_lowercase) for _ in range(12))

    if extra_url_parameters is None:
        extra_url_parameters = {}
    if table_columns is None:
        if discoverer_mode == 'details_view':
            table_columns = DETAIL_COLUMNS
        else:
            table_columns = RESEARCH_OUTPUT_COLUMNS
    if len(nodes_list) == 0:
        return get_message(table_header + '</br>Nothing found.')
    if tabs_on != 'name' and tabs_on != 'category':
        return get_message(message='get_tabbed_table(): Invalid value for "tabs_on": ' + tabs_on + '.')

    histogram = {}
    for node in nodes_list:
        if node[tabs_on] not in histogram:
            histogram[node[tabs_on]] = 1
        else:
            histogram[node[tabs_on]] += 1

    if len(histogram) == 1:
        # Note: len(histogram) cannot be 0, that has been caught above.
        # If we have only one thing to show tabs on, we do a regular table.
        html = get_regular_table(nodes_list=nodes_list,
                                 table_header=table_header,
                                 table_columns=table_columns,
                                 discoverer_mode=discoverer_mode,
                                 extra_url_parameters=extra_url_parameters)
        return html

    histogram_sort = sorted(histogram, key=histogram.get, reverse=True)

    histogram_list = []
    first_iteration = True
    tab_names_html = '<div class="w3-bar uu-yellow">'
    for tab_name in histogram_sort:
        tab_text = tab_name + '&nbsp;<i>(' + str(histogram[tab_name]) + ')</i>'
        tab_names_html += f'<button class="w3-bar-item w3-button tablink {table_id}'

        if first_iteration:
            tab_names_html += ' uu-orange'
            first_iteration = False
        else:
            tab_names_html += ''
        tab_names_html += f'" onclick="openTab_{table_id}(event,\'{tab_name}\',\'{table_id}\')">{tab_text}</button>'
        histogram_list.append({'name': tab_name, 'value': histogram[tab_name]})
    tab_names_html += '</div>'

    first_iteration = True
    tab_contents_html = ''
    for tab_name in histogram_sort:
        tab_contents_html += f'<div id="{tab_name}" class="w3-container w3-border tabitem {table_id}"'
        if first_iteration:
            tab_contents_html += ''
            first_iteration = False
        else:
            tab_contents_html += ' style="display:none"'
        tab_contents_html += '>'
        nodes_of_tab_name = []
        # Get the nodes of interest. Using rcg.get_all_neighbor_nodes() is not efficient.
        for node in nodes_list:
            if node[tabs_on] == tab_name:
                nodes_of_tab_name.append(node)
        table_title = 'List of ' + tab_name + 's:'
        table = get_regular_table(nodes_list=nodes_of_tab_name,
                                  table_header=table_title,
                                  table_columns=table_columns,
                                  discoverer_mode=discoverer_mode,
                                  extra_url_parameters=extra_url_parameters)
        tab_contents_html += table
        tab_contents_html += '</div>'

    # This code is inspired by https://www.w3schools.com/w3css/w3css_tabulators.asp.
    tab_javascript = """<script>
                        function openTab_""" + table_id + """(evt, tabName, table_id) {
                            var i, x, tablinks;
                            x = document.getElementsByClassName("tabitem");
                            for (i = 0; i < x.length; i++) {
                                if (x[i].className.split(' ').indexOf(table_id) != -1) {
                                    x[i].style.display = "none";
                                }
                            }
                            tablinks = document.getElementsByClassName("tablink");
                            for (i = 0; i < x.length; i++) {
                                if (tablinks[i].className.split(' ').indexOf(table_id) != -1) {
                                    tablinks[i].className = tablinks[i].className.replace(" uu-orange", "");
                                }
                            }
                            document.getElementById(tabName).style.display = "block";
                            evt.currentTarget.className += " uu-orange";
                        }
                        </script>"""

    len_nodes_list = len(nodes_list)
    nr_rows_in_table_message = ''
    max_nr_table_rows = int(extra_url_parameters['max_nr_table_rows'])
    if 0 < max_nr_table_rows < len_nodes_list:
        nr_rows_in_table_message = 'There are ' + str(len_nodes_list) + ' rows in this tabbed table, showing first '
        nr_rows_in_table_message += str(max_nr_table_rows) + '.'
    elif len_nodes_list == max_nr_table_rows:
        # Special case: we have truncated the number of search results somewhere out of efficiency reasons,
        # so we have no idea how many search results there are.
        nr_rows_in_table_message = 'This tabbed table shows the first ' + str(max_nr_table_rows) + ' rows.'
    elif len_nodes_list >= 2:
        nr_rows_in_table_message = 'There are ' + str(len_nodes_list) + ' rows in this tabbed table.'

    table_html = get_html_for_cardstart()
    table_html += '<span style="float:left;">' + table_header + '</span>'
    table_html += '<span style="float:right;">' + nr_rows_in_table_message + '</span>'

    table_html += tab_names_html + tab_contents_html + tab_javascript
    table_html += nr_rows_in_table_message
    table_html += get_html_for_cardend()

    # Note that len(histogram) and subsequently len(histogram_list) is always > 1.
    histogram_html = get_html_for_cardstart()
    histogram_html += get_html_for_histogram(histogram_list=histogram_list,
                                             histogram_width=200,
                                             histogram_title='Histogram')
    histogram_html += get_html_for_cardend()

    # The following is partly copied from get_faceted_table().
    # We could split this function similar to get_faceted_table(), i.e. in a function
    # that shows the left panel (histogram) and right panel (tabbed table),
    # and a function that generates the tabbed table, but this will not work since
    # the function that generates the histogram needs the histogram computed in the
    # function that generates the tabbed table.
    html = ''
    # Divide space between histogram panel and table.
    html += '<div class="w3-row-padding w3-stretch" >'
    html += '<div class="w3-col" style="width:20em" >'
    html += histogram_html
    html += '</div>'
    html += '<div class="w3-rest" >'
    html += table_html
    html += '</div>'
    html += '</div>'

    return html


def get_facets_from_nodes(parent_node: Node,
                          neighbor_nodes: list,
                          view_mode: str = '',
                          discoverer_mode: str = '',
                          extra_url_parameters: dict = None) -> str:
    """Do facet navigation in Ricgraph.
    The facets will be constructed based on 'name' and 'category'.
    Facets chosen will be "caught" in function search().
    If there is only one facet (for either one or both), it will not be shown.

    :param parent_node: the parent of the nodes to construct the facets from.
    :param neighbor_nodes: the nodes to construct the facets from.
    :param view_mode: which view to use.
    :param discoverer_mode: the discoverer_mode to use.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered, or empty string ('') if faceted navigation is
      not useful because there is only one facet.
    """
    if extra_url_parameters is None:
        extra_url_parameters = {}
    if len(neighbor_nodes) == 0:
        return ''

    name_histogram = {}
    category_histogram = {}
    for node in neighbor_nodes:
        if node['name'] not in name_histogram:
            name_histogram[node['name']] = 1
        else:
            name_histogram[node['name']] += 1

        if node['category'] not in category_histogram:
            category_histogram[node['category']] = 1
        else:
            category_histogram[node['category']] += 1

    if len(name_histogram) <= 1 and len(category_histogram) <= 1:
        # We have only one facet, so don't show the facet panel.
        return ''

    name_list = []
    category_list = []
    faceted_form = get_html_for_cardstart()
    faceted_form += '<div class="facetedform">'
    faceted_form += '<form method="get" action="' + url_for('resultspage') + '">'
    faceted_form += '<input type="hidden" name="key" value="' + str(parent_node['_key']) + '">'
    faceted_form += '<input type="hidden" name="view_mode" value="' + str(view_mode) + '">'
    faceted_form += '<input type="hidden" name="discoverer_mode" value="' + str(discoverer_mode) + '">'
    for item in extra_url_parameters:
        faceted_form += '<input type="hidden" name="' + item + '" value="' + extra_url_parameters[item] + '">'
    if len(name_histogram) == 1:
        # Get the first (and only) element in the dict, pass it as hidden field to search().
        name_key = str(list(name_histogram.keys())[0])
        faceted_form += '<input type="hidden" name="name_list" value="' + name_key + '">'
    else:
        faceted_form += '<div class="w3-card-4">'
        faceted_form += '<div class="w3-container uu-yellow">'
        faceted_form += '<b>Filter on "name"</b>'
        faceted_form += '</div>'
        faceted_form += '<div class="w3-container" style="font-size: 90%;">'
        # Sort a dict on value:
        # https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
        for bucket in sorted(name_histogram, key=name_histogram.get, reverse=True):
            name_label = bucket + '&nbsp;<i>(' + str(name_histogram[bucket]) + ')</i>'
            faceted_form += '<input class="w3-check" type="checkbox" name="name_list" value="'
            faceted_form += bucket + '" checked>'
            faceted_form += '<label>&nbsp;' + name_label + '</label><br/>'
            name_list.append({'name': bucket, 'value': name_histogram[bucket]})
        faceted_form += '</div>'
        faceted_form += '</div><br/>'

    if len(category_histogram) == 1:
        # Get the first (and only) element in the dict, pass it as hidden field to search().
        category_key = str(list(category_histogram.keys())[0])
        faceted_form += '<input type="hidden" name="category_list" value="' + category_key + '">'
    else:
        faceted_form += '<div class="w3-card-4">'
        faceted_form += '<div class="w3-container uu-yellow">'
        faceted_form += '<b>Filter on "category"</b>'
        faceted_form += '</div>'
        faceted_form += '<div class="w3-container" style="font-size: 90%;">'
        for bucket in sorted(category_histogram, key=category_histogram.get, reverse=True):
            category_label = bucket + '&nbsp;<i>(' + str(category_histogram[bucket]) + ')</i>'
            faceted_form += '<input class="w3-check" type="checkbox" name="category_list" value="'
            faceted_form += bucket + '" checked>'
            faceted_form += '<label>&nbsp;' + category_label + '</label><br/>'
            category_list.append({'name': bucket, 'value': category_histogram[bucket]})
        faceted_form += '</div>'
        faceted_form += '</div><br/>'

    # Send name, category and value as hidden fields to search().
    faceted_form += '<input class="w3-input' + button_style + '" style="width:8em;" type=submit value="refresh">'
    faceted_form += '</form>'
    faceted_form += '</div>'
    faceted_form += get_html_for_cardend()

    if len(name_list) > 1:
        faceted_form += get_html_for_cardstart()
        faceted_form += get_html_for_histogram(histogram_list=name_list,
                                               histogram_width=200,
                                               histogram_title='Histogram on "name"')
        faceted_form += get_html_for_cardend()
    if len(category_list) > 1:
        faceted_form += get_html_for_cardstart()
        faceted_form += get_html_for_histogram(histogram_list=category_list,
                                               histogram_width=200,
                                               histogram_title='Histogram on "category"')
        faceted_form += get_html_for_cardend()

    html = faceted_form
    return html


def get_html_for_histogram(histogram_list: list,
                           histogram_width: int = 200,
                           histogram_title: str = ''):
    """This function creates a histogram using the Observable D3 and Observable Plot framework
     for data visualization. See https://d3js.org and https://observablehq.com/plot.

    :param histogram_list: A list of histogram data to be plotted in the histogram.
      Each element in the list has a 'name' and 'value'.
      The histogram will be in the order as specified in the list. It is assumed that
      the largest value of the histogram is in the first element of the list. This
      value is used to compute whether a histogram label should be shown in the histogram
      bar or next to it.
    :param histogram_width: The width of the histogram, in pixels.
    :param histogram_title: The title of the histogram.
    :return: html to be rendered.
    """
    # The required js files for Observable are included in html_body_end above.
    # The code below is inspired by an example from
    # https://observablehq.com/@observablehq/plot-labelled-horizontal-bar-chart-variants.

    if len(histogram_list) == 0:
        message = 'Unexpected result in get_html_for_histogram(): '
        message += 'The histogram list is empty.'
        return get_message(message=message)

    # Note: 'histogram_list' is expected to be sorted with the largest value first.
    bar_label_threshold = histogram_list[0]['value']
    histogram_json = json.dumps(histogram_list)

    # The plot name should be unique, otherwise we get strange side effects.
    plot_name = 'myplot' + '_' + str(uuid.uuid4())

    html = '<div class="w3-card-4">'
    if histogram_title != '':
        html += '<div class="w3-container uu-yellow">'
        html += '<b>' + histogram_title + '</b>'
        html += '</div>'
    html += '</br>'
    html += '<div id="' + plot_name + '"></div>'
    html += '</br></div>'

    html += '<script type="module">'
    html += 'const brands = ' + histogram_json + '; '
    html += 'const plot = Plot.plot({ '
    html += 'width: ' + str(histogram_width) + ', '
    html += """axis: null,
                // Make height dependent on the number of items in brands.
                // The "+ 40" is for the horizontal scale.
                height: brands.length * 20 + 40,
                x: { insetRight: 10 },
                marks: [
                  Plot.axisX({anchor: "bottom"}),
                  Plot.barX(brands, {
                    x: "value",
                    y: "name",
                    // uu-yellow
                    fill: "#ffcd00",
                    // no ordering
                    sort: { y: "x", order: null }
                }),
                // labels for larger bars
                Plot.text(brands, {
                  text: (d) => `${d.name} (${d.value})`,
                  y: "name",
                  frameAnchor: "left",
                  dx: 3,
            """
    html += 'filter: (d) => d.value >= ' + str(bar_label_threshold/2) + ', '
    html += """}),
                // labels for smaller bars
                Plot.text(brands, {
                  text: (d) => `${d.name} (${d.value})`,
                  y: "name",
                  x: "value",
                  textAnchor: "start",
                  dx: 3,
            """
    html += 'filter: (d) => d.value < ' + str(bar_label_threshold/2) + ', '
    html += """})
            ]           // End of marks
            });         // End of Plot.plot()
            """
    html += 'const div = document.querySelector("#' + plot_name + '");'
    html += 'div.append(plot);'
    html += '</script>'

    return html


# ##############################################################################
# The general HTML for the tables is generated here.
# ##############################################################################
def get_html_for_tablestart() -> str:
    """Get the html required for the start of a html table.

    :return: html to be rendered.
    """
    html = '<table class="sortable w3-table">'
    return html


def get_html_for_tableheader(table_columns: list = None) -> str:
    """Get the html required for the header of a html table.

    :param table_columns: a list of columns to show in the table.
    :return: html to be rendered.
    """
    if table_columns is None:
        table_columns = []
    html = '<tr class="uu-yellow">'
    if 'name' in table_columns:
        html += '<th>name</th>'
    if 'category' in table_columns:
        html += '<th>category</th>'
    if 'value' in table_columns:
        html += '<th class=sorttable_alpha">value</th>'
    if 'comment' in table_columns:
        html += '<th>comment</th>'
    if 'year' in table_columns:
        html += '<th>year</th>'
    if 'url_main' in table_columns:
        html += '<th class="sorttable_nosort">url_main</th>'
    if 'url_other' in table_columns:
        html += '<th class="sorttable_nosort">url_other</th>'
    if '_source' in table_columns:
        html += '<th class="sorttable_nosort">_source</th>'
    if '_history' in table_columns:
        html += '<th class="sorttable_nosort">_history</th>'
    html += '</tr>'
    return html


def get_html_for_tablerow(node: Node,
                          table_id: str = '',
                          table_columns: list = None,
                          table_page_num: int = 1,
                          discoverer_mode: str = '',
                          extra_url_parameters: dict = None) -> str:
    """Get the html required for a row of a html table.

    :param node: the node to show in the table.
    :param table_id: the id of the table, required for pagination.
    :param table_columns: a list of columns to show in the table.
    :param table_page_num: the page number of the table.
    :param discoverer_mode: the discoverer_mode to use.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    if table_columns is None:
        table_columns = []
    if extra_url_parameters is None:
        extra_url_parameters = {}

    # Show only the first page initially.
    display_style = '' if table_page_num == 1 else 'display: none;'
    html = '<tr class="table-' + table_id + '-page-' + str(table_page_num) + ' '
    html += 'item" style="' + display_style + '">'

    if 'name' in table_columns:
        # Name can never be empty, it is part of _key.
        html += '<td>' + node['name'] + '</td>'
    if 'category' in table_columns:
        if node['category'] == '':
            html += '<td></td>'
        else:
            html += '<td>' + node['category'] + '</td>'
    if 'value' in table_columns:
        # Value can never be empty, it is part of _key.
        key = rcg.create_ricgraph_key(name=node['name'], value=node['value'])
        html += '<td><a href=' + url_for('optionspage') + '?'
        html += urllib.parse.urlencode({'key': key,
                                        'discoverer_mode': discoverer_mode}
                                       | extra_url_parameters) + '>'
        html += node['value'] + '</a></td>'
    if 'comment' in table_columns:
        if isinstance(node['comment'], str):
            if node['comment'] == '':
                html += '<td><ul>'
            else:
                html += '<td width=30%>' + node['comment'] + '</td>'
        else:
            if node['name'] == 'person-root' and isinstance(node['comment'], list):
                # If this is a person-root node, we put the FULL_NAME(s) in the comment column,
                # for easier browsing.
                html += '<td><ul>'
                for cached_name in node['comment']:
                    html += '<li>' + cached_name + '</li>'
                html += '</ul></td>'
            else:
                html += '<td width=30%>' + str(node['comment']) + '</td>'
    if 'year' in table_columns:
        if node['year'] == '':
            html += '<td></td>'
        else:
            html += '<td>' + node['year'] + '</td>'
    if 'url_main' in table_columns:
        if node['url_main'] == '':
            html += '<td></td>'
        else:
            html += '<td><a href=' + node['url_main'] + ' target="_blank"> url_main link </a></td>'
    if 'url_other' in table_columns:
        if node['url_other'] == '':
            html += '<td></td>'
        else:
            html += '<td><a href=' + node['url_other'] + ' target="_blank"> url_other link </a></td>'
    if '_source' in table_columns:
        if isinstance(node['_source'], str):
            html += '<td>' + node['_source'] + '</td>'
        else:
            html += '<td><ul>'
            for source in node['_source']:
                html += '<li>' + source + '</li>'
            html += '</ul></td>'
    if '_history' in table_columns:
        if isinstance(node['_history'], str):
            html += '<td>' + node['_history'] + '</td>'
        else:
            html += '<td><details><summary>Click for history</summary><ul>'
            for history in node['_history']:
                html += '<li>' + history + '</li>'
            html += '</ul></details></td>'
    html += '</tr>'
    return html


def get_html_for_tableend() -> str:
    """Get the html required for the end of a html table.

    :return: html to be rendered.
    """
    html = '</table>'
    return html


# ##############################################################################
# The HTML for the W3CSS cards is generated here.
# ##############################################################################
def get_html_for_cardstart() -> str:
    """Get the html required for the start of a W3.CSS 'card'.
    W3.CSS is a modern, responsive, mobile first CSS framework.

    :return: html to be rendered.
    """
    html = '<section class="w3-container">'
    html += '<div class="w3-card-4">'
    html += '<div class="w3-container w3-responsive">'
    return html


def get_html_for_cardend() -> str:
    """Get the html required for the end of a W3.CSS 'card'.
    W3.CSS is a modern, responsive, mobile first CSS framework.

    :return: html to be rendered.
    """
    html = '</div>'
    html += '</div>'
    html += '</section>'
    return html


def get_html_for_cardline() -> str:
    """Get the html required for a yellow line. It is a W3.CSS 'card'
    filled with the color 'yellow'.

    :return: html to be rendered.
    """
    html = '<section class="w3-container">'
    html += '<div class="w3-card-4">'
    # Adjust the height of the line is padding-top + padding-bottom.
    html += '<div class="w3-container uu-yellow" style="padding-top:3px; padding-bottom:3px">'
    html += '</div>'
    html += '</div>'
    html += '</section>'
    return html


# ##############################################################################
# REST API functions.
# Ricgraph uses the OpenAPI format: https://www.openapis.org.
# We use Connexion: https://connexion.readthedocs.io/en/latest.
# ##############################################################################
def api_search_person(value: str = '',
                      max_nr_items: str = MAX_ITEMS) -> Tuple[dict, int]:
    """REST API Search for a person.

    :param value: value of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    response, status = api_search_general(value=value,
                                          name_restriction='FULL_NAME',
                                          max_nr_items=max_nr_items)
    return response, status


def api_person_all_information(key: str = '',
                               max_nr_items: str = MAX_ITEMS):
    """REST API Show all information related to this person.

    :param key: key of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    # This implements view_mode = 'view_unspecified_table_everything'.
    # graph = current_app.config.get('graph')
    get_all_globals_from_app_context()
    if key == '':
        response, status = rcg.create_http_response(message='You have not specified a search key',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    nodes = rcg.read_all_nodes(key=key)
    if len(nodes) == 0:
        response, status = rcg.create_http_response(message='Nothing found',
                                                    http_status=rcg.HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    personroot_node = rcg.get_personroot_node(node=nodes[0])
    if personroot_node is None:
        response, status = rcg.create_http_response(message='No person-root node found',
                                                    http_status=rcg.HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    # Now we have the person-root, and we can reuse api_all_information_general().
    response, status = api_all_information_general(key=personroot_node['_key'],
                                                   max_nr_items=max_nr_items)
    return response, status


def api_person_share_research_results(key: str = '',
                                      max_nr_items: str = MAX_ITEMS):
    """REST API Find persons that share any share research result types with this person.

    :param key: key of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    # This implements view_mode = 'view_regular_table_person_share_resouts'.
    # See function find_person_share_resouts().
    get_all_globals_from_app_context()
    if key == '':
        response, status = rcg.create_http_response(message='You have not specified a search key',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if not max_nr_items.isnumeric():
        max_nr_items = MAX_ITEMS
    nodes = rcg.read_all_nodes(key=key)
    if len(nodes) == 0:
        response, status = rcg.create_http_response(message='Nothing found',
                                                    http_status=rcg.HTTP_RESPONSE_NOTHING_FOUND)
        return response, status

    connected_persons = \
        find_person_share_resouts_cypher(parent_node=nodes[0],
                                         category_dontwant_list=['person', 'competence', 'organization'],
                                         max_nr_items=max_nr_items)
    if len(connected_persons) == 0:
        message = 'Could not find persons that share any share research result types '
        message += 'with this person'
        response, status = rcg.create_http_response(message=message,
                                                    http_status=rcg.HTTP_RESPONSE_OK)
        return response, status

    result_list = rcg.convert_nodes_to_list_of_dict(connected_persons,
                                                    max_nr_items=max_nr_items)
    response, status = rcg.create_http_response(result_list=result_list,
                                                message=str(len(result_list)) + ' items found',
                                                http_status=rcg.HTTP_RESPONSE_OK)
    return response, status


def api_person_collaborating_organizations(key: str = '',
                                           max_nr_items: str = MAX_ITEMS):
    """REST API Find persons that share any share research result types with this person.

    :param key: key of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    # This implements view_mode = 'view_regular_table_person_organization_collaborations'.
    # See function find_person_organization_collaborations().
    get_all_globals_from_app_context()
    if key == '':
        response, status = rcg.create_http_response(message='You have not specified a search key',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if not max_nr_items.isnumeric():
        max_nr_items = MAX_ITEMS
    nodes = rcg.read_all_nodes(key=key)
    if len(nodes) == 0:
        response, status = rcg.create_http_response(message='Nothing found',
                                                    http_status=rcg.HTTP_RESPONSE_NOTHING_FOUND)
        return response, status

    personroot_node_organizations, collaborating_organizations = \
        find_person_organization_collaborations_cypher(parent_node=nodes[0],
                                                       max_nr_items=max_nr_items)
    message = ''
    if len(personroot_node_organizations) == 0:
        message += 'This person does not work at any organization. '
    else:
        message += 'This person works at ' + str(len(personroot_node_organizations))
        message += ' organizations, these are in "person_works_at". '
    if len(collaborating_organizations) == 0:
        message += 'This person has no collaborations with other organizations.'
    else:
        message += 'This person collaborates with ' + str(len(collaborating_organizations))
        message += ' organizations, these are in "person_collaborates_with".'

    person_worksat_list = rcg.convert_nodes_to_list_of_dict(personroot_node_organizations,
                                                            max_nr_items=max_nr_items)
    person_collaborates_list = rcg.convert_nodes_to_list_of_dict(collaborating_organizations,
                                                                 max_nr_items=max_nr_items)
    meta = {'message': message}
    result = {'meta': meta,
              'person_works_at': person_worksat_list,
              'person_collaborates_with': person_collaborates_list}
    result_list = [result]
    response, status = rcg.create_http_response(result_list=result_list,
                                                message=str(len(result_list)) + ' items found',
                                                http_status=rcg.HTTP_RESPONSE_OK)
    return response, status


def api_person_enrich(key: str = '',
                      name_want: list = None,
                      category_want: list = None,
                      source_system: str = '',
                      max_nr_items: str = MAX_ITEMS):
    """REST API Find persons that share any share research result types with this person.

    :param key: key of the node(s) to find.
    :param name_want: a list containing several node names, indicating
      that we want all neighbor nodes of the person-root node of the organization
      specified by 'key', where the property 'name' equals
      one of the names in the list 'name_want'
      (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty (empty string), return all nodes.
    :param category_want: similar to 'name_want', but now for the property 'category'.
    :param source_system: the source system to find enrichments for.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    # This implements view_mode = 'view_regular_table_person_enrich_source_system'.
    # See function find_enrich_candidates().
    get_all_globals_from_app_context()
    if name_want is None:
        name_want = []
    if category_want is None:
        category_want = []

    if key == '':
        response, status = rcg.create_http_response(message='You have not specified a search key',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if result := list(set(name_want) - set(name_all)):
        response, status = rcg.create_http_response(message='You have not specified a valid name_want: '
                                                            + str(result) + '".',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if result := list(set(category_want) - set(category_all)):
        response, status = rcg.create_http_response(message='You have not specified a valid category_want: '
                                                            + str(result) + '".',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if source_system == '':
        response, status = rcg.create_http_response(message='You have not specified a source system',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if source_system not in source_all:
        response, status = rcg.create_http_response(message='You have not specified a valid source system "'
                                                            + source_system + '".',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if not max_nr_items.isnumeric():
        max_nr_items = MAX_ITEMS
    nodes = rcg.read_all_nodes(key=key)
    if len(nodes) == 0:
        response, status = rcg.create_http_response(message='Nothing found',
                                                    http_status=rcg.HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    personroot_node = rcg.get_personroot_node(node=nodes[0])
    if personroot_node is None:
        response, status = rcg.create_http_response(message='No person-root node found',
                                                    http_status=rcg.HTTP_RESPONSE_NOTHING_FOUND)
        return response, status

    person_nodes, nodes_not_in_source_system = \
        find_enrich_candidates_one_person(personroot=personroot_node,
                                          name_want=name_want,
                                          category_want=category_want,
                                          source_system=source_system)
    if len(nodes_not_in_source_system) == 0:
        message = 'Ricgraph could not find any information in other source systems '
        message += 'to enrich source system "' + source_system + '"'
        response, status = rcg.create_http_response(message=message,
                                                    http_status=rcg.HTTP_RESPONSE_NOTHING_FOUND)
        return response, status

    message = ''
    if len(person_nodes) == 0:
        message += 'There are enrich candidates '
        message += 'to enrich source system "' + source_system
        message += '", but there are no "person" nodes to identify this item in "'
        message += source_system + '". '
    else:
        message += 'There are ' + str(len(person_nodes))
        message += ' items in "person_identifying_nodes" you can use to find this item '
        message += 'in source system "' + source_system + '". '

    # Note: len(nodes_not_in_source_system) > 0.
    message += 'There are ' + str(len(nodes_not_in_source_system))
    message += ' items in "person_enrich_nodes" you can use to enrich source system "'
    message += source_system + '" by using information harvested from other source systems.'

    person_identifying_nodes_list = rcg.convert_nodes_to_list_of_dict(person_nodes,
                                                                      max_nr_items=max_nr_items)
    person_enrich_nodes_list = rcg.convert_nodes_to_list_of_dict(nodes_not_in_source_system,
                                                                 max_nr_items=max_nr_items)
    meta = {'message': message}
    result = {'meta': meta,
              'person_identifying_nodes': person_identifying_nodes_list,
              'person_enrich_nodes': person_enrich_nodes_list}
    result_list = [result]
    response, status = rcg.create_http_response(result_list=result_list,
                                                message=str(len(result_list)) + ' items found',
                                                http_status=rcg.HTTP_RESPONSE_OK)
    return response, status


def api_search_organization(value: str = '',
                            max_nr_items: str = MAX_ITEMS) -> Tuple[dict, int]:
    """REST API Search for a (sub-)organization.

    :param value: value of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    response, status = api_search_general(value=value,
                                          category_restriction='organization',
                                          max_nr_items=max_nr_items)
    return response, status


def api_organization_all_information(key: str = '',
                                     max_nr_items: str = MAX_ITEMS):
    """REST API Show all information related to this organization.

    :param key: key of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    # This implements view_mode = 'view_unspecified_table_organizations'.
    response, status = api_all_information_general(key=key,
                                                   max_nr_items=max_nr_items)
    return response, status


def api_organization_information_persons_results(key: str = '',
                                                 name_want: list = None,
                                                 category_want: list = None,
                                                 max_nr_items: str = MAX_ITEMS):
    """REST API Find any information from persons or their results in this organization.

    :param key: key of the node(s) to find.
    :param name_want: a list containing several node names, indicating
      that we want all neighbor nodes of the person-root node of the organization
      specified by 'key', where the property 'name' equals
      one of the names in the list 'name_want'
      (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty (empty string), return all nodes.
    :param category_want: similar to 'name_want', but now for the property 'category'.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    # This implements view_mode = 'view_regular_table_organization_addinfo'.
    # See function find_organization_additional_info().
    response, status = api_organization_enrich(key=key,
                                               name_want=name_want,
                                               category_want=category_want,
                                               max_nr_items=max_nr_items)
    return response, status


def api_organization_enrich(key: str = '',
                            name_want: list = None,
                            category_want: list = None,
                            source_system: str = '',
                            max_nr_items: str = MAX_ITEMS):
    """REST API Find persons that share any share research result types with this organization.

    :param key: key of the node(s) to find.
    :param name_want: a list containing several node names, indicating
      that we want all neighbor nodes of the person-root node of the organization
      specified by 'key', where the property 'name' equals
      one of the names in the list 'name_want'
      (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty (empty string), return all nodes.
    :param category_want: similar to 'name_want', but now for the property 'category'.
    :param source_system: the source system to find enrichments for.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    # This implements view_mode = 'view_regular_table_organization_addinfo'.
    # See function find_organization_additional_info().
    get_all_globals_from_app_context()
    if name_want is None:
        name_want = []
    if category_want is None:
        category_want = []

    if key == '':
        response, status = rcg.create_http_response(message='You have not specified a search key',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if result := list(set(name_want) - set(name_all)):
        response, status = rcg.create_http_response(message='You have not specified a valid name_want: '
                                                            + str(result) + '".',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if result := list(set(category_want) - set(category_all)):
        response, status = rcg.create_http_response(message='You have not specified a valid category_want: '
                                                            + str(result) + '".',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if source_system == '':
        response, status = rcg.create_http_response(message='You have not specified a source system',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if source_system not in source_all:
        response, status = rcg.create_http_response(message='You have not specified a valid source system "'
                                                            + source_system + '".',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if not max_nr_items.isnumeric():
        max_nr_items = MAX_ITEMS
    nodes = rcg.read_all_nodes(key=key)
    if len(nodes) == 0:
        response, status = rcg.create_http_response(message='Nothing found',
                                                    http_status=rcg.HTTP_RESPONSE_NOTHING_FOUND)
        return response, status

    cypher_result = find_organization_additional_info_cypher(parent_node=nodes[0],
                                                             name_list=name_want,
                                                             category_list=category_want,
                                                             source_system=source_system,
                                                             max_nr_items=max_nr_items)
    if len(cypher_result) == 0:
        message = 'Could not find any information from persons or '
        message += 'their results in this organization'
        response, status = rcg.create_http_response(message=message,
                                                    http_status=rcg.HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    relevant_result = []
    for result in cypher_result:
        node = result['second_neighbor']
        relevant_result.append(node)

    result_list = rcg.convert_nodes_to_list_of_dict(relevant_result,
                                                    max_nr_items=max_nr_items)
    response, status = rcg.create_http_response(result_list=result_list,
                                                message=str(len(result_list)) + ' items found',
                                                http_status=rcg.HTTP_RESPONSE_OK)
    return response, status


def api_search_competence(value: str = '',
                          max_nr_items: str = MAX_ITEMS) -> Tuple[dict, int]:
    """REST API Search for a skill, expertise area or research area.

    :param value: value of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    response, status = api_search_general(value=value,
                                          category_restriction='competence',
                                          max_nr_items=max_nr_items)
    return response, status


def api_competence_all_information(key: str = '',
                                   max_nr_items: str = MAX_ITEMS):
    """REST API Show all information related to this competence.

    :param key: key of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    response, status = api_all_information_general(key=key,
                                                   max_nr_items=max_nr_items)
    return response, status


def api_broad_search(value: str = '',
                     max_nr_items: str = MAX_ITEMS) -> Tuple[dict, int]:
    """REST API Search for anything (broad search).

    :param value: value of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    response, status = api_search_general(value=value,
                                          max_nr_items=max_nr_items)
    return response, status


def api_advanced_search(name: str = '', category: str = '', value: str = '',
                        max_nr_items: str = MAX_ITEMS) -> Tuple[dict, int]:
    """REST API Advanced search.

    :param name: name of the node(s) to find.
    :param category: category of the node(s) to find.
    :param value: value of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    get_all_globals_from_app_context()
    if name == '' and category == '' and value == '':
        response, status = rcg.create_http_response(message='You have not specified any search string',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if not max_nr_items.isnumeric():
        max_nr_items = MAX_ITEMS
    nodes = rcg.read_all_nodes(name=name,
                               category=category,
                               value=value,
                               value_is_exact_match=True,
                               max_nr_nodes=int(max_nr_items))
    if len(nodes) == 0:
        response, status = rcg.create_http_response(message='Nothing found',
                                                    http_status=rcg.HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    result_list = rcg.convert_nodes_to_list_of_dict(nodes,
                                                    max_nr_items=max_nr_items)
    response, status = rcg.create_http_response(result_list=result_list,
                                                message=str(len(result_list)) + ' items found',
                                                http_status=rcg.HTTP_RESPONSE_OK)
    return response, status


def api_search_general(value: str = '',
                       name_restriction: str = '',
                       category_restriction: str = '',
                       max_nr_items: str = MAX_ITEMS) -> Tuple[dict, int]:
    """REST API General broad search function.

    :param value: value of the node(s) to find.
    :param name_restriction: Restrict the broad search on a certain name.
    :param category_restriction: Restrict the broad search on a certain category.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    get_all_globals_from_app_context()
    if value == '':
        response, status = rcg.create_http_response(message='You have not specified a search string',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if len(value) < 3:
        response, status = rcg.create_http_response(message='The search string should be at least three characters',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if not max_nr_items.isnumeric():
        max_nr_items = MAX_ITEMS
    nodes = rcg.read_all_nodes(name=name_restriction,
                               category=category_restriction,
                               value=value,
                               value_is_exact_match=False,
                               max_nr_nodes=int(max_nr_items))
    if len(nodes) == 0:
        response, status = rcg.create_http_response(message='Nothing found',
                                                    http_status=rcg.HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    result_list = rcg.convert_nodes_to_list_of_dict(nodes,
                                                    max_nr_items=max_nr_items)
    response, status = rcg.create_http_response(result_list=result_list,
                                                message=str(len(result_list)) + ' items found',
                                                http_status=rcg.HTTP_RESPONSE_OK)
    return response, status


def api_all_information_general(key: str = '',
                                max_nr_items: str = MAX_ITEMS):
    """REST API General all information about a node function.

    :param key: key of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    get_all_globals_from_app_context()
    if key == '':
        response, status = rcg.create_http_response(message='You have not specified a search key',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if not max_nr_items.isnumeric():
        max_nr_items = MAX_ITEMS
    nodes = rcg.read_all_nodes(key=key)
    if len(nodes) == 0:
        response, status = rcg.create_http_response(message='Nothing found',
                                                    http_status=rcg.HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    neighbor_nodes = rcg.get_all_neighbor_nodes(node=nodes[0],
                                                max_nr_neighbor_nodes=int(max_nr_items))
    if len(neighbor_nodes) == 0:
        response, status = rcg.create_http_response(message='Nothing found',
                                                    http_status=rcg.HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    result_list = rcg.convert_nodes_to_list_of_dict(neighbor_nodes,
                                                    max_nr_items=max_nr_items)
    response, status = rcg.create_http_response(result_list=result_list,
                                                message=str(len(result_list)) + ' items found',
                                                http_status=rcg.HTTP_RESPONSE_OK)
    return response, status


def api_get_all_personroot_nodes(key: str = '',
                                 max_nr_items: str = MAX_ITEMS):
    """REST API Get all the person-root nodes of a node.

    :param key: key of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    get_all_globals_from_app_context()
    if key == '':
        response, status = rcg.create_http_response(message='You have not specified a search key',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    nodes = rcg.read_all_nodes(key=key)
    if len(nodes) == 0:
        response, status = rcg.create_http_response(message='Nothing found',
                                                    http_status=rcg.HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    personroot_nodes = rcg.get_all_personroot_nodes(node=nodes[0])
    if len(personroot_nodes) == 0:
        response, status = rcg.create_http_response(message='Nothing found',
                                                    http_status=rcg.HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    result_list = rcg.convert_nodes_to_list_of_dict(personroot_nodes,
                                                    max_nr_items=max_nr_items)
    response, status = rcg.create_http_response(result_list=result_list,
                                                message=str(len(result_list)) + ' items found',
                                                http_status=rcg.HTTP_RESPONSE_OK)
    return response, status


def api_get_all_neighbor_nodes(key: str = '',
                               name_want: list = None,
                               name_dontwant: list = None,
                               category_want: list = None,
                               category_dontwant: list = None,
                               max_nr_items: str = MAX_ITEMS):
    """REST API Get all the neighbor nodes of a node.

    :param key: key of the node(s) to find.
    :param name_want: a list containing several node names, indicating
      that we want all neighbor nodes where the property 'name' equals
      one of the names in the list 'name_want'
      (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty (empty string), return all nodes.
    :param name_dontwant: similar, but for property 'name' and nodes we don't want.
      If empty (empty string), all nodes are 'wanted'.
    :param category_want: similar to 'name_want', but now for the property 'category'.
    :param category_dontwant: similar, but for property 'category' and nodes we don't want.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    get_all_globals_from_app_context()
    if name_want is None:
        name_want = []
    if name_dontwant is None:
        name_dontwant = []
    if category_want is None:
        category_want = []
    if category_dontwant is None:
        category_dontwant = []

    if key == '':
        response, status = rcg.create_http_response(message='You have not specified a search key',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if result := list(set(name_want) - set(name_all)):
        response, status = rcg.create_http_response(message='You have not specified a valid name_want: '
                                                            + str(result) + '".',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if result := list(set(name_dontwant) - set(name_all)):
        response, status = rcg.create_http_response(message='You have not specified a valid name_dontwant: '
                                                            + str(result) + '".',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if result := list(set(category_want) - set(category_all)):
        response, status = rcg.create_http_response(message='You have not specified a valid category_want: '
                                                            + str(result) + '".',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if result := list(set(category_dontwant) - set(category_all)):
        response, status = rcg.create_http_response(message='You have not specified a valid category_dontwant: '
                                                            + str(result) + '".',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    nodes = rcg.read_all_nodes(key=key)
    if len(nodes) == 0:
        response, status = rcg.create_http_response(message='Nothing found',
                                                    http_status=rcg.HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    neighbor_nodes = rcg.get_all_neighbor_nodes(node=nodes[0],
                                                name_want=name_want,
                                                name_dontwant=name_dontwant,
                                                category_want=category_want,
                                                category_dontwant=category_dontwant,
                                                max_nr_neighbor_nodes=int(max_nr_items))
    if len(neighbor_nodes) == 0:
        response, status = rcg.create_http_response(message='Nothing found',
                                                    http_status=rcg.HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    result_list = rcg.convert_nodes_to_list_of_dict(neighbor_nodes,
                                                    max_nr_items=max_nr_items)
    response, status = rcg.create_http_response(result_list=result_list,
                                                message=str(len(result_list)) + ' items found',
                                                http_status=rcg.HTTP_RESPONSE_OK)
    return response, status


def api_get_ricgraph_list(ricgraph_list_name: str = '') -> Tuple[dict, int]:
    """REST API Get values of a specified Ricgraph global list.

    :param ricgraph_list_name: name of the Ricgraph global list.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    global name_all, name_personal_all, category_all, source_all, resout_types_all
    global personal_types_all, remainder_types_all

    get_all_globals_from_app_context()
    if ricgraph_list_name == '':
        response, status = rcg.create_http_response(message='You have not specified a name of a Ricgraph list',
                                                    http_status=rcg.HTTP_RESPONSE_INVALID_SEARCH)
        return response, status

    result_list = []
    if ricgraph_list_name == 'name_all':
        result_list = name_all.copy()
    if ricgraph_list_name == 'name_personal_all':
        result_list = name_personal_all.copy()
    if ricgraph_list_name == 'category_all':
        result_list = category_all.copy()
    if ricgraph_list_name == 'source_all':
        result_list = source_all.copy()
    if ricgraph_list_name == 'resout_types_all':
        result_list = resout_types_all.copy()
    if ricgraph_list_name == 'personal_types_all':
        result_list = personal_types_all.copy()
    if ricgraph_list_name == 'remainder_types_all':
        result_list = remainder_types_all.copy()

    if len(result_list) == 0:
        response, status = rcg.create_http_response(message='You have not specified a valid name of a Ricgraph list',
                                                    http_status=rcg.HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    response, status = rcg.create_http_response(result_list=result_list,
                                                message=str(len(result_list)) + ' items found',
                                                http_status=rcg.HTTP_RESPONSE_OK)
    return response, status


# ################################################
# Ricgraph Explorer initialization.
# ################################################
def store_global_in_app_context(name: str, value) -> None:
    """Stores a global variable in the app context.
    This is required, otherwise we don't have them if we e.g. do
    a second REST API call.

    :param name: the name of the global.
    :param value: the value of the global.
    :return: None.
    """
    with ricgraph_explorer.app.app_context():
        ricgraph_explorer.app.config[name] = value
    return


def get_all_globals_from_app_context() -> None:
    """Get all global variables from the app context.

    :return: None.
    """
    global graph
    global name_all, name_personal_all, category_all, source_all, resout_types_all
    global name_all_datalist, category_all_datalist, source_all_datalist, resout_types_all_datalist
    global personal_types_all, remainder_types_all
    global privacy_statement_link, privacy_measures_link
    global homepage_intro_html

    if 'graph' in current_app.config:
        graph = current_app.config.get('graph')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "graph".')
        exit(2)
    if 'name_all' in current_app.config:
        name_all = current_app.config.get('name_all')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "name_all".')
        exit(2)
    if 'name_personal_all' in current_app.config:
        name_personal_all = current_app.config.get('name_personal_all')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "name_personal_all".')
        exit(2)
    if 'category_all' in current_app.config:
        category_all = current_app.config.get('category_all')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "category_all".')
        exit(2)
    if 'source_all' in current_app.config:
        source_all = current_app.config.get('source_all')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "source_all".')
        exit(2)
    if 'resout_types_all' in current_app.config:
        resout_types_all = current_app.config.get('resout_types_all')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "resout_types_all".')
        exit(2)
    if 'name_all_datalist' in current_app.config:
        name_all_datalist = current_app.config.get('name_all_datalist')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "name_all_datalist".')
        exit(2)
    if 'category_all_datalist' in current_app.config:
        category_all_datalist = current_app.config.get('category_all_datalist')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "category_all_datalist".')
        exit(2)
    if 'source_all_datalist' in current_app.config:
        source_all_datalist = current_app.config.get('source_all_datalist')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "source_all_datalist".')
        exit(2)
    if 'resout_types_all_datalist' in current_app.config:
        resout_types_all_datalist = current_app.config.get('resout_types_all_datalist')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "resout_types_all_datalist".')
        exit(2)
    if 'personal_types_all' in current_app.config:
        personal_types_all = current_app.config.get('personal_types_all')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "personal_types_all".')
        exit(2)
    if 'remainder_types_all' in current_app.config:
        remainder_types_all = current_app.config.get('remainder_types_all')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "remainder_types_all".')
        exit(2)
    if 'privacy_statement_link' in current_app.config:
        privacy_statement_link = current_app.config.get('privacy_statement_link')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "privacy_statement_link".')
        exit(2)
    if 'privacy_measures_link' in current_app.config:
        privacy_measures_link = current_app.config.get('privacy_measures_link')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "privacy_measures_link".')
        exit(2)
    if 'homepage_intro_html' in current_app.config:
        homepage_intro_html = current_app.config.get('homepage_intro_html')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "homepage_intro_html".')
        exit(2)
    return


def initialize_ricgraph_explorer():
    """Initialize Ricgraph Explorer.
    :return: None.
    """
    global graph
    global name_all, name_personal_all, category_all, source_all, resout_types_all
    global name_all_datalist, category_all_datalist, source_all_datalist, resout_types_all_datalist
    global personal_types_all, remainder_types_all
    global privacy_statement_link, privacy_measures_link
    global homepage_intro_html

    graph = rcg.open_ricgraph()
    if graph is None:
        print('Ricgraph could not be opened.')
        exit(2)
    store_global_in_app_context(name='graph', value=graph)

    name_all = rcg.read_all_values_of_property('name')
    if len(name_all) == 0:
        print('Warning (possibly Error) in obtaining list with all property values for property "name".')
        print('Continuing with an empty list. This might give unexpected results.')
        name_all = []
    name_personal_all = rcg.read_all_values_of_property('name_personal')
    if len(name_personal_all) == 0:
        print('Warning (possibly Error) in obtaining list with all property values for property "name_personal".')
        print('Continuing with an empty list. This might give unexpected results.')
        name_personal_all = []
    category_all = rcg.read_all_values_of_property('category')
    if len(category_all) == 0:
        print('Warning (possibly Error) in obtaining list with all property values for property "category".')
        print('Continuing with an empty list. This might give unexpected results.')
        category_all = []
    source_all = rcg.read_all_values_of_property('_source')
    if len(source_all) == 0:
        print('Warning (possibly Error) in obtaining list with all property values for property "_source".')
        print('Continuing with an empty list. This might give unexpected results.')
        source_all = []
    store_global_in_app_context(name='name_all', value=name_all)
    store_global_in_app_context(name='name_personal_all', value=name_personal_all)
    store_global_in_app_context(name='category_all', value=category_all)
    store_global_in_app_context(name='source_all', value=source_all)

    name_all_datalist = '<datalist id="name_all_datalist">'
    for property_item in name_all:
        name_all_datalist += '<option value="' + property_item + '">'
    name_all_datalist += '</datalist>'
    store_global_in_app_context(name='name_all_datalist', value=name_all_datalist)

    if 'competence' in category_all:
        personal_types_all = ['person', 'competence']
    else:
        personal_types_all = ['person']
    store_global_in_app_context(name='personal_types_all', value=personal_types_all)

    resout_types_all = []
    resout_types_all_datalist = '<datalist id="resout_types_all_datalist">'
    remainder_types_all = []
    category_all_datalist = '<datalist id="category_all_datalist">'
    for property_item in category_all:
        if property_item in rcg.ROTYPE_ALL:
            resout_types_all.append(property_item)
            resout_types_all_datalist += '<option value="' + property_item + '">'
        if property_item not in personal_types_all:
            remainder_types_all.append(property_item)
        category_all_datalist += '<option value="' + property_item + '">'
    resout_types_all_datalist += '</datalist>'
    category_all_datalist += '</datalist>'
    store_global_in_app_context(name='resout_types_all', value=resout_types_all)
    store_global_in_app_context(name='resout_types_all_datalist', value=resout_types_all_datalist)
    store_global_in_app_context(name='remainder_types_all', value=remainder_types_all)
    store_global_in_app_context(name='category_all_datalist', value=category_all_datalist)

    source_all_datalist = '<datalist id="source_all_datalist">'
    for property_item in source_all:
        source_all_datalist += '<option value="' + property_item + '">'
    source_all_datalist += '</datalist>'
    store_global_in_app_context(name='source_all_datalist', value=source_all_datalist)

    if flask_check_file_exists(filename=PRIVACY_STATEMENT_FILE):
        privacy_statement_link = '<a href=/static/' + PRIVACY_STATEMENT_FILE + '>'
        privacy_statement_link += 'Read the privacy statement</a>. '
    else:
        privacy_statement_link = ''
    store_global_in_app_context(name='privacy_statement_link', value=privacy_statement_link)
    if flask_check_file_exists(filename=PRIVACY_MEASURES_FILE):
        privacy_measures_link = '<a href=/static/' + PRIVACY_MEASURES_FILE + '>'
        privacy_measures_link += 'Read the privacy measures document</a>. '
    else:
        privacy_measures_link = ''
    store_global_in_app_context(name='privacy_measures_link', value=privacy_measures_link)

    homepage_intro_html = flask_read_file(filename=HOMEPAGE_INTRO_FILE)
    store_global_in_app_context(name='homepage_intro_html', value=homepage_intro_html)
    return


# ################################################
# #### Entry point for WSGI Gunicorn server   ####
# #### using Uvicorn for ASGI applications    ####
# ################################################
def create_ricgraph_explorer_app():
    global page_footer, page_footer_wsgi
    global ricgraph_explorer

    initialize_ricgraph_explorer()
    page_footer = ''
    if privacy_statement_link != '' or privacy_measures_link != '':
        page_footer = '<footer class="w3-container rj-gray" style="font-size:80%">'
        page_footer += privacy_statement_link
        page_footer += privacy_measures_link
        page_footer += '</footer>'
    page_footer += page_footer_wsgi

    return ricgraph_explorer


# ############################################
# ################### main ###################
# ############################################
if __name__ == "__main__":
    initialize_ricgraph_explorer()
    page_footer = ''
    if privacy_statement_link != '' or privacy_measures_link != '':
        page_footer = '<footer class="w3-container rj-gray" style="font-size:80%">'
        page_footer += privacy_statement_link
        page_footer += privacy_measures_link
        page_footer += '</footer>'
    page_footer += page_footer_development

    ricgraph_explorer.run(port=3030)
