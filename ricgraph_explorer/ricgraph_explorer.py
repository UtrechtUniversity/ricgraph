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
# To keep it simple, everything has been done in this file. It can be improved
# in many ways, but I didn't do that, since it is meant for research purposes,
# not for production use. That means, this code has not been hardened for
# "the outside world". Be careful if you expose it to the outside world.
# Original version Rik D.T. Janssen, January 2023.
# Extended Rik D.T. Janssen, February 2023.
#
# ########################################################################

import urllib.parse
from typing import Union
from py2neo import Node, NodeMatch
from flask import Flask, request, url_for
from markupsafe import escape
import ricgraph as rcg

ricgraph_explorer = Flask(__name__)

# When we do a query, we return at most this number of nodes.
MAX_RESULTS = 75

# The html stylesheet.
stylesheet = '<style>'
stylesheet += '.footer {font-size:85%;}'
stylesheet += 'p, ul, table {font-family:arial; font-size:90%;}'
stylesheet += 'ul {padding-left:2em; margin:0px}'
stylesheet += 'table, th, td {outline: 1px solid black;}'
stylesheet += 'th {background: #a6a6a6; text-align:left;}'
stylesheet += '.searchform label {display:inline-block; width:5em}'
stylesheet += '.searchform input {width:25em; margin:2px}'
stylesheet += '.facetedform label {}'
stylesheet += '.facetedform input {}'
stylesheet += '.facetedform {font-family:arial; font-size:90%;}'
# For table sorting.
stylesheet += 'table.sortable th:not(.sorttable_sorted):not(.sorttable_sorted_reverse)'
stylesheet += ':not(.sorttable_nosort):after{content:" \u25B4 \u25BE"}'
stylesheet += '</style>'

# The html page footer.
footer = '<div class="footer"><br><hr>'
footer += 'Disclaimer: Ricgraph explorer is recommended for research use, not for production use. '
footer += 'For more information about Ricgraph, see '
footer += '<a href=https://github.com/UtrechtUniversity/ricgraph>'
footer += 'https://github.com/UtrechtUniversity/ricgraph</a>.'
footer += '</div>'
# For table sorting. sorttable.js is copied from https://www.kryogenix.org/code/browser/sorttable
# on February 1, 2023. At that link, you'll find a how-to. It is licensed under X11-MIT.
# It is renamed to ricgraph_sorttable.js since it has a small modification.
footer += '<script src="/static/ricgraph_sorttable.js"></script>'

# The html search form.
search_form = '<div class="searchform"><form method="post">'
search_form += '<p>This is Ricgraph explorer.'
search_form += '<p>Type something to search (this is an case-sensitive, exact match '
search_form += 'search, using AND if you use multiple fields):'
search_form += '<br><label>name:</label><input type=text name=search_name>'
search_form += '<br><label>category:</label><input type=text name=search_category>'
search_form += '<br><label>value:</label><input type=text name=search_value>'
search_form += '<br><br><label></label><input type=submit value=search>'
search_form += '</form></div>'

searchcontains_form = '<div class="searchform"><form method="post">'
searchcontains_form += '<p>This is Ricgraph explorer.'
searchcontains_form += '<p>Type something to search (this is a case-insensitive, inexact match):'
searchcontains_form += '<br><label>value:</label><input type=text name=search_value>'
searchcontains_form += '<br><br><label></label><input type=submit value=search>'
searchcontains_form += '</form></div>'


# ##############################################################################
# Entry functions.
# ##############################################################################
@ricgraph_explorer.route("/")
def index_html() -> str:
    """Ricgraph explorer entry, the index page, when you access '/'.

    :return: html to be rendered.
    """
    global stylesheet, footer

    html = stylesheet
    html += '<p>This is Ricgraph explorer. You can use it to explore Ricgraph.'
    html += '<ul>'
    html += '<li><a href=' + url_for('search') + '>' + 'Do a case-sensitive, '
    html += 'exact match search on fields '
    html += '<em>name</em>, <em>category</em> and/or <em>value</em>' + '</a>;'
    html += '<li><a href=' + url_for('searchcontains') + '>' + 'Do a search on '
    html += 'field <em>value</em> containing a string' + '</a>.'
    html += '</ul>'
    html += footer
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
    global stylesheet, footer, search_form

    html = stylesheet
    if request.method == 'POST':
        search_name = request.form['search_name']
        search_category = request.form['search_category']
        search_value = request.form['search_value']
        name_want = request.form.getlist('name')
        category_want = request.form.getlist('category')
        html += find_nodes_in_ricgraph(name=escape(search_name),
                                       category=escape(search_category),
                                       value=escape(search_value),
                                       name_want=name_want,
                                       category_want=category_want)
    else:
        if id_value is None:
            html += search_form
        else:
            html += find_nodes_in_ricgraph(name='',
                                           category='',
                                           value=escape(id_value))
    html += footer
    return html


