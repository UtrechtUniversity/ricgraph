## Ricgraph script writing

Ricgraph scripts can be found in the directories
[harvest_to_ricgraph_examples](../harvest_to_ricgraph_examples) and
[find_enrich_ricgraph_examples](../find_enrich_ricgraph_examples).
The module code *ricgraph.py* can be found in directory [ricgraph](../ricgraph). The code is
documented and hints to use it can be found in those files.

For more information about harvesting data, 
see [Ricgraph harvest scripts](docs/ricgraph_harvest_scripts.md).

[Return to main README.md file](../README.md).


### How to make your own harvesting scripts
You can make your own harvesting script of your favorite source. The easiest way to
do so is to take one of the harvesting scripts as an example.
For example, if you use the script *harvest_pure_to_ricgraph.py*, you'll recognize the
three parts:
1. Code for harvesting. This is done with `harvest_json_and_write_to_file()` which also writes
   the harvested json data to a file. It gets data from a source.
1. Code for parsing. This is done with `parse_pure_persons()`, `parse_pure_organizations()` and
   `parse_pure_resout()` for persons, organizations and research outputs from Pure.
   It does data processing to get harvested results
   in a "useful" shape for inserting nodes and
   edges in Ricgraph.
1. Code for inserting the parsed results in Ricgraph. This is done with
   `parsed_persons_to_ricgraph()`, `parsed_organizations_to_ricgraph()` and
   `parsed_resout_to_ricgraph()`.
   It inserts the nodes and edges in Ricgraph.

You can adapt each of these parts as suits the source you would like to harvest.

### General program structure of a Python script using Ricgraph

```python
import ricgraph as rcg

rcg.open_ricgraph()
rcg.empty_ricgraph()  # use this only if you need to empty the graph
# some things happen
rcg.close_ricgraph()
```

### Structure of a Python script that is harvesting data
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

### Known bugs

#### Error while emptying Ricgraph
While deleting nodes and edges in Ricgraph you might get a Python error, similar to:

```
Deleting all nodes and edges in Ricgraph...

Traceback (most recent call last):
  File "[path]/ricgraph-master/harvest_to_ricgraph_examples/harvest_pure_to_ricgraph.py", 
    line 729, in <module> rcg.empty_ricgraph()
  File "[path]/ricgraph-master/ricgraph/ricgraph.py", line 223, in empty_ricgraph
    _graph.delete_all()   # Equivalent to "MATCH (a) DETACH DELETE a".
  […]
  py2neo.errors.TransientError: [General.MemoryPoolOutOfMemoryError] 
    The allocation of an extra 2.0 MiB would use more than the limit 716.8 MiB. Currently 
    using 715.0 MiB. dbms.memory.transaction.total.max threshold reached.
```

This is caused by that Neo4j Desktop does not have a statement similar to `DROP [database]`.
Py2neo, the library that Ricgraph uses, needs to delete every node and edge and this fails
when there are a lot of nodes and edges. This does not happen when you are using 
Neo4j Community Edition.

You can do the following to be able to use Neo4j Desktop and Ricgraph:
1. [Start Neo4j Desktop](ricgraph_query_visualize.md#start-neo4j-desktop) if it is not running yet.
1. Move your mouse to "Project" in the left column.
   A red trash can icon appears. Click it to remove the database. Confirm.
1. The text "No projects found" will appear. Create a project by clicking the button "+ New Project".
1. The text "Project" appears with the text "Add a DBMS to get started". Click on the "+ Add" button
   next to it and select "Local DBMS". Leave the name as it is ("Graph DBMS") and fill in a password. Choose
   an easy to type and short one
   since the DBMS will only be accessible from your own machine. Click "Create".
   Also, insert the password in field *neo4j_password* in
   the [Ricgraph initialization file](#Ricgraph-initialization-file).
1. Ready.

### Return to main README.md file

[Return to main README.md file](../README.md).

