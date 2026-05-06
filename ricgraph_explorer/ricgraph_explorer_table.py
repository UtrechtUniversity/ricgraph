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
from flask import url_for
from ricgraph import (nodes_cache_key_id_create,
                      create_ricgraph_key,
                      create_unique_string,
                      A_LARGE_NUMBER,
                      get_valuepart_from_ricgraph_value, get_additionalpart_from_ricgraph_value,
                      PERSON_CATEGORY_PERSON,
                      COMPETENCE_CATEGORY_COMPETENCE,
                      PERSON_NAME_PERSON_ROOT,
                      RICGRAPH_UNKNOWN,
                      PageParams, QueryParams)
from ricgraph_explorer_constants import (TABLE_DETAIL_COLUMNS,
                                         TABLE_RESEARCH_OUTPUT_COLUMNS,
                                         MAX_ROWS_TO_EXPORT, TABLE_ID_COLUMNS,
                                         RICGRAPH_NODEINFO,
                                         DISCOVERER_MODE_DETAILS,
                                         button_style)
from ricgraph_explorer_utils import (get_html_for_cardstart, get_html_for_cardend,
                                     get_global_list,
                                     get_message,
                                     merge_and_remove_empty)
from ricgraph_explorer_datavis import get_html_for_histogram
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
    len_nodes_list = len(nodes_list)
    if len_nodes_list == 0:
        return get_message(table_header + '</br>Nothing found.')

    max_nr_items = query_params['max_nr_items']
    if max_nr_items == 0:
        max_nr_items = A_LARGE_NUMBER
    if len_nodes_list > max_nr_items:
        # Remove elements from list following the max_nr_items'th.
        del nodes_list[max_nr_items:]
        len_nodes_list = max_nr_items

    nr_rows_in_table_message = ''
    max_nr_table_rows = page_params['max_nr_table_rows']
    if max_nr_table_rows == 0:
        max_nr_table_rows = min(len_nodes_list, max_nr_items)
    if 0 < max_nr_table_rows < len_nodes_list:
        nr_rows_in_table_message = 'There are ' + str(len_nodes_list) + ' rows in this table, showing pages of '
        nr_rows_in_table_message += str(max_nr_table_rows) + '.'
    elif len_nodes_list == max_nr_table_rows:
        # Special case: we have truncated the number of search results somewhere out of efficiency reasons,
        # so we have no idea how many search results there are.
        nr_rows_in_table_message = 'This table shows the first ' + str(max_nr_table_rows) + ' rows.'
    elif len_nodes_list >= 2:
        nr_rows_in_table_message = 'There are ' + str(len_nodes_list) + ' rows in this table.'

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
                                      table_id=table_id,
                                      table_columns=table_columns,
                                      table_page_num=table_page_num,
                                      url_parameters=
                                          merge_and_remove_empty(page_params=page_params,
                                                                 query_params=query_params))

        key = node['_key']
        nodes_cache_key_id_create(key=key, elementid=node.element_id)

    html += '</tbody>'
    html += get_html_for_tableend(table_id=table_id)
    html += '</div>'        # Ends </div> from above [A].
    html += nr_rows_in_table_message

    total_pages = ceil(min(len(nodes_list), max_nr_items) / max_nr_table_rows)
    pagination_html = create_table_pagination(total_pages, table_id)
    html += '<div class="w3-center" id="' + table_id + '-pagination-container">' + pagination_html + '</div>'
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

    faceted_html = get_facets_from_nodes(parent_node=parent_node,
                                         neighbor_nodes=neighbor_nodes,
                                         url_parameters=merge_and_remove_empty(page_params=page_params,
                                                                               query_params=query_params))
    table_html = get_regular_table(nodes_list=neighbor_nodes,
                                   page_params=page_params,
                                   query_params=query_params,
                                   table_header=table_header,
                                   table_columns=table_columns)
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

    max_nr_items = query_params['max_nr_items']
    if max_nr_items == 0:
        max_nr_items = A_LARGE_NUMBER
    if len_nodes_list > max_nr_items:
        # Remove elements from list following the max_nr_items'th.
        del nodes_list[max_nr_items:]
        len_nodes_list = max_nr_items

    name_histogram, category_histogram, access_histogram = \
        compute_histogramcards_name_category_access(nodes_list=nodes_list)

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

    histogram_sort = sorted(histogram, key=lambda x: histogram[x], reverse=True)

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

    nr_rows_in_table_message = ''
    max_nr_table_rows = page_params['max_nr_table_rows']
    if 0 < max_nr_table_rows < len_nodes_list:
        nr_rows_in_table_message = 'There are ' + str(len_nodes_list) + ' rows in this tabbed table, showing pages of '
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

    histogram_html = get_histogramcards_name_category_access(name_histogram=name_histogram,
                                                             category_histogram=category_histogram,
                                                             access_histogram=access_histogram)

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


