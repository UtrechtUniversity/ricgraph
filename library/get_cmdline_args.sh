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
# This script parses command line parameters for several scripts,
# a.o. the scripts in directory multiple_harvest_scripts.
#
# Usage:
# ./get_cmdline_args.sh [options]
# 
# Options:
#         -o, --organization [organization]
#                 The organization to harvest. Specify the organization
#                 abbreviation.
#         -e, --empty_ricgraph [yes|no]
#                 Whether to empty Ricgraph before harvesting the
#                 first organization. If absent, Ricgraph will not be emptied.
#         -c, --python_cmd [python interpreter]
#                 The python interpreter to use. If absent, and a python
#                 virtual environment is used, that interpreter is used.
#         -p, --python_path [python path]
#                 The value for PYTHONPATH, the path to python libraries.
#                 If absent, the current directory is used.
#         -h, --help
#                 Show this help text.
# 
# This script can be called using "source get_cmdline_args.sh".
# It will always return:
# - $organization: the organization for which to harvest.
# - $empty_ricgraph: whether to empty Ricgraph before harvesting
#   		     the first source.
# - $python_cmd: the python interpreter to be used.
# - $python_path: the PYTHONPATH to be used for the python interpreter.
#
# Original version Rik D.T. Janssen, April 2025.
#
# ########################################################################

usage="Usage:\n"
usage+="$0 [options]\n\nOptions:"
usage+="\n\t-o, --organization [organization]"
usage+="\n\t\tThe organization to harvest. Specify the organization"
usage+="\n\t\tabbreviation."
usage+="\n\t-e, --empty_ricgraph [yes|no]"
usage+="\n\t\tWhether to empty Ricgraph before harvesting the"
usage+="\n\t\tfirst organization. If absent, Ricgraph will not be emptied."
usage+="\n\t-c, --python_cmd [python interpreter]"
usage+="\n\t\tThe python interpreter to use. If absent, and a python"
usage+="\n\t\tvirtual environment is used, that interpreter is used."
usage+="\n\t-p, --python_path [python path]"
usage+="\n\t\tThe value for PYTHONPATH, the path to python libraries."
usage+="\n\t\tIf absent, the current directory is used."
usage+="\n\t-h, --help"
usage+="\n\t\tShow this help text."
usage+="\n"

if [ $# -eq 0 ]; then
  echo -e "$usage"
  exit 1
fi

# the ':' after a parameter tells us it needs a parameter value.
args=$(getopt --options o:e:c:p:h --longoptions organization:,empty_ricgraph:,python_cmd:,python_path:,help -n "$0" -- "$@")
exit_code=$?
if [ "$exit_code" != "0" ] ; then
  # 'getopt' went wrong, e.g. it got an invalid option.
  echo "Exiting."
  exit 1
fi
eval set -- "$args"
while true; do
  case "$1" in
  -o|--organization) organization=$2; shift 2;;
  -e|--empty_ricgraph) empty_ricgraph=$2; shift 2;;
  -c|--python_cmd) python_cmd=$2; shift 2;;
  -p|--python_path) python_path=$2; shift 2;;
  -h|--help) echo -e "$usage"; exit 1;;
  --) shift; break;;
  *) echo "Invalid option: $1"; exit 1;;
  esac
done

# Process $organization.
if [ -z "$organization" ]; then
  echo "Error: organization must be present."
  exit 1
fi
# Convert organization to uppercase.
organization=${organization^^}

# Process $empty_ricgrapy.
if [ -z "$empty_ricgraph" ]; then
  empty_ricgraph=no
fi
# Convert empty_ricgraph to lowercase.
empty_ricgraph=${empty_ricgraph,,}
if [ "$empty_ricgraph" != "yes" ]; then
  empty_ricgraph=no
fi

# Process $python_cmd.
if [ ! -z "$python_cmd" ]; then
  path_python=$(which $python_cmd 2>/dev/null)
  if [ -z "$path_python" ]; then
    echo "Error: cannot find python '$python_cmd' in '$PATH'."
    exit 1
  fi
  python_cmd=$path_python
fi
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

# Process $python_path.
if [ -z "$python_path" ]; then
  python_path=.
fi
if [ ! -d "$python_path" ]; then
  echo "Error: python path (PYTHONPATH) directory '$python_path' does not exist."
  exit 1
fi
# Do not remove or modify the next line, file Makefile may modify it.
# ## ### #### #####
# Do not remove or modify the line above.

# For debugging:
# remaining_args=("$@")
# echo "Python used: '$python_cmd', remaining script args: '${remaining_args[*]}'."

echo ""
echo "The following parameter values will be used:"
echo "Organization: '$organization'."
echo "Ricgraph is emptied before harvesting: $empty_ricgraph."
echo "Python interpreter: '$python_cmd'."
echo "Python path: '$python_path'."
echo ""
