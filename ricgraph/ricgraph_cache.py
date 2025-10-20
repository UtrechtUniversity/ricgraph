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
# Updated Rik D.T. Janssen, January to June, October 2025.
#
# ########################################################################


from sys import getsizeof
from typing import Optional
from pymemcache.client.base import Client
from .ricgraph_constants import MAX_NODES_CACHE_KEY_ID
from .ricgraph_utils import (get_configfile_key,
                             serialize_value, deserialize_value)


# This dict is used as a cache for node id's. If we have a node id, we can
# do a direct lookup for a node in O(1) in the graph database,
# instead of a search in O(log n).
# The dict has the format: [Ricgraph _key]: [Node element_id].
_nodes_cache_key_id = {}

# Global indicating whether Memcached is available.
_memcached_available = False

# Global for connection to Memcached.
# Type hint necessary to avoid PyCharm warning.
_memcached_client: Optional[Client] = None


def memcached_open_connection() -> None:
    """Open a connection to Memcached, but only when it should
    be used according to ricgraph.ini.
    If Memcached is not available, then return None.
    Set the Memcached client in a global variable.
    """
    global _MEMCACHED_HOST, _MEMCACHED_PORT
    global _memcached_available, _memcached_client

    if _MEMCACHED_TO_BE_USED != 'True':
        _memcached_available = False
        return

    if _MEMCACHED_HOST == '' or _MEMCACHED_PORT == '':
        _memcached_available = False
        return

    try:
        memcached_client = Client(server=(_MEMCACHED_HOST, int(_MEMCACHED_PORT)),
                                  allow_unicode_keys=True)

        # Test connection by setting and deleting a test key.
        memcached_client.set(key='test_key', value=b'test', expire=1)
        memcached_client.delete(key='test_key')

        _memcached_available = True
        _memcached_client = memcached_client
        return
    except:
        _memcached_available = False
        _memcached_client = None
        return


def memcached_check_available() -> bool:
    """Check if Memcached is available.

    :return: True if available, False otherwise.
    """
    global _memcached_available, _memcached_client

    if not _memcached_available:
        return False

    if _memcached_client is None:
        return False
    else:
        return True


def nodes_cache_key_id_create(key: str, elementid: str) -> None:
    """Create an entry in the cache for node id's.
    'id' in this sentence is the id assigned by de graph database.

    :param key: _key of a node.
    :param elementid: id of a node.
    :return: None.
    """
    global _nodes_cache_key_id, _memcached_available

    if key == '' or elementid == '':
        return

    if memcached_check_available():
        # The docs are unclear whether I need to serialize the key if I
        # use flag allow_unicode_keys=True in Client() above.
        # So I do serialize to be sure. Since keys cannot have spaces,
        # these are replaced first.
        key_serialized = serialize_value(value=key.replace(' ', '_'))
        elementid_serialized = serialize_value(value=elementid)
        try:
            _memcached_client.set(key=key_serialized,
                                  value=elementid_serialized,
                                  expire=0)
        except:
            print('nodes_cache_key_id_create(): Warning, connection to Memcached lost, continuing...')
            # Continue, hopefully the connection will come back soon.
        return

    if len(_nodes_cache_key_id) > MAX_NODES_CACHE_KEY_ID:
        nodes_cache_key_id_empty()

    # We use a 'dict', which does not allow for duplicates, so we
    # do not need to check for duplicates.
    # https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
    # tells that Python dict keys and values can have _almost_ any type.
    # So we do not need to serialize and deserialize.
    _nodes_cache_key_id[key] = elementid
    # print('Create: ' + str(key) + ' -- ' + _nodes_cache_key_id[key])
    return


def nodes_cache_key_id_read(key: str) -> str:
    """Read an entry from the cache for node id's.
    'id' in this sentence is the id assigned by de graph database.

    :param key: _key of a node.
    :return: The id of the node, or '' if not present.
    """
    global _nodes_cache_key_id, _memcached_available

    if key == '':
        return ''

    if memcached_check_available():
        key_serialized = serialize_value(value=key.replace(' ', '_'))
        try:
            elementid_serialized = _memcached_client.get(key=key_serialized)
        except:
            print('nodes_cache_key_id_read(): Warning, connection to Memcached lost, continuing...')
            # Continue, hopefully the connection will come back soon.
            return ''

        if elementid_serialized is None:
            # Key not found.
            return ''
        else:
            elementid = deserialize_value(serialized=elementid_serialized)
            return elementid

    if key in _nodes_cache_key_id:
        # print('Read: ' + str(key) + ' -- ' + _nodes_cache_key_id[key])
        return _nodes_cache_key_id[key]
    return ''


def nodes_cache_key_id_delete_key(key: str) -> None:
    """Delete a key 'key' from the cache for node id's.
    'id' in this sentence is the id assigned by de graph database.

    :param key: _key of a node.
    :return: None.
    """
    global _nodes_cache_key_id, _memcached_available

    if key == '':
        return

    if memcached_check_available():
        key_serialized = serialize_value(value=key.replace(' ', '_'))
        try:
            # Works regardless whether the key is present or not.
            _memcached_client.delete(key=key_serialized)
        except:
            print('nodes_cache_key_id_delete(): Error, connection to Memcached lost, exiting...')
            # Exit because the cache gets in an unexpected state:
            # an element remains in the cache while it should not.
            exit(1)
        return

    if key in _nodes_cache_key_id:
        # print('Delete: ' + str(key) + ' -- ' + _nodes_cache_key_id[key])
        _nodes_cache_key_id.pop(key)
    return


def nodes_cache_key_id_empty() -> None:
    """Empty the cache for node id's.
    'id' in this sentence is the id assigned by de graph database.

    :return: None.
    """
    global _nodes_cache_key_id, _memcached_available

    if memcached_check_available():
        try:
            _memcached_client.flush_all()
        except:
            print('nodes_cache_key_id_empty(): Error, connection to Memcached lost, exiting...')
            # Exit because the cache gets in an unexpected state:
            # it is not emptied while it should have been.
            exit(1)
        return

    # print('Clear cache.')
    _nodes_cache_key_id.clear()
    return


def nodes_cache_key_id_type_size() -> str:
    """Return the size of the cache for node id's.
    'id' in this sentence is the id assigned by de graph database.

    :return: a sentence with the length of the cache and its size.
    """
    global _nodes_cache_key_id

    if memcached_check_available():
        result = 'Ricgraph uses Memcached as cache. '
        try:
            stats = _memcached_client.stats()
            items = int(stats.get(b'curr_items', 0))
            bytes_used = int(stats.get(b'bytes', 0))
            size_kb = round(bytes_used / 1000, 1)
        except:
            # In case the connection to Memcached is lost, we will also end up here,
            # and we just continue.
            items = 0
            size_kb = 0.0
    else:
        result = 'Ricgraph uses a local cache. '
        items = len(_nodes_cache_key_id)
        size_kb = round(getsizeof(_nodes_cache_key_id) / 1000, 1)

    result += 'This cache has ' + str(items) + ' elements, and its size is '
    result += str(size_kb) + ' kB.'
    return result


# ############################################
# ################### main ###################
# ############################################
# This will be executed on module initialization
_MEMCACHED_HOST = get_configfile_key(section='Memcached',
                                     key='memcached_host')
# This returns a str, will be converted to int later on.
_MEMCACHED_PORT = get_configfile_key(section='Memcached',
                                     key='memcached_port')
_MEMCACHED_TO_BE_USED = get_configfile_key(section='Memcached',
                                           key='ricgraph_explorer_uses_memcached')
