#!/bin/bash
# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License, Copyright (c) 2025 Rik D.T. Janssen
#
# ########################################################################
#
# This script harvests UU and VUA sources.
# It also dumps the graph database and modifies organization names.
#
# You may want to start this script as follows:
# [name of this script] | tee output.txt
# In this case, output is written both to the terminal and to
# file 'output.txt'.
#
# Original version Rik D.T. Janssen, April 2025.
#
# ########################################################################


# Test if we can use 'sudo' without password.
echo ""
echo "We need to test whether you can use 'sudo' without a password."
echo "This is necessary since this script will dump the graph database,"
echo "and that can only be done as user 'root'."
echo "If a prompt for a password appears, you cannot use 'sudo' without a"
echo "password, and then this script will break. Type <cntr>-C to quit."
echo ""
sudo echo "You can use 'sudo' without a password, this script will continue."
echo ""

./batch_harvest_uu.sh

graphdb_backup_dir=/root/graphdb_backup-uu-$(date +%y%m%d-%H%M)
sudo make -f ../Makefile graphdb_backup_dir="$graphdb_backup_dir" ask_are_you_sure=yes dump_graphdb_neo4j_community
# Make sure neo4j is up and running.
sleep 120

./batch_harvest_organization.sh --organization VU --empty_ricgraph no

graphdb_backup_dir=/root/graphdb_backup-uu+vu-$(date +%y%m%d-%H%M)
sudo make -f ../Makefile graphdb_backup_dir="$graphdb_backup_dir" ask_are_you_sure=yes dump_graphdb_neo4j_community
# Make sure neo4j is up and running.
sleep 120

./batch_rename_organization.sh --organization UU

graphdb_backup_dir=/root/graphdb_backup-all-$(date +%y%m%d-%H%M)
sudo make -f ../Makefile graphdb_backup_dir="$graphdb_backup_dir" ask_are_you_sure=yes dump_graphdb_neo4j_community
