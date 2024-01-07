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
# Updated Rik D.T. Janssen, February, March, September to December 2023.
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

All nodes have the properties in RICGRAPH_PROPERTIES_STANDARD and
RICGRAPH_PROPERTIES_HIDDEN (see ricgraph.ini):

In RICGRAPH_PROPERTIES_STANDARD:

- name: name of the node, e.g. ISNI, ORCID, DOI, etc.

- category: category of the node,
  e.g. person, person-root, book, journal article, dataset, etc.

- value: value of the node.

In RICGRAPH_PROPERTIES_HIDDEN:

- _key: key value of the node, not to be modified by the user.

- _source: sorted list of sources a record has been harvested from,
  not to be modified by the user

- _history: list of history events of the node, not to be modified by the user.

Additional properties for nodes can be added by changing entry RICGRAPH_PROPERTIES_ADDITIONAL
in ricgraph.ini (make sure 'history_event' is last).
In the default configuration of Ricgraph, the following properties are included:

- comment: comment for a node, can be anything that is thought to be useful.

- url_main: main URL for a node, pointing to e.g. the corresponding ISNI, ORCID or DOI
  record on the web.

- url_other: other URL for a node, pointing to e.g. the originating record in a source system.

- year: year of a research output.

- source_event: an event to be added to the _source list.

