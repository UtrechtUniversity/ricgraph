# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
# 
# Copyright (c) 2023-2025 Rik D.T. Janssen
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
# Updated Rik D.T. Janssen, April, November 2023, February 2025.
#
# ########################################################################
#
# Usage
# harvest_uustaffpages_to_ricgraph.py [options]
#
# Options:
#   --empty_ricgraph <yes|no>
#           'yes': Ricgraph will be emptied before harvesting.
#           'no': Ricgraph will not be emptied before harvesting.
#           If this option is not present, the script will prompt the user
#           what to do.
#
# ########################################################################


import sys
import re
import pandas
from typing import Union
import requests
import pathlib
import ricgraph as rcg


# ######################################################
# Parameters for harvesting from UU staff pages
# ######################################################
ORGANIZATION = 'UU'
UUSTAFF_MAX_FACULTY_NR = 25
UUSTAFF_CONNECTDATA_FROM_FILE = False
UUSTAFF_HARVEST_FROM_FILE = False
UUSTAFF_HARVEST_FILENAME = 'uustaff_harvest.json'
UUSTAFF_DATA_FILENAME = 'uustaff_data.csv'
UUSTAFF_CONNECT_FILENAME = 'uustaff_connect.csv'
UUSTAFF_MAX_RECS_TO_HARVEST = 0                  # 0 = all records
# We can harvest many fields from the UU staff pages. For now,
# we only need a few.
UUSTAFF_FIELDS_TO_HARVEST = [
                             # 'ContactDetails',
                             'Email',
                             'Expertises',
                             # 'Faculties',        # Here 'Positions' is used.
                             'FocusAreas',
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
                             # 'Publications',
                             'Skills'
                             ]

