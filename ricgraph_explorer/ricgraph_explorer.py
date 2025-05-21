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
# This file is Ricgraph Explorer, a web based tool for Ricgraph.
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# If you expose Ricgraph Explorer to the outside world, at least use
# a web server such as Apache combined with a WSGI and ASGI server.
# Please read the documentation to learn how to do that, and to find
# example configuration files.
#
# ########################################################################
#
# Ricgraph Explorer uses W3.CSS, a modern, responsive, mobile first CSS framework.
# See https://www.w3schools.com/w3css/default.asp.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, January 2023.
# Extended Rik D.T. Janssen, February, September 2023 to December 2024.
#
# ##############################################################################


import os
from connexion import FlaskApp, options
from flask import current_app, request, send_from_directory
from neo4j.graph import Node
from ricgraph import (ricgraph_nr_nodes, ricgraph_nr_edges,
                      nodes_cache_nodelink_create, nodes_cache_nodelink_read,
                      nodes_cache_nodelink_size, create_ricgraph_key)
from ricgraph_explorer_constants import (html_body_start, html_body_end,
                                         html_preamble,
                                         page_footer_wsgi, page_footer_development,
                                         button_style, button_width,
                                         VIEW_MODE_ALL,
                                         DEFAULT_SEARCH_MODE, DEFAULT_DISCOVERER_MODE,
                                         DETAIL_COLUMNS, ID_COLUMNS, ORGANIZATION_COLUMNS,
                                         RESEARCH_OUTPUT_COLUMNS, MAX_ROWS_IN_TABLE)
from ricgraph_explorer_init import initialize_ricgraph_explorer
from ricgraph_explorer_graphdb import (find_overlap_in_source_systems,
                                       find_overlap_in_source_systems_records,
                                       find_person_share_resouts,
                                       find_enrich_candidates,
                                       find_person_organization_collaborations,
                                       find_organization_additional_info)
from ricgraph_explorer_utils import (get_html_for_cardstart, get_html_for_cardend,
                                     create_html_form, get_url_parameter_value,
                                     get_message, get_found_message,
                                     get_you_searched_for_card, get_page_title)
from ricgraph_explorer_table import (get_regular_table,
                                     view_personal_information,
                                     get_faceted_table, get_tabbed_table)
from ricgraph_explorer_restapi import *


graph = None
name_all = name_personal_all = category_all = source_all = resout_types_all = ''
name_all_datalist = category_all_datalist = source_all_datalist = resout_types_all_datalist = []
personal_types_all = remainder_types_all = []
privacy_statement_link = privacy_measures_link = ''
homepage_intro_html = ''
page_footer = ''


# We don't show the Swagger REST API page, we use RapiDoc for that (see restapidocpage()
# endpoint below). 'swagger_ui_options' is taken from
# https://connexion.readthedocs.io/en/latest/swagger_ui.html#connexion.options.SwaggerUIOptions.
# 'swagger_ui_config' options are on this page:
# https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration
swagger_ui_options = options.SwaggerUIOptions(swagger_ui=False)
ricgraph_explorer = FlaskApp(import_name=__name__,
                             specification_dir='./static/',
                             swagger_ui_options=swagger_ui_options)
ricgraph_explorer.add_api(specification='openapi.yaml',
                          swagger_ui_options=swagger_ui_options)


# ##############################################################################
# Favicon
# ##############################################################################
@ricgraph_explorer.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(ricgraph_explorer.app.root_path, 'static'),
                               path='favicon.ico',
                               mimetype='image/png')


# ##############################################################################
# Entry functions.
# Ricgraph Explorer has these web pages:
# 1. homepage.
# 2. searchpage:
# 2a. if there is more than one result: select a node from a list of nodes,
#     go to optionspage.
# 2b. if there is just one result: go to optionspage.
# 3. optionspage, this page depends on the node type found.
# 3. resultspage, this page depends on what the user would like to see.
# 4. restapidocpage, this page shows the documentation of the REST API.
# ##############################################################################
@ricgraph_explorer.route(rule='/')
def homepage() -> str:
    """Ricgraph Explorer entry, the home page, when you access '/'.

    :return: html to be rendered.
    """
    global page_footer, source_all, category_all, homepage_intro_html

    get_all_globals_from_app_context()
    html = html_body_start
    html += get_page_title(title='Ricgraph - Research in context graph')
    html += get_html_for_cardstart()
    html += 'Ricgraph, also known as Research in context graph, enables the exploration of researchers, '
    html += 'teams, their results, '
    html += 'collaborations, skills, projects, and the relations between these items. '
    html += 'Ricgraph can store many types of items into a single graph (network). '
    html += 'These items can be obtained from various systems and from '
    html += 'multiple organizations. '
    html += 'Ricgraph facilitates reasoning about these '
    html += 'items because it infers new relations between items, '
    html += 'relations that are not present in any of the separate source systems. '
    html += 'It is flexible and extensible, and can be adapted to new application areas. '

    html += '<p/>'
    html += homepage_intro_html
    html += '<p/>'

    html += 'You can use Ricgraph Explorer to explore Ricgraph. '
    html += 'There are various methods to start exploring:'
    html += '<p/>'
    html += create_html_form(destination='searchpage',
                             button_text='search for a person',
                             hidden_fields={'search_mode': 'value_search',
                                            'name': 'FULL_NAME'
                                            })
    html += '<p/>'
    html += create_html_form(destination='searchpage',
                             button_text='search for a (sub-)organization',
                             hidden_fields={'search_mode': 'value_search',
                                            'category': 'organization'
                                            })
    html += '<p/>'
    if 'competence' in category_all:
        html += create_html_form(destination='searchpage',
                                 button_text='search for a skill, expertise area or research area',
                                 hidden_fields={'search_mode': 'value_search',
                                                'category': 'competence'
                                                })
        html += '<p/>'
    html += create_html_form(destination='searchpage',
                             button_text='search for anything (broad search)',
                             hidden_fields={'search_mode': 'value_search'
                                            })
    html += '<p/>'
    html += create_html_form(destination='searchpage',
                             button_text='advanced search',
                             hidden_fields={'search_mode': 'exact_match'
                                            })
    html += '<p/>'
    html += get_html_for_cardend()

    html += get_html_for_cardstart()
    nr_nodes = ricgraph_nr_nodes()
    nr_edges = ricgraph_nr_edges()
    html += '<h2>About Ricgraph</h2>'
    html += 'More information:'
    html += '<ul>'
    html += '<li>'
    html += 'For a gentle introduction in Ricgraph, please read the reference publication: '
    html += 'Rik D.T. Janssen (2024). Ricgraph: A flexible and extensible graph to explore research in '
    html += 'context from various systems. <em>SoftwareX</em>, 26(101736). '
    html += '<a href="https://doi.org/10.1016/j.softx.2024.101736">https://doi.org/10.1016/j.softx.2024.101736</a>. '
    html += '</li>'
    html += '<li>'
    html += 'Extensive documentation, publications, videos and source code can be found in the GitHub repository '
    html += '<a href="https://github.com/UtrechtUniversity/ricgraph">'
    html += 'https://github.com/UtrechtUniversity/ricgraph</a>. '
    html += '</li>'
    html += '<li>'
    html += 'If you use or refer to Ricgraph, please cite both the reference publication '
    html += '(<a href="https://doi.org/10.1016/j.softx.2024.101736">https://doi.org/10.1016/j.softx.2024.101736</a>), '
    html += 'and the software '
    html += '(<a href="https://doi.org/10.5281/zenodo.7524314">https://doi.org/10.5281/zenodo.7524314</a>).'
    html += '</li>'
    html += '</ul>'
    html += '<br/>'
    html += 'What to find in this instance of Ricgraph:'
    html += '<ul>'
    html += '<li>'
    html += 'Items from the following source systems: '
    if len(source_all) == 0:
        html += '[no source systems harvested yet]'
    else:
        html += ', '.join([str(source) for source in source_all])
    html += '.'
    html += '</li>'
    html += '<li>'
    html += 'Types of items: '
    if len(name_all) == 0:
        html += '[no items yet]'
    else:
        html += ', '.join([str(name) for name in name_all])
    html += '.'
    html += '</li>'
    html += '<li>'
    html += 'Types of items that contain personal data: '
    if len(name_personal_all) == 0:
        html += '[no items that contain personal data yet]'
    else:
        html += ', '.join([str(name_personal) for name_personal in name_personal_all])
    html += '.'
    html += '</li>'
    html += '<li>'
    html += str(nr_nodes) + ' nodes and ' + str(nr_edges) + ' edges.'
    html += '</li>'
    html += '<li>'
    length, size_kb = nodes_cache_nodelink_size()
    html += 'The node cache has ' + str(length) + ' elements, and its size is '
    html += str(size_kb) + ' kB.'
    html += '</li>'
    html += '</ul>'
    html += get_html_for_cardend()
    html += page_footer + html_body_end
    return html


