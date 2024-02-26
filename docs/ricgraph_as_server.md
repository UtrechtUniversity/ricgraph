## Ricgraph as a server on Linux
This page describes how to install Ricgraph in a multi-user environment on Linux.
If you would like to use Ricgraph in such an environment, you will
need to install Ricgraph differently than described in 
[Install and configure Ricgraph](ricgraph_install_configure.md).
*Multi-user environment* means that you install Ricgraph on a (virtual) machine, 
and that various persons can logon to that machine, each with his own user id
and password, and that each person will be able to use Ricgraph by using a
web link in their web browser.

The reason that a multi-user environment for Ricgraph is different than installing and using
Ricgraph on your own user id, is that you will need to run Neo4j and
Ricgraph Explorer as a system user instead of running it using your own user id.
If you run Ricgraph with your own user id, you will be the only user able to use it.
In case other persons on that same machine would like to use Ricgraph, they have
to install it for themselves. 
By installing Ricgraph as a server, as described on this page,
Ricgraph will be started automatically when your machine boots, and
it can be used by any user on that machine.

[Go to the documentation describing the installation and configuration
of Ricgraph for a single user](ricgraph_install_configure.md).

[Return to main README.md file](../README.md).

### Installation instructions for a multi-user environment
* Please check the [Requirements for Ricgraph](ricgraph_install_configure.md#requirements).
* Login as user *root*.
 
### Install and start Neo4j Community Edition

* Install Neo4j Community Edition. 
  To do this, go to the 
  [Neo4j Deployment Center](https://neo4j.com/deployment-center). 
  Go to section "Graph Database Self-Managed", choose "Community".
  Choose the latest version of Neo4j. Then choose your favorite package
  format:
  * OpenSUSE: "Red Hat Linux Package (rpm)".
  * Debian/Ubuntu: "Debian/Ubuntu Package (deb)".
 
  Download the package and install it with your favorite package manager:
  * OpenSUSE: use either ``rpm -i <packagename>`` (first install)
    or ``rpm -U <packagename>`` (update).
  * Debian/Ubuntu: *to be done*.
 
  You might need to install other packages required to fulfill the dependencies
  of Neo4j Community Edition.

  If you get an error message about a failed dependency on *cypher-shell*, install
  *cypher-shell* separately as follows:
  * Go to the
    [Tools tab of the Neo4j Deployment Center](https://neo4j.com/deployment-center/#tools-tab). 
    Go to section "Cypher Shell", choose the version of Cypher Shell that matches
    the version of the Neo4j Community Edition you have downloaded above.
    Then choose the version that fits your Linux version:
    * OpenSUSE: "Linux cypher-shell_X.YY.0-Z.noarch.rpm".
    * Debian/Ubuntu: "Linux cypher-shell_X.YY.0_all.deb".
  * Click "Download"  
  * Install it using your favorite package manager (see above).
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
 
### Create a ricgraph user and group

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
  
### Create a Python virtual environment and install Ricgraph in it

* Go to directory */opt*: ``cd /opt``
* Create a Python virtual environment: 
  in */opt*, type ``python3 -m venv ricgraph_venv``
* While in */opt*, download the latest release of Ricgraph from the
  [Ricgraph downloads
  page](https://github.com/UtrechtUniversity/ricgraph/releases), get the
  ``tar.gz`` version.
* Install Ricgraph: 
  go to */opt/ricgraph_venv*, type ``tar xf /opt/ricgraph-X.YY.tar.gz`` (X.YY 
  is the version number you downloaded). You will get a directory 
  */opt/ricgraph_venv/ricgraph-X.YY*.
* Merge the Ricgraph you have extracted with *tar* with the virtual environment,
  and do some cleanup:
  in */opt/ricgraph_venv*, type: 
  ```
  mv ricgraph-X.YY/* /opt/ricgraph_venv
  rm -r /opt/ricgraph_venv/ricgraph-X.YY
  rm /opt/ricgraph-X.YY.tar.gz
  ```
* Activate the Python virtual environment: 
  in */opt/ricgraph_venv*, type 
  ``source bin/activate``
* Install the Python requirements for Ricgraph:
  in */opt/ricgraph_venv*, type 
  ``pip install -r requirements.txt``
* Create a Ricgraph initalization file, 
  read [Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file).
  Next, in this file, find the section
  "Choose either the parameters for Neo4j Desktop or Neo4j Community Edition".
  Make sure you disable the parameters for Neo4j Desktop (by commenting them)
  and enable the parameter for Neo4j Community Edition.
* Deactivate the Python virtual environment: 
  type ``deactivate``
* Change the owner and group to ricgraph of directory ricgraph:
  in */opt*, type 
  ```
  chown -R ricgraph:ricgraph /opt/ricgraph_venv
  ```
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
* Now you can use Ricgraph Explorer by typing
  [http://localhost:3030](http://localhost:3030) in your web browser.

### Execute Ricgraph scripts from the command line

After following the steps above, it is possible to run Ricgraph from the command line.
To be able to run these scripts you need to be
user *ricgraph* and group *ricgraph*.
You can become this by using the command
```
sudo su - ricgraph
``` 

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
    
### Configure Apache (optional)

* Install the Apache *Ricgraph Explorer* configuration file:
  copy
  [ricgraph_server_config/ricgraph_explorer.conf-apache](../ricgraph_server_config/ricgraph_explorer.conf-apache)
  to /etc/apache2/vhosts.d, type:
  ```
  cp /opt/ricgraph_venv/ricgraph_server_config/ricgraph_explorer.conf-apache /etc/apache2/vhosts.d/ricgraph_explorer.conf
  chmod 600 /etc/apache2/vhosts.d/ricgraph_explorer.conf
  ```
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
* Now you can use Ricgraph Explorer by typing
  [http://localhost](http://localhost) in your web browser.
* Note that this Apache VirtualHost config script only works on the (virtual) machine
  where Ricgraph has been installed. If you need to access it from outside that
  virtual machine, you have to modify the config script.

### Restore a Neo4j Desktop database dump of Ricgraph in Neo4j Community Edition

To read how this can be done, read
[Restore a Neo4j Desktop database dump of Ricgraph in Neo4j Community 
Edition](ricgraph_install_configure.md#restore-a-neo4j-desktop-database-dump-of-ricgraph-in-neo4j-community-edition).

### Return to main README.md file

[Return to main README.md file](../README.md).

