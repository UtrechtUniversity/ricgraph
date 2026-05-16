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
# Extended Rik D.T. Janssen, February, September 2023 to June 2025.
# Extended Rik D.T. Janssen, November 2025, March 2026.
#
# ##############################################################################


from os import path
from connexion import FlaskApp, options
from flask import send_from_directory, redirect, url_for, Response
from neo4j.graph import Node
from ricgraph import (read_all_nodes,
                      get_personroot_node, get_all_neighbor_nodes,
                      check_valid_year,
                      get_year_range_text,
                      RESEARCHRESULT_CATEGORY_PUBLICATION,
                      RESEARCHRESULT_CATEGORY_PUBLICATION_ALL,
                      PERSON_CATEGORY_PERSON,
                      ORGANIZATION_CATEGORY_ORGANISATION,
                      ORGANIZATION_CATEGORY_ALL,
                      COMPETENCE_CATEGORY_COMPETENCE,
                      PERSON_NAME_PERSON_ROOT,
                      PageParams, QueryParams)
from ricgraph_explorer_constants import (RICGRAPH_EXPLORER_DEBUG_PORT,
                                         RICGRAPH_EXPLORER_RUNMODE_GUNICORN,
                                         RICGRAPH_EXPLORER_RUNMODE_DEBUG,
                                         RICGRAPH_CACHEINFO,
                                         RICGRAPH_HARVESTINFO,
                                         RICGRAPH_HARVESTINFO_INTERNAL,
                                         RICGRAPH_NODEINFO,
                                         RICGRAPH_NODEINFO_INTERNAL,
                                         RICGRAPH_SYSTEMINFO,
                                         html_body_start, html_body_end,
                                         button_style, button_width,
                                         form_button_on_one_line_style,
                                         TABLE_DETAIL_COLUMNS,
                                         TABLE_ID_COLUMNS,
                                         TABLE_ORGANIZATION_COLUMNS,
                                         TABLE_RESEARCH_OUTPUT_COLUMNS,
                                         DISCOVERER_MODE_DETAILS,
                                         DISCOVERER_MODE_PERSONS,
                                         SEARCH_MODE_EXACT_MATCH, SEARCH_MODE_VALUE,
                                         SEARCH_STRING_MIN_LENGTH,
                                         ORIGIN_OPEN_SCIENCE_PROFILE_BUTTON,
                                         ORIGIN_OPEN_SCIENCE_DASHBOARD_BUTTON,
                                         ORIGIN_DEFAULT_BUTTON,
                                         OVERLAP_MODE_NEIGHBORNODE)
from ricgraph_explorer_init import initialize_ricgraph_explorer
from ricgraph_explorer_graphdb import (find_overlap_in_source_systems,
                                       find_overlap_in_source_systems_records,
                                       find_person_share_resouts,
                                       find_enrich_candidates,
                                       find_person_organization_collaborations,
                                       find_organization_additional_info)
from ricgraph_explorer_utils import (get_html_for_cardstart, get_html_for_cardend,
                                     create_html_form,
                                     get_message, get_found_message,
                                     get_you_searched_for_card, get_page_title,
                                     get_html_for_yearcard,
                                     get_global_list, get_global_str,
                                     get_page_footer,
                                     get_url_page_params, get_url_query_params,
                                     merge_and_remove_empty)
from ricgraph_explorer_table import (get_regular_table,
                                     view_personal_information,
                                     get_faceted_table, get_tabbed_table)
from ricgraph_explorer_osl import (_oslpage_bp, _osprofileresultpage_bp,
                                   _osdashboardresultpage_bp)
from ricgraph_explorer_collabs import _collabspage_bp, _collabsresultpage_bp
from ricgraph_explorer_topics import _topicspage_bp
# In PyCharm, the import below generates an "Unused import statement", but it is
# required. PyCharm doesn't seem to understand the line _ricgraph_explorer.add_api() below.
from ricgraph_explorer_restapi import (_restapidocpage_bp,
                                       api_search_person, api_person_all_information,
                                       api_person_share_researchresults,
                                       api_person_collaborating_organizations,
                                       api_search_organization, api_organization_all_information,
                                       api_organization_information_persons_results,
                                       api_person_enrich, api_organization_enrich,
                                       api_search_competence, api_competence_all_information,
                                       api_explore_collaborations,
                                       api_broad_search, api_advanced_search,
                                       api_get_all_personroot_nodes, api_get_all_neighbor_nodes,
                                       api_get_ricgraph_info)


# We don't show the Swagger REST API page, we use RapiDoc for that (see restapidocpage()
# endpoint below). '_swagger_ui_options' is taken from
# https://connexion.readthedocs.io/en/latest/swagger_ui.html#connexion.options.SwaggerUIOptions.
# 'swagger_ui_config' options are on this page:
# https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration
_swagger_ui_options = options.SwaggerUIOptions(swagger_ui=False)
_ricgraph_explorer = FlaskApp(import_name=__name__,
                              specification_dir='./static/',
                              swagger_ui_options=_swagger_ui_options)
# Disable key sorting on the underlying Flask app.
# This ensures that the JSON output from the REST API is in the order
# I would like to have it.
_ricgraph_explorer.app.json.sort_keys = False
_ricgraph_explorer.add_api(specification='openapi.yaml',
                           swagger_ui_options=_swagger_ui_options)

_ricgraph_explorer.app.register_blueprint(blueprint=_oslpage_bp)
_ricgraph_explorer.app.register_blueprint(blueprint=_osprofileresultpage_bp)
_ricgraph_explorer.app.register_blueprint(blueprint=_osdashboardresultpage_bp)
_ricgraph_explorer.app.register_blueprint(blueprint=_collabspage_bp)
_ricgraph_explorer.app.register_blueprint(blueprint=_collabsresultpage_bp)
_ricgraph_explorer.app.register_blueprint(blueprint=_topicspage_bp)
_ricgraph_explorer.app.register_blueprint(blueprint=_restapidocpage_bp)


