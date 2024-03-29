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
# With this code, you can enrich persons having an ORCID but no SCOPUS_AUTHOR_ID
# (using OpenAlex), or vice versa (using the Scopus API). Note that Scopus has a rate limit.
# You have to set some parameters in ricgraph.ini.
# Also, you can set a number of parameters in the code following the "import" statements below.
#
# Note:
# Enriching can be improved by saving the SCOPUS_AUTHOR_IDs or ORCIDs found in a file. These results
# can then be used when this program is called again. A missing personal ID should be first searched
# in that file, and if not found, at OpenAlex or Scopus. That will save a number of calls to
# OpenAlex and Scopus.
#
# Original version Rik D.T. Janssen, December 2022.
# Updated Rik D.T. Janssen, February 2023.
#
# ########################################################################


import os.path
import pyalex
import json
from urllib import parse
from urllib.error import HTTPError
import urllib.request
from ratelimit import limits, sleep_and_retry
import requests
import configparser
from pyalex import Authors
import ricgraph as rcg


# 17-12-2022: Rate limit for Scopus API, API Author Retrieval,
# is: weekly quota 5000, requests per second: 3
# See https://dev.elsevier.com/api_key_settings.html.
SCOPUS_NR_OF_API_CALLS_PER_SECOND = 1
SCOPUS_NR_OF_API_CALLS_IN_PERIOD = 1            # per second

# More info: https://dev.elsevier.com/documentation/AUTHORSearchAPI.wadl.
SCOPUS_HEADERS = {
    'Accept': 'application/json'
}


# The following code is inspired by ratelimit: https://github.com/tomasbasham/ratelimit.
@sleep_and_retry
@limits(calls=SCOPUS_NR_OF_API_CALLS_PER_SECOND, period=SCOPUS_NR_OF_API_CALLS_IN_PERIOD)
def scopus_call_url_ratelimit(url: str, headers: dict):
    """Get data from Scopus using the Scopus API, make sure not to exceed the rate limits.

    :param url: URL to harvest from.
    :param headers: headers for harvest.
    :return: the response.
    """
    request = urllib.request.Request(url=url, headers=headers)
    response = urllib.request.urlopen(request, timeout=5)
    if response.status != 200:
        raise Exception('scopus_call_url_ratelimit(): API response: {}'.format(response.status))
    return response


def scopus_read_jsondata(url: str, headers: dict) -> list:
    """Read json data from Scopus.

    :param url: URL to harvest from.
    :param headers: headers for harvest.
    :return: the response.
    """
    json_data = {}
    try:
        response = scopus_call_url_ratelimit(url=url, headers=headers)
        body = response.read().decode('utf-8')
        json_data = json.loads(body)
    except urllib.error.HTTPError:
        print('scopus_read_jsondata(): error during harvest, possibly a missing API-key or mixed up harvest URL?')
        exit(1)

    return json_data


def get_missing_personal_ids(we_have_id: str, we_want_id: str) -> dict:
    """Find a missing personal ID 'we_want_id', based on 'we_have_id'.

    :param we_have_id: personal ID we have.
    :param we_want_id: personal ID we want.
    :return: a dict with missing personal IDs.
    """
    personal_ids = {}
    if we_have_id != 'ORCID' and we_have_id != 'SCOPUS_AUTHOR_ID' \
       and we_want_id != 'ORCID' and we_want_id != 'SCOPUS_AUTHOR_ID':
        print('get_missing_person_ids(): not prepared yet for id ' + we_have_id
              + ' or ' + we_want_id + '.')
        return personal_ids

    nodes = rcg.read_all_nodes(name=we_have_id)
    if len(nodes) == 0:
        return personal_ids

    print('There are ' + str(len(nodes)) + ' ' + we_have_id + 's, trying to enrich with '
          + we_want_id + 's, processing node: 0  ', end='')
    count = 0

    for node in nodes:
        count += 1
        if count % 100 == 0:
            print(count, ' ', end='', flush=True)
        if count % 1000 == 0:
            print('\n', end='', flush=True)

        list_of_edges_from_node = rcg.get_edges(node)
        number_of_edges = len(list_of_edges_from_node)
        if number_of_edges != 1:
            # This personal ID node has been assigned to zero or more than
            # one node, that should not happen, skip.
            continue

        person_root_node = rcg.get_personroot_node(node)
        we_want_id_found = False
        for edge in rcg.get_edges(person_root_node):
            next_node = edge.end_node
            if next_node['name'] == we_want_id:
                # This 'we_have_id' node already has a 'we_want_id' node,
                # not necessary to do anything
                we_want_id_found = True
                break

        if we_want_id_found:
            continue

        personal_ids[node['value']] = ''

    print(count, '\n', end='', flush=True)
    print('Result: of the ' + str(len(nodes)) + ' ' + we_have_id + 's, '
          + str(len(personal_ids)) + ' have no ' + we_want_id + 's.\n')
    return personal_ids


