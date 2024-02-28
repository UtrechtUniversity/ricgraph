## Ricgraph as a server on Linux
This page describes how to install Ricgraph in a multi-user environment on Linux.
If you would like to use Ricgraph in such an environment, you will
need to install Ricgraph differently than described in 
[Install and configure Ricgraph](ricgraph_install_configure.md).
*Multi-user environment* means that you install Ricgraph on a (virtual) machine, 
and that various persons can log on to that machine, each with his own user id
and password, and that each person will be able to use Ricgraph by using a
web link in their web browser.

The reason that a multi-user environment for Ricgraph is different from installing and using
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
 
  Download the package and install it with your favorite package manager:
  * OpenSUSE: use either ``rpm -i <packagename>`` (first install)
    or ``rpm -U <packagename>`` (update).
  * Debian/Ubuntu: use ``apt install <packagename>`` 
 
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
  * Click "Download".
  * Install it using your favorite package manager (see above).
  * Go back to installing Neo4j Community Edition. 
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
  * Neo4j will ask you to change your password,
    for the new password, enter the password you have specified in
    the [Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file)
    (this saves you from entering a new password in that file).
 
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
* Go to directory */opt*: ``cd /opt``
* Create a Python virtual environment:
  in */opt*, type ``python3 -m venv ricgraph_venv``
* Change the owner and group to your own user *alice* and group *users*:
  in */opt*, type
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
  go to */opt/ricgraph_venv*, type ``tar xf /opt/ricgraph-X.YY.tar.gz`` (X.YY 
  is the version number you downloaded). You will get a directory 
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
  in */opt/ricgraph_venv*, type 
  ``source bin/activate``
* Install the Python requirements for Ricgraph:
  in */opt/ricgraph_venv*, type 
  ``pip install -r requirements.txt``
* Create a Ricgraph initialization file, 
  read [Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file).
* In *ricgraph.ini*, find the section
  "Choose either the parameters for Neo4j Desktop or Neo4j Community Edition".
  Make sure you disable the parameters for Neo4j Desktop (by commenting them)
  and enable the parameter for Neo4j Community Edition.
* Deactivate the Python virtual environment: 
  type ``deactivate``
* Login as user *root*.
* Change the owner and group to ricgraph of directory ricgraph:
  in */opt*, type 
  ```
  chown -R ricgraph:ricgraph /opt/ricgraph_venv
  ```
* Exit from user *root*.

### Run Ricgraph scripts from the command line
After following the steps in [Create a Python virtual environment and install Ricgraph in
it](ricgraph_as_server.md#create-a-python-virtual-environment-and-install-ricgraph-in-it),
it is possible to run Ricgraph from the command line or as a cron job.
To be able to run these scripts you need to be
user *ricgraph* and group *ricgraph*.
You can do this by using the command
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

Using a service unit file to run Ricgraph Explorer 
is very useful if you would like to set up a virtual machine that you want to use as
a demo server. After the steps in this section, both Neo4j Community Edition
and Ricgraph Explorer are run
automatically at the start of the virtual machine, so you can immediately start giving the demo.

For comparison, if you had installed Neo4j and Ricgraph for a single user, as
described in 
[the documentation describing the installation and configuration
of Ricgraph for a single user](ricgraph_install_configure.md), 
after the start of the virtual machine, you would need to start Neo4j, the virtual environment,
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
  [http://localhost:3030](http://localhost:3030) in your web browser.


### Use Apache and WSGI to make Ricgraph Explorer accessible from outside your virtual machine

Ricgraph Explorer is written in Flask, a framework for Python to build web interfaces.
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

Using Apache and WSGI will expose Ricgraph Explorer and Ricgraph data to the outside world.

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
  * Debian/Ubuntu: *to be done*.
* Install the Apache *Ricgraph Explorer* configuration file:
  copy
  [ricgraph_server_config/ricgraph_explorer.conf-apache](../ricgraph_server_config/ricgraph_explorer.conf-apache)
  to /etc/apache2/vhosts.d, type:
  ```
  cp /opt/ricgraph_venv/ricgraph_server_config/ricgraph_explorer.conf-apache /etc/apache2/vhosts.d/ricgraph_explorer.conf
  chmod 600 /etc/apache2/vhosts.d/ricgraph_explorer.conf
  ```
  Change *ricgraph_explorer.conf* so it fits your situation.
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

### Return to main README.md file

[Return to main README.md file](../README.md).

