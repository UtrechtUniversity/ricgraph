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
# With this code, you can harvest persons, organizations and research outputs from Pure,
# using both the READ API as well as the CRUD API. You don't need to specify this,
# the script will know.
# I would recommend to use the READ API, since the CRUD API is in development and does not have
# filters on e.g. active persons yet. Neither does it allow harvesting of research outputs
# for one year only, so you might hit memory bounds if you harvest every research output
# for all years with the CRUD API.
#
# In Pure, organizations are hierarchical. That means, an organization has a parent org,
# which has a parent org, up until a root org.
# At the end of this script, a person (i.e. its person-root node) will be connected to
# all of these hierarchical orgs.
#
# You have to set some parameters in ricgraph.ini.
# Also, you can set a number of parameters in the code following the "import" statements below.
#
# Original version Rik D.T. Janssen, December 2022.
# Updated Rik D.T. Janssen, April, October, November 2023, February 2025.
# Updated Rik D.T. Janssen, February 2026.
#
# ########################################################################
#
# Usage
# harvest_pure_to_ricgraph.py [options]
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
#   --year_first <first year of harvest>
#           Start the harvest from this year on.
#   --year_last <last year of harvest>
#           End the harvest at this year.
#   --harvest_projects <yes|no>
#           'yes': projects will be harvested.
#           'no' (or any other answer): projects will not be harvested.
#           If this option is not present, projects will not be harvested,
#           the script will not prompt the user.
#
# ########################################################################


import sys
import pandas
import numpy
from typing import Union
import requests
import pathlib
import ricgraph as rcg
from ricgraph import construct_extended_org_name

# ######################################################
# General parameters for harvesting from Pure.
# Documentation Pure API: PURE_URL/ws/api/524/api-docs/index.html
# ######################################################
# Pure can be harvested according to the READ or CRUD API.
global PURE_API_VERSION
PURE_READ_API_VERSION = 'ws/api/524'
PURE_CRUD_API_VERSION = 'ws/api'
PURE_CHUNKSIZE = 500
PURE_HEADERS = {'Accept': 'application/json'
                # The following will be read in __main__
                # 'api-key': PURE_API_KEY
                }
global PURE_URL
global HARVEST_SOURCE
global HARVEST_PROJECTS
global resout_uuid_or_doi

# ######################################################
# Parameters for harvesting persons from Pure
# ######################################################
# Pure can be harvested according to the READ or CRUD API.
global PURE_PERSONS_ENDPOINT
PURE_READ_PERSONS_ENDPOINT = 'persons'
PURE_CRUD_PERSONS_ENDPOINT = 'persons/search'

# Set this to True to simulate the harvest. If True, do not harvest, but read it from a file.
PURE_PERSONS_READ_HARVEST_FROM_FILE = False
# PURE_PERSONS_READ_HARVEST_FROM_FILE = True
PURE_PERSONS_HARVEST_FILENAME = 'pure_persons_harvest.json'

# Set this to True to read data from the csv file. No harvest will be done, this would
# not make sense. If False, a harvest will be done.
# If True, the value of PURE_PERSONS_READ_HARVEST_FROM_FILE does not matter.
PURE_PERSONS_READ_DATA_FROM_FILE = False
# PURE_PERSONS_READ_DATA_FROM_FILE = True
PURE_PERSONS_DATA_FILENAME = 'pure_persons_data.csv'

PURE_PERSONS_MAX_RECS_TO_HARVEST = 0                  # 0 = all records
# The current version of the Pure CRUD API does not have these filters yet.
PURE_PERSONS_FIELDS = {'fields': ['uuid',
                                  'name.*',
                                  'ids.*',
                                  'staffOrganisationAssociations.period.*',
                                  'staffOrganisationAssociations.organisationalUnit.*',
                                  'orcid'
                                  ]
                       # See remark below.
                       # 'employmentStatus': 'ACTIVE'
                       }

# For the Pure READ API.
# We harvest all persons from Pure, whether they are active or not. We do this,
# because persons not active might have contributed to a research output.
# But we only add these persons if their endDate is within
# PURE_PERSONS_INCLUDE_YEARS_BEFORE years before the lowest value in PURE_RESOUT_YEARS.
# Otherwise, we may end up with far too many persons.
#
# Sept 2024: In 2023 I thought not to add the organization of such a person
# because it seemed very probably outdated.
# But it appears that some organizations use an endDate in the future (instead
# of no endDate) for persons employed.
# So we do need to add the organization of these persons.
PURE_PERSONS_INCLUDE_YEARS_BEFORE = 5
# For the Pure CRUD API we use this value, because we cannot filter research
# outputs on years.
PURE_PERSONS_LOWEST_YEAR = 2010

# ######################################################
# Parameters for harvesting organizations from Pure
# ######################################################
# Pure can be harvested according to the READ or CRUD API.
global PURE_ORGANIZATIONS_ENDPOINT
PURE_READ_ORGANIZATIONS_ENDPOINT = 'organisational-units'
PURE_CRUD_ORGANIZATIONS_ENDPOINT = 'organizations/search'

# Set this to True to simulate the harvest. If True, do not harvest, but read it from a file.
PURE_ORGANIZATIONS_READ_HARVEST_FROM_FILE = False
# PURE_ORGANIZATIONS_READ_HARVEST_FROM_FILE = True
PURE_ORGANIZATIONS_HARVEST_FILENAME = 'pure_organizations_harvest.json'

# Set this to True to read data from the csv file. No harvest will be done, this would
# not make sense. If False, a harvest will be done.
# If True, the value of PURE_ORGANIZATIONS_READ_HARVEST_FROM_FILE does not matter.
PURE_ORGANIZATIONS_READ_DATA_FROM_FILE = False
# PURE_ORGANIZATIONS_READ_DATA_FROM_FILE = True
PURE_ORGANIZATIONS_DATA_FILENAME = 'pure_organizations_data.csv'

PURE_ORGANIZATIONS_MAX_RECS_TO_HARVEST = 0                  # 0 = all records
# The current version of the Pure CRUD API does not have these filters yet.
PURE_ORGANIZATIONS_FIELDS = {'fields': ['uuid',
                                        'period.*',
                                        'name.*',
                                        'type.*',
                                        'ids.*',
                                        'parents.*'
                                        ]
                             }

# ######################################################
# Parameters for harvesting research outputs from Pure
# ######################################################
# Pure can be harvested according to the READ or CRUD API.
global PURE_RESOUT_ENDPOINT
PURE_READ_RESOUT_ENDPOINT = 'research-outputs'
PURE_CRUD_RESOUT_ENDPOINT = 'research-outputs/search'

# Set this to True to simulate the harvest. If True, do not harvest, but read it from a file.
PURE_RESOUT_READ_HARVEST_FROM_FILE = False
# PURE_RESOUT_READ_HARVEST_FROM_FILE = True
PURE_RESOUT_HARVEST_FILENAME = 'pure_resout_harvest.json'

# Set this to True to read data from the csv file. No harvest will be done, this would
# not make sense. If False, a harvest will be done.
# Make sure PURE_READ_RESOUT_YEARS or PURE_CRUD_RESOUT_YEARS has been set correctly.
# If True, the value of PURE_RESOUT_READ_HARVEST_FROM_FILE does not matter.
PURE_RESOUT_READ_DATA_FROM_FILE = False
# PURE_RESOUT_READ_DATA_FROM_FILE = True
PURE_RESOUT_DATA_FILENAME = 'pure_resout_data.csv'

# For Pure READ API: this number is the max recs to harvest per year, not total
# For Pure CRUD API: this number is the max recs to harvest total.
PURE_RESOUT_MAX_RECS_TO_HARVEST = 0                  # 0 = all records
global PURE_RESOUT_FIELDS
# The current version of the Pure CRUD API does not have these filters yet.
PURE_READ_RESOUT_FIELDS = {'fields': ['uuid',
                                      'title.*',
                                      'confidential',
                                      'type.*',
                                      'workflow.*',
                                      'publicationStatuses.*',
                                      'personAssociations.*',
                                      'electronicVersions.*'
                                      ]
                           }
PURE_CRUD_RESOUT_FIELDS = {'orderings': ['publicationYear'],
                           'orderBy': 'descending'
                           }

# ######################################################
# Parameters for harvesting projects from Pure
# ######################################################
# Pure can be harvested according to the READ or CRUD API.
# However, for projects we only harvest them using the READ API.
global PURE_PROJECTS_ENDPOINT
PURE_READ_PROJECTS_ENDPOINT = 'projects'
# PURE_CRUD_PROJECTS_ENDPOINT = 'projects/search'

# Set this to True to simulate the harvest. If True, do not harvest, but read it from a file.
PURE_PROJECTS_READ_HARVEST_FROM_FILE = False
# PURE_PROJECTS_READ_HARVEST_FROM_FILE = True
PURE_PROJECTS_HARVEST_FILENAME = 'pure_projects_harvest.json'

# Set this to True to read data from the csv file. No harvest will be done, this would
# not make sense. If False, a harvest will be done.
# If True, the value of PURE_PROJECTS_READ_HARVEST_FROM_FILE does not matter.
PURE_PROJECTS_READ_DATA_FROM_FILE = False
# PURE_PROJECTS_READ_DATA_FROM_FILE = True
PURE_PROJECTS_DATA_FILENAME = 'pure_projects_data.csv'

PURE_PROJECTS_MAX_RECS_TO_HARVEST = 0                  # 0 = all records
# The current version of the Pure CRUD API does not have these filters yet.
PURE_PROJECTS_FIELDS = {'fields': ['uuid',
                                   'period.*',
                                   'confidential',
                                   'title.*',
                                   'status.*',
                                   'visibility.*',
                                   'workflow.*',
                                   'descriptions.*',
                                   'ids.*',
                                   'participants.person.uuid.*',
                                   'participants.organisationalUnits.uuid.*',
                                   # 'managingOrganisationalUnit.*', # We use the organization of the participant.
                                   # 'organizationalUnits.*',       # We use the organization of the participant.
                                   # 'collaborators.*',             # These are other organizations, skip.
                                   'relatedResearchOutputs.uuid.*',
                                   'relatedResearchOutputs.type.*',
                                   'relatedProjects.project.uuid.*',
                                   # 'relatedDataSets.*',           # Datasets are supposed to be in research outputs.
                                   # 'relatedActivities.*',
                                   # 'relatedPrizes.*',
                                   # 'relatedPressMedia.*',
                                   ]
                        }


