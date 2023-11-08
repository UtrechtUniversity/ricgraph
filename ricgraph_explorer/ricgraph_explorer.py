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
# This file is Ricgraph explorer, a web based tool to access nodes in
# Ricgraph.
# The purpose is to illustrate how web based access using Flask can be done.
# To keep it simple, everything has been done in this file.
#
# Please note that this code is meant for research purposes,
# not for production use. That means, this code has not been hardened for
# "the outside world". Be careful if you expose it to the outside world.
#
# Original version Rik D.T. Janssen, January 2023.
# Extended Rik D.T. Janssen, February, September to November 2023.
#
# ########################################################################
#
# For table sorting. Ricgraph explorer uses sorttable.js.
# It is copied from https://www.kryogenix.org/code/browser/sorttable
# on February 1, 2023. At that link, you'll find a how-to. It is licensed under X11-MIT.
# It is renamed to ricgraph_sorttable.js since it has a small modification
# related to case-insensitive sorting. The script is included in html_body_end.
#
# ##############################################################################
#
# Ricgraph explorer uses W3.CSS, a modern, responsive, mobile first CSS framework.
# See https://www.w3schools.com/w3css/default.asp.
#
# ##############################################################################


import urllib.parse
from typing import Union
from py2neo import Node, NodeMatch
from flask import Flask, request, url_for
from markupsafe import escape
import ricgraph as rcg

ricgraph_explorer = Flask(__name__)

# Ricgraph_explorerer is also a "discoverer". This parameter gives the
# default mode. Possibilities are:
# details_view: show all the details.
# person_view: show a person card, limit details (e.g. do not show _history & _source)
DEFAULT_DISCOVERER_MODE = 'person_view'

# You can search in two different ways in Ricgraph explorer. This parameter
# gives the default mode. Possibilities are:
# exact_match: do a search on exact match.
# value_search: do a string search on field 'value'.
DEFAULT_SEARCH_MODE = 'value_search'

# Ricgraph_explorer shows tables. You can specify which columns you need.
# You do this by making a list of one or more fields in a Ricgraph node.
# There are some predefined lists.
DETAIL_COLUMNS = ['name', 'category', 'value', 'comment', 'year',
                  'url_main', 'url_other', '_source', '_history']
RESEARCH_OUTPUT_COLUMNS = ['name', 'category', 'value', 'comment',
                           'year', 'url_main', 'url_other']
ORGANIZATION_COLUMNS = ['name', 'value', 'comment', 'url_main']
ID_COLUMNS = ['name', 'value', 'url_main']

# When we do a query, we return at most this number of nodes.
MAX_RESULTS = 50

# If we render a table, we return at most this number of rows in that table.
MAX_ROWS_IN_TABLE = 250

# It is possible to find enrichments for all nodes in Ricgraph. However, that
# will take a long time. This is the maximum number of nodes Ricgraph explorer
# is going to enrich in find_enrich_candidates().
MAX_NR_NODES_TO_ENRICH = 20

# The style for the buttons, note the space before and after the text.
button_style = ' w3-button uu-yellow w3-round-large w3-mobile '
# A button with a black line around it.
button_style_border = button_style + ' w3-border rj-border-black '

# The html stylesheet.
stylesheet = '<style>'
stylesheet += '.w3-container {padding: 16px;}'
stylesheet += '.w3-check {width:15px;height: 15px;position: relative; top:3px;}'
# Note: #ffcd00 is 'uu-yellow' below.
stylesheet += '.w3-radio {accent-color: #ffcd00;}'
# Define UU colors. We do not need to define "black" and "white" (they do exist).
# See https://www.uu.nl/organisatie/huisstijl/huisstijlelementen/kleur.
stylesheet += '.uu-yellow, .uu-hover-yellow:hover '
stylesheet += '{color: #000!important; background-color: #ffcd00!important;}'
stylesheet += '.uu-red, .uu-hover-red:hover '
stylesheet += '{color: #000!important; background-color: #c00a35!important;}'
stylesheet += '.uu-orange, .uu-hover-orange:hover '
stylesheet += '{color: #000!important; background-color: #f3965e!important;}'
stylesheet += '.uu-blue, .uu-hover-blue:hover '
stylesheet += '{color: #000!important; background-color: #5287c6!important;}'
stylesheet += '.rj-gray, .rj-hover-gray:hover '
stylesheet += '{color: #000!important; background-color: #cecece!important;}'
stylesheet += '.rj-border-black, .rj-hover-border-black:hover {border-color: #000!important;}'
stylesheet += 'body {background-color:white;}'
stylesheet += 'body, h1, h2, h3, h4, h5, h6 {font-family: "Open Sans", sans-serif;}'
stylesheet += 'ul {padding-left:2em; margin:0px}'
stylesheet += 'a:link, a:visited {color: blue;}'
stylesheet += 'a:hover {color: darkblue;}'
stylesheet += 'table {font-size:85%;}'
stylesheet += 'table, th, td {border-collapse:collapse; border: 1px solid black}'
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
page_header += '<div class="w3-bar-item w3-mobile" style="padding-left: 0em; padding-right: 4em">'
page_header += '<a href="/" style="text-decoration:none; color:#000000; font-size:130%">'
page_header += '<img src="/static/uu_logo_small.png" height="30" style="padding-right: 3em">'
page_header += '<img src="/static/ricgraph_logo.png" height="30" style="padding-right: 0.5em">explorer</a>'
page_header += '</div>'
page_header += '<a href="/" class="w3-bar-item' + button_style_border + '">Home</a>'
page_header += '<a href="/searchform?search_mode=exact_match" class="w3-bar-item'
page_header += button_style_border + '">Exact match search</a>'
page_header += '<a href="/searchform?search_mode=value_search" class="w3-bar-item'
page_header += button_style_border + '">String search</a>'
page_header += '</div>'
page_header += '</header>'

# The html page footer.
page_footer = '<footer class="w3-container rj-gray" style="font-size:80%">'
page_footer += 'Disclaimer: Ricgraph explorer is recommended for research use, not for production use. '
page_footer += 'For more information about Ricgraph, see '
page_footer += '<a href=https://github.com/UtrechtUniversity/ricgraph>'
page_footer += 'https://github.com/UtrechtUniversity/ricgraph</a>.'
page_footer += '</footer>'

# The first part of the html page, up to stylesheet and page_header.
html_body_start = '<!DOCTYPE html>'
html_body_start += '<html>'
html_body_start += html_preamble
html_body_start += '<title>Ricgraph explorer</title>'
html_body_start += '<body>'
html_body_start += stylesheet
html_body_start += page_header

# The last part of the html page, from page_footer to script inclusion.
html_body_end = page_footer
html_body_end += '<script src="/static/ricgraph_sorttable.js"></script>'
html_body_end += '</body>'
html_body_end += '</html>'