@ricgraph_explorer.route(rule='/searchpage/', methods=['GET'])
def searchpage() -> str:
    """Ricgraph Explorer entry, this 'page' shows the search form, both the
    exact match search form and the broad search on the 'value' field form.

    Possible parameters are:
    - discoverer_mode: the discoverer_mode to use, 'details_view' to see all details,
      or 'person_view' to have a nicer layout.
    - search_mode: the search_mode to use, 'exact_match' or 'value_search' (broad
      search on field 'value').

    returns html to parse.
    """
    global page_footer, name_all_datalist, category_all, category_all_datalist

    get_all_globals_from_app_context()
    name = get_url_parameter_value(parameter='name')
    category = get_url_parameter_value(parameter='category')
    search_mode = get_url_parameter_value(parameter='search_mode',
                                          allowed_values=['exact_match', 'value_search'],
                                          default_value=DEFAULT_SEARCH_MODE)
    discoverer_mode = get_url_parameter_value(parameter='discoverer_mode',
                                              allowed_values=['details_view', 'person_view'],
                                              default_value=DEFAULT_DISCOVERER_MODE)
    max_nr_items = get_url_parameter_value(parameter='max_nr_items',
                                           default_value=str(MAX_ITEMS))
    if not max_nr_items.isnumeric():
        # This also catches negative numbers, they contain a '-' and are not numeric.
        # See https://www.w3schools.com/python/ref_string_isnumeric.asp.
        max_nr_items = str(MAX_ITEMS)
    max_nr_table_rows = get_url_parameter_value(parameter='max_nr_table_rows',
                                                default_value=str(MAX_ROWS_IN_TABLE))
    if not max_nr_table_rows.isnumeric():
        max_nr_table_rows = str(MAX_ROWS_IN_TABLE)
    form = '<form method="get" action="/optionspage/">'
    if search_mode == 'exact_match':
        form += '<label for="name">Search for a value in Ricgraph field <em>name</em>:</label>'
        form += '<input id="name" class="w3-input w3-border" list="name_all_datalist"'
        form += 'name=name id=name autocomplete=off>'
        form += '<div class="firefox-only">Click twice to get a dropdown list.</div>'
        form += name_all_datalist
        form += '<br/>'

        form += '<label for="category">Search for a value in Ricgraph field <em>category</em>:</label>'
        form += '<input id="category" class="w3-input w3-border" list="category_all_datalist"'
        form += 'name=category id=category autocomplete=off>'
        form += '<div class="firefox-only">Click twice to get a dropdown list.</div>'
        form += category_all_datalist
        form += '<br/>'
    if search_mode == 'value_search' and name != '':
        form += '<input id="name" type="hidden" name="name" value=' + name + '>'
    if search_mode == 'value_search' and category != '':
        form += '<input id="category" type="hidden" name="category" value=' + category + '>'
    if search_mode == 'exact_match':
        form += '<label for="value">Search for a value in Ricgraph field <em>value</em>:</label>'
    else:
        form += '<label for="value">Type your search string:</label>'
    form += '<input id="value" class="w3-input w3-border" type=text name=value>'
    form += '<input type="hidden" name="search_mode" value=' + search_mode + '>'

    if search_mode == 'exact_match':
        form += 'These fields are case-sensitive and use exact match search. '
        form += 'If you enter values in more than one field, these fields are combined using AND.</br>'

    radio_person_text = ' <em>person_view</em>: only show relevant columns, '
    radio_person_text += 'results are presented in a <em>tabbed</em> format '
    radio_person_tooltip = '<img src="/static/images/circle_info_solid_uuyellow.svg" alt="Click for more information">'
    radio_person_tooltip += '<div class="w3-text" style="margin-left:60px;">'
    radio_person_tooltip += 'This view presents results in a <em>tabbed</em> format. '
    radio_person_tooltip += 'Also, tables have less columns to reduce information overload. '
    if 'competence' in category_all:
        radio_person_tooltip += 'This view has been tailored to the Utrecht University staff pages, since some '
        radio_person_tooltip += 'of these pages also include expertise areas, research areas, skills or photos. '
        radio_person_tooltip += 'These will be presented in a different way using lists. '
    radio_person_tooltip += '</div>'

    radio_details_text = ' <em>details_view</em>: show all columns, '
    radio_details_text += 'research results are presented in a table with <em>facets</em> '
    radio_details_tooltip = '<img src="/static/images/circle_info_solid_uuyellow.svg" alt="Click for more information">'
    radio_details_tooltip += '<div class="w3-text" style="margin-left:60px;"> '
    radio_details_tooltip += 'This view shows all columns in Ricgraph. '
    radio_details_tooltip += 'Research results are presented in a table with <em>facets</em>. '
    radio_details_tooltip += '</div>'

    form += '<br/>'
    form += '<fieldset>'
    form += '<legend>Please specify how you like to view your results:</legend>'
    form += '<input id="person_view" class="w3-radio" type="radio" name="discoverer_mode" value="person_view"'
    if discoverer_mode == 'person_view':
        form += 'checked'
    form += '>' + radio_person_text
    form += '<label for="person_view" class="w3-tooltip">' + radio_person_tooltip + '</label><br/>'
    form += '<input id="details_view" class="w3-radio" type="radio" name="discoverer_mode" value="details_view"'
    if discoverer_mode == 'details_view':
        form += 'checked'
    form += '>' + radio_details_text
    form += '<label for="details_view" class="w3-tooltip">' + radio_details_tooltip + '</label><br/>'
    form += '</fieldset>'

    form += '</br>'
    tooltip = '<img src="/static/images/circle_info_solid_uuyellow.svg" alt="Click for more information">'
    tooltip += '<div class="w3-text" style="margin-left:60px;"> '
    tooltip += 'More items will take more time, since they all have to be processed. '
    tooltip += '</div>'
    form += 'You might want to specify the maximum number of items to return, '
    form += 'or 0 to return all items (the more items, the more time it will take): '
    form += '<label for="max_nr_items" class="w3-tooltip">' + tooltip + '</label><br/>'
    form += '<input id="max_nr_items" class="w3-input w3-border" type=text value=' + max_nr_items + ' name=max_nr_items>'

    form += '</br>'
    tooltip = '<img src="/static/images/circle_info_solid_uuyellow.svg" alt="Click for more information">'
    tooltip += '<div class="w3-text" style="margin-left:60px;"> '
    tooltip += 'More rows will take more time, since HTML needs to be generated for every row. '
    tooltip += 'If the number of items returned is very large, and the number of rows in a table '
    tooltip += 'is also very large or 0 (i.e. all rows), your browser may crash. '
    tooltip += '</div>'
    form += 'You might want to specify the maximum number of rows in a table to return '
    form += '(the page size of the table), '
    form += 'or 0 to return all rows (the more rows, the more time it will take): '
    form += '<label for="max_nr_table_rows" class="w3-tooltip">' + tooltip + '</label><br/>'
    form += '<input id="max_nr_table_rows" class="w3-input w3-border" type=text value=' + max_nr_table_rows + ' name=max_nr_table_rows>'

    form += '<br/><input class="' + button_style + '" ' + button_width + ' type=submit value=search>'
    form += '</form>'

    html = html_body_start
    if search_mode == 'exact_match':
        html += get_page_title(title='Advanced search page')
    else:
        html += get_page_title(title='Search page')
    html += get_html_for_cardstart()
    html += form
    html += get_html_for_cardend()
    html += page_footer + html_body_end
    return html


