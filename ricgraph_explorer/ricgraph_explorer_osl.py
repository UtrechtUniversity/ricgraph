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
from ricgraph import (check_valid_year,
                      get_year_range_text,
                      PageParams, QueryParams,
                      ORGANIZATION_CATEGORY_ORGANIZATION,
                      ACCESS_OPEN)
from ricgraph_explorer_constants import (RICGRAPH_NODEINFO,
                                         html_body_start, html_body_end,
                                         ORIGIN_OPEN_SCIENCE_PROFILE_BUTTON,
                                         ORIGIN_OPEN_SCIENCE_DASHBOARD_BUTTON,
                                         button_style,
                                         form_button_on_one_line_flexspace_style,
                                         form_button_on_one_line_width,
                                         HISTOGRAM_MODE_COUNTS,
                                         HISTOGRAM_MODE_PERCENTAGES,
                                         SEARCH_MODE_VALUE)
from ricgraph_explorer_utils import (get_url_query_params, get_url_page_params,
                                     get_global_list,
                                     merge_and_remove_empty)
from ricgraph_explorer_html import (get_html_for_cardstart, get_html_for_cardend,
                                    create_html_form,
                                    get_message,
                                    get_you_searched_for_card, get_page_title,
                                    get_page_footer,
                                    compute_histogramcards,
                                    get_histogramcards, get_html_for_histogramcard,
                                    get_html_for_yearcard, get_html_for_facetcard)


_oslpage_bp = Blueprint(name='oslpage', import_name=__name__)
_osprofileresultpage_bp = Blueprint(name='osprofileresultpage', import_name=__name__)
_osdashboardresultpage_bp = Blueprint(name='osdashboardresultpage', import_name=__name__)


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
                             hidden_fields={'search_mode': SEARCH_MODE_VALUE,
                                            'category': ORGANIZATION_CATEGORY_ORGANIZATION,
                                            'origin': ORIGIN_OPEN_SCIENCE_PROFILE_BUTTON
                                           })
    html += '<p/>'
    html += create_html_form(destination='searchpage',
                             button_text='get an open science dashboard for a (sub-)organization',
                             hidden_fields={'search_mode': SEARCH_MODE_VALUE,
                                            'category': ORGANIZATION_CATEGORY_ORGANIZATION,
                                            'origin': ORIGIN_OPEN_SCIENCE_DASHBOARD_BUTTON
                                           })
    html += get_html_for_cardend()

    html += get_page_footer() + html_body_end
    return html


