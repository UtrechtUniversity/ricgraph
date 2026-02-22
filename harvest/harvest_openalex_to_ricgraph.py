# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
# 
# Copyright (c) 2023 - 2026 Rik D.T. Janssen
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
# Updated Rik D.T. Janssen, February 2026.
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
#   --year_first <first year of harvest>
#           Start the harvest from this year on.
#   --year_last <last year of harvest>
#           End the harvest at this year.
#
# ########################################################################


import sys
import pandas
from typing import Union
from pathlib import PurePath
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
# If True, the value of OPENALEX_READ_HARVEST_FROM_FILE does not matter.
OPENALEX_READ_DATA_FROM_FILE = False
# OPENALEX_READ_DATA_FROM_FILE = True
OPENALEX_DATA_FILENAME = 'openalex_data.csv'

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


# ######################################################
# Parsing
# ######################################################

def parse_openalex(harvest: list,
                   filename: str = '') -> Union[pandas.DataFrame, None]:
    """Parse the harvested persons and research outputs from OpenAlex.
    In case filename != '', write it to a file and read it back.

    :param harvest: the harvest.
    :param filename: If filename != '', write it to a file and read it back.
    :return: the harvested persons in a DataFrame, or None if nothing to parse.
    """
    if len(harvest) == 0:
        return None
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

        for authors in rcg.json_item_get_list(json_item=harvest_item,
                                              json_path='authorships'):
            if (openalex_path := rcg.json_item_get_str(json_item=authors,
                                                       json_path='author.id')) == '':
                # There must be an id, otherwise skip.
                continue

            openalex_id = PurePath(openalex_path).name
            if (orcid_path := rcg.json_item_get_str(json_item=authors,
                                                    json_path='author.orcid')) != '':
                parse_line = {'OPENALEX': openalex_id,
                              'ORCID': PurePath(orcid_path).name}
                parse_chunk.append(parse_line)

            if (display_name := rcg.json_item_get_str(json_item=authors,
                                                      json_path='author.display_name')) != '':
                parse_line = {'OPENALEX': openalex_id,
                              'FULL_NAME': display_name}
                parse_chunk.append(parse_line)

            for institution in rcg.json_item_get_list(json_item=authors, json_path='institutions'):
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
                if (ror_path := rcg.json_item_get_str(json_item=institution,
                                                      json_path='ror')) == '':
                    continue

                parse_line = {'OPENALEX': openalex_id,
                              'ROR': PurePath(ror_path).name}
                if (display_name := rcg.json_item_get_str(json_item=institution,
                                                          json_path='display_name')) != '':
                    parse_line['ORGANIZATION_NAME'] = display_name
                parse_chunk.append(parse_line)

            if (doi := rcg.json_item_get_str(json_item=harvest_item,
                                             json_path='doi')) == '' \
               or (title := rcg.json_item_get_str(json_item=harvest_item,
                                                  json_path='title')) == '' \
               or (resout_type := rcg.json_item_get_str(json_item=harvest_item,
                                                        json_path='type')) == '':
                continue

            publication_year = rcg.json_item_get_str(json_item=harvest_item,
                                                     json_path='publication_year')
            parse_line = {'OPENALEX': openalex_id,
                          'DOI': rcg.normalize_doi(identifier=doi),
                          'TITLE': title,
                          'YEAR': publication_year,
                          'TYPE': rcg.lookup_resout_type(research_output_type=resout_type,
                                                         research_output_mapping=ROTYPE_MAPPING_OPENALEX)}
            parse_chunk.append(parse_line)

    print(count, '(' + rcg.timestamp() + ')\n', end='', flush=True)

    parse_chunk_df = pandas.DataFrame(parse_chunk)
    parse_result = pandas.concat(objs=[parse_result, parse_chunk_df], ignore_index=True)
    return rcg.normalize_identifiers_write_read(parse_result=parse_result,
                                                filename=filename)


# ######################################################
# Harvesting and parsing
# ######################################################