@ricgraph_explorer.route(rule='/optionspage/', methods=['GET'])
def optionspage() -> str:
    """Ricgraph Explorer entry, this 'page' only uses URL parameters.
    Find nodes based on URL parameters passed.

    Possible parameters are:

    - key: key of the nodes to find. If present, this field is preferred above
      'name', 'category' or 'value'.
    - name: name of the nodes to find.
    - category: category of the nodes to find.
    - value: value of the nodes to find.
    - discoverer_mode: the discoverer_mode to use, 'details_view' to see all details,
      or 'person_view' to have a nicer layout.
    - search_mode: the search_mode to use, 'exact_match' or 'value_search' (broad
      search on field 'value').
    - extra_url_parameters: a dict containing url parameters to be passed with each
      url generated. This dict can be extended as desired.

    returns html to parse.
    """
    global page_footer

    get_all_globals_from_app_context()
    search_mode = get_url_parameter_value(parameter='search_mode',
                                          allowed_values=['exact_match', 'value_search'],
                                          default_value=DEFAULT_SEARCH_MODE)
    discoverer_mode = get_url_parameter_value(parameter='discoverer_mode',
                                              allowed_values=['details_view', 'person_view'],
                                              default_value=DEFAULT_DISCOVERER_MODE)
    extra_url_parameters = {}
    max_nr_items = get_url_parameter_value(parameter='max_nr_items',
                                           default_value=str(MAX_ITEMS))
    if not max_nr_items.isnumeric():
        # This also catches negative numbers, they contain a '-' and are not numeric.
        # See https://www.w3schools.com/python/ref_string_isnumeric.asp.
        max_nr_items = str(MAX_ITEMS)
    extra_url_parameters['max_nr_items'] = max_nr_items
    max_nr_table_rows = get_url_parameter_value(parameter='max_nr_table_rows',
                                                default_value=str(MAX_ROWS_IN_TABLE))
    if not max_nr_table_rows.isnumeric():
        max_nr_table_rows = str(MAX_ROWS_IN_TABLE)
    extra_url_parameters['max_nr_table_rows'] = max_nr_table_rows
    html = html_body_start
    #html += get_page_title(title='Results page')

    key = get_url_parameter_value(parameter='key', use_escape=False)
    if key == '':
        name = get_url_parameter_value(parameter='name')
        category = get_url_parameter_value(parameter='category')
        value = get_url_parameter_value(parameter='value', use_escape=False)
    else:
        name = ''
        category = ''
        value = ''

    if name == '' and category == '' and value == '' and key == '':
        html += get_message(message='Ricgraph Explorer could not find anything.')
        html += page_footer + html_body_end
        return html

    # First check if the node is in 'nodes_cache'.
    if key != '':
        if (node := nodes_cache_nodelink_read(key=key)) is not None:
            html += create_options_page(node=node,
                                        discoverer_mode=discoverer_mode,
                                        extra_url_parameters=extra_url_parameters)
            html += page_footer + html_body_end
            return html

    if name != '' and value != '':
        key_found = create_ricgraph_key(name=name, value=value)
        if (node := nodes_cache_nodelink_read(key=key_found)) is not None:
            html += create_options_page(node=node,
                                        discoverer_mode=discoverer_mode,
                                        extra_url_parameters=extra_url_parameters)
            html += page_footer + html_body_end
            return html

    # No, it is not.
    if key != '':
        result = read_all_nodes(key=key)
    elif search_mode == 'exact_match':
        result = read_all_nodes(name=name, category=category, value=value,
                                max_nr_nodes=int(extra_url_parameters['max_nr_items']))
    else:
        if len(value) < SEARCH_STRING_MIN_LENGTH:
            html += get_message(message='The search string should be at least '
                                        + str(SEARCH_STRING_MIN_LENGTH) + ' characters.')
            html += page_footer + html_body_end
            return html
        if name == 'FULL_NAME':
            # We also need to search on FULL_NAME_ASCII, therefore the 'name_is_exact_match = False'.
            result = read_all_nodes(name=name, category=category, value=value,
                                    name_is_exact_match=False,
                                    value_is_exact_match=False,
                                    max_nr_nodes=int(extra_url_parameters['max_nr_items']))
        else:
            result = read_all_nodes(name=name, category=category, value=value,
                                    value_is_exact_match=False,
                                    max_nr_nodes=int(extra_url_parameters['max_nr_items']))
    if len(result) == 0:
        # We didn't find anything.
        html += get_message(message='Ricgraph Explorer could not find anything.')
        html += page_footer + html_body_end
        return html
    if len(result) > 1:
        html += get_page_title(title='Results page')
        table_header = 'Your search resulted in more than one item. Please choose one item to continue:'
        html += get_regular_table(nodes_list=result,
                                  table_header=table_header,
                                  discoverer_mode=discoverer_mode,
                                  extra_url_parameters=extra_url_parameters)
        html += page_footer + html_body_end
        return html

    node = result[0]
    key = create_ricgraph_key(name=node['name'], value=node['value'])
    nodes_cache_nodelink_create(key=key, node=node)
    html += create_options_page(node=node,
                                discoverer_mode=discoverer_mode,
                                extra_url_parameters=extra_url_parameters)
    html += page_footer + html_body_end
    return html


