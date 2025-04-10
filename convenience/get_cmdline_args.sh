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
# This script parses command line parameters for the harvest scripts.
# It can be called using "source get_cmdline_args.sh" and will return:
# - $python_cmd: the python interpreter to be used.
# - $python_path: the PYTHONPATH to be used for the python interpreter.
# - $organization: the organization for which to harvest.
# - $empty_ricgraph: whether to empty Ricgraph before harvesting
#   		     the first source.
#
# Original version Rik D.T. Janssen, April 2025.
#
# ########################################################################

usage="\nUse Ricgraph to harvest an organization.\n"
usage+="Usage: $0 [options]\nOptions:"
usage+="\n\t-c, --python_cmd [python interpreter]"
usage+="\n\t\tSpecify a python interpreter. If absent, and a python"
usage+="\n\t\tvirtual environment is used, we try to get that interpreter."
usage+="\n\t-p, --python_path [python path]"
usage+="\n\t\tSpecify a value for PYTHONPATH. If absent, '.' is assumed."
usage+="\n\t-o, --organization [organization]"
usage+="\n\t\tSpecify an organization to harvest for."
usage+="\n\t-e, --empty_ricgraph [yes|no]"
usage+="\n\t\tSpecify whether to empty Ricgraph before harvesting the"
usage+="\n\t\tfirst organization. If absent, 'no' is assumed."
usage+="\n"

if [ $# -eq 0 ]; then
  echo -e "$usage"
  exit 1
fi

# the ':' after a parameter tells us it needs a parameter value.
args=$(getopt --options c:p:o:e:h --longoptions python_cmd:,python_path:,organization:,empty_ricgraph:,help -n "$0" -- "$@")
exit_code=$?
if [ "$exit_code" != "0" ] ; then
  # 'getopt' went wrong, e.g. it got an invalid option.
  echo "Exiting."
  exit 1
fi
eval set -- "$args"
while true; do
  case "$1" in
  -h|--help) echo -e "$usage"; exit 1;;
  -c|--python_cmd) python_cmd=$2; shift 2;;
  -p|--python_path) python_path=$2; shift 2;;
  -o|--organization) organization=$2; shift 2;;
  -e|--empty_ricgraph) empty_ricgraph=$2; shift 2;;
  --) shift; break;;
  *) echo "Invalid option: $1"; exit 1;;
  esac
done

if [ -z "$python_cmd" ] && [ -f ../bin/python3 ]; then
  # We are in a python venv in .../ricgraph_venv.
  python_cmd=../bin/python3
fi
if [ -z "$python_cmd" ] && [ -f ../venv/bin/python3 ]; then
  # We are very probably using a python venv in PyCharm.
  python_cmd=../venv/bin/python3
fi
if [ -z "$python_cmd" ]; then
  echo "Error: You have not specified a python interpreter with --python_cmd."
  exit 1
fi
if [ ! -f "$python_cmd" ]; then
  echo "Error: python interpreter '$python_cmd' does not exist."
  exit 1
fi

if [ -z "$python_path" ]; then
  python_path=.
fi
if [ ! -d "$python_path" ]; then
  echo "Error: python path (PYTHONPATH) directory '$python_path' does not exist."
  exit 1
fi

if [ -z "$organization" ]; then
  echo "Error: organization must be present."
  exit 1
fi

if [ -z "$empty_ricgraph" ]; then
  empty_ricgraph=no
fi
# Convert empty_ricgraph to lowercase.
empty_ricgraph=${empty_ricgraph,,}
if [ "$empty_ricgraph" != "yes" ]; then
  empty_ricgraph=no
fi

# For debugging:
# remaining_args=("$@")
# echo "Python used: '$python_cmd', remaining script args: '${remaining_args[*]}'."

# Convert organization to uppercase.
organization=${organization^^}

echo ""
echo "The following options will be used:"
echo "Python interpreter: '$python_cmd'."
echo "Python path: '$python_path'."
echo "This script is run for organization '$organization'."
echo "Ricgraph is emptied before harvesting: $empty_ricgraph."
echo ""