# ######################################################
# Mapping from Pure research output types to Ricgraph research output types.
# ######################################################
ROTYPE_PREFIX_PURE = '/dk/atira/pure/researchoutput/researchoutputtypes/'
ROTYPE_MAPPING_PURE = {
    ROTYPE_PREFIX_PURE + 'bookanthology/anthology': rcg.ROTYPE_BOOK,
    ROTYPE_PREFIX_PURE + 'bookanthology/book': rcg.ROTYPE_BOOK,
    ROTYPE_PREFIX_PURE + 'bookanthology/commissioned': rcg.ROTYPE_BOOK,
    ROTYPE_PREFIX_PURE + 'bookanthology/inaugural': rcg.ROTYPE_BOOK,
    ROTYPE_PREFIX_PURE + 'bookanthology/registered_report': rcg.ROTYPE_REGISTERED_REPORT,
    ROTYPE_PREFIX_PURE + 'bookanthology/valedictory': rcg.ROTYPE_BOOK,
    ROTYPE_PREFIX_PURE + 'contributiontobookanthology/case_note': rcg.ROTYPE_MEMORANDUM,
    ROTYPE_PREFIX_PURE + 'contributiontobookanthology/chapter': rcg.ROTYPE_BOOKCHAPTER,
    ROTYPE_PREFIX_PURE + 'contributiontobookanthology/commissioned': rcg.ROTYPE_BOOKCHAPTER,
    ROTYPE_PREFIX_PURE + 'contributiontobookanthology/conference': rcg.ROTYPE_BOOKCHAPTER,
    ROTYPE_PREFIX_PURE + 'contributiontobookanthology/entry': rcg.ROTYPE_ENTRY,
    ROTYPE_PREFIX_PURE + 'contributiontobookanthology/foreword': rcg.ROTYPE_ABSTRACT,
    ROTYPE_PREFIX_PURE + 'contributiontoconference/abstract': rcg.ROTYPE_ABSTRACT,
    ROTYPE_PREFIX_PURE + 'contributiontoconference/other': rcg.ROTYPE_CONFERENCE_ARTICLE,
    ROTYPE_PREFIX_PURE + 'contributiontoconference/paper': rcg.ROTYPE_CONFERENCE_ARTICLE,
    ROTYPE_PREFIX_PURE + 'contributiontoconference/poster': rcg.ROTYPE_POSTER,
    ROTYPE_PREFIX_PURE + 'contributiontojournal/abstract': rcg.ROTYPE_ABSTRACT,
    ROTYPE_PREFIX_PURE + 'contributiontojournal/article': rcg.ROTYPE_JOURNAL_ARTICLE,
    ROTYPE_PREFIX_PURE + 'contributiontojournal/book': rcg.ROTYPE_BOOK,
    ROTYPE_PREFIX_PURE + 'contributiontojournal/case_note': rcg.ROTYPE_MEMORANDUM,
    ROTYPE_PREFIX_PURE + 'contributiontojournal/comment': rcg.ROTYPE_MEMORANDUM,
    ROTYPE_PREFIX_PURE + 'contributiontojournal/conferencearticle': rcg.ROTYPE_CONFERENCE_ARTICLE,
    ROTYPE_PREFIX_PURE + 'contributiontojournal/editorial': rcg.ROTYPE_EDITORIAL,
    ROTYPE_PREFIX_PURE + 'contributiontojournal/erratum': rcg.ROTYPE_MEMORANDUM,
    ROTYPE_PREFIX_PURE + 'contributiontojournal/letter': rcg.ROTYPE_LETTER,
    ROTYPE_PREFIX_PURE + 'contributiontojournal/scientific': rcg.ROTYPE_JOURNAL_ARTICLE,
    ROTYPE_PREFIX_PURE + 'contributiontojournal/shortsurvey': rcg.ROTYPE_JOURNAL_ARTICLE,
    ROTYPE_PREFIX_PURE + 'contributiontojournal/special': rcg.ROTYPE_JOURNAL_ARTICLE,
    ROTYPE_PREFIX_PURE + 'contributiontojournal/systematicreview': rcg.ROTYPE_REVIEW,
    ROTYPE_PREFIX_PURE + 'memorandum/academicmemorandum': rcg.ROTYPE_MEMORANDUM,
    ROTYPE_PREFIX_PURE + 'methoddescription': rcg.ROTYPE_METHOD_DESCRIPTION,
    ROTYPE_PREFIX_PURE + 'nontextual/artefact': rcg.ROTYPE_ARTEFACT,
    ROTYPE_PREFIX_PURE + 'nontextual/database': rcg.ROTYPE_DATASET,
    ROTYPE_PREFIX_PURE + 'nontextual/design': rcg.ROTYPE_DESIGN,
    ROTYPE_PREFIX_PURE + 'nontextual/digitalorvisualproducts': rcg.ROTYPE_DIGITAL_VISUAL_PRODUCT,
    ROTYPE_PREFIX_PURE + 'nontextual/exhibition': rcg.ROTYPE_EXHIBITION_PERFORMANCE,
    ROTYPE_PREFIX_PURE + 'nontextual/performance': rcg.ROTYPE_EXHIBITION_PERFORMANCE,
    ROTYPE_PREFIX_PURE + 'nontextual/software': rcg.ROTYPE_SOFTWARE,
    ROTYPE_PREFIX_PURE + 'nontextual/web': rcg.ROTYPE_WEBSITE,
    ROTYPE_PREFIX_PURE + 'othercontribution/other': rcg.ROTYPE_OTHER_CONTRIBUTION,
    ROTYPE_PREFIX_PURE + 'patent/patent': rcg.ROTYPE_PATENT,
    ROTYPE_PREFIX_PURE + 'thesis/doc1': rcg.ROTYPE_PHDTHESIS,
    ROTYPE_PREFIX_PURE + 'thesis/doc2': rcg.ROTYPE_PHDTHESIS,
    ROTYPE_PREFIX_PURE + 'thesis/doc3': rcg.ROTYPE_PHDTHESIS,
    ROTYPE_PREFIX_PURE + 'thesis/doc4': rcg.ROTYPE_PHDTHESIS,
    ROTYPE_PREFIX_PURE + 'workingpaper/discussionpaper': rcg.ROTYPE_PREPRINT,
    ROTYPE_PREFIX_PURE + 'workingpaper/preprint': rcg.ROTYPE_PREPRINT,
    ROTYPE_PREFIX_PURE + 'workingpaper/workingpaper': rcg.ROTYPE_PREPRINT
}


# ######################################################
# Utility functions related to harvesting of Pure
# ######################################################

def create_pure_url(name: str, value: str) -> str:
    """Create a URL to refer to the source of a node.

    :param name: an identifier name, e.g. PURE_UUID_PERS, PURE_UUID_ORG, etc.
    :param value: the value.
    :return: a URL.
    """
    if name == '' or value == '':
        return ''

    if name == 'PURE_UUID_PERS':
        return PURE_URL + '/en/persons/' + value
    elif name == 'PURE_UUID_ORG':
        return PURE_URL + '/en/organisations/' + value
    elif name == 'PURE_UUID_RESOUT':
        return PURE_URL + '/en/publications/' + value
    elif name == 'PURE_UUID_PROJECT':
        return PURE_URL + '/en/projects/' + value
    else:
        return ''


def create_urlmain(type_id: str, doi_value: str, uuid_value: str) -> str:
    """A helper function for parsed_resout_to_ricgraph()"""
    if type_id == 'DOI':
        return rcg.create_well_known_url(name=type_id,
                                         value=doi_value)
    elif type_id == 'PURE_UUID_RESOUT':
        return create_pure_url(name=type_id,
                               value=uuid_value)
    else:
        # Should not happen
        print('create_urlmain(): error')
    return ''


def create_urlother(type_id: str, uuid_value: str) -> str:
    """A helper function for parsed_resout_to_ricgraph()"""
    if type_id == 'DOI':
        return create_pure_url(name='PURE_UUID_RESOUT',
                               value=uuid_value)
    else:
        return ''


def find_organization_name(uuid: str, organization_names: dict):
    """Find the full organization name which belongs to an organization with a certain UUID.

    :param uuid: the UUID.
    :param organization_names: the dict with organization names.
    :return: the full organization name.
    """
    if uuid in organization_names:
        return str(organization_names[uuid])
    else:
        return 'Organization name not found for UUID ' + uuid + '.'


# ######################################################
# Parsing
# ######################################################

def restructure_parse_persons(df: pandas.DataFrame) -> pandas.DataFrame:
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

    if 'ORCID' not in df_mod.columns:
        df_mod['ORCID'] = ''

    if 'ISNI' not in df_mod.columns:
        df_mod['ISNI'] = ''

    if 'Scopus Author ID' in df_mod.columns:
        df_mod.rename(columns={'Scopus Author ID': 'SCOPUS_AUTHOR_ID'}, inplace=True)
    else:
        df_mod['SCOPUS_AUTHOR_ID'] = ''

    if 'Researcher ID' in df_mod.columns:
        df_mod.rename(columns={'Researcher ID': 'RESEARCHER_ID'}, inplace=True)
    else:
        df_mod['RESEARCHER_ID'] = ''

    if 'Digital author ID' in df_mod.columns:
        df_mod.rename(columns={'Digital author ID': 'DIGITAL_AUTHOR_ID'}, inplace=True)
    else:
        df_mod['DIGITAL_AUTHOR_ID'] = ''

    if 'Employee ID' in df_mod.columns:
        df_mod.rename(columns={'Employee ID': 'EMPLOYEE_ID'}, inplace=True)
    else:
        df_mod['EMPLOYEE_ID'] = ''

    return df_mod


def restructure_parse_projects(df: pandas.DataFrame) -> pandas.DataFrame:
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

    if 'PURE_PROJECT_PARTICIPANT_UUID' not in df_mod.columns:
        df_mod['PURE_PROJECT_PARTICIPANT_UUID'] = ''

    return df_mod


