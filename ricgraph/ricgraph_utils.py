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
# Updated Rik D.T. Janssen, January to June, October 2025.
#
# ########################################################################


from os import path
from sys import prefix
from re import sub
from numpy import maximum
from pandas import DataFrame
from typing import Union
from ast import literal_eval
from random import choice
from string import ascii_lowercase
from datetime import datetime
from uuid import uuid4
from collections import defaultdict
from configparser import ConfigParser
from unidecode import unidecode
from .ricgraph_constants import (RICGRAPH_INI_FILENAME,
                                 RICGRAPH_KEY_SEPARATOR, RICGRAPH_KEY_SEPARATOR_REPLACEMENT,
                                 RICGRAPH_VALUE_SEPARATOR, RICGRAPH_VALUE_SEPARATOR_REPLACEMENT,
                                 MAX_ORG_ABBREVIATION_LENGTH)


def get_ricgraph_ini_file() -> str:
    """Get the location of the ricgraph ini file.

    :return: the location of the ini file.
    """
    # Try to find RICGRAPH_INI_FILENAME in the root of the virtual environment.
    ricgraph_ini_path = prefix
    ricgraph_ini = path.join(ricgraph_ini_path, RICGRAPH_INI_FILENAME)
    if path.exists(ricgraph_ini):
        return ricgraph_ini

    # Try to find RICGRAPH_INI_FILENAME in the parent directory of the venv,
    # which may happen when using a Python IDE.
    ricgraph_ini_path_parent = path.dirname(ricgraph_ini_path)
    ricgraph_ini = path.join(ricgraph_ini_path_parent, RICGRAPH_INI_FILENAME)
    if path.exists(ricgraph_ini):
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
        return str(uuid4())

    # This will generate a pseudo random string.
    value = ''.join(choice(ascii_lowercase) for _ in range(length))
    return value


def sanitize_string(to_sanitize: str) -> str:
    """Replace any character that is a non-ASCII letter or digit with '_'.
    ASCII characters will be converted to lower case.

    :param to_sanitize: the string to sanitize.
    :return: result.
    """
    result = to_sanitize.lower()
    result = sub(pattern=r'[^a-z0-9]', repl='_', string=result)
    return result


def serialize_value(value: str) -> bytes:
    """Serialize a value (convert to bytes).

    :param value: the value.
    :return: its serialized value.
    """
    return value.encode(encoding='utf-8')


def deserialize_value(serialized: bytes) -> str:
    """Deserialize a value (convert back from bytes).

    :param serialized: the serialized value.
    :return: its deserialized value.
    """
    return serialized.decode(encoding='utf-8')


def make_dataframe_square_symmetric(df: DataFrame) -> Union[DataFrame, None]:
    """Ensure the DataFrame is square by adding missing rows/columns
    filled with zeros. After that, make it symmetric.

    :param df: the DataFrame.
    :return: the resulting DataFrame.
    """
    if df is None or df.empty:
        print('make_df_square_symmetric(): Error, DataFrame is empty.')
        return None

    all_orgs = list(set(df.index).union(df.columns))
    df = df.reindex(index=all_orgs, columns=all_orgs, fill_value=0)

    # Make it a symmetric matrix. Since collaborations are symmetric,
    # we use the element wise maximum, using np.maximum().
    df_symmetric = df.combine(other=df.T, func=maximum)

    return df_symmetric


