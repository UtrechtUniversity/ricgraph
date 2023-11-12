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
# With this code, you can harvest datasets from Yoda, using Datacite, with the OAI-PMH protocol.
# You have to set some parameters in ricgraph.ini.
# Also, you can set a number of parameters in the code following the "import" statements below.
#
# Original version Rik D.T. Janssen, December 2022.
# Updated Rik D.T. Janssen, April, October 2023.
#
# ########################################################################
#
# Usage
# harvest_yoda_datacite_to_ricgraph.py [options]
#
# Options:
#   --empty_ricgraph <yes|no>
#           'yes': Ricgraph will be emptied before harvesting.
#           'no': Ricgraph will not be emptied before harvesting.
#           If this option is not present, the script will prompt the user
#           what to do.
#
# ########################################################################


import os.path
import sys
from datetime import datetime
import pandas
import xmltodict
from sickle import Sickle
import configparser
import ricgraph as rcg

YODA_HARVEST_FILENAME = 'yoda_datacite_harvest.xml'
YODA_DATA_FILENAME = 'yoda_datacite_data.csv'
YODA_HEADERS = {'metadataPrefix': 'oai_datacite',
                'ignore_deleted': True
                }
global YODA_URL


# ######################################################
# Mapping from Yoda Datacite research output types to Ricgraph research output types.
# ######################################################
ROTYPE_MAPPING_YODA = {
    'Research Data': rcg.ROTYPE_DATASET,
    'Method Description': rcg.ROTYPE_METHOD_DESCRIPTION,
    'Computer code': rcg.ROTYPE_SOFTWARE,
    'Other Document': rcg.ROTYPE_OTHER_CONTRIBUTION
}


# ######################################################
# Utility functions related to harvesting of Yoda
# ######################################################

# ######################################################
# Parsing
# ######################################################

def flatten_row(full_record: dict, dict_with_one_name: dict) -> dict:
    """The purpose of this function is, given a 'full_record', to
    flatten it. That means: most records have more than one name,
    sometimes as contributor, sometimes as creator.
    Full_records which have this, will be split into multiple records,
    where every record will have one of these names.
    Creator is a separate field, but I also include it in the list of contributors.

    :param full_record: see description above.
    :param dict_with_one_name: the dictionary with one name.
    :return: a dictionary with several parsed records.
    """
    new_record = {}
    for item_in_full_record in full_record:
        key = item_in_full_record
        value = full_record[item_in_full_record]
        if item_in_full_record == 'titles':
            # I pick the first one
            value = value['title']
        if item_in_full_record == 'identifier':
            key = value['@identifierType']
            value = value['#text']
        if item_in_full_record == 'resourceType':
            value = value['#text']
        if item_in_full_record == 'descriptions':
            description = value['description']
            value = description['#text']
        # This code was originally written to parse all elements. For Ricgraph, this is not necessary.
        #
        # if item_in_full_record == 'fundingReferences':
        #     if value is None:
        #         continue
        #     fundingref = value['fundingReference']
        #     counter = 0
        #     for fundingorgs in fundingref:
        #         counter = counter + 1
        #         if fundingorgs == 'funderName':
        #             # This is necessary, since there is only 1 dict
        #             key = fundingref['funderName']
        #             if 'awardNumber' in fundingref:
        #                 value = fundingref['awardNumber']
        #             else:
        #                 value = 'no award number for ' + key
        #             new_record['funderName_' + str(counter)] = key
        #             new_record['funderAwardNumber_' + str(counter)] = value
        #             break
        #
        #         key = fundingorgs['funderName']
        #         if 'awardNumber' in fundingorgs:
        #             value = fundingorgs['awardNumber']
        #         else:
        #             value = 'no award number for ' + key
        #         new_record['funderName_' + str(counter)] = key
        #         new_record['funderAwardNumber_' + str(counter)] = value
        # # if item_in_full_record == 'subjects':
        #     if value is None:
        #         continue
        #     subjectref = value['subject']
        #     keywords = ''
        #     oecd_fos_2007s = ''
        #     for subject in subjectref:
        #         if subject == '@subjectScheme':
        #             # This is necessary, since there is only 1 dict
        #             if subjectref['@subjectScheme'] == 'Keyword':
        #                 new_record['keywords'] = subjectref['#text']
        #             if subjectref['@subjectScheme'] == 'OECD FOS 2007':
        #                 new_record['oecd_fos_2007s'] = subjectref['#text']
        #             break
        #
        #         if subject['@subjectScheme'] == 'Keyword':
        #             keywords = keywords + '||' + subject['#text']
        #         if subject['@subjectScheme'] == 'OECD FOS 2007':
        #             oecd_fos_2007s = oecd_fos_2007s + '||' + subject['#text']
        #     if keywords != '':
        #         new_record['keywords'] = keywords[2:]
        #     if oecd_fos_2007s != '':
        #         new_record['oecd_fos_2007s'] = oecd_fos_2007s[2:]
        #
        # end of: This code was originally written to parse all elements.

        if item_in_full_record == 'creators' \
           or item_in_full_record == 'contributors':
            # This is done below
            continue
        if item_in_full_record != 'fundingReferences':
            # Prevent setting it twice for fundingReferences
            new_record[key] = value
        
    # write name and all its identifiers
    for item_in_names in dict_with_one_name:
        if item_in_names == 'nameIdentifier':
            # Separate the various nameIdentifiers (like SCOPUS_ID, ORCID, etc.)
            name_identifiers = dict_with_one_name['nameIdentifier']
            for identifier in name_identifiers:
                if identifier == '@nameIdentifierScheme':
                    # This is necessary, since there is only 1 dict
                    key = name_identifiers['@nameIdentifierScheme']
                    value = name_identifiers['#text']
                    new_record[key] = value
                    break

                key = identifier['@nameIdentifierScheme']
                value = identifier['#text']
                new_record[key] = value
        else:
            # All other name items
            key = item_in_names
            value = dict_with_one_name[key]
            new_record[key] = value
            if key == 'creatorName' or key == 'contributorName':
                # Also insert it in another colomn, for convenience
                if not isinstance(value, str):
                    # Sometimes it is an OrderedDict
                    new_record['contributorName'] = value['#text']
                else:
                    new_record['contributorName'] = value
                new_record['@contributorType'] = 'Creator'

    return new_record


