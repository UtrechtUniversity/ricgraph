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
# Note: if a 'value' field is passed as an URL parameter, it is not escaped
# using escape() (which is supposed to be good practise). If we would use escape(),
# a search with 'value' that contains an '&', will be translated to the HTML
# character '&amp;', which will not be found in the database.
#
# Original version Rik D.T. Janssen, January 2023.
# Extended Rik D.T. Janssen, February, September, October 2023.
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
page_header += '<a href="/search?discoverer_mode=' + DEFAULT_DISCOVERER_MODE + '" class="w3-bar-item'
page_header += button_style_border + '">Exact match search (' + DEFAULT_DISCOVERER_MODE + ')</a>'
page_header += '<a href="/searchcontains?discoverer_mode=' + DEFAULT_DISCOVERER_MODE + '" class="w3-bar-item'
page_header += button_style_border + '">String search (' + DEFAULT_DISCOVERER_MODE + ')</a>'
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
# Don't use this one, then 'discoverer_mode' will not be passed:
# search_form += '<form method="post" action="/search">'
search_form += '<form method="post">'
search_form += '<label>Search for a value in Ricgraph field <em>name</em>:</label>'
search_form += '<input class="w3-input w3-border" type=text name=search_name>'
search_form += '<br/><label>Search for a value in Ricgraph field <em>category</em>:</label>'
search_form += '<input class="w3-input w3-border" type=text name=search_category>'
search_form += '<br/><label>Search for a value in Ricgraph field <em>value</em>:</label>'
search_form += '<input class="w3-input w3-border" type=text name=search_value>'
search_form += '<input type="hidden" name="search_discoverer_mode" value=>'
search_form += '<br/><input class="w3-input' + button_style + '" type=submit value=search>'
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
# Don't use this one, then 'discoverer_mode' will not be passed:
# searchcontains_form += '<form method="post" action="/searchcontains">'
searchcontains_form += '<form method="post">'
searchcontains_form += '<label>Search for a value in Ricgraph field <em>value</em>:</label>'
searchcontains_form += '<input class="w3-input w3-border" type=text name=search_value>'
searchcontains_form += '<br/><input class="w3-input' + button_style + '" type=submit value=search>'
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
    html += '<h3>This is Ricgraph explorer</h3>'
    html += 'You can use Ricgraph explorer to explore Ricgraph. '

    html += 'There are two methods to start exploring:'
    html += '<ul>'
    html += '<li>find your first node by using exact match;'
    html += '<li>find your first node by using search on a field value.</li>'
    html += '</li>'
    html += '</ul>'
    html += '</p>'

    html += 'There are two methods for viewing the results '
    html += '(for an explation see the text below the table):'
    html += '<ul>'
    html += '<li><em>person_view</em>: only show relevant columns, '
    html += 'research outputs presented in a <em>tabbed</em> format;'
    html += '</li>'
    html += '<li><em>details_view</em>: show all columns, '
    html += 'research outputs presented in a table with <em>facets</em>.'
    html += '</li>'
    html += '</ul>'
    html += '</p>'
    html += '<br/>'

    html += get_html_for_tablestart()
    html += '<colgroup class="uu-yellow">'
    html += '<col span=1>'
    html += '</colgroup>'
    html += '<tr class="uu-yellow" style="font-size:120%">'
    html += '<th class="sorttable_nosort">view of the result</th>'
    html += '<th class="sorttable_nosort">case-sensitive, exact match search on fields<br/><i>name</i>, '
    html += '<i>category</i> and/or <i>value</i></th>'
    html += '<th class="sorttable_nosort">search on field <i>value</i> containing a string</th>'
    html += '</tr>'
    html += '<tr style="font-size:120%;">'
    html += '<td>person_view<br/>only show relevant columns</td>'
    html += '<td width=40% style="text-align:center;"><a href=' + url_for('search')
    html += '?discoverer_mode=person_view class="'
    html += button_style + '">choose this one</a></td>'
    html += '<td width=40% style="text-align:center"><a href=' + url_for('searchcontains')
    html += '?discoverer_mode=person_view class="'
    html += button_style + '">choose this one</a></td>'
    html += '</tr>'
    html += '<tr style="font-size:120%;">'
    html += '<td>details_view<br/>show all columns</td>'
    html += '<td style="text-align:center;"><a href=' + url_for('search')
    html += '?discoverer_mode=details_view class="'
    html += button_style + '">choose this one</a></td>'
    html += '<td style="text-align:center;"><a href=' + url_for('searchcontains')
    html += '?discoverer_mode=details_view class="'
    html += button_style + '">choose this one</a></td>'
    html += '</tr>'
    html += get_html_for_tableend()
    html += '</table>'
    html += '</p>'
    html += '<br/>'

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


