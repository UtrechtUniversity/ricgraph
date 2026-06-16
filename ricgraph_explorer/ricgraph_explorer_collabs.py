# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
#
# Copyright (c) 2025 Rik D.T. Janssen
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
# Ricgraph Explorer Collaborations between (sub-)organizations functions.
#
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, November 2025.
#
# ########################################################################


from urllib.parse import urlencode
from flask import Blueprint, url_for
from markupsafe import escape

from ricgraph import (ORGANIZATION_CATEGORY_ORGANIZATION, create_ricgraph_key,
                      get_year_range_text)
from ricgraph_explorer_constants import (RICGRAPH_NODEINFO,
                                         html_body_start, html_body_end,
                                         button_style, button_width,
                                         SEARCH_MODE_VALUE)
from ricgraph_explorer_table import get_regular_table
from ricgraph_explorer_utils import (get_url_page_params, get_url_query_params,
                                     get_global_list)
from ricgraph_explorer_html import (get_html_for_cardstart, get_html_for_cardend,
                                    get_spinner,
                                    get_message,
                                    get_you_searched_for_card, get_page_title,
                                    get_page_footer,
                                    compute_histogramcards,
                                    get_html_for_yearcard,
                                    get_html_for_facetcard,
                                    get_html_for_radiobuttoncomponent,
                                    get_html_for_checkboxcomponent)
from ricgraph_explorer_datavis import (org_collaborations_diagram,
                                       org_collaborations_persons_results)



_collabspage_bp = Blueprint(name='collabspage', import_name=__name__)
_collabsresultpage_bp = Blueprint(name='collabsresultpage', import_name=__name__)