- history_event: an event to be added to the _history list.
"""


import os.path
from datetime import datetime
import numpy
import pandas
import requests
import csv
import uuid
import json
from typing import Union
from collections import defaultdict
from functools import lru_cache, wraps
import configparser

from py2neo import *
from py2neo.matching import *


__author__ = 'Rik D.T. Janssen'
__copyright__ = 'Copyright (c) 2023 Rik D.T. Janssen'
__email__ = ''
__license__ = 'MIT License'
__package__ = 'Ricgraph'
__version__ = ''


# ########################################################################
# Start of constants section
# ########################################################################
LINKS_TO = Relationship.type('LINKS_TO')
RICGRAPH_INI_FILE = '../ricgraph.ini'
RICGRAPH_KEY_SEPARATOR = '|'


# Used for some loop iterations, in case no max iteration for such a loop is specified.
A_LARGE_NUMBER = 9999999999

# Cache size for read_node() function (in number of elements in cache). This
# cannot be read from the config file since it will be read too late.
CACHE_SIZE_READ_NODE = 15000

# ########################################################################
# Research output types used in Ricgraph.
# Harvested sources most often have a type for a research output.
# In a harvest script for a certain source, you specify a mapping
# from the names used in the source you harvest, to the values below.
# This ensures that Ricgraph uses the same wording for types of
# research outputs harvested from different sources.
#
# An example mapping may look like this:
# mapping = {
#    'book': ROTYPE_BOOK,
#    'dataset': ROTYPE_DATASET,
#    'software': ROTYPE_SOFTWARE
# }
#
# Call the function lookup_resout_type() to do this mapping.
# If you add a type, also add it to ROTYPE_ALL.
#
# This list is inspired by the Strategy Evaluation Protocol 2021-2027
# https://www.universiteitenvannederland.nl/files/documenten/Domeinen/Onderzoek/SEP_2021-2027.pdf,
# Appendix E2.
ROTYPE_ABSTRACT = 'abstract'
ROTYPE_BOOK = 'book'
ROTYPE_BOOKCHAPTER = 'book chapter'
ROTYPE_CONFERENCE_ARTICLE = 'conference article'
ROTYPE_DATASET = 'data set'
ROTYPE_DESIGN = 'design'
ROTYPE_DIGITAL_VISUAL_PRODUCT = 'digital or visual product'
ROTYPE_EDITORIAL = 'editorial'
ROTYPE_ENTRY = 'entry for encyclopedia or dictionary'
ROTYPE_EXHIBITION_PERFORMANCE = 'exhibition or performance'
ROTYPE_JOURNAL_ARTICLE = 'journal article'
ROTYPE_LETTER = 'letter to the editor'
ROTYPE_MEMORANDUM = 'memorandum'
ROTYPE_METHOD_DESCRIPTION = 'method description'
ROTYPE_OTHER_CONTRIBUTION = 'other contribution'
ROTYPE_PATENT = 'patent'
ROTYPE_PHDTHESIS = 'PhD thesis'
ROTYPE_POSTER = 'poster'
ROTYPE_PREPRINT = 'preprint'
ROTYPE_PRESENTATION = 'presentation'
ROTYPE_REPORT = 'report'
ROTYPE_REVIEW = 'review'
ROTYPE_SOFTWARE = 'software'
ROTYPE_THESIS = 'thesis'
ROTYPE_WEBSITE = 'website or web publication'

ROTYPE_ALL = [ROTYPE_ABSTRACT,
              ROTYPE_BOOK,
              ROTYPE_BOOKCHAPTER,
              ROTYPE_CONFERENCE_ARTICLE,
              ROTYPE_DATASET,
              ROTYPE_DESIGN,
              ROTYPE_DIGITAL_VISUAL_PRODUCT,
              ROTYPE_EDITORIAL,
              ROTYPE_ENTRY,
              ROTYPE_EXHIBITION_PERFORMANCE,
              ROTYPE_JOURNAL_ARTICLE,
              ROTYPE_LETTER,
              ROTYPE_MEMORANDUM,
              ROTYPE_METHOD_DESCRIPTION,
              ROTYPE_OTHER_CONTRIBUTION,
              ROTYPE_PATENT,
              ROTYPE_PHDTHESIS,
              ROTYPE_POSTER,
              ROTYPE_PREPRINT,
              ROTYPE_PRESENTATION,
              ROTYPE_REPORT,
              ROTYPE_REVIEW,
              ROTYPE_SOFTWARE,
              ROTYPE_THESIS,
              ROTYPE_WEBSITE]

# ########################################################################
# End of constants section
# ########################################################################


global _graph


# Values will only be stored in the cache if the function does not return None
# Used is the property that the standard @lru_cache doesn't do caching when
# an exception is raised within the wrapped function.
# This code is taken from
# https://stackoverflow.com/questions/71175293/make-built-in-lru-cache-skip-caching-when-function-returns-none.
# For extensive documentation of @lru_cache see
# https://docs.python.org/3/library/functools.html#functools.lru_cache.
def ricgraph_lru_cache(maxsize: int = 128, typed: bool = False):
    """This decorator is an LRU cache. It is similar to @lru_cache, with the
    difference that this function does not store values in the cache when
    the function returns None.

    :param maxsize: maximum size of the cache.
    :param typed: if True, function arguments of different types will be cached separately.
    :return: object.
    """
    class FunctionReturnsNoneException(Exception):
        pass

    def decorator(func):
        @lru_cache(maxsize=maxsize, typed=typed)
        def raise_exception_wrapper(*args, **kwargs):
            value = func(*args, **kwargs)
            if value is None:
                raise FunctionReturnsNoneException
            return value

        @wraps(func)
        def handle_exception_wrapper(*args, **kwargs):
            try:
                return raise_exception_wrapper(*args, **kwargs)
            except FunctionReturnsNoneException:
                return None

        handle_exception_wrapper.cache_info = raise_exception_wrapper.cache_info
        handle_exception_wrapper.cache_clear = raise_exception_wrapper.cache_clear
        return handle_exception_wrapper

    if callable(maxsize):
        user_function, maxsize = maxsize, 128
        return decorator(user_function)

    return decorator


def open_ricgraph() -> Graph:
    """Open Ricgraph.

    :return: graph that has been opened.
    """
    global _graph

    print('Opening ricgraph.\n')
    try:
        _graph = Graph(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASSWORD))
    except:
        print('open_ricgraph(): Error opening neo4j graph database using these parameters:')
        print('NEO4J_URL: ' + NEO4J_URL)
        print('NEO4J_USER: ' + NEO4J_USER)
        print('NEO4J_PASSWORD: ' + NEO4J_PASSWORD)
        print('\nAre these parameters correct and did you start neo4j?')
        print('Exiting.')
        exit(1)
    return _graph


def close_ricgraph() -> None:
    """Close Ricgraph.
    """
    global _graph

    print('Closing ricgraph.\n')
    # Seems to be done automatically, so no actual call.
    # In this way it is nicely symmetrical to open_ricgraph().
    return


def empty_ricgraph(answer: str = '') -> None:
    """Empty Ricgraph and create new indexes. Side effect: indexes are deleted and created.

    :param answer: prefilled answer whether the user wants to empty Ricgraph.
      'yes': Ricgraph will be emptied, no questions asked;
      'no': Ricgraph will not be emptied, no questions asked;
      any other answer: the user will be asked whether to empty Ricgraph.
    :return: None.
    """
    global _graph

    if answer == 'yes':
        print('Emptying Ricgraph: Ricgraph will be emptied.\n')
        # Fall through.
    elif answer == 'no':
        print('Emptying Ricgraph: Ricgraph will not be emptied.\n')
        return
    else:
        print('Do you want to empty Ricgraph? You have the following options:')
        print('- "yes": Ricgraph will be emptied.')
        print('- "no": Ricgraph will not be emptied.')
        print('- any other answer: Ricgraph will not be emptied, execution of this script will abort.')
        user_input = input('Please make a choice: ')
        if user_input.lower() == 'yes':
            print('\nRicgraph will be emptied.\n')
            # Fall through.
        elif user_input.lower() == 'no':
            print('\nRicgraph has not been emptied.\n')
            return
        else:
            print('\nRicgraph has not been emptied, exiting.\n')
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
    _graph.run('CREATE TEXT INDEX KeyIndex IF NOT EXISTS FOR(n: RicgraphNode) ON(n._key)')
    _graph.run('CREATE TEXT INDEX NameIndex IF NOT EXISTS FOR(n: RicgraphNode) ON(n.name)')
    _graph.run('CREATE TEXT INDEX CategoryIndex IF NOT EXISTS FOR(n: RicgraphNode) ON(n.category)')
    # graph.run('CREATE TEXT INDEX ValueIndex IF NOT EXISTS FOR(n: RicgraphNode) ON(n.value)')

    print('These indexes have been created (column "state" indicates if they have been generated yet):')
    out = _graph.run('SHOW INDEXES')
    print(out)
    return


def ricgraph_nr_nodes() -> Union[int, None]:
    """Count the number of nodes in Ricgraph.

    :return: the number of nodes.
    """
    global _graph

    if _graph is None:
        print('\nricgraph_nr_nodes(): Error: graph has not been initialized or opened.\n\n')
        return None

    cypher_query = 'MATCH () RETURN COUNT(*) AS count'
    result = _graph.run(cypher_query).data()
    if len(result) == 0:
        return None
    result = result[0]
    if 'count' not in result:
        return None
    result = int(result['count'])
    return result


def ricgraph_nr_edges() -> Union[int, None]:
    """Count the number of edges in Ricgraph.

    :return: the number of edges.
    """
    global _graph

    if _graph is None:
        print('\nricgraph_nr_edges(): Error: graph has not been initialized or opened.\n\n')
        return None

    cypher_query = 'MATCH() -[r]->() RETURN COUNT(r) AS count'
    result = _graph.run(cypher_query).data()
    if len(result) == 0:
        return None
    result = result[0]
    if 'count' not in result:
        return None
    result = int(result['count'])
    return result


def create_ricgraph_key(name: str, value: str) -> str:
    """Create a key for a node.
    This function generates a composite key for a node in a graph.

    :param name: name of the node.
    :param value: value of the node.
    :return: key generated for the node.
    """
    # Check and correct for occurrences of RICGRAPH_KEY_SEPARATOR.
    name = name.replace(RICGRAPH_KEY_SEPARATOR, '#')
    value = value.replace(RICGRAPH_KEY_SEPARATOR, '#')

    return value.lower() + RICGRAPH_KEY_SEPARATOR + name.lower()


def get_namepart_from_ricgraph_key(key: str) -> str:
    """Get the 'name' part from the composite key in a node.

    :param key: key of the node.
    :return: name part of key for the node.
    """
    key_list = key.split(sep=RICGRAPH_KEY_SEPARATOR)
    if len(key_list) != 2:
        return ''
    return key_list[1]


def get_valuepart_from_ricgraph_key(key: str) -> str:
    """Get the 'value' part from the composite key in a node.

    :param key: key of the node.
    :return: value part of key for the node.
    """
    key_list = key.split(sep=RICGRAPH_KEY_SEPARATOR)
    if len(key_list) != 2:
        return ''
    return key_list[0]


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
    elif name == 'GITHUB':
        return 'https://www.github.com/' + value
    elif name == 'ISNI':
        return 'https://isni.org/isni/' + value
    elif name == 'LINKEDIN':
        return 'https://www.linkedin.com/in/' + value
    # elif name == 'OPENALEX':
    #     return 'https://openalex.org/' + value
    elif name == 'ORCID':
        return 'https://orcid.org/' + value
    elif name == 'RESEARCHER_ID':
        return 'https://www.webofscience.com/wos/author/record/' + value
    elif name == 'ROR':
        return 'https://ror.org/' + value
    elif name == 'SCOPUS_AUTHOR_ID':
        return 'https://www.scopus.com/authid/detail.uri?authorId=' + value
    elif name == 'TWITTER':
        return 'https://www.twitter.com/' + value
    else:
        return ''


def create_history_line(property_name: str, old_value: str, new_value: str) -> str:
    """Create a line to be used in the 'history' property of a node.
    """
    return 'Updated property "' + property_name + '" from "' + old_value + '" to "' + new_value + '". '


def create_name_cache_in_personroot(node: Node, personroot: Node):
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
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d-%H%M%S")
        if isinstance(personroot['comment'], str):
            if personroot['comment'] == '':
                old_value = str(personroot['comment'])
                personroot['comment'] = []
                personroot['comment'].append(node['value'])
                history_line = create_history_line(property_name='comment',
                                                   old_value=old_value,
                                                   new_value=str(personroot['comment']))
                personroot['_history'].append(timestamp + ': ' + history_line)
                _graph.push(personroot)
        elif isinstance(personroot['comment'], list):
            if node['value'] not in personroot['comment']:
                old_value = str(personroot['comment'])
                personroot['comment'].append(node['value'])
                history_line = create_history_line(property_name='comment',
                                                   old_value=old_value,
                                                   new_value=str(personroot['comment']))
                personroot['_history'].append(timestamp + ': ' + history_line)
                _graph.push(personroot)
        # In all other cases: it is already in the cache,
        # or leave it as it is: 'comment' seems to be used for something we don't know.

    return


def recreate_name_cache_in_personroot(personroot: Node):
    """This function recreates the cache of all the nodes with 'name' 'FULL_NAME'
    in the 'comment' property of its person-root node 'personroot'.
    If the cache is not present, it is created.

    :param personroot: personroot node of 'node'. For efficiency, we do not check
      if this really is the case.
    :return: No return value.
    """
    if personroot is None:
        return
    neighbornodes = get_all_neighbor_nodes(node=personroot)
    name_cache = []
    for node in neighbornodes:
        if node['name'] == 'FULL_NAME':
            if node['value'] not in name_cache:
                name_cache.append(node['value'])

    if len(name_cache) != 0:
        if (isinstance(personroot['comment'], str) and personroot['comment'] == '') \
           or isinstance(personroot['comment'], list):
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d-%H%M%S")
            history_line = create_history_line(property_name='comment',
                                               old_value=str(personroot['comment']),
                                               new_value=str(name_cache))
            personroot['_history'].append(timestamp + ': Cleaned and recreated name cache. ' + history_line)
            personroot['comment'] = name_cache.copy()
            _graph.push(personroot)
        # In all other cases: leave it as it is: 'comment' seems to be used for something we don't know.
    return


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

    :param name: 'name' property of node.
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
        for prop_name in RICGRAPH_PROPERTIES_ADDITIONAL:
            node_properties[prop_name] = ''
            for other_name, other_value in other_properties.items():
                if prop_name == other_name:
                    node_properties[prop_name] = str(other_value)
                    break

        # If no url_main has been passed, insert an ISNI, DOI, etc. url if category is ISNI, DOI, etc.
        if node_properties['url_main'] == '' and url != '':
            node_properties['url_main'] = url

        if node_properties['source_event'] == '':
            source = []
        else:
            source = [node_properties['source_event']]
        node_properties['source_event'] = ''

        history = [timestamp + ': Created. ' + node_properties['history_event']]
        node_properties['history_event'] = ''
        new_node = Node('RicgraphNode', _key=create_ricgraph_key(name=lname, value=lvalue),
                        _source=source, _history=history,
                        name=lname, category=lcategory, value=lvalue, **node_properties)
        _graph.create(new_node)
        return new_node

    # Update from CRUD
    history_line = ''
    if node['category'] != lcategory:
        # Not necessary to do similar tests for lname, lvalue or _key, since changing one of these
        # means that a new node will be created, which is done in the "if" part above.
        history_line += create_history_line(property_name='category', old_value=node['category'], new_value=lcategory)
        node['category'] = lcategory

    for prop_name in RICGRAPH_PROPERTIES_ADDITIONAL:
        old_val = str(node[prop_name])
        # Note: if a property is not present in other_properties, its value does not change
        for other_name, other_value in other_properties.items():
            other_value_str = str(other_value)
            if prop_name == other_name:
                if old_val != other_value_str:
                    if prop_name != 'history_event' and prop_name != 'source_event':
                        # Do not enter (changes to) property history_event or source_event in _history
                        history_line += create_history_line(property_name=prop_name,
                                                            old_value=node[prop_name], new_value=other_value_str)
                    # Note: for now all properties (except _source and _history) will have string value
                    node[prop_name] = other_value_str
                break

    if node['url_main'] == '' and url != '':
        # If no url_main has been passed, insert an ISNI, DOI, etc. url if category is ISNI, DOI, etc.
        history_line += create_history_line(property_name='url_main', old_value=node['url_main'], new_value=url)
        node['url_main'] = url

    if node['source_event'] != '':
        if node['source_event'] not in node['_source']:
            old_list = node['_source'].copy()
            node['_source'].append(node['source_event'])
            node['_source'].sort()
            history_line += create_history_line(property_name='_source',
                                                old_value=str(old_list), new_value=str(node['_source']))
    node['source_event'] = ''

    if history_line == '':
        # No changes, clear property history_event
        node['history_event'] = ''
        return node

    node['_history'].append(timestamp + ': Updated. ' + history_line)
    node['history_event'] = ''
    # The push() only works after a graph has been created, merge() does not update
    _graph.push(node)

    return node


@ricgraph_lru_cache(maxsize=CACHE_SIZE_READ_NODE)
def read_node(name: str = '', value: str = '') -> Node:
    """Read a node based on name and value.
    Since all nodes are supposed to be unique if both are
    specified, return the first one found.

    :param name: 'name' property of node.
    :param value: 'value' property of node.
    :return: the node read, or None if no node was found.
    """
    first_node = read_all_nodes(name=name, value=value).first()
    return first_node


def read_all_nodes(name: str = '', category: str = '', value: str = '') -> Union[NodeMatch, None]:
    """Read a number of nodes based on name, category or value.
    Any of these parameters can be specified.

    :param name: 'name' property of node.
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

    # Use NodeMatch for more advanced node matching.
    nodes_in_graph = NodeMatcher(_graph)
    if lname != '' and lcategory == '' and lvalue != '':
        # I assume this is faster than querying on both property 'name' and 'value'.
        # You can limit the number nodes by using something like nodes_in_graph.match().limit(1000)
        all_nodes = nodes_in_graph.match('RicgraphNode', _key=create_ricgraph_key(name=lname, value=lvalue))
        return all_nodes

    node_properties = {}
    if lname != '':
        node_properties['name'] = lname
    if lcategory != '':
        node_properties['category'] = lcategory
    if lvalue != '':
        node_properties['value'] = lvalue

    # You can limit the number nodes by using something like nodes_in_graph.match().limit(1000)
    all_nodes = nodes_in_graph.match('RicgraphNode', **node_properties)
    return all_nodes


