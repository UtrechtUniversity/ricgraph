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
# Extended Rik D.T. Janssen, July, November 2025.
#
# ########################################################################


from urllib.parse import urlencode
from flask import url_for
from ricgraph_explorer_constants import (font_family,
                                         chord_fontsize, chord_space_for_labels,
                                         chord_label_linespacing,
                                         sankey_margin)


def get_spinner_javascript() -> str:
    """JavaScript to create a spinner.

    :return: html to be rendered.
    """
    javascript = f'''
                 <script>
                 // Hide the spinner on load, including when navigating back.
                 window.addEventListener("pageshow", function(){{
                   document.getElementById("ricgraph_spinner").style.display="none";}});
                 document.querySelector("form").addEventListener("submit", function(){{
                   document.getElementById("ricgraph_spinner").style.display="block";}});
                 </script>
                 '''
    return javascript


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


# The following code was inspired heavily by perplexity.ai.
def create_chord_diagram_javascript(matrix_json: str,
                                    labels_json: str,
                                    width: int,
                                    height: int,
                                    svg_id: str,
                                    figure_filename: str) -> str:
    """The JavaScript code to create a D3 chord diagram from a DataFrame.
    Chord diagram: https://d3-graph-gallery.com/chord.html.

    :param matrix_json: json with matrix.
    :param labels_json: json with labels.
    :param width: the width of the resulting svg image.
    :param height: the height of the resulting svg image.
    :param svg_id: svg id to be used.
    :param figure_filename: the filename of the resulting svg image,
        in case you choose to use the 'Download this image' button.
    :return: html to be rendered, or empty ''.
    """
    javascript = f'''
                 <script>
                 // Function drawChord() allows to change the width of the labels.
                 function drawChord(newLabelWidth) {{
                   const matrix = {matrix_json};
                   const names = {labels_json};
                   const width = {width}, height = {height};
                   // For centering the drawing area.
                   const svg = d3.select("#{svg_id}")
                         .attr("viewBox", [-width / 2, -height / 2, width, height]);
                   svg.selectAll("*").remove();
                   const outerRadius = Math.min(width, height) * 0.5 - newLabelWidth;
                   const innerRadius = outerRadius - 20;
                   const color = d3.scaleOrdinal(d3.schemeCategory10);
                   const chord = d3.chord().padAngle(0.05).sortSubgroups(d3.descending);
                   const arc = d3.arc().innerRadius(innerRadius).outerRadius(outerRadius);
                   const ribbon = d3.ribbon().radius(innerRadius);
                   const chords = chord(matrix);

                   // Draw groups (arcs).
                   const group = svg.append("g")
                     .selectAll("g")
                     .data(chords.groups)
                     .join("g");

                   group.append("path")
                     .attr("fill", d => color(d.index))
                     .attr("stroke", d => color(d.index))
                     .attr("d", arc);

                   // Sum all connections ending at this endpoint (column d.index).
                   // d.index is the endpoint's index.
                   group.on("mouseover", function(event, d) {{
                     let total = 0;
                     for (let i = 0; i < matrix.length; i++) {{
                       total += matrix[i][d.index];
                     }}
                     const tooltip = d3.select("#{svg_id}_tooltip");
                     tooltip
                       .style("display", "block")
                       .html(`<strong>Organization:</strong> ${{names[d.index]}}<br/>
                              <strong>Collaborations:</strong> ${{total}}`);
                   }})
                   .on("mousemove", function(event) {{
                     d3.select("#{svg_id}_tooltip")
                       .style("left", (event.pageX + 10) + "px")
                       .style("top", (event.pageY + 10) + "px");
                   }})
                   .on("mouseout", function(event, d) {{
                     d3.select("#{svg_id}_tooltip").style("display", "none");
                   }});
                   // End draw groups (arcs).

                   // Draw ribbons (connections).
                   svg.append("g")
                     .attr("fill-opacity", 0.7)
                     .selectAll("path")
                     .data(chords)
                     .join("path")
                       .attr("d", ribbon)
                       .attr("fill", d => color(d.target.index))
                       .attr("stroke", d => color(d.target.index))
                       .on("mouseover", function(event, d) {{
                         const value = matrix[d.source.index][d.target.index];
                         const tooltip = d3.select("#{svg_id}_tooltip");
                         tooltip
                           .style("display", "block")
                           .html(`<strong>Between:</strong> ${{names[d.source.index]}}<br/>
                                  <strong>and:</strong> ${{names[d.target.index]}}<br/>
                                  <strong>Collaborations:</strong> ${{value}}`);
                         d3.select(this).attr("fill-opacity", 1.0);
                       }})
                       .on("mousemove", function(event) {{
                         d3.select("#{svg_id}_tooltip")
                           .style("left", (event.pageX + 10) + "px")
                           .style("top", (event.pageY + 10) + "px");
                       }})
                       .on("mouseout", function(event, d) {{
                         d3.select("#{svg_id}_tooltip").style("display", "none");
                         d3.select(this).attr("fill-opacity", 0.7);
                       }});
                   // End draw ribbons (connections).


                   // Function to wrap text of the labels to 'maxWidth'.
                   function wrapText(text, maxWidth, fontSize, fontFamily) {{
                     // Find or create a hidden SVG for measurement. Note, we do only measure here.
                     let measureSVG = document.getElementById('measureSVG');
                     if (!measureSVG) {{
                       measureSVG = document.createElementNS("http://www.w3.org/2000/svg", "svg");
                       measureSVG.setAttribute("id", "measureSVG");
                       measureSVG.setAttribute("style", "position:absolute; left:-9999px; top:-9999px; visibility:hidden");
                       document.body.appendChild(measureSVG);
                     }}
                     const testElem = document.createElementNS("http://www.w3.org/2000/svg", "text");
                     testElem.setAttribute("font-size", fontSize + "px");
                     testElem.setAttribute("font-family", fontFamily);
                     measureSVG.appendChild(testElem);
                     const words = text.split(/\\s+/);
                     const lines = [];
                     let line = [];
                     let testLine = '';
                     for (let word of words) {{
                       testLine = line.concat(word).join(' ');
                       testElem.textContent = testLine;
                       if (testElem.getComputedTextLength() > maxWidth && line.length > 0) {{
                         lines.push(line.join(' '));
                         line = [word];
                       }} else {{
                         line.push(word);
                       }}
                     }}
                     lines.push(line.join(' '));
                     measureSVG.removeChild(testElem);
                     return lines;
                   }}
                   // End of function to wrap text of the labels to 'maxWidth'.

                   // Draw labels.
                   svg.append("g")
                     .selectAll("text")
                     .data(chords.groups)
                     .join("text")
                       .attr("dy", ".35em")
                       .attr("transform", d => {{
                         const angle = (d.startAngle + d.endAngle) / 2;
                         const rotate = angle * 180 / Math.PI - 90;
                         const translate = outerRadius + 40; // Make space for organization arc.
                         return `rotate(${{rotate}}) translate(${{translate}})${{angle > Math.PI ? " rotate(180)" : ""}}`;
                       }})
                       .attr("text-anchor", d => ((d.startAngle + d.endAngle) / 2 > Math.PI) ? "end" : "start")
                       .attr("font-family", "{font_family}")
                       .attr("font-size", "{chord_fontsize}px")
                       // Instead of just displaying the label text, wrap it.
                       .each(function(d) {{
                         const label = names[d.index];
                         // The '40' is the same value als in 'const translate'.
                         const lines = wrapText(label, newLabelWidth - 40, "{chord_fontsize}", "{font_family}");
                         d3.select(this)
                           .selectAll("tspan")
                           .data(lines)
                           .join("tspan")
                             .attr("x", 0)
                             .attr("dy", (line, i) => i === 0 ? "0" : "{chord_label_linespacing}")
                             .text(line => line);
                       // End of instead of just displaying the label text, wrap it.
                       }});
                   // End draw labels.

                   // Draw organization arcs for groups with same first three letters (may be a space).
                   // 1. Group label indices by their first three letters.
                   const prefixGroups = {{}};
                   names.forEach((name, idx) => {{
                     const prefix = name.slice(0, 3);
                     if (!prefixGroups[prefix]) prefixGroups[prefix] = [];
                     prefixGroups[prefix].push(idx);
                   }});
                   // 2. For each group, draw an outer arc if more than one org shares the prefix.
                   Object.entries(prefixGroups).forEach(([prefix, indices], groupIdx) => {{
                     // Find angular range for this group.
                     const startAngle = chords.groups[Math.min(...indices)].startAngle;
                     const endAngle = chords.groups[Math.max(...indices)].endAngle;

                     // Outer arc generator.
                     const groupArc = d3.arc()
                       .innerRadius(outerRadius + 15)
                       .outerRadius(outerRadius + 30)
                       .startAngle(startAngle)
                       .endAngle(endAngle);

                     const fillColor = d3.schemeCategory10[groupIdx % 10];
                     svg.append("path")
                       .attr("id", "outerArcPath-" + groupIdx)
                       .attr("d", groupArc())
                       .attr("fill", fillColor)
                       .attr("fill-opacity", 0.25)   // semi-transparent fill.

                       .on("mouseover", function(event) {{
                         // Sum all incoming connections for all endpoints in this group.
                         let total = 0;
                         indices.forEach(idx => {{
                           for (let i = 0; i < matrix.length; i++) {{
                             total += matrix[i][idx];
                           }}
                         }});
                         const tooltip = d3.select("#{svg_id}_tooltip");
                         tooltip
                           .style("display", "block")
                           .html(`<strong>Group:</strong> ${{prefix}}<br/>
                                  <strong>Collaborations:</strong> ${{total}}`);
                       }})
                       .on("mousemove", function(event) {{
                         d3.select("#{svg_id}_tooltip")
                           .style("left", (event.pageX + 10) + "px")
                           .style("top", (event.pageY + 10) + "px");
                       }})
                       .on("mouseout", function(event) {{
                         d3.select("#{svg_id}_tooltip").style("display", "none");
                       }});

                     // Label the group at the midpoint.
                     if (indices.length <= 2) return; // But no label with <= 2 collabs.
                     const midAngle = (startAngle + endAngle) / 2;
                     const labelRadius = outerRadius + 25; // Place in the middle of the arc band.
                     svg.append("text")
                       .attr("x", Math.cos(midAngle - Math.PI/2) * labelRadius)
                       .attr("y", Math.sin(midAngle - Math.PI/2) * labelRadius)
                       .attr("text-anchor", "middle")
                       .attr("alignment-baseline", "middle")
                       .attr("fill", fillColor)
                       .attr("font-family", "{font_family}")
                       .attr("font-size", "{chord_fontsize}px")
                       .text(prefix);
                   }}); 
                   // End draw organization arcs for groups.
                 }} 
                 // End of function drawChord(). 

                 // Listen for changes in the input box. This changes the width of the labels of the diagram.
                 document.getElementById("{svg_id}_labelwidth_input").addEventListener("change", function() {{
                   const newLabelWidth = +this.value;
                   drawChord(newLabelWidth);
                 }})
                 // End listen for changes in the input box.

                 // Initial render of this diagram.
                 drawChord({chord_space_for_labels});

                 // Download SVG functionality.
                 document.getElementById("{svg_id}_download_btn").onclick = function() {{
                   var svg = document.getElementById("{svg_id}");
                   var serializer = new XMLSerializer();
                   var source = serializer.serializeToString(svg);
                   if(!source.match(/^<svg[^>]+xmlns="http\\:\\/\\/www\\.w3\\.org\\/2000\\/svg"/)){{
                     source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
                   }}
                   if(!source.match(/^<svg[^>]+"http\\:\\/\\/www\\.w3\\.org\\/1999\\/xlink"/)){{
                     source = source.replace(/^<svg/, '<svg xmlns:xlink="http://www.w3.org/1999/xlink"');
                   }}
                   source = '<?xml version="1.0" standalone="no"?>\\r\\n' + source;
                   var url = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(source);
                   var downloadLink = document.createElement("a");
                   downloadLink.href = url;
                   downloadLink.download = "{figure_filename}";
                   document.body.appendChild(downloadLink);
                   downloadLink.click();
                   document.body.removeChild(downloadLink);
                 }};
                 // End download SVG functionality.
                 </script>
                 '''
    return javascript