def parse_yoda_datacite(harvest: dict) -> pandas.DataFrame:
    """Parse the harvested datasets (and other research outputs) from Yoda datacite.

    :param harvest: the harvest.
    :return: the harvested research outputs in a DataFrame.
    """
    list_of_records = harvest['makewellformedxml']['record']
    rowdict = []
    for item in list_of_records:
        record = item['metadata']['oai_datacite']
        record = record['payload']['resource']
        for item_in_record in record:
            if item_in_record == 'creators':
                # Make sure that all 'creators' will also be in 'contributors'
                name_elements = record[item_in_record]['creator']
                for name_item in name_elements:
                    if name_item == 'creatorName':
                        # This is necessary, since there is only 1 dict
                        newdict = flatten_row(record, name_elements)
                        rowdict.append(newdict)
                        break
                    newdict = flatten_row(record, name_item)
                    rowdict.append(newdict)

            if item_in_record == 'contributors':
                name_elements = record[item_in_record]['contributor']
                for name_item in name_elements:
                    if name_item == '@contributorType':
                        # This is necessary, since there is only 1 dict
                        newdict = flatten_row(record, name_elements)
                        rowdict.append(newdict)
                        break
                    newdict = flatten_row(record, name_item)
                    rowdict.append(newdict)

    datacite_data = pandas.DataFrame(rowdict)
    datacite_data['DOI_TYPE'] = datacite_data[['resourceType']].apply(
        lambda row: rcg.lookup_resout_type(research_output_type=row['resourceType'],
                                           research_output_mapping=ROTYPE_MAPPING_YODA), axis=1)
    datacite_data['DOI'] = datacite_data['DOI'].str.lower()
    datacite_data['ORCID'].replace(regex=r'[a-z/:_. ]*', value='', inplace=True)
    datacite_data['ISNI'].replace(regex=r'[ ]*', value='', inplace=True)

    yoda_data = datacite_data[['DOI', 'contributorName', 'DAI',
                               'ORCID', 'Author identifier (Scopus)',
                               'ISNI', 'ResearcherID (Web of Science)',
                               'titles', 'DOI_TYPE', 'publicationYear'
                               ]].copy(deep=True)
    # This does not seem to work:
    # yoda_data.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    yoda_data.rename(columns={'DAI': 'DIGITAL_AUTHOR_ID',
                              'Author identifier (Scopus)': 'SCOPUS_AUTHOR_ID',
                              'ResearcherID (Web of Science)': 'RESEARCHER_ID',
                              'contributorName': 'FULL_NAME',
                              'titles': 'TITLE'
                              }, inplace=True)

    return yoda_data