def harvest_and_parse_openalex(harvest_year: str,
                               headers: dict,
                               harvest_filename: str,
                               df_filename: str) -> Union[pandas.DataFrame, None]:
    """Harvest and parse data from OpenAlex.

    :param harvest_year: the year to harvest.
    :param headers: headers for OpenAlex.
    :param harvest_filename: filename to write harvest results to.
    :param df_filename: filename to write the DataFrame results to.
    :return: the DataFrame harvested, or None if nothing harvested.
    """
    print('Harvesting persons and research outputs from ' + HARVEST_SOURCE + '...')
    if OPENALEX_READ_HARVEST_FROM_FILE:
        harvest_data = rcg.read_json_from_file(filename=harvest_filename)
    else:
        url = OPENALEX_URL + '/' + OPENALEX_ENDPOINT + '?filter=institutions.ror:' + ORGANIZATION_ROR
        url += ',publication_year:' + harvest_year + '&select=' + OPENALEX_FIELDS
        harvest_data = rcg.harvest_json(url=url,
                                        headers=headers,
                                        max_recs_to_harvest=OPENALEX_MAX_RECS_TO_HARVEST,
                                        chunksize=OPENALEX_CHUNKSIZE,
                                        filename=harvest_filename)

    if (parse := parse_openalex(harvest=harvest_data, filename=df_filename)) is None:
        return None

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

    # The order of the columns in the DataFrame below is not random.
    # A good choice is to have in the first two columns:
    # a. the identifier that appears the most in the system we harvest.
    # b. the identifier(s) that is already present in Ricgraph from previous harvests,
    #    since new identifiers from this harvest will be  linked to an already existing
    #    person-root.
    # If you have 2 of type (b), use these as the first 2 columns.
    person_identifiers = parsed_content[['OPENALEX', 'ORCID', 'FULL_NAME']].copy(deep=True)
    rcg.create_parsed_persons_in_ricgraph(person_identifiers=person_identifiers,
                                          harvest_source=HARVEST_SOURCE)

    # Connect organizations to persons.
    organizations = parsed_content[['OPENALEX', 'ORGANIZATION_NAME']].copy(deep=True)
    rcg.create_parsed_entities_in_ricgraph(entities=organizations,
                                           harvest_source=HARVEST_SOURCE)

    if 'ROR' in parsed_content.columns:
        # Connect organization name to organization ROR.
        organizations = parsed_content[['ROR', 'ORGANIZATION_NAME']].copy(deep=True)
        rcg.create_parsed_rors_in_ricgraph(organizations=organizations,
                                           harvest_source=HARVEST_SOURCE)

    return


def parsed_resout_to_ricgraph(parsed_content: pandas.DataFrame) -> None:
    """Insert the parsed research outputs in Ricgraph.

    :param parsed_content: The records to insert in Ricgraph, if not present yet.
    :return: None.
    """
    resouts = parsed_content[['OPENALEX', 'DOI', 'TITLE', 'YEAR', 'TYPE']].copy(deep=True)
    rcg.create_parsed_dois_in_ricgraph(resouts=resouts, harvest_source=HARVEST_SOURCE)
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

org_name = 'organization_name_' + organization
org_ror = 'organization_ror_' + organization
ORGANIZATION_NAME = rcg.get_configfile_key(section='Organization', key=org_name)
ORGANIZATION_ROR = rcg.get_configfile_key(section='Organization', key=org_ror)
if ORGANIZATION_NAME == '' or ORGANIZATION_ROR == '':
    print('Ricgraph initialization: error, "' + org_name + '" or "' + org_ror + '"')
    print('  not existing or empty in Ricgraph ini file, exiting.')
    exit(1)

HARVEST_SOURCE = 'OpenAlex-' + organization

print('\nHarvesting ' + HARVEST_SOURCE + ', first year: ' + year_first + ', last year: ' + year_last + '.')

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
print(rcg.nodes_cache_key_id_type_size() + '\n')

for year_int in range(int(year_first), int(year_last) + 1):
    year = str(year_int)
    data_file_year = rcg.construct_filename(base_filename=OPENALEX_DATA_FILENAME,
                                            year=year, organization=organization)
    if OPENALEX_READ_DATA_FROM_FILE:
        error_message = 'There are no persons or research outputs from ' + HARVEST_SOURCE
        error_message += ' for year ' + year + ' to read from file ' + data_file_year + '.\n'
        print('Reading persons and research outputs from ' + HARVEST_SOURCE
              + ' for year ' + year + ' from file ' + data_file_year + '.')
        parse_persons_resout = rcg.read_dataframe_from_csv(filename=data_file_year,
                                                           datatype=str)
    else:
        error_message = 'There are no persons or research outputs from ' + HARVEST_SOURCE
        error_message += ' for year ' + year + ' to harvest.\n'
        print('Harvesting persons and research outputs from ' + HARVEST_SOURCE
              + ' for year ' + year + '.')
        harvest_file_year = rcg.construct_filename(base_filename=OPENALEX_HARVEST_FILENAME,
                                                   year=year, organization=organization)
        parse_persons_resout = harvest_and_parse_openalex(harvest_year=year,
                                                          headers=OPENALEX_HEADERS,
                                                          harvest_filename=harvest_file_year,
                                                          df_filename=data_file_year)

    if parse_persons_resout is None or parse_persons_resout.empty:
        print(error_message)
    else:
        parsed_persons_to_ricgraph(parsed_content=parse_persons_resout)
        parsed_resout_to_ricgraph(parsed_content=parse_persons_resout)

    rcg.graphdb_nr_accesses_print()
    print(rcg.nodes_cache_key_id_type_size() + '\n')

rcg.close_ricgraph()
