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
# Ricgraph Explorer general functions.
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, January 2023.
# Extended Rik D.T. Janssen, February, September 2023 to May 2025.
# Extended Rik D.T. Janssen, October, November 2025, March 2026.
#
# ########################################################################


from pandas import DataFrame
from pathlib import Path
from flask import request, url_for
from markupsafe import escape
from neo4j.graph import Node
from ricgraph import (create_unique_string,
                      extract_organization_abbreviation,
                      QueryParams, PageParams)
from ricgraph_explorer_constants import (RICGRAPH_CACHEINFO,
                                         RICGRAPH_HARVESTINFO,
                                         RICGRAPH_NODEINFO,
                                         RICGRAPH_NODEINFO_INTERNAL,
                                         RICGRAPH_SYSTEMINFO,
                                         HISTOGRAM_MODE_PERCENTAGES,
                                         OSL_PROFILE_MODE_GROUPS,
                                         OVERLAP_MODE_SOURCE_ALL,
                                         MAX_ITEMS_TO_RETURN, MAX_ROWS_IN_TABLE,
                                         spinner_style,
                                         button_style, button_width,
                                         font_family,
                                         form_button_on_one_line_flexspace_style,
                                         form_button_on_one_line_width)
from ricgraph_explorer_init import (get_ricgraph_explorer_global,
                                    collect_ricgraph_cacheinfo)
from ricgraph_explorer_javascript import get_spinner_javascript


# ##############################################################################
# Various global functions.
# ##############################################################################
def get_global_list(ricgraph_info: str, item: str) -> list:
    """Safely retrieve an entry from a Ricgraph info structure.
    A list return value is expected.

    :param ricgraph_info: The Ricgraph info structure.
    :param item: The element in that structure.
    :return: the value of the list, or [] if it does not exist.
    """
    if ricgraph_info == RICGRAPH_CACHEINFO:
        # First update the information about the cache.
        collect_ricgraph_cacheinfo()
    info = get_ricgraph_explorer_global(name=ricgraph_info)
    if info is None:
        return []
    value = info.get(item, [])
    return value


def get_global_str(ricgraph_info: str, item: str) -> str:
    """Safely retrieve an entry from a Ricgraph info structure.
    A str return value is expected.

    :param ricgraph_info: The Ricgraph info structure.
    :param item: The element in that structure.
    :return: the value of the str, or '' if it does not exist.
    """
    if ricgraph_info == RICGRAPH_CACHEINFO:
        # First update the information about the cache.
        collect_ricgraph_cacheinfo()
    info = get_ricgraph_explorer_global(name=ricgraph_info)
    if info is None:
        return ''
    value = info.get(item, '')
    return value


def get_global_dataframe(ricgraph_info: str, item: str) -> DataFrame | None:
    """Safely retrieve an entry from a Ricgraph info structure.
    A DataFrame return value is expected.

    :param ricgraph_info: The Ricgraph info structure.
    :param item: The element in that structure.
    :return: the value of the DataFrame, or None if it does not exist.
    """
    if ricgraph_info == RICGRAPH_CACHEINFO:
        # First update the information about the cache.
        collect_ricgraph_cacheinfo()
    info = get_ricgraph_explorer_global(name=ricgraph_info)
    if info is None:
        return None
    value = info.get(item, '')
    return DataFrame(value)


def get_page_footer() -> str:
    """Get the page footer.

    :return: HTML for the page footer.
    """
    page_footer = get_global_str(ricgraph_info=RICGRAPH_SYSTEMINFO,
                                 item='page_footer')
    return page_footer


# ##############################################################################
# URL related functions.
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


def get_url_parameter_list(parameter: str,
                           allowed_values: list = None,
                           default_value: str = '',
                           use_escape: bool = True) -> list:
    """Get a URL parameter list and its values.

    :param parameter: name of the URL parameter.
    :param allowed_values: allowed values of the URL parameter, if any.
    :param default_value: the default value, if any.
    :param use_escape: whether to call escape() or not for the values of the URL
        parameter. We should do this for safety, however, we cannot always do
        this, because for some cases we cannot search correctly in Ricgraph.
        For example, if we would use escape() for a URL parameter that contains an '&',
        such as in 'Department: Research & Data Management Services',
        that '&' will be translated to the HTML character '&amp;', which then
        will not be found in Ricgraph.
    :return: the list of values of the URL parameter.
    """
    if allowed_values is None:
        allowed_values = []

    raw_value_list = request.args.getlist(parameter)
    if use_escape:
        value_list = [str(escape(item)) for item in raw_value_list]
    else:
        value_list = raw_value_list.copy()

    if len(allowed_values) > 0:
        value_list = list(set(value_list) & set(allowed_values))

    if len(value_list) == 0:
        if default_value == '':
            value_list = []
        else:
            value_list = [default_value]
    return value_list


