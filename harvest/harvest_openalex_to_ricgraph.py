# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
# 
# Copyright (c) 2023-2025 Rik D.T. Janssen
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
# Updated Rik D.T. Janssen, April, October, November 2023, October 2024, February 2025.
#
# ########################################################################
#
# Usage
# harvest_openalex_to_ricgraph.py [options]
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
import pandas
from typing import Union
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

# ######################################################
# Parameters for harvesting persons and research outputs from OpenAlex
# ######################################################
OPENALEX_API_URL = 'https://api.openalex.org/'
OPENALEX_ENDPOINT = 'works'

# Set this to True to simulate the harvest. If True, do not harvest, but read it from a file.
OPENALEX_READ_HARVEST_FROM_FILE = False
OPENALEX_HARVEST_FILENAME = 'openalex_harvest.json'

# Set this to True to read data from the csv file. No harvest will be done, this would
# not make sense. If False, a harvest will be done.
# Make sure OPENALEX_RESOUT_YEARS has been set correctly.
# If True, the value of OPENALEX_READ_HARVEST_FROM_FILE does not matter.
OPENALEX_READ_DATA_FROM_FILE = False
# OPENALEX_READ_DATA_FROM_FILE = True
OPENALEX_DATA_FILENAME = 'openalex_data.csv'

OPENALEX_RESOUT_YEARS = ['2022', '2023', '2024', '2025']
# This number is the max recs to harvest per year, not total.
OPENALEX_MAX_RECS_TO_HARVEST = 0                        # 0 = all records
OPENALEX_FIELDS = 'doi,publication_year,title,type,authorships'


# ######################################################
# Mapping from OpenAlex research output types to Ricgraph research output types.
# ######################################################
ROTYPE_MAPPING_OPENALEX = {
    'article': rcg.ROTYPE_JOURNAL_ARTICLE,
    'book': rcg.ROTYPE_BOOK,
    'book-chapter': rcg.ROTYPE_BOOKCHAPTER,
    'dataset': rcg.ROTYPE_DATASET,
    'dissertation': rcg.ROTYPE_PHDTHESIS,
    'editorial': rcg.ROTYPE_EDITORIAL,
    'erratum': rcg.ROTYPE_MEMORANDUM,
    'letter': rcg.ROTYPE_LETTER,
    'monograph': rcg.ROTYPE_BOOK,
    'other': rcg.ROTYPE_OTHER_CONTRIBUTION,
    'paratext': rcg.ROTYPE_OTHER_CONTRIBUTION,
            # OpenAlex 'paratext': stuff that's in scholarly venue (like a journal)
            # but is about the venue rather than a scholarly work properly speaking.
            # https://docs.openalex.org/api-entities/works/work-object.
    'peer-review': rcg.ROTYPE_REVIEW,
    'posted-content': rcg.ROTYPE_PREPRINT,
    'preprint': rcg.ROTYPE_PREPRINT,
    'proceedings': rcg.ROTYPE_CONFERENCE_ARTICLE,
    'proceedings-article': rcg.ROTYPE_CONFERENCE_ARTICLE,
    'reference-entry': rcg.ROTYPE_ENTRY,
    'report': rcg.ROTYPE_REPORT,
    'retraction': rcg.ROTYPE_RETRACTION,
    'review': rcg.ROTYPE_REVIEW,
    'supplementary-materials': rcg.ROTYPE_OTHER_CONTRIBUTION
}


# ######################################################
# Utility functions related to harvesting of OpenAlex
# ######################################################

