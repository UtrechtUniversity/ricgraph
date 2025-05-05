# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
#
# Copyright (c) 2023 - 2025 Rik D.T. Janssen
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
# General Ricgraph functions.
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, December 2022.
# Updated Rik D.T. Janssen, February, March, September to December 2023.
# Updated Rik D.T. Janssen, February to June, September to December  2024.
# Updated Rik D.T. Janssen, January to June 2025.
#
# ########################################################################


import os
import sys
import random
import string
from datetime import datetime
import uuid
from collections import defaultdict
import configparser
from unidecode import unidecode
from .ricgraph_constants import (RICGRAPH_INI_FILENAME,
                                 RICGRAPH_KEY_SEPARATOR, RICGRAPH_KEY_SEPARATOR_REPLACEMENT,
                                 RICGRAPH_VALUE_SEPARATOR, RICGRAPH_VALUE_SEPARATOR_REPLACEMENT)


def get_ricgraph_ini_file() -> str:
    """Get the location of the ricgraph ini file.

    :return: the location of the ini file.
    """
    # Try to find RICGRAPH_INI_FILENAME in the root of the virtual environment.
    ricgraph_ini_path = sys.prefix
    ricgraph_ini = os.path.join(ricgraph_ini_path, RICGRAPH_INI_FILENAME)
    if os.path.exists(ricgraph_ini):
        return ricgraph_ini

    # Try to find RICGRAPH_INI_FILENAME in the parent directory of the venv,
    # which may happen when using a Python IDE.
    ricgraph_ini_path_parent = os.path.dirname(ricgraph_ini_path)
    ricgraph_ini = os.path.join(ricgraph_ini_path_parent, RICGRAPH_INI_FILENAME)
    if os.path.exists(ricgraph_ini):
        return ricgraph_ini

    print('Ricgraph initialization: error, Ricgraph ini file "' + RICGRAPH_INI_FILENAME + '" not found in')
    print('   directory "' + ricgraph_ini_path + '", nor in')
    print('   directory "' + ricgraph_ini_path_parent + '", exiting.')
    exit(1)


def timestamp(seconds: bool = False) -> str:
    """Get a timestamp only consisting of a time.

    :param seconds: If True, also show seconds in the timestamp.
    :return: the timestamp.
    """
    now = datetime.now()
    if seconds:
        time_stamp = now.strftime("%H:%M:%S")
    else:
        time_stamp = now.strftime("%H:%M")
    return time_stamp


def datetimestamp(seconds: bool = False) -> str:
    """Get a timestamp consisting of a date and a time.

    :param seconds: If True, also show seconds in the timestamp.
    :return: the timestamp.
    """
    now = datetime.now()
    if seconds:
        datetime_stamp = now.strftime("%Y-%m-%d %H:%M:%S")
    else:
        datetime_stamp = now.strftime("%Y-%m-%d %H:%M")
    return datetime_stamp


def convert_string_to_ascii(value: str = '') -> str:
    """Convert all accented etc. characters to their ASCII equivalent.
    We use Unidecode from https://github.com/avian2/unidecode.

    :return: the ASCII equivalent.
    """
    asc = unidecode(string=value)
    return asc


def create_unique_string(length: int = 0) -> str:
    """Create a (pseudo) unique string of characters.
    Only if you don't specify 'length' or give it value 0,
    the string will really be unique. Otherwise, it will
    be pseudo unique.

    :param length: 0 or empty for unique string, otherwise length
      of string to create.
    :return: unique string.
    """
    if length == 0:
        # UUID4 is randomly generated and guaranteed to be unique.
        # The probability to find a duplicate within 103 trillion
        # version-4 UUIDs is one in a billion.
        # https://en.wikipedia.org/wiki/Universally_unique_identifier.
        return str(uuid.uuid4())

    # This will generate a pseudo random string.
    value = ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
    return value


