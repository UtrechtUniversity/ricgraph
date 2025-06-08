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
# Ricgraph Cypher related functions.
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, December 2022.
# Updated Rik D.T. Janssen, February, March, September to December 2023.
# Updated Rik D.T. Janssen, February to June, September to December  2024.
# Updated Rik D.T. Janssen, January to June 2025.
#
# ########################################################################


from pandas import DataFrame
from typing import Union
from neo4j import GraphDatabase, Driver, Result
from neo4j.graph import Node
from .ricgraph_constants import A_LARGE_NUMBER
from .ricgraph_utils import *
from .ricgraph_cache import (nodes_cache_key_id_create, nodes_cache_key_id_read,
                             nodes_cache_key_id_delete_id, nodes_cache_key_id_empty)


# The graph. '_graph = None' will not work.
global _graph

# These counters are used to count the number of accesses to the
# graph database backend.
_graphdb_nr_creates = 0
_graphdb_nr_reads = 0
_graphdb_nr_updates = 0
_graphdb_nr_deletes = 0


# ##############################################################################
# Modification for Python module neo4j.
# ##############################################################################
def node_eq(self, other):
    """Modified __eq__ method for Python module neo4j.

    The __eq__ method of class Node does not work as expected (as of April 2024).
    Two Nodes are supposed to be equal if their Node.element_id's are equal.

    I would like to be able to test if a 'node' of type Node is in a list called
    'mylist' with an 'if' statement like this:
    'if node in mylist ...' or 'if node not in mylist ...',
    but it does not work: even if Nodes are in that list, the 'if' fails.
    I could have made my own class and extended it with an __eq__ method, but
    I choose this hack. It is called a 'Monkey patch': A Monkey patch is a piece
    of Python code which extends or modifies other code at runtime
    (typically at startup).

    :return: True on equality, or False if not.
    """
    return isinstance(other, Node) and self.element_id == other.element_id


# Modified __eq__ method for Python module neo4j (also see above).
Node.__eq__ = node_eq


# ##############################################################################
# Ricgraph general Cypher functions.
# ##############################################################################
# Note the use of WHERE clauses below. Some of them uses the function elementId(),
# which does a _direct_ lookup for a node with that id. That is the fastest way possible,
# compared to a WHERE clause on node['_key'], which is a search.
# To observe this difference, prefix a Cypher query with PROFILE, e.g.:
# PROFILE MATCH (n) WHERE elementId(n)=[a string here] RETURN *
#
# Read: https://neo4j.com/docs/cypher-manual/current/functions/scalar/#functions-elementid
# https://neo4j.com/docs/cypher-manual/current/planning-and-tuning/operators/operators-detail/#query-plan-node-by-elementid-seek
#
# [May 6, 2024] Note however, that memgraph on does not have elementId() but only id():
# https://memgraph.com/docs/querying/differences-in-cypher-implementations.
# ##############################################################################
def open_ricgraph() -> Driver:
    """Open Ricgraph.

    :return: graph that has been opened.
    """
    global _graph

    print('Opening Ricgraph.\n')
    try:
        _graph = GraphDatabase.driver(_GRAPHDB_URL,
                                      auth=(_GRAPHDB_USER, _GRAPHDB_PASSWORD))
        _graph.verify_connectivity()
    except Exception as e:
        print('open_ricgraph(): An exception occurred. Name: ' + type(e).__name__ + ',')
        print('  error message: ' + str(e) + '.')
        print('Error opening graph database backend using these parameters:')
        print('_GRAPHDB_URL: ' + _GRAPHDB_URL)
        print('_GRAPHDB_DATABASENAME: ' + ricgraph_databasename())
        print('_GRAPHDB_USER: ' + _GRAPHDB_USER)
        print('_GRAPHDB_PASSWORD: [see file ' + get_ricgraph_ini_file() + ']')
        print('\nAre these parameters correct and did you start your graph database backend "' + _GRAPHDB + '"?')
        print('Exiting.')
        exit(1)

    return _graph


def close_ricgraph() -> None:
    """Close Ricgraph.
    """
    global _graph

    if _graph is None:
        print('\nclose_ricgraph(): Error: graph has not been initialized or opened.\n\n')
        return

    print('Closing Ricgraph.\n')
    _graph.close()
    return


def ricgraph_database() -> str:
    """Return the name of the Ricgraph database backend.
    """
    return _GRAPHDB


def ricgraph_databasename() -> str:
    """Return the name of the database in the Ricgraph database backend.
    """
    return _GRAPHDB_DATABASENAME