# ##############################################################################
# Entry functions.
# ##############################################################################
@ricgraph_explorer.route(rule='/')
def index_html() -> str:
    """Ricgraph explorer entry, the index page, when you access '/'.

    :return: html to be rendered.
    """
    global html_body_start, html_body_end

    html = html_body_start
    html += get_html_for_cardstart()
    html += '<h3>This is Ricgraph explorer</h3>'
    html += 'You can use Ricgraph explorer to explore Ricgraph. '

    html += 'There are two methods to start exploring:'
    html += '<ul>'
    html += '<li>find your first node by using exact match;'
    html += '<li>find your first node by using search on a field value.</li>'
    html += '</li>'
    html += '</ul>'
    html += '</p>'
    html += '<br/>'

    html += get_html_for_tablestart()
    html += '<tr class="uu-yellow" style="font-size:120%; text-align:center;">'
    html += '<th class="sorttable_nosort">case-sensitive, exact match search on fields<i>name</i>, '
    html += '<i>category</i> and/or <i>value</i></th>'
    html += '<th class="sorttable_nosort">search on field <i>value</i> containing a string</th>'
    html += '</tr>'
    html += '<tr style="font-size:120%;">'
    html += '<td width=50% style="text-align:center;"><a href=' + url_for('searchform')
    html += '?search_mode=exact_match class="'
    html += button_style + '">choose this one</a></td>'
    html += '<td width=50% style="text-align:center"><a href=' + url_for('searchform')
    html += '?search_mode=value_search class="'
    html += button_style + '">choose this one</a></td>'
    html += '</tr>'
    html += get_html_for_tableend()
    html += '</table>'
    html += '</p>'
    html += '<br/>'

    html += '<h4>Explore persons</h4>'
    html += 'After a search for a peron, you can choose to find out with whom this person '
    html += 'shares research outputs. Also, you can find out how to '
    html += 'improve or enhance information in one of your source systems. This '
    html += 'is called "enriching" your source system, and '
    html += 'means that information found in one or more other harvested systems, '
    html += 'is used to improve or enhance information in the first source system. '
    html += 'The options to do this will appear automatically after a search for '
    html += 'a person.'

    html += '<h4>Explore (child) organizations</h4>'
    html += 'After a search for a (child) organization, you can choose what you '
    html += 'would like to see about the persons or their results in this (child) organization. '
    html += 'For instance, if you have harvested a source system containing '
    html += 'chairs, units, departments, faculties, etc., you can find out to what '
    html += 'research outputs the persons in that organization have contributed, '
    html += 'or what skills the persons in that organization have (but only '
    html += 'if you have harvested skills). '
    html += 'The option to do this will appear automatically after a search for '
    html += 'a (child) organization.'

    html += '<h4>Explore the overlap in source systems</h4>'
    html += 'If you have harvested more than one source system, you can choose '
    html += 'to find the overlap in these source systems, based on a node '
    html += 'you have searched for. '
    html += 'You will get two tables, one showing the number of records found in only '
    html += 'one source and the number of records found in multiple sources. '
    html += 'The other table shows the number of records found in multiple sources, '
    html += 'and in which source they were found. '
    html += 'The option to do this will appear automatically after a search for a node.'

    html += get_html_for_cardend()
    html += html_body_end
    return html


@ricgraph_explorer.route(rule='/searchform/', methods=['GET'])
def searchform() -> str:
    """Ricgraph explorer entry, this 'page' shows the search form, both the
    exact match search form and the string search on the 'value' field form.

    Possible parameters are:
    - discoverer_mode: the discoverer_mode to use, 'details_view' to see all details,
      or 'person_view' to have a nicer layout.
    - search_mode: the search_mode to use, 'exact_match' or 'value_search' (string
      search on field 'value').

    returns html to parse.
    """
    global html_body_start, html_body_end

    graph = rcg.open_ricgraph()         # Should probably be done in a Session
    if graph is None:
        return 'Ricgraph could not be opened.'

    search_mode = get_url_parameter_value(parameter='search_mode',
                                          allowed_values=['exact_match', 'value_search'],
                                          default_value=DEFAULT_SEARCH_MODE)
    discoverer_mode = get_url_parameter_value(parameter='discoverer_mode',
                                              allowed_values=['details_view', 'person_view'],
                                              default_value=DEFAULT_DISCOVERER_MODE)
    html = html_body_start
    html += get_html_for_cardstart()

    html += '<h3>Type something to search</h3>'
    if search_mode == 'value_search':
        html += 'This is a case-insensitive, inexact match:'
    else:
        html += 'This is an case-sensitive, exact match search, using AND if you use multiple fields:'

    form = '<form method="get" action="/findnodes">'
    if search_mode == 'exact_match':
        form += '<label>Search for a value in Ricgraph field <em>name</em>:</label>'
        form += '<input class="w3-input w3-border" type=text name=name>'
        form += '<br/><label>Search for a value in Ricgraph field <em>category</em>:</label>'
        form += '<input class="w3-input w3-border" type=text name=category>'
    form += '<br/><label>Search for a value in Ricgraph field <em>value</em>:</label>'
    form += '<input class="w3-input w3-border" type=text name=value>'
    form += '<input type="hidden" name="search_mode" value=' + search_mode + '>'

    radio_person_text = ' <em>person_view</em>: only show relevant columns, '
    radio_person_text += 'research outputs presented in a <em>tabbed</em> format'
    radio_details_text = ' <em>details_view</em>: show all columns, '
    radio_details_text += 'research outputs presented in a table with <em>facets</em>'

    form += '</br>Please specify how you like to view your results (for explanation see below):</br>'
    form += '<input class="w3-radio" type="radio" name="discoverer_mode" value="person_view"'
    if discoverer_mode == DEFAULT_DISCOVERER_MODE:
        form += 'checked'
    form += '>'
    form += '<label>' + radio_person_text + '</label></br>'
    form += '<input class="w3-radio" type="radio" name="discoverer_mode" value="details_view"'
    if discoverer_mode != DEFAULT_DISCOVERER_MODE:
        form += 'checked'
    form += '>'
    form += '<label>' + radio_details_text + '</label></br>'

    form += '<br/><input class="w3-input' + button_style + '" type=submit value=search>'
    form += '</form>'
    html += form

    html += get_html_for_cardend()
    html += get_html_for_cardstart()
    html += '<h4>Explanation of the modes for viewing the results</h4>'
    html += 'The two modes for viewing the results (the <em>discoverer_mode</em>) are:'
    html += '<ul>'
    html += '<li><em>person_view</em>: '
    html += 'only relevant columns are shown. '
    html += 'Research outputs are presented in a <em>tabbed</em> format. '
    html += 'Tables have less columns (to reduce information overload) '
    html += 'and the order of the tables is different compared to the other <em>discoverer_mode</em>. '
    html += '<br/>This view has been tailored to the Utrecht University staff pages, since some of these '
    html += 'pages also include expertise areas, research areas, skills or photos. '
    html += 'If present, these will be presented in a more attractive way. '
    html += 'If the UU staff pages have not been harvested, this view may still be relevant, '
    html += 'because it shows that the layout of information can be adapted to a target audience.'
    html += '</li>'
    html += '<li><em>details_view</em>: all columns in Ricgraph will be shown. '
    html += 'Research outputs are presented in a table with <em>facets</em>. '
    html += '</li>'
    html += '</ul>'
    html += '</p>Technically, these modes are implemented using a parameter "?discoverer_mode=<em>mode</em>" '
    html += 'in the url. You may modify this as you like.'

    html += get_html_for_cardend()
    html += html_body_end
    return html


@ricgraph_explorer.route(rule='/findnodes/', methods=['GET'])
def findnodes() -> str:
    """Ricgraph explorer entry, this 'page' only uses URL parameters.
    Find nodes based on URL parameters passed.

    Possible parameters are:

    - key: key of the nodes to find. If present, this field is preferred above
      'name', 'category' or 'value'.
    - name: name of the nodes to find.
    - category: category of the nodes to find.
    - value: value of the nodes to find.
    - faceted_name: either a string which indicates that we only want neighbor
      nodes where the property 'name' is equal to 'faceted_name'
      (e.g. 'ORCID'), or a list containing several node names, indicating
      that we want all neighbor nodes where the property 'name' equals
      one of the names in the list 'faceted_name' (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty (empty string), return all nodes.
    - faceted_category: similar to 'faceted_name', but now for the property 'category'.
    - discoverer_mode: the discoverer_mode to use, 'details_view' to see all details,
      or 'person_view' to have a nicer layout.
    - search_mode: the search_mode to use, 'exact_match' or 'value_search' (string
      search on field 'value').

    returns html to parse.
    """
    global html_body_start, html_body_end

    key = get_url_parameter_value(parameter='key', use_escape=False)
    if key != '':
        # We prefer the URL parameter 'key' above 'name' & 'value'
        name = rcg.get_namepart_from_ricgraph_key(key=key)
        category = ''
        value = rcg.get_valuepart_from_ricgraph_key(key=key)
    else:
        name = get_url_parameter_value(parameter='name')
        category = get_url_parameter_value(parameter='category')
        value = get_url_parameter_value(parameter='value', use_escape=False)

    search_mode = get_url_parameter_value(parameter='search_mode',
                                          allowed_values=['exact_match', 'value_search'],
                                          default_value=DEFAULT_SEARCH_MODE)
    discoverer_mode = get_url_parameter_value(parameter='discoverer_mode',
                                              allowed_values=['details_view', 'person_view'],
                                              default_value=DEFAULT_DISCOVERER_MODE)
    faceted_name_list = request.args.getlist('faceted_name')
    faceted_category_list = request.args.getlist('faceted_category')

    html = html_body_start

    if name == '' and category == '' and value == '':
        html += get_html_for_cardstart()
        html += 'Ricgraph explorer could not find anything.'
        html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
        html += get_html_for_cardend()
        html += html_body_end
        return html

    if search_mode == 'exact_match':
        result = rcg.read_all_nodes(name=name, category=category, value=value)
    else:
        if len(value) < 3:
            html += get_html_for_cardstart()
            html += 'The search string should be at least three characters.'
            html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
            html += get_html_for_cardend()
            html += html_body_end
            return html
        result = rcg.read_all_nodes_containing(value=value)

    if len(result) == 0:
        # We didn't find anything.
        html += get_html_for_cardstart()
        html += 'Ricgraph explorer could not find anything.'
        html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
        html += get_html_for_cardend()
        html += html_body_end
        return html

    if len(result) > 1:
        columns = ''
        table_header = 'Choose one node to continue, or '
        table_header += '<a href="' + url_for('getoverlap') + '?'
        table_header += urllib.parse.urlencode({'name': name, 'category': category, 'value': value,
                                                'discoverer_mode': discoverer_mode})
        table_header += '">'
        table_header += 'click here to show the overlap in source systems for your query'
        table_header += '</a>:'
        if discoverer_mode == 'details_view':
            columns = DETAIL_COLUMNS
        elif discoverer_mode == 'person_view':
            columns = RESEARCH_OUTPUT_COLUMNS
        html += get_html_table_from_nodes(nodes=result,
                                          table_header=table_header,
                                          table_columns=columns,
                                          discoverer_mode=discoverer_mode)
        html += html_body_end
        return html

    node = result.first()
    # If 'faceted_name_list' and/or 'faceted_category_list' have not been passed as
    # URL parameter(s), they will be '[]'. That means: all names and/or categories.
    # So no additional checks needed.
    html += results_page(node=node,
                         name_want=faceted_name_list,
                         category_want=faceted_category_list,
                         discoverer_mode=discoverer_mode)

    html += html_body_end
    return html