@_osprofileresultpage_bp.route(rule='/osprofileresultpage/', methods=['GET'])
def osprofileresultpage() -> str:
    """Ricgraph Explorer entry, this 'page' only uses URL parameters.
    Find the open science profile of a (sub-)organization based on
    URL parameters passed.

    Possible url parameters are:
    - key: key of the organization to find.
    - year_first: first year of the research results to count.
    - year_last: last year of the research results to count.
    - histogram_mode: The mode of the histogram, either counts
      (HISTOGRAM_MODE_COUNTS), or percentages (HISTOGRAM_MODE_PERCENTAGES).
    - discoverer_mode: the discoverer_mode to use, 'details_view' to see all details,
      or 'person_view' to have a nicer layout.
    - max_nr_items: this usually signifies the maximum number of items to return,
      or 0 to return all items. In this page, it will be ignored and set to 0.
    - max_nr_table_rows: the maximum number of rows in a table to return (the page
      size of the table), or 0 to return all rows.

    :return: HTML to be rendered.
    """
    page_params = get_url_page_params()
    query_params = get_url_query_params()
    if page_params['histogram_mode'] == '':
        # Set the default histogram_mode.
        page_params['histogram_mode'] = HISTOGRAM_MODE_PERCENTAGES
    # For this page, we ignore the value of 'max_nr_items' if it is passed.
    query_params['max_nr_items'] = 0

    researchresult_category_research_material = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                                                item='researchresult_category_research_material')
    researchresult_category_reporting_material = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                                                 item='researchresult_category_reporting_material')
    researchresult_category_engagement_material = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                                                  item='researchresult_category_engagement_material')
    if len(query_params['category_list']) == 0:
        query_params['category_list'] = researchresult_category_research_material + \
                                        researchresult_category_reporting_material + \
                                        researchresult_category_engagement_material
    html = html_body_start
    html += get_you_searched_for_card(page_params=page_params,
                                      query_params=query_params)
    if (message := check_valid_year(year_first=query_params['year_first'],
                                    year_last=query_params['year_last'])) != '':
        html += get_message(message=message)
        return html + get_page_footer() + html_body_end

    (name_histogram, category_histogram, year_histogram,
     license_histogram, access_histogram) = \
        compute_histogramcards(query_params=query_params,
                               reverse_sort_on_value=False)

    material_group = [researchresult_category_research_material,
                      researchresult_category_reporting_material,
                      researchresult_category_engagement_material]
    material_name = ['research material',
                     'reporting material',
                     'engagement material']
    new_histogram = []
    for group in material_group:
        total = 0
        for item in category_histogram:
            if item['name'] in group:
                total += item['value']
        new_histogram.append(total)
    histogram_list = [{'name': name, 'value': value} for name, value in zip(material_name, new_histogram)]

    buttons = create_researchresult_buttons(category_histogram=category_histogram,
                                            material_group=material_group,
                                            material_name=material_name,
                                            page_params=page_params,
                                            query_params=query_params)
    histogram_title = 'Open science profile '
    if page_params['histogram_mode'] == HISTOGRAM_MODE_PERCENTAGES:
        histogram_title += '(percentages, '
    else:
        histogram_title += '(counts, '
    histogram_title += 'conforming to the selections at the left) '
    histogram_title += get_year_range_text(year_first=query_params['year_first'],
                                           year_last=query_params['year_last'])
    histogram_title += ' for "' + query_params['value'] + '"'
    html_histogram = get_html_for_histogramcard(histogram_list=histogram_list,
                                                histogram_title=histogram_title,
                                                histogram_mode=page_params['histogram_mode'])

    modified_page_params: PageParams = page_params.copy()
    if page_params['histogram_mode'] == HISTOGRAM_MODE_PERCENTAGES:
        modified_page_params['histogram_mode'] = HISTOGRAM_MODE_COUNTS
        what_to_show = 'counts'
    else:
        modified_page_params['histogram_mode'] = HISTOGRAM_MODE_PERCENTAGES
        what_to_show = 'percentages'
    url = url_for(endpoint='osprofileresultpage.osprofileresultpage',
                  **merge_and_remove_empty(page_params=modified_page_params,
                                           query_params=query_params))
    html_histogram += '<br/>'
    html_histogram += '<div ' + form_button_on_one_line_flexspace_style + '>'
    html_histogram += '<a href="' + url + '">toggle this histogram to show '
    html_histogram += what_to_show + '</a> '

    modified_query_params: QueryParams = query_params.copy()
    if len(query_params['access']) == 0:
        modified_query_params['access'] = [ACCESS_OPEN]
        what_to_show = 'only research results that have "access" value "open"'
    else:
        modified_query_params['access'] = []
        what_to_show = 'research results with all "access" values'
    url = url_for(endpoint='osprofileresultpage.osprofileresultpage',
                  **merge_and_remove_empty(page_params=page_params,
                                           query_params=modified_query_params))
    html_histogram += '<a href="' + url + '">toggle this histogram to show '
    html_histogram += what_to_show + '</a>'
    html_histogram += '</div>'

    html += get_page_title(title='Open science profile for "' + query_params['value'] + '"')
    html += '<div class="w3-row-padding w3-stretch">'
    html += '<div class="w3-col s12 m3">'
    html += get_html_for_yearcard(for_year_histogram=year_histogram,
                                  header='Filter on "year"')
    html += get_html_for_facetcard(histogram=license_histogram,
                                   url_field_name='license',
                                   header='Filter on "license"')
    html += get_html_for_facetcard(histogram=access_histogram,
                                   url_field_name='access',
                                   header='Filter on "access"')
    html += '</div>'
    html += '<div class="w3-col s12 m9">'
    html += get_html_for_cardstart()
    html += html_histogram
    html += buttons
    html += get_html_for_cardend()
    html += '</div>'
    html += '</div>'

    html += get_html_for_cardstart()
    html += '<h2>What is an open science profile in Ricgraph?</h2>'
    html += 'In Ricgraph, an <em>open science profile</em> '
    html += 'relates to the distribution of research results '
    html += 'for a certain (sub-)organization, '
    html += 'in the three groups <em>research material</em>, <em>reporting material</em>, '
    html += 'and <em>engagement material</em>. '
    html += 'It is said that the form of this distribution may be characteristic '
    html += 'for such a (sub-)organization. '
    html += 'You can use this page to check this for yourself. '
    html += 'Also, you can choose whether you would like to see percentages '
    html += 'in the histogram, or rather prefer to see counts. '
    html += 'There are additional filters on <em>year</em>, '
    html += '<em>license</em>, and <em>access</em>. '
    html += '<br/><br/>'
    html += 'The three groups research material, reporting material, and engagement '
    html += 'material are defined in Ricgraph as:'
    html += '<ol><li>'
    html += '<em>Research material</em>: input/output and supporting material of the analysis.'
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


