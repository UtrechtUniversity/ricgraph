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
# With this code, you can harvest the Utrecht University (UU) staff pages.
# You have to set some parameters in ricgraph.ini.
# Also, you can set a number of parameters in the code following the "import" statements below.
#
# Original version Rik D.T. Janssen, March 2023.
#
# ########################################################################


import os.path
import pandas
import uuid
from datetime import datetime
from typing import Union
import requests
import pathlib
import configparser
import ricgraph as rcg

global UUSTAFF_URL


# ######################################################
# Parameters for harvesting from UU staff pages
# ######################################################
UUSTAFF_MAX_FACULTY_NR = 25
UUSTAFF_HARVEST_FROM_FILE = False
UUSTAFF_HARVEST_FILENAME = 'uustaff_harvest.json'
UUSTAFF_DATA_FILENAME = 'uustaff_data.csv'
#UUSTAFF_MAX_RECS_TO_HARVEST = 0                  # 0 = all records
UUSTAFF_MAX_RECS_TO_HARVEST = 10                  # 0 = all records
# We can harvest many fields from the UU staff pages. For now,
# we only need a few.
UUSTAFF_FIELDS_TO_HARVEST = [
                             # 'ContactDetails',
                             'Email',
                             # 'Faculties',        # Here 'Positions' is used.
                             # 'FocusAreas',
                             'Id',
                             # 'Images',
                             # 'KeyPublications',
                             # 'LastUpdate',
                             # 'Links',
                             'LinksSocialMedia',
                             # 'Name',
                             'NameShort',
                             'Organisation',
                             'PhotoUrl',
                             'Positions',
                             # 'Prizes',
                             # 'Profile',
                             # 'Projects',
                             # 'ProjectsCompleted',
                             # 'Publications'
                             ]

UUSTAFF_FACULTY_ENDPOINT = '/Public/GetEmployeesOrganogram?f='
UUSTAFF_EMPLOYEE_ENDPOINT = '/Public/getEmployeeData?page='
UUSTAFF_SOLISID_ENDPOINT = '/RestApi/getmedewerkers?selectie=solisid:'


# ######################################################
# Parsing
# ######################################################

def parse_uustaff_persons(harvest: list) -> pandas.DataFrame:
    """Parse the harvested persons from  the UU staff pages.

    :param harvest: the harvest.
    :return: the harvested persons in a DataFrame.
    """
    parse_result = pandas.DataFrame()
    parse_chunk = []                # list of dictionaries
    print('There are ' + str(len(harvest)) + ' person records, parsing record: 0  ', end='')
    count = 0
    for harvest_item in harvest:
        count += 1
        if count % 1000 == 0:
            print(count, ' ', end='', flush=True)
        if count % 20000 == 0:
            print('\n', end='', flush=True)

        if 'Id' not in harvest_item:
            # There must be an Id, otherwise skip.
            continue
        if 'NameShort' in harvest_item:
            parse_line = {}
            parse_line['UUSTAFF_ID'] = str(harvest_item['Id'])
            parse_line['FULL_NAME'] = str(harvest_item['NameShort'])
            parse_chunk.append(parse_line)
        if 'Employee_Url' in harvest_item:
            parse_line = {}
            parse_line['UUSTAFF_ID'] = str(harvest_item['Id'])
            path = pathlib.PurePath(harvest_item['Employee_Url'])
            parse_line['UUSTAFF_PAGE'] = str(path.name)
            parse_line['UUSTAFF_PAGE_URL'] = str(harvest_item['Employee_Url'])
            parse_chunk.append(parse_line)
        if 'Email' in harvest_item:
            parse_line = {}
            parse_line['UUSTAFF_ID'] = str(harvest_item['Id'])
            parse_line['EMAIL'] = str(harvest_item['Email'])
            parse_chunk.append(parse_line)
        if 'PhotoUrl' in harvest_item:
            parse_line = {}
            parse_line['UUSTAFF_ID'] = str(harvest_item['Id'])
            # 'PhotoUrl' is a substring of a weblink, this confuses things. Replace with a UUID.
            parse_line['UUPHOTO'] = str(uuid.uuid4())
            parse_line['UUPHOTO_URL'] = UUSTAFF_URL + str(harvest_item['PhotoUrl'])
            parse_chunk.append(parse_line)
        if 'LinksSocialMedia' in harvest_item:
            for links in harvest_item['LinksSocialMedia']:
                if 'Name' in links and 'Url' in links:
                    if links['Name'] is None or links['Url'] is None:
                        continue
                    parse_line = {}
                    parse_line['UUSTAFF_ID'] = str(harvest_item['Id'])
                    name_identifier = str(links['Name'].lower())
                    value_identifier = str(links['Url'])
                    path = pathlib.PurePath(value_identifier)
                    path_name = str(path.name)
                    if 'orcid' in name_identifier:
                        parse_line['ORCID'] = path_name
                    elif 'linkedin' in name_identifier or 'linked-in' in name_identifier:
                        parse_line['LINKEDIN'] = path_name
                    elif 'github' in name_identifier:
                        parse_line['GITHUB'] = path_name
                    elif 'twitter' in name_identifier:
                        parse_line['TWITTER'] = path_name
                    else:
                        parse_line[links['Name']] = value_identifier

                    parse_chunk.append(parse_line)
        if 'Positions' in harvest_item:
            # This might be improved by including department, institute, etc.
            org_name = ''
            for stafforg in harvest_item['Positions']:
                if 'Level1' in stafforg:
                    # We take the first organisation that is not 'Universiteit Utrecht'
                    if stafforg['Level1'] == '' \
                       or stafforg['Level1'] == 'Universiteit Utrecht':
                        continue
                    else:
                        org_name = str(stafforg['Level1'])
                        break

            if org_name != '':
                parse_line = {}
                parse_line['UUSTAFF_ID'] = str(harvest_item['Id'])
                parse_line['FACULTY'] = org_name
                parse_chunk.append(parse_line)

    print(count, '\n', end='', flush=True)

    parse_chunk_df = pandas.DataFrame(parse_chunk)
    parse_result = pandas.concat([parse_result, parse_chunk_df], ignore_index=True)
    # dropna(how='all'): drop row if all row values contain NaN
    parse_result.dropna(axis=0, how='all', inplace=True)
    parse_result.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    return parse_result


