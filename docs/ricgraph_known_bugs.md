# Ricgraph known bugs

## Error while emptying Ricgraph with Neo4j
While deleting nodes and edges in Ricgraph you might get a Python error, similar to:

```
Deleting all nodes and edges in Ricgraph...

Transaction failed and will be retried in [number]s (The allocation of an extra [number] MiB 
  would use more than the limit [number] MiB. Currently using [number] MiB. 
  dbms.memory.transaction.total.max threshold reached)

Traceback (most recent call last):
  File "[path]/harvest/harvest_pure_to_ricgraph.py", 
    line 729, in <module> rcg.empty_ricgraph()
  File "[path]/ricgraph/ricgraph.py", line [number], in empty_ricgraph
    _graph.execute_query('MATCH (node) DETACH DELETE node', database_=GRAPHDB_NAME)
  […]
  [module].errors.TransientError: [General.MemoryPoolOutOfMemoryError] 
    The allocation of an extra 2.0 MiB would use more than the limit 716.8 MiB. Currently 
    using 715.0 MiB. dbms.memory.transaction.total.max threshold reached.
```

This is caused by the free-to-use version of Neo4j, which does not have a 
statement similar to `DROP [database]`.
If you empty the graph database, it needs to delete every node and edge and this fails
when there are a lot of nodes and edges. This happens when you use
Neo4j Desktop, and might happen sometimes when you are using Neo4j Community Edition.

### Solution for Neo4j Community Edition

Read [Empty a Neo4j Community Edition database](ricgraph_backend_neo4j.md#empty-a-neo4j-community-edition-database).


### Solution for Neo4j Desktop

You can do the following for Neo4j Desktop and Ricgraph:

1. [Start Neo4j Desktop](ricgraph_backend_neo4j.md#start-neo4j-desktop) if it is not running yet.
1. Move your mouse to "Project" in the left column.
   A red trash can icon appears. Click it to remove the database. Confirm.
1. The text "No projects found" will appear. Create a project by clicking the button "+ New Project".
1. The text "Project" appears with the text "Add a DBMS to get started". Click on the "+ Add" button
   next to it and select "Local DBMS". Leave the name as it is ("Graph DBMS") and fill in a password. Choose
   an easy to type and short one
   since the DBMS will only be accessible from your own machine. Click "Create".
   Also, insert the password in field *graphdb_password* in
   the [Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file).
1. Ready.

