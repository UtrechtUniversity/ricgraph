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
# Ricgraph Explorer graph database functions.
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Explanation why sometimes Cypher queries are used.
# In some cases, Ricgraph Explorer uses a Cypher query instead of function calls
# that go from node to edges to neighbor nodes and so on.
# Sometimes, these calls can be slow, especially if:
# - the start node has a large number of neighbors (this may be the case with
#   top level organization nodes, e.g. with 'Utrecht University'), AND
# - the node type you'd want to find (in name_list and/or category_list) has
#   only a few matching nodes in Ricgraph (e.g. there are only a few 'competence'
#   or 'patent' nodes).
#
# I assume Cypher is faster because Python is an interpreted language, so loops
# may be a bit slow. In case a loop runs over a large number of nodes or edges,
# many calls to the graph database backend are done, which may take a lot of time.
# A cypher query is one call to the graph database backend. Also, there are
# many query optimizations in that backend, and the backend is a compiled application.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, January 2023.
# Extended Rik D.T. Janssen, February, September 2023 to May 2025.
#
# ########################################################################


from typing import Tuple, Union
from neo4j.graph import Node
from flask import url_for
from urllib.parse import urlencode
from ricgraph import (get_personroot_node,
                      get_all_neighbor_nodes, read_all_nodes,
                      create_multidimensional_dict)
from ricgraph_explorer_constants import (MAX_NR_NODES_TO_ENRICH,
                                         RESEARCH_OUTPUT_COLUMNS, DETAIL_COLUMNS)
from ricgraph_explorer_utils import (get_html_for_cardstart, get_html_for_cardend,
                                     get_message,
                                     get_you_searched_for_card)
from ricgraph_explorer_cypher import (find_organization_additional_info_cypher,
                                      find_person_organization_collaborations_cypher,
                                      find_person_share_resouts_cypher)
from ricgraph_explorer_table import  (get_regular_table, get_tabbed_table,
                                      get_html_for_histogram,
                                      get_html_for_tablestart, get_html_for_tableend)


