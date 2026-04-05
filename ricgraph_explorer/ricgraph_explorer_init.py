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
# Ricgraph Explorer initialization functions.
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, January 2023.
# Extended Rik D.T. Janssen, February, September 2023 to June 2025.
# Extended Rik D.T. Janssen, March 2026.
#
# ########################################################################


from os import path
from typing import Union
from json import loads
from connexion import FlaskApp
from pandas import DataFrame

from ricgraph import (open_ricgraph, read_all_values_of_property,
                      memcached_open_connection, memcached_check_available,
                      nodes_cache_key_id_type_size, nodes_cache_key_id_size,
                      ricgraph_get_harvest_date,
                      ACCESS_ALL, LICENSE_ALL,
                      COMPETENCE_CATEGORY_ALL,
                      COMPETENCE_CATEGORY_COMPETENCE,
                      ORGANIZATION_CATEGORY_ALL,
                      PERSON_CATEGORY_ALL,
                      PERSON_CATEGORY_PERSON,
                      PERSON_NAME_PERSON_ROOT_LIST,
                      PROJECT_CATEGORY_ALL,
                      RESEARCHRESULT_CATEGORY_ALL,
                      RESEARCHRESULT_CATEGORY_PUBLICATION,
                      RESEARCHRESULT_CATEGORY_PUBLICATION_ALL,
                      RESEARCHRESULT_CATEGORY_RESEARCH_MATERIAL,
                      RESEARCHRESULT_CATEGORY_REPORTING_MATERIAL,
                      RESEARCHRESULT_CATEGORY_ENGAGEMENT_MATERIAL,
                      get_ricgraph_ini_file,
                      get_ricgraph_version,
                      get_configfile_key,
                      get_configfile_key_organizations_with_hierarchies,
                      ricgraph_nr_nodes, ricgraph_nr_edges,
                      datetimestamp)

from ricgraph_explorer_constants import (RICGRAPH_CACHEINFO,
                                         RICGRAPH_HARVESTINFO,
                                         RICGRAPH_HARVESTINFO_INTERNAL,
                                         RICGRAPH_NODEINFO,
                                         RICGRAPH_NODEINFO_INTERNAL,
                                         RICGRAPH_SYSTEMINFO,
                                         RICGRAPH_EXPLORER_RUNMODE_GUNICORN,
                                         RICGRAPH_EXPLORER_RUNMODE_DEBUG,
                                         DISCOVERER_MODE_ALL,
                                         SEARCH_MODE_ALL,
                                         SEARCH_MODE_DEFAULT,
                                         OSL_PROFILE_MODE_ALL,
                                         HISTOGRAM_MODE_ALL,
                                         ACCESS_MODE_ALL,
                                         MAX_ITEMS_TO_RETURN_RESTAPI,
                                         page_footer_general,
                                         HOMEPAGE_INTRO_FILE, HOMEPAGE_OUTRO_FILE)


# This global contains the Ricgraph Explorer app context.
# We need it to store global variables for the app context.
_ricgraph_explorer_app = None


def store_ricgraph_explorer_app(app: FlaskApp) -> None:
    """Store the Ricgraph Explorer app in a global string. We
    need it to retrieve global variables.

    :param app: the app.
    :return: nothing.
    """
    global _ricgraph_explorer_app
    if app is None:
        print('store_ricgraph_explorer_app(): Error, no Ricgraph Explorer app passed, nothing to store.')
        return

    _ricgraph_explorer_app = app
    return


def retrieve_ricgraph_explorer_app() -> Union[FlaskApp, None]:
    """Retrieve the Ricgraph Explorer app from a global string. We
    need it to retrieve global variables.

    :return: the app, or None on error.
    """
    global _ricgraph_explorer_app
    if _ricgraph_explorer_app is None:
        print('retrieve_ricgraph_explorer_app(): Error, global Ricgraph Explorer app is None, nothing to retrieve.')
        return None
    return _ricgraph_explorer_app


def flask_check_file_exists(ricgraph_explorer_app: FlaskApp, filename: str) -> bool:
    """Check if a file exists in the static folder.

    :param ricgraph_explorer_app: The FlaskApp ricgraph_explorer.
    :param filename: The name of the file to check.
    :return: True if it exists, otherwise False.
    """
    # This function is called during app initialization.
    # We are outside the app context, because we are not in a route().
    # That means we need to get the app context.
    this_app = ricgraph_explorer_app.app
    file_path = path.join(str(this_app.static_folder), filename)
    if path.isfile(path=file_path):
        # The file exists in the static folder.
        return True
    else:
        # The file does not exist in the static folder.
        return False


