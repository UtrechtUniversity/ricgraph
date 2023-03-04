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
# With this code, you can harvest persons, organizations and research outputs from Pure.
# You have to set some parameters in ricgraph.ini.
# Also, you can set a number of parameters in the code following the "import" statements below.
#
# Original version Rik D.T. Janssen, December 2022.
# Updated Rik D.T. Janssen, February 2023.
#
# ########################################################################


import os.path
import re
import pandas
import numpy
from datetime import datetime
from typing import Union
import configparser
import ricgraph as rcg


# ######################################################
# General parameters for harvesting from Pure.
# Documentation Pure API: PURE_URL/ws/api/524/api-docs/index.html
# ######################################################
PURE_API_VERSION = 'ws/api/524'
PURE_CHUNKSIZE = 500
PURE_HEADERS = {'Accept': 'application/json'
                # The following will be read in __main__
                # 'api-key': PURE_API_KEY
                }
global PURE_URL

# ######################################################
# Parameters for harvesting persons from pure
# ######################################################
PURE_PERSONS_ENDPOINT = 'persons'
PURE_PERSONS_HARVEST_FROM_FILE = False
PURE_PERSONS_HARVEST_FILENAME = 'pure_persons_harvest.json'
PURE_PERSONS_DATA_FILENAME = 'pure_persons_data.csv'
PURE_PERSONS_MAX_RECS_TO_HARVEST = 0                  # 0 = all records
PURE_PERSONS_FIELDS = {'fields': ['uuid',
                                  'name.*',
                                  'ids.*',
                                  'staffOrganisationAssociations.period.*',
                                  'staffOrganisationAssociations.organisationalUnit.*',
                                  'orcid'
                                  ],
                       'employmentStatus': 'ACTIVE'
                       }

# ######################################################
# Parameters for harvesting organizations from pure
# ######################################################
PURE_ORGANIZATIONS_ENDPOINT = 'organisational-units'
PURE_ORGANIZATIONS_HARVEST_FROM_FILE = False
PURE_ORGANIZATIONS_HARVEST_FILENAME = 'pure_organizations_harvest.json'
PURE_ORGANIZATIONS_DATA_FILENAME = 'pure_organizations_data.csv'
PURE_ORGANIZATIONS_MAX_RECS_TO_HARVEST = 0                  # 0 = all records
PURE_ORGANIZATIONS_FIELDS = {'fields': ['uuid',
                                        'period.*',
                                        'name.*',
                                        'type.*',
                                        'ids.*',
                                        'parents.*'
                                        ]
                             }

# ######################################################
# Parameters for harvesting research outputs from pure
# ######################################################
PURE_RESOUT_ENDPOINT = 'research-outputs'
PURE_RESOUT_HARVEST_FROM_FILE = False
PURE_RESOUT_HARVEST_FILENAME = 'pure_resout_harvest.json'
PURE_RESOUT_DATA_FILENAME = 'pure_resout_data.csv'
PURE_RESOUT_YEARS = ['2020', '2021', '2022', '2023']
# This number is the max recs to harvest per year, not total
PURE_RESOUT_MAX_RECS_TO_HARVEST = 0                  # 0 = all records
PURE_RESOUT_FIELDS = {'fields': ['uuid',
                                 'title.*',
                                 'confidential',
                                 'type.*',
                                 'workflow.*',
                                 'publicationStatuses.*',
                                 'personAssociations.*',
                                 'electronicVersions.*'
                                 ]
                      }


# ######################################################
# Utility functions related to harvesting of Pure
# ######################################################

def create_pure_url(name: str, value: str) -> str:
    """Create a URL to refer to the source of a node.

    :param name: an identifier name, e.g. PureUUid-pers, PureUUid-org, etc.
    :param value: the value.
    :return: an URL.
    """
    if name == '' or value == '':
        return ''

    if name == 'PureUUid-pers':
        return PURE_URL + '/en/persons/' + value
    elif name == 'PureUUid-org':
        return PURE_URL + '/en/organisations/' + value
    elif name == 'PureUUid-resout':
        return PURE_URL + '/en/publications/' + value
    else:
        return ''