# Note the similarity with read_all_nodes().
# I only implemented this for property 'value'.
def read_all_nodes_containing_value(name: str = '', category: str = '', value: str = '') -> Union[NodeMatch, None]:
    """Read a number of nodes where property 'value' contains a certain value (a string search).
    If you also specify 'name' and/or 'category', they will be used to restrict the results.

    :param name: 'name' property of node, exact match.
    :param category: 'category' property of node, exact match.
    :param value: 'value' property of node, string search on this property only.
    :return: NodeMatch object, which is a kind of list of nodes read, or None if nothing found
    """
    global _graph

    if _graph is None:
        print('\nread_all_nodes_containing_value(): Error: graph has not been initialized or opened.\n\n')
        return None

    lname = str(name)
    if lname == 'nan':
        lname = ''
    lcategory = str(category)
    if lcategory == 'nan':
        lcategory = ''
    lvalue = str(value)
    if lvalue == 'nan':
        return None
    if lvalue == '':
        return None

    # Prepare Cypher query. String search on property 'value'
    cypher_query = 'toLower(_.value) CONTAINS toLower("' + lvalue + '")'
    if lname != '':
        # Exact match on property 'name', if present.
        cypher_query += ' AND (_.name) = "' + lname + '"'
    if lcategory != '':
        # Exact match on property 'category', if present.
        cypher_query += ' AND (_.category) = "' + lcategory + '"'
    nodes_in_graph = NodeMatch(_graph)
    all_nodes = nodes_in_graph.where(cypher_query)
    return all_nodes


