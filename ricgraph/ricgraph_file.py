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
# Ricgraph file functions.
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


from os.path import isfile
from pandas import DataFrame, read_csv
from csv import QUOTE_ALL
from json import load, dump
from .ricgraph_harvest import harvest_json


def harvest_json_and_write_to_file(filename: str, url: str, headers: dict, body: dict = None,
                                   max_recs_to_harvest: int = 0, chunksize: int = 0) -> list:
    """Harvest json data and write the data found to a file.
    This data is a list of records in json format. If no records are harvested, nothing is written.

    :param filename: filename of the file to use for writing.
    :param url: URL to harvest.
    :param headers: headers required.
    :param body: the body of a POST request, or '' for a GET request.
    :param max_recs_to_harvest: maximum records to harvest.
    :param chunksize: chunk size to use (i.e. the number of records harvested in one call to 'url').
    :return: list of records in json format, or empty list if nothing found.
    """
    if body is None:
        body = []

    json_data = harvest_json(url=url,
                             headers=headers,
                             body=body,
                             max_recs_to_harvest=max_recs_to_harvest,
                             chunksize=chunksize)
    if len(json_data) == 0:
        return []
    write_json_to_file(json_data=json_data, filename=filename)
    return json_data


def write_json_to_file(json_data: list, filename: str) -> None:
    """Write json data to a file.
    If no records are harvested, nothing is written.

    :param json_data: a list of records in json format.
    :param filename: filename of the file to use for writing.
    :return: None.
    """
    print('Saving json data to ' + filename + '... ', end='', flush=True)
    with open(filename, 'w') as fd:
        dump(obj=json_data, fp=fd, ensure_ascii=False, indent=2)
    print('Done.')
    return


def read_json_from_file(filename: str) -> list:
    """Read json data from a file.

    :param filename: filename of the file to use for writing.
    :return: list of records in json format, or empty list if nothing found.
    """
    if not isfile(path=filename):
        print('read_json_from_file(): Error, file "' + filename + '" does not exist, exiting...')
        exit(1)

    print('Reading json data from ' + filename + '... ', end='', flush=True)
    with open(filename) as fd:
        json_data = load(fp=fd)
    print('Done.')
    if json_data is None:
        return []
    return json_data


def write_dataframe_to_csv(filename: str,
                           df: DataFrame,
                           write_index: bool = False) -> None:
    """Write a datastructure (DataFrame) to file.

    :param filename: csv file to write.
    :param df: dataframe to write.
    :param write_index: whether to write the index of the DataFrame
      as first column to the csv file (True) or not (False).
    :return: None.
    """
    if df is None or df.empty:
        print('write_dataframe_to_csv(): Empty DataFrame, nothing to write, continuing.')
        return

    print('\nwrite_dataframe_to_csv(): Writing to csv file: ' + filename + '... ', end='', flush=True)
    df.to_csv(filename,
              sep=',',
              quotechar='"',
              quoting=QUOTE_ALL,
              encoding='utf-8',
              index=write_index)
    print('Done.')
    return


def read_dataframe_from_csv(filename: str,
                            columns: dict = None,
                            nr_rows: int = None,
                            datatype=str,
                            read_index: bool = False) -> DataFrame:
    """Reads a datastructure (DataFrame) from file

    :param filename: csv file to read.
    :param columns: which columns to read.
    :param nr_rows: how many rows to read (default: all).
    :param datatype: type of (some) columns to read.
    :param read_index: whether to use the first column
      from the csv file (True) or not (False) for index in the DataFrame.
    :return: dataframe read.
    """
    if not isfile(path=filename):
        print('read_dataframe_from_csv(): Error, file "' + filename + '" does not exist, exiting...')
        exit(1)

    # Note the inconsistent type of 'index_col'.
    if read_index:
        index_col = 0
    else:
        index_col = False

    try:
        # Some inputfiles have problems reading in utf-8
        csv_data = read_csv(filename,
                                   sep=',',
                                   index_col=index_col,
                                   usecols=columns,
                                   dtype=datatype,
                                   engine='python',
                                   nrows=nr_rows,
                                   keep_default_na=False,
                                   parse_dates=False,
                                   iterator=False,
                                   quotechar='"',
                                   encoding='utf-8')
    except BaseException:
        print('read_dataframe_from_csv(): error reading in utf-8 format, reading in latin-1 format.')
        csv_data = read_csv(filename,
                                   sep=',',
                                   index_col=index_col,
                                   usecols=columns,
                                   dtype=datatype,
                                   engine='python',
                                   nrows=nr_rows,
                                   keep_default_na=False,
                                   parse_dates=False,
                                   iterator=False,
                                   quotechar='"',
                                   encoding='latin-1')
    return csv_data
