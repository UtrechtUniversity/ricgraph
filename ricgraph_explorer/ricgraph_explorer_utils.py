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
# Ricgraph Explorer general functions.
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, January 2023.
# Extended Rik D.T. Janssen, February, September 2023 to May 2025.
# Extended Rik D.T. Janssen, October, November 2025, March, May 2026.
#
# ########################################################################


from pandas import DataFrame
from flask import request
from markupsafe import escape
from ricgraph import (extract_organization_abbreviation,
                      QueryParams, PageParams)
from ricgraph_explorer_constants import (RICGRAPH_CACHEINFO,
                                         RICGRAPH_HARVESTINFO,
                                         RICGRAPH_NODEINFO,
                                         RICGRAPH_SYSTEMINFO,
                                         OVERLAP_MODE_SOURCE_ALL,
                                         MAX_ITEMS_TO_RETURN, MAX_ROWS_IN_TABLE)
from ricgraph_explorer_init import (get_ricgraph_explorer_global,
                                    collect_ricgraph_cacheinfo)


# ##############################################################################
# Various global functions.
# ##############################################################################
def get_global_list(ricgraph_info: str, item: str) -> list:
    """Safely retrieve an entry from a Ricgraph info structure.
    A list return value is expected.

    :param ricgraph_info: The Ricgraph info structure.
    :param item: The element in that structure.
    :return: the value of the list, or [] if it does not exist.
    """
    if ricgraph_info == RICGRAPH_CACHEINFO:
        # First update the information about the cache.
        collect_ricgraph_cacheinfo()
    info = get_ricgraph_explorer_global(name=ricgraph_info)
    if info is None:
        return []
    value = info.get(item, [])
    return value


def get_global_str(ricgraph_info: str, item: str) -> str:
    """Safely retrieve an entry from a Ricgraph info structure.
    A str return value is expected.

    :param ricgraph_info: The Ricgraph info structure.
    :param item: The element in that structure.
    :return: the value of the str, or '' if it does not exist.
    """
    if ricgraph_info == RICGRAPH_CACHEINFO:
        # First update the information about the cache.
        collect_ricgraph_cacheinfo()
    info = get_ricgraph_explorer_global(name=ricgraph_info)
    if info is None:
        return ''
    value = info.get(item, '')
    return value


def get_global_dataframe(ricgraph_info: str, item: str) -> DataFrame | None:
    """Safely retrieve an entry from a Ricgraph info structure.
    A DataFrame return value is expected.

    :param ricgraph_info: The Ricgraph info structure.
    :param item: The element in that structure.
    :return: the value of the DataFrame, or None if it does not exist.
    """
    if ricgraph_info == RICGRAPH_CACHEINFO:
        # First update the information about the cache.
        collect_ricgraph_cacheinfo()
    info = get_ricgraph_explorer_global(name=ricgraph_info)
    if info is None:
        return None
    value = info.get(item, '')
    return DataFrame(value)


# ##############################################################################
# URL related functions.
# ##############################################################################
def get_url_parameter_value(parameter: str,
                            allowed_values: list = None,
                            default_value: str = '',
                            use_escape: bool = True) -> str:
    """Get a URL parameter and its value.


    :param parameter: name of the URL parameter.
    :param allowed_values: allowed values of the URL parameter, if any.
    :param default_value: the default value, if any.
    :param use_escape: whether to call escape() or not for the URL parameter. We should
        do this for safety, however, we cannot always do this, because then we
        cannot search correctly in Ricgraph.
        For example, if we would use escape() for a URL parameter that contains an '&',
        such as in 'Department: Research & Data Management Services',
        that '&' will be translated to the HTML character '&amp;', which then
        will not be found in Ricgraph.
    :return: the value of the URL parameter.
    """
    if allowed_values is None:
        allowed_values = []

    if use_escape:
        value = str(escape(request.args.get(parameter, default='')))
    else:
        value = str(request.args.get(parameter, default=''))

    if value == '' and default_value != '':
        value = str(default_value)

    if len(allowed_values) > 0:
        # If 'default_value' == '', then 'value' will be '', which is what we intend.
        if value not in allowed_values:
            value = str(default_value)

    return value


def get_url_parameter_list(parameter: str,
                           allowed_values: list = None,
                           default_value: str = '',
                           use_escape: bool = True) -> list:
    """Get a URL parameter list and its values.

    :param parameter: name of the URL parameter.
    :param allowed_values: allowed values of the URL parameter, if any.
    :param default_value: the default value, if any.
    :param use_escape: whether to call escape() or not for the values of the URL
        parameter. We should do this for safety, however, we cannot always do
        this, because for some cases we cannot search correctly in Ricgraph.
        For example, if we would use escape() for a URL parameter that contains an '&',
        such as in 'Department: Research & Data Management Services',
        that '&' will be translated to the HTML character '&amp;', which then
        will not be found in Ricgraph.
    :return: the list of values of the URL parameter.
    """
    if allowed_values is None:
        allowed_values = []

    raw_value_list = request.args.getlist(parameter)
    if use_escape:
        value_list = [str(escape(item)) for item in raw_value_list]
    else:
        value_list = raw_value_list.copy()

    if len(allowed_values) > 0:
        value_list = list(set(value_list) & set(allowed_values))

    if len(value_list) == 0:
        if default_value == '':
            value_list = []
        else:
            value_list = [default_value]
    return value_list


