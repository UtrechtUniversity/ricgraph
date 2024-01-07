# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
#
# Copyright (c) 2023 Rik D.T. Janssen
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
# To keep it simple, everything has been done in this file.
#
# Please note that this code is meant for research purposes,
# not for production use. That means, this code has not been hardened for
# "the outside world". Be careful if you expose it to the outside world.
#
# Original version Rik D.T. Janssen, January 2023.
# Extended Rik D.T. Janssen, February, September 2023 to January 2024.
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
# Explanation why sometimes Cypher query are used.
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
# may be a bit slow. In case a loop runs done over a large number of nodes or edges,
# many calls to the graph database backend are done, which may take a lot of time.
# A cypher query is one call to the graph database backend. Also, there are
# many query optimizations in that backend, and the backend is a compiled application.
#
# ##############################################################################


import os
import sys
import urllib.parse
from typing import Union
from py2neo import Node, NodeMatch
from flask import Flask, request, url_for, send_from_directory
from markupsafe import escape
import ricgraph as rcg

ricgraph_explorer = Flask(__name__)

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
MAX_RESULTS = 50

# If we render a table, we return at most this number of rows in that table.
MAX_ROWS_IN_TABLE = 250

# If we search for neighbors of an 'organization' node, in the first filter
# in filterorganization(), we restrict it to return at most this number of nodes.
MAX_ORGANIZATION_NODES_TO_RETURN = 4 * MAX_ROWS_IN_TABLE

# It is possible to find enrichments for all nodes in Ricgraph. However, that
# will take a long time. This is the maximum number of nodes Ricgraph Explorer
# is going to enrich in find_enrich_candidates().
MAX_NR_NODES_TO_ENRICH = 20

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

global name_all_datalist, category_all_datalist, source_all, source_all_datalist
global resout_types_all, resout_types_all_datalist
global personal_types_all, remainder_types_all

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
stylesheet += '</style>'

# The html preamble
html_preamble = '<meta name="viewport" content="width=device-width, initial-scale=1">'
# The W3.css style file is at https://www.w3schools.com/w3css/4/w3.css. I use the "pro" version.
# The pro version is identical to the standard version except for it has no colors defined.
html_preamble += '<link rel="stylesheet" href="/static/w3pro.css">'
html_preamble += '<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Open+Sans">'

# The html page header.
page_header = '<header class="w3-container uu-yellow">'
page_header += '<div class="w3-bar uu-yellow">'
page_header += '<div class="w3-bar-item w3-mobile" style="padding-left:0em; padding-right:4em;">'
page_header += '<a href="/" style="text-decoration:none; color:#000000; font-size:130%;">'
page_header += '<img src="/static/uu_logo_small.png" height="30" style="padding-right:3em;">'
page_header += '<img src="/static/ricgraph_logo.png" height="30" style="padding-right:0.5em;">Explorer</a>'
page_header += '</div>'
page_header += '<a href="/" class="w3-bar-item'
page_header += button_style_border + '" style="min-width:12em;">Home</a>'
page_header += '<a href="/searchpage?search_mode=exact_match" class="w3-bar-item'
page_header += button_style_border + '" style="min-width:12em;">Advanced search</a>'
page_header += '<a href="/searchpage?search_mode=value_search" class="w3-bar-item'
page_header += button_style_border + '" style="min-width:12em;">Broad search</a>'
page_header += '</div>'
page_header += '</header>'

# The html page footer.
page_footer = '<footer class="w3-container rj-gray" style="font-size:80%">'
page_footer += 'Disclaimer: Ricgraph Explorer is recommended for research use, not for production use. '
page_footer += 'For more information about Ricgraph and Ricgraph Explorer, see '
page_footer += '<a href=https://github.com/UtrechtUniversity/ricgraph>'
page_footer += 'https://github.com/UtrechtUniversity/ricgraph</a>.'
page_footer += '</footer>'

# The first part of the html page, up to stylesheet and page_header.
html_body_start = '<!DOCTYPE html>'
html_body_start += '<html>'
html_body_start += html_preamble
html_body_start += '<title>Ricgraph Explorer</title>'
html_body_start += '<body>'
html_body_start += stylesheet
html_body_start += page_header

# The last part of the html page, from page_footer to script inclusion.
html_body_end = page_footer
html_body_end += '<script src="/static/ricgraph_sorttable.js"></script>'
html_body_end += '</body>'
html_body_end += '</html>'


# ##############################################################################
# Favicon
# ##############################################################################
@ricgraph_explorer.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(ricgraph_explorer.root_path, 'static'),
                               path='favicon.ico',
                               mimetype='image/png')


