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
# Ricgraph graph database related functions.
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


from typing import Union
from neo4j.graph import Node
from .ricgraph_constants import MAX_NR_HISTORYITEMS_TO_ADD, A_LARGE_NUMBER
from .ricgraph_cypher import (cypher_create_node, cypher_read_node,
                              cypher_find_nodes, cypher_delete_node,
                              cypher_update_node_properties, cypher_create_edge_if_not_exists,
                              cypher_merge_nodes,
                              get_all_neighbor_nodes,
                              ricgraph_nr_edges_of_node)
from .ricgraph_utils import *
from .ricgraph_researchinfo import create_well_known_url


def create_history_line(property_name: str, old_value: str, new_value: str) -> str:
    """Create a line to be used in the 'history' property of a node.
    """
    return 'Updated property "' + property_name + '" from "' + old_value + '" to "' + new_value + '". '


def create_name_cache_in_personroot(node: Node, personroot: Node) -> None:
    """This function caches the value of a node with 'name' 'FULL_NAME'
    in the 'comment' property of its person-root node 'personroot'.
    If the cache is not present, it is created.

    :param node: node to add FULL_NAME to cache.
    :param personroot: personroot node of 'node'. For efficiency, we do not check
      if this really is the case.
    :return: No return value.
    """
    if node is None:
        return
    if personroot is None:
        return
    if node['name'] == 'FULL_NAME':
        time_stamp = datetimestamp()
        value = get_valuepart_from_ricgraph_value(node['value']) + ' ['
        value += get_additionalpart_from_ricgraph_value(node['value']) + ']'
        if isinstance(personroot['comment'], str):
            if personroot['comment'] == '':
                old_value = str(personroot['comment'])      # Not necessary, for symmetry.
                node_properties = {'comment': [value]}
                history_line = create_history_line(property_name='comment',
                                                   old_value=old_value,
                                                   new_value=str(node_properties['comment']))
                node_properties['_history'] = personroot['_history'].copy()
                node_properties['_history'].append(time_stamp + ': ' + history_line)
                cypher_update_node_properties(node_element_id=personroot.element_id,
                                              node_properties=node_properties)
        elif isinstance(personroot['comment'], list):
            # if node['value'] not in personroot['comment']:
            if value not in personroot['comment']:
                old_value = str(personroot['comment'])
                node_properties = {'comment': personroot['comment'].copy()}
                node_properties['comment'].append(value)
                history_line = create_history_line(property_name='comment',
                                                   old_value=old_value,
                                                   new_value=str(node_properties['comment']))
                node_properties['_history'] = personroot['_history'].copy()
                node_properties['_history'].append(time_stamp + ': ' + history_line)
                cypher_update_node_properties(node_element_id=personroot.element_id,
                                              node_properties=node_properties)
        # In all other cases: it is already in the cache,
        # or leave it as it is: 'comment' seems to be used for something we don't know.
    return


def recreate_name_cache_in_personroot(personroot: Node) -> None:
    """This function recreates the cache of all the nodes with 'name' 'FULL_NAME'
    in the 'comment' property of its person-root node 'personroot'.
    If the cache is not present, it is created.

    :param personroot: personroot node of 'node'. For efficiency, we do not check
      if this really is the case.
    :return: No return value.
    """
    if personroot is None:
        return
    neighbornodes = get_all_neighbor_nodes(node=personroot,
                                           name_want='FULL_NAME')
    name_cache = []
    for node in neighbornodes:
        value = get_valuepart_from_ricgraph_value(node['value']) + ' ['
        value += get_additionalpart_from_ricgraph_value(node['value']) + ']'
        if value not in name_cache:
            name_cache.append(value)

    # We need to do this irrespective of the length of name_cache.
    # If the length is 0, we might be deleting FULL_NAME nodes and that
    # should also be reflected in the name cache.
    if (isinstance(personroot['comment'], str) and personroot['comment'] == '') \
       or isinstance(personroot['comment'], list):
        time_stamp = datetimestamp()
        history_line = create_history_line(property_name='comment',
                                           old_value=str(personroot['comment']),
                                           new_value=str(name_cache))
        node_properties = {'comment': name_cache.copy(),
                           '_history': personroot['_history'].copy()}
        node_properties['_history'].append(time_stamp + ': Cleaned and recreated name cache. ' + history_line)
        cypher_update_node_properties(node_element_id=personroot.element_id,
                                      node_properties=node_properties)
    # In all other cases: leave it as it is: 'comment' seems to be used for something we don't know.
    return


