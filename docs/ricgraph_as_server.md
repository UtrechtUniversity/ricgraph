# Ricgraph as a server on Linux
This page describes how to install and run Ricgraph in a multi-user environment on Linux.
*Multi-user environment* means that you install Ricgraph on a Linux (virtual) machine, 
and that various persons can log on to that machine, each with his own user id
and password, and that each person will be able to use Ricgraph by using a
web link in their web browser.

The reason that a Linux multi-user environment for Ricgraph is different from installing and using
Ricgraph on your own user id, is that you will need to run the graph database backend and
[Ricgraph Explorer](ricgraph_explorer.md) 
as a system user instead of running it using your own user id.
If you run Ricgraph with your own user id, you will be the only user able to use it.
In case other persons on that same machine would like to use Ricgraph, they have
to install it for themselves. 
By installing Ricgraph as a server, as described on this page,
Ricgraph will be started automatically when your machine boots, and
it can be used by any user on that machine.

Other Ricgraph install options are:
* [Install and configure
  Ricgraph for a single user](ricgraph_install_configure.md).
* [Install and use
  Ricgraph in a container](ricgraph_containerized.md): 
  relatively quick with limited possibilities.

To install and run Ricgraph in a multi-user environment, you need to do most of
the following steps:
* [Fast and recommended way to install Ricgraph as a server](#fast-and-recommended-way-to-install-ricgraph-as-a-server-)
* [Create a ricgraph user and group](#create-a-ricgraph-user-and-group)
* [Create a Python virtual environment and install Ricgraph in it](#create-a-python-virtual-environment-and-install-ricgraph-in-it)
* [Run Ricgraph scripts from the command line or as a cronjob](#run-ricgraph-scripts-from-the-command-line-or-as-a-cronjob)
* [Use a service unit file to run Ricgraph Explorer and the Ricgraph REST API](#use-a-service-unit-file-to-run-ricgraph-explorer-and-the-ricgraph-rest-api)
* [Use Apache, WSGI, and ASGI to make Ricgraph Explorer and the Ricgraph REST API accessible from outside your virtual machine](#use-apache-wsgi-and-asgi-to-make-ricgraph-explorer-and-the-ricgraph-rest-api-accessible-from-outside-your-virtual-machine)
* [Use Nginx, WSGI, and ASGI to make Ricgraph Explorer and the Ricgraph REST API accessible from outside your virtual machine](#use-nginx-wsgi-and-asgi-to-make-ricgraph-explorer-and-the-ricgraph-rest-api-accessible-from-outside-your-virtual-machine)
* [Introduction Nginx webserver](#introduction-nginx-webserver)
* [How to install Ricgraph and Ricgraph Explorer on SURF Research Cloud](#how-to-install-ricgraph-and-ricgraph-explorer-on-surf-research-cloud)
 

[Return to main README.md file](../README.md).


## Fast and recommended way to install Ricgraph as a server 
To follow this procedure, you need to be able to change to user *root*.
1. [Check the requirements](ricgraph_install_configure.md#requirements-for-ricgraph).
1. Login as user *root*.
   ```
   sudo bash
   ```
1. Get the most recent Ricgraph Makefile. Type:
   ```
   cd
   wget https://raw.githubusercontent.com/UtrechtUniversity/ricgraph/main/Makefile
   ```
   Read more at [Ricgraph Makefile](ricgraph_install_configure.md#ricgraph-makefile).
1. Install Neo4j Community Edition. Type:
   ```
   make install_enable_neo4j_community
   ```
   Read more at [Install and start Neo4j Community Edition graph database
   backend](ricgraph_backend_neo4j.md#install-and-start-neo4j-community-edition).
1. Download and install Ricgraph in system directory */opt*.
   Read more at the sections below. Type:
   ```
   make install_ricgraph_server
   ```
1. Optional: use a service unit file to run Ricgraph Explorer and the Ricgraph REST API. Type:
   ```
   make install_enable_ricgraphexplorer_restapi
   ```
   Read more at [Use a service unit file to run Ricgraph Explorer and the Ricgraph 
   REST API](#use-a-service-unit-file-to-run-ricgraph-explorer-and-the-ricgraph-rest-api).
1. Optional and possibly dangerous: use Apache or Nginx webserver, WSGI, and ASGI to make 
   Ricgraph Explorer and the Ricgraph 
   REST API accessible from outside your virtual machine.
   Read more at
   [Use Apache...](#use-apache-wsgi-and-asgi-to-make-ricgraph-explorer-and-the-ricgraph-rest-api-accessible-from-outside-your-virtual-machine).
   or at
   [Use Nginx...](#use-nginx-wsgi-and-asgi-to-make-ricgraph-explorer-and-the-ricgraph-rest-api-accessible-from-outside-your-virtual-machine).
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
1. Exit from user *root*.
1. If everything succeeded, you can skip the remainder of this page.
   If not, the remainder of this page may help in finding solutions.


## Create a ricgraph user and group
If you use the [Ricgraph Makefile](ricgraph_install_configure.md#ricgraph-makefile),
you do not need to do this. Otherwise, follow these steps:

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
  
  
## Create a Python virtual environment and install Ricgraph in it
To do this, you can either use the [Ricgraph Makefile](ricgraph_install_configure.md#ricgraph-makefile) and execute
command `make full_server_install`, or follow the steps below.

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
* The path */opt/ricgraph_venv* is hardwired in the configuration files
  [ricgraph_server_config/ricgraph_explorer_gunicorn.service
  ](../ricgraph_server_config/ricgraph_explorer_gunicorn.service)
  and
  [ricgraph_server_config/ricgraph_explorer.conf-apache](../ricgraph_server_config/ricgraph_explorer.conf-apache).
  This is done for security reasons. If you change the path, also change it
  in these files.
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
  If you get an error message 
  ```
  ERROR: Could not find a version that satisfies the requirement neo4j>=5.8
  ```
  then your Python version is too old. Please read
  [How to solve an AttributeError: Neo4jDriver object has no attribute
  executequery](ricgraph_backend_neo4j.md#how-to-solve-an-attributeerror-neo4jdriver-object-has-no-attribute-executequery).
* Create a Ricgraph initialization file, 
  read [Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file).
  This is also the
  place where you specify which graph database backend you use.
  You can find these settings in section *GraphDB*.
  * For Neo4j, enter the new password for Neo4j from section
    [Install and start Neo4j Community Edition](ricgraph_backend_neo4j.md#install-and-start-neo4j-community-edition)
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


## Run Ricgraph scripts from the command line or as a cronjob

### In case you have installed Ricgraph as a server

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
  cd /opt/ricgraph_venv/harvest; ../bin/python harvest_rsd_to_ricgraph.py
  ```
* harvest all your favorite sources:
  ```
  cd /opt/ricgraph_venv/harvest; ../bin/python batch_harvest_demo.py
  ```
* run Ricgraph Explorer:
  ```
  cd /opt/ricgraph_venv/ricgraph_explorer; ../bin/python ricgraph_explorer.py
  ```

### In case you have installed Ricgraph for a single user
After following the steps in [Create a Python virtual environment and install Ricgraph in
it](ricgraph_as_server.md#create-a-python-virtual-environment-and-install-ricgraph-in-it),
it is possible to run Ricgraph from the command line. You do not need to be
user *ricgraph* and group *ricgraph*.
The following assumes your Python virtual environment is in your Linux home directory *$HOME*.

Examples of commands you can use are:
* harvest from the Research Software Directory:
  ```
  cd $HOME/ricgraph_venv/harvest; ../bin/python harvest_rsd_to_ricgraph.py
  ```
* harvest all your favorite sources:
  ```
  cd $HOME/ricgraph_venv/harvest; ../bin/python batch_harvest_demo.py
  ```
* run Ricgraph Explorer:
  ```
  cd $HOME/ricgraph_venv/ricgraph_explorer; ../bin/python ricgraph_explorer.py
  ```

### Using the Makefile
The [Ricgraph Makefile](ricgraph_install_configure.md#ricgraph-makefile) can also be used to execute
a Python batch file. Such a batch file can be used to harvest the sources specific to your organization.
This batch file is preconfigured in the variable
`harvest_script` at the top of the Makefile. It can be modified to refer to your favorite Python script.
If you have done this, and then execute
command `make run_batchscript`, that script will be executed and its output will appear both
on your screen and in a file. The Makefile will tell you the name of this log file.

The directory of the batch file depends on the user that is running the command
`make run_batchscript` (either a regular user or user *root*). 
The Makefile will tell which script it will use.

The Makefile also provides a command `make run_anyscript`, to run any Ricgraph script.
You will need to add the name of the script to run using the Makefile command line
parameter *ricgraph_anyscript*, e.g.
```
make run_anyscript ricgraph_anyscript=harvest/batch_harvest_demo.py
```

## Use a service unit file to run Ricgraph Explorer and the Ricgraph REST API
To do this, you can either use the [Ricgraph Makefile](ricgraph_install_configure.md#ricgraph-makefile) and execute
command `make install_enable_ricgraphexplorer_restapi`, or follow the steps below.

Using a service unit file to run
[Ricgraph Explorer](ricgraph_explorer.md) 
is very useful if you would like to set up a virtual machine that you want to use as
a demo server, or if you would like to use the [Ricgraph REST API](ricgraph_restapi.md).
After the steps in this section, 
Ricgraph Explorer and the Ricgraph REST API are run
automatically at the start of the virtual machine, so you can immediately start giving the demo.

For comparison, if you had installed the graph database backend
and Ricgraph for a single user, as
described in 
[the documentation describing the installation and configuration
of Ricgraph for a single user](ricgraph_install_configure.md), 
after the start of the virtual machine, you would need to start the graph database
backend, the virtual environment,
and *ricgraph_explorer.py* by hand.

Using a service unit file will *not* expose Ricgraph Explorer,
the Ricgraph REST API, and Ricgraph data to 
the outside world. All data will only be accessible in the virtual machine.

* Follow the steps in [Create a Python virtual environment and install Ricgraph in 
  it](ricgraph_as_server.md#create-a-python-virtual-environment-and-install-ricgraph-in-it).
* Login as user *root*.
* Install the *Ricgraph Explorer* service unit file:
  copy
  [ricgraph_server_config/ricgraph_explorer_gunicorn.service
  ](../ricgraph_server_config/ricgraph_explorer_gunicorn.service)
  to /etc/systemd/system, type:
  ```
  cp /opt/ricgraph_venv/ricgraph_server_config/ricgraph_explorer_gunicorn.service /etc/systemd/system
  ```
  Make it run by typing:
  ``` 
  systemctl enable ricgraph_explorer_gunicorn.service
  systemctl start ricgraph_explorer_gunicorn.service
  ```
  Check the log for any errors, use one of:
  ```
  systemctl -l status ricgraph_explorer_gunicorn.service
  journalctl -u ricgraph_explorer_gunicorn.service
  ```
* Exit from user *root*.
* Now you can use Ricgraph Explorer by typing
  [http://localhost:3030](http://localhost:3030) in your web browser (i.e., the web browser of
  the virtual machine).
  You can use the Ricgraph REST API by using the path
  *http://localhost:3030/api* followed by a REST API endpoint.


## Use Apache, WSGI, and ASGI to make Ricgraph Explorer and the Ricgraph REST API accessible from outside your virtual machine
To do this, you can either use the [Ricgraph Makefile](ricgraph_install_configure.md#ricgraph-makefile) and execute
command `make prepare_webserver_apache`, or follow the steps below.

### Introduction Apache webserver
[Ricgraph Explorer](ricgraph_explorer.md) 
is written in Flask, a framework for Python to build web interfaces.
Flask contains a development web server, and if you start Ricgraph Explorer by typing
*ricgraph_explorer.py*, it will be started using that development web server. As this development
web server is sufficient for development and demoing, it is certainly *not* sufficient
for exposing Ricgraph data to the outside world (that is, to users outside your own virtual machine).
The same holds for the [Ricgraph REST API](ricgraph_restapi.md).

For this, you will need a web server and a WSGI environment. 
For the REST API, you will need an ASGI environment.
This section describes how
to do that with Apache and *gunicorn*. 
Note that the example configuration file for Apache exposes Ricgraph Explorer
to the outside world on a http (unencrypted) connection, without any form of authentication.
Certainly, this is not the way to do it. At least you should expose Ricgraph Explorer
and the REST API
using a https (encrypted) connection, possibly with additional authentication.

Therefore, the configuration file provided is an example for further development.
There is no example code for a https connection, nor for authentication, nor for 
automatically obtaining and renewing SSL certificates, because these
are specific to a certain situation (such as your external IP address, hostname,
web server, domain name, SSL certificate provider, authentication source, etc.). 
So only expose Ricgraph Explorer, the Ricgraph REST API, and the data in Ricgraph
to the outside world if you have considered these subjects, and have made an informed
decision what is best for your situation.

To prevent accidental exposure of Ricgraph Explorer, the REST API, and the data in Ricgraph
to the outside world, you will have to modify the Apache configuration file. You
need to make a small modification to make it work. How to do this is described in the
comments at the start of the configuration file.

Note that it is also possible to use [Nginx as a
webserver](#use-nginx-wsgi-and-asgi-to-make-ricgraph-explorer-and-the-ricgraph-rest-api-accessible-from-outside-your-virtual-machine).
If you are using SURF Research Cloud, you will need to use Nginx.

### Installation Apache

Note that different Linux editions use different paths. In the steps below, path names from
OpenSUSE Leap are used. Please adapt them to you own Linux edition:
* OpenSUSE Leap: `apache2` and /etc/apache2/vhosts.d
* Ubuntu: `apache2` and /etc/apache/sites-available
* Fedora: `httpd` and /etc/httpd/conf.d

*Using Apache, WSGI, and ASGI will expose Ricgraph Explorer, the Ricgraph REST API,
and Ricgraph data to the outside world.*

* Follow the steps in [Create a Python virtual environment and install Ricgraph in
  it](ricgraph_as_server.md#create-a-python-virtual-environment-and-install-ricgraph-in-it).
* Login as user *root*.
* Make sure Apache has been installed.
* *Gunicorn* has already been installed when you installed the Python requirements.
* Enable two Apache modules (they have already been installed when you installed Apache):
  ```
  a2enmod mod_proxy
  a2enmod mod_proxy_http
  ```
* Install the Apache *Ricgraph Explorer* configuration file:
  copy
  [ricgraph_server_config/ricgraph_explorer.conf-apache](../ricgraph_server_config/ricgraph_explorer.conf-apache)
  to /etc/apache2/vhosts.d, type:
  ```
  cp /opt/ricgraph_venv/ricgraph_server_config/ricgraph_explorer.conf-apache /etc/apache2/vhosts.d
  chmod 600 /etc/apache2/vhosts.d/ricgraph_explorer.conf-apache
  ```

### Post-install steps Apache

* Login as user *root*.
* Move the Apache *Ricgraph Explorer* configuration file to its final location:
  ```
  mv /etc/apache2/vhosts.d/ricgraph_explorer.conf-apache /etc/apache2/vhosts.d/ricgraph_explorer.conf
  ```
  However, for Ubuntu do:
  ```
  mv /etc/apache2/sites-available/ricgraph_explorer.conf-apache /etc/apache2/sites-available/ricgraph_explorer.conf
  ln -s /etc/apache2/sites-enabled/ricgraph_explorer.conf /etc/apache2/sites-available/ricgraph_explorer.conf
  ```
  Change *ricgraph_explorer.conf* in such a way it fits your situation.
  Make the modification to *ricgraph_explorer.conf*
  as described in the comments at the start of *ricgraph_explorer.conf*.
  Test the result.
* Make it run by typing:
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
* You can use the Ricgraph REST API from inside your virtual machine by
  using the path *http://localhost:3030/api* followed by a REST API endpoint, or
  from outside your virtual machine by
  using the path *http://[your IP address/api* or
  *http://[your hostname]/api*,
  both followed by a REST API endpoint.


## Use Nginx, WSGI, and ASGI to make Ricgraph Explorer and the Ricgraph REST API accessible from outside your virtual machine
To do this, you can either use the [Ricgraph Makefile](ricgraph_install_configure.md#ricgraph-makefile) and execute
command `make prepare_webserver_nginx`, or follow the steps below.

### Introduction Nginx webserver
Please read the introduction of section
[Use Apache, WSGI, and ASGI to make Ricgraph Explorer and the Ricgraph
  REST API accessible from outside your virtual
  machine](#use-apache-wsgi-and-asgi-to-make-ricgraph-explorer-and-the-ricgraph-rest-api-accessible-from-outside-your-virtual-machine).
The same explanation and words of caution as for using Apache as a webserver hold for 
Nginx as a webserver.

To prevent accidental exposure of Ricgraph Explorer, the REST API, and the data in Ricgraph
to the outside world, you will have to modify the Nginx configuration file. You
need to make a small modification to make it work. How to do this is described in the
comments at the start of the configuration file.

Note that it is also possible to use [Apache as a
webserver](#use-apache-wsgi-and-asgi-to-make-ricgraph-explorer-and-the-ricgraph-rest-api-accessible-from-outside-your-virtual-machine).

### Installation Nginx

Note that different Linux editions use different paths. In the steps below, path names from
OpenSUSE Leap are used. Please adapt them to you own Linux edition:
* OpenSUSE Leap: /etc/nginx/vhosts.d
* Ubuntu: /etc/nginx/sites-available
* Fedora: /etc/nginx/conf.d
 
*Using Nginx, WSGI, and ASGI will expose Ricgraph Explorer, the Ricgraph REST API,
and Ricgraph data to the outside world.*

* Follow the steps in [Create a Python virtual environment and install Ricgraph in
  it](ricgraph_as_server.md#create-a-python-virtual-environment-and-install-ricgraph-in-it).
* Login as user *root*.
* Make sure Nginx has been installed.
* *Gunicorn* has already been installed when you installed the Python requirements.
* Install the Nginx *Ricgraph Explorer* configuration file:
  copy
  [ricgraph_server_config/ricgraph_explorer.conf-nginx](../ricgraph_server_config/ricgraph_explorer.conf-nginx)
  to /etc/nginx/vhosts.d, type:
  ```
  cp /opt/ricgraph_venv/ricgraph_server_config/ricgraph_explorer.conf-nginx /etc/nginx/vhosts.d
  chmod 600 /etc/nginx/vhosts.d/ricgraph_explorer.conf-nginx
  ```

### Post-install steps Nginx
* Login as user *root*.
* Move the Nginx *Ricgraph Explorer* configuration file to its final location:
  ```
  mv /etc/nginx/vhosts.d/ricgraph_explorer.conf-nginx /etc/nginx/vhosts.d/ricgraph_explorer.conf
  ```
  However, for Ubuntu do:
  ```
  mv /etc/nginx/sites-available/ricgraph_explorer.conf-nginx /etc/nginx/sites-available/ricgraph_explorer.conf
  ln -s /etc/nginx/sites-enabled/ricgraph_explorer.conf /etc/nginx/sites-available/ricgraph_explorer.conf
  ```
  Change *ricgraph_explorer.conf* in such a way it fits your situation.
  Make the modification to *ricgraph_explorer.conf*
  as described in the comments at the start of *ricgraph_explorer.conf*.
  Test the result.
* Make it run by typing:
  ``` 
  systemctl enable nginx.service
  systemctl start nginx.service
  ```
  Check the log for any errors, use one of:
  ```
  systemctl -l status nginx.service
  journalctl -u nginx.service
  ```
* Exit from user *root*.
* Now you can use Ricgraph Explorer from inside your virtual machine by typing
  [http://localhost](http://localhost) in your web browser in the virtual machine, or
  from outside your virtual machine by going to
  [http://[your IP address]](http://[your_IP_address) or
  [http://[your hostname]](http://[your_hostname).
* You can use the Ricgraph REST API from inside your virtual machine by
  using the path *http://localhost:3030/api* followed by a REST API endpoint, or
  from outside your virtual machine by
  using the path *http://[your IP address/api* or
  *http://[your hostname]/api*,
  both followed by a REST API endpoint.


## How to install Ricgraph and Ricgraph Explorer on SURF Research Cloud
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
* Allocate storage (optional). This step is only required if you expect 
  to install a lot of programs on
 the virtual research environment and expect to create or use a lot of
 data. In the case of Ricgraph: > 100M nodes and edges.
  * Click on "Create new storage".
  * Select the collaborative organization that you want to use for running
    Ricgraph. If you have only one, it will be preselected.
  * Select your wallet. If you have only one, it will be preselected.
  * Select the cloud provider. We use "SURF HPC Cloud volume".
  * Choose the size of your storage. In the video below we use "100GB".
    The larger, the more credits it will cost.
  * Enter a name and a description.
  * After a few moments your storage will be created and available.
* Create a workspace (that is, a virtual machine to run Ricgraph in):
  * Click on "Create new workspace".
  * Select the collaborative organization that you want to use for running
    Ricgraph (as above). If you have only one, it will be preselected.
  * Select your wallet (as above). If you have only one, it will be preselected.
  * Now select a "catalogue item", that is, a pre-installed virtual machine. 
    Choose "Ubuntu Desktop".
  * Select the cloud provider. We use "SURF HPC Cloud".
  * Select which version of Ubuntu you want to use. Choose "Ubuntu 22.04 Desktop".
  * Select a configuration.
    In the video below we use "1 Core - 8 GB RAM".
    The larger, the more credits it will cost.
  * By default, the workspace has ~95GB of storage on the system and home partition.
  * Optionally you can add more storage, above is explained how to allocate it. 
    If you have done this, select this additional storage.
  * Rename your workspace.
  * After some minutes your workspace will be created and available. It will
    be started up automatically.
* Done.

The next steps are to install Ricgraph. Start reading from 
[Install and start Neo4j Community Edition](ricgraph_backend_neo4j.md#install-and-start-neo4j-community-edition)
or [Install and start Memgraph](ricgraph_backend_memgraph.md#install-and-start-memgraph)
above.
Note that if you would like to use a webserver, you will need to use Nginx.


For more explanation, please watch the 
[video how to install Ricgraph and Ricgraph Explorer on SURF Research Cloud
(2m14s) (click to download)](videos/ricgraph_howto_install_on_SURFResearchCloud.mp4).
Note that in the video, we use an old version of Ubuntu. Please use
Ubuntu 22.04 as described above.

https://github.com/UtrechtUniversity/ricgraph/assets/121875841/c7196e89-3a2f-4a30-b7ae-d41a4c2fce5b
