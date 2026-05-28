# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
#
# Copyright (c) 2023 - 2026 Rik D.T. Janssen
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
# Ricgraph Explorer HTML related functions.
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, May 2026.
#
# ########################################################################


from typing import Tuple
from json import dumps
from pathlib import Path
from flask import request, url_for
from neo4j.graph import Node
from ricgraph import (create_unique_string,
                      get_year_range_text,
                      QueryParams, PageParams,
                      create_empty_query_params)
from ricgraph_explorer_constants import (RICGRAPH_NODEINFO,
                                         RICGRAPH_NODEINFO_INTERNAL,
                                         RICGRAPH_SYSTEMINFO,
                                         DISCOVERER_MODE_DETAILS,
                                         HISTOGRAM_MODE_COUNTS,
                                         observable_plot,
                                         spinner_style,
                                         button_style, button_width, button_width_half,
                                         font_family,
                                         form_button_on_one_line_flexspace_style,
                                         boxedcard_button_width)
from ricgraph_explorer_utils import get_global_str, get_global_list
from ricgraph_explorer_cypher import create_researchresult_histogram_cypher
from ricgraph_explorer_javascript import (get_spinner_javascript,
                                          get_html_for_histogram_javascript)



def get_page_footer() -> str:
    """Get the page footer.

    :return: HTML for the page footer.
    """
    page_footer = get_global_str(ricgraph_info=RICGRAPH_SYSTEMINFO,
                                 item='page_footer')
    return page_footer


def get_message(message: str, please_try_again: bool = True) -> str:
    """This function creates an HTML message containing 'message'.

    :param message: the message.
    :param please_try_again: if True, a link to try again will be added.
    :return: HTML to be rendered.
    """
    html = get_html_for_cardstart()
    html += message
    if please_try_again:
        html += '<br/><a href=' + url_for('homepage') + '>' + 'Please try again' + '</a>.'
    html += get_html_for_cardend()
    return html


def get_found_message(node: Node | None,
                      page_params: PageParams,
                      query_params: QueryParams,
                      table_header: str = '') -> str:
    """This function creates an HTML table containing 'node'.

    :param node: the node to put in the table.
    :param page_params: parameters related to the page passed in the URL.
    :param query_params: parameters related to the query passed in the URL.
    :param table_header: header for the table.
    :return: HTML to be rendered.
    """
    # To solve circular dependency on get_regular_table() which depends
    # on this file.
    from ricgraph_explorer_table import get_regular_table

    if table_header == '':
        header = 'Ricgraph Explorer found item:'
    else:
        header = table_header

    html = get_regular_table(nodes_list=[node],
                             page_params=page_params,
                             query_params=query_params,
                             table_header=header)
    return html


