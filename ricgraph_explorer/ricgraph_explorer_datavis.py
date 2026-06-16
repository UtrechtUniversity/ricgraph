# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
#
# Copyright (c) 2023 - 2026 Rik D.T. Janssen
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
# Extended Rik D.T. Janssen, October, November 2025, March 2026.
#
# ########################################################################

from json import dumps
from pandas import DataFrame
from functools import wraps
from inspect import signature
from ricgraph import (datetimestamp,
                      combine_dataframes, make_dataframe_square_symmetric,
                      convert_nodeslist_to_dataframe,
                      create_empty_page_params, create_empty_query_params,
                      write_text_to_file, write_dataframe_to_csv,
                      PageParams, QueryParams,
                      datestamp)
from ricgraph_explorer_constants import (RICGRAPH_SYSTEMINFO,
                                         ricgraph_reference, diagram_tooltip_style,
                                         observable_d3,
                                         chord_space_for_labels,
                                         sankey_pixels_per_link,
                                         sankey_min_height, sankey_max_height)
from ricgraph_explorer_utils import (remove_hierarchical_orgs,
                                     get_global_dataframe)
from ricgraph_explorer_html import create_full_htmlpage
from ricgraph_explorer_cypher import (find_collab_orgs_matrix,
                                      find_collab_orgs_persons_results)
from ricgraph_explorer_javascript import (create_chord_diagram_javascript,
                                          create_sankey_diagram_javascript)


# ########################################################################
# D3 functions, for Chord Diagram and Sankey Diagram.
# ########################################################################
def create_chord_diagram(df: DataFrame,
                         width: int = 1200,
                         figure_caption: str = '',
                         figure_filename: str = '') -> str:
    """Create a D3 chord diagram from a DataFrame.
    Chord diagram: https://d3-graph-gallery.com/chord.html.
    The DataFrame needs to be square and symmetric. It is best to sort it.

    :param df: the DataFrame (must be square, orgs as index/columns).
    :param width: the width of the resulting svg image.
    :param figure_caption: the caption of the resulting svg image, may be empty.
    :param figure_filename: the filename of the resulting svg image,
      in case you choose to use the 'Download this image' button.
    :return: HTML to be rendered, or empty ''.
    """
    if df is None or df.empty:
        print('create_chord_diagram(): Error, DataFrame is empty.')
        return ''

    if len(df.columns) != len(df.index):
        print('create_chord_diagram(): Error, the DataFrame needs to be square and symmetric.')
        return ''

    if figure_filename == '':
        figure_filename = datestamp() + '-ricgraph-chord-diagram.svg'

    matrix = df.values.tolist()
    labels = df.index.tolist()
    matrix_json = dumps(matrix)
    labels_json = dumps(labels)
    svg_id = 'chord'
    height = width          # After all, a chord diagram is a circle.
    timestamp = datetimestamp()
    stats = 'This diagram was created on ' + timestamp + '.'

    intro_html = f'''
                 <div id="{svg_id}_diagram">
                 {ricgraph_reference}
                 <!-- This Chord diagram was created on {timestamp}. -->
                 <figure style="margin:0px;">
                 '''
    if figure_caption == '':
        intro_html += f'<figcaption>{stats}</figcaption>'
    else:
        intro_html += f'<figcaption>{figure_caption}<br/>{stats}</figcaption>'
    intro_html += f'''
                  <div><br/>
                  <label for="{svg_id}_labelwidth_input">
                     Enter a value for the width of the labels (in pixels): </label>
                  <input id="{svg_id}_labelwidth_input" type="number" min="100" step="20"
                      value="{chord_space_for_labels}" style="width:50px;">.
                 <br/>
                 <button id="{svg_id}_download_btn" style="margin-top:10px;">
                   Download this image</button>
                 </div>
                 <svg id="{svg_id}" width="{width}" height="{height}"></svg>
                 <div id="{svg_id}_tooltip" {diagram_tooltip_style}></div>
                 </figure>
                 '''
    outro_html = '</div>'

    javascript = create_chord_diagram_javascript(matrix_json=matrix_json,
                                                 labels_json=labels_json,
                                                 width=width,
                                                 height=height,
                                                 svg_id=svg_id,
                                                 figure_filename=figure_filename)

    return observable_d3 + intro_html + javascript + outro_html