def create_update_node(name: str, category: str, value: str,
                       other_properties: dict = None) -> Union[Node, None]:
    """Create a node, or update its values if is already present.
    The new/updated node will have values 'name', 'category', and 'value', and
    the values in other_properties.
    For now all properties will have a string value, except for '_source'
    (a sorted list), and '_history' (a list).
    Changing the 'name' or 'value' properties (and, subsequently, the '_key' value),
    cannot be done with this function, since in that case we would not be able
    to find it.

    :param name: 'name' property of node to create or update.
    :param category: 'category' property of node.
    :param value: 'value' property of node.
    :param other_properties: a dictionary of all the other properties.
    :return: the node created, or None if this was not possible
    """
    if other_properties is None:
        other_properties = {}

    if not isinstance(name, str) \
       or not isinstance(category, str) \
       or not isinstance(value, str):
        return None

    if other_properties is None:
        other_properties = {}

    lname = str(name)
    lcategory = str(category)
    lvalue = str(value)

    if lname == '' or lcategory == '' or lvalue == '':
        return None

    node_properties = {}
    time_stamp = datetimestamp()
    node = read_node(name=lname, value=lvalue)
    if node is None:
        # Create a node.
        # First do the properties in RICGRAPH_PROPERTIES_STANDARD.
        node_properties['name'] = lname
        node_properties['category'] = lcategory
        node_properties['value'] = lvalue

        # Then do the properties in RICGRAPH_PROPERTIES_ADDITIONAL.
        for prop_name in RICGRAPH_PROPERTIES_ADDITIONAL:
            if prop_name in other_properties:
                node_properties[prop_name] = str(other_properties[prop_name])
            else:
                node_properties[prop_name] = ''

        # If no url_main has been passed, insert an ISNI, DOI, etc. url if category is ISNI, DOI, etc.
        url = create_well_known_url(name=lname, value=lvalue)
        if node_properties['url_main'] == '' and url != '':
            node_properties['url_main'] = url

        # Then do the properties in RICGRAPH_PROPERTIES_HIDDEN.
        node_properties['_key'] = create_ricgraph_key(name=lname, value=lvalue)
        if node_properties['source_event'] == '':
            node_properties['_source'] = []
        else:
            node_properties['_source'] = [node_properties['source_event']]
            node_properties['source_event'] = ''

        if node_properties['history_event'] == '':
            node_properties['_history'] = [time_stamp + ': Created. ']
        else:
            node_properties['_history'] = [time_stamp + ': Created. ' + node_properties['history_event']]
            node_properties['history_event'] = ''

        new_node = cypher_create_node(node_properties=node_properties)
        return new_node

    if RICGRAPH_NODEADD_MODE == 'strict' and node['name'] == 'FULL_NAME':
        # We only get here if we want to connect some other node A to this FULL_NAME node B.
        # This FULL_NAME node B already exists. Most probably it is connected to a person-root C
        # and that person-root C to some other nodes D and E.
        # If we would continue, A would be connected to B, and also to C, D and E.
        # However, connecting based on a name is not a very good idea, since two
        # different persons may have the same name.
        # So don't do this if we are in NODEADD_MODE 'strict'.
        return None

    # Update a node.
    history_line = ''

    # First do the properties in RICGRAPH_PROPERTIES_STANDARD.
    # It is not possible to update 'name' or 'value'.
    if node['category'] != lcategory:
        history_line += create_history_line(property_name='category',
                                            old_value=node['category'],
                                            new_value=lcategory)
        node_properties['category'] = lcategory

    # Then do the properties in RICGRAPH_PROPERTIES_ADDITIONAL.
    for prop_name in RICGRAPH_PROPERTIES_ADDITIONAL:
        if prop_name not in other_properties:
            continue
        if prop_name == 'history_event' or prop_name == 'source_event':
            # Do not add these to node_properties, and don't add them to _history.
            continue
        if str(other_properties[prop_name]) == '':
            # Do not change a value if the future value is ''.
            continue
        # Only in case a property is in other_properties, its value may change.
        present_val = str(node[prop_name])
        if present_val != str(other_properties[prop_name]):
            # But its value is only changed if it is different then the old value.
            node_properties[prop_name] = str(other_properties[prop_name])
            history_line += create_history_line(property_name=prop_name,
                                                old_value=present_val,
                                                new_value=str(other_properties[prop_name]))

    # Finally do the properties in RICGRAPH_PROPERTIES_HIDDEN.
    # It is not possible to update '_key'.
    if 'source_event' in other_properties:
        if other_properties['source_event'] != '':
            if other_properties['source_event'] not in node['_source']:
                node_properties['_source'] = node['_source'].copy()
                node_properties['_source'].append(other_properties['source_event'])
                node_properties['_source'].sort()
                history_line += create_history_line(property_name='_source',
                                                    old_value=str(node['_source']),
                                                    new_value=str(node_properties['_source']))

    if history_line == '':
        # No changes.
        return node

    node_properties['_history'] = node['_history'].copy()
    node_properties['_history'].append(time_stamp + ': Updated. ' + history_line)
    updated_node = cypher_update_node_properties(node_element_id=node.element_id,
                                                 node_properties=node_properties)
    return updated_node