# ##############################################################################
# Entry functions.
# Ricgraph Explorer has three web pages:
# 1. homepage.
# 2. searchpage.
# 3a. if there is more than one result: optionspage with a list of nodes to choose from.
# 3b. if there is just one result: optionspage, this page depends on the node type found.
# 4. resultspage, this page depends on what the user would like to see.
# ##############################################################################
@ricgraph_explorer.route(rule='/')
def homepage() -> str:
    """Ricgraph Explorer entry, the home page, when you access '/'.

    :return: html to be rendered.
    """
    global html_body_start, html_body_end
    global source_all, category_all

    html = html_body_start
    html += get_html_for_cardstart()
    html += '<h3>This is Ricgraph Explorer</h3>'
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
                             button_text='search for a (child) organization',
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
    html += '<h4>Statistics</h4>'
    html += '<ul>'
    html += '<li>'
    html += 'Ricgraph contains data from the following source systems: '
    html += ', '.join([str(source) for source in source_all])
    html += '.'
    html += '</li>'
    html += '<li>'
    html += 'There are ' + str(nr_nodes) + ' nodes and ' + str(nr_edges) + ' edges.'
    html += '</li>'
    html += '<li>'
    html += 'The node cache has ' + str(len(nodes_cache)) + ' elements, and its size is '
    html += str(round(sys.getsizeof(nodes_cache)/1000, 1)) + ' kB.'
    html += '</li>'
    html += '</ul>'
    html += get_html_for_cardend()
    html += html_body_end
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
    global html_body_start, html_body_end
    global name_all_datalist, category_all, category_all_datalist

    name = get_url_parameter_value(parameter='name')
    category = get_url_parameter_value(parameter='category')
    search_mode = get_url_parameter_value(parameter='search_mode',
                                          allowed_values=['exact_match', 'value_search'],
                                          default_value=DEFAULT_SEARCH_MODE)
    discoverer_mode = get_url_parameter_value(parameter='discoverer_mode',
                                              allowed_values=['details_view', 'person_view'],
                                              default_value=DEFAULT_DISCOVERER_MODE)
    html = html_body_start
    html += get_html_for_cardstart()

    form = '<form method="get" action="/optionspage">'
    if search_mode == 'exact_match':
        form += '<label>Search for a value in Ricgraph field <em>name</em>:</label>'
        form += '<input class="w3-input w3-border" list="name_all_datalist"'
        form += 'name=name id=name autocomplete=off>'
        form += name_all_datalist
        form += '<br/>'

        form += '<label>Search for a value in Ricgraph field <em>category</em>:</label>'
        form += '<input class="w3-input w3-border" list="category_all_datalist"'
        form += 'name=category id=category autocomplete=off>'
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
    radio_details_text += 'research outputs are presented in a table with <em>facets</em> '
    radio_details_tooltip = '<img src="/static/circle_info_solid_uuyellow.svg">'
    radio_details_tooltip += '<div class="w3-text" style="margin-left:60px;"> '
    radio_details_tooltip += 'This view shows all columns in Ricgraph. '
    radio_details_tooltip += 'Research outputs are presented in a table with <em>facets</em>. '
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

    form += '<br/><input class="' + button_style + '" ' + button_width + ' type=submit value=search>'
    form += '</form>'
    html += form

    html += get_html_for_cardend()
    html += html_body_end
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

    returns html to parse.
    """
    global html_body_start, html_body_end, nodes_cache

    search_mode = get_url_parameter_value(parameter='search_mode',
                                          allowed_values=['exact_match', 'value_search'],
                                          default_value=DEFAULT_SEARCH_MODE)
    key = get_url_parameter_value(parameter='key', use_escape=False)
    if key != '':
        # We prefer the URL parameter 'key' above 'name' & 'value'
        name = rcg.get_namepart_from_ricgraph_key(key=key)
        category = ''
        value = rcg.get_valuepart_from_ricgraph_key(key=key)
        search_mode = 'exact_match'
    else:
        name = get_url_parameter_value(parameter='name')
        category = get_url_parameter_value(parameter='category')
        value = get_url_parameter_value(parameter='value', use_escape=False)
    discoverer_mode = get_url_parameter_value(parameter='discoverer_mode',
                                              allowed_values=['details_view', 'person_view'],
                                              default_value=DEFAULT_DISCOVERER_MODE)

    html = html_body_start
    if name == '' and category == '' and value == '':
        html += get_message(message='Ricgraph Explorer could not find anything.')
        html += html_body_end
        return html

    # First check if the node is in 'node_cache'.
    if name != '' and value != '':
        key = rcg.create_ricgraph_key(name=name, value=value)
        if key in nodes_cache:
            node = nodes_cache[key]
            html += create_options_page(node=node, discoverer_mode=discoverer_mode)
            html += html_body_end
            return html

    # No, it is not.
    if search_mode == 'exact_match':
        result = rcg.read_all_nodes(name=name, category=category, value=value)
    else:
        if len(value) < 3:
            html += get_message(message='The search string should be at least three characters.')
            html += html_body_end
            return html
        result = rcg.read_all_nodes_containing_value(name=name, category=category, value=value)
    if len(result) == 0:
        # We didn't find anything.
        html += get_message(message='Ricgraph Explorer could not find anything.')
        html += html_body_end
        return html
    if len(result) > 1:
        table_header = 'Your search resulted in more than one node. Please choose one node to continue:'
        html += get_regular_table(nodes_list=result,
                                  table_header=table_header,
                                  discoverer_mode=discoverer_mode)
        html += html_body_end
        return html

    node = result.first()
    key = rcg.create_ricgraph_key(name=node['name'], value=node['value'])
    nodes_cache[key] = node
    html += create_options_page(node=node, discoverer_mode=discoverer_mode)
    html += html_body_end
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

    returns html to parse.
    """
    global html_body_start, html_body_end

    view_mode = get_url_parameter_value(parameter='view_mode')
    key = get_url_parameter_value(parameter='key', use_escape=False)
    discoverer_mode = get_url_parameter_value(parameter='discoverer_mode',
                                              allowed_values=['details_view', 'person_view'],
                                              default_value=DEFAULT_DISCOVERER_MODE)
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
        html += html_body_end
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
                                                       overlap_mode=overlap_mode)
        html += html_body_end
        return html

    html += create_results_page(view_mode=view_mode,
                                key=key,
                                name_list=name_list,
                                category_list=category_list,
                                discoverer_mode=discoverer_mode)

    html += html_body_end
    return html


# ##############################################################################
# This is where the work is done.
# ##############################################################################