# ######################################################
# Harvesting and parsing
# ######################################################

# Inspiration for this function is from
# https://christinakouridi.blog/2019/06/16/harvesting-metadata-of-1-5million-arxiv-papers.
def harvest_xml_and_write_to_file(url: str, headers: dict, harvest_filename: str) -> None:
    """Harvest and parse XML data from Yoda datacite.
    Get the data from an OAI-PMH endpoint. Save it to file.
    Best is to use "oai_datacite" protocol, not "datacite",
    see https://support.datacite.org/docs/datacite-oai-pmh.

    :param url: URL to harvest from
    :param headers: headers for harvest.
    :param harvest_filename: filename to write harvest results to.
    :return: the DataFrame harvested, or None if nothing harvested.
    """
    # Sickle takes care of resumptionToken if present, our source does not deliver all records in one xml
    print('Getting data from ' + url + '... ', end='')
    connection = Sickle(url)
    data = connection.ListRecords(**headers)
    print('Done.')

    iters = errors = 0
    print('Saving data to ' + harvest_filename + '...')
    print('Getting record: 0  ', end='')
    # Sickle doesn't deliver wellformed xml, so we place tags around it
    with open(harvest_filename, 'w') as f:
        f.write('<makewellformedxml>')

    with open(harvest_filename, 'a+') as f:
        while True:
            try:
                f.write(data.next().raw)
                iters += 1
                if iters % 50 == 0:
                    print(iters, " ", end='', flush=True)
            except AttributeError:
                if errors > 5:
                    raise AttributeError('\nharvest_xml_and_write_to_file(): Quitting, too many errors.\n')
                else:
                    print('\nharvest_xml_and_write_to_file(): some AttributeError occurred.\n')
                    errors += 1
            except StopIteration:
                print(iters, " Done.", flush=True)
                break

    with open(harvest_filename, 'a+') as f:
        f.write('</makewellformedxml>')

    return


def harvest_and_parse_yoda_datacite_data(url: str, headers: dict, harvest_filename: str) -> pandas.DataFrame:
    """Harvest and parse data from Yoda datacite.

    :param url: URL to harvest from.
    :param headers: headers for harvest.
    :param harvest_filename: filename to write harvest results to.
    :return: the DataFrame harvested, or None if nothing harvested.
    """
    harvest_xml_and_write_to_file(url=url,
                                  headers=headers,
                                  harvest_filename=harvest_filename)
    with open(harvest_filename) as fd:
        doc = xmltodict.parse(fd.read())

    parse = parse_yoda_datacite(harvest=doc)
    print('The harvested data from Yoda datacite are:')
    print(parse)
    return parse


# ######################################################
# Parsed results to Ricgraph
# ######################################################

