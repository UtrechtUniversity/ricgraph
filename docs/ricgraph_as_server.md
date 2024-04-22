## Ricgraph as a server on Linux
This page describes how to install and run Ricgraph in a multi-user environment on Linux.
If you would like to use Ricgraph in such an environment, you will
need to install Ricgraph differently than described in 
[Install and configure Ricgraph](ricgraph_install_configure.md).
*Multi-user environment* means that you install Ricgraph on a (virtual) machine, 
and that various persons can log on to that machine, each with his own user id
and password, and that each person will be able to use Ricgraph by using a
web link in their web browser.

The reason that a multi-user environment for Ricgraph is different from installing and using
Ricgraph on your own user id, is that you will need to run the graph database backend and
[Ricgraph Explorer](ricgraph_explorer.md) 
as a system user instead of running it using your own user id.
If you run Ricgraph with your own user id, you will be the only user able to use it.
In case other persons on that same machine would like to use Ricgraph, they have
to install it for themselves. 
By installing Ricgraph as a server, as described on this page,
Ricgraph will be started automatically when your machine boots, and
it can be used by any user on that machine.

[Go to the documentation describing the installation and configuration
of Ricgraph for a single user](ricgraph_install_configure.md).

To install and run Ricgraph in a multi-user environment, you need to do most of
the following steps:
* [Check the requirements](#check-the-requirements).
* Install a graph database backend:
  * [Install and start Neo4j Community Edition](#install-and-start-neo4j-community-edition).
  * [Install and start Memgraph](#install-and-start-memgraph).
* [Create a ricgraph user and group](#create-a-ricgraph-user-and-group).
* [Create a Python virtual environment and install Ricgraph in 
  it](#create-a-python-virtual-environment-and-install-ricgraph-in-it).
* [Run Ricgraph scripts from the command 
  line or as a cronjob](#run-ricgraph-scripts-from-the-command-line-or-as-a-cronjob).
* [Use a service unit file to run Ricgraph 
  Explorer](#use-a-service-unit-file-to-run-ricgraph-explorer).
* [Use Apache and WSGI to make Ricgraph Explorer accessible from outside your virtual 
  machine](#use-apache-and-wsgi-to-make-ricgraph-explorer-accessible-from-outside-your-virtual-machine).
* [Restore a Neo4j Desktop database dump of Ricgraph in Neo4j Community
  Edition](#restore-a-neo4j-desktop-database-dump-of-ricgraph-in-neo4j-community-edition).
* [How to install Ricgraph and Ricgraph Explorer on SURF Research 
  Cloud](#how-to-install-ricgraph-and-ricgraph-explorer-on-surf-research-cloud)
* [How to solve an AttributeError: 'Neo4jDriver' object has no attribute 
  'execute_query'](#how-to-solve-an-attributeerror-neo4jdriver-object-has-no-attribute-executequery).

[Return to main README.md file](../README.md).


### Check the requirements
* You will need access to a Linux virtual machine.
  You can use your own, or one provided by your organization, or you might
  want to use SURF Research Cloud.
* For SURF Research Cloud, 
  read [How to install Ricgraph and Ricgraph Explorer on SURF Research
  Cloud](#how-to-install-ricgraph-and-ricgraph-explorer-on-surf-research-cloud).
* Please check the [Requirements for Ricgraph](ricgraph_install_configure.md#requirements).

 
### Install and start Neo4j Community Edition
* Login as user *root*.
* Install Neo4j Community Edition. 
  To do this, go to the 
  [Neo4j Deployment Center](https://neo4j.com/deployment-center). 
  Go to section "Graph Database Self-Managed", choose "Community".
  Choose the latest version of Neo4j. Then choose your favorite package
  format:
  * OpenSUSE: "Red Hat Linux Package (rpm)".
  * Debian/Ubuntu: "Debian/Ubuntu Package (deb)".
 
  Download the package and install it.
  You might get an error message about a failed dependency on *cypher-shell*,
  or on other dependencies.
  * OpenSUSE: use either ``rpm -i <packagename>`` (first install)
    or ``rpm -U <packagename>`` (update).
  * Debian/Ubuntu: use ``apt install <packagename>`` 
  * If you get an error message about a failed dependency on *cypher-shell*, install
    *cypher-shell* separately as follows:
    * Go to the
      [Tools tab of the Neo4j Deployment Center](https://neo4j.com/deployment-center/#tools-tab). 
      Go to section "Cypher Shell", choose the version of Cypher Shell that matches
      the version of the Neo4j Community Edition you have downloaded above.
      Then choose the version that fits your Linux version:
      * OpenSUSE: "Linux cypher-shell_X.YY.0-Z.noarch.rpm".
      * Debian/Ubuntu: "Linux cypher-shell_X.YY.0_all.deb".
    * Click "Download" and install it. 
    * Install again Neo4j Community Edition (see above).
  * If you get an error message about failed other dependencies, install
    these other packages.

* If the installation has finished, make sure it runs by typing:
  ``` 
  systemctl enable neo4j.service
  systemctl start neo4j.service
  ```
  Check the log for any errors, use one of:
  ```
  systemctl -l status neo4j.service
  journalctl -u neo4j.service
  ```
* Exit from user *root*.
* Change the default username and password of Neo4j:
  * In your web browser, go to
    [http://localhost:7474/browser](http://localhost:7474/browser).
  * Neo4j will ask you to login, use username *neo4j* and password *neo4j*.
  * Neo4j will ask you to change your password. Change it.
    You will need this new password in section
    [Create a Python virtual environment and install Ricgraph in
    it](#create-a-python-virtual-environment-and-install-ricgraph-in-it) below.
  

### Install and start Memgraph
As an alternative to Neo4j, you can also use
[Memgraph](https://memgraph.com).
Memgraph is an in memory graph database 
and therefore (much) faster than Neo4j. 
However, it has not been tested extensively with Ricgraph yet.
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
 

### Create a ricgraph user and group
* Login as user *root*.
* Create group and user *ricgraph*. First check if they exist:
  ```
  grep ricgraph /etc/group
  grep ricgraph /etc/passwd
  ```
  If you get output, they already exist, and you don't need to do this step.
  If you get no output, you will need to create the group and user:
  ```
  groupadd --system ricgraph
  useradd --system --comment "Ricgraph user" --no-create-home --gid ricgraph ricgraph
  ```
* Exit from user *root*.
  
  
### Create a Python virtual environment and install Ricgraph in it
* Suppose you are a user with login *alice* and you are in Linux group *users*.
* Login as user *root*.
* For Debian/Ubuntu: type: 
  ```
  apt install python3-venv
  ``` 
* Go to directory */opt*, type: 
  ```
  cd /opt
  ```
* Create a Python virtual environment:
  in */opt*, type:
  ```
  python3 -m venv ricgraph_venv
  ```
* Change the owner and group to your own user *alice* and group *users*,
  in */opt*, type:
  ```
  chown -R alice:users /opt/ricgraph_venv
  ```
* Exit from user *root*. Do the following steps as your own user.
* Download the latest release of Ricgraph from the
  [Ricgraph downloads
  page](https://github.com/UtrechtUniversity/ricgraph/releases)
  to directory */opt/ricgraph_venv*.
  Get the ``tar.gz`` version.
* Install Ricgraph: 
  go to */opt/ricgraph_venv*, type: 
  ```
  tar xf /opt/ricgraph-X.YY.tar.gz 
  ```
  (X.YY is the version number you downloaded). You will get a directory 
  */opt/ricgraph_venv/ricgraph-X.YY*.
* Merge the Ricgraph you have extracted with *tar* with the virtual environment,
  and do some cleanup:
  in */opt/ricgraph_venv*, type: 
  ```
  mv ricgraph-X.YY/* /opt/ricgraph_venv
  rm -r /opt/ricgraph_venv/ricgraph-X.YY
  rm /opt/ricgraph_venv/ricgraph-X.YY.tar.gz
  ```
* Activate the Python virtual environment: 
  in */opt/ricgraph_venv*, type: 
  ```
  source bin/activate
  ```
* Install the standard Python requirements:
  in */opt/ricgraph_venv*, type:
  ```
  pip install setuptools pip wheel
  ```
* Install the Python requirements for Ricgraph:
  in */opt/ricgraph_venv*, type:
  ```
  pip install -r requirements.txt
  ```
* Create a Ricgraph initialization file, 
  read [Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file).
  This is also the
  place where you specify which graph database backend you use.
  You can find these settings in section *GraphDB*.
  * For Neo4j, enter the new password for Neo4j from section
    [Install and start Neo4j Community Edition](#install-and-start-neo4j-community-edition)
    at the parameter _graphdb_password_.
* Deactivate the Python virtual environment: 
  type 
  ```
  deactivate
  ```
* Login as user *root*.
* Change the owner and group to ricgraph of directory */opt/ricgraph_venv*.
  In */opt*, type 
  ```
  chown -R ricgraph:ricgraph /opt/ricgraph_venv
  ```
* Exit from user *root*.


### Run Ricgraph scripts from the command line or as a cronjob
After following the steps in [Create a Python virtual environment and install Ricgraph in
it](ricgraph_as_server.md#create-a-python-virtual-environment-and-install-ricgraph-in-it),
it is possible to run Ricgraph from the command line or as a
[cronjob](https://en.wikipedia.org/wiki/Cron).
To be able to run these scripts you need to be
user *ricgraph* and group *ricgraph*.
You can do this by using user *ricgraph* in your crontab file (e.g. in */etc/crontab*),
or by using the command
```
sudo su - ricgraph
``` 

If you are finished with these commands, exit from user *ricgraph*.

Examples of commands you can use are:
* harvest from the Research Software Directory:
  ```
  cd /opt/ricgraph_venv/harvest_to_ricgraph_examples; PYTHONPATH=/opt/ricgraph_venv/ricgraph ../bin/python harvest_rsd_to_ricgraph.py
  ```
* harvest all your favorite sources:
  ```
  cd /opt/ricgraph_venv/harvest_to_ricgraph_examples; PYTHONPATH=/opt/ricgraph_venv/ricgraph ../bin/python batch_harvest.py
  ```
* run Ricgraph Explorer:
  ```
  cd /opt/ricgraph_venv/ricgraph_explorer; PYTHONPATH=/opt/ricgraph_venv/ricgraph ../bin/python ricgraph_explorer.py
  ```
  
  
### Use a service unit file to run Ricgraph Explorer
Using a service unit file to run
[Ricgraph Explorer](ricgraph_explorer.md) 
is very useful if you would like to set up a virtual machine that you want to use as
a demo server. After the steps in this section, 
Ricgraph Explorer is run
automatically at the start of the virtual machine, so you can immediately start giving the demo.

For comparison, if you had installed the graph database backend
and Ricgraph for a single user, as
described in 
[the documentation describing the installation and configuration
of Ricgraph for a single user](ricgraph_install_configure.md), 
after the start of the virtual machine, you would need to start the graph database
backend, the virtual environment,
and *ricgraph_explorer.py* by hand.

Using a service unit file will *not* expose Ricgraph Explorer and Ricgraph data to 
the outside world. All data will only be accessible in the virtual machine.

* Follow the steps in [Create a Python virtual environment and install Ricgraph in 
  it](ricgraph_as_server.md#create-a-python-virtual-environment-and-install-ricgraph-in-it).
* Login as user *root*.
* Install the *Ricgraph Explorer* service unit file:
  copy
  [ricgraph_server_config/ricgraph_explorer.service](../ricgraph_server_config/ricgraph_explorer.service)
  to /etc/systemd/system, type:
  ```
  cp /opt/ricgraph_venv/ricgraph_server_config/ricgraph_explorer.service /etc/systemd/system
  ```
  Make it run by typing:
  ``` 
  systemctl enable ricgraph_explorer.service
  systemctl start ricgraph_explorer.service
  ```
  Check the log for any errors, use one of:
  ```
  systemctl -l status ricgraph_explorer.service
  journalctl -u ricgraph_explorer.service
  ```
* Exit from user *root*.
* Now you can use Ricgraph Explorer by typing
  [http://localhost:3030](http://localhost:3030) in your web browser (i.e., the web browser of
  the virtual machine).
  

### Use Apache and WSGI to make Ricgraph Explorer accessible from outside your virtual machine
[Ricgraph Explorer](ricgraph_explorer.md) 
is written in Flask, a framework for Python to build web interfaces.
Flask contains a development web server, and if you start Ricgraph Explorer by typing
*ricgraph_explorer.py*, it will be started using that development web server. As this development
web server is sufficient for development and demoing, it is certainly *not* sufficient
for exposing Ricgraph data to the outside world (that is, to users outside your own virtual machine).

For this, you will need a web server and a WSGI environment. This section describes how
to do that with Apache and WSGI. 
However, the example configuration file for Apache exposes Ricgraph Explorer
to the outside world on a http (unencrypted) connection, without any form of authentication.
Certainly, this is not the way to do it. At least you should expose Ricgraph Explorer
using a https (encrypted) connection, possibly with additional authentication.

Therefore, the configuration file provided is an example for further development.
There is no example code for a https connection, nor for authentication, nor for 
automatically obtaining and renewing SSL certificates, because these
are specific to a certain situation (such as your external IP address, hostname,
web server, domain name, SSL certificate provider, authentication source, etc.). 
So only expose Ricgraph Explorer and the data in Ricgraph
to the outside world if you have considered these subjects, and have made an informed
decision what is best for your situation.

To prevent accidental exposure of Ricgraph Explorer and the data in Ricgraph
to the outside world, you will have to modify the Apache configuration file. You
need to make a small modification to make it work. How to do this is described in the
comments at the start of the configuration file.

*Using Apache and WSGI will expose Ricgraph Explorer and Ricgraph data to the outside world.*

* Follow the steps in [Create a Python virtual environment and install Ricgraph in
  it](ricgraph_as_server.md#create-a-python-virtual-environment-and-install-ricgraph-in-it).
* Login as user *root*.
* Make sure Apache has been installed.
* Install and enable Apache's WSGI module:
  * OpenSUSE: 
    ```
    rpm -i apache2-mod_wsgi-python3
    a2enmod mod_wsgi-python3
    ```
  * Debian/Ubuntu:
    ```
    apt install libapache2-mod-wsgi-py3 
    a2enmod libapache2-mod-wsgi-py3 
    ```
* Install the Apache *Ricgraph Explorer* configuration file:
  copy
  [ricgraph_server_config/ricgraph_explorer.conf-apache](../ricgraph_server_config/ricgraph_explorer.conf-apache)
  to /etc/apache2/vhosts.d, type:
  ```
  cp /opt/ricgraph_venv/ricgraph_server_config/ricgraph_explorer.conf-apache /etc/apache2/vhosts.d/ricgraph_explorer.conf
  chmod 600 /etc/apache2/vhosts.d/ricgraph_explorer.conf
  ```
  Change *ricgraph_explorer.conf* in such a way it fits your situation.
  Make the modification to *ricgraph_explorer.conf*
  as described in the comments at the start of *ricgraph_explorer.conf*.
  Test the result.
  
  Make it run by typing:
  ``` 
  systemctl enable apache2.service
  systemctl start apache2.service
  ```
  Check the log for any errors, use one of:
  ```
  systemctl -l status apache2.service
  journalctl -u apache2.service
  ```
* Exit from user *root*.
* Now you can use Ricgraph Explorer from inside your virtual machine by typing 
  [http://localhost](http://localhost) in your web browser in the virtual machine, or 
  from outside your virtual machine by going to
  [http://[your IP address]](http://[your_IP_address) or
  [http://[your hostname]](http://[your_hostname). 


### Restore a Neo4j Desktop database dump of Ricgraph in Neo4j Community Edition
To read how this can be done, read
[Restore a Neo4j Desktop database dump of Ricgraph in Neo4j Community 
Edition](ricgraph_install_configure.md#restore-a-neo4j-desktop-database-dump-of-ricgraph-in-neo4j-community-edition).


### How to install Ricgraph and Ricgraph Explorer on SURF Research Cloud
[SURF Research Cloud](https://www.surf.nl/en/services/surf-research-cloud)
is a portal where you can easily build a virtual research environment. 
You can use preconfigured workspaces, or you can add them yourself.
A _virtual research environment_ or _workspace_ is a 
virtual machine that you can use to install Ricgraph.
Please follow these steps if you would like
to install Ricgraph and Ricgraph Explorer on SURF Research Cloud.

Preliminaries:
* Make sure you have access to SURF Research Cloud and that you have a wallet
  available. A _wallet_ is a budget.
  A wallet has _credits_, and these credits are used to pay for the
  SURF computing resources. 
  The more resources you use, the more you have to pay. For _resources_, think
  of disk space, the number of CPUs, the amount of memory, and the time the
  virtual machine is running.
* If you do not have access to SURF Research Cloud or you do not have a wallet,
  please contact the SURF Research Cloud contact person at your organization.
  These persons may be at the Research Data Management Support desk, 
  service desk, or help desk of your organization, or they might be persons like
  research engineers, data stewards, data managers, or data consultants.

Then, follow the following steps, and also watch the video below:
* Go to the [SURF Research Cloud portal](https://portal.live.surfresearchcloud.nl)
  and log in.
* Allocate storage:
  * Click on "Create new storage".
  * Select the collaborative organization that you want to use for running
    Ricgraph.
  * Select your wallet.
  * Select the cloud provider. 
    In the video we use "SURF HPC Cloud volume".
  * Allocate storage, make sure you allocate enough volume.
    In the video we use "100GB".
    The larger, the more credits it will cost.
  * Enter a name and a description.
  * After a few moments your storage will be created and available.
* Create a workspace (that is, a virtual machine to run Ricgraph in):
  * Click on "Create new workspace".
  * Select the collaborative organization that you want to use for running
    Ricgraph (as above).
  * Select your wallet (as above).
  * Now select a "catalogue item", that is, a pre-installed virtual machine. 
    Choose "Ubuntu Desktop 2004".
  * Select a configuration.
    In the video we use "1 Core - 8 GB RAM".
    The larger, the more credits it will cost.
  * Select storage, choose the one you created above.
  * Rename your workspace.
  * After a few moments your workspace will be created and available.
  * Start up your workspace.
* Done.

The next steps are to install Ricgraph. Start reading from 
[Install and start Neo4j Community Edition](#install-and-start-neo4j-community-edition)
or [Install and start Memgraph](#install-and-start-memgraph)
above.

For more explanation, please watch the 
[video how to install Ricgraph and Ricgraph Explorer on SURF Research Cloud
(2m14s) (click to download)](videos/ricgraph_howto_install_on_SURFResearchCloud.mp4).

https://github.com/UtrechtUniversity/ricgraph/assets/121875841/c7196e89-3a2f-4a30-b7ae-d41a4c2fce5b


### How to solve an AttributeError: 'Neo4jDriver' object has no attribute 'execute_query'
If, at some point while running Ricgraph scripts or Ricgraph Explorer in a
virtual environment, you get an error message like:
```
Traceback (most recent call last):
  File "ricgraph_explorer.py", line 2930, in <module>
    initialize_ricgraph_explorer()
  File "ricgraph_explorer.py", line 2867, in initialize_ricgraph_explorer
    name_all = rcg.read_all_values_of_property('name')
  File "/opt/ricgraph_venv/ricgraph/ricgraph.py", line 1140, in read_all_values_of_property
    result = _graph.execute_query(cypher_query,
AttributeError: 'Neo4jDriver' object has no attribute 'execute_query'
```
then this means that your version of the Python module *neo4j* is too old.
Note that this is related to the Python module *neo4j*, not to the graph database backend
Neo4j Desktop or Neo4j Community Edition.
You need at least version 5.8 of the Python module *neo4j*.
With an "old" version of Python (3.6 and earlier), an old version
of module *neo4j* will be used. The only way to solve this is using a new version of
Python while creating the Python virtual environment. You can do this by using the
following command:
* Create a Python virtual environment:
  in */opt*, type:
  ```
  python3.11 -m venv ricgraph_venv
  ```
in section
[Create a Python virtual environment and install Ricgraph in
it](#create-a-python-virtual-environment-and-install-ricgraph-in-it) above. For *python3.11* you can take any Python version that is installed
on your computer.


### Return to main README.md file
[Return to main README.md file](../README.md).

