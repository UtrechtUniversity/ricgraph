# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
#
# Copyright (c) 2024, 2025 Rik D.T. Janssen
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
# This file will make installing Ricgraph on Linux easier. It also helps
# e.g. with dumping and restoring graph databases, and with running
# Ricgraph batch scripts.
#
# Original version Rik D.T. Janssen, September 2024.
# Updated Rik D.T. Janssen, January, March, April 2025.
#
# ########################################################################


# ########################################################################
# These are the versions of the software to be installed.
# ########################################################################
ricgraph_version := 2.10
neo4j_community_version := 5.24.0
neo4j_desktop_version := 1.6.0

# The minimal Python version required for Ricgraph.
minimal_python_minor_version := 10


# ########################################################################
# The name of the Ricgraph batch harvest script to run and its log.
# It should be in directory [Ricgraph install directory]/harvest.
# ########################################################################
#batch_script := batch_harvest_demo.py
#batch_script_log := $(basename $(batch_script))_$$(date +%y%m%d-%H%M).log


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
	# Ubuntu and OpenSUSE and Debian have double quotes around the version number.
	linux_version := $(shell cat /etc/os-release | grep '^VERSION_ID=' | sed 's/VERSION_ID="\(.*\)"/\1/')
endif

# Ricgraph variables.
ricgraph_download := https://github.com/UtrechtUniversity/ricgraph
ricgraph_path := $(ricgraph_download)/archive/refs/tags/v$(ricgraph_version).tar.gz
ricgraph_cuttingedge_path := $(ricgraph_download)/archive/refs/heads/main.zip
# This is the GitHub name of the Ricgraph release file that is downloaded
ricgraph_tag_name := $(shell basename $(ricgraph_path))
ricgraph_cuttingedge_name := $(shell basename $(ricgraph_cuttingedge_path))
ricgraph_server_install_dir := /opt/ricgraph_venv
ricgraph_singleuser_install_dir := $(HOME)/ricgraph_venv
ricgraph_explorer := ricgraph_explorer.py

# This is the GitHub name of the Ricgraph release file that is in the downloaded tar file.
ricgraph := ricgraph-$(ricgraph_version)

# You can use the following two variables as command line arguments to run
# any Ricgraph Python script. 'python_script' should contain the path to the
# script relative to the directory where this Makefile is. The same for
# 'python_script_log', unless it starts with a '/'.
# If that directory or file is not writable for the user
# executing the script, you will get an error. The values below are placeholders.
# Example use:
# 'make python_script=[script name] python_script_log=[log file] run_python_script'
python_script := maintenance/create_toc_documentation.py
python_script_log := $(dir $(python_script))$(basename $(notdir $(python_script)))_$$(date +%y%m%d-%H%M).log

# Similar for Ricgraph bash scripts.
bash_script := harvest_multiple_sources/multiple_harvest_demo.sh
bash_script_log := $(dir $(bash_script))$(basename $(notdir $(bash_script)))_$$(date +%y%m%d-%H%M).log

# Neo4j variable.
# Ask https://perplexity.ai for download locations, prompt:
# "What is the direct download link for neo4j community edition rpm (or deb) version?"
neo4j_download := https://dist.neo4j.org

# Misc. variables.
readdoc_server := https://docs.ricgraph.eu/docs/ricgraph_as_server.html#create-a-python-virtual-environment-and-install-ricgraph-in-it
readdoc_singleuser := https://docs.ricgraph.eu/docs/ricgraph_install_configure.html#using-pythons-venv-module
tmp_dir := /tmp/cuttingedge_$(shell echo $$PPID)
graphdb_backup_dir := /root/graphdb_backup
graphdb_password_file := /tmp/0-ricgraph-password.txt
graphdb_password_length := 12
graphdb_password := [not_set]
systemctl_cmd := systemctl
# This controls whether the question "Are you sure" is shown to the user or not. If it is
# something else than "no", it will be shown. Useful when this Makefile is run from a script.
ask_are_you_sure := yes


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

# Determine which python command to use when running in a virtual environment.
# Make it relative to this Makefile.
# It is used in the 'run_' targets below.
ifeq ($(shell test -f bin/python3 && echo true),true)
	# Very probably we are running from a 'ricgraph_venv' directory.
	python_cmd_venv := bin/python3
else ifeq ($(shell test -f venv/bin/python3 && echo true),true)
	# Probably we are running PyCharm or equivalent.
	python_cmd_venv := venv/bin/python3
else
	python_cmd_venv := [not_set]
endif

# Determine which package install command to use, and subsequently which package names to use.
# We need a package manager that can install 'rpm' or 'deb' files (for Neo4j Community Edition).
ifeq ($(shell which rpm > /dev/null 2>&1 && echo $$?),0)
	# E.g. for OpenSUSE Leap & Tumbleweed, Fedora.
	# To update (not supported in this Makefile) you will need "rpm -iU".
	package_install_cmd := rpm -i
	neo4j_community_path := $(neo4j_download)/rpm/neo4j-$(neo4j_community_version)-1.noarch.rpm
	neo4j_cyphershell_path := $(neo4j_download)/cypher-shell/cypher-shell-$(neo4j_community_version)-1.noarch.rpm