def read_all_values_of_property(node_property: str = '') -> Union[list, None]:
    """Read all the values of a certain property.

    :param node_property: the property to find all values.
    :return: a sorted list with all the values.
    """
    global _graph

    if _graph is None:
        print('\nread_all_values_of_property(): Error: graph has not been initialized or opened.\n\n')
        return None

    if node_property != 'name' \
       and node_property != 'category' \
       and node_property != '_source':
        print('\nread_all_values_of_property(): Error: function does not work for property "'
              + node_property + '".\n\n')
        return None

    cypher_query = 'MATCH (p:RicgraphNode) RETURN COLLECT(DISTINCT p.' + node_property + ') AS entries'
    result = _graph.run(cypher_query).data()
    if len(result) == 0:
        return None
    result = result[0]
    if 'entries' not in result:
        return None
    result_list = result['entries']
    if len(result_list) == 0:
        return None
    if node_property == '_source':
        # This is a special case, we have a list of lists that we need to untangle.
        list_of_lists = result_list
        result_list = []
        for item in list_of_lists:
            if len(item) == 0:
                continue
            for encapsulated_item in item:
                if encapsulated_item not in result_list:
                    result_list.append(encapsulated_item)

    # We need 'key' to do a case insenstive search.
    result_list_sorted = sorted(result_list, key=str.lower)
    return result_list_sorted


def update_node(name: str, category: str, value: str,
                **other_properties: dict) -> Node:
    """Update a node.

    :param name: 'name' property of node.
    :param category: idem.
    :param value: idem.
    :param other_properties: a dictionary of all the other properties.
    :return: the node updated, or None if this was not possible
    """
    node = create_node(name=name, category=category, value=value, **other_properties)
    return node


def update_node_value(name: str, old_value: str, new_value: str) -> Union[Node, None]:
    """Update a node, change the value property.
    This is a special case of update_node() because we change the key. Therefore,
    a lot of restrictions apply which do not apply with update_node().
    Use carefully, because other property that contain 'old_value' (such
    as 'url_main' or 'url_other') are not being updated, so they will
    point to the wrong URL.

    :param name: 'name' property of node.
    :param old_value: old 'value' property of node.
    :param new_value: old 'value' property of node.
    :return: the node updated, or None if this was not possible
    """
    # A lot of the code below is copied from create_node().
    global _graph

    if _graph is None:
        print('\nupdate_node_value(): Error: graph has not been initialized or opened.\n\n')
        return None

    lname = str(name)
    loldvalue = str(old_value)
    lnewvalue = str(new_value)

    if lname == '' or loldvalue == '' or lnewvalue == '' \
       or lname == 'nan' or loldvalue == 'nan' or lnewvalue == 'nan':
        return None

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    node = read_node(name=lname, value=loldvalue)
    if node is None:
        # Node we want to change does not exist.
        return None

    newnode = read_node(name=lname, value=lnewvalue)
    if newnode is not None:
        # Node we want to change to does already exist.
        # We should do a merge of these two nodes, but merge does not work
        # satisfactorily (there is code for it, but it has not been tested
        # extensively). Therefore, we do not change.
        print('update_node_value(): Error: new node already exists, this should not happen.')
        print('Nothing has been changed.')
        return None

    # Create from CRUD
    node['value'] = lnewvalue
    oldkey = node['_key']
    newkey = create_ricgraph_key(name=lname, value=lnewvalue)
    node['_key'] = newkey
    history_line = create_history_line(property_name='value', old_value=loldvalue, new_value=lnewvalue)
    history_line += create_history_line(property_name='_key', old_value=oldkey, new_value=newkey)
    node['_history'].append(timestamp + ': Updated. ' + history_line)

    # The push() only works after a graph has been created, merge() does not update
    _graph.push(node)
    if node['name'] == 'FULL_NAME':
        personroot = get_or_create_personroot_node(person_node=node)
        recreate_name_cache_in_personroot(personroot=personroot)
    return node


# Note the similarity with create_nodepairs_and_edges_df().
def update_nodes_df(nodes: pandas.DataFrame) -> None:
    """Update the values in a node, but only if values have been changed.
    This is done for all the nodes passed in the DataFrame.

    The column names specify the property in a node (i.e. 'name', 'category', 'value').
    The row value of that column specify the property value of that property.

    :param nodes: the nodes in a DataFrame.
    :return: None.
    """
    nodes_clean = nodes.copy(deep=True)
    # Ensure that all '' values are NaN, so that those rows can be easily removed with dropna()
    nodes_clean.replace('', numpy.nan, inplace=True)
    nodes_clean.dropna(axis=0, how='any', inplace=True)
    nodes_clean.drop_duplicates(keep='first', inplace=True, ignore_index=True)

    print('\nCache used at start of function: ' + str(read_node.cache_info()) + '.')
    print('There are ' + str(len(nodes_clean)) + ' nodes, updating node: 0  ', end='')
    count = 0
    columns = nodes_clean.columns
    for row in nodes_clean.itertuples():
        count += 1
        if count % 250 == 0:
            print(count, ' ', end='', flush=True)
        if count % 10000 == 0:
            print('\n', end='', flush=True)

        node_properties = {}
        for prop_name in RICGRAPH_PROPERTIES_ADDITIONAL:
            for other_name in columns:
                if prop_name == other_name:
                    node_properties[prop_name] = getattr(row, other_name)

        update_node(name=row.name, category=row.category, value=row.value,
                    **node_properties)

    print(count, '\n', end='', flush=True)
    print('Cache used at end of function: ' + str(read_node.cache_info()) + '.')
    return


