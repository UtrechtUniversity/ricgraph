# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
#
# Copyright (c) 2024 Rik D.T. Janssen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# ########################################################################
#
# This file is the Makefile for Ricgraph.
# For make, see https://www.gnu.org/software/make.
#
# This file will make installing Ricgraph on Linux easier. It also helps with
# dumping and restoring graph databases.
#
# Original version Rik D.T. Janssen, September 2024.
#
# ########################################################################


# ########################################################################
# These are the versions of the software to be installed.
# ########################################################################
ricgraph_version := 2.4
neo4j_community_version := 5.23.0
neo4j_desktop_version := 1.6.0
minimal_python_minor_version := 10


# ########################################################################
# Define a number of variables.
# ########################################################################
# Determine the Linux edition and version number, for debug purposes only.
linux_edition := $(shell cat /etc/os-release | grep '^NAME=' | sed 's/NAME="\(.*\)"/\1/')
ifeq ($(linux_edition),Fedora Linux)
	# Fedora does not has double quotes around the version number.
	linux_version := $(shell cat /etc/os-release | grep '^VERSION_ID=' | sed 's/VERSION_ID=\(.*\)/\1/')
else ifeq ($(linux_edition),Manjaro Linux)
	# Manjaro does not has double quotes around the version number.
	linux_version := $(shell cat /etc/os-release | grep '^BUILD_ID=' | sed 's/BUILD_ID=\(.*\)/\1/')
else
	# Ubuntu and OpenSUSE have double quotes around the version number.
	linux_version := $(shell cat /etc/os-release | grep '^VERSION_ID=' | sed 's/VERSION_ID="\(.*\)"/\1/')
endif

# Ricgraph variables.
ricgraph_download := https://github.com/UtrechtUniversity/ricgraph
ricgraph_path := $(ricgraph_download)/archive/refs/tags/v$(ricgraph_version).tar.gz
ricgraph_cuttingedge_path := $(ricgraph_download)/archive/refs/heads/main.zip
# This is the GitHub name of the Ricgraph release file that is downloaded
ricgraph_tag_name := $(shell basename $(ricgraph_path))
ricgraph_cuttingedge_name := $(shell basename $(ricgraph_cuttingedge_path))
# This is the GitHub name of the Ricgraph release file that is in the downloaded tar file.
ricgraph := ricgraph-$(ricgraph_version)

# Neo4j variable.
# Ask https://perplexity.ai for download locations, prompt:
# "What is the direct download link for neo4j community edition rpm (or deb) version?"
neo4j_download := https://dist.neo4j.org

# Misc. variables.
tmpdir := /tmp/cuttingedge_$(shell echo $$PPID)
graphdb_backupdir := $(HOME)/graphdb_backup

# Determine which python command to use.
ifeq ($(shell which python3.11 > /dev/null 2>&1 && echo $$?),0)
	# E.g. for OpenSUSE Leap, Fedora.
	python_cmd := python3.11
	actual_python_minor_version := $(shell $(python_cmd) -c 'import sys; print(sys.version_info.minor)')
else ifeq ($(shell which python3 > /dev/null 2>&1 && echo $$?),0)
	# E.g. for Ubuntu.
	python_cmd := python3
	actual_python_minor_version := $(shell $(python_cmd) -c 'import sys; print(sys.version_info.minor)')
else
	python_cmd := [not_set]
	actual_python_minor_version := [not_set]
endif

# Determine which package install command to use, and subsequently which package names to use.
# We need a package manager that can install 'rpm' or 'deb' files (for Neo4j Community Edition).
ifeq ($(shell which rpm > /dev/null 2>&1 && echo $$?),0)
	# E.g. for OpenSUSE Leap & Tumbleweed, Fedora.
	package_install_cmd := rpm -i
	neo4j_community_path := $(neo4j_download)/rpm/neo4j-$(neo4j_community_version)-1.noarch.rpm
	neo4j_cyphershell_path := $(neo4j_download)/cypher-shell/cypher-shell-$(neo4j_community_version)-1.noarch.rpm