def parse_pure_persons(harvest: list,
                       filename: str = '',
                       year_start: str = '') -> Union[pandas.DataFrame, None]:
    """Parse the harvested persons from Pure.
    In case filename != '', write it to a file and read it back.

    :param harvest: the harvest.
    :param filename: If filename != '', write it to a file and read it back.
    :param year_start: the first year that we would like to harvest.
    :return: the harvested persons in a DataFrame, or None if nothing to parse.
    """
    if len(harvest) == 0:
        return None
    if year_start == '':
        print('parse_pure_persons(): Invalid value for "year_start" passed, exiting.')
        exit(1)

    if PURE_API_VERSION == PURE_READ_API_VERSION:
        # We use the Pure READ API.
        lowest_resout_year = int(year_start) - PURE_PERSONS_INCLUDE_YEARS_BEFORE
    else:
        lowest_resout_year = PURE_PERSONS_LOWEST_YEAR

    # parse_chunk_final: things we want to put in the DataFrame parse_result with
    # harvested persons to be returned.
    parse_chunk_final = []
    parse_result = pandas.DataFrame()
    print('There are ' + str(len(harvest)) + ' person records ('
          + rcg.timestamp() + '), parsing record: 0  ', end='')
    count = 0
    for harvest_item in harvest:
        # parse_chunk: things of this loop we might want to put in the DataFrame with
        # harvested persons to be returned. If so, we add them to parse_chunk_final.
        # If not they will not end up in the harvested persons.
        parse_chunk = []
        count += 1
        if count % 1000 == 0:
            print(count, ' ', end='', flush=True)
        if count % 10000 == 0:
            print('(' + rcg.timestamp() + ')\n', end='', flush=True)

        if 'uuid' not in harvest_item:
            # There must be an uuid, otherwise skip
            continue
        if 'name' in harvest_item:
            if 'lastName' in harvest_item['name']:
                parse_line = {'PURE_UUID_PERS': str(harvest_item['uuid']),
                              'FULL_NAME': harvest_item['name']['lastName']}
                if 'firstName' in harvest_item['name']:
                    parse_line['FULL_NAME'] += ', ' + harvest_item['name']['firstName']
                parse_chunk.append(parse_line)
        if 'orcid' in harvest_item:
            parse_line = {'PURE_UUID_PERS': str(harvest_item['uuid']),
                          'ORCID': str(harvest_item['orcid'])}
            parse_chunk.append(parse_line)
        if 'ids' in harvest_item:
            # Field in Pure READ API.
            for identities in harvest_item['ids']:
                if 'value' in identities and 'type' in identities:
                    value_identifier = str(identities['value']['value'])
                    name_identifier = str(identities['type']['term']['text'][0]['value'])
                    parse_line = {'PURE_UUID_PERS': str(harvest_item['uuid']),
                                  name_identifier: value_identifier}
                    parse_chunk.append(parse_line)
        if 'identifiers' in harvest_item:
            # Field in Pure CRUD API.
            for identities in harvest_item['identifiers']:
                if 'id' in identities and 'type' in identities:
                    value_identifier = str(identities['id'])
                    name_identifier = str(identities['type']['term']['en_GB'])
                    parse_line = {'PURE_UUID_PERS': str(harvest_item['uuid']),
                                  name_identifier: value_identifier}
                    parse_chunk.append(parse_line)
        label = ''
        if 'staffOrganisationAssociations' in harvest_item:
            # Field in Pure READ API.
            label = 'staffOrganisationAssociations'
        elif 'staffOrganizationAssociations' in harvest_item:
            # Field in Pure CRUD API.
            label = 'staffOrganizationAssociations'
        if label != '':
            for stafforg in harvest_item[label]:
                if 'period' in stafforg:
                    if 'endDate' in stafforg['period'] and stafforg['period']['endDate'] != '':
                        # Only consider persons of current organizations, that is an organization
                        # where endData is not existing or empty. If not, then skip.
                        end_year = int(stafforg['period']['endDate'][:4])
                        if end_year < lowest_resout_year:
                            continue
                        # else:
                        #     # In 2023:
                        #     # Put in the DataFrame with harvested persons to be returned.
                        #     # We do not add its organization because it is very probably outdated.
                        #     # No need to check if it is already there, it that is the case it will
                        #     # be filtered out from the dataframe below.
                        #     #
                        #     # Sept 2024: In 2023 I thought not to add the organization of such a person
                        #     # because it seemed very probably outdated.
                        #     # But it appears that some organizations use an endDate in the future (instead
                        #     # of no endDate) for persons employed.
                        #     # So we do need to add the organization of these persons.
                        #     # So I commented this 'else'.
                        #     parse_chunk_final.extend(parse_chunk)
                        #     continue
                else:
                    # If there is no period skip
                    continue

                if 'organisationalUnit' in stafforg:
                    # Field in Pure READ API.
                    orgunit = stafforg['organisationalUnit']
                    if 'type' in orgunit:
                        pure_org_uri = str(orgunit['type']['uri'])
                        if pure_org_uri[-3] == 'r':
                            # Skip research organizations (with an 'r' in the uri, like ..../r05)
                            continue
                elif 'organization' in stafforg:
                    # Field in Pure CRUD API.
                    orgunit = stafforg['organization']
                    # We don't have the 'type' in Pure CRUD API.
                else:
                    continue

                parse_line = {'PURE_UUID_PERS': str(harvest_item['uuid']),
                              'PURE_UUID_ORG': str(orgunit['uuid'])}
                parse_chunk.append(parse_line)

                # Put in the DataFrame with harvested persons to be returned.
                parse_chunk_final.extend(parse_chunk)

    print(count, '(' + rcg.timestamp() + ')\n', end='', flush=True)

    parse_chunk_df = pandas.DataFrame(parse_chunk_final)
    parse_result = pandas.concat([parse_result, parse_chunk_df], ignore_index=True)

    if 'PURE_UUID_ORG' not in parse_result.columns \
       and PURE_API_VERSION == PURE_CRUD_API_VERSION:
        print('\nPure is harvested using the Pure CRUD API.')
        print('Persons found are not members of any organization.')
        print('This is probably caused by field "staffOrganizationAssociations" not present in')
        print('the CRUD API export for "persons".')
        print('Please ask your Pure administrator to export this field. Exiting.')
        exit(1)

    parse_result = restructure_parse_persons(df=parse_result)
    return rcg.normalize_identifiers_write_read(parse_result=parse_result,
                                                filename=filename)


def parse_pure_organizations(harvest: list,
                             filename: str = '') -> Union[pandas.DataFrame, None]:
    """Parse the harvested organizations from Pure.
    In case filename != '', write it to a file and read it back.

    :param harvest: the harvest.
    :param filename: If filename != '', write it to a file and read it back.
    :return: the harvested organizations in a DataFrame,
        or None if nothing to parse.
    """
    global organization

    if len(harvest) == 0:
        return None
    parse_result = pandas.DataFrame()
    parse_chunk = []                # list of dictionaries
    organization_names = {}
    print('There are ' + str(len(harvest)) + ' organization records ('
          + rcg.timestamp() + '), parsing record: 0  ', end='')
    count = 0
    for harvest_item in harvest:
        count += 1
        if count % 1000 == 0:
            print(count, ' ', end='', flush=True)
        if count % 10000 == 0:
            print('(' + rcg.timestamp() + ')\n', end='', flush=True)

        if 'uuid' not in harvest_item:
            # There must be an uuid, otherwise skip
            continue
        label = ''
        if 'period' in harvest_item:
            # Field in Pure READ API.
            label = 'period'
        elif 'lifecycle' in harvest_item:
            # Field in Pure CRUD API.
            label = 'lifecycle'
        if label != '':
            if 'endDate' in harvest_item[label] and harvest_item[label]['endDate'] != '':
                # Only consider current organizations, that is an organization
                # where endDate is not existing or empty. If not, then skip.
                continue
        else:
            # If there is no period or lifecycle skip
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
                # Note: 'type' and 'name' must exist, otherwise we wouldn't have gotten here.
                if 'type' in parentsorg:
                    # Field in Pure READ API.
                    pure_parentsorg_uri = str(parentsorg['type']['uri'])
                    if pure_parentsorg_uri[-3] == 'r':
                        # Skip research organizations (with an 'r' in the uri, like ..../r05)
                        continue

                    org_type_name = str(harvest_item['type']['term']['text'][0]['value'])
                    org_name = str(harvest_item['name']['text'][0]['value'])
                elif 'systemName' in parentsorg:
                    # Field in Pure CRUD API.
                    org_type_name = str(harvest_item['type']['term']['en_GB'])
                    org_name = str(harvest_item['name']['en_GB'])
                else:
                    continue

                parse_line = {'PURE_UUID_ORG': str(harvest_item['uuid']),
                              'ORG_TYPE_NAME': org_type_name,
                              'ORG_NAME': org_name,
                              'FULL_ORG_NAME': organization + ' ' + org_type_name + ': ' + org_name,
                              'PARENT_UUID': str(parentsorg['uuid'])}
                parse_chunk.append(parse_line)
                organization_names[parse_line['PURE_UUID_ORG']] = parse_line['FULL_ORG_NAME']
        else:
            # Assume it is the top level organization since it doesn't have a parent.
            # Note: 'type' and 'name' must exist, otherwise we wouldn't have gotten here.
            if PURE_API_VERSION == PURE_READ_API_VERSION:
                # We are in Pure READ API.
                # org_type_name = str(harvest_item['type']['term']['text'][0]['value'])
                org_name = str(harvest_item['name']['text'][0]['value'])
            else:
                # We are in Pure CRUD API.
                # org_type_name = str(harvest_item['type']['term']['en_GB'])
                org_name = str(harvest_item['name']['en_GB'])
            # Only necessary to add the top level organization to the dict with organization names.
            # organization_names[str(harvest_item['uuid'])] = org_type_name + ': ' + org_name
            # organization_names[str(harvest_item['uuid'])] = organization + ' ' + org_type_name + ': ' + org_name
            organization_names[str(harvest_item['uuid'])] = construct_extended_org_name(org_name=org_name,
                                                                                        org_abbr=organization)

    print(count, '(' + rcg.timestamp() + ')\n', end='', flush=True)

    parse_chunk_df = pandas.DataFrame(parse_chunk)
    parse_result = pandas.concat([parse_result, parse_chunk_df], ignore_index=True)
    parse_result['FULL_PARENT_NAME'] = (
        parse_result[['PARENT_UUID']].apply(lambda row:
                                            find_organization_name(uuid=row['PARENT_UUID'],
                                                                   organization_names=organization_names),
                                            axis=1))
    return rcg.normalize_identifiers_write_read(parse_result=parse_result,
                                                filename=filename)