def delete_node(name: str, value: str) -> None:
    """Delete a node based on name and value.

    :param name: 'name' property of node.
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


def get_or_create_personroot_node(person_node: Node) -> Union[Node, None]:
    """Get a 'person-root' node for a given 'person' node, if that node has
    a 'person-root'. If not, create the 'person-root' node.

    :param person_node: the node.
    :return: the 'person-root' node, or None on error.
    """
    global _graph

    if person_node is None:
        print('get_or_create_personroot_node(): Error: node is None.')
        return

    if person_node['category'] != 'person':
        print('get_or_create_personroot_node(): node category is not person.')
        return None

    if person_node['name'] == 'person-root':
        return person_node

    nr_edges = len(get_edges(node=person_node))
    if nr_edges == 0:
        # Create the 'person-root' node with a unique value.
        value = str(uuid.uuid4())
        personroot = create_node(name='person-root', category='person', value=value)
        edge1 = LINKS_TO(person_node, personroot)
        edge2 = LINKS_TO(personroot, person_node)
        _graph.merge(edge1 | edge2, 'RicgraphNode', '_key')
        return personroot

    personroot_nodes = get_all_personroot_nodes(node=person_node)
    if personroot_nodes is None or len(personroot_nodes) == 0:
        # Should have been caught above.
        print('get_or_create_personroot_node(): not anticipated: person_node "'
              + person_node['_key'] + '" has zero person-root nodes.')
        return None

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
    global _graph

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

    edge1 = LINKS_TO(non_person_node, personroot)
    edge2 = LINKS_TO(personroot, non_person_node)
    _graph.merge(edge1 | edge2, 'RicgraphNode', '_key')
    return


def merge_two_personroot_nodes(left_personroot_node: Node, right_personroot_node: Node) -> None:
    """Merge two 'person-root' nodes. Or do nothing if they are the same.

    :param left_personroot_node: the left person-root node.
    :param right_personroot_node: the right person-root node.
    :return: None.
    """
    global _graph

    if left_personroot_node is None or right_personroot_node is None:
        print('merge_two_personroot_nodes(): Error: (one of the) nodes is None.')
        return

    if left_personroot_node['name'] != 'person-root' \
       or right_personroot_node['name'] != 'person-root':
        print('merge_two_personroot_nodes(): not anticipated: (one of the) nodes '
              + 'are not "person-root".')
        return

    if left_personroot_node == right_personroot_node:
        # They are already connected, we are done.
        return

    # There are two possible reasons why it can happen that two person-root nodes
    # of two nodes to insert are different:
    # (1) It can happen e.g. in case a personal ID (ISNI, ORCID, etc.) is assigned
    #     to two or more different persons.
    #     Of course, that should not happen. Most probably this in a typo in a source system.
    # (2) The two nodes refer to the same person, but originate from different source
    #     systems.
    #     E.g. harvest of system 1 results in ORCID and ISNI of the same person, which have a
    #     common person-root. Harvest of system 2 results in EMAIL with another person-root.
    #     Now a subsequent harvest results in ORCID and EMAIL of the same person. Then there
    #     are two different person-roots which need to be merged.
    # Both can happen, but we cannot know if it is either (1) or (2).

    now = datetime.now()
    timestamp = now.strftime('%Y%m%d-%H%M%S')
    count = 0
    what_happened = timestamp + '-' + format(count, '02d') + ': '
    what_happened += 'Merged person-root node "'
    what_happened += right_personroot_node['_key'] + '" to this person-root node '
    what_happened += 'and then deleted it. This was the history of the deleted node:'
    left_personroot_node['_history'].append(what_happened)
    for history in right_personroot_node['_history']:
        count += 1
        what_happened = timestamp + '-' + format(count, '02d') + ': '
        what_happened += history
        left_personroot_node['_history'].append(what_happened)

    count += 1
    what_happened = timestamp + '-' + format(count, '02d') + ': '
    what_happened += 'End of history of the deleted node.'
    left_personroot_node['_history'].append(what_happened)

    count += 1
    what_happened = timestamp + '-' + format(count, '02d') + ': '
    what_happened += 'These were the neighbors of the deleted node, '
    what_happened += 'now merged with the neighbors of this node:'
    left_personroot_node['_history'].append(what_happened)

    count += 1
    what_happened = timestamp + '-' + format(count, '02d') + ': '
    for edge_from_right_node in get_edges(right_personroot_node):
        right_node = edge_from_right_node.end_node
        if right_node is None:
            continue
        if right_node == right_personroot_node:
            continue

        what_happened += '"' + str(right_node['_key']) + '" '
        edge_delete1 = LINKS_TO(right_personroot_node, right_node)
        edge_delete2 = LINKS_TO(right_node, right_personroot_node)
        edge_create1 = LINKS_TO(left_personroot_node, right_node)
        edge_create2 = LINKS_TO(right_node, left_personroot_node)
        # _graph.delete() also deletes 'right_personroot_node'.
        # TODO: There seems to be a bug here. It does not only delete 'right_personroot_node', but sometimes it also
        #   deletes other nodes which have more than one edge, such as an 'organization' node connected to multiple
        #   person-root nodes (including right_personroot_node).
        #   The problem is that _graph.separate() does not seem to work, which seems to be the 'best' function
        #   since it only deletes edges. Use with caution (or don't use).
        _graph.delete(edge_delete1)
        _graph.delete(edge_delete2)
        _graph.merge(edge_create1 | edge_create2, 'RicgraphNode', '_key')

    what_happened += '.'
    left_personroot_node['_history'].append(what_happened)

    count += 1
    what_happened = timestamp + '-' + format(count, '02d') + ': '
    what_happened += 'End of list of neighbors of the deleted node.'
    left_personroot_node['_history'].append(what_happened)
    _graph.push(left_personroot_node)
    return


def merge_personroots_of_two_nodes(name1: str, value1: str,
                                   name2: str, value2: str) -> None:

    """Merge two 'person-root' nodes, by specifying one of its neighbors.
    Or do nothing if their person-roots are already the same node.

    :param name1: 'name' property of left node.
    :param value1: 'value' property of left node.
    :param name2: 'name' property of right node.
    :param value2: 'value' property of right node.
    :return: None.
    """
    left_node = read_node(name=name1, value=value1)
    right_node = read_node(name=name2, value=value2)
    if left_node is None or right_node is None:
        return

    left_personroot_node = get_or_create_personroot_node(person_node=left_node)
    right_personroot_node = get_or_create_personroot_node(person_node=right_node)
    if left_personroot_node is None or right_personroot_node is None:
        return

    if left_personroot_node == right_personroot_node:
        # They are already connected, we are done.
        return

    merge_two_personroot_nodes(left_personroot_node=left_personroot_node,
                               right_personroot_node=right_personroot_node)
    return


def connect_person_and_person_node(left_node: Node, right_node: Node) -> None:
    """Connect two person nodes.

    :param left_node: the left node.
    :param right_node: the right node.
    :return: None.
    """
    global _graph

    if left_node is None or right_node is None:
        print('connect_person_and_person_node(): (one of the) nodes is None.')
        return

    if left_node['category'] != 'person' or right_node['category'] != 'person':
        print('connect_person_and_person_node(): (one of the) nodes have wrong category.')
        return

    if left_node['name'] == 'person-root' or right_node['name'] == 'person-root':
        print('connect_person_and_person_node(): not anticipated: (one of the) person_nodes '
              + 'are "person-root" nodes.')
        return

    nr_edges_left_node = len(get_edges(node=left_node))
    nr_edges_right_node = len(get_edges(node=right_node))
    if nr_edges_left_node == 0 and nr_edges_right_node == 0:
        # None of the nodes have a 'person-root' node, create one and connect.
        personroot = get_or_create_personroot_node(person_node=left_node)
        if personroot is None:
            return
        edge1 = LINKS_TO(right_node, personroot)
        edge2 = LINKS_TO(personroot, right_node)
        _graph.merge(edge1 | edge2, 'RicgraphNode', '_key')
        return

    if nr_edges_left_node > 0 and nr_edges_right_node == 0:
        # 'left_node' already has a 'person-root' node.
        personroot = get_or_create_personroot_node(person_node=left_node)
        if personroot is None:
            return
        edge1 = LINKS_TO(right_node, personroot)
        edge2 = LINKS_TO(personroot, right_node)
        _graph.merge(edge1 | edge2, 'RicgraphNode', '_key')
        return

    if nr_edges_left_node == 0 and nr_edges_right_node > 0:
        # 'right_node' already has a 'person-root' node.
        personroot = get_or_create_personroot_node(person_node=right_node)
        if personroot is None:
            return
        edge1 = LINKS_TO(left_node, personroot)
        edge2 = LINKS_TO(personroot, left_node)
        _graph.merge(edge1 | edge2, 'RicgraphNode', '_key')
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
    edge1 = LINKS_TO(left_node, right_personroot_node)
    edge2 = LINKS_TO(right_personroot_node, left_node)
    edge3 = LINKS_TO(right_node, left_personroot_node)
    edge4 = LINKS_TO(left_personroot_node, right_node)
    _graph.merge(edge1 | edge2 | edge3 | edge4, 'RicgraphNode', '_key')

    now = datetime.now()
    timestamp = now.strftime('%Y%m%d-%H%M%S')
    message = 'The node pair "'
    message += left_node['_key'] + '" and "' + right_node['_key']
    message += '" caused this node to have more than one neighbor. '
    message += 'These are its person-root nodes: "'
    message += left_personroot_node['_key'] + '" and "'
    message += right_personroot_node['_key'] + '". '
    message += 'This might be caused by a mislabeling in a harvested system.'
    timestamped_message = timestamp + ': ' + message

    print('\nconnect_person_and_person_node(): ' + message)
    left_node['_history'].append(timestamped_message)
    right_node['_history'].append(timestamped_message)
    _graph.push(left_node)
    _graph.push(right_node)
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
    global _graph

    if left_node is None or right_node is None:
        return

    if left_node['category'] != 'person' and right_node['category'] != 'person':
        # This is not a person to person link, link directly
        edge1 = LINKS_TO(left_node, right_node)
        edge2 = LINKS_TO(right_node, left_node)

        # Do a "merge" instead of a "create" to prevent double edges.
        _graph.merge(edge1 | edge2, 'RicgraphNode', '_key')
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

    node1 = create_node(name=name1, category=category1, value=value1, **node_properties1)
    node2 = create_node(name=name2, category=category2, value=value2, **node_properties2)
    if node1 is None or node2 is None:
        return

    connect_two_nodes(left_node=node1, right_node=node2)
    if node1['name'] == 'FULL_NAME':
        personroot = get_or_create_personroot_node(person_node=node1)
        create_name_cache_in_personroot(node=node1, personroot=personroot)
    if node2['name'] == 'FULL_NAME':
        personroot = get_or_create_personroot_node(person_node=node2)
        create_name_cache_in_personroot(node=node2, personroot=personroot)
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
    # read_node.cache_clear()           # Optional, we don't need this for now.
    print('\nCache used at start of function: ' + str(read_node.cache_info()) + '.')
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
        for prop_name in RICGRAPH_PROPERTIES_ADDITIONAL:
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
    print('Cache used at end of function: ' + str(read_node.cache_info()) + '.')
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

    :param name1: 'name' property of left node.
    :param category1: idem.
    :param value1: idem.
    :param name2: 'name' property of right node.
    :param category2: idem.
    :param value2: idem.
    :param other_properties: a dictionary of all the other properties.
                             Names ending with '1' belong to a 'left' node,
                             names ending with '2' to a 'right' node.
    :return: None.
    """
    if isinstance(value1, str):
        left_and_right_nodepairs = pandas.DataFrame(data={'value1': value1},
                                                    index=[0])
    else:
        left_and_right_nodepairs = pandas.DataFrame(data=value1).copy(deep=True)
        left_and_right_nodepairs.rename(columns={value1.name: 'value1'}, inplace=True)

    # This makes programming more efficient
    allowed_properties = RICGRAPH_PROPERTIES_ADDITIONAL + RICGRAPH_PROPERTIES_STANDARD
    ext_other_properties = other_properties.copy()
    ext_other_properties['name1'] = name1
    ext_other_properties['name2'] = name2
    ext_other_properties['category1'] = category1
    ext_other_properties['category2'] = category2
    # 'value1' has been included above
    ext_other_properties['value2'] = value2

    for prop_name in allowed_properties:
        for other_name in ext_other_properties:
            other_value = ext_other_properties[other_name]
            if prop_name + '1' == other_name:
                if isinstance(other_value, str):
                    left_and_right_nodepairs[prop_name + '1'] = other_value
                else:
                    left_and_right_nodepairs = pandas.concat([left_and_right_nodepairs, other_value], axis='columns')
                    left_and_right_nodepairs.rename(columns={other_value.name: prop_name + '1'}, inplace=True)

            if prop_name + '2' == other_name:
                if isinstance(other_value, str):
                    left_and_right_nodepairs[prop_name + '2'] = other_value
                else:
                    left_and_right_nodepairs = pandas.concat([left_and_right_nodepairs, other_value], axis='columns')
                    left_and_right_nodepairs.rename(columns={other_value.name: prop_name + '2'}, inplace=True)

    # Reorder a bit, starting with the last, only the name-category-value property, since they will surely exist
    left_and_right_nodepairs.insert(0, 'value2', left_and_right_nodepairs.pop('value2'))
    left_and_right_nodepairs.insert(0, 'category2', left_and_right_nodepairs.pop('category2'))
    left_and_right_nodepairs.insert(0, 'name2', left_and_right_nodepairs.pop('name2'))
    left_and_right_nodepairs.insert(0, 'value1', left_and_right_nodepairs.pop('value1'))
    left_and_right_nodepairs.insert(0, 'category1', left_and_right_nodepairs.pop('category1'))
    left_and_right_nodepairs.insert(0, 'name1', left_and_right_nodepairs.pop('name1'))

    create_nodepairs_and_edges_df(left_and_right_nodepairs=left_and_right_nodepairs)
    return