def create_options_page(node: Node, discoverer_mode: str = '') -> str:
    """This function creates the page with options to choose from, depending on the
    choice the user has made on the index page.
    The 'view_mode' that is used, is caught first in resultspage() and then
    in create_results_page().

    :param node: the node that is found and that determines the possible choices.
    :param discoverer_mode: as usual.
    :return: html to be rendered.
    """
    global name_all_datalist, category_all_datalist, source_all_datalist
    global category_all, resout_types_all, resout_types_all_datalist

    html = ''
    if node is None:
        return get_message(message='create_options_page(): Node is None. This should not happen.')

    if discoverer_mode == 'details_view':
        html += get_you_searched_for_card(key=node['_key'],
                                          discoverer_mode=discoverer_mode)

    key = node['_key']
    html += get_found_message(node=node, discoverer_mode=discoverer_mode)

    # This is used more than once, so we define it here.
    overlap = get_html_for_cardstart()
    explanation = '<h5>More information about overlap in source systems</h5>'
    explanation += 'If the information in Ricgraph for for the neighbors of this node have originated '
    explanation += 'from more than one source system, you can find out from which ones.</br>'
    button_text = 'find the overlap in source systems for '
    button_text += 'the neighbor nodes of this node (this may take some time)'
    overlap += create_html_form(destination='resultspage',
                                button_text=button_text,
                                explanation=explanation,
                                hidden_fields={'key': key,
                                               'discoverer_mode': discoverer_mode,
                                               'view_mode': 'view_regular_table_overlap'
                                               })
    overlap += get_html_for_cardend()

    if node['category'] == 'organization':
        html += get_html_for_cardstart()
        html += '<h4>What would you like to see from this organization?</h4>'
        html += create_html_form(destination='resultspage',
                                 button_text='show persons related to this organization',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'name_list': 'person-root',
                                                'view_mode': 'view_regular_table_persons_of_org'
                                                })
        html += '<p/>'

        html += create_html_form(destination='resultspage',
                                 button_text='show all information related to this organization',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_unspecified_table_organizations'
                                                })
        html += get_html_for_cardend()

        html += get_html_for_cardstart()
        html += '<h4>Advanced information related to this organization</h4>'
        html += 'Depending on the number of persons in ' + str(node['value']) + ', '
        html += 'the following options may take some time before showing the result.'
        html += get_html_for_cardstart()
        html += '<h5>More information about persons or their results in this organization.</h5>'
        html += create_html_form(destination='resultspage',
                                 button_text='find research outputs from all persons in this organization',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'category_list': resout_types_all,
                                                'view_mode': 'view_regular_table_organization_addinfo'
                                                })
        html += '<p/>'

        if 'competence' in category_all:
            html += create_html_form(destination='resultspage',
                                     button_text='find skills from all persons in this organization',
                                     hidden_fields={'key': key,
                                                    'discoverer_mode': discoverer_mode,
                                                    'category_list': 'competence',
                                                    'view_mode': 'view_regular_table_organization_addinfo'
                                                    })
            html += '<p/>'

        button_text = 'find any information from persons or their results '
        button_text += 'in this organization'
        html += create_html_form(destination='resultspage',
                                 button_text=button_text,
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_regular_table_organization_addinfo'
                                                })
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
                                                })
        html += get_html_for_cardend()
        html += overlap
        html += get_html_for_cardend()

    elif node['category'] == 'person':
        html += get_html_for_cardstart()
        html += '<h4>What would you like to see from this person?</h4>'

        html += create_html_form(destination='resultspage',
                                 button_text='show personal information related to this person',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'category_list': 'person',
                                                'view_mode': 'view_regular_table_personal'
                                                })
        html += '<p/>'

        html += create_html_form(destination='resultspage',
                                 button_text='show organizations related to this person',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'category_list': 'organization',
                                                'view_mode': 'view_regular_table_organizations'
                                                })
        html += '<p/>'

        html += create_html_form(destination='resultspage',
                                 button_text='show research outputs related to this person',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'category_list': resout_types_all,
                                                'view_mode': 'view_unspecified_table_resouts'
                                                })
        html += '<p/>'

        everything_except_ids = category_all.copy()
        everything_except_ids.remove('person')
        html += create_html_form(destination='resultspage',
                                 button_text='show everything except identities related to this person',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'category_list': everything_except_ids,
                                                'view_mode': 'view_unspecified_table_everything_except_ids'
                                                })
        html += '<p/>'

        html += create_html_form(destination='resultspage',
                                 button_text='show all information related to this person',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'category_list': remainder_types_all,
                                                'view_mode': 'view_unspecified_table_everything'
                                                })
        html += get_html_for_cardend()

        html += get_html_for_cardstart()
        html += '<h4>Advanced information related to this person</h4>'
        html += get_html_for_cardstart()
        html += '<h5>With whom does this person share research outputs?</h5>'
        html += create_html_form(destination='resultspage',
                                 button_text='find persons that share any research output types with this person',
                                 hidden_fields={'key': key,
                                                'category_list': resout_types_all,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_regular_table_person_share_resouts'
                                                })

        html += '<br/>'
        label_text = 'By entering a value in the field below, '
        label_text += 'you will get a list of persons who share a specific research output type with this person:'
        input_spec = ('list', 'category_list', 'resout_types_all_datalist', resout_types_all_datalist)
        html += create_html_form(destination='resultspage',
                                 button_text='find persons that share a specific research output type with this person',
                                 input_fields={label_text: input_spec},
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_regular_table_person_share_resouts'
                                                })

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
                                                })
        html += get_html_for_cardend()
        html += overlap
        html += get_html_for_cardend()

    # Note: view_mode == 'view_regular_table_overlap_records' is caught in resultspage().

    else:
        html = create_results_page(view_mode='view_regular_table_category',
                                   key=key,
                                   discoverer_mode=discoverer_mode)

    return html


