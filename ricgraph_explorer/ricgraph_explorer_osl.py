# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
#
# Copyright (c) 2026 Rik D.T. Janssen
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
# Ricgraph Explorer Open science landscaping functions.
#
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, March 2026.
#
# ########################################################################


from flask import Blueprint, url_for
from neo4j.graph import Node
from ricgraph import (read_all_nodes,
                      check_valid_year,
                      get_year_range_text,
                      ORGANIZATION_CATEGORY_ORGANISATION,
                      ACCESS_OPEN,
                      ACCESS_ANY)
from ricgraph_explorer_constants import (RICGRAPH_NODEINFO,
                                         RICGRAPH_SYSTEMINFO,
                                         html_body_start, html_body_end,
                                         MAX_ROWS_IN_TABLE,
                                         ORIGIN_OPEN_SCIENCE_PROFILE_BUTTON,
                                         button_style,
                                         form_button_on_one_line_flexspace_style,
                                         form_button_on_one_line_width,
                                         HISTOGRAM_MODE_COUNTS,
                                         HISTOGRAM_MODE_PERCENTAGES,
                                         OSL_PROFILE_MODE_GROUPS,
                                         OSL_PROFILE_MODE_ITEMS)
from ricgraph_explorer_utils import (get_html_for_cardstart, get_html_for_cardend,
                                     create_html_form,
                                     get_page_title,
                                     get_url_parameter_value,
                                     get_message,
                                     get_spinner,
                                     get_html_for_yearcard,
                                     get_global_list, get_global_str,
                                     get_page_footer)
from ricgraph_explorer_datavis import get_html_for_histogram
from ricgraph_explorer_cypher import create_neighbor_histogram_cypher


_oslpage_bp = Blueprint(name='oslpage', import_name=__name__)
_osprofileresultpage_bp = Blueprint(name='osprofileresultpage', import_name=__name__)


@_oslpage_bp.route(rule='/oslpage/', methods=['GET'])
def oslpage() -> str:
    """Ricgraph Explorer entry, this 'page' does not have any url parameters.
    Probably, in the future, it should have.
    The Explore open science monitoring page.

    :return: HTML to be rendered.
    """
    html = html_body_start

    html += get_page_title(title='Explore open science monitoring')
    html += get_html_for_cardstart()
    html += 'There are various methods to start exploring open science landscaping:'
    html += '<p/>'
    html += create_html_form(destination='collabspage.collabspage',
                             button_text='explore collaborations')
    html += '<p/>'
    html += create_html_form(destination='searchpage',
                             button_text='get an open science profile for a (sub-)organization',
                             hidden_fields={'search_mode': 'value_search',
                                            'category': ORGANIZATION_CATEGORY_ORGANISATION,
                                            'origin': ORIGIN_OPEN_SCIENCE_PROFILE_BUTTON
                                            })
    html += get_html_for_cardend()

    html += get_page_footer() + html_body_end
    return html