def unify_personal_identifiers(personal_identifiers: pandas.DataFrame,
                               source_event: Union[dict, str], history_event: Union[dict, str]) -> None:
    """Unify a collection of personal identifiers (e.g. ORCID, ISNI, etc.).
    That means that every column is unified to every other column.
    The identifiers are specified as columns in a DataFrame.

    :param personal_identifiers: DataFrame containing personal identifiers.
    :param source_event: an event to add to the _source list.
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

            if RICGRAPH_NODEADD_MODE == 'strict':
                # Remove rows which have a cell value that occurs more than once.
                # E.g. if we have a DataFrame:
                # FULL_NAME     ORCID
                # Name1         10
                # Name2         11
                # Name3         11
                # then we remove both rows with ORCID 11.
                # For more explanation, see file docs/ricgraph_install_configure.md,
                # section RICGRAPH_NODEADD_MODE.
                identifiers.drop_duplicates(subset=column1, keep=False, inplace=True, ignore_index=True)
                identifiers.drop_duplicates(subset=column2, keep=False, inplace=True, ignore_index=True)

            create_nodepairs_and_edges_params(name1=column1, category1='person', value1=identifiers[column1],
                                              name2=column2, category2='person', value2=identifiers[column2],
                                              source_event1=source_event, source_event2=source_event,
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
    :return: the list of neighboring nodes satisfying all these criteria.
    """
    global _graph

    if _graph is None:
        print('\nget_all_neighbor_nodes(): Error: graph has not been initialized or opened.\n\n')
        return []

    if node is None:
        return []

    edges = get_edges(node)
    if len(edges) == 0:
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
    for edge in edges:
        if count >= max_nr_neighbor_nodes:
            break
        next_node = edge.end_node
        if node == next_node:
            continue
        if next_node['name'] in name_dontwant_list:
            continue
        if next_node['category'] in category_dontwant_list:
            continue
        if len(name_want) == 0 and len(category_want) == 0:
            neighbor_nodes.append(next_node)
            count += 1
            continue
        if next_node['name'] in name_want_list \
           and next_node['category'] in category_want_list:
            neighbor_nodes.append(next_node)
            count += 1
            continue
        if next_node['name'] in name_want_list and len(category_want_list) == 0:
            neighbor_nodes.append(next_node)
            count += 1
            continue
        if len(name_want_list) == 0 and next_node['category'] in category_want_list:
            neighbor_nodes.append(next_node)
            count += 1
            continue
        # Any other next_node we do not want.

    return neighbor_nodes


