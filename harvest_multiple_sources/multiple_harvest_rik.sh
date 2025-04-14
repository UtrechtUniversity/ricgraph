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
# This script simplifies running Ricgraph harvest scripts by 
# calling bash scripts that are wrappers around these harvest scripts.
# This script harvests UU and VUA sources.
# It also dumps the graph database and modifies organization names.
#
# You may want to start this script as follows:
# [name of this script] | tee output.txt
# In this case, output is written both to the terminal and to
# file 'output.txt'.
# Or use the Makefile and type:
# make bash_script=harvest_multiple_sources/multiple_harvest_rik.sh run_bash_script
#
# Original version Rik D.T. Janssen, April 2025.
#
# ########################################################################


exit_on_error() {
  exit_code=$1
  if [ "$exit_code" != "0" ] ; then
    echo ""
    echo "$0: an error occurred in a previous script."
    echo "Read above for more information, status: '$exit_code'. Exiting."
    echo ""
    exit "$exit_code"
  fi
}


echo "This script harvests a number of sources for Ricgraph from both UU and VUA."

# Test if we can use 'sudo' without password.
echo ""
echo "We need to test whether you can use 'sudo' without a password."
echo "This is necessary since this script will dump the graph database,"
echo "and that can only be done as user 'root'."
echo "If a prompt for a password appears, you cannot use 'sudo' without a"
echo "password, and then this script will break. Type <cntr>-C to quit."
echo ""
sudo make -f ../Makefile check_user_root
exit_code=$?
if [ "$exit_code" = "0" ] ; then
  echo "You can use 'sudo' without a password, this script will continue."
  echo ""
else
  echo ""
  echo "Error: you cannot use 'sudo' without a password."
  echo "You might want to add the next line to"
  echo "file /etc/sudoers with the 'visudo' command:"
  echo "$USER ALL=(ALL) NOPASSWD: /usr/bin/make"
  echo ""
  exit $exit_code
fi

data_collect_dir=$HOME/$(date +%y%m%d)-ricgraph_data_collect
graphdb_backup_dir=$data_collect_dir/graphdb_backup
harvest_result_dir=$data_collect_dir/harvest_result
explorer_data_collect_dir=$HOME/$(date +%y%m%d)-explorer_data_collect

echo "The following directories will be used:"
echo "data_collect_dir: $data_collect_dir"
echo "graphdb_backup_dir: $graphdb_backup_dir"
echo "harvest_result_dir: $harvest_result_dir"
echo "explorer_data_collect_dir: $explorer_data_collect_dir"
echo ""

if [ -d "$data_collect_dir" ]; then
  echo "Error: data_collect_dir '$data_collect_dir'"
  echo "does already exist, exiting."
  exit 1
else
  mkdir "$data_collect_dir"
fi

if [ -d "$explorer_data_collect_dir" ]; then
  echo "Error: explorer_data_collect_dir '$explorer_data_collect_dir'"
  echo "does already exist, exiting."
  exit 1
else
  mkdir "$explorer_data_collect_dir"
fi

mkdir "$graphdb_backup_dir"
mkdir "$harvest_result_dir"

echo "$0 start at $(date)."

./multiple_harvest_uu.sh
exit_on_error $?

graphdb_backup=$graphdb_backup_dir/graphdb_backup-uu-$(date +%y%m%d-%H%M)
sudo make -f ../Makefile graphdb_backup_dir="$graphdb_backup" ask_are_you_sure=no dump_graphdb_neo4j_community
exit_on_error $?
# Make sure neo4j is up and running.
sleep 120

./multiple_harvest_organization.sh --organization VUA --empty_ricgraph no
exit_on_error $?

graphdb_backup=$graphdb_backup_dir/graphdb_backup-uu+vu-$(date +%y%m%d-%H%M)
sudo make -f ../Makefile graphdb_backup_dir="$graphdb_backup" ask_are_you_sure=no dump_graphdb_neo4j_community
exit_on_error $?
# Make sure neo4j is up and running.
sleep 120

../enhance/rename_organizations.sh --organization UU
exit_on_error $?

graphdb_backup=$graphdb_backup_dir/graphdb_backup-all-$(date +%y%m%d-%H%M)
sudo make -f ../Makefile graphdb_backup_dir="$graphdb_backup" ask_are_you_sure=no dump_graphdb_neo4j_community
exit_on_error $?


# Do some saving operations.
# Save the final graphdb dump in a separate directory, for easy transfer
# to another VM.
cp "$graphdb_backup"/* "$explorer_data_collect_dir"
tar -czf "$explorer_data_collect_dir".tar.gz "$explorer_data_collect_dir"

# Collect all results in one directory, $data_collect_dir, for easy
# transfer to another computer.
mv ./*.log "$data_collect_dir"
cd ../harvest || exit 1
mv ./*.xml ./*.csv ./*.json "$harvest_result_dir"
tar -czf "$data_collect_dir.tar.gz" "$data_collect_dir"

echo "$0 done at $(date)."
echo "You can find the final graphdb dump in"
echo "  file '$explorer_data_collect_dir.tar.gz."
echo "You can find all of the harvested data in"
echo "  file '$data_collect_dir.tar.gz'."