def create_sankey_diagram(page_params: PageParams,
                          query_params: QueryParams,
                          df: DataFrame,
                          tooltip_show_links: bool = False,
                          width: int = 1200,
                          height: int = 0,
                          figure_caption: str = '',
                          figure_filename: str = '') -> str:
    """Create a D3 Sankey diagram from a DataFrame.
    Sankey diagram: https://d3-graph-gallery.com/sankey.html.

    :param page_params: parameters related to the page passed in the URL.
    :param query_params: parameters related to the query passed in the URL.
    :param df: the DataFrame (orgs as index/columns).
    :param tooltip_show_links: whether to show the 'drill down links' in
      the tooltip or not.
    :param width: the width of the resulting svg image.
    :param height: the height of the resulting svg image.
      If you specify 0, the height will be computed automatically,
      which usually gives a nice result, but sometimes does not.
    :param figure_caption: the caption of the resulting svg image, may be empty.
    :param figure_filename: the filename of the resulting svg image,
      in case you choose to use the 'Download this image' button.
    :return: HTML to be rendered, or empty ''.
    """
    if df is None or df.empty:
        print('create_sankey_diagram(): Error, DataFrame is empty.')
        return ''

    if figure_filename == '':
        figure_filename = datestamp() + '-ricgraph-sankey-diagram.svg'

    nodes = []
    node_map = {}
    links = []
    sources = sorted(df.index.tolist())
    targets = sorted(df.columns.tolist())

    for org in sources:
        node_id = f"{org}_from"
        node_map[node_id] = len(nodes)
        nodes.append({"name": org, "id": node_id, "side": "from"})

    for org in targets:
        node_id = f"{org}_to"
        node_map[node_id] = len(nodes)
        nodes.append({"name": org, "id": node_id, "side": "to"})

    total_connections = 0
    for src in sources:
        for tgt in targets:
            # PyCharm warns for an "Expected type".
            # Note: the df.at returns an int64 instead of int.
            value = int(df.at[src, tgt])
            if value > 0 and src != tgt:
                links.append({
                    "source": f"{src}_from",
                    "target": f"{tgt}_to",
                    "value": value
                })
                total_connections += int(value)

    nodes_json = dumps(nodes)
    links_json = dumps(links)
    svg_id = 'sankey'
    timestamp = datetimestamp()

    stats = 'This diagram contains ' + str(len(sources)) + ' '
    stats += 'organization ' if len(sources) == 1 else 'organizations '
    stats += 'on the left side, and ' + str(len(targets)) + ' on the right. '
    stats += 'It has ' + str(len(links)) + ' '
    stats += 'line ' if len(links) == 1 else 'lines '
    stats += 'between left and right organizations, and a total of '
    stats += str(total_connections) + ' collaborations. '
    stats += 'It was created on ' + timestamp + '.'

    if height == 0:
        # Determine the height of the svg dynamically, it can be made dependable
        # on many things, we choose on the number of connections.
        # Example situations that are really different:
        # - few bars, many links per bar.
        # - many bars, few links per bar.
        while (height := max(sankey_min_height, total_connections * sankey_pixels_per_link)) > sankey_max_height:
            # Try to reduce the height carefully.
            total_connections = int(total_connections / 2)

    intro_html = f'''
                 <div id="{svg_id}_diagram">
                 {ricgraph_reference}
                 <figure style="margin:0px;">
                 '''
    if figure_caption == '':
        intro_html += f'<figcaption>{stats}</figcaption>'
    else:
        intro_html += f'<figcaption>{figure_caption}<br/>{stats}</figcaption>'
    intro_html += f'''
                  <div><br/>
                  <label for="{svg_id}_height_input">
                      Enter a value for a new diagram height (in pixels): </label>
                  <input id="{svg_id}_height_input" type="number" min="{sankey_min_height}" step="200"
                      value="{height}" style="width:60px;">.
                  If you choose a height that is too small for the diagram, 
                  the colored bars left and right will disappear.
                  <br/>
                  <button id="{svg_id}_download_btn" style="margin-top:10px;">
                      Download this image</button>
                  </div>
                  <svg id="{svg_id}" width="{width}" height="{height}"></svg>
                  <div id="{svg_id}_tooltip" {diagram_tooltip_style}></div>
                  </figure>
                  '''
    outro_html = '</div>'

    javascript = create_sankey_diagram_javascript(page_params=page_params,
                                                  query_params=query_params,
                                                  nodes_json=nodes_json,
                                                  links_json=links_json,
                                                  tooltip_show_links=tooltip_show_links,
                                                  width=width,
                                                  height=height,
                                                  svg_id=svg_id,
                                                  figure_filename=figure_filename)

    return observable_d3 + intro_html + javascript + outro_html