@ricgraph_explorer.route(rule='/resultspage/', methods=['GET'])
def resultspage() -> str:
    """Ricgraph Explorer entry, this 'page' only uses URL parameters.
    View the results based on the values passed.
    This function is tied to create_results_page(), where, depending on the
    value of 'view_mode', is determined what will be viewed.
    This function will only be called with one node, so we can use 'key' to find it.

    Possible parameters are:

    - view_mode: determines what will be shown in create_results_page().
      This view_mode is first set in create_options_page(), and then
      caught first in resultspage() and then in create_results_page().
    - key: key of the nodes to find.
    - name_list: either a string which indicates that we only want neighbor
      nodes where the property 'name' is equal to 'name_list'
      (e.g. 'ORCID'), or a list containing several node names, indicating
      that we want all neighbor nodes where the property 'name' equals
      one of the names in the list 'name_list' (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty (empty string), return all nodes.
    - category_list: similar to 'name_list', but now for the property 'category'.
    - discoverer_mode: the discoverer_mode to use, 'details_view' to see all details,
      or 'person_view' to have a nicer layout.
    - extra_url_parameters: a dict containing url parameters to be passed with each
      url generated. This dict can be extended as desired.

    returns html to parse.
    """
    global page_footer

    get_all_globals_from_app_context()
    view_mode = get_url_parameter_value(parameter='view_mode')
    key = get_url_parameter_value(parameter='key', use_escape=False)
    discoverer_mode = get_url_parameter_value(parameter='discoverer_mode',
                                              allowed_values=['details_view', 'person_view'],
                                              default_value=DEFAULT_DISCOVERER_MODE)
    extra_url_parameters = {}
    max_nr_items = get_url_parameter_value(parameter='max_nr_items',
                                           default_value=str(MAX_ITEMS))
    if not max_nr_items.isnumeric():
        # This also catches negative numbers, they contain a '-' and are not numeric.
        # See https://www.w3schools.com/python/ref_string_isnumeric.asp.
        max_nr_items = str(MAX_ITEMS)
    extra_url_parameters['max_nr_items'] = max_nr_items
    max_nr_table_rows = get_url_parameter_value(parameter='max_nr_table_rows',
                                                default_value=str(MAX_ROWS_IN_TABLE))
    if not max_nr_table_rows.isnumeric():
        max_nr_table_rows = str(MAX_ROWS_IN_TABLE)
    extra_url_parameters['max_nr_table_rows'] = max_nr_table_rows
    name_list = request.args.getlist('name_list')
    category_list = request.args.getlist('category_list')
    # HTML forms with an empty field named e.g. 'aa' will result in a URL parameter '...&aa=&...'.
    # In this case, getlist() returns [''].
    # This is undesirable behaviour, since I'd rather have an empty list. Correct for it.
    if len(name_list) == 1 and name_list[0] == '':
        name_list = []
    if len(category_list) == 1 and category_list[0] == '':
        category_list = []

    html = html_body_start

    if view_mode not in VIEW_MODE_ALL:
        html += get_message(message='Unknown view_mode: "' + view_mode + '".')
        html += page_footer + html_body_end
        return html

    if view_mode == 'view_regular_table_overlap_records':
        # Special case, we catch it here because it needs a number of parameters which
        # I do not really want to pass down all the way.
        name = get_url_parameter_value(parameter='name')
        category = get_url_parameter_value(parameter='category')
        value = get_url_parameter_value(parameter='value', use_escape=False)
        system1 = get_url_parameter_value(parameter='system1')
        system2 = get_url_parameter_value(parameter='system2')
        overlap_mode = get_url_parameter_value(parameter='overlap_mode',
                                               allowed_values=['thisnode', 'neighbornodes'],
                                               default_value='neighbornodes')
        html += find_overlap_in_source_systems_records(name=name, category=category, value=value,
                                                       system1=system1, system2=system2,
                                                       discoverer_mode=discoverer_mode,
                                                       overlap_mode=overlap_mode,
                                                       extra_url_parameters=extra_url_parameters)
        html += page_footer + html_body_end
        return html

    html += create_results_page(view_mode=view_mode,
                                key=key,
                                name_list=name_list,
                                category_list=category_list,
                                discoverer_mode=discoverer_mode,
                                extra_url_parameters=extra_url_parameters)

    html += page_footer + html_body_end
    return html


