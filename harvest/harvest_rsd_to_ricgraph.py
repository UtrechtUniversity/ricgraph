# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
# 
# Copyright (c) 2022 - 2026 Rik D.T. Janssen
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
# Updated Rik D.T. Janssen, April, October 2023, February 2025.
# Updated Rik D.T. Janssen, February 2026.
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


import sys
import numpy
import json
import pandas
import urllib.request
from typing import Union
import ricgraph as rcg

# Set this to True to simulate the harvest. If True, do not harvest, but read it from a file.
RSD_READ_HARVEST_FROM_FILE = False
# RSD_READ_HARVEST_FROM_FILE = True
RSD_HARVEST_FILENAME = 'rsd_harvest.json'

# Set this to True to read data from the csv file. No harvest will be done, this would
# not make sense. If False, a harvest will be done.
# If True, the value of RSD_READ_HARVEST_FROM_FILE does not matter.
RSD_READ_DATA_FROM_FILE = False
# RSD_READ_DATA_FROM_FILE = True
RSD_DATA_FILENAME = 'rsd_data.csv'

RSD_ENDPOINT = 'api/v1/organisation'
RSD_FIELDS = 'software(brand_name,slug,concept_doi,' \
             + 'release(mention(doi,doi_registration_date,publication_year)),' \
             + 'contributor(family_names,given_names,orcid,affiliation))' \
             + '&software.release.mention.order=doi_registration_date.desc'
RSD_HEADERS = {
    'User-Agent': 'Harvesting from RSD'
}


# ######################################################
# Parsing
# ######################################################

def restructure_parse(df: pandas.DataFrame) -> pandas.DataFrame:
    """Restructure the parsed data from the source system.
    This means: convert all field names found in the source system
    to recognized Ricgraph fields (e.g. replace 'doi' with 'DOI'),
    and make sure that every column that is expected further down
    this code is present (i.e. insert an empty column if needed).
    No processing of data in columns is done.

    :param df: dataframe with identifiers.
    :return: Result of action described above.
    """
    df_mod = df.copy(deep=True)
    df_mod.rename(columns={'package_doi': 'DOI',
                           'orcid': 'ORCID',
                           'affiliation': 'ORGANIZATION_NAME',
                           'package_name': 'TITLE',
                           'package_year': 'YEAR',
                           'package_url': 'URL_OTHER'
                           }, inplace=True)
    df_mod['TYPE'] = rcg.ROTYPE_SOFTWARE
    return df_mod


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
        # 'Contributor' contains a number of fields. We add them in one go.
        # Now it has orcid, affiliation, given_names, and family_names.
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

    rsd_parse = restructure_parse(df=rsd_parse)
    return rcg.normalize_identifiers(df=rsd_parse)


# ######################################################
# Harvesting and parsing
# ######################################################

def rsd_harvest_json_and_write_to_file(filename: str, url: str, headers: dict) -> list:
    """Harvest JSON data from the Research Software Directory and write the data found to a file.
    This data is a list of records in JSON format. If no records are harvested, nothing is written.
    We cannot use ricgraph.harvest_json_and_write_to_file() since RSDs JSON
    does not conform to the standard.
    This is understandable, since at the moment there is no "official, correct" way of harvesting
    RSD yet, that is future work for RSD [December 2022].

    :param filename: filename of the file to use for writing.
    :param url: URL to harvest.
    :param headers: headers required.
    :return: list of records in JSON format, or empty list if nothing found.
    """
    print('Getting data from ' + url + '...')
    request = urllib.request.Request(url=url, headers=headers)
    response = urllib.request.urlopen(request, timeout=5)
    body = response.read().decode('utf-8')
    json_data = json.loads(body)
    print('Done.')

    if len(json_data) == 0:
        return []

    rcg.write_json_to_file(filename=filename,
                           json_data=json_data)
    return json_data