def combine_dataframes(df1: DataFrame, df2: DataFrame) -> Union[DataFrame, None]:
    """Combines two DataFrames with additive overlapping values
    and union of indices/columns.

    :param df1: first DataFrame.
    :param df2: second DataFrame.
    :return: combined DataFrame.
    """
    if (df1 is None or df1.empty) and (df2 is None or df2.empty):
        # Both DataFrames are emtpy.
        return None
    if df1 is None or df1.empty:
        # DataFrame 1 is empty.
        return df2.copy(deep=True)
    if df2 is None or df2.empty:
        # DataFrame 2 is empty.
        return df1.copy(deep=True)

    # Note that the top left cell contains the research_result_category/ies
    # that were used to get the result stored in the DataFrame.
    # The new DataFrame should have their combined values.
    index_name1 = str(df1.index.name) if df1.index.name is not None else ''
    index_name2 = str(df2.index.name) if df2.index.name is not None else ''
    df1_research_result_category = literal_eval(node_or_string=index_name1)
    df2_research_result_category = literal_eval(node_or_string=index_name2)
    df_combined_research_result_category = list(set(df1_research_result_category).union(set(df2_research_result_category)))
    df_combined_research_result_category.sort(key=lambda s: s.lower())
    df_combined = df1.copy(deep=True)
    df_combined = df_combined.add(df2, fill_value=0).fillna(0).astype(int)
    df_combined.index.name = str(df_combined_research_result_category)
    return df_combined


def convert_cypher_recordslist_to_nodeslist(records_list:list) -> list:
    """Convert a Cypher list with Records to a list of Nodes.
    This is necessary since cypher_result, _, _ = graph.execute_query()
    returns a list of Records, and most of the time I need a list of Nodes.
    Note that the nodes should have name 'node', so do something like
    'RETURN personroot AS node' in your Cypher query.

    :param records_list: the list of Records.
    :return: the list of Nodes, or [] if the list of Records is empty.
    """
    if len(records_list) == 0:
        return []

    if not 'node' in records_list[0].keys():
        print('convert_cypher_recordslist_to_nodeslist(): Error. The elements in the')
        print('list of Records do not have name "node". They should. Exiting...')
        exit(1)

    nodes_list = [record['node'] for record in records_list]
    return nodes_list


def convert_nodeslist_to_dataframe(nodes_list: list,
                                   columns_and_order: list = None) -> Union[None, DataFrame]:
    """Convert a list of RicgraphNode nodes to a DataFrame,
    with selected columns in an order given.

    :param nodes_list: the list of nodes.
    :param columns_and_order: only return these columns, and in the order given.
    :return: the DataFrame, or None if empty.
    """
    if len(nodes_list) == 0:
        return None
    if columns_and_order is None:
        print('convert_nodeslist_to_dataframe(): Warning, columns_and_order not specified, continuing...')
        return None

    nodes_dict = [dict(node) for node in nodes_list]
    result = DataFrame(data=nodes_dict)
    # Make sure we select only columns that exist.
    present_columns = [col for col in columns_and_order if col in result.columns]
    result = result[present_columns]
    if result is None or result.empty:
        return None
    result.set_index(keys='name', inplace=True)
    return result


def extract_organization_abbreviation(org_name: str) -> str:
    """This function extracts the organization abbreviation from an organization
    name. It is assumed that the organization name has an organization abbreviation,
    it should be the first 2 or 3 characters.

    :param org_name: the organization name.
    :return: uppercase version of the organization abbreviation.
    """
    org_abbr = org_name[:MAX_ORG_ABBREVIATION_LENGTH]
    org_abbr = org_abbr.rstrip()
    return org_abbr.upper()