def find_person_share_resouts(parent_node: Node,
                              category_want_list: list = None,
                              category_dontwant_list: list = None,
                              discoverer_mode: str = '',
                              extra_url_parameters: dict = None) -> str:
    """Function that finds with whom a person shares research results.

    :param parent_node: the starting node for finding shared research result types.
    :param category_want_list: the category list used for selection, or [] if any category.
    :param category_dontwant_list: the category list used for selection (i.e. not these).
    :param discoverer_mode: as usual.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    if extra_url_parameters is None:
        extra_url_parameters = {}
    if category_want_list is None:
        category_want_list = []
    if category_dontwant_list is None:
        category_dontwant_list = []

    html = ''
    if parent_node['category'] != 'person':
        message = 'Unexpected result in find_person_share_resouts(): '
        message += 'You have not passed an "person" node, but a "' + parent_node['category']
        message += '" node.'
        return get_message(message=message)

    connected_persons = find_person_share_resouts_cypher(parent_node=parent_node,
                                                         category_want_list=category_want_list,
                                                         category_dontwant_list=category_dontwant_list,
                                                         max_nr_items=extra_url_parameters['max_nr_items'])
    if discoverer_mode == 'details_view':
        table_columns = DETAIL_COLUMNS
    else:
        table_columns = RESEARCH_OUTPUT_COLUMNS

    table_header = 'This is the person we start with:'
    html += get_regular_table(nodes_list=[parent_node],
                              table_header=table_header,
                              table_columns=table_columns,
                              discoverer_mode=discoverer_mode,
                              extra_url_parameters=extra_url_parameters)
    if len(connected_persons) == 0:
        if len(category_want_list) == 1:
            message = 'This person does not share research result type "' + category_want_list[0] + '" '
        else:
            message = 'This person does not share any research result types '
        message += 'with other persons.'
        return html + get_message(message=message)

    if len(category_want_list) == 1:
        table_header = 'This person shares research result type "' + category_want_list[0] + '" '
    else:
        table_header = 'This person shares various research result types '
    table_header += 'with these persons:'
    html += get_regular_table(nodes_list=connected_persons,
                              table_header=table_header,
                              table_columns=table_columns,
                              discoverer_mode=discoverer_mode,
                              extra_url_parameters=extra_url_parameters)
    return html


def find_enrich_candidates_one_person(personroot: Node,
                                      name_want: list = None,
                                      category_want: list = None,
                                      source_system: str = '') -> Tuple[list, list]:
    """This function tries to find nodes to enrich source system 'source_system'.

    :param personroot: the starting node for finding enrichments for.
    :param name_want: a list containing several node names, indicating
      that we want all neighbor nodes of the person-root node of the organization
      specified by 'key', where the property 'name' equals
      one of the names in the list 'name_want'
      (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty (empty string), return all nodes.
    :param category_want: similar to 'name_want', but now for the property 'category'.
    :param source_system: the source system to find enrichments for.
    :return: 2 lists, nodes to identify and nodes to enrich.
    """
    nodes_in_source_system = []
    nodes_not_in_source_system = []
    neighbors = get_all_neighbor_nodes(node=personroot,
                                       name_want=name_want,
                                       category_want=category_want)
    for neighbor in neighbors:
        if source_system in neighbor['_source']:
            nodes_in_source_system.append(neighbor)
            continue
        if source_system not in neighbor['_source']:
            nodes_not_in_source_system.append(neighbor)
            continue

    if len(nodes_in_source_system) == 0:
        return [], nodes_not_in_source_system

    person_nodes = []
    for node_source in nodes_in_source_system:
        if node_source['category'] == 'person':
            person_nodes.append(node_source)

    return person_nodes, nodes_not_in_source_system


def find_enrich_candidates(parent_node: Union[Node, None],
                           source_system: str,
                           discoverer_mode: str = '',
                           extra_url_parameters: dict = None) -> str:
    """This function tries to find nodes to enrich source system 'source_system'.
    It is built around 'person-root' nodes. For each person-root node (in case there are
    more than one) we check if we can enrich that node.
    In case this function is used to find _all_ enrichments in Ricgraph,
    (then parent_node = None), a hard limit is used to break from the loop, since otherwise
    it would take too much time.
    We do not use 'name', 'category' and/or 'value' to get a list of nodes
    (as in e.g. find_overlap_in_source_systems()), because
    in that case we need to do an additional step to get these 'person-root' nodes.

    :param parent_node: the starting node for finding enrichments for, or None if
      you want to find enrichments for all 'person-root' nodes in Ricgraph.
    :param source_system: the source system to find enrichments for.
    :param discoverer_mode: as usual.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    import ricgraph_explorer as rcg_exp
    rcg_exp.get_all_globals_from_app_context()

    if extra_url_parameters is None:
        extra_url_parameters = {}

    if source_system not in rcg_exp.source_all:
        html = get_message(message='You have not specified a valid source system "'
                                   + source_system + '".')
        return html

    html = ''
    if parent_node is None:
        personroot_list = read_all_nodes(name='person-root',
                                         max_nr_nodes=int(extra_url_parameters['max_nr_items']))
        personroot_node = None
        message = 'You have chosen to enrich <em>all</em> nodes in Ricgraph for source system "'
        message += source_system + '". '
        message += 'However, that will take a long time. '
        message += 'Ricgraph Explorer will find enrich candidates for at most '
        message += str(MAX_NR_NODES_TO_ENRICH) + ' nodes. '
        message += 'If you want to find more nodes to enrich, change the constant '
        message += '<em>MAX_NR_NODES_TO_ENRICH</em> in file <em>ricgraph_explorer.py</em>.'
        html += get_message(message=message, please_try_again=False)
    else:
        personroot_node = get_personroot_node(node=parent_node)
        personroot_list = [personroot_node]

    if discoverer_mode == 'details_view':
        table_columns = DETAIL_COLUMNS
    else:
        table_columns = RESEARCH_OUTPUT_COLUMNS

    count = 1
    something_found = False
    for personroot in personroot_list:
        if count > MAX_NR_NODES_TO_ENRICH:
            break
        person_nodes, nodes_not_in_source_system = \
            find_enrich_candidates_one_person(personroot=personroot,
                                              source_system=source_system)
        if len(nodes_not_in_source_system) == 0:
            # All neighbors are only from 'source_system', nothing to report.
            continue

        # Now we are left with a node that _is_ in 'source_system'.
        something_found = True
        count += 1
        html += get_html_for_cardstart()
        table_header = 'This item is used to determine possible enrichments of source system "'
        table_header += source_system + '":'
        html += get_regular_table(nodes_list=[personroot],
                                  table_header=table_header,
                                  table_columns=table_columns,
                                  extra_url_parameters=extra_url_parameters)

        if len(person_nodes) == 0:
            message = 'There are enrich candidates '
            message += 'to enrich source system "' + source_system
            message += '", but there are no <em>person</em> nodes to identify this item in "'
            message += source_system + '".'
            html += get_message(message=message, please_try_again=False)
        else:
            table_header = 'You can use the information in this table to find this item in source system "'
            table_header += source_system + '":'
            html += get_regular_table(nodes_list=person_nodes,
                                      table_header=table_header,
                                      table_columns=table_columns,
                                      extra_url_parameters=extra_url_parameters)

        table_header = 'You could enrich source system "' + source_system + '" '
        table_header += 'by using this information harvested from other source systems. '
        table_header += 'This information is not in source system "' + source_system + '".'
        html += get_tabbed_table(nodes_list=nodes_not_in_source_system,
                                 table_header=table_header,
                                 table_columns=table_columns,
                                 tabs_on='category',
                                 discoverer_mode=discoverer_mode,
                                 extra_url_parameters=extra_url_parameters)
        html += get_html_for_cardend()

    if something_found:
        if parent_node is not None:
            pass
            # ### This may be added in a future release.
            # This message is only useful if we have entered this function with the
            # aim to enrich one node.
            # message = 'The table above shows how you can enrich source system "'
            # message += source_system + '" based on one person node. '
            # message += '<a href=' + url_for('findenrichcandidates') + '?'
            # message += urllib.parse.urlencode({'discoverer_mode': discoverer_mode,
            #                                    'source_system': source_system}) + '>'
            # message += 'You can click here if you would like to find candidates to enrich '
            # message += 'for <em>all</em> nodes in Ricgraph</a>. '
            # message += 'Warning: this may take quite some time.'
            # html += get_message(message=message, please_try_again=False)
            # ### end.
    else:
        if parent_node is None:
            message = 'Ricgraph could not find any information in other source systems '
            message += 'to enrich source system "' + source_system + '".'
            html += get_message(message=message)
        else:
            html += get_html_for_cardstart()
            table_header = 'This item is used to determine possible enrichments of source system "'
            table_header += source_system + '":'
            html += get_regular_table(nodes_list=[personroot_node],
                                      table_header=table_header,
                                      table_columns=table_columns,
                                      extra_url_parameters=extra_url_parameters)
            html += '</br>Ricgraph could not find any information in other source systems '
            html += 'to enrich source system "' + source_system + '".'
            html += get_html_for_cardend()

    html += '</p>'

    return html


def find_person_organization_collaborations(parent_node: Node,
                                            discoverer_mode: str = '',
                                            extra_url_parameters: dict = None) -> str:
    """Function that finds with which organization a person collaborates.

    A person X from organization A collaborates with a person Y from
    organization B if X and Y have both contributed to the same research result.
    All research result types are in 'resout_types_all'.
    This function does not give an overview of the persons that person X collaborates
    with (although those are determined in this function) because there is
    another function to do that.

    :param parent_node: the starting node for finding collaborating organizations.
    :param discoverer_mode: as usual.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    if extra_url_parameters is None:
        extra_url_parameters = {}

    html = ''
    if parent_node['category'] != 'person':
        message = 'Unexpected result in find_person_organization_collaborations(): '
        message += 'You have not passed an "person" node, but a "' + parent_node['category']
        message += '" node.'
        return get_message(message=message)

    personroot_node_organizations, collaborating_organizations = \
        find_person_organization_collaborations_cypher(parent_node=parent_node,
                                                       max_nr_items=extra_url_parameters['max_nr_items'])

    if discoverer_mode == 'details_view':
        table_columns = DETAIL_COLUMNS
    else:
        table_columns = RESEARCH_OUTPUT_COLUMNS

    table_header = 'This is the person we start with:'
    html += get_regular_table(nodes_list=[parent_node],
                              table_header=table_header,
                              table_columns=table_columns,
                              discoverer_mode=discoverer_mode,
                              extra_url_parameters=extra_url_parameters)

    if len(personroot_node_organizations) == 0:
        html += get_message(message='This person does not work at any organization.',
                            please_try_again=False)
    else:
        table_header = 'This person works at the following organizations:'
        html += get_regular_table(nodes_list=personroot_node_organizations,
                                  table_header=table_header,
                                  table_columns=table_columns,
                                  discoverer_mode=discoverer_mode,
                                  extra_url_parameters=extra_url_parameters)

    if len(collaborating_organizations) == 0:
        message = 'This person has no collaborations with other organizations.'
        return html + get_message(message=message)

    table_header = 'This person collaborates with the following organizations:'
    html += get_regular_table(nodes_list=collaborating_organizations,
                              table_header=table_header,
                              table_columns=table_columns,
                              discoverer_mode=discoverer_mode,
                              extra_url_parameters=extra_url_parameters)
    return html


def find_organization_additional_info(parent_node: Node,
                                      name_list: list = None,
                                      category_list: list = None,
                                      discoverer_mode: str = '',
                                      extra_url_parameters: dict = None) -> str:
    """Function that finds additional information connected to a (sub-)organization.

    :param parent_node: the starting node for finding additional information.
    :param name_list: the name list used for selection.
    :param category_list: the category list used for selection.
    :param discoverer_mode: as usual.
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    if extra_url_parameters is None:
        extra_url_parameters = {}

    if parent_node is None:
        message = 'Unexpected result in find_organization_additional_info(): '
        message += 'This organization cannot be found in Ricgraph.'
        return get_message(message=message)

    if parent_node['category'] != 'organization':
        message = 'Unexpected result in find_organization_additional_info(): '
        message += 'You have not passed an "organization" node, but a "' + parent_node['category']
        message += '" node. '
        return get_message(message=message)

    if name_list is None:
        name_list = []
    if category_list is None:
        category_list = []
    name_str = ''
    category_str = ''
    if len(name_list) == 1:
        name_str = name_list[0]
    if len(category_list) == 1:
        category_str = category_list[0]

    cypher_result = \
        find_organization_additional_info_cypher(parent_node=parent_node,
                                                 name_list=name_list,
                                                 category_list=category_list,
                                                 max_nr_items=extra_url_parameters['max_nr_items'])
    if len(cypher_result) == 0:
        message = 'Could not find any persons or results for this organization'
        if name_str != '' and category_str != '':
            message += ', using search terms '
            message += '"' + name_str + '" and "' + category_str + '".'
        elif name_str != '':
            message += ', using search term '
            message += '"' + name_str + '".'
        elif category_str != '':
            message += ', using search term '
            message += '"' + category_str + '".'
        else:
            message += '.'
        return get_message(message=message)

    relevant_result = []
    expertise_area_list = []
    research_area_list = []
    skill_list = []
    if 'competence' in category_list:
        we_have_competence = True
    else:
        we_have_competence = False

    for result in cypher_result:
        node = result['second_neighbor']
        relevant_result.append(node)
        if we_have_competence:
            if node['name'] == 'EXPERTISE_AREA':
                expertise_area_list.append({'name': node['value'],
                                            'value': result['count_second_neighbor']})
            elif node['name'] == 'RESEARCH_AREA':
                research_area_list.append({'name': node['value'],
                                           'value': result['count_second_neighbor']})
            elif node['name'] == 'SKILL':
                skill_list.append({'name': node['value'],
                                   'value': result['count_second_neighbor']})

    if discoverer_mode == 'details_view':
        table_columns = DETAIL_COLUMNS
    else:
        table_columns = RESEARCH_OUTPUT_COLUMNS

    html = ''
    table_header = 'This item is used for finding information about the persons '
    table_header += 'or their results of this organization:'
    html += get_regular_table(nodes_list=[parent_node],
                              table_header=table_header,
                              table_columns=table_columns,
                              discoverer_mode=discoverer_mode,
                              extra_url_parameters=extra_url_parameters)
    table_header = 'These are all the '
    if name_str != '' and category_str != '':
        table_header += '"' + name_str + '" and "' + category_str + '" '
    elif name_str != '':
        table_header += '"' + name_str + '" '
    elif category_str != '':
        table_header += '"' + category_str + '" '
    else:
        table_header += 'shared '
    table_header += 'items of this organization:'
    table_html = get_tabbed_table(nodes_list=relevant_result,
                                  table_header=table_header,
                                  table_columns=table_columns,
                                  tabs_on='category',
                                  discoverer_mode=discoverer_mode,
                                  extra_url_parameters=extra_url_parameters)

    if we_have_competence:
        histogram_html = ''
        if len(expertise_area_list) > 1:
            histogram_html += get_html_for_cardstart()
            histogram_html += get_html_for_histogram(histogram_list=expertise_area_list,
                                                     histogram_width=250,
                                                     histogram_title='Histogram of "expertise area":')
            histogram_html += get_html_for_cardend()
        if len(research_area_list) > 1:
            histogram_html += get_html_for_cardstart()
            histogram_html += get_html_for_histogram(histogram_list=research_area_list,
                                                     histogram_width=250,
                                                     histogram_title='Histogram of "research area":')
            histogram_html += get_html_for_cardend()
        if len(skill_list) > 1:
            histogram_html += get_html_for_cardstart()
            histogram_html += get_html_for_histogram(histogram_list=skill_list,
                                                     histogram_width=250,
                                                     histogram_title='Histogram of "skill":')
            histogram_html += get_html_for_cardend()

        if histogram_html == '':
            # No data for any of the histograms.
            html += table_html
        else:
            # Divide space between histogram and table.
            html += '<div class="w3-row-padding w3-stretch" >'
            html += '<div class="w3-col" style="width:23em" >'
            html += histogram_html
            html += '</div>'
            html += '<div class="w3-rest" >'
            html += table_html
            html += '</div>'
            html += '</div>'
    else:
        html += table_html

    return html


def find_overlap_in_source_systems(name: str = '', category: str = '', value: str = '',
                                   discoverer_mode: str = '',
                                   overlap_mode: str = 'neighbornodes',
                                   extra_url_parameters: dict = None) -> str:
    """Get the overlap in items from source systems.
    We do need a 'name', 'category' and/or 'value', otherwise we won't be able
    to find overlap in source systems for a list of items. That list can only be
    found using these fields, and then these fields can be passed to
    find_overlap_in_source_systems_records() to show the overlap nodes in a table.
    If we want to find overlap of only one node, these fields will result in only one item
    to be found, and the overlap will be computed of the neighbors of that node.
    This function is tightly connected to find_overlap_in_source_systems_records().

    :param name: name of the node(s) to find.
    :param category: category of the node(s) to find.
    :param value: value of the node(s) to find.
    :param discoverer_mode: the discoverer_mode to use.
    :param overlap_mode: which overlap to compute: from this node ('thisnode')
      or from the neighbors of this node ('neighbornodes').
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    if extra_url_parameters is None:
        extra_url_parameters = {}

    html = ''
    nodes = read_all_nodes(name=name, category=category, value=value)
    if len(nodes) == 0:
        # Let's try again, assuming we did a broad search instead of an exact match search.
        nodes = read_all_nodes(value=value,
                               value_is_exact_match=False)
        if len(nodes) == 0:
            return get_message(message='Ricgraph Explorer could not find anything.')

    if overlap_mode == 'neighbornodes':
        # In this case, we would like to know the overlap of nodes neighboring the node
        # we have just found. We can only do that if we have found only one node.
        if len(nodes) > 1:
            message = 'Ricgraph Explorer found too many nodes. It cannot compute the overlap '
            message += 'of the neighbor nodes of more than one node in get_overlap_in_source_systems().'
            return get_message(message=message)

        parent_node = nodes[0]
        if parent_node['category'] == 'person':
            personroot = get_personroot_node(node=parent_node)
            if personroot is None:
                message = 'Ricgraph Explorer found no "person-root" '
                message += 'node in get_overlap_in_source_systems().'
                return get_message(message=message)
            neighbor_nodes = get_all_neighbor_nodes(node=personroot)
        else:
            neighbor_nodes = get_all_neighbor_nodes(node=parent_node)
        nodes = neighbor_nodes.copy()

    nr_total_recs = 0
    nr_recs_from_one_source = 0
    nr_recs_from_multiple_sources = 0
    recs_from_one_source = create_multidimensional_dict(1, int)
    recs_from_multiple_sources = create_multidimensional_dict(1, int)
    recs_from_multiple_sources_histogram = create_multidimensional_dict(2, int)

    # Determine the overlap in source systems.
    for node in nodes:
        sources = node['_source']
        if len(sources) == 0:
            continue
        nr_total_recs += 1
        if len(sources) == 1:
            nr_recs_from_one_source += 1
            recs_from_one_source[sources[0]] += 1
            continue
        nr_recs_from_multiple_sources += 1
        for system1 in sources:
            recs_from_multiple_sources[system1] += 1
            for system2 in sources:
                recs_from_multiple_sources_histogram[system1][system2] += 1

    if nr_total_recs == 0:
        if overlap_mode == 'neighbornodes':
            message = 'Ricgraph Explorer found no overlap in source systems for '
            message += 'the neighbors of this node. '
            message += 'This may be caused by that these neighbors are "person-root" nodes. '
            message += 'These nodes are generated by Ricgraph and do not have a source system.'
            return get_message(message=message)
        return ''

    # Now determine all the systems we have harvested from.
    all_harvested_systems = []
    for system in recs_from_one_source:
        if system not in all_harvested_systems:
            all_harvested_systems.append(system)
    for system in recs_from_multiple_sources:
        if system not in all_harvested_systems:
            all_harvested_systems.append(system)
    all_harvested_systems.sort()

    html += get_html_for_cardstart()
    # html += '<h2>Your query</h2>'
    # html += 'This was your query:'
    # html += '<ul>'
    # if name != '':
    #     html += '<li>name: <i>"' + str(name) + '"</i>'
    # if category != '':
    #     html += '<li>category: <i>"' + str(category) + '"</i>'
    # if value != '':
    #     html += '<li>value: <i>"' + str(value) + '"</i>'
    # html += '</ul>'
    #
    # html += '<br/>'
    html += '<h2>Number of items in source systems</h2>'
    html += 'This table shows the number of items found in only one source or '
    html += 'found in multiple sources for your query. '
    html += 'You can click on a number to retrieve these items.'
    html += get_html_for_tablestart()
    html += '<tr class="uu-yellow">'
    html += '<th class="sorttable_nosort">Source systems</th>'
    html += '<th class="sorttable_nosort">Total items in source systems: '
    html += str(nr_total_recs)
    html += '</th>'
    html += '<th class="sorttable_nosort">Total items found in only one source: '
    html += str(nr_recs_from_one_source)
    html += ' (' + str(round(100 * nr_recs_from_one_source/nr_total_recs))
    html += '% of total ' + str(nr_total_recs) + ' items)'
    html += '</th>'
    html += '<th class="sorttable_nosort">Total items found in multiple sources: '
    html += str(nr_recs_from_multiple_sources)
    html += ' (' + str(round(100 * nr_recs_from_multiple_sources/nr_total_recs))
    html += '% of total ' + str(nr_total_recs) + ' items)'
    html += '</th>'
    html += '</tr>'

    for system in all_harvested_systems:
        html += '<tr class="item">'
        html += '<td>' + system + '</td>'
        row_total = 0
        if system in recs_from_one_source:
            row_total += recs_from_one_source[system]
        if system in recs_from_multiple_sources:
            row_total += recs_from_multiple_sources[system]

        if row_total > 0:
            html += '<td>' + str(row_total) + '</td>'
        else:
            html += '<td>0</td>'
        if system in recs_from_one_source:
            html += '<td>'
            html += '<a href="' + url_for('resultspage') + '?'
            html += urlencode({'name': name, 'category': category, 'value': value,
                                            'system1': system,
                                            'system2': 'singlesource',
                                            'view_mode': 'view_regular_table_overlap_records',
                                            'discoverer_mode': discoverer_mode,
                                            'overlap_mode': overlap_mode}
                                           | extra_url_parameters)
            html += '">'
            html += str(recs_from_one_source[system])
            html += '</a>'
            html += ' (' + str(round(100 * recs_from_one_source[system]/nr_recs_from_one_source))
            html += '% of ' + str(nr_recs_from_one_source) + ' items are only in ' + system + ')'
            html += '</td>'
        else:
            html += '<td>0</td>'
        if system in recs_from_multiple_sources:
            html += '<td>'
            html += '<a href="' + url_for('resultspage') + '?'
            html += urlencode({'name': name, 'category': category, 'value': value,
                                            'system1': system,
                                            'system2': 'multiplesource',
                                            'view_mode': 'view_regular_table_overlap_records',
                                            'discoverer_mode': discoverer_mode,
                                            'overlap_mode': overlap_mode}
                                           | extra_url_parameters)
            html += '">'
            html += str(recs_from_multiple_sources[system])
            html += '</a>'
            html += ' (' + str(round(100 * recs_from_multiple_sources[system]/nr_recs_from_multiple_sources))
            html += '% of ' + str(nr_recs_from_multiple_sources) + ' items are in multiple sources)'
            html += '</td>'
        else:
            html += '<td>0</td>'
    html += '</tr>'
    html += get_html_for_tableend()
    html += 'Note that the numbers in the columns "Total items in source systems" '
    html += 'and "Total items found in multiple sources" do not need '
    html += 'to count up to resp. '
    html += 'the total number of items ('
    html += str(nr_total_recs)
    html += ') and the total number of items from multiple sources ('
    html += str(nr_recs_from_multiple_sources)
    html += ') since an item in that column will originate from multiple sources, and subsequently will occur '
    html += 'in in multiple rows of that column.'

    if nr_recs_from_multiple_sources == 0:
        html += get_html_for_cardend()
        return html

    html += '<br/>'
    html += '<br/>'
    html += '<h2>Overlap in items from multiple sources</h2>'
    html += 'For the items found for your query in multiple sources, this table shows in which sources '
    html += 'they were found. '
    html += 'You can click on a number to retrieve these items. '
    html += 'The second column in this table corresponds to the last column in '
    html += 'the previous table.'

    html += get_html_for_tablestart()
    html_header2 = '<tr class="uu-yellow">'
    html_header2 += '<th class="sorttable_nosort">An item from \u25be...</th>'
    html_header2 += '<th class="sorttable_nosort">Total items found in multiple sources</th>'
    count = 0
    for second in all_harvested_systems:
        html_header2 += '<th class="sorttable_nosort">' + second + '</th>'
        count += 1
    html_header2 += '</tr>'
    html_header1 = '<tr class="uu-yellow">'
    html_header1 += '<th class="sorttable_nosort" colspan="2"></th>'
    html_header1 += '<th class="sorttable_nosort" colspan="' + str(count) + '">... was also found in \u25be</th>'
    html_header1 += '</tr>'
    html += html_header1 + html_header2

    for system1 in all_harvested_systems:
        html += '<tr class="item">'
        html += '<td>' + system1 + '</td>'
        if system1 in recs_from_multiple_sources:
            html += '<td>'
            html += '<a href="' + url_for('resultspage') + '?'
            html += urlencode({'name': name, 'category': category, 'value': value,
                                            'system1': system1,
                                            'system2': 'multiplesource',
                                            'view_mode': 'view_regular_table_overlap_records',
                                            'discoverer_mode': discoverer_mode,
                                            'overlap_mode': overlap_mode}
                                           | extra_url_parameters)
            html += '">'
            html += str(recs_from_multiple_sources[system1])
            html += '</a>'
            html += '</td>'
        else:
            html += '<td>0</td>'
        for system2 in all_harvested_systems:
            if system1 == system2:
                html += '<td>&check;</td>'
                continue
            if system2 in recs_from_multiple_sources_histogram[system1]:
                html += '<td>'
                html += '<a href="' + url_for('resultspage') + '?'
                html += urlencode({'name': name, 'category': category, 'value': value,
                                                'system1': system1,
                                                'system2': system2,
                                                'view_mode': 'view_regular_table_overlap_records',
                                                'discoverer_mode': discoverer_mode,
                                                'overlap_mode': overlap_mode}
                                               | extra_url_parameters)
                html += '">'
                html += str(recs_from_multiple_sources_histogram[system1][system2])
                percent = recs_from_multiple_sources_histogram[system1][system2]/recs_from_multiple_sources[system1]
                html += ' (' + str(round(100 * percent)) + '%)'
                html += '</a>'
                html += '</td>'
            else:
                html += '<td>0</td>'
        html += '</tr>'
    html += get_html_for_tableend()
    html += 'Note that the number of items in a row in column 3, 4, etc. do not need '
    html += 'to count up to the total number of items from that source (in the second column), '
    html += 'since an item in this table will originate from at least two sources, '
    html += 'and subsequently will occur multiple times on the same row.'
    html += get_html_for_cardend()

    return html


def find_overlap_in_source_systems_records(name: str = '', category: str = '', value: str = '',
                                           system1: str = '', system2: str = '',
                                           discoverer_mode: str = '',
                                           overlap_mode: str = '',
                                           extra_url_parameters: dict = None) -> str:
    """Show the overlap items in a html table.
    This function is tightly connected to find_overlap_in_source_systems().
    We do need a 'name', 'category' and/or 'value', otherwise we won't be able
    to find overlap in source systems for a list of items.

    :param name: name of the node(s) to find.
    :param category: category of the node(s) to find.
    :param value: value of the node(s) to find.
    :param system1: source system 1 used to compute the overlap.
    :param system2: source system 2 used to compute the overlap.
    :param discoverer_mode: the discoverer_mode to use.
    :param overlap_mode: which overlap to compute: from this node ('thisnode')
      or from the neighbors of this node ('neighbornodes').
    :param extra_url_parameters: extra parameters to be added to the url.
    :return: html to be rendered.
    """
    if extra_url_parameters is None:
        extra_url_parameters = {}

    html = ''
    if system1 == '' and system2 != '':
        # swap
        system1 = system2
        system2 = ''
    if system1 == 'singlesource' or system1 == 'multiplesource':
        if system2 != '':
            # swap
            temp = system1
            system1 = system2
            system2 = temp

    result = read_all_nodes(name=name, category=category, value=value)
    if len(result) == 0:
        # Let's try again, assuming we did a broad search instead of an exact match search.
        result = read_all_nodes(value=value,
                                value_is_exact_match=False)
        if len(result) == 0:
            # No, we really didn't find anything.
            message = 'Unexpected result in find_overlap_in_source_systems_records(): '
            message += 'This node cannot be found in Ricgraph.'
            return get_message(message=message)

    if overlap_mode == 'neighbornodes':
        # In this case, we would like to know the overlap of nodes neighboring the node
        # we have just found. We can only do that if we have found only one node.
        if len(result) > 1:
            message = 'Ricgraph Explorer found too many nodes. It cannot compute the overlap '
            message += 'of the neighbor nodes of more than one node '
            message += 'in find_overlap_in_source_systems_records().'
            return get_message(message=message)

        node = result[0]
        if node['category'] == 'person':
            personroot = get_personroot_node(node)
            if personroot is None:
                message = 'Unexpected result in find_overlap_in_source_systems_records(): '
                message += 'Ricgraph Explorer found no "person-root" node.'
                return get_message(message=message)
            neighbor_nodes = get_all_neighbor_nodes(node=personroot)
        else:
            neighbor_nodes = get_all_neighbor_nodes(node=node)
        result = neighbor_nodes.copy()

    relevant_result = []
    for node in result:
        sources = node['_source']
        if system1 == '':
            # Then system2 will also be '', see swap above.
            relevant_result.append(node)
            continue
        if system2 == '':
            if system1 in sources:
                relevant_result.append(node)
                continue
        if system2 == 'singlesource':
            if system1 in sources and len(sources) == 1:
                relevant_result.append(node)
                continue
        if system2 == 'multiplesource':
            if system1 in sources and len(sources) > 1:
                relevant_result.append(node)
                continue
        if system1 in sources and system2 in sources:
            relevant_result.append(node)

    if discoverer_mode == 'details_view':
        table_columns = DETAIL_COLUMNS
        html += get_you_searched_for_card(name=name,
                                          category=category,
                                          value=value,
                                          discoverer_mode=discoverer_mode,
                                          overlap_mode=overlap_mode,
                                          system1=system1,
                                          system2=system2,
                                          extra_url_parameters=extra_url_parameters)
    else:
        table_columns = RESEARCH_OUTPUT_COLUMNS

    html += get_regular_table(nodes_list=relevant_result,
                              table_header='These items conform to your selection:',
                              table_columns=table_columns,
                              discoverer_mode=discoverer_mode,
                              extra_url_parameters=extra_url_parameters)
    return html
