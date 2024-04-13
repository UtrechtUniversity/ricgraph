# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
# 
# Copyright (c) 2023 Rik D.T. Janssen
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
# This file contains example code for Ricgraph.
#
# With this code, you can harvest software from Research Software Directory (RSD).
# You have to set some parameters in ricgraph.ini.
# Also, you can set a number of parameters in the code following the "import" statements below.
#
# Original version Rik D.T. Janssen, December 2022.
# Updated Rik D.T. Janssen, April, October 2023.
#
# ########################################################################
#
# Usage
# harvest_rsd_to_ricgraph.py [options]
#
# Options:
#   --empty_ricgraph <yes|no>
#           'yes': Ricgraph will be emptied before harvesting.
#           'no': Ricgraph will not be emptied before harvesting.
#           If this option is not present, the script will prompt the user
#           what to do.
#   --organization <organization abbreviation>
#           Harvest data from organization <organization abbreviation>.
#           The organization abbreviations are specified in the Ricgraph ini
#           file.
#           If this option is not present, the script will prompt the user
#           what to do.
#
# ########################################################################


import os.path
import sys
import json
import pandas
import numpy
import urllib.request
from typing import Union
import configparser
import ricgraph as rcg


RSD_HARVEST_FILENAME = 'rsd_harvest.json'
RSD_DATA_FILENAME = 'rsd_data.csv'
RSD_ENDPOINT = 'api/v1/organisation'
RSD_FIELDS = 'software(brand_name,slug,concept_doi,' \
             + 'release(mention(doi,doi_registration_date,publication_year)),' \
             + 'contributor(family_names,given_names,orcid))' \
             + '&software.release.mention.order=doi_registration_date.desc'
RSD_HEADERS = {
    'User-Agent': 'Harvesting from RSD'
}
global FULL_RSD_URL
global HARVEST_SOURCE


# ######################################################
# Parsing
# ######################################################

def parse_rsd_software(harvest: list) -> pandas.DataFrame:
    """Parse the harvested software from Research Software Directory.

    :param harvest: the harvest.
    :return: the harvested software in a DataFrame.
    """
    rsd_parse = pandas.DataFrame()
    for software_package in harvest[0]['software']:
        package_name = software_package['brand_name']
        package_url = RSD_URL + '/software/' + software_package['slug']

        # RSD has several DOIs: 'Concept DOI' and 'Version DOI'. The Concept DOI always
        # represents the most recent version, and the Version DOI is specific to a version.
        # We prefer the Concept DOI, and if not present, take the first DOI in the list
        # as the correct one.
        if 'concept_doi' in software_package and software_package['concept_doi'] is not None:
            package_doi = software_package['concept_doi']
            package_doi_type = 'concept DOI'
        else:
            if 'release' not in software_package:
                continue
            release = software_package['release']
            if release is None:
                continue

            if 'mention' not in release:
                continue
            mention = release['mention']
            if len(mention) == 0:
                continue

            # DOIs are sorted on date, most recent first. Not sure what is 'correct' if there are DOIs
            # from the same date. Just take the first.
            first_doi_date = mention[0]
            package_doi = first_doi_date['doi']
            package_doi_type = 'version DOI'

        # Get year of most recent DOI, we assume that is the publication year of the software package.
        publication_year_most_recent_doi = ''
        if 'release' in software_package:
            release = software_package['release']
            if release is not None:
                if 'mention' in release:
                    mention = release['mention']
                    if len(mention) != 0:
                        if 'publication_year' in mention[0]:
                            publication_year_most_recent_doi = str(mention[0]['publication_year'])

        # The following results in names and ORCID's of contributors.
        # In case there are no names, the software will be added anyway to Ricgraph.
        contributor = pandas.json_normalize(software_package, 'contributor')

        if package_doi_type == 'version DOI':
            package_name = package_name + ' (' + package_doi_type + ')'

        contributor.fillna(value=numpy.nan, inplace=True)
        contributor['FULL_NAME'] = contributor['family_names'] + ', ' + contributor['given_names']
        contributor.insert(0, 'package_year', publication_year_most_recent_doi)
        contributor.insert(0, 'package_name', package_name)
        contributor.insert(0, 'package_url', package_url)
        contributor.insert(0, 'package_doi', str(package_doi).lower())
        rsd_parse = pandas.concat([rsd_parse, contributor], ignore_index=True)

    # dropna(how='all'): drop row if all row values contain NaN
    rsd_parse.dropna(axis=0, how='all', inplace=True)
    rsd_parse.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    return rsd_parse


