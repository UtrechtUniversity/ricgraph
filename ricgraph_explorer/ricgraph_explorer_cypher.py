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
# Extended Rik D.T. Janssen, October 2025.
#
# ########################################################################


from typing import Tuple, Union
from pandas import DataFrame
from neo4j.graph import Node
from ricgraph import (ROTYPE_PUBLICATION,
                      read_node,
                      get_personroot_node, get_all_neighbor_nodes,
                      ricgraph_database, ricgraph_databasename,
                      convert_cypher_recordslist_to_nodeslist,
                      extract_organization_abbreviation)
from ricgraph_explorer_constants import MAX_ITEMS
from ricgraph_explorer_init import get_ricgraph_explorer_global


def find_person_share_resouts_cypher(parent_node: Node,
                                     category_want_list: list = None,
                                     category_dontwant_list: list = None,
                                     max_nr_items: str = str(MAX_ITEMS)) -> list:
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
        print('\nfind_person_share_resouts_cypher(): Error: graph has not been initialized or opened.\n\n')
        return []

    if category_want_list is None:
        category_want_list = []
    if category_dontwant_list is None:
        category_dontwant_list = []

    # By using the following statement we can start with both a node and its person-root node.
    personroot_node = get_personroot_node(node=parent_node)
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
    if int(max_nr_items) > 0:
        cypher_query += 'LIMIT $max_nr_items '
    # print(cypher_query)

    # Note that the RETURN (as in RETURN DISTINCT *) also has all intermediate results, such
    # as the common research results (in 'neighbor'). We don't use them at the moment.
    cypher_result, _, _ = graph.execute_query(cypher_query,
                                              startnode_personroot_element_id=personroot_node.element_id,
                                              category_want_list=category_want_list,
                                              category_dontwant_list=category_dontwant_list,
                                              max_nr_items=int(max_nr_items),
                                              database_=ricgraph_databasename())

    # Convert 'cypher_result' to a list of Node's.
    # If we happened to use 'result_transformer_=Result.data' in execute_query(), we would
    # have gotten a list of dicts, which messes up 'nodes_cache_nodelink'.
    connected_persons = []
    for neighbor_node in cypher_result:
        if len(neighbor_node) == 0:
            continue
        person = neighbor_node['neighbor_personroot']
        connected_persons.append(person)

    return connected_persons


def find_person_organization_collaborations_cypher(parent_node: Node,
                                                   max_nr_items: str = str(MAX_ITEMS)) -> Tuple[list, list]:
    """ For documentation, see find_person_organization_collaborations().
    This is the cypher functionality for that function.

    :param parent_node:
    :param max_nr_items:
    :return:
    """
    graph = get_ricgraph_explorer_global(name='graph')
    if graph is None:
        print('\nfind_person_organization_collaborations_cypher(): Error: graph has not been initialized or opened.\n\n')
        return [], []

    # By using the following statement we can start with both a node and its person-root node.
    personroot_node = get_personroot_node(node=parent_node)
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
    cypher_query += 'neighbor.category IN $resout_types_all AND '
    cypher_query += 'neighbor_personroot.name="person-root" AND '
    if ricgraph_database() == 'neo4j':
        cypher_query += 'elementId(neighbor_personroot)<>elementId(startnode_personroot) AND '
    else:
        cypher_query += 'id(neighbor_personroot)<>id(startnode_personroot) AND '
    cypher_query += 'neighbor_organization.category="organization" '
    cypher_query += 'RETURN DISTINCT neighbor_organization '
    if int(max_nr_items) > 0:
        cypher_query += 'LIMIT $max_nr_items '
    # print(cypher_query)
    # Note that the RETURN (as in RETURN DISTINCT *) also has all intermediate results, such
    # as the collaborating researchers (in 'neighbor_personroot') and the common research
    # results (in 'neighbor'). We don't use them at the moment.

    # Note that 'cypher_result' will contain _all_ organizations that 'parent_node'
    # collaborates with, very probably also the organizations this person works for.
    resout_types_all = get_ricgraph_explorer_global(name='resout_types_all')
    cypher_result, _, _ = graph.execute_query(cypher_query,
                                              startnode_personroot_element_id=personroot_node.element_id,
                                              resout_types_all=resout_types_all,
                                              max_nr_items=int(max_nr_items),
                                              database_=ricgraph_databasename())

    # Get the organizations from 'parent_node'.
    personroot_node = get_personroot_node(node=parent_node)
    personroot_node_organizations = get_all_neighbor_nodes(node=personroot_node,
                                                           category_want='organization')
    # Now get the organizations that 'parent_node' collaborates with, excluding
    # this person's own organizations. Note that the types of 'cypher_result'
    # and 'personroot_node_organizations' are not the same.
    personroot_node_organizations_key = []
    for organization in personroot_node_organizations:
        personroot_node_organizations_key.append(organization['_key'])

    # Convert 'cypher_result' to a list of Node's.
    # If we happened to use 'result_transformer_=Result.data' in execute_query(), we would
    # have gotten a list of dicts, which messes up 'nodes_cache_nodelink'.
    collaborating_organizations = []
    for organization_node in cypher_result:
        if len(organization_node) == 0:
            continue
        organization = organization_node['neighbor_organization']
        organization_key = organization['_key']
        if organization_key not in personroot_node_organizations_key:
            collaborating_organizations.append(organization)

    return personroot_node_organizations, collaborating_organizations