def create_urlmain(type_id: str, doi_value: str, uuid_value: str) -> str:
    """A helper function for parsed_resout_to_ricgraph()"""
    if type_id == 'DOI':
        return rcg.create_well_known_url(name=type_id, value=doi_value)
    elif type_id == 'PureUUid-resout':
        return create_pure_url(name=type_id, value=uuid_value)
    else:
        # Should not happen
        print('create_urlmain(): error')
    return ''


def create_urlother(type_id: str, uuid_value: str) -> str:
    """A helper function for parsed_resout_to_ricgraph()"""
    if type_id == 'DOI':
        return create_pure_url(name='PureUUid-resout', value=uuid_value)
    else:
        return ''


def rewrite_pure_doi(doi: str) -> str:
    """Rewrite the DOI obtained from Pure.
    They are written in various different ways, so they need to be rewritten.

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
    doi = re.sub(pattern=r'.proxy.uu.nl/', repl='', string=doi)
    return doi


def lookup_resout_type_pure(type_uri: str) -> str:
    """Convert the Pure output type to a shorter and easier readable output type.
    This list is inspired by the Strategy Evaluation Protocol 2021-2027
    https://www.universiteitenvannederland.nl/files/documenten/Domeinen/Onderzoek/SEP_2021-2027.pdf,
    Appendix E2.

    :param type_uri: The TYPE_URI string from Pure.
    :return: The result, in a few words.
    """
    if type_uri == '':
        print('lookup_resout_type_pure(): research output has no type.')
        return 'empty'

    pure_prefix = '/dk/atira/pure/researchoutput/researchoutputtypes'
    if type_uri.startswith(pure_prefix):
        end = type_uri[len(pure_prefix) + 1:]
    else:
        print('lookup_resout_type_pure(): research output malformed: "' + type_uri + '".')
        return 'Pure research output malformed: ' + type_uri

    if end.startswith('bookanthology'):
        return 'book'
    elif end.startswith('contributiontobookanthology'):
        return 'book chapter'
    elif end.startswith('contributiontoconference'):
        return 'conference proceeding'
    elif end.startswith('contributiontojournal'):
        return 'journal article'
    elif end.startswith('nontextual/database'):
        return 'dataset'
    elif end.startswith('nontextual/software'):
        return 'software'
    elif end.startswith('nontextual/web'):
        return 'website'
    elif end.startswith('nontextual/digitalorvisualproducts'):
        return 'digital or visual product'
    elif end.startswith('nontextual/exhibition') or end.startswith('nontextual/performance'):
        return 'exhibition or performance'
    elif end.startswith('patent'):
        return 'patent'
    elif end.startswith('thesis'):
        return 'thesis'
    elif end.startswith('memorandum'):
        return 'memorandum'
    elif end.startswith('workingpaper'):
        return 'working paper'
    elif end.startswith('othercontribution'):
        return 'other contribution'
    else:
        print('lookup_resout_type_pure(): unknown pure output type: "' + end + '".')
        return 'unknown'


# ######################################################
# Parsing
# ######################################################

def parse_pure_persons(harvest: list) -> pandas.DataFrame:
    """Parse the harvested persons from Pure.

    :param harvest: the harvest.
    :return: the harvested persons in a DataFrame.
    """
    parse_result = pandas.DataFrame()
    parse_chunk = []                # list of dictionaries
    print('There are ' + str(len(harvest)) + ' person records, parsing record: 0  ', end='')
    count = 0
    for harvest_item in harvest:
        count += 1
        if count % 1000 == 0:
            print(count, ' ', end='', flush=True)
        if count % 20000 == 0:
            print('\n', end='', flush=True)

        if 'uuid' not in harvest_item:
            # There must be an uuid, otherwise skip
            continue
        if 'name' in harvest_item:
            parse_line = {}
            parse_line['UUID'] = str(harvest_item['uuid'])
            parse_line['FULL_NAME'] = harvest_item['name']['lastName'] \
                                      + ', ' + harvest_item['name']['firstName']
            parse_chunk.append(parse_line)
        if 'orcid' in harvest_item:
            parse_line = {}
            parse_line['UUID'] = str(harvest_item['uuid'])
            parse_line['ORCID'] = str(harvest_item['orcid'])
            parse_chunk.append(parse_line)
        if 'ids' in harvest_item:
            for identities in harvest_item['ids']:
                if 'value' in identities and 'type' in identities:
                    value_identifier = str(identities['value']['value'])
                    name_identifier = str(identities['type']['term']['text'][0]['value'])
                    parse_line = {}
                    parse_line['UUID'] = str(harvest_item['uuid'])
                    parse_line[name_identifier] = value_identifier
                    parse_chunk.append(parse_line)
        if 'staffOrganisationAssociations' in harvest_item:
            for stafforg in harvest_item['staffOrganisationAssociations']:
                if 'period' in stafforg:
                    if 'endDate' in stafforg['period'] and stafforg['period']['endDate'] != '':
                        # Only consider current organizations, that is an organization
                        # where endData is not existing or empty. If not, then skip.
                        continue
                else:
                    # If there is no period skip
                    continue

                if 'organisationalUnit' in stafforg:
                    orgunit = stafforg['organisationalUnit']
                    if 'type' in orgunit:
                        pure_org_uri = str(orgunit['type']['uri'])
                        if pure_org_uri[-3] == 'r':
                            # Skip research organizations (with an 'r' in the uri, like ..../r05)
                            continue

                    parse_line = {}
                    parse_line['UUID'] = str(harvest_item['uuid'])
                    parse_line['organisationalUnit'] = str(orgunit['uuid'])
                    parse_chunk.append(parse_line)

    print(count, '\n', end='', flush=True)

    parse_chunk_df = pandas.DataFrame(parse_chunk)
    parse_result = pandas.concat([parse_result, parse_chunk_df], ignore_index=True)
    # dropna(how='all'): drop row if all row values contain NaN
    parse_result.dropna(axis=0, how='all', inplace=True)
    parse_result.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    parse_result.rename(columns={'Digital author ID': 'DIGITAL_AUTHOR_ID',
                                 'Scopus Author ID': 'SCOPUS_AUTHOR_ID',
                                 'Employee ID': 'EMPLOYEE_ID',
                                 'Researcher ID': 'RESEARCHER_ID',
                                 'organisationalUnit': 'ORG_UUID',
                                 }, inplace=True)
    return parse_result


def parse_pure_organizations(harvest: list) -> pandas.DataFrame:
    """Parse the harvested organizations from Pure.

    :param harvest: the harvest.
    :return: the harvested organizations in a DataFrame.
    """
    parse_result = pandas.DataFrame()
    parse_chunk = []                # list of dictionaries
    print('There are ' + str(len(harvest)) + ' organization records, parsing record: 0  ', end='')
    count = 0
    for harvest_item in harvest:
        count += 1
        if count % 1000 == 0:
            print(count, ' ', end='', flush=True)
        if count % 20000 == 0:
            print('\n', end='', flush=True)

        if 'uuid' not in harvest_item:
            # There must be an uuid, otherwise skip
            continue
        if 'period' in harvest_item:
            if 'endDate' in harvest_item['period'] and harvest_item['period']['endDate'] != '':
                # Only consider current organizations, that is an organization
                # where endDate is not existing or empty. If not, then skip.
                continue
        else:
            # If there is no period skip
            continue
        if 'type' in harvest_item:
            pure_org_uri = str(harvest_item['type']['uri'])
            if pure_org_uri[-3] == 'r':
                # Skip research organizations (with an 'r' in the uri, like ..../r05)
                continue
        else:
            # If there is no type skip
            continue
        if 'name' not in harvest_item:
            # If there is no name skip
            continue
        # Skip the organization ids. There are only a few, and it
        # seems to complicated to implement for now (we will need
        # something like 'organization-root' aka 'person-root').
        # if 'ids' in harvest_item:
        #     for identities in harvest_item['ids']:
        #         if 'value' in identities and 'type' in identities:
        #             value_identifier = str(identities['value']['value'])
        #             name_identifier = str(identities['type']['term']['text'][0]['value'])
        #             parse_line = {}
        #             parse_line['UUID'] = str(harvest_item['uuid'])
        #             parse_line[name_identifier] = value_identifier
        #             parse_chunk.append(parse_line)
        if 'parents' in harvest_item:
            for parentsorg in harvest_item['parents']:
                if 'uuid' not in parentsorg:
                    # There must be an uuid, otherwise skip
                    continue
                # Note: 'parents' does not have a 'period', so we don't need to do something.
                if 'type' in parentsorg:
                    pure_parentsorg_uri = str(parentsorg['type']['uri'])
                    if pure_parentsorg_uri[-3] == 'r':
                        # Skip research organizations (with an 'r' in the uri, like ..../r05)
                        continue
                else:
                    continue

                parse_line = {}
                parse_line['UUID'] = str(harvest_item['uuid'])
                # 'type' and 'name' must exist, otherwise we wouldn't have gotten here
                parse_line['ORG_TYPE_NAME'] = harvest_item['type']['term']['text'][0]['value']
                parse_line['ORG_NAME'] = harvest_item['name']['text'][0]['value']
                parse_line['PARENT_UUID'] = str(parentsorg['uuid'])
                parse_chunk.append(parse_line)

    print(count, '\n', end='', flush=True)

    parse_chunk_df = pandas.DataFrame(parse_chunk)
    parse_result = pandas.concat([parse_result, parse_chunk_df], ignore_index=True)
    # dropna(how='all'): drop row if all row values contain NaN
    parse_result.dropna(axis=0, how='all', inplace=True)
    parse_result.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    return parse_result


def parse_pure_resout(harvest: list) -> pandas.DataFrame:
    """Parse the harvested research outputs from Pure.

    :param harvest: the harvest.
    :return: the harvested research outputs in a DataFrame.
    """
    parse_result = pandas.DataFrame()
    parse_chunk = []                # list of dictionaries
    print('There are ' + str(len(harvest)) + ' research output records, parsing record: 0  ', end='')
    count = 0
    for harvest_item in harvest:
        count += 1
        if count % 1000 == 0:
            print(count, ' ', end='', flush=True)
        if count % 20000 == 0:
            print('\n', end='', flush=True)

        if 'uuid' not in harvest_item:
            # There must be an uuid, otherwise skip
            continue
        if 'title' not in harvest_item:
            # There must be a title, otherwise skip
            continue
        if 'confidential' in harvest_item:
            if harvest_item['confidential']:
                # Skip the confidential ones
                continue
        if 'type' not in harvest_item:
            # There must be a type of this resout, otherwise skip
            continue
        if 'workflow' in harvest_item:
            if harvest_item['workflow']['workflowStep'] != 'validated':
                # Only 'validated' resouts
                continue
        else:
            # Skip if no workflow
            continue
        if 'publicationStatuses' in harvest_item:
            # We need a current status.
            published_found = False
            for pub_item in harvest_item['publicationStatuses']:
                if pub_item['current']:
                    if pub_item['publicationStatus']['term']['text'][0]['value'] == 'Published':
                        # Only 'Published' resouts
                        published_found = True
                        break

            if not published_found:
                continue
        else:
            # Skip if no publicationStatuses
            continue
        doi = ''
        if 'electronicVersions' in harvest_item:
            for elecversions in harvest_item['electronicVersions']:
                # Take the last doi found for a resout
                if 'doi' in elecversions:
                    doi = str(elecversions['doi'])
                    doi = rewrite_pure_doi(doi=doi)
        if 'personAssociations' in harvest_item:
            for persons in harvest_item['personAssociations']:
                if 'person' in persons:                             # internal person
                    if 'uuid' not in persons['person']:
                        # There must be an uuid, otherwise skip
                        continue
                    author_uuid = str(persons['person']['uuid'])
                elif 'externalPerson' in persons:                  # external person
                    if 'uuid' not in persons['externalPerson']:
                        # There must be an uuid, otherwise skip
                        continue
                    author_uuid = str(persons['externalPerson']['uuid'])
                    author_uuid += ' (external person)'
                elif 'authorCollaboration' in persons:             # author collaboration
                    if 'uuid' not in persons['authorCollaboration']:
                        # There must be an uuid, otherwise skip
                        continue
                    author_uuid = str(persons['authorCollaboration']['uuid'])
                    author_uuid += ' (author collaboration)'
                else:
                    # If we get here you might want to add another "elif" above with
                    # the missing personAssociation. Sometimes there is no, then it is ok.
                    print('\nparse_pure_resout(): Warning: Unknown personAssociation for publication '
                          + str(harvest_item['uuid']))
                    continue

                parse_line = {}
                parse_line['RESOUT_UUID'] = str(harvest_item['uuid'])
                parse_line['DOI'] = doi
                parse_line['TITLE'] = str(harvest_item['title']['value'])
                parse_line['TYPE'] = lookup_resout_type_pure(str(harvest_item['type']['uri']))
                parse_line['PERSON_UUID'] = author_uuid
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

def harvest_and_parse_pure_data(mode: str, endpoint: str,
                                headers: dict, body: dict,
                                harvest_filename: str) -> Union[pandas.DataFrame, None]:
    """Harvest and parse data from Pure.

    :param mode: 'persons', 'organizations' or 'research outputs', to indicate what to harvest.
    :param endpoint: endpoint Pure.
    :param headers: headers for Pure.
    :param body: the body of a POST request, or '' for a GET request.
    :param harvest_filename: filename to write harvest results to.
    :return: the DataFrame harvested, or None if nothing harvested.
    """
    if mode != 'persons' and mode != 'organizations' and mode != 'research outputs':
        print('harvest_and_parse_pure_data(): unknown mode ' + mode + '.')
        return None

    if mode == 'persons':
        max_recs_to_harvest = PURE_PERSONS_MAX_RECS_TO_HARVEST
    elif mode == 'organizations':
        max_recs_to_harvest = PURE_ORGANIZATIONS_MAX_RECS_TO_HARVEST
    elif mode == 'research outputs':
        max_recs_to_harvest = PURE_RESOUT_MAX_RECS_TO_HARVEST
    else:
        # Should not happen
        return None

    print('Harvesting ' + mode + ' from Pure...')
    if (mode == 'persons' and not PURE_PERSONS_HARVEST_FROM_FILE) \
       or (mode == 'organizations' and not PURE_ORGANIZATIONS_HARVEST_FROM_FILE) \
       or (mode == 'research outputs' and not PURE_RESOUT_HARVEST_FROM_FILE):
        url = PURE_URL + '/' + PURE_API_VERSION + '/' + endpoint
        retval = rcg.harvest_json_and_write_to_file(filename=harvest_filename,
                                                    url=url,
                                                    headers=headers,
                                                    body=body,
                                                    max_recs_to_harvest=max_recs_to_harvest,
                                                    chunksize=PURE_CHUNKSIZE)
        if len(retval) == 0:
            # Nothing found
            return None

    harvest_data = rcg.read_json_from_file(filename=harvest_filename)
    parse = pandas.DataFrame()
    if mode == 'persons':
        parse = parse_pure_persons(harvest=harvest_data)
    elif mode == 'organizations':
        parse = parse_pure_organizations(harvest=harvest_data)
    elif mode == 'research outputs':
        parse = parse_pure_resout(harvest=harvest_data)

    print('The harvested ' + mode + ' are:')
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
    print('Inserting persons from Pure in Ricgraph...')
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    history_event = 'Source: Harvest Pure persons at ' + timestamp + '.'

    person_identifiers = parsed_content[['UUID', 'FULL_NAME', 'DIGITAL_AUTHOR_ID',
                                         'ORCID', 'SCOPUS_AUTHOR_ID', 'EMPLOYEE_ID',
                                         'ISNI', 'RESEARCHER_ID']].copy(deep=True)
    person_identifiers.rename(columns={'UUID': 'PureUUid-pers'}, inplace=True)
    # dropna(how='all'): drop row if all row values contain NaN
    person_identifiers.dropna(axis=0, how='all', inplace=True)
    person_identifiers.drop_duplicates(keep='first', inplace=True, ignore_index=True)

    print('The following persons from Pure will be inserted in Ricgraph:')
    print(person_identifiers)
    rcg.unify_personal_identifiers(personal_identifiers=person_identifiers, history_event=history_event)

    organizations = parsed_content[['UUID', 'ORG_UUID']].copy(deep=True)
    organizations.dropna(axis=0, how='all', inplace=True)
    organizations.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    organizations['url_main1'] = organizations[['UUID']].apply(
                                 lambda row: create_pure_url('PureUUid-pers', row['UUID']), axis=1)
    # Do not insert the organization URL here, it is done in parsed_organizations_to_ricgraph()
    organizations.rename(columns={'UUID': 'value1',
                                  'ORG_UUID': 'value2'}, inplace=True)
    new_organization_columns = {'name1': 'PureUUid-pers',
                                'category1': 'person',
                                'name2': 'PureUUid-org',
                                'category2': 'organization',
                                'history_event2': history_event}
    organizations = organizations.assign(**new_organization_columns)
    organizations = organizations[['name1', 'category1', 'value1', 'url_main1',
                                   'name2', 'category2', 'value2', 'history_event2']]

    print('The following organizations from persons from Pure will be inserted in Ricgraph:')
    print(organizations)
    rcg.create_nodepairs_and_edges_df(organizations)
    print('\nDone.\n')
    return


def parsed_organizations_to_ricgraph(parsed_content: pandas.DataFrame) -> None:
    """Insert the parsed organizations in Ricgraph.

    :param parsed_content: The records to insert in Ricgraph, if not present yet.
    :return: None.
    """
    print('Inserting organizations from Pure in Ricgraph...')
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    history_event = 'Source: Harvest Pure organizations at ' + timestamp + '.'

    parsed_content['FULL_ORG_NAME'] = parsed_content['ORG_TYPE_NAME'] + ': ' + parsed_content['ORG_NAME']
    organizations = parsed_content[['UUID', 'FULL_ORG_NAME', 'PARENT_UUID']].copy(deep=True)
    organizations.dropna(axis=0, how='all', inplace=True)
    organizations.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    organizations['url_main1'] = organizations[['UUID']].apply(
                                 lambda row: create_pure_url('PureUUid-org', row['UUID']), axis=1)
    organizations.rename(columns={'UUID': 'value1',
                                  'FULL_ORG_NAME': 'comment1',
                                  'PARENT_UUID': 'value2'}, inplace=True)
    new_organization_columns = {'name1': 'PureUUid-org',
                                'category1': 'organization',
                                'history_event1': history_event,
                                'name2': 'PureUUid-org',
                                'category2': 'organization',
                                'history_event2': history_event}
    organizations = organizations.assign(**new_organization_columns)
    organizations = organizations[['name1', 'category1', 'value1', 'history_event1', 'comment1', 'url_main1',
                                   'name2', 'category2', 'value2', 'history_event2']]

    print('The following organizations from Pure will be inserted in Ricgraph:')
    print(organizations)
    rcg.create_nodepairs_and_edges_df(organizations)
    print('\nDone.\n')
    return


def parsed_resout_to_ricgraph(parsed_content: pandas.DataFrame) -> None:
    """Insert the parsed research outputs in Ricgraph.

    :param parsed_content: The records to insert in Ricgraph, if not present yet.
    :return: None.
    """
    print('Inserting research outputs from Pure in Ricgraph...')
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    history_event = 'Source: Harvest Pure research outputs at ' + timestamp + '.'

    resout = parsed_content[['RESOUT_UUID', 'TITLE', 'TYPE', 'DOI', 'PERSON_UUID']].copy(deep=True)
    resout.dropna(axis=0, how='all', inplace=True)
    resout.drop_duplicates(keep='first', inplace=True, ignore_index=True)

    # A number of research outputs in Pure have a DOI, but not all. We prefer the DOI above PureUUid-resout.
    # So if there is a DOI, use it, otherwise use PureUUid-resout UUID. Some shuffling is required.
    # First, fill the column 'name1' with 'DOI', unless the value is '', then fill with 'PureUUid-resout'.
    resout['name1'] = resout[['DOI']].apply(lambda x: 'PureUUid-resout' if x.item() == '' else 'DOI', axis=1)
    # Make sure we have the correct URL.
    resout['url_main1'] = resout[['name1', 'DOI', 'RESOUT_UUID']].apply(
                          lambda row: create_urlmain(row['name1'], row['DOI'], row['RESOUT_UUID']), axis=1)
    resout['url_other1'] = resout[['name1', 'DOI', 'RESOUT_UUID']].apply(
                           lambda row: create_urlother(row['name1'], row['RESOUT_UUID']), axis=1)
    # Now replace all empty strings in column DOI for NaNs
    resout['DOI'].replace('', numpy.nan, inplace=True)
    # Then fill the column 'value1' with the value from column DOI, unless the value is NaN,
    # then fill with the value from column RESOUT_UUID.
    resout['value1'] = resout['DOI'].copy(deep=True)
    resout.value1.fillna(resout['RESOUT_UUID'], inplace=True)

    resout.rename(columns={'TYPE': 'category1',
                           'TITLE': 'comment1',
                           'PERSON_UUID': 'value2'}, inplace=True)
    new_resout_columns = {'history_event1': history_event,
                          'name2': 'PureUUid-pers',
                          'category2': 'person'}
    resout = resout.assign(**new_resout_columns)
    resout = resout[['name1', 'category1', 'value1', 'history_event1', 'comment1', 'url_main1', 'url_other1',
                     'name2', 'category2', 'value2']]

    print('The following research outputs from Pure will be inserted in Ricgraph:')
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
    PURE_URL = config['Pure_harvesting']['pure_url']
    PURE_API_KEY = config['Pure_harvesting']['pure_api_key']
    PURE_HEADERS['api-key'] = PURE_API_KEY
except KeyError:
    print('Error, Pure URL or Pure API key not found in Ricgraph ini file, exiting.')
    exit(1)

print('\nPreparing graph...')
rcg.open_ricgraph()

# Empty Ricgraph, choose one of the following.
# rcg.empty_ricgraph(answer='yes')
# rcg.empty_ricgraph(answer='no')
rcg.empty_ricgraph()

# You can use 'True' or 'False' depending on your needs to harvest persons/organizations/research outputs.
# This might be handy if you are testing your parsing.

# if False:
if True:
    parse_persons = harvest_and_parse_pure_data(mode='persons',
                                                endpoint=PURE_PERSONS_ENDPOINT,
                                                headers=PURE_HEADERS,
                                                body=PURE_PERSONS_FIELDS,
                                                harvest_filename=PURE_PERSONS_HARVEST_FILENAME)
    if parse_persons is None:
        print('There are no persons from Pure to harvest.\n')
    else:
        rcg.write_dataframe_to_csv(PURE_PERSONS_DATA_FILENAME, parse_persons)
        parsed_persons_to_ricgraph(parse_persons)


# if False:
if True:
    parse_organizations = harvest_and_parse_pure_data(mode='organizations',
                                                      endpoint=PURE_ORGANIZATIONS_ENDPOINT,
                                                      headers=PURE_HEADERS,
                                                      body=PURE_ORGANIZATIONS_FIELDS,
                                                      harvest_filename=PURE_ORGANIZATIONS_HARVEST_FILENAME)
    if parse_organizations is None:
        print('There are no organizations from Pure to harvest.\n')
    else:
        rcg.write_dataframe_to_csv(PURE_ORGANIZATIONS_DATA_FILENAME, parse_organizations)
        parsed_organizations_to_ricgraph(parse_organizations)


# if False:
if True:
    for year in PURE_RESOUT_YEARS:
        print('Harvesting research outputs from Pure for year ' + year + '.')
        harvest_filename_year = PURE_RESOUT_HARVEST_FILENAME.split('.')[0] \
                                + '-' + year + '.' \
                                + PURE_RESOUT_HARVEST_FILENAME.split('.')[1]
        data_filename_year = PURE_RESOUT_DATA_FILENAME.split('.')[0] \
                             + '-' + year + '.' \
                             + PURE_RESOUT_DATA_FILENAME.split('.')[1]
        PURE_RESOUT_FIELDS['publishedBeforeDate'] = year + '-12-31'
        PURE_RESOUT_FIELDS['publishedAfterDate'] = year + '-01-01'
        parse_resout = harvest_and_parse_pure_data(mode='research outputs',
                                                   endpoint=PURE_RESOUT_ENDPOINT,
                                                   headers=PURE_HEADERS,
                                                   body=PURE_RESOUT_FIELDS,
                                                   harvest_filename=harvest_filename_year)
        if parse_resout is None:
            print('There are no research outputs from Pure to harvest.\n')
        else:
            rcg.write_dataframe_to_csv(data_filename_year, parse_resout)
            parsed_resout_to_ricgraph(parse_resout)

rcg.close_ricgraph()