@ricgraph_explorer.route(rule='/restapidocpage/', methods=['GET'])
def restapidocpage() -> str:
    """Show the documentation for the Ricgraph REST API. Ricgraph uses RapiDoc.

    :return: html to be rendered.
    """
    # For more information, see: https://rapidocweb.com and https://github.com/rapi-doc/RapiDoc.
    # For options see: https://rapidocweb.com/api.html.
    html = '<!DOCTYPE html>'
    html += '<html>'
    html += '<head>'
    html += html_preamble
    html += '<script type="module" src="/static/rapidoc-min.js"></script>'
    html += '<title>Ricgraph REST API</title>'
    html += '</head>'
    html += """<body>
              <style>
                rapi-doc { --font-regular:"Open Sans",sans-serif; }
                rapi-doc::part(section-navbar) { /* <<< targets navigation bar */
                    background:#ffcd00;              /* uu-yellow */
                }
              </style>
              <rapi-doc
                show-header="false"
                spec-url="/static/openapi.yaml"
                nav-text-color="#000000"        /* black */
                nav-hover-text-color="#5287c6"  /* uu-blue */
                sort-endpoints-by="none"
              > 
              <div slot="nav-logo">
                <img slot="nav-logo" src="/static/images/ricgraph_logo.png" width="200" 
                  style="vertical-align:middle;padding-right:0.5em;">REST API</img>
                <p/>
                <a href="/">Return to Ricgraph Explorer</a>
              </div>
              </rapi-doc>
              </body>
              </html>"""
    return html