def flask_read_file(ricgraph_explorer_app: FlaskApp, filename: str) -> str:
    """Read the contents of a file in the static folder.

    :param ricgraph_explorer_app: The FlaskApp ricgraph_explorer.
    :param filename: The name of the file to read.
    :return: the contents of the file, or '' when the file does not exist.
    """
    if not flask_check_file_exists(ricgraph_explorer_app=ricgraph_explorer_app, filename=filename):
        return ''

    # This function is called during app initialization.
    # We are outside the app context, because we are not in a route().
    # That means we need to get the app context.
    this_app = ricgraph_explorer_app.app
    file_path = path.join(str(this_app.static_folder), filename)
    with open(file_path, 'r') as file:
        html = file.read()
    return html


# ################################################
# Ricgraph Explorer initialization.
# ################################################
def collect_ricgraph_cacheinfo() -> None:
    """Collect information related to the cache.
    Put it in a RICGRAPH_CACHEINFO dict in 'ricgraph_explorer_app'.

    :return: None.
    """
    # The cache is not constant, it changes while running Ricgraph Explorer.
    nr_items, size_kb = nodes_cache_key_id_size()
    if memcached_check_available():
        cache_name = 'Memcached cache'
    else:
        cache_name = 'local cache'

    ricgraph_cacheinfo = {
        'cache_name': cache_name,
        'nr_items': str(nr_items),
        'size_kb': str(size_kb),
        'last_update': datetimestamp(seconds=True)
    }
    set_ricgraph_explorer_global(name=RICGRAPH_CACHEINFO,
                                 value=ricgraph_cacheinfo)
    return


def collect_ricgraph_harvestinfo() -> None:
    """Collect information related to the harvest.
    Put it in a RICGRAPH_HARVESTINFO or RICGRAPH_HARVESTINFO_INTERNAL
    dict in 'ricgraph_explorer_app'.

    :return: None.
    """
    # Read things from the graph database and store it in the app context.
    # These are all constant in Ricgraph Explorer.
    harvest_date = ricgraph_get_harvest_date()
    if harvest_date == '':
        print('The harvest date of Ricgraph is empty.')
    else:
        print('The harvest date of Ricgraph is ' + harvest_date + '.')

    source_active = read_all_values_of_property('_source')
    if len(source_active) == 0:
        print('Warning (possibly Error) in obtaining list with all property values for property "_source".')
        print('Continuing with an empty list. This might give unexpected results.')
        source_active = []
    source_active = sorted(source_active, key=lambda x: x.lower())
    source_active_datalist = '<datalist id="source_active_datalist">'
    for property_item in source_active:
        source_active_datalist += '<option value="' + property_item + '">'
    source_active_datalist += '</datalist>'

    ricgraph_harvestinfo = {
        'harvest_date': ricgraph_get_harvest_date(),
        'nr_edges': str(ricgraph_nr_edges()),
        'nr_nodes': str(ricgraph_nr_nodes()),
        'source_active': source_active,
        'last_update': datetimestamp(seconds=True)
    }
    set_ricgraph_explorer_global(name=RICGRAPH_HARVESTINFO,
                                 value=ricgraph_harvestinfo)
    ricgraph_harvestinfo = {
        'source_active_datalist': source_active_datalist,
    }
    set_ricgraph_explorer_global(name=RICGRAPH_HARVESTINFO_INTERNAL,
                                 value=ricgraph_harvestinfo)
    return