def create_results_page(view_mode: str,
                        key: str,
                        name_list: list = None,
                        category_list: list = None,
                        discoverer_mode: str = '') -> str:
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
    category_list_str = ''
    if len(category_list) == 1:
        category_list_str = category_list[0]

    html = ''
    if key in nodes_cache:
        node = nodes_cache[key]
    else:
        result = rcg.read_all_nodes(name=rcg.get_namepart_from_ricgraph_key(key=key),
                                    value=rcg.get_valuepart_from_ricgraph_key(key=key))
        if len(result) == 0 or len(result) > 1:
            if len(result) == 0:
                message = 'Ricgraph Explorer could not find anything. '
            else:
                message = 'Ricgraph Explorer found too many nodes. '
            message += 'This should not happen. '
            return get_message(message=message)
        node = result.first()
        nodes_cache[key] = node

    if discoverer_mode == 'details_view':
        table_columns_ids = DETAIL_COLUMNS
        table_columns_org = DETAIL_COLUMNS
        table_columns_resout = DETAIL_COLUMNS
        if node is not None:
            html += get_you_searched_for_card(key=node['_key'],
                                              name_list=name_list,
                                              category_list=category_list,
                                              view_mode=view_mode,
                                              discoverer_mode=discoverer_mode)
    else:
        table_columns_ids = ID_COLUMNS
        table_columns_org = ORGANIZATION_COLUMNS
        table_columns_resout = RESEARCH_OUTPUT_COLUMNS

    # We need this multiple times.
    node_found = get_found_message(node=node, discoverer_mode=discoverer_mode)

    if view_mode == 'view_regular_table_personal':
        personroot_node = rcg.get_personroot_node(node=node)
        neighbor_nodes_personal = rcg.get_all_neighbor_nodes(node=personroot_node,
                                                             category_want=personal_types_all)
        html += node_found
        if discoverer_mode == 'details_view':
            html += get_regular_table(nodes_list=neighbor_nodes_personal,
                                      table_header='This is personal information related to this person:',
                                      table_columns=table_columns_ids,
                                      discoverer_mode=discoverer_mode)
        else:
            html += view_personal_information(nodes_list=neighbor_nodes_personal,
                                              discoverer_mode=discoverer_mode)

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
                                  discoverer_mode=discoverer_mode)

    elif view_mode == 'view_regular_table_persons_of_org':
        # Some organizations have a large number of neighbors, but we will only show
        # MAX_ROWS_IN_TABLE in the table. Therefore, reduce the number of neighbors when
        # searching for persons in an organization. Don't do this for other view_modes, because
        # in that case the table shows how many records are found.
        neighbor_nodes = rcg.get_all_neighbor_nodes(node=node,
                                                    name_want=name_list,
                                                    category_want=category_list,
                                                    max_nr_neighbor_nodes=MAX_ROWS_IN_TABLE)
        table_header = 'These are persons related to this organization:'
        table_columns = table_columns_ids
        html += node_found
        html += get_regular_table(nodes_list=neighbor_nodes,
                                  table_header=table_header,
                                  table_columns=table_columns,
                                  discoverer_mode=discoverer_mode)

    elif view_mode == 'view_unspecified_table_organizations':
        # Some organizations have a large number of neighbors, but we will only show
        # MAX_ROWS_IN_TABLE in the table. Therefore, reduce the number of neighbors when
        # searching for persons in an organization. Don't do this for other view_modes, because
        # in that case the table shows how many records are found.
        neighbor_nodes = rcg.get_all_neighbor_nodes(node=node,
                                                    name_want=name_list,
                                                    category_want=category_list,
                                                    max_nr_neighbor_nodes=MAX_ROWS_IN_TABLE)
        table_header = 'This is all information related to this organization:'
        html += node_found
        if discoverer_mode == 'details_view':
            html += get_faceted_table(parent_node=node,
                                      neighbor_nodes=neighbor_nodes,
                                      table_header=table_header,
                                      table_columns=table_columns_resout,
                                      view_mode=view_mode,
                                      discoverer_mode=discoverer_mode)
        else:
            html += get_tabbed_table(nodes_list=neighbor_nodes,
                                     table_header=table_header,
                                     table_columns=table_columns_resout,
                                     tabs_on='category',
                                     discoverer_mode=discoverer_mode)

    elif view_mode == 'view_unspecified_table_resouts' \
            or view_mode == 'view_unspecified_table_everything_except_ids':
        personroot_node = rcg.get_personroot_node(node=node)
        neighbor_nodes = rcg.get_all_neighbor_nodes(node=personroot_node,
                                                    name_want=name_list,
                                                    category_want=category_list)
        if view_mode == 'view_unspecified_table_resouts':
            table_header = 'These are the research outputs related to this person:'
        else:
            table_header = 'These are all the neighbors related to this person (without its identities):'
        html += node_found
        if discoverer_mode == 'details_view':
            html += get_faceted_table(parent_node=node,
                                      neighbor_nodes=neighbor_nodes,
                                      table_header=table_header,
                                      table_columns=table_columns_resout,
                                      view_mode=view_mode,
                                      discoverer_mode=discoverer_mode)
        else:
            html += get_tabbed_table(nodes_list=neighbor_nodes,
                                     table_header=table_header,
                                     table_columns=table_columns_resout,
                                     tabs_on='category',
                                     discoverer_mode=discoverer_mode)

    elif view_mode == 'view_unspecified_table_everything':
        personroot_node = rcg.get_personroot_node(node=node)
        html += node_found
        neighbor_nodes_personal = rcg.get_all_neighbor_nodes(node=personroot_node,
                                                             category_want=personal_types_all)
        neighbor_nodes_remainder = rcg.get_all_neighbor_nodes(node=personroot_node,
                                                              name_want=name_list,
                                                              category_want=category_list)
        if discoverer_mode == 'details_view':
            html += get_regular_table(nodes_list=neighbor_nodes_personal,
                                      table_header='This is personal information related to this person:',
                                      table_columns=table_columns_ids,
                                      discoverer_mode=discoverer_mode)
            html += get_faceted_table(parent_node=node,
                                      neighbor_nodes=neighbor_nodes_remainder,
                                      table_header='This is other information related to this person:',
                                      table_columns=table_columns_resout,
                                      view_mode=view_mode,
                                      discoverer_mode=discoverer_mode)
        else:
            html += view_personal_information(nodes_list=neighbor_nodes_personal,
                                              discoverer_mode=discoverer_mode)
            html += get_tabbed_table(nodes_list=neighbor_nodes_remainder,
                                     table_header='This is other information related to this person:',
                                     table_columns=table_columns_resout,
                                     tabs_on='category',
                                     discoverer_mode=discoverer_mode)

    elif view_mode == 'view_regular_table_person_share_resouts':
        personroot_node = rcg.get_personroot_node(node=node)
        neighbor_nodes = rcg.get_all_neighbor_nodes(node=personroot_node,
                                                    category_want=category_list,
                                                    category_dontwant=['person', 'competence', 'organization'])
        html += find_person_share_resouts(parent_node=node,
                                          neighbor_nodes=neighbor_nodes,
                                          category_str=category_list_str,
                                          discoverer_mode=discoverer_mode)

    elif view_mode == 'view_regular_table_person_enrich_source_system':
        # Note: we misuse the field 'category_list' to pass the name of the source system
        # we would like to enrich.
        if len(category_list) == 0:
            source_system = ''
        else:
            source_system = str(category_list[0])
        html += find_enrich_candidates(parent_node=node,
                                       source_system=source_system,
                                       discoverer_mode=discoverer_mode)

    elif view_mode == 'view_regular_table_organization_addinfo':
        # Note the hard limit.
        html += find_organization_additional_info(parent_node=node,
                                                  name_list=name_list,
                                                  category_list=category_list,
                                                  max_nr_neighbor_nodes=MAX_ROWS_IN_TABLE,
                                                  discoverer_mode=discoverer_mode)
    elif view_mode == 'view_regular_table_overlap':
        html += find_overlap_in_source_systems(name=node['name'],
                                               category=node['category'],
                                               value=node['value'],
                                               discoverer_mode=discoverer_mode,
                                               overlap_mode='neighbornodes')

    # Note: view_mode == 'view_regular_table_overlap_records' is caught in resultspage().

    else:
        html += get_message(message='create_results_page(): Unknown view_mode "' + view_mode + '".')
    return html


def view_personal_information(nodes_list: Union[list, NodeMatch],
                              discoverer_mode: str = '') -> str:
    """Create a person page of the node.
    This page shows the name variants, a photo (if present),
    and a list of competences (if present). Then a table with the other identities.
    'discover_mode' will always be 'person_view', but we still pass it for future
    extensions.

    :param nodes_list: the nodes to create a table from.
    :param discoverer_mode: the discoverer_mode to use.
    :return: html to be rendered.
    """
    if len(nodes_list) == 0:
        return get_message('No neighbors found.')

    html = get_html_for_cardstart()
    names = []
    for node in nodes_list:
        if node['name'] != 'FULL_NAME':
            continue
        key = rcg.create_ricgraph_key(name=node['name'], value=node['value'])
        item = '<a href=' + url_for('optionspage') + '?'
        item += urllib.parse.urlencode({'key': key,
                                        'discoverer_mode': discoverer_mode}) + '>'
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
                                        'discoverer_mode': discoverer_mode}) + '>'
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
                                        'discoverer_mode': discoverer_mode}) + '>'
        item += node['value'] + '</a>'
        if node['name'] == 'SKILL':
            skills.append(item)
        if node['name'] == 'RESEARCH_AREA':
            research_areas.append(item)
        if node['name'] == 'EXPERTISE_AREA':
            expertise_areas.append(item)
        continue
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
                             discoverer_mode=discoverer_mode)
    return html


