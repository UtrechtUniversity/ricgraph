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
# Ricgraph harvest functions.
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, December 2022.
# Updated Rik D.T. Janssen, February, March, September to December 2023.
# Updated Rik D.T. Janssen, February to June, September to December  2024.
# Updated Rik D.T. Janssen, January to June 2025.
# Updated Rik D.T. Janssen, February 2026.
#
# ########################################################################


from numpy import nan
from pandas import DataFrame
from requests import get, post
from requests import codes
from .ricgraph import (unify_personal_identifiers, create_nodepairs_and_edges_df,
                       update_nodes_df)
from .ricgraph_file import write_read_json_file
from .ricgraph_utils import (timestamp, datetimestamp,
                             timestamp_posix, print_records_per_minute)
from .ricgraph_constants import A_LARGE_NUMBER


# #####
# Note:
# This function was written using the JSON harvested by the following python files:
# - GET: harvest_openalex_to_ricgraph.py.
# - POST: harvest_pure_to_ricgraph.py.
#
# Possibly for other harvests some changes should be made. Please also test the result
# with the above-mentioned files, and add the filename of the new harvest script.
# #####
def harvest_json(url: str,
                 headers: dict = None, body: dict = None,
                 max_recs_to_harvest: int = 0, chunksize: int = 0,
                 filename: str = '') -> list:
    """Harvest JSON data from a file.
    In case filename != '', write it to a file and read it back.

    :param url: URL to harvest.
    :param headers: headers required.
        If headers is None, we can get all data in one go, we do not need
        the 'while' loop below. This is the case for
        e.g. Research Software Directory.
    :param body: the body of a POST request, or None/{} for a GET request.
    :param max_recs_to_harvest: maximum records to harvest.
    :param chunksize: chunk size to use (i.e. the number of records harvested in one call to 'url').
    :param filename: If filename != '', write it to a file and read it back.
    :return: list of records in JSON format, or empty list if nothing found.
    """
    if body is None:
        body = {}
    if headers is None:
        headers = {}

    print('Harvesting json data from ' + url + '.')
    print('Getting data at ' + datetimestamp() + '...')

    all_records = A_LARGE_NUMBER
    if max_recs_to_harvest == 0:
        max_recs_to_harvest = all_records
    if chunksize == 0:
        chunksize = 1
    if len(body) == 0:
        # GET http request
        request_type = 'get'
        if len(headers) > 0:
            url += '&per_page=' + str(chunksize)
    else:
        # POST http request
        request_type = 'post'
        body['size'] = chunksize

    # Do a first harvest to determine the number of records to harvest.
    if request_type == 'get':
        response = get(url=url, headers=headers)
    else:
        response = post(url=url, headers=headers, json=body)

    if response.status_code != codes.ok:
        print('harvest_json(): error during harvest, possibly '
              + 'a missing API-key or mixed up POST body?')
        print('Status code: ' + str(response.status_code))
        print('Url: ' + response.url)
        print('Error: ' + response.text)
        exit(1)

    chunk_json_data = response.json()
    if len(headers) == 0:
        return write_read_json_file(json_data=chunk_json_data,
                                    filename=filename)

    total_records = 0
    if request_type == 'get':
        if 'meta' in chunk_json_data:
            if 'count' in chunk_json_data['meta']:
                total_records = chunk_json_data['meta']['count']
    else:
        if 'count' in chunk_json_data:
            total_records = chunk_json_data['count']

    if total_records == 0:
        print('harvest_json(): Warning: malformed json, "count" is missing.')

    if max_recs_to_harvest == all_records:
        print('There are ' + str(total_records)
              + ' records, harvesting in chunks of ' + str(chunksize)
              + ' items.')
    else:
        print('There are ' + str(total_records)
              + ' records, harvesting in chunks of ' + str(chunksize)
              + ', at most ' + str(max_recs_to_harvest) + ' items.')

    print('Harvesting record: ', end='', flush=True)

    json_data = []
    records_harvested = 0
    start_ts = timestamp_posix()
    page_nr = 1
    # And now start the real harvesting.
    while records_harvested <= max_recs_to_harvest:
        if request_type == 'get':
            url_page = url + '&page=' + str(page_nr)
            response = get(url=url_page, headers=headers)
        else:
            if max_recs_to_harvest - records_harvested <= chunksize:
                # We have to harvest the last few (< chunksize).
                body['size'] = max_recs_to_harvest - records_harvested
            body['offset'] = records_harvested
            response = post(url=url, headers=headers, json=body)

        if response.status_code != codes.ok:
            print('harvest_json(): error during harvest, possibly '
                  + 'a missing API-key or mixed up POST body?')
            print('Status code: ' + str(response.status_code))
            print('Url: ' + response.url)
            print('Error: ' + response.text)
            exit(1)

        chunk_json_data = response.json()
        if request_type == 'get':
            if 'results' not in chunk_json_data:
                print('harvest_json(): Error: malformed json, "results" is missing.')
                return []
            if len(chunk_json_data['results']) == 0:
                break
            json_items = chunk_json_data['results']
        else:
            if 'items' not in chunk_json_data:
                print('harvest_json(): Error: malformed json, "items" is missing.')
                return []
            if len(chunk_json_data['items']) == 0:
                break
            json_items = chunk_json_data['items']

        json_data += json_items
        print(records_harvested, ' ', end='', flush=True)
        if page_nr % 10 == 0:
            if page_nr != 0:
                print('(' + timestamp() + ')\n', end='', flush=True)
        records_harvested += chunksize
        page_nr += 1

    print(' Done at ' + timestamp() + '.')
    end_ts = timestamp_posix()
    print_records_per_minute(start_ts=start_ts, end_ts=end_ts,
                             nr_records=records_harvested,
                             what='Harvested')
    print('')
    return write_read_json_file(json_data=json_data,
                                filename=filename)


