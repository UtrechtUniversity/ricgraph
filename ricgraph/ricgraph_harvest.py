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


from sys import stdout
from time import sleep
from numpy import nan
from pandas import DataFrame
from requests import get, post, Response
from .ricgraph_constants import (A_LARGE_NUMBER,
                                 PERSON_CATEGORY_PERSON,
                                 COMPETENCE_CATEGORY_COMPETENCE,
                                 ORGANIZATION_CATEGORY_ORGANISATION,
                                 HARVEST_JSON_SOURCE_OPENALEX,
                                 HARVEST_JSON_SOURCE_PURE,
                                 HARVEST_JSON_SOURCE_RSD)
from .ricgraph_file import write_read_json_file
from .ricgraph_utils import (timestamp, datetimestamp, timestamp_posix,
                             print_records_per_minute, print_progress)
from .ricgraph import (unify_personal_identifiers, create_nodepairs_and_edges_df,
                       update_nodes_df)


# The timeout for getting JSON from a source, in seconds.
HARVEST_JSON_TIMEOUT = 60
# If the JSON harvest fails (for any reason), try again
# this number of times.
HARVEST_JSON_MAX_RETRIES = 3
# If the JSON harvest fails (for any reason), wait
# this number of seconds before trying again.
HARVEST_JSON_WAIT_AFTER_FAILED_ATTEMPT = 120


def _harvest_json_get_print_nr_records(source: str,
                                       chunk_json_data: dict,
                                       max_recs_to_harvest: int,
                                       chunksize: int) -> None:
    """Helper function for harvest_json(), to get and print the
    total number of records to harvest.

    :param source: The source to harvest from.
    :param chunk_json_data: A chunk with harvested JSON data.
    :param max_recs_to_harvest: maximum records to harvest.
    :param chunksize: chunk size to use (i.e. the number of records harvested in one call to 'url').
    :return: None.
    """
    total_records = 0
    if source == HARVEST_JSON_SOURCE_OPENALEX:
        if 'meta' in chunk_json_data:
            if 'count' in chunk_json_data['meta']:
                total_records = chunk_json_data['meta']['count']
    elif source == HARVEST_JSON_SOURCE_PURE:
        if 'count' in chunk_json_data:
            total_records = chunk_json_data['count']
    else:
        print('harvest_json_get_print_nr_records(): Should not happen.')
        exit(1)

    if total_records == 0:
        print('harvest_json_get_print_nr_records(): Warning: malformed json, "count" is missing.')
    if max_recs_to_harvest == A_LARGE_NUMBER:
        print('There are ' + str(total_records)
              + ' records, harvesting in chunks of ' + str(chunksize)
              + ' items.')
    else:
        print('There are ' + str(total_records)
              + ' records, harvesting in chunks of ' + str(chunksize)
              + ', at most ' + str(max_recs_to_harvest) + ' items.')
    return


def _harvest_json_error(response: Response | None) -> None:
    """Prints an error message if an error during harvest occurs.

    :param response: Response object.
    :return: None.
    """
    if response is None:
        return
    print('harvest_json(): Error during harvest, possibly '
          + 'a missing API-key or mixed up params or headers?')
    print('Status code: ' + str(response.status_code))
    print('Url: ' + response.url)
    print('Error: ' + response.text)
    return