def openalex_create_missing_ids(collected_ids: dict, we_have_id: str, we_want_id: str) -> None:
    """Use OpenAlex to find the missing personal IDs.
    For now, OpenAlex can only enrich records based on ORCIDs. This function is already
    prepared to enrich records based on SCOPUS_AUTHOR_ID.

    :param collected_ids: a dict with personal IDs we want to find.
    :param we_have_id: personal ID we have.
    :param we_want_id: personal ID we want.
    :return: None.
    """
    if we_have_id != 'ORCID' and we_have_id != 'SCOPUS_AUTHOR_ID' \
            and we_want_id != 'ORCID' and we_want_id != 'SCOPUS_AUTHOR_ID' \
            and len(collected_ids) == 0:
        print('\nopenalex_create_missing_ids(): Not prepared yet for ids ' + we_have_id
              + ' or ' + we_want_id + ', or len(collected_ids) is zero.\n')
        return

    if we_have_id == 'SCOPUS_AUTHOR_ID':
        print('\nopenalex_create_missing_ids(): Error, OpenAlex does not have an index on ' + we_have_id + ' yet.')
        print('For more information, see https://docs.openalex.org/about-the-data#canonical-external-ids.\n')
        return

    print('There are ' + str(len(collected_ids)) + ' ' + we_have_id + 's, not having a ' + we_want_id
          + '. Using OpenAlex to enrich these with ' + we_want_id + 's. Processing node: 0  ', end='')
    count = 0
    nodes_enriched = 0
    for person_id in collected_ids:
        count += 1
        if count % 20 == 0:
            print(count, ' ', end='', flush=True)
        if count % 300 == 0:
            print('\n', end='', flush=True)

        if we_have_id == 'ORCID':
            openalex_search_val = 'https://orcid.org/' + person_id
        elif we_have_id == 'SCOPUS_AUTHOR_ID':
            # For now, only this type of link, skip URLs like
            # http://www.scopus.com/authid/detail.url?authorId=7202676966.
            # This enrich doesn't work yet, so it has not been tested.
            openalex_search_val = 'http://www.scopus.com/inward/authorDetails.url?authorID=' \
                                    + person_id + '&partnerID=MN8TOARS'
        else:
            # Should not happen
            return

        error_catched = False
        openalex_result = {}
        try:
            openalex_result = Authors()[openalex_search_val]
        except requests.HTTPError:
            # OpenAlex throws this exception if the search value does not exist
            error_catched = True

        if error_catched:
            # Nothing found in OpenAlex
            continue

        if 'ids' in openalex_result:
            ids = openalex_result['ids']
            id_found = ''
            if we_want_id == 'ORCID':
                if 'orcid' in ids:
                    openalex_found_val = ids['orcid']
                    # Return value something like https://orcid.org/0000-0001-9510-0802
                    id_found = openalex_found_val.remove_prefix('https://orcid.org/')
                    nodes_enriched += 1
            elif we_want_id == 'SCOPUS_AUTHOR_ID':
                if 'scopus' in ids:
                    openalex_found_val = ids['scopus']
                    # Return value something like
                    # http://www.scopus.com/inward/authorDetails.url?authorID=7202676966&partnerID=MN8TOARS
                    # or http://www.scopus.com/authid/detail.url?authorId=7202676966.
                    # Get the correct parameter,
                    # from: https://stackoverflow.com/questions/5074803/retrieving-parameters-from-a-url.
                    if 'authorID' in openalex_found_val:
                        id_found = parse.parse_qs(parse.urlparse(openalex_found_val).query)['authorID'][0]
                        nodes_enriched += 1
                    elif 'authorId' in openalex_found_val:
                        id_found = parse.parse_qs(parse.urlparse(openalex_found_val).query)['authorId'][0]
                        nodes_enriched += 1
                    else:
                        continue
            else:
                # Should not happen
                return

            if id_found == '':
                continue

            history_line = 'OpenAlex enrich: using ' + we_have_id + ': ' + person_id + \
                           ', found ' + we_want_id + ': ' + id_found + '.'
            rcg.create_two_nodes_and_edge(name1=we_have_id, category1='person', value1=person_id,
                                          name2=we_want_id, category2='person', value2=id_found,
                                          comment2='OpenAlex enrich', history_event2=history_line)

    print(count, '\n', end='', flush=True)
    print('Result: using OpenAlex, of the ' + str(len(collected_ids)) + ' ' + we_have_id + 's, '
          + str(nodes_enriched) + ' have been enriched with ' + we_want_id + 's.\n')
    return