def get_url_query_params() -> QueryParams:
    """Construct a dict that contains all possible parameters
    for a Cypher query from the URL. If the URL does not
    contain a certain parameter, insert its default value,
    so that we can always assume that every key in the dict
    exists.
    If you add fields, add them to
    ricgraph/ricgraph_utils.py/create_empty_query_params() too.

    :return: The dict with all URL parameters related to a query.
    """
    max_nr_items = get_url_parameter_value(parameter='max_nr_items',
                                           default_value=str(MAX_ITEMS_TO_RETURN))
    if not max_nr_items.isnumeric():
        # This also catches negative numbers, they contain a '-' and are not numeric.
        # See https://www.w3schools.com/python/ref_string_isnumeric.asp.
        max_nr_items = str(MAX_ITEMS_TO_RETURN)

    name_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                  item='name_active')
    category_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                      item='category_active')
    license_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                    item='license_active')
    access_active = get_global_list(ricgraph_info=RICGRAPH_NODEINFO,
                                    item='access_active')
    source_active = get_global_list(ricgraph_info=RICGRAPH_HARVESTINFO,
                                    item='source_active')

    # The rationale behind the following is as follows:
    # 1. Only allow 'active' values for a property of type list.
    # 2. Then, if the list passed in the URL param has the same length
    #    as the list of active values, the two list must be the same.
    # 3. If (2) is the case, then, for Cypher queries, it is not
    #    necessary to filter on that property using a WHERE, since
    #    any value for that property in the graph database is
    #    already taken into account. Change the list to [], so
    #    it will not be added to the Cypher query (so the query
    #    is faster).
    name_list = get_url_parameter_list(parameter='name_list',
                                       allowed_values=name_active)
    if len(name_active) == len(name_list):
        name_list = []
    category_list = get_url_parameter_list(parameter='category_list',
                                           allowed_values=category_active)
    if len(name_active) == len(category_list):
        category_list = []
    licentie = get_url_parameter_list(parameter='license',
                                      allowed_values=license_active)
    if len(license_active) == len(licentie):
        licentie = []
    access = get_url_parameter_list(parameter='access',
                                    allowed_values=access_active)
    if len(access_active) == len(access):
        access = []

    query_params: QueryParams = {
        'key': get_url_parameter_value(parameter='key', use_escape=False),
        'name': get_url_parameter_value(parameter='name',
                                        allowed_values=name_active),
        'name_list': name_list,
        'category': get_url_parameter_value(parameter='category',
                                            allowed_values=category_active),
        'category_list': category_list,
        'value': get_url_parameter_value(parameter='value', use_escape=False),
        'year_first': get_url_parameter_value(parameter='year_first'),
        'year_last': get_url_parameter_value(parameter='year_last'),
        'license': licentie,
        'access': access,
        'source_system': get_url_parameter_value(parameter='source_system',
                                                 allowed_values=source_active),
        'source_system2': get_url_parameter_value(parameter='source_system2',
                                                  allowed_values=source_active + OVERLAP_MODE_SOURCE_ALL),
        'start_orgs': get_url_parameter_value(parameter='start_orgs', use_escape=False),
        'collab_orgs': get_url_parameter_value(parameter='collab_orgs', use_escape=False),
        'max_nr_items': int(max_nr_items)
    }
    return query_params


def get_url_page_params() -> PageParams:
    """Construct a dict that contains all possible parameters
    for a page from the URL. If the URL does not
    contain a certain parameter, insert its default value,
    so that we can always assume that every key in the dict
    exists.
    If you add fields, add them to
    ricgraph/ricgraph_utils.py/create_empty_page_params() too.

    :return: The dict with all URL parameters related to a page.
    """
    max_nr_table_rows = get_url_parameter_value(parameter='max_nr_table_rows',
                                                default_value=str(MAX_ROWS_IN_TABLE))
    if not max_nr_table_rows.isnumeric():
        # This also catches negative numbers, they contain a '-' and are not numeric.
        # See https://www.w3schools.com/python/ref_string_isnumeric.asp.
        max_nr_table_rows = str(MAX_ROWS_IN_TABLE)

    page_params: PageParams = {
        # Used in collabspage() and collabsresultpage() and some related functions.
        'collab_mode': get_url_parameter_value(parameter='collab_mode',
                                               allowed_values=get_global_list(
                                                   ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                   item='collab_mode_all')),
        # Used in many pages.
        'discoverer_mode': get_url_parameter_value(parameter='discoverer_mode',
                                                   allowed_values=get_global_list(
                                                      ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                      item='discoverer_mode_all'),
                                                   default_value=get_global_str(
                                                      ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                      item='discoverer_mode_default')),
        # Used in osprofileresultpage() and osdashboardresultpage().
        'histogram_mode': get_url_parameter_value(parameter='histogram_mode',
                                                  allowed_values=get_global_list(
                                                      ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                      item='histogram_mode_all')),
        # Used in many pages.
        'max_nr_table_rows': int(max_nr_table_rows),
        # Used in some pages.
        'origin': get_url_parameter_value(parameter='origin',
                                          allowed_values=get_global_list(
                                              ricgraph_info=RICGRAPH_SYSTEMINFO,
                                              item='origin_button_all')),
        # Used in some pages.
        'overlap_mode': get_url_parameter_value(parameter='overlap_mode',
                                                allowed_values=get_global_list(
                                                    ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                    item='overlap_mode_all')),
        # Used in many pages.
        'search_mode': get_url_parameter_value(parameter='search_mode',
                                               allowed_values=get_global_list(
                                                   ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                   item='search_mode_all')),
        # Used in many pages.
        'view_mode': get_url_parameter_value(parameter='view_mode',
                                             allowed_values=get_global_list(
                                                 ricgraph_info=RICGRAPH_SYSTEMINFO,
                                                 item='view_mode_all'))
    }
    return page_params