# ######################################################
# Harvesting and parsing
# ######################################################

def harvest_json_uustaffpages(url: str, max_recs_to_harvest: int = 0) -> list:
    """Harvest json data from a file.

    :param url: URL to harvest.
    :param max_recs_to_harvest: maximum records to harvest.
    :return: list of records in json format, or empty list if nothing found.
    """
    print('Harvesting json data from ' + url + '.')
    print('Getting data...')

    all_records = 9999999999                # a large number
    if max_recs_to_harvest == 0:
        max_recs_to_harvest = all_records
    json_data = []
    count = 0
    for faculty_nr in range(UUSTAFF_MAX_FACULTY_NR):
        if count >= max_recs_to_harvest:
            break
        print('[faculty nr ' + str(faculty_nr) + ']')
        # 'l-EN' ensures that phone numbers are preceeded with "+31".
        # 'fullresult=true' or '=false' only differ in 'Guid' field value.
        faculty_url = url + UUSTAFF_FACULTY_ENDPOINT + str(faculty_nr) + '&l=EN&fullresult=true'
        faculty_response = requests.get(faculty_url)
        if faculty_response.status_code != requests.codes.ok:
            print('harvest_json_uustaffpages(): error during harvest faculties.')
            print('Status code: ' + str(faculty_response.status_code))
            print('Url: ' + faculty_response.url)
            print('Error: ' + faculty_response.text)
            exit(1)
        faculty_page = faculty_response.json()
        if 'Employees' not in faculty_page:
            # Empty faculty.
            continue
        if len(faculty_page['Employees']) == 0:
            # Empty faculty.
            continue

        df_employees = pandas.DataFrame(faculty_page['Employees'])
        df_employees_url = df_employees['Url']
        df_employees_url.dropna(axis=0, how='any', inplace=True)
        if df_employees_url is None:
            # Nothing found.
            continue

        employees_of_faculty = list(df_employees_url)
        for employee_id in employees_of_faculty:
            if count >= max_recs_to_harvest:
                break
            employee_url = url + UUSTAFF_EMPLOYEE_ENDPOINT + employee_id
            employee_response = requests.get(employee_url)
            if employee_response.status_code != requests.codes.ok:
                print('harvest_json_uustaffpages(): error during harvest employees.')
                print('Status code: ' + str(employee_response.status_code))
                print('Url: ' + employee_response.url)
                print('Error: ' + employee_response.text)
                exit(1)
            employee_page = employee_response.json()

            if 'Employee' in employee_page:
                parse = {}
                path = pathlib.PurePath(url)
                parse['Employee_Url'] = str(path.parent) + '/' + employee_id
                for element in UUSTAFF_FIELDS_TO_HARVEST:
                    if element in employee_page['Employee']:
                        tmp = employee_page['Employee'][element]
                        if type(tmp) == list and tmp == []:
                            continue
                        if tmp is not None:
                            parse[element] = tmp
                json_data.append(parse)

            count += 1
            if count % 50 == 0:
                print(count, ' ', end='', flush=True)
            if count % 1000 == 0:
                print('\n', end='', flush=True)

    print(' Done.\n', end='', flush=True)
    return json_data


