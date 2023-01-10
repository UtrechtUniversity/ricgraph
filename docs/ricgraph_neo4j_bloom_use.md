## Start Neo4j and use Bloom

[Return to main README.md file](../README.md).

### Start Neo4j Desktop

* Click on the downloaded AppImage. It will be called something
  like *neo4j-desktop-X.Y.Z-x86_64.AppImage*, where *X.Y.Z* is a version number.
* At the top right there is a text "No active DBMS".
* Move your mouse to the text "Graph DBMS". When you hoover it, a button
  will appear with the text "Start". Click it.
* Wait until the Neo4j graph database engine has started.
  It may ask for a password that has
  been changed. Enter the password you have used
  while creating your database. Click "Save". 
* Now, next to the text "Graph DBMS" a green icon appears with
  the text "ACTIVE". Your graph database engine is active and ready for use.

### How to use Bloom

[Bloom is Neo4j's graph visualization tool](https://neo4j.com/product/bloom).
It is included with Neo4j Desktop.
According to Neo4j it is:
"A beautiful and expressive data visualization tool to quickly explore and freely interact with
Neo4j’s graph data platform with no coding required".
Neo4j has
[extensive documentation how to use Bloom](https://neo4j.com/docs/bloom-user-guide/current)
and a 
[Bloom overview](https://neo4j.com/docs/bloom-user-guide/2.6/bloom-visual-tour/bloom-overview).
Below are some examples for a quick start.

#### Open Bloom

* [Start Neo4j Desktop](#Start-neo4j-desktop).
* Click on the icon
  <img src="images/neo4j1.jpg" height="20"/>
  on the left side of Neo4j Desktop.
* Click on "Neo4j Bloom". A new window appears.

#### Execute queries

The [Ricgraph Bloom configuration file](ricgraph_install_configure.md#install-bloom-configuration)
contains four different shortcuts for
[Cypher queries](https://en.wikipedia.org/wiki/Cypher_(query_language)):

* "Node name \[value of node to find\]": finds a node
  where property *name* of a node has value *\[value of node to find\]*.
* "Node category \[value of node to find\]": similar to
  "Node name ..." for property *category*.
* "Node value \[value of node to find\]": similar to
  "Node name ..." for property *value*.
* "Node comment \[value of node to find\]": similar to
  "Node name ..." for property *comment*.

These queries can be entered in the Bloom text box "Search graph",
by typing e.g. "Node name ORCID" or "Node category dataset".
For more information see
[Bloom search bar](https://neo4j.com/docs/bloom-user-guide/2.6/bloom-visual-tour/search-bar)
and [Boom pattern
search](https://neo4j.com/docs/bloom-user-guide/current/bloom-tutorial/graph-pattern-search).

Nodes found can be examined or expanded as described in the section
[Actions while clicking on a node](#Actions-while-clicking-on-a-node).
The result will be visualized as described in section
[Visualization of nodes](#Visualization-of-nodes).

#### Actions while clicking on a node

The following are some examples of actions while clicking on a node:

* Double left-click on a node: the properties of a node are shown in a window.
* Right-click right on a node, choose "Expand", choose "All": The node will be
  expanded with all nodes connected to it.
* Multiple nodes can be selected by selecting one node, holding the
  Control key and selecting other nodes.
* Right-click on a node, choose "Dismiss": This node will
  be removed from the visualization.
* Right-click on a node, choose "Dismiss other nodes": All other nodes will
  be removed from the visualization.
* For other actions, see
  [Bloom actions](https://neo4j.com/docs/bloom-user-guide/2.6/bloom-visual-tour/search-bar/#_actions).

#### Visualization of nodes

Nodes can be visualized in different ways, by changing e.g. their
size or color. This can be changed as follows:

* On the right side of the Bloom window, there is
  an icon <img src="images/neo4j3.jpg" height="20"/>. Click it
  (Neo4j has [extensive documentation how to use
  it](https://neo4j.com/docs/bloom-user-guide/current/bloom-visual-tour/perspective-drawer)).
* A new window appears. It shows the default settings for the display
  of nodes. You can change the color, size, the property to
  show on the node, and the icon.
* In the tab "Rule-based" you can add your own rules.

The [Ricgraph Bloom configuration file](ricgraph_install_configure.md#install-bloom-configuration)
contains a few rules based on the value of properties.
Rules which determine the color of a node:

* if property *category* = "person": color = blue.
* if property *category* = "dataset": color = green.
* if property *category* = "journal article": color = yellow.
* if property *category* = "software": color = red.
* all other nodes: color = grey.

Rules which determine the size of a node:

* if property *url_main* contains "uu01": size of the node = small. This indicates
  which nodes have been harvested from
  the data repository [Yoda](https://search.datacite.org/repositories/delft.uu).
* if property *url_other* contains "research-software-directory": size of the node = large.
  This indicates which nodes have been harvested from
  the [Research Software Directory](https://research-software-directory.org).
* all other nodes: size = medium.

### Return to main README.md file

[Return to main README.md file](../README.md).