def harvest_and_parse_software(headers: dict, url: str, harvest_filename: str) -> Union[pandas.DataFrame, None]:
    """Harvest and parse software from Research Software Directory.

    :param headers: headers for RSD.
    :param url: url to RSD.
    :param harvest_filename: filename to write harvest results to.
    :return: the DataFrame harvested, or None if nothing harvested.
    """
    print('Harvesting software packages from ' + HARVEST_SOURCE + '...')
    if not RSD_READ_HARVEST_FROM_FILE:
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
    person_identifiers = parsed_content[['ORCID', 'FULL_NAME']].copy(deep=True)
    rcg.create_parsed_persons_in_ricgraph(person_identifiers=person_identifiers,
                                          harvest_source=HARVEST_SOURCE)

    software = parsed_content[['ORCID', 'DOI', 'TITLE', 'YEAR', 'TYPE', 'URL_OTHER']].copy(deep=True)
    rcg.create_parsed_dois_in_ricgraph(resouts=software, harvest_source=HARVEST_SOURCE)

    # ####
    # As of the current implementation of RSD (2023-2025), RSD has organizations in two
    # different places:
    # 1. As part of 'contributor', i.e., part of a person.
    #    Then its name is 'affiliation'. This is a free text field in RSD.
    #    A person has one 'affiliation' field.
    # 2. As part of the software item.
    #    This is a field where you can enter a ROR, an organization name that is checked
    #    by RSD, or a free field.
    #    A software item can have 1 or more organizations.
    # In Ricgraph, I use organizations of persons, so (1) is implemented below.
    # This does not allow for more than one organization for a person. Unless someone
    # decides to enter multiple organizations in the same field, which is unexpected.
    # I cannot do (2), since I would not know which organization belongs to which person.
    organizations = parsed_content[['ORCID', 'ORGANIZATION_NAME']].copy(deep=True)
    rcg.create_parsed_organizations_in_ricgraph(organizations=organizations, harvest_source=HARVEST_SOURCE)
    return


# ############################################
# ################### main ###################
# ############################################
rcg.print_commandline_arguments(argument_list=sys.argv)
if (organization := rcg.get_commandline_argument_organization(argument_list=sys.argv)) == '':
    print('Exiting.\n')
    exit(1)

rsd_organization = 'rsd_organization_' + organization
RSD_URL = rcg.get_configfile_key(section='RSD_harvesting', key='rsd_url')
RSD_ORGANIZATION = rcg.get_configfile_key(section='RSD_harvesting', key=rsd_organization)
if RSD_URL == '' or RSD_ORGANIZATION == '':
    print('\nRicgraph initialization: error, "rsd_url" or "' + rsd_organization + '"')
    print('  not existing or empty in Ricgraph ini file, exiting.')
    exit(1)

FULL_RSD_URL = RSD_URL + '/' + RSD_ENDPOINT + '?slug=eq.' + RSD_ORGANIZATION + '&select=' + RSD_FIELDS
HARVEST_SOURCE = 'Research Software Directory-' + organization

print('\nPreparing graph...')
rcg.open_ricgraph()

empty_graph = rcg.get_commandline_argument_empty_ricgraph(argument_list=sys.argv)
if empty_graph == 'yes' or empty_graph == 'no':
    rcg.empty_ricgraph(answer=empty_graph)
else:
    print('Exiting.\n')
    exit(1)

rcg.graphdb_nr_accesses_print()
print(rcg.nodes_cache_key_id_type_size() + '\n')

data_file = RSD_DATA_FILENAME.split('.')[0] \
            + '-' + organization + '.' \
            + RSD_DATA_FILENAME.split('.')[1]
if RSD_READ_DATA_FROM_FILE:
    error_message = 'There are no software packages from ' + HARVEST_SOURCE + ' to read from file ' + data_file + '.\n'
    print('Reading software packages from ' + HARVEST_SOURCE + ' from file ' + data_file + '.')
else:
    error_message = 'There are no software packages from ' + HARVEST_SOURCE + ' to harvest.\n'
    print('Harvesting software packages from ' + HARVEST_SOURCE + '.')
    harvest_file = RSD_HARVEST_FILENAME.split('.')[0] \
                   + '-' + organization + '.' \
                   + RSD_HARVEST_FILENAME.split('.')[1]
    rsd_data = harvest_and_parse_software(headers=RSD_HEADERS,
                                          url=FULL_RSD_URL,
                                          harvest_filename=harvest_file)
    rcg.write_dataframe_to_csv(filename=data_file, df=rsd_data)

rsd_data = rcg.read_dataframe_from_csv(filename=data_file, datatype=str)
if rsd_data is None or rsd_data.empty:
    print(error_message)
else:
    parsed_software_to_ricgraph(parsed_content=rsd_data)

rcg.graphdb_nr_accesses_print()
print(rcg.nodes_cache_key_id_type_size() + '\n')
rcg.close_ricgraph()