def parse_pure_resout(harvest: list,
                      filename: str = '') -> Union[pandas.DataFrame, None]:
    """Parse the harvested research outputs from Pure.
    In case filename != '', write it to a file and read it back.

    :param harvest: the harvest.
    :param filename: If filename != '', write it to a file and read it back.
    :return: the harvested research outputs in a DataFrame,
        or None if nothing to parse.
    """
    global organization

    if len(harvest) == 0:
        return None
    parse_result = pandas.DataFrame()
    parse_chunk = []                # list of dictionaries
    print('There are ' + str(len(harvest)) + ' research output records ('
          + rcg.timestamp() + '), parsing record: 0  ', end='')
    count = 0
    for harvest_item in harvest:
        count += 1
        if count % 1000 == 0:
            print(count, ' ', end='', flush=True)
        if count % 10000 == 0:
            print('(' + rcg.timestamp() + ')\n', end='', flush=True)

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
            if 'workflowStep' in harvest_item['workflow']:
                # Field in Pure READ API.
                if harvest_item['workflow']['workflowStep'] != 'validated' \
                   and harvest_item['workflow']['workflowStep'] != 'approved':
                    # Only 'validated' or 'approved' resouts.
                    continue
            if 'step' in harvest_item['workflow']:
                # Field in Pure CRUD API.
                if harvest_item['workflow']['step'] != 'validated' \
                        and harvest_item['workflow']['step'] != 'approved':
                    # Only 'validated' or 'approved' resouts.
                    continue
        else:
            # Skip if no workflow
            continue
        publication_year = ''
        if 'publicationStatuses' in harvest_item:
            # We need a current status.
            published_found = False
            for pub_item in harvest_item['publicationStatuses']:
                if pub_item['current']:
                    if 'publicationDate' in pub_item:
                        if 'year' in pub_item['publicationDate']:
                            publication_year = pub_item['publicationDate']['year']
                    if 'publicationStatus' in pub_item:
                        if pathlib.PurePath(pub_item['publicationStatus']['uri']).name == 'published':
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
                    doi = rcg.normalize_doi(identifier=doi)

        label = ''
        if 'personAssociations' in harvest_item:
            # Field in Pure READ API.
            label = 'personAssociations'
        elif 'contributors' in harvest_item:
            # Field in Pure CRUD API.
            label = 'contributors'
        if label != '':
            for persons in harvest_item[label]:
                author_name = ''
                author_externalorg_flag = False
                author_externalorg_name = ''
                if 'person' in persons:                             # internal person
                    if 'uuid' not in persons['person']:
                        # There must be an uuid, otherwise skip
                        continue
                    author_uuid = str(persons['person']['uuid'])
                    # Don't set 'author_name', it is not necessary.
                elif 'externalPerson' in persons:                  # external person
                    if 'uuid' not in persons['externalPerson']:
                        # There must be an uuid, otherwise skip
                        continue
                    author_uuid = str(persons['externalPerson']['uuid'])
                    if 'name' in persons['externalPerson'] \
                       and 'text' in persons['externalPerson']['name'] \
                       and 'value' in persons['externalPerson']['name']['text'][0]:
                        author_name = persons['externalPerson']['name']['text'][0]['value']
                        # 2025-07-04: The more sources we harvest, the less useful this is.
                        # author_name += ' (' + organization + ' external person)'

                        # Get the external organization of this person.
                        # There may be many externalOrganizations, for now we only take the first.
                        if 'externalOrganisations' in persons:
                            if 'name' in persons['externalOrganisations'][0] \
                               and 'text' in persons['externalOrganisations'][0]['name'] \
                               and 'value' in persons['externalOrganisations'][0]['name']['text'][0]:
                                author_externalorg_flag = True
                                author_externalorg_name = persons['externalOrganisations'][0]['name']['text'][0]['value']
                elif 'authorCollaboration' in persons:             # author collaboration
                    if 'uuid' not in persons['authorCollaboration']:
                        # There must be an uuid, otherwise skip
                        continue
                    author_uuid = str(persons['authorCollaboration']['uuid'])
                    if 'name' in persons['authorCollaboration'] \
                            and 'text' in persons['authorCollaboration']['name'] \
                            and 'value' in persons['authorCollaboration']['name']['text'][0]:
                        author_name = persons['authorCollaboration']['name']['text'][0]['value']
                        author_name += ' (' + organization + ' author collaboration)'
                else:
                    # If we get here you might want to add another "elif" above with
                    # the missing personAssociation. Sometimes there is none, then it is ok.
                    # Do not print a warning message, most of the time it is an external person
                    # without any identifier.
                    # print('\nparse_pure_resout(): Warning: Unknown personAssociation/contributor for publication '
                    #      + str(harvest_item['uuid']))
                    continue

                parse_line = {'RESOUT_UUID': str(harvest_item['uuid']),
                              'DOI': doi,
                              'TITLE': str(harvest_item['title']['value']),
                              'YEAR': str(publication_year),
                              'TYPE': rcg.lookup_resout_type(research_output_type=str(harvest_item['type']['uri']),
                                                             research_output_mapping=ROTYPE_MAPPING_PURE),
                              'PURE_UUID_PERS': author_uuid,
                              'FULL_NAME': author_name}
                if author_externalorg_flag:
                    parse_line['AUTHOR_EXTERNALORG_NAME'] = author_externalorg_name
                parse_chunk.append(parse_line)

    print(count, '(' + rcg.timestamp() + ')\n', end='', flush=True)

    if len(parse_chunk) == 0 \
       and PURE_API_VERSION == PURE_CRUD_API_VERSION:
        print('\nPure is harvested using the Pure CRUD API.')
        print('No research outputs were found.')
        print('This is probably caused by one or more of the following fields not present in')
        print('the CRUD API export for "research outputs":')
        print('"workflow", "publicationStatuses" and/or "contributors".')
        print('Please ask your Pure administrator to export these fields. Exiting.')
        exit(1)

    parse_chunk_df = pandas.DataFrame(parse_chunk)
    parse_result = pandas.concat([parse_result, parse_chunk_df], ignore_index=True)
    return rcg.normalize_identifiers_write_read(parse_result=parse_result,
                                                filename=filename)


def parse_pure_projects(harvest: list,
                        filename: str = '') -> Union[pandas.DataFrame, None]:
    """Parse the harvested projects from Pure.
    In case filename != '', write it to a file and read it back.

    :param harvest: the harvest.
    :param filename: If filename != '', write it to a file and read it back.
    :return: the harvested persons in a DataFrame,
        or None if nothing to parse.
    """
    global resout_uuid_or_doi
    global organization

    if len(harvest) == 0:
        return None
    parse_result = pandas.DataFrame()
    parse_chunk = []                # list of dictionaries
    print('There are ' + str(len(harvest)) + ' project records ('
          + rcg.timestamp() + '), parsing record: 0  ', end='')
    count = 0
    for harvest_item in harvest:
        count += 1
        if count % 1000 == 0:
            print(count, ' ', end='', flush=True)
        if count % 10000 == 0:
            print('(' + rcg.timestamp() + ')\n', end='', flush=True)

        if 'uuid' in harvest_item:
            uuid = str(harvest_item['uuid'])
        else:
            # There must be an uuid, otherwise skip.
            continue
        if 'confidential' in harvest_item \
           and harvest_item['confidential']:
            # It may not be confidential.
            continue
        if 'title' in harvest_item:
            title = str(harvest_item['title']['text'][0]['value'])
        else:
            # There must be a title, otherwise skip.
            continue
        if 'visibility' in harvest_item:
            if 'key' in harvest_item['visibility'] \
                    and harvest_item['visibility']['key'] != 'FREE':
                # TODO: Hack for Utrecht University Pure. Their projects have visibility
                # 'BACKEND'. This will change sometime in the future and then this
                # hack should be removed. Date of the hack: November 11, 2023.
                # It should be like this:
                # #### start
                # It must be public, otherwise skip.
                # continue
                # #### end
                # But with the hack it is:
                if organization != 'UU':
                    # It must be public, otherwise skip.
                    continue
        else:
            # It must be explicitly declared to be public, otherwise skip.
            continue
        if 'period' in harvest_item:
            if 'startDate' in harvest_item['period']:
                start_date = str(harvest_item['period']['startDate'])[0:10]
                period = 'started: ' + start_date + ', '
            else:
                period = 'not started, '
            if 'endDate' in harvest_item['period']:
                end_date = str(harvest_item['period']['endDate'])[0:10]
                period += 'ended: ' + end_date
            else:
                period += 'not ended'

            title += ' (' + period + ')'
        if 'status' in harvest_item:
            title += ' (' + str(harvest_item['status']['key'].lower()) + ')'

        # For now, we don't care about the 'workflow' status.

        # One could say: "There are no ids, so do not harvest". However, for
        # now we don't use 'ids' as 'value' field, so for now we _do_ harvest.
        if 'ids' in harvest_item:
            name = ''
            value = ''
            if 'value' in harvest_item['ids'][0]:
                value = str(harvest_item['ids'][0]['value']['value'])
            if 'type' in harvest_item['ids'][0] \
               and 'uri' in harvest_item['ids'][0]['type']:
                name = str(pathlib.PurePath(harvest_item['ids'][0]['type']['uri']).name)
            if name == '' or value == '':
                continue
            title = '[' + name + ': ' + value + '] ' + title
        # else:
        #    continue

        title = organization + ' ' + title
        if 'participants' in harvest_item:
            for participant in harvest_item['participants']:
                if 'person' in participant \
                   and 'uuid' in participant['person']:
                    participant_uuid = str(participant['person']['uuid'])
                else:
                    continue

                if 'organisationalUnits' in participant \
                   and 'uuid' in participant['organisationalUnits'][0]:
                    participant_org = str(participant['organisationalUnits'][0]['uuid'])
                else:
                    continue

                parse_line = {'PURE_UUID_PROJECT': uuid,
                              'PURE_UUID_PROJECT_URL': create_pure_url(name='PURE_UUID_PROJECT',
                                                                       value=uuid),
                              'PURE_PROJECT_TITLE': title,
                              'PURE_PROJECT_PARTICIPANT_UUID': participant_uuid,
                              'PURE_PROJECT_PARTICIPANT_ORG': participant_org}
                parse_chunk.append(parse_line)

        if 'relatedResearchOutputs' in harvest_item:
            for resout in harvest_item['relatedResearchOutputs']:
                if 'uuid' in resout:
                    resout_uuid = str(resout['uuid'])
                else:
                    continue
                if 'type' in resout \
                   and 'uri' in resout['type']:
                    resout_category = rcg.lookup_resout_type(research_output_type=str(resout['type']['uri']),
                                                             research_output_mapping=ROTYPE_MAPPING_PURE)
                else:
                    continue

                resout_name = 'PURE_UUID_RESOUT'
                resout_value = resout_uuid
                if resout_uuid_or_doi != {} \
                   and resout_uuid in resout_uuid_or_doi:
                    resout_value = resout_uuid_or_doi[resout_uuid]
                    if not numpy.isnan(resout_value):
                        if '/' in resout_value:
                            resout_name = 'DOI'
                        else:
                            resout_name = 'PURE_UUID_RESOUT'
                parse_line = {'PURE_UUID_PROJECT': uuid,
                              'PURE_UUID_PROJECT_URL': create_pure_url(name='PURE_UUID_PROJECT',
                                                                       value=uuid),
                              'PURE_PROJECT_TITLE': title,
                              'PURE_PROJECT_RESOUT_NAME': resout_name,
                              'PURE_PROJECT_RESOUT_CATEGORY': resout_category,
                              'PURE_PROJECT_RESOUT_VALUE': resout_value}
                parse_chunk.append(parse_line)

        if 'relatedProjects' in harvest_item:
            for related_project in harvest_item['relatedProjects']:
                if 'project' in related_project \
                   and 'uuid' in related_project['project']:
                    related_project_uuid = str(related_project['project']['uuid'])
                else:
                    continue

                parse_line = {'PURE_UUID_PROJECT': uuid,
                              'PURE_UUID_PROJECT_URL': create_pure_url(name='PURE_UUID_PROJECT',
                                                                       value=uuid),
                              'PURE_PROJECT_TITLE': title,
                              'PURE_PROJECT_RELATEDPROJECT_UUID': related_project_uuid}
                parse_chunk.append(parse_line)

    print(count, '(' + rcg.timestamp() + ')\n', end='', flush=True)

    parse_chunk_df = pandas.DataFrame(parse_chunk)
    parse_result = pandas.concat([parse_result, parse_chunk_df], ignore_index=True)
    parse_result = restructure_parse_projects(df=parse_result)
    return rcg.normalize_identifiers_write_read(parse_result=parse_result,
                                                filename=filename)


