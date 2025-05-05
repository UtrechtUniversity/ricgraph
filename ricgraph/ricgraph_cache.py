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
# Ricgraph cache functions.
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


import sys
from typing import Union
from neo4j.graph import Node
from .ricgraph_constants import MAX_NODES_CACHE_NODELINK, MAX_NODES_CACHE_KEY_ID


# This dict is used as a cache for node id's. If we have a node id, we can
# do a direct lookup for a node in O(1), instead of a search in O(log n).
# The dict has the format: [Ricgraph _key]: [Node element_id].
_nodes_cache_key_id = {}

# The dict '_nodes_cache_nodelink' is used to be able to pass nodes (i.e. links to Node)
# between the pages of Ricgraph Explorer. If we would not do this, we would need
# to search the node again every time we go to a new page. Then we would
# lose the advantage of using a graph.
# I could have used rcg.read_node() with @ricgraph_lru_cache, but I'd prefer to be
# able to store any node in the cache at the moment I prefer, as is done
# in function ricgraph_explorer.py/get_regular_table()).
# This dict has the format: [Ricgraph _key]: [Node link]
_nodes_cache_nodelink = {}


def nodes_cache_key_id_create(key: str, elementid: str) -> None:
    """Create an entry in the cache for node id's.
    'id' in this sentence is the id assigned by de graph database.

    :param key: _key of a node.
    :param elementid: id of a node.
    :return: None.
    """
    global _nodes_cache_key_id

    if len(_nodes_cache_key_id) > MAX_NODES_CACHE_KEY_ID:
        nodes_cache_key_id_empty()

    # We use a 'dict', which does not allow for duplicates, so we
    # do not need to check for it.
    _nodes_cache_key_id[key] = elementid
    return


def nodes_cache_key_id_read(key: str) -> str:
    """Read an entry from the cache for node id's.
    'id' in this sentence is the id assigned by de graph database.

    :param key: _key of a node.
    :return: The id of the node, or '' if not present.
    """
    global _nodes_cache_key_id

    if key in _nodes_cache_key_id:
        return _nodes_cache_key_id[key]
    return ''


def nodes_cache_key_id_delete_key(key: str) -> None:
    """Delete a key 'key' from the cache for node id's.
    'id' in this sentence is the id assigned by de graph database.

    :param key: _key of a node.
    :return: None.
    """
    global _nodes_cache_key_id

    if key in _nodes_cache_key_id:
        _nodes_cache_key_id.pop(key)
    return


def nodes_cache_key_id_delete_id(elementid: str) -> None:
    """Delete a value 'elementid' from the cache for node id's.
    'id' in this sentence is the id assigned by de graph database.
    This need to iterate over the full dict, so it is not efficient.

    :param elementid: the id of a node.
    :return: None.
    """
    global _nodes_cache_key_id

    key_to_delete = ''
    for key in _nodes_cache_key_id:
        if _nodes_cache_key_id[key] == elementid:
            key_to_delete = key
            break
    if key_to_delete != '':
        nodes_cache_key_id_delete_key(key=key_to_delete)
    return


def nodes_cache_key_id_empty() -> None:
    """Empty the cache for node id's.
    'id' in this sentence is the id assigned by de graph database.

    :return: None.
    """
    global _nodes_cache_key_id

    _nodes_cache_key_id.clear()
    return


def nodes_cache_nodelink_create(key: str, node: Node) -> None:
    """Create an entry in the cache for nodes.

    :param key: _key of a node.
    :param node: a node.
    :return: None.
    """
    global _nodes_cache_nodelink

    if len(_nodes_cache_nodelink) > MAX_NODES_CACHE_NODELINK:
        nodes_cache_nodelink_empty()

    # We use a 'dict', which does not allow for duplicates, so we
    # do not need to check for it.
    _nodes_cache_nodelink[key] = node
    return


def nodes_cache_nodelink_read(key: str) -> Union[Node, None]:
    """Read an entry from the cache for nodes.

    :param key: _key of a node.
    :return: The node, or None if not present.
    """
    global _nodes_cache_nodelink

    if key in _nodes_cache_nodelink:
        return _nodes_cache_nodelink[key]
    return None


def nodes_cache_nodelink_empty() -> None:
    """Empty the cache for nodes.

    :return: None.
    """
    global _nodes_cache_nodelink

    _nodes_cache_nodelink.clear()
    return


def nodes_cache_nodelink_size() -> tuple[int, float]:
    """Return the size of the cache for nodes.

    :return: the length of the dict (int) and the size in kB (float).
    """
    global _nodes_cache_nodelink

    length = len(_nodes_cache_nodelink)
    size_kb = round(sys.getsizeof(_nodes_cache_nodelink) / 1000, 1)
    return length, size_kb