@_osdashboardresultpage_bp.route(rule='/osdashboardresultpage/', methods=['GET'])
def osdashboardresultpage() -> str:
    """Ricgraph Explorer entry, this 'page' only uses URL parameters.
    Find the open science dashboard of a (sub-)organization based on
    URL parameters passed.

    :return: HTML to be rendered.
    """
    page_params = get_url_page_params()
    query_params = get_url_query_params()
    page_params['histogram_mode'] = HISTOGRAM_MODE_COUNTS
    # For this page, we ignore the value of 'max_nr_items' if it is passed.
    query_params['max_nr_items'] = 0

    html = html_body_start
    html += get_you_searched_for_card(page_params=page_params,
                                      query_params=query_params)
    if (message := check_valid_year(year_first=query_params['year_first'],
                                    year_last=query_params['year_last'])) != '':
        html += get_message(message=message)
        return html + get_page_footer() + html_body_end

    (name_histogram, category_histogram, year_histogram,
     license_histogram, access_histogram) = \
        compute_histogramcards(query_params=query_params,
                               reverse_sort_on_value=False)
    if len(query_params['category_list']) == 0:
        # We cannot use category_histogram.
        query_params['category_list'] = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                                        item='researchresult_category_active')

    material_group = query_params['category_list'].copy()
    # Now convert it to a list of lists.
    material_group = [[x] for x in material_group]
    material_name = query_params['category_list'].copy()
    buttons = create_researchresult_buttons(category_histogram=category_histogram,
                                            material_group=material_group,
                                            material_name=material_name,
                                            page_params=page_params,
                                            query_params=query_params)

    html += get_page_title(title='Open science dashboard for "' + query_params['value'] + '"')

    html += '<div class="w3-row-padding w3-stretch">'
    html += '<div class="w3-col s12 m3">'
    html += get_histogramcards(name_histogram=[],
                               category_histogram=[],
                               year_histogram=year_histogram,
                               license_histogram=license_histogram,
                               access_histogram=access_histogram)
    html += '</div>'
    html += '<div class="w3-col s12 m9">'
    html += get_html_for_cardstart()
    histogram_title = 'Open science dashboard ('
    histogram_title += 'conforming to the selections at the left) '
    histogram_title += get_year_range_text(year_first=query_params['year_first'],
                                           year_last=query_params['year_last'])
    histogram_title += ' for "' + query_params['value'] + '". '
    histogram_title += 'You can modify the selections at the bottom of this page.'
    html += get_html_for_histogramcard(histogram_list=category_histogram,
                                       histogram_mode=page_params['histogram_mode'],
                                       histogram_title=histogram_title)
    html += buttons
    html += get_html_for_cardend()
    html += '</div>'
    html += '</div>'

    html += get_html_for_cardstart()
    html += '<h2>You can modify this dashboard by filtering</h2>'
    html += '<div class="w3-row-padding w3-stretch">'
    html += '<div class="w3-col s12 m3">'
    html += get_html_for_facetcard(histogram=category_histogram,
                                            url_field_name='category_list',
                                            header='Filter on "category"')
    html += '</div>'
    html += '<div class="w3-col s12 m3">'
    html += get_html_for_yearcard(for_year_histogram=year_histogram,
                                  header='Filter on "year"')
    html += '</div>'
    html += '<div class="w3-col s12 m3">'
    html += get_html_for_facetcard(histogram=license_histogram,
                                           url_field_name='license',
                                           header='Filter on "license"')
    html += '</div>'
    html += '<div class="w3-col s12 m3">'
    html += get_html_for_facetcard(histogram=access_histogram,
                                          url_field_name='access',
                                          header='Filter on "access"')
    html += '</div>'
    html += get_html_for_cardend()

    html += '</div>'
    html += '</div>'

    url_parameters = merge_and_remove_empty(page_params=page_params,
                                            query_params=query_params)
    html += get_html_for_cardstart()
    html += '<h2>Other exploration options for this organization</h2>'
    html += 'Finding collaborations may take (very) long depending on the '
    html += 'number of items involved. It may take anything between 5 seconds and 5 minutes. '
    html += 'If there appear to be a huge amount of collaborations (as in > 20000), your '
    html += 'browser may become unresponsive due to the huge number of lines that have to be drawn. '
    html += 'All filters will be propagated.'
    html += create_html_form(destination='collabsresultpage.collabsresultpage',
                             button_text='explore collaborations for this organization, may take long',
                             hidden_fields=url_parameters |
                                           {'histogram_mode': '',
                                            'collab_mode': 'return_collab_sankey',
                                            'start_orgs': query_params['value']
                                           })
    html += '<br/>'
    html += 'Choosing to get an open science profile for this (sub-)organization '
    html += 'will reset any filter on "category". '
    html += 'Other filters will be propagated.'
    html += create_html_form(destination='osprofileresultpage.osprofileresultpage',
                             button_text='get an open science profile for this organization',
                             hidden_fields=url_parameters |
                                           {'histogram_mode': '',
                                            'category_list': []
                                           })
    html += get_html_for_cardend()

    html += get_html_for_cardstart()
    html += '<h2>What is an open science dashboard in Ricgraph?</h2>'
    html += 'The open science dashboard in Ricgraph '
    html += 'allows to explore research results for a (sub-)organization. '
    html += 'Starting with a (sub-)organization, you can filter its '
    html += 'research results based on "category", "year", "license", '
    html += 'and "access" values. '
    html += 'After clicking "refresh", the result of your selection will '
    html += 'be shown as a histogram. '
    html += get_html_for_cardend()

    return html + get_page_footer() + html_body_end