def find_enrich_candidates(parent_node: Union[Node, None],
                           source_system: str,
                           discoverer_mode: str = '') -> str:
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
    :return: html to be rendered.
    """
    html = ''
    if parent_node is None:
        personroot_list = rcg.read_all_nodes(name='person-root')
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
        personroot_node = rcg.get_personroot_node(parent_node)
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
        node_in_source_system = []
        node_not_in_source_system = []
        neighbors = rcg.get_all_neighbor_nodes(node=personroot)
        for neighbor in neighbors:
            if source_system in neighbor['_source']:
                node_in_source_system.append(neighbor)
                continue
            if source_system not in neighbor['_source']:
                node_not_in_source_system.append(neighbor)
                continue
        if len(node_in_source_system) == 0:
            # Node is not harvested from 'source_system'.
            continue
        if len(node_not_in_source_system) == 0:
            # All neighbors are only from 'source_system', nothing to report.
            continue

        # Now we are left with a node that _is_ in 'source_system'.
        something_found = True
        count += 1
        html += get_html_for_cardstart()
        table_header = 'This node is used to determine possible enrichments of source system "'
        table_header += source_system + '":'
        html += get_regular_table(nodes_list=[personroot],
                                  table_header=table_header,
                                  table_columns=table_columns)

        person_nodes = []
        for node_source in node_in_source_system:
            if node_source['category'] == 'person':
                person_nodes.append(node_source)
        if len(person_nodes) == 0:
            html += 'find_enrich_candidates(): there are enrich candidates '
            html += 'to enrich source system "' + source_system
            html += '", but there are no <em>person</em> nodes to identify this node in "'
            html += source_system + '".'
        else:
            table_header = 'You can use the information in this table to find this node in source system "'
            table_header += source_system + '":'
            html += get_regular_table(nodes_list=person_nodes,
                                      table_header=table_header,
                                      table_columns=table_columns)

        table_header = 'You could enrich source system "' + source_system + '" '
        table_header += 'by using this information harvested from other source systems. '
        table_header += 'This information is not in source system "' + source_system + '".'
        html += get_regular_table(nodes_list=node_not_in_source_system,
                                  table_header=table_header,
                                  table_columns=table_columns)
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
            table_header = 'This node is used to determine possible enrichments of source system "'
            table_header += source_system + '":'
            html += get_regular_table(nodes_list=[personroot_node],
                                      table_header=table_header,
                                      table_columns=table_columns)
            html += '</br>Ricgraph could not find any information in other source systems '
            html += 'to enrich source system "' + source_system + '".'
            html += get_html_for_cardend()

    html += '</p>'

    return html


def find_person_share_resouts(parent_node: Node,
                              neighbor_nodes: Union[list, NodeMatch],
                              category_str: str = '',
                              discoverer_mode: str = '') -> str:
    """Function that finds with whom a person shares research outputs.

    :param parent_node: the starting node for finding shared research output types.
    :param neighbor_nodes: the neighbors of that node.
    :param category_str: the category of research outputs, or '' if any category.
      Note that this value is only used to display the category used, not to select
      nodes, that has already been done in create_results_page().
    :param discoverer_mode: as usual.
    :return: html to be rendered.
    """
    html = ''
    if parent_node['category'] != 'person':
        message = 'Unexpected result in find_person_share_resouts(): '
        message += 'You have not passed an "person" node, but a "' + parent_node['category']
        message += '" node.'
        return get_message(message=message)

    if len(neighbor_nodes) == 0:
        # Nothing found
        if category_str == '':
            message = 'This person does not share any research output types '
            message += 'with other persons.'
        else:
            message = 'This person does not share research output type "'
            message += category_str + '" with other persons.'
        return get_message(message=message)

    # Now for all relevant_results found, find the connecting 'person-root' node
    connected_persons = []
    for node in neighbor_nodes:
        persons = rcg.get_all_neighbor_nodes(node=node, name_want='person-root')
        for person in persons:
            if person['_key'] == parent_node['_key']:
                # Note: we do not include ourselves.
                continue
            if person not in connected_persons:
                connected_persons.append(person)

    if discoverer_mode == 'details_view':
        table_columns = DETAIL_COLUMNS
    else:
        table_columns = RESEARCH_OUTPUT_COLUMNS

    table_header = 'This is the person we start with:'
    html += get_regular_table(nodes_list=[parent_node],
                              table_header=table_header,
                              table_columns=table_columns,
                              discoverer_mode=discoverer_mode)
    if category_str == '':
        table_header = 'This person shares research output types '
    else:
        table_header = 'This person shares research output type "' + category_str + '" '
    table_header += 'with these persons:'
    html += get_regular_table(nodes_list=connected_persons,
                              table_header=table_header,
                              table_columns=table_columns,
                              discoverer_mode=discoverer_mode)
    return html


def find_organization_additional_info(parent_node: Node,
                                      name_list: list = None,
                                      category_list: list = None,
                                      max_nr_neighbor_nodes: int = 0,
                                      discoverer_mode: str = '') -> str:
    """Function that finds additional information connected to a (child) organization.

    :param parent_node: the starting node for finding additional information.
    :param name_list: the name list used for selection.
    :param category_list: the category list used for selection.
    :param max_nr_neighbor_nodes: return at most this number of nodes, 0 = all nodes.
    :param discoverer_mode: as usual.
    :return: html to be rendered.
    """
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

    # ### Start.
    # I use a Cypher query instead of the much slower code commented below.
    # See 'Explanation why sometimes Cypher query are used.' at the start of this file.
    #
    # edges = rcg.get_edges(parent_node)
    # if len(edges) == 0:
    #     message = 'Unexpected result in find_organization_additional_info(): '
    #     message += 'parent_node does not have neighbors.'
    #     return get_message(message=message)
    #
    # # Use a set, since it does not have duplicates.
    # neighbor_nodes_set = set()
    # count = 0
    # all_nodes = rcg.A_LARGE_NUMBER
    # if max_nr_neighbor_nodes == 0:
    #     max_nr_neighbor_nodes = all_nodes
    # for edge in edges:
    #     if count >= max_nr_neighbor_nodes:
    #         break
    #     next_node = edge.end_node
    #     if parent_node == next_node:
    #         continue
    #     if next_node['name'] != 'person-root':
    #         continue
    #     more_neighbors = rcg.get_all_neighbor_nodes(node=next_node,
    #                                                 name_want=name_list,
    #                                                 category_want=category_list,
    #                                                 max_nr_neighbor_nodes=max_nr_neighbor_nodes - count)
    #     neighbor_nodes_set.update(set(more_neighbors))
    #     count = len(neighbor_nodes_set)
    # relevant_result = list(neighbor_nodes_set)
    # ### End.

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
    cypher_query = 'MATCH (node)-[]->(neighbor) WHERE node._key = '
    cypher_query += '"' + parent_node['_key'] + '"' + ' AND neighbor.name = "person-root" '
    cypher_query += 'MATCH (neighbor)-[]->(second_neighbor) '
    if len(name_list) > 0 or len(category_list) > 0:
        cypher_query += 'WHERE '
    if len(name_list) > 0:
        cypher_query += 'second_neighbor.name IN ' + second_neighbor_name_list + ' '
    if len(name_list) > 0 and len(category_list) > 0:
        cypher_query += 'AND '
    if len(category_list) > 0:
        cypher_query += 'second_neighbor.category IN ' + second_neighbor_category_list + ' '
    cypher_query += 'RETURN DISTINCT second_neighbor '
    if max_nr_neighbor_nodes > 0:
        cypher_query += 'LIMIT ' + str(max_nr_neighbor_nodes)
    print(cypher_query)
    relevant_result = graph.run(cypher_query).to_series().to_list()

    if len(relevant_result) == 0:
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

    if discoverer_mode == 'details_view':
        table_columns = DETAIL_COLUMNS
    else:
        table_columns = RESEARCH_OUTPUT_COLUMNS

    html = ''
    table_header = 'This node is used for finding information about the persons '
    table_header += 'or their results of this organization:'
    html += get_regular_table(nodes_list=[parent_node],
                              table_header=table_header,
                              table_columns=table_columns,
                              discoverer_mode=discoverer_mode)
    table_header = 'These are all the '
    if name_str != '' and category_str != '':
        table_header += '"' + name_str + '" and "' + category_str + '" '
    elif name_str != '':
        table_header += '"' + name_str + '" '
    elif category_str != '':
        table_header += '"' + category_str + '" '
    else:
        table_header += 'shared '
    table_header += 'nodes of this organization:'
    html += get_regular_table(nodes_list=relevant_result,
                              table_header=table_header,
                              table_columns=table_columns,
                              discoverer_mode=discoverer_mode)
    return html


def find_overlap_in_source_systems(name: str = '', category: str = '', value: str = '',
                                   discoverer_mode: str = '',
                                   overlap_mode: str = 'neighbornodes') -> str:
    """Get the overlap in records from source systems.
    We do need a 'name', 'category' and/or 'value', otherwise we won't be able
    to find overlap in source systems for a list of records. That list can only be
    found using these fields, and then these fields can be passed to
    find_overlap_in_source_systems_records() to show the overlap nodes in a table.
    If we want to find overlap of only one node, these fields will result in only one record
    to be found, and the overlap will be computed of the neighbors of that node.
    This function is tightly connected to find_overlap_in_source_systems_records().

    :param name: name of the node(s) to find.
    :param category: category of the node(s) to find.
    :param value: value of the node(s) to find.
    :param discoverer_mode: the discoverer_mode to use.
    :param overlap_mode: which overlap to compute: from this node ('thisnode')
    or from the neighbors of this node ('neighbornodes').
    :return: html to be rendered.
    """
    html = ''
    nodes = rcg.read_all_nodes(name=name, category=category, value=value)
    if len(nodes) == 0:
        # Let's try again, assuming we did a broad search instead of an exact match search.
        nodes = rcg.read_all_nodes_containing_value(value=value)
        if len(nodes) == 0:
            return get_message(message='Ricgraph Explorer could not find anything.')

    if overlap_mode == 'neighbornodes':
        # In this case, we would like to know the overlap of nodes neighboring the node
        # we have just found. We can only do that if we have found only one node.
        if len(nodes) > 1:
            message = 'Ricgraph Explorer found too many nodes. It cannot compute the overlap '
            message += 'of the neighbor nodes of more than one node in get_overlap_in_source_systems().'
            return get_message(message=message)

        parent_node = nodes.first()
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
    html += '<h3>Number of records in source systems</h3>'
    html += 'This table shows the number of records found in only one source or '
    html += 'found in multiple sources for your query. '
    html += 'You can click on a number to retrieve these records.'
    html += get_html_for_tablestart()
    html += '<tr class="uu-yellow">'
    html += '<th class="sorttable_nosort">Source systems</th>'
    html += '<th class="sorttable_nosort">Total records in source systems: '
    html += str(nr_total_recs)
    html += '</th>'
    html += '<th class="sorttable_nosort">Total records found in only one source: '
    html += str(nr_recs_from_one_source)
    html += ' (' + str(round(100 * nr_recs_from_one_source/nr_total_recs))
    html += '% of total ' + str(nr_total_recs) + ' records)'
    html += '</th>'
    html += '<th class="sorttable_nosort">Total records found in multiple sources: '
    html += str(nr_recs_from_multiple_sources)
    html += ' (' + str(round(100 * nr_recs_from_multiple_sources/nr_total_recs))
    html += '% of total ' + str(nr_total_recs) + ' records)'
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
                                            'overlap_mode': overlap_mode})
            html += '">'
            html += str(recs_from_one_source[system])
            html += '</a>'
            html += ' (' + str(round(100 * recs_from_one_source[system]/nr_recs_from_one_source))
            html += '% of ' + str(nr_recs_from_one_source) + ' records are only in ' + system + ')'
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
                                            'overlap_mode': overlap_mode})
            html += '">'
            html += str(recs_from_multiple_sources[system])
            html += '</a>'
            html += ' (' + str(round(100 * recs_from_multiple_sources[system]/nr_recs_from_multiple_sources))
            html += '% of ' + str(nr_recs_from_multiple_sources) + ' records are in multiple sources)'
            html += '</td>'
        else:
            html += '<td>0</td>'
    html += '</tr>'
    html += get_html_for_tableend()
    html += 'Note that the numbers in the columns "Total records in source systems" '
    html += 'and "Total records found in multiple sources" do not need '
    html += 'to count up to resp. '
    html += 'the total number of records ('
    html += str(nr_total_recs)
    html += ') and the total number of records from multiple sources ('
    html += str(nr_recs_from_multiple_sources)
    html += ') since a record in that column will originate from multiple sources, and subsequently will occur '
    html += 'in in multiple rows of that column.'

    if nr_recs_from_multiple_sources == 0:
        html += get_html_for_cardend()
        return html

    html += '<br/>'
    html += '<br/>'
    html += '<h3>Overlap in records from multiple sources</h3>'
    html += 'For the records found for your query in multiple sources, this table shows in which sources '
    html += 'they were found. '
    html += 'You can click on a number to retrieve these records. '
    html += 'The second column in this table corresponds to the last column in '
    html += 'the previous table.'

    html += get_html_for_tablestart()
    html_header2 = '<tr class="uu-yellow">'
    html_header2 += '<th class="sorttable_nosort">A record from \u25be...</th>'
    html_header2 += '<th class="sorttable_nosort">Total records found in multiple sources</th>'
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
                                            'overlap_mode': overlap_mode})
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
                                                'overlap_mode': overlap_mode})
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
    html += 'Note that the number of records in a row in column 3, 4, etc. do not need '
    html += 'to count up to the total number of records from that source (in the second column), '
    html += 'since a record in this table will originate from at least two sources, '
    html += 'and subsequently will occur multiple times on the same row.'
    html += get_html_for_cardend()

    return html


def find_overlap_in_source_systems_records(name: str = '', category: str = '', value: str = '',
                                           system1: str = '', system2: str = '',
                                           discoverer_mode: str = '',
                                           overlap_mode: str = '') -> str:
    """Show the overlap records in a html table.
    This function is tightly connected to find_overlap_in_source_systems().
    We do need a 'name', 'category' and/or 'value', otherwise we won't be able
    to find overlap in source systems for a list of records.

    :param name: name of the node(s) to find.
    :param category: category of the node(s) to find.
    :param value: value of the node(s) to find.
    :param system1: source system 1 used to compute the overlap.
    :param system2: source system 2 used to compute the overlap.
    :param discoverer_mode: the discoverer_mode to use.
    :param overlap_mode: which overlap to compute: from this node ('thisnode')
    or from the neighbors of this node ('neighbornodes').
    :return: html to be rendered.
    """
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
        result = rcg.read_all_nodes_containing_value(value=value)
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

        node = result.first()
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
                                          system2=system2)
    else:
        table_columns = RESEARCH_OUTPUT_COLUMNS

    html += get_regular_table(nodes_list=relevant_result,
                              table_header='These records conform to your selection:',
                              table_columns=table_columns,
                              discoverer_mode=discoverer_mode)
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
                      discoverer_mode: str = '') -> str:
    """This function creates a html table containing 'node'.

    :param node: the node to put in the table.
    :param table_header: header for the table.
    :param discoverer_mode: as usual.
    :return: html to be rendered.
    """
    if table_header == '':
        header = 'Ricgraph Explorer found node:'
    else:
        header = table_header

    html = get_regular_table(nodes_list=[node],
                             table_header=header,
                             discoverer_mode=discoverer_mode)
    return html


def create_html_form(destination: str,
                     button_text: str,
                     explanation: str = '',
                     input_fields: dict = '',
                     hidden_fields: dict = '') -> str:
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
    form = explanation
    form += '<form method="get" action="/' + destination + '">'
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
                              category_filter: str = 'None') -> str:
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
    :return: html to be rendered.
    """
    if name_list is None:
        name_list = []
    if category_list is None:
        category_list = []

    html = get_html_for_cardstart()
    html += '<details><summary>Click for information about your search</summary><ul>'
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
    html += '</ul>'
    html += '</details>'
    html += get_html_for_cardend()
    html += get_html_for_cardline()
    return html