@ricgraph_explorer.route(rule='/filterorganization/', methods=['GET'])
def filterorganization() -> str:
    """Ricgraph explorer entry, this 'page' only uses URL parameters.
    This function filters for persons or their results in a certain organization.
    This URL creates a table with the filter results with the parameters
    provided in the URL.

    Possible parameters are:

    - key: as usual.
    - discoverer_mode: as usual.
    - name_filter: filter persons or research outputs on this name field.
    - category_filter: filter persons or research outputs on this category field.

    :return: html to be rendered.
    """
    global html_body_start, html_body_end

    html = html_body_start

    key = get_url_parameter_value(parameter='key', use_escape=False)
    if key == '':
        html += 'filterorganization(): "key" URL parameter is required.'
        html += html_body_end
        return html
    name = rcg.get_namepart_from_ricgraph_key(key=key)
    value = rcg.get_valuepart_from_ricgraph_key(key=key)
    discoverer_mode = get_url_parameter_value(parameter='discoverer_mode',
                                              allowed_values=['details_view', 'person_view'],
                                              default_value=DEFAULT_DISCOVERER_MODE)
    name_filter = get_url_parameter_value(parameter='name_filter')
    category_filter = get_url_parameter_value(parameter='category_filter')

    result = rcg.read_all_nodes(name=name, value=value)
    if len(result) == 0:
        # Let's try again, assuming we did a string search instead of an exact match search.
        result = rcg.read_all_nodes_containing(value=value)
        if len(result) == 0:
            # No, we really didn't find anything.
            html += get_html_for_cardstart()
            html += 'Unexpected result in filterorganization(): '
            html += 'This organization cannot be found in Ricgraph.'
            html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
            html += get_html_for_cardend()
            html += html_body_end
            return html

    # Now 'result' contains the node(s) on the (previous) screen where you pressed the button to get
    # more info about that node. We get the first one.
    node = result.first()
    if node['category'] != 'organization':
        html += get_html_for_cardstart()
        html += 'Unexpected result in filterorganization(): '
        html += 'You have not passed an "organization" node, but a "' + node['category']
        html += '" node in fiterorganization(). '
        html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
        html += get_html_for_cardend()
        html += html_body_end
        return html

    # Get the neighbors of the 'organization' node.
    relevant_result = []
    neighbors = rcg.get_all_neighbor_nodes(node=node, name_want='person-root')
    for neighbor in neighbors:
        # We include ourselves.
        # For get_all_neighbor_nodes(), for the '_want' parameters: if we pass '',
        # that means we do not want a filter for that parameter.
        more_neighbors = rcg.get_all_neighbor_nodes(node=neighbor,
                                                    name_want=name_filter,
                                                    category_want=category_filter)
        for item in more_neighbors:
            if item not in relevant_result:
                relevant_result.append(item)

    if len(relevant_result) == 0:
        # Nothing found
        html += get_html_for_cardstart()
        html += 'Could not find any persons or results for this organization.'
        html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
        html += get_html_for_cardend()
        html += html_body_end
        return html

    if discoverer_mode == 'details_view':
        table_colums = DETAIL_COLUMNS
        html += get_you_searched_for_card(key=key,
                                          discoverer_mode=discoverer_mode,
                                          name_filter=name_filter,
                                          category_filter=category_filter)
    else:
        table_colums = RESEARCH_OUTPUT_COLUMNS

    table_header = 'This node is used for finding information about the persons '
    table_header += 'or their results of this organization:'
    html += get_html_table_from_nodes(nodes=result,
                                      table_header=table_header,
                                      table_columns=table_colums,
                                      discoverer_mode=discoverer_mode)
    table_header = 'These are all the '
    if name_filter != '' and category_filter != '':
        table_header += '"' + name_filter + '" and "' + category_filter + '" '
    elif name_filter != '':
        table_header += '"' + name_filter + '" '
    elif category_filter != '':
        table_header += '"' + category_filter + '" '
    table_header += 'nodes of all the persons or their results of this organization:'
    html += get_html_table_from_nodes(nodes=relevant_result,
                                      table_header=table_header,
                                      table_columns=table_colums,
                                      discoverer_mode=discoverer_mode)

    html += html_body_end
    return html


@ricgraph_explorer.route(rule='/filterperson/', methods=['GET'])
def filterperson() -> str:
    """Ricgraph explorer entry, this 'page' only uses URL parameters.
    This function filters for persons who are connected to one person,
    sharing a certain research output type.
    This URL creates a table with the filter results with the parameters
    provided in the URL.

    Possible parameters are:

    - key: as usual.
    - discoverer_mode: as usual.
    - category_filter: the type of research output to filter on.

    :return: html to be rendered.
    """
    global html_body_start, html_body_end

    html = html_body_start

    key = get_url_parameter_value(parameter='key', use_escape=False)
    if key == '':
        html += 'filterperson(): "key" URL parameter is required.'
        html += html_body_end
        return html
    name = rcg.get_namepart_from_ricgraph_key(key=key)
    value = rcg.get_valuepart_from_ricgraph_key(key=key)
    discoverer_mode = get_url_parameter_value(parameter='discoverer_mode',
                                              allowed_values=['details_view', 'person_view'],
                                              default_value=DEFAULT_DISCOVERER_MODE)
    category_filter = get_url_parameter_value(parameter='category_filter')

    result = rcg.read_all_nodes(name=name, value=value)
    if len(result) == 0:
        # Let's try again, assuming we did a string search instead of an exact match search.
        result = rcg.read_all_nodes_containing(value=value)
        if len(result) == 0:
            # No, we really didn't find anything.
            html += get_html_for_cardstart()
            html += 'Unexpected result in filterperson(): '
            html += 'This person cannot be found in Ricgraph.'
            html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
            html += get_html_for_cardend()
            html += html_body_end
            return html

    # Now 'result' contains the node(s) on the (previous) screen where you pressed the button to get
    # more info about that node. We get the first one.
    node = result.first()
    if node['category'] != 'person':
        html += get_html_for_cardstart()
        html += 'Unexpected result in filterperson(): '
        html += 'You have not passed an "person" node, but a "' + node['category']
        html += '" node in filterperson().'
        html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
        html += get_html_for_cardend()
        html += html_body_end
        return html
    if node['name'] != 'person-root':
        personroot = rcg.get_personroot_node(node=node)
    else:
        personroot = node

    if category_filter == '':
        neighbors = rcg.get_all_neighbor_nodes(node=personroot,
                                               category_dontwant=['person', 'competence', 'organization'])
    else:
        neighbors = rcg.get_all_neighbor_nodes(node=personroot,
                                               category_want=category_filter,
                                               category_dontwant=['person', 'competence', 'organization'])

    if len(neighbors) == 0:
        # Nothing found
        html += get_html_for_cardstart()
        html += 'This person does not seem to share any research output types '
        html += 'with other persons.'
        html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
        html += get_html_for_cardend()
        html += html_body_end
        return html

    # Now for all relevant_results found, find the connecting 'person-root' node
    connected_persons = []
    for node in neighbors:
        persons = rcg.get_all_neighbor_nodes(node=node, name_want='person-root')
        for person in persons:
            if person['value'] == personroot:
                # Note: we do not include ourselves.
                continue
            if person not in connected_persons:
                connected_persons.append(person)

    if discoverer_mode == 'details_view':
        table_colums = DETAIL_COLUMNS
        html += get_you_searched_for_card(key=key,
                                          discoverer_mode=discoverer_mode,
                                          category_filter=category_filter)
    else:
        table_colums = RESEARCH_OUTPUT_COLUMNS

    table_header = 'This is the person we start with:'
    html += get_html_table_from_nodes(nodes=personroot,
                                      table_header=table_header,
                                      table_columns=table_colums,
                                      discoverer_mode=discoverer_mode)
    if category_filter == '':
        table_header = 'This person shares research output types '
    else:
        table_header = 'This person shares research output type "' + category_filter + '" '
    table_header += 'with these persons:'
    html += get_html_table_from_nodes(nodes=connected_persons,
                                      table_header=table_header,
                                      table_columns=table_colums,
                                      discoverer_mode=discoverer_mode)

    html += html_body_end
    return html