# ##############################################################################
# Favicon
# ##############################################################################
@_ricgraph_explorer.route('/favicon.ico')
def favicon():
    return send_from_directory(path.join(str(_ricgraph_explorer.app.root_path), 'static'),
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
#
# 5. oslpage, this page allows to do open science landscaping.
# 6. topicspage, this page allows to explore topics.
# ##############################################################################
@_ricgraph_explorer.route(rule='/')
def homepage() -> str:
    """Ricgraph Explorer entry, the home page, when you access '/'.

    Possible url parameters are:
    - none.

    :return: HTML to be rendered.
    """
    html = html_body_start
    html += get_page_title(title='Ricgraph - Research in context graph')
    html += get_html_for_cardstart()
    html += 'Ricgraph, also known as '
    html += '<a href="https://www.ricgraph.eu" target="_blank">'
    html += 'Research in context graph</a>, enables the exploration of persons, '
    html += 'teams, their results, (sub-)organizations, '
    html += 'collaborations, skills, projects, and the relations between these items. '
    html += 'Ricgraph can store many types of items into a single graph (network). '
    html += 'These items can be obtained from various systems and from '
    html += 'multiple organizations. '
    html += 'Ricgraph facilitates reasoning about these '
    html += 'items because it infers new relations between items, '
    html += 'relations that are not present in any of the separate source systems. '
    html += 'It is flexible and extensible, and can be adapted to new application areas. '
    html += 'Persons are only included in Ricgraph if they have at least '
    html += 'one person identifier (such as ORCID, ISNI, or a source system identifier) '
    html += 'in the source systems harvested.'

    html += get_global_str(ricgraph_info=RICGRAPH_SYSTEMINFO,
                           item='homepage_intro_html')

    html += '<h1>Start exploring</h1>'
    html += 'You can use Ricgraph Explorer to explore Ricgraph. '
    html += 'There are various methods to start exploring:'
    html += '<p/>'
    html += '<div ' + form_button_on_one_line_style + '>'
    html += create_html_form(destination='searchpage',
                             button_text='search for a person',
                             hidden_fields={'search_mode': SEARCH_MODE_VALUE,
                                            'name': 'FULL_NAME',
                                            'category': PERSON_CATEGORY_PERSON
                                            })
    html += create_html_form(destination='searchpage',
                             button_text='search for a (sub-)organization',
                             hidden_fields={'search_mode': SEARCH_MODE_VALUE,
                                            'category': ORGANIZATION_CATEGORY_ORGANISATION,
                                            })
    if COMPETENCE_CATEGORY_COMPETENCE in get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                                         item='category_active'):
        html += create_html_form(destination='searchpage',
                                 button_text='search for a skill, expertise area or research area',
                                 hidden_fields={'search_mode': SEARCH_MODE_VALUE,
                                                'category': COMPETENCE_CATEGORY_COMPETENCE,
                                                })
    html += '</div>'
    html += '<p/>'
    html += '<div ' + form_button_on_one_line_style + '>'
    html += create_html_form(destination='collabspage.collabspage',
                             button_text='explore collaborations')
    html += create_html_form(destination='oslpage.oslpage',
                             button_text='explore the open science landscape')
    html += '</div>'
    html += '<p/>'
    if 'topic' in get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                  item='category_active'):
        html += create_html_form(destination='topicspage.topicspage',
                                 button_text='explore topics')
        html += '<p/>'
    html += '<div ' + form_button_on_one_line_style + '>'
    html += create_html_form(destination='searchpage',
                             button_text='search for anything (broad search)',
                             hidden_fields={'search_mode': SEARCH_MODE_VALUE
                                            })
    html += create_html_form(destination='searchpage',
                             button_text='advanced search',
                             hidden_fields={'search_mode': SEARCH_MODE_EXACT_MATCH
                                            })
    html += '</div>'
    html += get_html_for_cardend()

    html += get_html_for_cardstart()
    html += '<h1>About Ricgraph</h1>'
    html += 'More information:'
    html += '<ul>'
    html += '<li>'
    html += 'For a gentle introduction in Ricgraph, please read the reference publication: '
    html += 'Rik D.T. Janssen (2024). Ricgraph: A flexible and extensible graph to explore research in '
    html += 'context from various systems. <em>SoftwareX</em>, 26(101736). '
    html += '<a href="https://doi.org/10.1016/j.softx.2024.101736"'
    html += 'target="_blank">doi.org/10.1016/j.softx.2024.101736</a>. '
    html += '</li>'
    html += '<li>'
    html += 'To read more about visualizing collaborations between (sub-)organizations '
    html += 'in Ricgraph, please read '
    html += 'Rik D.T. Janssen (2025). Utilizing Ricgraph to gain insights into '
    html += 'research collaborations across institutions, at every organizational '
    html += 'level. [preprint]. <a href="https://doi.org/10.2139/ssrn.5524439">'
    html += 'https://doi.org/10.2139/ssrn.5524439</a>.'
    html += '</li>'
    html += '<li>'
    html += 'Extensive documentation, publications, videos and source code can be found in the GitHub repository '
    html += '<a href="https://github.com/UtrechtUniversity/ricgraph"'
    html += 'target="_blank">github.com/UtrechtUniversity/ricgraph</a>. '
    html += '</li>'
    html += '<li>'
    html += 'If you use or refer to Ricgraph, please cite both the reference publication '
    html += '(<a href="https://doi.org/10.1016/j.softx.2024.101736"'
    html += 'target="_blank">doi.org/10.1016/j.softx.2024.101736</a>), '
    html += 'and the software '
    html += '(<a href="https://doi.org/10.5281/zenodo.7524314"'
    html += 'target="_blank"">doi.org/10.5281/zenodo.7524314</a>).'
    html += '</li>'
    html += '</ul>'
    html += '<br/>'
    html += 'What to find in this instance of Ricgraph:'
    html += '<ul>'
    html += '<li>'
    html += 'Items from the following source systems: '
    source_active = get_global_list(ricgraph_info=RICGRAPH_HARVESTINFO,
                                    item='source_active')
    if len(source_active) == 0:
        html += '[no source systems harvested yet]'
    else:
        html += ', '.join([str(source) for source in source_active])
    html += '.'
    html += '</li>'
    html += '<li>'
    html += 'Types of items: '
    name_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                  item='name_active')
    if len(name_active) == 0:
        html += '[no items yet]'
    else:
        html += ', '.join([str(name) for name in name_active])
    html += '.'
    html += '</li>'
    html += '<li>'
    html += 'Types of items that contain personal data: '
    person_name_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                         item='person_name_active')
    if len(person_name_active) == 0:
        html += '[no items that contain personal data yet]'
    else:
        html += ', '.join([str(person_name) for person_name in person_name_active])
    html += '.'
    html += '</li>'
    html += '<li>'
    html += get_global_str(ricgraph_info=RICGRAPH_HARVESTINFO,
                           item='nr_nodes')
    html += ' nodes and '
    html += get_global_str(ricgraph_info=RICGRAPH_HARVESTINFO,
                           item='nr_edges')
    html += ' edges, '
    harvest_date = get_global_str(ricgraph_info=RICGRAPH_HARVESTINFO,
                                  item='harvest_date')
    if harvest_date == '':
        html += 'nothing has been harvested yet.'
    else:
        html += 'harvested on ' + harvest_date + '.'
    html += '</li>'
    html += '<li>'
    html += 'Ricgraph uses a '
    html += get_global_str(ricgraph_info=RICGRAPH_CACHEINFO,
                           item='cache_name')
    html += '. This cache has '
    html += get_global_str(ricgraph_info=RICGRAPH_CACHEINFO,
                           item='nr_items')
    html += ' elements, and its size is '
    html += get_global_str(ricgraph_info=RICGRAPH_CACHEINFO,
                           item='size_kb')
    html += ' kB.'
    html += '</li>'
    html += '</ul>'

    html += get_global_str(ricgraph_info=RICGRAPH_SYSTEMINFO,
                           item='homepage_outro_html')

    html += get_html_for_cardend()
    html += get_page_footer() + html_body_end
    return html


