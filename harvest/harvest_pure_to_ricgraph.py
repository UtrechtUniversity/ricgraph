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
# With this code, you can harvest persons, organizations, research outputs,
# data sets, press media items, and projects from Pure.
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
from pathlib import PurePath
import ricgraph as rcg
from ricgraph import construct_extended_org_name

# ######################################################
# General parameters for harvesting from Pure.
# ######################################################
# These specify what you would like to harvest.
HARVEST_PERSONS = True
HARVEST_ORGANIZATIONS = True
# For HARVEST_ORGANIZATIONS you might also want to set
# 'PURE_PERSONS_READ_HARVEST_FROM_FILE = True' (see comment in
# main() in Code for harvesting organizations).
HARVEST_RESOUTS = True
HARVEST_DATASETS = True
HARVEST_PRESS_MEDIA = True
# HARVEST_PROJECTS is a command line option.


# These specify the mode for harvesting.
MODE_PERSONS = 'persons'
MODE_ORGANIZATIONS = 'organizations'
MODE_RESOUTS = 'research outputs'
MODE_DATASETS = 'data sets'
MODE_PRESS_MEDIA = 'press media'
MODE_PROJECTS = 'projects'
MODE_ALL = [MODE_PERSONS,
            MODE_ORGANIZATIONS,
            MODE_RESOUTS,
            MODE_DATASETS,
            MODE_PRESS_MEDIA,
            MODE_PROJECTS]


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
# PURE_PERSONS_INCLUDE_YEARS_BEFORE years before the
# command line argument --year_first.
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
global PURE_RESOUTS_ENDPOINT
PURE_READ_RESOUTS_ENDPOINT = 'research-outputs'
PURE_CRUD_RESOUTS_ENDPOINT = 'research-outputs/search'

# Set this to True to simulate the harvest. If True, do not harvest, but read it from a file.
PURE_RESOUTS_READ_HARVEST_FROM_FILE = False
# PURE_RESOUTS_READ_HARVEST_FROM_FILE = True
PURE_RESOUTS_HARVEST_FILENAME = 'pure_resout_harvest.json'

# Set this to True to read data from the csv file. No harvest will be done, this would
# not make sense. If False, a harvest will be done.
# If True, the value of PURE_RESOUTS_READ_HARVEST_FROM_FILE does not matter.
PURE_RESOUTS_READ_DATA_FROM_FILE = False
# PURE_RESOUTS_READ_DATA_FROM_FILE = True
PURE_RESOUTS_DATA_FILENAME = 'pure_resout_data.csv'

# For Pure READ API: this number is the max recs to harvest per year, not total
# For Pure CRUD API: this number is the max recs to harvest total.
PURE_RESOUTS_MAX_RECS_TO_HARVEST = 0                  # 0 = all records
global PURE_RESOUTS_FIELDS
# The current version of the Pure CRUD API does not have these filters yet.
PURE_READ_RESOUTS_FIELDS = {'fields': ['uuid',
                                      'title.*',
                                      'confidential',
                                      'type.*',
                                      'workflow.*',
                                      'publicationStatuses.*',
                                      'personAssociations.*',
                                      'electronicVersions.*'
                                       ],
                            # These values will be overwritten.
                            # They exist to prevent a PyCharm warning.
                            'publishedBeforeDate': '',
                            'publishedAfterDate': '',
                            }
PURE_CRUD_RESOUTS_FIELDS = {'orderings': ['publicationYear'],
                           'orderBy': 'descending'
                            }

# ######################################################
# Parameters for harvesting data sets from Pure
# ######################################################
# Pure can be harvested according to the READ or CRUD API.
# However, for data sets we only harvest them using the READ API.
global PURE_DATASETS_ENDPOINT
PURE_READ_DATASETS_ENDPOINT = 'datasets'
# PURE_CRUD_DATASETS_ENDPOINT = 'datasets/search'

# Set this to True to simulate the harvest. If True, do not harvest, but read it from a file.
PURE_DATASETS_READ_HARVEST_FROM_FILE = False
# PURE_PRESS_MEDIA_READ_HARVEST_FROM_FILE = True
PURE_DATASETS_HARVEST_FILENAME = 'pure_datasets_harvest.json'

# Set this to True to read data from the csv file. No harvest will be done, this would
# not make sense. If False, a harvest will be done.
# If True, the value of PURE_PRESS_MEDIA_READ_HARVEST_FROM_FILE does not matter.
PURE_DATASETS_READ_DATA_FROM_FILE = False
# PURE_PRESS_MEDIA_READ_DATA_FROM_FILE = True
PURE_DATASETS_DATA_FILENAME = 'pure_datasets_data.csv'

PURE_DATASETS_MAX_RECS_TO_HARVEST = 0                  # 0 = all records
# The current version of the Pure CRUD API does not have these filters yet.
PURE_DATASETS_FIELDS = {'fields': ['uuid',
                                   'doi',
                                   'publicationDate.*',
                                   'confidential',
                                   'title.*',
                                   'type.*',
                                   'workflow.*',
                                   'personAssociations.*',
                                   'links.*',
                                  ]
                        }

# ######################################################
# Parameters for harvesting press media items from Pure
# ######################################################
# Pure can be harvested according to the READ or CRUD API.
# However, for press media items we only harvest them using the READ API.
global PURE_PRESS_MEDIA_ENDPOINT
PURE_READ_PRESS_MEDIA_ENDPOINT = 'press-media'
# PURE_CRUD_PRESS_MEDIA_ENDPOINT = 'press-media/search'

# Set this to True to simulate the harvest. If True, do not harvest, but read it from a file.
PURE_PRESS_MEDIA_READ_HARVEST_FROM_FILE = False
# PURE_PRESS_MEDIA_READ_HARVEST_FROM_FILE = True
PURE_PRESS_MEDIA_HARVEST_FILENAME = 'pure_pressmedia_harvest.json'

# Set this to True to read data from the csv file. No harvest will be done, this would
# not make sense. If False, a harvest will be done.
# If True, the value of PURE_PRESS_MEDIA_READ_HARVEST_FROM_FILE does not matter.
PURE_PRESS_MEDIA_READ_DATA_FROM_FILE = False
# PURE_PRESS_MEDIA_READ_DATA_FROM_FILE = True
PURE_PRESS_MEDIA_DATA_FILENAME = 'pure_pressmedia_data.csv'