@ricgraph_explorer.route(rule='/getoverlap/', methods=['GET'])
def getoverlap() -> str:
    """Ricgraph explorer entry, this 'page' does not allow data entry.
    The data entry is via the url parameters.
    This url calls get_overlap_in_source_systems() with the parameters
    provided in the url.

    Possible parameters are:

    - name, category, value: as usual.
    - discoverer_mode: which discoverer mode to use:
      only show relevant columns, research outputs
      presented in a tabbed format ('person_view'), or
      show all columns, research outputs presented
      in a table with facets ('details_view').
    - overlap_mode: which overlap to compute: from this node ('thisnode'),
      or from the neighbors of this node ('neighbornodes').

    :return: html to be rendered.
    """
    global html_body_start, html_body_end

    name = get_url_parameter_value(parameter='name')
    category = get_url_parameter_value(parameter='category')
    value = get_url_parameter_value(parameter='value', use_escape=False)
    discoverer_mode = get_url_parameter_value(parameter='discoverer_mode',
                                              allowed_values=['details_view', 'person_view'],
                                              default_value=DEFAULT_DISCOVERER_MODE)
    overlap_mode = get_url_parameter_value(parameter='overlap_mode',
                                           allowed_values=['thisnode', 'neighbornodes'],
                                           default_value='thisnode')

    html = html_body_start

    html += get_overlap_in_source_systems(name=name, category=category, value=value,
                                          discoverer_mode=discoverer_mode,
                                          overlap_mode=overlap_mode)

    html += html_body_end
    return html


@ricgraph_explorer.route(rule='/getoverlaprecords/', methods=['GET'])
def getoverlaprecords() -> str:
    """Ricgraph explorer entry, this 'page' does not allow data entry.
    The data entry is via the url parameters.
    This url creates a table with the search results with the parameters
    provided in the url.

    Possible parameters are:

    - name, category, value: as usual.
    - system1, system2: the source systems used to compute the overlap.
    - discoverer_mode: which discoverer mode to use:
      only show relevant columns, research outputs
      presented in a tabbed format ('person_view'), or
      show all columns, research outputs presented
      in a table with facets ('details_view').
    - overlap_mode: which overlap to compute: from this node ('thisnode'),
      or from the neighbors of this node ('neighbornodes').

    :return: html to be rendered.
    """
    global html_body_start, html_body_end

    name = get_url_parameter_value(parameter='name')
    category = get_url_parameter_value(parameter='category')
    value = get_url_parameter_value(parameter='value', use_escape=False)
    system1 = get_url_parameter_value(parameter='system1')
    system2 = get_url_parameter_value(parameter='system2')
    discoverer_mode = get_url_parameter_value(parameter='discoverer_mode',
                                              allowed_values=['details_view', 'person_view'],
                                              default_value=DEFAULT_DISCOVERER_MODE)
    overlap_mode = get_url_parameter_value(parameter='overlap_mode',
                                           allowed_values=['thisnode', 'neighbornodes'],
                                           default_value='thisnode')
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

    html = html_body_start
    result = rcg.read_all_nodes(name=name, category=category, value=value)
    if len(result) == 0:
        # Let's try again, assuming we did a string search instead of an exact match search.
        result = rcg.read_all_nodes_containing(value=value)
        if len(result) == 0:
            # No, we really didn't find anything.
            html += get_html_for_cardstart()
            html += 'Unexpected result in getoverlaprecords(): '
            html += 'This node cannot be found in Ricgraph.'
            html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
            html += get_html_for_cardend()
            html += html_body_end
            return html

    if overlap_mode == 'neighbornodes':
        # In this case, we would like to know the overlap of nodes neighboring the node
        # we have just found. We can only do that if we have found only one node.
        if len(result) > 1:
            html += get_html_for_cardstart()
            html += 'Ricgraph explorer found too many nodes. It cannot compute the overlap '
            html += 'of the neighbor nodes of more than one node in getoverlaprecords().'
            html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
            html += get_html_for_cardend()
            html += html_body_end
            return html

        node = result.first()
        if node['category'] == 'person':
            personroot = rcg.get_personroot_node(node)
            if personroot is None:
                html += get_html_for_cardstart()
                html += 'Unexpected result in getoverlaprecords(): '
                html += 'Ricgraph explorer found no "person-root" node.'
                html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
                html += get_html_for_cardend()
                html += html_body_end
                return html
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
        table_colums = DETAIL_COLUMNS
        html += get_you_searched_for_card(name=name,
                                          category=category,
                                          value=value,
                                          discoverer_mode=discoverer_mode,
                                          overlap_mode=overlap_mode,
                                          system1=system1,
                                          system2=system2)
    else:
        table_colums = RESEARCH_OUTPUT_COLUMNS

    html += get_html_table_from_nodes(nodes=relevant_result,
                                      table_header='These records conform to your selection:',
                                      table_columns=table_colums,
                                      discoverer_mode=discoverer_mode)

    html += html_body_end
    return html


@ricgraph_explorer.route(rule='/findenrichcandidates/', methods=['GET'])
def findenrichcandidates() -> str:
    """Ricgraph explorer entry, this 'page' only uses URL parameters.
    This url calls find_enrich_candidates() with the parameters
    provided in the url.

    Possible parameters are:

    - key: as usual, if key = '' , all nodes will be enriched.
    - discoverer_mode: as usual.
    - source_system: the source system to be enriched.

    :return: html to be rendered.
    """
    global html_body_start, html_body_end

    html = html_body_start

    key = get_url_parameter_value(parameter='key', use_escape=False)
    if key == '':
        # We are going to enrich all nodes in Ricgraph.
        node = None
    else:
        name = rcg.get_namepart_from_ricgraph_key(key=key)
        value = rcg.get_valuepart_from_ricgraph_key(key=key)
        nodes = rcg.read_all_nodes(name=name, value=value)
        node = nodes.first()
    discoverer_mode = get_url_parameter_value(parameter='discoverer_mode',
                                              allowed_values=['details_view', 'person_view'],
                                              default_value=DEFAULT_DISCOVERER_MODE)
    source_system = get_url_parameter_value(parameter='source_system')
    if source_system == '':
        html += get_html_for_cardstart()
        html += 'You need to specify a source system if you would like to '
        html += 'enhance a source system.'
        html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
        html += get_html_for_cardend()
        html += html_body_end
        return html

    html += find_enrich_candidates(node=node,
                                   source_system=source_system,
                                   discoverer_mode=discoverer_mode)
    html += html_body_end
    return html


