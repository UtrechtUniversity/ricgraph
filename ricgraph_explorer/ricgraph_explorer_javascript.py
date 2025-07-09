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
# Ricgraph Explorer JavaScript related functions.
# Each JavaScript function is named like this: function_name_javascript().
# Such a function belong to a corresponding function_name().
#
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, 2023.
# Extended Rik D.T. Janssen, July 2025.
#
# ########################################################################


def get_regular_table_javascript(table_id: str,
                                 len_nodes_list: int,
                                 max_nr_table_rows: int) -> str:
    """Create a paginated html table for all nodes in the list.
    This javascript code is for the pagination of the table.

    :param table_id: the table id to use.
    :param len_nodes_list: the length of the list of nodes to put in the table.
    :param max_nr_table_rows: the maximum number of rows in a page of the table.
    :return: html to be rendered.
    """
    javascript = f"""
                 <script>
                 // Initialize currentPage and totalPages for all tables
                 currentPage['{table_id}'] = 1; 
                 totalPages['{table_id}'] = Math.ceil({len_nodes_list} / {max_nr_table_rows});
                 function showPage(page, tableId) {{
                     page = parseInt(page);
                     if (page < 1 || page > totalPages[tableId]) return;

                     // Update table visibility
                     document.querySelectorAll(`.table-${{tableId}}-page-${{currentPage[tableId]}}`)
                           .forEach(tr => tr.style.display = 'none');
                     document.querySelectorAll(`.table-${{tableId}}-page-${{page}}`)
                           .forEach(tr => tr.style.display = '');

                     currentPage[tableId] = page;
                     updatePagination(tableId);
                 }}
                 function updatePagination(tableId) {{
                     const buttons = document.querySelectorAll(`.page-num-${{tableId}}`);
                     const total = totalPages[tableId];
                     let start = 1;
                     if (total > 5) {{
                         if (currentPage[tableId] <= 3) {{
                             start = 1;
                         }} else if (currentPage[tableId] >= total - 2) {{
                             start = total - 4;
                         }} else {{
                             start = currentPage[tableId] - 2;
                         }}
                     }}
                     buttons.forEach((btn, index) => {{
                         const pageNum = start + index;
                         if (btn) {{
                             btn.textContent = pageNum;
                             btn.onclick = function() {{ showPage(pageNum, tableId); }};
                             btn.classList.toggle('uu-yellow', pageNum === currentPage[tableId]);
                             btn.style.display = pageNum <= total ? '' : 'none';
                         }}
                     }});
                     const ellipsisLeft = document.querySelector(`.ellipsis-left-${{tableId}}`);
                     const ellipsisRight = document.querySelector(`.ellipsis-right-${{tableId}}`);
                     if (ellipsisLeft) ellipsisLeft.style.display = start > 1 ? '' : 'none';
                     if (ellipsisRight) 
                        ellipsisRight.style.display = (start + buttons.length - 1) < total ? '' : 'none';
                     const firstButton = document.querySelector(`a[onclick="showPage(1, '${{tableId}}')"]`);
                     const prevButton = document.querySelector(`a[onclick=
                                        "showPage(currentPage['${{tableId}}']-1, '${{tableId}}')"]`);
                     const nextButton = document.querySelector(`a[onclick=
                                        "showPage(currentPage['${{tableId}}']+1, '${{tableId}}')"]`);
                     const lastButton = document.querySelector(`a[onclick="showPage(${{total}}, '${{tableId}}')"]`);
                     if (firstButton) firstButton.classList.toggle('w3-disabled', currentPage[tableId] === 1);
                     if (prevButton) prevButton.classList.toggle('w3-disabled', currentPage[tableId] === 1);
                     if (nextButton) nextButton.classList.toggle('w3-disabled', currentPage[tableId] === total);
                     if (lastButton) lastButton.classList.toggle('w3-disabled', currentPage[tableId] === total);
                 }}
                 document.addEventListener('DOMContentLoaded', () => {{
                     {f'updatePagination("{table_id}");'}
                 }});
                 </script>
                 """
    return javascript


