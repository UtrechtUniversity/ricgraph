# Ricgraph as a server on Linux
This page describes how to install and run Ricgraph in a multi-user environment on Linux.
*Multi-user environment* means that you install Ricgraph on a Linux (virtual) machine, 
and that various persons can log on to that machine, each with his own user id
and password. Each person will be able to use Ricgraph by using a
web link in their web browser.
For other Ricgraph install options start reading at
[Install and configure
Ricgraph for a single user](ricgraph_install_configure.md#install-and-configure-ricgraph).

The reason that a Linux multi-user environment for Ricgraph is different from installing and using
Ricgraph on your own user id, is that you will need to run the graph database backend and
[Ricgraph Explorer](ricgraph_explorer.md) 
as a system user instead of running it using your own user id.
In case you run Ricgraph with your own user id, you will be the only user able to use it.
In case other persons on that same machine would like to use Ricgraph, they have
to install it for themselves. 
By installing Ricgraph as a server, as described on this page,
Ricgraph will be started automatically when your machine boots, and
it can be used by any user on that machine.


To install and run Ricgraph in a multi-user environment, read
[Fast and recommended way to install Ricgraph as a 
server](#fast-and-recommended-way-to-install-ricgraph-as-a-server).

On this page, you can find:

* [Fast and recommended way to install Ricgraph as a server](#fast-and-recommended-way-to-install-ricgraph-as-a-server)
* [Run Ricgraph scripts from the command line or as a cronjob](#run-ricgraph-scripts-from-the-command-line-or-as-a-cronjob)
* [Use a service unit file to run Ricgraph Explorer and the Ricgraph REST API](#use-a-service-unit-file-to-run-ricgraph-explorer-and-the-ricgraph-rest-api)
* [Use Apache, WSGI, and ASGI to make Ricgraph Explorer and the Ricgraph REST API accessible from outside your virtual machine](#use-apache-wsgi-and-asgi-to-make-ricgraph-explorer-and-the-ricgraph-rest-api-accessible-from-outside-your-virtual-machine)
* [Use Nginx, WSGI, and ASGI to make Ricgraph Explorer and the Ricgraph REST API accessible from outside your virtual machine](#use-nginx-wsgi-and-asgi-to-make-ricgraph-explorer-and-the-ricgraph-rest-api-accessible-from-outside-your-virtual-machine)
* [Install Munin monitoring](#install-munin-monitoring)
* [Install AWStats web server log analysis](#install-awstats-web-server-log-analysis)
* [How to install Ricgraph and Ricgraph Explorer on SURF Research Cloud](#how-to-install-ricgraph-and-ricgraph-explorer-on-surf-research-cloud)
* [Steps to take to install Ricgraph as a server by hand](#steps-to-take-to-install-ricgraph-as-a-server-by-hand)

[Return to main README.md file](../README.md#ricgraph---research-in-context-graph).

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
   On success, the Makefile will print *installed successfully*.
1. Download and install Ricgraph in system directory */opt*.
   ```
   make install_ricgraph_server
   ```
   On success, the Makefile will print *installed successfully*.
1. Harvest two source systems in Ricgraph:
   ```
   cd /opt/ricgraph_venv
   make run_bash_script
   ```
   This will harvest two source systems,
   [the data repository Yoda](https://www.uu.nl/en/research/yoda) and
   [the Research Software Directory](https://research-software-directory.org).
   It will print a lot of output, and it will take a few minutes.
   When ready, it will print *Done*.

   To read more about harvesting data,
   see [Ricgraph harvest scripts](ricgraph_harvest_scripts.md).
   To read more about writing harvesting scripts,
   see [Ricgraph script writing](ricgraph_script_writing.md).
1. Start Ricgraph Explorer to browse the information harvested:
   ```
   cd /opt/ricgraph_venv
   make run_ricgraph_explorer
   ```
   The Makefile will tell you to go to
   your web browser, and go to 
   [http://127.0.0.1:3030](http://127.0.0.1:3030).
   Read more at [Ricgraph Explorer](ricgraph_explorer.md).
   For the Ricgraph REST API, read
   more on the [Ricgraph REST API page](ricgraph_restapi.md#ricgraph-rest-api).
1. Optional: use a service unit file to run Ricgraph Explorer and the Ricgraph REST API. Type:
   ```
   make install_enable_ricgraphexplorer_restapi
   ```
   On success, the Makefile will print *installed successfully*.
   Read more at [Use a service unit file to run Ricgraph Explorer and the Ricgraph
   REST API](#use-a-service-unit-file-to-run-ricgraph-explorer-and-the-ricgraph-rest-api).
1. Optional and possibly dangerous: use Apache or Nginx webserver, WSGI, and ASGI to make
   Ricgraph Explorer and the Ricgraph
   REST API accessible from outside your virtual machine.
   Read more at
   [Use Apache...](#use-apache-wsgi-and-asgi-to-make-ricgraph-explorer-and-the-ricgraph-rest-api-accessible-from-outside-your-virtual-machine).
   or at
   [Use Nginx...](#use-nginx-wsgi-and-asgi-to-make-ricgraph-explorer-and-the-ricgraph-rest-api-accessible-from-outside-your-virtual-machine).
   On success, the Makefile will print *installed successfully*.
1. Optional: install [Munin monitoring](https://munin-monitoring.org).
   Munin is a networked resource monitoring tool that can help analyze resource 
   trends and "what just happened to kill our performance?" problems. 
   You can only do this if you have installed Apache or Nginx.
   Read more at
   [Install Munin monitoring](#install-munin-monitoring).
1. Optional: install [AWStats](https://awstats.sourceforge.io).
   AWStats is a real-time logfile analyser, for e.g. web server log files.
   You can only do this if you have installed Apache or Nginx.
   Read more at
   [Install AWStats web server log analysis](#install-awstats-web-server-log-analysis).
1. Exit from user *root*.

If everything succeeded, you are done installing Ricgraph as a server.
If not, sections
[Steps to take to install Ricgraph as a server by hand](#steps-to-take-to-install-ricgraph-as-a-server-by-hand)
or [Install and start Neo4j Community Edition graph database
backend](ricgraph_backend_neo4j.md#install-and-start-neo4j-community-edition)
may help in finding solutions.


## Run Ricgraph scripts from the command line or as a cronjob

### Using the Makefile
The [Ricgraph Makefile](ricgraph_install_configure.md#ricgraph-makefile) can also be used to execute
a Python script or a bash script.
Such a script can be used to harvest the sources specific to your organization.
The Makefile provides a command `make run_python_script`, to run any Ricgraph Python script.
You will need to add the name of the script to run using the Makefile command line
parameter *python_script*, e.g.
```
make run_python_script python_script=[path]/[python script]
```

There is a similar command for running bash scripts:
```
make run_bash_script bash_script=[path]/[bash script]
```

Both `make` commands execute the script and the output will appear both
on your screen and in a file. The Makefile will tell you the name of this log file.

Examples of commands you can use are:

* harvest from the Research Software Directory:
  ```
  make run_python_script python_script=harvest/harvest_rsd_to_ricgraph.py
  ```
* harvest two sources without needing any keys or configuration:
  ```
  make run_bash_script
  ```
* run Ricgraph Explorer:
  ```
  make run_ricgraph_explorer
  ```

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
* harvest two sources without needing any keys or configuration:
  ```
  cd /opt/ricgraph_venv/harvest_multiple_sources; ./multiple_harvest_demo.sh
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
  cd $HOME/ricgraph_venv/harvest_multiple_sources; ./multiple_harvest_demo.sh
  ```
* run Ricgraph Explorer:
  ```
  cd $HOME/ricgraph_venv/ricgraph_explorer; ../bin/python ricgraph_explorer.py
  ```

## Use a service unit file to run Ricgraph Explorer and the Ricgraph REST API

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

To use a service unit file, 
you can either use the [Ricgraph Makefile](ricgraph_install_configure.md#ricgraph-makefile) and execute
command:
```
make install_enable_ricgraphexplorer_restapi
```
or follow the steps below.

Using a service unit file will *not* expose Ricgraph Explorer,
the Ricgraph REST API, and Ricgraph data to 
the outside world. All data will only be accessible in the virtual machine.

* Follow the steps in [Create a Python virtual environment and install Ricgraph in 
  it](ricgraph_as_server.md#create-a-python-virtual-environment-and-install-ricgraph-in-it).
* Login as user *root*.
* Install the *Ricgraph Explorer* service unit file:
  copy file
  *ricgraph_server_config/ricgraph_explorer_gunicorn.service*
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
  [http://localhost:3030/api](http://localhost:3030/api) followed by a REST API endpoint.


## Use Apache, WSGI, and ASGI to make Ricgraph Explorer and the Ricgraph REST API accessible from outside your virtual machine

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

To use Apache c.s., you can either use the 
[Ricgraph Makefile](ricgraph_install_configure.md#ricgraph-makefile) and execute
command:
```
make prepare_webserver_apache
```
or follow the steps below.

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
* Recommended: Make sure Certbot has been installed.
  Execute:
  ```
  [Your Linux package install command] certbot python3-certbot-apache
  ```
  For some Linux versions you will need to do:
  ```
  [Your Linux package install command] python3-certbot python3-certbot-apache
  ```
  Check if Certbot has been set up to renew SSL certificates automatically.
  Do this by making sure `certbot.timer` is enabled and started:
  ```
  systemctl status certbot.timer
  ```
* *Gunicorn* has already been installed when you installed the Python requirements.
* Enable two Apache modules (they have already been installed when you installed Apache):
  ```
  a2enmod mod_proxy
  a2enmod mod_proxy_http
  ```
* Install the Apache *Ricgraph Explorer* configuration file:
  copy file
  *ricgraph_server_config/ricgraph_explorer.conf-apache*
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
* Generate a SSL certificate for your host. In the Apache config file is explained how to do
  that. Then restart Apache.
  For some specific situations this is not necessary (e.g. if you are running
  Ricgraph on a local machine).
* Exit from user *root*.
* Now you can use Ricgraph Explorer from inside your virtual machine by typing 
  [http://localhost](http://localhost) in your web browser in the virtual machine, or 
  from outside your virtual machine by going to
  [http://[your IP address]](http://[your_IP_address) or
  [http://[your hostname]](http://[your_hostname).
* You can use the Ricgraph REST API from inside your virtual machine by
  using the path [http://localhost:3030/api](http://localhost:3030/api) followed by a REST API endpoint, or
  from outside your virtual machine by
  using the path [http://[your IP address/api]](http://[your IP address]/api) or
  [http://[your hostname]/api](http://[your hostname]/api),
  both followed by a REST API endpoint.


## Use Nginx, WSGI, and ASGI to make Ricgraph Explorer and the Ricgraph REST API accessible from outside your virtual machine

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

To use Nginx c.s., you can either use the
[Ricgraph Makefile](ricgraph_install_configure.md#ricgraph-makefile) and execute
command:
```
make prepare_webserver_nginx
```
or follow the steps below.

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
* Recommended: Make sure Certbot has been installed.
  Execute:
  ```
  [Your Linux package install command] certbot python3-certbot-nginx
  ```
  For some Linux versions you will need to do:
  ```
  [Your Linux package install command] python3-certbot python3-certbot-nginx
  ```
  Check if Certbot has been set up to renew SSL certificates automatically.
  Do this by making sure `certbot.timer` is enabled and started:
  ```
  systemctl status certbot.timer
  ```
* *Gunicorn* has already been installed when you installed the Python requirements.
* Install the Nginx *Ricgraph Explorer* configuration file:
  copy file
  *ricgraph_server_config/ricgraph_explorer.conf-nginx*
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
* Generate a SSL certificate for your host. In the Nginx config file is explained how to do
  that. Then restart Nginx.
  For some specific situations this is not necessary (e.g. if you are running
  Ricgraph on a local machine).
* Exit from user *root*.
* Now you can use Ricgraph Explorer from inside your virtual machine by typing
  [http://localhost](http://localhost) in your web browser in the virtual machine, or
  from outside your virtual machine by going to
  [http://[your IP address]](http://[your_IP_address) or
  [http://[your hostname]](http://[your_hostname).
* You can use the Ricgraph REST API from inside your virtual machine by
  using the path [http://localhost:3030/api](http://localhost:3030/api) followed by a REST API endpoint, or
  from outside your virtual machine by
  using the path 
  [http://[your IP address]/api](http://[your_IP_address/api) or
  [http://[your hostname]/api](http://[your_hostname/api),
  both followed by a REST API endpoint.


## Install Munin monitoring
[Munin monitoring](https://munin-monitoring.org)
is a networked resource monitoring tool that can help analyze resource
trends and "what just happened to kill our performance?" problems.
You can only do this if you have installed Apache or Nginx.

### Munin with Apache
Follow the steps at [Munin with Nginx](#munin-with-nginx). 
You will need to create your own Apache configuration file
(this has not been done yet).

### Munin with Nginx

* Login as user *root*.
* Execute:
   ```
   make install_munin_nginx
   ```
* Exit from user *root*.
* You can only access Munin on the server you have installed it
  on. Go to [http://localhost:8060](http://localhost:8060).
  Note that you will only be able to see any results after `munin-node` has
  executed at least once. This may take up to 5 minutes after your install.


## Install AWStats web server log analysis
[AWStats](https://awstats.sourceforge.io)
is a real-time logfile analyser, for e.g. web server log files.
You can only do this if you have installed Apache or Nginx.

### AWStats with Apache
Follow the steps at [AWStats with Nginx](#awstats-with-nginx).
You will need to create your own Apache configuration file
(this has not been done yet).
Also, you have to change the path to the web server log files directory.
Read the first few lines of file
*/etc/awstats/awstats.ricgraph.conf* (after installation) how to do that.

### AWStats with Nginx

* Login as user *root*.
* Execute:
   ```
   make install_awstats_nginx
   ```
* Exit from user *root*.

### Post-install steps AWStats with Nginx

* Login as user *root*.
* Add the following line at the end of /etc/crontab:
  ```
  5 * * * * root (date; /usr/lib/cgi-bin/awstats.pl -config=ricgraph -update; /usr/share/awstats/tools/awstats_buildstaticpages.pl -config=ricgraph -awstatsprog=/usr/lib/cgi-bin/awstats.pl -dir=/var/www/html/awstats ) >> /var/log/cron-awstats.log 2>&1
  ```
  However, for OpenSUSE or Tumbleweed do (note the difference in path):
  ```
  5 * * * * root (date; /usr/lib/cgi-bin/awstats.pl -config=ricgraph -update; /usr/share/awstats/tools/awstats_buildstaticpages.pl -config=ricgraph -awstatsprog=/usr/lib/cgi-bin/awstats.pl -dir=/srv/www/htdocs/awstats ) >> /var/log/cron-awstats.log 2>&1
  ```
* Note that AWStats also has a cron job in file
  */etc/cron.d/awstats* that comes with the installation of AWStats.
  We do not use the results it produces (but we let it run).
* Exit from user *root*.
* You can only access AWStats on the server you have installed it
  on. Go to [http://localhost:8070](http://localhost:8070).
  Note that you will only be able to see any results after `cron` has 
  executed the crontab entry above at least once.


## How to install Ricgraph and Ricgraph Explorer on SURF Research Cloud
[SURF Research Cloud](https://www.surf.nl/en/services/surf-research-cloud)
is a portal where you can easily build a virtual research environment. 
You can use preconfigured workspaces, or you can add them yourself.
A _virtual research environment_ or _workspace_ is a 
virtual machine that you can use to install Ricgraph.
Please follow these steps if you would like
to install Ricgraph and Ricgraph Explorer on SURF Research Cloud.

### Preliminaries

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

### Create a SURF Research Cloud workspace

To create a SURF Research Cloud workspace, 
follow the following steps:

* Go to the [SURF Research Cloud portal](https://portal.live.surfresearchcloud.nl)
  and log in.
* Optional: Allocate storage. This step is only required if you expect 
  to install a lot of programs on
  the virtual research environment and expect to create or use a lot of
  data. In the case of Ricgraph: > 100M nodes and edges.
  This is for advanced use only, since this storage will be attached to
  */data* in the virtual research environment, and not to */var/lib*,
  where the Neo4j Community Edition graph database lives.
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
  * Note that your workspace has a *will be removed* date. You might want
    to set it to a suitable date.
* Done.

You might want to watch the
[video how to install Ricgraph and Ricgraph Explorer on SURF Research Cloud
(2m14s) (click to view or download)](videos/ricgraph_howto_install_on_SURFResearchCloud.mp4).
Note that in the video, we use an old version of Ubuntu. Please use
Ubuntu 22.04 as described above.

<!--- GitHub embedded video link
https://github.com/UtrechtUniversity/ricgraph/assets/121875841/c7196e89-3a2f-4a30-b7ae-d41a4c2fce5b
--->

### Install Ricgraph in a SURF Research Cloud workspace

The next steps in your workspace are to install the graph database backend and
Ricgraph. You can install
[Ricgraph for a single user](ricgraph_install_configure.md#install-and-configure-ricgraph)
or
[Ricgraph as a server](ricgraph_as_server.md#ricgraph-as-a-server-on-linux).
Note that if you would like to use a webserver, you will need to use Nginx.

### Pause and resume a SURF Research Cloud workspace

On the [SURF Research Cloud portal](https://portal.live.surfresearchcloud.nl), you 
can *pause* and *resume* your workspace. *Pausing* means that the workspace will not run,
and of course then it will not be accessible. If you have paused your workspace, it does
not cost credits (money). If you *resume* your workspace, you can use it again.

### Access a SURF Research Cloud workspace

On the workspace window, you will find the name of the workspace. It will be a
*https* link that ends with *.src.surf-hosted.nl*.
SURF Research Cloud uses *guacamole*, which provides you with a desktop window
in your browser. There are two ways to access your workspace and authenticate:

* Use port 443, then you will login on your workspace using SURF conext.
  In this case, the link will look like: 
  [https://[name of your workspace].src.surf-hosted.nl](https://[name of your workspace].src.surf-hosted.nl).
* Use port 3389, then you will login on your workspace using a one time password.
  In this case, the link will look like: 
  [https://[name of your workspace].src.surf-hosted.nl:3389](https://[name of your workspace].src.surf-hosted.nl:3389).


## Steps to take to install Ricgraph as a server by hand
Skip this section if you have done the
[Fast and recommended way to install Ricgraph as a
server](#fast-and-recommended-way-to-install-ricgraph-as-a-server)
and there were no errors.

1. [Install your graph database backend](#install-your-graph-database-backend).
1. [Create a ricgraph user and group](#create-a-ricgraph-user-and-group).
1. [Create a Python virtual environment and install Ricgraph in it](#create-a-python-virtual-environment-and-install-ricgraph-in-it).
1. Create and update the [Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file).
   This is also the
   place where you specify which graph database backend you use.
1. Start harvesting data, see [Ricgraph harvest scripts](ricgraph_harvest_scripts.md#ricgraph-harvest-scripts), or
   writing scripts, see [Ricgraph script writing](ricgraph_script_writing.md#ricgraph-script-writing).
1. Start browsing using
   [Ricgraph Explorer](ricgraph_explorer.md#ricgraph-explorer).

### Install your graph database backend
Install your graph database backend (choose one of these):

* [Install and start Neo4j Community
  Edition](ricgraph_backend_neo4j.md#install-and-start-neo4j-community-edition).
* [Install and start Memgraph](ricgraph_backend_memgraph.md#install-and-start-memgraph).

### Create a ricgraph user and group
Follow these steps:

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
Follow these steps:

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
  *ricgraph_server_config/ricgraph_explorer_gunicorn.service*
  and
  *ricgraph_server_config/ricgraph_explorer.conf-apache*.
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