def construct_extended_org_name(org_name: str, org_abbr: str) -> str:
    """Construct the extended organization name.
    This is done by appending the organization abbreviation and the
    organization name.

    :param org_name: the organization name.
    :param org_abbr: the organization abbreviation.
    :return: the combination of both.
    """
    return org_abbr.upper() + ' ' + org_name


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
    """Create a multidimensional dict.
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


def get_commandline_argument_filename(argument_list: list) -> str:
    """Get the value of a command line argument '--filename'.
    Prompt if no argument is given.

    :param argument_list: the argument list.
    :return: 'yes' or 'no', the answer whether to harvest projects,
      or '' if no answer is given.
    """
    answer = get_commandline_argument(argument='--filename',
                                      argument_list=argument_list)
    if answer == '':
        answer = input('Please specify a filename: ')
        if answer == '':
            return ''

    answer = answer.lower()
    return answer


def get_configfile_key(section: str, key: str) -> str:
    """Get the value of a key in the Ricgraph config file.

    :param section: the section where the key is to be read from.
    :param key: the name of the key.
    :return: the value of the key (can be ''), or '' if absent.
    """
    config = ConfigParser(inline_comment_prefixes='#')
    config.read(get_ricgraph_ini_file())
    try:
        value = config[section][key]
    except KeyError:
        return ''

    return value


def get_configfile_key_organizations_with_hierarchies() -> Union[DataFrame, None]:
    """Get the value of the key 'organizations_with_hierarchies'
    in the Ricgraph config file.

    :return: the value of the key as a DataFrame, or None if absent.
    """
    multi_line_str = get_configfile_key(section='Organization',
                                        key='organizations_with_hierarchies')
    if multi_line_str == '':
        return None

    # Split the multiline string into lines and strip spaces
    lines = multi_line_str.strip().splitlines()

    # Join lines with commas and wrap as a list string
    list_str = "[" + ",".join(line.strip() for line in lines) + "]"

    orgs_with_hierarchies_list = literal_eval(list_str)
    if len(orgs_with_hierarchies_list) <= 1:
        # The first element of the list is the header, so if len <= 1
        # then there is still no data.
        return None
    else:
        headers = orgs_with_hierarchies_list[0]
        rows = orgs_with_hierarchies_list[1:]
        orgs_with_hierarchies = DataFrame(data=rows, columns=headers)
        orgs_with_hierarchies['org_abbreviation'] = orgs_with_hierarchies['org_abbreviation'].str.upper()
        orgs_with_hierarchies['org_fullname'] = orgs_with_hierarchies['org_abbreviation'] + ' ' + orgs_with_hierarchies['org_name']
        orgs_with_hierarchies = orgs_with_hierarchies.drop(columns=['org_name'])

    return orgs_with_hierarchies


def get_configfile_key_graphdb_parameters() -> tuple[str, str, str, str, str]:
    """Get the value of multiple keys in the Ricgraph config file
    that relate to the graph database.

    :return: the value of the graph database parameters, as a python tuple.
    """
    graphdb = get_configfile_key(section='GraphDB', key='graphdb')
    graphdb_hostname = get_configfile_key(section='GraphDB', key='graphdb_hostname')
    graphdb_databasename = get_configfile_key(section='GraphDB', key='graphdb_databasename')
    graphdb_user = get_configfile_key(section='GraphDB', key='graphdb_user')
    graphdb_password = get_configfile_key(section='GraphDB', key='graphdb_password')
    graphdb_scheme = get_configfile_key(section='GraphDB', key='graphdb_scheme')
    graphdb_port = get_configfile_key(section='GraphDB', key='graphdb_port')
    if graphdb == '' or graphdb_hostname == '' or graphdb_databasename == '' \
            or graphdb_user == '' or graphdb_password == '' \
            or graphdb_scheme == '' or graphdb_port == '':
        print('Ricgraph initialization: error, one or more of the GraphDB parameters')
        print('  not existing or empty in Ricgraph ini')
        print('  file "' + get_ricgraph_ini_file() + '", exiting.')
        exit(1)

    graphdb_url = '{scheme}://{hostname}:{port}'.format(scheme=graphdb_scheme,
                                                         hostname=graphdb_hostname,
                                                         port=graphdb_port)
    return graphdb, graphdb_url, graphdb_databasename, graphdb_user, graphdb_password


def get_configfile_key_memcached_parameters() -> tuple[bool, str, int]:
    """Get the value of multiple keys in the Ricgraph config file
    that relate to the Memcached cache.

    :return: the value of the Memcached parameters, as a python tuple.
    """
    memcached_to_be_used_str = get_configfile_key(section='Memcached',
                                                  key='ricgraph_explorer_uses_memcached')
    memcached_host = get_configfile_key(section='Memcached',
                                         key='memcached_host')
    memcached_port_str = get_configfile_key(section='Memcached',
                                        key='memcached_port')

    memcached_to_be_used = False
    if memcached_to_be_used_str == 'True':
        memcached_to_be_used = True
    memcached_port = int(memcached_port_str)

    return memcached_to_be_used, memcached_host, memcached_port