def get_url_query_params() -> QueryParams:
    """Construct a dict that contains all possible parameters
    for a Cypher query from the URL. If the URL does not
    contain a certain parameter, insert its default value,
    so that we can always assume that every key in the dict
    exists.
    If you add fields, add them to
    ricgraph/ricgraph_utils.py/create_empty_query_params() too.

    :return: The dict with all URL parameters related to a query.
    """
    max_nr_items = get_url_parameter_value(parameter='max_nr_items',
                                           default_value=str(MAX_ITEMS_TO_RETURN))
    if not max_nr_items.isnumeric():
        # This also catches negative numbers, they contain a '-' and are not numeric.
        # See https://www.w3schools.com/python/ref_string_isnumeric.asp.
        max_nr_items = str(MAX_ITEMS_TO_RETURN)

    name_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                  item='name_active')
    category_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                      item='category_active')
    access_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                    item='access_active')
    source_active = get_global_list(ricgraph_info=RICGRAPH_HARVESTINFO,
                                    item='source_active')

    # The rationale behind the following is as follows:
    # 1. Only allow 'active' values for a property of type list.
    # 2. Then, if the list passed in the URL param has the same length
    #    as the list of active values, the two list must be the same.
    # 3. If (2) is the case, then, for Cypher queries, it is not
    #    necessary to filter on that property using a WHERE, since
    #    any value for that property in the graph database is
    #    already taken into account. Change the list to [], so
    #    it will not be added to the Cypher query (so the query
    #    is faster).
    name_list = get_url_parameter_list(parameter='name_list',
                                       allowed_values=name_active)
    if len(name_active) == len(name_list):
        name_list = []
    category_list = get_url_parameter_list(parameter='category_list',
                                           allowed_values=category_active)
    if len(name_active) == len(category_list):
        category_list = []
    access = get_url_parameter_list(parameter='access',
                                    allowed_values=access_active)
    if len(access_active) == len(access):
        # Note that access_active may also contain '', for unknown.
        access = []

    query_params: QueryParams = {
        'key': get_url_parameter_value(parameter='key', use_escape=False),
        'name': get_url_parameter_value(parameter='name',
                                        allowed_values=name_active),
        'name_list': name_list,
        'category': get_url_parameter_value(parameter='category',
                                            allowed_values=category_active),
        'category_list': category_list,
        'value': get_url_parameter_value(parameter='value', use_escape=False),
        'year_first': get_url_parameter_value(parameter='year_first'),
        'year_last': get_url_parameter_value(parameter='year_last'),
        'access': access,
        'source_system': get_url_parameter_value(parameter='source_system',
                                                 allowed_values=source_active),
        'source_system2': get_url_parameter_value(parameter='source_system2',
                                                  allowed_values=source_active + OVERLAP_MODE_SOURCE_ALL),
        'start_orgs': get_url_parameter_value(parameter='start_orgs', use_escape=False),
        'collab_orgs': get_url_parameter_value(parameter='collab_orgs', use_escape=False),
        'max_nr_items': int(max_nr_items)
    }
    return query_params