def collect_ricgraph_nodeinfo() -> None:
    """Collect information related to nodes.
    Put it in a RICGRAPH_NODEINFO or RICGRAPH_NODEINFO_INTERNAL
    dict in 'ricgraph_explorer_app'.

    :return: None.
    """
    # Read a lot of things from the graph database and store it in the app context.
    # These are all constant in Ricgraph Explorer.

    # Fields related to property 'name' in a node.
    name_active = read_all_values_of_property('name')
    if len(name_active) == 0:
        print('Warning (possibly Error) in obtaining list with all property values for property "name".')
        print('Continuing with an empty list. This might give unexpected results.')
        name_active = []
    name_active = sorted(name_active, key=lambda x: x.lower())
    name_active_datalist = '<datalist id="name_active_datalist">'
    for property_item in name_active:
        name_active_datalist += '<option value="' + property_item + '">'
    name_active_datalist += '</datalist>'
    person_name_active = read_all_values_of_property('person_name')
    if len(person_name_active) == 0:
        print('Warning (possibly Error) in obtaining list with all property values for property "person_name".')
        print('Continuing with an empty list. This might give unexpected results.')
        person_name_active = []
    person_name_active = sorted(person_name_active, key=lambda x: x.lower())

    # Fields related to property 'category' in a node.
    category_active = read_all_values_of_property('category')
    if len(category_active) == 0:
        print('Warning (possibly Error) in obtaining list with all property values for property "category".')
        print('Continuing with an empty list. This might give unexpected results.')
        category_active = []
    category_active = sorted(category_active, key=lambda x: x.lower())

    if COMPETENCE_CATEGORY_COMPETENCE in category_active:
        person_category_active = [PERSON_CATEGORY_PERSON, COMPETENCE_CATEGORY_COMPETENCE]
    else:
        person_category_active = [PERSON_CATEGORY_PERSON]

    remainder_category_active = []
    category_active_datalist = '<datalist id="category_active_datalist">'
    # 'researchresult_category_active' are elements of RESEARCHRESULT_CATEGORY_ALL that are present in your Ricgraph.
    # I.e., those have been harvested from the source systems that you chose to harvest.
    researchresult_category_active = []
    researchresult_category_active_datalist = '<datalist id="researchresult_category_active_datalist">'
    # Add the meta type representing all publications, as first item.
    # This only happens in the list of items that you can choose from
    # in a text entry field. You will need to catch it further on in the code.
    researchresult_category_active_datalist += '<option value="' + RESEARCHRESULT_CATEGORY_PUBLICATION_ALL + '">'
    # These are elements of RESEARCHRESULT_CATEGORY_PUBLICATION that are present in your Ricgraph.
    # I.e., those have been harvested from the source systems that you chose to harvest.
    researchresult_category_publication_active = []
    researchresult_category_publication_active_datalist = '<datalist id="researchresult_category_publication_active_datalist">'
    # Since 'category_active' is sorted, all vars derived from it will be sorted too,
    # except for researchresult_category_active_datalist.
    for property_item in category_active:
        if property_item in RESEARCHRESULT_CATEGORY_ALL:
            researchresult_category_active.append(property_item)
            researchresult_category_active_datalist += '<option value="' + property_item + '">'
        if property_item in RESEARCHRESULT_CATEGORY_PUBLICATION:
            researchresult_category_publication_active.append(property_item)
            researchresult_category_publication_active_datalist += '<option value="' + property_item + '">'
        if property_item not in person_category_active:
            remainder_category_active.append(property_item)
        category_active_datalist += '<option value="' + property_item + '">'
    researchresult_category_active_datalist += '</datalist>'
    researchresult_category_publication_active_datalist += '</datalist>'
    category_active_datalist += '</datalist>'

    # Fields related to property 'year' in a node.
    year_active = read_all_values_of_property('year')
    year_active = [x for x in year_active if x != '']       # Remove empty values.
    if len(year_active) == 0:
        print('Warning (possibly Error) in obtaining list with all property values for property "year".')
        print('Continuing with an empty list. This might give unexpected results.')
        year_active = []
    year_active = sorted(year_active, key=lambda x: x.lower())
    year_active_datalist = '<datalist id="year_active_datalist">'
    for property_item in year_active:
        year_active_datalist += '<option value="' + property_item + '">'
    year_active_datalist += '</datalist>'

    # Check on the completeness of some lists.
    # The following three should be equal to RESEARCHRESULT_CATEGORY_ALL.
    parts = ( RESEARCHRESULT_CATEGORY_RESEARCH_MATERIAL
            + RESEARCHRESULT_CATEGORY_REPORTING_MATERIAL
            + RESEARCHRESULT_CATEGORY_ENGAGEMENT_MATERIAL)
    if len(parts) != len(set(parts)):
        print('collect_ricgraph_nodeinfo(): Warning, ')
        print('  there are duplicates in the ')
        print('  RESEARCHRESULT_CATEGORY_*_MATERIAL lists.')
    if set(parts) != set(RESEARCHRESULT_CATEGORY_ALL):
        print('collect_ricgraph_nodeinfo(): Warning, ')
        print('  RESEARCHRESULT_CATEGORY_*_MATERIAL lists combined ')
        print('  have a different length then they should have.')

    ricgraph_nodeinfo = {
        'access_all': ACCESS_ALL,
        'category_active': category_active,
        'competence_category_all': COMPETENCE_CATEGORY_ALL,
        'name_active': name_active,
        'license_all': LICENSE_ALL,
        'organization_category_all': ORGANIZATION_CATEGORY_ALL,
        'person_category_active': person_category_active,
        'person_category_all': PERSON_CATEGORY_ALL,
        'person_name_active': person_name_active,
        'person_name_person_root_list': PERSON_NAME_PERSON_ROOT_LIST,
        'project_category_all': PROJECT_CATEGORY_ALL,
        'remainder_category_active': remainder_category_active,
        'researchresult_category_active': researchresult_category_active,
        'researchresult_category_all': RESEARCHRESULT_CATEGORY_ALL,
        'researchresult_category_publication_active': researchresult_category_active,
        'researchresult_category_publication_all': RESEARCHRESULT_CATEGORY_PUBLICATION,
        'researchresult_category_research_material': RESEARCHRESULT_CATEGORY_RESEARCH_MATERIAL,
        'researchresult_category_reporting_material': RESEARCHRESULT_CATEGORY_REPORTING_MATERIAL,
        'researchresult_category_engagement_material': RESEARCHRESULT_CATEGORY_ENGAGEMENT_MATERIAL,
        'year_active': year_active,
        'last_update': datetimestamp(seconds=True)
    }
    set_ricgraph_explorer_global(name=RICGRAPH_NODEINFO,
                                 value=ricgraph_nodeinfo)
    ricgraph_nodeinfo_internal = {
        'category_active_datalist': category_active_datalist,
        'name_active_datalist': name_active_datalist,
        'researchresult_category_active_datalist': researchresult_category_active_datalist,
        'researchresult_category_publication_active_datalist': researchresult_category_active_datalist,
        'year_active_datalist': year_active_datalist,
        'last_update': datetimestamp(seconds=True)
    }
    set_ricgraph_explorer_global(name=RICGRAPH_NODEINFO_INTERNAL,
                                 value=ricgraph_nodeinfo_internal)
    return