def harvest_json_and_write_to_file_uustaffpages(filename: str,
                                                url: str,
                                                max_recs_to_harvest: int = 0) -> list:
    """Harvest json data and write the data found to a file.
    This data is a list of records in json format. If no records are harvested, nothing is written.

    :param filename: filename of the file to use for writing.
    :param url: URL to harvest.
    :param max_recs_to_harvest: maximum records to harvest.
    :return: list of records in json format, or empty list if nothing found.
    """
    json_data = harvest_json_uustaffpages(url=url, max_recs_to_harvest=max_recs_to_harvest)
    if len(json_data) == 0:
        return []
    rcg.write_json_to_file(json_data=json_data, filename=filename)
    return json_data


def harvest_and_parse_uustaffpages_data(url: str,
                                        harvest_filename: str) -> Union[pandas.DataFrame, None]:
    """Harvest and parse data from UU staff pages.

    :param url: API link to UU staff pages.
    :param harvest_filename: filename to write harvest results to.
    :return: the DataFrame harvested, or None if nothing harvested.
    """
    print('Harvesting UU staff pages...')
    retval = harvest_json_and_write_to_file_uustaffpages(filename=harvest_filename,
                                                         url=url,
                                                         max_recs_to_harvest=UUSTAFF_MAX_RECS_TO_HARVEST)
    if len(retval) == 0:
        # Nothing found.
        return None

    harvest_data = rcg.read_json_from_file(filename=harvest_filename)
    parse = parse_uustaff_persons(harvest=harvest_data)
    print('The harvested records are:')
    print(parse)
    return parse


# ######################################################
# Parsed results to Ricgraph
# ######################################################

def parsed_uustaff_persons_to_ricgraph(parsed_content: pandas.DataFrame) -> None:
    """Insert the parsed persons in Ricgraph.

    :param parsed_content: The records to insert in Ricgraph, if not present yet.
    :return: None.
    """
    print('Inserting persons from UU staff pages in Ricgraph...')
    now = datetime.now()
    timestamp = now.strftime('%Y%m%d-%H%M%S')
    history_event = 'Source: Harvest UU staff pages persons at ' + timestamp + '.'

    # The order of the columns in the DataFrame below is not random.
    # A good choice is to have in the first two columns:
    # a. the identifier that appears the most in the system we harvest.
    # b. the identifier(s) that is already present in Ricgraph from previous harvests,
    #    since new identifiers from this harvest will be  linked to an already existing
    #    person-root.
    # If you have 2 of type (b), use these as the first 2 columns.
    person_identifiers = parsed_content[['UUSTAFF_ID', 'ORCID', 'FULL_NAME',
                                         'EMAIL', 'UUSTAFF_PAGE', 'UUPHOTO',
                                         'TWITTER', 'LINKEDIN',
                                         'GITHUB']].copy(deep=True)
    person_identifiers.rename(columns={'UUSTAFF_ID': 'UUStaffId-pers'}, inplace=True)
    # dropna(how='all'): drop row if all row values contain NaN
    person_identifiers.dropna(axis=0, how='all', inplace=True)
    person_identifiers.drop_duplicates(keep='first', inplace=True, ignore_index=True)

    print('The following persons from UU staff pages will be inserted in Ricgraph:')
    print(person_identifiers)
    rcg.unify_personal_identifiers(personal_identifiers=person_identifiers,
                                   history_event=history_event)

    # Add weblinks (by using 'url_main') to nodes we have inserted above.
    nodes_to_update = parsed_content[['UUSTAFF_PAGE', 'UUSTAFF_PAGE_URL']].copy(deep=True)
    nodes_to_update.rename(columns={'UUSTAFF_PAGE': 'value',
                                    'UUSTAFF_PAGE_URL': 'url_main'}, inplace=True)
    nodes_to_update_columns = {'name': 'UUSTAFF_PAGE', 'category': 'person'}
    nodes_to_update = nodes_to_update.assign(**nodes_to_update_columns)
    nodes_to_update = nodes_to_update[['name', 'category', 'value', 'url_main']]
    print('\nThe following nodes will be updated in Ricgraph:')
    print(nodes_to_update)
    rcg.update_nodes_df(nodes_to_update)

    # Add weblinks (by using 'url_main') to nodes we have inserted above.
    nodes_to_update = parsed_content[['UUPHOTO', 'UUPHOTO_URL']].copy(deep=True)
    nodes_to_update.rename(columns={'UUPHOTO': 'value',
                                    'UUPHOTO_URL': 'url_main'}, inplace=True)
    nodes_to_update_columns = {'name': 'UUPHOTO', 'category': 'person'}
    nodes_to_update = nodes_to_update.assign(**nodes_to_update_columns)
    nodes_to_update = nodes_to_update[['name', 'category', 'value', 'url_main']]
    print('\nThe following nodes will be updated in Ricgraph:')
    print(nodes_to_update)
    rcg.update_nodes_df(nodes_to_update)

    organizations = parsed_content[['UUSTAFF_ID', 'FACULTY']].copy(deep=True)
    organizations.dropna(axis=0, how='any', inplace=True)
    organizations.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    organizations.rename(columns={'UUSTAFF_ID': 'value1',
                                  'FACULTY': 'value2'}, inplace=True)
    new_organization_columns = {'name1': 'UUStaffId-pers',
                                'category1': 'person',
                                'name2': 'UUStaffId-org',
                                'category2': 'organization',
                                'history_event2': history_event}
    organizations = organizations.assign(**new_organization_columns)
    organizations = organizations[['name1', 'category1', 'value1',
                                   'name2', 'category2', 'value2', 'history_event2']]
    print('The following organizations from UU staff pages will be inserted in Ricgraph:')
    print(organizations)
    rcg.create_nodepairs_and_edges_df(organizations)
    print('\nDone.\n')
    return