@_osprofileresultpage_bp.route(rule='/osprofileresultpage/', methods=['GET'])
def osprofileresultpage() -> str:
    """Ricgraph Explorer entry, this 'page' only uses URL parameters.
    Find the open science profile of a (sub-)organizations based on
    URL parameters passed.

    Possible url parameters are:
    - key: key of the organization to find.
    - year_first: first year of the research results to count.
    - year_last: last year of the research results to count.
    - histogram_mode: The mode of the histogram, either counts
      (HISTOGRAM_MODE_COUNTS), or percentages (HISTOGRAM_MODE_PERCENTAGES).
    - oslprofile_mode: report on the three groups
      (OSL_PROFILE_MODE_GROUPS), or on all item types (OSL_PROFILE_MODE_ITEMS).
    - discoverer_mode: the discoverer_mode to use, 'details_view' to see all details,
      or 'person_view' to have a nicer layout.
    - max_nr_items: this usually signifies the maximum number of items to return,
      or 0 to return all items. In this page, it will be ignored and set to 0.
    - max_nr_table_rows: the maximum number of rows in a table to return (the page
      size of the table), or 0 to return all rows.

    :return: HTML to be rendered.
    """
    researchresult_category_research_material = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                                                item='researchresult_category_research_material')
    researchresult_category_reporting_material = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                                                 item='researchresult_category_reporting_material')
    researchresult_category_engagement_material = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                                                  item='researchresult_category_engagement_material')
    key = get_url_parameter_value(parameter='key', use_escape=False)
    year_first = get_url_parameter_value(parameter='year_first')
    year_last = get_url_parameter_value(parameter='year_last')
    histogram_mode = get_url_parameter_value(parameter='histogram_mode',
                                             allowed_values=get_global_list(ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                                            item='histogram_mode_all'),
                                             default_value=HISTOGRAM_MODE_PERCENTAGES)
    oslprofile_mode = get_url_parameter_value(parameter='oslprofile_mode',
                                              allowed_values=get_global_list(ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                                             item='osl_profile_mode_all'),
                                              default_value=OSL_PROFILE_MODE_GROUPS)
    access = get_url_parameter_value(parameter='access',
                                     allowed_values=get_global_list(ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                                    item='access_all'),
                                     default_value=ACCESS_ANY)
    discoverer_mode = get_url_parameter_value(parameter='discoverer_mode',
                                              allowed_values=get_global_list(ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                                             item='discoverer_mode_all'),
                                              default_value=get_global_str(ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                                           item='discoverer_mode_default'))
    # For this page, we ignore the value of 'max_nr_items' if it is passed.
    max_nr_items = '0'
    extra_url_parameters = {}
    extra_url_parameters['max_nr_items'] = max_nr_items
    max_nr_table_rows = get_url_parameter_value(parameter='max_nr_table_rows',
                                                default_value=str(MAX_ROWS_IN_TABLE))
    if not max_nr_table_rows.isnumeric():
        max_nr_table_rows = str(MAX_ROWS_IN_TABLE)
    html = html_body_start
    if (message := check_valid_year(year_first=year_first, year_last=year_last)) != '':
        html += get_message(message=message)
        return html + get_page_footer() + html_body_end

    extra_url_parameters['max_nr_table_rows'] = max_nr_table_rows
    extra_url_parameters['key'] = key
    extra_url_parameters['year_first'] = year_first
    extra_url_parameters['year_last'] = year_last
    extra_url_parameters['discoverer_mode'] = discoverer_mode
    extra_url_parameters['histogram_mode'] = histogram_mode
    extra_url_parameters['oslprofile_mode'] = oslprofile_mode
    extra_url_parameters['access'] = access

    result = read_all_nodes(key=key)
    if len(result) == 0 or len(result) > 1:
        if len(result) == 0:
            message = 'Ricgraph Explorer could not find anything. '
        else:
            message = 'Ricgraph Explorer found too many nodes. '
        message += 'This should not happen. '
        html += get_message(message=message)
        return html + get_page_footer() + html_body_end
    node = result[0]

    if oslprofile_mode == OSL_PROFILE_MODE_ITEMS:
        # List of items.
        material_group = researchresult_category_research_material + \
                         researchresult_category_reporting_material + \
                         researchresult_category_engagement_material
        material_group = sorted(material_group, key=lambda x: x.lower())
        material_name = material_group.copy()
    else:
        # List of lists.
        material_group = [researchresult_category_research_material,
                          researchresult_category_reporting_material,
                          researchresult_category_engagement_material]
        material_name = ['research material',
                         'reporting material',
                         'engagement material']
    histogram_list, buttons = prepare_oslprofile(node=node,
                                                 material_group=material_group,
                                                 material_name=material_name,
                                                 all_url_parameters=extra_url_parameters)
    histogram_title = 'Open science profile '
    if histogram_mode == HISTOGRAM_MODE_PERCENTAGES:
        histogram_title += '(percentages, '
    else:
        histogram_title += '(counts, '
    if access == ACCESS_ANY:
        histogram_title += '"any" access) '
    else:
        histogram_title += ' only "open" access) '
    histogram_title += get_year_range_text(year_first=year_first,
                                           year_last=year_last)
    histogram_title += ' for "' + node['value'] + '"'
    html_histogram = '<div ' + form_button_on_one_line_flexspace_style + '>'
    html_histogram += get_html_for_histogram(histogram_list=histogram_list,
                                            histogram_title=histogram_title,
                                            histogram_mode=histogram_mode)

    modified_url_parameters = extra_url_parameters.copy()
    if histogram_mode == HISTOGRAM_MODE_PERCENTAGES:
        modified_url_parameters['histogram_mode'] = HISTOGRAM_MODE_COUNTS
        what_to_show = 'counts'
    else:
        modified_url_parameters['histogram_mode'] = HISTOGRAM_MODE_PERCENTAGES
        what_to_show = 'percentages'
    url = url_for(endpoint='osprofileresultpage.osprofileresultpage',
                  **modified_url_parameters)
    html_histogram += '<a href="' + url + '">toggle this histogram to show '
    html_histogram += what_to_show + '</a> '

    modified_url_parameters = extra_url_parameters.copy()
    if access == ACCESS_ANY:
        modified_url_parameters['access'] = ACCESS_OPEN
        what_to_show = 'only "open" access research results'
    else:
        modified_url_parameters['access'] = ACCESS_ANY
        what_to_show = '"any" access research results'
    url = url_for(endpoint='osprofileresultpage.osprofileresultpage',
                  **modified_url_parameters)
    html_histogram += '<a href="' + url + '">toggle this histogram to show '
    html_histogram += what_to_show + '</a>'

    modified_url_parameters = extra_url_parameters.copy()
    if oslprofile_mode == OSL_PROFILE_MODE_GROUPS:
        modified_url_parameters['oslprofile_mode'] = OSL_PROFILE_MODE_ITEMS
        what_to_show = 'all research result item types'
    else:
        modified_url_parameters['oslprofile_mode'] = OSL_PROFILE_MODE_GROUPS
        what_to_show = 'research, reporting, and engagement material'
    url = url_for(endpoint='osprofileresultpage.osprofileresultpage',
                  **modified_url_parameters)
    html_histogram += '<a href="' + url + '">toggle this histogram to show '
    html_histogram += what_to_show + '</a>'
    html_histogram += '</div>'

    message = 'You can choose a different time period for this open science profile, '
    message += 'note that recreating it may take a while:'
    form = get_html_for_yearcard(show_as_card=False,
                                 message=message,
                                 button_text='recreate')

    html += get_page_title(title='Open science profile for "' + node['value'] + '"')
    html += get_html_for_cardstart()
    html += html_histogram
    html += buttons
    html += '<br/>'
    html += form
    message = 'Recreating the open science profile, this may take a while. Please wait...'
    html += get_spinner(message=message)
    html += get_html_for_cardend()

    html += get_html_for_cardstart()
    html += '<h2>What is an open science profile in Ricgraph?</h2>'
    html += 'Ricgraph can show two types of <em>open science profiles</em>, one '
    html += 'consisting of the three groups research, reporting, '
    html += 'and engagement material, and one consisting of '
    html += 'all research result item types in Ricgraph. '
    html += 'Both relate to the distribution of research results '
    html += 'for a certain (sub-)organization. '
    html += 'It is said that the form of this distribution may be characteristic '
    html += 'for such a (sub-)organization. '
    html += 'You can use this page to check this for yourself. '
    html += 'Also, you can choose whether you would like to see percentages '
    html += 'in the histogram, or rather prefer to see counts. '
    html += '<br/><br/>'
    html += 'The three groups research, reporting, and engagement '
    html += 'material are defined in Ricgraph as:'
    html += '<ol><li>'
    html += '<em>Research material</em>: input/output and supporting materials of the analysis.'
    html += '<br/>'
    html += 'These are the result result categories ' + str(researchresult_category_research_material) + '.'
    html += '</li><li>'
    html += '<em>Reporting material</em>: documents reporting on process and results of analysis.'
    html += '<br/>'
    html += 'These are the result result categories ' + str(researchresult_category_reporting_material) + '.'
    html += '</li><li>'
    html += '<em>Engagement material</em>: everything used to involve stakeholders and '
    html += 'wider audiences into influencing the research and '
    html += 'using or implementing its results.'
    html += '<br/>'
    html += 'These are the result result categories ' + str(researchresult_category_engagement_material) + '.'
    html += '</li></ol>'
    html += get_html_for_cardend()

    return html + get_page_footer() + html_body_end