def find_organization_additional_info_cypher(parent_node: Node,
                                             name_list: list = None,
                                             category_list: list = None,
                                             source_system: str = '',
                                             max_nr_items: str = str(MAX_ITEMS)) -> list:
    """For documentation, see find_organization_additional_info().
    This is the cypher functionality for that function.

    :param parent_node:
    :param name_list:
    :param category_list:
    :param source_system:
    :param max_nr_items:
    :return:
    """
    graph = get_ricgraph_explorer_global(name='graph')
    if graph is None:
        print('\nfind_organization_additional_info_cypher(): Error: graph has not been initialized or opened.\n\n')
        return []

    if name_list is None:
        name_list = []
    if category_list is None:
        category_list = []

    # Prepare and execute Cypher query.
    cypher_query = 'MATCH (node:RicgraphNode)-[]->(neighbor:RicgraphNode) '
    if ricgraph_database() == 'neo4j':
        cypher_query += 'WHERE elementId(node)=$node_element_id '
    else:
        cypher_query += 'WHERE id(node)=toInteger($node_element_id) '
    cypher_query += ' AND neighbor.name = "person-root" '

    cypher_query += 'MATCH (neighbor:RicgraphNode)-[]->(second_neighbor:RicgraphNode) '
    if len(name_list) > 0 or len(category_list) > 0 or source_system != '':
        cypher_query += 'WHERE '
    if len(name_list) > 0:
        cypher_query += 'second_neighbor.name IN $name_list '
    if len(name_list) > 0 and len(category_list) > 0:
        cypher_query += 'AND '
    if len(category_list) > 0:
        cypher_query += 'second_neighbor.category IN $category_list '
    if source_system != '':
        if len(name_list) > 0 or len(category_list) > 0:
            cypher_query += 'AND '
        cypher_query += 'NOT "' + source_system + '" IN second_neighbor._source '
    cypher_query += 'RETURN DISTINCT second_neighbor, count(second_neighbor) as count_second_neighbor '
    cypher_query += 'ORDER BY count_second_neighbor DESC '
    if int(max_nr_items) > 0:
        cypher_query += 'LIMIT $max_nr_items '
    # print(cypher_query)
    cypher_result, _, _ = graph.execute_query(cypher_query,
                                              node_element_id=parent_node.element_id,
                                              name_list=name_list,
                                              category_list=category_list,
                                              max_nr_items=int(max_nr_items),
                                              database_=ricgraph_databasename())
    if len(cypher_result) == 0:
        return []
    else:
        return cypher_result