@_ricgraph_explorer.route(rule='/searchpage/', methods=['GET'])
def searchpage() -> str:
    """Ricgraph Explorer entry, this 'page' shows the search form, both the
    exact match search form and the broad search on the 'value' field form.

    Possible url parameters are:
    - name: name of the nodes to find.
    - category: category of the nodes to find.
    - origin: optional, specifies where the request for this page originates from.
    - search_mode: the search_mode to use, 'exact_match' or 'value_search' (broad
      search on field 'value').
    - discoverer_mode: the discoverer_mode to use, 'details_view' to see all details,
      or 'person_view' to have a nicer layout.
    - max_nr_items: the maximum number of items to return, or 0 to return all items.

    :return: HTML to be rendered.
    """
    page_params = get_url_page_params()
    query_params = get_url_query_params()
    form = '<form method="get" action="' + url_for(endpoint='optionspage') + '">'
    if page_params['search_mode'] == SEARCH_MODE_EXACT_MATCH:
        form += '<label for="name">Search for a value in Ricgraph field <em>name</em>:</label>'
        form += '<input id="name" class="w3-input w3-border" list="name_active_datalist"'
        form += 'name=name autocomplete=off>'
        form += '<div class="firefox-only">Click twice to get a dropdown list.</div>'
        form += get_global_str(ricgraph_info=RICGRAPH_NODEINFO_INTERNAL,
                               item='name_active_datalist')
        form += '<br/>'

        form += '<label for="category">Search for a value in Ricgraph field <em>category</em>:</label>'
        form += '<input id="category" class="w3-input w3-border" list="category_active_datalist"'
        form += 'name=category autocomplete=off>'
        form += '<div class="firefox-only">Click twice to get a dropdown list.</div>'
        form += get_global_str(ricgraph_info=RICGRAPH_NODEINFO_INTERNAL,
                               item='category_active_datalist')
        form += '<br/>'
    if page_params['search_mode'] == SEARCH_MODE_VALUE and query_params['name'] != '':
        form += '<input id="name" type="hidden" name="name" value="' + query_params['name'] + '">'
    if page_params['search_mode'] == SEARCH_MODE_VALUE and query_params['category'] != '':
        form += '<input id="category" type="hidden" name="category" value="' + query_params['category'] + '">'
    if page_params['search_mode'] == SEARCH_MODE_EXACT_MATCH:
        form += '<label for="value">Search for a value in Ricgraph field <em>value</em>:</label>'
    else:
        form += '<label for="value">Type your search string:</label>'
    form += '<input id="value" class="w3-input w3-border" type=text name=value>'
    form += '<input type="hidden" name="search_mode" value="' + page_params['search_mode'] + '">'
    if page_params['origin'] != '':
        form += '<input type="hidden" name="origin" value="' + page_params['origin'] + '">'

    if page_params['search_mode'] == SEARCH_MODE_EXACT_MATCH:
        form += 'These fields are case-sensitive and use exact match search. '
        form += 'If you enter values in more than one field, these fields are combined using AND.</br>'

    # April 3, 2026: I disable the year form since here seems a confusing place.
    # # 14.5em is half of 'field_button_width' (a constant from
    # # ricgraph_explorer_constants.py, the width of the text & input fields
    # # on this page) minus 1em for the spacing between the input fields for year.
    # form_button_width = ' style="width:14.5em !important;" '
    #
    # form += '<br/>'
    # form += 'If your search involves research results, you can specify their first and last year:'
    # form += '<div ' + form_button_on_one_line_style + '>'
    # form += '<div' + form_button_width + '>'
    # form += '<label for="year_first">first year of research result:</label>'
    # form += '<input id="year_first" class="w3-input w3-border" list="year_active_datalist"'
    # form += 'name=year_first autocomplete=off' + form_button_width + '>'
    # form += '<div class="firefox-only">Click twice to get a dropdown list.</div>'
    # form += year_active_datalist
    # form += '</div>'
    # form += '<div' + form_button_width + '>'
    # form += '<label for="year_last">last year of research result:</label>'
    # form += '<input id="year_last" class="w3-input w3-border" list="year_active_datalist"'
    # form += 'name=year_last autocomplete=off' + form_button_width + '>'
    # form += '<div class="firefox-only">Click twice to get a dropdown list.</div>'
    # form += year_active_datalist
    # form += '</div>'
    # form += '</div>'

    radio_person_text = ' <em>person_view</em>: only show relevant columns, '
    radio_person_text += 'results are presented in a <em>tabbed</em> format '
    radio_person_tooltip = '<img src="/static/images/circle_info_solid_uuyellow.svg" alt="Click for more information">'
    radio_person_tooltip += '<div class="w3-text" style="margin-left:60px;">'
    radio_person_tooltip += 'This view presents results in a <em>tabbed</em> format. '
    radio_person_tooltip += 'Also, tables have fewer columns to reduce information overload. '
    if COMPETENCE_CATEGORY_COMPETENCE in get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                                         item='category_active'):
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
    if page_params['discoverer_mode'] == DISCOVERER_MODE_PERSONS:
        form += 'checked'
    form += '>' + radio_person_text
    form += '<label for="person_view" class="w3-tooltip">' + radio_person_tooltip + '</label><br/>'
    form += '<input id="details_view" class="w3-radio" type="radio" name="discoverer_mode" value="details_view"'
    if page_params['discoverer_mode'] == DISCOVERER_MODE_DETAILS:
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
    form += '<input id="max_nr_items" class="w3-input w3-border" type=text value='
    form += str(query_params['max_nr_items']) + ' name=max_nr_items>'

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
    form += '<input id="max_nr_table_rows" class="w3-input w3-border" type=text value='
    form += str(page_params['max_nr_table_rows']) + ' name=max_nr_table_rows>'

    form += '<br/><input class="' + button_style + '" ' + button_width + ' type=submit value=search>'
    form += '</form>'

    html = html_body_start
    if page_params['search_mode'] == SEARCH_MODE_EXACT_MATCH:
        html += get_page_title(title='Advanced search page')
    else:
        if query_params['category'] == '':
            html += get_page_title(title='Search page')
        else:
            html += get_page_title(title='Search page for ' + query_params['category'])
    html += get_html_for_cardstart()
    html += form
    html += get_html_for_cardend()
    html += get_page_footer() + html_body_end
    return html