@_collabspage_bp.route(rule='/collabspage/', methods=['GET'])
def collabspage() -> str:
    """Ricgraph Explorer entry, this 'page' does not have any url parameters.
    Probably, in the future, it should have.
    The Explore collaborations page.

    Possible url parameters are:
    - start_orgs: the organization(s) to start with. This may be
      a substring, then a match on the start of the organization name is done.

    :return: HTML to be rendered.
    """
    page_params = get_url_page_params()
    query_params = get_url_query_params()
    # For this page, we ignore the value of 'max_nr_items' if it is passed.
    query_params['max_nr_items'] = 0

    start_orgs = query_params['start_orgs']

    html = html_body_start
    html += get_you_searched_for_card(page_params=page_params,
                                      query_params=query_params)
    html += get_page_title(title='Explore collaborations page')
    html += get_html_for_cardstart()
    html += 'Using this page, you can explore collaborations between organizations in Ricgraph. '
    html += 'You may also be able to explore collaborations between sub-organizations, '
    html += 'such as between faculties/departments/chairs of one research organization '
    html += 'and (sub-)organizations of other organizations. '
    html += 'This depends on whether sub-organizations have been harvested '
    html += 'in this instance  of Ricgraph. '
    html += '<p/>'
    html += 'In Ricgraph, collaborations are defined as follows <a href="#ref1">[1]</a>:'
    html += '<p/>'
    html += '''<table style="font-size:100%; width:100%; table-layout:fixed; 
                      border-collapse:collapse; border:1px solid black;">
                 <tr>
                   <td style="width:35%; border:1px solid black; padding:1em;">
                     a collaboration between organization <em>start organization</em> 
                     and organization <em>collaborating organization</em> 
                   </td>
                   <td style="width:15%; text-align: center; border:1px solid black; padding:1em;">
                     is defined as
                   </td>
                   <td style="width:50%; border:1px solid black; padding:1em;">
                     a path from organization <em>start organization</em> to 
                     organization <em>collaborating organization</em> 
                     conforming to both of the following conditions:
                     <ul>
                       <li>having one research result in common; </li>
                       <li>having three nodes in between: a person, 
                           a research result, and a person.</li>
                     </ul>
                   </td>
                 </tr>
               </table>'''
    html += '<p/>'
    html += get_html_for_cardend()

    html += get_html_for_cardstart()
    base_url = url_for(endpoint='searchpage') + '?'
    base_url += urlencode(query={'search_mode': SEARCH_MODE_VALUE,
                                 'category': ORGANIZATION_CATEGORY_ORGANIZATION})
    form = '<form method="get" action="' + url_for(endpoint='collabsresultpage.collabsresultpage') + '">'
    form += '<label for="start_orgs">Type the name for <em>start organization</em> '
    form += '(or enter text that begins a (sub-)organization name):</label>'
    form += '<input id="start_orgs" class="w3-input w3-border" '
    form += 'type=text name=start_orgs value="' + str(escape(start_orgs)) + '">'

    form += 'Note. For now, you have to type the exact spelling in this field, '
    form += 'including correct upper and lower case. '
    form += '<a href="' + base_url + '" target="_blank">'
    form += 'Click here to search for a (sub-)organization '
    form += 'and find this correct spelling</a>. '
    form += 'Then you can copy and paste it in the <em>start organization</em> '
    form += 'input field above. '
    form += 'This also holds for the <em>collaborating organization</em> input '
    form += 'field below. For example, if you have "DUT", you can type e.g. '
    form += '"DUT", "DUT Faculty", or "DUT Faculty: Mechanical Engineering", '
    form += 'but not "Faculty", "dut faculty", or "Faculty: Mechanical Engineering" '
    form += '(in fact, you can, but they will not match DUT sub-organizations). '
    form += '<br/>'
    form += '<br/>'
    form += '<label for="collab_orgs">Type the name for <em>collaborating organization</em> '
    form += '(or enter text that begins a (sub-)organization name, or leave it empty to '
    form += 'match any organization (if you leave it empty, only <em>top level</em> '
    form += 'organization names will be retrieved)):</label>'
    form += '<input id="collab_orgs" class="w3-input w3-border" type=text name=collab_orgs>'
    form += '<br/>'

    header = 'Restrict the collaborations to research results '
    header += 'of a specific <em>category</em>: '
    researchresult_category_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                                     item='researchresult_category_active')
    form += get_html_for_checkboxcomponent(checkboxes=researchresult_category_active,
                                           url_field_name='category_list',
                                           header=header)
    form += '<br/>'

    radiobuttons = [{'button_id': 'return_collab_sankey',
                     'button_label': 'return the collaborations in a Sankey diagram'},
                    {'button_id': 'return_startorg_persons',
                     'button_label': 'return the persons from '
                                     '<em>start organizations</em> '
                                     'involved in the collaborations'},
                    {'button_id': 'return_researchresults',
                     'button_label': 'return the research results that '
                                     'originate from the collaborations'},
                    {'button_id': 'return_collaborg_persons',
                     'button_label': 'return the persons from '
                                     '<em>collaborating organizations</em> '
                                     'involved in the collaborations'}]
    header = 'Choose how to explore collaborations:'
    form += get_html_for_radiobuttoncomponent(radiobuttons=radiobuttons,
                                              url_field_name='collab_mode',
                                              header=header)
    form += '<p/>'

    form += 'Finding collaborations may take (very) long depending on the '
    form += 'number of items involved. It may take anything between 5 seconds and 5 minutes. '
    form += 'If you have chosen to view the Sankey diagram, and '
    form += 'there appear to be a huge amount of collaborations (as in > 20000), your '
    form += 'browser may become unresponsive due to the huge number of lines that have to be drawn. '
    form += '<p/><input class="' + button_style + '" ' + button_width
    form += 'type=submit value="find collaborations, this may take (very) long">'
    form += '<p/>'
    form += '</form>'
    html += form
    message = 'Finding collaborations, this may take (very) long. Please wait...'
    html += get_spinner(message=message)
    html += get_html_for_cardend()

    html += get_html_for_cardstart()
    html += 'To read more about collaborations in Ricgraph:'
    html += '<p id="ref1">[1] '
    html += 'Rik D.T. Janssen (2025). <em>Utilizing Ricgraph to gain insights into '
    html += 'research collaborations across institutions, at every organizational '
    html += 'level</em>. [preprint]. <a href="https://doi.org/10.2139/ssrn.5524439">'
    html += 'https://doi.org/10.2139/ssrn.5524439</a>.</p>'
    html += get_html_for_cardend()
    html += get_page_footer() + html_body_end
    return html