UU_WEBSITE = 'https://www.uu.nl'
UUSTAFF_FACULTY_ENDPOINT = '/Public/GetEmployeesOrganogram?f='
UUSTAFF_EMPLOYEE_ENDPOINT = '/Public/getEmployeeData?page='
UUSTAFF_SOLISID_ENDPOINT = '/RestApi/getmedewerkers?selectie=solisid:'
UUSTAFF_PHOTO_ENDPOINT = '/Public/GetImage?Employee='


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
    print('There are ' + str(len(harvest)) + ' person records ('
          + rcg.timestamp() + '), parsing record: 0  ', end='')
    count = 0
    for harvest_item in harvest:
        count += 1
        if count % 1000 == 0:
            print(count, ' ', end='', flush=True)
        if count % 10000 == 0:
            print('(' + rcg.timestamp() + ')\n', end='', flush=True)

        if 'Employee_Url' in harvest_item:
            path = pathlib.PurePath(harvest_item['Employee_Url'])
            uustaff_page_id = str(path.name)
            parse_line = {'UUSTAFF_PAGE_ID': uustaff_page_id,
                          'UUSTAFF_PAGE_URL': str(harvest_item['Employee_Url'])}
            # Sometimes EmployeeUrl has 'https:/www...' instead of 'https://www...', repair.
            parse_line['UUSTAFF_PAGE_URL'] = re.sub(pattern=r'https:/www',
                                                    repl='https://www',
                                                    string=parse_line['UUSTAFF_PAGE_URL'])
            parse_chunk.append(parse_line)
        else:
            # There must be an Employee_Url (UUSTAFF_PAGE_ID), otherwise skip.
            continue

        if 'Id' in harvest_item:
            parse_line = {'UUSTAFF_PAGE_ID': uustaff_page_id,
                          'UUSTAFF_ID_PERS': str(harvest_item['Id'])}
            parse_chunk.append(parse_line)
        else:
            # There must be an Id (UUSTAFF_ID_PERS), otherwise skip.
            continue

        if 'NameShort' in harvest_item:
            parse_line = {'UUSTAFF_PAGE_ID': uustaff_page_id,
                          'FULL_NAME': str(harvest_item['NameShort'])}
            if (asc := rcg.convert_string_to_ascii(parse_line['FULL_NAME'])) != parse_line['FULL_NAME']:
                parse_line['FULL_NAME_ASCII'] = asc
            parse_chunk.append(parse_line)
        if 'Email' in harvest_item:
            parse_line = {'UUSTAFF_PAGE_ID': uustaff_page_id,
                          'EMAIL': str(harvest_item['Email'])}
            parse_chunk.append(parse_line)
        if 'PhotoUrl' in harvest_item:
            # 'PhotoUrl' has the form '/Public/GetImage?Employee=12&_t=34567890&t='
            # The values after '_t=' and 't=' are not relevant, the value after 'Employee=' is.
            # Probably it is UUSTAFF_ID_PERS, but I'd rather use the 'Employee' value to be sure.
            # Remove everything before 'Employee=' and after '&'.
            employee_id = str(harvest_item['PhotoUrl']).lower()
            employee_id = re.sub(pattern=r'^.*employee=', repl='', string=employee_id)
            employee_id = re.sub(pattern=r'&.*', repl='', string=employee_id)
            if employee_id == '':
                continue

            parse_line = {'UUSTAFF_PAGE_ID': uustaff_page_id,
                          'PHOTO_ID': str(employee_id)}
            parse_line['PHOTO_URL'] = UUSTAFF_URL + UUSTAFF_PHOTO_ENDPOINT + parse_line['PHOTO_ID']
            parse_chunk.append(parse_line)
        if 'LinksSocialMedia' in harvest_item:
            for links in harvest_item['LinksSocialMedia']:
                if 'Name' in links and 'Url' in links:
                    if links['Name'] is None or links['Url'] is None:
                        continue
                    parse_line = {'UUSTAFF_PAGE_ID': uustaff_page_id}
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
                    # We take the first organization that is not 'Universiteit Utrecht'
                    if stafforg['Level1'] == '' \
                       or stafforg['Level1'] == 'Universiteit Utrecht':
                        continue
                    else:
                        org_name = str(stafforg['Level1'])
                        break

            if org_name != '':
                parse_line = {'UUSTAFF_PAGE_ID': uustaff_page_id,
                              'FACULTY': ORGANIZATION + ' ' + org_name}
                parse_chunk.append(parse_line)
        if 'Expertises' in harvest_item:
            for expertise in harvest_item['Expertises']:
                if 'Name' in expertise and 'Url' in expertise:
                    parse_line = {'UUSTAFF_PAGE_ID': uustaff_page_id,
                                  'EXPERTISE_AREA_NAME': str(expertise['Name']),
                                  'EXPERTISE_AREA_URL': UU_WEBSITE + str(expertise['Url'])}
                    parse_chunk.append(parse_line)
        if 'FocusAreas' in harvest_item:
            for focusarea in harvest_item['FocusAreas']:
                if 'Name' in focusarea and 'Url' in focusarea:
                    # Focus areas are called 'Research areas' on the UU website.
                    parse_line = {'UUSTAFF_PAGE_ID': uustaff_page_id,
                                  'RESEARCH_AREA_NAME': str(focusarea['Name']),
                                  'RESEARCH_AREA_URL': UU_WEBSITE + str(focusarea['Url'])}
                    parse_chunk.append(parse_line)
        if 'Skills' in harvest_item:
            for skill in harvest_item['Skills']:
                if 'Name' in skill and 'Url' in skill:
                    parse_line = {'UUSTAFF_PAGE_ID': uustaff_page_id,
                                  'SKILL_NAME': str(skill['Name']),
                                  'SKILL_URL': UU_WEBSITE + str(skill['Url'])}
                    parse_chunk.append(parse_line)

    print(count, '(' + rcg.timestamp() + ')\n', end='', flush=True)

    parse_chunk_df = pandas.DataFrame(parse_chunk)
    parse_result = pandas.concat([parse_result, parse_chunk_df], ignore_index=True)
    return rcg.normalize_identifiers(df=parse_result)


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
        print('[faculty nr ' + str(faculty_nr) + ' at ' + rcg.timestamp() + ']')
        # 'l-EN' ensures that phone numbers are preceded with "+31".
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
            employee_url = url + UUSTAFF_EMPLOYEE_ENDPOINT + employee_id + '&l=EN'
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
                        if isinstance(tmp, list) and len(tmp) == 0:
                            continue
                        if tmp is not None:
                            parse[element] = tmp
                json_data.append(parse)

            count += 1
            if count % 50 == 0:
                print(count, '(' + rcg.timestamp() + ')  ', end='', flush=True)
            if count % 500 == 0:
                print('\n', end='', flush=True)

    print(' Done at ' + rcg.timestamp() + '.\n')
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
    json_data = harvest_json_uustaffpages(url=url,
                                          max_recs_to_harvest=max_recs_to_harvest)
    if len(json_data) == 0:
        return []
    rcg.write_json_to_file(json_data=json_data,
                           filename=filename)
    return json_data


