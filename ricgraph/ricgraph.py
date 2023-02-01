# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
# 
# Copyright (c) 2023 Rik D.T. Janssen
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
# This file is the main file for Ricgraph.
# Original version Rik D.T. Janssen, December 2022.
# Updated Rik D.T. Janssen, February 2023.
#
# ########################################################################


"""Ricgraph - Research in context graph.

This is Ricgraph - Research in context graph, a graph structure with nodes and edges
to represent information (as properties in the nodes)
and their relations (the edges).

Ricgraph uses Neo4j as graph database, https://neo4j.com.
Neo4j only allows directed graphs, so Ricgraph is a directed graph.
They have several products. Their free products are:

- Neo4j Desktop (https://neo4j.com/download-center/#desktop);

- Neo4j Community Edition (https://neo4j.com/download-center/#community).

Neo4j Desktop includes Bloom, which allows exploring the graph in a more
intuitive way. Community Edition allows only Cypher queries.
Therefore, Neo4j Desktop is recommended.

To be able to access neo4j from python, py2neo is used (https://py2neo.org).

Ricgraph can be extended for other brands of graph databases
by changing minor bits of the code.

All nodes have the following properties:

- name: name of the node, e.g. ISNI, ORCID, DOI, etc.

- category: category of the node,
  e.g. person, person-root, book, journal article, dataset, etc.

- value: value of the node.

- _key: key value of the node, not to be modified by the user.

- _history: list of history events of the node, not to be modified by the user.

Additional properties for nodes can be added by changing an entry in the initialization file.
In the default configuration of Ricgraph, the following properties are included:

- comment: comment for a node, can be anything that is thought to be useful.

- url_main: main URL for a node, pointing to e.g. the corresponding ISNI, ORCID or DOI
  record on the web.

- url_other: other URL for a node, pointing to e.g. the originating record in a source system.

- history_event: an event to be added to the _history list.
"""

# Additional properties for nodes are in ALLOWED_RICGRAPH_PROPERTIES
# (make sure 'history_event' is last) which is read in __main__

import os.path
from datetime import datetime
import csv
import uuid
import json
import urllib.request
from urllib.error import HTTPError
from typing import Union
import configparser
from py2neo import *
from py2neo.matching import *
import numpy
import pandas

LINKS_TO = Relationship.type('LINKS_TO')
RICGRAPH_INI_FILE = '../ricgraph.ini'
global _graph