else ifeq ($(shell which apt > /dev/null 2>&1 && echo $$?),0)
	# E.g. for Ubuntu.
	package_install_cmd := apt install
	neo4j_community_path := $(neo4j_download)/deb/neo4j_$(neo4j_community_version)_all.deb
	neo4j_cyphershell_path := $(neo4j_download)/cypher-shell/cypher-shell_$(neo4j_community_version)_all.deb
else ifeq ($(shell which dpkg > /dev/null 2>&1 && echo $$?),0)
	# E.g. for Debian.
	package_install_cmd := dpkg -i
	neo4j_community_path := $(neo4j_download)/deb/neo4j_$(neo4j_community_version)_all.deb
	neo4j_cyphershell_path := $(neo4j_download)/cypher-shell/cypher-shell_$(neo4j_community_version)_all.deb
else
	package_install_cmd := [not_set]
	neo4j_community_path := [not_set]
	neo4j_cyphershell_path := [not_set]
endif
neo4j_desktop_path := $(neo4j_download)/neo4j-desktop/linux-offline/neo4j-desktop-$(neo4j_desktop_version)-x86_64.AppImage
neo4j_desktop := $(shell basename $(neo4j_desktop_path))
neo4j_community := $(shell basename $(neo4j_community_path))
neo4j_cyphershell := $(shell basename $(neo4j_cyphershell_path))

# Determine which Apache paths to use.
ifeq ($(shell test -d /etc/apache2/vhosts.d && echo true),true)
	# E.g. for OpenSUSE Leap & Tumbleweed.
	apache_vhosts_dir := /etc/apache2/vhosts.d
	apache_service_file := /usr/lib/systemd/system/apache2.service
else ifeq ($(shell test -d /etc/apache2/sites-available && echo true),true)
	# E.g. for Ubuntu.
	apache_vhosts_dir := /etc/apache2/sites-available
	apache_service_file := /usr/lib/systemd/system/apache2.service
else ifeq ($(shell test -d /etc/httpd/conf.d && echo true),true)
	# E.g. for Fedora.
	apache_vhosts_dir := /etc/httpd/conf.d
	apache_service_file := /usr/lib/systemd/system/httpd.service
else
	apache_vhosts_dir := [not_set]
	apache_service_file := [not_set]
endif

# Determine which Nginx paths to use.
# Virtual hosts are called "Server blocks" in Nginx but I still use vhost for readability.
ifeq ($(shell test -d /etc/nginx/vhosts.d && echo true),true)
	# E.g. for OpenSUSE Leap & Tumbleweed.
	nginx_vhosts_dir := /etc/nginx/vhosts.d
else ifeq ($(shell test -d /etc/nginx/sites-available && echo true),true)
	# E.g. for Ubuntu.
	nginx_vhosts_dir := /etc/nginx/sites-available
else ifeq ($(shell test -d /etc/nginx/conf.d && echo true),true)
	# E.g. for Fedora.
	nginx_vhosts_dir := /etc/nginx/conf.d
else
	nginx_vhosts_dir := [not_set]
endif


# ########################################################################
# General targets.
# ########################################################################
all: help