# ######################################################
# Harvesting and parsing
# ######################################################

def harvest_and_parse_pure_data(mode: str, endpoint: str,
                                headers: dict, body: dict,
                                harvest_filename: str,
                                df_filename: str,
                                year_start:str = '') -> Union[pandas.DataFrame, None]:
    """Harvest and parse data from Pure.

    :param mode: 'persons', 'organizations' or 'research outputs', to indicate what to harvest.
    :param endpoint: endpoint Pure.
    :param headers: headers for Pure.
    :param body: the body of a POST request, or '' for a GET request.
    :param harvest_filename: filename to write harvest results to.
    :param df_filename: filename to write the DataFrame results to.
    :param year_start: the first year that we would like to harvest.
        Only relevant when parsing persons.
    :return: the DataFrame harvested, or None if nothing harvested.
    """
    if mode != 'persons' \
       and mode != 'organizations' \
       and mode != 'research outputs' \
       and mode != 'projects':
        print('harvest_and_parse_pure_data(): unknown mode ' + mode + '.')
        return None

    if mode == 'persons':
        max_recs_to_harvest = PURE_PERSONS_MAX_RECS_TO_HARVEST
    elif mode == 'organizations':
        max_recs_to_harvest = PURE_ORGANIZATIONS_MAX_RECS_TO_HARVEST
    elif mode == 'research outputs':
        max_recs_to_harvest = PURE_RESOUT_MAX_RECS_TO_HARVEST
    elif mode == 'projects':
        max_recs_to_harvest = PURE_PROJECTS_MAX_RECS_TO_HARVEST
    else:
        # Should not happen
        return None

    print('Harvesting ' + mode + ' from ' + HARVEST_SOURCE + '...')
    if (mode == 'persons' and not PURE_PERSONS_READ_HARVEST_FROM_FILE) \
       or (mode == 'organizations' and not PURE_ORGANIZATIONS_READ_HARVEST_FROM_FILE) \
       or (mode == 'research outputs' and not PURE_RESOUT_READ_HARVEST_FROM_FILE) \
       or (mode == 'projects' and not PURE_PROJECTS_READ_HARVEST_FROM_FILE):
        url = PURE_URL + '/' + PURE_API_VERSION + '/' + endpoint
        harvest_data = rcg.harvest_json(url=url,
                                        headers=headers, body=body,
                                        max_recs_to_harvest=max_recs_to_harvest,
                                        chunksize=PURE_CHUNKSIZE,
                                        filename=harvest_filename)
    else:
        harvest_data = rcg.read_json_from_file(filename=harvest_filename)

    # To prevent PyCharm warning
    # Local variable 'parse' might be referenced before assignment.
    parse = pandas.DataFrame()
    if mode == 'persons':
        parse = parse_pure_persons(harvest=harvest_data, filename=df_filename,
                                   year_start=year_start)
    elif mode == 'organizations':
        parse = parse_pure_organizations(harvest=harvest_data, filename=df_filename)
    elif mode == 'research outputs':
        parse = parse_pure_resout(harvest=harvest_data, filename=df_filename)
    elif mode == 'projects':
        parse = parse_pure_projects(harvest=harvest_data, filename=df_filename)

    if parse is None:
        return None
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
    all_possible_cols = ['PURE_UUID_PERS', 'FULL_NAME', 'ORCID', 'ISNI',
                         'SCOPUS_AUTHOR_ID', 'DIGITAL_AUTHOR_ID',
                         'RESEARCHER_ID', 'EMPLOYEE_ID']
    existing_cols = [c for c in all_possible_cols if c in parsed_content.columns]
    person_identifiers = parsed_content[existing_cols].copy(deep=True)
    rcg.create_parsed_persons_in_ricgraph(person_identifiers=person_identifiers,
                                          harvest_source=HARVEST_SOURCE)
    # Add the URL to this person in Pure. Some persons do not seem to have
    # this page.
    nodes_to_update = parsed_content[['PURE_UUID_PERS']].copy(deep=True)
    nodes_to_update['URL_MAIN'] = nodes_to_update[['PURE_UUID_PERS']].apply(
                                  lambda row: create_pure_url(name='PURE_UUID_PERS',
                                                              value=row['PURE_UUID_PERS']), axis=1)
    rcg.update_urls_in_ricgraph(entities=nodes_to_update,
                               harvest_source=HARVEST_SOURCE,
                               what='URLs of PURE_UUID_PERS nodes')
    return


def determine_all_parent_organizations(parsed_content_organizations: pandas.DataFrame) -> dict:
    """Determine all the parents from a given organization.
    In Pure, organizations are hierarchical. That means, an organization has a parent org,
    which has a parent org, up until a root org.

    :param parsed_content_organizations: a DataFrame containing an organization and its parent.
    :return: a dict of lists. The dict is on organization UUID, the list has as
      first element the name of the organization UUID, followed by UUIDS of all of its parents, or
      followed by nothing if no parent for organization UUID exists.
    """
    print('Determining all parent organizations of an organization...')
    parsed_content = parsed_content_organizations[['PURE_UUID_ORG',
                                                   'FULL_ORG_NAME',
                                                   'PARENT_UUID']].copy(deep=True)
    parsed_content.dropna(axis=0, how='any', inplace=True)
    parsed_content.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    organization_and_all_parents = {}

    # Transform dataframe to dict. The first entry in the list at a dict[<org>] is the
    # name, following entries are the parents of <org>.
    # In this loop, construct the dict and its direct parent, in the second loop
    # the top-level orgs will be added, and in the third loop all of its
    # parents will be appended to dict[<org>].
    for index in range(len(parsed_content)):
        orgid = str(parsed_content.iloc[index, 0])
        orgname = str(parsed_content.iloc[index, 1])
        parentorgid = str(parsed_content.iloc[index, 2])
        if orgid in organization_and_all_parents:
            # This orgid seems to have more than one parent.
            organization_and_all_parents[orgid].append(parentorgid)
            continue
        organization_and_all_parents.setdefault(orgid, [])
        organization_and_all_parents[orgid].append(orgname)
        organization_and_all_parents[orgid].append(parentorgid)

    # 2nd loop: Do the same for PARENT_UUID and FULL_PARENT_NAME. This is necessary because the
    # top-level org will not be in PURE_UUID_ORG.
    parsed_content = parsed_content_organizations[['PARENT_UUID',
                                                   'FULL_PARENT_NAME']].copy(deep=True)
    parsed_content.dropna(axis=0, how='any', inplace=True)
    parsed_content.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    for index in range(len(parsed_content)):
        orgid = str(parsed_content.iloc[index, 0])
        orgname = str(parsed_content.iloc[index, 1])
        if orgid not in organization_and_all_parents:
            organization_and_all_parents.setdefault(orgid, [])
            organization_and_all_parents[orgid].append(orgname)

    # 3rd loop: For each organization, find all of its parents.
    something_changed = True
    nr_iterations = 0
    while something_changed:
        something_changed = False
        nr_iterations += 1
        for orgid in organization_and_all_parents:
            orgid_name_and_parentslist = organization_and_all_parents[orgid]
            # For each parent of orgid, find its parent, up to the top org.
            # In this first loop, we loop over the parents of orgid we've already found.
            for index in range(len(orgid_name_and_parentslist)):
                if index == 0:
                    # Remember: first entry in list is the name of orgid.
                    continue
                parentorgid = orgid_name_and_parentslist[index]
                # Now, find the parents of parentorgid, first check if there is any.
                if parentorgid not in organization_and_all_parents:
                    continue
                parentslist = organization_and_all_parents[parentorgid]
                # Now loop over the lists of parents of 'parentorgid'.
                for index_pl in range(len(parentslist)):
                    if index_pl == 0:
                        # Remember: first entry in list is the name of the parent org.
                        continue
                    parent_of_parentorgid = parentslist[index_pl]
                    if parent_of_parentorgid not in organization_and_all_parents[orgid]:
                        something_changed = True
                        organization_and_all_parents[orgid].append(parent_of_parentorgid)

    print(str(nr_iterations) + ' iterations were necessary to determine all parent organizations.')

    return organization_and_all_parents


