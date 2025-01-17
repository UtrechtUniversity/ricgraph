# Install and configure Ricgraph

This page describes how to install Ricgraph for a single user on Linux.
If you would like to use Ricgraph in a multi-user environment
on Linux, you will need to install Ricgraph differently.
In case you have no idea what would be the best for your situation, please 
install Ricgraph for a single user on Linux, as described on this page.
Or go for Ricgraph in a container.

Other Ricgraph install options are:
* [Install and configure
  Ricgraph as a server](ricgraph_as_server.md): 
  multi-user environment on Linux.
* [Install and use
  Ricgraph in a container](ricgraph_containerized.md):
  relatively quick with limited possibilities.
 
[Continue reading here if you would like to install Ricgraph on
Windows](#ricgraph-on-windows).

On this page you can find:
* [Ricgraph Makefile](#ricgraph-makefile)
* [Installation instructions for a single user](#installation-instructions-for-a-single-user)
* [Requirements](#requirements)
* [Steps to take](#steps-to-take)
* [Install Neo4j Desktop](#install-neo4j-desktop)
* [Install Bloom configuration](#install-bloom-configuration)
* [Download Ricgraph](#download-ricgraph)
* [Use a Python virtual environment and install Python requirements](#use-a-python-virtual-environment-and-install-python-requirements)
* [Ricgraph initialization file](#ricgraph-initialization-file)
* [Using Ricgraph](#using-ricgraph)
* [Dumping and restoring the Ricgraph database](#dumping-and-restoring-the-ricgraph-database)
* [Ricgraph on Windows](#ricgraph-on-windows)
 
[Return to main README.md file](../README.md).

## Ricgraph Makefile
A Ricgraph installation involves a number of steps.
Ricgraph uses a *Makefile* to make installation of (parts of) Ricgraph easier.
Such a Makefile automates a number of these steps. 
A Makefile command is executed by typing:
```
make [target]
```

To use the Ricgraph Makefile, first go to your home directory on Linux and 
then download it, by typing:
```
cd
wget https://raw.githubusercontent.com/UtrechtUniversity/ricgraph/main/Makefile
```

In the example above, the *[target]* specifies what has to be done. 
Assuming that you are in your home directory, you can 
execute one of these commands to find the possible targets:
```
make
make help
```
You can add command line parameters to the `make` command, e.g. to get the
Ricgraph *cutting edge* version, or to specify an installation path. 
Look in the [Makefile](../Makefile) for possiblities. Any variable defined
in the Makefile can be used as `make` command line parameter.
For an example, see the [Podman Containerfile](../Containerfile).

Most often, you do not need to install the `make` command, but if you get a
"command not found" error message, you need to install it using your Linux 
package manager.

If you read the documentation below or on page
[Ricgraph as a server on Linux](ricgraph_as_server.md),
you will notice that some sections start with mentioning a Makefile command. 
That means, that if you execute that command, the steps in that section will
be done automatically.
Sometimes, you will
have to do some post-install steps, e.g. because you have to choose a password for the
graph database. 


## Installation instructions for a single user

Ricgraph can use two [graph database 
backends](https://en.wikipedia.org/wiki/Graph_database):
[Neo4j](https://neo4j.com) and [Memgraph](https://memgraph.com). 

### Neo4j 
Neo4j has several products:

* [Neo4j Desktop](https://neo4j.com/download-center/#desktop);
* [Neo4j Bloom graph visualization tool](https://neo4j.com/product/bloom),
  included with Neo4j Desktop
  (according to Neo4j:
  "A beautiful and expressive data visualization tool to quickly explore and freely interact with
  Neo4j’s graph data platform with no coding required");
* [Neo4j Community Edition](https://neo4j.com/download-center/#community), allows
  to explore the graph using
  [Cypher queries](https://en.wikipedia.org/wiki/Cypher_(query_language)) only.

### Memgraph
[Memgraph](https://memgraph.com) is an in memory graph database
and therefore faster than Neo4j. However,
it has not been tested extensively with Ricgraph yet.
Read [Install and start Memgraph](ricgraph_as_server.md#install-and-start-memgraph).

## Requirements
The easiest method for using Ricgraph is by using a Linux virtual machine (VM) such as
you can create using 
[VirtualBox](https://www.virtualbox.org). A VM of size 25GB with 4GB memory will work.
Of course, this depends on the (size of the) sources you plan to harvest and the
capabilities of your computer. The more, the better. The author uses a VM of 35GB with
10GB memory and 3 vCPUs on an 11th gen Intel i7 mobile processor. 

Ricgraph has been
developed with Python 3.11. For some features you need at least Python 3.9.
E.g., if you have Ubuntu 20.04, you can install Python 3.11 as follows:
* Login as user *root*.
* Type the following commands:
  ```
  add-apt-repository ppa:deadsnakes/ppa
  apt install python3.11
  ```
* Exit from user *root*.

## Steps to take

1. Install your graph database backend (choose one of these):
   * [Install Neo4j Desktop](#install-neo4j-desktop) (recommended, since it includes Bloom).
     Optional: [Install the Bloom configuration](#install-bloom-configuration).
   * [Install and start Neo4j Community 
     Edition](ricgraph_as_server.md#install-and-start-neo4j-community-edition).
   * [Install and start Memgraph](ricgraph_as_server.md#install-and-start-memgraph).
1. [Download Ricgraph](#download-ricgraph).
1. [Use a Python virtual environment and install Python 
   requirements](#use-a-python-virtual-environment-and-install-python-requirements).
1. Create and update the [Ricgraph initialization file](#Ricgraph-initialization-file). This is also the
   place where you specify which graph database backend you use.
1. Start 
   - harvesting data, see [Ricgraph harvest scripts](ricgraph_harvest_scripts.md);
   - writing scripts, see [Ricgraph script writing](ricgraph_script_writing.md).
1. [Execute queries and visualize the results](ricgraph_query_visualize.md).

Other things you might want to do, if you use Neo4j:
* [Create a Neo4j Desktop database dump of Ricgraph](#create-a-neo4j-desktop-database-dump-of-ricgraph).
* [Restore a Neo4j Desktop database dump of Ricgraph in Neo4j Desktop](#restore-a-neo4j-desktop-database-dump-of-ricgraph-in-neo4j-desktop).
* [Restore a Neo4j Desktop database dump of Ricgraph in Neo4j Community 
  Edition](#restore-a-neo4j-desktop-database-dump-of-ricgraph-in-neo4j-community-edition).

## Install Neo4j Desktop

To install, you can either use the [Ricgraph Makefile](#ricgraph-makefile) and execute
command `make install_neo4j_desktop`, or follow the steps below.

1. Install Neo4j Desktop Edition (it is free). 
   To do this, go to the 
   [Neo4j Deployment Center](https://neo4j.com/deployment-center). 
   Go to section "Neo4j Desktop". Choose the latest version of Neo4j Desktop.
   Download the Linux version. It is an [AppImage](https://en.wikipedia.org/wiki/AppImage),
   so it can be installed and used without root permissions. You will be asked to fill in a form before
   you can download. In the following screen you will be given a "Neo4j Desktop Activation Key". Save it.
1. The downloaded file is called something
   like *neo4j-desktop-X.Y.Z-x86_64.AppImage*, where *X.Y.Z* is a version number.
   Make it executable using "chmod 755 \[filename\]". 

### Post-install steps Neo4j Desktop
1. Start Neo4j Desktop by clicking on the downloaded file. 
1. Accept the license. 
1. Enter your activation key in the right part of the screen.
   Click "Activate".
   If you do not have a key, fill in the left part of the screen.
   Click "Register with Email".
   Wait awhile.
1. Choose whether you would like to participate in anonymous reporting.
1. You may be offered updates for Neo4j Desktop components, please update.
1. Move your mouse to "Example Project" in the left column.
   A red trash can icon appears. Click it to remove the Example
   Project database "Movie DBMS". Confirm. Then wait awhile.
1. The text "No projects found" will appear. Create a project by clicking the button "+ New Project".
1. The text "Project" appears with the text "Add a DBMS to get started". Click on the "+ Add" button
   next to it and select "Local DBMS". Leave the name as it is ("Graph DBMS") and fill in a password. 
   Click "Create".
1. [This step is not necessary if you use the [Ricgraph Makefile](#ricgraph-makefile).]
   Insert the password in field *graphdb_password* in
   the [Ricgraph initialization file](#Ricgraph-initialization-file), see below.
1. Exit Neo4j Desktop using the "File" menu and select "Quit". If your database was active
   a message similar to "Your DBMS [name] is running, are you sure you want to quit" appears,
   choose "Stop DBMS, then quit".
1. Ready.

Now we need to find the port number which Neo4j Desktop is using:

1. [Start Neo4j Desktop](ricgraph_query_visualize.md#start-neo4j-desktop). Start the Graph DBMS.
1. Click on the words "Graph DBMS". At the right (or below, 
   depending on the width of the Neo4j Desktop window) a new screen appears.
   Look at the tab "Details". Note the port number next to "Bolt port" (the default
   value is 7687).
   Insert this port number in field *graphdb_port* in
   the [Ricgraph initialization file](#Ricgraph-initialization-file), see below.
1. Ready.

## Install Bloom configuration

This is only necessary if you plan to use Bloom. If you don't know, skip this step for now,
you can come back to it later.

1. [Start Neo4j Desktop](ricgraph_query_visualize.md#start-neo4j-desktop).
1. Click on the icon <img src="images/neo4j1.jpg" height="20">
   on the left side of Neo4j Desktop.
1. Click on "Neo4j Bloom". A new window appears.
1. In this window, click on the icon <img src="images/neo4j2.jpg" height="20">
   at the top left. A Bloom "Perspective" slides out
   (Neo4j has an
   [extensive description how to
   use it](https://neo4j.com/docs/bloom-user-guide/current/bloom-visual-tour/perspective-drawer)).
1. Click on "neo4j > Untitled Perspective 1".
1. A new window appears.
   Right of the words "Untitled Perspective 1" there are three vertical dots. Click on it.
   Click on "Delete". The perspective "Untitled Perspective 1" is removed.
1. In the same window, right of the word "Perspectives" click on the word "Import".
   A file open window appears. Go to directory
   [neo4j_config](../neo4j_config) that is part of Ricgraph and
   select file *ricgraph_bloom_config.json*. Click "Open".
   The perspective "ricgraph_bloom_config" is loaded.
1. Click on the text "ricgraph_bloom_config".
1. Note that the text "neo4j > Untitled Perspective 1"
   has been changed in "neo4j > ricgraph_bloom_config".
1. A few centimeters below "neo4j > ricgraph_bloom_config", just below the text "Add category",
   click on the oval "RicgraphNode". At the right, a new window will appear.
1. In this window, below the word "Labels", check if an oval box with the text "RicgraphNode" is
   shown. If not, click on "Add labels", click on "RicgraphNode".
1. Click on the icon <img src="images/neo4j2.jpg" height="20">
   to go back to the main screen of Bloom.
1. Click on the cog icon below <img src="images/neo4j2.jpg" height="20">, you might want
   to set "Use classic search" to "on".
1. Ready.

## Download Ricgraph

To you use the [Ricgraph Makefile](#ricgraph-makefile),
this will be done automatically while creating a Python virtual environment
(see the following section).

You can choose two types of downloads for Ricgraph:

* The latest released version. Go to the
  [Release page of Ricgraph](https://github.com/UtrechtUniversity/ricgraph/releases),
  choose the most recent version, download either the *zip* or *tar.gz* version.
* The "cutting edge" version. Go to the
  [GitHub page of Ricgraph](https://github.com/UtrechtUniversity/ricgraph/),
  click the green button "Code", choose tab "Local", choose "Download zip".

## Use a Python virtual environment and install Python requirements

To do this, you can either use the [Ricgraph Makefile](#ricgraph-makefile) and execute
command `make full_singleuser_install`, or follow the steps below.

To be able to use Ricgraph, you will need a Python virtual environment.
Virtual environments are a kind of lightweight Python environments,
each with their own independent set of Python packages installed
in their site directories. A virtual environment is created on top of
an existing Python installation.
There are two ways of doing this:
* Using Python's venv module;
* Using a Python Integrated development environment (IDE).

### Using Python's venv module
* Using Python's venv module.
  Read [Create a Python virtual environment and install Ricgraph in
  it](ricgraph_as_server.md#create-a-python-virtual-environment-and-install-ricgraph-in-it).
  This documentation has been written for a multi-user installation of Ricgraph.
  To use it for a single users install (as you are doing since you are on this page):
  * Suppose you are a user with login _alice_.
  * Suppose your home directory is _/home/alice_ (check this by typing ``cd`` followed
    by ``pwd``).
  * For every occurrence of _/opt_ in
    [Create a Python virtual environment and install Ricgraph in
    it](ricgraph_as_server.md#create-a-python-virtual-environment-and-install-ricgraph-in-it),
    read _/home/alice_, and ignore any references to "login as user _root_" and ``chown``.
  * Follow the other instructions as written. 

### Using a Python Integrated development environment (IDE)
* Using a Python
  [Integrated development
  environment (IDE)](https://en.wikipedia.org/wiki/Integrated_development_environment),
  such as [PyCharm](https://www.jetbrains.com/pycharm).
  An IDE will automatically generate a virtual environment, and any time you
  use the IDE, it will "transfer" you to that virtual environment.
  It will also help to execute and debug your scripts.
  * If PyCharm does not automatically generate a virtual environment, you
    need to go to File --> Settings --> Project: [your project name] --> 
    Python Interpreter, and check if
    there is a valid interpreter in the right column next to
    "Python Interpreter". If not, add one, using "Add Interpreter",
    and choose for example "Add Local Interpreter". A venv will be generated.
  * Next, ``unzip`` or ``tar xf`` the downloaded file for Ricgraph (see previous section).
  * Install the Python requirements.
    Depending on the Python IDE, single or double-click on
    file *requirements.txt*. Probably, a button or text appears
    that asks you to install requirements. Click on it.
  
    If this does not work, type in the IDE (PyCharm) Terminal:
    ```
    pip3.11 install -r requirements.txt
    ```
    You may want to change *3.11* in *pip3.11* for the Python version you use.

### Notable dependencies used in Ricgraph:
* [PyAlex](https://github.com/J535D165/pyalex).
  PyAlex is a Python library for [OpenAlex](https://openalex.org/).
  OpenAlex is an index of hundreds of millions of interconnected scholarly papers, authors,
  institutions, and more. OpenAlex offers a robust, open, and free [REST API](https://docs.openalex.org/)
  to extract, aggregate, or search scholarly data.
  PyAlex is a lightweight and thin Python interface to this API.

## Ricgraph initialization file

Ricgraph requires an initialization file. A sample file is included as *ricgraph.ini-sample*.
You need to copy this file to *ricgraph.ini* and modify it
to include settings for your graph database backend, and
API keys and/or email addresses for other systems you plan to use.

### Settings for graph database backend
Ricgraph has a *[GraphDB]* section where you have to specify the graph database
backend that you will be using. First, you will need to set 
the parameter *graphdb* to the graph database backend name (you can
choose between *neo4j* and *memgraph*). Further down that section, you will have
to fill in six parameters for hostname, port number, username, etc. The comments
in the initialization file explain how to do that.

### Extending Ricgraph with new properties in the nodes
Optionally, you can extend Ricgraph by adding new
[properties of nodes](ricgraph_details.md#Properties-of-nodes-in-Ricgraph).
Before you can do this, [download Ricgraph](#download-ricgraph).

### RICGRAPH_NODEADD_MODE
There is a parameter *RICGRAPH_NODEADD_MODE* in the initialization file 
which influences how nodes are added to Ricgraph. Suppose we harvest a source system
and that results in the following table:

| FULL_NAME | ORCID               |
|-----------|---------------------|
| Name-1    | 0000-0001-1111-1111 |
| Name-2    | 0000-0001-1111-2222 |
| Name-3    | 0000-0001-1111-2222 |
| Name-4    | 0000-0001-1111-3333 |

*Name-2* and *Name-3* have the same ORCID. This may be correct, e.g. if *Name-2* is a name variant
of *Name-3*, e.g. *John Doe* vs *J. Doe*, but it also may not be correct, e.g. if 
*Name-2* is *John* and *Name-3* is *Peter* (possibly caused by a typing mistake in a
source system). There is no way for Ricgraph to know which of these two options it is.

RICGRAPH_NODEADD_MODE can be either *strict* or *lenient*:
* *strict* (default setting): only add nodes to Ricgraph which conform to the model
  described in the [Implementation details](ricgraph_details.md). 
  In the example above, *ORCID* *0000-0001-1111-2222* will not be inserted.
* *lenient*: add every node.
  In the example above, *ORCID* *0000-0001-1111-2222* will be inserted.

This will have the following consequences: 
* *strict*: since *ORCID* *0000-0001-1111-2222* 
  will not be inserted, a research output from a person with
  that *ORCID* may not be inserted in Ricgraph. Or the research output will be inserted,
  but it might not be linked to the person with this *ORCID*.
* *lenient*: as has been described [Implementation details](ricgraph_details.md), *person-root*
  "represents" a person. Person identifiers (such as *ORCID*) 
  and research outputs are connected to the
  *person-root* node of a person. 
  That means that the *person-root* node is connected to everything a person has contributed to. 
 
  In the example above, *ORCID* *0000-0001-1111-2222* 
  is inserted. That means that the *person-root*s of the two persons 
  *Name-2* or *Name-3* are "merged" and
  that all research outputs of *Name-2* and *Name-3* will be connected to one *person-root* node.
  After this has been done, there is no way to know which research output belongs to
  *Name-2* or *Name-3*. 
 
  As said, that is fine if *Name-2* and *Name-3* are name variants,
  but not fine if they are different names.
  (Side note: if you want to capture spelling variants, you may want to use a fuzzy string match library
  such as [TheFuzz](https://github.com/seatgeek/thefuzz).)

*Lenient* is advisable if the sources you harvest from do not contain errors. However, the author
of Ricgraph has noticed that this does not occur often, therefore the default is *strict*.

## Using Ricgraph
Before you can do anything with Ricgraph, you need to harvest sources,
see [Ricgraph harvest scripts](ricgraph_harvest_scripts.md).
After you have harvested sources, you can execute queries and visualize the results,
see [Query and visualize Ricgraph](ricgraph_query_visualize.md).


## Dumping and restoring the Ricgraph database
Depending on your situation (whether you use Neo4j Desktop or
Neo4j Community Edition), this section lists the methods for
dumping and restoring the Ricgraph database:
* [Create a Neo4j Desktop database dump of Ricgraph](#create-a-neo4j-desktop-database-dump-of-ricgraph)
* [Create a Neo4j Community Edition database dump of Ricgraph](#create-a-neo4j-community-edition-database-dump-of-ricgraph)
* [Restore a Neo4j Desktop database dump of Ricgraph in Neo4j Desktop](#restore-a-neo4j-desktop-database-dump-of-ricgraph-in-neo4j-desktop)
* [Restore a Neo4j Desktop database dump of Ricgraph in Neo4j Community Edition](#restore-a-neo4j-desktop-database-dump-of-ricgraph-in-neo4j-community-edition)
* [Restore a Neo4j Community Edition database dump of Ricgraph in Neo4j Community Edition](#restore-a-neo4j-community-edition-database-dump-of-ricgraph-in-neo4j-community-edition)

### Create a Neo4j Desktop database dump of Ricgraph
To create a Neo4j Desktop database dump of Ricgraph, follow these steps:
1. Start Neo4j Desktop if it is not running, or
   stop the graph database if it is running.
1. Hoover over the name of your graph database (probably "Graph DBMS"),
   and click on the three horizontal dots at the right.
1. Select "Dump".
1. Your graph database will be dumped. This may take a while. When it
   is ready, a message appears.
1. Ready.

### Create a Neo4j Community Edition database dump of Ricgraph
To do this, you can either use the [Ricgraph Makefile](#ricgraph-makefile) and execute
command `make dump_graphdb_neo4j_community`, or follow the steps below.

To create a Neo4j Community Edition database dump of Ricgraph, follow these steps:
1. Login as user *root*.
1. Stop Neo4j Community Edition:
   ```
   systemctl stop neo4j.service
   ```
1. To be able to restore a Neo4j database dump you need to set several permissions
   on */etc/neo4j*:
   ```
   chmod 640 /etc/neo4j/*
   chmod 750 /etc/neo4j
   ```
1. Do the database dump:
   ```
   neo4j-admin database dump --expand-commands system --to-path=[path to database dump directory]
   neo4j-admin database dump --expand-commands neo4j --to-path=[path to database dump directory]
   ```
1. Start Neo4j Community Edition:
   ```
   systemctl start neo4j.service
   ```
1. Check the log for any errors, use one of:
   ```
   systemctl -l status neo4j.service
   journalctl -u neo4j.service
   ```
1. Exit from user *root*.
 

### Restore a Neo4j Desktop database dump of Ricgraph in Neo4j Desktop
To restore a 
[Neo4j Desktop database dump of Ricgraph](#create-a-neo4j-desktop-database-dump-of-ricgraph) 
in Neo4j Desktop, follow these steps:
1. Start Neo4j Desktop if it is not running, or 
   stop the graph database if it is running.
1. Click on the button "Add" on the right side of "Project" and select "File".
1. Select the file "neo4j.dump" from a previous Neo4j Desktop database dump.
   This file will be added to the "File" section a little down the "Project" window.
1. Hoover over this file and click on the three horizontal dots at the right.
1. Select "Create new DBMS from dump".
1. Give it a name, e.g. "Graph DBMS from import file".
1. When asked, enter the password you have specified in 
   the [Ricgraph initialization file](#ricgraph-initialization-file)
   (this saves you from entering a new password in that file).
1. A new local graph database is being created. This may take a while.
1. Hoover over the newly created graph database and click "Start" to run it.
1. Once it is active, [install the Bloom configuration](#install-bloom-configuration).
1. Now you are ready to explore the data 
   using [Bloom](ricgraph_query_visualize.md#how-to-use-bloom)
   or [Ricgraph Explorer](ricgraph_explorer.md).

### Restore a Neo4j Desktop database dump of Ricgraph in Neo4j Community Edition
To restore a
[Neo4j Desktop database dump of Ricgraph](#create-a-neo4j-desktop-database-dump-of-ricgraph)
in Neo4j Community Edition, follow these steps:
1. Login as user *root*.
1. Stop Neo4j Community Edition:
   ```
   systemctl stop neo4j.service
   ```
1. To be able to restore a Neo4j database dump you need to set several permissions
   on */etc/neo4j*:
   ```
   chmod 640 /etc/neo4j/*
   chmod 750 /etc/neo4j
   ```
1. Save the old database:
   ```
   cd /var/lib/neo4j
   mv data/ data-old
   ```
1. Go back to your working directory and restore the database dump:
   ```
   cd
   neo4j-admin database load --expand-commands neo4j --from-path=[path to database dump directory] --overwrite-destination=true
   ```
   For *path to database dump directory*, specify the path, not the path and the name of the
   database dump file (this name is *neo4j.dump*, it will be inferred automatically
   by the *neo4j-admin* command).
1. Set the correct permissions on */var/lib/neo4j/data*:
   ```
   cd /var/lib/neo4j
   chown -R neo4j:neo4j data
   ```
1. Start Neo4j Community Edition:
   ```
   systemctl start neo4j.service
   ```
1. Check the log for any errors, use one of:
   ```
   systemctl -l status neo4j.service
   journalctl -u neo4j.service
   ```
1. In your web browser, go to 
   [http://localhost:7474/browser](http://localhost:7474/browser).
1. Neo4j will ask you to login, use username *neo4j* and password *neo4j*.
1. Neo4j will ask you to change your password, 
   for the new password, enter the password you have specified in
   the [Ricgraph initialization file](#ricgraph-initialization-file)
   (this saves you from entering a new password in that file).
1. Restart Ricgraph Explorer if you use 
   [Ricgraph in a multi-user environment](ricgraph_as_server.md):
   ```
   systemctl restart ricgraph_explorer_gunicorn.service
   ```
1. Check the log for any errors, use one of:
   ```
   systemctl -l status ricgraph_explorer_gunicorn.service
   journalctl -u ricgraph_explorer_gunicorn.service
   ```
1. Done. If all works well you might want to remove your old database:
   ```
   cd /var/lib/neo4j
   rm -r data-old
   ```
1. Exit from user *root*.


### Restore a Neo4j Community Edition database dump of Ricgraph in Neo4j Community Edition
To do this, you can either use the [Ricgraph Makefile](#ricgraph-makefile) and execute
command `make restore_graphdb_neo4j_community`, or follow the steps below.

To restore a
[Neo4j Community Edition database dump of Ricgraph](#create-a-neo4j-community-edition-database-dump-of-ricgraph)
in Neo4j Community Edition, follow these steps:
1. Login as user *root*.
1. Stop Neo4j Community Edition:
   ```
   systemctl stop neo4j.service
   ```
1. To be able to restore a Neo4j database dump you need to set several permissions
   on */etc/neo4j*:
   ```
   chmod 640 /etc/neo4j/*
   chmod 750 /etc/neo4j
   ```
1. Save the old database:
   ```
   cd /var/lib
   mv neo4j/ neo4j-old
   mkdir /var/lib/neo4j
   ```
1. Go back to your working directory and restore the database dump:
   ```
   cd
   neo4j-admin database load --expand-commands system --from-path=[path to database dump directory] --overwrite-destination=true
   neo4j-admin database load --expand-commands neo4j --from-path=[path to database dump directory] --overwrite-destination=true
   ```
   For *path to database dump directory*, specify the path, not the path and the name of the
   database dump file, it will be inferred automatically
   by the *neo4j-admin* command.
1. Set the correct permissions on */var/lib/neo4j/data*:
   ```
   cd /var/lib
   chown -R neo4j:neo4j neo4j
   ```
1. Start Neo4j Community Edition:
   ```
   systemctl start neo4j.service
   ```
1. Check the log for any errors, use one of:
   ```
   systemctl -l status neo4j.service
   journalctl -u neo4j.service
   ```
1. Restart Ricgraph Explorer if you use
   [Ricgraph in a multi-user environment](ricgraph_as_server.md):
   ```
   systemctl restart ricgraph_explorer_gunicorn.service
   ```
1. Check the log for any errors, use one of:
   ```
   systemctl -l status ricgraph_explorer_gunicorn.service
   journalctl -u ricgraph_explorer_gunicorn.service
   ```
1. Done. If all works well you might want to remove your old database:
   ```
   cd /var/lib
   rm -r neo4j-old
   ```
1. Exit from user *root*.


## Ricgraph on Windows
The easiest way to go is to [Install and use
Ricgraph in a container](ricgraph_containerized.md).
This is relatively quick but it offers limited possibilities.

If you would like to go for a "full" install of Ricgraph on Windows using either 
[Install and configure Ricgraph for a single user](ricgraph_install_configure.md) or 
[Install and configure Ricgraph as a server](ricgraph_as_server.md),
you are very probably the first
person to do so, as far as known. The creator of Ricgraph has no experience
in developing software on Windows. So please let me know which steps you have
taken, so I can add them to this documentation. If you are a Windows user,
I would recommend to create a Linux virtual machine using e.g.
[VirtualBox](https://www.virtualbox.org), and install Ricgraph in that 
virtual machine as described above.
