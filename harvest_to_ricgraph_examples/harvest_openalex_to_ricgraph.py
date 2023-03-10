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
# With this code, you can harvest persons and research outputs from OpenAlex.
# You have to set some parameters in ricgraph.ini.
# Also, you can set a number of parameters in the code following the "import" statements below.
#
# Original version Rik D.T. Janssen, March 2023.
#
# ########################################################################


import os.path
import re
import pandas
from datetime import datetime
from typing import Union
import configparser
import pathlib
import ricgraph as rcg


# ######################################################
# General parameters for harvesting from OpenAlex.
# ######################################################
OPENALEX_CHUNKSIZE = 150
OPENALEX_HEADERS = {'Accept': 'application/json'
                    # The following will be read in __main__
                    # 'User-Agent': 'mailto:email@somewhere.com'
                    }

global OPENALEX_URL
global ORGANIZATION_ROR
global ORGANIZATION_NAME

# ######################################################
# Parameters for harvesting persons and research outputs from OpenAlex
# ######################################################
OPENALEX_ENDPOINT = 'works'
OPENALEX_HARVEST_FROM_FILE = False
OPENALEX_HARVEST_FILENAME = 'openalex_harvest.json'
OPENALEX_DATA_FILENAME = 'openalex_data.csv'
OPENALEX_RESOUT_YEARS = ['2020', '2021', '2022', '2023']
# This number is the max recs to harvest per year, not total
OPENALEX_MAX_RECS_TO_HARVEST = 0                             # 0 = all records
OPENALEX_FIELDS = 'doi,publication_year,title,type,authorships'


# ######################################################
# Utility functions related to harvesting of OpenAlex
# ######################################################

def rewrite_openalex_doi(doi: str) -> str:
    """Rewrite the DOI obtained from OpenAlex.

    :param doi: DOI to rewrite.
    :return: Result of rewriting.
    """
    doi = doi.lower()
    # '|' in regex is "or"
    # 'flags=re.IGNORECASE' not necessary, everything is lowercase already
    doi = re.sub(pattern=r'https|http', repl='', string=doi)
    doi = re.sub(pattern=r'doi.org', repl='', string=doi)
    doi = re.sub(pattern=r'doi', repl='', string=doi)
    # Remove any /, : or space at the beginning
    doi = re.sub(pattern=r'^[/: ]*', repl='', string=doi)
    return doi


def lookup_resout_type_openalex(type_uri: str) -> str:
    """Convert the OpenAlex output type to a shorter and easier readable output type.
    See function lookup_resout_type_pure()
    in harvest_pure_to_ricgraph.py for possible return types.

    :param type_uri: The TYPE_URI string from OpenAlex.
    :return: The result, in a few words.
    """
    if type_uri == '':
        print('lookup_resout_type_openalex(): research output has no type.')
        return 'empty'

    end = type_uri
    # The order used is the same order as in lookup_resout_type_pure().
    if end.startswith('book') or end.startswith('monograph'):
        return 'book'
    elif end.startswith('book-chapter') or end.startswith('reference-entry'):
        return 'book chapter'
    elif end.startswith('proceedings') or end.startswith('proceedings-article'):
        return 'conference proceeding'
    elif end.startswith('journal-article') or end.startswith('peer-review'):
        return 'journal article'
    elif end.startswith('dataset'):
        return 'dataset'
    elif end.startswith('dissertation'):
        return 'thesis'
    elif end.startswith('posted-content'):
        return 'working paper'
    elif end.startswith('other') or end.startswith('report'):
        return 'other contribution'
    else:
        print('lookup_resout_type_openalex(): unknown OpenAlex output type: "' + end + '".')
        return 'unknown'


# ######################################################
# Parsing
# ######################################################

