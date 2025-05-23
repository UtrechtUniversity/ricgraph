# Install and configure Ricgraph

This page describes how to install Ricgraph for a single user on Linux.
If you would like to use Ricgraph in a [multi-user environment
on Linux, you will need to install Ricgraph
differently](ricgraph_as_server.md#ricgraph-as-a-server-on-linux).
In case you have no idea what would be the best for your situation, please 
install Ricgraph for a single user on Linux, as described on this page.
Or go for [Ricgraph in a
container](ricgraph_containerized.md#ricgraph-in-a-container).

To install and run Ricgraph for a single user, read
[Fast and recommended way to install 
Ricgraph for a single user](#fast-and-recommended-way-to-install-ricgraph-for-a-single-user).

On this page, you can find:

* [Fast and recommended way to install Ricgraph for a single user](#fast-and-recommended-way-to-install-ricgraph-for-a-single-user)
* [Requirements for Ricgraph](#requirements-for-ricgraph)
* [Ricgraph Makefile](#ricgraph-makefile)
* [Ricgraph initialization file](#ricgraph-initialization-file)
* [Ricgraph on Windows](#ricgraph-on-windows)
* [Steps to take to install Ricgraph for a single user by hand](#steps-to-take-to-install-ricgraph-for-a-single-user-by-hand)

[Return to main README.md file](../README.md#ricgraph---research-in-context-graph).


## Fast and recommended way to install Ricgraph for a single user

### You can change to user *root*
To follow this procedure, you need to be able to change to user *root*.
This is the recommended method to install Ricgraph for a single user, since
it will install everything automatically (by using the 
[Ricgraph Makefile](#ricgraph-makefile)).

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
   On success, the Makefile will print *installed successfully*.
1. Download and install Ricgraph in your home directory.
   Type as regular user (i.e., be sure you are not user *root*):
   ```
   make install_ricgraph_singleuser_neo4j_community
   ```
   On success, the Makefile will print *installed successfully*.
1. Harvest two source systems in Ricgraph:
   ```
   cd $HOME/ricgraph_venv
   make run_bash_script
   ```
   This will harvest two source systems,
   [the data repository Yoda](https://www.uu.nl/en/research/yoda) and
   [the Research Software Directory](https://research-software-directory.org).
   It will print a lot of output, and it will take a few minutes. 
   When ready, it will print *Done*.

   To read more about harvesting data, 
   see [Ricgraph harvest scripts](ricgraph_harvest_scripts.md#ricgraph-harvest-scripts).
   To read more about writing harvesting scripts,
   see [Ricgraph script writing](ricgraph_script_writing.md#ricgraph-script-writing).
1. Start Ricgraph Explorer to browse the information harvested:
   ```
   cd $HOME/ricgraph_venv
   make run_ricgraph_explorer
   ```
   The Makefile will tell you to go to 
   your web browser, and go to 
   [http://127.0.0.1:3030](http://127.0.0.1:3030).
   Read more at [Ricgraph Explorer](ricgraph_explorer.md#ricgraph-explorer).

If everything succeeded, you are done installing Ricgraph for a single user.
If not, sections
[Steps to take to install Ricgraph for a single user by hand](#steps-to-take-to-install-ricgraph-for-a-single-user-by-hand)
or [Install and start Neo4j Community Edition graph database
backend](ricgraph_backend_neo4j.md#install-and-start-neo4j-community-edition) may help in finding solutions.


### You cannot change to user *root*
If you are not able to change to user *root*,
change step 3 and 4 in the previous section.
This is a less recommended method to install Ricgraph for a single user,
since you have to do a number of things manually.

3. Install Neo4j Desktop. Type:
   ```
   make install_neo4j_desktop
   ```
   On success, the Makefile will print *installed successfully*.
   You will need to do a number of [post install 
   steps](ricgraph_backend_neo4j.md#post-install-steps-neo4j-desktop).
   Any time you want to use Neo4j Desktop, you will need to start
   it by hand, read [Start Neo4j Desktop](ricgraph_backend_neo4j.md#start-neo4j-desktop).
4. Download and install Ricgraph in your home directory.
   Read more at the sections below. Type:
   ```
   make install_ricgraph_singleuser_neo4j_desktop
   ```
   On success, the Makefile will print *installed successfully*.

If everything succeeded, you are done installing Ricgraph for a single user.
If not, sections
[Steps to take to install Ricgraph for a single user by hand](#steps-to-take-to-install-ricgraph-for-a-single-user-by-hand)
or [Install and start Neo4j Community Edition graph database
backend](ricgraph_backend_neo4j.md#install-and-start-neo4j-community-edition) may help in finding solutions.

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
  you can use your own Linux machine,
  your own Linux virtual machine, a Linux VM
  provided by your organization, or 
  a Linux VM provided by a Cloud provider such as SURF Research Cloud.

  Own Linux machine:
    * You already have Linux, skip to the next bullet in this list. 
      
  Own Linux virtual machine:
    * On your own Mac, Windows, or Linux machine, 
      install [VirtualBox](https://www.virtualbox.org). Create a virtual machine
      in VirtualBox. Install a Linux distribution
      "in" the virtual machine you have just created.
      Then, install the graph database backend and Ricgraph in the Linux virtual machine
      you have just created, as described on this page or on
      [Install and configure
      Ricgraph as a server](ricgraph_as_server.md#ricgraph-as-a-server-on-linux). 
    * There are many tutorials on installing VirtualBox on internet.
      For example, [How to Install VirtualBox on Ubuntu
      (Beginner's Tutorial)](https://itsfoss.com/install-virtualbox-ubuntu).
    * Also, you will need to install the VirtualBox GuestAdditions.
      They will enable e.g. shared folders with the host and automatic
      adjustment of guest display resolution.
      You install them inside a virtual machine after the 
      guest operating system has been installed.
      Read, for example, [How to Install & Use VirtualBox Guest Additions on
      Ubuntu](https://itsfoss.com/virtualbox-guest-additions-ubuntu).
    * Very probably you will *not* need the VirtualBox Extension Pack.
      You need to be user *root* (Linux) or *Administrator* (Windows) 
      on your computer to be able to do this. Don't do it for now.
    * Almost any Linux distribution will work, the author uses both
      [OpenSUSE Leap](https://www.opensuse.org) and
      [Ubuntu](https://ubuntu.com/desktop). Others will also work.
    * For the configuration in VirtualBox, a VM of size 25GB with 8GB memory will work.
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
  developed with Python 3.11. 
  Check your Python version by typing:
  ```
  python3 --version
  ```
  Look at the first two numbers. If they are lower than 3.9, you will need to install
  a newer Python version. How you do it, is dependent on your Linux version.
  E.g., if you have Ubuntu 20.04, you can install Python 3.11 as follows:
    * Login as user *root*.
    * Type the following commands:
      
      ```
      add-apt-repository ppa:deadsnakes/ppa
      apt install python3.11
      ```
  * Exit from user *root*.
    For other Linux distributions there will be similar commands.
* You need the linux command `make`. Try typing 
  ```
  make
  ```
  If you get an error, install it using your package manager.


## Ricgraph Makefile
A Ricgraph installation involves a number of steps.
Ricgraph uses [*make* and a Makefile](https://www.gnu.org/software/make)
to make installation of (parts of) Ricgraph easier.
A Makefile automates a number of these steps.
A `make` command is executed by typing:
```
make [target]
```
or
```
make [make command line parameter]=[value] [target]
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
In that case, the make command may look like 
```
make ricgraph_version=cuttingedge [target] 
```
or
```
make ricgraph_server_install_dir=/opt/ricgraph_venv [target]
```
Look in file *Makefile* for possibilities. Any variable defined
in the Makefile can be used as `make` command line parameter.
For an example, see the Podman Containerfile in file *Containerfile*.

Most often, you do not need to install the `make` command, but if you get a
"command not found" error message, you need to install it using your Linux
package manager.

If you read the documentation below or on page
[Ricgraph as a server on Linux](ricgraph_as_server.md#ricgraph-as-a-server-on-linux),
you will notice that some sections start with mentioning a Makefile command.
That means, that if you execute that command, the steps in that section will
be done automatically.
Sometimes, you will
have to do some post-install steps, e.g. because you have to choose a password for the
graph database.


## Ricgraph initialization file
Ricgraph requires an initialization file. A sample file is included as *ricgraph.ini-sample*.
You need to copy this file to *ricgraph.ini* and modify it
to include settings for your graph database backend, and
API keys and/or email addresses for other systems you plan to use.
If you have used the Ricgraph Makefile, the copying 
and the settings for the graph database backend will have been set, but
you still need to fill in
API keys and/or email addresses for other systems you plan to use.

### Settings for the graph database backend
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
that influences how nodes are added to Ricgraph. Suppose we harvest a source system
and that results in the following table:

| ISNI   | ORCID               |
|--------|---------------------|
| ISNI-1 | 0000-0001-1111-1111 |
| ISNI-2 | 0000-0001-1111-2222 |
| ISNI-3 | 0000-0001-1111-2222 |
| ISNI-4 | 0000-0001-1111-3333 |

*ISNI-2* and *ISNI-3* have the same ORCID. This may be correct, e.g. if the person
with the *ORCID* has multiple *ISNI* records.
But it also may be incorrect, e.g. if
*ISNI-2* and *ISNI-3* do not refer to the same person,
possibly caused by a typing mistake in a
source system. There is no way for Ricgraph to know which of these two options it is.

RICGRAPH_NODEADD_MODE can be either *strict* or *lenient*:

* *strict* (default setting): only add nodes to Ricgraph which conform to the model
  described in the [Implementation details](ricgraph_details.md#implementation-details). 
  In the example above, *ORCID* *0000-0001-1111-2222* will not be inserted.
* *lenient*: add every node.
  In the example above, *ORCID* *0000-0001-1111-2222* will be inserted.

This will have the following consequences: 

* *strict*: since *ORCID* *0000-0001-1111-2222* 
  will not be inserted, a research output from a person with
  that *ORCID* may not be inserted in Ricgraph. Or the research output will be inserted,
  but it might not be linked to the person with this *ORCID*.
* *lenient*: as has been described [Implementation details](ricgraph_details.md#implementation-details), *person-root*
  "represents" a person. Person identifiers (such as *ORCID*) 
  and research outputs are connected to the
  *person-root* node of a person. 
  That means that the *person-root* node is connected to everything a person has contributed to. 
 
  In the example above, *ORCID* *0000-0001-1111-2222* 
  is inserted. That means that the *person-root*s of the two persons 
  with *ISNI-2* or *ISNI-3* are "merged", and
  that all research outputs of *ISNI-2* and *ISNI-3* will be connected to one *person-root* node.
  After this has been done, there is no way to know which research output belongs to
  *ISNI-2* or *ISNI-3*. 
 
  As said, that is fine if *ISNI-2* and *ISNI-3* refer to the same person (having two ISNIs),
  but not fine if they refer to two different persons.

*Lenient* is advisable if the sources you harvest from do not contain errors. However, with
source systems that contain a lot of information this is not likely,
therefore the default is *strict*.


## Ricgraph on Windows
The easiest way to go is to [Install and use
Ricgraph in a container](ricgraph_containerized.md#ricgraph-in-a-container).
This is relatively quick but it offers limited possibilities.

If you would like to go for a "full" install of Ricgraph on Windows using either 
[Install and configure Ricgraph for a single user](ricgraph_install_configure.md#install-and-configure-ricgraph) or 
[Install and configure Ricgraph as a server](ricgraph_as_server.md#ricgraph-as-a-server-on-linux),
you are very probably the first
person to do so, as far as known. The creator of Ricgraph has no experience
in developing software on Windows. So please let me know which steps you have
taken, so I can add them to this documentation. If you are a Windows user,
I would recommend to create a Linux virtual machine using e.g.
VirtualBox as explained in section [Requirements](#requirements-for-ricgraph), 
and install Ricgraph in that 
virtual machine as described above.


## Steps to take to install Ricgraph for a single user by hand
Skip this section if you have done the
[Fast and recommended way to install Ricgraph for a single
user](#fast-and-recommended-way-to-install-ricgraph-for-a-single-user) and there were no errors.

1. [Install your graph database backend](#install-your-graph-database-backend).
1. [Download Ricgraph](#download-ricgraph).
1. [Use a Python virtual environment and install Python
   requirements](#use-a-python-virtual-environment-and-install-python-requirements).
1. Create and update the [Ricgraph initialization file](#Ricgraph-initialization-file). This is also the
   place where you specify which graph database backend you use.
1. Start harvesting data, see [Ricgraph harvest scripts](ricgraph_harvest_scripts.md#ricgraph-harvest-scripts), or
   writing scripts, see [Ricgraph script writing](ricgraph_script_writing.md#ricgraph-script-writing).
1. Start browsing using
   [Ricgraph Explorer](ricgraph_explorer.md#ricgraph-explorer).


### Install your graph database backend
Install your graph database backend (choose one of these):

* [Install and start Neo4j Community
  Edition](ricgraph_backend_neo4j.md#install-and-start-neo4j-community-edition) (recommended, only possible if you are able to change to user *root*).
* [Install Neo4j Desktop](ricgraph_backend_neo4j.md#install-neo4j-desktop)
  Optional: [Install the Bloom
  configuration](ricgraph_backend_neo4j.md#install-bloom-configuration-for-neo4j-desktop-optional).
* [Install and start Memgraph](ricgraph_backend_memgraph.md#install-and-start-memgraph).

### Download Ricgraph
You can choose two types of downloads for Ricgraph:

* The latest released version. Go to the
  [Release page of Ricgraph](https://github.com/UtrechtUniversity/ricgraph/releases),
  choose the most recent version, download either the *zip* or *tar.gz* version.
* The "cutting edge" version. Go to the
  [GitHub page of Ricgraph](https://github.com/UtrechtUniversity/ricgraph/),
  click the green button "Code", choose tab "Local", choose "Download zip".

### Use a Python virtual environment and install Python requirements

To be able to use Ricgraph, you will need a Python virtual environment.
Virtual environments are a kind of lightweight Python environments,
each with their own independent set of Python packages installed
in their site directories. A virtual environment is created on top of
an existing Python installation.
There are two ways of doing this:

* Using Python's venv module;
* Using a Python Integrated development environment (IDE).

#### Using Python's venv module

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

#### Using a Python Integrated development environment (IDE)

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
    