def empty_ricgraph(answer: str = '') -> None:
    """Empty Ricgraph and create new indexes. Side effect: indexes are deleted and created.

    :param answer: prefilled answer whether the user wants to empty Ricgraph.
      'yes': Ricgraph will be emptied, no questions asked;
      'no': Ricgraph will not be emptied, no questions asked;
      any other answer: the user will be asked whether to empty Ricgraph.
    :return: None.
    """
    global _graph

    if answer != 'yes' and answer != 'no':
        print('empty_ricgraph(): invalid answer "' + answer + '" on the question')
        print('to empty Ricgraph, exiting.')
        exit(1)

    if answer == 'no':
        print('empty_ricgraph(): Ricgraph will not be emptied.\n')
        return

    print('empty_ricgraph(): Ricgraph will be emptied.\n')
    graphdb_name = ricgraph_database()
    graphdb_databasename = ricgraph_databasename()

    # Delete the database and start over again.
    # Sometimes the following statement fails with Neo4j Desktop graph database backend
    # if there are many nodes, see e.g.
    # https://stackoverflow.com/questions/23310114/how-to-reset-clear-delete-neo4j-database.
    # Apparently, the community edition of Neo4j does not have a
    # "CREATE OR REPLACE DATABASE customers" command.
    print('Deleting all nodes and edges in Ricgraph...\n')
    _graph.execute_query('MATCH (node) DETACH DELETE node', database_=graphdb_databasename)

    if graphdb_name == 'neo4j':
        # Do not use TEXT indexes, use RANGE indexes, these are much faster during harvesting
        # (but they do not support a CONTAINS substring search which is being used for a broad search
        # in read_all_nodes()). The RANGE index is the default in Neo4j. More info:
        # https://neo4j.com/docs/cypher-manual/current/indexes/search-performance-indexes/managing-indexes
        # [Jan. 2023] The graph database backend Neo4j can have at most 3 indexes.
        # [June 5, 2024] This is not true anymore. I use 4 indexes.
        _graph.execute_query('DROP INDEX KeyIndex IF EXISTS', database_=graphdb_databasename)
        _graph.execute_query('DROP INDEX NameIndex IF EXISTS', database_=graphdb_databasename)
        _graph.execute_query('DROP INDEX CategoryIndex IF EXISTS', database_=graphdb_databasename)
        _graph.execute_query('DROP INDEX ValueIndex IF EXISTS', database_=graphdb_databasename)

        print('Creating indexes...')
        _graph.execute_query('CREATE INDEX KeyIndex IF NOT EXISTS FOR (node:RicgraphNode) ON (node._key)',
                             database_=graphdb_databasename)
        _graph.execute_query('CREATE INDEX NameIndex IF NOT EXISTS FOR (node:RicgraphNode) ON (node.name)',
                             database_=graphdb_databasename)
        _graph.execute_query('CREATE INDEX CategoryIndex IF NOT EXISTS FOR (node:RicgraphNode) ON (node.category)',
                             database_=graphdb_databasename)
        _graph.execute_query('CREATE INDEX ValueIndex IF NOT EXISTS FOR (node:RicgraphNode) ON (node.value)',
                             database_=graphdb_databasename)

        print('These indexes have been created:')
        records, summary, keys = _graph.execute_query('SHOW INDEXES',
                                                      database_=graphdb_databasename)
        index_table = DataFrame(data=records, columns=keys)
        print(index_table.to_string(index=False))
        print('')
    elif graphdb_name == 'memgraph':
        # For Memgraph, we need to create indexes in the following way, otherwise we get an
        # 'Index manipulation not allowed in multicommand transactions'
        # error. We should use implicit (or auto-commit) transactions.
        # See https://memgraph.com/docs/client-libraries/python#transaction-management.
        with _graph.session(database=_GRAPHDB) as session:
            # These also work in case they do not exist.
            session.run('DROP INDEX ON :RicgraphNode;')
            session.run('DROP INDEX ON :RicgraphNode(_key);')
            session.run('DROP INDEX ON :RicgraphNode(name);')
            session.run('DROP INDEX ON :RicgraphNode(category);')
            session.run('DROP INDEX ON :RicgraphNode(value);')

            print('Creating indexes...')
            session.run('CREATE INDEX ON :RicgraphNode;')
            session.run('CREATE INDEX ON :RicgraphNode(_key);')
            session.run('CREATE INDEX ON :RicgraphNode(name);')
            session.run('CREATE INDEX ON :RicgraphNode(category);')
            session.run('CREATE INDEX ON :RicgraphNode(value);')

            print('These indexes have been created:')
            for index_line in session.run('SHOW INDEX INFO;'):
                print(index_line)
            print('')

        # session.close() is done automatically because of 'with'.
    else:
        print('empty_ricgraph(): Unknown graph database backend "' + graphdb_name + '".')
        print('Exiting.')
        exit(1)
    return


def ricgraph_nr_nodes() -> int:
    """Count the number of nodes in Ricgraph.

    :return: the number of nodes, or -1 on error.
    """
    global _graph

    if _graph is None:
        print('\nricgraph_nr_nodes(): Error: graph has not been initialized or opened.\n\n')
        return -1

    cypher_query = 'MATCH () RETURN count(*) AS count'
    result = _graph.execute_query(cypher_query,
                                  result_transformer_=Result.data,
                                  database_=ricgraph_databasename())
    if len(result) == 0:
        return -1
    result = result[0]
    if 'count' not in result:
        return -1
    result = int(result['count'])
    return result


def ricgraph_nr_edges() -> int:
    """Count the number of edges in Ricgraph.

    :return: the number of edges, or -1 on error.
    """
    global _graph

    if _graph is None:
        print('\nricgraph_nr_edges(): Error: graph has not been initialized or opened.\n\n')
        return -1

    cypher_query = 'MATCH ()-[r]->() RETURN count(r) AS count'
    result = _graph.execute_query(cypher_query,
                                  result_transformer_=Result.data,
                                  database_=ricgraph_databasename())
    if len(result) == 0:
        return -1
    result = result[0]
    if 'count' not in result:
        return -1
    result = int(result['count'])
    return result