def create_openalex_url(name: str, value: str) -> str:
    """Create a URL to refer to the source of a node.
    The id for an author in the json looks like a URL. I am not sure if it is
    supposed to be a URL that works, but now (November 2023) it does not.
    Since there is no other URL which shows author information, we use a link
    to the json for the author in the API.

    :param name: an identifier name.
    :param value: the value.
    :return: a URL.
    """
    if name == '' or value == '':
        return ''

    if name == 'AUTHOR':
        return OPENALEX_API_URL + 'authors/' + value
    else:
        return ''


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
    print('There are ' + str(len(harvest)) + ' person and research output records ('
          + rcg.timestamp() + '), parsing record: 0  ', end='')
    count = 0
    for harvest_item in harvest:
        count += 1
        if count % 1000 == 0:
            print(count, ' ', end='', flush=True)
        if count % 10000 == 0:
            print('(' + rcg.timestamp() + ')\n', end='', flush=True)

        if 'authorships' not in harvest_item:
            # There must be authors, otherwise skip.
            continue

        for authors in harvest_item['authorships']:
            # Previously, we only inserted authors from ORGANIZATION_ROR.
            # Now we insert authors from any organization.
            if 'author' not in authors \
               or 'institutions' not in authors:
                # They must be present, otherwise skip this author.
                continue

            if 'id' not in authors['author']:
                # There must be an id, otherwise skip.
                continue

            path = pathlib.PurePath(authors['author']['id'])
            openalex_id = str(path.name)

            if 'orcid' in authors['author']:
                if authors['author']['orcid'] is not None:
                    parse_line = {'OPENALEX': openalex_id}
                    path = pathlib.PurePath(authors['author']['orcid'])
                    parse_line['ORCID'] = str(path.name)
                    parse_chunk.append(parse_line)

            if 'display_name' in authors['author']:
                if authors['author']['display_name'] is not None:
                    parse_line = {'OPENALEX': openalex_id,
                                  'FULL_NAME': str(authors['author']['display_name'])}
                    parse_chunk.append(parse_line)

            for institution in authors['institutions']:
                # An author can work at multiple institutions.
                # With the code in this for, we collect in the parse
                # any institution connected to this author.
                # This may or may not be a good idea, since sometimes institutions
                # connected to an author in OpenAlex are not correct. Options are e.g.:
                # 1. Do not collect any institution in OpenAlex to an author.
                # 2. Collect any institution in OpenAlex to an author.
                # 3. Only collect institutions to an author if the author is NOT
                #    from our own organization (then path.name != ORGANIZATION_ROR).
                # In the code below, we do (2).
                if 'ror' not in institution:
                    continue
                if institution['ror'] is None:
                    continue

                path = pathlib.PurePath(institution['ror'])
                parse_line = {'OPENALEX': openalex_id,
                              'ROR': str(path.name)}
                if 'display_name' in institution and institution['display_name'] is not None:
                    parse_line['ORGANIZATION_NAME'] = str(institution['display_name'])
                parse_chunk.append(parse_line)

            if 'doi' not in harvest_item:
                continue
            if 'title' not in harvest_item:
                continue
            if 'type' not in harvest_item:
                continue
            if harvest_item['doi'] is None or harvest_item['title'] is None:
                continue

            parse_line = {'OPENALEX': openalex_id,
                          'DOI': rcg.normalize_doi(identifier=str(harvest_item['doi'])),
                          'TITLE': str(harvest_item['title'])}
            if 'publication_year' in harvest_item:
                parse_line['YEAR'] = str(harvest_item['publication_year'])
            else:
                parse_line['YEAR'] = ''
            if harvest_item['type'] is None:
                parse_line['DOI_TYPE'] = str(rcg.lookup_resout_type(research_output_type='',
                                                                research_output_mapping=ROTYPE_MAPPING_OPENALEX))
            else:
                parse_line['DOI_TYPE'] = str(rcg.lookup_resout_type(research_output_type=harvest_item['type'],
                                                                research_output_mapping=ROTYPE_MAPPING_OPENALEX))
            parse_chunk.append(parse_line)

    print(count, '(' + rcg.timestamp() + ')\n', end='', flush=True)

    parse_chunk_df = pandas.DataFrame(parse_chunk)
    parse_result = pandas.concat([parse_result, parse_chunk_df], ignore_index=True)
    return rcg.normalize_identifiers(df=parse_result)


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
    print('Harvesting persons and research outputs from ' + HARVEST_SOURCE + '...')
    if not OPENALEX_READ_HARVEST_FROM_FILE:
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
    print('The harvested persons and research outputs from ' + HARVEST_SOURCE + ' are:')
    print(parse)
    return parse


# ######################################################
# Parsed results to Ricgraph
# ######################################################