@ricgraph_explorer.route('/search/', methods=['GET', 'POST'])
@ricgraph_explorer.route('/search/<path:key_value>', methods=['GET'])
def search(key_value=None) -> str:
    """Ricgraph explorer entry, the search page, when you access '/search'.
    If you add a parameter, like '/search/abcd' Ricgraph will search
    for 'abcd' in the 'value' field of a node.
    Without parameter, it will present a search page, where you can search
    on the 'name', 'category' and/or 'value' field of a node.

    :param key_value: key to search for in the 'name' and 'value' fields.
    :return: html to be rendered.
    """
    global html_body_start, html_body_end, search_form

    discoverer_mode = str(escape(request.args.get('discoverer_mode')))
    if discoverer_mode == 'None':
        discoverer_mode_passed_in_url = False
    else:
        discoverer_mode_passed_in_url = True

    if discoverer_mode != 'details_view' \
       and discoverer_mode != 'person_view':
        discoverer_mode = DEFAULT_DISCOVERER_MODE

    html = html_body_start
    if request.method == 'POST':
        search_name = str(escape(request.form['search_name']))
        search_category = str(escape(request.form['search_category']))
        # Do not use escape() for 'value', see note at beginning of this file.
        search_value = str(request.form['search_value'])
        # Check if we do either a string search or an exact match search.
        if search_name == '' and search_value != '':
            string_search = True
        else:
            string_search = False

        if not discoverer_mode_passed_in_url:
            # Only get discoverer_mode from the form if it has not been
            # passed in the url. This happens with the faceted search.
            # Then the discoverer_mode is in the form, not in the url.
            discoverer_mode = str(escape(request.form['search_discoverer_mode']))
            if discoverer_mode != 'details_view' \
               and discoverer_mode != 'person_view':
                discoverer_mode = DEFAULT_DISCOVERER_MODE

        faceted_name_list = request.form.getlist('faceted_name')
        faceted_category_list = request.form.getlist('faceted_category')
        html += find_nodes_in_ricgraph(name=search_name,
                                       category=search_category,
                                       value=search_value,
                                       use_contain_phrase=string_search,
                                       name_want=faceted_name_list,
                                       category_want=faceted_category_list,
                                       discoverer_mode=discoverer_mode)
    else:
        if key_value is None:
            html += search_form
        else:
            # Don't use escape() here. Then e.g. a search value that contains an '&', will be
            # translated to the HTML character '&amp;', which will not be found in the database.
            search_name = rcg.get_namepart_from_ricgraph_key(key=str(key_value))
            search_value = rcg.get_valuepart_from_ricgraph_key(key=str(key_value))
            html += find_nodes_in_ricgraph(name=search_name,
                                           value=search_value,
                                           discoverer_mode=discoverer_mode)
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

    discoverer_mode = str(escape(request.args.get('discoverer_mode')))
    if discoverer_mode != 'details_view' \
       and discoverer_mode != 'person_view':
        discoverer_mode = DEFAULT_DISCOVERER_MODE

    html = html_body_start
    if request.method == 'POST':
        # Do not use escape() for 'value', see note at beginning of this file.
        search_value = str(request.form['search_value'])
        html += find_nodes_in_ricgraph(value=search_value,
                                       use_contain_phrase=True,
                                       discoverer_mode=discoverer_mode)
    else:
        html += searchcontains_form

    html += html_body_end
    return html


@ricgraph_explorer.route('/searchdetails/', methods=['GET'])
def searchdetails() -> str:
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

    name = str(escape(request.args.get('name')))
    category = str(escape(request.args.get('category')))
    # Do not use escape() for 'value', see note at beginning of this file.
    value = str(request.args.get('value'))
    system1 = str(escape(request.args.get('system1')))
    system2 = str(escape(request.args.get('system2')))
    discoverer_mode = str(escape(request.args.get('discoverer_mode')))
    if discoverer_mode != 'details_view' \
            and discoverer_mode != 'person_view':
        discoverer_mode = DEFAULT_DISCOVERER_MODE
    overlap_mode = str(escape(request.args.get('overlap_mode')))
    if overlap_mode != 'thisnode' \
            and overlap_mode != 'neighbornodes':
        overlap_mode = 'thisnode'

    if system1 == 'None':
        system1 = ''
    if system2 == 'None':
        system2 = ''
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
            html += 'Ricgraph explorer could not find anything in searchdetails().'
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
            html += 'of the neighbor nodes of more than one node in searchdetails().'
            html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
            html += get_html_for_cardend()
            html += html_body_end
            return html

        node = result.first()
        if node['category'] == 'person':
            personroot = rcg.get_personroot_node(node)
            if personroot is None:
                html += get_html_for_cardstart()
                html += 'Ricgraph explorer found no "person-root" node in searchdetails().'
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
        html += get_you_searched_for_card(name=name,
                                          category=category,
                                          value=value,
                                          discoverer_mode=discoverer_mode,
                                          overlap_mode=overlap_mode,
                                          system1=system1,
                                          system2=system2)

    html += get_html_table_from_nodes(nodes=relevant_result,
                                      table_header='These records conform to your selection:',
                                      table_columns=DETAIL_COLUMNS,
                                      discoverer_mode=discoverer_mode)

    html += html_body_end
    return html