# ##############################################################################
# This is where the work is done.
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


def results_page(node: Node,
                 name_want: list = None, category_want: list = None,
                 discoverer_mode: str = '') -> str:
    """Show the result page for a node.

    :param node: node to show the result page for.
    :param name_want: either a string which indicates that we only want neighbor
      nodes where the property 'name' is equal to 'name_want'
      (e.g. 'ORCID'),
      or a list containing several node names, indicating
      that we want all neighbor nodes where the property 'name' equals
      one of the names in the list 'name_want'
      (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty (empty string), return all nodes.
    :param category_want: similar to 'name_want', but now for the property 'category'.
    :param discoverer_mode: the discoverer_mode to use.
    :return: html to be rendered.
    """
    if name_want is None:
        name_want = []
    if category_want is None:
        category_want = []

    name = node['name']
    category = node['category']
    value = node['value']
    html = ''
    columns = ''
    if discoverer_mode == 'details_view':
        html += get_you_searched_for_card(name=name,
                                          category=category,
                                          value=value,
                                          name_want=name_want,
                                          category_want=category_want,
                                          discoverer_mode=discoverer_mode)

    if discoverer_mode == 'details_view':
        columns = DETAIL_COLUMNS
    elif discoverer_mode == 'person_view':
        columns = RESEARCH_OUTPUT_COLUMNS
    html += get_html_table_from_nodes(nodes=node,
                                      table_header='Ricgraph explorer found node:',
                                      table_columns=columns,
                                      discoverer_mode=discoverer_mode)

    html += get_more_options_card(node=node,
                                  name=name, category=category, value=value,
                                  discoverer_mode=discoverer_mode)

    category_dontwant = ''
    if node['category'] == 'person':
        personroot_nodes = rcg.get_all_personroot_nodes(node=node)
        if len(personroot_nodes) == 0:
            html += get_html_for_cardstart()
            html += 'No person-root node found, this should not happen.'
            html += get_html_for_cardend()
            return html
        elif len(personroot_nodes) == 1:
            person_neighbor_nodes = rcg.get_all_neighbor_nodes_person(node=node)
            table_header = ''
            node_to_find_neighbors = personroot_nodes[0]
            if discoverer_mode == 'details_view':
                table_header = 'This is a <i>person</i> node, '
                table_header += 'these are all IDs of its <i>person-root</i> node:'
                html += details_view_page(nodes=person_neighbor_nodes,
                                          table_header=table_header,
                                          table_columns=DETAIL_COLUMNS,
                                          discoverer_mode=discoverer_mode)
                table_header = 'These are all the neighbors of this <i>person-root</i> node '
                table_header += '(without <i>person</i> nodes):'
                category_dontwant = 'person'
            elif discoverer_mode == 'person_view':
                html += person_view_page(nodes=person_neighbor_nodes,
                                         personroot=node_to_find_neighbors,
                                         discoverer_mode=discoverer_mode)
                table_header = 'These are all the research outputs of this person:'
                # These are excluded because they have already been shown in person_view_page().
                category_dontwant = ['person', 'competence', 'organization', 'project']
            # And now fall through.
        else:
            # More than one person-root node, that should not happen, but it did.
            table_header = 'There is more than one <i>person-root</i> node '
            table_header += 'for the node found. '
            table_header += 'This should not happen, but it did, and that may have been '
            table_header += 'caused by a mislabeling in a source system we harvested. '
            table_header += 'Choose one <i>person-root</i> node to continue:'
            html += get_html_table_from_nodes(nodes=personroot_nodes,
                                              table_header=table_header,
                                              table_columns=DETAIL_COLUMNS,
                                              discoverer_mode=discoverer_mode)
            return html
    else:
        table_header = 'These are the neighbors of this node:'
        node_to_find_neighbors = node

    neighbor_nodes = rcg.get_all_neighbor_nodes(node=node_to_find_neighbors,
                                                name_want=name_want,
                                                category_want=category_want,
                                                category_dontwant=category_dontwant)
    table_html = ''
    if discoverer_mode == 'details_view':
        columns = DETAIL_COLUMNS
        table_html = get_faceted_html_table_from_nodes(nodes=neighbor_nodes,
                                                       name=name,
                                                       category=category,
                                                       value=value,
                                                       table_header=table_header,
                                                       table_columns=columns,
                                                       discoverer_mode=discoverer_mode)
    elif discoverer_mode == 'person_view':
        columns = RESEARCH_OUTPUT_COLUMNS
        table_html = get_tabbed_html_table_from_nodes(nodes=neighbor_nodes,
                                                      table_header=table_header,
                                                      table_columns=columns,
                                                      tabs_on='category',
                                                      discoverer_mode=discoverer_mode)
    html += table_html

    return html


def find_enrich_candidates(node: Union[Node, None],
                           source_system: str = '',
                           discoverer_mode: str = '') -> str:
    """This function tries to find nodes to enrich source system 'source_system'.
    This function can be used to find _all_ enrichments in Ricgraph, but that would
    take too much time, so a hard limit is used to break from the loop.

    :param node: the starting node for finding enrichments for, or None if
      you want to find enrichments for all 'person-root' nodes in Ricgraph.
    :param source_system: the source system to find enrichments for.
    :param discoverer_mode: as usual.
    :return: html to be rendered.
    """
    html = ''
    if node is None:
        personroot_nodes = rcg.read_all_nodes(name='person-root')
        person_root_node = None
        html += get_html_for_cardstart()
        html += 'You have chosen to enrich <em>all</em> nodes in Ricgraph for source system "'
        html += source_system + '". '
        html += 'However, that will take a long time. '
        html += 'Ricgraph explorer will find enrich candidates for at most '
        html += str(MAX_NR_NODES_TO_ENRICH) + ' nodes. '
        html += 'If you want to find more nodes to enrich, change the constant '
        html += '<em>MAX_NR_NODES_TO_ENRICH</em> in file <em>ricgraph_explorer.py</em>.'
        html += get_html_for_cardend()
    else:
        person_root_node = rcg.get_personroot_node(node)
        personroot_nodes = [person_root_node]

    if discoverer_mode == 'details_view':
        table_colums = DETAIL_COLUMNS
        if node is not None:
            html += get_you_searched_for_card(name=node['name'],
                                              category=node['category'],
                                              value=node['value'],
                                              discoverer_mode=discoverer_mode,
                                              source_system=source_system)
    else:
        table_colums = RESEARCH_OUTPUT_COLUMNS

    count = 0
    something_found = False
    for personroot in personroot_nodes:
        if count > MAX_NR_NODES_TO_ENRICH:
            break
        count += 1
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
        html += get_html_for_cardstart()
        table_header = 'This node is used to determine possible enrichments of source system "'
        table_header += source_system + '":'
        html += get_html_table_from_nodes(nodes=personroot,
                                          table_header=table_header,
                                          table_columns=table_colums)

        person_nodes = []
        for node in node_in_source_system:
            if node['category'] == 'person':
                person_nodes.append(node)
        if len(person_nodes) == 0:
            html += 'find_enrich_candidate(): Unexpected, although we have found enrich candidates, '
            html += 'there are no "person" nodes to identify this node. '
            html += 'This does not seem to make sense.'
        else:
            table_header = 'You can use the information in this table to find this node in source system "'
            table_header += source_system + '":'
            html += get_html_table_from_nodes(nodes=person_nodes,
                                              table_header=table_header,
                                              table_columns=table_colums)

        table_header = 'You could enrich source system "' + source_system + '" '
        table_header += 'by using this information harvested from other source systems. '
        table_header += 'This information is not in source system "' + source_system + '".'
        html += get_html_table_from_nodes(nodes=node_not_in_source_system,
                                          table_header=table_header,
                                          table_columns=table_colums)
        html += get_html_for_cardend()

    if something_found:
        html += get_html_for_cardstart()
        html += 'The table above shows how you can enrich source system "'
        html += source_system + '" based on one person node. '
        html += '<a href=' + url_for('findenrichcandidates') + '?'
        html += urllib.parse.urlencode({'discoverer_mode': discoverer_mode,
                                        'source_system': source_system}) + '>'
        html += 'You can click here if you would like to find candidates to enrich '
        html += 'for <em>all</em> nodes in Ricgraph</a>. '
        html += 'Warning: this may take quite some time.'
        html += get_html_for_cardend()
    else:
        if node is None:
            html += get_html_for_cardstart()
            html += 'Ricgraph could not find any candidates to enrich for source system "'
            html += source_system + '".'
            html += get_html_for_cardend()
        else:
            html += get_html_for_cardstart()
            table_header = 'This node is used to determine possible enrichments of source system "'
            table_header += source_system + '":'
            html += get_html_table_from_nodes(nodes=person_root_node,
                                              table_header=table_header,
                                              table_columns=table_colums)
            html += '</br>Ricgraph could not find any candidates to enrich this node. '
            html += 'This might also be caused by a misspelling in the name of the source system.'
            html += get_html_for_cardend()

    html += '</p>'

    return html


