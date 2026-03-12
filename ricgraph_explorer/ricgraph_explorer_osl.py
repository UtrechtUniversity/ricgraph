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
from ricgraph import (read_all_nodes,
                      ROCATEGORY_RESEARCH_MATERIAL,
                      ROCATEGORY_REPORTING_MATERIAL,
                      ROCATEGORY_ENGAGEMENT_MATERIAL)
from ricgraph_explorer_constants import (html_body_start, html_body_end,
                                         DISCOVERER_MODE_ALL,
                                         MAX_ROWS_IN_TABLE,
                                         ORIGIN_OPEN_SCIENCE_PROFILE_BUTTON,
                                         button_style)
from ricgraph_explorer_init import get_ricgraph_explorer_global
from ricgraph_explorer_utils import (get_html_for_cardstart, get_html_for_cardend,
                                     create_html_form,
                                     get_page_title,
                                     get_url_parameter_value,
                                     get_message,
                                     get_spinner)
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
    page_footer = get_ricgraph_explorer_global('page_footer')

    html = html_body_start

    html += get_page_title(title='Explore open science monitoring')
    html += get_html_for_cardstart()
    # html += 'There are various methods to start exploring open science monitoring:'
    html += 'For the moment, there is only one method to start exploring open science monitoring:'
    html += '<p/>'
    html += create_html_form(destination='collabspage',
                             button_text='explore collaborations')
    html += '<p/>'
    html += create_html_form(destination='searchpage',
                             button_text='get an open science profile for a (sub-)organization',
                             hidden_fields={'search_mode': 'value_search',
                                            'category': 'organization',
                                            'origin': ORIGIN_OPEN_SCIENCE_PROFILE_BUTTON
                                            })
    html += get_html_for_cardend()

    html += page_footer + html_body_end
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
    - discoverer_mode: the discoverer_mode to use, 'details_view' to see all details,
      or 'person_view' to have a nicer layout.
    - max_nr_items: this usually signifies the maximum number of items to return,
      or 0 to return all items. In this page, it will be ignored and set to 0.
    - max_nr_table_rows: the maximum number of rows in a table to return (the page
      size of the table), or 0 to return all rows.

    :return: HTML to be rendered.
    """
    page_footer = get_ricgraph_explorer_global('page_footer')
    year_all_datalist = get_ricgraph_explorer_global('year_all_datalist')
    key = get_url_parameter_value(parameter='key', use_escape=False)
    year_first = get_url_parameter_value(parameter='year_first')
    year_last = get_url_parameter_value(parameter='year_last')

    extra_url_parameters = {}
    discoverer_mode = get_url_parameter_value(parameter='discoverer_mode',
                                              allowed_values=DISCOVERER_MODE_ALL,
                                              default_value=get_ricgraph_explorer_global(name='discoverer_mode_default'))
    # For this page, we ignore the value of 'max_nr_items' if it is passed.
    max_nr_items = '0'
    extra_url_parameters['max_nr_items'] = max_nr_items
    max_nr_table_rows = get_url_parameter_value(parameter='max_nr_table_rows',
                                                default_value=str(MAX_ROWS_IN_TABLE))
    if not max_nr_table_rows.isnumeric():
        max_nr_table_rows = str(MAX_ROWS_IN_TABLE)
    extra_url_parameters['max_nr_table_rows'] = max_nr_table_rows

    html = html_body_start
    if (year_first != '' and not year_first.isnumeric()) \
       or (year_last != '' and not year_last.isnumeric()):
        html += get_message(message='Error: "year_first" or "year_last" are not numeric.')
        html += page_footer + html_body_end
        return html
    if year_first != '' and year_last != '' and int(year_first) > int(year_last):
        message = 'Error: you did not specify a valid year range ['
        message += year_first + ', ' + year_last + '].'
        html += get_message(message=message)
        html += page_footer + html_body_end
        return html

    result = read_all_nodes(key=key)
    if len(result) == 0 or len(result) > 1:
        if len(result) == 0:
            message = 'Ricgraph Explorer could not find anything. '
        else:
            message = 'Ricgraph Explorer found too many nodes. '
        message += 'This should not happen. '
        html += get_message(message=message)
        html += page_footer + html_body_end
        return html
    node = result[0]

    hist_research_mat = create_neighbor_histogram_cypher(node=node,
                                                         category=ROCATEGORY_RESEARCH_MATERIAL,
                                                         year_first=year_first,
                                                         year_last=year_last)
    hist_reporting_mat = create_neighbor_histogram_cypher(node=node,
                                                          category=ROCATEGORY_REPORTING_MATERIAL,
                                                          year_first=year_first,
                                                          year_last=year_last)
    hist_engagement_mat = create_neighbor_histogram_cypher(node=node,
                                                           category=ROCATEGORY_ENGAGEMENT_MATERIAL,
                                                           year_first=year_first,
                                                           year_last=year_last)
    hist_research_mat_total = hist_reporting_mat_total = hist_engagement_mat_total = 0
    for item in hist_research_mat:
        hist_research_mat_total += hist_research_mat[item]
    for item in hist_reporting_mat:
        hist_reporting_mat_total += hist_reporting_mat[item]
    for item in hist_engagement_mat:
        hist_engagement_mat_total += hist_engagement_mat[item]

    histogram_list = [{'name': 'research material', 'value': hist_research_mat_total},
                      {'name': 'reporting material', 'value': hist_reporting_mat_total},
                      {'name': 'engagement material', 'value': hist_engagement_mat_total}]
    histogram_title = 'Open science profile '
    if year_first == '' and year_last == '':
        histogram_title += 'for all years '
    else:
        if year_first == '':
            histogram_title += 'up '
        else:
            histogram_title += 'from ' + year_first + ' '
        if year_last == '':
            histogram_title += 'onwards '
        else:
            histogram_title += 'to ' + year_last + ' '
    histogram_title += 'for "' + node['value'] + '"'
    html_histogram = get_html_for_histogram(histogram_list=histogram_list,
                                            histogram_title=histogram_title)

    html_style = ' style="display:flex; justify-content:space-between; '
    html_style += 'width:100%; align-items:end; gap:1em; flex-wrap:wrap;" '
    html_field_width = ' style="width:16em !important;" '

    material_group = [ROCATEGORY_RESEARCH_MATERIAL,
                      ROCATEGORY_REPORTING_MATERIAL,
                      ROCATEGORY_ENGAGEMENT_MATERIAL]
    material_name = ['research', 'reporting', 'engagement']
    buttons = '</p><div ' + html_style + '>'
    for material, name in zip(material_group, material_name):
        url = url_for(endpoint='resultspage',
                      key=key,
                      view_mode='view_regular_table_organization_addinfo',
                      discoverer_mode=discoverer_mode,
                      category_list=material,
                      **extra_url_parameters)
        buttons += '<a href="' + url + '" class="w3-bar-item'
        buttons += button_style + '"' + html_field_width
        buttons += '>show ' + name + ' material</a>'
    buttons += '</div>'

    form = '<form method="get" action="/osprofileresultpage/"' + html_style + '>'
    form += '<div' + html_field_width + '>'
    form += '<label for="year_first">Specify the first year:</label>'
    form += '<input id="year_first" class="w3-input w3-border" list="year_all_datalist"'
    form += 'name=year_first autocomplete=off' + html_field_width + '>'
    form += '<div class="firefox-only">Click twice to get a dropdown list.</div>'
    form += str(year_all_datalist)
    form += '</div>'

    form += '<div' + html_field_width + '>'
    form += '<label for="year_last">Specify the last year:</label>'
    form += '<input id="year_last" class="w3-input w3-border" list="year_all_datalist"'
    form += 'name=year_last autocomplete=off' + html_field_width + '>'
    form += '<div class="firefox-only">Click twice to get a dropdown list.</div>'
    form += str(year_all_datalist)
    form += '</div>'

    form += '<input type="hidden" name="key" value="' + key + '">'
    form += '<input type="hidden" name="discoverer_mode" value="' + discoverer_mode + '">'
    form += '<input class="' + button_style + '"' + html_field_width
    form += 'type=submit value="recreate">'
    form += '</form>'

    html += get_page_title(title='Open science profile for "' + node['value'] + '"')

    html += get_html_for_cardstart()
    html += html_histogram
    if year_first == '' and year_last == '':
        # Only show buttons if we have the full year range. We cannot
        # show the research results from a partial year range,
        # since the page we go to does not provide that yet.
        html += buttons
    html += '<br/>'
    html += 'You can choose a different time period for this open science profile, '
    html += 'note that recreating it may take a while.'
    html += '<br/>'
    html += form
    message = 'Recreating the open science profile, this may take a while. Please wait...'
    html += get_spinner(message=message)
    html += get_html_for_cardend()

    html += get_html_for_cardstart()
    html += '<h2>What is an open science profile in Ricgraph?</h2>'
    html += 'The <em>open science profile</em> for a (sub-)organization is defined '
    html += 'in Ricgraph as the distribution of its research results '
    html += 'across three groups:'
    html += '<ol><li>'
    html += '<em>Research material</em>: input/output and supporting materials of the analysis;'
    html += '</li><li>'
    html += '<em>Reporting material</em>: documents reporting on process and results of analysis;'
    html += '</li><li>'
    html += '<em>Engagement material</em>: everything used to involve stakeholders and '
    html += 'wider audiences into influencing the research and '
    html += 'using or implementing its results.'
    html += '</li></ol>'
    html += 'It is said that the form of this distribution may be characteristic '
    html += 'for a certain (sub-)organization. '
    html += 'You can use this page to check this for yourself. '
    html += '<br/><br/>'
    html += 'In creating these groups, '
    html += 'the following research result categories have been used:'
    html += '<ul><li>'
    html += 'Research material: ' + str(ROCATEGORY_RESEARCH_MATERIAL) + '.'
    html += '</li><li>'
    html += 'Reporting material: ' + str(ROCATEGORY_REPORTING_MATERIAL) + '.'
    html += '</li><li>'
    html += 'Engagement material: ' + str(ROCATEGORY_ENGAGEMENT_MATERIAL) + '.'
    html += '</li></ul>'
    html += get_html_for_cardend()

    html += page_footer + html_body_end
    return html
