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
 

On this page you can find:
* [Fast and recommended way to install Ricgraph](#fast-and-recommended-way-to-install-ricgraph-for-a-single-user)
* [Requirements](#requirements-for-ricgraph)
* [Ricgraph Makefile](#ricgraph-makefile)
* [Steps to take](#steps-to-take)
* [Download Ricgraph](#download-ricgraph)
* [Use a Python virtual environment and install Python requirements](#use-a-python-virtual-environment-and-install-python-requirements)
* [Ricgraph initialization file](#ricgraph-initialization-file)
* [Using Ricgraph](#using-ricgraph)
* [Dumping and restoring the Ricgraph database](#dumping-and-restoring-the-ricgraph-database)
* [Ricgraph on Windows](#ricgraph-on-windows)

[Return to main README.md file](../README.md).


## Fast and recommended way to install Ricgraph for a single user
To follow this procedure, you need to be able to change to user *root*.
This is the recommended method to install Ricgraph for a single user, since
it will install everything automatically (by using the Makefile).
1. [Check the requirements](#requirements-for-ricgraph).
1. Get the most recent Ricgraph Makefile.
   Type as regular user (i.e., be sure you are not user *root*):
   ```
   cd
   wget https://raw.githubusercontent.com/UtrechtUniversity/ricgraph/main/Makefile
   ```
   Read more at [Ricgraph Makefile](#ricgraph-makefile).
1. Install Neo4j Community Edition. Only for this step you need to be user *root*.
   Type:
   ```
   sudo bash
   make install_enable_neo4j_community
   exit
   ```
   Read more at [Install and start Neo4j Community Edition graph database
   backend](ricgraph_backend_neo4j.md#install-and-start-neo4j-community-edition).
1. Download and install Ricgraph in your home directory.
   Read more at the sections below.
   Type as regular user (i.e., be sure you are not user *root*):
   ```
   make install_ricgraph_singleuser_neo4jcommunity
   ```
1. Harvest two source systems in Ricgraph:
   ```
   make run_batchscript
   ```
   This will harvest two source systems,
   [the data repository Yoda](https://www.uu.nl/en/research/yoda) and
   [the Research Software Directory](https://research-software-directory.org).
   To read more about harvesting data, 
   see [Ricgraph harvest scripts](ricgraph_harvest_scripts.md).
   To read more about writing harvesting scripts,
   see [Ricgraph script writing](ricgraph_script_writing.md).
1. Start Ricgraph Explorer to browse the information harvested:
   ```
   make run_ricgraph_explorer
   ```
   In your web browser, go to http://127.0.0.1:3030.
   Read more at [Ricgraph Explorer](ricgraph_explorer.md), or
   at [Execute queries and visualize the results](ricgraph_query_visualize.md).
1. If everything succeeded, you can skip the remainder of this page.
   If not, the remainder of this page may help in finding solutions.

If you are not able to change to user *root*,
change step 3 and 4.
This is a less recommended method to install Ricgraph for a single user,
since you have to do a number of things manually.

3. Install Neo4j Desktop. Type:
   ```
   make install_neo4j_desktop
   ```
   Read more at [Install and start Neo4j Desktop graph database
   backend](ricgraph_backend_neo4j.md#install-neo4j-desktop).
   You will need to do a number of post install steps.
   Any time you want to use Neo4j Desktop, you will need to start
   it by hand, read [Start Neo4j Desktop](ricgraph_backend_neo4j.md#start-neo4j-desktop).
4. Download and install Ricgraph in your home directory.
   Read more at the sections below. Type:
   ```
   make install_ricgraph_singleuser_neo4jdesktop
   ```

## Requirements for Ricgraph
* To install the graph database backend and Ricgraph,
  you will need access to a Linux machine.
  All instructions in this documentation are written for a Linux machine,
  except when otherwise noted. This doesn't mean that you cannot install
  the graph database backend and Ricgraph *directly* on a Mac or Windows machine,
  it means that the author has no experience with this, except for
  [Read here if you would like to install Ricgraph on
  Windows](#ricgraph-on-windows).
* If you have a Mac or Windows machine, you can create a
  Linux virtual machine (VM) on it using e.g. VirtualBox. This also holds
  if you have a Linux machine and would like to install
  the graph database backend and Ricgraph separated from your usual working environment.
* A virtual machine is like a separate computer in a box that is running on your own
  computer. You can install anything in it, and it will not interfere with your
  usual working environment on your machine.
* So, to install the graph database backend and Ricgraph,
  you can use your own Linux (virtual) machine, or a Linux VM
  provided by your organization, or you might
  want to use a Linux VM on SURF Research Cloud.

  Own Linux (virtual) machine:
    * On your own Mac, Windows, or Linux machine, 
      install [VirtualBox](https://www.virtualbox.org). Create a virtual machine
      in VirtualBox. Install a Linux distribution
      "in" the virtual machine you have just created.
      Then, install the graph database backend and Ricgraph in the Linux virtual machine
      you have just created, as described on this page or on
      [Install and configure
      Ricgraph as a server](ricgraph_as_server.md). 
    * There are many tutorials on installing VirtualBox on internet.
      For example, [How to Install VirtualBox on Ubuntu
      (Beginner's Tutorial)](https://itsfoss.com/install-virtualbox-ubuntu).
      Also, you will need to install the VirtualBox GuestAdditions.
      Read, for example, [How to Install & Use VirtualBox Guest Additions on
      Ubuntu](https://itsfoss.com/virtualbox-guest-additions-ubuntu).
      You need to be user *root* (Linux) or *Administrator* (Windows) on your computer to be able to
      do this.
    * Almost any Linux distribution will work, the author uses both
      [OpenSUSE Leap](https://www.opensuse.org) and
      [Ubuntu](https://ubuntu.com/desktop). Others will also work.
    * For the configuration in VirtualBox, a VM of size 25GB with 4GB memory will work.
      This depends on the (size of the) sources you plan to harvest and the
      capabilities of your computer. The more, the better. The author uses a 
      VirtualBox VM of size 35GB with
      10GB memory and 3 vCPUs on an 11th gen Intel i7 mobile processor.

  Linux VM provided by your organization:
    * Ask your organization.

  Linux VM on SURF Research Cloud:
    * Read [How to install Ricgraph and Ricgraph Explorer on SURF Research
      Cloud](ricgraph_as_server.md#how-to-install-ricgraph-and-ricgraph-explorer-on-surf-research-cloud).
* You will need at least Python 3.9 or newer.
  Ricgraph has been
  developed with Python 3.11. For some features you need at least Python 3.9.
  E.g., if you have Ubuntu 20.04, you can install Python 3.11 as follows:
    * Login as user *root*.
    * Type the following commands:
      ```
      add-apt-repository ppa:deadsnakes/ppa
      apt install python3.11
      ```
      For other Linux distributions there will be similar commands.
    * Exit from user *root*.


## Ricgraph Makefile
A Ricgraph installation involves a number of steps.
Ricgraph uses a *Makefile* to make installation of (parts of) Ricgraph easier.
Such a Makefile automates a number of these steps.
A Makefile command is executed by typing:
```
make [target]
```

To use the Ricgraph Makefile, first go to your home directory on Linux and
then download the most recent version from the GitHub repository, by typing:
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
make allhelp
```
You can add command line parameters to the `make` command, e.g. to get the
Ricgraph *cutting edge* version, or to specify an installation path.
Look in the [Makefile](../Makefile) for possibilities. Any variable defined
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


## Steps to take
Skip this if you have done the
[Fast and recommended way to install Ricgraph for a single 
user](#fast-and-recommended-way-to-install-ricgraph-for-a-single-user).
1. Install your graph database backend (choose one of these):
    * [Install and start Neo4j Community
      Edition](ricgraph_backend_neo4j.md#install-and-start-neo4j-community-edition)
   * [Install Neo4j Desktop](ricgraph_backend_neo4j.md#install-neo4j-desktop)
     (recommended, since it includes Bloom).
     Optional: [Install the Bloom 
     configuration](ricgraph_backend_neo4j.md#install-bloom-configuration-for-neo4j-desktop-optional).
   * [Install and start Memgraph](ricgraph_backend_memgraph.md#install-and-start-memgraph).
1. [Download Ricgraph](#download-ricgraph).
1. [Use a Python virtual environment and install Python 
   requirements](#use-a-python-virtual-environment-and-install-python-requirements).
1. Create and update the [Ricgraph initialization file](#Ricgraph-initialization-file). This is also the
   place where you specify which graph database backend you use.
1. Start 
   - harvesting data, see [Ricgraph harvest scripts](ricgraph_harvest_scripts.md);
   - writing scripts, see [Ricgraph script writing](ricgraph_script_writing.md).
1. [Execute queries and visualize the results](ricgraph_query_visualize.md).


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
Very likely, you may want to use Ricgraph Explorer, read
more on the [Ricgraph Explorer page](ricgraph_explorer.md#how-to-start-ricgraph-explorer).


## Dumping and restoring the Ricgraph database
If you use Neo4j, read more at [Dumping and restoring the Ricgraph
database](ricgraph_backend_neo4j.md#dumping-and-restoring-the-ricgraph-database).


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
