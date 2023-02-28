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
# Please note that this code is meant for research purposes,
# not for production use. That means, this code has not been hardened for
# "the outside world". Be careful if you expose it to the outside world.
# Original version Rik D.T. Janssen, January 2023.
# Extended Rik D.T. Janssen, February 2023.
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

# When we do a query, we return at most this number of nodes.
MAX_RESULTS = 50

# The style for the buttons, note the space before and after the text.
button_style = ' w3-button uu-yellow w3-round-large w3-mobile '
# A button with a black line around it.
button_style_border = button_style + ' w3-border rj-border-black '

# The html stylesheet.
stylesheet = '<style>'
stylesheet += '.w3-container {padding: 16px;}'
stylesheet += '.w3-check {width:15px;height: 15px;position: relative; top:3px;}'
# Define UU colors. We do not need to define "black" and "white" (they do exist).
# See https://www.uu.nl/organisatie/huisstijl/huisstijlelementen/kleur.
stylesheet += '.uu-yellow, .uu-hover-yellow:hover '
stylesheet += '{color: #000!important; background-color: #ffcd00!important;}'
stylesheet += '.uu-red, .uu-hover-red:hover '
stylesheet += '{color: #000!important; background-color: #c00a35!important;}'
stylesheet += '.rj-gray, .rj-hover-gray:hover '
stylesheet += '{color: #000!important; background-color: #cecece!important;}'
stylesheet += '.rj-border-black, .rj-hover-border-black:hover {border-color: #000!important;}'
stylesheet += 'body {background-color:white;}'
stylesheet += 'body, h1, h2, h3, h4, h5, h6 {font-family: "Open Sans", sans-serif;}'
stylesheet += 'ul {padding-left:2em; margin:0px}'
stylesheet += 'table {font-size:85%;}'
stylesheet += 'table, th, td {border-collapse:collapse; border: 1px solid black}'
stylesheet += 'th {text-align:left;}'
stylesheet += '.facetedform {font-size:90%;}'
# For table sorting. \u00a0 is a non-breaking space.
stylesheet += 'table.sortable th:not(.sorttable_sorted):not(.sorttable_sorted_reverse)'
stylesheet += ':not(.sorttable_nosort):after{content:"\u00a0\u25b4\u00a0\u25be"}'
stylesheet += '</style>'

# The html preamble
html_preamble = '<meta name="viewport" content="width=device-width, initial-scale=1">'
html_preamble += '<link rel="stylesheet" href="/static/w3pro.css">'
html_preamble += '<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Open+Sans">'

# The html page header.
page_header = '<header class="w3-container uu-yellow">'
page_header += '<div class="w3-bar uu-yellow">'
page_header += '<div class="w3-bar-item w3-mobile" style="width:25%">'
page_header += '<a href="/" style="text-decoration:none">'
page_header += '<img src="/static/uu_logo_small.png" height="30" style="padding-right: 3em">'
page_header += '<img src="/static/ricgraph_logo.png" height="30" style="padding-right: 0.5em">explorer</a>'
page_header += '</div>'
page_header += '<a href="/" class="w3-bar-item' + button_style_border + '">Home</a>'
page_header += '<a href="/search" class="w3-bar-item' + button_style_border + '">Exact match search</a>'
page_header += '<a href="/searchcontains" class="w3-bar-item' + button_style_border + '">String search</a>'
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

# The html search form for an exact match search (on /search).
search_form = '<section class="w3-container">'
search_form += '<div class="w3-card-4">'
search_form += '<div class="w3-container uu-yellow">'
search_form += '<h3>Type something to search</h3>'
search_form += 'This is an case-sensitive, exact match search, using AND if you use multiple fields:'
search_form += '</div>'
search_form += '<div class="w3-container">'
search_form += '<form method="post">'
search_form += '<label>name:</label><input class="w3-input w3-border" type=text name=search_name>'
search_form += '<br><label>category:</label><input class="w3-input w3-border" type=text name=search_category>'
search_form += '<br><label>value:</label><input class="w3-input w3-border" type=text name=search_value>'
search_form += '<br><input class="w3-input' + button_style + '" type=submit value=search>'
search_form += '</form>'
search_form += '</div>'
search_form += '</div>'
search_form += '</section>'

