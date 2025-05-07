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


import json
import urllib.parse
from math import ceil, floor
from typing import Union
from ricgraph import (nodes_cache_nodelink_create,
                      create_ricgraph_key,
                      create_unique_string,
                      A_LARGE_NUMBER,
                      get_valuepart_from_ricgraph_value, get_additionalpart_from_ricgraph_value)
from ricgraph_explorer_constants import (DETAIL_COLUMNS, RESEARCH_OUTPUT_COLUMNS,
                                         MAX_ROWS_TO_EXPORT, ID_COLUMNS)
from ricgraph_explorer_utils import *


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
    if extra_url_parameters is None:
        extra_url_parameters = {}

    if len(nodes_list) == 0:
        return get_message('No neighbors found.')

    html = get_html_for_cardstart()
    names = []
    for node in nodes_list:
        key = node['_key']
        nodes_cache_nodelink_create(key=key, node=node)
        if node['name'] != 'FULL_NAME':
            continue
        key = create_ricgraph_key(name=node['name'], value=node['value'])
        value = get_valuepart_from_ricgraph_value(node['value'])
        # Don't get the 'additionalpart'.
        item = '<a href=' + url_for('optionspage') + '?'
        item += urllib.parse.urlencode({'key': key,
                                        'discoverer_mode': discoverer_mode}
                                       | extra_url_parameters) + '>'
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
        html += urllib.parse.urlencode({'key': key,
                                        'discoverer_mode': discoverer_mode}
                                       | extra_url_parameters) + '>'
        html += '<img src="' + node['url_main'] + '" alt="' + node['value']
        html += '" title="' + node['value'] + '" height="100"></a>'
    html += '</p>'

    skills = []
    research_areas = []
    expertise_areas = []

    # Get the nodes of interest. Using get_all_neighbor_nodes() is not efficient.
    for node in nodes_list:
        if node['category'] != 'competence':
            continue
        key = create_ricgraph_key(name=node['name'], value=node['value'])
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
           and node['name'] != 'FULL_NAME_ASCII' \
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

    table_id = create_unique_string(length=12)
    table_html = get_regular_table_worker(nodes_list=nodes_list,
                                          table_id=table_id,
                                          table_header=table_header,
                                          table_columns=table_columns,
                                          discoverer_mode=discoverer_mode,
                                          extra_url_parameters=extra_url_parameters)

    max_nr_items = int(extra_url_parameters['max_nr_items'])
    if max_nr_items == 0:
        max_nr_items = A_LARGE_NUMBER
    len_nodes_list = min(len(nodes_list), max_nr_items)
    max_nr_table_rows = int(extra_url_parameters['max_nr_table_rows'])
    if max_nr_table_rows == 0:
        max_nr_table_rows = len_nodes_list

    # This javascript code is for the pagination of the table.
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
        max_nr_items = A_LARGE_NUMBER
    if len_nodes_list > max_nr_items:
        # Remove elements from list following the max_nr_items'th.
        del nodes_list[max_nr_items:]
        len_nodes_list = max_nr_items

    nr_rows_in_table_message = ''
    max_nr_table_rows = int(extra_url_parameters['max_nr_table_rows'])
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
    html += '<div id="' + table_id + '-container">'     # <div> ends below.
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
                                      discoverer_mode=discoverer_mode,
                                      extra_url_parameters=extra_url_parameters)

        key = node['_key']
        nodes_cache_nodelink_create(key=key, node=node)

    html += '</tbody>'
    html += get_html_for_tableend(table_id=table_id)
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

    max_nr_items = int(extra_url_parameters['max_nr_items'])
    if max_nr_items == 0:
        max_nr_items = A_LARGE_NUMBER
    if len(neighbor_nodes) > max_nr_items:
        # Remove elements from list following the max_nr_items'th.
        del neighbor_nodes[max_nr_items:]

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

    table_id = create_unique_string(length=12)
    if extra_url_parameters is None:
        extra_url_parameters = {}
    if table_columns is None:
        if discoverer_mode == 'details_view':
            table_columns = DETAIL_COLUMNS
        else:
            table_columns = RESEARCH_OUTPUT_COLUMNS
    if tabs_on != 'name' and tabs_on != 'category':
        return get_message(message='get_tabbed_table(): Invalid value for "tabs_on": ' + tabs_on + '.')

    len_nodes_list = len(nodes_list)
    if len_nodes_list == 0:
        return get_message(table_header + '</br>Nothing found.')

    max_nr_items = int(extra_url_parameters['max_nr_items'])
    if max_nr_items == 0:
        max_nr_items = A_LARGE_NUMBER
    if len_nodes_list > max_nr_items:
        # Remove elements from list following the max_nr_items'th.
        del nodes_list[max_nr_items:]
        len_nodes_list = max_nr_items

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
        # Get the nodes of interest. Using get_all_neighbor_nodes() is not efficient.
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

    nr_rows_in_table_message = ''
    max_nr_table_rows = int(extra_url_parameters['max_nr_table_rows'])
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
    plot_name = 'myplot' + '_' + create_unique_string()

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
        key = create_ricgraph_key(name=node['name'], value=node['value'])
        if node['name'] == 'FULL_NAME' or node['name'] == 'FULL_NAME_ASCII':
            value = get_valuepart_from_ricgraph_value(node['value']) + ' ['
            value += get_additionalpart_from_ricgraph_value(node['value']) + ']'
        else:
            value = node['value']

        html += '<td><a href=' + url_for('optionspage') + '?'
        html += urllib.parse.urlencode({'key': key,
                                        'discoverer_mode': discoverer_mode}
                                       | extra_url_parameters) + '>'
        html += value + '</a></td>'
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