def ricgraph_nr_edges_of_node(node_element_id: str) -> int:
    """Count the number of edges in Ricgraph of a given node.

    :param node_element_id: the element_id of the node.
    :return: the number of nodes, or -1 on error.
    """
    global _graph

    if _graph is None:
        print('\nricgraph_nr_edges_of_node(): Error: graph has not been initialized or opened.\n\n')
        return -1

    cypher_query = 'MATCH (node:RicgraphNode)-[r]->() '
    if ricgraph_database() == 'neo4j':
        cypher_query += 'WHERE elementId(node)=$node_element_id '
    else:
        cypher_query += 'WHERE id(node)=toInteger($node_element_id) '
    cypher_query += 'RETURN count(r) AS count'

    result = _graph.execute_query(cypher_query,
                                  node_element_id=node_element_id,
                                  result_transformer_=Result.data,
                                  database_=ricgraph_databasename())
    if len(result) == 0:
        return -1
    result = result[0]
    if 'count' not in result:
        return -1
    result = int(result['count'])
    return result


# ##############################################################################
# Ricgraph graph database CRUD related functions.
# ##############################################################################
def cypher_create_node(node_properties: dict) -> Union[Node, None]:
    """
    Create a node in the graph database.
    Create means: the node will be created, regardless if it is already
    present or not. No test for presence of a node is done.
    The properties and their values in 'node_properties' will be added
    as properties & values of the node.
    The 'name', 'category', and 'value' properties are expected to be
    in 'node_properties'.

    :param node_properties: the properties of the node.
    :return: the node updated, or None on error.
    """
    global _graph, _graphdb_nr_creates

    if _graph is None:
        print('\ncypher_create_node(): Error: graph has not been initialized or opened.\n\n')
        return None

    # There are several methods for creating a node in the graph database.
    # This would be an alternative, but it seems to use more memory than the
    # one used now, according to 'PROFILE <cypher query>'.
    # cypher_query = 'CREATE (node:RicgraphNode) SET node=$node_properties ' [etc.]
    cypher_query = 'CREATE (node:RicgraphNode $node_properties) RETURN node'

    # print('cypher_create_node(): cypher_query: ' + cypher_query)
    # print('                      node_properties: ' + str(node_properties))

    nodes = _graph.execute_query(cypher_query,
                                 node_properties=node_properties,
                                 result_transformer_=Result.value,
                                 database_=ricgraph_databasename())
    _graphdb_nr_creates += 1
    if len(nodes) == 0:
        return None
    else:
        node = nodes[0]
        nodes_cache_key_id_create(key=node['_key'], elementid=node.element_id)
        return node


def cypher_read_node(name: str, value: str) -> Union[Node, None]:
    """
    Read a node from the graph database.

    :param name: the 'name' of the node to find.
    :param value: the 'value' of the node to find.
    :return: the node found, or None if not present.
    """
    global _graph, _graphdb_nr_reads

    if _graph is None:
        print('\ncypher_read_node(): Error: graph has not been initialized or opened.\n\n')
        return None

    node_in_cache = False
    key = create_ricgraph_key(name=name, value=value)
    cypher_query = 'MATCH (node:RicgraphNode) '
    if (node_element_id := nodes_cache_key_id_read(key=key)) != '':
        node_in_cache = True
        if ricgraph_database() == 'neo4j':
            cypher_query += 'WHERE elementId(node)=$node_element_id '
        else:
            cypher_query += 'WHERE id(node)=toInteger($node_element_id) '
        cypher_query += 'RETURN node'
        nodes = _graph.execute_query(cypher_query,
                                     node_element_id=node_element_id,
                                     result_transformer_=Result.value,
                                     database_=ricgraph_databasename())
    else:
        cypher_query += 'WHERE (node._key=$node_key) '
        cypher_query += 'RETURN node'
        nodes = _graph.execute_query(cypher_query,
                                     node_key=key,
                                     result_transformer_=Result.value,
                                     database_=ricgraph_databasename())
    _graphdb_nr_reads += 1
    if len(nodes) == 0:
        return None
    else:
        node = nodes[0]
        if not node_in_cache:
            nodes_cache_key_id_create(key=node['_key'], elementid=node.element_id)
        return node