def parsed_persons_to_ricgraph(parsed_content: pandas.DataFrame) -> None:
    """Insert the parsed persons in Ricgraph.

    :param parsed_content: The records to insert in Ricgraph, if not present yet.
    :return: None.
    """
    timestamp = rcg.datetimestamp()
    print('Inserting persons from ' + HARVEST_SOURCE + ' in Ricgraph at '
          + timestamp + '...')
    history_event = 'Source: Harvest ' + HARVEST_SOURCE + ' persons at ' + timestamp + '.'

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

    print('The following persons from ' + HARVEST_SOURCE + ' will be inserted in Ricgraph at '
          + rcg.timestamp() + ':')
    print(person_identifiers)
    rcg.unify_personal_identifiers(personal_identifiers=person_identifiers,
                                   source_event=HARVEST_SOURCE,
                                   history_event=history_event)

    # Connect organizations to persons.
    organizations = parsed_content[['OPENALEX', 'ORGANIZATION_NAME']].copy(deep=True)
    organizations['url_main1'] = organizations[['OPENALEX']].apply(
                                 lambda row: create_openalex_url(name='AUTHOR',
                                                                 value=row['OPENALEX']), axis=1)
    organizations.dropna(axis=0, how='any', inplace=True)
    organizations.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    organizations.rename(columns={'OPENALEX': 'value1', 'ORGANIZATION_NAME': 'value2'}, inplace=True)
    new_organization_columns = {'name1': 'OPENALEX',
                                'category1': 'person',
                                'name2': 'ORGANIZATION_NAME',
                                'category2': 'organization',
                                'source_event2': HARVEST_SOURCE,
                                'history_event2': history_event}
    organizations = organizations.assign(**new_organization_columns)
    organizations = organizations[['name1', 'category1', 'value1',
                                   'url_main1',
                                   'name2', 'category2', 'value2',
                                   'source_event2', 'history_event2']]

    print('The following organizations from persons from ' + HARVEST_SOURCE
          + ' will be inserted in Ricgraph at ' + rcg.timestamp() + ':')
    print(organizations)
    rcg.create_nodepairs_and_edges_df(left_and_right_nodepairs=organizations)

    # Connect organization name to organization ROR.
    organizations = parsed_content[['ROR', 'ORGANIZATION_NAME']].copy(deep=True)
    organizations.dropna(axis=0, how='any', inplace=True)
    organizations.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    organizations.rename(columns={'ROR': 'value1', 'ORGANIZATION_NAME': 'value2'}, inplace=True)
    new_organization_columns = {'name1': 'ROR',
                                'category1': 'organization',
                                'source_event1': HARVEST_SOURCE,
                                'history_event1': history_event,
                                'name2': 'ORGANIZATION_NAME',
                                'category2': 'organization'}
    organizations = organizations.assign(**new_organization_columns)
    organizations = organizations[['name1', 'category1', 'value1',
                                   'source_event1', 'history_event1',
                                   'name2', 'category2', 'value2']]

    print('The following organization RORs to organization names from persons from ' + HARVEST_SOURCE
          + ' will be inserted in Ricgraph at ' + rcg.timestamp() + ':')
    print(organizations)
    rcg.create_nodepairs_and_edges_df(left_and_right_nodepairs=organizations)

    print('\nDone at ' + rcg.timestamp() + '.\n')
    return


def parsed_resout_to_ricgraph(parsed_content: pandas.DataFrame) -> None:
    """Insert the parsed research outputs in Ricgraph.

    :param parsed_content: The records to insert in Ricgraph, if not present yet.
    :return: None.
    """
    timestamp = rcg.datetimestamp()
    print('Inserting research outputs from ' + HARVEST_SOURCE + ' in Ricgraph at '
          + timestamp + '...')
    history_event = 'Source: Harvest ' + HARVEST_SOURCE + ' research outputs at ' + timestamp + '.'

    resout = parsed_content[['OPENALEX', 'DOI', 'TITLE', 'YEAR', 'DOI_TYPE']].copy(deep=True)
    resout.dropna(axis=0, how='any', inplace=True)
    resout.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    resout.rename(columns={'DOI_TYPE': 'category1',
                           'DOI': 'value1',
                           'TITLE': 'comment1',
                           'YEAR': 'year1',
                           'OPENALEX': 'value2'}, inplace=True)
    new_resout_columns = {'name1': 'DOI',
                          'source_event1': HARVEST_SOURCE,
                          'history_event1': history_event,
                          'name2': 'OPENALEX',
                          'category2': 'person'}
    resout = resout.assign(**new_resout_columns)
    resout = resout[['name1', 'category1', 'value1', 'comment1', 'year1',
                     'source_event1', 'history_event1',
                     'name2', 'category2', 'value2']]

    print('The following research outputs from ' + HARVEST_SOURCE
          + ' will be inserted in Ricgraph at ' + rcg.timestamp() + ':')
    print(resout)
    rcg.create_nodepairs_and_edges_df(left_and_right_nodepairs=resout)
    print('\nDone at ' + rcg.timestamp() + '.\n')
    return


