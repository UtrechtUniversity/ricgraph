# Ricgraph with Memgraph graph database backend

Ricgraph can use two [graph database
backends](https://en.wikipedia.org/wiki/Graph_database):
[Neo4j](https://neo4j.com) and [Memgraph](https://memgraph.com). 
This page describes how to install Ricgraph with Memgraph graph
database backend.

## Install and start Memgraph
As an alternative to Neo4j, you can also use
[Memgraph](https://memgraph.com).
Memgraph is an in memory graph database
and therefore faster than Neo4j.
However, it has not been tested extensively with Ricgraph.

* Login as user *root*.
* Make sure you have Docker. If not, install it:
    * Debian/Ubuntu: follow [Install Docker using the apt
      repository](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository).
* Install Memgraph Platform.
  To do this, follow the instructions on
  the [Memgraph download page](https://memgraph.com/download) in the block 'Memgraph Platform'.
  Memgraph will be started automatically. Stop it by typing _Control-C_.
* To start Memgraph, go to the directory _memgraph-platform_:
  ```
  cd memgraph-platform
  ```
  and type:
  ```
  docker compose up
  ```
  If you want to stop Memgraph, type _Control-C_.
* In the log printed on the terminal, you might get a message like:
  ``Max virtual memory areas vm.max_map_count 65530 is too low, increase to at least 262144``.
  To resolve this, create a file in _/etc/sysctl.d_ with the name _90-local.conf_
  and the following content:
  ```
  vm.max_map_count=262144 
  ```
  After you have done that, type:
  ```
  sysctl --system
  ```
  and the message should be gone. Start Memgraph as above.
* To use Memgraph Platform, go to [http://localhost:3000](http://localhost:3000).
* How to start Memgraph automatically at system startup, is a 'to be done'.