def parsed_yoda_datacite_to_ricgraph(parsed_content: pandas.DataFrame) -> None:
    """Insert the parsed datasets, etc. in Ricgraph.

    :param parsed_content: The records to insert in Ricgraph, if not present yet.
    :return: None.
    """
    print('Inserting datasets from Yoda (harvested from datacite) in Ricgraph...')
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    history_event = 'Source: Harvest Yoda-datacite at ' + timestamp + '.'

    # The order of the columns in the DataFrame below is not random.
    # A good choice is to have in the first two columns:
    # a. the identifier that appears the most in the system we harvest.
    # b. the identifier(s) that is already present in Ricgraph from previous harvests,
    #    since new identifiers from this harvest will be  linked to an already existing
    #    person-root.
    # If you have 2 of type (b), use these as the first 2 columns.
    person_identifiers = parsed_content[['ORCID', 'SCOPUS_AUTHOR_ID',
                                         'FULL_NAME', 'DIGITAL_AUTHOR_ID',
                                         'ISNI', 'RESEARCHER_ID']].copy(deep=True)
    # dropna(how='all'): drop row if all row values contain NaN
    person_identifiers.dropna(axis=0, how='all', inplace=True)
    person_identifiers.drop_duplicates(keep='first', inplace=True, ignore_index=True)

    print('The following persons from Yoda will be inserted in Ricgraph:')
    print(person_identifiers)
    rcg.unify_personal_identifiers(personal_identifiers=person_identifiers,
                                   source_event='Yoda-DataCite',
                                   history_event=history_event)

    print('The following datasets (DOIs) from Yoda will be inserted in Ricgraph:')
    print(parsed_content)
    print('\nAdding DOIs and ORCIDs...')
    rcg.create_nodepairs_and_edges_params(name1='DOI',
                                          category1=parsed_content['DOI_TYPE'],
                                          value1=parsed_content['DOI'],
                                          comment1=parsed_content['TITLE'],
                                          year1=parsed_content['publicationYear'],
                                          source_event1='Yoda-DataCite',
                                          history_event1=history_event,
                                          name2='ORCID',
                                          category2='person',
                                          value2=parsed_content['ORCID'])
    # Don't need to add a source_event to the following calls, since we have already inserted
    # each source above, here we are connecting them.
    print('\nAdding DOIs and DIGITAL_AUTHOR_IDs...')
    rcg.create_nodepairs_and_edges_params(name1='DOI',
                                          category1=parsed_content['DOI_TYPE'],
                                          value1=parsed_content['DOI'],
                                          name2='DIGITAL_AUTHOR_ID',
                                          category2='person',
                                          value2=parsed_content['DIGITAL_AUTHOR_ID'])
    print('\nAdding DOIs and SCOPUS_AUTHOR_IDs...')
    rcg.create_nodepairs_and_edges_params(name1='DOI',
                                          category1=parsed_content['DOI_TYPE'],
                                          value1=parsed_content['DOI'],
                                          name2='SCOPUS_AUTHOR_ID',
                                          category2='person',
                                          value2=parsed_content['SCOPUS_AUTHOR_ID'])
    print('\nAdding DOIs and RESEARCHER_IDs...')
    rcg.create_nodepairs_and_edges_params(name1='DOI',
                                          category1=parsed_content['DOI_TYPE'],
                                          value1=parsed_content['DOI'],
                                          name2='RESEARCHER_ID',
                                          category2='person',
                                          value2=parsed_content['RESEARCHER_ID'])
    print('\nAdding DOIs and ISNIs...')
    rcg.create_nodepairs_and_edges_params(name1='DOI',
                                          category1=parsed_content['DOI_TYPE'],
                                          value1=parsed_content['DOI'],
                                          name2='ISNI',
                                          category2='person',
                                          value2=parsed_content['ISNI'])
    print('\nDone.\n')
    return


# ############################################
# ################### main ###################
# ############################################
if not os.path.exists(rcg.RICGRAPH_INI_FILE):
    print('Error, Ricgraph ini file "' + rcg.RICGRAPH_INI_FILE + '" not found, exiting.')
    exit(1)

rcg.print_commandline_arguments(argument_list=sys.argv)

config = configparser.ConfigParser()
config.read(rcg.RICGRAPH_INI_FILE)
try:
    YODA_URL = config['Yoda_harvesting']['yoda_url']
    YODA_SET = config['Yoda_harvesting']['yoda_set']
    if YODA_URL == '' or YODA_SET == '':
        print('Ricgraph initialization: error, yoda_url or yoda_set empty in Ricgraph ini file, exiting.')
        exit(1)

    YODA_HEADERS['set'] = YODA_SET
except KeyError:
    print('Ricgraph initialization: error, yoda_url or yoda_set not found in Ricgraph ini file, exiting.')
    exit(1)

print('\nPreparing graph...')
rcg.open_ricgraph()

empty_graph = rcg.get_commandline_argument(argument='--empty_ricgraph',
                                           argument_list=sys.argv)
if empty_graph == '':
    # Empty Ricgraph, choose one of the following.
    # rcg.empty_ricgraph(answer='yes')
    # rcg.empty_ricgraph(answer='no')
    rcg.empty_ricgraph()
else:
    rcg.empty_ricgraph(answer=empty_graph)

parse_yoda_data = harvest_and_parse_yoda_datacite_data(url=YODA_URL,
                                                       headers=YODA_HEADERS,
                                                       harvest_filename=YODA_HARVEST_FILENAME)
if parse_yoda_data is None or parse_yoda_data.empty:
    print('There are no data from Yoda to harvest.\n')
else:
    rcg.write_dataframe_to_csv(filename=YODA_DATA_FILENAME,
                               df=parse_yoda_data)
    parsed_yoda_datacite_to_ricgraph(parsed_content=parse_yoda_data)

rcg.close_ricgraph()