@_ricgraph_explorer.route(rule='/optionspage/', methods=['GET'])
def optionspage() -> str | Response:
    """Ricgraph Explorer entry, this 'page' only uses URL parameters.
    Find nodes based on URL parameters passed.

    Possible url parameters are:
    - key: key of the nodes to find. If present, this field is preferred above
      'name', 'category' or 'value'.
    - name: name of the nodes to find.
    - category: category of the nodes to find.
    - value: value of the nodes to find.
    - year_first: first year of the research results to count.
    - year_last: last year of the research results to count.
    - origin: optional, specifies where the request for this page originates from.
    - search_mode: the search_mode to use, 'exact_match' or 'value_search' (broad
      search on field 'value').
    - discoverer_mode: the discoverer_mode to use, 'details_view' to see all details,
      or 'person_view' to have a nicer layout.
    - max_nr_items: the maximum number of items to return, or 0 to return all items.
    - max_nr_table_rows: the maximum number of rows in a table to return (the page
      size of the table), or 0 to return all rows.

    :return: HTML to be rendered.
    """
    page_params = get_url_page_params()
    query_params = get_url_query_params()
    html = html_body_start
    if (message := check_valid_year(year_first=query_params['year_first'],
                                    year_last=query_params['year_last'])) != '':
        html += get_message(message=message)
        return html + get_page_footer() + html_body_end

    if query_params['name'] == '' and query_params['category'] == '' \
       and query_params['value'] == '' and query_params['key'] == '':
        html += get_message(message='Ricgraph Explorer could not find anything.')
        html += get_page_footer() + html_body_end
        return html

    # Not necessary to check if the node ('key') is in the cache, that is done in
    # read_all_nodes() --> cypher_read_node(). It will also be added to the cache
    # in cypher_read_node() if not present yet.
    if query_params['key'] != '':
        result = read_all_nodes(key=query_params['key'])
    elif page_params['search_mode'] == SEARCH_MODE_EXACT_MATCH:
        result = read_all_nodes(name=query_params['name'],
                                category=query_params['category'],
                                value=query_params['value'],
                                max_nr_nodes=query_params['max_nr_items'])
    else:
        if len(query_params['value']) < SEARCH_STRING_MIN_LENGTH:
            html += get_message(message='The search string should be at least '
                                        + str(SEARCH_STRING_MIN_LENGTH) + ' characters.')
            html += get_page_footer() + html_body_end
            return html
        if query_params['name'] == 'FULL_NAME':
            # We also need to search on FULL_NAME_ASCII, therefore the 'name_is_exact_match = False'.
            result = read_all_nodes(name=query_params['name'],
                                    category=query_params['category'],
                                    value=query_params['value'],
                                    name_is_exact_match=False,
                                    value_is_exact_match=False,
                                    max_nr_nodes=query_params['max_nr_items'])
        else:
            result = read_all_nodes(name=query_params['name'],
                                    category=query_params['category'],
                                    value=query_params['value'],
                                    value_is_exact_match=False,
                                    max_nr_nodes=query_params['max_nr_items'])
    if len(result) == 0:
        # We didn't find anything.
        html += get_message(message='Ricgraph Explorer could not find anything.')
        html += get_page_footer() + html_body_end
        return html
    if len(result) > 1:
        html += get_page_title(title='Selection page')
        table_header = 'Your search resulted in more than one item. Please choose one item to continue:'
        html += get_regular_table(nodes_list=result,
                                  page_params=page_params,
                                  query_params=query_params,
                                  table_header=table_header)
        html += get_page_footer() + html_body_end
        return html

    node = result[0]
    if page_params['origin'] == ORIGIN_OPEN_SCIENCE_PROFILE_BUTTON \
       or page_params['origin'] == ORIGIN_OPEN_SCIENCE_DASHBOARD_BUTTON:
        # If we have reached this point, and we came here using the
        # button 'get an open science profile for a (sub-)organization'
        # on page oslpage(), then skip the options page and go directly
        # to the osprofileresult() page. Reset 'origin'.
        merged = merge_and_remove_empty(page_params=page_params,
                                        query_params=query_params) | {'key': node['_key'],
                                                                      'origin': ORIGIN_DEFAULT_BUTTON}
        if page_params['origin'] == ORIGIN_OPEN_SCIENCE_PROFILE_BUTTON:
            return redirect(url_for(endpoint='osprofileresultpage.osprofileresultpage',
                                    **merged))
        elif page_params['origin'] == ORIGIN_OPEN_SCIENCE_DASHBOARD_BUTTON:
            return redirect(url_for(endpoint='osdashboardresultpage.osdashboardresultpage',
                                    **merged))
        else:
            html += get_message(message='optionspage(): Error, this cannot happen.')
            html += get_page_footer() + html_body_end

    html += create_options_page(node=node,
                                page_params=page_params,
                                query_params=query_params)
    html += get_page_footer() + html_body_end
    return html


@_ricgraph_explorer.route(rule='/resultspage/', methods=['GET'])
def resultspage() -> str:
    """Ricgraph Explorer entry, this 'page' only uses URL parameters.
    View the results based on the values passed.
    This function is tied to create_results_page(), where, depending on the
    value of 'view_mode', is determined what will be viewed.
    This function will only be called with one node, so we can use 'key' to find it.

    Possible url parameters are:
    - view_mode: determines what will be shown in create_results_page().
      This view_mode is first set in create_options_page(), and then
      caught first in resultspage() and then in create_results_page().
    - key: key of the nodes to find.
    - year_first: first year of the research results to count.
    - year_last: last year of the research results to count.
    - discoverer_mode: the discoverer_mode to use, 'details_view' to see all details,
      or 'person_view' to have a nicer layout.
    - name_list: either a string which indicates that we only want neighbor
      nodes where the property 'name' is equal to 'name_list'
      (e.g. 'ORCID'), or a list containing several node names, indicating
      that we want all neighbor nodes where the property 'name' equals
      one of the names in the list 'name_list' (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty (empty string), return all nodes.
    - category_list: similar to 'name_list', but now for the property 'category'.
    - view_mode: indicates which page to create in create_results_page().
    - max_nr_items: the maximum number of items to return, or 0 to return all items.
    - max_nr_table_rows: the maximum number of rows in a table to return (the page
      size of the table), or 0 to return all rows.

    :return: HTML to be rendered.
    """
    page_params = get_url_page_params()
    query_params = get_url_query_params()

    html = html_body_start
    if (message := check_valid_year(year_first=query_params['year_first'],
                                    year_last=query_params['year_last'])) != '':
        html += get_message(message=message)
        return html + get_page_footer() + html_body_end

    html += create_results_page(page_params=page_params,
                                query_params=query_params)

    html += get_page_footer() + html_body_end
    return html