else ifeq ($(shell which apt > /dev/null 2>&1 && echo $$?),0)
	# E.g. for Ubuntu and Debian.
	package_install_cmd := apt-get install --yes
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
	# E.g. for Ubuntu and Debian.
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
	# E.g. for Ubuntu and Debian.
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
help:
	@echo ""
	@echo "RICGRAPH MAKEFILE HELP"
	@echo "You can use this Makefile to install (parts of) Ricgraph and dump/restore"
	@echo "its graph database. There are also other options as listed below."
	@echo ""
	@echo "The output of this Makefile will be the commands that have been executed"
	@echo "and their results. If you do not get any output, then nothing has been done."
	@echo "On success, the Makefile will print 'finished successfully'."
	@echo ""
	@echo "INFORMATIONAL COMMANDS FOR THIS MAKEFILE"
	@echo "- 'make' or 'make help': Display this help message."
	@echo "- 'make allhelp': Display the extensive help message."
	@echo ""
	@echo "RECOMMENDED METHOD TO INSTALL RICGRAPH FOR A SINGLE USER"
	@echo "Recommended for users that can change to user 'root' (for other"
	@echo "install options, type 'make allhelp'):"
	@echo "- [as user 'root'] make install_enable_neo4j_community:"
	@echo "       Download, install, enable, and run Neo4j Community Edition."
	@echo "- [as regular user] make install_ricgraph_singleuser_neo4j_community:"
	@echo "       Install Ricgraph for a single"
	@echo "       user. Neo4j Community Edition will be the graph database backend."
	@echo "       This will be done in a Python virtual environment"
	@echo "       in $(ricgraph_singleuser_install_dir)."
	@echo ""
	@echo "Commands to run something:"
	@echo "- make run_ricgraph_explorer: run Ricgraph Explorer in development mode."
	@echo "       If you use Neo4j Desktop, you need to start it first."
#	@echo "- make run_batchscript: run Ricgraph batch script '$(batch_script)'."
#	@echo "       You can change the name of this script by"
#	@echo "       adding 'batch_script=my_batchscript.py' to your 'make' command."
#	@echo "       If you use Neo4j Desktop, you need to start it first."
	@echo "- make run_python_script: you can use this to run any Ricgraph Python script."
	@echo "       Use command line parameter 'python_script',"
	@echo "       and possibly 'python_script_log'. E.g. "
	@echo "       'make python_script=[path]/[script name] run_python_script'."
	@echo "- make run_bash_script: you can use this to run any Ricgraph bash script."
	@echo "       Use command line parameter 'bash_script',"
	@echo "       and possibly 'bash_script_log'. E.g. "
	@echo "       'make bash_script=[path]/[script name] run_bash_script'."
	@echo ""
	@echo "There are many more options, to read more, type 'make allhelp'."
	@echo ""

allhelp: help
	@echo "OTHER RICGRAPH INSTALL METHODS"
	@echo "For installation options, please read"
	@echo "https://docs.ricgraph.eu/docs/ricgraph_install_configure.html"
	@echo ""
	@echo "Commands to install Ricgraph as a single user, recommended for"
	@echo "users that cannot change to user 'root':"
	@echo "- make install_neo4j_desktop: Download and install Neo4j Desktop."
	@echo "- make install_ricgraph_singleuser_neo4j_desktop: Install Ricgraph for a single"
	@echo "       user. Neo4j Desktop will be the graph database backend."
	@echo "       This will be done in a Python virtual environment"
	@echo "       in $(ricgraph_singleuser_install_dir)."
	@echo ""
	@echo "Commands to install Ricgraph as a server (you need to be 'root'):"
	@echo "- make install_enable_neo4j_community: Download, install, enable, and run"
	@echo "       Neo4j Community Edition."
	@echo "- make install_ricgraph_server: Install Ricgraph as a server."
	@echo "       This will be done in a Python virtual environment"
	@echo "       in $(ricgraph_server_install_dir)."
	@echo "- make install_enable_ricgraphexplorer_restapi: Install, enable, and run"
	@echo "       Ricgraph Explorer and its REST API as a service."
	@echo "- make prepare_webserver_apache: Prepare webserver Apache for use with Ricgraph."
	@echo "- make prepare_webserver_nginx: Prepare webserver Nginx for use with Ricgraph."
	@echo "       For SURF Research Cloud you will need the Nginx webserver."
	@echo ""
	@echo "Various install options:"
	@echo "- install the 'cutting edge' version of Ricgraph, i.e. the most current version"
	@echo "       of Ricgraph on GitHub ($(ricgraph_download)):"
	@echo "       add 'ricgraph_version=cuttingedge' to your 'make' command, e.g. as in"
	@echo "       'make ricgraph_version=cuttingedge install_ricgraph_singleuser_neo4j_community'"
	@echo "- make full_singleuser_install_neo4j_desktop: Install Neo4j Desktop"
	@echo "       and Ricgraph for a single user."
	@echo "       This will be done in a Python virtual environment"
	@echo "       in $(ricgraph_singleuser_install_dir)."
	@echo "[Note: there is no equivalent such as 'full_singleuser_install_neo4j_community',"
	@echo "since you need to be both 'root' and a 'normal user'.]"
	@echo "- make full_server_install: Install Neo4j Community Edition"
	@echo "       and Ricgraph as a server."
	@echo "       This will be done in a Python virtual environment"
	@echo "       in $(ricgraph_server_install_dir)."
	@echo ""
	@echo "ADVANCED OPTIONS"
	@echo "Emptying, dumping, or restoring the graph database:"
	@echo "- make empty_graphdb_neo4j_community: emtpy Neo4j Community graph database."
	@echo "- make dump_graphdb_neo4j_community: dump Neo4j Community graph database"
	@echo "       in directory $(graphdb_backup_dir)."
	@echo "       You can use command line parameter 'graphdb_backup_dir'"
	@echo "       to specify the directory to dump."
	@echo "- make restore_graphdb_neo4j_community: restore Neo4j Community graph database"
	@echo "       from directory $(graphdb_backup_dir)."
	@echo "       You can use command line parameter 'graphdb_backup_dir'"
	@echo "       to specify the directory to restore from."
	@echo ""
	@echo "Miscellaneous options:"
	@echo "- make makefile_variables: list all variables used in this Makefile."
	@echo "- make generate_graphdb_password: generate a password for the graph database."
	@echo "       Write it to file $(graphdb_password_file)."
	@echo "       Only do this if the file does not exist."
	@echo "- make specify_graphdb_password: specify (type) a password for the graph"
	@echo "       database. Write it to file $(graphdb_password_file)."
	@echo "       Always create this file, even if it already exists."
	@echo "- make clean: removes files you have downloaded."
	@echo "       If you have used command line parameters for previous make calls"
	@echo "       (e.g. ricgraph_version=cuttingedge), you will have to call this clean"
	@echo "       with the same command line parameters."
	@echo ""
	@echo "If you use 'make --dry-run [Makefile target]' the commands that are to be"
	@echo "executed will be shown, but they will not be executed."
	@echo ""
	@echo "'make $(MAKEOVERRIDES) $@' finished successfully."