def get_all_neighbor_nodes_person(node: Node,
                                  max_nr_neighbor_nodes: int = 0) -> list:
    """Get all the 'person' neighbor nodes connected to 'node',
    also including 'node'.

    :param node: the node.
    :param max_nr_neighbor_nodes: return at most this number of nodes, 0 = all nodes.
    :return: all person nodes connected to 'node'.
    """
    if node is None:
        return []

    personroot = get_personroot_node(node)
    if personroot is None:
        return []

    neighbor_nodes = get_all_neighbor_nodes(node=personroot,
                                            category_want='person',
                                            max_nr_neighbor_nodes=max_nr_neighbor_nodes)
    neighbor_nodes.append(personroot)

    return neighbor_nodes


# ##############################################################################
# Utility functions
# ##############################################################################

def create_multidimensional_dict(dimension: int, dict_type):
    """Create a multimensional dict.
    Non-existing keys will be added automatically.
    From https://stackoverflow.com/questions/29348345/declaring-a-multi-dimensional-dictionary-in-python,
    the second answer.

    Example use:
    new_dict = create_multidimensional_dict(2, int)
    new_dict['key1']['key2'] += 5

    :param dimension: dimension of the dict.
    :param dict_type: type of the dict.
    :return: the dict.
    """
    if dimension == 0:
        return None
    if dimension == 1:
        return defaultdict(dict_type)
    else:
        return defaultdict(lambda: create_multidimensional_dict(dimension=dimension - 1,
                                                                dict_type=dict_type))


def lookup_resout_type(research_output_type: str,
                       research_output_mapping: dict) -> str:
    """Convert a research output type from a harvested system
    to a shorter and easier Ricgraph research output type, according to a certain mapping.
    The reason for doing this is to ensure a constant naming of research output
    types for objects harvested from different sources.
    For more explanation, see the text at 'Research output types used in Ricgraph' at
    the start of this file.

    :param research_output_type: A research output type from a source system.
    :param research_output_mapping: The mapping from the source system to Ricgraph
    research output types.
    :return: The result, in a few words.
    """
    if research_output_type == '':
        print('lookup_resout_type(): no research output type specified .')
        return 'empty'

    if research_output_type not in research_output_mapping:
        print('lookup_resout_type(): unknown research output type: "' + research_output_type + '".')
        return 'unknown'

    return research_output_mapping[research_output_type]


# #####
# Note:
# This function was written using the JSON harvested by the following python files:
# - GET: harvest_openalex_to_ricgraph.py.
# - POST: harvest_pure_to_ricgraph.py.
#
# Possibly for other harvests some changes should be made. Please also test the result
# with the above-mentioned files, and add the filename of the new harvest script.
# #####
def harvest_json(url: str, headers: dict, body: dict = None, max_recs_to_harvest: int = 0, chunksize: int = 0) -> list:
    """Harvest json data from a file.

    :param url: URL to harvest.
    :param headers: headers required.
    :param body: the body of a POST request, or [] for a GET request.
    :param max_recs_to_harvest: maximum records to harvest.
    :param chunksize: chunk size to use (i.e. the number of records harvested in one call to 'url').
    :return: list of records in json format, or empty list if nothing found.
    """
    if body is None:
        body = []

    print('Harvesting json data from ' + url + '.')
    print('Getting data...')

    all_records = A_LARGE_NUMBER
    if max_recs_to_harvest == 0:
        max_recs_to_harvest = all_records
    if chunksize == 0:
        chunksize = 1
    if len(body) == 0:
        # GET http request
        request_type = 'get'
        url += '&per_page=' + str(chunksize)
    else:
        # POST http request
        request_type = 'post'
        body['size'] = chunksize

    # Do a first harvest to determine the number of records to harvest.
    if request_type == 'get':
        response = requests.get(url=url, headers=headers)
    else:
        response = requests.post(url=url, headers=headers, json=body)

    if response.status_code != requests.codes.ok:
        print('harvest_json(): error during harvest, possibly '
              + 'a missing API-key or mixed up POST body?')
        print('Status code: ' + str(response.status_code))
        print('Url: ' + response.url)
        print('Error: ' + response.text)
        exit(1)

    chunk_json_data = response.json()
    total_records = 0
    if request_type == 'get':
        if 'meta' in chunk_json_data:
            if 'count' in chunk_json_data['meta']:
                total_records = chunk_json_data['meta']['count']
    else:
        if 'count' in chunk_json_data:
            total_records = chunk_json_data['count']

    if total_records == 0:
        print('harvest_json(): Warning: malformed json, "count" is missing.')

    if max_recs_to_harvest == all_records:
        print('There are ' + str(total_records)
              + ' records, harvesting in chunks of ' + str(chunksize)
              + ' items.')
    else:
        print('There are ' + str(total_records)
              + ' records, harvesting in chunks of ' + str(chunksize)
              + ', at most ' + str(max_recs_to_harvest) + ' items.')

    print('Harvesting record: ', end='', flush=True)

    json_data = []
    records_harvested = 0
    page_nr = 1
    # And now start the real harvesting.
    while records_harvested <= max_recs_to_harvest:
        if request_type == 'get':
            url_page = url + '&page=' + str(page_nr)
            response = requests.get(url=url_page, headers=headers)
        else:
            if max_recs_to_harvest - records_harvested <= chunksize:
                # We have to harvest the last few (< chunksize).
                body['size'] = max_recs_to_harvest - records_harvested
            body['offset'] = records_harvested
            response = requests.post(url=url, headers=headers, json=body)

        if response.status_code != requests.codes.ok:
            print('harvest_json(): error during harvest, possibly '
                  + 'a missing API-key or mixed up POST body?')
            print('Status code: ' + str(response.status_code))
            print('Url: ' + response.url)
            print('Error: ' + response.text)
            exit(1)

        chunk_json_data = response.json()
        if request_type == 'get':
            if 'results' not in chunk_json_data:
                print('harvest_json(): Error: malformed json, "results" is missing.')
                return []
            if len(chunk_json_data['results']) == 0:
                break
            json_items = chunk_json_data['results']
        else:
            if 'items' not in chunk_json_data:
                print('harvest_json(): Error: malformed json, "items" is missing.')
                return []
            if len(chunk_json_data['items']) == 0:
                break
            json_items = chunk_json_data['items']

        json_data += json_items
        print(records_harvested, ' ', end='', flush=True)
        if page_nr % 20 == 0:
            if page_nr != 0:
                print('\n', end='', flush=True)
        records_harvested += chunksize
        page_nr += 1

    print(' Done.\n', end='', flush=True)
    return json_data