help:
	@echo ""
	@echo "Ricgraph Makefile help."
	@echo "You can use this Makefile to install (parts of) Ricgraph and dump/restore"
	@echo "its graph database. The outputs will be the commands that have been executed"
	@echo "and their results. If you do not get any output, then nothing has been done,"
	@echo "because the action that you requested has already been executed."
	@echo ""
	@echo "Please be careful running this Makefile and make sure you know what"
	@echo "you do (especially with the Apache or Nginx webserver). For some actions you"
	@echo "will need to be user 'root', this Makefile will test for it."
	@echo "If you use 'make --dry-run' the commands that are to be executed will be shown,"
	@echo "but they will not be executed."
	@echo ""
	@echo "Informational commands for this Makefile:"
	@echo "- make: Displays this message."
	@echo "- make all: Displays this message."
	@echo "- make help: Displays this message."
	@echo ""
	@echo "Commands for Ricgraph as a single user (please read"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_install_configure.md):"
	@echo "- make install_neo4j_desktop: Download and install Neo4j Desktop."
	@echo "- make install_ricgraph_as_singleuser: Install Ricgraph for a single user."
	@echo "       This will also do a 'make install_neo4j_desktop' (if not done yet)."
	@echo ""
	@echo "Commands for Ricgraph as a server (you need to be 'root') (please read"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_as_server.md):"
	@echo "- make install_enable_neo4j_community: Install and enable (run)"
	@echo "       Neo4j Community Edition."
	@echo "- make install_ricgraph_as_server: Install Ricgraph as a server."
	@echo "       This will also do a 'make install_enable_neo4j_community'"
	@echo "       (if not done yet)."
	@echo "- make install_enable_ricgraphexplorer_restapi: Install and enable"
	@echo "       Ricgraph Explorer and REST API."
	@echo "       This will also do a 'make install_ricgraph_as_server' (if not done yet)."
	@echo "- make prepare_webserver_apache: Prepare webserver Apache for use with Ricgraph."
	@echo "       This will also do a 'make install_ricgraph_as_server' (if not done yet)."
	@echo "- make prepare_webserver_nginx: Prepare webserver Nginx for use with Ricgraph."
	@echo "       For SURF Research Cloud you will need the Nginx webserver."
	@echo "       This will also do a 'make install_ricgraph_as_server' (if not done yet)."
	@echo "- make dump_graphdb_neo4j_community: dump Neo4j Community graph database."
	@echo "- make restore_graphdb_neo4j_community: restore Neo4j Community graph database."
	@echo ""
	@echo "Advanced commands for this Makefile:"
	@echo "- make makefile_variables: list all variables used in this Makefile."
	@echo "- make download_cuttingedge_version: download the 'cutting edge' version of"
	@echo "       Ricgraph, that is the most current version of Ricgraph on GitHub "
	@echo "       ($(ricgraph_download)), and use that one to"
	@echo "       install Ricgraph (instead of Ricgraph release version $(ricgraph_version))."
	@echo ""

makefile_variables:
	@echo ""
	@echo "This is a list of the internal variables in this Makefile:"
	@echo "- linux_name: $(linux_edition)"
	@echo "- linux_version: $(linux_version)"
	@echo "- HOME: $(HOME)"
	@echo "- graphdb_backupdir: $(graphdb_backupdir)"
	@echo "- apache_vhosts_dir: $(apache_vhosts_dir)"
	@echo "- apache_service_file: $(apache_service_file)"
	@echo "- nginx_vhosts_dir: $(nginx_vhosts_dir)"
	@echo "- package_install_cmd: $(package_install_cmd)"
	@echo "- python_cmd: $(python_cmd)"
	@echo "- actual_python_minor_version: $(actual_python_minor_version)"
	@echo "- minimal_python_minor_version: $(minimal_python_minor_version)"
	@echo "- neo4j_community_path: $(neo4j_community_path)"
	@echo "- neo4j_cyphershell_path: $(neo4j_cyphershell_path)"
	@echo "- neo4j_desktop_path: $(neo4j_desktop_path)"
	@echo "- neo4j_community: $(neo4j_community)"
	@echo "- neo4j_cyphershell: $(neo4j_cyphershell)"
	@echo "- neo4j_desktop: $(neo4j_desktop)"
	@echo ""

check_python_minor_version:
ifeq ($(python_cmd),[not_set])
	@echo ""
	@echo "Error: Python has not been installed, please install Python >= 3.$(minimal_python_minor_version) using your package manager."
	@echo ""
	exit 1
endif
	@if [ $(actual_python_minor_version) -lt $(minimal_python_minor_version) ]; then echo "Error: Wrong Python version 3.$(actual_python_minor_version) on your system, please install Python >= 3.$(minimal_python_minor_version) using your package manager."; exit 1; fi

check_user_root:
	@if [ $(shell id -u) -ne 0 ]; then echo "Error: You need to be root. Please execute 'sudo bash' and then rerun this Makefile target."; exit 1; fi