def read_node(name: str = '', value: str = '') -> Union[Node, None]:
    """Read a node based on name and value.
    Since all nodes are supposed to be unique if both are
    specified, return the first one found.

    :param name: 'name' property of node.
    :param value: 'value' property of node.
    :return: the node read, or None if no node was found.
    """
    if not isinstance(name, str) or not isinstance(value, str):
        return None

    if name == '' or value == '':
        return None

    node =  cypher_read_node(name=name, value=value)
    return node


def read_all_nodes(name: str = '', category: str = '', value: str = '',
                   key: str = '',
                   name_is_exact_match: bool = True,
                   value_is_exact_match: bool = True,
                   max_nr_nodes: int = 0) -> list:
    """Read a number of nodes based on name, category or value.
    Any of these parameters can be specified.
    It is also possible to read a number of nodes based on key.
    But not name, category, value, and key at the same time.
    If key has been specified, the values of name_is_exact_match and
    value_is_exact_match are not used.

    :param name: 'name' property of node.
    :param category: idem.
    :param value: idem.
    :param key: idem.
    :param name_is_exact_match: if True, then do an exact match search
      on field 'name', if False, then do a case-insensitive match.
      Note that a case-insensitive match is more expensive.
    :param value_is_exact_match: if True, then do an exact match search
      on field 'value', if False, then do a case-insensitive match.
      Note that a case-insensitive match is more expensive.
    :param max_nr_nodes: return at most this number of nodes, 0 = all nodes.
    :return: list of nodes read, or empty list if nothing found.
    """
    if not isinstance(name, str) \
       or not isinstance(category, str) \
       or not isinstance(value, str) \
       or not isinstance(key, str):
        return []

    # Special case, for speed.
    if value_is_exact_match and name != '' and category == '' and value != '':
        node = cypher_read_node(name=name, value=value)
        if node is None:
            return []
        else:
            return [node]

    # Don't allow a search for everything.
    if name == '' and category == '' and value == '' and key == '':
        return []

    if key != '' and name == '' and category == '' and value == '':
        node = cypher_read_node(name=get_namepart_from_ricgraph_key(key=key),
                                value=get_valuepart_from_ricgraph_key(key=key))
        if node is None:
            return []
        else:
            return [node]

    # All other cases.
    nodes = cypher_find_nodes(name=name, category=category, value=value,
                              name_is_exact_match=name_is_exact_match,
                              value_is_exact_match=value_is_exact_match,
                              max_nr_nodes=max_nr_nodes)
    return nodes


def update_node_value(name: str, old_value: str, new_value: str) -> Union[Node, None]:
    """Update a node, change the value property.
    This is a special case because we change the key.
    Use carefully, because other property that contain 'old_value' (such
    as 'url_main' or 'url_other') are not being updated, so they will
    point to the wrong URL.

    :param name: 'name' property of node.
    :param old_value: old 'value' property of node.
    :param new_value: old 'value' property of node.
    :return: the node updated, or None if this was not possible.
    """
    # A lot of the code below is copied from create_update_node().
    if not isinstance(name, str) \
       or not isinstance(old_value, str) \
       or not isinstance(new_value, str):
        return None

    lname = str(name)
    loldvalue = str(old_value)
    lnewvalue = str(new_value)

    if lname == '' or loldvalue == '' or lnewvalue == '':
        return None

    time_stamp = datetimestamp()
    node = read_node(name=lname, value=loldvalue)
    newnode = read_node(name=lname, value=lnewvalue)
    if node is None and newnode is None:
        # Node we want to change does not exist.
        print('update_node_value(): Error: both of the nodes do not exist.')
        return None

    if node is None and newnode is not None:
        # Node we want to change does not exist,
        # but newnode does, we don't do anything.
        return newnode

    if node is not None and newnode is not None:
        # The node we want to change to does already exist.
        # So this happens to be a merge of two nodes.
        merged_node = merge_two_nodes(node_merge_from=node,
                                      node_merge_to=newnode)
        return merged_node

    node_properties = {'value': lnewvalue,
                       '_history': []}
    # The following generates a Cannot find reference '[' in 'None'
    # warning in PyCharm, but the 'None' case has been caught above.
    oldkey = node['_key']
    newkey = create_ricgraph_key(name=lname, value=lnewvalue)
    node_properties['_key'] = newkey
    history_line = create_history_line(property_name='value', old_value=loldvalue, new_value=lnewvalue)
    history_line += create_history_line(property_name='_key', old_value=oldkey, new_value=newkey)
    # The following generates a Cannot find reference '[' in 'None'
    # warning in PyCharm, but the 'None' case has been caught above.
    node_properties['_history'] = node['_history'].copy()
    node_properties['_history'].append(time_stamp + ': Updated. ' + history_line)
    # The following generates a Cannot find reference 'element_id' in 'None'
    # warning in PyCharm, but the 'None' case has been caught above.
    updated_node = cypher_update_node_properties(node_element_id=node.element_id,
                                                 node_properties=node_properties)

    if updated_node['name'] == 'FULL_NAME':
        personroot = get_or_create_personroot_node(person_node=updated_node)
        recreate_name_cache_in_personroot(personroot=personroot)
    return updated_node