def harvest_json(source: str,
                 url: str,
                 headers: dict = None,
                 body: dict = None,
                 max_recs_to_harvest: int = 0, chunksize: int = 0,
                 filename: str = '') -> list:
    """Harvest JSON data from a file.
    OpenAlex (GET) uses cursor based navigation, because OpenAlex
    breaks the connection after a maximum nr of records harvested
    while using page based navigation.
    Pure (POST) uses offset (page) based navigation. It uses POST,
    since that is the only way to specify a time period for the harvest.
    RSD (GET) can be harvested in one go (no paging or cursor necessary).
    In case filename != '', write it to a file and read it back.

    :param source: The source to harvest from. We need this,
        because not every source uses the same harvest URL-keywords.
    :param url: URL to harvest.
    :param headers: headers required.
    :param body: body required.
    :param max_recs_to_harvest: maximum records to harvest.
    :param chunksize: chunk size to use (i.e. the number of records harvested in one call to 'url').
    :param filename: If filename != '', write it to a file and read it back.
    :return: list of records in JSON format, or empty list if nothing found.
    """
    if headers is None:
        headers = {}
    if body is None:
        body = {}

    params = {}
    if source == HARVEST_JSON_SOURCE_OPENALEX:
        params['cursor'] = '*'
        params['per_page'] = str(chunksize)
    elif source == HARVEST_JSON_SOURCE_PURE:
        params['size'] = chunksize
    elif source == HARVEST_JSON_SOURCE_RSD:
        # RSD does not use this.
        pass
    else:
        print('harvest_json(): Error: source "'
              + source + '" not implemented yet.')
        exit(1)

    print('Harvesting json data from source '
          + source + ' using url ' + url + '.')
    print('Getting data at ' + datetimestamp() + '.')
    all_records = A_LARGE_NUMBER
    if max_recs_to_harvest == 0:
        max_recs_to_harvest = all_records
    if chunksize == 0:
        chunksize = 1

    # Using a Session (from requests) makes it faster.
    # However, Session() does not always work, sometimes
    # Pure times out and then breaks the connection.
    # session = Session()

    json_data = []
    records_harvested = 0
    first_time = True
    start_ts = timestamp_posix()
    while records_harvested <= max_recs_to_harvest:
        attempt = 0
        while True:
            attempt += 1
            response = None
            try:
                if source == HARVEST_JSON_SOURCE_PURE:
                    response = post(url=url,
                                    params=params,
                                    headers=headers,
                                    json=body,
                                    timeout=HARVEST_JSON_TIMEOUT)
                else:
                    response = get(url=url,
                                   params=params,
                                   headers=headers,
                                   timeout=HARVEST_JSON_TIMEOUT)
                response.raise_for_status()
                break
            except Exception as exc:
                print('\nharvest_json(): Failed JSON harvest attempt number '
                      + str(attempt) + '.')
                _harvest_json_error(response=response)
                print('harvest_json(): This may add more information:')
                print('    Exception return value: ' + str(exc) + '.')
                print('    Params: ' + str(params) + '.')
                print('    Headers: ' + str(headers) + '.')
                if attempt <= HARVEST_JSON_MAX_RETRIES:
                    print('harvest_json(): Trying JSON harvest again after '
                          + str(HARVEST_JSON_WAIT_AFTER_FAILED_ATTEMPT) + ' seconds.')
                    stdout.flush()
                    sleep(HARVEST_JSON_WAIT_AFTER_FAILED_ATTEMPT)
                    continue
                print('harvest_json(): Failed all JSON harvest attempts, exiting.')
                exit(1)

        if response is None:
            # To silence a PyCharm warning.
            continue
        chunk_json_data = response.json()
        if first_time:
            first_time = False
            if source == HARVEST_JSON_SOURCE_RSD:
                # For RSD, we have already gotten all data,
                # (it can be gotten in one go), save & continue.
                return write_read_json_file(json_data=chunk_json_data,
                                            filename=filename)
            _harvest_json_get_print_nr_records(source=source,
                                               chunk_json_data=chunk_json_data,
                                               max_recs_to_harvest=max_recs_to_harvest,
                                               chunksize=chunksize)
            print('Harvesting record:')
            stdout.flush()

        if source == HARVEST_JSON_SOURCE_OPENALEX:
            if 'results' not in chunk_json_data:
                print('harvest_json(): Error: malformed json, "results" is missing.')
                return []
            if len(chunk_json_data['results']) == 0:
                break
            json_items = chunk_json_data['results']
        elif source == HARVEST_JSON_SOURCE_PURE:
            if 'items' not in chunk_json_data:
                print('harvest_json(): Error: malformed json, "items" is missing.')
                return []
            if len(chunk_json_data['items']) == 0:
                break
            json_items = chunk_json_data['items']
        else:
            # Not possible, we have tested for it above.
            exit(1)

        records_harvested += len(json_items)
        json_data += json_items

        # For the next round, if any.
        if source == HARVEST_JSON_SOURCE_OPENALEX:
            next_cursor = chunk_json_data.get('meta', {}).get('next_cursor', None)
            if next_cursor is None:
                # We are ready.
                break
            params['cursor'] = next_cursor
        elif source == HARVEST_JSON_SOURCE_PURE:
            if max_recs_to_harvest - records_harvested <= chunksize:
                # We have to harvest the last few (< chunksize).
                params['size'] = max_recs_to_harvest - records_harvested
            params['offset'] = records_harvested

        # Note that we cannot use print_progress() because of
        # the '+= chunksize'.
        print(records_harvested, ' ', end='', flush=True)
        if (records_harvested % (chunksize * 10)) == 0:
            print('(' + timestamp() + ')\n', end='', flush=True)

    print_progress(count=records_harvested, now=True)
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
        A person (in the 1st column) is connected to something else
        (an entity) determined by all other columns.
        The order of the columns and their names in this DataFrame
        are important.
        - The 1st column should be: a person identifier (ORCID,
          OPENALEX_ID_PERS, etc.). The 'name' property in the
          person node will get the name of this column.
          The 'value' property will be the value in this columns' row.
        The other columns are expected to be:
        - 'NAME': a research result name identifier (DOI, etc.).
          This will become the 'name' property in the entity.
        - 'CATEGORY': The category, will become 'category' property.
        - 'VALUE': the value of a research result identifier
          (DOI value, etc.). This will become the 'value' property.
        - Optionally, there may be columns 'TITLE', 'YEAR', 'URL_MAIN'
          and 'URL_OTHER'.
    :param harvest_source: The source system we harvest from.
    :param what: Text to show to the user and in '_history'
    :return: None.
    """
    if entities is None or entities.empty:
        # Nothing to do.
        return
    for column in ['NAME', 'CATEGORY', 'VALUE']:
        if column not in entities.columns:
            print('create_parsed_entities_in_ricgraph_general(): Error, missing column "'
                  + column + '".')
            exit(1)

    print('Inserting ' + what + ' from ' + harvest_source
          + ' in Ricgraph at ' + timestamp() + '...')
    history_event = 'Source: Harvest "' + harvest_source + '" '
    history_event += what + ' at ' + datetimestamp() + '.'

    personal_id_name = entities.columns[0]

    # Ensure that all '' values in the important columns are NaN,
    # so that those rows can be easily removed with dropna().
    entities[[personal_id_name, 'VALUE']] = entities[[personal_id_name,
                                                      'VALUE']].replace(to_replace='', value=nan)

    # Drop a row from selected columns if any of its value is NaN.
    entities.dropna(subset=[personal_id_name, 'VALUE'], how='any', inplace=True)
    entities.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    entities.rename(columns={'NAME': 'name1',
                             'CATEGORY': 'category1',
                             'VALUE': 'value1',
                             personal_id_name: 'value2'}, inplace=True)
    new_entities_columns = {'source_event1': harvest_source,
                            'history_event1': history_event,
                            'name2': personal_id_name,
                            'category2': PERSON_CATEGORY_PERSON,
                            'source_event2': harvest_source,
                            'history_event2': history_event}
    entities = entities.assign(**new_entities_columns)

    cols = ['name1', 'category1', 'value1']
    for column in ['TITLE', 'YEAR', 'LICENSE', 'ACCESS', 'URL_MAIN', 'URL_OTHER']:
        if column in entities.columns:
            if column == 'TITLE':
                entities.rename(columns={'TITLE': 'comment1'}, inplace=True)
                cols.append('comment1')
            else:
                ricgraph_column = column.lower() + '1'
                entities.rename(columns={column: ricgraph_column}, inplace=True)
                cols.append(ricgraph_column)
    cols.extend(['source_event1', 'history_event1',
                 'name2', 'category2', 'value2', 'source_event2', 'history_event2'])
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
                                   harvest_source: str,
                                   what: str = 'research results') -> None:
    """Insert the parsed research results in Ricgraph.

    :param resouts: The records to insert in Ricgraph, if not present yet.
        The order of the columns in this DataFrame is important.
        We expect:
        - In the 1st column: a person identifier (ORCID, OPENALEX_ID_PERS, etc.).
          The 'name' property in the person node will get the name
          of this column.
          The 'value' property will be the value in this columns' row.
        - The other columns should be named 'DOI', 'TITLE', 'YEAR', and 'CATEGORY'.
        - Optionally, there may be a column 'URL_MAIN', referring to
          the main URL.
        - Optionally, there may be a column 'URL_OTHER', referring to
          the URL in the source system.
          If URL_MAIN is not present, note that the URL to the
          DOI will be added automatically.
    :param harvest_source: The source system we harvest from.
    :param what: Text to show to the user and in '_history'
    :return: None.
    """
    if 'DOI' not in resouts.columns:
        print('create_parsed_dois_in_ricgraph(): Error, missing column "DOI".')
        exit(1)
    resouts.rename(columns={'DOI': 'VALUE'}, inplace=True)
    resouts.insert(loc=1, column='NAME', value='DOI')
    create_parsed_entities_in_ricgraph_general(entities=resouts,
                                               harvest_source=harvest_source,
                                               what=what)
    return


def create_parsed_entities_in_ricgraph(entities: DataFrame,
                                       harvest_source: str,
                                       what: str = 'entities') -> None:
    """Insert the parsed research results in Ricgraph.

    :param entities: The records to insert in Ricgraph, if not present yet.
        The order of the columns in this DataFrame is important.
        We expect:
        - In the 1st column: a person identifier (ORCID, OPENALEX_ID_PERS, etc.).
          The 'name' property in the person node will get the name
          of this column.
          The 'value' property will be the value in this columns' row.
        - The 2nd column should be an entity to be linked to the person
          identifier in the 1st column.
        - Optionally there may be a 3rd column that contains the URLs
          to the entity in the 2nd column.
    :param harvest_source: The source system we harvest from.
    :param what: Text to show to the user and in '_history'
    :return: None.
    """
    entity_name = entities.columns[1]
    entities.rename(columns={entity_name: 'VALUE'}, inplace=True)
    entities.insert(loc=1, column='NAME', value=entity_name)

    if entity_name in ['ORGANIZATION_NAME']:
        entities['CATEGORY'] = ORGANIZATION_CATEGORY_ORGANISATION
    elif entity_name in ['EXPERTISE_AREA', 'RESEARCH_AREA', 'SKILL']:
        entities['CATEGORY'] = COMPETENCE_CATEGORY_COMPETENCE
        if len(entities.columns) != 5:
            # Note that we have entered this function with a DataFrame
            # containing 3 columns, but we have inserted a 4th column at
            # entities.insert() above and added a 5th at the previous line.
            print('create_parsed_entities_in_ricgraph(): Error, missing third column.')
            exit(1)
        url_name = entities.columns[3]
        entities.rename(columns={url_name: 'URL_MAIN'}, inplace=True)
    elif entity_name in ['UUSTAFF_PAGEID', 'FULL_NAME']:
        entities['CATEGORY'] = PERSON_CATEGORY_PERSON
    else:
        print('create_parsed_entities_in_ricgraph(): Error, unknown column "'
              + entity_name + '".')
        exit(1)

    create_parsed_entities_in_ricgraph_general(entities=entities,
                                               harvest_source=harvest_source,
                                               what=what)
    return


def update_urls_in_ricgraph(entities: DataFrame,
                            harvest_source: str,
                            what: str) -> None:
    """Update the URLs of the parsed entities in Ricgraph.

    :param entities: The records to update URLs in Ricgraph.
        The order of the columns in this DataFrame is important.
        We expect:
        - In the 1st column: an identifier (ORCID, OPENALEX_ID_PERS, etc.).
          The 'name' property in the node will get the name
          of this column.
          The 'value' property will be the value in this columns' row.
        - The other column should be named 'URL_MAIN'.
    :param harvest_source: The source system we harvest from.
    :param what: Text to show to the user and in '_history'
    :return: None.
    """
    if 'URL_MAIN' not in entities.columns:
        print('update_url_in_ricgraph(): Error, missing column "URL_MAIN".')
        exit(1)
    print('Updating ' + what + ' from ' + harvest_source
          + ' in Ricgraph at ' + timestamp() + '...')
    history_event = 'Source: Harvest "' + harvest_source + '" '
    history_event += what + ' at ' + datetimestamp() + '.'

    entity_name = entities.columns[0]
    if entity_name in ['PURE_ID_PERS', 'UUSTAFF_PAGEID', 'PHOTO_ID']:
        entities['category'] = PERSON_CATEGORY_PERSON
    elif entity_name in ['ORGANIZATION_NAME']:
        entities['category'] = ORGANIZATION_CATEGORY_ORGANISATION
    else:
        print('update_urls_in_ricgraph(): Error, unknown column "'
              + entity_name + '".')
        exit(1)

    # Ensure that all '' values are NaN, so that those rows can be easily removed with dropna()
    entities.replace(to_replace='', value=nan, inplace=True)
    # Drop a row if any of its values is NaN.
    entities.dropna(axis=0, how='any', inplace=True)
    entities.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    entities.rename(columns={entity_name: 'value',
                             'URL_MAIN': 'url_main'}, inplace=True)
    new_entities_columns = {'name': entity_name,
                            'source_event': harvest_source,
                            'history_event': history_event}
    entities = entities.assign(**new_entities_columns)
    entities = entities[['name', 'category', 'value', 'url_main',
                         'source_event', 'history_event']]

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
    """Insert the parsed research results in Ricgraph.

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
                                'category1': ORGANIZATION_CATEGORY_ORGANISATION,
                                'name2': 'ROR',
                                'category2': ORGANIZATION_CATEGORY_ORGANISATION,
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