check_user_notroot:
	@if [ $(shell id -u) -eq 0 ]; then echo "Error: You need to be a regular user. Please make sure you are and then rerun this Makefile target."; exit 1; fi

check_package_install_cmd:
ifeq ($(package_install_cmd),[not_set])
	@echo ""
	@echo "Error: Your package manager is unknown. Please make sure you have"
	@echo "a package manager that can install 'rpm' or 'deb' files."
	@echo "That is required to install Neo4j Community Edition."
	@echo ""
	exit 1
endif

check_webserver_apache:
ifeq ($(shell test ! -f $(apache_service_file) && echo true),true)
	@echo ""
	@echo "Error: Apache webserver is not installed."
	@echo "Please install it using your package manager."
	@echo ""
	exit 1
endif

check_webserver_nginx:
ifeq ($(shell test ! -f /lib/systemd/system/nginx.service && echo true),true)
	@echo ""
	@echo "Error: Nginx webserver is not installed."
	@echo "Please install it using your package manager."
	@echo ""
	exit 1
endif

# Only seems necessary for Ubuntu.
install_python_venv: check_user_root check_package_install_cmd
	$(package_install_cmd) python3-venv


# ########################################################################
# Ricgraph targets.
# ########################################################################
create_user_group_ricgraph: check_user_root
	@if ! getent group 'ricgraph' > /dev/null 2>&1; then groupadd --system ricgraph; echo "Created group 'ricgraph'."; fi
	@if ! getent passwd 'ricgraph' > /dev/null 2>&1; then useradd --system --comment "Ricgraph user" --no-create-home --gid ricgraph ricgraph; echo "Created user 'ricgraph'."; fi

install_enable_neo4j_community: check_user_root check_python_minor_version check_package_install_cmd
ifeq ($(shell test ! -f /lib/systemd/system/neo4j.service && echo true),true)
	@echo ""
	@echo "Starting Install and enable Neo4j Community Edition. Read documentation at:"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_as_server.md#install-and-start-neo4j-community-edition"
	@if echo -n "Are you sure you want to proceed? [y/N] " && read ans && ! [ $${ans:-N} = y ]; then echo "Make stopped."; exit 1; fi
	@echo ""
	@if [ ! -f $(HOME)/$(neo4j_community) ]; then cd $(HOME); echo "Downloading Neo4j Community Edition..."; wget $(neo4j_community_path); fi
	@if [ ! -f $(HOME)/$(neo4j_cyphershell) ]; then cd $(HOME); echo "Downloading Neo4j Cypher Shell..."; wget $(neo4j_cyphershell_path); fi
	$(package_install_cmd) $(HOME)/$(neo4j_cyphershell)
	$(package_install_cmd) $(HOME)/$(neo4j_community)
	@echo "If you get any errors on missing dependencies, please install them using '$(package_install_cmd)'."
	systemctl enable neo4j.service
	systemctl start neo4j.service
	@echo ""
	@echo "Done."
	@echo "Neo4j Community Edition version $(neo4j_community_version) has"
	@echo "been installed, enabled and will be run at system start."
	@echo "Before you can use it, please read the post-install steps at"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_as_server.md#post-install-steps-neo4j-community-edition"
	@echo "If you are finished, please fill in your graph database backend"
	@echo "password in file 'ricgraph.ini'. This can be done after the"
	@echo "installation of Ricgraph as server or as single user."
	@echo ""
endif

install_neo4j_desktop: check_user_notroot check_python_minor_version
ifeq ($(shell test ! -f $(HOME)/$(neo4j_desktop) && echo true),true)
	@echo ""
	@echo "Starting Download and install Neo4j Desktop. Read documentation at:"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_install_configure.md#install-neo4j-desktop"
	@if echo -n "Are you sure you want to proceed? [y/N] " && read ans && ! [ $${ans:-N} = y ]; then echo "Make stopped."; exit 1; fi
	@echo ""
	@cd $(HOME); echo "Downloading Neo4j Desktop..."; wget $(neo4j_desktop_path)
	chmod 755 $(HOME)/$(neo4j_desktop)
	@echo ""
	@echo "Done."
	@echo "Neo4j Desktop version $(neo4j_desktop_version) has been downloaded."
	@echo "Before you can use it, please read the post-install steps at"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_install_configure.md#post-install-steps-neo4j-desktop"
	@echo "If you are finished, please fill in your graph database backend"
	@echo "password in file 'ricgraph.ini'. This can be done after the"
	@echo "installation of Ricgraph as server or as single user."
	@echo ""