def prepare_oslprofile(node: Node,
                       material_group: list,
                       material_name: list,
                       all_url_parameters: dict) -> tuple[list, str]:
    """Prepare information for the Ricgraph open science profile.

    :param node: Organization node to consider.
    :param material_group: List of research result items.
    :param material_name: List of names how to name these research result items.
    :param all_url_parameters: Parameters to be passed in the URL.
    :return: A list that contains the histogram (as JSON), and
      HTML for the buttons to get more information about the items
      in the histogram.
    """
    year_first = all_url_parameters['year_first']
    year_last = all_url_parameters['year_last']
    access = all_url_parameters['access']
    buttons = '</p><div ' + form_button_on_one_line_flexspace_style + '>'
    histogram_list = []
    for material, name in zip(material_group, material_name):
        if isinstance(material, str):
            material = [material]
        hist_part = create_neighbor_histogram_cypher(node=node,
                                                     category=material,
                                                     year_first=year_first,
                                                     year_last=year_last,
                                                     access=access)
        hist_part_total = 0
        for item in hist_part:
            hist_part_total += hist_part[item]
        histogram_list.append({'name': name, 'value': hist_part_total})

        if hist_part_total > 0:
            # Only a button if there is material to show.
            url = url_for(endpoint='resultspage',
                          view_mode='view_regular_table_organization_addinfo',
                          category_list=material,
                          **all_url_parameters)
            buttons += '<a href="' + url + '" class="w3-bar-item'
            buttons += button_style + '"' + form_button_on_one_line_width
            buttons += '>show ' + name + '</a>'
    buttons += '</div>'
    return histogram_list, buttons