all:
	@echo ""
	@echo "You have typed 'make all'."
	@echo "With the Ricgraph Makefile, this will not install anything."
	@echo "To learn about valid Makefile options (targets), type 'make help'."
	@echo ""


makefile_variables:
	@echo ""
	@echo "This is a list of the internal variables in this Makefile:"
	@echo "- ricgraph_version: $(ricgraph_version)"
	@echo "- neo4j_community_version: $(neo4j_community_version)"
	@echo "- neo4j_desktop_version: $(neo4j_desktop_version)"
	@echo "- package_install_cmd: $(package_install_cmd)"
	@echo "- python_cmd: $(python_cmd)"
	@echo "- python_cmd_venv: $(python_cmd_venv)"
	@echo "- actual_python_minor_version: $(actual_python_minor_version)"
	@echo "- minimal_python_minor_version: $(minimal_python_minor_version)"
	@echo "- linux_name: $(linux_edition)"
	@echo "- linux_version: $(linux_version)"
	@echo "- HOME: $(HOME)"
	@echo "- ricgraph_server_install_dir: $(ricgraph_server_install_dir)"
	@echo "- ricgraph_singleuser_install_dir: $(ricgraph_singleuser_install_dir)"
	@echo "- apache_vhosts_dir: $(apache_vhosts_dir)"
	@echo "- apache_service_file: $(apache_service_file)"
	@echo "- nginx_vhosts_dir: $(nginx_vhosts_dir)"
	@echo "- neo4j_community: $(neo4j_community)"
	@echo "- neo4j_community_path: $(neo4j_community_path)"
	@echo "- neo4j_cyphershell: $(neo4j_cyphershell)"
	@echo "- neo4j_cyphershell_path: $(neo4j_cyphershell_path)"
	@echo "- neo4j_desktop: $(neo4j_desktop)"
	@echo "- neo4j_desktop_path: $(neo4j_desktop_path)"
	@echo "- graphdb_backup_dir: $(graphdb_backup_dir)"
	@echo "- graphdb_password_file: $(graphdb_password_file)"
	@echo "- graphdb_password_length: $(graphdb_password_length)"
#	@echo "- batch_script: $(batch_script)"
#	@echo "- batch_script_log: $(batch_script_log)"
	@echo "- ricgraph_explorer: $(ricgraph_explorer)"
	@echo "- python_script: $(python_script)"
	@echo "- python_script_log: $(python_script_log)"
	@echo "- bash_script: $(bash_script) "
	@echo "- bash_script_log: $(bash_script_log)"
	@echo ""


# ########################################################################
# Ricgraph targets.
# ########################################################################
create_user_group_ricgraph: check_user_root
	@# Do not put '[' and ']' around the condition of the if's below, 
	@# then it will not work.
	@if ! getent group 'ricgraph' > /dev/null 2>&1; then groupadd --system ricgraph; echo "Created group 'ricgraph'."; fi
	@if ! getent passwd 'ricgraph' > /dev/null 2>&1; then useradd --system --comment "Ricgraph user" --no-create-home --gid ricgraph ricgraph; echo "Created user 'ricgraph'."; fi