@_collabsresultpage_bp.route(rule='/collabsresultpage/', methods=['GET'])
def collabsresultpage() -> str:
    """Ricgraph Explorer entry, this 'page' only uses URL parameters.
    Find collaborations based on URL parameters passed.

    Possible url parameters are:
    - start_orgs: the organization(s) to start with. This may be
      a substring, then a match on the start of the organization name is done.
    - collab_orgs: if specified, only return organization(s) that
      collaborate with start_orgs. If empty '', return any organization(s)
      that start_orgs collaborate with. It may also be
      a substring, then a match on the start of the organization name is done.
    - category_list: either a string which indicates that we only want to
      return collaborations for this research result category,
      or a list containing several category names, indicating
      that we want all collaborations for those categories.
      If empty (empty string), return all collaborations.
    - collab_mode: one of the following:
      - mode = 'return_collab_sankey': return the collaborations in a Sankey diagram.
      - mode = 'return_startorg_persons': return the person-roots from start_organizations.
      - mode = 'return_researchresults': return the research results.
      - mode = 'return_collaborg_persons': return the person-roots from collab_organizations.
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
    html += get_you_searched_for_card(page_params=page_params,
                                      query_params=query_params)
    # A fragment of text to be reused. Escape organization names for safety, since
    # they will be included in the HTML of the webpage that is being generated.
    start_collab_html = "'" + str(escape(query_params['start_orgs'])) + "' and "
    start_collab_html += 'any organization' if query_params['collab_orgs'] == '' \
                                            else "'" + str(escape(query_params['collab_orgs'])) + "'"
    start_collab_html += '. '
    html += get_page_title(title='Collaborations between ' + start_collab_html)
    html += get_html_for_cardstart()
    if page_params['collab_mode'] == 'return_collab_sankey':
        html += 'This Sankey diagram shows the collaborations between '
        html += start_collab_html
        html += 'It conforms to the selections at the bottom of this page. '
        html += 'There, you can also modify these selections and recreate this diagram. '
        html += '<p/>'
        result_html = org_collaborations_diagram(page_params=page_params,
                                                 query_params=query_params,
                                                 diagram_type='sankey',
                                                 caption='',
                                                 generate_full_html=False)
        header = ''
        if result_html == '':
            result_html = get_message('Nothing found.')
        else:
            header += '<p/>If you hover the lines in the diagram, you will get a tooltip. After '
            header += 'clicking a line, you can explore the collaborations in more depth '
            header += 'by clicking the buttons in the tooltip. '
            header += 'Click "Close" to remove the tooltip.'
            result_html = header + '<p/>' + result_html
    else:
        header = 'This table shows the '
        if page_params['collab_mode'] == 'return_researchresults':
            header += 'research results that originate from the collaborations between '
            header += start_collab_html
            what = 'These research results '
        elif page_params['collab_mode'] == 'return_startorg_persons':
            header += 'persons that are participating in the collaborations between '
            header += start_collab_html
            header += 'They are member of the first organization. '
            what = 'The research results involved in these collaborations '
        else:
            header += 'persons that are participating in the collaborations between '
            header += start_collab_html
            header += 'They are member of the latter organization(s). '
            what = 'The research results involved in these collaborations '
        year_range_text = get_year_range_text(year_first=query_params['year_first'],
                                              year_last=query_params['year_last'])
        what += 'are ' + year_range_text + ', and '
        if len(query_params['category_list']) == 0:
            header += what + 'include all categories. '
        else:
            header += what + 'include the following categories: '
            header += str(query_params['category_list']) + '. '
        if len(query_params['license']) == 0:
            header += 'They also include all license values, '
        else:
            header += 'They also include the following license values: '
            header += str(query_params['license']) + ', '
        if len(query_params['access']) == 0:
            header += 'and all access values. '
        else:
            header += 'and the following access values: '
            header += str(query_params['access']) + '. '
        nodes_list = org_collaborations_persons_results(query_params=query_params,
                                                        mode=page_params['collab_mode'])
        if len(nodes_list) == 0:
            result_html = get_message(header + '<p/>Nothing found.')
        else:
            result_html = get_regular_table(nodes_list=nodes_list,
                                            page_params=page_params | {'collab_mode': ''},
                                            query_params=query_params | {'start_orgs': '',
                                                                         'collab_orgs': ''},
                                            table_header=header)
    html += result_html
    html += get_html_for_cardend()

    if page_params['collab_mode'] != 'return_collab_sankey':
        # We are done.
        html += get_page_footer() + html_body_end
        return html

    html += get_html_for_cardstart()
    html += '<h2>You can modify this collaboration diagram by filtering</h2>'
    key = create_ricgraph_key(name='ORGANIZATION_NAME',
                              value=query_params['start_orgs'])
    (_, _, year_histogram,
     license_histogram, access_histogram) = \
        compute_histogramcards(query_params=query_params | {'key': key},
                               reverse_sort_on_value=False)

    # If 'start_orgs' is not a full organization name, but only an
    # initial part of an organization name (i.e. it is 'UU Department'
    # instead of a department name), compute_histogramcards()
    # will return empty lists for year_histogram, license_histogram,
    # and access_histogram. We have to correct for them, to be able
    # to filter on them.
    # Note that 'value' does not matter since we don't show it.
    if len(year_histogram) == 0:
        for item in get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                    item='year_active'):
            year_histogram.append({'name': item,
                                   'value': 0})
        year_histogram.sort(key=lambda x: x['name'].lower())
    if len(license_histogram) == 0:
        if len(query_params['license']) == 0:
            items = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                    item='license_active')
        else:
            items = query_params['license'].copy()
        for item in items:
            license_histogram.append({'name': item,
                                      'value': 0})
        license_histogram.sort(key=lambda x: x['name'].lower())
    if len(access_histogram) == 0:
        if len(query_params['access']) == 0:
            items = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                    item='access_active')
        else:
            items = query_params['access'].copy()
        for item in items:
            access_histogram.append({'name': item,
                                     'value': 0})
        access_histogram.sort(key=lambda x: x['name'].lower())

    # Create a category_histogram based on what is in
    # query_params['category_list'], because it may be different from what
    # compute_histogramcards() may deliver (it may have been passed
    # from a previous page).
    # Note that 'value' does not matter since we don't show it.
    category_histogram = []
    for item in query_params['category_list']:
        category_histogram.append({'name': item,
                                   'value': 0})
    category_histogram.sort(key=lambda x: x['name'].lower())
    html += '<div class="w3-row-padding w3-stretch">'
    html += '<div class="w3-col s12 m3">'
    html += get_html_for_facetcard(histogram=category_histogram,
                                   url_field_name='category_list',
                                   header='Filter on "category"',
                                   show_counts=False)
    html += '</div>'
    html += '<div class="w3-col s12 m3">'
    html += get_html_for_yearcard(for_year_histogram=year_histogram,
                                  header='Filter on "year"')
    html += '</div>'
    html += '<div class="w3-col s12 m3">'
    html += get_html_for_facetcard(histogram=license_histogram,
                                   url_field_name='license',
                                   header='Filter on "license"',
                                   show_counts=False)
    html += '</div>'
    html += '<div class="w3-col s12 m3">'
    html += get_html_for_facetcard(histogram=access_histogram,
                                   url_field_name='access',
                                   header='Filter on "access"',
                                   show_counts=False)
    html += '</div>'
    html += get_html_for_cardend()

    html += get_page_footer() + html_body_end
    return html