def collect_ricgraph_systeminfo(ricgraph_explorer_app: FlaskApp,
                                runmode: str) -> None:
    """Collect information related to Ricgraph or Ricgraph Explorer.
    Put it in a RICGRAPH_SYSTEMINFO dict in 'ricgraph_explorer_app'.
    Note that 'ricgraph_explorer_app' is modified in this function (it is
    accessed by reference).

    :param ricgraph_explorer_app: The FlaskApp ricgraph_explorer.

    :param runmode: Indicates whether Ricgraph Explorer is run via
      gunicorn or as debug.
    :return: None.
    """
    # Read a lot of things from the Ricgraph ini file.
    # These are all constant in Ricgraph Explorer.
    orgs_with_hierarchies = get_configfile_key_organizations_with_hierarchies()
    if orgs_with_hierarchies is None:
        orgs_with_hierarchies = DataFrame()
    # Convert the DataFrame to a list of dicts, for ricgraph_systeminfo.
    orgs_with_hierarchies_str = orgs_with_hierarchies.to_json(orient="records")
    orgs_with_hierarchies_records = loads(orgs_with_hierarchies_str)

    discoverer_mode_default = get_configfile_key(section='Ricgraph_explorer',
                                                 key='ricgraph_explorer_display_results_mode')
    if discoverer_mode_default not in DISCOVERER_MODE_ALL:
        print('collect_ricgraph_systeminfo(): Error, ')
        print('  not existing or unknown value "' + discoverer_mode_default + '"')
        print('  for "ricgraph_explorer_display_results_mode" in Ricgraph ini')
        print('  file "' + get_ricgraph_ini_file() + '", exiting.')
        exit(1)

    homepage_intro_html = flask_read_file(ricgraph_explorer_app=ricgraph_explorer_app,
                                          filename=HOMEPAGE_INTRO_FILE)
    homepage_outro_html = flask_read_file(ricgraph_explorer_app=ricgraph_explorer_app,
                                          filename=HOMEPAGE_OUTRO_FILE)

    if runmode == RICGRAPH_EXPLORER_RUNMODE_GUNICORN:
        runmode_message = 'You are using Ricgraph Explorer in '
        runmode_message += 'development mode. Do only use this '
        runmode_message += 'for research use, not for production use.'
    elif runmode == RICGRAPH_EXPLORER_RUNMODE_DEBUG:
        runmode_message = 'You are using Ricgraph Explorer with a '
        runmode_message += 'WSGI Gunicorn server using Uvicorn '
        runmode_message += 'for ASGI applications.'
    else:
        print('collect_ricgraph_systeminfo(): Error, unknown runmode "'
              + runmode + '".')
        exit(1)
    ricgraph_version = get_ricgraph_version()
    page_footer = '<footer class="w3-container rj-gray" style="font-size:80%">'
    page_footer += runmode_message + ' ' + page_footer_general
    page_footer += 'This site uses Ricgraph version ' + ricgraph_version + '.'
    page_footer += '</footer>'

    ricgraph_systeminfo = {
        'access_mode_all': ACCESS_MODE_ALL,
        'discoverer_mode_all': DISCOVERER_MODE_ALL,
        'discoverer_mode_default': discoverer_mode_default,
        'histogram_mode_all': HISTOGRAM_MODE_ALL,
        'homepage_intro_html': homepage_intro_html,
        'homepage_outro_html': homepage_outro_html,
        'max_items_to_return_restapi': MAX_ITEMS_TO_RETURN_RESTAPI,
        'orgs_with_hierarchies': orgs_with_hierarchies_records,
        'osl_profile_mode_all': OSL_PROFILE_MODE_ALL,
        'page_footer': page_footer,
        'ricgraph_explorer_runmode': runmode,
        'ricgraph_version': ricgraph_version,
        'search_mode_all': SEARCH_MODE_ALL,
        'search_mode_default': SEARCH_MODE_DEFAULT,
        'last_update': datetimestamp(seconds=True)
    }
    set_ricgraph_explorer_global(name=RICGRAPH_SYSTEMINFO,
                                 value=ricgraph_systeminfo)
    return


