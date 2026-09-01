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
# Updated Rik D.T. Janssen, January to June, October 2025, July 2026.
#
# ########################################################################


from sys import getsizeof
from typing import Optional, Tuple, Any
from pymemcache.client.base import Client
from .ricgraph_constants import MAX_NODES_CACHE_KEY_ID
from .ricgraph_utils import (get_configfile_key_memcached_parameters,
                             serialize_value, deserialize_value)


# This dict is used as a cache. 
# It may be used for node ids. If we have a node id, we can
# do a direct lookup for a node in O(1) in the graph database,
# instead of a search in O(log n).
# For nodes, the dict has the format: [Ricgraph _key]: [Node element_id].
# For all other types, it uses JSON, and it has the 
# format: [key]: [value].
_ricgraph_cache = {}

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
    global _memcached_available, _memcached_client

    memcached_to_be_used, memcached_host, memcached_port = get_configfile_key_memcached_parameters()
    if memcached_to_be_used:
        _memcached_available = True
    else:
        _memcached_available = False
        return

    if memcached_host == '':
        _memcached_available = False
        return

    try:
        memcached_client = Client(server=(memcached_host, memcached_port),
                                  allow_unicode_keys=True)

        # Test connection by setting and deleting a test key.
        memcached_client.set(key='test_key', value=b'test', expire=1)
        memcached_client.delete(key='test_key')

        _memcached_available = True
        _memcached_client = memcached_client
        return
    except:
        print('memcached_open_connection(): Warning: could not reach Memcached cache daemon,')
        print('     it is probably not running, continuing with local cache.')
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


def ricgraph_cache_item_create(key: str, value: Any) -> None:
    """Create an entry in the cache.

    :param key: key of a cache item.
    :param value: value of a cache item.
    :return: None.
    """
    global _ricgraph_cache, _memcached_available, _memcached_client

    if key == '' or value == '':
        return

    key_clean = key.replace(' ', '_')
    value_serialized = serialize_value(value=value)
    if memcached_check_available():
        if _memcached_client is None:
            return
        try:
            _memcached_client.set(key=key_clean,
                                  value=value_serialized,
                                  expire=0)
        except:
            print('ricgraph_cache_item_create(): Warning, connection to Memcached lost, continuing...')
            # Continue, hopefully the connection will come back soon.
        return

    if len(_ricgraph_cache) > MAX_NODES_CACHE_KEY_ID:
        ricgraph_cache_empty()

    # We use a 'dict', which does not allow for duplicates, so we
    # do not need to check for duplicates.
    # https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
    # tells that Python dict keys and values can have _almost_ any type.
    # We serialize for symmetry with Memcached.
    # print('Create: ' + str(key_clean) + ' -- ' + str(value_serialized))
    _ricgraph_cache[key_clean] = value_serialized
    return


def ricgraph_cache_item_read(key: str) -> Any:
    """Read an entry from the cache.

    :param key: key of a cache item.
    :return: The value of the cache item, or '' if not present.
    """
    global _ricgraph_cache, _memcached_available, _memcached_client

    if key == '':
        return ''

    key_clean = key.replace(' ', '_')
    if memcached_check_available():
        if _memcached_client is None:
            return ''
        try:
            value_serialized = _memcached_client.get(key=key_clean)
        except:
            print('ricgraph_cache_item_read(): Warning, connection to Memcached lost, continuing...')
            # Continue, hopefully the connection will come back soon.
            return ''

        if value_serialized is None:
            # Key not found.
            return ''
        else:
            value = deserialize_value(serialized=value_serialized)
            return value

    if key_clean in _ricgraph_cache:
        value_serialized = _ricgraph_cache[key_clean]
        # print('Read: ' + str(key_clean) + ' -- ' + str(value_serialized))
        value = deserialize_value(serialized=value_serialized)
        return value
    return ''


def ricgraph_cache_item_delete_key(key: str) -> None:
    """Delete a key 'key' from the cache.

    :param key: key of a cache item.
    :return: None.
    """
    global _ricgraph_cache, _memcached_available, _memcached_client

    if key == '':
        return

    key_clean = key.replace(' ', '_')
    if memcached_check_available():
        if _memcached_client is None:
            return
        try:
            # Works regardless whether the key is present or not.
            _memcached_client.delete(key=key_clean)
        except:
            print('nodes_cache_item_delete_key(): Error, connection to Memcached lost, exiting...')
            # Exit because the cache gets in an unexpected state:
            # an element remains in the cache while it should not.
            exit(1)
        return

    if key_clean in _ricgraph_cache:
        # print('Delete: ' + str(key_clean) + ' -- ' + _ricgraph_cache[key_clean])
        _ricgraph_cache.pop(key_clean)
    return


def ricgraph_cache_empty() -> None:
    """Empty the cache.

    :return: None.
    """
    global _ricgraph_cache, _memcached_available, _memcached_client

    if memcached_check_available():
        if _memcached_client is None:
            return
        try:
            _memcached_client.flush_all()
        except:
            print('ricgraph_cache_empty(): Error, connection to Memcached lost, exiting...')
            # Exit because the cache gets in an unexpected state:
            # it is not emptied while it should have been.
            exit(1)
        return

    # print('Clear cache.')
    _ricgraph_cache.clear()
    return


def ricgraph_cache_size() -> Tuple[int, float]:
    """Return the size of the cache.

    :return: a tuple with number of items and size in kB.
    """
    global _ricgraph_cache, _memcached_client

    if memcached_check_available():
        if _memcached_client is None:
            return 0, 0.0
        try:
            stats = _memcached_client.stats()
            nr_items = int(stats.get(b'curr_items', 0))
            bytes_used = int(stats.get(b'bytes', 0))
            size_kb = round(bytes_used / 1000, 1)
        except:
            # In case the connection to Memcached is lost, we will also end up here,
            # and we just continue.
            nr_items = 0
            size_kb = 0.0
    else:
        nr_items = len(_ricgraph_cache)
        size_kb = round(getsizeof(_ricgraph_cache) / 1000, 1)
    return nr_items, size_kb


def ricgraph_cache_size_text() -> str:
    """Return the size of the cache for node id's.
    'id' in this sentence is the id assigned by de graph database.

    :return: a sentence with the length of the cache and its size.
    """
    nr_items, size_kb = ricgraph_cache_size()
    if memcached_check_available():
        result = 'Ricgraph uses Memcached as cache. '
    else:
        result = 'Ricgraph uses a local cache. '

    result += 'This cache has ' + str(nr_items) + ' elements, and its size is '
    result += str(size_kb) + ' kB.'
    return result