# ########################################################################
# Functions related to collaborations
# ########################################################################
def error_check(func):
    """This is a decorator function for other functions.
    It checks if the function called returns an empty string ('') or not,
    and if that function returns '' it prints an error message.

    :param func: the function that this function is a decorator of.
    :return: '' or the return value of the function called.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the function's signature, bind the passed arguments
        # to the signature, and include default values if not provided.
        sig = signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        # Call the function.
        result = func(*args, **kwargs)
        if result == '':
            print('--> Function ' + str(func.__name__) + '() gave no results.')
            print('    These were the parameters passed:')
            for name, value in bound.arguments.items():
                print('    ' + str(name) + ' = ' + str(value))
            print('\n')

        return result
    return wrapper


@error_check
def org_collaborations_persons_results(query_params: QueryParams,
                                       mode: str = 'return_researchresults') -> list:
    """Find all collaborations of an organizations starting with a string,
    with other organizations with the same starting string
    (e.g. UU Faculty and UU Faculty).
    Return the result of 'mode' in a list.
    Note the similarity with org_collaborations_persons_results_df(),
    that does the same but returns a DataFrame.

    Please read the design decision at org_collaborations_diagram().

    :param query_params: Parameters related to the query passed in the URL.
    :param mode: one of the following:
      - mode = 'return_researchresults': return the research results.
      - mode = 'return_startorg_persons': return the person-roots from start_orgs.
      - mode = 'return_collaborg_persons': return the person-roots from collab_orgs.
    :return: a list of nodes, or [] if nothing found.
    """
    print('-- org_collaborations_start_org_persons(): start at ' + datetimestamp() + '.')
    nodes_list = find_collab_orgs_persons_results(query_params=query_params,
                                                  mode=mode)
    # No need to check for nothing found, if so, nodes_list will be [].
    print('-- org_collaborations_start_org_persons(): finished at ' + datetimestamp() + '.\n')
    return nodes_list


def org_collaborations_persons_results_df(query_params: QueryParams,
                                          mode: str = 'return_researchresults',
                                          filename: str = '') -> DataFrame | None:
    """Find all collaborations of an organizations starting with a string,
    with other organizations with the same starting string
    (e.g. UU Faculty and UU Faculty).
    Return the result of 'mode' in a DataFrame.
    Note the similarity with org_collaborations_persons_results(),
    that does the same but returns a list of nodes.

    Please read the design decision at org_collaborations_diagram().

    :param query_params: Parameters related to the query passed in the URL.
    :param mode: one of the following:
      - mode = 'return_researchresults': return the research results.
      - mode = 'return_startorg_persons': return the person-roots from start_orgs.
      - mode = 'return_collaborg_persons': return the person-roots from collab_orgs.
    :param filename: this will the base of the filename, you can use it
      to reflect the type of query.
      It will also work if you specify a directory and filename.
      If you specify '', no files will be produced.
    :return: the DataFrame with the result, or None if nothing found.
    """
    nodes_list = org_collaborations_persons_results(query_params=query_params,
                                                    mode=mode)
    if len(nodes_list) == 0:
        return None
    result = convert_nodeslist_to_dataframe(nodes_list=nodes_list,
                                            columns_and_order=['name', 'category', 'value',
                                                               'comment', 'year',
                                                               'url_main', 'url_other', '_source'])
    if filename != '':
        write_dataframe_to_csv(filename=filename + '.csv', df=result, write_index=True)
    return result


@error_check
def org_collaborations_diagram(page_params: PageParams,
                               query_params: QueryParams,
                               diagram_type: str = 'sankey',
                               filename: str = '',
                               caption: str = 'default_caption',
                               generate_full_html: bool = True) -> str:
    """Find all collaborations of an organizations starting with a string,
    with other organizations with the same starting string
    (e.g. UU Faculty and UU Faculty).
    Note the similarity with three_org_collaborations_chord(),
    that does the same but for three organizations in a Chord diagram.

    Design decision.
    If collab_organizations == '', i.e., it is
    'any organization', only top level organizations will be
    counted (and returned). So, if you have organizations
    with sub-organizations, the sub-organizations will not be returned.
    Since a top level organization may have a lot of sub-organizations,
    this may confuse the user (and clutter the diagram).
    To be able to remove these sub-organizations,
    we need a list of organizations that have hierarchies.
    Ultimately, this parameter is set in 'ricgraph.ini', since it
    is dependent on the sources you have harvested.
    Note that this is not necessary for org_collaborations_persons_results()
    and org_collaborations_persons_results_df(), since they return
    unique persons and research results.
    It is also not necessary for three_org_collaborations_chord(),
    function since it find collaborations for three organizations.

    :param page_params: parameters related to the page passed in the URL.
    :param query_params: Parameters related to the query passed in the URL.
    :param diagram_type: the type of diagram to create, 'sankey' or 'chord'.
    :param filename: this will the base of the filename, you can use it
      to reflect the type of query.
      It will also work if you specify a directory and filename.
      If you specify '', no files will be produced.
    :param caption: the caption of the diagram. If it is 'default_caption',
      the default caption will be generated (including statistics).
      If it is '', only statistics will be shown.
    :param generate_full_html: whether to return full HTML for a page, or only body HTML.
    :return: the HTML produced (either full or body, see 'generate_full_html'),
      or '' if no HTML produced.
    """
    orgs_with_hierarchies = get_global_dataframe(ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                 item='orgs_with_hierarchies')
    print('-- org_collaborations_diagram(): start at ' + datetimestamp() + '.')
    if diagram_type != 'sankey' and diagram_type != 'chord':
        print('org_collaborations_diagram(): Error, unknown diagram type "' + diagram_type + '", exiting.')
        exit(1)

    collabs_orgs_raw = find_collab_orgs_matrix(query_params=query_params)
    if collabs_orgs_raw is None:
        return ''

    collabs_orgs = collabs_orgs_raw.copy(deep=True)
    if query_params['collab_orgs'] == '':
        if orgs_with_hierarchies is None or orgs_with_hierarchies.empty:
            print('org_collaborations_diagram(): Error, you should have specified "orgs_with_hierarchies", exiting...')
            exit(1)
        collabs_orgs = remove_hierarchical_orgs(df=collabs_orgs,
                                                orgs_with_hierarchies=orgs_with_hierarchies,
                                                org_to_keep=query_params['start_orgs'])
    if query_params['start_orgs'] == query_params['collab_orgs']:
        collabs_orgs = make_dataframe_square_symmetric(df=collabs_orgs)
    if collabs_orgs is None:
        # To silence a PyCharm warning.
        return ''
    # Sort row index (axis=0) case-insensitively, then sort column index (axis=1) case-insensitively
    collabs_orgs = collabs_orgs.sort_index(axis=0, key=lambda x: x.str.lower()).sort_index(axis=1, key=lambda x: x.str.lower())
    if caption == 'default_caption':
        caption = 'Overview of '
        if filename == '':
            caption += 'collaborations'
        else:
            caption += filename
        caption += ' of a number of years for '
        caption += query_params['start_orgs'] + ' and '
        if query_params['collab_orgs'] == '':
            caption += 'all' + '.'
        else:
            caption += query_params['collab_orgs'] + '.'
    if diagram_type == 'sankey':
        if generate_full_html:
            tooltip_show_links = False
        else:
            tooltip_show_links = True
        body_html = create_sankey_diagram(page_params=page_params,
                                          query_params=query_params,
                                          df=collabs_orgs,
                                          tooltip_show_links=tooltip_show_links,
                                          figure_caption=caption,
                                          figure_filename=filename)
    else:
        body_html = create_chord_diagram(df=collabs_orgs,
                                         figure_caption=caption,
                                         figure_filename=filename)

    if generate_full_html:
        return_html = create_full_htmlpage(body_html=body_html)
    else:
        return_html = body_html
    if filename != '':
        write_dataframe_to_csv(filename=filename + '-raw.csv', df=collabs_orgs_raw, write_index=True)
        write_dataframe_to_csv(filename=filename + '.csv', df=collabs_orgs, write_index=True)
        write_text_to_file(filename=filename + '.html', text=return_html)
    print('-- org_collaborations_diagram(): finished at ' + datetimestamp() + '.\n')
    return return_html


@error_check
def three_org_collaborations_chord(query_params: QueryParams,
                                   first_org: str,
                                   second_org: str,
                                   third_org: str,
                                   filename: str = '',
                                   generate_full_html: bool = True) -> str:
    """Find all collaborations for three (sub-)organizations.
    These may be part of sub-organizations, such as 'UU Faculty'.
    This function will very probably only work (or be useful) if you
    choose (sub-)organizations from the same level.
    Note the similarity with org_collaborations_diagram(),
    that does the same but for two organizations.

    Please read the design decision at org_collaborations_diagram().
    It is not applicable for this function since it find collaborations
    for three organizations.

    :param query_params: Parameters related to the query passed in the URL.
     - category_list: do it for this category,
       either a str or list of categories.
    :param first_org: the first (sub-)organization or substring of it.
    :param second_org: the second (sub-)organization or substring of it.
    :param third_org: the third (sub-)organization or substring of it.
    :param filename: this will the base of the filename, you can use it
      to reflect the type of query.
      It will also work if you specify a directory and filename.
      If you specify '', no files will be produced.
    :param generate_full_html: whether to return full HTML for a page, or only body HTML.
    :return: the HTML produced (either full or body, see 'generate_full_html'),
      or '' if no HTML produced.
    """
    print('-- collabs_three_orgs(): start at ' + datetimestamp() + '.')
    query_params['start_orgs'] = first_org
    query_params['collab_orgs'] = second_org
    collabs_1st_2nd = find_collab_orgs_matrix(query_params=query_params)
    if collabs_1st_2nd is None:
        return ''

    query_params['start_orgs'] = first_org
    query_params['collab_orgs'] = third_org
    collabs_1st_3rd = find_collab_orgs_matrix(query_params=query_params)
    if collabs_1st_3rd is None:
        return ''

    query_params['start_orgs'] = second_org
    query_params['collab_orgs'] = third_org
    collabs_2nd_3rd = find_collab_orgs_matrix(query_params=query_params)
    if collabs_2nd_3rd is None:
        return ''

    # Combine data sets, software and publications.
    combine_df = combine_dataframes(df1=collabs_1st_2nd, df2=collabs_1st_3rd)
    combine_df = combine_dataframes(df1=combine_df, df2=collabs_2nd_3rd)
    combine_df = make_dataframe_square_symmetric(df=combine_df)
    if combine_df is None:
        # To silence a PyCharm warning.
        return ''
    # Sort row index (axis=0) case-insensitively, then sort column index (axis=1) case-insensitively
    combine_df = combine_df.sort_index(axis=0, key=lambda x: x.str.lower()).sort_index(axis=1, key=lambda x: x.str.lower())
    caption = 'Overview of ' + str(query_params['category_list'])
    caption += ' of a number of years for the (sub-)organizations '
    caption += first_org + ', ' + second_org + ', and ' + third_org + '.'
    body_html = create_chord_diagram(df=combine_df,
                                     figure_caption=caption,
                                     figure_filename=filename)
    if generate_full_html:
        return_html = create_full_htmlpage(body_html=body_html)
    else:
        return_html = body_html
    if filename != '':
        write_dataframe_to_csv(filename=filename + '-1st2nd-raw.csv', df=collabs_1st_2nd, write_index=True)
        write_dataframe_to_csv(filename=filename + '-1st3rd-raw.csv', df=collabs_1st_3rd, write_index=True)
        write_dataframe_to_csv(filename=filename + '-2nd3rd-raw.csv', df=collabs_2nd_3rd, write_index=True)
        write_dataframe_to_csv(filename=filename + '-combined.csv', df=combine_df, write_index=True)
        write_text_to_file(filename=filename + '.html', text=return_html)
    print('-- collabs_three_orgs(): finished at ' + datetimestamp() + '.')
    return return_html


def org_collaborations_diagram_qss(start_organizations: str,
                                   collab_organizations: str,
                                   researchresult_category: list,
                                   diagram_type: str = 'sankey',
                                   filename: str = '',
                                   caption: str = 'default_caption',
                                   generate_full_html: bool = True) -> str:
    """This is a wrapper for org_collaborations_diagram(), to be
    used for the supplementary material for:
    Rik D.T. Janssen (2026). Multi-source, multi-level, graph-based
    institutional collaboration indicators for research assessment
    with Ricgraph.
    Reference to the supplementary material:
    Janssen, Rik D. T. (2026). Supplemental material for
    Rik D.T. Janssen (2026), Multi-source, multi-level, graph-based
    institutional collaboration indicators for research assessment
    with Ricgraph. https://doi.org/10.5281/zenodo.19591591.

    :param start_organizations: See org_collaborations_diagram().
    :param collab_organizations: See org_collaborations_diagram().
    :param researchresult_category: See org_collaborations_diagram().
    :param diagram_type: See org_collaborations_diagram().
    :param filename: See org_collaborations_diagram().
    :param caption: See org_collaborations_diagram().
    :param generate_full_html: See org_collaborations_diagram().
    :return: See org_collaborations_diagram().
    """
    page_params = create_empty_page_params()
    query_params = create_empty_query_params()
    query_params['start_orgs'] = start_organizations
    query_params['collab_orgs'] = collab_organizations
    query_params['category_list'] = researchresult_category
    html = org_collaborations_diagram(page_params=page_params,
                                      query_params=query_params,
                                      diagram_type=diagram_type,
                                      filename=filename,
                                      caption=caption,
                                      generate_full_html=generate_full_html)
    return html


def three_org_collaborations_chord_qss(first_org: str,
                                       second_org: str,
                                       third_org: str,
                                       researchresult_category: list,
                                       filename: str = '',
                                       generate_full_html: bool = True) -> str:
    """This is a wrapper for three_org_collaborations_chord(), to be
    used for the supplementary material for:
    Rik D.T. Janssen (2026). Multi-source, multi-level, graph-based
    institutional collaboration indicators for research assessment
    with Ricgraph.
    Reference to the supplementary material:
    Janssen, Rik D. T. (2026). Supplemental material for
    Rik D.T. Janssen (2026), Multi-source, multi-level, graph-based
    institutional collaboration indicators for research assessment
    with Ricgraph. https://doi.org/10.5281/zenodo.19591591.

    :param first_org: See three_org_collaborations_chord().
    :param second_org: See three_org_collaborations_chord().
    :param third_org: See three_org_collaborations_chord().
    :param researchresult_category: See three_org_collaborations_chord().
    :param filename: See three_org_collaborations_chord().
    :param generate_full_html: See three_org_collaborations_chord().
    :return: See three_org_collaborations_chord().
    """
    query_params = create_empty_query_params()
    query_params['category_list'] = researchresult_category
    html = three_org_collaborations_chord(query_params=query_params,
                                          first_org=first_org,
                                          second_org=second_org,
                                          third_org=third_org,
                                          filename=filename,
                                          generate_full_html=generate_full_html)
    return html