def harvest_json_and_write_to_file(filename: str, url: str, headers: dict, body: dict = None,
                                   max_recs_to_harvest: int = 0, chunksize: int = 0) -> list:
    """Harvest json data and write the data found to a file.
    This data is a list of records in json format. If no records are harvested, nothing is written.

    :param filename: filename of the file to use for writing.
    :param url: URL to harvest.
    :param headers: headers required.
    :param body: the body of a POST request, or '' for a GET request.
    :param max_recs_to_harvest: maximum records to harvest.
    :param chunksize: chunk size to use (i.e. the number of records harvested in one call to 'url').
    :return: list of records in json format, or empty list if nothing found.
    """
    if body is None:
        body = []

    json_data = harvest_json(url=url,
                             headers=headers,
                             body=body,
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


def print_commandline_arguments(argument_list: list) -> None:
    """Print the script name and all command line arguments.

    :param argument_list: the argument list.
    :return: None.
    """
    if len(argument_list) == 0:
        print('print_commandline_arguments(): Error, empty argument_list passed, exiting.')
        exit(1)

    print('\nScript name: ' + argument_list[0])
    if len(argument_list) == 1:
        print('Command line arguments: [none]')
    else:
        print('Command line arguments: '
              + ' '.join([str(arg) for arg in argument_list[1:]])
              + '\n')
    return


def get_commandline_argument(argument: str, argument_list: list) -> str:
    """Get the value of a command line argument

    :param argument: the command line argument name.
    :param argument_list: the argument list.
    :return: the value that belongs to 'argument'.
    """
    length = len(argument_list)
    if length == 0:
        print('get_commandline_argument(): Error, empty argument_list passed, exiting.')
        exit(1)

    if str(argument) == '':
        # No argument passed.
        return ''

    if length == 1:
        # The argument list contains the script name only.
        return ''

    for i in range(1, length - 1):
        if str(argument_list[i]) == str(argument):
            if i + 1 <= length:
                # Only get the next index if we are still in the array bounds.
                return str(argument_list[i + 1])
    return ''


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
    RICGRAPH_PROPERTIES_STANDARD = tuple(config['Ricgraph']['ricgraph_properties_standard'].split(','))
    RICGRAPH_PROPERTIES_HIDDEN = tuple(config['Ricgraph']['ricgraph_properties_hidden'].split(','))
    RICGRAPH_PROPERTIES_ADDITIONAL = tuple(config['Ricgraph']['ricgraph_properties_additional'].split(','))
    if len(RICGRAPH_PROPERTIES_STANDARD) == 0 \
       or len(RICGRAPH_PROPERTIES_HIDDEN) == 0 \
       or len(RICGRAPH_PROPERTIES_ADDITIONAL) == 0:
        print('Ricgraph initialization: error, ricgraph_properties_standard and/or')
        print('  ricgraph_properties_hidden and/or ricgraph_properties_additional')
        print('  are empty in Ricgraph ini file, exiting.')
        exit(1)

    if RICGRAPH_PROPERTIES_STANDARD[0] == '' \
       or RICGRAPH_PROPERTIES_HIDDEN[0] == '' \
       or RICGRAPH_PROPERTIES_ADDITIONAL[0] == '':
        print('Ricgraph initialization: error, ricgraph_properties_standard and/or')
        print('  ricgraph_properties_hidden and/or ricgraph_properties_additional')
        print('  are empty in Ricgraph ini file, exiting.')
        exit(1)

    # For more explanation, see file docs/ricgraph_install_configure.md,
    # section RICGRAPH_NODEADD_MODE.
    RICGRAPH_NODEADD_MODE = config['Ricgraph']['ricgraph_nodeadd_mode']
    if RICGRAPH_NODEADD_MODE != 'strict' and RICGRAPH_NODEADD_MODE != 'lenient':
        print('Ricgraph initialization: error, unknown value "' + RICGRAPH_NODEADD_MODE
              + '" for ricgraph_nodeadd_mode in Ricgraph ini file, exiting.')
        exit(1)
    else:
        print('Ricgraph is using "' + RICGRAPH_NODEADD_MODE + '" for ricgraph_nodeadd_mode.')
except KeyError:
    print('Ricgraph initialization: error, ricgraph_properties_standard and/or')
    print('  ricgraph_properties_hidden and/or ricgraph_properties_additional and/or ricgraph_nodeadd_mode')
    print('  not found in Ricgraph ini file, exiting.')
    exit(1)

try:
    NEO4J_HOSTNAME = config['Neo4j']['neo4j_hostname']
    NEO4J_USER = config['Neo4j']['neo4j_user']
    NEO4J_PASSWORD = config['Neo4j']['neo4j_password']
    NEO4J_SCHEME = config['Neo4j']['neo4j_scheme']
    NEO4J_PORT = config['Neo4j']['neo4j_port']
    if NEO4J_HOSTNAME == '' or NEO4J_USER == '' or NEO4J_PASSWORD == '' \
       or NEO4J_SCHEME == '' or NEO4J_PORT == '':
        print('Ricgraph initialization: error, one or more of Neo4j parameters '
              + 'empty in Ricgraph ini file, exiting.')
        exit(1)
    NEO4J_URL = '{scheme}://{hostname}:{port}'.format(scheme=NEO4J_SCHEME, hostname=NEO4J_HOSTNAME, port=NEO4J_PORT)
except KeyError:
    print('Ricgraph initialization: error, one or more of Neo4j parameters '
          + 'not found in Ricgraph ini file, exiting.')
    exit(1)

# Make sure DataFrames are printed with all columns on full width
pandas.set_option('display.max_columns', None)
pandas.set_option('display.width', 500)