def cypher_find_nodes(name: str, category: str, value: str,
                      name_is_exact_match: bool = True,
                      value_is_exact_match: bool = True,
                      max_nr_nodes: int = 0) -> list:
    """
    Find nodes in the graph database.

    :param name: the 'name' of the node to find.
    :param category: the 'category' of the node to find.
    :param value: the 'value' of the node to find.
    :param name_is_exact_match: if True, then do an exact match search
      on field 'name', if False, then do a case-insensitive match.
      Note that a case-insensitive match is more expensive.
    :param value_is_exact_match: if True, then do an exact match search
      on field 'value', if False, then do a case-insensitive match.
      Note that a case-insensitive match is more expensive.
    :param max_nr_nodes: return at most this number of nodes, 0 = all nodes.
    :return: a list of the nodes found, or [] if nothing found.
    """
    global _graph, _graphdb_nr_reads

    if _graph is None:
        print('\ncypher_find_nodes(): Error: graph has not been initialized or opened.\n\n')
        return []

    cypher_query = 'MATCH (node:RicgraphNode) WHERE '
    if name != '':
        if name_is_exact_match:
            cypher_query += '(node.name="' + name + '") AND '
        else:
            cypher_query += '(toLower(node.name) CONTAINS toLower("' + name + '")) AND '
    if category != '':
        cypher_query += '(node.category="' + category + '") AND '
    if value != '':
        # Value may contain special characters.
        if value_is_exact_match:
            # Exact match search.
            cypher_query += '(node.value=$node_value) AND '
        else:
            # Case-insensitive search.
            cypher_query += '(toLower(node.value) CONTAINS toLower($node_value)) AND '

    # Remove last 'AND ', is of length -4.
    cypher_query = cypher_query[:-4]
    cypher_query += 'RETURN node '

    if max_nr_nodes > 0:
        cypher_query += 'LIMIT ' + str(max_nr_nodes)
    # print(cypher_query)

    if value != '':
        # Value may contain special characters.
        nodes = _graph.execute_query(cypher_query,
                                     node_value=value,
                                     result_transformer_=Result.value,
                                     database_=ricgraph_databasename())
    else:
        nodes = _graph.execute_query(cypher_query,
                                     result_transformer_=Result.value,
                                     database_=ricgraph_databasename())

    nr_nodes = len(nodes)
    # Unsure what to count here, this seems reasonable. '+ 1' for first node.
    _graphdb_nr_reads += nr_nodes + 1
    if nr_nodes == 0:
        return []
    else:
        return nodes


def cypher_delete_node(node_element_id: str) -> None:
    """Delete a node in the graph database.
    If it has any edges, these will also be deleted.

    :param node_element_id: the element_id of the node.
    :return: None.
    """
    global _graph, _graphdb_nr_deletes

    if _graph is None:
        print('\ncypher_delete_node(): Error: graph has not been initialized or opened.\n\n')
        return

    cypher_query = 'MATCH (node:RicgraphNode) '
    if ricgraph_database() == 'neo4j':
        cypher_query += 'WHERE elementId(node)=$node_element_id '
    else:
        cypher_query += 'WHERE id(node)=toInteger($node_element_id) '
    cypher_query += 'DETACH DELETE node'
    _graph.execute_query(cypher_query,
                         node_element_id=node_element_id,
                         result_transformer_=Result.value,
                         database_=ricgraph_databasename())

    nr_edges = ricgraph_nr_edges_of_node(node_element_id=node_element_id)
    _graphdb_nr_deletes += 1 + nr_edges      # '1' for node, add all of its edges.
    nodes_cache_key_id_delete_id(elementid=node_element_id)
    return


def cypher_update_node_properties(node_element_id: str, node_properties: dict) -> Union[Node, None]:
    """
    Update node properties in a node in the graph database.
    If the node is not present, nothing will happen.
    Only the properties and their values in 'node_properties' will be changed (if
    a property is present in the node) or added (if the property is not present).
    All other properties (i.e. not specified properties in 'node_properties')
    will be left as they are.

    :param node_element_id: the element_id of the node.
    :param node_properties: the properties of the node.
    :return: the node updated, or None on error.
    """
    global _graph, _graphdb_nr_reads, _graphdb_nr_updates

    if _graph is None:
        print('\ncypher_update_node_properties(): Error: graph has not been initialized or opened.\n\n')
        return None

    cypher_query = 'MATCH (node:RicgraphNode) '
    if ricgraph_database() == 'neo4j':
        cypher_query += 'WHERE elementId(node)=$node_element_id '
    else:
        cypher_query += 'WHERE id(node)=toInteger($node_element_id) '
    cypher_query += 'SET node+=$node_properties RETURN node'

    # print('cypher_update_node_properties(): node_element_id: ' + str(node_element_id) +
    #       ', cypher_query: ' + cypher_query)
    # print('                     node_properties: ' + str(node_properties))

    nodes = _graph.execute_query(cypher_query,
                                 node_element_id=node_element_id,
                                 node_properties=node_properties,
                                 result_transformer_=Result.value,
                                 database_=ricgraph_databasename())
    _graphdb_nr_reads += 1
    _graphdb_nr_updates += 1
    if len(nodes) == 0:
        return None
    else:
        node = nodes[0]
        if 'name' in node_properties or 'value' in node_properties:
            # 'name' or 'value' has changed and thus '_key' has changed.
            nodes_cache_key_id_delete_id(elementid=node_element_id)
            nodes_cache_key_id_create(key=node['_key'], elementid=node.element_id)
        return node