def parse_openalex(harvest: list) -> pandas.DataFrame:
    """Parse the harvested persons and research outputs from OpenAlex.

    :param harvest: the harvest.
    :return: the harvested persons in a DataFrame.
    """
    parse_result = pandas.DataFrame()
    parse_chunk = []                # list of dictionaries
    print('There are ' + str(len(harvest)) + ' person and research output records, parsing record: 0  ', end='')
    count = 0
    for harvest_item in harvest:
        count += 1
        if count % 1000 == 0:
            print(count, ' ', end='', flush=True)
        if count % 20000 == 0:
            print('\n', end='', flush=True)

        if 'authorships' not in harvest_item:
            # There must be authors, otherwise skip.
            continue

        for authors in harvest_item['authorships']:
            # We only insert authors from ORGANIZATION_ROR, we
            # skip all other authors.
            if 'author' not in authors \
               or 'institutions' not in authors:
                # They must be present, otherwise skip this author.
                continue

            own_organization_found = False
            for institution in authors['institutions']:
                if 'ror' not in institution:
                    continue
                if institution['ror'] is None:
                    continue

                path = pathlib.PurePath(institution['ror'])
                if path.name != ORGANIZATION_ROR:
                    # Skip, not our institution.
                    continue
                own_organization_found = True

            if not own_organization_found:
                continue

            if 'id' not in authors['author']:
                # There must be an id, otherwise skip.
                continue

            path = pathlib.PurePath(authors['author']['id'])
            openalex_id = str(path.name)

            if 'orcid' in authors['author']:
                if authors['author']['orcid'] is not None:
                    parse_line = {}
                    parse_line['OPENALEX'] = openalex_id
                    path = pathlib.PurePath(authors['author']['orcid'])
                    parse_line['ORCID'] = str(path.name)
                    parse_chunk.append(parse_line)

            if 'display_name' in authors['author']:
                if authors['author']['display_name'] is not None:
                    parse_line = {}
                    parse_line['OPENALEX'] = openalex_id
                    parse_line['FULL_NAME'] = str(authors['author']['display_name'])
                    parse_chunk.append(parse_line)

            parse_line = {}
            parse_line['OPENALEX'] = openalex_id
            parse_line['ROR'] = str(ORGANIZATION_ROR)
            parse_chunk.append(parse_line)

            if 'doi' not in harvest_item:
                continue
            if 'title' not in harvest_item:
                continue
            if 'type' not in harvest_item:
                continue
            if harvest_item['doi'] is None or harvest_item['title'] is None:
                continue

            parse_line = {}
            parse_line['OPENALEX'] = openalex_id
            parse_line['DOI'] = str(rewrite_openalex_doi(harvest_item['doi']))
            parse_line['TITLE'] = str(harvest_item['title'])
            if harvest_item['type'] is None:
                parse_line['TYPE'] = str(lookup_resout_type_openalex(''))
            else:
                parse_line['TYPE'] = str(lookup_resout_type_openalex(harvest_item['type']))
            parse_chunk.append(parse_line)

    print(count, '\n', end='', flush=True)

    parse_chunk_df = pandas.DataFrame(parse_chunk)
    parse_result = pandas.concat([parse_result, parse_chunk_df], ignore_index=True)
    # dropna(how='all'): drop row if all row values contain NaN
    parse_result.dropna(axis=0, how='all', inplace=True)
    parse_result.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    return parse_result


# ######################################################
# Harvesting and parsing
# ######################################################

def harvest_and_parse_openalex(harvest_year: str,
                               headers: dict,
                               harvest_filename: str) -> Union[pandas.DataFrame, None]:
    """Harvest and parse data from OpenAlex.

    :param harvest_year: the year to harvest.
    :param headers: headers for OpenAlex.
    :param harvest_filename: filename to write harvest results to.
    :return: the DataFrame harvested, or None if nothing harvested.
    """

    print('Harvesting persons and research outputs from OpenAlex...')
    if not OPENALEX_HARVEST_FROM_FILE:
        url = OPENALEX_URL + '/' + OPENALEX_ENDPOINT + '?filter=institutions.ror:' + ORGANIZATION_ROR
        url += ',publication_year:' + harvest_year + '&select=' + OPENALEX_FIELDS
        retval = rcg.harvest_json_and_write_to_file(filename=harvest_filename,
                                                    url=url,
                                                    headers=headers,
                                                    max_recs_to_harvest=OPENALEX_MAX_RECS_TO_HARVEST,
                                                    chunksize=OPENALEX_CHUNKSIZE)
        if len(retval) == 0:
            # Nothing found
            return None

    harvest_data = rcg.read_json_from_file(filename=harvest_filename)
    parse = parse_openalex(harvest=harvest_data)
    print('The harvested persons and research outputs from OpenAlex are:')
    print(parse)
    return parse


# ######################################################
# Parsed results to Ricgraph #
# ######################################################

def parsed_persons_to_ricgraph(parsed_content: pandas.DataFrame) -> None:
    """Insert the parsed persons in Ricgraph.

    :param parsed_content: The records to insert in Ricgraph, if not present yet.
    :return: None.
    """
    print('Inserting persons from OpenAlex in Ricgraph...')
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    history_event = 'Source: Harvest OpenAlex persons at ' + timestamp + '.'

    # The order of the columns in the DataFrame below is not random.
    # A good choice is to have in the first two columns:
    # a. the identifier that appears the most in the system we harvest.
    # b. the identifier(s) that is already present in Ricgraph from previous harvests,
    #    since new identifiers from this harvest will be  linked to an already existing
    #    person-root.
    # If you have 2 of type (b), use these as the first 2 columns.
    person_identifiers = parsed_content[['OPENALEX', 'ORCID', 'FULL_NAME']].copy(deep=True)
    # dropna(how='all'): drop row if all row values contain NaN
    person_identifiers.dropna(axis=0, how='all', inplace=True)
    person_identifiers.drop_duplicates(keep='first', inplace=True, ignore_index=True)

    print('The following persons from OpenAlex will be inserted in Ricgraph:')
    print(person_identifiers)
    rcg.unify_personal_identifiers(personal_identifiers=person_identifiers, history_event=history_event)

    organizations = parsed_content[['OPENALEX', 'ROR']].copy(deep=True)
    organizations.dropna(axis=0, how='all', inplace=True)
    organizations.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    organizations.rename(columns={'OPENALEX': 'value1', 'ROR': 'value2'}, inplace=True)
    new_organization_columns = {'name1': 'OPENALEX',
                                'category1': 'person',
                                'name2': 'ROR',
                                'category2': 'organization',
                                'comment2': ORGANIZATION_NAME,
                                'history_event2': history_event}
    organizations = organizations.assign(**new_organization_columns)
    organizations = organizations[['name1', 'category1', 'value1',
                                   'name2', 'category2', 'value2', 'comment2', 'history_event2']]

    print('The following organizations from persons from OpenAlex will be inserted in Ricgraph:')
    print(organizations)
    rcg.create_nodepairs_and_edges_df(organizations)
    print('\nDone.\n')
    return