# ##############################################################################
# Other page handling functions.
# ##############################################################################
def create_options_page(node: Node,
                        page_params: PageParams,
                        query_params: QueryParams) -> str:
    """This function creates the page with options to choose from, depending on the
    choice the user has made on the index page.
    The 'view_mode' that is used, is caught first in resultspage() and then
    in create_results_page().

    :param node: the node that is found and that determines the possible choices.
    :param page_params: parameters related to the page passed in the URL.
    :param query_params: parameters related to the query passed in the URL.
    :return: HTML to be rendered.
    """
    # Note: This function gets a 'node', then it extracts '_key' from
    # node, and passes the key to create_result_page(), which then again
    # retrieves the node (from the cache). This is one time too many,
    # but nodes cannot be passed using HTML forms, so we have to live with it.

    if node is None:
        return get_message(message='create_options_page(): Node is None. This should not happen.')

    html_options_page = ''
    if page_params['discoverer_mode'] == DISCOVERER_MODE_DETAILS:
        html_options_page += get_you_searched_for_card(page_params=page_params,
                                                       query_params=query_params)
    html_options_page += get_page_title(title='Options page')
    html_options_page += get_found_message(node=node,
                                           page_params=page_params,
                                           query_params=query_params)
    if node['category'] == ORGANIZATION_CATEGORY_ORGANISATION:
        result_html = create_options_page_organization(node=node,
                                                       page_params=page_params,
                                                       query_params=query_params)
        return html_options_page + result_html
    elif node['category'] == PERSON_CATEGORY_PERSON:
        result_html = create_options_page_person(node=node,
                                                 page_params=page_params,
                                                 query_params=query_params)
        return html_options_page + result_html
    else:
        result_html = create_results_page(page_params=page_params
                                                      | {'view_mode': 'view_regular_table_category'},
                                          query_params=query_params
                                                       | {'key': node['_key']})
    return result_html


def create_options_page_organization(node: Node,
                                     page_params: PageParams,
                                     query_params: QueryParams) -> str:
    """This function creates the page with options to choose from,
    for an organization, depending on the
    choice the user has made on the index page.
    The 'view_mode' that is used, is caught first in resultspage() and then
    in create_results_page().

    :param node: the node that is found and that determines the possible choices.
    :param page_params: parameters related to the page passed in the URL.
    :param query_params: parameters related to the query passed in the URL.
    :return: HTML to be rendered.
    """
    name_active_datalist = get_global_str(ricgraph_info=RICGRAPH_NODEINFO_INTERNAL,
                                          item='name_active_datalist')
    category_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                      item='category_active')
    category_active_datalist = get_global_str(ricgraph_info=RICGRAPH_NODEINFO_INTERNAL,
                                              item='category_active_datalist')
    researchresult_category_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                                     item='researchresult_category_active')
    key = node['_key']
    url_parameters = merge_and_remove_empty(page_params=page_params,
                                            query_params=query_params)

    html = get_html_for_cardstart()
    html += '<h2>What would you like to see from this organization?</h2>'
    html += create_html_form(destination='resultspage',
                             button_text='show all information related to this organization',
                             hidden_fields=url_parameters |
                                           {'key': key,
                                            'view_mode': 'view_unspecified_table_organizations'
                                           })
    html += '<p/>'
    html += create_html_form(destination='resultspage',
                             button_text='show persons related to this organization',
                             hidden_fields=url_parameters |
                                           {'key': key,
                                            'name_list': PERSON_NAME_PERSON_ROOT,
                                            'view_mode': 'view_regular_table_persons_of_org'
                                           })
    html += '<p/>'
    html += create_html_form(destination='collabspage.collabspage',
                             button_text='explore collaborations for this organization',
                             hidden_fields={'start_orgs': node['value']
                                           })
    html += '<p/>'
    html += create_html_form(destination='osprofileresultpage.osprofileresultpage',
                             button_text='get an open science profile for this organization',
                             hidden_fields={'key': key
                                           })
    html += '<p/>'
    html += create_html_form(destination='osdashboardresultpage.osdashboardresultpage',
                             button_text='get an open science dashboard for this organization',
                             hidden_fields={'key': key
                                            })
    html += get_html_for_cardend()

    html += get_html_for_cardstart()
    html += '<h2>Advanced information related to this organization</h2>'
    html += get_html_for_cardstart()
    html += '<h3>More information about persons or their results in this organization</h3>'
    html += create_html_form(destination='resultspage',
                             button_text='find any information from all persons in this organization',
                             hidden_fields=url_parameters |
                                           {'key': key,
                                            'view_mode': 'view_regular_table_organization_addinfo'
                                           })
    html += '<p/>'

    html += create_html_form(destination='resultspage',
                             button_text='find research results from all persons in this organization',
                             hidden_fields=url_parameters |
                                           {'key': key,
                                            'category_list': researchresult_category_active,
                                            'view_mode': 'view_regular_table_organization_addinfo'
                                           })
    html += '<p/>'

    if COMPETENCE_CATEGORY_COMPETENCE in category_active:
        html += create_html_form(destination='resultspage',
                                 button_text='find skills from all persons in this organization',
                                 hidden_fields=url_parameters |
                                               {'key': key,
                                                'category_list': COMPETENCE_CATEGORY_COMPETENCE,
                                                'view_mode': 'view_regular_table_organization_addinfo'
                                               })
        html += '<p/>'

    html += '<br/>'

    explanation = 'By using the fields below, you can choose '
    explanation += 'what you would like to see from the persons or their results in this organization. '
    explanation += 'You can use one or both fields.'
    label_text_name = 'Search for persons or results using field <em>name</em>: '
    input_spec_name = ('list', 'name_list', 'name_active_datalist', name_active_datalist)
    label_text_category = '</br>Search for persons or results using field <em>category</em>: '
    input_spec_category = ('list', 'category_list', 'category_active_datalist', category_active_datalist)
    html += create_html_form(destination='resultspage',
                             button_text='find specific information',
                             explanation=explanation,
                             input_fields={label_text_name: input_spec_name,
                                           label_text_category: input_spec_category,
                                           },
                             hidden_fields=url_parameters |
                                           {'key': key,
                                            'view_mode': 'view_regular_table_organization_addinfo'
                                           })
    html += get_html_for_cardend()
    html += get_html_for_cardend()
    return html