def initialize_ricgraph_explorer(ricgraph_explorer_app: FlaskApp,
                                 runmode: str) -> None:
    """Initialize Ricgraph Explorer.
    Note that 'ricgraph_explorer_app' is modified in this function (it is
    accessed by reference).

    :param ricgraph_explorer_app: The FlaskApp ricgraph_explorer.
    :param runmode: Indicates whether Ricgraph Explorer is run via
      gunicorn or as debug.
    :return: None.
    """
    print('Initializing Ricgraph Explorer...')
    store_ricgraph_explorer_app(app=ricgraph_explorer_app)
    graph = open_ricgraph()
    if graph is None:
        print('initialize_ricgraph_explorer(): Error, Ricgraph could not be opened.')
        exit(1)

    # This is the only global one that is to be retrieved using
    # set_ricgraph_explorer_global(), besides
    # ricgraph_cacheinfo, ricgraph_harvestinfo,
    # ricgraph_nodeinfo, and ricgraph_systeminfo.
    set_ricgraph_explorer_global(name='graph', value=graph)

    # Open the global cache (for nodes).
    # These are not constant, they change while running Ricgraph Explorer.
    memcached_open_connection()
    print(nodes_cache_key_id_type_size())

    collect_ricgraph_cacheinfo()
    collect_ricgraph_harvestinfo()
    collect_ricgraph_nodeinfo()
    collect_ricgraph_systeminfo(ricgraph_explorer_app=ricgraph_explorer_app,
                                runmode=runmode)
    print('Done initializing Ricgraph Explorer.\n')
    return


def set_ricgraph_explorer_global(name: str, value) -> None:
    """Set a global variable in the app context.
    This is required, otherwise we don't have them if we e.g. do
    a second REST API call.

    :param name: the name of the global.
    :param value: the value of the global. Note that it does not
      have a type since it can be any type.
    :return: None.
    """
    current_app = retrieve_ricgraph_explorer_app()
    if current_app is None:
        return
    with current_app.app.app_context():
        current_app.app.config[name] = value
    return


def get_ricgraph_explorer_global(name: str):
    """Get a global variable from the app context.

    :return: the value of that variable (can be anything).
    """
    current_app = retrieve_ricgraph_explorer_app()
    if current_app is None:
        return None
    if name in current_app.app.config:
        value = current_app.app.config.get(name)
    else:
        print('get_ricgraph_explorer_global(): Error, cannot find global "' + name + '".')
        return None

    return value