@ricgraph_explorer.route('/searchcontains/', methods=['GET', 'POST'])
def searchcontains() -> str:
    """Ricgraph explorer entry, the search on a substring page,
    when you access '/searchcontains'.
    This page will present a search page, where you can search
    on the 'value' field of a node.

    :return: html to be rendered.
    """
    global stylesheet, footer, searchcontains_form

    html = stylesheet
    if request.method == 'POST':
        search_value = request.form['search_value']
        html += find_nodes_in_ricgraph(value=escape(search_value),
                                       use_contain_phrase=True)
    else:
        html += searchcontains_form

    html += footer
    return html


# ##############################################################################
# This is where the work is done.
# ##############################################################################
def faceted_search_in_ricgraph(nodes: list,
                               name: str = '', category: str = '', value: str = '') -> str:
    """Do a faceted search in Ricgraph.
    The facets will be constructed based on 'name' and 'category'.
    Facets chosen will be catched in function search().
    If there is only one facet, it will not be shown.

    :param nodes: the nodes to construct the facets from.
    :param name: name of the nodes to find.
    :param category: category of the nodes to find.
    :param value: value of the nodes to find.
    :return: html to be rendered.
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
        # Faceted search does not make sense, don't show facets.
        return ''

    faceted_form = '<div class="facetedform"><form method="post" action="/search">'
    if len(name_histogram) == 1:
        # Get the first (and only) element in the dict, we pass it as hidden field to search().
        name_key = str(list(name_histogram.keys())[0])
        faceted_form += '<input type="hidden" name="name" value="' + name_key + '">'
    else:
        faceted_form += '<fieldset><legend>Select for faceted search on "name"</legend>'
        # Sort a dict on value:
        # https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
        for bucket in sorted(name_histogram, key=name_histogram.get, reverse=True):
            name_label = bucket + '&nbsp;<em>(' + str(name_histogram[bucket]) + ')</em>&emsp;'
            faceted_form += '<input type="checkbox" name ="name" value="' + bucket + '" checked>'
            faceted_form += '<label>' + name_label + ' </label>'
        faceted_form += '</fieldset>'

    if len(category_histogram) == 1:
        # Get the first (and only) element in the dict, we pass it as hidden field to search().
        category_key = str(list(category_histogram.keys())[0])
        faceted_form += '<input type="hidden" name="category" value="' + category_key + '">'
    else:
        faceted_form += '<fieldset><legend>Select for faceted search on "category":</legend>'
        for bucket in sorted(category_histogram, key=category_histogram.get, reverse=True):
            category_label = bucket + '&nbsp;<em>(' + str(category_histogram[bucket]) + ')</em>&emsp;'
            faceted_form += '<input type="checkbox" name ="category" value="' + bucket + '" checked>'
            faceted_form += '<label>' + category_label + '</label>'
        faceted_form += '</fieldset><br>'

    # Send name, category and value as hidden field to search().
    faceted_form += '<input type="hidden" name="search_name" value="' + str(name) + '">'
    faceted_form += '<input type="hidden" name="search_category" value="' + str(category) + '">'
    faceted_form += '<input type="hidden" name="search_value" value="' + str(value) + '">'
    faceted_form += '<label></label><input type=submit value="Do the faceted search">'
    faceted_form += '</form></div>'
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
        html = '<p>Please enter a value in the search field.'
        html += '<br><a href=' + url_for('index_html') + '>' + 'Try again' + '</a>.'
        return html

    if name_want is None:
        name_want = []
    if category_want is None:
        category_want = []

    if use_contain_phrase:
        if len(value) < 3:
            html = '<p>Please use at least three characters for your search string.'
            html += '<br><a href=' + url_for('index_html') + '>' + 'Try again' + '</a>.'
            return html

        result = rcg.read_all_nodes_containing(value=value)
    else:
        result = rcg.read_all_nodes(name=name, category=category, value=value)

    if len(result) == 0:
        html = '<p>Ricgraph explorer could not find anything.'
        html += '<br><a href=' + url_for('index_html') + '>' + 'Try again' + '</a>.'
        return html

    html = '<p>You searched for:<ul>'
    if not use_contain_phrase:
        html += '<li>name: "' + str(name) + '"'
        html += '<li>category: "' + str(category) + '"'

    html += '<li>value: "' + str(value) + '"'
    if len(name_want) > 0:
        html += '<li>name_want: "' + str(name_want) + '"'
    if len(category_want) > 0:
        html += '<li>category_want: "' + str(category_want) + '"'

    html += '</ul>'

    if use_contain_phrase:
        header = '<p>Choose one node to continue:'
        html += get_html_table_from_nodes(nodes=result, header_html=header)
        return html

    if len(result) > MAX_RESULTS:
        html += '<p>There are ' + str(len(result)) + ' results, showing first '
        html += str(MAX_RESULTS) + '.<br>'
    count = 0
    for node in result:
        # Loop over the nodes found.
        count += 1
        if count > MAX_RESULTS:
            break

        html += '<br><p>Ricgraph explorer found node:'
        html += get_html_for_tablestart()
        html += get_html_for_tableheader()
        html += get_html_for_tablerow(node=node)
        html += get_html_for_tableend()
        if node['category'] == 'person':
            personroot_nodes = rcg.get_all_personroot_nodes(node)
            if len(personroot_nodes) == 0:
                html += '<p>No person-root node found, this should not happen.'
                return html
            elif len(personroot_nodes) == 1:
                header = '<p>This is a <em>person</em> node, '
                header += 'these are all IDs of its <em>person-root</em> node:'
                neighbor_nodes = rcg.get_all_neighbor_nodes_person(node)
                html += get_html_table_from_nodes(nodes=neighbor_nodes,
                                                  header_html=header)

                header = '<p>These are all the neighbors of this <em>person-root</em> node '
                header += '(without <em>person</em> nodes):'
                neighbor_nodes = rcg.get_all_neighbor_nodes(personroot_nodes[0],
                                                            name_want=name_want,
                                                            category_want=category_want,
                                                            category_dontwant='person')

                html += get_html_table_from_nodes(nodes=neighbor_nodes,
                                                  header_html=header)
                html += faceted_search_in_ricgraph(nodes=neighbor_nodes,
                                                   name=name,
                                                   category=category,
                                                   value=value)
            else:
                # More than one person-root node, that should not happen, but it did.
                header = '<p>There is more than one <em>person-root</em> node '
                header += 'for the node we have found. '
                header += 'This should not happen, but it did, and that is probably caused '
                header += 'by a mislabeling in a source system we harvested. '
                header += 'Choose one <em>person-root</em> node to continue:'
                html += get_html_table_from_nodes(nodes=personroot_nodes,
                                                  header_html=header)
                break
        else:
            header = '<p>These are the neighbors of this node:'
            neighbor_nodes = rcg.get_all_neighbor_nodes(node,
                                                        name_want=name_want,
                                                        category_want=category_want)
            html += get_html_table_from_nodes(nodes=neighbor_nodes,
                                              header_html=header)
            html += faceted_search_in_ricgraph(nodes=neighbor_nodes,
                                               name=name,
                                               category=category,
                                               value=value)
    return html


def get_html_table_from_nodes(nodes: Union[list, NodeMatch, None], header_html: str = '') -> str:
    """Create a html table for all nodes in the list.

    :param nodes: the nodes to create a table from.
    :param header_html: the html to show above the table.
    :return: html to be rendered.
    """
    if len(nodes) == 0:
        return '<p>No neighbors found.'

    html = header_html
    html += get_html_for_tablestart()
    html += get_html_for_tableheader()
    for node in nodes:
        html += get_html_for_tablerow(node=node)

    html += get_html_for_tableend()
    return html


# ##############################################################################
# The HTML for the tables is generated here.
# ##############################################################################
def get_html_for_tablestart() -> str:
    """Get the html required for the start of a html table.

    :return: html to be rendered.
    """
    html = '<table class="sortable">'
    return html


def get_html_for_tableheader() -> str:
    """Get the html required for the header of a html table.

    :return: html to be rendered.
    """
    html = '<tr>'
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