def harvest_and_parse_uustaffpages_data(url: str,
                                        harvest_filename: str) -> Union[pandas.DataFrame, None]:
    """Harvest and parse data from UU staff pages.

    :param url: API link to UU staff pages.
    :param harvest_filename: filename to write harvest results to.
    :return: the DataFrame harvested, or None if nothing harvested.
    """
    print('Harvesting UU staff pages...')
    if not UUSTAFF_HARVEST_FROM_FILE:
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
    timestamp = rcg.datetimestamp()
    print('Inserting persons from UU staff pages in Ricgraph at '
          + timestamp + '...')
    history_event = 'Source: Harvest UU staff pages persons at ' + timestamp + '.'

    # The order of the columns in the DataFrame below is not random.
    # A good choice is to have in the first two columns:
    # a. the identifier that appears the most in the system we harvest.
    # b. the identifier(s) that is already present in Ricgraph from previous harvests,
    #    since new identifiers from this harvest will be  linked to an already existing
    #    person-root.
    # If you have 2 of type (b), use these as the first 2 columns.
    #
    # Below, we chose UUSTAFF_PAGE_ID as first identifier, because this is the identifier
    # we used to link SolisID to in the previous step
    # (in parsed_pure_uustaffpages_to_ricgraph()).

    # ####### Insert persons.
    person_identifiers = parsed_content[['UUSTAFF_PAGE_ID', 'ORCID',
                                         'UUSTAFF_ID_PERS',
                                         'FULL_NAME', 'FULL_NAME_ASCII',
                                         'EMAIL', 'PHOTO_ID',
                                         'TWITTER', 'LINKEDIN',
                                         'GITHUB']].copy(deep=True)
    # dropna(how='all'): drop row if all row values contain NaN
    person_identifiers.dropna(axis=0, how='all', inplace=True)
    person_identifiers.drop_duplicates(keep='first', inplace=True, ignore_index=True)

    print('The following persons from UU staff pages will be inserted in Ricgraph at '
          + rcg.timestamp() + ':')
    print(person_identifiers)
    rcg.unify_personal_identifiers(personal_identifiers=person_identifiers,
                                   source_event='UU staff pages',
                                   history_event=history_event)

    # ####### Add weblinks (by using 'url_main') to nodes we have inserted above.
    nodes_to_update = parsed_content[['UUSTAFF_PAGE_ID', 'UUSTAFF_PAGE_URL']].copy(deep=True)
    nodes_to_update.rename(columns={'UUSTAFF_PAGE_ID': 'value',
                                    'UUSTAFF_PAGE_URL': 'url_main'}, inplace=True)
    nodes_to_update_columns = {'name': 'UUSTAFF_PAGE_ID',
                               'category': 'person'}
    nodes_to_update = nodes_to_update.assign(**nodes_to_update_columns)
    nodes_to_update = nodes_to_update[['name', 'category', 'value', 'url_main']]
    print('\nThe following page nodes will be updated in Ricgraph at '
          + rcg.timestamp() + ':')
    print(nodes_to_update)
    rcg.update_nodes_df(nodes=nodes_to_update)

    # ####### Add weblinks (by using 'url_main') to nodes we have inserted above.
    nodes_to_update = parsed_content[['PHOTO_ID', 'PHOTO_URL']].copy(deep=True)
    nodes_to_update.rename(columns={'PHOTO_ID': 'value',
                                    'PHOTO_URL': 'url_main'}, inplace=True)
    nodes_to_update_columns = {'name': 'PHOTO_ID',
                               'category': 'person'}
    nodes_to_update = nodes_to_update.assign(**nodes_to_update_columns)
    nodes_to_update = nodes_to_update[['name', 'category', 'value', 'url_main']]
    print('\nThe following photo nodes will be updated in Ricgraph at '
          + rcg.timestamp() + ':')
    print(nodes_to_update)
    rcg.update_nodes_df(nodes=nodes_to_update)

    # ####### Insert organizations (faculties only).
    organizations = parsed_content[['UUSTAFF_PAGE_ID', 'FACULTY']].copy(deep=True)
    organizations.dropna(axis=0, how='any', inplace=True)
    organizations.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    organizations.rename(columns={'UUSTAFF_PAGE_ID': 'value1',
                                  'FACULTY': 'value2'}, inplace=True)
    new_organization_columns = {'name1': 'UUSTAFF_PAGE_ID',
                                'category1': 'person',
                                'name2': 'ORGANIZATION_NAME',
                                'category2': 'organization',
                                'source_event2': 'UU staff pages',
                                'history_event2': history_event}
    organizations = organizations.assign(**new_organization_columns)
    organizations = organizations[['name1', 'category1', 'value1',
                                   'name2', 'category2', 'value2',
                                   'source_event2', 'history_event2']]
    print('The following organizations from UU staff pages will be inserted in Ricgraph at '
          + rcg.timestamp() + ':')
    print(organizations)
    rcg.create_nodepairs_and_edges_df(left_and_right_nodepairs=organizations)

    # ####### Insert organizations (connect all to Utrecht University, all staff is part of UU).
    organizations.drop(columns={'value2'}, inplace=True)
    organizations['value2'] = 'Utrecht University'
    organizations = organizations[['name1', 'category1', 'value1',
                                   'name2', 'category2', 'value2',
                                   'source_event2', 'history_event2']]
    print('"Utrecht University" will be connected to anyone from UU staff pages in Ricgraph at '
          + rcg.timestamp() + ':')
    print(organizations)
    rcg.create_nodepairs_and_edges_df(left_and_right_nodepairs=organizations)

    # ####### Insert expertises.
    expertises = parsed_content[['UUSTAFF_PAGE_ID', 'EXPERTISE_AREA_NAME',
                                 'EXPERTISE_AREA_URL']].copy(deep=True)
    expertises.dropna(axis=0, how='any', inplace=True)
    expertises.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    expertises.rename(columns={'UUSTAFF_PAGE_ID': 'value1',
                               'EXPERTISE_AREA_NAME': 'value2',
                               'EXPERTISE_AREA_URL': 'url_main2'}, inplace=True)
    new_expertises_columns = {'name1': 'UUSTAFF_PAGE_ID',
                              'category1': 'person',
                              'name2': 'EXPERTISE_AREA',
                              'category2': 'competence',
                              'source_event2': 'UU staff pages',
                              'history_event2': history_event}
    expertises = expertises.assign(**new_expertises_columns)
    expertises = expertises[['name1', 'category1', 'value1',
                             'name2', 'category2', 'value2',
                             'url_main2', 'source_event2', 'history_event2']]
    print('The following expertises from UU staff pages will be inserted in Ricgraph at '
          + rcg.timestamp() + ':')
    print(expertises)
    rcg.create_nodepairs_and_edges_df(left_and_right_nodepairs=expertises)

    # ####### Insert research areas.
    research_areas = parsed_content[['UUSTAFF_PAGE_ID', 'RESEARCH_AREA_NAME',
                                     'RESEARCH_AREA_URL']].copy(deep=True)
    research_areas.dropna(axis=0, how='any', inplace=True)
    research_areas.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    research_areas.rename(columns={'UUSTAFF_PAGE_ID': 'value1',
                                   'RESEARCH_AREA_NAME': 'value2',
                                   'RESEARCH_AREA_URL': 'url_main2'}, inplace=True)
    new_research_areas_columns = {'name1': 'UUSTAFF_PAGE_ID',
                                  'category1': 'person',
                                  'name2': 'RESEARCH_AREA',
                                  'category2': 'competence',
                                  'source_event2': 'UU staff pages',
                                  'history_event2': history_event}
    research_areas = research_areas.assign(**new_research_areas_columns)
    research_areas = research_areas[['name1', 'category1', 'value1',
                                     'name2', 'category2', 'value2',
                                     'url_main2', 'source_event2', 'history_event2']]
    print('The following research areas from UU staff pages will be inserted in Ricgraph at '
          + rcg.timestamp() + ':')
    print(research_areas)
    rcg.create_nodepairs_and_edges_df(left_and_right_nodepairs=research_areas)

    # ####### Insert skills.
    skills = parsed_content[['UUSTAFF_PAGE_ID', 'SKILL_NAME', 'SKILL_URL']].copy(deep=True)
    skills.dropna(axis=0, how='any', inplace=True)
    skills.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    skills.rename(columns={'UUSTAFF_PAGE_ID': 'value1',
                           'SKILL_NAME': 'value2',
                           'SKILL_URL': 'url_main2'}, inplace=True)
    new_skills_columns = {'name1': 'UUSTAFF_PAGE_ID',
                          'category1': 'person',
                          'name2': 'SKILL',
                          'category2': 'competence',
                          'source_event2': 'UU staff pages',
                          'history_event2': history_event}
    skills = skills.assign(**new_skills_columns)
    skills = skills[['name1', 'category1', 'value1',
                     'name2', 'category2', 'value2',
                     'url_main2', 'source_event2', 'history_event2']]
    print('The following skills from UU staff pages will be inserted in Ricgraph at '
          + rcg.timestamp() + ':')
    print(skills)
    rcg.create_nodepairs_and_edges_df(left_and_right_nodepairs=skills)

    print('\nDone at ' + rcg.timestamp() + '.\n')
    return