def delete_node(node: Node) -> None:
    """Delete a node in the graph database.
    If it has any edges, these will also be deleted.

    :param node: the node to delete.
    :return: None.
    """
    if node is None:
        print('delete_node(): Error: node is None - cannot be found.')
        return

    if node['name'] == 'FULL_NAME':
        # We need to recreate the name cache in the person-root node.
        personroot = get_personroot_node(node=node)
    else:
        personroot = None

    cypher_delete_node(node_element_id=node.element_id)

    if personroot is not None:
        recreate_name_cache_in_personroot(personroot=personroot)

    return


def get_or_create_personroot_node(person_node: Node) -> Union[Node, None]:
    """Get a 'person-root' node for a given 'person' node, if that node has
    a 'person-root'. If not, create the 'person-root' node.

    :param person_node: the node.
    :return: the 'person-root' node, or None on error.
    """
    if person_node is None:
        print('get_or_create_personroot_node(): Error: node is None.')
        return None

    if person_node['category'] != 'person':
        print('get_or_create_personroot_node(): node category is not person.')
        return None

    if person_node['name'] == 'person-root':
        return person_node

    personroot_nodes = get_all_personroot_nodes(node=person_node)
    if len(personroot_nodes) == 0:
        # Create the 'person-root' node with a unique value.
        value = create_unique_string()
        personroot = create_update_node(name='person-root', category='person', value=value)
        cypher_create_edge_if_not_exists(left_node_element_id=person_node.element_id,
                                         right_node_element_id=personroot.element_id)
        return personroot

    if len(personroot_nodes) > 1:
        print('get_or_create_personroot_node(): not anticipated: person_node "'
              + person_node['_key'] + '" has more than one person-root nodes: ')
        for node in personroot_nodes:
            print('"' + node['_key'] + '" ', end='')
        print('\nReturn the first.')
        # And fall through.

    personroot = personroot_nodes[0]
    return personroot


def connect_person_and_non_person_node(person_node: Node,
                                       non_person_node: Node) -> None:
    """Connect a 'person' and a non 'person' node.

    :param person_node: the left node, being of category 'person'.
    :param non_person_node: the right node, being of a different category than 'person'.
    :return: None.
    """
    if person_node is None or non_person_node is None:
        print('connect_persons_and_non_person_node(): Error: (one of the) nodes is None.')
        return

    if person_node['category'] != 'person' or non_person_node['category'] == 'person':
        print('connect_person_and_non_person_node(): (one of the) nodes have wrong category.')
        return

    if person_node['name'] == 'person-root':
        personroot = person_node
    else:
        personroot = get_or_create_personroot_node(person_node=person_node)
        if personroot is None:
            return

    cypher_create_edge_if_not_exists(left_node_element_id=non_person_node.element_id,
                                     right_node_element_id=personroot.element_id)
    return