def cypher_merge_nodes(node_merge_from_element_id: str,
                       node_merge_to_element_id: str,
                       node_merge_to_properties: dict) -> Union[Node, None]:
    """Merge two nodes in the graph database.
    The neighbors of 'node_merge_from' will be merged to node 'node_merge_to'
    and 'node_merge_from' will be deleted.
    The node properties in 'node_merge_to' will be set according to
    'node_merge_to_properties'.

    Only the properties and their values in 'node_properties' will be changed (if
    a property is present in the node) or added (if the property is not present).
    All other properties (i.e. not specified properties in 'node_properties')
    will be left as they are.

    :param node_merge_from_element_id: the element_id of node_merge_from.
    :param node_merge_to_element_id: the element_id of node_merge_to.
    :param node_merge_to_properties: the properties of node_merge_to.
    :return: the node updated, or None on error.
    """
    global _graph, _graphdb_nr_reads, _graphdb_nr_updates

    if _graph is None:
        print('\ncypher_merge_nodes(): Error: graph has not been initialized or opened.\n\n')
        return None

    graphdb_name = ricgraph_database()

    if node_merge_from_element_id == node_merge_to_element_id:
        # We only update node properties.
        node = cypher_update_node_properties(node_element_id=node_merge_to_element_id,
                                             node_properties=node_merge_to_properties)
        return node

    cypher_query = 'MATCH (node_from:RicgraphNode) '
    if graphdb_name == 'neo4j':
        cypher_query += 'WHERE elementId(node_from)=$node_merge_from_element_id '
    else:
        cypher_query += 'WHERE id(node_from)=toInteger($node_merge_from_element_id) '
    cypher_query += 'MATCH (node_to:RicgraphNode) '
    if graphdb_name == 'neo4j':
        cypher_query += 'WHERE elementId(node_to)=$node_merge_to_element_id '
    else:
        cypher_query += 'WHERE id(node_to)=toInteger($node_merge_to_element_id) '

    cypher_query += 'SET node_to+=$node_merge_to_properties '
    cypher_query += 'WITH node_from, node_to '
    # Only test for an edge in one direction, that is sufficient.
    cypher_query += 'MATCH (node_from:RicgraphNode)-[:LINKS_TO]->(neighbor_node:RicgraphNode) '
    # Prevent creating a self-relationship on node_to.
    cypher_query += 'WHERE node_to <> neighbor_node '
    cypher_query += 'MERGE (node_to)-[:LINKS_TO]->(neighbor_node) '
    cypher_query += 'MERGE (node_to)<-[:LINKS_TO]-(neighbor_node) '
    cypher_query += 'DETACH DELETE node_from '
    cypher_query += 'RETURN node_to'

    # print('cypher_merge_nodes(): node_merge_from_element_id: ' + str(node_merge_from_element_id))
    # print('                      node_merge_to_element_id: ' + str(node_merge_to_element_id))
    # print('                      node_merge_to_properties: ' + str(node_merge_to_properties))
    # print('                      cypher_query: ' + cypher_query)

    nodes = _graph.execute_query(cypher_query,
                                 node_merge_from_element_id=node_merge_from_element_id,
                                 node_merge_to_element_id=node_merge_to_element_id,
                                 node_merge_to_properties=node_merge_to_properties,
                                 result_transformer_=Result.value,
                                 database_=ricgraph_databasename())

    if len(nodes) == 0:
        # If merge_node_from does not have neighbors, len(nodes) will be 0.
        # Also, it will not have been deleted. The merge has been done.
        # Do another Cypher query to be sure it is gone.
        cypher_delete_node(node_element_id=node_merge_from_element_id)
        node_merge_to_properties['_history'].append('Merged two nodes of which the merged from did not have neighbors.')
        node = cypher_update_node_properties(node_element_id=node_merge_to_element_id,
                                             node_properties=node_merge_to_properties)
        return node

    nr_edges = ricgraph_nr_edges_of_node(node_element_id=node_merge_to_element_id)
    _graphdb_nr_reads += 2 * nr_edges        # Approximation: edges are in two directions.
    _graphdb_nr_updates += 2 * nr_edges      # Approximation: edges are in two directions.

    # Too much may have happened, no idea how to efficiently update nodes_cache_key_id, just empty it.
    nodes_cache_key_id_empty()
    return nodes[0]


