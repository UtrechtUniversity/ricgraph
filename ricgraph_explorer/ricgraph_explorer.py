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
#
# ########################################################################

import urllib.parse
from typing import Union
from py2neo import Graph, Node
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
stylesheet += 'label {display:inline-block; width:5em}'
stylesheet += 'input {width:25em; margin:2px}'
stylesheet += '</style>'

# The html page footer.
footer = '<div class="footer"><br><hr>'
footer += 'Disclaimer: Ricgraph explorer is recommended for research use, not for production use. '
footer += 'For more information about Ricgraph, see '
footer += '<a href=https://github.com/UtrechtUniversity/ricgraph>'
footer += 'https://github.com/UtrechtUniversity/ricgraph</a>.'
footer += '</div>'

# The html search form.
search_form = '<form method="post">'
search_form += '<p>This is Ricgraph explorer.'
search_form += '<p>Type something to search (this is an exact match, '
search_form += 'case sensitive search, using AND if you use multiple fields):'
search_form += '<br><label>name:</label><input type=text name=search_name>'
search_form += '<br><label>category:</label><input type=text name=search_category>'
search_form += '<br><label>value:</label><input type=text name=search_value>'
search_form += '<br><br><label></label><input type=submit value=search>'
search_form += '</form>'


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
    html += '<br><a href=' + url_for('search') + '>' + 'Start here' + '</a>.'
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
        html += find_nodes_in_ricgraph(name=escape(search_name),
                                       category=escape(search_category),
                                       value=escape(search_value))
    else:
        if id_value is None:
            html += search_form
        else:
            html += find_nodes_in_ricgraph(name='',
                                           category='',
                                           value=escape(id_value))
    html += footer
    return html


# ##############################################################################
# This is where the work is done.
# ##############################################################################
def find_person_root_node(graph: Graph, node: Node) -> Union[Node, None]:
    """Find the 'person-root' node of a 'person' node.

    :param graph: the graph.
    :param node: a 'person' node.
    :return: the person-root node of 'node', or None if nothing found.
    """
    if graph is None or node is None:
        return None
    if node['category'] != 'person':
        return None

    person_root_node = None
    if node['name'] == 'person-root':
        # This is the person-root node.
        person_root_node = node
    else:
        for edge in graph.match((node,), r_type='LINKS_TO'):
            # We have to find the person-root node first.
            next_node = edge.end_node
            if node == next_node:
                continue
            if next_node['name'] == 'person-root':
                person_root_node = next_node
                break

    return person_root_node


def find_nodes_in_ricgraph(name: str, category: str, value: str) -> str:
    """Find all nodes conforming to a query
    in Ricgraph and generate html for the result page.

    :param name: name of the nodes to find.
    :param category: category of the nodes to find.
    :param value: value of the nodes to find.
    :return: html to be rendered.
    """
    graph = rcg.open_ricgraph()         # Should probably be done in a Session
    if graph is None:
        return 'Ricgraph could not be opened.'

    result = rcg.read_all_nodes(name=name, category=category, value=value)
    if len(result) == 0:
        html = '<p>Ricgraph explorer could not find anything.'
        html += '<br><a href=' + url_for('search') + '>' + 'Try again' + '</a>.'
        return html

    html = '<p>You searched for:<ul>'
    html += '<li>name: "' + str(name) + '"'
    html += '<li>category: "' + str(category) + '"'
    html += '<li>value: "' + str(value) + '"'
    html += '</ul>'
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
            # If the node is a person node, show all person records connected
            # to its person-root node (i.e. ORCID, ISNI, etc).
            html += find_person_neighbors_from_node(graph=graph, node=node)

            person_root_node = find_person_root_node(graph=graph, node=node)
            if person_root_node is None:
                html += '<p>No person-root node found, this should not happen.'
                return html
            else:
                header = '<p>These are all the neighbors of this <em>person-root</em> node '
                header += '(including <em>person</em> nodes):'
                html += find_all_neighbors_from_node(graph=graph,
                                                     node=person_root_node,
                                                     header_html=header)
        else:
            header = '<p>These are the neighbors of this node:'
            html += find_all_neighbors_from_node(graph=graph,
                                                 node=node,
                                                 header_html=header)
    return html


def find_person_neighbors_from_node(graph: Graph, node: Node) -> str:
    """Find the person neighbors of a node.

    :param graph: the graph.
    :param node: neighbors of this node.
    :return: html to be rendered.
    """
    if graph is None or node is None:
        return 'No person neighbors found.'

    person_root_node = find_person_root_node(graph=graph, node=node)
    if person_root_node is None:
        html = '<p>Nothing found, this should not happen.'
    else:
        header = '<p>This is a <em>person</em> node, '
        header += 'these are all IDs of its <em>person-root</em> node:'
        html = find_all_neighbors_from_node(graph=graph,
                                            node=person_root_node,
                                            header_html=header,
                                            category='person')

    return html


def find_all_neighbors_from_node(graph: Graph, node: Node,
                                 header_html: str = '', category: str = '') -> str:
    """Find all neighbors of a node (including person neighbors).

    :param graph: the graph.
    :param node: neighbors of this node.
    :param header_html: the html to show above the table.
    :param category: only return nodes of this category (default: return all nodes).
    :return: html to be rendered.
    """
    if graph is None or node is None:
        return 'No neighbors found.'

    html = header_html
    html += get_html_for_tablestart()
    html += get_html_for_tableheader()
    if category != '' and node['category'] == category:
        # Also get the current node.
        html += get_html_for_tablerow(node=node)

    for edge in graph.match((node,), r_type='LINKS_TO'):
        next_node = edge.end_node
        if node == next_node:
            continue
        if category != '':
            if next_node['category'] != category:
                continue
        html += get_html_for_tablerow(node=next_node)

    html += get_html_for_tableend()
    return html


# ##############################################################################
# The HTML for the tables is generated here.
# ##############################################################################
def get_html_for_tablestart() -> str:
    """Get the html required for the start of a html table.

    :return: html to be rendered.
    """
    html = '<table>'
    return html


def get_html_for_tableheader() -> str:
    """Get the html required for the header of a html table.

    :return: html to be rendered.
    """
    html = '<tr>'
    html += '<th>name</th>'
    html += '<th>category</th>'
    html += '<th>value</th>'
    html += '<th>comment</th>'
    html += '<th>url_main</th>'
    html += '<th>url_other</th>'
    html += '<th>_history</th>'
    html += '</tr>'
    return html


def get_html_for_tablerow(node: Node) -> str:
    """Get the html required for a row of a html table.

    :return: html to be rendered.
    """
    html = '<tr>'
    html += '<td>' + node['name'] + '</td>'
    html += '<td>' + node['category'] + '</td>'
    html += '<td><a href=' + url_for('search') + urllib.parse.quote(node['value']) + '>'
    html += node['value'] + '</a></td>'
    if node['comment'] == '':
        html += '<td></td>'
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
