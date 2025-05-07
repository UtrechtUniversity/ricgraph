# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
#
# Copyright (c) 2023 - 2025 Rik D.T. Janssen
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
# Ricgraph Explorer REST API functions.
# Ricgraph uses the OpenAPI format: https://www.openapis.org.
# We use Connexion: https://connexion.readthedocs.io/en/latest.
#
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, January 2023.
# Extended Rik D.T. Janssen, February, September 2023 to May 2025.
#
# ########################################################################


from typing import Tuple
from ricgraph import (create_http_response, HTTP_RESPONSE_OK,
                      HTTP_RESPONSE_NOTHING_FOUND, HTTP_RESPONSE_INVALID_SEARCH,
                      read_all_nodes, get_all_neighbor_nodes,
                      get_personroot_node, get_all_personroot_nodes,
                      convert_nodes_to_list_of_dict)
from ricgraph_explorer_constants import MAX_ITEMS, SEARCH_STRING_MIN_LENGTH
from ricgraph_explorer_graphdb import (find_person_share_resouts_cypher,
                                       find_person_organization_collaborations_cypher,
                                       find_organization_additional_info_cypher,
                                       find_enrich_candidates_one_person)


def api_search_person(value: str = '',
                      max_nr_items: str = str(MAX_ITEMS)) -> Tuple[dict, int]:
    """REST API Search for a person.

    :param value: value of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    response, status = api_search_general(value=value,
                                          name_restriction='FULL_NAME',
                                          max_nr_items=max_nr_items)
    return response, status


def api_person_all_information(key: str = '',
                               max_nr_items: str = str(MAX_ITEMS)):
    """REST API Show all information related to this person.

    :param key: key of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    # This implements view_mode = 'view_unspecified_table_everything'.
    # graph = current_app.config.get('graph')
    from ricgraph_explorer import get_all_globals_from_app_context

    get_all_globals_from_app_context()
    if key == '':
        response, status = create_http_response(message='You have not specified a search key',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    nodes = read_all_nodes(key=key)
    if len(nodes) == 0:
        response, status = create_http_response(message='Nothing found',
                                                http_status=HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    personroot_node = get_personroot_node(node=nodes[0])
    if personroot_node is None:
        response, status = create_http_response(message='No person-root node found',
                                                http_status=HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    # Now we have the person-root, and we can reuse api_all_information_general().
    response, status = api_all_information_general(key=personroot_node['_key'],
                                                   max_nr_items=max_nr_items)
    return response, status


def api_person_share_research_results(key: str = '',
                                      max_nr_items: str = str(MAX_ITEMS)):
    """REST API Find persons that share any share research result types with this person.

    :param key: key of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    # This implements view_mode = 'view_regular_table_person_share_resouts'.
    # See function find_person_share_resouts().
    from ricgraph_explorer import get_all_globals_from_app_context

    get_all_globals_from_app_context()
    if key == '':
        response, status = create_http_response(message='You have not specified a search key',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if not max_nr_items.isnumeric():
        max_nr_items = str(MAX_ITEMS)
    nodes = read_all_nodes(key=key)
    if len(nodes) == 0:
        response, status = create_http_response(message='Nothing found',
                                                http_status=HTTP_RESPONSE_NOTHING_FOUND)
        return response, status

    connected_persons = \
        find_person_share_resouts_cypher(parent_node=nodes[0],
                                         category_dontwant_list=['person', 'competence', 'organization'],
                                         max_nr_items=max_nr_items)
    if len(connected_persons) == 0:
        message = 'Could not find persons that share any share research result types '
        message += 'with this person'
        response, status = create_http_response(message=message,
                                                http_status=HTTP_RESPONSE_OK)
        return response, status

    result_list = convert_nodes_to_list_of_dict(connected_persons,
                                                max_nr_items=max_nr_items)
    response, status = create_http_response(result_list=result_list,
                                            message=str(len(result_list)) + ' items found',
                                            http_status=HTTP_RESPONSE_OK)
    return response, status


def api_person_collaborating_organizations(key: str = '',
                                           max_nr_items: str = str(MAX_ITEMS)):
    """REST API Find persons that share any share research result types with this person.

    :param key: key of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    # This implements view_mode = 'view_regular_table_person_organization_collaborations'.
    # See function find_person_organization_collaborations().
    from ricgraph_explorer import get_all_globals_from_app_context

    get_all_globals_from_app_context()
    if key == '':
        response, status = create_http_response(message='You have not specified a search key',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if not max_nr_items.isnumeric():
        max_nr_items = str(MAX_ITEMS)
    nodes = read_all_nodes(key=key)
    if len(nodes) == 0:
        response, status = create_http_response(message='Nothing found',
                                                http_status=HTTP_RESPONSE_NOTHING_FOUND)
        return response, status

    personroot_node_organizations, collaborating_organizations = \
        find_person_organization_collaborations_cypher(parent_node=nodes[0],
                                                       max_nr_items=max_nr_items)
    message = ''
    if len(personroot_node_organizations) == 0:
        message += 'This person does not work at any organization. '
    else:
        message += 'This person works at ' + str(len(personroot_node_organizations))
        message += ' organizations, these are in "person_works_at". '
    if len(collaborating_organizations) == 0:
        message += 'This person has no collaborations with other organizations.'
    else:
        message += 'This person collaborates with ' + str(len(collaborating_organizations))
        message += ' organizations, these are in "person_collaborates_with".'

    person_worksat_list = convert_nodes_to_list_of_dict(personroot_node_organizations,
                                                        max_nr_items=max_nr_items)
    person_collaborates_list = convert_nodes_to_list_of_dict(collaborating_organizations,
                                                             max_nr_items=max_nr_items)
    meta = {'message': message}
    result = {'meta': meta,
              'person_works_at': person_worksat_list,
              'person_collaborates_with': person_collaborates_list}
    result_list = [result]
    response, status = create_http_response(result_list=result_list,
                                            message=str(len(result_list)) + ' items found',
                                            http_status=HTTP_RESPONSE_OK)
    return response, status


def api_person_enrich(key: str = '',
                      name_want: list = None,
                      category_want: list = None,
                      source_system: str = '',
                      max_nr_items: str = str(MAX_ITEMS)):
    """REST API Find persons that share any share research result types with this person.

    :param key: key of the node(s) to find.
    :param name_want: a list containing several node names, indicating
      that we want all neighbor nodes of the person-root node of the organization
      specified by 'key', where the property 'name' equals
      one of the names in the list 'name_want'
      (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty (empty string), return all nodes.
    :param category_want: similar to 'name_want', but now for the property 'category'.
    :param source_system: the source system to find enrichments for.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    # This implements view_mode = 'view_regular_table_person_enrich_source_system'.
    # See function find_enrich_candidates().
    import ricgraph_explorer as rcg_exp

    rcg_exp.get_all_globals_from_app_context()
    if name_want is None:
        name_want = []
    if category_want is None:
        category_want = []

    if key == '':
        response, status = create_http_response(message='You have not specified a search key',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if result := list(set(name_want) - set(rcg_exp.name_all)):
        response, status = create_http_response(message='You have not specified a valid name_want: '
                                                        + str(result) + '".',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if result := list(set(category_want) - set(rcg_exp.category_all)):
        response, status = create_http_response(message='You have not specified a valid category_want: '
                                                        + str(result) + '".',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if source_system == '':
        response, status = create_http_response(message='You have not specified a source system',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if source_system not in rcg_exp.source_all:
        response, status = create_http_response(message='You have not specified a valid source system "'
                                                        + source_system + '".',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if not max_nr_items.isnumeric():
        max_nr_items = str(MAX_ITEMS)
    nodes = read_all_nodes(key=key)
    if len(nodes) == 0:
        response, status = create_http_response(message='Nothing found',
                                                http_status=HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    personroot_node = get_personroot_node(node=nodes[0])
    if personroot_node is None:
        response, status = create_http_response(message='No person-root node found',
                                                http_status=HTTP_RESPONSE_NOTHING_FOUND)
        return response, status

    person_nodes, nodes_not_in_source_system = \
        find_enrich_candidates_one_person(personroot=personroot_node,
                                          name_want=name_want,
                                          category_want=category_want,
                                          source_system=source_system)
    if len(nodes_not_in_source_system) == 0:
        message = 'Ricgraph could not find any information in other source systems '
        message += 'to enrich source system "' + source_system + '"'
        response, status = create_http_response(message=message,
                                                http_status=HTTP_RESPONSE_NOTHING_FOUND)
        return response, status

    message = ''
    if len(person_nodes) == 0:
        message += 'There are enrich candidates '
        message += 'to enrich source system "' + source_system
        message += '", but there are no "person" nodes to identify this item in "'
        message += source_system + '". '
    else:
        message += 'There are ' + str(len(person_nodes))
        message += ' items in "person_identifying_nodes" you can use to find this item '
        message += 'in source system "' + source_system + '". '

    # Note: len(nodes_not_in_source_system) > 0.
    message += 'There are ' + str(len(nodes_not_in_source_system))
    message += ' items in "person_enrich_nodes" you can use to enrich source system "'
    message += source_system + '" by using information harvested from other source systems.'

    person_identifying_nodes_list = convert_nodes_to_list_of_dict(person_nodes,
                                                                  max_nr_items=max_nr_items)
    person_enrich_nodes_list = convert_nodes_to_list_of_dict(nodes_not_in_source_system,
                                                             max_nr_items=max_nr_items)
    meta = {'message': message}
    result = {'meta': meta,
              'person_identifying_nodes': person_identifying_nodes_list,
              'person_enrich_nodes': person_enrich_nodes_list}
    result_list = [result]
    response, status = create_http_response(result_list=result_list,
                                            message=str(len(result_list)) + ' items found',
                                            http_status=HTTP_RESPONSE_OK)
    return response, status


def api_search_organization(value: str = '',
                            max_nr_items: str = str(MAX_ITEMS)) -> Tuple[dict, int]:
    """REST API Search for a (sub-)organization.

    :param value: value of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    response, status = api_search_general(value=value,
                                          category_restriction='organization',
                                          max_nr_items=max_nr_items)
    return response, status


def api_organization_all_information(key: str = '',
                                     max_nr_items: str = str(MAX_ITEMS)):
    """REST API Show all information related to this organization.

    :param key: key of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    # This implements view_mode = 'view_unspecified_table_organizations'.
    response, status = api_all_information_general(key=key,
                                                   max_nr_items=max_nr_items)
    return response, status


def api_organization_information_persons_results(key: str = '',
                                                 name_want: list = None,
                                                 category_want: list = None,
                                                 max_nr_items: str = str(MAX_ITEMS)):
    """REST API Find any information from persons or their results in this organization.

    :param key: key of the node(s) to find.
    :param name_want: a list containing several node names, indicating
      that we want all neighbor nodes of the person-root node of the organization
      specified by 'key', where the property 'name' equals
      one of the names in the list 'name_want'
      (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty (empty string), return all nodes.
    :param category_want: similar to 'name_want', but now for the property 'category'.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    # This implements view_mode = 'view_regular_table_organization_addinfo'.
    # See function find_organization_additional_info().
    response, status = api_organization_enrich(key=key,
                                               name_want=name_want,
                                               category_want=category_want,
                                               max_nr_items=max_nr_items)
    return response, status


def api_organization_enrich(key: str = '',
                            name_want: list = None,
                            category_want: list = None,
                            source_system: str = '',
                            max_nr_items: str = str(MAX_ITEMS)):
    """REST API Find persons that share any share research result types with this organization.

    :param key: key of the node(s) to find.
    :param name_want: a list containing several node names, indicating
      that we want all neighbor nodes of the person-root node of the organization
      specified by 'key', where the property 'name' equals
      one of the names in the list 'name_want'
      (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty (empty string), return all nodes.
    :param category_want: similar to 'name_want', but now for the property 'category'.
    :param source_system: the source system to find enrichments for.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    # This implements view_mode = 'view_regular_table_organization_addinfo'.
    # See function find_organization_additional_info().
    import ricgraph_explorer as rcg_exp

    rcg_exp.get_all_globals_from_app_context()
    if name_want is None:
        name_want = []
    if category_want is None:
        category_want = []

    if key == '':
        response, status = create_http_response(message='You have not specified a search key',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if result := list(set(name_want) - set(rcg_exp.name_all)):
        response, status = create_http_response(message='You have not specified a valid name_want: '
                                                        + str(result) + '".',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if result := list(set(category_want) - set(rcg_exp.category_all)):
        response, status = create_http_response(message='You have not specified a valid category_want: '
                                                        + str(result) + '".',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if source_system == '':
        response, status = create_http_response(message='You have not specified a source system',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if source_system not in rcg_exp.source_all:
        response, status = create_http_response(message='You have not specified a valid source system "'
                                                        + source_system + '".',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if not max_nr_items.isnumeric():
        max_nr_items = str(MAX_ITEMS)
    nodes = read_all_nodes(key=key)
    if len(nodes) == 0:
        response, status = create_http_response(message='Nothing found',
                                                http_status=HTTP_RESPONSE_NOTHING_FOUND)
        return response, status

    cypher_result = find_organization_additional_info_cypher(parent_node=nodes[0],
                                                             name_list=name_want,
                                                             category_list=category_want,
                                                             source_system=source_system,
                                                             max_nr_items=max_nr_items)
    if len(cypher_result) == 0:
        message = 'Could not find any information from persons or '
        message += 'their results in this organization'
        response, status = create_http_response(message=message,
                                                http_status=HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    relevant_result = []
    for result in cypher_result:
        node = result['second_neighbor']
        relevant_result.append(node)

    result_list = convert_nodes_to_list_of_dict(relevant_result,
                                                max_nr_items=max_nr_items)
    response, status = create_http_response(result_list=result_list,
                                            message=str(len(result_list)) + ' items found',
                                            http_status=HTTP_RESPONSE_OK)
    return response, status


def api_search_competence(value: str = '',
                          max_nr_items: str = str(MAX_ITEMS)) -> Tuple[dict, int]:
    """REST API Search for a skill, expertise area or research area.

    :param value: value of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    response, status = api_search_general(value=value,
                                          category_restriction='competence',
                                          max_nr_items=max_nr_items)
    return response, status


def api_competence_all_information(key: str = '',
                                   max_nr_items: str = str(MAX_ITEMS)):
    """REST API Show all information related to this competence.

    :param key: key of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    response, status = api_all_information_general(key=key,
                                                   max_nr_items=max_nr_items)
    return response, status


def api_broad_search(value: str = '',
                     max_nr_items: str = str(MAX_ITEMS)) -> Tuple[dict, int]:
    """REST API Search for anything (broad search).

    :param value: value of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    response, status = api_search_general(value=value,
                                          max_nr_items=max_nr_items)
    return response, status


def api_advanced_search(name: str = '', category: str = '', value: str = '',
                        max_nr_items: str = str(MAX_ITEMS)) -> Tuple[dict, int]:
    """REST API Advanced search.

    :param name: name of the node(s) to find.
    :param category: category of the node(s) to find.
    :param value: value of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    from ricgraph_explorer import get_all_globals_from_app_context

    get_all_globals_from_app_context()
    if name == '' and category == '' and value == '':
        response, status = create_http_response(message='You have not specified any search string',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if not max_nr_items.isnumeric():
        max_nr_items = str(MAX_ITEMS)
    nodes = read_all_nodes(name=name,
                           category=category,
                           value=value,
                           value_is_exact_match=True,
                           max_nr_nodes=int(max_nr_items))
    if len(nodes) == 0:
        response, status = create_http_response(message='Nothing found',
                                                http_status=HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    result_list = convert_nodes_to_list_of_dict(nodes,
                                                max_nr_items=max_nr_items)
    response, status = create_http_response(result_list=result_list,
                                            message=str(len(result_list)) + ' items found',
                                            http_status=HTTP_RESPONSE_OK)
    return response, status


def api_search_general(value: str = '',
                       name_restriction: str = '',
                       category_restriction: str = '',
                       max_nr_items: str = str(MAX_ITEMS)) -> Tuple[dict, int]:
    """REST API General broad search function.

    :param value: value of the node(s) to find.
    :param name_restriction: Restrict the broad search on a certain name.
    :param category_restriction: Restrict the broad search on a certain category.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    from ricgraph_explorer import get_all_globals_from_app_context

    get_all_globals_from_app_context()
    if value == '':
        response, status = create_http_response(message='You have not specified a search string',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if len(value) < SEARCH_STRING_MIN_LENGTH:
        message = 'The search string should be at least ' + str(SEARCH_STRING_MIN_LENGTH) + ' characters'
        response, status = create_http_response(message=message,
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if not max_nr_items.isnumeric():
        max_nr_items = str(MAX_ITEMS)
    nodes = read_all_nodes(name=name_restriction,
                           category=category_restriction,
                           value=value,
                           value_is_exact_match=False,
                           max_nr_nodes=int(max_nr_items))
    if name_restriction == 'FULL_NAME' \
       and len(nodes) < int(max_nr_items):
        # Also return FULL_NAME_ASCII nodes, if applicable.
        nodes_ascii = read_all_nodes(name='FULL_NAME_ASCII',
                                     category=category_restriction,
                                     value=value,
                                     value_is_exact_match=False,
                                     max_nr_nodes=int(max_nr_items) - len(nodes))
        nodes.extend(nodes_ascii)

    if len(nodes) == 0:
        response, status = create_http_response(message='Nothing found',
                                                http_status=HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    result_list = convert_nodes_to_list_of_dict(nodes,
                                                max_nr_items=max_nr_items)
    response, status = create_http_response(result_list=result_list,
                                            message=str(len(result_list)) + ' items found',
                                            http_status=HTTP_RESPONSE_OK)
    return response, status


def api_all_information_general(key: str = '',
                                max_nr_items: str = str(MAX_ITEMS)):
    """REST API General all information about a node function.

    :param key: key of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    from ricgraph_explorer import get_all_globals_from_app_context

    get_all_globals_from_app_context()
    if key == '':
        response, status = create_http_response(message='You have not specified a search key',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if not max_nr_items.isnumeric():
        max_nr_items = str(MAX_ITEMS)
    nodes = read_all_nodes(key=key)
    if len(nodes) == 0:
        response, status = create_http_response(message='Nothing found',
                                                http_status=HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    neighbor_nodes = get_all_neighbor_nodes(node=nodes[0],
                                            max_nr_neighbor_nodes=int(max_nr_items))
    if len(neighbor_nodes) == 0:
        response, status = create_http_response(message='Nothing found',
                                                http_status=HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    result_list = convert_nodes_to_list_of_dict(neighbor_nodes,
                                                max_nr_items=max_nr_items)
    response, status = create_http_response(result_list=result_list,
                                            message=str(len(result_list)) + ' items found',
                                            http_status=HTTP_RESPONSE_OK)
    return response, status


def api_get_all_personroot_nodes(key: str = '',
                                 max_nr_items: str = str(MAX_ITEMS)):
    """REST API Get all the person-root nodes of a node.

    :param key: key of the node(s) to find.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    from ricgraph_explorer import get_all_globals_from_app_context

    get_all_globals_from_app_context()
    if key == '':
        response, status = create_http_response(message='You have not specified a search key',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    nodes = read_all_nodes(key=key)
    if len(nodes) == 0:
        response, status = create_http_response(message='Nothing found',
                                                http_status=HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    personroot_nodes = get_all_personroot_nodes(node=nodes[0])
    if len(personroot_nodes) == 0:
        response, status = create_http_response(message='Nothing found',
                                                http_status=HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    result_list = convert_nodes_to_list_of_dict(personroot_nodes,
                                                max_nr_items=max_nr_items)
    response, status = create_http_response(result_list=result_list,
                                            message=str(len(result_list)) + ' items found',
                                            http_status=HTTP_RESPONSE_OK)
    return response, status


def api_get_all_neighbor_nodes(key: str = '',
                               name_want: list = None,
                               name_dontwant: list = None,
                               category_want: list = None,
                               category_dontwant: list = None,
                               max_nr_items: str = str(MAX_ITEMS)):
    """REST API Get all the neighbor nodes of a node.

    :param key: key of the node(s) to find.
    :param name_want: a list containing several node names, indicating
      that we want all neighbor nodes where the property 'name' equals
      one of the names in the list 'name_want'
      (e.g. ['ORCID', 'ISNI', 'FULL_NAME']).
      If empty (empty string), return all nodes.
    :param name_dontwant: similar, but for property 'name' and nodes we don't want.
      If empty (empty string), all nodes are 'wanted'.
    :param category_want: similar to 'name_want', but now for the property 'category'.
    :param category_dontwant: similar, but for property 'category' and nodes we don't want.
    :param max_nr_items: The maximum number of items to return.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    import ricgraph_explorer as rcg_exp

    rcg_exp.get_all_globals_from_app_context()
    if name_want is None:
        name_want = []
    if name_dontwant is None:
        name_dontwant = []
    if category_want is None:
        category_want = []
    if category_dontwant is None:
        category_dontwant = []

    if key == '':
        response, status = create_http_response(message='You have not specified a search key',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if result := list(set(name_want) - set(rcg_exp.name_all)):
        response, status = create_http_response(message='You have not specified a valid name_want: '
                                                        + str(result) + '".',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if result := list(set(name_dontwant) - set(rcg_exp.name_all)):
        response, status = create_http_response(message='You have not specified a valid name_dontwant: '
                                                        + str(result) + '".',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if result := list(set(category_want) - set(rcg_exp.category_all)):
        response, status = create_http_response(message='You have not specified a valid category_want: '
                                                        + str(result) + '".',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    if result := list(set(category_dontwant) - set(rcg_exp.category_all)):
        response, status = create_http_response(message='You have not specified a valid category_dontwant: '
                                                        + str(result) + '".',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status
    nodes = read_all_nodes(key=key)
    if len(nodes) == 0:
        response, status = create_http_response(message='Nothing found',
                                                http_status=HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    neighbor_nodes = get_all_neighbor_nodes(node=nodes[0],
                                            name_want=name_want,
                                            name_dontwant=name_dontwant,
                                            category_want=category_want,
                                            category_dontwant=category_dontwant,
                                            max_nr_neighbor_nodes=int(max_nr_items))
    if len(neighbor_nodes) == 0:
        response, status = create_http_response(message='Nothing found',
                                                http_status=HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    result_list = convert_nodes_to_list_of_dict(neighbor_nodes,
                                                max_nr_items=max_nr_items)
    response, status = create_http_response(result_list=result_list,
                                            message=str(len(result_list)) + ' items found',
                                            http_status=HTTP_RESPONSE_OK)
    return response, status


def api_get_ricgraph_list(ricgraph_list_name: str = '') -> Tuple[dict, int]:
    """REST API Get values of a specified Ricgraph global list.

    :param ricgraph_list_name: name of the Ricgraph global list.
    :return: An HTTP response (as dict, to be translated to json)
      and an HTTP response code.
    """
    import ricgraph_explorer as rcg_exp

    rcg_exp.get_all_globals_from_app_context()
    if ricgraph_list_name == '':
        response, status = create_http_response(message='You have not specified a name of a Ricgraph list',
                                                http_status=HTTP_RESPONSE_INVALID_SEARCH)
        return response, status

    result_list = []
    if ricgraph_list_name == 'name_all':
        result_list = rcg_exp.name_all.copy()
    if ricgraph_list_name == 'name_personal_all':
        result_list = rcg_exp.name_personal_all.copy()
    if ricgraph_list_name == 'category_all':
        result_list = rcg_exp.category_all.copy()
    if ricgraph_list_name == 'source_all':
        result_list = rcg_exp.source_all.copy()
    if ricgraph_list_name == 'resout_types_all':
        result_list = rcg_exp.resout_types_all.copy()
    if ricgraph_list_name == 'personal_types_all':
        result_list = rcg_exp.personal_types_all.copy()
    if ricgraph_list_name == 'remainder_types_all':
        result_list = rcg_exp.remainder_types_all.copy()

    if len(result_list) == 0:
        response, status = create_http_response(message='You have not specified a valid name of a Ricgraph list',
                                                http_status=HTTP_RESPONSE_NOTHING_FOUND)
        return response, status
    response, status = create_http_response(result_list=result_list,
                                            message=str(len(result_list)) + ' items found',
                                            http_status=HTTP_RESPONSE_OK)
    return response, status