def find_collabs_cypher(start_organizations: str,
                        collab_organizations: str = '',
                        research_result_category: Union[str, list] = '',
                        cypher_return_clause: str = '',
                        max_nr_nodes: int = 0) -> list:
    """Find collaborations, starting from start_organizations,
    for a certain research result.
    Collaborations are defined as nodes connected as follows:
    (start_organizations)-[]->(persroot1)-[]->(research_result)
       -[]->(persroot2)-[]->(collab_organizations).
    This function is used for several purposes, but for all of those purposes
    only the RETURN part is different. That is why the RETURN is passed
    as 'cypher_return_clause'.

    :param start_organizations: the organization(s) to start with. This may be
      a substring, then a STARTS WITH is used in the cypher query.
    :param collab_organizations: if specified, only return organization(s) that
      collaborate with start_organizations. If empty '', return any organization(s)
      that start_organizations collaborate with.
    :param research_result_category: if specified, only return collaborations
      for this research result category. If not, return all collaborations,
      regardless of the research result category.
      The value can be both a string containing one category, or
      a list of categories.
    :param cypher_return_clause: the RETURN part of the cypher query that is
      constructed in this function.
    :param max_nr_nodes: return at most this number of collaborating organizations,
      0 = return all collaborating organizations,
    :return: a list of nodes conforming to the cypher query, or [] if nothing found.
    """
    orgs_with_hierarchies = get_ricgraph_explorer_global('orgs_with_hierarchies')
    graph = get_ricgraph_explorer_global(name='graph')
    if graph is None:
        print('\nfind_collab_orgs_cypher(): Error: graph has not been initialized or opened.\n\n')
        return []

    if cypher_return_clause == '':
        print('find_collab_orgs_cypher(): Error, you have not specified a cypher RETURN clause, exiting.')
        exit(1)

    print('Finding collaborations')
    if collab_organizations == '':
        print('  from "' + start_organizations + '" to "all"')
    else:
        print('  from "' + start_organizations + '" to "' + collab_organizations + '"')
    if isinstance(research_result_category, str):
        print('  using research result category "' + research_result_category + '".')
    elif isinstance(research_result_category, list):
        if sorted(research_result_category) == sorted(ROTYPE_PUBLICATION):
            print('  using research result category (meta category) "publication".')
        else:
            print('  using research result category "' + str(research_result_category) + '".')
    else:
        print('find_collab_orgs_cypher(): Error, unexpected type.')
        return []

    cypher_query = 'MATCH (start_orgs:RicgraphNode)'
    cypher_query += '-[]->(persroot1:RicgraphNode)'
    cypher_query += '-[]->(research_result:RicgraphNode)'
    cypher_query += '-[]->(persroot2:RicgraphNode)'
    cypher_query += '-[]->(collab_orgs:RicgraphNode) '

    cypher_query += 'WHERE start_orgs.name="ORGANIZATION_NAME" '
    if read_node(name='ORGANIZATION_NAME', value=start_organizations) is None:
        # We are to find collaborating organizations of a series of organizations,
        # because we cannot find start_organizations.
        cypher_query += 'AND start_orgs.value STARTS WITH $start_orgs '
    else:
        # We are to find collaborating organizations of only one organization.
        # This query is much more efficient.
        cypher_query += 'AND start_orgs.value=$start_orgs '

    if isinstance(research_result_category, str):
        if research_result_category != '':
            # Restrict the result to collaborations of a certain research result category.
            cypher_query += 'AND research_result.category=$research_result_category '
    elif isinstance(research_result_category, list):
        if len(research_result_category) > 0:
            # Restrict the result to collaborations of a certain research result category.
            cypher_query += 'AND research_result.category IN $research_result_category '
    else:
        print('find_collab_orgs_cypher(): unknown type for research_result_category "'
              + str(research_result_category) + '".')
        exit(1)

    cypher_query += 'AND persroot1.name="person-root" '
    cypher_query += 'AND persroot2.name="person-root" '
    cypher_query += 'AND persroot1._key<>persroot2._key '
    cypher_query += 'AND start_orgs._key<>collab_orgs._key '
    cypher_query += 'AND collab_orgs.name="ORGANIZATION_NAME" '

    org_abbr = ''
    if collab_organizations == '':
        # If we are to match any organization...
        org_abbr = extract_organization_abbreviation(org_name=start_organizations)
        if org_abbr in orgs_with_hierarchies['org_abbreviation'].values:
            # ... and 'start_organization' has sub-organizations (which is specified
            # in orgs_with_hierarchies), do not match any (sub-)organizations of it in
            # 'collab_organizations'.
            # Please also read the design decision at org_collaborations_diagram().
            cypher_query += 'AND NOT collab_orgs.value STARTS WITH $org_abbr '
    else:
        # We are to find collaborations limited to certain organization(s).
        if read_node(name='ORGANIZATION_NAME', value=collab_organizations) is None:
            # We are to find collaborations from start_organizations with multiple organizations,
            # because we cannot find collab_organizations.
            cypher_query += 'AND collab_orgs.value STARTS WITH $collab_orgs '
        else:
            # We are to find collaborations from start_organizations with only one organization.
            # This query is much more efficient.
            cypher_query += 'AND collab_orgs.value=$collab_orgs '

    cypher_query += cypher_return_clause + ' '

    if max_nr_nodes > 0:
        cypher_query += 'LIMIT $max_nr_nodes '
    # print(cypher_query)

    # This call returns a list of Records and not a list of Nodes, which
    # is logical since it needs to be able to store any type of result.
    cypher_result, _, _ = graph.execute_query(cypher_query,
                                              start_orgs=start_organizations,
                                              collab_orgs=collab_organizations,
                                              research_result_category=research_result_category,
                                              org_abbr=org_abbr,
                                              max_nr_nodes=max_nr_nodes,
                                              database_=ricgraph_databasename())

    if len(cypher_result) == 0:
        return []
    else:
        return cypher_result