def merge_two_nodes(node_merge_from: Node, node_merge_to: Node) -> Union[Node, None]:
    """Merge two nodes.
    The neighbors of 'node_merge_from' will be merged to node 'node_merge_to'
    and 'node_merge_from' will be deleted.

    :param node_merge_from: the node to merge from.
    :param node_merge_to: the node to merge to.
    :return: the merged node, or None if this was not possible.
    """
    if node_merge_from is None and node_merge_to is not None:
        # Done.
        return node_merge_to

    if node_merge_from is not None and node_merge_to is None:
        print('merge_two_nodes(): Error: it seems that you are trying to move a node')
        print('  to another node. This is not supported.')
        print('  You might want to use update_node_value().')
        return None

    if node_merge_from is None and node_merge_to is None:
        print('merge_two_nodes(): Error: both of the nodes do not exist.')
        return None

    if node_merge_from['name'] != node_merge_to['name'] \
       or node_merge_from['category'] != node_merge_to['category']:
        print('merge_two_nodes(): nodes "' + node_merge_from['_key']
              + '" and "' + node_merge_to['_key']
              + '" have a different "name" or "category" field: not supported.')
        return None

    if node_merge_from == node_merge_to:
        # They are the same, done.
        return node_merge_to

    node_merge_to_properties = {'_history': node_merge_to['_history'].copy()}
    node_merge_to_properties['_source'] = list(set(node_merge_from['_source'] + node_merge_to['_source']))
    node_merge_to_properties['_source'].sort()

    time_stamp = datetimestamp(seconds=True)
    count = 0
    what_happened = time_stamp + '-' + format(count, '02d') + ': '
    what_happened += 'Merged node "'
    what_happened += node_merge_from['_key'] + '" to this node '
    what_happened += 'and then deleted it.'
    node_merge_to_properties['_history'].append(what_happened)

    count += 1
    what_happened = time_stamp + '-' + format(count, '02d') + ': '
    what_happened += '----- Start of deleted node history and neighbors -----'
    node_merge_to_properties['_history'].append(what_happened)

    count += 1
    what_happened = time_stamp + '-' + format(count, '02d') + ': '
    what_happened += '--- Start of history of the deleted node.'
    node_merge_to_properties['_history'].append(what_happened)

    for history in node_merge_from['_history']:
        count += 1
        what_happened = time_stamp + '-' + format(count, '02d') + ': '
        if count >= MAX_NR_HISTORYITEMS_TO_ADD:
            what_happened += 'List truncated, too many history lines for _history.'
            node_merge_to_properties['_history'].append(what_happened)
            break
        what_happened += history
        node_merge_to_properties['_history'].append(what_happened)

    count += 1
    what_happened = time_stamp + '-' + format(count, '02d') + ': '
    what_happened += '--- End of history of the deleted node.'
    node_merge_to_properties['_history'].append(what_happened)

    count += 1
    what_happened = time_stamp + '-' + format(count, '02d') + ': '
    what_happened += '--- These were the neighbors of the deleted node, '
    what_happened += 'now merged with the neighbors of this node:'
    node_merge_to_properties['_history'].append(what_happened)

    neighbornodes = get_all_neighbor_nodes(node=node_merge_from)
    if len(neighbornodes) == 0:
        count += 1
        what_happened = time_stamp + '-' + format(count, '02d') + ': '
        what_happened += '[the node to be deleted has no neighbors]'
        node_merge_to_properties['_history'].append(what_happened)
    else:
        for node in neighbornodes:
            count += 1
            what_happened = time_stamp + '-' + format(count, '02d') + ': '
            if count >= MAX_NR_HISTORYITEMS_TO_ADD:
                what_happened += 'List truncated, too many history lines for _history.'
                node_merge_to_properties['_history'].append(what_happened)
                break
            what_happened += '"' + str(node['_key']) + '" '
            node_merge_to_properties['_history'].append(what_happened)

    count += 1
    what_happened = time_stamp + '-' + format(count, '02d') + ': '
    what_happened += '--- End of list of neighbors of the deleted node.'
    node_merge_to_properties['_history'].append(what_happened)

    count += 1
    what_happened = time_stamp + '-' + format(count, '02d') + ': '
    what_happened += '----- End of deleted node history and neighbors -----'
    node_merge_to_properties['_history'].append(what_happened)

    # Note only properties '_history' and '_source' are changed.
    merged_node = cypher_merge_nodes(node_merge_from_element_id=node_merge_from.element_id,
                                     node_merge_to_element_id=node_merge_to.element_id,
                                     node_merge_to_properties=node_merge_to_properties)
    if merged_node is None:
        return None
    if merged_node['name'] == 'person-root':
        # Property 'comment' is also updated.
        recreate_name_cache_in_personroot(personroot=merged_node)

    return merged_node