@ricgraph_explorer.route('/getoverlap/', methods=['GET'])
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

    name = str(escape(request.args.get('name')))
    category = str(escape(request.args.get('category')))
    # Do not use escape() for 'value', see note at beginning of this file.
    value = str(request.args.get('value'))
    discoverer_mode = str(escape(request.args.get('discoverer_mode')))
    if discoverer_mode != 'details_view' \
            and discoverer_mode != 'person_view':
        discoverer_mode = DEFAULT_DISCOVERER_MODE
    overlap_mode = str(escape(request.args.get('overlap_mode')))
    if overlap_mode != 'thisnode' \
            and overlap_mode != 'neighbornodes':
        overlap_mode = 'thisnode'

    html = html_body_start

    html += get_overlap_in_source_systems(name=name, category=category, value=value,
                                          discoverer_mode=discoverer_mode,
                                          overlap_mode=overlap_mode)

    html += html_body_end
    return html


# ##############################################################################
# This is where the work is done.
# ##############################################################################

def find_nodes_in_ricgraph(name: str = '', category: str = '', value: str = '',
                           use_contain_phrase: bool = False,
                           name_want: list = None, category_want: list = None,
                           discoverer_mode: str = '') -> str:
    """Find all nodes conforming to a query
    in Ricgraph and generate html for the result page.

    :param name: name of the nodes to find.
    :param category: category of the nodes to find.
    :param value: value of the nodes to find.
    :param use_contain_phrase: determines either case-sensitive & exact match (False),
      or case-insensitive & inexact match (True).
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
    graph = rcg.open_ricgraph()         # Should probably be done in a Session
    if graph is None:
        return 'Ricgraph could not be opened.'

    if name == '' and category == '' and value == '':
        html = get_html_for_cardstart()
        html += 'Ricgraph explorer could not find anything.'
        html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
        html += get_html_for_cardend()
        return html

    if discoverer_mode != 'details_view' and discoverer_mode != 'person_view':
        return 'Error, unknown discoverer_mode: ' + discoverer_mode + '. Please try again.'

    if name_want is None:
        name_want = []
    if category_want is None:
        category_want = []

    if use_contain_phrase:
        if len(value) < 3:
            html = get_html_for_cardstart()
            html += 'The search string should be at least three characters.'
            html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
            html += get_html_for_cardend()
            return html
        result = rcg.read_all_nodes_containing(value=value)
    else:
        result = rcg.read_all_nodes(name=name, category=category, value=value)

    if len(result) == 0:
        html = get_html_for_cardstart()
        html += 'Ricgraph explorer could not find anything.'
        html += '<br/><a href=' + url_for('index_html') + '>' + 'Please try again' + '</a>.'
        html += get_html_for_cardend()
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
        html = get_html_table_from_nodes(nodes=result,
                                         table_header=table_header,
                                         table_columns=columns,
                                         discoverer_mode=discoverer_mode)
        return html

    html = ''
    if discoverer_mode == 'details_view':
        html += get_you_searched_for_card(name=name,
                                          category=category,
                                          value=value,
                                          name_want=name_want,
                                          category_want=category_want,
                                          discoverer_mode=discoverer_mode)

    columns = ''
    node = result.first()
    if discoverer_mode == 'details_view':
        columns = DETAIL_COLUMNS
    elif discoverer_mode == 'person_view':
        columns = RESEARCH_OUTPUT_COLUMNS
    html += get_html_table_from_nodes(nodes=[node],
                                      table_header='Ricgraph explorer found node:',
                                      table_columns=columns,
                                      discoverer_mode=discoverer_mode)
    html += get_html_for_cardstart()
    html += 'You can '
    html += '<a href="' + url_for('getoverlap') + '?'
    html += urllib.parse.urlencode({'name': name, 'category': category, 'value': value,
                                    'discoverer_mode': discoverer_mode,
                                    'overlap_mode': 'neighbornodes'})
    html += '">'
    html += 'click here to do show the overlap in source systems for '
    html += 'the neighbor nodes of this node'
    html += '</a>.'
    html += get_html_for_cardend()

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


def get_you_searched_for_card(name: str = '', category: str = '', value: str = '',
                              name_want: list = None,
                              category_want: list = None,
                              discoverer_mode: str = '',
                              overlap_mode: str = '',
                              system1: str = '',
                              system2: str = '') -> str:
    """Get the html for the "You searched for" card.
    With the exception of name, category, and value, only search fields with are not
    empty will be shown.

    :param name: name.
    :param category: category.
    :param value: value.
    :param name_want: name_want.
    :param category_want: category_want.
    :param discoverer_mode: discoverer_mode.
    :param overlap_mode: overlap_mode.
    :param system1: system1.
    :param system2: system2.
    :return: html to be rendered.
    """
    if name_want is None:
        name_want = []
    if category_want is None:
        category_want = []

    html = get_html_for_cardstart()
    html += '<details><summary>Click for information about your search</summary><ul>'
    html += '<li>name: <i>"' + str(name) + '"</i>'
    html += '<li>category: <i>"' + str(category) + '"</i>'
    html += '<li>value: <i>"' + str(value) + '"</i>'
    if len(name_want) > 0:
        html += '<li>name_want: <i>"' + str(name_want) + '"</i>'
    if len(category_want) > 0:
        html += '<li>category_want: <i>"' + str(category_want) + '"</i>'
    if discoverer_mode != '':
        html += '<li>discoverer_mode: <i>"' + str(discoverer_mode) + '"</i>'
    if overlap_mode != '':
        html += '<li>overlap: <i>"' + str(overlap_mode) + '"</i>'
    if system1 != '':
        html += '<li>system1: <i>"' + str(system1) + '"</i>'
    if system2 != '':
        html += '<li>system2: <i>"' + str(system2) + '"</i>'
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
        item = '<a href=' + url_for('search')
        item += urllib.parse.quote(key) + '?'
        item += urllib.parse.urlencode({'discoverer_mode': discoverer_mode}) + '>'
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
        html += '<a href=' + url_for('search')
        html += urllib.parse.quote(key) + '?'
        html += urllib.parse.urlencode({'discoverer_mode': discoverer_mode}) + '>'
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
        item = '<a href=' + url_for('search')
        item += urllib.parse.quote(key) + '?'
        item += urllib.parse.urlencode({'discoverer_mode': discoverer_mode}) + '>'
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
    # An option might be to pass 'discoverer_mode' in the url, but that might confuse the user:
    # although in that case you can modify that mode, it will not work because other required
    # parameters have been passed as POST data and those are already gone.
    faceted_form += '<form method="post" action="' + url_for('search') + '">'
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
    faceted_form += '<input type="hidden" name="search_name" value="' + str(name) + '">'
    faceted_form += '<input type="hidden" name="search_category" value="' + str(category) + '">'
    faceted_form += '<input type="hidden" name="search_value" value="' + str(value) + '">'
    faceted_form += '<input type="hidden" name="search_discoverer_mode" value="' + str(discoverer_mode) + '">'
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
            html += '<a href="' + url_for('searchdetails') + '?'
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
            html += '<a href="' + url_for('searchdetails') + '?'
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
            html += '<a href="' + url_for('searchdetails') + '?'
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
                html += '<a href="' + url_for('searchdetails') + '?'
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
def get_html_table_from_nodes(nodes: Union[list, NodeMatch, None],
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

    html = get_html_for_cardstart()
    html += '<span style="float: left;">' + table_header + '</span>'
    if len(nodes) > MAX_ROWS_IN_TABLE:
        html += '<span style="float: right;">There are ' + str(len(nodes)) + ' rows in this table, showing first '
        html += str(MAX_ROWS_IN_TABLE) + '.</span>'
    elif len(nodes) >= 10:
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
    if faceted_html == '' \
       and discoverer_mode == 'details_view':
        table_header += '<br/>[Facet panel not shown because there is only one facet to show.]'

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
        html += '<td><a href=' + url_for('search')
        html += urllib.parse.quote(key) + '?'
        html += urllib.parse.urlencode({'discoverer_mode': discoverer_mode}) + '>'
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