def find_collab_orgs_matrix(start_organizations: str,
                            collab_organizations: str = '',
                            research_result_category: Union[str, list] = '',
                            max_nr_nodes: int = 0) -> Union[DataFrame, None]:
    """Find collaborating organizations, starting from start_organizations,
    for a certain research result.
    Collaborations are defined as nodes connected as follows:
    (start_organizations)-[]->(persroot1)-[]->(research_result)
       -[]->(persroot2)-[]->(collab_organizations).
    This function returns the collaboration count.

    :param start_organizations: the organization(s) to start with. This may be
      a substring, then a STARTS WITH is used in the cypher query.
    :param collab_organizations: if specified, only return organization(s) that
      collaborate with start_organizations. If empty '', return any organization(s)
      that start_organizations collaborate with.
    :param research_result_category: if specified, only return collaborations
      for this research result category. If not, return all collaborations,
      regardless of the research result category.
      The value can be both a string containing one category, or
      a list of categories.
    :param max_nr_nodes: return at most this number of collaborating organizations,
      0 = return all collaborating organizations,
    :return: a DataFrame where the rows correspond to start_organizations,
      the columns to collab_organizations, and the cell value to the number
      of collaborations between start_organizations and collab_organizations.
    """
    resout_types_all = get_ricgraph_explorer_global(name='resout_types_all')

    if isinstance(research_result_category, str) and research_result_category == '':
        research_result_category = resout_types_all.copy()
    if isinstance(research_result_category, list) and len(research_result_category) == 0:
        research_result_category = resout_types_all.copy()

    cypher_return_clause = 'RETURN '
    cypher_return_clause += '  start_orgs.value AS start_orgs, '
    cypher_return_clause += '  collab_orgs.value AS collab_orgs, '
    cypher_return_clause += '  COUNT(DISTINCT research_result._key) as count_research_result_category '

    records_list = find_collabs_cypher(start_organizations=start_organizations,
                                       collab_organizations=collab_organizations,
                                       research_result_category=research_result_category,
                                       cypher_return_clause=cypher_return_clause,
                                       max_nr_nodes=max_nr_nodes)
    if len(records_list) == 0:
        return None

    result = DataFrame(records_list,
                       columns=['start_orgs', 'collab_orgs',
                                'count_research_result_category'])
    if result is None or result.empty:
        # Should not happen, apparently something went wrong.
        return None
    result = result.pivot_table(index='start_orgs',
                                columns='collab_orgs',
                                values='count_research_result_category',
                                fill_value=0)
    result = result.convert_dtypes(convert_integer=True)
    # Sort row index (axis=0) case-insensitively, then sort column index (axis=1) case-insensitively
    result = result.sort_index(axis=0, key=lambda x: x.str.lower()).sort_index(axis=1, key=lambda x: x.str.lower())

    # Label the top left cell with the research_result_category used to get this result.
    # Make sure it is a list.
    if isinstance(research_result_category, str):
        result.index.name = str([research_result_category])
    else:
        research_result_category.sort(key=lambda s: s.lower())
        result.index.name = str(research_result_category)
    return result