# ##############################################################################
# The HTML for the regular, tabbed and faceted tables is generated here.
# ##############################################################################
def get_regular_table(nodes_list: Union[list, NodeMatch],
                      table_header: str = '',
                      table_columns: list = None,
                      discoverer_mode: str = '') -> str:
    """Create a html table for all nodes in the list.

    :param nodes_list: the nodes to create a table from.
    :param table_header: the html to show above the table.
    :param table_columns: a list of columns to show in the table.
    :param discoverer_mode: the discoverer_mode to use.
    :return: html to be rendered.
    """
    if table_columns is None:
        if discoverer_mode == 'details_view':
            table_columns = DETAIL_COLUMNS
        else:
            table_columns = RESEARCH_OUTPUT_COLUMNS
    if len(nodes_list) == 0:
        return get_message(table_header + '</br>Nothing found.')

    html = get_html_for_cardstart()
    html += '<span style="float:left;">' + table_header + '</span>'
    if len(nodes_list) > MAX_ROWS_IN_TABLE:
        html += '<span style="float:right;">There are ' + str(len(nodes_list)) + ' rows in this table, showing first '
        html += str(MAX_ROWS_IN_TABLE) + '.</span>'
    elif len(nodes_list) == MAX_ROWS_IN_TABLE:
        # Special case: we have truncated the number of search results somewhere out of efficiency reasons,
        # so we have no idea how many search results there are.
        html += '<span style="float:right;">Showing first ' + str(MAX_ROWS_IN_TABLE) + ' rows.</span>'
    elif len(nodes_list) >= 2:
        html += '<span style="float:right;">There are ' + str(len(nodes_list)) + ' rows in this table.</span>'
    html += get_html_for_tablestart()
    html += get_html_for_tableheader(table_columns=table_columns)
    count = 0
    for node in nodes_list:
        count += 1
        if count > MAX_ROWS_IN_TABLE:
            break
        html += get_html_for_tablerow(node=node,
                                      table_columns=table_columns,
                                      discoverer_mode=discoverer_mode)
        # Add node to nodes_cache if it is not there already.
        key = node['_key']
        if key not in nodes_cache:
            nodes_cache[key] = node

    html += get_html_for_tableend()
    html += get_html_for_cardend()
    return html