def get_url_page_params() -> PageParams:
    """Construct a dict that contains all possible parameters
    for a page from the URL. If the URL does not
    contain a certain parameter, insert its default value,
    so that we can always assume that every key in the dict
    exists.
    If you add fields, add them to
    ricgraph/ricgraph_utils.py/create_empty_page_params() too.

    :return: The dict with all URL parameters related to a page.
    """
    max_nr_table_rows = get_url_parameter_value(parameter='max_nr_table_rows',
                                                default_value=str(MAX_ROWS_IN_TABLE))
    if not max_nr_table_rows.isnumeric():
        # This also catches negative numbers, they contain a '-' and are not numeric.
        # See https://www.w3schools.com/python/ref_string_isnumeric.asp.
        max_nr_table_rows = str(MAX_ROWS_IN_TABLE)

    page_params: PageParams = {
        'collab_mode': get_url_parameter_value(parameter='collab_mode',
                                               allowed_values=get_global_list(
                                                   ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                   item='collab_mode_all')),
        'discoverer_mode': get_url_parameter_value(parameter='discoverer_mode',
                                                   allowed_values=get_global_list(
                                                      ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                      item='discoverer_mode_all'),
                                                   default_value=get_global_str(
                                                      ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                      item='discoverer_mode_default')),
        'histogram_mode': get_url_parameter_value(parameter='histogram_mode',
                                                  allowed_values=get_global_list(
                                                      ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                      item='histogram_mode_all'),
                                                  default_value=HISTOGRAM_MODE_PERCENTAGES),
        'max_nr_table_rows': int(max_nr_table_rows),
        'origin': get_url_parameter_value(parameter='origin',
                                          allowed_values=get_global_list(
                                              ricgraph_info=RICGRAPH_SYSTEMINFO,
                                              item='origin_button_all')),
        'oslprofile_mode': get_url_parameter_value(parameter='oslprofile_mode',
                                                   allowed_values=get_global_list(
                                                      ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                      item='osl_profile_mode_all'),
                                                   default_value=OSL_PROFILE_MODE_GROUPS),
        'overlap_mode': get_url_parameter_value(parameter='overlap_mode',
                                                allowed_values=get_global_list(
                                                    ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                    item='overlap_mode_all')),
        'search_mode': get_url_parameter_value(parameter='search_mode',
                                               allowed_values=get_global_list(
                                                   ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                   item='search_mode_all'),
                                               default_value=get_global_str(ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                                           item='search_mode_default')),
        'view_mode': get_url_parameter_value(parameter='view_mode',
                                             allowed_values=get_global_list(
                                                 ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                 item='view_mode_all'))
    }
    return page_params


def merge_and_remove_empty(page_params: PageParams,
                           query_params: QueryParams) -> dict:
    """Merges two TypedDicts 'page_params' and 'query_params',
    and removes empty values (as in '' or []) from  the result.
    To be used before constructing a URL, to prevent lots of empty
    values in the URL (as in ...&year_first=&year_last=&...).

    :param page_params: The PageParams dict.
    :param query_params: The QueryParams dict.
    :return: The dict that has no empty values.
    """
    merge = {**page_params, **query_params}
    non_empty = {}
    for key in merge:
        if merge[key] not in ['', []]:
            non_empty[key] = merge[key]
    return non_empty


# ##############################################################################
# HTML utility functions.
# ##############################################################################
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


def get_html_for_yearcard(show_as_card: bool = True,
                          message: str = '',
                          button_text: str = 'refresh') -> str:
    """Get the HTML required for a card that can be used to filter on
    year.

    :param show_as_card: If True, show as card, otherwise show inline.
    :param message: The message to show before the input fields.
    :param button_text: The text to show on the 'submit' button.
    :return: HTML to be rendered.
    """
    year_active_datalist = get_global_str(ricgraph_info=RICGRAPH_NODEINFO_INTERNAL,
                                          item='year_active_datalist')
    hidden_fields = ''
    if message == '':
        message = 'You can choose a different time period for the research results:'

    # Get all current URL parameters using Flask's request. Note that
    # Flask’s request.args.to_dict(flat=False) always returns values as lists,
    # which we need. Assume the URL has ...&cat=abc&cat=def&..., then, with
    # 'flat=True', only the last 'cat' is returned.
    endpoint = str(request.endpoint)
    current_params = request.args.to_dict(flat=False)

    # Put all query parameters into hidden fields, except year_first/year_last,
    # because they will be the result of the form below.
    for key, values in current_params.items():
        if key == 'year_first' or key == 'year_last':
            continue
        # If it appears multiple times, emit each value.
        for val in values:
            hidden_fields += '<input type="hidden" name="'
            hidden_fields += key + '" value="' + val + '">'

    form = ''
    if show_as_card:
        form += get_html_for_cardstart()
    form += message
    form += '<br/>'
    form += '<form method="get" action="' + url_for(endpoint=endpoint)
    form += '"' + form_button_on_one_line_flexspace_style + '>'

    form += hidden_fields

    form += '<div' + form_button_on_one_line_width + '>'
    form += '<label for="year_first">specify the first year:</label>'
    form += '<input id="year_first" class="w3-input w3-border" list="year_active_datalist"'
    form += 'name=year_first autocomplete=off' + form_button_on_one_line_width + '>'
    form += '<div class="firefox-only">Click twice to get a dropdown list.</div>'
    form += str(year_active_datalist)
    form += '</div>'

    form += '<div' + form_button_on_one_line_width + '>'
    form += '<label for="year_last">specify the last year:</label>'
    form += '<input id="year_last" class="w3-input w3-border" list="year_active_datalist"'
    form += 'name=year_last autocomplete=off' + form_button_on_one_line_width + '>'
    form += '<div class="firefox-only">Click twice to get a dropdown list.</div>'
    form += str(year_active_datalist)
    form += '</div>'

    form += '<input class="' + button_style + '"' + form_button_on_one_line_width
    form += 'type=submit value="' + button_text + '">'
    form += '</form>'
    if show_as_card:
        form += get_html_for_cardend()
    return form


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