def merge_two_nodes_name_value(node_merge_from_name: str, node_merge_from_value: str,
                               node_merge_to_name: str, node_merge_to_value: str) -> None:
    """Merge two nodes, by specifying their 'name' and 'value' fields.
    The neighbors of 'node_merge_from' will be merged to node 'node_merge_to'
    and 'node_merge_from' will be deleted.

    :param node_merge_from_name: 'name' property of node_merge_from.
    :param node_merge_from_value: 'value' property of node_merge_from.
    :param node_merge_to_name: 'name' property of node_merge_to.
    :param node_merge_to_value: 'value' property of node_merge_to.
    :return: None.
    """
    node_merge_from = read_node(name=node_merge_from_name,
                                value=node_merge_from_value)
    node_merge_to = read_node(name=node_merge_to_name,
                              value=node_merge_to_value)
    merge_two_nodes(node_merge_from=node_merge_from,
                    node_merge_to=node_merge_to)
    return


def connect_person_and_person_node(left_node: Node, right_node: Node) -> None:
    """Connect two person nodes.

    :param left_node: the left node.
    :param right_node: the right node.
    :return: None.
    """
    if left_node is None or right_node is None:
        print('connect_person_and_person_node(): (one of the) nodes is None.')
        return

    if left_node['category'] != 'person' or right_node['category'] != 'person':
        print('connect_person_and_person_node(): (one of the) nodes have wrong category.')
        return

    if left_node['name'] == 'person-root' or right_node['name'] == 'person-root':
        cypher_create_edge_if_not_exists(left_node_element_id=left_node.element_id,
                                         right_node_element_id=right_node.element_id)
        return

    nr_edges_left_node = ricgraph_nr_edges_of_node(node_element_id=left_node.element_id)
    nr_edges_right_node = ricgraph_nr_edges_of_node(node_element_id=right_node.element_id)
    if nr_edges_left_node == 0 and nr_edges_right_node == 0:
        # None of the nodes have a 'person-root' node, create one and connect.
        personroot = get_or_create_personroot_node(person_node=left_node)
        if personroot is None:
            return
        cypher_create_edge_if_not_exists(left_node_element_id=right_node.element_id,
                                         right_node_element_id=personroot.element_id)
        return

    if nr_edges_left_node > 0 and nr_edges_right_node == 0:
        # 'left_node' already has a 'person-root' node.
        personroot = get_or_create_personroot_node(person_node=left_node)
        if personroot is None:
            return
        cypher_create_edge_if_not_exists(left_node_element_id=right_node.element_id,
                                         right_node_element_id=personroot.element_id)
        return

    if nr_edges_left_node == 0 and nr_edges_right_node > 0:
        # 'right_node' already has a 'person-root' node.
        personroot = get_or_create_personroot_node(person_node=right_node)
        if personroot is None:
            return
        cypher_create_edge_if_not_exists(left_node_element_id=left_node.element_id,
                                         right_node_element_id=personroot.element_id)
        return

    left_personroot_node = get_or_create_personroot_node(person_node=left_node)
    right_personroot_node = get_or_create_personroot_node(person_node=right_node)
    if left_personroot_node is None or right_personroot_node is None:
        return

    if left_personroot_node == right_personroot_node:
        # Already connected, nothing to do.
        return

    # Only continue depending on RICGRAPH_NODEADD_MODE.
    if RICGRAPH_NODEADD_MODE == 'strict':
        # For more explanation, see file docs/ricgraph_install_configure.md,
        # section RICGRAPH_NODEADD_MODE.
        return

    # Connect crosswise.
    cypher_create_edge_if_not_exists(left_node_element_id=left_node.element_id,
                                     right_node_element_id=right_personroot_node.element_id)
    cypher_create_edge_if_not_exists(left_node_element_id=right_node.element_id,
                                     right_node_element_id=left_personroot_node.element_id)

    time_stamp = datetimestamp()
    message = 'The node pair "'
    message += left_node['_key'] + '" and "' + right_node['_key']
    message += '" caused this node to have more than one neighbor. '
    message += 'These are its person-root nodes: "'
    message += left_personroot_node['_key'] + '" and "'
    message += right_personroot_node['_key'] + '". '
    message += 'This might be caused by a mislabeling in a harvested system.'
    timestamped_message = time_stamp + ': ' + message

    print('\nconnect_person_and_person_node(): ' + message)
    node_property = {'_history': left_node['_history'].copy()}
    node_property['_history'].append(timestamped_message)
    cypher_update_node_properties(node_element_id=left_node.element_id,
                                  node_properties=node_property)
    node_property = {'_history': right_node['_history'].copy()}
    node_property['_history'].append(timestamped_message)
    cypher_update_node_properties(node_element_id=right_node.element_id,
                                  node_properties=node_property)
    return