def get_more_options_card(node: Node,
                          name: str = '', category: str = '', value: str = '',
                          discoverer_mode: str = '') -> str:
    html = get_html_for_cardstart()
    html += 'You can choose one of the following options (but you do not need to):</br>'

    # Option 1.
    if node['category'] == 'organization':
        # This type of filtering can only be done starting from an 'organization' node.
        key = rcg.create_ricgraph_key(name=node['name'], value=node['value'])
        html += '<details><summary>Click for more information about persons or their results '
        html += 'in this organization.</summary><ul>'
        html += 'By using the fields below, you can choose '
        html += 'what you would like to see about the persons or their results in this organization. '
        html += 'If you leave both fields empty, you will get a list of all persons '
        html += 'and their results in this organization. '
        html += 'These are case-sensitive, exact match fields.</br>'
        form = '<form method="get" action="/filterorganization">'
        form += '<input type="hidden" name="key" value="' + key + '">'
        form += '<input type="hidden" name="discoverer_mode" value="' + discoverer_mode + '">'
        form += '<label>Search for persons or results using field <em>name</em>: '
        form += '</label>'
        form += '<input class="w3-border" type=text name=name_filter></br>'
        form += '<label>Search for persons or results using field <em>category</em>: '
        form += '</label>'
        form += '<input class="w3-border" type=text name=category_filter></br>'
        button_text = 'find more information about persons or their results '
        button_text += 'in this organization'
        form += '<input class="' + button_style + '" type=submit value="' + button_text + '">'
        form += '</form>'
        html += form
        html += '</ul></details>'

    if node['category'] == 'person':
        # Option 2.
        # This type of filtering can only be done starting from an 'person' node.
        key = rcg.create_ricgraph_key(name=node['name'], value=node['value'])
        html += '<details><summary>Click here to find out with whom this person shares '
        html += 'research output types.</summary><ul>'
        html += 'By entering a value in the field below, '
        html += 'you will get a list of persons who share that research output type with this person. '
        html += 'If you leave the field empty, you will get a list of persons who share any research '
        html += 'output type with this person. '
        html += 'This is a case-sensitive, exact match field.</br>'
        form = '<form method="get" action="/filterperson">'
        form += '<input type="hidden" name="key" value="' + key + '">'
        form += '<input type="hidden" name="discoverer_mode" value="' + discoverer_mode + '">'
        form += '<label>Search for this research output type using field <em>category</em>: '
        form += '</label>'
        form += '<input class="w3-border" type=text name=category_filter></br>'
        button_text = 'find persons that share certain research output types with this person'
        form += '<input class="' + button_style + '" type=submit value="' + button_text + '">'
        form += '</form>'
        html += form
        html += '</ul></details>'

        # Option 3.
        # Enriching can only be done starting from a 'person' node.
        key = rcg.create_ricgraph_key(name=node['name'], value=node['value'])
        # html += '<details><summary>Click for more information about enriching your source systems.</summary><ul>'
        html += '<details><summary>Click for more information about improving or '
        html += 'enhancing information in one of your source systems.</summary><ul>'
        html += 'The process of improving or enhancing information in a source system is called "enriching" '
        html += 'your source system. This means that information found in one or more other harvested systems, '
        html += 'is used to improve or enhance information in this source system. '
        html += 'This is possible if the neighbors of this node originate from various source systems. '
        html += 'Use the field below to enter a name of one of your source systems. '
        html += 'Ricgraph explorer will show what information can be added to this source system, '
        html += 'based on the information harvested from other source systems. '
        html += 'This is a case-sensitive, exact match field.</br>'
        form = '<form method="get" action="/findenrichcandidates">'
        form += '<input type="hidden" name="key" value="' + key + '">'
        form += '<input type="hidden" name="discoverer_mode" value="' + discoverer_mode + '">'
        form += '<label>The name of the source system als it appears in column <em>_source</em>: '
        form += '</label>'
        form += '<input class="w3-border" type=text name=source_system></br>'
        button_text = 'find information harvested from other source systems, not present in this source system'
        form += '<input class="' + button_style + '" type=submit value="' + button_text + '">'
        form += '</form>'
        html += form
        html += '</ul></details>'

    # Option 4.
    html += '<details><summary>Click for more information about overlap in '
    html += 'source systems.</summary><ul>'
    html += 'If the information in Ricgraph has orginated from more than one '
    html += 'source system, you can find out from which ones.</br>'
    form = '<form method="get" action="/getoverlap">'
    form += '<input type="hidden" name="name" value="' + name + '">'
    form += '<input type="hidden" name="category" value="' + category + '">'
    form += '<input type="hidden" name="value" value="' + value + '">'
    form += '<input type="hidden" name="discoverer_mode" value="' + discoverer_mode + '">'
    form += '<input type="hidden" name="overlap_mode" value="' + 'neighbornodes' + '">'
    button_text = 'find the overlap in source systems for '
    button_text += 'the neighbor nodes of this node'
    form += '<input class="' + button_style + '" type=submit value="' + button_text + '">'
    form += '</form>'
    html += form
    html += '</ul></details>'
    html += get_html_for_cardend()

    return html


