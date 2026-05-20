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
# Ricgraph Explorer Cypher related functions.
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
# Extended Rik D.T. Janssen, February, September 2023 to June 2025.
# Extended Rik D.T. Janssen, October 2025, March 2026.
#
# ########################################################################


from typing import Tuple
from pandas import DataFrame
from neo4j.graph import Node
from ricgraph import (read_node,
                      get_personroot_node, get_all_neighbor_nodes,
                      ricgraph_database, ricgraph_databasename,
                      convert_cypher_recordslist_to_nodeslist,
                      extract_organization_abbreviation,
                      ORGANIZATION_CATEGORY_ORGANISATION,
                      RICGRAPH_UNKNOWN,
                      cypher_print_resultsummary,
                      check_valid_year,
                      QueryParams)
from ricgraph_explorer_constants import (RICGRAPH_NODEINFO,
                                         RICGRAPH_SYSTEMINFO,
                                         MAX_ITEMS_TO_RETURN)
from ricgraph_explorer_init import get_ricgraph_explorer_global
from ricgraph_explorer_utils import get_global_list, get_global_dataframe


def find_person_share_resouts_cypher(parent_node: Node | None,
                                     category_want_list: list = None,
                                     category_dontwant_list: list = None,
                                     max_nr_items: int = MAX_ITEMS_TO_RETURN) -> list:
    """ For documentation, see find_person_share_resouts().
    This is the cypher functionality for that function.

    :param parent_node:
    :param category_want_list:
    :param category_dontwant_list:
    :param max_nr_items:
    :return:
    """
    graph = get_ricgraph_explorer_global(name='graph')
    if graph is None:
        print('find_person_share_resouts_cypher(): Error: graph has not been initialized or opened.')
        return []

    if category_want_list is None:
        category_want_list = []
    if category_dontwant_list is None:
        category_dontwant_list = []

    # By using the following statement we can start with both a node and its person-root node.
    personroot_node = get_personroot_node(node=parent_node)
    if personroot_node is None:
        return []
    cypher_query = 'MATCH (startnode_personroot:RicgraphNode)'
    cypher_query += '-[]->(neighbor:RicgraphNode)'
    cypher_query += '-[]->(neighbor_personroot:RicgraphNode)'
    cypher_query += 'WHERE '
    if ricgraph_database() == 'neo4j':
        cypher_query += 'elementId(startnode_personroot)=$startnode_personroot_element_id AND '
    else:
        cypher_query += 'id(startnode_personroot)=toInteger($startnode_personroot_element_id) AND '
    # The following statement is really necessary for speed reasons.
    cypher_query += 'startnode_personroot.name="person-root" AND '
    if len(category_want_list) > 0:
        cypher_query += 'neighbor.category IN $category_want_list AND '
    if len(category_dontwant_list) > 0:
        cypher_query += 'NOT neighbor.category IN $category_dontwant_list AND '
    cypher_query += 'neighbor_personroot.name="person-root" AND '
    if ricgraph_database() == 'neo4j':
        cypher_query += 'elementId(neighbor_personroot)<>elementId(startnode_personroot) '
    else:
        cypher_query += 'id(neighbor_personroot)<>id(startnode_personroot) '
    cypher_query += 'RETURN DISTINCT neighbor_personroot '
    if max_nr_items > 0:
        cypher_query += 'LIMIT $max_nr_items '
    # print(cypher_query)

    # Note that the RETURN (as in RETURN DISTINCT *) also has all intermediate results, such
    # as the common research results (in 'neighbor'). We don't use them at the moment.
    records, _, _ = graph.execute_query(query_=cypher_query,
                                        startnode_personroot_element_id=personroot_node.element_id,
                                        category_want_list=category_want_list,
                                        category_dontwant_list=category_dontwant_list,
                                        max_nr_items=max_nr_items,
                                        database_=ricgraph_databasename())
    connected_persons = [record['neighbor_personroot'] for record in records]
    return connected_persons


