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
# Ricgraph Explorer general functions.
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, January 2023.
# Extended Rik D.T. Janssen, February, September 2023 to May 2025.
#
# ########################################################################


from typing import Union
from pandas import DataFrame
from flask import request, url_for
from markupsafe import escape
from neo4j.graph import Node
from ricgraph import create_unique_string, extract_organization_abbreviation
from ricgraph_explorer_constants import (button_style, button_width,
                                         font_family, d3_headers)


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


def get_message(message: str, please_try_again: bool = True) -> str:
    """This function creates a html message containing 'message'.

    :param message: the message.
    :param please_try_again: if True, a link to try again will be added.
    :return: html to be rendered.
    """
    html = get_html_for_cardstart()
    html += message
    if please_try_again:
        html += '<br/><a href=' + url_for('homepage') + '>' + 'Please try again' + '</a>.'
    html += get_html_for_cardend()
    return html


def get_found_message(node: Node,
                      table_header: str = '',
                      discoverer_mode: str = '',
                      extra_url_parameters: dict = None) -> str:
    """This function creates a html table containing 'node'.

    :param node: the node to put in the table.
    :param table_header: header for the table.
    :param discoverer_mode: as usual.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    # To solve circular dependency on get_regular_table() which depends
    # on this file.
    from ricgraph_explorer_table import get_regular_table

    if extra_url_parameters is None:
        extra_url_parameters = {}

    if table_header == '':
        header = 'Ricgraph Explorer found item:'
    else:
        header = table_header

    html = get_regular_table(nodes_list=[node],
                             table_header=header,
                             discoverer_mode=discoverer_mode,
                             extra_url_parameters=extra_url_parameters)
    return html


def get_page_title(title: str) -> str:
    """This function creates a html card with the page title.

    :param title: the message.
    :return: html to be rendered.
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
    and 'input_spec' is a list that specifies how the html for the
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
    :return: html for the form.
    """
    if input_fields is None:
        input_fields = {}
    if hidden_fields is None:
        hidden_fields = {}
    form = explanation
    form += '<form method="get" action="/' + destination + '/">'
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


def get_you_searched_for_card(name: str = 'None', category: str = 'None', value: str = 'None',
                              key: str = 'None',
                              name_list: list = None,
                              category_list: list = None,
                              view_mode: str = 'None',
                              discoverer_mode: str = 'None',
                              overlap_mode: str = 'None',
                              system1: str = 'None',
                              system2: str = 'None',
                              source_system: str = 'None',
                              name_filter: str = 'None',
                              category_filter: str = 'None',
                              extra_url_parameters: dict = None) -> str:
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
    :param name_list: name_list.
    :param category_list: category_list.
    :param view_mode: view_mode.
    :param discoverer_mode: discoverer_mode.
    :param overlap_mode: overlap_mode.
    :param system1: system1.
    :param system2: system2.
    :param source_system: source_system.
    :param name_filter: name_filter.
    :param category_filter: category_filter.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    if name_list is None:
        name_list = []
    if category_list is None:
        category_list = []
    if extra_url_parameters is None:
        extra_url_parameters = {}

    html = '<details><summary class="uu-yellow" '
    # Use the same amount at both 'top' and 'margin-bottom'.
    html += 'style="position:relative; top:-3ex; text-align:right; margin-bottom:-3ex; float:right;">'
    html += 'Click for information about your search&nbsp;</summary>'
    html += get_html_for_cardstart()
    html += 'Your search consisted of these fields and values:'
    html += '<ul>'
    if name != 'None':
        html += '<li>name: <i>"' + str(name) + '"</i>'
    if category != 'None':
        html += '<li>category: <i>"' + str(category) + '"</i>'
    if value != 'None':
        html += '<li>value: <i>"' + str(value) + '"</i>'
    if key != 'None':
        html += '<li>key: <i>"' + str(key) + '"</i>'
    if len(name_list) > 0:
        html += '<li>name_list: <i>"' + str(name_list) + '"</i>'
    if len(category_list) > 0:
        html += '<li>category_list: <i>"' + str(category_list) + '"</i>'
    if view_mode != 'None':
        html += '<li>view_mode: <i>"' + str(view_mode) + '"</i>'
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
    for item in extra_url_parameters:
        html += '<li>extra_url_parameters["' + item + '"]: <i>"' + extra_url_parameters[item] + '"</i>'
    html += '</ul>'
    html += get_html_for_cardend()
    html += '</details>'
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


# ##############################################################################
# DataFrame related functions for diagrams.
# ##############################################################################
def remove_hierarchical_orgs(df: DataFrame,
                             orgs_with_hierarchies: DataFrame,
                             org_to_keep: str) -> Union[DataFrame, None]:
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
        org_abbr = row.org_abbreviation
        orgs_name = row.org_fullname
        if org_abbr == org_keep_abbr:
            # Already done.
            continue
        df = remove_one_hierarchical_org(df=df,
                                         orgs_to_keep=orgs_name,
                                         orgs_to_drop_pattern=org_abbr)
        if df is None or df.empty:
            return None
    return df


def remove_one_hierarchical_org(df: DataFrame,
                                orgs_to_keep: Union[str, list],
                                orgs_to_drop_pattern: str) -> Union[DataFrame, None]:
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


def create_htmlpage(body_html: str, filename: str) -> None:
    """Given some HTML, create an HTML page from it,
    and write it to a file.

    :param body_html: the HTML to convert to a full HTML page.
    :param filename: the filename to save the html to.
    :return: None.
    """
    # global font_family, d3_headers

    start_html = f'''
                 <!DOCTYPE html>
                 <meta charset="utf-8">
                 <style>body {{ font-family: {font_family}; }}</style>
                 <body>
                 {d3_headers}
                 '''

    end_html = '</body>'

    full_html = start_html + body_html + end_html

    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_html)
    print('Diagram saved to file: ' + filename + '.')
    print('')
    return