def create_options_page_person(node: Node,
                               page_params: PageParams,
                               query_params: QueryParams) -> str:
    """This function creates the page with options to choose from,
    for a person, depending on the
    choice the user has made on the index page.
    The 'view_mode' that is used, is caught first in resultspage() and then
    in create_results_page().

    :param node: the node that is found and that determines the possible choices.
    :param page_params: parameters related to the page passed in the URL.
    :param query_params: parameters related to the query passed in the URL.
    :return: HTML to be rendered.
    """
    researchresult_category_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                                     item='researchresult_category_active')
    researchresult_category_active_datalist = get_global_str(ricgraph_info=RICGRAPH_NODEINFO_INTERNAL,
                                                             item='researchresult_category_active_datalist')
    source_active_datalist = get_global_str(ricgraph_info=RICGRAPH_HARVESTINFO_INTERNAL,
                                            item='source_active_datalist')
    non_person_category_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                                item='non_person_category_active')
    key = node['_key']
    url_parameters = merge_and_remove_empty(page_params=page_params,
                                            query_params=query_params)

    html = get_html_for_cardstart()
    html += '<h2>What would you like to see from this person?</h2>'

    html += create_html_form(destination='resultspage',
                             button_text='show all information related to this person',
                             hidden_fields=url_parameters |
                                           {'key': key,
                                            'category_list': non_person_category_active,
                                            'view_mode': 'view_unspecified_table_everything'
                                           })
    html += '<p/>'

    html += create_html_form(destination='resultspage',
                             button_text='show personal information related to this person',
                             hidden_fields=url_parameters |
                                           {'key': key,
                                            'category_list': PERSON_CATEGORY_PERSON,
                                            'view_mode': 'view_regular_table_personal'
                                           })
    html += '<p/>'

    html += create_html_form(destination='resultspage',
                             button_text='show organizations related to this person',
                             hidden_fields=url_parameters |
                                           {'key': key,
                                            'category_list': ORGANIZATION_CATEGORY_ORGANISATION,
                                            'view_mode': 'view_regular_table_organizations'
                                           })
    html += '<p/>'

    html += create_html_form(destination='resultspage',
                             button_text='show research results related to this person',
                             hidden_fields=url_parameters |
                                           {'key': key,
                                            'category_list': researchresult_category_active,
                                            'view_mode': 'view_unspecified_table_resouts'
                                           })
    html += get_html_for_cardend()

    html += get_html_for_cardstart()
    html += '<h2>Advanced information related to this person</h2>'
    html += get_html_for_cardstart()
    html += '<h3>With whom does this person share research results?</h3>'
    html += create_html_form(destination='resultspage',
                             button_text='find persons that share any research result types with this person',
                             hidden_fields=url_parameters |
                                           {'key': key,
                                            'category_list': researchresult_category_active,
                                            'view_mode': 'view_regular_table_person_share_resouts'
                                           })

    html += '<br/>'
    label_text = 'By entering a value in the field below, '
    label_text += 'you will get a list of persons who share a specific research result type with this person '
    label_text += '(you can also type <em>' + RESEARCHRESULT_CATEGORY_PUBLICATION_ALL
    label_text += '</em> to match any publication research result):'
    input_spec = ('list', 'category_list', 'researchresult_category_active_datalist', researchresult_category_active_datalist)
    html += create_html_form(destination='resultspage',
                             button_text='find persons that share a specific research result type with this person',
                             input_fields={label_text: input_spec},
                             hidden_fields=url_parameters |
                                           {'key': key,
                                            'view_mode': 'view_regular_table_person_share_resouts'
                                           })

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
                             hidden_fields=url_parameters |
                                           {'key': key,
                                            'view_mode': 'view_regular_table_person_organization_collaborations'
                                           })

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
    button_text = 'find information harvested from other source systems, '
    button_text += 'not present in this source system'
    input_spec = ('list', 'source_system', 'source_active_datalist', source_active_datalist)
    html += create_html_form(destination='resultspage',
                             button_text=button_text,
                             explanation=explanation,
                             input_fields={label_text: input_spec},
                             hidden_fields=url_parameters |
                                           {'key': key,
                                            'view_mode': 'view_regular_table_person_enrich_source_system'
                                           })
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
                             hidden_fields=url_parameters |
                                           {'key': key,
                                            'view_mode': 'view_regular_table_overlap'
                                           })
    html += get_html_for_cardend()
    html += get_html_for_cardend()
    return html


def create_results_page(page_params: PageParams,
                        query_params: QueryParams) -> str:
    """This function creates the page with results to show to the user.
    What is produced depends on 'view_mode'.
    The 'view_mode' that is used, is first set in create_options_page(), and then
    caught first in resultspage() and then in create_results_page().

    :param page_params: parameters related to the page passed in the URL.
    :param query_params: parameters related to the query passed in the URL.
    :return: HTML to be rendered.
    """
    if len(query_params['category_list']) == 1 \
       and query_params['category_list'][0] == RESEARCHRESULT_CATEGORY_PUBLICATION_ALL:
        # Special case: return all publication type research results.
        query_params['category_list'] = RESEARCHRESULT_CATEGORY_PUBLICATION.copy()

    html = ''
    result = read_all_nodes(key=query_params['key'])
    if len(result) == 0 or len(result) > 1:
        if len(result) == 0:
            message = 'Ricgraph Explorer could not find anything. '
        else:
            message = 'Ricgraph Explorer found too many nodes. '
        message += 'This should not happen. '
        return get_message(message=message)
    node = result[0]

    if page_params['discoverer_mode'] == DISCOVERER_MODE_DETAILS:
        table_columns_ids = TABLE_DETAIL_COLUMNS
        table_columns_org = TABLE_DETAIL_COLUMNS
        table_columns_resout = TABLE_DETAIL_COLUMNS
        if node is not None:
            html += get_you_searched_for_card(page_params=page_params,
                                              query_params=query_params)
    else:
        table_columns_ids = TABLE_ID_COLUMNS
        table_columns_org = TABLE_ORGANIZATION_COLUMNS
        table_columns_resout = TABLE_RESEARCH_OUTPUT_COLUMNS

    node_found = get_found_message(node=node,
                                   page_params=page_params,
                                   query_params=query_params)
    if node is None:
        # To silence a PyCharm warning.
        return ''

    view_mode = page_params['view_mode']
    if view_mode == 'view_unspecified_table_organizations' \
      or view_mode == 'view_regular_table_persons_of_org' \
      or view_mode == 'view_regular_table_organization_addinfo':
        html += create_results_page_organization(node=node,
                                                 page_params=page_params,
                                                 query_params=query_params,
                                                 table_columns_ids=table_columns_ids,
                                                 table_columns_resout=table_columns_resout)
    elif view_mode == 'view_unspecified_table_everything' \
       or view_mode == 'view_regular_table_personal' \
       or view_mode == 'view_unspecified_table_resouts' \
       or view_mode == 'view_regular_table_person_share_resouts' \
       or view_mode == 'view_regular_table_person_organization_collaborations' \
       or view_mode == 'view_regular_table_person_enrich_source_system' \
       or view_mode == 'view_regular_table_overlap' \
       or view_mode == 'view_regular_table_overlap_records':
        html += create_results_page_person(node=node,
                                           page_params=page_params,
                                           query_params=query_params,
                                           table_columns_ids=table_columns_ids,
                                           table_columns_org=table_columns_org,
                                           table_columns_resout=table_columns_resout)
    elif view_mode == 'view_regular_table_organizations' \
      or view_mode == 'view_regular_table_category':
        if view_mode == 'view_regular_table_category':
            personroot_node = node
        else:
            personroot_node = get_personroot_node(node=node)
        neighbor_nodes = get_all_neighbor_nodes(node=personroot_node,
                                                name_want=query_params['name_list'],
                                                category_want=query_params['category_list'])
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
                                  page_params=page_params,
                                  query_params=query_params,
                                  table_header=table_header,
                                  table_columns=table_columns)
    else:
        html += get_message(message='create_results_page(): Unknown view_mode "' + view_mode + '".')
    return html