# ############################################
# ################### main ###################
# ############################################
rcg.print_commandline_arguments(argument_list=sys.argv)
if (organization := rcg.get_commandline_argument_organization(argument_list=sys.argv)) == '':
    print('Exiting.\n')
    exit(1)

org_name = 'organization_name_' + organization
org_ror = 'organization_ror_' + organization
ORGANIZATION_NAME = rcg.get_configfile_key(section='Organization', key=org_name)
ORGANIZATION_ROR = rcg.get_configfile_key(section='Organization', key=org_ror)
if ORGANIZATION_NAME == '' or ORGANIZATION_ROR == '':
    print('Ricgraph initialization: error, "' + org_name + '" or "' + org_ror + '"')
    print('  not existing or empty in Ricgraph ini file, exiting.')
    exit(1)

HARVEST_SOURCE = 'OpenAlex-' + organization

# The OpenAlex 'polite pool' has much faster and more consistent response times.
# See https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication#the-polite-pool.
# They have rate limits, but they are high:
# https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication.
OPENALEX_URL = rcg.get_configfile_key(section='OpenAlex_harvesting', key='openalex_url')
email = rcg.get_configfile_key(section='OpenAlex_harvesting', key='openalex_polite_pool_email')
if OPENALEX_URL == '' or email == '':
    print('Ricgraph initialization: error, "openalex_url" or "openalex_polite_pool_email"')
    print('  not existing or empty in Ricgraph ini file, exiting.')
    exit(1)
OPENALEX_HEADERS['User-Agent'] = 'mailto:' + email

print('\nPreparing graph...')
rcg.open_ricgraph()

empty_graph = rcg.get_commandline_argument_empty_ricgraph(argument_list=sys.argv)
if empty_graph == 'yes' or empty_graph == 'no':
    rcg.empty_ricgraph(answer=empty_graph)
else:
    print('Exiting.\n')
    exit(1)

rcg.graphdb_nr_accesses_print()

for year in OPENALEX_RESOUT_YEARS:
    data_file_year = OPENALEX_DATA_FILENAME.split('.')[0] \
                     + '-' + year + '-' + organization + '.' \
                     + OPENALEX_DATA_FILENAME.split('.')[1]
    if OPENALEX_READ_DATA_FROM_FILE:
        error_message = 'There are no persons or research outputs from ' + HARVEST_SOURCE
        error_message += ' for year ' + year + ' to read from file ' + data_file_year + '.\n'
        print('Reading persons and research outputs from ' + HARVEST_SOURCE
              + ' for year ' + year + ' from file ' + data_file_year + '.')
    else:
        error_message = 'There are no persons or research outputs from ' + HARVEST_SOURCE
        error_message += ' for year ' + year + ' to harvest.\n'
        print('Harvesting persons and research outputs from ' + HARVEST_SOURCE
              + ' for year ' + year + '.')
        harvest_file_year = OPENALEX_HARVEST_FILENAME.split('.')[0] \
                            + '-' + year + '-' + organization + '.' \
                            + OPENALEX_HARVEST_FILENAME.split('.')[1]
        parse_persons_resout = harvest_and_parse_openalex(harvest_year=year,
                                                          headers=OPENALEX_HEADERS,
                                                          harvest_filename=harvest_file_year)
        rcg.write_dataframe_to_csv(filename=data_file_year, df=parse_persons_resout)

    parse_persons_resout = rcg.read_dataframe_from_csv(filename=data_file_year)
    if parse_persons_resout is None or parse_persons_resout.empty:
        print(error_message)
    else:
        parsed_persons_to_ricgraph(parsed_content=parse_persons_resout)
        parsed_resout_to_ricgraph(parsed_content=parse_persons_resout)

    rcg.graphdb_nr_accesses_print()

rcg.close_ricgraph()