def create_ricgraph_key(name: str, value: str) -> str:
    """Create a key for a node.
    This function generates a composite key for a node in a graph.

    :param name: name of the node.
    :param value: value of the node.
    :return: key generated for the node.
    """
    # Check and correct for occurrences of RICGRAPH_KEY_SEPARATOR.
    name = name.replace(RICGRAPH_KEY_SEPARATOR, RICGRAPH_KEY_SEPARATOR_REPLACEMENT)
    value = value.replace(RICGRAPH_KEY_SEPARATOR, RICGRAPH_KEY_SEPARATOR_REPLACEMENT)

    return value.lower() + RICGRAPH_KEY_SEPARATOR + name.lower()


def get_namepart_from_ricgraph_key(key: str) -> str:
    """Get the 'name' part from the composite key in a node.

    :param key: key of the node.
    :return: name part of key for the node, or '' on error.
    """
    key_list = key.split(sep=RICGRAPH_KEY_SEPARATOR)
    if len(key_list) != 2:
        return ''
    return key_list[1]


def get_valuepart_from_ricgraph_key(key: str) -> str:
    """Get the 'value' part from the composite key in a node.

    :param key: key of the node.
    :return: value part of key for the node, or '' on error.
    """
    key_list = key.split(sep=RICGRAPH_KEY_SEPARATOR)
    if len(key_list) != 2:
        return ''
    return key_list[0]


def create_ricgraph_value(value: str, additional: str) -> str:
    """Sometimes, we may want to have non-unique nodes.
    E.g. the same name may apply to different persons,
    so FULL_NAME is not unique.
    However, for Ricgraph every node needs to be unique,
    so we append a certain value to it, 'additional'.
    Together they need to be unique.

    :param value: value.
    :param additional: an additional value to make this node unique.
    :return: the concatenation.
    """
    # Check and correct for occurrences of RICGRAPH_KEY_SEPARATOR.
    value = value.replace(RICGRAPH_VALUE_SEPARATOR, RICGRAPH_VALUE_SEPARATOR_REPLACEMENT)
    additional = additional.replace(RICGRAPH_VALUE_SEPARATOR, RICGRAPH_VALUE_SEPARATOR_REPLACEMENT)

    # Note that we don't do a .lower(), since we want the correctly spelled name.
    return value + RICGRAPH_VALUE_SEPARATOR + additional.lower()


def get_valuepart_from_ricgraph_value(key: str) -> str:
    """Get the 'value' part from the composite key in a node.

    :param key: key of the node.
    :return: the value part, or '' on error.
    """
    key_list = key.split(sep=RICGRAPH_VALUE_SEPARATOR)
    if len(key_list) != 2:
        return ''
    return key_list[0]


def get_additionalpart_from_ricgraph_value(key: str) -> str:
    """Get the 'value' part from the composite key in a node.

    :param key: key of the node.
    :return: the additional part, or '' on error.
    """
    key_list = key.split(sep=RICGRAPH_VALUE_SEPARATOR)
    if len(key_list) != 2:
        return ''
    return key_list[1]


def create_multidimensional_dict(dimension: int, dict_type):
    """Create a multimensional dict.
    Non-existing keys will be added automatically.
    From https://stackoverflow.com/questions/29348345/declaring-a-multi-dimensional-dictionary-in-python,
    the second answer.

    Example use:
    new_dict = create_multidimensional_dict(2, int)
    new_dict['key1']['key2'] += 5

    :param dimension: dimension of the dict.
    :param dict_type: type of the dict.
    :return: the dict.
    """
    if dimension == 0:
        return None
    if dimension == 1:
        return defaultdict(dict_type)
    else:
        return defaultdict(lambda: create_multidimensional_dict(dimension=dimension - 1,
                                                                dict_type=dict_type))