def connect_pure_with_uustaffpages_to_ricgraph(url: str) -> None:
    print('Connecting Pure with persons from UU staff pages in Ricgraph...')
    nodes_with_solisid = rcg.read_all_nodes(name='EMPLOYEE_ID')
    print('There are ' + str(len(nodes_with_solisid)) + ' SolisID records, parsing record: 0  ', end='')
    count = 0
    for node in nodes_with_solisid:
        count += 1
        if count % 100 == 0:
            print(count, ' ', end='', flush=True)
        if count % 2000 == 0:
            print('\n', end='', flush=True)

        solis_id = node['value']
        solis_url = url + UUSTAFF_SOLISID_ENDPOINT + solis_id
        response = requests.get(solis_url)
        if response.status_code != requests.codes.ok:
            print('connect_pure_with_uustaffpages_to_ricgraph(): error during harvest solisID.')
            print('Status code: ' + str(response.status_code))
            print('Url: ' + response.url)
            print('Error: ' + response.text)
            exit(1)
        page = response.json()
        if len(page) == 0:
            continue
        if 'UrlEN' in page[0]:
            uustaff_page_url = str(page[0]['UrlEN'])
        elif 'UrlNL' in page:
            uustaff_page_url = str(page[0]['UrlNL'])
        else:
            # Link to staff page not present, continue.
            continue

        path = pathlib.PurePath(uustaff_page_url)
        uustaff_page = str(path.name)
        # Does not make sense to add a 'history_event' since the two nodes already
        # exist and are not modified. So the 'history_event' will not be registered.
        rcg.merge_personroots_of_two_nodes(name1='EMPLOYEE_ID',
                                           value1=node['value'],
                                           name2='UUSTAFF_PAGE',
                                           value2=uustaff_page)

    print('\nDone.\n')
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
    UUSTAFF_URL = config['UU_staff_pages_harvesting']['uustaff_url']
except KeyError:
    print('Error, UU staff pages URL not found in Ricgraph ini file, exiting.')
    exit(1)

rcg.open_ricgraph()

# Empty Ricgraph, choose one of the following.
# rcg.empty_ricgraph(answer='yes')
# rcg.empty_ricgraph(answer='no')
rcg.empty_ricgraph()

parse_uustaff = harvest_and_parse_uustaffpages_data(url=UUSTAFF_URL,
                                                    harvest_filename=UUSTAFF_HARVEST_FILENAME)
if parse_uustaff is None:
    print('There are no UU staff data to harvest.\n')
else:
    rcg.write_dataframe_to_csv(UUSTAFF_DATA_FILENAME, parse_uustaff)

    # Harvesting from UU staff pages could be improved by better
    # parsing for UU sub organisations and UU research output.
    # For inspiration see harvest_pure_to_ricgraph.py.
    parsed_uustaff_persons_to_ricgraph(parse_uustaff)

    connect_pure_with_uustaffpages_to_ricgraph(url=UUSTAFF_URL)

rcg.close_ricgraph()