def find_person_organization_collaborations_cypher(parent_node: Node | None,
                                                   max_nr_items: int = MAX_ITEMS_TO_RETURN) -> Tuple[list, list]:
    """ For documentation, see find_person_organization_collaborations().
    This is the cypher functionality for that function.

    :param parent_node:
    :param max_nr_items:
    :return:
    """
    graph = get_ricgraph_explorer_global(name='graph')
    if graph is None:
        print('find_person_organization_collaborations_cypher(): Error: graph has not been initialized or opened.')
        return [], []

    # By using the following statement we can start with both a node and its person-root node.
    personroot_node = get_personroot_node(node=parent_node)
    if personroot_node is None:
        return [], []
    cypher_query = 'MATCH (startnode_personroot:RicgraphNode)'
    cypher_query += '-[]->(neighbor:RicgraphNode)'
    cypher_query += '-[]->(neighbor_personroot:RicgraphNode)'
    cypher_query += '-[]->(neighbor_organization:RicgraphNode) '
    cypher_query += 'WHERE '
    if ricgraph_database() == 'neo4j':
        cypher_query += 'elementId(startnode_personroot)=$startnode_personroot_element_id AND '
    else:
        cypher_query += 'id(startnode_personroot)=toInteger($startnode_personroot_element_id) AND '
    # The following statement is really necessary for speed reasons.
    cypher_query += 'startnode_personroot.name="person-root" AND '
    cypher_query += 'neighbor.category IN $researchresult_category_active AND '
    cypher_query += 'neighbor_personroot.name="person-root" AND '
    if ricgraph_database() == 'neo4j':
        cypher_query += 'elementId(neighbor_personroot)<>elementId(startnode_personroot) AND '
    else:
        cypher_query += 'id(neighbor_personroot)<>id(startnode_personroot) AND '
    cypher_query += 'neighbor_organization.category="organization" '
    cypher_query += 'RETURN DISTINCT neighbor_organization '
    if max_nr_items > 0:
        cypher_query += 'LIMIT $max_nr_items '
    # print(cypher_query)
    # Note that the RETURN (as in RETURN DISTINCT *) also has all intermediate results, such
    # as the collaborating researchers (in 'neighbor_personroot') and the common research
    # results (in 'neighbor'). We don't use them at the moment.

    # Note that 'records' will contain _all_ organizations that 'parent_node'
    # collaborates with, very probably also the organizations this person works for.
    researchresult_category_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                                     item='researchresult_category_active')
    records, _, _ = graph.execute_query(query_=cypher_query,
                                        startnode_personroot_element_id=personroot_node.element_id,
                                        researchresult_category_active=researchresult_category_active,
                                        max_nr_items=max_nr_items,
                                        database_=ricgraph_databasename())

    # Get the organizations from 'parent_node'.
    personroot_node = get_personroot_node(node=parent_node)
    personroot_node_organizations = get_all_neighbor_nodes(node=personroot_node,
                                                           category_want=[ORGANIZATION_CATEGORY_ORGANISATION])
    # Now get the organizations that 'parent_node' collaborates with, excluding
    # this person's own organizations. Note that the types of 'records'
    # and 'personroot_node_organizations' are not the same.
    personroot_node_organizations_key = []
    for organization in personroot_node_organizations:
        personroot_node_organizations_key.append(organization['_key'])

    collaborating_organizations = []
    for organization_node in records:
        if len(organization_node) == 0:
            continue
        organization = organization_node['neighbor_organization']
        organization_key = organization['_key']
        if organization_key not in personroot_node_organizations_key:
            collaborating_organizations.append(organization)

    return personroot_node_organizations, collaborating_organizations


def find_organization_additional_info_nodes(parent_node: Node,
                                            query_params: QueryParams) -> list:
    """Function that finds additional information connected to a (sub-)organization.
    Very similar to find_organization_additional_info_cypher(),
    except that this function returns a list of nodes.

    :param parent_node: the starting node for finding additional information.
    :param query_params: parameters related to the query passed in the URL.
    :return: A list of Nodes.
"""
    records = find_organization_additional_info_cypher(parent_node=parent_node,
                                                       query_params=query_params)
    nodes_list = [record['second_neighbor'] for record in records]
    if len(nodes_list) == 0:
        return []
    else:
        return nodes_list


