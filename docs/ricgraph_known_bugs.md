## Ricgraph known bugs

### Error while emptying Ricgraph
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
   the [Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file).
1. Ready.

### Return to main README.md file

[Return to main README.md file](../README.md).