# The html search form for a search on a string (on /searchcontains).
searchcontains_form = '<section class="w3-container">'
searchcontains_form += '<div class="w3-card-4">'
searchcontains_form += '<div class="w3-container uu-yellow">'
searchcontains_form += '<h3>Type something to search</h3>'
searchcontains_form += 'This is a case-insensitive, inexact match:'
searchcontains_form += '</div>'
searchcontains_form += '<div class="w3-container">'
searchcontains_form += '<form method="post">'
searchcontains_form += '<label>value:</label><input class="w3-input w3-border" type=text name=search_value>'
searchcontains_form += '<br><input class="w3-input' + button_style + '" type=submit value=search>'
searchcontains_form += '</form>'
searchcontains_form += '</div>'
searchcontains_form += '</div>'
searchcontains_form += '</section>'


# ##############################################################################
# Entry functions.
# ##############################################################################
@ricgraph_explorer.route("/")
def index_html() -> str:
    """Ricgraph explorer entry, the index page, when you access '/'.

    :return: html to be rendered.
    """
    global html_body_start, html_body_end

    html = html_body_start
    html += get_html_for_cardstart()
    html += 'This is Ricgraph explorer. You can use it to explore Ricgraph.'
    html += '<ul>'
    html += '<li><a href=' + url_for('search') + '>' + 'Do a case-sensitive, '
    html += 'exact match search on fields '
    html += '<i>name</i>, <i>category</i> and/or <i>value</i>' + '</a>;'
    html += '<li><a href=' + url_for('searchcontains') + '>' + 'Do a search on '
    html += 'field <i>value</i> containing a string' + '</a>.'
    html += '</ul>'
    html += get_html_for_cardend()
    html += html_body_end
    return html


@ricgraph_explorer.route('/search/', methods=['GET', 'POST'])
@ricgraph_explorer.route('/search/<path:id_value>', methods=['GET'])
def search(id_value=None) -> str:
    """Ricgraph explorer entry, the search page, when you access '/search'.
    If you add a parameter, like '/search/abcd' Ricgraph will search
    for 'abcd' in the 'value' field of a node.
    Without parameter, it will present a search page, where you can search
    on the 'name', 'category' and/or 'value' field of a node.

    :param id_value: value to search for in the 'value' field.
    :return: html to be rendered.
    """
    global html_body_start, html_body_end, search_form

    html = html_body_start
    if request.method == 'POST':
        search_name = request.form['search_name']
        search_category = request.form['search_category']
        search_value = request.form['search_value']
        faceted_name_list = request.form.getlist('faceted_name')
        faceted_category_list = request.form.getlist('faceted_category')
        html += find_nodes_in_ricgraph(name=escape(search_name),
                                       category=escape(search_category),
                                       value=escape(search_value),
                                       name_want=faceted_name_list,
                                       category_want=faceted_category_list)
    else:
        if id_value is None:
            html += search_form
        else:
            html += find_nodes_in_ricgraph(name='',
                                           category='',
                                           value=escape(id_value))
    html += html_body_end
    return html


@ricgraph_explorer.route('/searchcontains/', methods=['GET', 'POST'])
def searchcontains() -> str:
    """Ricgraph explorer entry, the search on a substring page,
    when you access '/searchcontains'.
    This page will present a search page, where you can search
    on the 'value' field of a node.

    :return: html to be rendered.
    """
    global html_body_start, html_body_end, searchcontains_form

    html = html_body_start
    if request.method == 'POST':
        search_value = request.form['search_value']
        html += find_nodes_in_ricgraph(value=escape(search_value),
                                       use_contain_phrase=True)
    else:
        html += searchcontains_form

    html += html_body_end
    return html


