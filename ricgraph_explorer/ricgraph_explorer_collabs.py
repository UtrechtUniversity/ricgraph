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

from ricgraph import ROTYPE_PUBLICATION
from ricgraph_explorer_constants import (html_body_start, html_body_end,
                                         button_style, button_width,
                                         DISCOVERER_MODE_ALL,
                                         COLLABORATION_MODES_ALL,
                                         MAX_ROWS_IN_TABLE,
                                         MAX_ITEMS)
from ricgraph_explorer_init import get_ricgraph_explorer_global
from ricgraph_explorer_utils import (get_html_for_cardstart, get_html_for_cardend,
                                     get_url_parameter_value, get_url_parameter_list,
                                     get_message,
                                     get_spinner, get_page_title)
from ricgraph_explorer_table import get_regular_table
from ricgraph_explorer_datavis import (org_collaborations_diagram,
                                       org_collaborations_persons_results)



_collabspage_bp = Blueprint(name='collabspage', import_name=__name__)
_collabsresultpage_bp = Blueprint(name='collabsresultpage', import_name=__name__)


@_collabspage_bp.route(rule='/collabspage/', methods=['GET'])
def collabspage() -> str:
    """Ricgraph Explorer entry, this 'page' does not have any url parameters.
    Probably, in the future, it should have.
    The Explore collaborations page.

    :return: html to be rendered.
    """
    page_footer = get_ricgraph_explorer_global('page_footer')

    html = html_body_start
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
    base_url += urlencode(query={'search_mode': 'value_search',
                                 'category': 'organization'})
    form = '<form method="get" action="/collabsresultpage/">'
    form += '<label for="start_orgs">Type the name for <em>start organization</em> '
    form += '(or enter text that begins a (sub-)organization name):</label>'
    form += '<input id="start_orgs" class="w3-input w3-border" type=text name=start_orgs>'

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
    form += '<label for="category_list">Restrict the collaborations to research results '
    form += 'of a specific <em>category</em> '
    form += '(or leave it empty to match research results of any category, or type '
    form += '<em>publication_all</em> to match any publication research result):</label>'
    form += '<input id="category_list" class="w3-input w3-border" list="resout_types_all_datalist"'
    form += 'name=category_list autocomplete=off>'
    form += '<div class="firefox-only">Click twice to get a dropdown list.</div>'
    form += str(get_ricgraph_explorer_global(name='resout_types_all_datalist'))

    form += '<br/>'
    form += '<fieldset>'
    form += '<legend>Choose how to explore collaborations:</legend>'
    form += '<input id="return_collab_sankey" class="w3-radio" type="radio" '
    form += 'name="collab_mode" value="return_collab_sankey" checked>'
    form += ' return the collaborations in a Sankey diagram'
    form += '<br/>'
    form += '<input id="return_startorg_persons" class="w3-radio" type="radio" '
    form += 'name="collab_mode" value="return_startorg_persons">'
    form += ' return the persons from <em>start organizations</em> '
    form += 'involved in the collaborations'
    form += '<br/>'
    form += '<input id="return_research_results" class="w3-radio" type="radio" '
    form += 'name="collab_mode" value="return_research_results">'
    form += ' return the research results that originate from the collaborations'
    form += '<br/>'
    form += '<input id="return_collaborg_persons" class="w3-radio" type="radio" '
    form += 'name="collab_mode" value="return_collaborg_persons">'
    form += ' return the persons from <em>collaborating organizations</em> '
    form += 'involved in the collaborations'
    form += '<br/>'
    form += '</fieldset>'
    form += '<p/>'

    form += 'Finding collaborations may take (very) long depending on the '
    form += 'number of items involved. It may take anything between 5 seconds and 10 minutes. '
    form += 'If you have chosen to view the Sankey diagram, and '
    form += 'there appear to be a huge amount of collaborations (as in > 20000), your '
    form += 'browser may become unresponsive due to the hugh number of lines that have to be drawn. '
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
    html += page_footer + html_body_end
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
      - mode = 'return_research_results': return the research results.
      - mode = 'return_collaborg_persons': return the person-roots from collab_organizations.
    - discoverer_mode: the discoverer_mode to use, 'details_view' to see all details,
      or 'person_view' to have a nicer layout.
    - max_nr_items: the maximum number of items to return, or 0 to return all items.
    - max_nr_table_rows: the maximum number of rows in a table to return (the page
      size of the table), or 0 to return all rows.

    :return: html to be rendered.
    """
    page_footer = get_ricgraph_explorer_global('page_footer')
    start_orgs = get_url_parameter_value(parameter='start_orgs', use_escape=False)
    collab_orgs = get_url_parameter_value(parameter='collab_orgs', use_escape=False)
    category_list = get_url_parameter_list(parameter='category_list')
    if len(category_list) == 1 and category_list[0] == 'publication_all':
        # Special case: return all publication type research results.
        category_list = ROTYPE_PUBLICATION.copy()
    collab_mode = get_url_parameter_value(parameter='collab_mode')
    discoverer_mode = get_url_parameter_value(parameter='discoverer_mode',
                                              allowed_values=DISCOVERER_MODE_ALL,
                                              default_value=get_ricgraph_explorer_global(name='discoverer_mode_default'))
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
    if collab_mode not in COLLABORATION_MODES_ALL:
        html += get_message(message='Unknown collab_mode: "' + collab_mode + '".')
        html += page_footer + html_body_end
        return html

    html += get_page_title(title='Collaborations related to these organizations')
    html += get_html_for_cardstart()
    # A fragment of text to be reused. Escape organization names for safety, since
    # they will be included in the HTML of the webpage that is being generated.
    start_collab_html = '"' + str(escape(start_orgs)) + '" and '
    start_collab_html += 'any organization.' if collab_orgs == '' else '"' + str(escape(collab_orgs)) + '"'
    if collab_mode == 'return_collab_sankey':
        header = 'This Sankey diagram shows the collaborations between '
        header += start_collab_html + '. '
        if collab_orgs == '':
            result_html = org_collaborations_diagram(start_organizations=start_orgs,
                                                     collab_organizations=collab_orgs,
                                                     research_result_category=category_list,
                                                     diagram_type='sankey',
                                                     caption='',
                                                     generate_full_html=False)
        else:
            result_html = org_collaborations_diagram(start_organizations=start_orgs,
                                                     collab_organizations=collab_orgs,
                                                     research_result_category=category_list,
                                                     diagram_type='sankey',
                                                     caption='',
                                                     generate_full_html=False)
        if len(category_list) == 0:
            header += ' It shows collaborations for all categories. '
        else:
            header += ' It shows collaborations for the following categories: '
            header += str(category_list) + '. '
        if result_html == '':
            result_html = get_message(header + '<p/>Nothing found.')
        else:
            header += '<p/>If you hover the lines in the diagram, you will get a tooltip. After '
            header += 'clicking a line, you can explore the collaborations in more depth '
            header += 'by clicking the buttons in the tooltip. '
            header += 'Click "Close" to remove the tooltip.'
            result_html = header + '<p/>' + result_html
    else:
        header = 'This table shows the '
        if collab_mode == 'return_research_results':
            header += 'research results that originate from the collaborations between '
            header += start_collab_html + '. '
            what = 'research results'
        elif collab_mode == 'return_startorg_persons':
            header += 'persons that are participating in the collaborations between '
            header += start_collab_html
            header += ', they are member of the first organization.'
            what = 'collaborations'
        else:
            header += 'persons that are participating in the collaborations between '
            header += start_collab_html
            header += ', they are member of the latter organization(s).'
            what = 'collaborations'
        if len(category_list) == 0:
            header += ' It shows ' + what + ' for all categories.'
        else:
            header += ' It shows ' + what + ' for the following categories: '
            header += str(category_list) + '.'
        nodes_list = org_collaborations_persons_results(start_organizations=start_orgs,
                                                        collab_organizations=collab_orgs,
                                                        research_result_category=category_list,
                                                        mode=collab_mode)
        if len(nodes_list) == 0:
            result_html = get_message(header + '<p/>Nothing found.')
        else:
            result_html = get_regular_table(nodes_list=nodes_list,
                                            table_header=header,
                                            discoverer_mode=discoverer_mode,
                                            extra_url_parameters=extra_url_parameters)
    html += result_html
    html += get_html_for_cardend()

    html += page_footer + html_body_end
    return html