def get_page_title(title: str) -> str:
    """This function creates an HTML card with the page title.

    :param title: the message.
    :return: HTML to be rendered.
    """
    html = get_html_for_cardstart()
    html += '<h1 style="margin-top:0px; margin-bottom:0px">' + title + '</h1>'
    html += get_html_for_cardend()
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
    and 'input_spec' is a list that specifies how the HTML for the
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
    :return: HTML for the form.
    """
    if input_fields is None:
        input_fields = {}
    if hidden_fields is None:
        hidden_fields = {}
    form = explanation
    form += '<form method="get" action="' + url_for(endpoint=destination) + '">'
    for item in input_fields:
        label_id = create_unique_string(length=12)
        if input_fields[item][0] == 'list':
            if len(input_fields[item]) != 4:
                print('Wrong length for input field of type "list": ' +
                      str(len(input_fields[item])) + ', should be 4.')
                continue
            form += '<label for="' + label_id + '">' + item + '</label>'
            form += '<input id="' + label_id + '" class="w3-input w3-border" '
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
            form += '<label for="' + label_id + '">' + item + '</label>'
            form += '<input id="' + label_id + '" class="w3-input w3-border" '
            form += 'type="' + input_fields[item][0] + '" '     # 0: type of field ('text')
            form += 'name="' + input_fields[item][1] + '" '     # 1: name of field
            form += '>'

    for item in hidden_fields:
        if isinstance(hidden_fields[item], str) \
           or isinstance(hidden_fields[item], int):
            form += '<input type="hidden" name="' + item
            form += '" value="' + str(hidden_fields[item]) + '">'
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


def get_you_searched_for_card(page_params: PageParams,
                              query_params: QueryParams,
                              name_filter: str = 'None',
                              category_filter: str = 'None') -> str:
    """Get the HTML for the "You searched for" card.
    If you do not pass a str parameter, such as 'key', the default value will
    be 'None', which indicates that that value has not been passed.
    Its value will not be shown.
    That is different to passing a parameter 'key' with a value ''.
    Then that parameter will be shown.
    This makes it possible to pass a parameter with value '' and show that value.

    :param page_params: parameters related to the page passed in the URL.
    :param query_params: parameters related to the query passed in the URL.
    :param name_filter: name_filter.
    :param category_filter: category_filter.
    :return: HTML to be rendered.
    """
    if page_params['discoverer_mode'] != DISCOVERER_MODE_DETAILS:
        return ''

    html = '<details><summary class="uu-yellow" '
    # Use the same amount at both 'top' and 'margin-bottom'.
    html += 'style="position:relative; top:-3ex; text-align:right; margin-bottom:-3ex; float:right;">'
    html += 'Click for information about your search&nbsp;</summary>'
    html += get_html_for_cardstart()
    html += 'Your search consisted of these fields and values:'
    html += '<ul>'
    for item, value in page_params.items():
        html += '<li>page_params["' + item + '"]: <i>"' + str(value) + '"</i>'
    for item, value in query_params.items():
        html += '<li>query_params["' + item + '"]: <i>"' + str(value) + '"</i>'
    if name_filter != 'None':
        html += '<li>name_filter: <i>"' + str(name_filter) + '"</i>'
    if category_filter != 'None':
        html += '<li>category_filter: <i>"' + str(category_filter) + '"</i>'
    html += '</ul>'
    html += get_html_for_cardend()
    html += '</details>'
    return html


def get_html_for_boxedcard(header: str = '',
                           inner_html: str = '',
                           outer_html: str = '') -> str:
    """Get the HTML required for a boxed card. Such a card has
    a header and a body, the body can have a button. This button
    will appear outside of the body.

    :param header: The header of the boxed card.
    :param inner_html: The HTML for the body.
    :param outer_html: The HTML for the button.
    :return:
    """
    form = ''
    form += get_html_for_cardstart()
    form += '<div class="boxedcard">'

    form += '<div class="w3-card-4">'

    form += '<div class="w3-container uu-yellow">'
    form += '<b>' + header + '</b>'
    form += '</div>'

    form += inner_html

    form += '</div>'  # from '<div class="w3-card-4">'.

    if outer_html != '':
        form += '<br/>'
        form += outer_html

    form += '</div>'  # from '<div class="boxedcard">'.
    form += get_html_for_cardend()
    return form


def histogram_dict_to_list(histogram: dict,
                           reverse_sort_on_value: bool = True) -> list:
    """Convert a histogram in dict format to a list format.
    The dict should look like:
    {'DOI': 148, 'PURE_ID_PRESS_MEDIA': 102, 'PURE_ID_RESOUT': 183}.
    Then the resulting list will look like:
    [{'name': 'DOI', 'value': 148},
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
      Each histogram will look like
      [{'name': 'DOI', 'value': 148},
      {'name': 'PURE_ID_PRESS_MEDIA', 'value': 102},
      [etc.]].
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
    Each histogram needs to look like
    [{'name': 'DOI', 'value': 148},
    {'name': 'PURE_ID_PRESS_MEDIA', 'value': 102},
    [etc.]].

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


def get_html_for_histogramcard(histogram_list: list,
                               histogram_width: int = 0,
                               histogram_mode: str = HISTOGRAM_MODE_COUNTS,
                               histogram_title: str = ''):
    """This function creates a histogram using the Observable D3 and Observable Plot framework
    for data visualization. See https://d3js.org and https://observablehq.com/plot.

    :param histogram_list: A list of histogram data to be plotted in the histogram.
      Its elements need to look like
      [{'name': 'DOI', 'value': 148},
      {'name': 'PURE_ID_PRESS_MEDIA', 'value': 102},
      [etc.]].
      The histogram will be in the order as specified in the list.
    :param histogram_width: The width of the histogram, in pixels.
      If 0, then use the space available.
    :param histogram_mode: The mode of the histogram, either counts
      (HISTOGRAM_MODE_COUNTS), or percentages (HISTOGRAM_MODE_PERCENTAGES).
    :param histogram_title: The title of the histogram.
    :return: HTML to be rendered.
    """
    if len(histogram_list) == 0:
        message = 'Nothing to show, the histogram is empty.'
        return get_message(message=message)

    histogram_json = dumps(histogram_list)

    # The plot name should be unique, otherwise we get strange side effects.
    plot_name = 'myplot' + '_' + create_unique_string()

    body = '<div class="w3-container">'
    body += '<div id="' + plot_name + '"></div>'
    body += '</div>'

    javascript = get_html_for_histogram_javascript(histogram_json=histogram_json,
                                                   histogram_width=histogram_width,
                                                   histogram_mode=histogram_mode,
                                                   plot_name=plot_name)
    html = get_html_for_boxedcard(header=histogram_title,
                                  inner_html=observable_plot + body + javascript)
    return html


def get_html_for_facetcard(histogram: list,
                           url_field_name: str,
                           header:str,
                           show_counts: bool = True) -> str:
    """Do facet navigation in Ricgraph.
    The facets will be constructed based on 'url_field_name'.

    :param histogram: The histogram to construct the facets from.
      Its elements need to look like
      [{'name': 'DOI', 'value': 148},
      {'name': 'PURE_ID_PRESS_MEDIA', 'value': 102},
      [etc.]].
    :param url_field_name: The facet that is built will produce url_field_name
      in the URL.
    :param header: The header of the facet.
    :param show_counts: Whether to show a count after the facet item name.
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
        label = item['name']
        if show_counts:
            label += '&nbsp;<i>(' + str(item['value']) + ')</i>'
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


def get_html_for_yearcard(for_year_histogram: list = None,
                          header: str = '',
                          button_text: str = 'refresh') -> str:
    """Get the HTML required for a card that can be used to filter on
    year.

    :param for_year_histogram: If specified, the years in the list are
      shown in the selection boxes, otherwise the active years
      in Ricgraph. Its elements need to look like
      [{'name': 'DOI', 'value': 148},
      {'name': 'PURE_ID_PRESS_MEDIA', 'value': 102},
      [etc.]].
    :param header: The header to show before the input fields.
    :param button_text: The text to show on the 'submit' button.
    :return: HTML to be rendered.
    """
    if header == '':
        header = 'You can choose a different time period'

    if for_year_histogram is None:
        for_year_histogram = []

    if len(for_year_histogram) == 0:
        year_active_datalist = get_global_str(ricgraph_info=RICGRAPH_NODEINFO_INTERNAL,
                                              item='year_active_datalist')
    else:
        year_histogram = for_year_histogram.copy()
        year_histogram.sort(key=lambda x: x['name'].lower())
        year_active_datalist = '<datalist id="year_active_datalist">'
        for item in year_histogram:
            year_active_datalist += '<option value="' + item['name'] + '">'
        year_active_datalist += '</datalist>'

    # Get all current URL parameters using Flask's request. Note that
    # Flask’s request.args.to_dict(flat=False) always returns values as lists,
    # which we need. Assume the URL has ...&cat=abc&cat=def&..., then, with
    # 'flat=True', only the last 'cat' is returned.
    endpoint = str(request.endpoint)
    current_params = request.args.to_dict(flat=False)

    # Put all query parameters into hidden fields, except year_first/year_last,
    # because they will be the result of the form below.
    # Remember year_first/year_last (if present), to inform the user.
    hidden_fields = ''
    year_first = ''
    year_last = ''
    for key, values in current_params.items():
        if key == 'year_first':
            year_first = values[0]
            continue
        if key == 'year_last':
            year_last = values[0]
            continue
        # If it appears multiple times, emit each value.
        for val in values:
            hidden_fields += '<input type="hidden" name="'
            hidden_fields += key + '" value="' + val + '">'

    now_showing = 'Now showing '
    now_showing += get_year_range_text(year_first=year_first,
                                       year_last=year_last)
    now_showing += '.<br/>'

    form = '<div class="w3-container">'
    form += '<form method="get" action="' + url_for(endpoint=endpoint)
    form += '"' + form_button_on_one_line_flexspace_style + '>'

    form += now_showing
    form += hidden_fields

    form += '<div>'
    form += '<label for="year_first">specify the first year:</label>'
    form += '<input id="year_first" class="w3-input w3-border" list="year_active_datalist"'
    form += 'name=year_first autocomplete=off' + boxedcard_button_width + '>'
    form += '<div class="firefox-only">Click twice to get a dropdown list.</div>'
    form += str(year_active_datalist)
    form += '</div>'

    form += '<div>'
    form += '<label for="year_last">specify the last year:</label>'
    form += '<input id="year_last" class="w3-input w3-border" list="year_active_datalist"'
    form += 'name=year_last autocomplete=off' + boxedcard_button_width + '>'
    form += '<div class="firefox-only">Click twice to get a dropdown list.</div>'
    form += str(year_active_datalist)
    form += '</div>'

    form += '</div>'        # from '<div class="w3-container">'.

    button = '<input class="' + button_style + '"' + boxedcard_button_width
    button += 'type=submit value="' + button_text + '">'
    button += '</form>'
    html = get_html_for_boxedcard(header=header,
                                  inner_html=form,
                                  outer_html=button)
    return html


def get_html_for_checkboxcomponent(checkboxes: list,
                                   url_field_name: str,
                                   header:str) -> str:
    """Get HTML for a component that has a number of checkboxes.
    It will contain an "invert selection" button.

    :param checkboxes: The list of checkboxes to generate.
    :param url_field_name: The field name of the URL parameters where
      the result is set.
    :param header: The header of the group of checkboxes.
    :return: HTML to be rendered.
    """
    html = '<fieldset>'
    html += '<legend>'
    html += header
    html += '</legend>'
    html += '<div class="w3-row-padding w3-stretch">'
    for item in checkboxes:
        label_id = create_unique_string(length=12)
        html += '<div class="w3-col s12 m4">'
        html += '<input id="' + label_id + '" class="w3-check" '
        html += 'type="checkbox" name="' + url_field_name + '" value="'
        html += item + '" checked'
        html += '>'
        html += '<label for="' + label_id + '">&nbsp;' + item + '</label>'
        html += '</div>'
    html += '</div>'
    html += '<br/>'
    html += '<button type="button" class="w3-input' + button_style + '"' + button_width_half + '" '
    html += 'onclick="document.querySelectorAll(\'input[name=&quot;' + url_field_name
    html += '&quot;]\').forEach(cb=>cb.checked=!cb.checked)">'
    html += 'invert checkbox selection'
    html += '</button>'
    html += '</fieldset>'
    return html


def get_html_for_radiobuttoncomponent(radiobuttons: list,
                                      url_field_name: str,
                                      header:str) -> str:
    """Get HTML for a component that has a number of radiobuttons.
    The first element of the list will be checked.

    :param radiobuttons: The list of radiobuttons to generate.
      It needs to look like this:
      [{'button_id': 'first_button',
        'button_label': 'label of first button'},
       {'button_id': 'second_button',
        'button_label': 'label of second button'}]
    :param url_field_name: The field name of the URL parameters where
      the result is set. It is set by the value of 'button_id' that is chosen.
    :param header: The header of the group of radiobuttons.
    :return: HTML to be rendered.
    """
    html = '<fieldset>'
    html += '<legend>'
    html += header
    html += '</legend>'
    state = 'checked'
    for item in radiobuttons:
        button_id = item['button_id']
        button_label = item['button_label']
        html += '<input id="' + button_id + '" class="w3-radio" type="radio" '
        html += 'name="' + url_field_name + '" value="'
        html += button_id + '" ' + state + '>'
        html += ' ' + button_label
        html += '<br/>'
        if state == 'checked':
            state = ''
    html += '</fieldset>'
    return html


def get_spinner(message: str = '') -> str:
    """Get a spinner, indicating that an operation may take a long time.

    :param message: message to show below the spinner.
    :return: HTML to be rendered.
    """
    html = f'''
           <div id="ricgraph_spinner" class="ricgraph_spinner_overlay w3-center">
             <div class="{button_style}" style="width:30vw;">
               <span class="ricgraph_spinner"></span>
               <div style="margin-left: 10px; white-space:normal;">{message}</div>
             </div>
           </div>
           '''
    javascript = get_spinner_javascript()
    return spinner_style + html + javascript


def create_full_htmlpage(body_html: str) -> str:
    """Given some HTML, create an HTML page from it, and return it.
    The JavaScript files in 'body_html' that are expected to be
    in .../static/... are replaced with their contents.
    We do that, since we do not know whether the server that generates
    this page, is alive or externally accessible when the full HTML
    file is viewed by someone in its browser.

    :param body_html: the HTML to convert to a full HTML page.
    :return: the full HTML page.
    """
    # A non-zero margin looks better when we create a full HTML page.
    # Therefore, for 'figure' 'margin': this needs to be
    # (re)set, because it is set at 0px in create_sankey_diagram() and
    # create_chord_diagram().
    start_html = f'''
                 <!DOCTYPE html>
                 <meta charset="utf-8">
                 <style>body {{ font-family: {font_family}; }}
                        figure {{ margin: 1em 40px !important; }}</style>
                 <body>
                 '''

    result_html = body_html
    # Replace the references to JavaScript files in 'result_hmtl' with their
    # contents. Usually these JavaScript files should be gotten from the server
    # that generates this page. However, some may want just one a static
    # standalone HTML, therefore we just include the JavaScript.
    # You can find the JavaScript files here:
    # https://github.com/UtrechtUniversity/ricgraph/tree/main/ricgraph_explorer/static.
    js_map = [
        'static/d3.v7.min.js',
        'static/d3-chord.v3.min.js',
        'static/d3-scale-chromatic.v1.min.js',
        'static/d3-sankey.v0.12.3.min.js']

    for filename in js_map:
        js_text = Path(filename).read_text(encoding='utf-8')
        filename_with_slash = '/' + filename
        result_html = result_html.replace(
            f'<script src="{filename_with_slash}"></script>',
            f'<script>{js_text}</script>'
        )

    end_html = '</body>'
    full_html = start_html + result_html + end_html
    return full_html


def get_html_for_cardstart() -> str:
    """Get the HTML required for the start of a W3.CSS 'card'.
    W3.CSS is a modern, responsive, mobile first CSS framework.

    :return: HTML to be rendered.
    """
    html = '<section class="w3-container">'
    html += '<div class="w3-card-4">'
    html += '<div class="w3-container w3-responsive">'
    return html


def get_html_for_cardend() -> str:
    """Get the HTML required for the end of a W3.CSS 'card'.
    W3.CSS is a modern, responsive, mobile first CSS framework.

    :return: HTML to be rendered.
    """
    html = '</div>'
    html += '</div>'
    html += '</section>'
    return html


def get_html_for_cardline() -> str:
    """Get the HTML required for a yellow line. It is a W3.CSS 'card'
    filled with the color 'yellow'.

    :return: HTML to be rendered.
    """
    html = '<section class="w3-container">'
    html += '<div class="w3-card-4">'
    # Adjust the height of the line is padding-top + padding-bottom.
    html += '<div class="w3-container uu-yellow" style="padding-top:3px; padding-bottom:3px">'
    html += '</div>'
    html += '</div>'
    html += '</section>'
    return html