def find_organization_additional_info_cypher(parent_node: Node,
                                             query_params: QueryParams) -> list:
    """Function that finds additional information connected to a (sub-)organization.
    This is the cypher functionality for find_organization_additional_info().
    You can also use it to find additional info for any type of node, which
    is connected to a person-root.

    :param parent_node: the starting node for finding additional information.
    :param query_params: parameters related to the query passed in the URL.
    :return: A list of Records. Each element is a Record, where the first
      element is a Node, and the second the number of times it is found.
      If you only need nodes, use find_organization_additional_info_nodes().
    """
    graph = get_ricgraph_explorer_global(name='graph')
    if graph is None:
        print('find_organization_additional_info_cypher(): Error: graph has not been initialized or opened.')
        return []
    if (message := check_valid_year(year_first=query_params['year_first'],
                                    year_last=query_params['year_last'])) != '':
        print(message)
        return []

    # Prepare and execute Cypher query.
    clauses = []
    cypher_query = 'MATCH (node:RicgraphNode)'
    cypher_query += '-[]->(neighbor:RicgraphPersonRoot)'
    cypher_query += '-[]->(second_neighbor:RicgraphNode) '
    if ricgraph_database() == 'neo4j':
        cypher_query += 'WHERE elementId(node)=$node_element_id '
    else:
        cypher_query += 'WHERE id(node)=toInteger($node_element_id) '
    if len(query_params['name_list']) > 0:
        clauses.append('second_neighbor.name IN $name_list')
    if len(query_params['category_list']) > 0:
        clauses.append('second_neighbor.category IN $category_list')
    if query_params['source_system'] != '':
        clauses.append('NOT $source_system IN second_neighbor._source')
    if query_params['year_first'] != '':
        clauses.append('second_neighbor.year >= $year_first')
    if query_params['year_last'] != '':
        clauses.append('second_neighbor.year <= $year_last')
    if len(query_params['license']) > 0:
        clauses.append('second_neighbor.license IN $license')
    if len(query_params['access']) > 0:
        clauses.append('second_neighbor.access IN $access')

    if len(clauses) >= 1:
        cypher_query += 'AND ' + ' AND '.join(clauses) + ' '

    cypher_query += 'RETURN DISTINCT second_neighbor, COUNT(second_neighbor) AS count_second_neighbor '
    cypher_query += 'ORDER BY count_second_neighbor DESC '
    if query_params['max_nr_items'] > 0:
        cypher_query += 'LIMIT $max_nr_items '
    # print(cypher_query)
    records, _, _ = graph.execute_query(query_=cypher_query,
                                        node_element_id=parent_node.element_id,
                                        **query_params,
                                        database_=ricgraph_databasename())
    if len(records) == 0:
        return []
    else:
        return records


