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
# Ricgraph Explorer Open science monitoring functions.
#
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, November 2025.
#
# ########################################################################


from flask import Blueprint

from ricgraph_explorer_constants import (html_body_start, html_body_end,
                                         html_preamble,
                                         page_footer_wsgi, page_footer_development,
                                         button_style, button_width,
                                         VIEW_MODE_ALL,
                                         DEFAULT_SEARCH_MODE, DEFAULT_DISCOVERER_MODE,
                                         DETAIL_COLUMNS, ID_COLUMNS, ORGANIZATION_COLUMNS,
                                         RESEARCH_OUTPUT_COLUMNS, MAX_ROWS_IN_TABLE,
                                         MAX_ITEMS, SEARCH_STRING_MIN_LENGTH)
from ricgraph_explorer_init import initialize_ricgraph_explorer, get_ricgraph_explorer_global
from ricgraph_explorer_utils import (get_html_for_cardstart, get_html_for_cardend,
                                     create_html_form, get_url_parameter_value,
                                     get_message, get_found_message,
                                     get_you_searched_for_card, get_page_title)

osmpage_bp = Blueprint('osmpage', __name__)


@osmpage_bp.route(rule='/osmpage/', methods=['GET'])
def osmpage() -> str:
    """Ricgraph Explorer entry, this 'page' does not have any parameters.
    Probably, in the future, it should have.
    The Open science monitoring page.

    returns html to parse.
    """
    page_footer = get_ricgraph_explorer_global('page_footer')

    # In the other Ricgraph Explorer flow, the following params come from
    # the search page, but we skip that. We set them anyway to be sure.
    discoverer_mode = DEFAULT_DISCOVERER_MODE
    extra_url_parameters = {}
    max_nr_items = str(MAX_ITEMS)
    if not max_nr_items.isnumeric():
        # This also catches negative numbers, they contain a '-' and are not numeric.
        # See https://www.w3schools.com/python/ref_string_isnumeric.asp.
        max_nr_items = str(MAX_ITEMS)
    extra_url_parameters['max_nr_items'] = max_nr_items
    max_nr_table_rows = str(MAX_ROWS_IN_TABLE)
    if not max_nr_table_rows.isnumeric():
        max_nr_table_rows = str(MAX_ROWS_IN_TABLE)
    extra_url_parameters['max_nr_table_rows'] = max_nr_table_rows

    html = html_body_start

    html += get_page_title(title='Open science monitoring')
    html += get_html_for_cardstart()
    html += 'You can use text in a card like this.'
    html += get_html_for_cardend()

    html += get_html_for_cardstart()
    html += '<h2>A title is done like this</h2>'
    html += 'And then some more text.'
    html += get_html_for_cardend()

    html += page_footer + html_body_end
    return html