def get_faceted_table(parent_node: Node,
                      neighbor_nodes: Union[list, NodeMatch, None],
                      table_header: str = '',
                      table_columns: list = None,
                      view_mode: str = '',
                      discoverer_mode: str = '') -> str:
    """Create a faceted html table for all neighbor_nodes in the list.

    :param parent_node: the parent of the nodes to construct the facets from.
    :param neighbor_nodes: the neighbor_nodes to create a table from.
    :param table_header: the html to show above the table.
    :param table_columns: a list of columns to show in the table.
    :param view_mode: which view to use.
    :param discoverer_mode: the discoverer_mode to use.
    :return: html to be rendered.
    """
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
                                         discoverer_mode=discoverer_mode)
    table_html = get_regular_table(nodes_list=neighbor_nodes,
                                   table_header=table_header,
                                   table_columns=table_columns,
                                   discoverer_mode=discoverer_mode)
    html = ''
    if faceted_html == '':
        # Faceted navigation not useful, don't show the panel.
        html += table_html
    else:
        # Divide space between facet panel and table.
        html += '<div class="w3-row-padding w3-stretch" >'
        html += '<div class="w3-col" style="width:20em" >'
        html += faceted_html
        html += '</div>'
        html += '<div class="w3-rest" >'
        html += table_html
        html += '</div>'
        html += '</div>'

    return html