# ######################################################
# Functions to get harvested results in Ricgraph.
# The functions below all have a 'person' node as
# first element in the DataFrame.
# ######################################################

def create_parsed_persons_in_ricgraph(person_identifiers: DataFrame,
                                      harvest_source: str) -> None:
    """Insert the parsed persons in Ricgraph.

    :param person_identifiers: The records to insert in Ricgraph, if not present yet.
        The order of the columns in this DataFrame is not random.
        A good choice is to have in the first two columns:
        a. the identifier that appears the most in the system we harvest.
        b. the identifier(s) that is already present in Ricgraph from previous harvests,
           since new identifiers from this harvest will be  linked to an already existing
           person-root.
    :param harvest_source: The source system we harvest from.
    :return: None.
    """
    if person_identifiers is None or person_identifiers.empty:
        # Nothing to do.
        return
    print('Inserting persons from ' + harvest_source + ' in Ricgraph at ' + timestamp() + '...')
    history_event = 'Source: Harvest "' + harvest_source + '" persons at ' + datetimestamp() + '.'

    # dropna(how='all'): drop row if all row values contain NaN
    person_identifiers.dropna(axis=0, how='all', inplace=True)
    person_identifiers.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    if person_identifiers.empty:
        print('There are no persons to insert in Ricgraph.')
        return

    print('The following persons will be inserted in Ricgraph:')
    print(person_identifiers)
    unify_personal_identifiers(personal_identifiers=person_identifiers,
                               source_event=harvest_source,
                               history_event=history_event)
    print('Done inserting persons at ' + timestamp() + '.')
    return