def create_researchresult_buttons(category_histogram: list,
                                  material_group: list,
                                  material_name: list,
                                  page_params: PageParams,
                                  query_params: QueryParams) -> str:
    """Create the buttons that correspond to 'material_name'.

    :param category_histogram: The histogram to build the buttons from.
    :param material_group: List of lists of research result items.
    :param material_name: List of names how to name these research result items.
    :param page_params: Parameters related to the page passed in the URL.
    :param query_params: Parameters related to the query passed in the URL.
    :return: HTML for the buttons to get more information about the items
      in the histogram.
    """
    # Use a dict for efficiency.
    histogram_by_name = {
        item['name']: item['value']
        for item in category_histogram
    }

    buttons = '</p><div ' + form_button_on_one_line_flexspace_style + '>'
    for group, name in zip(material_group, material_name):
        value = sum(histogram_by_name.get(cat, 0) for cat in group)
        if value == 0:
            # Skip buttons for groups that have 0 elements.
            continue

        url = url_for(endpoint='resultspage',
                      **merge_and_remove_empty(page_params=page_params | {'histogram_mode': '',
                                                                          'view_mode': 'view_regular_table_organization_addinfo'},
                                               query_params=query_params) | {'category_list': group})

        buttons += '<a href="' + url + '" class="w3-bar-item'
        buttons += button_style + '"' + form_button_on_one_line_width
        buttons += '>show ' + name + '</a>'

    buttons += '</div>'
    return buttons