def connect_pure_with_uustaffpages(url: str) -> Union[pandas.DataFrame, None]:
    """Connect Pure with the UU staff pages.
    Get SolisID from Ricgraph and harvest the corresponding data from the
    UU staff pages.

    :param url: url to the UU staff pages.
    :return: the DataFrame harvested, or None if nothing harvested.
    """
    print('Connect Pure SolisIDs with corresponding persons from UU staff pages at '
          + rcg.datetimestamp() + '...')
    nodes_with_solisid = rcg.read_all_nodes(name='EMPLOYEE_ID')
    print('There are ' + str(len(nodes_with_solisid)) + ' SolisID records, parsing record: 0  ', end='')
    parse_result = pandas.DataFrame()
    parse_chunk = []                # list of dictionaries
    count = 0
    for node in nodes_with_solisid:
        count += 1
        if count % 50 == 0:
            print(count, ' ', end='', flush=True)
        if count % 500 == 0:
            print('(' + rcg.timestamp() + ')\n', end='', flush=True)

        solis_id = node['value']
        solis_url = url + UUSTAFF_SOLISID_ENDPOINT + solis_id
        response = requests.get(solis_url)
        if response.status_code != requests.codes.ok:
            print('connect_pure_with_uustaffpages(): error during harvest solisID.')
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
        parse_line = {'EMPLOYEE_ID': str(node['value']),
                      'UUSTAFF_PAGE_ID': str(path.name)}
        parse_chunk.append(parse_line)

    print(count, '\n', end='', flush=True)
    print('Done at ' + rcg.timestamp() + '.\n')

    parse_chunk_df = pandas.DataFrame(parse_chunk)
    parse_result = pandas.concat([parse_result, parse_chunk_df], ignore_index=True)
    return rcg.normalize_identifiers(df=parse_result)