# Additional target "install_python_venv" since we may need it later on, and we are root now, so let's do it.
install_enable_neo4j_community: check_user_root check_python_minor_version check_package_install_cmd generate_graphdb_password install_python_venv
ifeq ($(shell test ! -f /lib/systemd/system/neo4j.service && echo true),true)
	@echo ""
	@echo "Starting Install and enable Neo4j Community Edition."
	@echo "You may want to read more at:"
	@echo "https://docs.ricgraph.eu/docs/ricgraph_backend_neo4j.html#install-and-start-neo4j-community-edition"
	$(call are_you_sure)
	@echo ""
	@if [ ! -f $(HOME)/$(neo4j_community) ]; then cd $(HOME); echo "Downloading Neo4j Community Edition..."; wget $(neo4j_community_path); fi
	@if [ ! -f $(HOME)/$(neo4j_cyphershell) ]; then cd $(HOME); echo "Downloading Neo4j Cypher Shell..."; wget $(neo4j_cyphershell_path); fi
	$(package_install_cmd) $(HOME)/$(neo4j_cyphershell)
	$(package_install_cmd) $(HOME)/$(neo4j_community)
	@echo "If you get any errors on missing dependencies, please install them using '$(package_install_cmd)'."
	$(call read_graphdb_password)
	@# The following can only be done if you have not started Neo4j yet.
	neo4j-admin dbms set-initial-password $(graphdb_password)
	$(systemctl_cmd) enable neo4j.service
	$(systemctl_cmd) start neo4j.service
	@echo ""
	@echo "Done."
	@echo "Neo4j Community Edition version $(neo4j_community_version) has"
	@echo "been installed, enabled and will be run at system start."
	@echo "The password to access it can be found in $(graphdb_password_file)."
	@echo ""
	@echo "'make $(MAKEOVERRIDES) $@' finished successfully."
endif


install_neo4j_desktop: check_user_notroot check_python_minor_version generate_graphdb_password
ifeq ($(shell test ! -f $(HOME)/$(neo4j_desktop) && echo true),true)
	@echo ""
	@echo "Starting Download and install Neo4j Desktop." 
	@echo "You may want to read more at:"
	@echo "https://docs.ricgraph.eu/docs/ricgraph_backend_neo4j.html#install-neo4j-desktop"
	$(call are_you_sure)
	@echo ""
	@cd $(HOME); echo "Downloading Neo4j Desktop..."; wget $(neo4j_desktop_path)
	chmod 755 $(HOME)/$(neo4j_desktop)
	@echo ""
	@echo "Done."
	@echo "Neo4j Desktop version $(neo4j_desktop_version) has been downloaded."
	@echo "Before you can use it, please read the post-install steps at"
	@echo "https://docs.ricgraph.eu/docs/ricgraph_backend_neo4j.html#post-install-steps-neo4j-desktop"
	@echo "One of the steps is to fill in a password. Use the"
	@echo "password in file $(graphdb_password_file)."
	@echo "If you do this, you do not need to fill in this password in"
	@echo "file 'ricgraph.ini' later on, this Makefile will take care of it."
	@echo ""
	@echo "'make $(MAKEOVERRIDES) $@' finished successfully."
endif


full_server_install: install_enable_neo4j_community install_ricgraph_server
	@echo ""


install_ricgraph_server: check_user_root check_python_minor_version create_user_group_ricgraph
ifeq ($(shell test ! -d $(ricgraph_server_install_dir) && echo true),true)
	@# This test is placed here instead of in function install_ricgraph
	@# because it will keep the code of install_ricgraph more clear.
	$(call install_ricgraph,$(ricgraph_server_install_dir),"server","neo4j_community_edition",$(ricgraph_version),$(readdoc_server))
endif


full_singleuser_install_neo4j_desktop: install_neo4j_desktop install_ricgraph_singleuser_neo4j_desktop
	@echo ""


install_ricgraph_singleuser_neo4j_community: check_user_notroot check_python_minor_version
ifeq ($(shell test ! -d $(ricgraph_singleuser_install_dir) && echo true),true)
	@# This test is placed here instead of in function install_ricgraph
	@# because it will keep the code of install_ricgraph more clear.
	$(call install_ricgraph,$(ricgraph_singleuser_install_dir),"singleuser","neo4j_community_edition",$(ricgraph_version),$(readdoc_singleuser))
endif


install_ricgraph_singleuser_neo4j_desktop: check_user_notroot check_python_minor_version
ifeq ($(shell test ! -d $(ricgraph_singleuser_install_dir) && echo true),true)
	@# This test is placed here instead of in function install_ricgraph
	@# because it will keep the code of install_ricgraph more clear.
	$(call install_ricgraph,$(ricgraph_singleuser_install_dir),"singleuser","neo4j_desktop",$(ricgraph_version),$(readdoc_singleuser))
endif


install_enable_ricgraphexplorer_restapi: check_user_root full_server_install
ifeq ($(shell test ! -f /etc/systemd/system/ricgraph_explorer_gunicorn.service && echo true),true)
	@echo ""
	@echo "Starting Install and enable Ricgraph Explorer and REST API."
	@echo "You may want to read more at:"
	@echo "https://docs.ricgraph.eu/docs/ricgraph_as_server.html#use-a-service-unit-file-to-run-ricgraph-explorer-and-the-ricgraph-rest-api"
	$(call are_you_sure)
	@echo ""
	cp $(ricgraph_server_install_dir)/ricgraph_server_config/ricgraph_explorer_gunicorn.service /etc/systemd/system
	$(systemctl_cmd) daemon-reload
	$(systemctl_cmd) enable ricgraph_explorer_gunicorn.service
	$(systemctl_cmd) start ricgraph_explorer_gunicorn.service
	@echo ""
	@echo "Done."
	@echo "Ricgraph Explorer and the Ricgraph REST API have"
	@echo "been enabled, started, and will be run at system start."
	@echo "These are only accessible at this (local) machine."
	@echo "You can use Ricgraph Explorer by typing http://localhost:3030 in"
	@echo "your web browser, or you can use the Ricgraph REST API by using"
	@echo "the path http://localhost:3030/api followed by a REST API endpoint."
	@echo ""
	@echo "'make $(MAKEOVERRIDES) $@' finished successfully."