def create_parsed_entities_in_ricgraph_general(entities: DataFrame,
                                               harvest_source: str,
                                               what: str) -> None:
    """Insert the parsed entities in Ricgraph.

    :param entities: The records to insert in Ricgraph, if not present yet.
        The order of the columns in this DataFrame is important.
        We expect:
        - In the 1st column: a person identifier (ORCID, OPENALEX, etc.).
          The 'name' property in the person node will get the name
          of this column.
          The 'value' property will be the value in this columns' row.
        - In the 2nd column: a research output name identifier (DOI, etc.).
          The name of this column must be RESOUT_ID.
          The 'name' property in the research output will get the value
          in this columns' row.
        - In the 3rd column: the value of a research output identifier
          (DOI value, etc.).
          The name of this column must be RESOUT_VALUE.
          The 'value' property in the research output will get the value
          in this columns' row.
        - The other column should be named 'TYPE'.
        - Optionally, there may be columns 'TITLE', 'YEAR', 'URL_MAIN'
          and 'URL_OTHER'.
    :param harvest_source: The source system we harvest from.
    :param what: Text to show to the user and in '_source'
    :return: None.
    """
    if entities is None or entities.empty:
        # Nothing to do.
        return
    if 'RESOUT_ID' not in entities.columns:
        print('create_parsed_entities_in_ricgraph_general(): Error, missing column "RESOUT_ID".')
        exit(1)
    if 'RESOUT_VALUE' not in entities.columns:
        print('create_parsed_entities_in_ricgraph_general(): Error, missing column "RESOUT_VALUE".')
        exit(1)
    if 'TYPE' not in entities.columns:
        print('create_parsed_entities_in_ricgraph_general(): Error, missing column "TYPE".')
        exit(1)

    print('Inserting ' + what + ' from ' + harvest_source
          + ' in Ricgraph at ' + timestamp() + '...')
    history_event = 'Source: Harvest "' + harvest_source + '" '
    history_event += what + ' at ' + datetimestamp() + '.'

    personal_id_name = entities.columns[0]

    # Ensure that all '' values in the important columns are NaN,
    # so that those rows can be easily removed with dropna().
    entities[[personal_id_name, 'RESOUT_VALUE']] = entities[[personal_id_name,
                                                           'RESOUT_VALUE']].replace(to_replace='', value=nan)

    # Drop a row from selected columns if any of its value is NaN.
    entities.dropna(subset=[personal_id_name, 'RESOUT_VALUE'], how='any', inplace=True)
    entities.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    entities.rename(columns={'RESOUT_ID': 'name1',
                            'TYPE': 'category1',
                            'RESOUT_VALUE': 'value1',
                             personal_id_name: 'value2'}, inplace=True)
    new_entities_columns = {'source_event1': harvest_source,
                            'history_event1': history_event,
                            'name2': personal_id_name,
                            'category2': 'person'}
    entities = entities.assign(**new_entities_columns)

    cols = ['name1', 'category1', 'value1']
    if 'TITLE' in entities.columns:
        entities.rename(columns={'TITLE': 'comment1'}, inplace=True)
        cols.append('comment1')
    if 'YEAR' in entities.columns:
        entities.rename(columns={'YEAR': 'year1'}, inplace=True)
        cols.append('year1')
    if 'URL_MAIN' in entities.columns:
        entities.rename(columns={'URL_MAIN': 'url_main1'}, inplace=True)
        cols.append('url_main1')
    if 'URL_OTHER' in entities.columns:
        entities.rename(columns={'URL_OTHER': 'url_other1'}, inplace=True)
        cols.append('url_other1')
    cols.extend(['source_event1', 'history_event1', 'name2', 'category2', 'value2'])
    entities = entities[cols]

    if entities.empty:
        print('There are no ' + what + ' to insert in Ricgraph.')
        return

    print('The following ' + what + ' will be inserted in Ricgraph:')
    print(entities)
    create_nodepairs_and_edges_df(left_and_right_nodepairs=entities)
    print('\nDone inserting ' + what + ' at ' + timestamp() + '.\n')
    return


def create_parsed_dois_in_ricgraph(resouts: DataFrame,
                                   harvest_source: str) -> None:
    """Insert the parsed research outputs in Ricgraph.

    :param resouts: The records to insert in Ricgraph, if not present yet.
        The order of the columns in this DataFrame is important.
        We expect:
        - In the 1st column: a person identifier (ORCID, OPENALEX, etc.).
          The 'name' property in the person node will get the name
          of this column.
          The 'value' property will be the value in this columns' row.
        - The other columns should be named 'DOI', 'TITLE', 'YEAR', and 'TYPE'.
        - Optionally, there may be a column 'URL_MAIN', referring to
          the main URL.
        - Optionally, there may be a column 'URL_OTHER', referring to
          the URL in the source system.
          If URL_MAIN is not present, note that the URL to the
          DOI will be added automatically.
    :param harvest_source: The source system we harvest from.
    :return: None.
    """
    if 'DOI' not in resouts.columns:
        print('create_parsed_dois_in_ricgraph(): Error, missing column "DOI".')
        exit(1)
    resouts.rename(columns={'DOI': 'RESOUT_VALUE'}, inplace=True)
    resouts.insert(loc=1, column='RESOUT_ID', value='DOI')
    create_parsed_entities_in_ricgraph_general(entities=resouts,
                                               harvest_source=harvest_source,
                                               what='research outputs')
    return


def create_parsed_entities_in_ricgraph(entities: DataFrame,
                                       harvest_source: str) -> None:
    """Insert the parsed research outputs in Ricgraph.

    :param entities: The records to insert in Ricgraph, if not present yet.
        The order of the columns in this DataFrame is important.
        We expect:
        - In the 1st column: a person identifier (ORCID, OPENALEX, etc.).
          The 'name' property in the person node will get the name
          of this column.
          The 'value' property will be the value in this columns' row.
        - The 2nd column should be an entity to be linked to the person
          identifier in the 1st column.
        - Optionally there may be a 3rd column that contains the URLs
          to the entity in the 2nd column.
    :param harvest_source: The source system we harvest from.
    :param harvest_source: The source system we harvest from.
    :return: None.
    """
    entity_name = entities.columns[1]
    entities.rename(columns={entity_name: 'RESOUT_VALUE'}, inplace=True)
    entities.insert(loc=1, column='RESOUT_ID', value=entity_name)

    if entity_name in ['ORGANIZATION_NAME']:
        entities['TYPE'] = 'organization'
    elif entity_name in ['EXPERTISE_AREA', 'RESEARCH_AREA', 'SKILL']:
        entities['TYPE'] = 'competence'
        if len(entities.columns) != 5:
            # Note that we have entered this function with a DataFrame
            # containing 3 columns, but we have inserted a 4th column at
            # entities.insert() above and added a 5th at the previous line.
            print('create_parsed_entities_in_ricgraph(): Error, missing third column.')
            exit(1)
        url_name = entities.columns[3]
        entities.rename(columns={url_name: 'URL_MAIN'}, inplace=True)
    elif entity_name in ['UUSTAFF_PAGE_ID', 'FULL_NAME']:
        entities['TYPE'] = 'person'
    else:
        print('create_parsed_entities_in_ricgraph(): Error, unknown column "'
              + entity_name + '".')
        exit(1)

    create_parsed_entities_in_ricgraph_general(entities=entities,
                                               harvest_source=harvest_source,
                                               what='organizations')
    return