endif

install_ricgraph_as_server: check_user_root check_python_minor_version install_enable_neo4j_community create_user_group_ricgraph
ifeq ($(shell test ! -d /opt/ricgraph_venv && echo true),true)
	@echo ""
	@echo "Starting Install Ricgraph as a server. Read documentation at:"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_as_server.md#create-a-python-virtual-environment-and-install-ricgraph-in-it"
	@if echo -n "Are you sure you want to proceed? [y/N] " && read ans && ! [ $${ans:-N} = y ]; then echo "Make stopped."; exit 1; fi
	@echo ""
ifeq ($(linux_edition),Ubuntu)
ifeq ($(shell test ! -e /usr/share/doc/python3-venv && echo true),true)
	@# Only seems necessary for Ubuntu. Note that we are user 'root'.
	make install_ubuntu_python_venv
endif
endif
	$(python_cmd) -m venv /opt/ricgraph_venv
	@if [ ! -f /opt/$(ricgraph_tag_name) ]; then cd /opt; echo "Downloading Ricgraph..."; wget $(ricgraph_path); fi
	cd /opt; tar xf /opt/$(ricgraph_tag_name)
	mv /opt/$(ricgraph)/* /opt/ricgraph_venv
	rm -r /opt/$(ricgraph)
	/opt/ricgraph_venv/bin/pip install setuptools pip wheel
	/opt/ricgraph_venv/bin/pip install -r /opt/ricgraph_venv/requirements.txt
	cp /opt/ricgraph_venv/ricgraph.ini-sample /opt/ricgraph_venv/ricgraph.ini
	@# Prepare ricgraph.ini for Neo4j Community Edition.
	sed -i 's/^graphdb_scheme = bolt/###graphdb_scheme = bolt/' /opt/ricgraph_venv/ricgraph.ini
	sed -i 's/^graphdb_port = 7687/###graphdb_port = 7687/' /opt/ricgraph_venv/ricgraph.ini
	sed -i 's/^#graphdb_scheme = neo4j/graphdb_scheme = neo4j/' /opt/ricgraph_venv/ricgraph.ini
	sed -i 's/^#graphdb_port = 7687/graphdb_port = 7687/' /opt/ricgraph_venv/ricgraph.ini
	chown -R ricgraph:ricgraph /opt/ricgraph_venv
	chmod -R go-w /opt/ricgraph_venv
	@echo ""
	@echo "Done."
	@echo "Ricgraph version $(ricgraph_version) has been installed in"
	@echo "a Python virtual environment in /opt/ricgraph_venv."
	@echo "You may want to modify /opt/ricgraph_venv/ricgraph.ini to suit"
	@echo "your needs, please read:"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_install_configure.md#ricgraph-initialization-file"
	@echo "E.g., did you fill in your graph database backend"
	@echo "password in file 'ricgraph.ini'?"
	@echo ""
	@echo "Please read this to learn how to start Ricgraph scripts from the command line:"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_as_server.md#in-case-you-have-installed-ricgraph-as-a-server"
	@echo ""
	@echo "Alternatively, you may want to install a Python Integrated"
	@echo "development environment (IDE), such as PyCharm. Read documenentation at:"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_install_configure.md#using-a-python-integrated-development-environment-ide"
	@echo ""
endif

install_ricgraph_as_singleuser: check_user_notroot check_python_minor_version install_neo4j_desktop
ifeq ($(shell test ! -d $(HOME)/ricgraph_venv && echo true),true)
	@echo ""
	@echo "Starting Install Ricgraph for a single user. Read documentation at:"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_install_configure.md#using-pythons-venv-module"
	@if echo -n "Are you sure you want to proceed? [y/N] " && read ans && ! [ $${ans:-N} = y ]; then echo "Make stopped."; exit 1; fi
	@echo ""
ifeq ($(linux_edition),Ubuntu)
ifeq ($(shell test ! -e /usr/share/doc/python3-venv && echo true),true)
	@# Only seems necessary for Ubuntu. To install packages, we need to be 'root'.
	@echo ""
	@echo "You are missing Python package 'python3-venv'. To install, please"
	@echo "change to user 'root' and execute 'make install_ubuntu_python_venv'."
	@echo "After that, exit from user 'root' and become a regular user again."
	@echo "Next, rerun 'make install_ricgraph_as_singleuser'."
	@echo ""
	exit 1
endif
endif
	$(python_cmd) -m venv $(HOME)/ricgraph_venv
	@if [ ! -f $(HOME)/$(ricgraph_tag_name) ]; then echo cd $(HOME); "Downloading Ricgraph..."; wget $(ricgraph_path); fi
	cd $(HOME); tar xf $(HOME)/$(ricgraph_tag_name)
	mv $(HOME)/$(ricgraph)/* $(HOME)/ricgraph_venv
	rm -r $(HOME)/$(ricgraph)
	$(HOME)/ricgraph_venv/bin/pip install setuptools pip wheel
	$(HOME)/ricgraph_venv/bin/pip install -r $(HOME)/ricgraph_venv/requirements.txt
	cp $(HOME)/ricgraph_venv/ricgraph.ini-sample $(HOME)/ricgraph_venv/ricgraph.ini
	@# No need to prepare ricgraph.ini for Neo4j Desktop: that is the default.
	chmod -R go-w $(HOME)/ricgraph_venv
	@echo ""
	@echo "Done."
	@echo "Ricgraph version $(ricgraph_version) has been installed in"
	@echo "a Python virtual environment in $(HOME)/ricgraph_venv."
	@echo "You may want to modify $(HOME)/ricgraph_venv/ricgraph.ini to suit"
	@echo "your needs, please read:"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_install_configure.md#ricgraph-initialization-file"
	@echo "E.g., did you fill in your graph database backend"
	@echo "password in file 'ricgraph.ini'?"
	@echo ""
	@echo "Please read this to learn how to start Ricgraph scripts from the command line:"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_as_server.md#in-case-you-have-installed-ricgraph-for-a-single-user"
	@echo ""
	@echo "Alternatively, you may want to install a Python Integrated"
	@echo "development environment (IDE), such as PyCharm. Read documenentation at:"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_install_configure.md#using-a-python-integrated-development-environment-ide"
	@echo ""
endif

install_enable_ricgraphexplorer_restapi: check_user_root install_ricgraph_as_server
ifeq ($(shell test ! -f /etc/systemd/system/ricgraph_explorer_gunicorn.service && echo true),true)
	@echo ""
	@echo "Starting Install and enable Ricgraph Explorer and REST API."
	@echo "Read documentation at:"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_as_server.md#use-a-service-unit-file-to-run-ricgraph-explorer-and-the-ricgraph-rest-api"
	@if echo -n "Are you sure you want to proceed? [y/N] " && read ans && ! [ $${ans:-N} = y ]; then echo "Make stopped."; exit 1; fi
	@echo ""
	cp /opt/ricgraph_venv/ricgraph_server_config/ricgraph_explorer_gunicorn.service /etc/systemd/system
	systemctl daemon-reload
	systemctl enable ricgraph_explorer_gunicorn.service
	systemctl start ricgraph_explorer_gunicorn.service
	@echo ""
	@echo "Done."
	@echo "Ricgraph Explorer and the Ricgraph REST API have"
	@echo "been enabled and will be run at system start."
	@echo "These are only accessible at this (local) machine."
	@echo "You can use Ricgraph Explorer by typing http://localhost:3030 in"
	@echo "your web browser, or you can use the Ricgraph REST API by using"
	@echo "the path http://localhost:3030/api followed by a REST API endpoint."
	@echo ""
endif

prepare_webserver_apache: check_user_root check_webserver_apache install_ricgraph_as_server
ifeq ($(shell test ! -f $(apache_vhosts_dir)/ricgraph_explorer.conf && echo true),true)
ifeq ($(shell test ! -f $(apache_vhosts_dir)/ricgraph_explorer.conf-apache && echo true),true)
	@echo ""
	@echo "Starting Preparing webserver Apache for use with Ricgraph."
	@echo "Read documentation at:"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_as_server.md#use-apache-wsgi-and-asgi-to-make-ricgraph-explorer-and-the-ricgraph-rest-api-accessible-from-outside-your-virtual-machine"
	@if echo -n "Are you sure you want to proceed? [y/N] " && read ans && ! [ $${ans:-N} = y ]; then echo "Make stopped."; exit 1; fi
	@echo ""
	cp /opt/ricgraph_venv/ricgraph_server_config/ricgraph_explorer.conf-apache $(apache_vhosts_dir)
	chmod 600 $(apache_vhosts_dir)/ricgraph_explorer.conf-apache
	a2enmod mod_proxy
	a2enmod mod_proxy_http
	@echo ""
	@echo "Done."
	@echo "Webserver Apache has been prepared. To make it work, continue reading at:"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_as_server.md#post-install-steps-apache"
	@echo ""
endif
endif

prepare_webserver_nginx: check_user_root check_webserver_nginx install_ricgraph_as_server
ifeq ($(shell test ! -f $(nginx_vhosts_dir)/ricgraph_explorer.conf && echo true),true)
ifeq ($(shell test ! -f $(nginx_vhosts_dir)/ricgraph_explorer.conf-nginx && echo true),true)
	@echo ""
	@echo "Starting Preparing webserver Nginx for use with Ricgraph."
	@echo "Read documentation at:"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_as_server.md#use-nginx-wsgi-and-asgi-to-make-ricgraph-explorer-and-the-ricgraph-rest-api-accessible-from-outside-your-virtual-machine"
	@if echo -n "Are you sure you want to proceed? [y/N] " && read ans && ! [ $${ans:-N} = y ]; then echo "Make stopped."; exit 1; fi
	@echo ""
	cp /opt/ricgraph_venv/ricgraph_server_config/ricgraph_explorer.conf-nginx $(nginx_vhosts_dir)
	chmod 600 $(nginx_vhosts_dir)/ricgraph_explorer.conf-nginx
	@echo ""
	@echo "Done."
	@echo "Webserver Nginx has been prepared. To make it work, continue reading at:"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_as_server.md#post-install-steps-nginx"
	@echo ""
endif
endif

download_cuttingedge_version:
	@echo ""
	@echo "Starting Download of the 'cutting edge' version of Ricgraph, that is the most current"
	@echo "version of Ricgraph on GitHub ($(ricgraph_download))."
	@echo ""
	@echo "If you follow this download by either 'make install_ricgraph_as_singleuser' or"
	@echo "'make install_ricgraph_as_server', this Makefile will use this cutting"
	@echo "edge version instead of Ricgraph release version $(ricgraph_version)."
	@echo "This is kind of a hack, those two 'make' commands will silently use"
	@echo "the cutting edge version, while they will think it is version $(ricgraph_version)."
	@if echo -n "Are you sure you want to proceed? [y/N] " && read ans && ! [ $${ans:-N} = y ]; then echo "Make stopped."; exit 1; fi
	@echo ""
	mkdir $(tmpdir)
	cd $(tmpdir); echo "Downloading Ricgraph cutting edge version..."; wget $(ricgraph_cuttingedge_path)
	cd $(tmpdir); unzip -q $(ricgraph_cuttingedge_name)
	cd $(tmpdir); mv ricgraph-main $(ricgraph)
	cd $(tmpdir); echo "This is the cutting edge version of Ricgraph of `date +%y%m%d-%H%M`." > $(ricgraph)/0_ricgraph_cuttingedge_`date +%y%m%d-%H%M`
	cd $(tmpdir); tar czf $(ricgraph_tag_name) $(ricgraph)
	@# If this script is run as root, we assume that someone is using
	@# target 'install_ricgraph_as_server' (otherwise, why would this Makefile be run as root?).
	@# Otherwise, we assume the target is 'install_ricgraph_as_singleuser'.
	@cd $(tmpdir); if [ $(HOME) = '/root' ]; then echo "Moving cutting edge tar file $(ricgraph_tag_name) to /opt."; mv $(ricgraph_tag_name) /opt; \
		else echo "Moving cutting edge tar file $(ricgraph_tag_name) to $(HOME)."; mv $(ricgraph_tag_name) $(HOME); fi
	rm -r $(tmpdir)
	@echo ""
	@echo "Done."
	@echo ""

# Documentation for dump & restore: https://neo4j.com/docs/operations-manual/current/kubernetes/operations/dump-load
dump_graphdb_neo4j_community: check_user_root install_enable_neo4j_community
	@echo ""
	@echo "Starting Dump of graph database of Neo4j Community Edition in"
	@echo "directory $(graphdb_backupdir)."
	@echo "Read documentation at:"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_install_configure.md#create-a-neo4j-community-edition-database-dump-of-ricgraph"
	@if echo -n "Are you sure you want to proceed? [y/N] " && read ans && ! [ $${ans:-N} = y ]; then echo "Make stopped."; exit 1; fi
	@echo ""
	@if [ ! -d $(graphdb_backupdir) ]; then mkdir $(graphdb_backupdir); fi
	systemctl stop neo4j.service
	chmod 640 /etc/neo4j/*
	chmod 750 /etc/neo4j
	neo4j-admin database dump --expand-commands system --to-path=$(graphdb_backupdir)
	neo4j-admin database dump --expand-commands neo4j --to-path=$(graphdb_backupdir)
	systemctl start neo4j.service
	@echo ""
	@echo "Done."
	@echo "The graph database of Neo4j Community Edition has been dumped"
	@echo "in directory $(graphdb_backupdir)."
	@echo ""

restore_graphdb_neo4j_community: check_user_root install_enable_neo4j_community
	@echo ""
	@echo "Starting Restore of graph database of Neo4j Community Edition"
	@echo "from directory $(graphdb_backupdir)."
	@echo "Your old graph database will be removed."
	@echo "Read documentation at:"
	@echo "https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_install_configure.md#restore-a-neo4j-community-edition-database-dump-of-ricgraph-in-neo4j-community-edition"
	@if echo -n "Are you sure you want to proceed? [y/N] " && read ans && ! [ $${ans:-N} = y ]; then echo "Make stopped."; exit 1; fi
	@echo ""
	@if [ ! -f $(graphdb_backupdir)/system.dump ]; then echo "Error: Graph database dump file $(graphdb_backupdir)/system.dump does not exist."; exit 1; fi
	@if [ ! -f $(graphdb_backupdir)/neo4j.dump ]; then echo "Error: Graph database dump file $(graphdb_backupdir)/neo4j.dump does not exist."; exit 1; fi
	systemctl stop neo4j.service
	chmod 640 /etc/neo4j/*
	chmod 750 /etc/neo4j
	@# Save old database
	mv /var/lib/neo4j /var/lib/neo4j-`date +%y%m%d-%H%M`
	mkdir /var/lib/neo4j
	neo4j-admin database load --expand-commands system --from-path=$(graphdb_backupdir) --overwrite-destination=true
	neo4j-admin database load --expand-commands neo4j --from-path=$(graphdb_backupdir) --overwrite-destination=true
	chown -R neo4j:neo4j /var/lib/neo4j
	systemctl start neo4j.service
	@echo ""
	@echo "Done."
	@echo "If you get a warning that the system database may contain unwanted"
	@echo "metadata from the DBMS it was taken from, please ignore it."
	@echo "The graph database of Neo4j Community Edition has been restored"
	@echo "from directory $(graphdb_backupdir)."
	@echo ""