def find_collabs_cypher(query_params: QueryParams,
                        cypher_return_clause: str = '') -> list:
    """Find collaborations, starting from start_orgs,
    for a certain research result.
    Collaborations are defined as nodes connected as follows:
    (start_orgs)-[]->(persroot1)-[]->(researchresult)
       -[]->(persroot2)-[]->(collab_orgs).
    This function is used for several purposes, but for all of those purposes
    only the RETURN part is different. That is why the RETURN is passed
    as 'cypher_return_clause'.

    :param query_params: Parameters related to the query passed in the URL.
     - start_orgs: the organization(s) to start with. This may be
       a substring, then a STARTS WITH is used in the cypher query.
     - collab_orgs: if specified, only return organization(s) that
       collaborate with start_orgs. If empty '', return any organization(s)
       that start_orgs collaborate with.
     - category_list: if specified, only return collaborations
       for this research result category. If empty list, return all collaborations,
       regardless of the research result category.
     - max_nr_items: return at most this number of collaborating organizations,
       0 = return all collaborating organizations,
    :param cypher_return_clause: the RETURN part of the cypher query that is
      constructed in this function.
    :return: a list of nodes conforming to the cypher query, or [] if nothing found.
    """
    orgs_with_hierarchies = get_global_dataframe(ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                 item='orgs_with_hierarchies')
    researchresult_category_publication = get_global_list(ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                          item='researchresult_category_publication')
    graph = get_ricgraph_explorer_global(name='graph')
    if graph is None:
        print('find_collabs_cypher(): Error: graph has not been initialized or opened.')
        return []
    if query_params['start_orgs'] == '':
        print('find_collabs_cypher(): Warning: empty "start_orgs" not possible.')
        return []
    if cypher_return_clause == '':
        print('find_collabs_cypher(): Error, you have not specified a cypher RETURN clause, exiting.')
        exit(1)
    if query_params['category_list'] is None:
        query_params['category_list'] = []

    print('Finding collaborations')
    if query_params['collab_orgs'] == '':
        print('  from "' + query_params['start_orgs'] + '" to "all"')
    else:
        print('  from "' + query_params['start_orgs'] + '" to "' + query_params['collab_orgs'] + '"')
    if len(query_params['category_list']) == 0:
        print('  using research result category "all".')
    elif sorted(query_params['category_list']) == sorted(researchresult_category_publication):
        print('  using research result category (meta category) "publication".')
    else:
        print('  using research result category "' + str(query_params['category_list']) + '".')

    cypher_query = 'MATCH (start_orgs:RicgraphNode)'
    cypher_query += '-[]->(persroot1:RicgraphPersonRoot)'
    cypher_query += '-[]->(researchresult:RicgraphResearchResult)'
    cypher_query += '-[]->(persroot2:RicgraphPersonRoot)'
    cypher_query += '-[]->(collab_orgs:RicgraphOrganization) '

    cypher_query += 'WHERE start_orgs.name="ORGANIZATION_NAME" '
    if read_node(name='ORGANIZATION_NAME', value=query_params['start_orgs']) is None:
        # We are to find collaborating organizations of a series of organizations,
        # because we cannot find start_orgs.
        cypher_query += 'AND start_orgs.value STARTS WITH $start_orgs '
    else:
        # We are to find collaborating organizations of only one organization.
        # This query is much more efficient.
        cypher_query += 'AND start_orgs.value=$start_orgs '

    if len(query_params['category_list']) > 0:
        # Restrict the result to collaborations of a certain research result category.
        cypher_query += 'AND researchresult.category IN $category_list '

    cypher_query += 'AND persroot1<>persroot2 '
    cypher_query += 'AND start_orgs<>collab_orgs '

    org_abbr = ''
    if query_params['collab_orgs'] == '':
        # If we are to match any organization...
        org_abbr = extract_organization_abbreviation(org_name=query_params['start_orgs'])
        if orgs_with_hierarchies is None or orgs_with_hierarchies.empty:
            print('find_collabs_cypher(): Error, you should have specified "orgs_with_hierarchies", exiting...')
            exit(1)
        if org_abbr in orgs_with_hierarchies['org_abbreviation'].values:
            # ... and 'start_organization' has sub-organizations (which is specified
            # in orgs_with_hierarchies), do not match any (sub-)organizations of it in
            # 'collab_orgs'.
            # Please also read the design decision at org_collaborations_diagram().
            cypher_query += 'AND NOT collab_orgs.value STARTS WITH $org_abbr '
    else:
        # We are to find collaborations limited to certain organization(s).
        if read_node(name='ORGANIZATION_NAME', value=query_params['collab_orgs']) is None:
            # We are to find collaborations from start_orgs with multiple organizations,
            # because we cannot find collab_orgs.
            cypher_query += 'AND collab_orgs.value STARTS WITH $collab_orgs '
        else:
            # We are to find collaborations from start_orgs with only one organization.
            # This query is much more efficient.
            cypher_query += 'AND collab_orgs.value=$collab_orgs '

    cypher_query += cypher_return_clause + ' '

    if query_params['max_nr_items'] > 0:
        cypher_query += 'LIMIT $max_nr_items '
    # print(cypher_query)

    # This call returns a list of Records and not a list of Nodes, which
    # is logical since it needs to be able to store any type of result.
    records, summary, _ = graph.execute_query(cypher_query,
                                              org_abbr=org_abbr,
                                              **query_params,
                                              database_=ricgraph_databasename())
    cypher_print_resultsummary(summary=summary,
                               print_cypher_query=False,
                               nr_results=len(records))
    if len(records) == 0:
        return []
    else:
        return records