def scopus_create_missing_ids(collected_ids: dict, we_have_id: str, we_want_id: str) -> None:
    """Use Scopus to find the missing personal IDs.

    :param collected_ids: a dict with personal IDs we want to find.
    :param we_have_id: personal ID we have.
    :param we_want_id: personal ID we want.
    :return: None.
    """
    if we_have_id != 'SCOPUS_AUTHOR_ID' \
            and we_want_id != 'ORCID' \
            and len(collected_ids) == 0:
        print('\nscopus_create_missing_ids(): Not prepared yet for ids ' + we_have_id
              + ' or ' + we_want_id + ', or len(collected_ids) is zero.\n')
        return

    print('There are ' + str(len(collected_ids)) + ' ' + we_have_id + 's, not having a ' + we_want_id
          + '. Using Scopus to enrich these with ' + we_want_id + 's. Processing node: 0  ', end='')
    count = 0
    nodes_enriched = 0
    for person_id in collected_ids:
        count += 1
        if count % 20 == 0:
            print(count, ' ', end='', flush=True)
        if count % 300 == 0:
            print('\n', end='', flush=True)

        scopus_search_val = 'https://api.elsevier.com/content/search/author?query=au-id(' \
                            + person_id + ')&field=orcid&suppressNavLinks=true'
        try:
            scopus_result_json = scopus_read_jsondata(url=scopus_search_val, headers=SCOPUS_HEADERS)
        except urllib.error.HTTPError as err:
            # There is a rate limit, then we get a 'HTTPError: HTTP Error 429: Too Many Requests'.
            # However, this should have been caught in scopus_read_jsondata().
            print('\n\nscopus_create_missing_ids(): Error, rate limit exceeded.')
            print('This should not happen since it should have been caught.')
            print('Message: ' + str(err))
            return

        scopus_result = scopus_result_json['search-results']['entry'][0]
        if 'orcid' in scopus_result:
            id_found = scopus_result['orcid']
            nodes_enriched += 1
        else:
            # Nothing found
            continue

        history_line = 'Scopus enrich: using ' + we_have_id + ': ' + person_id + \
                       ', found ' + we_want_id + ': ' + id_found + '.'
        rcg.create_two_nodes_and_edge(name1=we_have_id, category1='person', value1=person_id,
                                      name2=we_want_id, category2='person', value2=id_found,
                                      comment2='Scopus enrich', history_event2=history_line)

    print(count, '\n', end='', flush=True)
    print('Result: using Scopus, of the ' + str(len(collected_ids)) + ' ' + we_have_id + 's, '
          + str(nodes_enriched) + ' have been enriched with ' + we_want_id + 's.\n')
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
    SCOPUS_API_KEY = config['Scopus_harvesting']['scopus_api_key']
    SCOPUS_INSTITUTIONAL_TOKEN = config['Scopus_harvesting']['scopus_institutional_token']
    SCOPUS_HEADERS['X-ELS-APIKey'] = SCOPUS_API_KEY
    SCOPUS_HEADERS['X-ELS-Insttoken'] = SCOPUS_INSTITUTIONAL_TOKEN
except KeyError:
    print('Error, Scopus API keys not found in Ricgraph ini file, exiting.')
    exit(1)

try:
    # The OpenAlex 'polite pool' has much faster and more consistent response times.
    # See https://docs.openalex.org/api#the-polite-pool.
    # They have rate limits, but they are high: https://docs.openalex.org/api#rate-limits.
    pyalex.config.email = config['OpenAlex_harvesting']['openalex_polite_pool_email']
except KeyError:
    print('Error, OpenAlex email address not found in Ricgraph ini file, exiting.')
    exit(1)

if pyalex.config.email == '':
    print('Error, insert an email address in the Ricgraph ini file for OpenAlex, exiting.')
    exit(1)

print('\nPreparing graph...')
graph = rcg.open_ricgraph()

orcids_with_missing_scopus_ids = get_missing_personal_ids(we_have_id='ORCID', we_want_id='SCOPUS_AUTHOR_ID')
if len(orcids_with_missing_scopus_ids) > 0:
    openalex_create_missing_ids(collected_ids=orcids_with_missing_scopus_ids,
                                we_have_id='ORCID', we_want_id='SCOPUS_AUTHOR_ID')

# Scopus has a rate limit, so it is more efficient to first use OpenAlex, then Scopus.
scopusids_with_missing_orcids = get_missing_personal_ids(we_have_id='SCOPUS_AUTHOR_ID', we_want_id='ORCID')
if len(scopusids_with_missing_orcids) > 0:
    scopus_create_missing_ids(collected_ids=scopusids_with_missing_orcids,
                              we_have_id='SCOPUS_AUTHOR_ID', we_want_id='ORCID')

# OpenAlex cannot use SCOPUS_AUTHOR_ID as index as of December 2022.
# It is here for future extension.
# scopusids_with_missing_orcids = get_missing_personal_ids(we_have_id='SCOPUS_AUTHOR_ID', we_want_id='ORCID')
# if len(scopusids_with_missing_orcids) > 0:
#     openalex_create_missing_ids(collected_ids=scopusids_with_missing_orcids,
#                                 we_have_id='SCOPUS_AUTHOR_ID', we_want_id='ORCID')

rcg.close_ricgraph()