def parsed_organizations_to_ricgraph(parsed_content_persons: pandas.DataFrame,
                                     organization_and_all_parents: dict) -> None:
    """Insert the parsed organizations in Ricgraph.

    In Pure, organizations are hierarchical. That means, an organization has a parent org,
    which has a parent org, up until a root org.
    At the end of this function, a person (i.e. its person-root node) will be connected to
    all of these hierarchical orgs.

    :param parsed_content_persons: The person records to connect to organization records in Ricgraph.
    :param organization_and_all_parents: a dict of lists. The dict is on organization UUID, the list has as
      first element the name of the organization UUID, followed by UUIDS of all of its parents, or
      followed by nothing if no parent for organization UUID exists.
    :return: None.
    """
    timestamp = rcg.datetimestamp()
    print('\nInserting organizations and persons from organizations from '
          + HARVEST_SOURCE + ' in Ricgraph at ' + timestamp + '...')
    history_event = 'Source: Harvest ' + HARVEST_SOURCE + ' organizations at ' + timestamp + '.'

    print('Determining all links between persons and all of their organizations... ', end='', flush=True)
    parsed_content = parsed_content_persons[['PURE_UUID_PERS',
                                             'PURE_UUID_ORG']].copy(deep=True)
    parsed_content.dropna(axis=0, how='any', inplace=True)
    parsed_content.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    person_organization = {}
    for index in range(len(parsed_content)):
        personid = parsed_content.iloc[index, 0]
        orgid = parsed_content.iloc[index, 1]
        if personid in person_organization:
            # This personid seems to be in more than one org.
            person_organization[personid].append(orgid)
            continue
        person_organization.setdefault(personid, [])
        person_organization[personid].append(orgid)

    parse_chunk = []                # list of dictionaries
    for personid in person_organization:
        orgidlist = person_organization[personid]
        # This person may be in several organizations in 'orgidlist'.
        for orgid in orgidlist:
            if orgid not in organization_and_all_parents:
                continue
            orgid_name_and_parentslist = organization_and_all_parents[orgid]
            orgid_name = orgid_name_and_parentslist[0]

            # First connect this person and 'orgid'.
            parse_line = {'PURE_UUID_PERS': str(personid),
                          'PURE_UUID_ORG': orgid,
                          'FULL_ORG_NAME': orgid_name}
            parse_chunk.append(parse_line)

            # Now get all parents of orgid.
            # Then connect this person with the parents of 'orgid'.
            for index in range(len(orgid_name_and_parentslist)):
                if index == 0:
                    # Remember: first entry in list is the name of the org.
                    continue
                parse_line = {'PURE_UUID_PERS': str(personid)}
                parent_orgid = str(orgid_name_and_parentslist[index])
                parent_name = str(organization_and_all_parents[parent_orgid][0])
                parse_line['PURE_UUID_ORG'] = parent_orgid
                parse_line['FULL_ORG_NAME'] = parent_name
                parse_chunk.append(parse_line)

    print('Done.\n')

    if len(parse_chunk) == 0:
        print('No link found between persons and all of their organizations.')
        return

    persorgnodes = pandas.DataFrame()
    parse_chunk_df = pandas.DataFrame(parse_chunk)
    persorgnodes = pandas.concat([persorgnodes, parse_chunk_df], ignore_index=True)
    # Add the URL to this organization in Pure. Some organizations do
    # not seem to have this page.
    persorgnodes['URL_MAIN'] = persorgnodes[['PURE_UUID_ORG']].apply(
                               lambda row: create_pure_url(name='PURE_UUID_ORG',
                                                           value=row['PURE_UUID_ORG']), axis=1)
    persorgnodes.drop(labels='PURE_UUID_ORG', axis='columns', inplace=True)
    persorgnodes.rename(columns={'FULL_ORG_NAME': 'ORGANIZATION_NAME'}, inplace=True)
    rcg.create_parsed_entities_in_ricgraph(entities=persorgnodes,
                                           harvest_source=HARVEST_SOURCE)
    return


def parsed_resout_to_ricgraph(parsed_content: pandas.DataFrame) -> None:
    """Insert the parsed research outputs in Ricgraph.

    :param parsed_content: The records to insert in Ricgraph, if not present yet.
    :return: None.
    """
    global resout_uuid_or_doi

    # Do some shuffling to prepare insert of research outputs in Ricgraph.
    resouts = parsed_content[['RESOUT_UUID', 'TITLE', 'YEAR', 'TYPE', 'DOI', 'PURE_UUID_PERS']].copy(deep=True)
    resouts.dropna(axis=0, how='all', inplace=True)
    resouts.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    resouts['DOI'] = resouts['DOI'].fillna('')

    # A number of research outputs in Pure have a DOI, but not all. We prefer the DOI above PURE_UUID_RESOUT.
    # So if there is a DOI, use it, otherwise use PURE_UUID_RESOUT UUID. Some shuffling is required.
    # First, fill the column 'name1' with 'DOI', unless the value is '', then fill with 'PURE_UUID_RESOUT'.
    resouts['RESOUT_ID'] = resouts[['DOI']].apply(lambda x: 'PURE_UUID_RESOUT' if x.item() == '' else 'DOI', axis=1)
    # Make sure we have the correct URL.
    resouts['URL_MAIN'] = resouts[['RESOUT_ID', 'DOI', 'RESOUT_UUID']].apply(
                          lambda row: create_urlmain(type_id=row['RESOUT_ID'],
                                                     doi_value=row['DOI'],
                                                     uuid_value=row['RESOUT_UUID']), axis=1)
    resouts['URL_OTHER'] = resouts[['RESOUT_ID', 'DOI', 'RESOUT_UUID']].apply(
                           lambda row: create_urlother(type_id=row['RESOUT_ID'],
                                                       uuid_value=row['RESOUT_UUID']), axis=1)
    # Now replace all empty strings in column DOI for NaNs
    # The next statement will result in a 'behavior will change in pandas 3.0' warning.
    resouts['DOI'] = resouts['DOI'].replace('', numpy.nan)
    # Then fill the column 'value1' with the value from column DOI, unless the value is NaN,
    # then fill with the value from column RESOUT_UUID.
    resouts['value1'] = resouts['DOI'].copy(deep=True)
    # The next statement will result in a 'behavior will change in pandas 3.0' warning.
    resouts['RESOUT_UUID'] = resouts.value1.fillna(resouts['RESOUT_UUID'])
    resouts.rename(columns={'RESOUT_UUID': 'RESOUT_VALUE'}, inplace=True)

    if HARVEST_PROJECTS:
        # This is only necessary if we are going to harvest projects later on.
        if resout_uuid_or_doi == {}:
            resout_uuid_or_doi = dict(zip(resouts.RESOUT_UUID, resouts.value1))
        else:
            resout_uuid_or_doi.update((zip(resouts.RESOUT_UUID, resouts.value1)))

    resouts = resouts[['PURE_UUID_PERS', 'RESOUT_ID', 'RESOUT_VALUE',
                       'TITLE', 'YEAR', 'TYPE', 'URL_MAIN', 'URL_OTHER']].copy(deep=True)
    rcg.create_parsed_entities_in_ricgraph_general(entities=resouts,
                                                   harvest_source=HARVEST_SOURCE,
                                                   what='research outputs')

    if 'FULL_NAME' in parsed_content.columns:
        # This is specifically for external persons and author collaborations. We only
        # find these while parsing research outputs, not while parsing persons.
        external_persons = parsed_content[['PURE_UUID_PERS', 'FULL_NAME']].copy(deep=True)
        rcg.create_parsed_entities_in_ricgraph(entities=external_persons,
                                               harvest_source=HARVEST_SOURCE)

    if 'AUTHOR_EXTERNALORG_NAME' in parsed_content.columns:
        # This is specifically for external persons and external organizations. We only
        # find these while parsing research outputs, not while parsing persons.
        print('Determining external organizations from external persons...')
        persorgnodes = parsed_content[['PURE_UUID_PERS',
                                       'AUTHOR_EXTERNALORG_NAME']].copy(deep=True)
        persorgnodes.rename(columns={'AUTHOR_EXTERNALORG_NAME': 'ORGANIZATION_NAME'}, inplace=True)
        rcg.create_parsed_entities_in_ricgraph(entities=persorgnodes,
                                               harvest_source=HARVEST_SOURCE)
    return