def cypher_create_edge_if_not_exists(left_node_element_id: str, right_node_element_id: str) -> None:
    """Create an edge between two nodes, but only if the edge does not exist.

    :param left_node_element_id: the element_id of the left node.
    :param right_node_element_id: the element_id of the right node.
    :return: None.
    """
    global _graph, _graphdb_nr_reads, _graphdb_nr_updates

    if _graph is None:
        print('\ncypher_create_edge_if_not_exists(): Error: graph has not been initialized or opened.\n\n')
        return

    graphdb_name = ricgraph_database()

    # There are several methods for getting the nodes in the graph database.
    # This one takes the most time.
    # It amounts to ?? database hits according to 'PROFILE <cypher query>', using 'AllNodesScan'.
    # cypher_query = 'MATCH (left_node {ID:' + str(left_node.element_id) + '}) ' [etc.]
    # The next one takes average time.
    # It amounts to 23 database hits according to 'PROFILE', using 'AllNodesScan'.
    # cypher_query = 'MATCH (left_node) WHERE left_node._key="' + str(left_node['_key']) + '" ' [etc.]
    # The next one is the fastest.
    # It amounts to 1 database hits according to 'PROFILE' using 'NodeByIdSeek'.
    cypher_query = 'MATCH (left_node:RicgraphNode) '
    if graphdb_name == 'neo4j':
        cypher_query += 'WHERE elementId(left_node)=$left_node_element_id '
    else:
        cypher_query += 'WHERE id(left_node)=toInteger($left_node_element_id) '
    cypher_query += 'MATCH (right_node:RicgraphNode) '
    if graphdb_name == 'neo4j':
        cypher_query += 'WHERE elementId(right_node)=$right_node_element_id '
    else:
        cypher_query += 'WHERE id(right_node)=toInteger($right_node_element_id) '

    # We could use 'CREATE', but then we may get multiple edges for the same direction.
    # cypher_query += 'CREATE (left_node)-[:LINKS_TO]->(right_node), ' [etc.]
    # A MERGE is more expensive since it first checks for presence of the edge.
    cypher_query += 'MERGE (left_node)-[:LINKS_TO]->(right_node) '
    cypher_query += 'MERGE (left_node)<-[:LINKS_TO]-(right_node) '

    # print('cypher_create_edge_if_not_exists(): left_node_id: ' + str(left_node_id) + ', right_node_id: '
    #       + str(right_node_id) + ', cypher_query: ' + cypher_query)

    _graph.execute_query(cypher_query,
                         left_node_element_id=left_node_element_id,
                         right_node_element_id=right_node_element_id,
                         database_=ricgraph_databasename())
    _graphdb_nr_reads += 2             # one for left_node, one for right_node
    _graphdb_nr_updates += 2           # one for ->, one for <-.
    return


# ##############################################################################
# General graph database Ricgraph functions.
# ##############################################################################
def graphdb_nr_accesses_reset() -> None:
    """Reset the counters that are used to count the number of accesses
    to the graph database backend.

    :return: None.
    """
    global _graphdb_nr_creates, _graphdb_nr_reads
    global _graphdb_nr_updates, _graphdb_nr_deletes

    _graphdb_nr_creates = 0
    _graphdb_nr_reads = 0
    _graphdb_nr_updates = 0
    _graphdb_nr_deletes = 0
    return


def graphdb_nr_accesses_print() -> None:
    """Print the values of the counters for the number of accesses to
    the graph database backend.

    :return: None.
    """
    # These counters are used to count the number of accesses to the graph database.
    global _graphdb_nr_creates, _graphdb_nr_reads, _graphdb_nr_updates, _graphdb_nr_deletes

    graphdb_total_accesses = _graphdb_nr_creates + _graphdb_nr_reads
    graphdb_total_accesses += (2 * _graphdb_nr_updates) + _graphdb_nr_deletes
    nr_nodes = ricgraph_nr_nodes()
    nr_edges = ricgraph_nr_edges()

    print('\n')
    print('These are the number of accesses to the graph database backend at ' + datetimestamp() + ':')
    print('- total number of creates:  {:>10}'.format(_graphdb_nr_creates))
    print('- total number of reads:    {:>10}'.format(_graphdb_nr_reads))
    print('- total number of updates:  {:>10}'.format(_graphdb_nr_updates))
    print('- total number of deletes:  {:>10}'.format(_graphdb_nr_deletes))
    print('- total number of accesses: {:>10}'.format(graphdb_total_accesses))
    print('Please note that for the total number of accesses, an "update" counts twice: '
          + 'one for the read and one for the update of the value.')
    print('\n')
    print('These are the number of nodes and edges in Ricgraph:')
    print('- total number of nodes: {:>8}'.format(nr_nodes))
    print('- total number of edges: {:>8}'.format(nr_edges))
    print('\n')
    return


def read_all_values_of_property(node_property: str = '') -> list:
    """Read all the values of a certain property.

    :param node_property: the property to find all values:
       'name': all different name properties.
       'category': all different category properties.
       '_source': all different _source properties.
       'name_personal': all different name properties that are personal identifiers.
    :return: a sorted list with all the values, or empty list on error.
    """
    global _graph

    if _graph is None:
        print('\nread_all_values_of_property(): Error: graph has not been initialized or opened.')
        return []

    if ricgraph_nr_nodes() == 0:
        print('\nread_all_values_of_property(): Warning: graph is empty.')
        return []

    if node_property != 'name' \
       and node_property != 'name_personal' \
       and node_property != 'category' \
       and node_property != '_source':
        print('\nread_all_values_of_property(): Error: function does not work for property "'
              + node_property + '".\n\n')
        return []

    cypher_query = 'MATCH (node:RicgraphNode) '
    if node_property == 'name_personal':
        # Note that the comment property of 'person-root' contains FULL_NAMEs,
        # so it is also a name property that is a personal identifier.
        cypher_query += 'WHERE node.category = "person" '
        cypher_query += 'RETURN DISTINCT node.name AS entry '
    else:
        # This UNWIND is only necessary for node_property = _source. It 'flattens' the list.
        # For other values of node_property it does not really matter.
        cypher_query += 'UNWIND node.' + node_property + ' AS value '
        cypher_query += 'RETURN DISTINCT value AS entry '

    # If we happened to use 'result_transformer_=Result.data' in execute_query(), we would
    # have gotten a list of dicts instead of a list.
    result, _, _ = _graph.execute_query(cypher_query,
                                        database_=ricgraph_databasename())
    if len(result) == 0:
        return []
    result_list = [record['entry'] for record in result]

    # We need 'key' to do a case insenstive search.
    result_list_sorted = sorted(result_list, key=str.lower)
    return result_list_sorted


