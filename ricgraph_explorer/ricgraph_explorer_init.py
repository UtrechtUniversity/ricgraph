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
# Ricgraph Explorer initialization functions.
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, January 2023.
# Extended Rik D.T. Janssen, February, September 2023 to June 2025.
#
# ########################################################################


from os import path
from typing import Union
from connexion import FlaskApp
from ricgraph import (open_ricgraph, read_all_values_of_property,
                      ROTYPE_ALL, ROTYPE_PUBLICATION)
from ricgraph_explorer_constants import (HOMEPAGE_INTRO_FILE,
                                         PRIVACY_STATEMENT_FILE, PRIVACY_MEASURES_FILE)


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
    file_path = path.join(this_app.static_folder, filename)
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
    file_path = path.join(this_app.static_folder, filename)
    with open(file_path, 'r') as file:
        html = file.read()
    return html


def initialize_ricgraph_explorer(ricgraph_explorer_app: FlaskApp) -> None:
    """Initialize Ricgraph Explorer.

    Note that although 'ricgraph_explorer_app' is not 'returned', it is modified.

    :param ricgraph_explorer_app: The FlaskApp ricgraph_explorer.
    :return: None.
    """
    store_ricgraph_explorer_app(app=ricgraph_explorer_app)
    graph = open_ricgraph()
    if graph is None:
        print('Ricgraph could not be opened.')
        exit(1)
    set_ricgraph_explorer_global(name='graph', value=graph)

    name_all = read_all_values_of_property('name')
    if len(name_all) == 0:
        print('Warning (possibly Error) in obtaining list with all property values for property "name".')
        print('Continuing with an empty list. This might give unexpected results.')
        name_all = []
    name_personal_all = read_all_values_of_property('name_personal')
    if len(name_personal_all) == 0:
        print('Warning (possibly Error) in obtaining list with all property values for property "name_personal".')
        print('Continuing with an empty list. This might give unexpected results.')
        name_personal_all = []
    category_all = read_all_values_of_property('category')
    if len(category_all) == 0:
        print('Warning (possibly Error) in obtaining list with all property values for property "category".')
        print('Continuing with an empty list. This might give unexpected results.')
        category_all = []
    source_all = read_all_values_of_property('_source')
    if len(source_all) == 0:
        print('Warning (possibly Error) in obtaining list with all property values for property "_source".')
        print('Continuing with an empty list. This might give unexpected results.')
        source_all = []
    set_ricgraph_explorer_global(name='name_all', value=name_all)
    set_ricgraph_explorer_global(name='name_personal_all', value=name_personal_all)
    set_ricgraph_explorer_global(name='category_all', value=category_all)
    set_ricgraph_explorer_global(name='source_all', value=source_all)


    publication_types_all = list(set(ROTYPE_PUBLICATION).intersection(set(category_all)))
    publication_types_all = sorted(publication_types_all, key=str.lower)
    if len(publication_types_all) == 0:
        print('Warning (possibly Error) in obtaining list with all publication types from property "category".')
        print('Continuing with an empty list. This might give unexpected results.')
        publication_all = []
    set_ricgraph_explorer_global(name='publication_types_all', value=publication_types_all)

    name_all_datalist = '<datalist id="name_all_datalist">'
    for property_item in name_all:
        name_all_datalist += '<option value="' + property_item + '">'
    name_all_datalist += '</datalist>'
    set_ricgraph_explorer_global(name='name_all_datalist', value=name_all_datalist)

    if 'competence' in category_all:
        personal_types_all = ['competence', 'person']
    else:
        personal_types_all = ['person']
    set_ricgraph_explorer_global(name='personal_types_all', value=personal_types_all)

    resout_types_all = []
    resout_types_all_datalist = '<datalist id="resout_types_all_datalist">'
    remainder_types_all = []
    category_all_datalist = '<datalist id="category_all_datalist">'
    for property_item in category_all:
        if property_item in ROTYPE_ALL:
            resout_types_all.append(property_item)
            resout_types_all_datalist += '<option value="' + property_item + '">'
        if property_item not in personal_types_all:
            remainder_types_all.append(property_item)
        category_all_datalist += '<option value="' + property_item + '">'
    resout_types_all_datalist += '</datalist>'
    category_all_datalist += '</datalist>'
    set_ricgraph_explorer_global(name='resout_types_all', value=resout_types_all)
    set_ricgraph_explorer_global(name='resout_types_all_datalist', value=resout_types_all_datalist)
    set_ricgraph_explorer_global(name='remainder_types_all', value=remainder_types_all)
    set_ricgraph_explorer_global(name='category_all_datalist', value=category_all_datalist)

    source_all_datalist = '<datalist id="source_all_datalist">'
    for property_item in source_all:
        source_all_datalist += '<option value="' + property_item + '">'
    source_all_datalist += '</datalist>'
    set_ricgraph_explorer_global(name='source_all_datalist', value=source_all_datalist)

    if flask_check_file_exists(ricgraph_explorer_app=ricgraph_explorer_app,
                               filename=PRIVACY_STATEMENT_FILE):
        privacy_statement_link = '<a href=/static/' + PRIVACY_STATEMENT_FILE + '>'
        privacy_statement_link += 'Read the privacy statement</a>. '
    else:
        privacy_statement_link = ''
    set_ricgraph_explorer_global(name='privacy_statement_link', value=privacy_statement_link)
    if flask_check_file_exists(ricgraph_explorer_app=ricgraph_explorer_app,
                               filename=PRIVACY_MEASURES_FILE):
        privacy_measures_link = '<a href=/static/' + PRIVACY_MEASURES_FILE + '>'
        privacy_measures_link += 'Read the privacy measures document</a>. '
    else:
        privacy_measures_link = ''
    set_ricgraph_explorer_global(name='privacy_measures_link', value=privacy_measures_link)

    homepage_intro_html = flask_read_file(ricgraph_explorer_app=ricgraph_explorer_app,
                                          filename=HOMEPAGE_INTRO_FILE)
    set_ricgraph_explorer_global(name='homepage_intro_html', value=homepage_intro_html)
    store_ricgraph_explorer_app(ricgraph_explorer_app)
    return


# ################################################
# Ricgraph Explorer initialization.
# ################################################
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
    with current_app.app.app_context():
        current_app.app.config[name] = value
    return


def get_ricgraph_explorer_global(name: str):
    """Get a global variable from the app context.

    :return: the value of that variable (can be anything).
    """
    current_app = retrieve_ricgraph_explorer_app()
    if name in current_app.app.config:
        value = current_app.app.config.get(name)
    else:
        print('get_ricgraph_explorer_global(): Error, cannot find global "' + name + '".')
        return None

    return value