def parsed_projects_to_ricgraph(parsed_content: pandas.DataFrame,
                                organization_and_all_parents: dict) -> None:
    """Insert the parsed projects in Ricgraph.

    :param parsed_content: The records to insert in Ricgraph, if not present yet.
    :param organization_and_all_parents: a dict of lists. The dict is on organization UUID, the list has as
      first element the name of the organization UUID, followed by UUIDS of all of its parents, or
      followed by nothing if no parent for organization UUID exists.
    :return: None.
    """
    # RDTJ, February 17, 2026. This code should be cleaned up. Calls to
    # create_nodepairs_and_edges_df() should be moved to file ricgraph_harvest.py,
    # as has been done above.
    timestamp = rcg.datetimestamp()
    print('Inserting projects from ' + HARVEST_SOURCE + ' in Ricgraph at '
          + timestamp + '...')
    history_event = 'Source: Harvest ' + HARVEST_SOURCE + ' projects at ' + timestamp + '.'

    # ##### Insert projects and related participants.
    project_identifiers = parsed_content[['PURE_UUID_PROJECT',
                                          'PURE_UUID_PROJECT_URL',
                                          'PURE_PROJECT_TITLE',
                                          'PURE_PROJECT_PARTICIPANT_UUID']].copy(deep=True)

    # dropna(how='all'): drop row if all row values contain NaN
    project_identifiers.dropna(axis=0, how='any', inplace=True)
    project_identifiers.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    if len(project_identifiers) == 0:
        print('There seem to be no projects connected to persons, nothing to do:')
        print(project_identifiers)
        return

    print('The following projects connected to persons from '
          + HARVEST_SOURCE + ' will be inserted in Ricgraph at ' + rcg.timestamp() + ':')
    print(project_identifiers)
    project_identifiers.rename(columns={'PURE_UUID_PROJECT': 'value1',
                                        'PURE_UUID_PROJECT_URL': 'url_main1',
                                        'PURE_PROJECT_TITLE': 'comment1',
                                        'PURE_PROJECT_PARTICIPANT_UUID': 'value2'}, inplace=True)
    new_project_columns = {'name1': 'PURE_UUID_PROJECT',
                           'category1': 'project',
                           'source_event1': HARVEST_SOURCE,
                           'history_event1': history_event,
                           'name2': 'PURE_UUID_PERS',
                           'category2': 'person',
                           'source_event2': HARVEST_SOURCE}
    project_identifiers = project_identifiers.assign(**new_project_columns)
    project_identifiers = project_identifiers[['name1', 'category1', 'value1',
                                               'url_main1', 'comment1',
                                               'source_event1', 'history_event1',
                                               'name2', 'category2', 'value2',
                                               'source_event2']]

    print('The following projects connected to persons from '
          + HARVEST_SOURCE + ' will be inserted in Ricgraph at ' + rcg.timestamp() + ':')
    print(project_identifiers)
    rcg.create_nodepairs_and_edges_df(left_and_right_nodepairs=project_identifiers)

    # ##### Insert projects and related organizations (that is, where their participants work).
    if 'PURE_PROJECT_PARTICIPANT_ORG' in parsed_content.columns:
        print('Determining all links between projects and all of their organizations at '
              + rcg.timestamp() + '... ', end='', flush=True)
        project_identifiers = parsed_content[['PURE_UUID_PROJECT',
                                              'PURE_PROJECT_PARTICIPANT_ORG']].copy(deep=True)
        project_identifiers.dropna(axis=0, how='any', inplace=True)
        project_identifiers.drop_duplicates(keep='first', inplace=True, ignore_index=True)
        project_organization = {}
        for index in range(len(project_identifiers)):
            projectid = project_identifiers.iloc[index, 0]
            orgid = project_identifiers.iloc[index, 1]
            if projectid in project_organization:
                # This projectid seems to be in more than one org.
                project_organization[projectid].append(orgid)
                continue
            project_organization.setdefault(projectid, [])
            project_organization[projectid].append(orgid)

        parse_chunk = []                # list of dictionaries
        for projectid in project_organization:
            orgidlist = project_organization[projectid]
            # This person may be in several organizations in 'orgidlist'.
            for orgid in orgidlist:
                if orgid not in organization_and_all_parents:
                    continue
                orgid_name_and_parentslist = organization_and_all_parents[orgid]
                orgid_name = orgid_name_and_parentslist[0]

                # First connect this person and 'orgid'.
                parse_line = {'PURE_UUID_PROJECT': str(projectid),
                              'PURE_UUID_ORG': orgid,
                              'FULL_ORG_NAME': orgid_name}
                parse_chunk.append(parse_line)

                # Now get all parents of orgid.
                # Then connect this person with the parents of 'orgid'.
                for index in range(len(orgid_name_and_parentslist)):
                    if index == 0:
                        # Remember: first entry in list is the name of the org.
                        continue
                    parse_line = {'PURE_UUID_PROJECT': str(projectid)}
                    parent_orgid = str(orgid_name_and_parentslist[index])
                    parent_name = str(organization_and_all_parents[parent_orgid][0])
                    parse_line['PURE_UUID_ORG'] = parent_orgid
                    parse_line['FULL_ORG_NAME'] = parent_name
                    parse_chunk.append(parse_line)

        print('Done at ' + rcg.timestamp() + '.\n')

        projorgnodes = pandas.DataFrame()
        parse_chunk_df = pandas.DataFrame(parse_chunk)
        projorgnodes = pandas.concat([projorgnodes, parse_chunk_df], ignore_index=True)

        projorgnodes.drop(labels='PURE_UUID_ORG', axis='columns', inplace=True)
        projorgnodes.dropna(axis=0, how='any', inplace=True)
        projorgnodes.drop_duplicates(keep='first', inplace=True, ignore_index=True)
        projorgnodes.rename(columns={'PURE_UUID_PROJECT': 'value1',
                                     'FULL_ORG_NAME': 'value2'}, inplace=True)
        new_projorgnodes_columns = {'name1': 'PURE_UUID_PROJECT',
                                    'category1': 'project',
                                    'name2': 'ORGANIZATION_NAME',
                                    'category2': 'organization'}
        projorgnodes = projorgnodes.assign(**new_projorgnodes_columns)
        projorgnodes = projorgnodes[['name1', 'category1', 'value1',
                                     'name2', 'category2', 'value2']]

        print('The following projects and their organizations from '
              + HARVEST_SOURCE + ' will be inserted in Ricgraph at ' + rcg.timestamp() + ':')
        print(projorgnodes)
        rcg.create_nodepairs_and_edges_df(left_and_right_nodepairs=projorgnodes)
        # ##### end of Insert projects and related organizations.

    # ##### Insert projects and related research outputs.
    project_identifiers = parsed_content[['PURE_UUID_PROJECT',
                                          'PURE_PROJECT_RESOUT_NAME',
                                          'PURE_PROJECT_RESOUT_CATEGORY',
                                          'PURE_PROJECT_RESOUT_VALUE']].copy(deep=True)
    # dropna(how='all'): drop row if all row values contain NaN
    project_identifiers.dropna(axis=0, how='any', inplace=True)
    project_identifiers.drop_duplicates(keep='first', inplace=True, ignore_index=True)

    print('The following projects connected to research outputs from '
          + HARVEST_SOURCE + ' will be inserted in Ricgraph at ' + rcg.timestamp() + ':')
    print(project_identifiers)
    project_identifiers.rename(columns={'PURE_UUID_PROJECT': 'value1',
                                        'PURE_PROJECT_RESOUT_NAME': 'name2',
                                        'PURE_PROJECT_RESOUT_CATEGORY': 'category2',
                                        'PURE_PROJECT_RESOUT_VALUE': 'value2'}, inplace=True)
    new_project_columns = {'name1': 'PURE_UUID_PROJECT',
                           'category1': 'project',
                           'source_event2': HARVEST_SOURCE}
    project_identifiers = project_identifiers.assign(**new_project_columns)
    project_identifiers = project_identifiers[['name1', 'category1', 'value1',
                                               'name2', 'category2', 'value2',
                                               'source_event2']]

    print('The following projects connected to research outputs from '
          + HARVEST_SOURCE + ' will be inserted in Ricgraph at ' + rcg.timestamp() + ':')
    print(project_identifiers)
    rcg.create_nodepairs_and_edges_df(left_and_right_nodepairs=project_identifiers)

    if 'PURE_PROJECT_RELATEDPROJECT_UUID' in parsed_content.columns:
        # ##### Insert projects and related projects.
        project_identifiers = parsed_content[['PURE_UUID_PROJECT',
                                              'PURE_PROJECT_RELATEDPROJECT_UUID']].copy(deep=True)
        project_identifiers.dropna(axis=0, how='any', inplace=True)
        project_identifiers.drop_duplicates(keep='first', inplace=True, ignore_index=True)

        print('The following projects connected to related projects from '
              + HARVEST_SOURCE + ' will be inserted in Ricgraph at ' + rcg.timestamp() + ':')
        print(project_identifiers)
        project_identifiers.rename(columns={'PURE_UUID_PROJECT': 'value1',
                                            'PURE_PROJECT_RELATEDPROJECT_UUID': 'value2'}, inplace=True)
        new_project_columns = {'name1': 'PURE_UUID_PROJECT',
                               'category1': 'project',
                               'name2': 'PURE_UUID_PROJECT',
                               'category2': 'project',
                               'source_event2': HARVEST_SOURCE}
        project_identifiers = project_identifiers.assign(**new_project_columns)
        project_identifiers = project_identifiers[['name1', 'category1', 'value1',
                                                   'name2', 'category2', 'value2',
                                                   'source_event2']]

        print('The following projects connected to related projects from '
              + HARVEST_SOURCE + ' will be inserted in Ricgraph at ' + rcg.timestamp() + ':')
        print(project_identifiers)
        rcg.create_nodepairs_and_edges_df(left_and_right_nodepairs=project_identifiers)
    else:
        print('\nThere are no projects connected to related projects from ' + HARVEST_SOURCE + '.')

    print('\nDone at ' + rcg.timestamp() + '.\n')
    return


# ############################################
# ################### main ###################
# ############################################
rcg.print_commandline_arguments(argument_list=sys.argv)
if (organization := rcg.get_commandline_argument_organization(argument_list=sys.argv)) == '':
    print('Exiting.\n')
    exit(1)

print('')
year_first, year_last = rcg.get_commandline_argument_year_first_last(argument_list=sys.argv)
if year_first == '' or year_last == '':
    # An error message has already been printed
    # in get_commandline_argument_year_first_last().
    exit(1)

if (harvest_projects := rcg.get_commandline_argument_harvest_projects(argument_list=sys.argv)) == 'yes':
    HARVEST_PROJECTS = True
else:
    HARVEST_PROJECTS = False

pure_url = 'pure_url_' + organization
pure_api_key = 'pure_api_key_' + organization
PURE_URL = rcg.get_configfile_key(section='Pure_harvesting', key=pure_url)
PURE_API_KEY = rcg.get_configfile_key(section='Pure_harvesting', key=pure_api_key)
if PURE_URL == '' or PURE_API_KEY == '':
    print('Ricgraph initialization: error, "' + pure_url + '" or "' + pure_api_key + '"')
    print('  not existing or empty in Ricgraph ini file, exiting.')
    exit(1)

PURE_HEADERS['api-key'] = PURE_API_KEY

print('\n')

# Find out if we should harvest Pure according to the Pure READ API or the Pure CRUD API.
read_url = PURE_URL + '/' + PURE_READ_API_VERSION + '/' + PURE_READ_PERSONS_ENDPOINT
crud_url = PURE_URL + '/' + PURE_CRUD_API_VERSION + '/' + PURE_CRUD_PERSONS_ENDPOINT
read_response = requests.post(url=read_url, headers=PURE_HEADERS, json={'fields': ['*']})
crud_response = requests.post(url=crud_url, headers=PURE_HEADERS, json={'fields': ['*']})
if read_response.status_code == requests.codes.ok:
    print('Pure will be harvested using the Pure READ API.')
    PURE_API_VERSION = PURE_READ_API_VERSION
    PURE_PERSONS_ENDPOINT = PURE_READ_PERSONS_ENDPOINT
    PURE_ORGANIZATIONS_ENDPOINT = PURE_READ_ORGANIZATIONS_ENDPOINT
    PURE_RESOUT_ENDPOINT = PURE_READ_RESOUT_ENDPOINT
    PURE_RESOUT_FIELDS = PURE_READ_RESOUT_FIELDS
    PURE_PROJECTS_ENDPOINT = PURE_READ_PROJECTS_ENDPOINT