def create_results_page_organization(node: Node,
                                     page_params: PageParams,
                                     query_params: QueryParams,
                                     table_columns_ids: list,
                                     table_columns_resout: list) -> str:
    """This function creates the page with results to show to the user,
    for 'organization' like pages. It is a helper function for
    create_results_page_organization().
    What is produced depends on 'view_mode'.

    :param node: the node that is found and that determines where we start from.
    :param page_params: parameters related to the page passed in the URL.
    :param query_params: parameters related to the query passed in the URL.
    :param table_columns_ids: Columns to use for the table with IDs.
    :param table_columns_resout: Columns to use for the table with research results.
    :return: HTML to be rendered.
    """
    node_found = get_found_message(node=node,
                                   page_params=page_params,
                                   query_params=query_params)
    html = ''
    view_mode = page_params['view_mode']
    if view_mode == 'view_unspecified_table_organizations':
        # Some organizations have a large number of neighbors, but we will only show
        # 'max_nr_items' in the table. Therefore, reduce the number of neighbors when
        # searching for persons in an organization. Don't do this for other view_modes, because
        # in that case the table shows how many items are found.
        neighbor_nodes = get_all_neighbor_nodes(node=node,
                                                name_want=query_params['name_list'],
                                                category_want=query_params['category_list'],
                                                max_nr_neighbor_nodes=query_params['max_nr_items'])
        table_header = 'This is all information related to this organization:'
        html += get_page_title(title='All information related to this organization')
        html += node_found
        if page_params['discoverer_mode'] == DISCOVERER_MODE_DETAILS:
            html += get_faceted_table(parent_node=node,
                                      neighbor_nodes=neighbor_nodes,
                                      page_params=page_params,
                                      query_params=query_params,
                                      table_header=table_header,
                                      table_columns=table_columns_resout)
        else:
            html += get_tabbed_table(nodes_list=neighbor_nodes,
                                     page_params=page_params,
                                     query_params=query_params,
                                     table_header=table_header,
                                     table_columns=table_columns_resout,
                                     tabs_on='category')
    elif view_mode == 'view_regular_table_persons_of_org':
        # Some organizations have a large number of neighbors, but we will only show
        # 'max_nr_items' in the table. Therefore, reduce the number of neighbors when
        # searching for persons in an organization. Don't do this for other view_modes, because
        # in that case the table shows how many items are found.
        neighbor_nodes = get_all_neighbor_nodes(node=node,
                                                name_want=query_params['name_list'],
                                                category_want=query_params['category_list'],
                                                max_nr_neighbor_nodes=query_params['max_nr_items'])
        table_header = 'These are persons related to this organization:'
        table_columns = table_columns_ids
        html += get_page_title(title='Persons related to this organization')
        html += node_found
        html += get_regular_table(nodes_list=neighbor_nodes,
                                  page_params=page_params,
                                  query_params=query_params,
                                  table_header=table_header,
                                  table_columns=table_columns)

    elif view_mode == 'view_regular_table_organization_addinfo':
        html += get_page_title(title='Information about this organization')
        html += find_organization_additional_info(parent_node=node,
                                                  page_params=page_params,
                                                  query_params=query_params)
    else:
        html += get_message(message='create_results_page(): Unknown view_mode "' + view_mode + '".')
    return html


