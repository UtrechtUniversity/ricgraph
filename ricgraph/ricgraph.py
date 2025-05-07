# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
# 
# Copyright (c) 2023, 2024, 2025 Rik D.T. Janssen
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
# Updated Rik D.T. Janssen, February to June, September to December  2024.
# Updated Rik D.T. Janssen, January to June 2025.
#
# ########################################################################


"""Ricgraph - Research in context graph.

This is Ricgraph - Research in context graph, a graph structure with nodes and edges
to represent information (as properties in the nodes)
and their relations (the edges). You can find the code and documentation on
https://github.com/UtrechtUniversity/ricgraph/.

Ricgraph uses Neo4j as graph database, https://neo4j.com.
Neo4j only allows directed graphs, so Ricgraph is a directed graph.
They have several products. Their free products are:

- Neo4j Desktop (https://neo4j.com/download-center/#desktop);

- Neo4j Community Edition (https://neo4j.com/download-center/#community).

Neo4j Desktop includes Bloom, which allows exploring the graph in a more
intuitive way. Community Edition allows only Cypher queries.

Ricgraph can be extended for other brands of graph databases
by changing minor bits of the code.

All nodes have the properties in RICGRAPH_PROPERTIES_STANDARD and
RICGRAPH_PROPERTIES_HIDDEN (see ricgraph.ini):

In RICGRAPH_PROPERTIES_STANDARD:

- name: name of the node, e.g. ISNI, ORCID, DOI, etc.

- category: category of the node,
  e.g. person, person-root, book, journal article, data set, etc.

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


import numpy
import pandas
from typing import Union
from .ricgraph_graphdb import (timestamp,
                               create_update_node, create_two_nodes_and_edge,
                               RICGRAPH_NODEADD_MODE,
                               RICGRAPH_PROPERTIES_STANDARD, RICGRAPH_PROPERTIES_ADDITIONAL)


__author__ = 'Rik D.T. Janssen'
__copyright__ = 'Copyright (c) 2023, 2024, 2025 Rik D.T. Janssen'
__email__ = ''
__license__ = 'MIT License'
__package__ = 'Ricgraph'

# __version__ should be placed here instead of in __init__.py.
# If not here, it cannot be found when executing something like
# PYTHONPATH=../ricgraph ../bin/python ricgraph_explorer.py
__version__ = '2.12'


# ##############################################################################
# General Ricgraph functions.
# ##############################################################################
def get_ricgraph_version() -> str:
    """Get the version Ricgraph.

    :return: the version string.
    """
    return __version__


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

    print('There are ' + str(len(nodes_clean)) + ' nodes ('
          + timestamp() + '), updating node: 0  ', end='')
    count = 0
    columns = nodes_clean.columns
    for row in nodes_clean.itertuples():
        count += 1
        if count % 250 == 0:
            print(count, ' ', end='', flush=True)
        if count % 2500 == 0:
            print('(' + timestamp() + ')\n', end='', flush=True)

        node_properties = {}
        for prop_name in RICGRAPH_PROPERTIES_ADDITIONAL:
            for other_name in columns:
                if prop_name == other_name:
                    node_properties[prop_name] = getattr(row, other_name)

        create_update_node(name=row.name, category=row.category, value=row.value,
                           other_properties=node_properties)

    print(count, '(' + timestamp() + ')\n', end='', flush=True)
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
    print('There are ' + str(len(left_and_right_nodepairs)) + ' rows ('
          + timestamp() + '), creating nodes and edges for row: 0  ', end='')
    count = 0
    columns = left_and_right_nodepairs.columns
    for row in left_and_right_nodepairs.itertuples():
        count += 1
        if count % 250 == 0:
            print(count, ' ', end='', flush=True)
        if count % 2500 == 0:
            print('(' + timestamp() + ')\n', end='', flush=True)

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
    print(count, '(' + timestamp() + ')\n', end='', flush=True)
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
            print('\nUnifying personal identifiers ' + column1 + ' and ' + column2
                  + ' at ' + timestamp() + '...')
            identifiers = personal_identifiers[[column1, column2]].copy(deep=True)

            # Ensure that all '' values are NaN, so that those rows can be easily removed with dropna()
            identifiers.replace('', numpy.nan, inplace=True)
            # dropna(how='any'): drop row if one or more row values contain NaN
            identifiers.dropna(axis=0, how='any', inplace=True)
            identifiers.drop_duplicates(keep='first', inplace=True, ignore_index=True)

            if RICGRAPH_NODEADD_MODE == 'strict':
                # Remove rows which have a cell value that occurs more than once.
                # There are two situations: (1) nodes with unique value; (2) nodes with non-unique value.
                # (1) We assume that in one source system, always the same ID is used to connect to
                # research results.
                # In principle, more than one ID could be used, but it could also be that someone made
                # a typo and entered the ID from another person. We cannot know which one it is,
                # therefore we assume that the same ID is used. This leads to the following,
                # e.g. if we have a DataFrame:
                # ISNI          ORCID
                # ISNI1         10
                # ISNI2         11
                # ISNI3         11
                # then we remove both rows with ORCID 11.
                # (2) It can very well be the same name belongs to more than one person (to more than one ID).
                # E.g. if we have a DataFrame:
                # FULL_NAME     ORCID
                # Name1         10
                # Name2         10
                # In this case we remove nothing.
                # For more explanation, see file docs/ricgraph_install_configure.md,
                # section RICGRAPH_NODEADD_MODE.
                if column1 != 'FULL_NAME' and column2 != 'FULL_NAME':
                    identifiers.drop_duplicates(subset=column1, keep=False, inplace=True, ignore_index=True)
                    identifiers.drop_duplicates(subset=column2, keep=False, inplace=True, ignore_index=True)

            create_nodepairs_and_edges_params(name1=column1, category1='person', value1=identifiers[column1],
                                              name2=column2, category2='person', value2=identifiers[column2],
                                              source_event1=source_event, source_event2=source_event,
                                              history_event1=history_event, history_event2=history_event)
    print('\nDone at ' + timestamp() + '.\n')
    return


# ############################################
# ################### main ###################
# ############################################
# This will be executed on module initialization

# Make sure DataFrames are printed with all columns on full width
pandas.set_option('display.max_columns', None)
pandas.set_option('display.width', 500)
# To prevent warning
# "FutureWarning: Downcasting behavior in `replace` is deprecated and will be removed
# in a future version. To retain the old behavior, explicitly call `result.infer_objects(copy=False)`.
# To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`"
pandas.set_option('future.no_silent_downcasting', True)