def find_collab_orgs_matrix(query_params: QueryParams) -> DataFrame | None:
    """Find collaborating organizations, starting from start_orgs,
    for a certain research result.
    Collaborations are defined as nodes connected as follows:
    (start_orgs)-[]->(persroot1)-[]->(researchresult)
       -[]->(persroot2)-[]->(collab_orgs).
    This function returns the collaboration count.

    :param query_params: Parameters related to the query passed in the URL.
     - start_orgs: the organization(s) to start with. This may be
       a substring, then a STARTS WITH is used in the cypher query.
     - collab_orgs: if specified, only return organization(s) that
       collaborate with start_orgs. If empty '', return any organization(s)
       that start_orgs collaborate with.
     - category_list: if specified, only return collaborations
       for this research result category. If not, return all collaborations,
       regardless of the research result category.
       The value can be both a string containing one category, or
       a list of categories.
     - max_nr_items: return at most this number of collaborating organizations,
       0 = return all collaborating organizations,
    :return: a DataFrame where the rows correspond to start_orgs,
      the columns to collab_orgs, and the cell value to the number
      of collaborations between start_orgs and collab_orgs.
    """
    researchresult_category_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                                     item='researchresult_category_active')
    if len(query_params['category_list']) == 0:
        query_params['category_list'] = researchresult_category_active.copy()

    cypher_return_clause = 'RETURN '
    cypher_return_clause += '  start_orgs.value AS start_orgs, '
    cypher_return_clause += '  collab_orgs.value AS collab_orgs, '
    cypher_return_clause += '  COUNT(DISTINCT researchresult._key) AS count_researchresult_category '

    records_list = find_collabs_cypher(query_params=query_params,
                                       cypher_return_clause=cypher_return_clause)
    if len(records_list) == 0:
        return None

    result = DataFrame(records_list,
                       columns=['start_orgs', 'collab_orgs',
                                'count_researchresult_category'])
    if result is None or result.empty:
        # Should not happen, apparently something went wrong.
        return None
    result = result.pivot_table(index='start_orgs',
                                columns='collab_orgs',
                                values='count_researchresult_category',
                                fill_value=0)
    result = result.convert_dtypes(convert_integer=True)
    # Sort row index (axis=0) case-insensitively, then sort column index (axis=1) case-insensitively
    result = result.sort_index(axis=0, key=lambda x: x.str.lower()).sort_index(axis=1, key=lambda x: x.str.lower())

    # Label the top left cell with the category_list used to get this result.
    # Make sure it is a list.
    query_params['category_list'].sort(key=lambda s: s.lower())
    result.index.name = str(query_params['category_list'])
    return result


def find_collab_orgs_persons_results(query_params: QueryParams,
                                     mode: str = 'return_researchresults') -> list:
    """Find collaborating organizations, starting from start_orgs,
    for a certain research result.
    Collaborations are defined as nodes connected as follows:
    (start_orgs)-[]->(persroot1)-[]->(researchresult)
       -[]->(persroot2)-[]->(collab_orgs).
    This function returns either start org persons, collab org persons,
    or research results, depending on 'mode'.

    :param query_params: Parameters related to the query passed in the URL.
     - start_orgs: the organization(s) to start with. This may be
       a substring, then a STARTS WITH is used in the cypher query.
     - collab_orgs: if specified, only return organization(s) that
       collaborate with start_orgs. If empty '', return any organization(s)
       that start_orgs collaborate with.
     - category_list: if specified, only return collaborations
       for this research result category. If not, return all collaborations,
       regardless of the research result category.
       The value can be both a string containing one category, or
       a list of categories.
     - max_nr_items: return at most this number of collaborating organizations,
       0 = return all collaborating organizations,
    :param mode: one of the following:
      - mode = 'return_researchresults': return the research results.
      - mode = 'return_startorg_persons': return the person-roots from start_orgs.
      - mode = 'return_collaborg_persons': return the person-roots from collab_orgs.
    :return: for all modes: a list of nodes, or [] if nothing found.
    """
    researchresult_category_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                                     item='researchresult_category_active')
    if len(query_params['category_list']) == 0:
        query_params['category_list'] = researchresult_category_active.copy()

    if mode != 'return_researchresults' \
       and mode != 'return_startorg_persons' \
       and mode != 'return_collaborg_persons':
        print('find_collab_orgs_persons_resuls(): unknown type for mode "' + mode + '", exiting...')
        exit(1)

    cypher_return_clause = 'RETURN DISTINCT '
    if mode == 'return_researchresults':
        cypher_return_clause += 'researchresult '
    if mode == 'return_startorg_persons':
        cypher_return_clause += 'persroot1 '
    if mode == 'return_collaborg_persons':
        cypher_return_clause += 'persroot2 '
    cypher_return_clause += 'AS node '

    records_list = find_collabs_cypher(query_params=query_params,
                                       cypher_return_clause=cypher_return_clause)
    if len(records_list) == 0:
        return []
    nodes_list = convert_cypher_recordslist_to_nodeslist(records_list=records_list)
    return nodes_list


