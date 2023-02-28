## Ricgraph programming examples

Ricgraph programming code can be found in the directories
[harvest_to_ricgraph_examples](../harvest_to_ricgraph_examples) and
[find_enrich_ricgraph_examples](../find_enrich_ricgraph_examples).
The module code *ricgraph.py* can be found in directory [ricgraph](../ricgraph). The code is
documented and hints to use it can be found in those files.

[Return to main README.md file](../README.md).

### Harvest of Utrecht University datasets and software

You can start with a harvest for Utrecht University datasets
from the data repository [Yoda](https://search.datacite.org/repositories/delft.uu),
and for Utrecht University software
from the [Research Software Directory](https://research-software-directory.org).
You can use the scripts
*harvest_yoda_datacite_to_ricgraph.py* and *harvest_rsd_to_ricgraph.py*.
They can be used out of the box since they don't need an
[API](https://en.wikipedia.org/wiki/API) key.
You will observe that the information from these two sources is neatly combined in one graph.

### Harvest of Pure

A script for harvesting persons, organizations and research outputs from Pure is provided
with the script *harvest_pure_to_ricgraph.py*. You need an API key to be able to do this, 
enter it as value to field *pure_api_key* in the
[Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file).
Also, you need to specify the url to Pure in the field *pure_url*.

There is a lot of data in Pure, so your harvest may take a long time. You may
reduce this by adjusting parameters at the start of the script. Look in the sections
"Parameters for harvesting persons/organizations/research outputs from pure".
E.g., for research outputs you can adjust
the years to harvest with the parameter *PURE_RESOUT_YEARS* and the maximum number of
records to harvest with *PURE_RESOUT_MAX_RECS_TO_HARVEST*.

### General program structure of a Python program using Ricgraph

```python
import ricgraph as rcg

rcg.open_ricgraph()
rcg.empty_ricgraph()  # use this only if you need to empty the graph
# some things happen
rcg.close_ricgraph()
```

### Program structure of a Python program that is harvesting data

This structure is used in the programming examples in the directory
[harvest_to_ricgraph_examples](../harvest_to_ricgraph_examples).

```python
import ricgraph as rcg

rcg.open_ricgraph()
rcg.empty_ricgraph()  # use this only if you need to empty the graph

# Harvesting code: code to get data from a system

# Parsing code: post process the data found, and put it in a format that 
#   can easily be processed in Python, e.g. in a DataFrame

# Code to store the post processed results in Ricgraph

rcg.close_ricgraph()
```

### Function calls for inserting nodes

Ricgraph stores objects and relations to objects. Therefore, most calls to insert nodes
in have two nodes as parameter that are to be connected. Or two sets of nodes.
Examples of these calls are (without the opening, emptying and closing of the graph):

```python
import ricgraph as rcg

# example 1
rcg.create_two_nodes_and_edge()  # create two nodes and connect with one edge

# example 2
rcg.create_nodepairs_and_edges_df()  # the same, now using a DataFrame to insert
# a number of node pairs and their edges in one go

# example 3
rcg.create_nodepairs_and_edges_params()  # the same, now using Python Dicts to insert
# a number of node pairs and their edges in one go
```

### Function call for unifying personal identifiers

Unification is the process of making sure that every personal identifier found for a
certain person is connected to every other, via the
[*person-root*](ricgraph_details.md#person-root-node-in-ricgraph) node.
E.g., if there are four identifiers for a person: ORCID, ISNI, FULL_NAME
and SCOPUS_AUTHOR_ID, they have to be unified pairwise.
There is a function call to make this easier:

```python
import ricgraph as rcg

rcg.unify_personal_identifiers()  # takes a DataFrame with all identifiers to be unified
```

### Function calls to create, read (find), update and delete (CRUD) nodes

Of course, there are function calls
to create, read, update and delete (CRUD) nodes. "Read" is used as term for "Find" or "Search".

```python
import ricgraph as rcg

rcg.create_node()       # create a node
rcg.read_node()         # read (find) a node and return one
rcg.read_all_nodes()    # read (find) nodes and return all nodes found
rcg.update_node()       # update the values in a node
rcg.delete_node()       # delete a node
```

### Function calls to get neighbors of nodes

There are several function calls
to get neighbors of nodes. For a more extensive description how to use these,
see the code comments in file *ricgraph.py* in directory [ricgraph](../ricgraph)
or the code examples in file *ricgraph_explorer.py* in directory
[ricgraph_explorer](../ricgraph_explorer).

```python
import ricgraph as rcg

rcg.get_personroot_node()            # get a 'person-root' node starting from any 'person' node
rcg.get_all_personroot_nodes()       # get all 'person-root' nodes (there should be only one)
rcg.get_all_neighbor_nodes()         # get all neighbor nodes connected to a node. 
                                     # it is possible to restrict to nodes having
                                     # a certain property 'name' or 'category'
rcg.get_all_neighbor_nodes_person()  # get all neighbor nodes connected to a 'person' node
```

### Return to main README.md file

[Return to main README.md file](../README.md).