endif


prepare_webserver_apache: check_user_root check_webserver_apache full_server_install
ifeq ($(shell test ! -f $(apache_vhosts_dir)/ricgraph_explorer.conf && echo true),true)
ifeq ($(shell test ! -f $(apache_vhosts_dir)/ricgraph_explorer.conf-apache && echo true),true)
	@echo ""
	@echo "Starting Preparing webserver Apache for use with Ricgraph."
	@echo "Please make sure you know what you do."
	@echo "Please, please, do read the documentation at:"
	@echo "https://docs.ricgraph.eu/docs/ricgraph_as_server.html#use-apache-wsgi-and-asgi-to-make-ricgraph-explorer-and-the-ricgraph-rest-api-accessible-from-outside-your-virtual-machine"
	$(call are_you_sure)
	@echo ""
	cp $(ricgraph_server_install_dir)/ricgraph_server_config/ricgraph_explorer.conf-apache $(apache_vhosts_dir)
	chmod 600 $(apache_vhosts_dir)/ricgraph_explorer.conf-apache
	a2enmod mod_proxy
	a2enmod mod_proxy_http
	@echo ""
	@echo "Done."
	@echo "Webserver Apache has been prepared. To make it work, continue reading at:"
	@echo "https://docs.ricgraph.eu/docs/ricgraph_as_server.html#post-install-steps-apache"
	@echo ""
	@echo "'make $(MAKEOVERRIDES) $@' finished successfully."
endif
endif


prepare_webserver_nginx: check_user_root check_webserver_nginx full_server_install
ifeq ($(shell test ! -f $(nginx_vhosts_dir)/ricgraph_explorer.conf && echo true),true)
ifeq ($(shell test ! -f $(nginx_vhosts_dir)/ricgraph_explorer.conf-nginx && echo true),true)
	@echo ""
	@echo "Starting Preparing webserver Nginx for use with Ricgraph."
	@echo "Please make sure you know what you do."
	@echo "Please, please, do read the documentation at:"
	@echo "https://docs.ricgraph.eu/docs/ricgraph_as_server.html#use-nginx-wsgi-and-asgi-to-make-ricgraph-explorer-and-the-ricgraph-rest-api-accessible-from-outside-your-virtual-machine"
	$(call are_you_sure)
	@echo ""
	cp $(ricgraph_server_install_dir)/ricgraph_server_config/ricgraph_explorer.conf-nginx $(nginx_vhosts_dir)
	chmod 600 $(nginx_vhosts_dir)/ricgraph_explorer.conf-nginx
	@echo ""
	@echo "Done."
	@echo "Webserver Nginx has been prepared. To make it work, continue reading at:"
	@echo "https://docs.ricgraph.eu/docs/ricgraph_as_server.html#post-install-steps-nginx"
	@echo ""
	@echo "'make $(MAKEOVERRIDES) $@' finished successfully."
endif
endif