# The following code was inspired heavily by perplexity.ai.
def create_sankey_diagram_javascript(nodes_json: str,
                                     links_json: str,
                                     research_result_category: list,
                                     tooltip_show_links: bool,
                                     width: int,
                                     height: int,
                                     svg_id: str,
                                     figure_filename: str) -> str:
    """The JavaScript code to create a D3 Sankey diagram from a DataFrame.
    Sankey diagram: https://d3-graph-gallery.com/sankey.html.

    :param nodes_json: json with nodes.
    :param links_json: json with links.
    :param research_result_category: if specified, only return collaborations
      for this research result category. If not, return all collaborations,
      regardless of the research result category.
      The value can be both a string containing one category, or
      a list of categories.
    :param tooltip_show_links: whether to show the 'drill down links' in
      the tooltip or not.
    :param width: the width of the resulting svg image.
    :param height: the height of the resulting svg image.
    :param svg_id: svg id to be used.
    :param figure_filename: the filename of the resulting svg image,
        in case you choose to use the 'Download this image' button.
    :return: html to be rendered, or empty ''.
    """

    # Note about the absence of an outline around lines in a Sankey diagram.
    # There is a difference between D3 Chord diagrams and D3 Sankey diagrams,
    # in that it is easy to have a small outline around a Chord line, but
    # you cannot do so (easily) for a Sankey line.
    # Chord diagrams in D3 use the d3.ribbon generator, which creates
    # closed SVG paths. These paths are like filled shapes, not just lines.
    # Because the path is closed, you can use both fill and stroke:
    # 'fill' colors the inside of the ribbon, and
    # 'stroke' draws a border (outline) around the entire ribbon shape.
    #
    # This doesn't work for D3 Sankey links.
    # Sankey diagrams in D3 use d3.sankeyLinkHorizontal, which generates
    # open SVG paths. These are not closed shapes, but "fat lines"
    # (open paths with a width). SVG's stroke property draws the line itself,
    # but you can't add a second "stroke" behind it (so no border for strokes).
    # If you set both 'fill' and 'stroke', only the stroke is visible,
    # because the path is not a closed area, so that will not work.
    #
    # An alternative would be to use gradient lines, but since we often have
    # many small lines, this wouldn't make much of a difference.
    if len(research_result_category) == 0:
        print('create_sankey_diagram_javascript(): Error: Research result category is empty. Exiting...')
        return ''
    if tooltip_show_links:
        base_url = url_for(endpoint='collabsresultpage.collabsresultpage') + '?'
        base_url += urlencode(query={'category_list': research_result_category}, doseq=True)
        url_style = 'style="display:inline-block; background:buttonface; width:14em; '
        url_style += 'border:1px solid buttonborder; border-radius:4px; text-decoration:none; '
        url_style += 'margin:0.2em 0em; text-align:center;"'
    else:
        base_url = ''
        url_style = ''

    javascript = f'''
                 <script>
                 let pathHovered = false;
                 let tooltipHovered = false;
                 let tooltipPinned = false;
                 const tooltip = d3.select("#{svg_id}_tooltip");
                 const tooltip_show_links = {str(tooltip_show_links).lower()};
                 
                 tooltip
                   .on("mouseenter", function() {{
                     tooltipHovered = true;
                     tooltip.style("display", "block");
                   }})
                   .on("mouseleave", function() {{
                     tooltipHovered = false;
                     if (!pathHovered && !tooltipPinned)
                       tooltip.style("display", "none");
                   }});
               
                 // Create a tooltip at a certain position (left, top) that has 
                 // clickable elements in it. For this to work, it must be pinnable.
                 // This allows to 'drill down' on the collaborations.
                 function updateTooltip(event, d, left, top) {{
                   let popup = `<strong>From:</strong> ${{d.source.name}}<br/>`
                   
                   popup += `<strong>To:</strong> ${{d.target.name}}<br/>`
                   popup += `<strong>Collaborations:</strong> ${{d.value}}<br/>`
                   if (tooltip_show_links) {{
                     const orgs_url = "{base_url}" +
                                      "&start_orgs=" + encodeURIComponent(d.source.name) +
                                      "&collab_orgs=" + encodeURIComponent(d.target.name);
                     const startorg_persons_url = `${{orgs_url}}&collab_mode=return_startorg_persons`;
                     const research_results_url = `${{orgs_url}}&collab_mode=return_research_results`;
                     const collaborg_persons_url = `${{orgs_url}}&collab_mode=return_collaborg_persons`;
                     
                     popup += `<a href="${{startorg_persons_url}}"  {url_style} `
                     popup += `  target="_blank">persons from <em>start organizations</em></a> `
                     popup += `<a href="${{research_results_url}}" {url_style} `
                     popup += `  target="_blank">research results</a> `
                     popup += `<a href="${{collaborg_persons_url}}" {url_style} `
                     popup += `  target="_blank">persons from <em>collaborating organizations</em></a> `
                     popup += `<br/>Note that finding these collaborations may take (very) long.<br/> `
                   }};
                   popup += `<button id="close_tooltip">close</button>`
                   
                   tooltip
                     .style("display", "block")
                     .style("left", left + "px")
                     .style("top", top + "px")
                     .html(popup);
                   d3.select("#{svg_id}_tooltip #close_tooltip").on("click", function() {{
                     tooltipPinned = false;
                     tooltip.style("display", "none");
                   }});
                 }}
                 // End create a tooltip.
                
                 // Get the position of the tooltip.
                 function getTooltipPosition(event, svg_id, tooltip_id) {{
                   const svgWidth = d3.select("#{svg_id}").node().getBoundingClientRect().width;
                   const mouseX = event.clientX - d3.select("#{svg_id}").node().getBoundingClientRect().left;
                   const isLeftHalf = mouseX < svgWidth / 2;
                   const offsetX = isLeftHalf ? 10 : -10 - d3.select("#{svg_id}_tooltip").node().offsetWidth;
                   const left = event.pageX + offsetX;
                   const top = event.pageY + 10;
                   return {{ left, top }};
                 }}
                 // End get the position of the tooltip.

                 // Function drawSankey() allows to change the height of the diagram.
                 function drawSankey(newHeight) {{
                   const graph = {{ nodes: {nodes_json}, links: {links_json} }};
                   const totalLinks = graph.links.length;
                   const width = {width}, height = {height};
                   const color = d3.scaleOrdinal(d3.schemeCategory10);
                   const svg = d3.select("#{svg_id}")

                   svg.selectAll("*").remove();
                   svg.attr("height", newHeight);

                   const sankey = d3.sankey()
                     .nodeWidth(20)           // Width of a bar in pixels.
                     .nodePadding(10)         // Vertical space between bars in pixels.
                     .extent([[{sankey_margin}, {sankey_margin}], [width - {sankey_margin}, newHeight - {sankey_margin}]])
                     .nodeId(d => d.id)
                     .nodeAlign(d => d.side === "from" ? 0 : 1)
                     .nodeSort(null)
                     .linkSort((a, b) => d3.descending(a.value, b.value));
                   const {{nodes, links}} = sankey(graph);

                   // Assign color to nodes.
                   nodes.forEach((d, i) => d.color = color(d.name));
                   
                   // Draw links (lines) -- set all color/opacity as attributes.
                   svg.append("g")
                     .selectAll("path")
                     .data(links)
                     .join("path")
                       .attr("class", "link")
                       .attr("d", d3.sankeyLinkHorizontal())
                       .attr("stroke-width", d => Math.max(1, d.width))
                       .attr("stroke", d => nodes.find(n => n.id === d.source.id).color)
                       .attr("fill", "none")
                       .attr("stroke-opacity", 0.25)
                       .on("mouseover", function(event, d) {{
                          pathHovered = true;               // Set hover state.
                          if (!tooltipPinned) {{            // Don't update if pinned.
                            d3.select(this).classed("highlighted", true).attr("stroke-opacity", 0.8);
                            const pos = getTooltipPosition(event, "{{svg_id}}", "{{svg_id}}_tooltip");
                            updateTooltip(event, d, pos.left, pos.top);
                          }}
                       }})
                       .on("mousemove", function(event, d) {{
                         if (!tooltipPinned) {{    
                           // Determine if node is on left or right.
                           const svgWidth = d3.select("#{svg_id}").node().getBoundingClientRect().width;
                           // We use the mouse's position relative to the SVG.
                           const mouseX = event.clientX - d3.select("#{svg_id}")
                             .node().getBoundingClientRect().left;
                           const isLeftHalf = mouseX < svgWidth / 2;
                           const offsetX = isLeftHalf ? 10 : -10 - d3.select("#{svg_id}_tooltip")
                             .node().offsetWidth;
                           d3.select("#{svg_id}_tooltip")
                             .style("left", (event.pageX + offsetX) + "px")
                             .style("top", (event.pageY + 10) + "px");
                         }}
                       }})
                       .on("click", function(event, d) {{
                         tooltipPinned = true;              // Stick tooltip on click.
                         const pos = getTooltipPosition(event, "{{svg_id}}", "{{svg_id}}_tooltip");
                         updateTooltip(event, d, pos.left, pos.top);
                       }})
                       .on("mouseout", function(event, d) {{
                          pathHovered = false;              // Remove hover state.
                          d3.select(this).classed("highlighted", false)
                            .attr("stroke-opacity", 0.25);
                       }});
                   // End draw links (lines).

                   // Draw nodes (bars) -- set fill and fill-opacity as attributes.
                   svg.append("g")
                     .attr("class", "node")
                     .selectAll("rect")
                     .data(nodes)
                     .join("rect")
                       .attr("x", d => d.x0)
                       .attr("y", d => d.y0)
                       .attr("height", d => d.y1 - d.y0)
                       .attr("width", d => d.x1 - d.x0)
                       .attr("fill", d => d.color)
                       .attr("fill-opacity", 0.7)
                       .on("mouseover", function(event, d) {{
                         // Show tooltip for node
                         d3.select("#{svg_id}_tooltip")
                           .style("display", "block")
                           .html(`<strong>Organization:</strong> ${{d.name}}<br/>
                                  <strong>Total connections:</strong> ${{d.value}}`);
                       }})
                       .on("mousemove", function(event, d) {{
                         // Determine if node is on left or right.
                         const svgWidth = d3.select("#{svg_id}").node().getBoundingClientRect().width;
                         const isLeft = d.x0 < svgWidth / 2;
                         // Offset: right for left bars, left for right bars
                         const offsetX = isLeft ? 10 : -10 - d3.select("#{svg_id}_tooltip").node().offsetWidth;
                         d3.select("#{svg_id}_tooltip")
                           .style("left", (event.pageX + offsetX) + "px")
                           .style("top", (event.pageY + 10) + "px");
                       }})
                       .on("mouseout", function(event, d) {{
                         d3.select("#{svg_id}_tooltip").style("display", "none");
                       }});
                   // End draw nodes (bars).

                   // Draw labels.
                   svg.append("g")
                     .selectAll("text")
                     .data(nodes)
                     .join("text")
                       .attr("x", d => d.x0 < width / 2 ? d.x1 + 25 : d.x0 - 25)
                       .attr("y", d => (d.y1 + d.y0) / 2)
                       .attr("dy", "0.35em")
                       .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
                       .text(d => d.name);
                   // End draw labels.
                 }} 
                 // End of function drawSankey(). 

                 // Listen for changes in the input box. This changes the height of the diagram.
                 document.getElementById("{svg_id}_height_input").addEventListener("change", function() {{
                   const newHeight = +this.value;
                   drawSankey(newHeight);
                 }})
                 // End listen for changes in the input box.

                 // Initial render of this diagram.
                 drawSankey({height});

                 // Download SVG functionality.
                 document.getElementById("{svg_id}_download_btn").onclick = function() {{
                   var svg = document.getElementById("{svg_id}");
                   var serializer = new XMLSerializer();
                   var source = serializer.serializeToString(svg);
                   if(!source.match(/^<svg[^>]+xmlns="http\\:\\/\\/www\\.w3\\.org\\/2000\\/svg"/)){{
                     source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
                   }}
                   if(!source.match(/^<svg[^>]+"http\\:\\/\\/www\\.w3\\.org\\/1999\\/xlink"/)){{
                     source = source.replace(/^<svg/, '<svg xmlns:xlink="http://www.w3.org/1999/xlink"');
                   }}
                   source = '<?xml version="1.0" standalone="no"?>\\r\\n' + source;
                   var url = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(source);
                   var downloadLink = document.createElement("a");
                   downloadLink.href = url;
                   downloadLink.download = "{figure_filename}";
                   document.body.appendChild(downloadLink);
                   downloadLink.click();
                   document.body.removeChild(downloadLink);
                 }};
                 // End download SVG functionality.
                 </script>
                 '''
    return javascript


