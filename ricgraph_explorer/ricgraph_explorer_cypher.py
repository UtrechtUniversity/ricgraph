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
# Extended Rik D.T. Janssen, February, September 2023 to May 2025.
#
# ########################################################################


from typing import Tuple
from neo4j.graph import Node
from ricgraph import (get_personroot_node, get_all_neighbor_nodes,
                      ricgraph_database, ricgraph_databasename)
from ricgraph_explorer_constants import MAX_ITEMS


def find_person_share_resouts_cypher(parent_node: Node,
                                     category_want_list: list = None,
                                     category_dontwant_list: list = None,
                                     max_nr_items: str = str(MAX_ITEMS)) -> list:
    """ For documentation, see find_person_share_resouts().

    :param parent_node:
    :param category_want_list:
    :param category_dontwant_list:
    :param max_nr_items:
    :return:
    """
    import ricgraph_explorer as rcg_exp
    rcg_exp.get_all_globals_from_app_context()

    if category_want_list is None:
        category_want_list = []
    if category_dontwant_list is None:
        category_dontwant_list = []

    # By using the following statement we can start with both a node and its person-root node.
    personroot_node = get_personroot_node(node=parent_node)
    cypher_query = 'MATCH (startnode_personroot:RicgraphNode)-[]'
    cypher_query += '->(neighbor:RicgraphNode)-[]->(neighbor_personroot:RicgraphNode)'
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
    # cypher_query += 'id(neighbor_personroot)<>id(startnode_personroot) '
    if ricgraph_database() == 'neo4j':
        cypher_query += 'elementId(neighbor_personroot)<>elementId(startnode_personroot) '
    else:
        cypher_query += 'id(neighbor_personroot)<>id(startnode_personroot) '
    cypher_query += 'RETURN DISTINCT neighbor_personroot '
    if int(max_nr_items) > 0:
        cypher_query += 'LIMIT ' + max_nr_items
    # print(cypher_query)

    # Note that the RETURN (as in RETURN DISTINCT *) also has all intermediate results, such
    # as the common research results (in 'neighbor'). We don't use them at the moment.
    cypher_result, _, _ = rcg_exp.graph.execute_query(cypher_query,
                                                      startnode_personroot_element_id=personroot_node.element_id,
                                                      category_want_list=category_want_list,
                                                      category_dontwant_list=category_dontwant_list,
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
    """ For documentation, see find_person_organization_collaborations_cypher().

    :param parent_node:
    :param max_nr_items:
    :return:
    """
    import ricgraph_explorer as rcg_exp
    rcg_exp.get_all_globals_from_app_context()

    # By using the following statement we can start with both a node and its person-root node.
    personroot_node = get_personroot_node(node=parent_node)
    cypher_query = 'MATCH (startnode_personroot:RicgraphNode)-[]'
    cypher_query += '->(neighbor:RicgraphNode)-[]->(neighbor_personroot:RicgraphNode)-[]'
    cypher_query += '->(neighbor_organization:RicgraphNode) '
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
        cypher_query += 'LIMIT ' + max_nr_items
    # print(cypher_query)
    # Note that the RETURN (as in RETURN DISTINCT *) also has all intermediate results, such
    # as the collaborating researchers (in 'neighbor_personroot') and the common research
    # results (in 'neighbor'). We don't use them at the moment.

    # Note that 'cypher_result' will contain _all_ organizations that 'parent_node'
    # collaborates with, very probably also the organizations this person works for.
    cypher_result, _, _ = rcg_exp.graph.execute_query(cypher_query,
                                                      startnode_personroot_element_id=personroot_node.element_id,
                                                      resout_types_all=rcg_exp.resout_types_all,
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

    :param parent_node:
    :param name_list:
    :param category_list:
    :param source_system:
    :param max_nr_items:
    :return:
    """
    import ricgraph_explorer as rcg_exp
    rcg_exp.get_all_globals_from_app_context()

    if name_list is None:
        name_list = []
    if category_list is None:
        category_list = []

    second_neighbor_name_list = ''
    second_neighbor_category_list = ''
    if len(name_list) > 0:
        second_neighbor_name_list = '["'
        second_neighbor_name_list += '", "'.join(str(item) for item in name_list)
        second_neighbor_name_list += '"]'
    if len(category_list) > 0:
        second_neighbor_category_list = '["'
        second_neighbor_category_list += '", "'.join(str(item) for item in category_list)
        second_neighbor_category_list += '"]'

    # Prepare and execute Cypher query.
    cypher_query = 'MATCH (node)-[]->(neighbor) '
    if ricgraph_database() == 'neo4j':
        cypher_query += 'WHERE elementId(node)=$node_element_id '
    else:
        cypher_query += 'WHERE id(node)=toInteger($node_element_id) '
    cypher_query += ' AND neighbor.name = "person-root" '

    cypher_query += 'MATCH (neighbor)-[]->(second_neighbor) '
    if len(name_list) > 0 or len(category_list) > 0 or source_system != '':
        cypher_query += 'WHERE '
    if len(name_list) > 0:
        cypher_query += 'second_neighbor.name IN ' + second_neighbor_name_list + ' '
    if len(name_list) > 0 and len(category_list) > 0:
        cypher_query += 'AND '
    if len(category_list) > 0:
        cypher_query += 'second_neighbor.category IN ' + second_neighbor_category_list + ' '
    if source_system != '':
        if len(name_list) > 0 or len(category_list) > 0:
            cypher_query += 'AND '
        cypher_query += 'NOT "' + source_system + '" IN second_neighbor._source '
    cypher_query += 'RETURN DISTINCT second_neighbor, count(second_neighbor) as count_second_neighbor '
    cypher_query += 'ORDER BY count_second_neighbor DESC '
    if int(max_nr_items) > 0:
        cypher_query += 'LIMIT ' + max_nr_items
    # print(cypher_query)
    cypher_result, _, _ = rcg_exp.graph.execute_query(cypher_query,
                                                      node_element_id=parent_node.element_id,
                                                      database_=ricgraph_databasename())
    if len(cypher_result) == 0:
        return []
    else:
        return cypher_result