def get_html_for_tableend(table_id: str = '') -> str:
    """Get the html required for the end of a html table.
    Offer a possibility to export the table.

    :param table_id: the id of the table, required for exporting the
      table to csv, but not if you don't want it to be exported.
    :return: html to be rendered.
    """
    html = '</table>'
    if table_id == '':
        return html

    # This javascript code is to export the table with the given tableId as a CSV file.
    # Only maxRows are exported (as a kind of safety not to be able to export everything).
    javascript = '''<script>
                 function exportTableToCSV(tableId, maxRows) {
                     const rows = document.querySelectorAll(`#${tableId} tr`);
                     const rowsToExport = [];
                     // Always include the header row (first row), then up to (maxRows) rows total (header + data)
                     for (let i = 0; i < rows.length && i <= maxRows; i++) {
                         rowsToExport.push(rows[i]);
                     }
                     // For each row, get all cells (th or td), and for each cell:
                     // - Replace any double quotes with two double quotes (CSV escaping).
                     // - Enclose every cell value in double quotes.
                     // Join each cell in a row with commas, and join rows with newlines.
                     const csvContent = Array.from(rowsToExport).map(row =>
                         Array.from(row.children).map(cell =>
                             '"' + cell.innerText.replace(/"/g, '""') + '"'
                         ).join(',')
                     ).join('\\n');
                     const blob = new Blob([csvContent], {type: 'text/csv'});
                     // Create a hidden <a> element to trigger the download.
                     const link = document.createElement('a');
                     link.href = URL.createObjectURL(blob);
                     link.download = tableId + '.csv';
                     document.body.appendChild(link);
                     link.click();
                     document.body.removeChild(link);
                     URL.revokeObjectURL(link.href);
                 }
                 </script>'''

    html += f'''<div style="float:right;">
                    <a href="#" onclick="exportTableToCSV('{table_id}-container', {MAX_ROWS_TO_EXPORT}); return false;">
                        Export table to CSV file, at most {MAX_ROWS_TO_EXPORT} rows.</a>
                </div>'''
    return javascript + html