def find_collab_orgs_persons_results(start_organizations: str,
                                     collab_organizations: str = '',
                                     research_result_category: Union[str, list] = '',
                                     mode: str = 'return_research_results',
                                     max_nr_nodes: int = 0) -> list:
    """Find collaborating organizations, starting from start_organizations,
    for a certain research result.
    Collaborations are defined as nodes connected as follows:
    (start_organizations)-[]->(persroot1)-[]->(research_result)
       -[]->(persroot2)-[]->(collab_organizations).
    This function returns either start org persons, collab org persons,
    or research results, depending on 'mode'.

    :param start_organizations: the organization(s) to start with. This may be
      a substring, then a STARTS WITH is used in the cypher query.
    :param collab_organizations: if specified, only return organization(s) that
      collaborate with start_organizations. If empty '', return any organization(s)
      that start_organizations collaborate with.
    :param research_result_category: if specified, only return collaborations
      for this research result category. If not, return all collaborations,
      regardless of the research result category.
      The value can be both a string containing one category, or
      a list of categories.
    :param mode: one of the following:
      - mode = 'return_research_results': return the research results.
      - mode = 'return_startorg_persons': return the person-roots from start_organizations.
      - mode = 'return_collaborg_persons': return the person-roots from collab_organizations.
    :param max_nr_nodes: return at most this number of collaborating organizations,
      0 = return all collaborating organizations,
    :return: for all modes: a list of nodes, or [] if nothing found.
    """
    resout_types_all = get_ricgraph_explorer_global(name='resout_types_all')

    if isinstance(research_result_category, str) and research_result_category == '':
        research_result_category = resout_types_all.copy()
    if isinstance(research_result_category, list) and len(research_result_category) == 0:
        research_result_category = resout_types_all.copy()

    if mode != 'return_research_results' \
       and mode != 'return_startorg_persons' \
       and mode != 'return_collaborg_persons':
        print('find_collab_orgs_persons_resuls(): unknown type for mode "' + mode + '", exiting...')
        exit(1)

    cypher_return_clause = 'RETURN DISTINCT '
    if mode == 'return_research_results':
        cypher_return_clause += 'research_result '
    if mode == 'return_startorg_persons':
        cypher_return_clause += 'persroot1 '
    if mode == 'return_collaborg_persons':
        cypher_return_clause += 'persroot2 '
    cypher_return_clause += 'AS node '

    records_list = find_collabs_cypher(start_organizations=start_organizations,
                                       collab_organizations=collab_organizations,
                                       research_result_category=research_result_category,
                                       cypher_return_clause=cypher_return_clause,
                                       max_nr_nodes=max_nr_nodes)
    if len(records_list) == 0:
        return []
    nodes_list = convert_cypher_recordslist_to_nodeslist(records_list=records_list)
    return nodes_list