def update_urls_in_ricgraph(entities: DataFrame,
                            harvest_source: str,
                            what: str) -> None:
    """Update the URLs of the parsed entities in Ricgraph.

    :param entities: The records to insert in Ricgraph, if not present yet.
        The order of the columns in this DataFrame is important.
        We expect:
        - In the 1st column: a person identifier (ORCID, OPENALEX, etc.).
          The 'name' property in the person node will get the name
          of this column.
          The 'value' property will be the value in this columns' row.
        - The other column should be named 'URL_MAIN'.
    :param harvest_source: The source system we harvest from.
    :param what: Text to show to the user and in '_source'
    :return: None.
    """
    if 'URL_MAIN' not in entities.columns:
        print('update_url_in_ricgraph(): Error, missing column "URL_MAIN".')
        exit(1)
    print('Updating ' + what + ' from ' + harvest_source
          + ' in Ricgraph at ' + timestamp() + '...')

    personal_id_name = entities.columns[0]

    # Ensure that all '' values are NaN, so that those rows can be easily removed with dropna()
    entities.replace(to_replace='', value=nan, inplace=True)
    # Drop a row if any of its values is NaN.
    entities.dropna(axis=0, how='any', inplace=True)
    entities.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    entities.rename(columns={personal_id_name: 'value',
                             'URL_MAIN': 'url_main'}, inplace=True)
    new_entities_columns = {'name': personal_id_name,
                            'category': 'person'}
    entities = entities.assign(**new_entities_columns)
    entities = entities[['name', 'category', 'value', 'url_main']]

    print('The following ' + what + ' will be updated in Ricgraph:')
    print(entities)
    update_nodes_df(nodes=entities)
    print('\nDone updating ' + what + ' at ' + timestamp() + '.\n')
    return


# ######################################################
# Functions to get harvested results in Ricgraph.
# The function below has two organizations in
# the DataFrame (and subsequently is different from the
# ones above).
# ######################################################

def create_parsed_rors_in_ricgraph(organizations: DataFrame,
                                   harvest_source: str) -> None:
    """Insert the parsed research outputs in Ricgraph.

    :param organizations: The records to insert in Ricgraph, if not present yet.
        We expect two columns: ROR' and 'ORGANIZATION_NAME'.
        The order does not matter.
    :param harvest_source: The source system we harvest from.
    :return: None.
    """
    if 'ROR' not in organizations.columns:
        print('create_parsed_rors_in_ricgraph(): Error, missing column "ROR".')
        exit(1)
    if 'ORGANIZATION_NAME' not in organizations.columns:
        print('create_parsed_rors_in_ricgraph(): Error, missing column "ORGANIZATION_NAME".')
        exit(1)

    print('Inserting organization RORs from ' + harvest_source + ' in Ricgraph at ' + timestamp() + '...')
    history_event = 'Source: Harvest "' + harvest_source + '" organization RORs at ' + datetimestamp() + '.'

    # Ensure that all '' values are NaN, so that those rows can be easily removed with dropna()
    organizations.replace(to_replace='', value=nan, inplace=True)
    # Drop a row if any of its values is NaN.
    organizations.dropna(axis=0, how='any', inplace=True)
    organizations.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    organizations.rename(columns={'ORGANIZATION_NAME': 'value1',
                                  'ROR': 'value2'}, inplace=True)
    new_organization_columns = {'name1': 'ORGANIZATION_NAME',
                                'category1': 'organization',
                                'name2': 'ROR',
                                'category2': 'organization',
                                'source_event2': harvest_source,
                                'history_event2': history_event}
    organizations = organizations.assign(**new_organization_columns)
    organizations = organizations[['name1', 'category1', 'value1',
                                   'name2', 'category2', 'value2',
                                   'source_event2', 'history_event2']]

    print('The following organization RORs will be inserted in Ricgraph:')
    print(organizations)
    create_nodepairs_and_edges_df(left_and_right_nodepairs=organizations)
    print('\nDone inserting organization RORs at ' + timestamp() + '.\n')
    return