def create_results_page_person(node: Node,
                               page_params: PageParams,
                               query_params: QueryParams,
                               table_columns_ids: list,
                               table_columns_org: list,
                               table_columns_resout: list) -> str:
    """This function creates the page with results to show to the user,
    for 'person' like pages. It is a helper function for
    create_results_page_organization().
    What is produced depends on 'view_mode'.

    :param node: the node that is found and that determines where we start from.
    :param page_params: parameters related to the page passed in the URL.
    :param query_params: parameters related to the query passed in the URL.
    :param table_columns_ids: Columns to use for the table with IDs.
    :param table_columns_org: Columns to use for the table with organizations.
    :param table_columns_resout: Columns to use for the table with research results.
    :return: HTML to be rendered.
    """
    person_category_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                             item='person_category_active')
    year_range_text = get_year_range_text(year_first=query_params['year_first'],
                                          year_last=query_params['year_last'])
    node_found = get_found_message(node=node,
                                   page_params=page_params,
                                   query_params=query_params)
    html = ''
    view_mode = page_params['view_mode']
    if view_mode == 'view_unspecified_table_everything':
        personroot_node = get_personroot_node(node=node)
        html += get_page_title(title='All information related to this person')
        html += node_found
        neighbor_nodes_personal = get_all_neighbor_nodes(node=personroot_node,
                                                         category_want=person_category_active)
        neighbor_nodes_organization = get_all_neighbor_nodes(node=personroot_node,
                                                             category_want=ORGANIZATION_CATEGORY_ALL)
        if len(query_params['category_list']) == 0:
            # We have only personal identifier records for this person,
            # so there are no other categories of nodes to show.
            neighbor_nodes_researchresult = []
        else:
            researchresult_list = [node for node in query_params['category_list']
                                   if node not in ORGANIZATION_CATEGORY_ALL]
            neighbor_nodes_researchresult = get_all_neighbor_nodes(node=personroot_node,
                                                                   name_want=query_params['name_list'],
                                                                   category_want=researchresult_list,
                                                                   year_first=query_params['year_first'],
                                                                   year_last=query_params['year_last'])
        other_table_header = 'These are the research results related to this person '
        other_table_header += year_range_text + ':'
        if page_params['discoverer_mode'] == DISCOVERER_MODE_DETAILS:
            html += get_tabbed_table(nodes_list=neighbor_nodes_personal,
                                     page_params=page_params,
                                     query_params=query_params,
                                     table_header='This is personal information related to this person:',
                                     table_columns=table_columns_ids,
                                     tabs_on='name')
            # [29-3-2026] Generates a PyCharm warning:
            # Expected type 'Node', got 'Node | str' instead.
            # I don't understand, above it is ok.
            html += get_faceted_table(parent_node=node,
                                      neighbor_nodes=neighbor_nodes_researchresult,
                                      page_params=page_params,
                                      query_params=query_params,
                                      table_header=other_table_header,
                                      table_columns=table_columns_resout)
        else:
            html += view_personal_information(nodes_list=neighbor_nodes_personal,
                                              page_params=page_params,
                                              query_params=query_params)
            html += get_tabbed_table(nodes_list=neighbor_nodes_researchresult,
                                     page_params=page_params,
                                     query_params=query_params,
                                     table_header=other_table_header,
                                     table_columns=table_columns_resout,
                                     tabs_on='category')
        html += get_regular_table(nodes_list=neighbor_nodes_organization,
                                  page_params=page_params,
                                  query_params=query_params,
                                  table_header='These are organizations related to this person:',
                                  table_columns=table_columns_org)
    elif view_mode == 'view_regular_table_personal':
        personroot_node = get_personroot_node(node=node)
        neighbor_nodes_personal = get_all_neighbor_nodes(node=personroot_node,
                                                         category_want=person_category_active)
        html += get_page_title(title='Personal information related to this person')
        html += node_found
        if page_params['discoverer_mode'] == DISCOVERER_MODE_DETAILS:
            html += get_regular_table(nodes_list=neighbor_nodes_personal,
                                      page_params=page_params,
                                      query_params=query_params,
                                      table_header='This is personal information related to this person:',
                                      table_columns=table_columns_ids)
        else:
            html += view_personal_information(nodes_list=neighbor_nodes_personal,
                                              page_params=page_params,
                                              query_params=query_params)
    # For "elif view_mode == 'view_regular_table_organizations'"
    # see create_results_page().
    elif view_mode == 'view_unspecified_table_resouts':
        # [April 4, 2026] We do not have this anymore:
        # or view_mode == 'view_unspecified_table_everything_except_ids':
        personroot_node = get_personroot_node(node=node)
        neighbor_nodes = get_all_neighbor_nodes(node=personroot_node,
                                                name_want=query_params['name_list'],
                                                category_want=query_params['category_list'],
                                                year_first = query_params['year_first'],
                                                year_last = query_params['year_last'])
        if view_mode == 'view_unspecified_table_resouts':
            table_header = 'These are the research results related to this person '
            table_header += year_range_text + ':'
        else:
            table_header = 'These are all the neighbors related to this person (without its identities):'
        html += get_page_title(title='Research results related to this person')
        html += node_found
        if page_params['discoverer_mode'] == DISCOVERER_MODE_DETAILS:
            html += get_faceted_table(parent_node=node,
                                      neighbor_nodes=neighbor_nodes,
                                      page_params=page_params,
                                      query_params=query_params,
                                      table_header=table_header,
                                      table_columns=table_columns_resout)
        else:
            html += get_tabbed_table(nodes_list=neighbor_nodes,
                                     page_params=page_params,
                                     query_params=query_params,
                                     table_header=table_header,
                                     table_columns=table_columns_resout,
                                     tabs_on='category')
    elif view_mode == 'view_regular_table_person_share_resouts':
        # Note the hard limit.
        html += get_page_title(title='Persons that share research results with this person')
        html += find_person_share_resouts(parent_node=node,
                                          page_params=page_params,
                                          query_params=query_params,
                                          category_want_list=query_params['category_list'],
                                          category_dontwant_list=[PERSON_CATEGORY_PERSON,
                                                                  ORGANIZATION_CATEGORY_ORGANISATION,
                                                                  COMPETENCE_CATEGORY_COMPETENCE])
    elif view_mode == 'view_regular_table_person_organization_collaborations':
        html += get_page_title(title='Organizations that this person collaborates with')
        html += find_person_organization_collaborations(parent_node=node,
                                                        page_params=page_params,
                                                        query_params=query_params)
    elif view_mode == 'view_regular_table_person_enrich_source_system':
        html += get_page_title(title='Information harvested from other source systems, not present in this source system')
        html += find_enrich_candidates(parent_node=node,
                                       page_params=page_params,
                                       query_params=query_params)
    elif view_mode == 'view_regular_table_overlap':
        html += get_page_title(title='Overlap in source systems for the neighbor nodes of this node')
        page_params['overlap_mode'] = OVERLAP_MODE_NEIGHBORNODE
        html += find_overlap_in_source_systems(node=node,
                                               page_params=page_params,
                                               query_params=query_params)
    elif view_mode == 'view_regular_table_overlap_records':
        html += find_overlap_in_source_systems_records(node=node,
                                                       page_params=page_params,
                                                       query_params=query_params)
    else:
        html += get_message(message='create_results_page(): Unknown view_mode "' + view_mode + '".')
    return html


# ################################################
# #### Entry point for WSGI Gunicorn server   ####
# #### using Uvicorn for ASGI applications    ####
# ################################################
def create_ricgraph_explorer_app():
    global _ricgraph_explorer
    initialize_ricgraph_explorer(ricgraph_explorer_app=_ricgraph_explorer,
                                 runmode=RICGRAPH_EXPLORER_RUNMODE_GUNICORN)
    return _ricgraph_explorer


# ############################################
# ################### main ###################
# ############################################
if __name__ == "__main__":
    initialize_ricgraph_explorer(ricgraph_explorer_app=_ricgraph_explorer,
                                 runmode=RICGRAPH_EXPLORER_RUNMODE_DEBUG)
    _ricgraph_explorer.run(port=RICGRAPH_EXPLORER_DEBUG_PORT)