# ######################################################
# Harvesting and parsing
# ######################################################

def rsd_harvest_json_and_write_to_file(filename: str, url: str, headers: dict) -> list:
    """Harvest json data from the Research Software Directory and write the data found to a file.
    This data is a list of records in json format. If no records are harvested, nothing is written.
    We cannot use ricgraph.harvest_json_and_write_to_file() since RSDs json
    does not conform to the standard.
    This is understandable, since at the moment there is no "official, correct" way of harvesting
    RSD yet, that is future work for RSD [December 2022].

    :param filename: filename of the file to use for writing.
    :param url: URL to harvest.
    :param headers: headers required.
    :return: list of records in json format, or empty list if nothing found.
    """
    print('Getting data from ' + url + '...')
    request = urllib.request.Request(url=url, headers=headers)
    response = urllib.request.urlopen(request, timeout=5)
    body = response.read().decode('utf-8')
    json_data = json.loads(body)
    print('Done.')

    if len(json_data) == 0:
        return []

    rcg.write_json_to_file(json_data=json_data,
                           filename=filename)
    return json_data


def harvest_and_parse_software(headers: dict, url: str, harvest_filename: str) -> Union[pandas.DataFrame, None]:
    """Harvest and parse software from Research Software Directory.

    :param headers: headers for RSD.
    :param url: url to RSD.
    :param harvest_filename: filename to write harvest results to.
    :return: the DataFrame harvested, or None if nothing harvested.
    """
    print('Harvesting software packages from ' + HARVEST_SOURCE + '...')
    retval = rsd_harvest_json_and_write_to_file(filename=harvest_filename,
                                                url=url,
                                                headers=headers)
    if len(retval) == 0:
        # Nothing found
        return None

    harvest_data = rcg.read_json_from_file(filename=harvest_filename)
    parse = parse_rsd_software(harvest=harvest_data)

    print('The harvested software packages are:')
    print(parse)
    return parse


# ######################################################
# Parsed results to Ricgraph
# ######################################################

def parsed_software_to_ricgraph(parsed_content: pandas.DataFrame) -> None:
    """Insert the parsed software in Ricgraph.

    :param parsed_content: The records to insert in Ricgraph, if not present yet.
    :return: None.
    """
    timestamp = rcg.datetimestamp()
    print('Inserting software packages from ' + HARVEST_SOURCE + ' in Ricgraph at '
          + timestamp + '...')
    history_event = 'Source: Harvest ' + HARVEST_SOURCE + ' at ' + timestamp + '.'

    person_identifiers = parsed_content[['orcid', 'FULL_NAME']].copy(deep=True)
    person_identifiers.rename(columns={'orcid': 'ORCID'}, inplace=True)
    # dropna(how='all'): drop row if all row values contain NaN
    person_identifiers.dropna(axis=0, how='all', inplace=True)
    person_identifiers.drop_duplicates(keep='first', inplace=True, ignore_index=True)

    print('The following persons from ' + HARVEST_SOURCE + ' will be inserted in Ricgraph:')
    print(person_identifiers)
    rcg.unify_personal_identifiers(personal_identifiers=person_identifiers,
                                   source_event=HARVEST_SOURCE,
                                   history_event=history_event)

    software = parsed_content.copy(deep=True)
    software.dropna(axis=0, how='all', inplace=True)
    software.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    software.rename(columns={'package_doi': 'value1',
                             'package_name': 'comment1',
                             'package_year': 'year1',
                             'package_url': 'url_other1',
                             'orcid': 'value2'}, inplace=True)
    new_software_columns = {'name1': 'DOI',
                            'category1': rcg.ROTYPE_SOFTWARE,
                            'source_event1': HARVEST_SOURCE,
                            'history_event1': history_event,
                            'name2': 'ORCID',
                            'category2': 'person',
                            'source_event2': HARVEST_SOURCE,
                            'history_event2': history_event}
    software = software.assign(**new_software_columns)
    software = software[['name1', 'category1', 'value1', 'comment1', 'year1', 'url_other1',
                         'source_event1', 'history_event1',
                         'name2', 'category2', 'value2',
                         'source_event2', 'history_event2']]

    print('The following software packages from ' + HARVEST_SOURCE + ' will be inserted in Ricgraph:')
    print(software)
    rcg.create_nodepairs_and_edges_df(left_and_right_nodepairs=software)
    print('\nDone at ' + rcg.timestamp() + '.\n')
    return