def print_commandline_arguments(argument_list: list) -> None:
    """Print the script name and all command line arguments.

    :param argument_list: the argument list.
    :return: None.
    """
    if len(argument_list) == 0:
        print('print_commandline_arguments(): Error, empty argument_list passed, exiting.')
        exit(1)

    print('\nScript name: ' + argument_list[0])
    if len(argument_list) == 1:
        print('Command line arguments: [none]')
    else:
        print('Command line arguments: '
              + ' '.join([str(arg) for arg in argument_list[1:]])
              + '\n')
    return


def get_commandline_argument(argument: str, argument_list: list) -> str:
    """Get the value of a command line argument

    :param argument: the command line argument name.
    :param argument_list: the argument list.
    :return: the value that belongs to 'argument'.
    """
    length = len(argument_list)
    if length == 0:
        print('get_commandline_argument(): Error, empty argument_list passed, exiting.')
        exit(1)

    if str(argument) == '':
        # No argument passed.
        return ''

    if length == 1:
        # The argument list contains the script name only.
        return ''

    for i in range(1, length - 1):
        if str(argument_list[i]) == str(argument):
            if i + 1 <= length:
                # Only get the next index if we are still in the array bounds.
                return str(argument_list[i + 1])
    return ''


def get_commandline_argument_organization(argument_list: list) -> str:
    """Get the value of a command line argument '--organization'.
    Prompt if no argument is given.

    :param argument_list: the argument list.
    :return: the organization, or '' if no answer is given.
    """
    answer = get_commandline_argument(argument='--organization',
                                      argument_list=argument_list)
    if answer == '':
        print('\nYou need to specify an organization abbreviation.')
        print('This script will be run for that organization.')
        print('The organization abbreviation you enter will determine')
        print('which parameters will be read from the Ricgraph ini file')
        print('"' + get_ricgraph_ini_file() + '".')
        print('If you make a typo, you can run this script again.')
        print('If you enter an empty value, this script will exit.')
        answer = input('For what organization do you want to run this script? ')
        if answer == '':
            return ''

    answer = answer.upper()
    return answer


def get_commandline_argument_empty_ricgraph(argument_list: list) -> str:
    """Get the value of a command line argument '--empty_ricgraph'.
    Prompt if no argument is given.

    :param argument_list: the argument list.
    :return: 'yes' or 'no', the answer whether to empty Ricgraph,
      or '' if no answer is given.
    """
    answer = get_commandline_argument(argument='--empty_ricgraph',
                                      argument_list=argument_list)
    if answer == '':
        print('\nDo you want to empty Ricgraph? You have the following options:')
        print('- "yes": Ricgraph will be emptied.')
        print('- "no": Ricgraph will not be emptied.')
        print('- any other answer: Ricgraph will not be emptied,')
        print('  execution of this script will abort.')
        answer = input('Please make a choice: ')
        if answer == '':
            return ''

    answer = answer.lower()
    if answer != 'yes' and answer != 'no':
        return ''
    return answer


def get_commandline_argument_harvest_projects(argument_list: list) -> str:
    """Get the value of a command line argument '--harvest_projects'.
    Prompt if no argument is given.

    :param argument_list: the argument list.
    :return: 'yes' or 'no', the answer whether to harvest projects,
      or '' if no answer is given.
    """
    answer = get_commandline_argument(argument='--harvest_projects',
                                      argument_list=argument_list)
    if answer == '':
        print('\nYou can specify whether you want to harvest projects.')
        print('Only if enter "yes", this script will harvest projects.')
        answer = input('Do you want to harvest projects? ')
        if answer == '':
            return ''

    answer = answer.lower()
    if answer != 'yes' and answer != 'no':
        return ''
    return answer


def get_configfile_key(section: str, key: str) -> str:
    """Get the value of a key in the Ricgraph config file.

    :param section: the section where the key is to be read from.
    :param key: the name of the key.
    :return: the value of the key (can be ''), or '' if absent.
    """
    config = configparser.ConfigParser()
    config.read(get_ricgraph_ini_file())
    try:
        value = config[section][key]
    except KeyError:
        return ''

    return value