def connect_two_nodes(left_node: Node, right_node: Node) -> None:
    """Connect two nodes with two directed edges.

    In case a node is to contain a personal ID (e.g. ORCID, ISNI, etc.) (then it has
    category = 'person'), a 'person-root' node will be created if it does not exist.
    This 'person-root' node is to be seen as the 'representative' for a person.
    All research outputs will be linked to the 'person-root' node, not to the personal ID node.

    :param left_node: the left node.
    :param right_node: the right node.
    :return: None.
    """
    if left_node is None or right_node is None:
        return

    if left_node['category'] != 'person' and right_node['category'] != 'person':
        # This is not a person to person link, link directly
        cypher_create_edge_if_not_exists(left_node_element_id=left_node.element_id,
                                         right_node_element_id=right_node.element_id)
        return

    # At least one of the nodes is a 'person' link. These should be linked via their 'person-root' node.
    if left_node['category'] == 'person' and right_node['category'] != 'person':
        connect_person_and_non_person_node(person_node=left_node,
                                           non_person_node=right_node)
        return

    if left_node['category'] != 'person' and right_node['category'] == 'person':
        connect_person_and_non_person_node(person_node=right_node,
                                           non_person_node=left_node)
        return

    connect_person_and_person_node(left_node=left_node,
                                   right_node=right_node)
    return


def create_two_nodes_and_edge(name1: str, category1: str, value1: str,
                              name2: str, category2: str, value2: str,
                              **other_properties: Union[dict, str]) -> None:
    """Create two nodes (if they do not exist) and two directed edges between those two nodes.
    The nodes are specified by the properties passed.
    All 'left' nodes end with '1', all right nodes end with '2'.

    :param name1: 'name' property of left node.
    :param category1: idem.
    :param value1: idem.
    :param name2: 'name' property of right node.
    :param category2: idem.
    :param value2: idem
    :param other_properties: a dictionary of all the other properties.
                             Names ending with '1' belong to a 'left' node,
                             names ending with '2' to a 'right' node.
    :return: None.
    """
    node_properties1 = {}
    node_properties2 = {}
    for prop_name in RICGRAPH_PROPERTIES_ADDITIONAL:
        for other_name, other_value in other_properties.items():
            if prop_name + '1' == other_name:
                node_properties1.update({prop_name: other_value})
            if prop_name + '2' == other_name:
                node_properties2.update({prop_name: other_value})

    node1 = create_update_node(name=name1, category=category1, value=value1,
                               other_properties=node_properties1)
    node2 = create_update_node(name=name2, category=category2, value=value2,
                               other_properties=node_properties2)
    if node1 is None or node2 is None:
        return

    connect_two_nodes(left_node=node1, right_node=node2)
    if node1['name'] == 'FULL_NAME':
        personroot = get_or_create_personroot_node(person_node=node1)
        new_value = create_ricgraph_value(value=node1['value'], additional=personroot['value'])
        if (asc := convert_string_to_ascii(node1['value'])) != node1['value']:
            history_event = 'From node "FULL_NAME" with value "' + new_value + '".'
            create_two_nodes_and_edge(name1=personroot['name'],
                                      category1=personroot['category'],
                                      value1=personroot['value'],
                                      name2='FULL_NAME_ASCII',
                                      category2=node1['category'],
                                      value2=create_ricgraph_value(value=asc,
                                                                   additional=personroot['value']),
                                      history_event2=history_event)
        node_upd = update_node_value(name='FULL_NAME',
                                     old_value=node1['value'],
                                     new_value=new_value)
        create_name_cache_in_personroot(node=node_upd, personroot=personroot)
    if node2['name'] == 'FULL_NAME':
        personroot = get_or_create_personroot_node(person_node=node2)
        new_value = create_ricgraph_value(value=node2['value'], additional=personroot['value'])
        if (asc := convert_string_to_ascii(node2['value'])) != node2['value']:
            history_event = 'From node "FULL_NAME" with value "' + new_value + '".'
            create_two_nodes_and_edge(name1=personroot['name'],
                                      category1=personroot['category'],
                                      value1=personroot['value'],
                                      name2='FULL_NAME_ASCII',
                                      category2=node2['category'],
                                      value2=create_ricgraph_value(value=asc,
                                                                   additional=personroot['value']),
                                      history_event2=history_event)
        node_upd = update_node_value(name='FULL_NAME',
                                     old_value=node2['value'],
                                     new_value=new_value)
        create_name_cache_in_personroot(node=node_upd, personroot=personroot)
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
    for prop_name in RICGRAPH_PROPERTIES_ADDITIONAL:
        print(prop_name + ': ' + node[prop_name])
    print('source:')
    for source in node['_source']:
        print('- ' + source)
    print('history:')
    for history in node['_history']:
        print('- ' + history)
    print('')
    return