# This code is inspired by https://www.w3schools.com/w3css/w3css_tabulators.asp.
def get_tabbed_table_javascript(table_id: str) -> str:
    """JavaScript to create a html table with tabs for all nodes in the list.
    This code creates the tabs.

    :param table_id: table_id of the table.
    :return: html to be rendered.
    """
    javascript = f"""
                 <script>
                 function openTab_{table_id}(evt, tabName, table_id) {{
                   var i, x, tablinks;
                   x = document.getElementsByClassName("tabitem");
                   for (i = 0; i < x.length; i++) {{
                     if (x[i].className.split(' ').indexOf(table_id) != -1) {{
                       x[i].style.display = "none";
                     }}
                   }}
                   tablinks = document.getElementsByClassName("tablink");
                   for (i = 0; i < x.length; i++) {{
                     if (tablinks[i].className.split(' ').indexOf(table_id) != -1) {{
                       tablinks[i].className = tablinks[i].className.replace(" uu-orange", "");
                     }}
                   }}
                   document.getElementById(tabName).style.display = "block";
                   evt.currentTarget.className += " uu-orange";
                 }}
                 </script>
                 """
    return javascript


def get_html_for_tableend_javascript(figure_filename: str) -> str:
    """This javascript code is to export the table with the given tableId as a CSV file.
    Only maxRows are exported (as a kind of safety not to be able to export everything).
    Note that the table is exported as it is shown on the webpage.

    :param figure_filename: the filename of the resulting csv download file.
    :return: html to be rendered.
    """
    javascript = f'''
                 <script>
                 function exportTableToCSV(tableId, maxRows) {{
                     const rows = document.querySelectorAll(`#${{tableId}} tr`);
                     const rowsToExport = [];
                     // Always include the header row (first row), then up to (maxRows) rows total (header + data)
                     for (let i = 0; i < rows.length && i <= maxRows; i++) {{
                         rowsToExport.push(rows[i]);
                     }}
                     // For each row, get all cells (th or td), and for each cell:
                     // - Replace any double quotes with two double quotes (CSV escaping).
                     // - Enclose every cell value in double quotes.
                     // Join each cell in a row with commas, and join rows with newlines.
                     const csvContent = Array.from(rowsToExport).map(row =>
                         Array.from(row.children).map(cell =>
                             '"' + cell.innerText.replace(/"/g, '""') + '"'
                         ).join(',')
                     ).join('\\n');
                     const blob = new Blob([csvContent], {{type: 'text/csv'}});
                     // Create a hidden <a> element to trigger the download.
                     const link = document.createElement('a');
                     link.href = URL.createObjectURL(blob);
                     link.download = '{figure_filename}';
                     document.body.appendChild(link);
                     link.click();
                     document.body.removeChild(link);
                     URL.revokeObjectURL(link.href);
                 }}
                 </script>
                 '''
    return javascript


def get_html_for_histogram_javascript(histogram_json: str,
                                      histogram_width: int,
                                      bar_label_threshold: int,
                                      plot_name: str) -> str:
    """JavaScript for creating a histogram using the
    Observable D3 and Observable Plot framework
    for data visualization. See https://d3js.org and https://observablehq.com/plot.

    :param histogram_json: The histogram data.
    :param histogram_width: The width of the histogram, in pixels.
    :param bar_label_threshold: The largest value in the histogram. This
      value is used to compute whether a histogram label should be shown
      in the histogram bar or next to it.
    :param plot_name: The name of the plot.
    :return: html to be rendered.
    """

    javascript = f'''
                 <script type="module">
                 const brands = {histogram_json};
                 const plot = Plot.plot({{
                   width: {histogram_width},
                   axis: null,
                   // Make height dependent on the number of items in brands.
                   // The "+ 40" is for the horizontal scale.
                   height: brands.length * 20 + 40,
                   x: {{ insetRight: 10 }},
                   marks: [
                     Plot.axisX({{ anchor: "bottom" }}),
                     Plot.barX(brands, {{
                       x: "value",
                       y: "name",
                       fill: "#ffcd00",                 // uu-yellow.
                       sort: {{ y: "x", order: null }}  // no ordering.
                     }}),
                     // labels for larger bars.
                     Plot.text(brands, {{
                       text: (d) => `${{d.name}} (${{d.value}})`,
                       y: "name",
                       frameAnchor: "left",
                       dx: 3,
                       filter: (d) => d.value >= {bar_label_threshold / 2},
                     }}),
                     // labels for smaller bars.
                     Plot.text(brands, {{
                       text: (d) => `${{d.name}} (${{d.value}})`,
                       y: "name",
                       x: "value",
                       textAnchor: "start",
                       dx: 3,
                       filter: (d) => d.value < {bar_label_threshold / 2},
                     }})
                   ]           // End of marks.
                 }});         // End of Plot.plot().
                 const div = document.querySelector("#{plot_name}");
                 div.append(plot);
                 </script>
                 '''
    return javascript