def parsed_pure_uustaffpages_to_ricgraph(parsed_content: pandas.DataFrame) -> None:
    """Insert the parsed Pure SolisIDs and UU staff data in Ricgraph.

    :param parsed_content: The records to insert in Ricgraph, if not present yet.
    :return: None.
    """
    timestamp = rcg.datetimestamp()
    history_event = 'Source: Harvest UU staff pages connect EMPLOYEE_ID and UUSTAFF_PAGE_ID at ' + timestamp + '.'

    solisids_staffids = parsed_content[['EMPLOYEE_ID', 'UUSTAFF_PAGE_ID']].copy(deep=True)
    solisids_staffids.rename(columns={'EMPLOYEE_ID': 'value1',
                                      'UUSTAFF_PAGE_ID': 'value2'}, inplace=True)
    new_solisids_staffids_columns = {'name1': 'EMPLOYEE_ID',
                                     'category1': 'person',
                                     'name2': 'UUSTAFF_PAGE_ID',
                                     'category2': 'person',
                                     'source_event2': 'UU staff pages',
                                     'history_event2': history_event}
    solisids_staffids = solisids_staffids.assign(**new_solisids_staffids_columns)
    solisids_staffids = solisids_staffids[['name1', 'category1', 'value1',
                                           'name2', 'category2', 'value2',
                                           'source_event2', 'history_event2']]

    print('The following Pure SolisIDs and corresponding persons from UU staff pages will be inserted in Ricgraph at '
          + rcg.timestamp() + ':')
    print(solisids_staffids)
    rcg.create_nodepairs_and_edges_df(left_and_right_nodepairs=solisids_staffids)

    print('Done at ' + rcg.timestamp() + '.\n')
    return