def open_ricgraph() -> Graph:
    """Open Ricgraph.

    :return: graph that has been opened.
    """
    global _graph

    print('Opening ricgraph...\n')
    _graph = Graph(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return _graph


def close_ricgraph() -> None:
    """Close Ricgraph.
    """
    global _graph

    print('Closing ricgraph...\n')
    # Seems to be done automatically, so no actual call.
    # In this way it is nicely symmetrical to open_ricgraph().
    return


def empty_ricgraph() -> None:
    """Empty Ricgraph and create new indexes. Side effect: indexes are deleted and created.
    """
    global _graph

    user_input = input('Do you really want to empty Ricgraph (yes/no)? ')
    if user_input.lower() != 'yes':
        print('Ricgraph has not been emptied, exiting...\n')
        exit(1)

    # Sometimes the following statement fails if there are many nodes, see e.g.
    # https://stackoverflow.com/questions/23310114/how-to-reset-clear-delete-neo4j-database.
    # If this happens, delete all Neo4j Desktop files and run the AppImage again to fully
    # start over again.
    # Apparently, the community edition of Neo4j does not have a
    # "CREATE OR REPLACE DATABASE customers" command.
    print('Deleting all nodes and edges in Ricgraph...\n')
    _graph.delete_all()                     # Equivalent to "MATCH (a) DETACH DELETE a".

    # More info on indexes: https://neo4j.com/docs/cypher-manual/current/indexes-for-search-performance.
    # Don't use the call from py2neo, since it generates a B-tree index and that does not seem to exist
    # anymore according to that webpage: "The B-tree index type has been replaced by more specific index
    # types (Range, Point, and Text)."
    # Indexes will be generated on the fly.
    # If I understand correctly there can be at most 3 indexes, while I would like to have 4.
    # I decide not use a ValueIndex
    _graph.run('DROP INDEX KeyIndex IF EXISTS')
    _graph.run('DROP INDEX NameIndex IF EXISTS')
    _graph.run('DROP INDEX CategoryIndex IF EXISTS')
    # graph.run('DROP INDEX ValueIndex IF EXISTS')

    print('Creating indexes...')
    _graph.run('CREATE TEXT INDEX KeyIndex IF NOT EXISTS FOR(n: RCGNode) ON(n._key)')
    _graph.run('CREATE TEXT INDEX NameIndex IF NOT EXISTS FOR(n: RCGNode) ON(n.name)')
    _graph.run('CREATE TEXT INDEX CategoryIndex IF NOT EXISTS FOR(n: RCGNode) ON(n.category)')
    # graph.run('CREATE TEXT INDEX ValueIndex IF NOT EXISTS FOR(n: RCGNode) ON(n.value)')

    print('These indexes have been created (column "state" indicates if they have been generated yet):')
    out = _graph.run('SHOW INDEXES')
    print(out)
    return


def create_ricgraph_key(name: str, value: str) -> str:
    """Create a key for a node.
    This function generates a composite key for a node in a graph.

    :param name: name of the node.
    :param value: value of the node.
    :return: key generated for the node.
    """
    return value.lower() + '|' + name.lower()


def create_well_known_url(name: str, value: str) -> str:
    """Create a URL to refer to the source of a 'well known' identifier (i.e. ORCID, ISNI, etc.).

    :param name: an identifier name, e.g. ORCID, ISNI, etc.
    :param value: the value.
    :return: URL.
    """
    if name == '' or value == '':
        return ''

    if name == 'DOI':
        return 'https://doi.org/' + value
    elif name == 'ISNI':
        return 'https://isni.org/isni/' + value
    elif name == 'ORCID':
        return 'https://orcid.org/' + value
    elif name == 'SCOPUS_AUTHOR_ID':
        return 'https://www.scopus.com/authid/detail.uri?authorId=' + value
    else:
        return ''


def create_history_line(field_name: str, old_value: str, new_value: str) -> str:
    """Create a line to be used in the 'history' property of a node.
    """
    return 'Updated field "' + field_name + '" from "' + old_value + '" to "' + new_value + '". '


# _history should be an ordered list:
# "[...] that the items have a defined order, and that order will not change.
# If you add new items to a list, the new items will be placed at the end of the list."
# https://www.w3schools.com/python/python_lists.asp
# That means, list or tuple, or with python 3.7 (OpenSUSE 15.4 has 3.6), a dictionary.
# However, we cannot use a dict, because neo4j requires:
# "Property values can only be of primitive types or arrays thereof"
# This might change if another graph database is going to be used.
def create_node(name: str, category: str, value: str,
                **other_properties: dict) -> Union[Node, None]:
    """Create a node.
    For now all properties will have string value, except for _history, which is a list.

    :param name: 'name' field of node.
    :param category: idem.
    :param value: idem.
    :param other_properties: a dictionary of all the other properties.
    :return: the node created, or None if this was not possible
    """
    global _graph

    if _graph is None:
        print('\ncreate_node(): Error: graph has not been initialized or opened.\n\n')
        return None

    lname = str(name)
    lcategory = str(category)
    lvalue = str(value)

    if lname == '' or lcategory == '' or lvalue == '' \
       or lname == 'nan' or lcategory == 'nan' or lvalue == 'nan':
        return None

    url = create_well_known_url(name=lname, value=lvalue)
    node_properties = {}
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    node = read_node(name=lname, value=lvalue)
    if node is None:
        # Create from CRUD
        for prop_name in ALLOWED_RICGRAPH_PROPERTIES:
            node_properties[prop_name] = ''
            for other_name, other_value in other_properties.items():
                if prop_name == other_name:
                    node_properties[prop_name] = str(other_value)
                    break

        # If no url_main has been passed, insert an ISNI, DOI, etc. url if category is ISNI, DOI, etc.
        if node_properties['url_main'] == '' and url != '':
            node_properties['url_main'] = url

        history = [timestamp + ': Created. ' + node_properties['history_event']]
        node_properties['history_event'] = ''
        new_node = Node('RCGNode', _key=create_ricgraph_key(name=lname, value=lvalue), _history=history,
                        name=lname, category=lcategory, value=lvalue, **node_properties)
        _graph.create(new_node)
        return new_node

    # Update from CRUD
    history_line = ''
    if node['category'] != lcategory:
        # Not necessary to do similar tests for lname, lvalue or _key, since changing one of these
        # means that a new node will be created, which is done in the "if" part above.
        history_line += create_history_line(field_name='category', old_value=node['category'], new_value=lcategory)
        node['category'] = lcategory

    for prop_name in ALLOWED_RICGRAPH_PROPERTIES:
        old_val = str(node[prop_name])
        # Note: if a property is not present in other_properties, its value does not change
        for other_name, other_value in other_properties.items():
            other_value_str = str(other_value)
            if prop_name == other_name:
                if old_val != other_value_str:
                    if prop_name != 'history_event':
                        # Do not enter (changes to) property history_event in _history
                        history_line += create_history_line(field_name=prop_name,
                                                            old_value=node[prop_name], new_value=other_value_str)
                    # Note: for now all properties will have string value
                    node[prop_name] = other_value_str
                break

    if node['url_main'] == '' and url != '':
        # If no url_main has been passed, insert an ISNI, DOI, etc. url if category is ISNI, DOI, etc.
        history_line += create_history_line(field_name='url_main', old_value=node['url_main'], new_value=url)
        node['url_main'] = url

    if history_line == '':
        # No changes, clear property history_event
        node['history_event'] = ''
        return node

    node['history_event'] = ''
    node['_history'].append(timestamp + ': Updated. ' + history_line + node['history_event'])
    # The push() only works after a graph has been created, merge() does not update
    _graph.push(node)

    return node


def read_node(name: str = '', value: str = '') -> Node:
    """Read a node based on name and value.
    Since all nodes are supposed to be unique, return the first one found.

    :param name: 'name' field of node.
    :param value: idem.
    :return: the node read, or None if no node was found.
    """
    first_node = read_all_nodes(name=name, value=value).first()
    return first_node


def read_all_nodes(name: str = '', category: str = '', value: str = '') -> Union[NodeMatch, None]:
    """Read a number of nodes based on name, category or value.
    Any of these parameters can be specified.

    :param name: 'name' field of node.
    :param category: idem.
    :param value: idem.
    :return: NodeMatch object, which is a kind of list of nodes read, or None if nothing found
    """
    global _graph

    if _graph is None:
        print('\nread_all_nodes(): Error: graph has not been initialized or opened.\n\n')
        return None

    lname = str(name)
    lcategory = str(category)
    lvalue = str(value)

    if lname == 'nan' or lcategory == 'nan' or lvalue == 'nan':
        return None
    if lname == '' and lcategory == '' and lvalue == '':
        return None

    node_properties = {}
    if lname != '':
        node_properties['name'] = lname
    if lcategory != '':
        node_properties['category'] = lcategory
    if lvalue != '':
        node_properties['value'] = lvalue

    # Use NodeMatch for more advanced node matching
    nodes_in_graph = NodeMatcher(_graph)
    all_nodes = nodes_in_graph.match('RCGNode', **node_properties)
    return all_nodes


def update_node(name: str, category: str, value: str,
                **other_properties: dict) -> Node:
    """Update a node.

    :param name: 'name' field of node.
    :param category: idem.
    :param value: idem.
    :param other_properties: a dictionary of all the other properties.
    :return: the node created, or None if this was not possible
    """
    node = create_node(name=name, category=category, value=value, **other_properties)
    return node


def delete_node(name: str, value: str) -> None:
    """Delete a node based on name and value.

    :param name: 'name' field of node.
    :param value: idem.
    """
    global _graph

    if _graph is None:
        print('\ndelete_node(): Error: graph has not been initialized or opened.\n\n')
        return

    lname = str(name)
    lvalue = str(value)

    if lname == '' or lvalue == '' or lname == 'nan' or lvalue == 'nan':
        return

    node = read_node(name=lname, value=lvalue)
    if node is None:
        return

    _graph.delete(node)
    return


def connect_two_nodes(left_node: Node, right_node: Node) -> None:
    """Connect two nodes with two directed edges.

    In case a node is to contain a personal ID (e.g. ORCID, ISNI, etc.) (then it has
    category = 'person'), a 'person-root' node will be created if it does not exist.
    This 'person-root' node is to be seen as the 'representative' for a person.
    All research outputs will be linked to the 'person-root' node, not to the personal ID node.

    In some cases this will go wrong, e.g. if the same personal ID (e.g. ORCID)
    has been assigned to two different
    persons. This is an error, probably caused by a typo in the system we harvest from. In that case,
    a warning is printed while harvesting, and a warning is added to the edge connecting 'left_node' and
    'right_node'. Two edge properties are created: 'warning' (True or False) and 'reason' (string).
    Ideally, this should be corrected in the system we harvest from.
    To conclude: every node with a personal ID should have 2 edges, if there are more, there has been
    an error.

    :param left_node: the left node.
    :param right_node: the right node.
    :return: None.
    """
    global _graph

    if left_node['category'] != 'person' and right_node['category'] != 'person':
        # This is not a person to person link, link directly
        edge1 = LINKS_TO(left_node, right_node)
        edge2 = LINKS_TO(right_node, left_node)

        # Do a "merge" instead of a "create" to prevent double edges.
        _graph.merge(edge1 | edge2, 'RCGNode', '_key')
        return

    # At least one of the nodes is a 'person' link. These should be linked via their 'person-root' node.
    person_root_left_node = None
    person_root_right_node = None
    if left_node['category'] == 'person':
        for edge in get_edges(left_node):
            if edge.end_node['name'] == 'person-root':
                person_root_left_node = edge.end_node

    if right_node['category'] == 'person':
        for edge in get_edges(right_node):
            if edge.end_node['name'] == 'person-root':
                person_root_right_node = edge.end_node

    if person_root_left_node is None \
       or person_root_right_node is None \
       or person_root_left_node == person_root_right_node:
        # This covers:
        # (1) left & right node have no parent, i.e. both person-root nodes are None
        # (2) one of left or right node is None, join to the person-root of the other
        # (3) both left & right node have the same parent, join together
        if person_root_left_node is not None:
            person_root = person_root_left_node
        else:
            person_root = person_root_right_node

        if person_root is None:
            # Case 1: Create the in-between node, "person-root" node, create a unique value
            lvalue = str(uuid.uuid4())
            person_root = create_node(name='person-root', category='person', value=lvalue,
                                      other_properties={'comment': 'inserted person-root'})

        # Now link via the in-between node, "person-root" node
        edge1 = LINKS_TO(left_node, person_root)
        edge2 = LINKS_TO(person_root, left_node)
        edge3 = LINKS_TO(right_node, person_root)
        edge4 = LINKS_TO(person_root, right_node)
        _graph.merge(edge1 | edge2 | edge3 | edge4, 'RCGNode', '_key')
        return

    # Now we are left with the complicated case: left & right node point to a different person-root.
    # This can happen e.g. in case a personal ID (ISNI, ORCID, etc.) is assigned to two or more different persons.
    # Of course, that should not happen. Most probably this in a typo in the source system.
    # To solve this, the personal ID node is going to point to both (different) person-root nodes.
    # There are two cases:
    # (1) The personal ID node has (in a previous iteration) already been assigned to two (or more) person-root nodes.
    #     Check if there exists a common person-root node of this PID node and the other node.
    #     If so, join start & end node to this common node.
    # (2) This is not the case, start & end node have no common person-root.
    #     This is tricky, because we don't know which of start or end node has been assigned to two different
    #     persons. I think there is no "good" solution for this.
    #     Connect one node to the person-root node of the other and vice versa.
    #
    # Case 1
    for edge_from_left_node in get_edges(left_node):
        person_root_left = edge_from_left_node.end_node
        for edge_from_right_node in get_edges(right_node):
            person_root_right = edge_from_right_node.end_node
            if person_root_left == person_root_right:
                # Link via the common person-root node
                person_root = person_root_left         # doesn't matter which one
                edge1 = LINKS_TO(left_node, person_root)
                edge2 = LINKS_TO(person_root, left_node)
                edge3 = LINKS_TO(right_node, person_root)
                edge4 = LINKS_TO(person_root, right_node)
                _graph.merge(edge1 | edge2 | edge3 | edge4, 'RCGNode', '_key')
                return

    # Case 2
    message = '\nconnect_two_nodes(): WARNING: different person_root_left_node & person_root_right_node found.\n'
    message += 'This usually means that the same identifier (ORCID, ISNI, etc) has been assigned '
    message += 'to two different persons:\n'
    message += '"_key" left_node: "' + left_node['_key'] + '";\n'
    message += '"_key" person_root_left_node: "' + person_root_left_node['_key'] + '";\n'
    message += '"_key" person_root_right_node: "' + person_root_right_node['_key'] + '";\n'
    message += '"_key" right_node: "' + right_node['_key'] + '"\n'

    print(message)
    message.replace('\n', ' ')

    edge1 = LINKS_TO(left_node, person_root_right_node)
    edge2 = LINKS_TO(person_root_right_node, left_node)
    edge3 = LINKS_TO(right_node, person_root_left_node)
    edge4 = LINKS_TO(person_root_left_node, right_node)

    # Add a "warning" attribute to all edges involved
    edge1['warning'] = edge2['warning'] = edge3['warning'] = edge4['warning'] = 'True'
    edge1['reason'] = edge2['reason'] = edge3['reason'] = edge4['reason'] = message
    _graph.merge(edge1 | edge2 | edge3 | edge4, 'RCGNode', '_key')
    return


def create_two_nodes_and_edge(name1: str, category1: str, value1: str,
                              name2: str, category2: str, value2: str,
                              **other_properties: Union[dict, str]) -> None:
    """Create two nodes (if they do not exist) and two directe/d edges between those two nodes.
    The nodes are specified by the properties passed.
    All 'left' nodes end with '1', all right nodes end with '2'.

    :param name1: 'name' field of left node.
    :param category1: idem.
    :param value1: idem.
    :param name2: 'name' field of right node.
    :param category2: idem.
    :param value2: idem
    :param other_properties: a dictionary of all the other properties.
                             Names ending with '1' belong to a 'left' node,
                             names ending with '2' to a 'right' node.
    :return: None.
    """
    node_properties1 = {}
    node_properties2 = {}
    for prop_name in ALLOWED_RICGRAPH_PROPERTIES:
        for other_name, other_value in other_properties.items():
            if prop_name + '1' == other_name:
                node_properties1.update({prop_name: other_value})
            if prop_name + '2' == other_name:
                node_properties2.update({prop_name: other_value})

    node1 = create_node(name=name1, category=category1, value=value1, **node_properties1)
    node2 = create_node(name=name2, category=category2, value=value2, **node_properties2)
    if node1 is None or node2 is None:
        return

    connect_two_nodes(left_node=node1, right_node=node2)
    return


def create_nodepairs_and_edges_df(left_and_right_nodepairs: pandas.DataFrame) -> None:
    """Create two nodes (called 'node pairs') and two directed edges between those nodes.
    This is done for all the nodes passed. The nodes are specified in a DataFrame.
    One row in the DataFrame contains two nodes which are to be connected.

    The column names specify the property in a node (i.e. 'name1', 'category1', 'value1').
    The row value of that column specify the property value of that property.
    All 'left' nodes end with '1', all right nodes end with '2'.

    :param left_and_right_nodepairs: the node pairs in a DataFrame.
    :return: None.
    """
    print('There are ' + str(len(left_and_right_nodepairs)) + ' rows, creating nodes and edges for row: 0  ', end='')
    count = 0
    columns = left_and_right_nodepairs.columns
    for row in left_and_right_nodepairs.itertuples():
        count += 1
        if count % 250 == 0:
            print(count, ' ', end='', flush=True)
        if count % 10000 == 0:
            print('\n', end='', flush=True)

        node_properties = {}
        for prop_name in ALLOWED_RICGRAPH_PROPERTIES:
            for other_name in columns:
                if prop_name + '1' == other_name:
                    node_properties[prop_name + '1'] = getattr(row, other_name)
            for other_name in columns:
                if prop_name + '2' == other_name:
                    node_properties[prop_name + '2'] = getattr(row, other_name)

        create_two_nodes_and_edge(name1=row.name1, category1=row.category1, value1=row.value1,
                                  name2=row.name2, category2=row.category2, value2=row.value2,
                                  **node_properties)
    print(count, '\n', end='', flush=True)
    return


def create_nodepairs_and_edges_params(name1: Union[dict, str], category1: Union[dict, str], value1: Union[dict, str],
                                      name2: Union[dict, str], category2: Union[dict, str], value2: Union[dict, str],
                                      **other_properties: Union[dict, str]) -> None:
    """Create two nodes (called 'node pairs') and two directed edges between those nodes.
    This is done for all the nodes passed. The nodes are specified by values passed to this function.
    Each value can be either a string or a dict containing strings.
    All 'left' nodes end with '1', all right nodes end with '2'.

    If it is a string (like 'ORCID') then that value will be used for every
    property value for that property. That is, every node pair will have the same value for that property.

    If it is a dict containing strings, then every node pair will have a different value for that property.

    :param name1: 'name' field of left node.
    :param category1: idem.
    :param value1: idem.
    :param name2: 'name' field of right node.
    :param category2: idem.
    :param value2: idem.
    :param other_properties: a dictionary of all the other properties.
                             Names ending with '1' belong to a 'left' node,
                             names ending with '2' to a 'right' node.
    :return: None.
    """
    left_and_right_nodepairs = pandas.DataFrame(value1).copy(deep=True)
    left_and_right_nodepairs.rename(columns={value1.name: 'value1'}, inplace=True)

    # This makes programming more efficient
    ext_allowed_rgi_properties = ALLOWED_RICGRAPH_PROPERTIES + ('name', 'category', 'value')
    ext_other_properties = other_properties.copy()
    ext_other_properties['name1'] = name1
    ext_other_properties['name2'] = name2
    ext_other_properties['category1'] = category1
    ext_other_properties['category2'] = category2
    # 'value1' has been included above
    ext_other_properties['value2'] = value2

    for prop_name in ext_allowed_rgi_properties:
        for other_name in ext_other_properties:
            other_value = ext_other_properties[other_name]
            if prop_name + '1' == other_name:
                if type(other_value) == str:
                    left_and_right_nodepairs[prop_name + '1'] = other_value
                else:
                    left_and_right_nodepairs = pandas.concat([left_and_right_nodepairs, other_value], axis='columns')
                    left_and_right_nodepairs.rename(columns={other_value.name: prop_name + '1'}, inplace=True)

            if prop_name + '2' == other_name:
                if type(other_value) == str:
                    left_and_right_nodepairs[prop_name + '2'] = other_value
                else:
                    left_and_right_nodepairs = pandas.concat([left_and_right_nodepairs, other_value], axis='columns')
                    left_and_right_nodepairs.rename(columns={other_value.name: prop_name + '2'}, inplace=True)

    # Reorder a bit, starting with the last, only the name-category-value fields, since they will surely exist
    left_and_right_nodepairs.insert(0, 'value2', left_and_right_nodepairs.pop('value2'))
    left_and_right_nodepairs.insert(0, 'category2', left_and_right_nodepairs.pop('category2'))
    left_and_right_nodepairs.insert(0, 'name2', left_and_right_nodepairs.pop('name2'))
    left_and_right_nodepairs.insert(0, 'value1', left_and_right_nodepairs.pop('value1'))
    left_and_right_nodepairs.insert(0, 'category1', left_and_right_nodepairs.pop('category1'))
    left_and_right_nodepairs.insert(0, 'name1', left_and_right_nodepairs.pop('name1'))

    create_nodepairs_and_edges_df(left_and_right_nodepairs=left_and_right_nodepairs)
    return


def unify_personal_identifiers(personal_identifiers: pandas.DataFrame, history_event: Union[dict, str]) -> None:
    """Unify a collection of personal identifiers (e.g. ORCID, ISNI, etc).
    That means that every column is unified to every other column.
    The identifiers are specified as columns in a DataFrame.

    :param personal_identifiers: DataFrame containing personal identifiers.
    :param history_event: a history event to add.
    :return: None.
    """
    # Use i & j to make sure not to unify twice
    i = 0
    for column1 in personal_identifiers.columns:
        i += 1
        j = 0
        for column2 in personal_identifiers.columns:
            j += 1
            if i >= j:
                continue
            print('\nUnifying personal identifiers ' + column1 + ' and ' + column2 + '...')
            identifiers = personal_identifiers[[column1, column2]].copy(deep=True)

            # Ensure that all '' values are NaN, so that those rows can be easily removed with dropna()
            identifiers.replace('', numpy.nan, inplace=True)
            # dropna(how='any'): drop row if one or more row values contain NaN
            identifiers.dropna(axis=0, how='any', inplace=True)
            identifiers.drop_duplicates(keep='first', inplace=True, ignore_index=True)

            create_nodepairs_and_edges_params(name1=column1, category1='person', value1=identifiers[column1],
                                              name2=column2, category2='person', value2=identifiers[column2],
                                              history_event1=history_event, history_event2=history_event)
    return


def print_node_values(node: Node) -> None:
    """Print the values of all properties in a node.

    :param node: the node.
    :return: None.
    """
    print('Node values:')
    print('_key:     ' + node['_key'])
    print('name:     ' + node['name'])
    print('category: ' + node['category'])
    print('value:    ' + node['value'])
    for prop_name in ALLOWED_RICGRAPH_PROPERTIES:
        print(prop_name + ': ' + node[prop_name])
    print('history:')
    for history in node['_history']:
        print('- ' + history)
    print('')
    return


# ##############################################################################
# Neighbor node and edge functions.
# These start with "get_", not with "read_" as some above.
# The difference is that "get_" functions work in constant time (starting from
# a node) while the "read_" functions read (aka search, find) the whole graph.
# ##############################################################################
def get_edges(node: Node) -> RelationshipMatch:
    """Get the edges attached to a node.

    :param node: the node.
    :return: the edges.
    """
    global _graph

    edges_connected_to_node = _graph.match((node,), r_type='LINKS_TO')
    return edges_connected_to_node


# For the reason why there could be more than one 'person-root' node, see the
# extensive comments in function connect_two_nodes().
def get_personroot_node(node: Node) -> Union[Node, None]:
    """Get the 'person-root' node for a 'person' node.
    If 'node' is already a 'person-root' node, return 'node'.
    If there is more than one person-root node (which should not happen),
    return the first.

    :param node: the node.
    :return: the person-root node.
    """
    personroot_nodes = get_all_personroot_nodes(node)
    if len(personroot_nodes) == 0:
        return None
    else:
        return personroot_nodes[0]


# For the reason why there could be more than one 'person-root' node, see the
# extensive comments in function connect_two_nodes().
def get_all_personroot_nodes(node: Node) -> list:
    """Get the 'person-root' node(s) for a 'person' node.
    If 'node' is already a 'person-root' node, return 'node'.
    If there is more than one person-root node (which should not happen),
    all will be returned in a list.

    :param node: the node.
    :return: a list of all the person-root nodes found.
    """
    if node is None:
        return []

    if node['category'] != 'person':
        return []

    personroot_nodes = []
    if node['name'] == 'person-root':
        personroot_nodes.append(node)
        return personroot_nodes

    edges = get_edges(node)
    if len(edges) == 0:
        print('get_personroot_node(): warning, "person" node with _key "' + node['_key'] + '"')
        print('  has 0 neighbors, that should not happen, continuing...')
        return []

    for edge in edges:
        next_node = edge.end_node
        if node == next_node:
            continue
        if next_node['name'] == 'person-root':
            personroot_nodes.append(next_node)
            continue

    return personroot_nodes


def get_all_neighbor_nodes(node: Node,
                           name_want: Union[str, list] = '',
                           name_dontwant: Union[str, list] = '',
                           category_want: Union[str, list] = '',
                           category_dontwant: Union[str, list] = '') -> list:
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
    :return: the list of neighboring nodes satisfying all these criteria.
    """
    global _graph

    if _graph is None:
        print('\nget_personroot_node(): Error: graph has not been initialized or opened.\n\n')
        return []

    if node is None:
        return []

    edges = get_edges(node)
    if len(edges) == 0:
        return []

    # If 'name_want' etc. are strings, convert them to lists.
    if type(name_want) == str:
        if name_want == '':
            name_want_list = []
        else:
            name_want_list = [name_want]
    else:
        name_want_list = name_want

    if type(name_dontwant) == str:
        if name_dontwant == '':
            name_dontwant_list = []
        else:
            name_dontwant_list = [name_dontwant]
    else:
        name_dontwant_list = name_dontwant

    if type(category_want) == str:
        if category_want == '':
            category_want_list = []
        else:
            category_want_list = [category_want]
    else:
        category_want_list = category_want

    if type(category_dontwant) == str:
        if category_dontwant == '':
            category_dontwant_list = []
        else:
            category_dontwant_list = [category_dontwant]
    else:
        category_dontwant_list = category_dontwant

    neighbor_nodes = []
    for edge in edges:
        next_node = edge.end_node
        if node == next_node:
            continue
        if next_node['name'] in name_dontwant_list:
            continue
        if next_node['category'] in category_dontwant_list:
            continue
        if len(name_want) == 0 and len(category_want) == 0:
            neighbor_nodes.append(next_node)
            continue
        if next_node['name'] in name_want_list \
           and next_node['category'] in category_want_list:
            neighbor_nodes.append(next_node)
            continue
        if next_node['name'] in name_want_list and len(category_want_list) == 0:
            neighbor_nodes.append(next_node)
            continue
        if len(name_want_list) == 0 and next_node['category'] in category_want_list:
            neighbor_nodes.append(next_node)
            continue
        # Any other next_node we do not want.

    return neighbor_nodes


def get_all_neighbor_nodes_person(node: Node) -> list:
    """Get all the 'person' neighbor nodes connected to 'node',
    also including 'node'.

    :param node: the node.
    :return: all person nodes connected to 'node'.
    """
    if node is None:
        return []

    personroot = get_personroot_node(node)
    if personroot is None:
        return []

    neighbor_nodes = get_all_neighbor_nodes(personroot, category_want='person')
    neighbor_nodes.append(personroot)

    return neighbor_nodes


# ##############################################################################
# Utility functions
# ##############################################################################

def harvest_json(url: str, headers: dict, max_recs_to_harvest: int = 0, chunksize: int = 0) -> list:
    """Harvest json data from a file.

    :param url: URL to harvest.
    :param headers: headers required.
    :param max_recs_to_harvest: maximum records to harvest.
    :param chunksize: chunk size to use (i.e. the number of records harvested in one call to 'url').
    :return: list of records in json format, or empty list if nothing found.
    """
    if chunksize > 0:
        if 0 < max_recs_to_harvest <= chunksize:
            chunksize = max_recs_to_harvest
        # Adapt url to include chunk size
        url = url + '&size=' + str(chunksize)
    else:
        chunksize = 1

    all_records = 9999999999                # a large number
    if max_recs_to_harvest == 0:
        max_recs_to_harvest = all_records

    print('Harvesting json data from ' + url + '.')
    print('Getting data...')
    json_data = []
    count = 0
    more_records = True
    first_time = True
    while more_records:
        if count >= max_recs_to_harvest:
            break

        chunk_json_data = {}
        try:
            request = urllib.request.Request(url=url, headers=headers)
            response = urllib.request.urlopen(request, timeout=30)
            body = response.read().decode('utf-8')
            chunk_json_data = json.loads(body)
        except urllib.error.HTTPError:
            print('harvest_json(): error during harvest, possibly '
                  + 'a missing API-key or mixed up harvest URL?')
            exit(1)

        if 'items' not in chunk_json_data:
            print('harvest_json(): Error: malformed json, "items" is missing.')
            return []

        if first_time:
            if 'count' in chunk_json_data:
                if max_recs_to_harvest == all_records:
                    print('There are ' + str(chunk_json_data['count'])
                          + ' records, harvesting in chunks of ' + str(chunksize)
                          + ' items.')
                else:
                    print('There are ' + str(chunk_json_data['count'])
                          + ' records, harvesting in chunks of ' + str(chunksize)
                          + ', at most ' + str(max_recs_to_harvest) + ' items.')
                print('Harvesting record: ', end='', flush=True)
            else:
                print('harvest_json(): Warning: malformed json, "count" is missing.')
            first_time = False

        json_items = chunk_json_data['items']
        json_data += json_items

        if 'navigationLinks' in chunk_json_data:
            more_records = False
            for link in chunk_json_data['navigationLinks']:
                if link['ref'] == 'next':
                    url = link['href']
                    more_records = True
        else:
            more_records = False

        if count % 500 == 0:
            print(count, ' ', end='', flush=True)
        if count % 10000 == 0:
            if count != 0:
                print('\n', end='', flush=True)
        count += chunksize

    print(count, ' Done.\n', end='', flush=True)
    return json_data


def harvest_json_and_write_to_file(filename: str, url: str, headers: dict,
                                   max_recs_to_harvest: int = 0, chunksize: int = 0) -> list:
    """Harvest json data and write the data found to a file.
    This data is a list of records in json format. If no records are harvested, nothing is written.

    :param filename: filename of the file to use for writing.
    :param url: URL to harvest.
    :param headers: headers required.
    :param max_recs_to_harvest: maximum records to harvest.
    :param chunksize: chunk size to use (i.e. the number of records harvested in one call to 'url').
    :return: list of records in json format, or empty list if nothing found.
    """
    json_data = harvest_json(url=url,
                             headers=headers,
                             max_recs_to_harvest=max_recs_to_harvest,
                             chunksize=chunksize)
    if len(json_data) == 0:
        return []
    write_json_to_file(json_data=json_data, filename=filename)
    return json_data


def write_json_to_file(json_data: list, filename: str) -> None:
    """Write json data to a file.
    If no records are harvested, nothing is written.

    :param json_data: a list of records in json format.
    :param filename: filename of the file to use for writing.
    :return: None.
    """
    print('Saving json data to ' + filename + '... ', end='', flush=True)
    with open(filename, 'w') as fd:
        json.dump(obj=json_data, fp=fd, ensure_ascii=False, indent=2)
    print('Done.')
    return


def read_json_from_file(filename: str) -> list:
    """Read json data from a file.

    :param filename: filename of the file to use for writing.
    :return: list of records in json format, or empty list if nothing found.
    """
    print('Reading json data from ' + filename + '... ', end='', flush=True)
    with open(filename) as fd:
        json_data = json.load(fp=fd)
    print('Done.')
    if json_data is None:
        return []
    return json_data


def read_dataframe_from_csv(filename: str, columns: dict = None,
                            nr_rows: int = None, datatype=None) -> pandas.DataFrame:
    """Reads a datastructure (DataFrame) from file

    :param filename: csv file to read.
    :param columns: which columns to read.
    :param nr_rows: how many rows to read (default: all).
    :param datatype: type of (some) columns to read.
    :return: dataframe read.
    """
    try:
        # Some inputfiles have problems reading in utf-8
        csv_data = pandas.read_csv(filename,
                                   sep=',',
                                   usecols=columns,
                                   dtype=datatype,
                                   engine='python',
                                   nrows=nr_rows,
                                   parse_dates=False,
                                   iterator=False,
                                   quotechar='"',
                                   encoding='utf-8')
    except BaseException:
        print('read_dataframe_from_csv(): error reading in utf-8 format, reading in latin-1 format.')
        csv_data = pandas.read_csv(filename,
                                   sep=',',
                                   usecols=columns,
                                   dtype=datatype,
                                   engine='python',
                                   nrows=nr_rows,
                                   parse_dates=False,
                                   iterator=False,
                                   quotechar='"',
                                   encoding='latin-1')
    return csv_data


def write_dataframe_to_csv(filename: str, df: pandas.DataFrame) -> None:
    """Write a datastructure (DataFrame) to file.

    :param filename: csv file to write.
    :param df: dataframe to write.
    :return: None.
    """
    print('\nWriting to csv file: ' + filename + '... ', end='', flush=True)
    df.to_csv(filename,
              sep=',',
              quotechar='"',
              quoting=csv.QUOTE_ALL,
              encoding='utf-8',
              index=False)
    print('Done.')
    return


# ############################################
# ################### main ###################
# ############################################
# This will be executed on module initialization
if not os.path.exists(RICGRAPH_INI_FILE):
    print('Ricgraph initialization: error, Ricgraph ini file "' + RICGRAPH_INI_FILE + '" not found, exiting.')
    exit(1)

config = configparser.ConfigParser()
config.read(RICGRAPH_INI_FILE)
try:
    ALLOWED_RICGRAPH_PROPERTIES = tuple(config['Ricgraph']['allowed_ricgraph_properties'].split(','))

    NEO4J_HOSTNAME = config['Neo4j']['neo4j_hostname']
    NEO4J_USER = config['Neo4j']['neo4j_user']
    NEO4J_PASSWORD = config['Neo4j']['neo4j_password']
    NEO4J_SCHEME = config['Neo4j']['neo4j_scheme']
    NEO4J_PORT = config['Neo4j']['neo4j_port']
    NEO4J_URL = '{scheme}://{hostname}:{port}'.format(scheme=NEO4J_SCHEME, hostname=NEO4J_HOSTNAME, port=NEO4J_PORT)
except KeyError:
    print('Ricgraph initialization: error, required key values not found in Ricgraph ini file, exiting.')
    exit(1)

# Make sure DataFrames are printed with all columns on full width
pandas.set_option('display.max_columns', None)
pandas.set_option('display.width', 500)
