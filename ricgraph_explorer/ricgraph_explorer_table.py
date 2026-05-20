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
# Ricgraph Explorer functions related to tables.
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Ricgraph Explorer uses W3.CSS, a modern, responsive, mobile first CSS framework.
# See https://www.w3schools.com/w3css/default.asp.
#
# ########################################################################
#
# For table sorting. Ricgraph Explorer uses sorttable.js.
# It is copied from https://www.kryogenix.org/code/browser/sorttable
# on February 1, 2023. At that link, you'll find a how-to. It is licensed under X11-MIT.
# It is renamed to ricgraph_sorttable.js since it has a small modification
# related to case-insensitive sorting. The script is included in html_body_end.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, January 2023.
# Extended Rik D.T. Janssen, February, September 2023 to May 2025.
#
# ########################################################################


from urllib.parse import urlencode
from math import ceil, floor
from typing import Tuple
from neo4j.graph import Node
from flask import request, url_for
from ricgraph import (nodes_cache_key_id_create,
                      create_ricgraph_key,
                      create_unique_string,
                      A_LARGE_NUMBER,
                      get_valuepart_from_ricgraph_value,
                      get_additionalpart_from_ricgraph_value,
                      PERSON_CATEGORY_PERSON,
                      COMPETENCE_CATEGORY_COMPETENCE,
                      PERSON_NAME_PERSON_ROOT,
                      RICGRAPH_UNKNOWN,
                      PageParams, QueryParams,
                      create_empty_page_params,
                      create_empty_query_params)
from ricgraph_explorer_cypher import create_researchresult_histogram_cypher
from ricgraph_explorer_constants import (TABLE_DETAIL_COLUMNS,
                                         TABLE_RESEARCH_OUTPUT_COLUMNS,
                                         MAX_ROWS_TO_EXPORT, TABLE_ID_COLUMNS,
                                         RICGRAPH_NODEINFO,
                                         DISCOVERER_MODE_DETAILS,
                                         button_style,
                                         boxedcard_button_width)
from ricgraph_explorer_utils import (get_html_for_cardstart, get_html_for_cardend,
                                     get_global_list,
                                     get_message,
                                     merge_and_remove_empty,
                                     get_html_for_yearcard,
                                     get_html_for_boxedcard)
from ricgraph_explorer_datavis import get_html_for_histogramcard
from ricgraph_explorer_javascript import (get_regular_table_javascript, get_tabbed_table_javascript,
                                          get_html_for_tableend_javascript)


def view_personal_information(nodes_list: list,
                              page_params: PageParams,
                              query_params: QueryParams) -> str:
    """Create a person page of the node.
    This page shows the name variants, a photo (if present),
    and a list of competences (if present). Then a table with the other identities.
    'discover_mode' will always be 'person_view', but we still pass it for future
    extensions.

    :param nodes_list: the nodes to create a table from.
    :param page_params: parameters related to the page passed in the URL.
    :param query_params: parameters related to the query passed in the URL.
    :return: HTML to be rendered.
    """
    if len(nodes_list) == 0:
        return get_message('No neighbors found.')

    html = get_html_for_cardstart()
    names = []
    url_parameters = merge_and_remove_empty(page_params=page_params,
                                            query_params=query_params)
    for node in nodes_list:
        key = node['_key']
        nodes_cache_key_id_create(key=key, elementid=node.element_id)
        if node['name'] != 'FULL_NAME':
            continue
        key = create_ricgraph_key(name=node['name'], value=node['value'])
        value = get_valuepart_from_ricgraph_value(node['value'])
        # Don't get the 'additionalpart'.
        item = '<a href=' + url_for('optionspage') + '?'
        item += urlencode(url_parameters |
                          {'key': key}) + '>'
        item += value + '</a>'
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
        key = create_ricgraph_key(name=node['name'], value=node['value'])
        html += '&nbsp;&nbsp;'
        html += '<a href=' + url_for('optionspage') + '?'
        html += urlencode(url_parameters |
                          {'key': key}) + '>'
        html += '<img src="' + node['url_main'] + '" alt="' + node['value']
        html += '" title="' + node['value'] + '" height="100"></a>'
    html += '</p>'

    skills = []
    research_areas = []
    expertise_areas = []

    # Get the nodes of interest. Using get_all_neighbor_nodes() is not efficient.
    for node in nodes_list:
        if node['category'] != COMPETENCE_CATEGORY_COMPETENCE:
            continue
        key = create_ricgraph_key(name=node['name'], value=node['value'])
        item = '<a href=' + url_for('optionspage') + '?'
        item += urlencode(url_parameters |
                          {'key': key}) + '>'
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
        if node['category'] != PERSON_CATEGORY_PERSON:
            continue
        if node['name'] != 'FULL_NAME' \
           and node['name'] != 'FULL_NAME_ASCII' \
           and node['name'] !=  PERSON_NAME_PERSON_ROOT \
           and node['name'] != 'PHOTO_ID':
            id_nodes.append(node)
    html += get_tabbed_table(nodes_list=id_nodes,
                             page_params=page_params,
                             query_params=query_params,
                             table_header='These are the identities related to this person:',
                             table_columns=TABLE_ID_COLUMNS,
                             tabs_on='name')
    return html