# ############################################
# ################### main ###################
# ############################################
rcg.print_commandline_arguments(argument_list=sys.argv)
UUSTAFF_URL = rcg.get_configfile_key(section='UU_staff_pages_harvesting', key='uustaff_url')
if UUSTAFF_URL == '':
    print('Ricgraph initialization: error, "uustaff_url"')
    print('  not existing or empty in Ricgraph ini file, exiting.')
    exit(1)

rcg.open_ricgraph()

empty_graph = rcg.get_commandline_argument_empty_ricgraph(argument_list=sys.argv)
if empty_graph == 'yes' or empty_graph == 'no':
    rcg.empty_ricgraph(answer=empty_graph)
else:
    print('Exiting.\n')
    exit(1)

rcg.graphdb_nr_accesses_print()

# ########## Code block A ##########
# You can use 'True' or 'False' depending on your needs to harvest.
# This might be handy if you are testing your parsing.

# if False:             # Uncomment this line to comment out code block A
if True:              # Comment this line to comment out code block A
    print('\nNote: If this script hangs, just run it again.')
    print('This is probably due to a time-out of the server that is hosting the UU staff pages.\n')

    if not UUSTAFF_CONNECTDATA_FROM_FILE:
        parsed_results = connect_pure_with_uustaffpages(url=UUSTAFF_URL)
        if parsed_results is None or parsed_results.empty:
            print('There are no Pure SolisIDs to connect to UU staff pages.\n')
        else:
            rcg.write_dataframe_to_csv(filename=UUSTAFF_CONNECT_FILENAME,
                                       df=parsed_results)
            parsed_pure_uustaffpages_to_ricgraph(parsed_content=parsed_results)
    else:
        parsed_results = rcg.read_dataframe_from_csv(filename=UUSTAFF_CONNECT_FILENAME)
        parsed_pure_uustaffpages_to_ricgraph(parsed_content=parsed_results)

    rcg.graphdb_nr_accesses_print()
# ########## End of code block A ##########


# if False:
if True:
    print('\nNote: If this script hangs from this point on, do the following:')
    print('1. Edit the python code, comment out code block A (i.e. make sure it does not get executed).')
    print('2. Rerun this script.')
    print('This is probably due to a time-out of the server that is hosting the UU staff pages.\n')
    parse_uustaff = harvest_and_parse_uustaffpages_data(url=UUSTAFF_URL,
                                                        harvest_filename=UUSTAFF_HARVEST_FILENAME)
    if parse_uustaff is None or parse_uustaff.empty:
        print('There are no UU staff data to harvest.\n')
        exit(0)

    rcg.write_dataframe_to_csv(filename=UUSTAFF_DATA_FILENAME,
                               df=parse_uustaff)

    # Harvesting from UU staff pages could be improved by better
    # parsing for UU sub organizations and UU research output.
    # For inspiration see harvest_pure_to_ricgraph.py.
    parsed_uustaff_persons_to_ricgraph(parsed_content=parse_uustaff)

    rcg.graphdb_nr_accesses_print()

rcg.close_ricgraph()