PURE_PRESS_MEDIA_MAX_RECS_TO_HARVEST = 0                  # 0 = all records
# The current version of the Pure CRUD API does not have these filters yet.
PURE_PRESS_MEDIA_FIELDS = {'fields': ['uuid',
                                      'title.*',
                                      'type.*',
                                      'confidential',
                                      'workflow.*',
                                      'references.*',
                                      'personAssociations.*'
                                      ],
                           # These values will be overwritten.
                           # They exist to prevent a PyCharm warning.
                           'period': {'startDate': {'day': '1',
                                                    'month': '1',
                                                    'year': '0'},
                                      'endDate': {'day': '31',
                                                  'month': '12',
                                                  'year': '9999'},
                                     }
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
ROCATEGORY_PREFIX_PURE = '/dk/atira/pure/researchoutput/researchoutputtypes/'
ROCATEGORY_MAPPING_PURE = {
    ROCATEGORY_PREFIX_PURE + 'bookanthology/anthology': rcg.ROCATEGORY_BOOK,
    ROCATEGORY_PREFIX_PURE + 'bookanthology/book': rcg.ROCATEGORY_BOOK,
    ROCATEGORY_PREFIX_PURE + 'bookanthology/commissioned': rcg.ROCATEGORY_BOOK,
    ROCATEGORY_PREFIX_PURE + 'bookanthology/inaugural': rcg.ROCATEGORY_BOOK,
    ROCATEGORY_PREFIX_PURE + 'bookanthology/registered_report': rcg.ROCATEGORY_REGISTERED_REPORT,
    ROCATEGORY_PREFIX_PURE + 'bookanthology/valedictory': rcg.ROCATEGORY_BOOK,
    ROCATEGORY_PREFIX_PURE + 'contributiontobookanthology/case_note': rcg.ROCATEGORY_MEMORANDUM,
    ROCATEGORY_PREFIX_PURE + 'contributiontobookanthology/chapter': rcg.ROCATEGORY_BOOKCHAPTER,
    ROCATEGORY_PREFIX_PURE + 'contributiontobookanthology/commissioned': rcg.ROCATEGORY_BOOKCHAPTER,
    ROCATEGORY_PREFIX_PURE + 'contributiontobookanthology/conference': rcg.ROCATEGORY_BOOKCHAPTER,
    ROCATEGORY_PREFIX_PURE + 'contributiontobookanthology/entry': rcg.ROCATEGORY_ENTRY,
    ROCATEGORY_PREFIX_PURE + 'contributiontobookanthology/foreword': rcg.ROCATEGORY_ABSTRACT,
    ROCATEGORY_PREFIX_PURE + 'contributiontoconference/abstract': rcg.ROCATEGORY_ABSTRACT,
    ROCATEGORY_PREFIX_PURE + 'contributiontoconference/other': rcg.ROCATEGORY_CONFERENCE_ARTICLE,
    ROCATEGORY_PREFIX_PURE + 'contributiontoconference/paper': rcg.ROCATEGORY_CONFERENCE_ARTICLE,
    ROCATEGORY_PREFIX_PURE + 'contributiontoconference/poster': rcg.ROCATEGORY_POSTER,
    ROCATEGORY_PREFIX_PURE + 'contributiontojournal/abstract': rcg.ROCATEGORY_ABSTRACT,
    ROCATEGORY_PREFIX_PURE + 'contributiontojournal/article': rcg.ROCATEGORY_JOURNAL_ARTICLE,
    ROCATEGORY_PREFIX_PURE + 'contributiontojournal/book': rcg.ROCATEGORY_BOOK,
    ROCATEGORY_PREFIX_PURE + 'contributiontojournal/case_note': rcg.ROCATEGORY_MEMORANDUM,
    ROCATEGORY_PREFIX_PURE + 'contributiontojournal/comment': rcg.ROCATEGORY_MEMORANDUM,
    ROCATEGORY_PREFIX_PURE + 'contributiontojournal/conferencearticle': rcg.ROCATEGORY_CONFERENCE_ARTICLE,
    ROCATEGORY_PREFIX_PURE + 'contributiontojournal/editorial': rcg.ROCATEGORY_EDITORIAL,
    ROCATEGORY_PREFIX_PURE + 'contributiontojournal/erratum': rcg.ROCATEGORY_MEMORANDUM,
    ROCATEGORY_PREFIX_PURE + 'contributiontojournal/letter': rcg.ROCATEGORY_LETTER,
    ROCATEGORY_PREFIX_PURE + 'contributiontojournal/scientific': rcg.ROCATEGORY_JOURNAL_ARTICLE,
    ROCATEGORY_PREFIX_PURE + 'contributiontojournal/shortsurvey': rcg.ROCATEGORY_JOURNAL_ARTICLE,
    ROCATEGORY_PREFIX_PURE + 'contributiontojournal/special': rcg.ROCATEGORY_JOURNAL_ARTICLE,
    ROCATEGORY_PREFIX_PURE + 'contributiontojournal/systematicreview': rcg.ROCATEGORY_REVIEW,
    ROCATEGORY_PREFIX_PURE + 'memorandum/academicmemorandum': rcg.ROCATEGORY_MEMORANDUM,
    ROCATEGORY_PREFIX_PURE + 'methoddescription': rcg.ROCATEGORY_METHOD_DESCRIPTION,
    ROCATEGORY_PREFIX_PURE + 'nontextual/artefact': rcg.ROCATEGORY_ARTEFACT,
    ROCATEGORY_PREFIX_PURE + 'nontextual/database': rcg.ROCATEGORY_DATASET,
    ROCATEGORY_PREFIX_PURE + 'nontextual/design': rcg.ROCATEGORY_DESIGN,
    ROCATEGORY_PREFIX_PURE + 'nontextual/digitalorvisualproducts': rcg.ROCATEGORY_DIGITAL_VISUAL_PRODUCT,
    ROCATEGORY_PREFIX_PURE + 'nontextual/exhibition': rcg.ROCATEGORY_EXHIBITION_PERFORMANCE,
    ROCATEGORY_PREFIX_PURE + 'nontextual/performance': rcg.ROCATEGORY_EXHIBITION_PERFORMANCE,
    ROCATEGORY_PREFIX_PURE + 'nontextual/software': rcg.ROCATEGORY_SOFTWARE,
    ROCATEGORY_PREFIX_PURE + 'nontextual/web': rcg.ROCATEGORY_WEBSITE,
    ROCATEGORY_PREFIX_PURE + 'othercontribution/other': rcg.ROCATEGORY_OTHER_CONTRIBUTION,
    ROCATEGORY_PREFIX_PURE + 'patent/patent': rcg.ROCATEGORY_PATENT,
    ROCATEGORY_PREFIX_PURE + 'thesis/doc1': rcg.ROCATEGORY_PHDTHESIS,
    ROCATEGORY_PREFIX_PURE + 'thesis/doc2': rcg.ROCATEGORY_PHDTHESIS,
    ROCATEGORY_PREFIX_PURE + 'thesis/doc3': rcg.ROCATEGORY_PHDTHESIS,
    ROCATEGORY_PREFIX_PURE + 'thesis/doc4': rcg.ROCATEGORY_PHDTHESIS,
    ROCATEGORY_PREFIX_PURE + 'workingpaper/discussionpaper': rcg.ROCATEGORY_PREPRINT,
    ROCATEGORY_PREFIX_PURE + 'workingpaper/preprint': rcg.ROCATEGORY_PREPRINT,
    ROCATEGORY_PREFIX_PURE + 'workingpaper/workingpaper': rcg.ROCATEGORY_PREPRINT
}


# ######################################################
# Utility functions related to harvesting of Pure
# ######################################################

def create_pure_url(name: str, value: str) -> str:
    """Create a URL to refer to the source of a node.

    :param name: an identifier name, e.g. PURE_ID_PERS, PURE_ID_ORG, etc.
    :param value: the value.
    :return: a URL.
    """
    if name == '' or value == '':
        return ''

    if name == 'PURE_ID_PERS':
        return PURE_URL + '/en/persons/' + value
    elif name == 'PURE_ID_ORG':
        return PURE_URL + '/en/organisations/' + value
    elif name == 'PURE_ID_RESOUT':
        return PURE_URL + '/en/publications/' + value
    elif name == 'PURE_ID_DATASET':
        return PURE_URL + '/en/datasets/' + value
    elif name == 'PURE_ID_PRESS_MEDIA':
        return PURE_URL + '/en/clippings/' + value
    elif name == 'PURE_ID_PROJECT':
        return PURE_URL + '/en/projects/' + value
    else:
        return ''


def create_urlmain(type_id: str, doi_value: str, uuid_value: str) -> str:
    """A helper function for parsed_entities_to_ricgraph()"""
    if type_id == 'DOI':
        return rcg.create_well_known_url(name=type_id,
                                         value=doi_value)
    elif type_id == 'PURE_ID_RESOUT':
        return create_pure_url(name=type_id,
                               value=uuid_value)
    else:
        # Should not happen
        print('create_urlmain(): error')
    return ''


def create_urlother(type_id: str, uuid_value: str) -> str:
    """A helper function for parsed_entities_to_ricgraph()"""
    if type_id == 'DOI':
        return create_pure_url(name='PURE_ID_RESOUT',
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
    to recognized Ricgraph fields (e.g. replace 'doi' with 'DOI').
    No processing of data in columns is done.

    :param df: dataframe with identifiers.
    :return: Result of action described above.
    """
    df_mod = df.copy(deep=True)

    if 'Scopus Author ID' in df_mod.columns:
        df_mod.rename(columns={'Scopus Author ID': 'SCOPUS_AUTHOR_ID'}, inplace=True)

    if 'Researcher ID' in df_mod.columns:
        df_mod.rename(columns={'Researcher ID': 'RESEARCHER_ID'}, inplace=True)

    if 'Digital author ID' in df_mod.columns:
        df_mod.rename(columns={'Digital author ID': 'DIGITAL_AUTHOR_ID'}, inplace=True)

    if 'Employee ID' in df_mod.columns:
        df_mod.rename(columns={'Employee ID': 'EMPLOYEE_ID'}, inplace=True)

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

    print('There are ' + str(len(harvest)) + ' person records ('
          + rcg.timestamp() + '), parsing record:')
    parse_chunk_final = []
    count = 0
    for harvest_item in harvest:
        # parse_chunk: things of this loop we might want to put in the DataFrame with
        # harvested persons to be returned. If so, we add them to parse_chunk_final.
        # If not they will not end up in the harvested persons.
        parse_chunk = []
        count = rcg.print_progress(count=count, interval=1000)
        if (pers_uuid := rcg.json_item_get_str(json_item=harvest_item,
                                               json_path='uuid')) == '':
            # There must be an uuid, otherwise skip.
            continue
        if (lastname := rcg.json_item_get_str(json_item=harvest_item,
                                              json_path='name.lastName')) != '':
            parse_line = {'PURE_ID_PERS': pers_uuid,
                          'FULL_NAME': lastname}
            if (firstname := rcg.json_item_get_str(json_item=harvest_item,
                                                   json_path='name.firstName')) != '':
                parse_line['FULL_NAME'] += ', ' + firstname
            parse_chunk.append(parse_line)
        if (orcid := rcg.json_item_get_str(json_item=harvest_item,
                                           json_path='orcid')) != '':
            parse_line = {'PURE_ID_PERS': pers_uuid,
                          'ORCID': orcid}
            parse_chunk.append(parse_line)

        for identities in rcg.json_item_get_list(json_item=harvest_item,
                                                 json_path='ids'):
            # Field in Pure READ API.
            if (value_identifier := rcg.json_item_get_str(json_item=identities,
                                                          json_path='value.value')) != '' \
               and (name_identifier := rcg.json_item_get_str(json_item=identities,
                                                            json_path='type.term.text.0.value')) != '':
                parse_line = {'PURE_ID_PERS': pers_uuid,
                              name_identifier: value_identifier}
                parse_chunk.append(parse_line)
        for identities in rcg.json_item_get_list(json_item=harvest_item,
                                                 json_path='identifiers'):
            # Field in Pure CRUD API.
            if (value_identifier := rcg.json_item_get_str(json_item=identities,
                                                          json_path='id')) != '' \
               and (name_identifier := rcg.json_item_get_str(json_item=identities,
                                                             json_path='type.term.en_GB')) != '':
                parse_line = {'PURE_ID_PERS': pers_uuid,
                              name_identifier: value_identifier}
                parse_chunk.append(parse_line)

        for stafforg in rcg.json_item_get_list(json_item=harvest_item,
                                               json_path='staffOrganisationAssociations'):
            if (rcg.json_item_get_dict(json_item=stafforg,
                                       json_path='period')) == {}:
                # There is no period, skip.
                continue
            if (enddate := rcg.json_item_get_str(json_item=stafforg,
                                                 json_path='period.endDate')) != '':
                # Only consider persons of current organizations, that is an organization
                # where endData is not existing or empty. If not, then skip.
                end_year = int(enddate[:4])
                if end_year < lowest_resout_year:
                    continue
                # Add all other organizations, because some organizations
                # use an endDate in the future (instead of no endDate)
                # for persons employed.
            if (org_uuid := rcg.json_item_get_str(json_item=stafforg,
                                                  json_path='organisationalUnit.uuid')) != '':
                # Field in Pure READ API.
                if (org_uri := rcg.json_item_get_str(json_item=stafforg,
                                                     json_path='organisationalUnit.type.uri')) != '':
                    if org_uri[-3] == 'r':
                        # Skip research organizations (with an 'r' in the uri, like ..../r05)
                        continue
            elif (org_uuid := rcg.json_item_get_str(json_item=stafforg,
                                                    json_path='organisation.uuid')) != '':
                # Field in Pure CRUD API, where we don't have 'type'.
                pass
            else:
                continue

            parse_line = {'PURE_ID_PERS': pers_uuid,
                          'PURE_ID_ORG': org_uuid}
            parse_chunk.append(parse_line)
            # Put in the DataFrame with harvested persons to be returned.
            parse_chunk_final.extend(parse_chunk)

    rcg.print_progress(count=count, now=True)
    parse_result = pandas.DataFrame(parse_chunk_final)

    if 'PURE_ID_ORG' not in parse_result.columns \
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
    print('There are ' + str(len(harvest)) + ' organization records ('
          + rcg.timestamp() + '), parsing record:')
    parse_chunk = []                # list of dictionaries
    organization_names = {}
    count = 0
    for harvest_item in harvest:
        count = rcg.print_progress(count=count, interval=1000)
        if (org_uuid := rcg.json_item_get_str(json_item=harvest_item,
                                              json_path='uuid')) == '':
            # There must be an uuid, otherwise skip.
            continue

        # Only consider current organizations, that is an organization
        # where endDate is not existing or empty. If not, then skip.
        if rcg.json_item_get_str(json_item=harvest_item,
                                 json_path='period.endDate') != '':
            # Field in Pure READ API.
            continue
        elif rcg.json_item_get_str(json_item=harvest_item,
                                   json_path='lifecycle.endDate') != '':
            # Field in Pure CRUD API.
            continue
        if (org_uri := rcg.json_item_get_str(json_item=harvest_item,
                                             json_path='type.uri')) != '':
            if org_uri[-3] == 'r':
                # Skip research organizations (with an 'r' in the uri, like ..../r05)
                continue
        else:
            # If there is no organization type skip
            continue
        if (rcg.json_item_get_dict(json_item=harvest_item,
                                   json_path='name')) == {}:
            # If there is no name dict skip
            continue

        # Skip the organization ids. There are only a few, and it
        # seems to complicated to implement for now (we will need
        # something like 'organization-root' aka 'person-root').

        if PURE_API_VERSION == PURE_READ_API_VERSION:
            # We are in Pure READ API.
            org_type_name = rcg.json_item_get_str(json_item=harvest_item,
                                                  json_path='type.term.text.0.value')
            org_name = rcg.json_item_get_str(json_item=harvest_item,
                                             json_path='name.text.0.value')
        else:
            # We are in Pure CRUD API.
            org_type_name = rcg.json_item_get_str(json_item=harvest_item,
                                                  json_path='type.term.en_GB')
            org_name = rcg.json_item_get_str(json_item=harvest_item,
                                             json_path='name.en_GB')
        if len(parents := rcg.json_item_get_list(json_item=harvest_item,
                                                 json_path='parents')) == 0:
            # Assume it is the top level organization since it doesn't have a parent.
            # Only necessary to add the top level organization to the dict with organization names.
            organization_names[org_uuid] = construct_extended_org_name(org_name=org_name,
                                                                       org_abbr=organization)
            continue

        for parentorg in parents:
            if (parentorg_uuid := rcg.json_item_get_str(json_item=parentorg,
                                                         json_path='uuid')) == '':
                # There must be an uuid, otherwise skip.
                continue
            # Note: 'parents' does not have a 'period', so we don't need to do something.
            if (parentorg_uri := rcg.json_item_get_str(json_item=parentorg,
                                                        json_path='type.uri')) != '':
                # Field in Pure READ API.
                if parentorg_uri[-3] == 'r':
                    # Skip research organizations (with an 'r' in the uri, like ..../r05)
                    continue
            elif (rcg.json_item_get_str(json_item=parentorg,
                                        json_path='systemName')) != '':
                # Field in Pure CRUD API.
                pass
            else:
                continue
            parse_line = {'PURE_ID_ORG': org_uuid,
                          'ORG_NAME_TYPE': org_type_name,
                          'ORG_NAME': org_name,
                          'ORG_NAME_FULL': organization + ' ' + org_type_name + ': ' + org_name,
                          'PURE_ID_PARENTORG': parentorg_uuid}
            parse_chunk.append(parse_line)
            organization_names[org_uuid] = parse_line['ORG_NAME_FULL']

    rcg.print_progress(count=count, now=True)
    parse_result = pandas.DataFrame(parse_chunk)
    parse_result['PARENTORG_NAME_FULL'] = (
        parse_result[['PURE_ID_PARENTORG']].apply(lambda row:
                                            find_organization_name(uuid=row['PURE_ID_PARENTORG'],
                                                                   organization_names=organization_names),
                                            axis=1))
    return rcg.normalize_identifiers_write_read(parse_result=parse_result,
                                                filename=filename)


def parse_pure_entities(harvest: list,
                        filename: str = '',
                        mode: str = '') -> Union[pandas.DataFrame, None]:
    """Parse the harvested entities from Pure.
    In case filename != '', write it to a file and read it back.

    :param harvest: the harvest.
    :param filename: If filename != '', write it to a file and read it back.
    :param mode: Mode to indicate what to harvest.
    :return: the harvested research outputs in a DataFrame,
        or None if nothing to parse.
    """
    global organization

    if len(harvest) == 0:
        return None
    if mode not in [MODE_RESOUTS, MODE_DATASETS, MODE_PRESS_MEDIA]:
        print('parse_pure_entities: Error, invalid mode "' + mode + '". Exiting.')
        exit(1)

    print('There are ' + str(len(harvest)) + ' ' + mode + ' records ('
          + rcg.timestamp() + '), parsing record:')
    parse_chunk = []                # list of dictionaries
    count = 0
    for harvest_item in harvest:
        count = rcg.print_progress(count=count, interval=1000)
        if (uuid := rcg.json_item_get_str(json_item=harvest_item,
                                                 json_path='uuid')) == '':
            # There must be an uuid, otherwise skip.
            continue
        if (title := rcg.json_item_get_str(json_item=harvest_item,
                                           json_path='title.value')) != '':
            pass
        elif (title := rcg.json_item_get_str(json_item=harvest_item,
                                             json_path='title.text.0.value')) != '':
            pass
        elif (title := rcg.json_item_get_str(json_item=harvest_item,
                                             json_path='references.0.title.text.0.value')) != '':
            pass
        if rcg.json_item_get_bool(json_item=harvest_item,
                                  json_path='confidential'):
            # Skip the confidential ones. Assume non-confidential if not present.
            continue
        if (category := rcg.json_item_get_str(json_item=harvest_item,
                                              json_path='type.uri')) == '':
            # There must be a type (category) of this resout, otherwise skip.
            continue
        # #####
        if (workflow_step := rcg.json_item_get_str(json_item=harvest_item,
                                                   json_path='workflow.workflowStep')) != '':
            # Field in Pure READ API.
            if workflow_step != 'validated' and workflow_step != 'approved':
                # Only 'validated' or 'approved' resouts.
                continue
        elif (workflow_step := rcg.json_item_get_str(json_item=harvest_item,
                                                     json_path='workflow.step')) != '':
            if workflow_step != 'validated' and workflow_step != 'approved':
                # Only 'validated' or 'approved' resouts.
                continue
        else:
            # Skip if no workflow.
            continue
        # #####
        publication_year = ''
        if mode == MODE_RESOUTS:
            if len(rcg.json_item_get_list(json_item=harvest_item,
                                          json_path='publicationStatuses')) == 0:
                # Skip if no publicationStatuses.
                continue
            published_found = False
            for pub_item in rcg.json_item_get_list(json_item=harvest_item,
                                                   json_path='publicationStatuses'):
                if pub_item['current']:
                    publication_year = str(rcg.json_item_get_int(json_item=pub_item,
                                                                 json_path='publicationDate.year'))
                    publication_path = rcg.json_item_get_str(json_item=pub_item,
                                                             json_path='publicationStatus.uri')
                    if PurePath(publication_path).name == 'published':
                        published_found = True
                        break
            if not published_found:
                # We need a 'published' status.
                continue
        elif mode == MODE_DATASETS:
            publication_year = rcg.json_item_get_str(json_item=harvest_item,
                                                     json_path='publicationDate.year')
        elif mode == MODE_PRESS_MEDIA:
            publication_year = rcg.json_item_get_str(json_item=harvest_item,
                                                     json_path='references.0.date')
            publication_year = publication_year[:4]
        # #####
        doi = ''
        if mode == MODE_RESOUTS:
            for dois in rcg.json_item_get_list(json_item=harvest_item,
                                            json_path='electronicVersions'):
                # Take the last DOI found for a resout.
                if (newdoi := rcg.json_item_get_str(json_item=dois, json_path='doi')) != '':
                    doi = newdoi
        elif mode == MODE_DATASETS:
            doi = rcg.json_item_get_str(json_item=harvest_item,
                                        json_path='doi')
        elif mode == MODE_PRESS_MEDIA:
            # Press media items do not have a DOI.
            doi = ''
        doi = rcg.normalize_doi(identifier=doi)
        # #####
        id_name = id_name_tobeused = ''
        if mode == MODE_RESOUTS:
            id_name = id_name_tobeused = 'PURE_ID_RESOUT'
            category = rcg.lookup_resout_category(research_output_category=category,
                                                  research_output_mapping=ROCATEGORY_MAPPING_PURE)
        elif mode == MODE_DATASETS:
            # Treat data sets of Pure endpoint datasets as data sets from Pure
            # endpoint researchoutputs.
            id_name = 'PURE_ID_DATASET'
            id_name_tobeused = 'PURE_ID_RESOUT'
            category = rcg.ROCATEGORY_DATASET
        elif mode == MODE_PRESS_MEDIA:
            id_name = id_name_tobeused = 'PURE_ID_PRESS_MEDIA'
            category = rcg.CATEGORY_PRESS_MEDIA
        # #####
        if len(list_of_persons := rcg.json_item_get_list(json_item=harvest_item,
                                                         json_path='personAssociations')) > 0:
            # Field in Pure READ API.
            pass
        elif len(list_of_persons := rcg.json_item_get_list(json_item=harvest_item,
                                                           json_path='contributors')) > 0:
            # Field in Pure CRUD API.
            pass
        else:
            continue
        for persons in list_of_persons:
            externalorg_name = ''
            if (author_uuid := rcg.json_item_get_str(json_item=persons,
                                                     json_path='person.uuid')) != '':
                # Internal person, don't set 'external_author_name', it is not necessary.
                external_author_name = ''
            elif (author_uuid := rcg.json_item_get_str(json_item=persons,
                                                       json_path='externalPerson.uuid')) != '':
                # External person.
                external_author_name = rcg.json_item_get_str(json_item=persons,
                                                    json_path='externalPerson.name.text.0.value')
                # Get the external organization of this person.
                # There may be many externalOrganizations, for now we only take the first.
                externalorg_name = rcg.json_item_get_str(json_item=persons,
                                                                json_path='externalOrganisations.0.name.text.0.value')
            elif (author_uuid := rcg.json_item_get_str(json_item=persons,
                                                       json_path='authorCollaboration.uuid')) != '':
                # Author collaboration.
                external_author_name = rcg.json_item_get_str(json_item=persons,
                                                    json_path='authorCollaboration.name.text.0.value')
                external_author_name += ' (' + organization + ' author collaboration)'
            else:
                # If we get here you might want to add another "elif" above with
                # the missing personAssociation. Sometimes there is none, then it is ok.
                # Do not print a warning message, most of the time it is an external person
                # without any identifier.
                continue
            # #####
            parse_line = {}
            if mode == MODE_PRESS_MEDIA:
                if (press_media_url := rcg.json_item_get_str(json_item=harvest_item,
                                                             json_path='references.0.url')) != '':
                    parse_line = {'NAME': id_name_tobeused,
                                  'CATEGORY': category,
                                  'VALUE': uuid,
                                  'URL_MAIN': press_media_url,
                                  'URL_OTHER': create_pure_url(name=id_name,
                                                               value=uuid)
                                  }
            elif doi != '':
                parse_line = {'NAME': 'DOI',
                              'CATEGORY': category,
                              'VALUE': doi,
                              'URL_MAIN': rcg.create_well_known_url(name='DOI',
                                                                    value=doi),
                              'URL_OTHER': create_pure_url(name=id_name,
                                                           value=uuid)
                              }
            # #####
            if len(parse_line) == 0:
                # All other situations.
                parse_line = {'NAME': id_name_tobeused,
                              'CATEGORY': category,
                              'VALUE': uuid,
                              'URL_MAIN': create_pure_url(name=id_name,
                                                          value=uuid),
                              'URL_OTHER': ''
                              }
            if mode == MODE_RESOUTS:
                parse_line['EXTERNAL_AUTHOR_NAME'] = external_author_name
                if externalorg_name != '':
                    parse_line['EXTERNAL_ORG_NAME'] = externalorg_name
            # '|=': merges a dict in place with another dict.
            parse_line |= {'TITLE': title,
                           'YEAR': publication_year,
                           'PURE_ID_PERS': author_uuid}
            parse_chunk.append(parse_line)

    rcg.print_progress(count=count, now=True)
    if len(parse_chunk) == 0 \
       and PURE_API_VERSION == PURE_CRUD_API_VERSION:
        print('\nPure is harvested using the Pure CRUD API.')
        print('No entities were found.')
        print('This is probably caused by one or more of the following fields not present in')
        print('the CRUD API export for "research outputs":')
        print('"workflow", "publicationStatuses" and/or "contributors".')
        print('Please ask your Pure administrator to export these fields. Exiting.')
        exit(1)

    parse_result = pandas.DataFrame(parse_chunk)
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
    # RDTJ, February 22, 2026. This code should be cleaned up,
    # just as the functions for persons, organizations, and entities above.
    # Also rewrite parsed_projects_to_ricgraph().
    global resout_uuid_or_doi
    global organization

    if len(harvest) == 0:
        return None
    print('There are ' + str(len(harvest)) + ' project records ('
          + rcg.timestamp() + '), parsing record:')
    parse_chunk = []                # list of dictionaries
    count = 0
    for harvest_item in harvest:
        count = rcg.print_progress(count=count, interval=1000)
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
                name = str(PurePath(harvest_item['ids'][0]['type']['uri']).name)
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

                parse_line = {'PURE_ID_PROJECT': uuid,
                              'PURE_ID_PROJECT_URL': create_pure_url(name='PURE_ID_PROJECT',
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
                    category = rcg.lookup_resout_category(research_output_category=str(resout['type']['uri']),
                                                          research_output_mapping=ROCATEGORY_MAPPING_PURE)
                else:
                    continue

                resout_name = 'PURE_ID_RESOUT'
                resout_value = resout_uuid
                if resout_uuid_or_doi != {} \
                   and resout_uuid in resout_uuid_or_doi:
                    resout_value = resout_uuid_or_doi[resout_uuid]
                    if not numpy.isnan(resout_value):
                        if '/' in resout_value:
                            resout_name = 'DOI'
                        else:
                            resout_name = 'PURE_ID_RESOUT'
                parse_line = {'PURE_ID_PROJECT': uuid,
                              'PURE_ID_PROJECT_URL': create_pure_url(name='PURE_ID_PROJECT',
                                                                     value=uuid),
                              'PURE_PROJECT_TITLE': title,
                              'PURE_PROJECT_RESOUT_NAME': resout_name,
                              'PURE_PROJECT_RESOUT_CATEGORY': category,
                              'PURE_PROJECT_RESOUT_VALUE': resout_value}
                parse_chunk.append(parse_line)

        if 'relatedProjects' in harvest_item:
            for related_project in harvest_item['relatedProjects']:
                if 'project' in related_project \
                   and 'uuid' in related_project['project']:
                    related_project_uuid = str(related_project['project']['uuid'])
                else:
                    continue

                parse_line = {'PURE_ID_PROJECT': uuid,
                              'PURE_ID_PROJECT_URL': create_pure_url(name='PURE_ID_PROJECT',
                                                                     value=uuid),
                              'PURE_PROJECT_TITLE': title,
                              'PURE_PROJECT_RELATEDPROJECT_UUID': related_project_uuid}
                parse_chunk.append(parse_line)

    rcg.print_progress(count=count, now=True)
    parse_result = pandas.DataFrame(parse_chunk)
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
                                year_start:str = '',
                                year_end: str = '') -> Union[pandas.DataFrame, None]:
    """Harvest and parse data from Pure.

    :param mode: as in MODE_ALL, to indicate what to harvest.
    :param endpoint: endpoint Pure.
    :param headers: headers for Pure.
    :param body: the body of a POST request, or '' for a GET request.
    :param harvest_filename: filename to write harvest results to.
    :param df_filename: filename to write the DataFrame results to.
    :param year_start: the first year that we would like to harvest.
        Only relevant when parsing persons and data sets.
    :param year_end: the first year that we would like to harvest.
        Only relevant when data sets.
    :return: the DataFrame harvested, or None if nothing harvested.
    """
    if mode not in MODE_ALL:
        print('harvest_and_parse_pure_data(): unknown mode ' + mode + '.')
        return None

    if mode == MODE_PERSONS:
        max_recs_to_harvest = PURE_PERSONS_MAX_RECS_TO_HARVEST
    elif mode == MODE_ORGANIZATIONS:
        max_recs_to_harvest = PURE_ORGANIZATIONS_MAX_RECS_TO_HARVEST
    elif mode == MODE_RESOUTS:
        max_recs_to_harvest = PURE_RESOUTS_MAX_RECS_TO_HARVEST
    elif mode == MODE_DATASETS:
        max_recs_to_harvest = PURE_DATASETS_MAX_RECS_TO_HARVEST
    elif mode == MODE_PRESS_MEDIA:
        max_recs_to_harvest = PURE_PRESS_MEDIA_MAX_RECS_TO_HARVEST
    elif mode == MODE_PROJECTS:
        max_recs_to_harvest = PURE_PROJECTS_MAX_RECS_TO_HARVEST
    else:
        # Should not happen
        return None

    print('Harvesting ' + mode + ' from ' + HARVEST_SOURCE + '...')
    if (mode == MODE_PERSONS and not PURE_PERSONS_READ_HARVEST_FROM_FILE) \
       or (mode == MODE_ORGANIZATIONS and not PURE_ORGANIZATIONS_READ_HARVEST_FROM_FILE) \
       or (mode == MODE_RESOUTS and not PURE_RESOUTS_READ_HARVEST_FROM_FILE) \
       or (mode == MODE_DATASETS and not PURE_DATASETS_READ_HARVEST_FROM_FILE) \
       or (mode == MODE_PRESS_MEDIA and not PURE_PRESS_MEDIA_READ_HARVEST_FROM_FILE) \
       or (mode == MODE_PROJECTS and not PURE_PROJECTS_READ_HARVEST_FROM_FILE):
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
    if mode == MODE_PERSONS:
        parse = parse_pure_persons(harvest=harvest_data, filename=df_filename,
                                   year_start=year_first)
    elif mode == MODE_ORGANIZATIONS:
        parse = parse_pure_organizations(harvest=harvest_data, filename=df_filename)
    elif mode == MODE_RESOUTS:
        parse = parse_pure_entities(harvest=harvest_data, filename=df_filename,
                                    mode=mode)
    elif mode == MODE_DATASETS:
        # For Pure end point 'datasets', there is no way to specify the year range.
        # So traverse the items found and only keep the ones in the correct range.
        print('Removing data sets that are not in the correct year range.')
        harvest_data_new = []
        for harvest_item in harvest_data:
            publication_year = rcg.json_item_get_str(json_item=harvest_item,
                                                     json_path='publicationDate.year')
            if int(year_start) <= int(publication_year) <= int(year_end):
                harvest_data_new.append(harvest_item)
        parse = parse_pure_entities(harvest=harvest_data_new, filename=df_filename,
                                    mode=mode)
    elif mode == MODE_PRESS_MEDIA:
        parse = parse_pure_entities(harvest=harvest_data, filename=df_filename,
                                    mode=mode)
    elif mode == MODE_PROJECTS:
        parse = parse_pure_projects(harvest=harvest_data, filename=df_filename)

    if parse is None or parse.empty:
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
    all_possible_cols = ['PURE_ID_PERS', 'FULL_NAME', 'ORCID', 'ISNI',
                         'SCOPUS_AUTHOR_ID', 'DIGITAL_AUTHOR_ID',
                         'RESEARCHER_ID', 'EMPLOYEE_ID']
    existing_cols = [c for c in all_possible_cols if c in parsed_content.columns]
    person_identifiers = parsed_content[existing_cols].copy(deep=True)
    rcg.create_parsed_persons_in_ricgraph(person_identifiers=person_identifiers,
                                          harvest_source=HARVEST_SOURCE)
    # Add the URL to this person in Pure. Some persons do not seem to have
    # this page.
    nodes_to_update = parsed_content[['PURE_ID_PERS']].copy(deep=True)
    nodes_to_update['URL_MAIN'] = nodes_to_update[['PURE_ID_PERS']].apply(
                                  lambda row: create_pure_url(name='PURE_ID_PERS',
                                                              value=row['PURE_ID_PERS']), axis=1)
    rcg.update_urls_in_ricgraph(entities=nodes_to_update,
                               harvest_source=HARVEST_SOURCE,
                               what='URLs of PURE_ID_PERS nodes')
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
    parsed_content = parsed_content_organizations[['PURE_ID_ORG',
                                                   'ORG_NAME_FULL',
                                                   'PURE_ID_PARENTORG']].copy(deep=True)
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

    # 2nd loop: Do the same for PURE_ID_PARENTORG and PARENTORG_NAME_FULL. This is necessary because the
    # top-level org will not be in PURE_ID_ORG.
    parsed_content = parsed_content_organizations[['PURE_ID_PARENTORG',
                                                   'PARENTORG_NAME_FULL']].copy(deep=True)
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

    print('Determining all links between persons and all of their organizations...', end=' ')
    parsed_content = parsed_content_persons[['PURE_ID_PERS',
                                             'PURE_ID_ORG']].copy(deep=True)
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
            parse_line = {'PURE_ID_PERS': str(personid),
                          'PURE_ID_ORG': orgid,
                          'ORG_NAME_FULL': orgid_name}
            parse_chunk.append(parse_line)

            # Now get all parents of orgid.
            # Then connect this person with the parents of 'orgid'.
            for index in range(len(orgid_name_and_parentslist)):
                if index == 0:
                    # Remember: first entry in list is the name of the org.
                    continue
                parse_line = {'PURE_ID_PERS': str(personid)}
                parent_orgid = str(orgid_name_and_parentslist[index])
                parent_name = str(organization_and_all_parents[parent_orgid][0])
                parse_line['PURE_ID_ORG'] = parent_orgid
                parse_line['ORG_NAME_FULL'] = parent_name
                parse_chunk.append(parse_line)

    print('Done.\n')

    if len(parse_chunk) == 0:
        print('No link found between persons and all of their organizations.')
        return

    persorgnodes = pandas.DataFrame(parse_chunk)
    # Add the URL to this organization in Pure. Some organizations do
    # not seem to have this page.
    persorgnodes['URL_MAIN'] = persorgnodes[['PURE_ID_ORG']].apply(
                               lambda row: create_pure_url(name='PURE_ID_ORG',
                                                           value=row['PURE_ID_ORG']), axis=1)
    persorgnodes.drop(labels='PURE_ID_ORG', axis='columns', inplace=True)
    persorgnodes.rename(columns={'ORG_NAME_FULL': 'ORGANIZATION_NAME'}, inplace=True)
    rcg.create_parsed_entities_in_ricgraph(entities=persorgnodes,
                                           harvest_source=HARVEST_SOURCE,
                                           what='organizations')
    return


def parsed_entities_to_ricgraph(parsed_content: pandas.DataFrame,
                                what: str = 'entities') -> None:
    """Insert the parsed entities in Ricgraph.

    :param parsed_content: The records to insert in Ricgraph, if not present yet.
    :param what: Text to show to the user and in '_source'
    :return: None.
    """
    global resout_uuid_or_doi

    cols = ['PURE_ID_PERS', 'NAME', 'CATEGORY', 'VALUE', 'TITLE', 'YEAR']
    if 'URL_MAIN' in parsed_content.columns:
        cols.append('URL_MAIN')
    if 'URL_OTHER' in parsed_content.columns:
        cols.append('URL_OTHER')
    resouts = parsed_content[cols].copy(deep=True)
    if HARVEST_PROJECTS:
        # This is only necessary if we are going to harvest projects later on.
        # 26-2-2026: This code used to be (before a thorough rewrite of harvesting Pure):
        # if resout_uuid_or_doi == {}:
        #     resout_uuid_or_doi = dict(zip(resouts.PURE_ID_RESOUT, resouts.value1))
        # else:
        #     resout_uuid_or_doi.update((zip(resouts.PURE_ID_RESOUT, resouts.value1)))
        # At the rewrite, I made it as follows, but this may not be correct.
        # It needs to be tested (just as the code for projects needs to be rewritten).
        if resout_uuid_or_doi == {}:
            resout_uuid_or_doi = dict(zip(resouts.NAME, resouts.VALUE))
        else:
            resout_uuid_or_doi.update((zip(resouts.NAME, resouts.VALUE)))

    rcg.create_parsed_entities_in_ricgraph_general(entities=resouts,
                                                   harvest_source=HARVEST_SOURCE,
                                                   what=what)

    if 'EXTERNAL_AUTHOR_NAME' in parsed_content.columns:
        # This is specifically for external persons and author collaborations. We only
        # find these while parsing entities, not while parsing persons.
        external_persons = parsed_content[['PURE_ID_PERS', 'EXTERNAL_AUTHOR_NAME']].copy(deep=True)
        external_persons.rename(columns={'EXTERNAL_AUTHOR_NAME': 'FULL_NAME'}, inplace=True)
        rcg.create_parsed_entities_in_ricgraph(entities=external_persons,
                                               harvest_source=HARVEST_SOURCE,
                                               what=what + ': external persons and author collaborations')

    if 'EXTERNAL_ORG_NAME' in parsed_content.columns:
        # This is specifically for external persons and external organizations. We only
        # find these while parsing entities, not while parsing persons.
        persorgnodes = parsed_content[['PURE_ID_PERS',
                                       'EXTERNAL_ORG_NAME']].copy(deep=True)
        persorgnodes.rename(columns={'EXTERNAL_ORG_NAME': 'ORGANIZATION_NAME'}, inplace=True)
        rcg.create_parsed_entities_in_ricgraph(entities=persorgnodes,
                                               harvest_source=HARVEST_SOURCE,
                                               what=what + ': external organizations from external persons')
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
    # Also rewrite parse_pure_projects().
    timestamp = rcg.datetimestamp()
    print('Inserting projects from ' + HARVEST_SOURCE + ' in Ricgraph at '
          + timestamp + '...')
    history_event = 'Source: Harvest ' + HARVEST_SOURCE + ' projects at ' + timestamp + '.'

    # ##### Insert projects and related participants.
    project_identifiers = parsed_content[['PURE_ID_PROJECT',
                                          'PURE_ID_PROJECT_URL',
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
    project_identifiers.rename(columns={'PURE_ID_PROJECT': 'value1',
                                        'PURE_ID_PROJECT_URL': 'url_main1',
                                        'PURE_PROJECT_TITLE': 'comment1',
                                        'PURE_PROJECT_PARTICIPANT_UUID': 'value2'}, inplace=True)
    new_project_columns = {'name1': 'PURE_ID_PROJECT',
                           'category1': 'project',
                           'source_event1': HARVEST_SOURCE,
                           'history_event1': history_event,
                           'name2': 'PURE_ID_PERS',
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
        project_identifiers = parsed_content[['PURE_ID_PROJECT',
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
                parse_line = {'PURE_ID_PROJECT': str(projectid),
                              'PURE_ID_ORG': orgid,
                              'ORG_NAME_FULL': orgid_name}
                parse_chunk.append(parse_line)

                # Now get all parents of orgid.
                # Then connect this person with the parents of 'orgid'.
                for index in range(len(orgid_name_and_parentslist)):
                    if index == 0:
                        # Remember: first entry in list is the name of the org.
                        continue
                    parse_line = {'PURE_ID_PROJECT': str(projectid)}
                    parent_orgid = str(orgid_name_and_parentslist[index])
                    parent_name = str(organization_and_all_parents[parent_orgid][0])
                    parse_line['PURE_ID_ORG'] = parent_orgid
                    parse_line['ORG_NAME_FULL'] = parent_name
                    parse_chunk.append(parse_line)

        print('Done at ' + rcg.timestamp() + '.\n')

        projorgnodes = pandas.DataFrame()
        parse_chunk_df = pandas.DataFrame(parse_chunk)
        projorgnodes = pandas.concat([projorgnodes, parse_chunk_df], ignore_index=True)

        projorgnodes.drop(labels='PURE_ID_ORG', axis='columns', inplace=True)
        projorgnodes.dropna(axis=0, how='any', inplace=True)
        projorgnodes.drop_duplicates(keep='first', inplace=True, ignore_index=True)
        projorgnodes.rename(columns={'PURE_ID_PROJECT': 'value1',
                                     'ORG_NAME_FULL': 'value2'}, inplace=True)
        new_projorgnodes_columns = {'name1': 'PURE_ID_PROJECT',
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
    project_identifiers = parsed_content[['PURE_ID_PROJECT',
                                          'PURE_PROJECT_RESOUT_NAME',
                                          'PURE_PROJECT_RESOUT_CATEGORY',
                                          'PURE_PROJECT_RESOUT_VALUE']].copy(deep=True)
    # dropna(how='all'): drop row if all row values contain NaN
    project_identifiers.dropna(axis=0, how='any', inplace=True)
    project_identifiers.drop_duplicates(keep='first', inplace=True, ignore_index=True)

    print('The following projects connected to research outputs from '
          + HARVEST_SOURCE + ' will be inserted in Ricgraph at ' + rcg.timestamp() + ':')
    print(project_identifiers)
    project_identifiers.rename(columns={'PURE_ID_PROJECT': 'value1',
                                        'PURE_PROJECT_RESOUT_NAME': 'name2',
                                        'PURE_PROJECT_RESOUT_CATEGORY': 'category2',
                                        'PURE_PROJECT_RESOUT_VALUE': 'value2'}, inplace=True)
    new_project_columns = {'name1': 'PURE_ID_PROJECT',
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
        project_identifiers = parsed_content[['PURE_ID_PROJECT',
                                              'PURE_PROJECT_RELATEDPROJECT_UUID']].copy(deep=True)
        project_identifiers.dropna(axis=0, how='any', inplace=True)
        project_identifiers.drop_duplicates(keep='first', inplace=True, ignore_index=True)

        print('The following projects connected to related projects from '
              + HARVEST_SOURCE + ' will be inserted in Ricgraph at ' + rcg.timestamp() + ':')
        print(project_identifiers)
        project_identifiers.rename(columns={'PURE_ID_PROJECT': 'value1',
                                            'PURE_PROJECT_RELATEDPROJECT_UUID': 'value2'}, inplace=True)
        new_project_columns = {'name1': 'PURE_ID_PROJECT',
                               'category1': 'project',
                               'name2': 'PURE_ID_PROJECT',
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
    PURE_RESOUTS_ENDPOINT = PURE_READ_RESOUTS_ENDPOINT
    PURE_RESOUTS_FIELDS = PURE_READ_RESOUTS_FIELDS
    PURE_PRESS_MEDIA_ENDPOINT = PURE_READ_PRESS_MEDIA_ENDPOINT
    PURE_DATASETS_ENDPOINT = PURE_READ_DATASETS_ENDPOINT
    PURE_PROJECTS_ENDPOINT = PURE_READ_PROJECTS_ENDPOINT
elif crud_response.status_code == requests.codes.ok:
    print('Pure will be harvested using the Pure CRUD API.')
    PURE_API_VERSION = PURE_CRUD_API_VERSION
    PURE_PERSONS_ENDPOINT = PURE_CRUD_PERSONS_ENDPOINT
    PURE_ORGANIZATIONS_ENDPOINT = PURE_CRUD_ORGANIZATIONS_ENDPOINT
    PURE_RESOUTS_ENDPOINT = PURE_CRUD_RESOUTS_ENDPOINT
    PURE_RESOUTS_FIELDS = PURE_CRUD_RESOUTS_FIELDS
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
# You can use 'True' or 'False' depending on your needs to harvest
# persons/organizations/research outputs/data sets/press media items.
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

if HARVEST_PERSONS:
    if PURE_PERSONS_READ_DATA_FROM_FILE:
        error_message = 'There are no persons from ' + HARVEST_SOURCE + ' to read from file ' + data_file + '.\n'
        print('Reading persons from ' + HARVEST_SOURCE + ' from file ' + data_file + '.')
        parse_persons = rcg.read_dataframe_from_csv(filename=data_file, datatype=str)
    else:
        error_message = 'There are no persons from ' + HARVEST_SOURCE + ' to harvest.\n'
        print('Harvesting persons from ' + HARVEST_SOURCE + '.')
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
if HARVEST_ORGANIZATIONS:
    # Uncomment the next line for (some) debugging purposes.
    # You might also want to set 'PURE_PERSONS_READ_HARVEST_FROM_FILE = True'
    # at the top of this file.
    if not HARVEST_PERSONS:
        parse_persons = rcg.read_dataframe_from_csv(filename=data_file, datatype=str)

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
if HARVEST_RESOUTS:
    # Note that in 2023, the Pure CRUD API did not allow
    # harvesting separate years. This might cause memory problems.
    # You might want to set PURE_RESOUTS_MAX_RECS_TO_HARVEST.
    # The Pure READ API does allow to specify years to harvest.
    for year_int in range(int(year_first), int(year_last) + 1):
        year = str(year_int)
        data_file_year = rcg.construct_filename(base_filename=PURE_RESOUTS_DATA_FILENAME,
                                                year=year, organization=organization)
        if PURE_RESOUTS_READ_DATA_FROM_FILE:
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
            harvest_file_year = rcg.construct_filename(base_filename=PURE_RESOUTS_HARVEST_FILENAME,
                                                       year=year, organization=organization)
            PURE_RESOUTS_FIELDS['publishedBeforeDate'] = year + '-12-31'
            PURE_RESOUTS_FIELDS['publishedAfterDate'] = year + '-01-01'
            parse_resout = harvest_and_parse_pure_data(mode=MODE_RESOUTS,
                                                       endpoint=PURE_RESOUTS_ENDPOINT,
                                                       headers=PURE_HEADERS,
                                                       body=PURE_RESOUTS_FIELDS,
                                                       harvest_filename=harvest_file_year,
                                                       df_filename=data_file_year)

        if parse_resout is None or parse_resout.empty:
            print(error_message)
        else:
            parsed_entities_to_ricgraph(parsed_content=parse_resout,
                                        what='research outputs')

        rcg.graphdb_nr_accesses_print()
        print(rcg.nodes_cache_key_id_type_size() + '\n')


# ########################################################################
# Code for data sets from the Pure datasets endpoint.
if HARVEST_DATASETS:
    if PURE_API_VERSION == PURE_CRUD_API_VERSION:
        print('\nPure is harvested using the Pure CRUD API.')
        print('Harvesting data sets from Pure using the CRUD API is not implemented yet.')
        exit(1)

    data_file = rcg.construct_filename(base_filename=PURE_DATASETS_DATA_FILENAME,
                                       organization=organization)
    if PURE_DATASETS_READ_DATA_FROM_FILE:
        error_message = 'There are no data sets from ' + HARVEST_SOURCE
        error_message += ' for year ' + year_first + ' to ' + year_last
        error_message += ' to read from file ' + data_file + '.\n'
        print('Reading data sets from ' + HARVEST_SOURCE + ' for year '
              + year_first + ' to ' + year_last + ' from file ' + data_file + '.')
        parse_datasets = rcg.read_dataframe_from_csv(filename=data_file,
                                                        datatype=str)
    else:
        error_message = 'There are no data sets from ' + HARVEST_SOURCE
        error_message += ' for year ' + year_first + ' to ' + year_last
        error_message += ' to harvest.\n'
        print('Harvesting data sets from ' + HARVEST_SOURCE
              + ' for year ' + year_first + ' to ' + year_last + '.')
        harvest_file = rcg.construct_filename(base_filename=PURE_DATASETS_HARVEST_FILENAME,
                                              organization=organization)
        parse_datasets = harvest_and_parse_pure_data(mode=MODE_DATASETS,
                                                     endpoint=PURE_DATASETS_ENDPOINT,
                                                     headers=PURE_HEADERS,
                                                     body=PURE_DATASETS_FIELDS,
                                                     harvest_filename=harvest_file,
                                                     df_filename=data_file,
                                                     year_start=year_first,
                                                     year_end=year_last)

    if parse_datasets is None or parse_datasets.empty:
        print(error_message)
    else:
        parsed_entities_to_ricgraph(parsed_content=parse_datasets,
                                    what='data sets (from Pure datasets endpoint)')

    rcg.graphdb_nr_accesses_print()
    print(rcg.nodes_cache_key_id_type_size() + '\n')


# ########################################################################
# Code for harvesting press media items.
if HARVEST_PRESS_MEDIA:
    if PURE_API_VERSION == PURE_CRUD_API_VERSION:
        print('\nPure is harvested using the Pure CRUD API.')
        print('Harvesting press media items from Pure using the CRUD API is not implemented yet.')
        exit(1)

    data_file = rcg.construct_filename(base_filename=PURE_PRESS_MEDIA_DATA_FILENAME,
                                       organization=organization)
    if PURE_PRESS_MEDIA_READ_DATA_FROM_FILE:
        error_message = 'There are no press media items from ' + HARVEST_SOURCE
        error_message += ' for year ' + year_first + ' to ' + year_last
        error_message += ' to read from file ' + data_file + '.\n'
        print('Reading press media items from ' + HARVEST_SOURCE + ' for year '
              + year_first + ' to ' + year_last + ' from file ' + data_file + '.')
        parse_press_media = rcg.read_dataframe_from_csv(filename=data_file,
                                                        datatype=str)
    else:
        error_message = 'There are no press media items from ' + HARVEST_SOURCE
        error_message += ' for year ' + year_first + ' to ' + year_last
        error_message += ' to harvest.\n'
        print('Harvesting press media items from ' + HARVEST_SOURCE
              + ' for year ' + year_first + ' to ' + year_last + '.')
        harvest_file = rcg.construct_filename(base_filename=PURE_PRESS_MEDIA_HARVEST_FILENAME,
                                              organization=organization)
        PURE_PRESS_MEDIA_FIELDS['period']['startDate'] = {'day': '1',
                                                          'month': '1',
                                                          'year': year_first}
        PURE_PRESS_MEDIA_FIELDS['period']['endDate'] = {'day': '31',
                                                        'month': '12',
                                                        'year': year_last}
        parse_press_media = harvest_and_parse_pure_data(mode=MODE_PRESS_MEDIA,
                                                        endpoint=PURE_PRESS_MEDIA_ENDPOINT,
                                                        headers=PURE_HEADERS,
                                                        body=PURE_PRESS_MEDIA_FIELDS,
                                                        harvest_filename=harvest_file,
                                                        df_filename=data_file)

    if parse_press_media is None or parse_press_media.empty:
        print(error_message)
    else:
        parsed_entities_to_ricgraph(parsed_content=parse_press_media,
                                    what='press media items')

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