def get_tabbed_table(nodes_list: Union[list, NodeMatch, None],
                     table_header: str = '',
                     table_columns: list = None,
                     tabs_on: str = '',
                     discoverer_mode: str = '') -> str:
    """Create a html table with tabs for all nodes in the list.

    :param nodes_list: the nodes to create a table from.
    :param table_header: the html to show above the table.
    :param table_columns: a list of columns to show in the table.
    :param tabs_on: the name of the field in Ricgraph you'd like to have tabs on.
    :param discoverer_mode: the discoverer_mode to use.
    :return: html to be rendered.
    """
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

    histogram_sort = sorted(histogram, key=histogram.get, reverse=True)

    first_iteration = True
    tab_names_html = '<div class="w3-bar uu-yellow">'
    for tab_name in histogram_sort:
        tab_text = tab_name + '&nbsp;<i>(' + str(histogram[tab_name]) + ')</i>'
        tab_names_html += '<button class="w3-bar-item w3-button tablink'
        if first_iteration:
            tab_names_html += ' uu-orange'
            first_iteration = False
        else:
            tab_names_html += ''
        tab_names_html += '" onclick="openTab(event,\'' + tab_name + '\')">' + tab_text + '</button>'
    tab_names_html += '</div>'

    first_iteration = True
    tab_contents_html = ''
    for tab_name in histogram_sort:
        tab_contents_html += '<div id="' + tab_name + '" class="w3-container w3-border tabitem"'
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
                                  discoverer_mode=discoverer_mode)
        tab_contents_html += table
        tab_contents_html += '</div>'

    # This code is from https://www.w3schools.com/w3css/w3css_tabulators.asp.
    tab_javascript = """<script>
                        function openTab(evt, tabName) {
                          var i, x, tablinks;
                          x = document.getElementsByClassName("tabitem");
                          for (i = 0; i < x.length; i++) {
                            x[i].style.display = "none";
                          }
                          tablinks = document.getElementsByClassName("tablink");
                          for (i = 0; i < x.length; i++) {
                            tablinks[i].className = tablinks[i].className.replace(" uu-orange", "");
                          }
                          document.getElementById(tabName).style.display = "block";
                          evt.currentTarget.className += " uu-orange";
                        }
                        </script>"""

    html = get_html_for_cardstart()
    html += table_header
    html += tab_names_html + tab_contents_html + tab_javascript
    html += get_html_for_cardend()

    return html


def get_facets_from_nodes(parent_node: Node,
                          neighbor_nodes: list,
                          view_mode: str = '',
                          discoverer_mode: str = '') -> str:
    """Do facet navigation in Ricgraph.
    The facets will be constructed based on 'name' and 'category'.
    Facets chosen will be "caught" in function search().
    If there is only one facet (for either one or both), it will not be shown.

    :param parent_node: the parent of the nodes to construct the facets from.
    :param neighbor_nodes: the nodes to construct the facets from.
    :param view_mode: which view to use.
    :param discoverer_mode: the discoverer_mode to use.
    :return: html to be rendered, or empty string ('') if faceted navigation is
      not useful because there is only one facet.
    """
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

    faceted_form = get_html_for_cardstart()
    faceted_form += '<div class="facetedform">'
    faceted_form += '<form method="get" action="' + url_for('resultspage') + '">'
    faceted_form += '<input type="hidden" name="key" value="' + str(parent_node['_key']) + '">'
    faceted_form += '<input type="hidden" name="view_mode" value="' + str(view_mode) + '">'
    faceted_form += '<input type="hidden" name="discoverer_mode" value="' + str(discoverer_mode) + '">'
    if len(name_histogram) == 1:
        # Get the first (and only) element in the dict, pass it as hidden field to search().
        name_key = str(list(name_histogram.keys())[0])
        faceted_form += '<input type="hidden" name="name_list" value="' + name_key + '">'
    else:
        faceted_form += '<div class="w3-card-4">'
        faceted_form += '<div class="w3-container uu-yellow">'
        faceted_form += '<b>Filter on "name"</b>'
        faceted_form += '</div>'
        faceted_form += '<div class="w3-container">'
        # Sort a dict on value:
        # https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
        for bucket in sorted(name_histogram, key=name_histogram.get, reverse=True):
            name_label = bucket + '&nbsp;<i>(' + str(name_histogram[bucket]) + ')</i>'
            faceted_form += '<input class="w3-check" type="checkbox" name="name_list" value="'
            faceted_form += bucket + '" checked>'
            faceted_form += '<label>&nbsp;' + name_label + '</label><br/>'
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
        faceted_form += '<div class="w3-container">'
        for bucket in sorted(category_histogram, key=category_histogram.get, reverse=True):
            category_label = bucket + '&nbsp;<i>(' + str(category_histogram[bucket]) + ')</i>'
            faceted_form += '<input class="w3-check" type="checkbox" name="category_list" value="'
            faceted_form += bucket + '" checked>'
            faceted_form += '<label>&nbsp;' + category_label + '</label><br/>'
        faceted_form += '</div>'
        faceted_form += '</div><br/>'

    # Send name, category and value as hidden fields to search().
    faceted_form += '<input class="w3-input' + button_style + '" style="width:8em;" type=submit value="refresh">'
    faceted_form += '</form>'
    faceted_form += '</div>'
    faceted_form += get_html_for_cardend()
    html = faceted_form
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
                          table_columns: list = None,
                          discoverer_mode: str = '') -> str:
    """Get the html required for a row of a html table.

    :param node: the node to show in the table.
    :param table_columns: a list of columns to show in the table.
    :param discoverer_mode: the discoverer_mode to use.
    :return: html to be rendered.
    """
    if table_columns is None:
        table_columns = []
    html = '<tr class="item">'
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
                                        'discoverer_mode': discoverer_mode}) + '>'
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


# ############################################
# ################### main ###################
# ############################################
if __name__ == "__main__":
    graph = rcg.open_ricgraph()         # Should probably be done in a Session
    if graph is None:
        print('Ricgraph could not be opened.')
        exit(2)

    name_all = rcg.read_all_values_of_property('name')
    if name_all is None:
        print('Error in obtaining list with all property values for property "name".')
        exit(2)
    category_all = rcg.read_all_values_of_property('category')
    if category_all is None:
        print('Error in obtaining list with all property values for property "category".')
        exit(2)
    source_all = rcg.read_all_values_of_property('_source')
    if source_all is None:
        print('Error in obtaining list with all property values for property "_source".')
        exit(2)

    name_all_datalist = '<datalist id="name_all_datalist">'
    for property_item in name_all:
        name_all_datalist += '<option value="' + property_item + '">'
    name_all_datalist += '</datalist>'

    resout_types_all = []
    if 'competence' in category_all:
        personal_types_all = ['person', 'competence']
    else:
        personal_types_all = ['person']
    remainder_types_all = []
    resout_types_all_datalist = '<datalist id="resout_types_all_datalist">'
    category_all_datalist = '<datalist id="category_all_datalist">'
    for property_item in category_all:
        if property_item in rcg.ROTYPE_ALL:
            resout_types_all.append(property_item)
            resout_types_all_datalist += '<option value="' + property_item + '">'
        if property_item not in personal_types_all:
            remainder_types_all.append(property_item)
        category_all_datalist += '<option value="' + property_item + '">'
    category_all_datalist += '</datalist>'
    resout_types_all_datalist += '</datalist>'

    source_all_datalist = '<datalist id="source_all_datalist">'
    for property_item in source_all:
        source_all_datalist += '<option value="' + property_item + '">'
    source_all_datalist += '</datalist>'

    # For normal use:
    ricgraph_explorer.run(port=3030)

    # For debug purposes:
    # ricgraph_explorer.run(debug=True, port=3030)

    # If you uncomment the next line, Ricgraph Explorer will be exposed to
    # the outside world. Read the remarks at the top of this file before you do so.
    # Also, comment out the line above.
    # ricgraph_explorer.run(host='0.0.0.0', debug=True, port=3030)