def get_you_searched_for_card(name: str = 'None', category: str = 'None', value: str = 'None',
                              key: str = 'None',
                              name_want: list = None,
                              category_want: list = None,
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
    :param name_want: name_want.
    :param category_want: category_want.
    :param discoverer_mode: discoverer_mode.
    :param overlap_mode: overlap_mode.
    :param system1: system1.
    :param system2: system2.
    :param source_system: source_system.
    :param name_filter: name_filter.
    :param category_filter: category_filter.
    :return: html to be rendered.
    """
    if name_want is None:
        name_want = []
    if category_want is None:
        category_want = []

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
    if len(name_want) > 0:
        html += '<li>name_want: <i>"' + str(name_want) + '"</i>'
    if len(category_want) > 0:
        html += '<li>category_want: <i>"' + str(category_want) + '"</i>'
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


def details_view_page(nodes: Union[list, NodeMatch, None],
                      table_header: str = '',
                      table_columns: list = None,
                      discoverer_mode: str = '') -> str:
    """Create a details page of the node.

    :param nodes: the nodes to create a table from.
    :param table_header: the html to show above the table.
    :param table_columns: a list of columns to show in the table.
    :param discoverer_mode: the discoverer_mode to use.
    :return: html to be rendered.
    """
    if table_columns is None:
        table_columns = []
    html = get_html_table_from_nodes(nodes=nodes,
                                     table_header=table_header,
                                     table_columns=table_columns,
                                     discoverer_mode=discoverer_mode)
    return html


def person_view_page(nodes: Union[list, NodeMatch, None],
                     personroot: Node = None,
                     discoverer_mode: str = '') -> str:
    """Create a person page of the node.

    :param nodes: the nodes to create a table from.
    :param personroot: the person-root of nodes (passed for efficiency).
    :param discoverer_mode: the discoverer_mode to use.
    :return: html to be rendered.
    """
    if len(nodes) == 0:
        html = get_html_for_cardstart()
        html += 'No neighbors found.'
        html += get_html_for_cardend()
        return html

    html = get_html_for_cardstart()
    names = []
    for node in nodes:
        if node['name'] != 'FULL_NAME':
            continue
        key = rcg.create_ricgraph_key(name=node['name'], value=node['value'])
        item = '<a href=' + url_for('findnodes') + '?'
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

    for node in nodes:
        if node['name'] != 'PHOTO_ID':
            continue
        key = rcg.create_ricgraph_key(name=node['name'], value=node['value'])
        html += '&nbsp;&nbsp;'
        html += '<a href=' + url_for('findnodes') + '?'
        html += urllib.parse.urlencode({'key': key,
                                        'discoverer_mode': discoverer_mode}) + '>'
        html += '<img src="' + node['url_main'] + '" alt="' + node['value']
        html += '" title="' + node['value'] + '" height="100"></a>'
    html += '</p>'

    # Note: 'nodes' only contains nodes of category 'person'. We also need all neighbors.
    all_neighbor_nodes = rcg.get_all_neighbor_nodes(node=personroot)
    skills = []
    research_areas = []
    expertise_areas = []
    competence_nodes = []

    # Get the nodes of interest. Using rcg.get_all_neighbor_nodes() is not efficient.
    for node in all_neighbor_nodes:
        if node['category'] == 'competence':
            competence_nodes.append(node)
    for node in competence_nodes:
        key = rcg.create_ricgraph_key(name=node['name'], value=node['value'])
        item = '<a href=' + url_for('findnodes') + '?'
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
    for node in nodes:
        if node['name'] != 'FULL_NAME' \
           and node['name'] != 'person-root' \
           and node['name'] != 'PHOTO_ID':
            id_nodes.append(node)
    html += get_tabbed_html_table_from_nodes(nodes=id_nodes,
                                             table_header='These are all the IDs of this person:',
                                             table_columns=ID_COLUMNS,
                                             tabs_on='name',
                                             discoverer_mode=discoverer_mode)

    organization_nodes = []
    for node in all_neighbor_nodes:
        if node['category'] == 'organization':
            organization_nodes.append(node)
    html += get_html_table_from_nodes(nodes=organization_nodes,
                                      table_header='This person is connected to the following organizations:',
                                      table_columns=ORGANIZATION_COLUMNS,
                                      discoverer_mode=discoverer_mode)

    project_nodes = []
    for node in all_neighbor_nodes:
        if node['category'] == 'project':
            project_nodes.append(node)
    html += get_html_table_from_nodes(nodes=project_nodes,
                                      table_header='This person is connected to the following projects:',
                                      table_columns=RESEARCH_OUTPUT_COLUMNS,
                                      discoverer_mode=discoverer_mode)
    return html


def get_facets_from_nodes(nodes: list,
                          name: str = '', category: str = '', value: str = '',
                          discoverer_mode: str = '') -> str:
    """Do facet navigation in Ricgraph.
    The facets will be constructed based on 'name' and 'category'.
    Facets chosen will be "catched" in function search().
    If there is only one facet (for either one or both), it will not be shown.

    :param nodes: the nodes to construct the facets from.
    :param name: name of the nodes to find.
    :param category: category of the nodes to find.
    :param value: value of the nodes to find.
    :param discoverer_mode: the discoverer_mode to use.
    :return: html to be rendered, or empty string ('') if faceted navigation is
      not useful because there is only one facet.
    """
    if len(nodes) == 0:
        return ''

    name_histogram = {}
    category_histogram = {}
    for node in nodes:
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
    faceted_form += '<form method="get" action="' + url_for('findnodes') + '">'
    faceted_form += '<input type="hidden" name="name" value="' + str(name) + '">'
    faceted_form += '<input type="hidden" name="category" value="' + str(category) + '">'
    faceted_form += '<input type="hidden" name="value" value="' + str(value) + '">'
    faceted_form += '<input type="hidden" name="discoverer_mode" value="' + str(discoverer_mode) + '">'
    if len(name_histogram) == 1:
        # Get the first (and only) element in the dict, pass it as hidden field to search().
        name_key = str(list(name_histogram.keys())[0])
        faceted_form += '<input type="hidden" name="faceted_name" value="' + name_key + '">'
    else:
        faceted_form += '<div class="w3-card-4">'
        faceted_form += '<div class="w3-container uu-yellow">'
        faceted_form += '<b>Faceted navigation on "name"</b>'
        faceted_form += '</div>'
        faceted_form += '<div class="w3-container">'
        # Sort a dict on value:
        # https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
        for bucket in sorted(name_histogram, key=name_histogram.get, reverse=True):
            name_label = bucket + '&nbsp;<i>(' + str(name_histogram[bucket]) + ')</i>'
            faceted_form += '<input class="w3-check" type="checkbox" name="faceted_name" value="'
            faceted_form += bucket + '" checked>'
            faceted_form += '<label>&nbsp;' + name_label + '</label><br/>'
        faceted_form += '</div>'
        faceted_form += '</div><br/>'

    if len(category_histogram) == 1:
        # Get the first (and only) element in the dict, pass it as hidden field to search().
        category_key = str(list(category_histogram.keys())[0])
        faceted_form += '<input type="hidden" name="faceted_category" value="' + category_key + '">'
    else:
        faceted_form += '<div class="w3-card-4">'
        faceted_form += '<div class="w3-container uu-yellow">'
        faceted_form += '<b>Faceted navigation on "category"</b>'
        faceted_form += '</div>'
        faceted_form += '<div class="w3-container">'
        for bucket in sorted(category_histogram, key=category_histogram.get, reverse=True):
            category_label = bucket + '&nbsp;<i>(' + str(category_histogram[bucket]) + ')</i>'
            faceted_form += '<input class="w3-check" type="checkbox" name="faceted_category" value="'
            faceted_form += bucket + '" checked>'
            faceted_form += '<label>&nbsp;' + category_label + '</label><br/>'
        faceted_form += '</div>'
        faceted_form += '</div><br/>'

    # Send name, category and value as hidden fields to search().
    faceted_form += '<input class="w3-input' + button_style + '" type=submit value="Do the faceted navigation">'
    faceted_form += '</form>'
    faceted_form += '</div>'
    faceted_form += get_html_for_cardend()
    html = faceted_form
    return html


def get_overlap_in_source_systems(name: str = '', category: str = '', value: str = '',
                                  discoverer_mode: str = '',
                                  overlap_mode: str = 'thisnode') -> str:
    """Get the overlap in records from source systems.

    :param name: name of the nodes to find.
    :param category: category of the nodes to find.
    :param value: value of the nodes to find.
    :param discoverer_mode: the discoverer_mode to use.
    :param overlap_mode: which overlap to compute: from this node ('thisnode')
    or from the neighbors of this node ('neighbornodes').
    :return: html to be rendered.
    """
    html = ''
    if discoverer_mode == 'details_view':
        html += get_you_searched_for_card(name=name,
                                          category=category,
                                          value=value,
                                          discoverer_mode=discoverer_mode,
                                          overlap_mode=overlap_mode)

    if name == '' and category == '' and value == '':
        html += get_html_for_cardstart()
        html += 'Ricgraph explorer could not find anything.'
        html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
        html += get_html_for_cardend()
        return html

    if discoverer_mode != 'details_view' and discoverer_mode != 'person_view':
        return 'Error, unknown discoverer_mode: ' + discoverer_mode + '. Please try again.'

    if overlap_mode != 'thisnode' and overlap_mode != 'neighbornodes':
        return 'Error, unknown overlap_mode: ' + overlap_mode + '. Please try again.'

    nodes = rcg.read_all_nodes(name=name, category=category, value=value)
    if len(nodes) == 0:
        # Let's try again, assuming we did a string search instead of an exact match search.
        nodes = rcg.read_all_nodes_containing(value=value)
        if len(nodes) == 0:
            # No, we really didn't find anything.
            html += get_html_for_cardstart()
            html += 'Ricgraph explorer could not find anything.'
            html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
            html += get_html_for_cardend()
            return html

    if overlap_mode == 'neighbornodes':
        # In this case, we would like to know the overlap of nodes neighboring the node
        # we have just found. We can only do that if we have found only one node.
        if len(nodes) > 1:
            html += get_html_for_cardstart()
            html += 'Ricgraph explorer found too many nodes. It cannot compute the overlap '
            html += 'of the neighbor nodes of more than one node in get_overlap_in_source_systems().'
            html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
            html += get_html_for_cardend()
            return html

        node = nodes.first()
        if node['category'] == 'person':
            personroot = rcg.get_personroot_node(node)
            if personroot is None:
                html += get_html_for_cardstart()
                html += 'Ricgraph explorer found no "person-root" '
                html += 'node in get_overlap_in_source_systems().'
                html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
                html += get_html_for_cardend()
                return html
            neighbor_nodes = rcg.get_all_neighbor_nodes(node=personroot)
        else:
            neighbor_nodes = rcg.get_all_neighbor_nodes(node=node)
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
            html += get_html_for_cardstart()
            html += 'Ricgraph explorer found no overlap in source systems for '
            html += 'the neighbors of this node. '
            html += 'This may be caused by that these neighbors are "person-root" nodes. '
            html += 'These nodes are generated by Ricgraph and do not have a source system.'
            html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
            html += get_html_for_cardend()
            return html
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
            html += '<a href="' + url_for('getoverlaprecords') + '?'
            html += urllib.parse.urlencode({'name': name, 'category': category, 'value': value,
                                            'system1': system,
                                            'system2': 'singlesource',
                                            'discoverer_mode': discoverer_mode,
                                            'overlap_mode': overlap_mode})
            html += '">'
            html += str(recs_from_one_source[system])
            html += ' (' + str(round(100 * recs_from_one_source[system]/nr_recs_from_one_source)) + '%)'
            html += '</a>'
            html += '</td>'
        else:
            html += '<td>0</td>'
        if system in recs_from_multiple_sources:
            html += '<td>'
            html += '<a href="' + url_for('getoverlaprecords') + '?'
            html += urllib.parse.urlencode({'name': name, 'category': category, 'value': value,
                                            'system1': system,
                                            'system2': 'multiplesource',
                                            'discoverer_mode': discoverer_mode,
                                            'overlap_mode': overlap_mode})
            html += '">'
            html += str(recs_from_multiple_sources[system])
            html += ' (' + str(round(100 * recs_from_multiple_sources[system]/nr_recs_from_multiple_sources)) + '%)'
            html += '</a>'
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
    html += 'You can click on a number to retrieve these records.'

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
            html += '<a href="' + url_for('getoverlaprecords') + '?'
            html += urllib.parse.urlencode({'name': name, 'category': category, 'value': value,
                                            'system1': system1,
                                            'system2': 'multiplesource',
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
                html += '<a href="' + url_for('getoverlaprecords') + '?'
                html += urllib.parse.urlencode({'name': name, 'category': category, 'value': value,
                                                'system1': system1,
                                                'system2': system2,
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


# ##############################################################################
# The HTML for the various 'discover_mode's is generated here.
# ##############################################################################
def get_html_table_from_nodes(nodes: Union[list, NodeMatch, Node],
                              table_header: str = '',
                              table_columns: list = None,
                              discoverer_mode: str = '') -> str:
    """Create a html table for all nodes in the list.

    :param nodes: the nodes to create a table from.
    :param table_header: the html to show above the table.
    :param table_columns: a list of columns to show in the table.
    :param discoverer_mode: the discoverer_mode to use.
    :return: html to be rendered.
    """
    if isinstance(nodes, Node):
        # Make a list.
        nodes = [nodes]

    if table_columns is None:
        table_columns = DETAIL_COLUMNS
    if len(nodes) == 0:
        if set(table_columns) == set(DETAIL_COLUMNS):
            html = get_html_for_cardstart()
            html += 'No neighbors found.'
            html += get_html_for_cardend()
            return html
        else:
            return ''

    html = get_html_for_cardstart()
    html += '<span style="float: left;">' + table_header + '</span>'
    if len(nodes) > MAX_ROWS_IN_TABLE:
        html += '<span style="float: right;">There are ' + str(len(nodes)) + ' rows in this table, showing first '
        html += str(MAX_ROWS_IN_TABLE) + '.</span>'
    elif len(nodes) >= 2:
        html += '<span style="float: right;">There are ' + str(len(nodes)) + ' rows in this table.</span>'
    html += get_html_for_tablestart()
    html += get_html_for_tableheader(table_columns=table_columns)
    count = 0
    for node in nodes:
        count += 1
        if count > MAX_ROWS_IN_TABLE:
            break
        html += get_html_for_tablerow(node=node,
                                      table_columns=table_columns,
                                      discoverer_mode=discoverer_mode)

    html += get_html_for_tableend()
    html += get_html_for_cardend()
    return html


def get_faceted_html_table_from_nodes(nodes: Union[list, NodeMatch, None],
                                      name: str = '',
                                      category: str = '',
                                      value: str = '',
                                      table_header: str = '',
                                      table_columns: list = None,
                                      discoverer_mode: str = '') -> str:
    """Create a faceted html table for all nodes in the list.

    :param nodes: the nodes to create a table from.
    :param name: name of the nodes to find.
    :param category: category of the nodes to find.
    :param value: value of the nodes to find.
    :param table_header: the html to show above the table.
    :param table_columns: a list of columns to show in the table.
    :param discoverer_mode: the discoverer_mode to use.
    :return: html to be rendered.
    """
    if table_columns is None:
        table_columns = []
    if len(nodes) == 0:
        if set(table_columns) == set(DETAIL_COLUMNS):
            html = get_html_for_cardstart()
            html += 'No neighbors found.'
            html += get_html_for_cardend()
            return html
        else:
            return ''

    faceted_html = get_facets_from_nodes(nodes=nodes,
                                         name=name,
                                         category=category,
                                         value=value,
                                         discoverer_mode=discoverer_mode)
    table_html = get_html_table_from_nodes(nodes=nodes,
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
        html += '<div class="w3-col" style="width:300px" >'
        html += faceted_html
        html += '</div>'
        html += '<div class="w3-rest" >'
        html += table_html
        html += '</div>'
        html += '</div>'

    return html


def get_tabbed_html_table_from_nodes(nodes: Union[list, NodeMatch, None],
                                     table_header: str = '',
                                     table_columns: list = None,
                                     tabs_on: str = '',
                                     discoverer_mode: str = '') -> str:
    """Create a html table with tabs for all nodes in the list.

    :param nodes: the nodes to create a table from.
    :param table_header: the html to show above the table.
    :param table_columns: a list of columns to show in the table.
    :param tabs_on: the name of the field in Ricgraph you'd like to have tabs on.
    :param discoverer_mode: the discoverer_mode to use.
    :return: html to be rendered.
    """
    if table_columns is None:
        table_columns = []
    if len(nodes) == 0:
        if set(table_columns) == set(DETAIL_COLUMNS):
            html = get_html_for_cardstart()
            html += 'No neighbors found.'
            html += get_html_for_cardend()
            return html
        else:
            return ''
    if tabs_on != 'name' and tabs_on != 'category':
        return 'get_tabbed_html_table_from_nodes(): Invalid value for "tabs_on": ' + tabs_on + '.'

    histogram = {}
    for node in nodes:
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
        for node in nodes:
            if node[tabs_on] == tab_name:
                nodes_of_tab_name.append(node)
        table_title = 'List of ' + tab_name + 's for this person:'
        table = get_html_table_from_nodes(nodes=nodes_of_tab_name,
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


# ##############################################################################
# The HTML for the tables is generated here.
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
        html += '<td><a href=' + url_for('findnodes') + '?'
        html += urllib.parse.urlencode({'key': key,
                                        'discoverer_mode': discoverer_mode}) + '>'
        html += node['value'] + '</a></td>'
    if 'comment' in table_columns:
        if node['comment'] == '':
            # If this is a person-root node, we put the FULL_NAME(s) in the comment column,
            # for easier browsing.
            # TODO: this is very time consuming.
            html += '<td><ul>'
            if node['name'] == 'person-root':
                for full_name_node in rcg.get_all_neighbor_nodes(node, name_want='FULL_NAME'):
                    html += '<li>' + full_name_node['value'] + '</li>'
            html += '</ul></td>'
        else:
            html += '<td width=30%>' + node['comment'] + '</td>'
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
        if node['_source'] == '':
            html += '<td></td>'
        else:
            html += '<td><ul>'
            for source in node['_source']:
                html += '<li>' + source
            html += '</ul></td>'
    if '_history' in table_columns:
        if node['_history'] == '':
            html += '<td></td>'
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
    # For normal use:
    ricgraph_explorer.run(port=3030)

    # For debug purposes:
    # ricgraph_explorer.run(debug=True, port=3030)

    # If you uncomment the next line, ricgraph explorer will be exposed to
    # the outside world. Read the remarks at the top of this file before you do so.
    # ricgraph_explorer.run(host='0.0.0.0', debug=True, port=3030)