def get_all_neighbor_nodes(node: Node,
                           name_want: Union[str, list] = '',
                           name_dontwant: Union[str, list] = '',
                           category_want: Union[str, list] = '',
                           category_dontwant: Union[str, list] = '',
                           max_nr_neighbor_nodes: int = 0) -> list:
    """Get all the neighbors of 'node' in a list.
    You can restrict the nodes returned by specifying one or more of the
    other parameters. If more than one is specified, the result is an AND.

    :param node: the node we need neighbors from.
    :param name_want: either a string which indicates that we only want neighbor
      nodes where the property 'name' is equal to 'name_want'
      (e.g. 'ORCID'),
      or a list containing several node names, indicating
      that we want all neighbor nodes where the property 'name' equals
      one of the names in the list 'name_want'
      (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty (empty string), return all nodes.
    :param name_dontwant: similar, but for property 'name' and nodes we don't want.
      If empty (empty string), all nodes are 'wanted'.
    :param category_want: similar to 'name_want', but now for the property 'category'.
    :param category_dontwant: similar, but for property 'category' and nodes we don't want.
    :param max_nr_neighbor_nodes: return at most this number of nodes, 0 = all nodes.
    :return: the list of neighboring nodes satisfying all these criteria, or
      empty list if nothing found.
    """
    global _graph
    global _graphdb_nr_reads

    if _graph is None:
        print('\nget_all_neighbor_nodes(): Error: graph has not been initialized or opened.\n\n')
        return []

    if node is None:
        return []

    if name_want is None:
        name_want = []
    if name_dontwant is None:
        name_dontwant = []
    if category_want is None:
        category_want = []
    if category_dontwant is None:
        category_dontwant = []

    cypher_query = 'MATCH (node:RicgraphNode)-[]->(neighbor:RicgraphNode) '
    if ricgraph_database() == 'neo4j':
        cypher_query += 'WHERE (elementId(node)=$node_element_id) '
    else:
        cypher_query += 'WHERE (id(node)=toInteger($node_element_id)) '

    nr_of_not_clauses = 0
    if isinstance(name_want, str):
        if name_want != '':
            cypher_query += 'AND (neighbor.name IN ["' + name_want + '"]) '
    else:
        if len(name_want) > 0:
            string_list = '["' + '", "'.join(str(item) for item in name_want) + '"]'
            cypher_query += 'AND (neighbor.name IN ' + string_list + ') '

    if isinstance(name_dontwant, str):
        if name_dontwant != '':
            cypher_query += 'AND (NOT neighbor.name IN ["' + name_dontwant + '"]) '
            nr_of_not_clauses += 1
    else:
        if len(name_dontwant) > 0:
            string_list = '["' + '", "'.join(str(item) for item in name_dontwant) + '"]'
            cypher_query += 'AND (NOT neighbor.name IN ' + string_list + ') '
            nr_of_not_clauses += 1

    if isinstance(category_want, str):
        if category_want != '':
            cypher_query += 'AND (neighbor.category IN ["' + category_want + '"]) '
    else:
        if len(category_want) > 0:
            string_list = '["' + '", "'.join(str(item) for item in category_want) + '"]'
            cypher_query += 'AND (neighbor.category IN ' + string_list + ') '

    if isinstance(category_dontwant, str):
        if category_dontwant != '':
            cypher_query += 'AND (NOT neighbor.category IN ["' + category_dontwant + '"]) '
            nr_of_not_clauses += 1
    else:
        if len(category_dontwant) > 0:
            string_list = '["' + '", "'.join(str(item) for item in category_dontwant) + '"]'
            cypher_query += 'AND (NOT neighbor.category IN ' + string_list + ') '
            nr_of_not_clauses += 1

    if nr_of_not_clauses >= 2:
        # This is a special case in which the Cypher query produces unexpected results.
        neighbor_nodes = get_all_neighbor_nodes_loop(node=node,
                                                     name_want=name_want,
                                                     name_dontwant=name_dontwant,
                                                     category_want=category_want,
                                                     category_dontwant=category_dontwant,
                                                     max_nr_neighbor_nodes=max_nr_neighbor_nodes)
        return neighbor_nodes

    cypher_query += 'RETURN DISTINCT neighbor '
    if max_nr_neighbor_nodes > 0:
        cypher_query += 'LIMIT ' + str(max_nr_neighbor_nodes)
    # print(cypher_query)

    neighbor_nodes = _graph.execute_query(cypher_query,
                                          node_element_id=node.element_id,
                                          result_transformer_=Result.value,
                                          database_=ricgraph_databasename())
    nr_neighbors = len(neighbor_nodes)
    # Unsure what to count here, this seems reasonable. '+ 1' for 'node'.
    _graphdb_nr_reads += nr_neighbors + 1
    if nr_neighbors == 0:
        return []
    else:
        return neighbor_nodes