def _get_part_of_facet_form(histogram: dict,
                            url_field_name: str,
                            title: str) -> str:
    """Helper function for get_facets_from_nodes() to avoid code
    duplication.

    :param histogram: Histogram
    :param url_field_name: The facet that is built will produce url_field_name
      in the URL.
    :param title: The title of the facet.
    :return: HTML to be rendered.
    """
    part_of_form = ''
    if len(histogram) == 1:
        # Get the first (and only) element in the dict, pass it as hidden field.
        name_key = str(list(histogram.keys())[0])
        part_of_form += '<input type="hidden" name="' + url_field_name
        part_of_form += '" value="' + name_key + '">'
    else:
        part_of_form += '<div class="w3-card-4">'
        part_of_form += '<div class="w3-container uu-yellow">'
        part_of_form += '<b>' + title + '</b>'
        part_of_form += '</div>'
        part_of_form += '<div class="w3-container" style="font-size: 90%;">'
        part_of_form += '<fieldset style="border:none; margin:0px; padding:0px;">'
        # For screen readers.
        part_of_form += '<legend style="display:none">' + title + '</legend>'

        # Sort a dict on value:
        # https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
        for bucket in sorted(histogram, key=lambda x: histogram[x], reverse=True):
            label_id = create_unique_string(length=12)
            label = bucket + '&nbsp;<i>(' + str(histogram[bucket]) + ')</i>'
            part_of_form += '<input id="' + label_id + '" class="w3-check" '
            part_of_form += 'type="checkbox" name="' + url_field_name + '" value="'
            part_of_form += bucket + '" checked>'
            part_of_form += '<label for="' + label_id + '">&nbsp;' + label + '</label><br/>'
        part_of_form += '</fieldset>'
        part_of_form += '</div>'
        part_of_form += '</div><br/>'
    return part_of_form


def compute_histogramcards_name_category_access(nodes_list: list) -> Tuple[dict, dict, dict]:
    """Computer the histograms for name, category, and access.

    :param nodes_list: The list of nodes the histogram is based on.
    :return: Three histograms, on 'name', 'category', and 'access'.
    """
    name_histogram = {}
    category_histogram = {}
    access_histogram = {}
    researchresult_category_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                                     item='researchresult_category_active')
    for node in nodes_list:
        if node['name'] not in name_histogram:
            name_histogram[node['name']] = 1
        else:
            name_histogram[node['name']] += 1

        if node['category'] not in category_histogram:
            category_histogram[node['category']] = 1
        else:
            category_histogram[node['category']] += 1

        if node['category'] in researchresult_category_active:
            # Only for research results.
            access_name = node['access']
            if access_name not in access_histogram:
                access_histogram[access_name] = 1
            else:
                access_histogram[access_name] += 1

    return name_histogram, category_histogram, access_histogram


