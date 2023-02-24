## Install and configure Ricgraph

Ricgraph uses [Neo4j](https://neo4j.com)
as [graph database engine](https://en.wikipedia.org/wiki/Graph_database).
They have several products:

* [Neo4j Desktop](https://neo4j.com/download-center/#desktop);
* [Neo4j Bloom graph visualization tool](https://neo4j.com/product/bloom),
  included with Neo4j Desktop
  (according to Neo4j:
  "A beautiful and expressive data visualization tool to quickly explore and freely interact with
  Neo4j’s graph data platform with no coding required");
* [Neo4j Community Edition](https://neo4j.com/download-center/#community), allows
  to explore the graph using
  [Cypher queries](https://en.wikipedia.org/wiki/Cypher_(query_language)) only.

To be able to use Ricgraph, you need to:

* [Install Neo4j Desktop](#install-neo4j-desktop) (recommended, since it includes Bloom).
* [Install the Bloom configuration](#install-bloom-configuration).
* [Download this Ricgraph repository](#download-ricgraph).
* [Use a Python virtual environment](#use-a-python-virtual-environment).
* [Install the Python requirements](#install-the-python-requirements).
* Create and update the [Ricgraph initialization file](#Ricgraph-initialization-file).
* Start writing code, or start reusing code,
  see [Ricgraph programming examples](ricgraph_programming_examples.md).
* [Execute queries and visualize the results](ricgraph_query_visualize.md).

[Return to main README.md file](../README.md).

### Install Neo4j Desktop

* Download [Neo4j Desktop](https://neo4j.com/download-center/#desktop) for your
  operating system. For linux it is an [AppImage](https://en.wikipedia.org/wiki/AppImage),
  so it can be installed and used without root permissions. You will be asked to fill in a form before
  you can download. In the following screen you will be given a "Neo4j Desktop Activation Key". Save it.
* The downloaded file is called something
  like *neo4j-desktop-X.Y.Z-x86_64.AppImage*, where *X.Y.Z* is a version number.
  Make it executable using "chmod 755 \[filename\]". Then click on it.
* Accept the license, and then enter your activation key in the right part of the screen. Click "Activate".
* Move your mouse to "Example Project" in the left column.
  A red trash can icon appears. Click it to remove the Example
  Project database "Movie DBMS". Confirm.
* The text "No projects found" will appear. Create a project by clicking the button "+ New Project".
* The text "Project" appears with the text "Add a DBMS to get started". Click on the "+ Add" button
  next to it and select "Local DBMS". Leave the name as it is ("Graph DBMS") and fill in a password. Choose
  an easy to type and short one
  since the DBMS will only be accessible from your own machine. Click "Create".
* Exit Neo4j Desktop using the "File" menu and select "Quit".
* Ready.

Now we need to find the port number which Neo4j Desktop is using:

* [Start Neo4j Desktop](ricgraph_query_visualize.md#start-neo4j-desktop).
* Click on the words "Graph DBMS". At the right a new screen appears.
  Look at the tab "Details". Note the port number next to "Bolt port" (the default
  value is 7687).
  You need to put it in the [Ricgraph initialization file](#Ricgraph-initialization-file).
* Ready.

### Install Bloom configuration

* [Start Neo4j Desktop](ricgraph_query_visualize.md#start-neo4j-desktop).
* Click on the icon
  <img src="images/neo4j1.jpg" height="20"/>
  on the left side of Neo4j Desktop.
* Click on "Neo4j Bloom". A new window appears.
* In this window, click on the icon
  <img src="images/neo4j2.jpg" height="20"/>
  at the top left. A Bloom "Perspective" slides out
  (Neo4j has an
  [extensive description how to
  use it](https://neo4j.com/docs/bloom-user-guide/current/bloom-visual-tour/perspective-drawer)).
* Click on "neo4j > Untitled Perspective 1".
* A new window appears.
  Right of the words "Untitled Perspective 1" there are three vertical dots. Click on it.
  Click on "Delete". The perspective "Untitled Perspective 1" is removed.
* In the same window, right of the word "Perspectives" click on the word "Import".
  A file open window appears. Go to directory
  [neo4j_config](../neo4j_config) that is part of Ricgraph and
  select file *ricgraph_bloom_config.json*. Click "Open".
  The perspective "ricgraph_bloom_config" is loaded.
* Click on the small left arrow at the left of the word "Perspectives".
* Note that the text "neo4j > Untitled Perspective 1"
  has been changed in "neo4j > ricgraph_bloom_config".
* Click on the icon
  <img src="images/neo4j2.jpg" height="20"/>
  to go back to the main screen of Bloom.
* Ready.

### Download Ricgraph

You can choose two types of downloads for Ricgraph: 
* The latest released version. Go to the 
  [Release page of Ricgraph](https://github.com/UtrechtUniversity/ricgraph/releases),
choose the most recent version, download either the *zip* or *tar.gz* version.
* The "cutting edge" version. Go to the 
  [GitHub page of Ricgraph](https://github.com/UtrechtUniversity/ricgraph/),
  click the green button "Code", choose tab "Local", choose "Download zip".

### Use a Python virtual environment

To be able to use Ricgraph, you will need a Python virtual environment. 
Virtual environments are a kind of lightweight Python environments, 
each with their own independent set of Python packages installed 
in their site directories. A virtual environment is created on top of 
an existing Python installation.
There are two ways of doing this:
* Using Python's venv module. 
  [Read this primer to learn how to do 
  this](https://realpython.com/python-virtual-environments-a-primer/).
* Use a Python
  [Integrated development
  environment (IDE)](https://en.wikipedia.org/wiki/Integrated_development_environment),
  such as [PyCharm](https://www.jetbrains.com/pycharm).
  An IDE will automatically generate a virtual environment, and any time you 
  use the IDE, it will "transfer" you to that virtual environment.
  It is also more easy to execute and debug your scripts.

### Install the Python requirements

Ricgraph is dependent on a number of Python modules,
such as [Py2neo](#Py2neo) and [PyAlex](#PyAlex).
They are listed in the file *requirements.txt*.
You can install these in different ways:

* If you use a virtual environment, in the virtual environment, type
  `pip install -r requirements.txt`.
* If you use a Python IDE (see previous paragraph), depending on the IDE, 
  single or double click on
  file *requirements.txt*. Somewhere, there will appear a button or text 
  with something like "Install requirements". Click on it.

#### Py2neo

Ricgraph uses [Py2neo](https://py2neo.org). Py2neo is (according to its author) "a client library
and toolkit for working with Neo4j from within
Python applications and from the command line.
The library supports both Bolt and HTTP and provides a high level
API, an OGM, admin tools, an interactive console, a
Cypher lexer for Pygments, and many other bells and whistles."

#### PyAlex

Ricgraph uses [PyAlex](https://github.com/J535D165/pyalex).
PyAlex is a Python library for [OpenAlex](https://openalex.org/).
OpenAlex is an index of hundreds of millions of interconnected scholarly papers, authors,
institutions, and more. OpenAlex offers a robust, open, and free [REST API](https://docs.openalex.org/)
to extract, aggregate, or search scholarly data.
PyAlex is a lightweight and thin Python interface to this API.

### Ricgraph initialization file

Ricgraph requires an initialization file. A sample file is included as *ricgraph.ini-sample*.
You need to copy this file to *ricgraph.ini* and modify it by including a password and
a port number for Neo4j Desktop, and API keys or email addresses for other systems you plan to use.
Optionally, you can extend Ricgraph by adding new
[properties of nodes](#Properties-of-nodes-in-Ricgraph).

### Properties of nodes in Ricgraph

All nodes in Ricgraph have the following properties:

* `name`: name of the node, e.g. ISNI, ORCID, DOI, FULL_NAME, SCOPUS_AUTHOR_ID, etc.;
* `category`: category of the node,
  e.g. person, person-root, book, journal article, dataset, software, etc.;
* `value`: value of the node;
* `_key`: key value of the node, not to be modified by the user;
* `_history`: list of history events of the node, not to be modified by the user.

Additional properties for nodes can be added by changing an entry in the
[Ricgraph initialization file](#Ricgraph-initialization-file).
In the default configuration, the following properties are included:

* `comment`: comment for a node;
* `url_main`: main URL for a node, pointing to e.g. the corresponding ISNI, ORCID or DOI
  record on the web;
* `url_other`: other URL for a node, pointing to e.g. the originating record in the source system;
* `history_event`: an event to be added to `_history list`.

### Return to main README.md file

[Return to main README.md file](../README.md).