# ##############################################################################
# This is where the work is done.
# ##############################################################################
def faceted_navigation_in_ricgraph(nodes: list,
                                   name: str = '', category: str = '', value: str = '') -> str:
    """Do facet navigation in Ricgraph.
    The facets will be constructed based on 'name' and 'category'.
    Facets chosen will be "catched" in function search().
    If there is only one facet (for either one or both), it will not be shown.

    :param nodes: the nodes to construct the facets from.
    :param name: name of the nodes to find.
    :param category: category of the nodes to find.
    :param value: value of the nodes to find.
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
    faceted_form += '<form method="post" action="/search">'
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
            faceted_form += '<label>&nbsp;' + name_label + '</label><br>'
        faceted_form += '</div>'
        faceted_form += '</div></br>'

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
            faceted_form += '<label>&nbsp;' + category_label + '</label><br>'
        faceted_form += '</div>'
        faceted_form += '</div></br>'

    # Send name, category and value as hidden fields to search().
    faceted_form += '<input type="hidden" name="search_name" value="' + str(name) + '">'
    faceted_form += '<input type="hidden" name="search_category" value="' + str(category) + '">'
    faceted_form += '<input type="hidden" name="search_value" value="' + str(value) + '">'
    faceted_form += '<input class="w3-input' + button_style + '" type=submit value="Do the faceted navigation">'
    faceted_form += '</form>'
    faceted_form += '</div>'
    faceted_form += get_html_for_cardend()
    html = faceted_form
    return html


def find_nodes_in_ricgraph(name: str = '', category: str = '', value: str = '',
                           use_contain_phrase: bool = False,
                           name_want: list = None, category_want: list = None) -> str:
    """Find all nodes conforming to a query
    in Ricgraph and generate html for the result page.

    :param name: name of the nodes to find.
    :param category: category of the nodes to find.
    :param value: value of the nodes to find.
    :param use_contain_phrase: determines either case-sensitive & exact match,
      or case-insensitive & inexact match.
    :param name_want: either a string which indicates that we only want neighbor
      nodes where the property 'name' is equal to 'name_want'
      (e.g. 'ORCID'),
      or a list containing several node names, indicating
      that we want all neighbor nodes where the property 'name' equals
      one of the names in the list 'name_want'
      (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty (empty string), return all nodes.
    :param category_want: similar to 'name_want', but now for the property 'category'.
    :return: html to be rendered.
    """
    graph = rcg.open_ricgraph()         # Should probably be done in a Session
    if graph is None:
        return 'Ricgraph could not be opened.'

    if name == '' and category == '' and value == '':
        html = get_html_for_cardstart()
        html += 'The search field should have a value.'
        html += '<br><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
        html += get_html_for_cardend()
        return html

    if name_want is None:
        name_want = []
    if category_want is None:
        category_want = []

    if use_contain_phrase:
        if len(value) < 3:
            html = get_html_for_cardstart()
            html += 'The search string should be at least three characters.'
            html += '<br><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
            html += get_html_for_cardend()
            return html

        result = rcg.read_all_nodes_containing(value=value)
    else:
        result = rcg.read_all_nodes(name=name, category=category, value=value)

    if len(result) == 0:
        html = get_html_for_cardstart()
        html += 'Ricgraph explorer could not find anything.'
        html += '<br><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
        html += get_html_for_cardend()
        return html

    html = get_html_for_cardstart()
    html += 'You searched for:<ul>'
    if not use_contain_phrase:
        html += '<li>name: <i>"' + str(name) + '"</i>'
        html += '<li>category: <i>"' + str(category) + '"</i>'

    html += '<li>value: <i>"' + str(value) + '"</i>'
    if len(name_want) > 0:
        html += '<li>name_want: <i>"' + str(name_want) + '"</i>'
    if len(category_want) > 0:
        html += '<li>category_want: <i>"' + str(category_want) + '"</i>'
    html += '</ul>'
    html += get_html_for_cardend()

    if use_contain_phrase:
        table_header = 'Choose one node to continue:'
        html += get_html_table_from_nodes(nodes=result, table_header=table_header)
        return html

    if len(result) > MAX_RESULTS:
        html += get_html_for_cardstart()
        html += 'There are ' + str(len(result)) + ' results, showing first '
        html += str(MAX_RESULTS) + '.<br>'
        html += get_html_for_cardend()
    count = 0
    # Loop over the nodes found.
    for node in result:
        count += 1
        if count > MAX_RESULTS:
            break

        html += get_html_for_cardline()
        html += get_html_table_from_nodes(nodes=[node],
                                          table_header='Ricgraph explorer found node:')
        if node['category'] == 'person':
            personroot_nodes = rcg.get_all_personroot_nodes(node)
            if len(personroot_nodes) == 0:
                html += get_html_for_cardstart()
                html += 'No person-root node found, this should not happen.'
                html += get_html_for_cardend()
                return html
            elif len(personroot_nodes) == 1:
                table_header = 'This is a <i>person</i> node, '
                table_header += 'these are all IDs of its <i>person-root</i> node:'
                neighbor_nodes = rcg.get_all_neighbor_nodes_person(node)
                html += get_html_table_from_nodes(nodes=neighbor_nodes,
                                                  table_header=table_header)

                table_header = 'These are all the neighbors of this <i>person-root</i> node '
                table_header += '(without <i>person</i> nodes):'
                node_to_find_neighbors = personroot_nodes[0]
                category_dontwant = 'person'
                # And now fall through.
            else:
                # More than one person-root node, that should not happen, but it did.
                table_header = 'There is more than one <i>person-root</i> node '
                table_header += 'for the node found. '
                table_header += 'This should not happen, but it did, and that may have been '
                table_header += 'caused by a mislabeling in a source system we harvested. '
                table_header += 'Choose one <i>person-root</i> node to continue:'
                html += get_html_table_from_nodes(nodes=personroot_nodes,
                                                  table_header=table_header)
                return html
        else:
            table_header = 'These are the neighbors of this node:'
            node_to_find_neighbors = node
            category_dontwant = ''

        neighbor_nodes = rcg.get_all_neighbor_nodes(node=node_to_find_neighbors,
                                                    name_want=name_want,
                                                    category_want=category_want,
                                                    category_dontwant=category_dontwant)
        faceted_html = faceted_navigation_in_ricgraph(nodes=neighbor_nodes,
                                                      name=name,
                                                      category=category,
                                                      value=value)
        if faceted_html == '':
            table_header += '<br>[Facet panel not shown because there is only one facet to show.]'

        table_html = get_html_table_from_nodes(nodes=neighbor_nodes,
                                               table_header=table_header)
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


def get_html_table_from_nodes(nodes: Union[list, NodeMatch, None], table_header: str = '') -> str:
    """Create a html table for all nodes in the list.

    :param nodes: the nodes to create a table from.
    :param table_header: the html to show above the table.
    :return: html to be rendered.
    """
    if len(nodes) == 0:
        html = get_html_for_cardstart()
        html += 'No neighbors found.'
        html += get_html_for_cardend()
        return html

    html = get_html_for_cardstart()
    html += table_header
    html += get_html_for_tablestart()
    html += get_html_for_tableheader()
    for node in nodes:
        html += get_html_for_tablerow(node=node)

    html += get_html_for_tableend()
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


def get_html_for_tableheader() -> str:
    """Get the html required for the header of a html table.

    :return: html to be rendered.
    """
    html = '<tr class="uu-yellow">'
    html += '<th>name</th>'
    html += '<th>category</th>'
    html += '<th class=sorttable_alpha">value</th>'
    html += '<th>comment</th>'
    html += '<th class="sorttable_nosort">url_main</th>'
    html += '<th class="sorttable_nosort">url_other</th>'
    html += '<th class="sorttable_nosort">_history</th>'
    html += '</tr>'
    return html


def get_html_for_tablerow(node: Node) -> str:
    """Get the html required for a row of a html table.

    :return: html to be rendered.
    """
    html = '<tr class="item">'
    html += '<td>' + node['name'] + '</td>'
    html += '<td>' + node['category'] + '</td>'
    html += '<td><a href=' + url_for('search') + urllib.parse.quote(node['value']) + '>'
    html += node['value'] + '</a></td>'
    if node['comment'] == '':
        # If this is a person-root node, we put the FULL_NAME(s) in the comment column,
        # for easier browsing.
        html += '<td><ul>'
        if node['name'] == 'person-root':
            for full_name_node in rcg.get_all_neighbor_nodes(node, name_want='FULL_NAME'):
                html += '<li>' + full_name_node['value'] + '</li>'
        html += '</ul></td>'
    else:
        html += '<td width=30%>' + node['comment'] + '</td>'

    if node['url_main'] == '':
        html += '<td></td>'
    else:
        html += '<td><a href=' + node['url_main'] + ' target="_blank"> url_main link </a></td>'

    if node['url_other'] == '':
        html += '<td></td>'
    else:
        html += '<td><a href=' + node['url_other'] + ' target="_blank"> url_other link </a></td>'

    if node['_history'] == '':
        html += '<td></td>'
    else:
        html += '<td><details><summary>Click for history</summary><ul>'
        for history in node['_history']:
            html += '<li>' + history
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