def parsed_resout_to_ricgraph(parsed_content: pandas.DataFrame) -> None:
    """Insert the parsed research outputs in Ricgraph.

    :param parsed_content: The records to insert in Ricgraph, if not present yet.
    :return: None.
    """
    print('Inserting research outputs from OpenAlex in Ricgraph...')
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    history_event = 'Source: Harvest OpenAlex research outputs at ' + timestamp + '.'

    resout = parsed_content[['OPENALEX', 'DOI', 'TITLE', 'TYPE']].copy(deep=True)
    resout.dropna(axis=0, how='all', inplace=True)
    resout.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    resout['value1'] = resout['DOI'].copy(deep=True)
    resout.rename(columns={'TYPE': 'category1',
                           'TITLE': 'comment1',
                           'OPENALEX': 'value2'}, inplace=True)
    new_resout_columns = {'name1': 'DOI',
                          'history_event1': history_event,
                          'name2': 'OPENALEX',
                          'category2': 'person'}
    resout = resout.assign(**new_resout_columns)
    resout = resout[['name1', 'category1', 'value1', 'history_event1', 'comment1',
                     'name2', 'category2', 'value2']]

    print('The following research outputs from OpenAlex will be inserted in Ricgraph:')
    print(resout)
    rcg.create_nodepairs_and_edges_df(resout)
    print('\nDone.\n')
    return


# ############################################
# ################### main ###################
# ############################################
if not os.path.exists(rcg.RICGRAPH_INI_FILE):
    print('Error, Ricgraph ini file "' + rcg.RICGRAPH_INI_FILE + '" not found, exiting.')
    exit(1)

config = configparser.ConfigParser()
config.read(rcg.RICGRAPH_INI_FILE)
try:
    ORGANIZATION_NAME = config['Organization']['organization_name']
    ORGANIZATION_ROR = config['Organization']['organization_ror']
except KeyError:
    print('Error, organization name or ROR not found in Ricgraph ini file, exiting.')
    exit(1)

try:
    # The OpenAlex 'polite pool' has much faster and more consistent response times.
    # See https://docs.openalex.org/api#the-polite-pool.
    # They have rate limits, but they are high: https://docs.openalex.org/api#rate-limits.
    OPENALEX_URL = config['OpenAlex_harvesting']['openalex_url']
    email = config['OpenAlex_harvesting']['openalex_polite_pool_email']
    if email == '':
        print('Error, insert an email address in the Ricgraph ini file for OpenAlex, exiting.')
        exit(1)
    OPENALEX_HEADERS['User-Agent'] = 'mailto:' + email
except KeyError:
    print('Error, OpenAlex URL or email address not found in Ricgraph ini file, exiting.')
    exit(1)

print('\nPreparing graph...')
rcg.open_ricgraph()

# Empty Ricgraph, choose one of the following.
# rcg.empty_ricgraph(answer='yes')
# rcg.empty_ricgraph(answer='no')
rcg.empty_ricgraph()

for year in OPENALEX_RESOUT_YEARS:
    print('Harvesting persons and research outputs from OpenAlex for year ' + year + '.')
    harvest_filename_year = OPENALEX_HARVEST_FILENAME.split('.')[0] \
                            + '-' + year + '.' \
                            + OPENALEX_HARVEST_FILENAME.split('.')[1]
    data_filename_year = OPENALEX_DATA_FILENAME.split('.')[0] \
                         + '-' + year + '.' \
                         + OPENALEX_DATA_FILENAME.split('.')[1]
    parse_persons_resout = harvest_and_parse_openalex(harvest_year=year,
                                                      headers=OPENALEX_HEADERS,
                                                      harvest_filename=harvest_filename_year)

    if parse_persons_resout is None:
        print('There are no persons or research outputs from OpenAlex to harvest.\n')
    else:
        rcg.write_dataframe_to_csv(data_filename_year, parse_persons_resout)
        parsed_persons_to_ricgraph(parse_persons_resout)
        parsed_resout_to_ricgraph(parse_persons_resout)

rcg.close_ricgraph()