def get_histogramcards_name_category_access(name_histogram: dict,
                                            category_histogram: dict,
                                            access_histogram: dict) -> str:
    """Get the histogram cards for name, category, and access.

    :param name_histogram: Histogram on 'name', or {} when there is none.
    :param category_histogram: Histogram on 'access', or {} when there is none.
    :param access_histogram: Histogram on 'access', or {} when there is none.
    :return: HTML to be rendered.
    """
    name_list = []
    category_list = []
    access_list = []
    if len(name_histogram) > 0:
        for bucket in sorted(name_histogram, key=lambda x: name_histogram[x], reverse=True):
            name_list.append({'name': bucket, 'value': name_histogram[bucket]})
    if len(category_histogram) > 0:
        for bucket in sorted(category_histogram, key=lambda x: category_histogram[x], reverse=True):
            category_list.append({'name': bucket, 'value': category_histogram[bucket]})
    if len(access_histogram) > 0:
        for bucket in sorted(access_histogram, key=lambda x: access_histogram[x], reverse=True):
            access_list.append({'name': bucket, 'value': access_histogram[bucket]})
    html = ''
    if len(name_list) > 1:
        html += get_html_for_cardstart()
        html += get_html_for_histogram(histogram_list=name_list,
                                       histogram_width=200,
                                       histogram_title='Histogram on "name"')
        html += get_html_for_cardend()
    if len(category_list) > 1:
        html += get_html_for_cardstart()
        html += get_html_for_histogram(histogram_list=category_list,
                                       histogram_width=200,
                                       histogram_title='Histogram on "category"')
        html += get_html_for_cardend()
    if len(access_list) > 1:
        html += get_html_for_cardstart()
        html += get_html_for_histogram(histogram_list=access_list,
                                       histogram_width=200,
                                       histogram_title='Histogram on "access"')
        html += get_html_for_cardend()
    return html


def get_facets_from_nodes(parent_node: Node | None,
                          neighbor_nodes: list,
                          url_parameters: dict) -> str:
    """Do facet navigation in Ricgraph.
    The facets will be constructed based on 'name' and 'category'.
    Facets chosen will be "caught" in function search().
    If there is only one facet (for either one or both), it will not be shown.

    :param parent_node: the parent of the nodes to construct the facets from.
    :param neighbor_nodes: the nodes to construct the facets from.
    :param url_parameters: parameters to be added to the url.
    :return: HTML to be rendered, or empty string ('') if faceted navigation is
      not useful because there is only one facet.
    """
    if parent_node is None:
        return ''
    if len(neighbor_nodes) == 0:
        return ''

    name_histogram, category_histogram, access_histogram = \
        compute_histogramcards_name_category_access(nodes_list=neighbor_nodes)

    if len(name_histogram) <= 1 and len(category_histogram) <= 1:
        # We have only one facet, so don't show the facet panel.
        return ''

    faceted_form = get_html_for_cardstart()
    faceted_form += '<div class="facetedform">'
    faceted_form += '<form method="get" action="' + url_for('resultspage') + '">'
    faceted_form += '<input type="hidden" name="key" value="' + str(parent_node['_key']) + '">'
    for item, value in url_parameters.items():
        if item in ['key', 'name_list', 'category_list']:
            # Skip. 'key' has been done above, 'name_list' and
            # 'category_list' will be done below.
            continue
        if isinstance(value, list):
            for one_value in value:
                faceted_form += '<input type="hidden" name="' + item
                faceted_form += '" value="' + str(one_value) + '">'
        else:
            faceted_form += '<input type="hidden" name="' + item
            faceted_form += '" value="' + str(value) + '">'
    faceted_form += _get_part_of_facet_form(histogram=name_histogram,
                                            url_field_name='name_list',
                                            title='Filter on "name"')
    faceted_form += _get_part_of_facet_form(histogram=category_histogram,
                                            url_field_name='category_list',
                                            title='Filter on "category"')
    # No facet on 'access'.

    # Send name, category and value as hidden fields to search().
    faceted_form += '<input class="w3-input' + button_style + '" style="width:8em;" type=submit value="refresh">'
    faceted_form += '</form>'
    faceted_form += '</div>'
    faceted_form += get_html_for_cardend()

    faceted_form += get_histogramcards_name_category_access(name_histogram=name_histogram,
                                                            category_histogram=category_histogram,
                                                            access_histogram=access_histogram)
    return faceted_form


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
                          table_id: str = '',
                          table_columns: list = None,
                          table_page_num: int = 1,
                          url_parameters: dict = None) -> str:
    """Get the HTML required for a row of an HTML table.

    :param node: the node to show in the table.
    :param table_id: the id of the table, required for pagination.
    :param table_columns: a list of columns to show in the table.
    :param table_page_num: the page number of the table.
    :param url_parameters: parameters to be added to the url.
    :return: HTML to be rendered.
    """
    if table_columns is None:
        table_columns = []
    if url_parameters is None:
        url_parameters = {}

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

            html += '<td><a href=' + url_for('optionspage') + '?'
            html += urlencode(url_parameters | {'key': key}) + '>'
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
