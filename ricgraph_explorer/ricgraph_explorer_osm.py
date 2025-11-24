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

from ricgraph_explorer_constants import html_body_start, html_body_end
from ricgraph_explorer_init import get_ricgraph_explorer_global
from ricgraph_explorer_utils import (get_html_for_cardstart, get_html_for_cardend,
                                     create_html_form,
                                     get_page_title)


_osmpage_bp = Blueprint(name='osmpage', import_name=__name__)


# For future usage.
@_osmpage_bp.route(rule='/osmpage/', methods=['GET'])
def osmpage() -> str:
    """Ricgraph Explorer entry, this 'page' does not have any url parameters.
    Probably, in the future, it should have.
    The Explore open science monitoring page.

    :return: html to be rendered.
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
    html += get_html_for_cardend()

    html += page_footer + html_body_end
    return html