# ############################################
# ################### main ###################
# ############################################
if not os.path.exists(rcg.RICGRAPH_INI_FILE):
    print('Error, Ricgraph ini file "' + rcg.RICGRAPH_INI_FILE + '" not found, exiting.')
    exit(1)

rcg.print_commandline_arguments(argument_list=sys.argv)

organization = rcg.get_commandline_argument(argument='--organization',
                                            argument_list=sys.argv)
if organization == '':
    print('You need to specify an organization abbreviation. This script will be run for that organization.')
    print('The organization abbreviation you enter will determine which parameters will be read from')
    print('the Ricgraph ini file. If you make a typo, you can run this script again.')
    print('If you enter an empty value, this script will exit.')
    organization = input('For what organization do you want to run this script? ')
    if organization == '':
        print('Exiting.\n')
        exit(1)

config = configparser.ConfigParser()
config.read(rcg.RICGRAPH_INI_FILE)
rsd_url = 'rsd_url'
rsd_organization = 'rsd_organization_' + organization
try:
    RSD_URL = config['RSD_harvesting'][rsd_url]
    RSD_ORGANIZATION = config['RSD_harvesting'][rsd_organization]
    if RSD_URL == '' or RSD_ORGANIZATION == '':
        print('\nRicgraph initialization: error, "'
              + rsd_url + '" or "' + rsd_organization
              + '" empty in Ricgraph ini file, exiting.')
        exit(1)

    FULL_RSD_URL = RSD_URL + '/' + RSD_ENDPOINT + '?slug=eq.' + RSD_ORGANIZATION + '&select=' + RSD_FIELDS
except KeyError:
    print('\nRicgraph initialization: error, "'
          + rsd_url + '" or "' + rsd_organization
          + '" not found in Ricgraph ini file, exiting.')
    exit(1)

HARVEST_SOURCE = 'Research Software Directory-' + organization

print('\nPreparing graph...')
rcg.open_ricgraph()

empty_graph = rcg.get_commandline_argument(argument='--empty_ricgraph',
                                           argument_list=sys.argv)
if empty_graph == '':
    # Empty Ricgraph, choose one of the following.
    # rcg.empty_ricgraph(answer='yes')
    # rcg.empty_ricgraph(answer='no')
    rcg.empty_ricgraph()
else:
    rcg.empty_ricgraph(answer=empty_graph)

rcg.graphdb_nr_accesses_print()

harvest_file = RSD_HARVEST_FILENAME.split('.')[0] \
               + '-' + organization + '.' \
               + RSD_HARVEST_FILENAME.split('.')[1]
data_file = RSD_DATA_FILENAME.split('.')[0] \
            + '-' + organization + '.' \
            + RSD_DATA_FILENAME.split('.')[1]
rsd_data = harvest_and_parse_software(headers=RSD_HEADERS,
                                      url=FULL_RSD_URL,
                                      harvest_filename=harvest_file)
if rsd_data is None or rsd_data.empty:
    print('There are no software packages from ' + HARVEST_SOURCE + ' to harvest.\n')
else:
    rcg.write_dataframe_to_csv(filename=data_file,
                               df=rsd_data)
    parsed_software_to_ricgraph(parsed_content=rsd_data)

rcg.graphdb_nr_accesses_print()
rcg.close_ricgraph()