# ##############################################################################
# The HTML for the W3CSS cards is generated here.
# ##############################################################################
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


# ##############################################################################
# DataFrame related functions for diagrams.
# ##############################################################################
def remove_hierarchical_orgs(df: DataFrame | None,
                             orgs_with_hierarchies: DataFrame,
                             org_to_keep: str) -> DataFrame | None:
    """
    This function removes hierarchical orgs from a DataFrame, leaving the
    top level organization only, for the organizations in orgs_with_hierarchies,
    except for org_to_keep (it will be kept).
    This is useful if you specifically query for 'org_to_keep'.

    :param df: DataFrame.
    :param orgs_with_hierarchies: DataFrame with hierarchical orgs.
    :param org_to_keep: if the row and column name starts with
      an element of this list or with this string, do NOT remove it.
      For now, this function only works for str, not list.
    :return: modified DataFrame, or None on error.
    """
    org_keep_abbr = extract_organization_abbreviation(org_name=org_to_keep)

    # No need to check for df is None, will be done in remove_one_hierarchical_org().
    df = remove_one_hierarchical_org(df=df,
                                     orgs_to_keep=org_to_keep,
                                     orgs_to_drop_pattern=org_keep_abbr)
    if df is None or df.empty:
        return None

    if orgs_with_hierarchies is None or df.empty:
        # Nothing more to be done.
        return df

    for row in orgs_with_hierarchies.itertuples(index=False):
        org_abbr = str(row.org_abbreviation)
        orgs_name = str(row.org_fullname)
        if org_abbr == org_keep_abbr:
            # Already done.
            continue
        df = remove_one_hierarchical_org(df=df,
                                         orgs_to_keep=orgs_name,
                                         orgs_to_drop_pattern=org_abbr)
        if df is None or df.empty:
            return None
    return df


def remove_one_hierarchical_org(df: DataFrame | None,
                                orgs_to_keep: str | list,
                                orgs_to_drop_pattern: str) -> DataFrame | None:
    """
    Remove rows and columns from DataFrame whose
    index or column starts with orgs_to_drop_pattern,
    except for organizations that are in orgs_to_keep.
    Note that this can be done because all (sub-)organizations of a person
    are linked to that person in the graph.
    This means that the column of the top level organization contains
    counts for its sub-organizations. So the sub-organizations can be removed
    without loosing data.

    :param df: DataFrame.
    :param orgs_to_drop_pattern: a string pattern that is matched
      to index and column name, if it starts with this string, remove it.
    :param orgs_to_keep: if the index and column name starts with
      an element of this list or with this string, do NOT remove it.
    :return: modified DataFrame, or None on error.
    """
    if df is None or df.empty:
        print('remove_one_hierarchical_org(): Error, DataFrame is empty.')
        return None

    # Define keep-check() functions based on orgs_to_keep type.
    if isinstance(orgs_to_keep, str):
        def should_keep(name):
            return name.startswith(orgs_to_keep)
    elif isinstance(orgs_to_keep, list):
        def should_keep(name):
            return name in orgs_to_keep
    else:
        print('remove_one_hierarchical_org(): Error, unknown type for parameter "orgs_to_keep".')
        return None

    # Find rows and columns to drop
    rows_to_drop = [idx for idx in df.index
                    if idx.startswith(orgs_to_drop_pattern) and not should_keep(idx)]
    cols_to_drop = [col for col in df.columns
                    if col.startswith(orgs_to_drop_pattern) and not should_keep(col)]

    df_copy = df.copy(deep=True)
    result = df_copy.drop(index=rows_to_drop, columns=cols_to_drop)
    return result
