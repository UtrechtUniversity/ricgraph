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
# Ricgraph Explorer functions related to data visualization.
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Ricgraph Explorer uses W3.CSS, a modern, responsive, mobile first CSS framework.
# See https://www.w3schools.com/w3css/default.asp.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, January 2023.
# Extended Rik D.T. Janssen, February, September 2023 to May 2025.
#
# ########################################################################


from json import dumps
from ricgraph import  create_unique_string
from ricgraph_explorer_utils import get_message
from ricgraph_explorer_javascript import get_html_for_histogram_javascript


def get_html_for_histogram(histogram_list: list,
                           histogram_width: int = 200,
                           histogram_title: str = ''):
    """This function creates a histogram using the Observable D3 and Observable Plot framework
    for data visualization. See https://d3js.org and https://observablehq.com/plot.

    :param histogram_list: A list of histogram data to be plotted in the histogram.
      Each element in the list has a 'name' and 'value'.
      The histogram will be in the order as specified in the list. It is assumed that
      the largest value of the histogram is in the first element of the list. This
      value is used to compute whether a histogram label should be shown in the histogram
      bar or next to it.
    :param histogram_width: The width of the histogram, in pixels.
    :param histogram_title: The title of the histogram.
    :return: html to be rendered.
    """
    # The required js files for Observable are included in html_body_end above.
    # The code below is inspired by an example from
    # https://observablehq.com/@observablehq/plot-labelled-horizontal-bar-chart-variants.

    if len(histogram_list) == 0:
        message = 'Unexpected result in get_html_for_histogram(): '
        message += 'The histogram list is empty.'
        return get_message(message=message)

    # Note: 'histogram_list' is expected to be sorted with the largest value first.
    bar_label_threshold = histogram_list[0]['value']
    histogram_json = dumps(histogram_list)

    # The plot name should be unique, otherwise we get strange side effects.
    plot_name = 'myplot' + '_' + create_unique_string()

    html = '<div class="w3-card-4">'
    if histogram_title != '':
        html += '<div class="w3-container uu-yellow">'
        html += '<b>' + histogram_title + '</b>'
        html += '</div>'
    html += '</br>'
    html += '<div id="' + plot_name + '"></div>'
    html += '</br></div>'

    javascript = get_html_for_histogram_javascript(histogram_json=histogram_json,
                                                   histogram_width=histogram_width,
                                                   bar_label_threshold=bar_label_threshold,
                                                   plot_name=plot_name)
    return html + javascript