def create_researchresult_histogram_cypher(query_params: QueryParams) -> Tuple[dict, dict, dict, dict, dict]:
    """Compute histograms for name, category, year, license, and access.
    To do this, we need a node that is connected to a 'person-root' node.
    The histograms are computed from the research results neighbors of that
    person-root node.

    :param query_params: Parameters related to the query passed in the URL.
    :return: five dicts that represent the five histograms.
    """
    # Note that this function is similar to find_organization_additional_info_cypher(),
    # except that this function returns a dict and the other a list with nodes.
    # It might be possible to integrate them, but it might also be clearer.
    # to have two different versions.
    graph = get_ricgraph_explorer_global(name='graph')
    if graph is None:
        print('create_researchresult_histogram_cypher(): Error: graph has not been initialized or opened.')
        return {}, {}, {}, {}, {}
    if (message := check_valid_year(year_first=query_params['year_first'],
                                    year_last=query_params['year_last'])) != '':
        print(message)
        return {}, {}, {}, {}, {}

    cypher_query = 'MATCH (node:RicgraphNode)'
    cypher_query += '-[]->(persroot:RicgraphPersonRoot)'
    cypher_query += '-[]->(researchresult:RicgraphResearchResult) '
    cypher_query += 'WHERE node._key = $key '
    if len(query_params['name_list']) > 0:
        cypher_query += 'AND researchresult.name IN $name_list '
    if len(query_params['category_list']) > 0:
        cypher_query += 'AND researchresult.category IN $category_list '
    if query_params['year_first'] != '':
        cypher_query += 'AND researchresult.year >= $year_first '
    if query_params['year_last'] != '':
        cypher_query += 'AND researchresult.year <= $year_last '
    if len(query_params['license']) > 0:
        cypher_query += 'AND researchresult.license IN $license '
    if len(query_params['access']) > 0:
        cypher_query += 'AND researchresult.access IN $access '
    cypher_query += 'WITH DISTINCT researchresult '
    cypher_query += 'UNWIND ['
    cypher_query += '{prop: "name", name: researchresult.name}, '
    cypher_query += '{prop: "category", name: researchresult.category}, '
    cypher_query += '{prop: "year", name: researchresult.year}, '
    cypher_query += '{prop: "license", name: researchresult.license}, '
    cypher_query += '{prop: "access", name: researchresult.access}'
    cypher_query += '] AS row '
    cypher_query += 'WITH row.prop AS property, row.name AS name '
    cypher_query += 'WHERE name IS NOT NULL '
    cypher_query += 'RETURN property, name, COUNT(*) AS value '
    cypher_query += 'ORDER BY property, value DESC, name '
    # print(cypher_query)

    # This call returns a list of Records and not a list of Nodes, which
    # is logical since it needs to be able to store any type of result.
    records, _, _ = graph.execute_query(query_=cypher_query,
                                        #node_element_id=node.element_id,
                                        **query_params,
                                        database_=ricgraph_databasename())

    name_histogram = {}
    category_histogram = {}
    year_histogram = {}
    license_histogram = {}
    access_histogram = {}
    for record in records:
        if record['property'] == 'name':
            name_histogram[record['name']] = record['value']
        if record['property'] == 'category':
            category_histogram[record['name']] = record['value']
        if record['property'] == 'year':
            if record['name'] != RICGRAPH_UNKNOWN:
                # Note that we have only research results.
                # For years, we do not want RICGRAPH_UNKNOWN value.
                # This is also done in ricgraph_explorer_init.py,
                # function collect_ricgraph_nodeinfo().
                year_histogram[record['name']] = record['value']
        if record['property'] == 'license':
            license_histogram[record['name']] = record['value']
        if record['property'] == 'access':
            access_histogram[record['name']] = record['value']

    return (name_histogram, category_histogram,
            year_histogram, license_histogram, access_histogram)