# ##############################################################################
# Ricgraph neighbor node and edge functions.
# These start with "get_", not with "read_" as some above.
# The difference is that "get_" functions work in constant time (starting from
# a node) while the "read_" functions read (aka search, find) the whole graph.
# ##############################################################################
def get_personroot_node(node: Node) -> Union[Node, None]:
    """Get the 'person-root' node for any type of node.
    If 'node' is already a 'person-root' node, return 'node'.
    If there is more than one person-root node (which should not happen
    if the category is 'person'), return the first.

    :param node: the node.
    :return: the person-root node.
    """
    personroot_nodes = get_all_personroot_nodes(node)
    if len(personroot_nodes) == 0:
        return None
    else:
        return personroot_nodes[0]


def get_all_personroot_nodes(node: Node) -> list:
    """Get the 'person-root' node(s) for any type of node.
    If 'node' is already a 'person-root' node, return 'node'.
    If there is more than one person-root node (which can happen if
    node is e.g. a research output, and which should not happen
    if the category is 'person'), all will be returned in a list.

    :param node: the node.
    :return: a list of all the person-root nodes found.
    """
    if node is None:
        return []

    if node['name'] == 'person-root':
        return [node]

    personroot_nodes = get_all_neighbor_nodes(node=node,
                                              name_want='person-root')
    return personroot_nodes


def convert_nodes_to_list_of_dict(nodes_list: list,
                                  max_nr_items: str = '0') -> list:
    """Convert a list of nodes to a list of dict.

    :param nodes_list: The list of nodes.
    :param max_nr_items: The maximum number of items to return.
    :return: A list of dicts
    """
    if max_nr_items == '0':
        max_nr_nodes = A_LARGE_NUMBER
    else:
        max_nr_nodes = int(max_nr_items)

    result_list = []
    count = 0
    for node in nodes_list:
        count += 1
        if count > max_nr_nodes:
            break
        result = {}
        for item in node:
            result[item] = node[item]
        result_list.append(result)
    return result_list


# ############################################
# ################### main ###################
# ############################################
# This will be executed on module initialization
RICGRAPH_PROPERTIES_STANDARD = tuple(get_configfile_key(section='Ricgraph',
                                                        key='ricgraph_properties_standard').split(','))
RICGRAPH_PROPERTIES_HIDDEN = tuple(get_configfile_key(section='Ricgraph',
                                                      key='ricgraph_properties_hidden').split(','))
RICGRAPH_PROPERTIES_ADDITIONAL = tuple(get_configfile_key(section='Ricgraph',
                                                          key='ricgraph_properties_additional').split(','))
if len(RICGRAPH_PROPERTIES_STANDARD) == 0 \
   or len(RICGRAPH_PROPERTIES_HIDDEN) == 0 \
   or len(RICGRAPH_PROPERTIES_ADDITIONAL) == 0 \
   or RICGRAPH_PROPERTIES_STANDARD[0] == '' \
   or RICGRAPH_PROPERTIES_HIDDEN[0] == '' \
   or RICGRAPH_PROPERTIES_ADDITIONAL[0] == '':
    print('Ricgraph initialization: error, "ricgraph_properties_standard" and/or')
    print('  "ricgraph_properties_hidden" and/or "ricgraph_properties_additional"')
    print('  are not existing or empty in Ricgraph ini')
    print('  file "' + get_ricgraph_ini_file() + '", exiting.')
    exit(1)

# For more explanation, see file docs/ricgraph_install_configure.md,
# section RICGRAPH_NODEADD_MODE.
RICGRAPH_NODEADD_MODE = get_configfile_key(section='Ricgraph', key='ricgraph_nodeadd_mode')
if RICGRAPH_NODEADD_MODE != 'strict' and RICGRAPH_NODEADD_MODE != 'lenient':
    print('Ricgraph initialization: error, not existing or unknown value "' + RICGRAPH_NODEADD_MODE + '"')
    print('  for "ricgraph_nodeadd_mode" in Ricgraph ini')
    print('  file "' + get_ricgraph_ini_file() + '", exiting.')
    exit(1)

print('Ricgraph is using "' + RICGRAPH_NODEADD_MODE + '" for "ricgraph_nodeadd_mode".')