# ##############################################################################
# Other page handling functions.
# ##############################################################################
def create_options_page(node: Node,
                        discoverer_mode: str = '',
                        extra_url_parameters: dict = None) -> str:
    """This function creates the page with options to choose from, depending on the
    choice the user has made on the index page.
    The 'view_mode' that is used, is caught first in resultspage() and then
    in create_results_page().

    :param node: the node that is found and that determines the possible choices.
    :param discoverer_mode: as usual.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    global name_all_datalist, category_all_datalist, source_all_datalist
    global category_all, resout_types_all, resout_types_all_datalist

    if extra_url_parameters is None:
        extra_url_parameters = {}

    html = ''
    if node is None:
        return get_message(message='create_options_page(): Node is None. This should not happen.')

    if discoverer_mode == 'details_view':
        html += get_you_searched_for_card(key=node['_key'],
                                          discoverer_mode=discoverer_mode,
                                          extra_url_parameters=extra_url_parameters)
    html += get_page_title(title='Results page')
    key = node['_key']
    html += get_found_message(node=node,
                              discoverer_mode=discoverer_mode,
                              extra_url_parameters=extra_url_parameters)
    if node['category'] == 'organization':
        html += get_html_for_cardstart()
        html += '<h2>What would you like to see from this organization?</h2>'
        html += create_html_form(destination='resultspage',
                                 button_text='show all information related to this organization',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_unspecified_table_organizations'
                                                } | extra_url_parameters)
        html += '<p/>'

        html += create_html_form(destination='resultspage',
                                 button_text='show persons related to this organization',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'name_list': 'person-root',
                                                'view_mode': 'view_regular_table_persons_of_org'
                                                } | extra_url_parameters)
        html += get_html_for_cardend()

        html += get_html_for_cardstart()
        html += '<h2>Advanced information related to this organization</h2>'
        html += get_html_for_cardstart()
        html += '<h3>More information about persons or their results in this organization.</h3>'
        html += create_html_form(destination='resultspage',
                                 button_text='find any information from all persons in this organization',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_regular_table_organization_addinfo'
                                                } | extra_url_parameters)
        html += '<p/>'

        html += create_html_form(destination='resultspage',
                                 button_text='find research results from all persons in this organization',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'category_list': resout_types_all,
                                                'view_mode': 'view_regular_table_organization_addinfo'
                                                } | extra_url_parameters)
        html += '<p/>'

        if 'competence' in category_all:
            html += create_html_form(destination='resultspage',
                                     button_text='find skills from all persons in this organization',
                                     hidden_fields={'key': key,
                                                    'discoverer_mode': discoverer_mode,
                                                    'category_list': 'competence',
                                                    'view_mode': 'view_regular_table_organization_addinfo'
                                                    } | extra_url_parameters)
            html += '<p/>'

        html += '<br/>'

        explanation = 'By using the fields below, you can choose '
        explanation += 'what you would like to see from the persons or their results in this organization. '
        explanation += 'You can use one or both fields.'
        label_text_name = 'Search for persons or results using field <em>name</em>: '
        input_spec_name = ('list', 'name_list', 'name_all_datalist', name_all_datalist)
        label_text_category = '</br>Search for persons or results using field <em>category</em>: '
        input_spec_category = ('list', 'category_list', 'category_all_datalist', category_all_datalist)
        html += create_html_form(destination='resultspage',
                                 button_text='find specific information',
                                 explanation=explanation,
                                 input_fields={label_text_name: input_spec_name,
                                               label_text_category: input_spec_category,
                                               },
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_regular_table_organization_addinfo'
                                                } | extra_url_parameters)
        html += get_html_for_cardend()
        html += get_html_for_cardend()

    elif node['category'] == 'person':
        html += get_html_for_cardstart()
        html += '<h2>What would you like to see from this person?</h2>'

        html += create_html_form(destination='resultspage',
                                 button_text='show all information related to this person',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'category_list': remainder_types_all,
                                                'view_mode': 'view_unspecified_table_everything'
                                                } | extra_url_parameters)
        html += '<p/>'

        html += create_html_form(destination='resultspage',
                                 button_text='show personal information related to this person',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'category_list': 'person',
                                                'view_mode': 'view_regular_table_personal'
                                                } | extra_url_parameters)
        html += '<p/>'

        html += create_html_form(destination='resultspage',
                                 button_text='show organizations related to this person',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'category_list': 'organization',
                                                'view_mode': 'view_regular_table_organizations'
                                                } | extra_url_parameters)
        html += '<p/>'

        html += create_html_form(destination='resultspage',
                                 button_text='show research results related to this person',
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'category_list': resout_types_all,
                                                'view_mode': 'view_unspecified_table_resouts'
                                                } | extra_url_parameters)
        html += get_html_for_cardend()

        html += get_html_for_cardstart()
        html += '<h2>Advanced information related to this person</h2>'
        html += get_html_for_cardstart()
        html += '<h3>With whom does this person share research results?</h3>'
        html += create_html_form(destination='resultspage',
                                 button_text='find persons that share any research result types with this person',
                                 hidden_fields={'key': key,
                                                'category_list': resout_types_all,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_regular_table_person_share_resouts'
                                                } | extra_url_parameters)

        html += '<br/>'
        label_text = 'By entering a value in the field below, '
        label_text += 'you will get a list of persons who share a specific research result type with this person:'
        input_spec = ('list', 'category_list', 'resout_types_all_datalist', resout_types_all_datalist)
        html += create_html_form(destination='resultspage',
                                 button_text='find persons that share a specific research result type with this person',
                                 input_fields={label_text: input_spec},
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_regular_table_person_share_resouts'
                                                } | extra_url_parameters)

        html += get_html_for_cardend()

        html += get_html_for_cardstart()
        explanation = '<h3>With which organizations does this person collaborate?</h3>'
        explanation += 'By clicking the following button, you will get an overview '
        explanation += 'of organizations that his person collaborates with. '
        explanation += 'A person <em>X</em> from organization <em>A</em> '
        explanation += 'collaborates with a person <em>Y</em> from '
        explanation += 'organization <em>B</em> if <em>X</em> and <em>Y</em> have both contributed to '
        explanation += 'the same research result.'
        button_text = 'find organizations that this person collaborates with'
        html += create_html_form(destination='resultspage',
                                 button_text=button_text,
                                 explanation=explanation,
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_regular_table_person_organization_collaborations'
                                                } | extra_url_parameters)

        html += get_html_for_cardend()

        html += get_html_for_cardstart()
        explanation = '<h3>Improve or enhance information in one of your source systems</h3>'
        explanation += 'The process of improving or enhancing information in a source system is called "enriching" '
        explanation += 'that source system. This is only possible if you have harvested more than one source system. '
        explanation += 'By using information found in one or more other harvested systems, '
        explanation += 'information in this source system can be improved or enhanced. '
        explanation += '</br>Use the field below to enter a name of one of your source systems. '
        explanation += 'Ricgraph Explorer will show what information can be added to this source system, '
        explanation += 'based on the information harvested from other source systems. '
        label_text = 'The name of the source system you would like to enrich:'
        # Note: we misuse the field 'category_list' to pass the name of the source system.
        button_text = 'find information harvested from other source systems, '
        button_text += 'not present in this source system'
        input_spec = ('list', 'category_list', 'source_all_datalist', source_all_datalist)
        html += create_html_form(destination='resultspage',
                                 button_text=button_text,
                                 explanation=explanation,
                                 input_fields={label_text: input_spec},
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_regular_table_person_enrich_source_system'
                                                } | extra_url_parameters)
        html += get_html_for_cardend()

        html += get_html_for_cardstart()
        explanation = '<h3>More information about overlap in source systems</h3>'
        explanation += 'In case more than one source systems have been harvested, '
        explanation += 'and the information in Ricgraph for the neighbors of this node have originated '
        explanation += 'from more than one source system, you can find out from which ones.</br>'
        button_text = 'find the overlap in source systems for '
        button_text += 'the neighbor nodes of this node (this may take some time)'
        html += create_html_form(destination='resultspage',
                                 button_text=button_text,
                                 explanation=explanation,
                                 hidden_fields={'key': key,
                                                'discoverer_mode': discoverer_mode,
                                                'view_mode': 'view_regular_table_overlap'
                                                } | extra_url_parameters)
        html += get_html_for_cardend()

        html += get_html_for_cardend()

    # ###
    # Note: view_mode == 'view_regular_table_overlap_records' is caught in resultspage().
    # ###
    else:
        html = create_results_page(view_mode='view_regular_table_category',
                                   key=key,
                                   discoverer_mode=discoverer_mode,
                                   extra_url_parameters=extra_url_parameters)

    return html


def create_results_page(view_mode: str,
                        key: str,
                        name_list: list = None,
                        category_list: list = None,
                        discoverer_mode: str = '',
                        extra_url_parameters: dict = None) -> str:
    """This function creates the page with results to show to the user.
    What is produced depends on 'view_mode'.
    The 'view_mode' that is used, is first set in create_options_page(), and then
    caught first in resultspage() and then in create_results_page().

    :param view_mode: what type of page to create.
    :param key: the _key of the node that is found and that determines where we start from.
    :param name_list: a list containing several node names, indicating
      that we want all neighbor nodes where the property 'name' equals
      one of the names in the list 'name_str' (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty , return all nodes.
    :param category_list: as name_str, but for category.
    :param discoverer_mode: as usual.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    global resout_types_all, personal_types_all, remainder_types_all

    if name_list is None:
        name_list = []
    # The following is not used yet.
    # name_list_str = ''
    # if len(name_list) == 1:
    #     name_list_str = name_list[0]
    if category_list is None:
        category_list = []
    # The following is not used yet.
    # category_list_str = ''
    # if len(category_list) == 1:
    #     category_list_str = category_list[0]
    if extra_url_parameters is None:
        extra_url_parameters = {}

    max_nr_items = int(extra_url_parameters['max_nr_items'])
    html = ''
    if (node := nodes_cache_nodelink_read(key=key)) is None:
        result = read_all_nodes(key=key)
        if len(result) == 0 or len(result) > 1:
            if len(result) == 0:
                message = 'Ricgraph Explorer could not find anything. '
            else:
                message = 'Ricgraph Explorer found too many nodes. '
            message += 'This should not happen. '
            return get_message(message=message)
        nodes_cache_nodelink_create(key=key, node=result[0])
        node = result[0]

    if discoverer_mode == 'details_view':
        table_columns_ids = DETAIL_COLUMNS
        table_columns_org = DETAIL_COLUMNS
        table_columns_resout = DETAIL_COLUMNS
        if node is not None:
            html += get_you_searched_for_card(key=node['_key'],
                                              name_list=name_list,
                                              category_list=category_list,
                                              view_mode=view_mode,
                                              discoverer_mode=discoverer_mode,
                                              extra_url_parameters=extra_url_parameters)
    else:
        table_columns_ids = ID_COLUMNS
        table_columns_org = ORGANIZATION_COLUMNS
        table_columns_resout = RESEARCH_OUTPUT_COLUMNS

    # We need this multiple times.
    node_found = get_found_message(node=node,
                                   discoverer_mode=discoverer_mode,
                                   extra_url_parameters=extra_url_parameters)

    if view_mode == 'view_regular_table_personal':
        personroot_node = get_personroot_node(node=node)
        neighbor_nodes_personal = get_all_neighbor_nodes(node=personroot_node,
                                                         category_want=personal_types_all)
        html += get_page_title(title='Personal information related to this person')
        html += node_found
        if discoverer_mode == 'details_view':
            html += get_regular_table(nodes_list=neighbor_nodes_personal,
                                      table_header='This is personal information related to this person:',
                                      table_columns=table_columns_ids,
                                      discoverer_mode=discoverer_mode,
                                      extra_url_parameters=extra_url_parameters)
        else:
            html += view_personal_information(nodes_list=neighbor_nodes_personal,
                                              discoverer_mode=discoverer_mode,
                                              extra_url_parameters=extra_url_parameters)

    elif view_mode == 'view_regular_table_organizations' \
            or view_mode == 'view_regular_table_category':
        if view_mode == 'view_regular_table_category':
            personroot_node = node
        else:
            personroot_node = get_personroot_node(node=node)
        neighbor_nodes = get_all_neighbor_nodes(node=personroot_node,
                                                name_want=name_list,
                                                category_want=category_list)
        if view_mode == 'view_regular_table_organizations':
            table_header = 'These are the organizations related to this person:'
            table_columns = table_columns_org
            html += get_page_title(title='Organizations related to this person')
        else:
            table_header = 'This is all information related to this ' + node['category'] + ':'
            table_columns = table_columns_resout
            html += get_page_title(title='All information related to this ' + node['category'])
        html += node_found
        html += get_regular_table(nodes_list=neighbor_nodes,
                                  table_header=table_header,
                                  table_columns=table_columns,
                                  discoverer_mode=discoverer_mode,
                                  extra_url_parameters=extra_url_parameters)

    elif view_mode == 'view_regular_table_persons_of_org':
        # Some organizations have a large number of neighbors, but we will only show
        # 'max_nr_items' in the table. Therefore, reduce the number of neighbors when
        # searching for persons in an organization. Don't do this for other view_modes, because
        # in that case the table shows how many items are found.
        neighbor_nodes = get_all_neighbor_nodes(node=node,
                                                name_want=name_list,
                                                category_want=category_list,
                                                max_nr_neighbor_nodes=max_nr_items)
        table_header = 'These are persons related to this organization:'
        table_columns = table_columns_ids
        html += get_page_title(title='Persons related to this organization')
        html += node_found
        html += get_regular_table(nodes_list=neighbor_nodes,
                                  table_header=table_header,
                                  table_columns=table_columns,
                                  discoverer_mode=discoverer_mode,
                                  extra_url_parameters=extra_url_parameters)

    elif view_mode == 'view_unspecified_table_organizations':
        # Some organizations have a large number of neighbors, but we will only show
        # 'max_nr_items' in the table. Therefore, reduce the number of neighbors when
        # searching for persons in an organization. Don't do this for other view_modes, because
        # in that case the table shows how many items are found.
        neighbor_nodes = get_all_neighbor_nodes(node=node,
                                                name_want=name_list,
                                                category_want=category_list,
                                                max_nr_neighbor_nodes=max_nr_items)
        table_header = 'This is all information related to this organization:'
        html += get_page_title(title='All information related to this organization')
        html += node_found
        if discoverer_mode == 'details_view':
            html += get_faceted_table(parent_node=node,
                                      neighbor_nodes=neighbor_nodes,
                                      table_header=table_header,
                                      table_columns=table_columns_resout,
                                      view_mode=view_mode,
                                      discoverer_mode=discoverer_mode,
                                      extra_url_parameters=extra_url_parameters)
        else:
            html += get_tabbed_table(nodes_list=neighbor_nodes,
                                     table_header=table_header,
                                     table_columns=table_columns_resout,
                                     tabs_on='category',
                                     discoverer_mode=discoverer_mode,
                                     extra_url_parameters=extra_url_parameters)

    elif view_mode == 'view_unspecified_table_resouts' \
            or view_mode == 'view_unspecified_table_everything_except_ids':
        personroot_node = get_personroot_node(node=node)
        neighbor_nodes = get_all_neighbor_nodes(node=personroot_node,
                                                name_want=name_list,
                                                category_want=category_list)
        if view_mode == 'view_unspecified_table_resouts':
            table_header = 'These are the research results related to this person:'
        else:
            table_header = 'These are all the neighbors related to this person (without its identities):'
        html += get_page_title(title='Research results related to this person')
        html += node_found
        if discoverer_mode == 'details_view':
            html += get_faceted_table(parent_node=node,
                                      neighbor_nodes=neighbor_nodes,
                                      table_header=table_header,
                                      table_columns=table_columns_resout,
                                      view_mode=view_mode,
                                      discoverer_mode=discoverer_mode,
                                      extra_url_parameters=extra_url_parameters)
        else:
            html += get_tabbed_table(nodes_list=neighbor_nodes,
                                     table_header=table_header,
                                     table_columns=table_columns_resout,
                                     tabs_on='category',
                                     discoverer_mode=discoverer_mode,
                                     extra_url_parameters=extra_url_parameters)

    elif view_mode == 'view_unspecified_table_everything':
        personroot_node = get_personroot_node(node=node)
        html += get_page_title(title='All information related to this person')
        html += node_found
        neighbor_nodes_personal = get_all_neighbor_nodes(node=personroot_node,
                                                         category_want=personal_types_all)
        neighbor_nodes_remainder = get_all_neighbor_nodes(node=personroot_node,
                                                          name_want=name_list,
                                                          category_want=category_list)
        if discoverer_mode == 'details_view':
            html += get_tabbed_table(nodes_list=neighbor_nodes_personal,
                                     table_header='This is personal information related to this person:',
                                     table_columns=table_columns_ids,
                                     tabs_on='name',
                                     discoverer_mode=discoverer_mode,
                                     extra_url_parameters=extra_url_parameters)
            html += get_faceted_table(parent_node=node,
                                      neighbor_nodes=neighbor_nodes_remainder,
                                      table_header='This is other information related to this person:',
                                      table_columns=table_columns_resout,
                                      view_mode=view_mode,
                                      discoverer_mode=discoverer_mode,
                                      extra_url_parameters=extra_url_parameters)
        else:
            html += view_personal_information(nodes_list=neighbor_nodes_personal,
                                              discoverer_mode=discoverer_mode,
                                              extra_url_parameters=extra_url_parameters)
            html += get_tabbed_table(nodes_list=neighbor_nodes_remainder,
                                     table_header='This is other information related to this person:',
                                     table_columns=table_columns_resout,
                                     tabs_on='category',
                                     discoverer_mode=discoverer_mode,
                                     extra_url_parameters=extra_url_parameters)

    elif view_mode == 'view_regular_table_person_share_resouts':
        # Note the hard limit.
        html += get_page_title(title='Persons that share research results with this person')
        html += find_person_share_resouts(parent_node=node,
                                          category_want_list=category_list,
                                          category_dontwant_list=['person', 'competence', 'organization'],
                                          discoverer_mode=discoverer_mode,
                                          extra_url_parameters=extra_url_parameters)

    elif view_mode == 'view_regular_table_person_enrich_source_system':
        # Note: we misuse the field 'category_list' to pass the name of the source system
        # we would like to enrich.
        if len(category_list) == 0:
            source_system = ''
        else:
            source_system = str(category_list[0])
        html += get_page_title(title='Information harvested from other source systems, not present in this source system')
        html += find_enrich_candidates(parent_node=node,
                                       source_system=source_system,
                                       discoverer_mode=discoverer_mode,
                                       extra_url_parameters=extra_url_parameters)

    elif view_mode == 'view_regular_table_person_organization_collaborations':
        html += get_page_title(title='Organizations that this person collaborates with')
        html += find_person_organization_collaborations(parent_node=node,
                                                        discoverer_mode=discoverer_mode,
                                                        extra_url_parameters=extra_url_parameters)

    elif view_mode == 'view_regular_table_organization_addinfo':
        # Note the hard limit.
        html += get_page_title(title='Information about this organization')
        html += find_organization_additional_info(parent_node=node,
                                                  name_list=name_list,
                                                  category_list=category_list,
                                                  discoverer_mode=discoverer_mode,
                                                  extra_url_parameters=extra_url_parameters)
    elif view_mode == 'view_regular_table_overlap':
        html += get_page_title(title='Overlap in source systems for the neighbor nodes of this node')
        html += find_overlap_in_source_systems(name=node['name'],
                                               category=node['category'],
                                               value=node['value'],
                                               discoverer_mode=discoverer_mode,
                                               overlap_mode='neighbornodes',
                                               extra_url_parameters=extra_url_parameters)

    # Note: view_mode == 'view_regular_table_overlap_records' is caught in resultspage().

    else:
        html += get_message(message='create_results_page(): Unknown view_mode "' + view_mode + '".')
    return html


# ################################################
# Ricgraph Explorer initialization.
# ################################################
def store_global_in_app_context(ricgraph_explorer_app: FlaskApp, name: str, value) -> None:
    """Stores a global variable in the app context.
    This is required, otherwise we don't have them if we e.g. do
    a second REST API call.

    :param ricgraph_explorer_app: The FlaskApp ricgraph_explorer.
    :param name: the name of the global.
    :param value: the value of the global.
    :return: None.
    """
    with ricgraph_explorer_app.app.app_context():
        ricgraph_explorer_app.app.config[name] = value
    return


def get_all_globals_from_app_context() -> None:
    """Get all global variables from the app context.

    :return: None.
    """
    # This function cannot be moved to a separate file since we need
    # all the globals that we get from the app context in this file.
    global graph
    global name_all, name_personal_all, category_all, source_all, resout_types_all
    global name_all_datalist, category_all_datalist, source_all_datalist, resout_types_all_datalist
    global personal_types_all, remainder_types_all
    global privacy_statement_link, privacy_measures_link
    global homepage_intro_html

    if 'graph' in current_app.config:
        graph = current_app.config.get('graph')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "graph".')
        exit(2)
    if 'name_all' in current_app.config:
        name_all = current_app.config.get('name_all')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "name_all".')
        exit(2)
    if 'name_personal_all' in current_app.config:
        name_personal_all = current_app.config.get('name_personal_all')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "name_personal_all".')
        exit(2)
    if 'category_all' in current_app.config:
        category_all = current_app.config.get('category_all')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "category_all".')
        exit(2)
    if 'source_all' in current_app.config:
        source_all = current_app.config.get('source_all')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "source_all".')
        exit(2)
    if 'resout_types_all' in current_app.config:
        resout_types_all = current_app.config.get('resout_types_all')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "resout_types_all".')
        exit(2)
    if 'name_all_datalist' in current_app.config:
        name_all_datalist = current_app.config.get('name_all_datalist')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "name_all_datalist".')
        exit(2)
    if 'category_all_datalist' in current_app.config:
        category_all_datalist = current_app.config.get('category_all_datalist')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "category_all_datalist".')
        exit(2)
    if 'source_all_datalist' in current_app.config:
        source_all_datalist = current_app.config.get('source_all_datalist')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "source_all_datalist".')
        exit(2)
    if 'resout_types_all_datalist' in current_app.config:
        resout_types_all_datalist = current_app.config.get('resout_types_all_datalist')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "resout_types_all_datalist".')
        exit(2)
    if 'personal_types_all' in current_app.config:
        personal_types_all = current_app.config.get('personal_types_all')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "personal_types_all".')
        exit(2)
    if 'remainder_types_all' in current_app.config:
        remainder_types_all = current_app.config.get('remainder_types_all')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "remainder_types_all".')
        exit(2)
    if 'privacy_statement_link' in current_app.config:
        privacy_statement_link = current_app.config.get('privacy_statement_link')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "privacy_statement_link".')
        exit(2)
    if 'privacy_measures_link' in current_app.config:
        privacy_measures_link = current_app.config.get('privacy_measures_link')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "privacy_measures_link".')
        exit(2)
    if 'homepage_intro_html' in current_app.config:
        homepage_intro_html = current_app.config.get('homepage_intro_html')
    else:
        print('get_all_globals_from_app_context(): Error, cannot find global "homepage_intro_html".')
        exit(2)
    return


# ################################################
# #### Entry point for WSGI Gunicorn server   ####
# #### using Uvicorn for ASGI applications    ####
# ################################################
def create_ricgraph_explorer_app():
    global page_footer, ricgraph_explorer

    initialize_ricgraph_explorer(ricgraph_explorer_app=ricgraph_explorer)
    page_footer = ''
    if privacy_statement_link != '' or privacy_measures_link != '':
        page_footer = '<footer class="w3-container rj-gray" style="font-size:80%">'
        page_footer += privacy_statement_link
        page_footer += privacy_measures_link
        page_footer += '</footer>'
    page_footer += page_footer_wsgi

    return ricgraph_explorer


# ############################################
# ################### main ###################
# ############################################
if __name__ == "__main__":
    initialize_ricgraph_explorer(ricgraph_explorer_app=ricgraph_explorer)
    page_footer = ''
    if privacy_statement_link != '' or privacy_measures_link != '':
        page_footer = '<footer class="w3-container rj-gray" style="font-size:80%">'
        page_footer += privacy_statement_link
        page_footer += privacy_measures_link
        page_footer += '</footer>'
    page_footer += page_footer_development

    ricgraph_explorer.run(port=3030)