def merge_and_remove_empty(page_params: PageParams,
                           query_params: QueryParams) -> dict:
    """Merges two TypedDicts 'page_params' and 'query_params',
    and removes empty values (as in '' or []) from  the result.
    To be used before constructing a URL, to prevent lots of empty
    values in the URL (as in ...&year_first=&year_last=&...).

    :param page_params: The PageParams dict.
    :param query_params: The QueryParams dict.
    :return: The dict that has no empty values.
    """
    merge = {**page_params, **query_params}
    non_empty = {}
    for key in merge:
        if merge[key] not in ['', []]:
            non_empty[key] = merge[key]
    return non_empty


# ##############################################################################
# DataFrame related functions for diagrams.
# ##############################################################################
def remove_hierarchical_orgs(df: DataFrame | None,
                             orgs_with_hierarchies: DataFrame,
                             org_to_keep: str) -> DataFrame | None:
    """
    This function removes hierarchical orgs from a DataFrame, leaving the
    top level organization only, for the organizations in orgs_with_hierarchies,
    except for org_to_keep (it will be kept).
    This is useful if you specifically query for 'org_to_keep'.

    :param df: DataFrame.
    :param orgs_with_hierarchies: DataFrame with hierarchical orgs.
    :param org_to_keep: if the row and column name starts with
      an element of this list or with this string, do NOT remove it.
      For now, this function only works for str, not list.
    :return: modified DataFrame, or None on error.
    """
    org_keep_abbr = extract_organization_abbreviation(org_name=org_to_keep)

    # No need to check for df is None, will be done in remove_one_hierarchical_org().
    df = remove_one_hierarchical_org(df=df,
                                     orgs_to_keep=org_to_keep,
                                     orgs_to_drop_pattern=org_keep_abbr)
    if df is None or df.empty:
        return None

    if orgs_with_hierarchies is None or df.empty:
        # Nothing more to be done.
        return df

    for row in orgs_with_hierarchies.itertuples(index=False):
        org_abbr = str(row.org_abbreviation)
        orgs_name = str(row.org_fullname)
        if org_abbr == org_keep_abbr:
            # Already done.
            continue
        df = remove_one_hierarchical_org(df=df,
                                         orgs_to_keep=orgs_name,
                                         orgs_to_drop_pattern=org_abbr)
        if df is None or df.empty:
            return None
    return df


def remove_one_hierarchical_org(df: DataFrame | None,
                                orgs_to_keep: str | list,
                                orgs_to_drop_pattern: str) -> DataFrame | None:
    """
    Remove rows and columns from DataFrame whose
    index or column starts with orgs_to_drop_pattern,
    except for organizations that are in orgs_to_keep.
    Note that this can be done because all (sub-)organizations of a person
    are linked to that person in the graph.
    This means that the column of the top level organization contains
    counts for its sub-organizations. So the sub-organizations can be removed
    without loosing data.

    :param df: DataFrame.
    :param orgs_to_drop_pattern: a string pattern that is matched
      to index and column name, if it starts with this string, remove it.
    :param orgs_to_keep: if the index and column name starts with
      an element of this list or with this string, do NOT remove it.
    :return: modified DataFrame, or None on error.
    """
    if df is None or df.empty:
        print('remove_one_hierarchical_org(): Error, DataFrame is empty.')
        return None

    # Define keep-check() functions based on orgs_to_keep type.
    if isinstance(orgs_to_keep, str):
        def should_keep(name):
            return name.startswith(orgs_to_keep)
    elif isinstance(orgs_to_keep, list):
        def should_keep(name):
            return name in orgs_to_keep
    else:
        print('remove_one_hierarchical_org(): Error, unknown type for parameter "orgs_to_keep".')
        return None

    # Find rows and columns to drop
    rows_to_drop = [idx for idx in df.index
                    if idx.startswith(orgs_to_drop_pattern) and not should_keep(idx)]
    cols_to_drop = [col for col in df.columns
                    if col.startswith(orgs_to_drop_pattern) and not should_keep(col)]

    df_copy = df.copy(deep=True)
    result = df_copy.drop(index=rows_to_drop, columns=cols_to_drop)
    return result