elif crud_response.status_code == requests.codes.ok:
    print('Pure will be harvested using the Pure CRUD API.')
    PURE_API_VERSION = PURE_CRUD_API_VERSION
    PURE_PERSONS_ENDPOINT = PURE_CRUD_PERSONS_ENDPOINT
    PURE_ORGANIZATIONS_ENDPOINT = PURE_CRUD_ORGANIZATIONS_ENDPOINT
    PURE_RESOUT_ENDPOINT = PURE_CRUD_RESOUT_ENDPOINT
    PURE_RESOUT_FIELDS = PURE_CRUD_RESOUT_FIELDS
    # No harvesting of projects with CRUD API.
else:
    print('Could not determine whether Pure should be harvested using the READ or CRUD API.')
    print('Response Pure READ API:')
    print('Status code: ' + str(read_response.status_code))
    print('Url: ' + read_response.url)
    print('Error: ' + read_response.text)
    print('Response Pure CRUD API:')
    print('Status code: ' + str(crud_response.status_code))
    print('Url: ' + crud_response.url)
    print('Error: ' + crud_response.text)
    exit(1)

HARVEST_SOURCE = 'Pure-' + organization

print('\nHarvesting ' + HARVEST_SOURCE + ', first year: ' + year_first + ', last year: ' + year_last + '.')

print('\nPreparing graph...')
rcg.open_ricgraph()

empty_graph = rcg.get_commandline_argument_empty_ricgraph(argument_list=sys.argv)
if empty_graph == 'yes' or empty_graph == 'no':
    rcg.empty_ricgraph(answer=empty_graph)
else:
    print('Exiting.\n')
    exit(1)

resout_uuid_or_doi = {}

# ########################################################################
# You can use 'True' or 'False' depending on your needs to harvest persons/organizations/research outputs.
# This might be handy if you are testing your parsing.
# You might also want to set parameters as 'PURE_[object name]_HARVEST_FROM_FILE' = True,
# see the top of this file.
# ########################################################################


# ########################################################################
# Code for harvesting persons. Harvested persons are required for organizations.
data_file = rcg.construct_filename(base_filename=PURE_PERSONS_DATA_FILENAME,
                                   organization=organization)

rcg.graphdb_nr_accesses_print()
print(rcg.nodes_cache_key_id_type_size() + '\n')

# if False:
if True:
    if PURE_PERSONS_READ_DATA_FROM_FILE:
        error_message = 'There are no persons from ' + HARVEST_SOURCE + ' to read from file ' + data_file + '.\n'
        print('Reading persons from ' + HARVEST_SOURCE + ' from file ' + data_file + '.')
        parse_persons = rcg.read_dataframe_from_csv(filename=data_file, datatype=str)
    else:
        error_message = 'There are no persons from ' + HARVEST_SOURCE + ' to harvest.\n'
        print('Harvesting person from ' + HARVEST_SOURCE + '.')
        harvest_file = rcg.construct_filename(base_filename=PURE_PERSONS_HARVEST_FILENAME,
                                              organization=organization)
        parse_persons = harvest_and_parse_pure_data(mode='persons',
                                                    endpoint=PURE_PERSONS_ENDPOINT,
                                                    headers=PURE_HEADERS,
                                                    body=PURE_PERSONS_FIELDS,
                                                    harvest_filename=harvest_file,
                                                    df_filename=data_file,
                                                    year_start=year_first)

    if parse_persons is None or parse_persons.empty:
        print(error_message)
    else:
        parsed_persons_to_ricgraph(parsed_content=parse_persons)

    rcg.graphdb_nr_accesses_print()
    print(rcg.nodes_cache_key_id_type_size() + '\n')

org_and_all_parents = {}

# ########################################################################
# Code for harvesting organizations. This is dependent on harvested persons.
# if False:
if True:
    # Uncomment the next line for (some) debugging purposes.
    # You might also want to set 'PURE_PERSONS_READ_HARVEST_FROM_FILE = True'
    # at the top of this file.
    # parse_persons = rcg.read_dataframe_from_csv(filename=data_file, datatype=str)

    data_file = rcg.construct_filename(base_filename=PURE_ORGANIZATIONS_DATA_FILENAME,
                                       organization=organization)
    if PURE_ORGANIZATIONS_READ_DATA_FROM_FILE:
        error_message = 'There are no organizations from ' + HARVEST_SOURCE + ' to read from file ' + data_file + '.\n'
        print('Reading organizations from ' + HARVEST_SOURCE + ' from file ' + data_file + '.')
        parse_organizations = rcg.read_dataframe_from_csv(filename=data_file,
                                                          datatype=str)
    else:
        error_message = 'There are no organizations from ' + HARVEST_SOURCE + ' to harvest.\n'
        print('Harvesting organizations from ' + HARVEST_SOURCE + '.')
        harvest_file = rcg.construct_filename(base_filename=PURE_ORGANIZATIONS_HARVEST_FILENAME,
                                              organization=organization)
        parse_organizations = harvest_and_parse_pure_data(mode='organizations',
                                                          endpoint=PURE_ORGANIZATIONS_ENDPOINT,
                                                          headers=PURE_HEADERS,
                                                          body=PURE_ORGANIZATIONS_FIELDS,
                                                          harvest_filename=harvest_file,
                                                          df_filename=data_file)

    if parse_organizations is None or parse_organizations.empty:
        print(error_message)
    else:
        org_and_all_parents = determine_all_parent_organizations(parsed_content_organizations=parse_organizations)
        # Next may generate a PyCharm warning "Name 'parse_persons' can be undefined".
        parsed_organizations_to_ricgraph(parsed_content_persons=parse_persons,
                                         organization_and_all_parents=org_and_all_parents)

    rcg.graphdb_nr_accesses_print()
    print(rcg.nodes_cache_key_id_type_size() + '\n')


# ########################################################################
# Code for harvesting research outputs.
# if False:
if True:
    # Note that in 2023, the Pure CRUD API did not allow
    # harvesting separate years. This might cause memory problems.
    # You might want to set PURE_RESOUT_MAX_RECS_TO_HARVEST.
    # The Pure READ API does allow to specify years to harvest.
    for year_int in range(int(year_first), int(year_last) + 1):
        year = str(year_int)
        data_file_year = rcg.construct_filename(base_filename=PURE_RESOUT_DATA_FILENAME,
                                                year=year, organization=organization)
        if PURE_RESOUT_READ_DATA_FROM_FILE:
            error_message = 'There are no research outputs from ' + HARVEST_SOURCE
            error_message += ' for year ' + year + ' to read from file ' + data_file_year + '.\n'
            print('Reading research outputs from ' + HARVEST_SOURCE + ' for year '
                  + year + ' from file ' + data_file_year + '.')
            parse_resout = rcg.read_dataframe_from_csv(filename=data_file_year,
                                                       datatype=str)
        else:
            error_message = 'There are no research outputs from ' + HARVEST_SOURCE
            error_message += ' for year ' + year + ' to harvest.\n'
            print('Harvesting research outputs from ' + HARVEST_SOURCE
                  + ' for year ' + year + '.')
            harvest_file_year = rcg.construct_filename(base_filename=PURE_RESOUT_HARVEST_FILENAME,
                                                       year=year, organization=organization)
            # The following create a PyCharm warning
            # Unexpected type(s):(str, str)Possible type(s):(str, list[str])(str, list[str]).
            PURE_RESOUT_FIELDS['publishedBeforeDate'] = year + '-12-31'
            PURE_RESOUT_FIELDS['publishedAfterDate'] = year + '-01-01'
            parse_resout = harvest_and_parse_pure_data(mode='research outputs',
                                                       endpoint=PURE_RESOUT_ENDPOINT,
                                                       headers=PURE_HEADERS,
                                                       body=PURE_RESOUT_FIELDS,
                                                       harvest_filename=harvest_file_year,
                                                       df_filename=data_file_year)

        if parse_resout is None or parse_resout.empty:
            print(error_message)
        else:
            parsed_resout_to_ricgraph(parsed_content=parse_resout)

        rcg.graphdb_nr_accesses_print()
        print(rcg.nodes_cache_key_id_type_size() + '\n')


# ########################################################################
# Code for harvesting projects.
if HARVEST_PROJECTS:
    if PURE_API_VERSION == PURE_CRUD_API_VERSION:
        print('\nPure is harvested using the Pure CRUD API.')
        print('Harvesting projects from Pure using the CRUD API is not implemented yet.')
        exit(1)

    data_file = rcg.construct_filename(base_filename=PURE_PROJECTS_DATA_FILENAME,
                                       organization=organization)
    if PURE_PROJECTS_READ_DATA_FROM_FILE:
        error_message = 'There are no projects from ' + HARVEST_SOURCE + ' to read from file ' + data_file + '.\n'
        print('Reading projects from ' + HARVEST_SOURCE + ' from file ' + data_file + '.')
        parse_projects = rcg.read_dataframe_from_csv(filename=data_file,
                                                     datatype=str)
    else:
        error_message = 'There are no projects from ' + HARVEST_SOURCE + ' to harvest.\n'
        print('Harvesting projects from ' + HARVEST_SOURCE + '.')
        harvest_file = rcg.construct_filename(base_filename=PURE_PROJECTS_HARVEST_FILENAME,
                                              organization=organization)
        parse_projects = harvest_and_parse_pure_data(mode='projects',
                                                     endpoint=PURE_PROJECTS_ENDPOINT,
                                                     headers=PURE_HEADERS,
                                                     body=PURE_PROJECTS_FIELDS,
                                                     harvest_filename=harvest_file,
                                                     df_filename=data_file)

    if parse_projects is None or parse_projects.empty:
        print(error_message)
    else:
        parsed_projects_to_ricgraph(parsed_content=parse_projects,
                                    organization_and_all_parents=org_and_all_parents)

    rcg.graphdb_nr_accesses_print()
    print(rcg.nodes_cache_key_id_type_size() + '\n')

rcg.close_ricgraph()