# Documentation for dump & restore: https://neo4j.com/docs/operations-manual/current/kubernetes/operations/dump-load
dump_graphdb_neo4j_community: check_user_root check_neo4jadmin_cmd
	@echo ""
	@echo "Starting Dump of graph database of Neo4j Community Edition in"
	@echo "directory $(graphdb_backup_dir)."
	$(call are_you_sure)
	@echo ""
	@if [ ! -d $(graphdb_backup_dir) ]; then mkdir $(graphdb_backup_dir); fi
	@if [ -f $(graphdb_backup_dir)/system.dump ]; then echo "Error: Graph database dump file $(graphdb_backup_dir)/system.dump does exist, you may overwrite an existing dump. Please remove it first."; exit 1; fi
	@if [ -f $(graphdb_backup_dir)/neo4j.dump ]; then echo "Error: Graph database dump file $(graphdb_backup_dir)/neo4j.dump does exist, you may overwrite an existing dump. Please remove it first."; exit 1; fi
	$(systemctl_cmd) stop neo4j.service
	chmod 640 /etc/neo4j/*
	chmod 750 /etc/neo4j
	neo4j-admin database dump --expand-commands system --to-path=$(graphdb_backup_dir)
	neo4j-admin database dump --expand-commands neo4j --to-path=$(graphdb_backup_dir)
	$(systemctl_cmd) start neo4j.service
	@echo ""
	@echo "Done."
	@echo "The graph database of Neo4j Community Edition has been dumped"
	@echo "in directory $(graphdb_backup_dir)."
	@echo ""
	@echo "'make $(MAKEOVERRIDES) $@' finished successfully."


restore_graphdb_neo4j_community: check_user_root check_neo4jadmin_cmd
	@echo ""
	@echo "Starting Restore of graph database of Neo4j Community Edition"
	@echo "from directory $(graphdb_backup_dir)."
	@echo "Your old graph database will be removed."
	$(call are_you_sure)
	@echo ""
	@if [ ! -f $(graphdb_backup_dir)/system.dump ]; then echo "Error: Graph database dump file $(graphdb_backup_dir)/system.dump does not exist."; exit 1; fi
	@if [ ! -f $(graphdb_backup_dir)/neo4j.dump ]; then echo "Error: Graph database dump file $(graphdb_backup_dir)/neo4j.dump does not exist."; exit 1; fi
	$(systemctl_cmd) stop neo4j.service
	chmod 640 /etc/neo4j/*
	chmod 750 /etc/neo4j
	@# Save old database
	@if [ -d /var/lib/neo4j ]; then mv /var/lib/neo4j /var/lib/neo4j-$$(date +%y%m%d-%H%M); fi
	mkdir /var/lib/neo4j
	neo4j-admin database load --expand-commands system --from-path=$(graphdb_backup_dir) --overwrite-destination=true
	neo4j-admin database load --expand-commands neo4j --from-path=$(graphdb_backup_dir) --overwrite-destination=true
	chown -R neo4j:neo4j /var/lib/neo4j
	$(systemctl_cmd) start neo4j.service
	@echo ""
	@echo "If you get a warning that the system database may contain unwanted"
	@echo "metadata from the DBMS it was taken from, please ignore it."
	@echo ""
	@echo "Done."
	@echo "The graph database of Neo4j Community Edition has been restored"
	@echo "from directory $(graphdb_backup_dir)."
	@echo ""
	@echo "If you use the Ricgraph Explorer gunicorn service, please execute"
	@echo "the command 'systemctl restart ricgraph_explorer_gunicorn' now."
	@echo ""
	@echo "'make $(MAKEOVERRIDES) $@' finished successfully."


empty_graphdb_neo4j_community: check_user_root generate_graphdb_password check_neo4jadmin_cmd
	@echo ""
	@echo "Starting emptying of graph database of Neo4j Community Edition."
	@echo "Your old graph database will be removed."
	$(call are_you_sure)
	@echo ""
	$(systemctl_cmd) stop neo4j.service
	chmod 640 /etc/neo4j/*
	chmod 750 /etc/neo4j
	@# Save old database
	@if [ -d /var/lib/neo4j ]; then mv /var/lib/neo4j /var/lib/neo4j-$$(date +%y%m%d-%H%M); fi
	mkdir /var/lib/neo4j
	$(call read_graphdb_password)
	neo4j-admin dbms set-initial-password $(graphdb_password)
	chown -R neo4j:neo4j /var/lib/neo4j
	$(systemctl_cmd) start neo4j.service
	@echo ""
	@echo "Done."
	@echo "The graph database of Neo4j Community Edition is now emtpy."
	@echo "The password to access it can be found in $(graphdb_password_file)."
	@echo ""
	@echo "'make $(MAKEOVERRIDES) $@' finished successfully."


#run_batchscript:
#	@echo ""
#	@echo "This target will run Ricgraph batch script harvest/$(batch_script)."
#	@echo "The output will be both on screen as well as in file"
#	@echo "harvest/$(batch_script_log)."
#	@echo "It may take a while before the output appears on screen,"
#	@echo "this is due to buffering of the output."
#	@echo ""
#	@echo "If you continue, this script may delete your current graph database."
#	$(call are_you_sure)
#	@echo ""
#	@if [ ! -f harvest/$(batch_script) ]; then echo "Error: batch script '$(batch_script)' does not exist."; exit 1; fi
#	@if [ ! -f $(python_cmd_venv) ]; then echo "Error: python '$(python_cmd_venv)' does not exist."; exit 1; fi
#	@if [ $(shell id -u) = 0 ]; then \
#		sudo -u ricgraph bash -c 'cd harvest; ../$(python_cmd_venv) $(batch_script) | tee $(batch_script_log)'; \
#	else \
#		cd harvest; ../$(python_cmd_venv) $(batch_script) | tee $(batch_script_log); \
#	fi


run_ricgraph_explorer:
	@echo ""
	@echo "This target will run Ricgraph Explorer in development mode"
	@echo "from ricgraph_explorer/$(ricgraph_explorer)."
	@echo ""
	@if [ ! -f ricgraph_explorer/$(ricgraph_explorer) ]; then echo "Error: script '$(ricgraph_explorer)' does not exist."; exit 1; fi
	@if [ ! -f $(python_cmd_venv) ]; then echo "Error: python '$(python_cmd_venv)' does not exist."; exit 1; fi
	cd ricgraph_explorer; ../$(python_cmd_venv) $(ricgraph_explorer)


run_python_script:
	@echo ""
	@echo "This target will run Ricgraph Python script $(python_script)."
	@echo "You need to specify the path to the script, in a subdirectory"
	@echo "of the directory this Makefile is in."
	@echo "The output will be both on screen as well as in file"
	@echo "$(python_script_log)."
	@echo "If you don't have write permission to this file, you will get an error."
	@echo "It may take a while before the output appears on screen,"
	@echo "this is due to buffering of the output."
	$(call are_you_sure)
	@echo ""
	@if [ ! -f $(python_script) ]; then echo "Error: script '$(python_script)' does not exist."; exit 1; fi
	@if [ ! -f $(python_cmd_venv) ]; then echo "Error: python '$(python_cmd_venv)' does not exist."; exit 1; fi
	@# Check if the path to 'python_script_log' starts with '/'. If so, it is considered a full path.
	@if [ $(shell echo $(python_script_log) | cut -c1) = '/' ]; then \
		cd $(dir $(python_script)); ../$(python_cmd_venv) $(notdir $(python_script)) | tee $(python_script_log); \
	else \
		cd $(dir $(python_script)); ../$(python_cmd_venv) $(notdir $(python_script)) | tee ../$(python_script_log); \
	fi


run_bash_script:
	@echo ""
	@echo "This target will run Ricgraph bash script $(bash_script)."
	@echo "You need to specify the path to the script, in a subdirectory"
	@echo "of the directory this Makefile is in."
	@echo "The output will be both on screen as well as in file"
	@echo "$(bash_script_log)."
	@echo "If you don't have write permission to this file, you will get an error."
	@echo "It may take a while before the output appears on screen,"
	@echo "this is due to buffering of the output."
	$(call are_you_sure)
	@echo ""
	@if [ ! -f $(bash_script) ]; then echo "Error: script '$(bash_script)' does not exist."; exit 1; fi
	@# Check if the path to 'bash_script_log' starts with '/'. If so, it is considered a full path.
	@if [ $(shell echo $(bash_script_log) | cut -c1) = '/' ]; then \
		cd $(dir $(bash_script)); ./$(notdir $(bash_script)) | tee $(bash_script_log); \
	else \
		cd $(dir $(bash_script)); ./$(notdir $(bash_script)) | tee ../$(bash_script_log); \
	fi


# Note that if you have used command line parameters for previous make calls
# (e.g. ricgraph_version=cuttingedge), you will have to call this clean
# with the same command line parameters.
clean:
	rm -f $(HOME)/$(neo4j_cyphershell) $(HOME)/$(neo4j_community)
	rm -f $(dir $(ricgraph_server_install_dir))/$(ricgraph_tag_name)
	rm -f $(dir $(ricgraph_singleuser_install_dir))/$(ricgraph_tag_name)


# ########################################################################
# General targets.
# ########################################################################
check_python_minor_version:
ifeq ($(python_cmd),[not_set])
	@echo ""
	@echo "Error: Python has not been installed, please install Python >= 3.$(minimal_python_minor_version) using your package manager."
	@echo ""
	exit 1
endif
	@if [ $(actual_python_minor_version) -lt $(minimal_python_minor_version) ]; then \
		echo "Error: Wrong Python version 3.$(actual_python_minor_version) on your system,"; \
		echo "please install Python >= 3.$(minimal_python_minor_version) using your package manager."; \
		exit 1; \
	fi


check_user_root:
	@if [ $(shell id -u) != 0 ]; then echo "Error: You need to be root. Please execute 'sudo bash' and then rerun the 'make' command you started with."; exit 1; fi


check_user_notroot:
	@if [ $(shell id -u) = 0 ]; then echo "Error: You need to be a regular user. Please make sure you are and then rerun the 'make' command you started with."; exit 1; fi


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
install_python_venv: check_package_install_cmd
ifeq ($(linux_edition),Ubuntu)
ifeq ($(shell test ! -e /usr/share/doc/python3.$(actual_python_minor_version)-venv && echo true),true)
	@if [ $(shell id -u) != 0 ]; then \
		echo ""; \
		echo "You are missing Python package 'python3.$(actual_python_minor_version)-venv'. To install, please"; \
		echo "change to user 'root' (type 'sudo bash') and execute 'make install_python_venv'."; \
		echo "After that, exit from user 'root' and become a regular user again."; \
		echo "Then rerun the 'make' command you started with."; \
		echo ""; \
		exit 1; \
	fi
	$(package_install_cmd) python3.$(actual_python_minor_version)-venv
endif
endif


check_neo4jadmin_cmd:
ifneq ($(shell which neo4j-admin > /dev/null 2>&1 && echo $$?),0)
	@echo ""
	@echo "Error: You need the 'neo4j-admin' command to dump or restore a graph database."
	@echo "You can install it by running 'make install_enable_neo4j_community'."
	@echo ""
	exit 1
endif


generate_graphdb_password:
	@if [ ! -f $(graphdb_password_file) ]; then \
		< /dev/urandom tr -dc 'A-Za-z0-9' | head -c $(graphdb_password_length) > $(graphdb_password_file); \
		echo "Created graphdb_password_file $(graphdb_password_file)."; \
	fi


specify_graphdb_password:
	@echo -n "Specify the graph database password you want to use: "
	@read answer && echo -n "$$answer" > $(graphdb_password_file)
	@echo "Created graphdb_password_file $(graphdb_password_file)."


# 'read_graphdb_password' is a function, defined below.

# ########################################################################
# Ricgraph functions.
# ########################################################################
define read_graphdb_password
	@if [ ! -f $(graphdb_password_file) ]; then \
		echo "Error: graphdb_password_file $(graphdb_password_file) not found."; \
		echo "You need to install Neo4j first. This will generate this file."; \
		exit 1; \
	fi
	$(eval graphdb_password := $(shell cat $(graphdb_password_file)))
endef


define are_you_sure
	@if [ $(ask_are_you_sure) != "no" ]; then \
		if echo -n "Are you sure you want to proceed? [y/n] " && read ans && ! [ $${ans:-N} = y ]; then \
			echo "Make stopped."; \
			exit 1; \
		fi \
	fi
endef


# $(1) is install location (full path), $(2) is either "server" or "singleuser",
# $(3) is either "neo4j_desktop" or "neo4j_community_edition", $(4) is version, $(5) is documentation link.
define install_ricgraph
	@echo ""
	@echo "Starting install of Ricgraph version '$(4)' in"
	@echo "directory '$(1)'."
	@echo "as '$(2)'. The database to be used is '$(3)'."
	@echo "You may want to read more at:"
	@echo "$(5)"
	$(call are_you_sure)
	@echo ""
	@if [ -d $(1) ]; then echo -e "Error: Ricgraph install dir $(1) already exists,\nplease remove it first."; exit 1; fi
	@if [ $(2) != "server" ] && [ $(2) != "singleuser" ]; then echo "Error: wrong value for parameter #2: '$(2)'."; exit 1; fi
	@if [ $(3) != "neo4j_desktop" ] && [ $(3) != "neo4j_community_edition" ]; then echo "Error: wrong value for parameter #3: '$(3)'."; exit 1; fi
	@# Only seems necessary for Ubuntu.
	@if [ "$(linux_edition)" = "Ubuntu" ]; then \
		make install_python_venv; \
	fi
	@if [ ! -d $(dir $(1)) ]; then mkdir -p $(dir $(1)); fi
	@# Note $(4) is version. If it is 'cuttingedge', download it first.
	@# For the change in Makefile, if we use cutting edge, we need to use the local version
	@# of the ricgraph module in the Makefile instead of PyPIs version.
	@if [ "$(4)" = "cuttingedge" ]; then \
		mkdir $(tmp_dir); \
		cd $(tmp_dir); \
		echo "Downloading Ricgraph cutting edge version..."; \
		wget $(ricgraph_cuttingedge_path); \
		unzip -q $(ricgraph_cuttingedge_name); \
		mv ricgraph-main $(ricgraph); \
		echo "This is the cutting edge version of Ricgraph of $$(date +%y%m%d-%H%M)." > $(ricgraph)/0_ricgraph_cuttingedge_$$(date +%y%m%d-%H%M); \
		sed -i 's|; ../$$(python_cmd_venv)|; PYTHONPATH=../ricgraph ../$$(python_cmd_venv)|' $(ricgraph)/Makefile; \
		sed -i 's|# ## ### #### #####|python_path=../ricgraph|' $(ricgraph)/library/get_cmdline_args.sh; \
		tar czf $(ricgraph_tag_name) $(ricgraph); \
		mv -f $(ricgraph_tag_name) $(dir $(1)); \
		rm -r $(tmp_dir); \
	fi
	@if [ ! -f $(dir $(1))/$(ricgraph_tag_name) ]; then cd $(dir $(1)); echo "Downloading Ricgraph..."; wget $(ricgraph_path); fi
	$(python_cmd) -m venv $(1)
	cd $(1); tar xf $(dir $(1))/$(ricgraph_tag_name)
	mv $(1)/$(ricgraph)/* $(1)
	rm -r $(1)/$(ricgraph)
	$(1)/bin/pip install setuptools pip wheel
	$(1)/bin/pip install -r $(1)/requirements.txt
	cp $(1)/ricgraph.ini-sample $(1)/ricgraph.ini
	$(call read_graphdb_password)
	sed -i 's/^graphdb_password =/graphdb_password = $(graphdb_password)/' $(1)/ricgraph.ini
	@# Neo4j Community is the default in ricgraph.ini, for Desktop we need to modify.
	@# Note $(3) is either "neo4j_desktop" or "neo4j_community_edition".
	@if [ "$(3)" = "neo4j_desktop" ]; then \
		sed -i 's/^graphdb_scheme = neo4j/###graphdb_scheme = neo4j/' $(1)/ricgraph.ini; \
		sed -i 's/^graphdb_port = 7687/###graphdb_port = 7687/' $(1)/ricgraph.ini; \
		sed -i 's/^#graphdb_scheme = bolt/graphdb_scheme = bolt/' $(1)/ricgraph.ini; \
		sed -i 's/^#graphdb_port = 7687/graphdb_port = 7687/' $(1)/ricgraph.ini; \
	fi
	@if [ "$(2)" = "server" ]; then \
		chown -R ricgraph:ricgraph $(dir $(1)); \
		chmod -R go-w $(dir $(1)); \
	fi
	@echo ""
	@echo "Done."
	@echo "Ricgraph version '$(4)' has been installed in"
	@echo "a Python virtual environment in '$(1)'."
	@echo "It is ready to be used. You may want to use one of this Makefile"
	@echo "'run_' targets, type 'make help' to learn more."
	@echo "Also, you may want to modify '$(1)/ricgraph.ini'"
	@echo "to suit your needs, please read:"
	@echo "https://docs.ricgraph.eu/docs/ricgraph_install_configure.html#ricgraph-initialization-file"
	@echo ""
	@echo "'make $(MAKEOVERRIDES) $@' finished successfully."
endef