# ##############################################################################
# The HTML for the regular, tabbed and faceted tables is generated here.
# ##############################################################################
def create_table_pagination(total_pages, table_id) -> str:
    """Generates w3.css pagination controls for a table.

    :param total_pages: the total pages in the table.
    :param table_id: the id of the table.
    :return: HTML to be rendered.
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
                      page_params: PageParams,
                      query_params: QueryParams,
                      table_header: str = '',
                      table_columns: list = None) -> str:
    """Create a paginated HTML table for all nodes in the list.

    :param nodes_list: the nodes to create a table from.
    :param page_params: parameters related to the page passed in the URL.
    :param query_params: parameters related to the query passed in the URL.
    :param table_header: the HTML to show above the table.
    :param table_columns: a list of columns to show in the table.
    :return: HTML to be rendered.
    """
    table_id = create_unique_string(length=12)
    table_html = get_regular_table_worker(nodes_list=nodes_list,
                                          page_params=page_params,
                                          query_params=query_params,
                                          table_id=table_id,
                                          table_header=table_header,
                                          table_columns=table_columns)

    max_nr_items = query_params['max_nr_items']
    if max_nr_items == 0:
        max_nr_items = A_LARGE_NUMBER
    len_nodes_list = min(len(nodes_list), max_nr_items)
    max_nr_table_rows = page_params['max_nr_table_rows']
    if max_nr_table_rows == 0:
        max_nr_table_rows = len_nodes_list

    javascript = get_regular_table_javascript(table_id=table_id,
                                              len_nodes_list=len_nodes_list,
                                              max_nr_table_rows=max_nr_table_rows)
    return javascript + table_html


def get_regular_table_worker(nodes_list: list,
                             page_params: PageParams,
                             query_params: QueryParams,
                             table_id: str = '',
                             table_header: str = '',
                             table_columns: list = None) -> str:
    """Create an HTML table for all nodes in the list.
    Here the real work is done.

    :param nodes_list: the nodes to create a table from.
    :param page_params: parameters related to the page passed in the URL.
    :param query_params: parameters related to the query passed in the URL.
    :param table_id: the id of the table, required for pagination.
    :param table_header: the HTML to show above the table.
    :param table_columns: a list of columns to show in the table.
    :return: HTML to be rendered.
    """
    if table_columns is None:
        if page_params['discoverer_mode'] == DISCOVERER_MODE_DETAILS:
            table_columns = TABLE_DETAIL_COLUMNS
        else:
            table_columns = TABLE_RESEARCH_OUTPUT_COLUMNS
    if nodes_list is None or (len_nodes_list := len(nodes_list)) == 0:
        return get_message(table_header + '</br>Nothing found.')

    nr_rows_in_table_message = ''
    max_nr_items = query_params['max_nr_items']
    if max_nr_items == 0 or len_nodes_list < max_nr_items:
        # We show everything.
        nr_rows_in_table_message += 'There are ' + str(len_nodes_list)
        nr_rows_in_table_message += ' rows in this table'
    else:
        if len_nodes_list > max_nr_items:
            # Remove elements from list following the max_nr_items'th.
            del nodes_list[max_nr_items:]
            len_nodes_list = max_nr_items
        # We cannot show everything.
        nr_rows_in_table_message += 'This table shows the first ' + str(len_nodes_list)
        nr_rows_in_table_message += ' rows'

    max_nr_table_rows = page_params['max_nr_table_rows']
    if max_nr_table_rows == 0 or len_nodes_list <= max_nr_table_rows:
        # All rows fit on one page of the table.
        nr_rows_in_table_message += '.'
        max_nr_table_rows = len_nodes_list
    else:
        # We will need more than one page for the table.
        nr_rows_in_table_message += ', showing pages of '
        nr_rows_in_table_message += str(max_nr_table_rows) + '.'

    if len_nodes_list == 1:
        # No message above the table.
        nr_rows_in_table_message = ''

    # Clean the URL to be passed in the 'value' field of the table.
    # Seeing from where we have come here, this URL may have any parameters in it,
    # but to continue we only need to pass a few URL parameters.
    # key, name, value will be set in get_html_for_tablerow().
    page_params_cleaned = create_empty_page_params()
    page_params_cleaned['discoverer_mode'] = page_params['discoverer_mode']
    page_params_cleaned['max_nr_table_rows'] = page_params['max_nr_table_rows']
    page_params_cleaned['view_mode'] = page_params['view_mode']
    query_params_cleaned = create_empty_query_params()
    query_params_cleaned['max_nr_items'] = query_params['max_nr_items']

    html = get_html_for_cardstart()
    html += '<span style="float:left;">' + table_header + '</span>'
    html += '<span style="float:right;">' + nr_rows_in_table_message + '</span>'
    html += '<div id="' + table_id + '-container">'     # <div> ends below [A].
    html += get_html_for_tablestart()
    html += '<thead>'
    html += get_html_for_tableheader(table_columns=table_columns)
    html += '</thead>'
    html += '<tbody>'
    for count, node in enumerate(nodes_list):
        table_page_num = floor(count / max_nr_table_rows) + 1
        html += get_html_for_tablerow(node=node,
                                      page_params=page_params_cleaned,
                                      query_params=query_params_cleaned,
                                      table_id=table_id,
                                      table_columns=table_columns,
                                      table_page_num=table_page_num)
        key = node['_key']
        nodes_cache_key_id_create(key=key, elementid=node.element_id)

    html += '</tbody>'
    html += get_html_for_tableend(table_id=table_id)
    html += '</div>'        # Ends </div> from above [A].
    html += nr_rows_in_table_message

    total_pages = ceil(len_nodes_list / max_nr_table_rows)
    pagination_html = create_table_pagination(total_pages, table_id)
    html += '<div class="w3-center" id="' + table_id + '-pagination-container">'
    html += pagination_html + '</div>'
    html += get_html_for_cardend()
    return html


def get_faceted_table(parent_node: Node,
                      neighbor_nodes: list,
                      page_params: PageParams,
                      query_params: QueryParams,
                      table_header: str = '',
                      table_columns: list = None) -> str:
    """Create a faceted HTML table for all neighbor_nodes in the list.

    :param parent_node: the parent of the nodes to construct the facets from.
    :param neighbor_nodes: the neighbor_nodes to create a table from.
    :param page_params: parameters related to the page passed in the URL.
    :param query_params: parameters related to the query passed in the URL.
    :param table_header: the HTML to show above the table.
    :param table_columns: a list of columns to show in the table.
    :return: HTML to be rendered.
    """
    if table_columns is None:
        if page_params['discoverer_mode'] == DISCOVERER_MODE_DETAILS:
            table_columns = TABLE_DETAIL_COLUMNS
        else:
            table_columns = TABLE_RESEARCH_OUTPUT_COLUMNS
    if parent_node is None or \
       neighbor_nodes is None or len(neighbor_nodes) == 0:
        return get_message(table_header + '</br>Nothing found.')

    max_nr_items = query_params['max_nr_items']
    if max_nr_items == 0:
        max_nr_items = A_LARGE_NUMBER
    if len(neighbor_nodes) > max_nr_items:
        # Remove elements from list following the max_nr_items'th.
        del neighbor_nodes[max_nr_items:]

    (name_histogram, category_histogram, year_histogram,
     license_histogram, access_histogram) = \
        compute_histogramcards(nodes_list=neighbor_nodes)

    # Divide space between panels and table.
    html = '<div class="w3-row-padding w3-stretch">'
    html += '<div class="w3-col s12 m3">'
    html += get_html_for_yearcard()
    html += get_html_for_facetcard(histogram=name_histogram,
                                   url_field_name='name_list',
                                   header='Filter on "name"')
    html += get_html_for_facetcard(histogram=category_histogram,
                                   url_field_name='category_list',
                                   header='Filter on "category"')
    html += get_histogramcards(name_histogram=name_histogram,
                               category_histogram=category_histogram,
                               year_histogram=year_histogram,
                               license_histogram=license_histogram,
                               access_histogram=access_histogram)
    html += '</div>'
    html += '<div class="w3-col s12 m9">'
    html += get_regular_table(nodes_list=neighbor_nodes,
                              page_params=page_params,
                              query_params=query_params,
                              table_header=table_header,
                              table_columns=table_columns)
    html += '</div>'
    html += '</div>'

    return html


def get_tabbed_table(nodes_list: list,
                     page_params: PageParams,
                     query_params: QueryParams,
                     table_header: str = '',
                     table_columns: list = None,
                     tabs_on: str = '') -> str:
    """Create an HTML table with tabs for all nodes in the list.

    :param nodes_list: the nodes to create a table from.
    :param page_params: parameters related to the page passed in the URL.
    :param query_params: parameters related to the query passed in the URL.
    :param table_header: the HTML to show above the table.
    :param table_columns: a list of columns to show in the table.
    :param tabs_on: the name of the field in Ricgraph you'd like to have tabs on.
    :return: HTML to be rendered.
    """

    table_id = create_unique_string(length=12)
    if table_columns is None:
        if page_params['discoverer_mode'] == DISCOVERER_MODE_DETAILS:
            table_columns = TABLE_DETAIL_COLUMNS
        else:
            table_columns = TABLE_RESEARCH_OUTPUT_COLUMNS
    if tabs_on != 'name' and tabs_on != 'category':
        return get_message(message='get_tabbed_table(): Invalid value for "tabs_on": ' + tabs_on + '.')

    if nodes_list is None or (len_nodes_list := len(nodes_list)) == 0:
        return get_message(table_header + '</br>Nothing found.')

    nr_rows_in_table_message = ''
    max_nr_items = query_params['max_nr_items']
    if max_nr_items == 0 or len_nodes_list < max_nr_items:
        # We show everything.
        nr_rows_in_table_message += 'There are ' + str(len_nodes_list)
        nr_rows_in_table_message += ' rows in this table.'
    else:
        if len_nodes_list > max_nr_items:
            # Remove elements from list following the max_nr_items'th.
            del nodes_list[max_nr_items:]
            len_nodes_list = max_nr_items
        # We cannot show everything.
        nr_rows_in_table_message += 'This table shows the first ' + str(len_nodes_list)
        nr_rows_in_table_message += ' rows.'

    if len_nodes_list == 1:
        # No message above the table.
        nr_rows_in_table_message = ''

    (name_histogram, category_histogram, year_histogram,
     license_histogram, access_histogram) = \
        compute_histogramcards(nodes_list=nodes_list)

    if tabs_on == 'name':
        histogram = name_histogram.copy()
    else:
        histogram = category_histogram.copy()

    if len(histogram) == 1:
        # Note: len(histogram) cannot be 0, that has been caught above.
        # If we have only one thing to show tabs on, we do a regular table.
        html = get_regular_table(nodes_list=nodes_list,
                                 page_params=page_params,
                                 query_params=query_params,
                                 table_header=table_header,
                                 table_columns=table_columns)
        return html

    first_iteration = True
    tab_names_html = '<div class="w3-bar uu-yellow">'
    for item in histogram:
        tab_name = item['name']
        tab_text = tab_name + '&nbsp;<i>(' + str(item['value']) + ')</i>'
        tab_names_html += f'<button class="w3-bar-item w3-button tablink {table_id}'

        if first_iteration:
            tab_names_html += ' uu-orange'
            first_iteration = False
        else:
            tab_names_html += ''
        tab_names_html += f'" onclick="openTab_{table_id}(event,\'{tab_name}\',\'{table_id}\')">{tab_text}</button>'
    tab_names_html += '</div>'

    first_iteration = True
    tab_contents_html = ''
    for item in histogram:
        tab_name = item['name']
        tab_contents_html += f'<div id="{tab_name}" class="w3-container w3-border tabitem {table_id}"'
        if first_iteration:
            tab_contents_html += ''
            first_iteration = False
        else:
            tab_contents_html += ' style="display:none"'
        tab_contents_html += '>'
        nodes_of_tab_name = []
        # Get the nodes of interest. Using get_all_neighbor_nodes() is not efficient.
        for node in nodes_list:
            if node[tabs_on] == tab_name:
                nodes_of_tab_name.append(node)
        table_title = 'List of ' + tab_name + 's:'
        table = get_regular_table(nodes_list=nodes_of_tab_name,
                                  page_params=page_params,
                                  query_params=query_params,
                                  table_header=table_title,
                                  table_columns=table_columns)
        tab_contents_html += table
        tab_contents_html += '</div>'

    tab_javascript = get_tabbed_table_javascript(table_id=table_id)

    # Divide space between panels and table.
    html = '<div class="w3-row-padding w3-stretch" >'
    html += '<div class="w3-col s12 m3">'
    if len(year_histogram) > 0:
        html += get_html_for_yearcard()
    html += get_histogramcards(name_histogram=name_histogram,
                               category_histogram=category_histogram,
                               year_histogram=year_histogram,
                               license_histogram=license_histogram,
                               access_histogram=access_histogram)
    html += '</div>'
    html += '<div class="w3-col s12 m9">'
    html += get_html_for_cardstart()
    html += '<span style="float:left;">' + table_header + '</span>'
    html += '<span style="float:right;">' + nr_rows_in_table_message + '</span>'
    html += tab_names_html + tab_contents_html + tab_javascript
    html += nr_rows_in_table_message
    html += get_html_for_cardend()
    html += '</div>'
    html += '</div>'

    return html


def histogram_dict_to_list(histogram: dict,
                           reverse_sort_on_value: bool = True) -> list:
    """Convert a histogram in dict format to a list format.
    The dict should look like:
    {'DOI': 148, 'PURE_ID_PRESS_MEDIA': 102, 'PURE_ID_RESOUT': 183}.
    Then the list will look like:
    having elements like [{'name': 'DOI', 'value': 148},
    {'name': 'PURE_ID_PRESS_MEDIA', 'value': 102},
    {'name': 'PURE_ID_RESOUT', 'value': 183}].

    :param histogram: The dict with the histogram.
    :param reverse_sort_on_value: If True: reverse sort on the 'value' field.
      If two items have the same value for 'value', the one that is
      lexicographically first will be first in the resulting list.
      Otherwise, sort on 'name'.
    :return: The sorted list.
    """
    if reverse_sort_on_value:
        sorted_list = [
            {'name': k, 'value': v}
            for k, v in sorted(histogram.items(), key=lambda kv: (-kv[1], kv[0]))
        ]
    else:
        sorted_list = [
            {'name': k, 'value': v}
            for k, v in sorted(histogram.items(), key=lambda kv: kv[0].lower())
        ]
    return sorted_list


def compute_histogramcards(nodes_list: list = None,
                           query_params: QueryParams = None,
                           reverse_sort_on_value: bool = True,
                           remove_zero_values: bool = True) -> Tuple[list, list, list, list, list]:
    """Compute histograms for name, category, year, license, and access.
    This can be done either on the basis of a 'nodes_list', or on
    a Cypher query, based on query_params['key'].
    The latter will be much faster, because the graph database will compute
    the histograms.

    :param nodes_list: The list of nodes the histogram are based on.
    :param query_params: parameters related to the query passed in the URL.
    :param reverse_sort_on_value: If True: reverse sort on the 'value' field.
      If two items have the same value for 'value', the one that is
      lexicographically first will be first in the resulting list.
      Otherwise, sort on 'name'.
    :param remove_zero_values: If True, remove values that are 0 from
      the resulting histogram list.
    :return: Five histograms, on 'name', 'category', 'year',
      'license', and 'access'.
      Each histogram elements looks like [{'name': 'DOI', 'value': 148},
      {'name': 'PURE_ID_PRESS_MEDIA', 'value': 102}, [etc] ].
    """
    if nodes_list is None:
        nodes_list = []
    if query_params is None:
        query_params = create_empty_query_params()

    name_histogram = {}
    category_histogram = {}
    year_histogram = {}
    license_histogram = {}
    access_histogram = {}
    if len(nodes_list) > 0:
        # Use a dict for intermediate storage because it is fast.
        researchresult_category_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                                         item='researchresult_category_active')
        for node in nodes_list:
            name_histogram[node['name']] = name_histogram.get(node['name'], 0) + 1
            category_histogram[node['category']] = category_histogram.get(node['category'], 0) + 1
            if node['category'] in researchresult_category_active:
                # Only for research results.
                year_histogram[node['year']] = year_histogram.get(node['year'], 0) + 1
                license_histogram[node['license']] = license_histogram.get(node['license'], 0) + 1
                access_histogram[node['access']] = access_histogram.get(node['access'], 0) + 1
    else:
        (name_histogram, category_histogram, year_histogram,
         license_histogram, access_histogram) = \
            create_researchresult_histogram_cypher(query_params=query_params)

    name_histogram_list = histogram_dict_to_list(name_histogram,
                                                 reverse_sort_on_value=reverse_sort_on_value)
    category_histogram_list = histogram_dict_to_list(category_histogram,
                                                     reverse_sort_on_value=reverse_sort_on_value)
    year_histogram_list = histogram_dict_to_list(year_histogram,
                                                 reverse_sort_on_value=reverse_sort_on_value)
    license_histogram_list = histogram_dict_to_list(license_histogram,
                                                    reverse_sort_on_value=reverse_sort_on_value)
    access_histogram_list = histogram_dict_to_list(access_histogram,
                                                   reverse_sort_on_value=reverse_sort_on_value)
    if remove_zero_values:
        name_histogram_list = [x for x in name_histogram_list if x.get('value') != 0]
        category_histogram_list = [x for x in category_histogram_list if x.get('value') != 0]
        year_histogram_list = [x for x in year_histogram_list if x.get('value') != 0]
        license_histogram_list = [x for x in license_histogram_list if x.get('value') != 0]
        access_histogram_list = [x for x in access_histogram_list if x.get('value') != 0]

    return (name_histogram_list, category_histogram_list,
            year_histogram_list, license_histogram_list, access_histogram_list)


def get_histogramcards(name_histogram: list,
                       category_histogram: list,
                       year_histogram: list,
                       license_histogram: list,
                       access_histogram: list) -> str:
    """Get the histograms for name, category, year, license, and access.
    Each histogram elements looks like [{'name': 'DOI', 'value': 148},
    {'name': 'PURE_ID_PRESS_MEDIA', 'value': 102}, [etc] ].

    :param name_histogram: Histogram on 'name', or [] when there is none.
    :param category_histogram: Histogram on 'access', or [] when there is none.
    :param year_histogram: Histogram on 'year', or [] when there is none.
    :param license_histogram: Histogram on 'license', or [] when there is none.
    :param access_histogram: Histogram on 'access', or [] when there is none.
    :return: HTML to be rendered.
    """
    histograms = [
        ('name', name_histogram),
        ('category', category_histogram),
        ('year', year_histogram),
        ('license', license_histogram),
        ('access', access_histogram),
    ]
    html = ''
    for title, histogram in histograms:
        if len(histogram) > 0:
            html += get_html_for_histogramcard(histogram_list=histogram,
                                               histogram_title='Histogram on "' + title + '"')
    return html


def get_html_for_facetcard(histogram: list,
                           url_field_name: str,
                           header:str) -> str:
    """Do facet navigation in Ricgraph.
    The facets will be constructed based on 'url_field_name'.

    :param histogram: The histogram to construct the facets from.
      Its elements look like [{'name': 'DOI', 'value': 148},
      {'name': 'PURE_ID_PRESS_MEDIA', 'value': 102}, [etc] ].
    :param url_field_name: The facet that is built will produce url_field_name
      in the URL.
    :param header: The header of the facet.
    :return: HTML to be rendered, or '' if there is no facet.
    """
    if len(histogram) == 0:
        # There is nothing to show.
        return ''

    hidden_fields = ''

    # Get all current URL parameters using Flask's request. Note that
    # Flask’s request.args.to_dict(flat=False) always returns values as lists,
    # which we need. Assume the URL has ...&cat=abc&cat=def&..., then, with
    # 'flat=True', only the last 'cat' is returned.
    endpoint = str(request.endpoint)
    current_params = request.args.to_dict(flat=False)

    # Put all query parameters into hidden fields, except url_field_name,
    # because it will be the result of the form below.
    for key, values in current_params.items():
        if key == url_field_name:
            continue
        # If it appears multiple times, emit each value.
        for val in values:
            hidden_fields += '<input type="hidden" name="'
            hidden_fields += key + '" value="' + val + '">'

    additional_hidden_field = ''
    form = '<div class="w3-container" style="font-size: 90%;">'
    form += '<form method="get" action="' + url_for(endpoint=endpoint) + '">'

    form += hidden_fields

    form += '<fieldset style="border:none; margin:0px; padding:0px;">'
    # For screen readers.
    form += '<legend style="display:none">' + header + '</legend>'
    for item in histogram:
        label_id = create_unique_string(length=12)
        label = item['name'] + '&nbsp;<i>(' + str(item['value']) + ')</i>'
        form += '<input id="' + label_id + '" class="w3-check" '
        form += 'type="checkbox" name="' + url_field_name + '" value="'
        form += item['name'] + '" checked'
        if len(histogram) == 1:
            form += ' disabled'
            # If a checkbox is disabled, it is not added to the URL, so
            # we need to add it explicitly by using a hidden field.
            additional_hidden_field += '<input type="hidden" name="' + url_field_name
            additional_hidden_field += '" value="' + str(item['name']) + '">'
        form += '>'
        form += '<label for="' + label_id + '">&nbsp;' + label + '</label><br/>'
    form += '</fieldset>'

    if len(histogram) == 1:
        form += additional_hidden_field

    form += '</div>'        # from '<div class="w3-container">'.

    button = '<input class="w3-input' + button_style + '"'
    button += boxedcard_button_width + '" type=submit value="refresh">'
    button += '</form>'
    html = get_html_for_boxedcard(header=header,
                                  inner_html=form,
                                  outer_html=button)
    return html


# ##############################################################################
# The general HTML for the tables is generated here.
# ##############################################################################
def get_html_for_tablestart() -> str:
    """Get the HTML required for the start of an HTML table.

    :return: HTML to be rendered.
    """
    html = '<table class="sortable w3-table">'
    return html


def get_html_for_tableheader(table_columns: list = None) -> str:
    """Get the HTML required for the header of an HTML table.

    :param table_columns: a list of columns to show in the table.
    :return: HTML to be rendered.
    """
    if table_columns is None:
        table_columns = []
    html = '<tr class="uu-yellow">'
    for column in table_columns:
        if column == 'value':
            html += '<th class=sorttable_alpha">' + column + '</th>'
        elif column in ['url_main', 'url_other', '_source', '_history']:
            html += '<th class="sorttable_nosort">' + column + '</th>'
        else:
            html += '<th>' + column + '</th>'
    html += '</tr>'
    return html


def get_html_for_tablerow(node: Node,
                          page_params: PageParams,
                          query_params: QueryParams,
                          table_id: str = '',
                          table_columns: list = None,
                          table_page_num: int = 1) -> str:
    """Get the HTML required for a row of an HTML table.

    :param node: the node to show in the table.
    :param page_params: parameters related to the page passed in the URL.
    :param query_params: parameters related to the query passed in the URL.
    :param table_id: the id of the table, required for pagination.
    :param table_columns: a list of columns to show in the table.
    :param table_page_num: the page number of the table.
    :return: HTML to be rendered.
    """
    if table_columns is None:
        table_columns = []

    # Show only the first page initially.
    display_style = '' if table_page_num == 1 else 'display: none;'
    html = '<tr class="table-' + table_id + '-page-' + str(table_page_num) + ' '
    html += 'item" style="' + display_style + '">'

    for column in table_columns:
        if column == 'value':
            key = create_ricgraph_key(name=node['name'], value=node['value'])
            if node['name'] == 'FULL_NAME' or node['name'] == 'FULL_NAME_ASCII':
                value = get_valuepart_from_ricgraph_value(node['value']) + ' ['
                value += get_additionalpart_from_ricgraph_value(node['value']) + ']'
            else:
                value = node['value']

            query_params['key'] = key
            query_params['name'] = node['name']
            query_params['value'] = node['value']
            url_parameters = merge_and_remove_empty(page_params=page_params,
                                                    query_params=query_params)
            html += '<td><a href=' + url_for('optionspage') + '?'
            html += urlencode(url_parameters) + '>'
            html += value + '</a></td>'
        elif column in ['url_main', 'url_other']:
            if node[column] == RICGRAPH_UNKNOWN:
                html += '<td></td>'
            else:
                html += '<td><a href=' + node[column] + ' target="_blank">'
                html += column + ' link</a></td>'
        elif column in ['_history', '_source']:
            if isinstance(node[column], str):
                html += '<td>' + node[column] + '</td>'
            else:
                if column == '_history':
                    html += '<td><details><summary>Click for history</summary><ul>'
                    html += '<li>Node labels: ' + str(list(node.labels)) + '</li>'
                else:
                    html += '<td><ul>'
                for item in node[column]:
                    html += '<li>' + item + '</li>'
                if column == '_history':
                    html += '</ul></details></td>'
                else:
                    html += '</ul></td>'
        elif column == 'comment':
            if isinstance(node[column], str):
                if node[column] == RICGRAPH_UNKNOWN:
                    html += '<td><ul>'
                else:
                    html += '<td width=30%>' + node[column] + '</td>'
            else:
                if node['name'] == PERSON_NAME_PERSON_ROOT \
                        and isinstance(node[column], list):
                    # If this is a person-root node, we put the FULL_NAME(s) in the comment column,
                    # for easier browsing.
                    html += '<td><ul>'
                    for cached_name in node[column]:
                        html += '<li>' + cached_name + '</li>'
                    html += '</ul></td>'
                else:
                    html += '<td width=30%>' + str(node[column]) + '</td>'
        else:
            if node[column] == RICGRAPH_UNKNOWN:
                html += '<td></td>'
            else:
                html += '<td>' + node[column] + '</td>'
    html += '</tr>'
    return html


def get_html_for_tableend(table_id: str = '') -> str:
    """Get the HTML required for the end of an HTML table.
    Offer a possibility to export the table.

    :param table_id: the id of the table, required for exporting the
      table to csv, but not if you don't want it to be exported.
    :return: HTML to be rendered.
    """
    html = '</table>'
    if table_id == '':
        return html

    html += f'''
            <div style="float:right;">
                <a href="#" onclick="exportTableToCSV('{table_id}-container', {MAX_ROWS_TO_EXPORT}); return false;">
                   Export table to CSV file, at most {MAX_ROWS_TO_EXPORT} rows.</a>
            </div>
            '''

    figure_filename = 'ricgraph_explorer_export_' + table_id + '.csv'
    javascript = get_html_for_tableend_javascript(figure_filename=figure_filename)
    return javascript + html