def get_all_neighbor_nodes_loop(node: Node,
                                name_want: Union[str, list] = '',
                                name_dontwant: Union[str, list] = '',
                                category_want: Union[str, list] = '',
                                category_dontwant: Union[str, list] = '',
                                max_nr_neighbor_nodes: int = 0) -> list:
    """Get all the neighbors of 'node' in a list.
    You can restrict the nodes returned by specifying one or more of the
    other parameters. If more than one is specified, the result is an AND.

    This is the same function as get_all_neighbor_nodes() but it is much slower
    since it uses a loop. We need this in case
    len(name_dontwant_list) > 0 and len(category_dontwant_list) > 0.

    :param node: the node we need neighbors from.
    :param name_want: either a string which indicates that we only want neighbor
      nodes where the property 'name' is equal to 'name_want'
      (e.g. 'ORCID'),
      or a list containing several node names, indicating
      that we want all neighbor nodes where the property 'name' equals
      one of the names in the list 'name_want'
      (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty (empty string), return all nodes.
    :param name_dontwant: similar, but for property 'name' and nodes we don't want.
      If empty (empty string), all nodes are 'wanted'.
    :param category_want: similar to 'name_want', but now for the property 'category'.
    :param category_dontwant: similar, but for property 'category' and nodes we don't want.
    :param max_nr_neighbor_nodes: return at most this number of nodes, 0 = all nodes.
    :return: the list of neighboring nodes satisfying all these criteria.
    """
    global _graph
    global _graphdb_nr_reads

    if _graph is None:
        print('\nget_all_neighbor_nodes_loop(): Error: graph has not been initialized or opened.\n\n')
        return []

    if node is None:
        return []

    candidate_neighbor_nodes = get_all_neighbor_nodes(node=node)
    if len(candidate_neighbor_nodes) == 0:
        return []

    # If 'name_want' etc. are strings, convert them to lists.
    if isinstance(name_want, str):
        if name_want == '':
            name_want_list = []
        else:
            name_want_list = [name_want]
    else:
        name_want_list = name_want

    if isinstance(name_dontwant, str):
        if name_dontwant == '':
            name_dontwant_list = []
        else:
            name_dontwant_list = [name_dontwant]
    else:
        name_dontwant_list = name_dontwant

    if isinstance(category_want, str):
        if category_want == '':
            category_want_list = []
        else:
            category_want_list = [category_want]
    else:
        category_want_list = category_want

    if isinstance(category_dontwant, str):
        if category_dontwant == '':
            category_dontwant_list = []
        else:
            category_dontwant_list = [category_dontwant]
    else:
        category_dontwant_list = category_dontwant

    count = 0
    all_nodes = A_LARGE_NUMBER
    if max_nr_neighbor_nodes == 0:
        max_nr_neighbor_nodes = all_nodes
    neighbor_nodes = []
    for neighbor in candidate_neighbor_nodes:
        if count >= max_nr_neighbor_nodes:
            break
        if node == neighbor:
            continue
        if neighbor['name'] in name_dontwant_list:
            continue
        if neighbor['category'] in category_dontwant_list:
            continue
        if len(name_want) == 0 and len(category_want) == 0:
            neighbor_nodes.append(neighbor)
            count += 1
            continue
        if neighbor['name'] in name_want_list \
                and neighbor['category'] in category_want_list:
            neighbor_nodes.append(neighbor)
            count += 1
            continue
        if neighbor['name'] in name_want_list and len(category_want_list) == 0:
            neighbor_nodes.append(neighbor)
            count += 1
            continue
        if len(name_want_list) == 0 and neighbor['category'] in category_want_list:
            neighbor_nodes.append(neighbor)
            count += 1
            continue
        # Any other next_node we do not want.

    # Unsure what to count here, this seems reasonable. '+ 1' for 'node'.
    _graphdb_nr_reads += len(neighbor_nodes) + 1
    return neighbor_nodes


# ############################################
# ################### main ###################
# ############################################
# This will be executed on module initialization
_GRAPHDB = get_configfile_key(section='GraphDB', key='graphdb')
_GRAPHDB_HOSTNAME = get_configfile_key(section='GraphDB', key='graphdb_hostname')
_GRAPHDB_DATABASENAME = get_configfile_key(section='GraphDB', key='graphdb_databasename')
_GRAPHDB_USER = get_configfile_key(section='GraphDB', key='graphdb_user')
_GRAPHDB_PASSWORD = get_configfile_key(section='GraphDB', key='graphdb_password')
_GRAPHDB_SCHEME = get_configfile_key(section='GraphDB', key='graphdb_scheme')
_GRAPHDB_PORT = get_configfile_key(section='GraphDB', key='graphdb_port')
if _GRAPHDB == '' or _GRAPHDB_HOSTNAME == '' or _GRAPHDB_DATABASENAME == '' \
   or _GRAPHDB_USER == '' or _GRAPHDB_PASSWORD == '' \
   or _GRAPHDB_SCHEME == '' or _GRAPHDB_PORT == '':
    print('Ricgraph initialization: error, one or more of the GraphDB parameters')
    print('  not existing or empty in Ricgraph ini')
    print('  file "' + get_ricgraph_ini_file() + '", exiting.')
    exit(1)

_GRAPHDB_URL = '{scheme}://{hostname}:{port}'.format(scheme=_GRAPHDB_SCHEME,
                                                     hostname=_GRAPHDB_HOSTNAME,
                                                     port=_GRAPHDB_PORT)
