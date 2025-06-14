# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
#
# MIT License
# 
# Copyright (c) 2022-2025 Rik D.T. Janssen
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
# With this code, you can harvest data sets from Yoda, using Datacite, with
# the OAI-PMH protocol.
# You have to set some parameters in ricgraph.ini.
# Also, you can set a number of parameters in the code following the "import"
# statements below.
#
# Original version Rik D.T. Janssen, December 2022.
# Updated Rik D.T. Janssen, April, October 2023, February 2025.
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
#   --organization <organization abbreviation>
#           Harvest data from organization <organization abbreviation>.
#           The organization abbreviations are specified in the Ricgraph ini
#           file.
#           If this option is not present, the script will prompt the user
#           what to do.
#
# ########################################################################


import sys
import pandas
import xmltodict
from sickle import Sickle
import ricgraph as rcg

# Set this to True to simulate the harvest. If True, do not harvest, but read it from a file.
YODA_READ_HARVEST_FROM_FILE = False
YODA_HARVEST_FILENAME = 'yoda_datacite_harvest.xml'

# Set this to True to read data from the csv file. No harvest will be done, this would
# not make sense. If False, a harvest will be done.
# If True, the value of YODA_READ_HARVEST_FROM_FILE does not matter.
YODA_READ_DATA_FROM_FILE = False
# YODA_READ_DATA_FROM_FILE = True
YODA_DATA_FILENAME = 'yoda_datacite_data.csv'

YODA_HEADERS = {'metadataPrefix': 'oai_datacite',
                'ignore_deleted': True
                }


# ######################################################
# Mapping from Yoda Datacite research output types to Ricgraph research output types.
# ######################################################
ROTYPE_MAPPING_YODA = {
    'Research Data': rcg.ROTYPE_DATASET,
    'Method Description': rcg.ROTYPE_METHOD_DESCRIPTION,
    'Model': rcg.ROTYPE_MODEL,
    'Computer code': rcg.ROTYPE_SOFTWARE,
    'Other Document': rcg.ROTYPE_OTHER_CONTRIBUTION
}


# ######################################################
# Utility functions related to harvesting of Yoda
# ######################################################

# ######################################################
# Parsing
# ######################################################

def restructure_parse(df: pandas.DataFrame) -> pandas.DataFrame:
    """Restructure the parsed data from the source system.
    This means: convert all field names found in the source system
    to recognized Ricgraph fields (e.g. replace 'doi' with 'DOI'),
    and make sure that every column that is expected further down
    this code is present (i.e. insert an empty column if needed).
    No processing of data in columns is done.

    :param df: dataframe with identifiers.
    :return: Result of action described above.
    """
    df_mod = df.copy(deep=True)

    # We assume these fiels are present.
    df_mod.rename(columns={'contributorName': 'FULL_NAME',
                           'affiliation': 'ORGANIZATION_NAME',
                           'resourceType': 'DOI_TYPE',
                           }, inplace=True)

    # But for these, we do not know for sure.
    if 'ORCID' not in df_mod.columns:
        df_mod['ORCID'] = ''

    if 'ISNI' not in df_mod.columns:
        df_mod['ISNI'] = ''

    if 'Author identifier (Scopus)' in df_mod.columns:
        df_mod.rename(columns={'Author identifier (Scopus)': 'SCOPUS_AUTHOR_ID'}, inplace=True)
    else:
        df_mod['SCOPUS_AUTHOR_ID'] = ''

    if 'ResearcherID (Web of Science)' in df_mod.columns:
        df_mod.rename(columns={'ResearcherID (Web of Science)': 'RESEARCHER_ID'}, inplace=True)
    else:
        df_mod['RESEARCHER_ID'] = ''

    if 'DAI' in df_mod.columns:
        df_mod.rename(columns={'DAI': 'DIGITAL_AUTHOR_ID'}, inplace=True)
    else:
        df_mod['DIGITAL_AUTHOR_ID'] = ''

    df_mod = df_mod[['DOI', 'DOI_TYPE', 'FULL_NAME',
                     'DIGITAL_AUTHOR_ID',
                     'ORCID', 'SCOPUS_AUTHOR_ID',
                     'ISNI', 'RESEARCHER_ID',
                     'titles', 'publicationYear',
                     'ORGANIZATION_NAME'
                     ]].copy(deep=True)
    return df_mod


def process_parsed_data(df: pandas.DataFrame) -> pandas.DataFrame:
    """Process the parsed data from the source system.
    This means: do any type of processing on values in 'df'.
    This function is only to change all values in a
    column, not for one value in a column.

    :param df: dataframe with identifiers.
    :return: Result of action described above.
    """
    df_mod = df.copy(deep=True)

    # In column "affiliation", sometimes there is a string (when someone has one affiliation),
    # and sometimes a list of strings (when someone has more than one affiliation).
    # First, convert any string values in that column to single-element lists.
    # This ensures that all values in the column are list-like.
    df_mod['ORGANIZATION_NAME'] = df_mod['ORGANIZATION_NAME'].apply(lambda x: [x] if isinstance(x, str) else x)
    # Then, use the explode() function on the that column.
    # This will create a new row for each element in the lists, while keeping the other column values the same.
    # Finally, a reset_index(drop=True) is used to create a new unique index for all rows.
    df_mod = df_mod.explode('ORGANIZATION_NAME').reset_index(drop=True)

    df_mod['DOI_TYPE'] = df_mod[['DOI_TYPE']].apply(
        lambda row: rcg.lookup_resout_type(research_output_type=row['DOI_TYPE'],
                                           research_output_mapping=ROTYPE_MAPPING_YODA), axis=1)

    return df_mod


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
        elif item_in_names == 'affiliation':
            affiliation_identifiers = dict_with_one_name['affiliation']
            for identifier in affiliation_identifiers:
                if identifier == '@affiliationIdentifierScheme':
                    # This one is to catch XML lines like
                    # <affiliation affiliationIdentifier="https://ror.org/04pp8hn57"
                    #     affiliationIdentifierScheme="ROR">Utrecht University</affiliation>
                    key = item_in_names
                    value = affiliation_identifiers['#text']
                    new_record[key] = value
                    # TODO: get the ROR from 'affiliation_identifiers'. The following works.
                    # But it should also work down below, otherwise it is kind of useless.
                    # if '@affiliationIdentifierScheme' in affiliation_identifiers \
                    #    and '@affiliationIdentifier' in affiliation_identifiers:
                    #     id_scheme = affiliation_identifiers['@affiliationIdentifierScheme']
                    #     value_id_scheme = affiliation_identifiers['@affiliationIdentifier']
                    #     new_record[id_scheme] = value_id_scheme
                    break

                # This one is to catch XML lines like
                # <affiliation>Utrecht University</affiliation>
                key = item_in_names
                value = dict_with_one_name[key]

                if isinstance(value, dict):
                    # A person is from multiple organizations.
                    value = value['#text']

                if isinstance(value, list):
                    newvalue = []
                    for item in value:
                        if isinstance(item, dict):
                            # TODO: get the ROR from 'affiliation_identifiers'.
                            # For inspiration: see above. More complicated.
                            newvalue.append(item['#text'])
                        if isinstance(item, str):
                            newvalue.append(item)
                    if len(newvalue) == 0:
                        break
                    value = newvalue.copy()

                new_record[key] = value
        else:
            # All other name items
            key = item_in_names
            value = dict_with_one_name[key]
            new_record[key] = value
            if key == 'creatorName' or key == 'contributorName':
                # Also insert it in another column, for convenience
                if not isinstance(value, str):
                    # Sometimes it is an OrderedDict
                    new_record['contributorName'] = value['#text']
                else:
                    new_record['contributorName'] = value
                new_record['@contributorType'] = 'Creator'

    return new_record


def parse_yoda_datacite(harvest: dict) -> pandas.DataFrame:
    """Parse the harvested data sets (and other research outputs) from Yoda datacite.

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
    datacite_data = restructure_parse(df=datacite_data)
    datacite_data = process_parsed_data(df=datacite_data)
    return rcg.normalize_identifiers(df=datacite_data)


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
    print('Getting data from ' + HARVEST_SOURCE + ' from ' + url + '... ', end='')
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
    print('Harvesting from ' + HARVEST_SOURCE + '...')
    if not YODA_READ_HARVEST_FROM_FILE:
        harvest_xml_and_write_to_file(url=url,
                                      headers=headers,
                                      harvest_filename=harvest_filename)

    with open(harvest_filename) as fd:
        doc = xmltodict.parse(fd.read())

    parse = parse_yoda_datacite(harvest=doc)
    print('The harvested data from ' + HARVEST_SOURCE + ' are:')
    print(parse)
    return parse


# ######################################################
# Parsed results to Ricgraph
# ######################################################

def parsed_yoda_datacite_to_ricgraph(parsed_content: pandas.DataFrame) -> None:
    """Insert the parsed data sets, etc. in Ricgraph.

    :param parsed_content: The records to insert in Ricgraph, if not present yet.
    :return: None.
    """
    timestamp = rcg.datetimestamp()
    print('Inserting data sets from ' + HARVEST_SOURCE + ' in Ricgraph at '
          + timestamp + '...')
    history_event = 'Source: Harvest ' + HARVEST_SOURCE + ' at ' + timestamp + '.'

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

    print('The following persons from ' + HARVEST_SOURCE + ' will be inserted in Ricgraph:')
    print(person_identifiers)
    rcg.unify_personal_identifiers(personal_identifiers=person_identifiers,
                                   source_event=HARVEST_SOURCE,
                                   history_event=history_event)

    # We need to connect a data set to a person-root. However, there is no single
    # person identifier that every person has. So we will need to connect DOIs to
    # every person-identifier we have.
    print('The following data sets (DOIs) from ' + HARVEST_SOURCE + ' will be inserted in Ricgraph:')
    print(parsed_content)
    print('\nAdding DOIs and ORCIDs at ' + rcg.timestamp() + '...')
    rcg.create_nodepairs_and_edges_params(name1='DOI',
                                          category1=parsed_content['DOI_TYPE'],
                                          value1=parsed_content['DOI'],
                                          comment1=parsed_content['titles'],
                                          year1=parsed_content['publicationYear'],
                                          source_event1=HARVEST_SOURCE,
                                          history_event1=history_event,
                                          name2='ORCID',
                                          category2='person',
                                          value2=parsed_content['ORCID'])
    # Don't need to add a source_event to the following calls, since we have already inserted
    # each source above, here we are connecting them.
    print('\nAdding DOIs and DIGITAL_AUTHOR_IDs at ' + rcg.timestamp() + '...')
    rcg.create_nodepairs_and_edges_params(name1='DOI',
                                          category1=parsed_content['DOI_TYPE'],
                                          value1=parsed_content['DOI'],
                                          name2='DIGITAL_AUTHOR_ID',
                                          category2='person',
                                          value2=parsed_content['DIGITAL_AUTHOR_ID'])
    print('\nAdding DOIs and SCOPUS_AUTHOR_IDs at ' + rcg.timestamp() + '...')
    rcg.create_nodepairs_and_edges_params(name1='DOI',
                                          category1=parsed_content['DOI_TYPE'],
                                          value1=parsed_content['DOI'],
                                          name2='SCOPUS_AUTHOR_ID',
                                          category2='person',
                                          value2=parsed_content['SCOPUS_AUTHOR_ID'])
    print('\nAdding DOIs and RESEARCHER_IDs at ' + rcg.timestamp() + '...')
    rcg.create_nodepairs_and_edges_params(name1='DOI',
                                          category1=parsed_content['DOI_TYPE'],
                                          value1=parsed_content['DOI'],
                                          name2='RESEARCHER_ID',
                                          category2='person',
                                          value2=parsed_content['RESEARCHER_ID'])
    print('\nAdding DOIs and ISNIs at ' + rcg.timestamp() + '...')
    rcg.create_nodepairs_and_edges_params(name1='DOI',
                                          category1=parsed_content['DOI_TYPE'],
                                          value1=parsed_content['DOI'],
                                          name2='ISNI',
                                          category2='person',
                                          value2=parsed_content['ISNI'])

    # Same for organizations.
    print('The following organizations from person from ' + HARVEST_SOURCE + ' will be inserted in Ricgraph:')
    print(parsed_content)
    print('\nAdding organizations and ORCIDs at ' + rcg.timestamp() + '...')
    rcg.create_nodepairs_and_edges_params(name1='ORGANIZATION_NAME',
                                          category1='organization',
                                          value1=parsed_content['ORGANIZATION_NAME'],
                                          source_event1=HARVEST_SOURCE,
                                          history_event1=history_event,
                                          name2='ORCID',
                                          category2='person',
                                          value2=parsed_content['ORCID'])
    # Don't need to add a source_event to the following calls, since we have already inserted
    # each source above, here we are connecting them.
    print('\nAdding organizations and DIGITAL_AUTHOR_IDs at ' + rcg.timestamp() + '...')
    rcg.create_nodepairs_and_edges_params(name1='ORGANIZATION_NAME',
                                          category1='organization',
                                          value1=parsed_content['ORGANIZATION_NAME'],
                                          name2='DIGITAL_AUTHOR_ID',
                                          category2='person',
                                          value2=parsed_content['DIGITAL_AUTHOR_ID'])
    print('\nAdding organizations and SCOPUS_AUTHOR_IDs at ' + rcg.timestamp() + '...')
    rcg.create_nodepairs_and_edges_params(name1='ORGANIZATION_NAME',
                                          category1='organization',
                                          value1=parsed_content['ORGANIZATION_NAME'],
                                          name2='SCOPUS_AUTHOR_ID',
                                          category2='person',
                                          value2=parsed_content['SCOPUS_AUTHOR_ID'])
    print('\nAdding organizations and RESEARCHER_IDs at ' + rcg.timestamp() + '...')
    rcg.create_nodepairs_and_edges_params(name1='ORGANIZATION_NAME',
                                          category1='organization',
                                          value1=parsed_content['ORGANIZATION_NAME'],
                                          name2='RESEARCHER_ID',
                                          category2='person',
                                          value2=parsed_content['RESEARCHER_ID'])
    print('\nAdding organizations and ISNIs at ' + rcg.timestamp() + '...')
    rcg.create_nodepairs_and_edges_params(name1='ORGANIZATION_NAME',
                                          category1='organization',
                                          value1=parsed_content['ORGANIZATION_NAME'],
                                          name2='ISNI',
                                          category2='person',
                                          value2=parsed_content['ISNI'])

    print('\nDone at ' + rcg.timestamp() + '.\n')
    return


# ############################################
# ################### main ###################
# ############################################
rcg.print_commandline_arguments(argument_list=sys.argv)
if (organization := rcg.get_commandline_argument_organization(argument_list=sys.argv)) == '':
    print('Exiting.\n')
    exit(1)

yoda_organization = 'yoda_set_' + organization
YODA_URL = rcg.get_configfile_key(section='Yoda_harvesting', key='yoda_url')
YODA_SET = rcg.get_configfile_key(section='Yoda_harvesting', key=yoda_organization)
if YODA_URL == '' or YODA_SET == '':
    print('Ricgraph initialization: error, "yoda_url" or "' + yoda_organization + '" are')
    print('  not existing or empty in Ricgraph ini file, exiting.')
    exit(1)

YODA_HEADERS['set'] = YODA_SET
HARVEST_SOURCE = 'Yoda-DataCite-' + organization

print('\nPreparing graph...')
rcg.open_ricgraph()

empty_graph = rcg.get_commandline_argument_empty_ricgraph(argument_list=sys.argv)
if empty_graph == 'yes' or empty_graph == 'no':
    rcg.empty_ricgraph(answer=empty_graph)
else:
    print('Exiting.\n')
    exit(1)

rcg.graphdb_nr_accesses_print()

data_file = YODA_DATA_FILENAME.split('.')[0] \
            + '-' + organization + '.' \
            + YODA_DATA_FILENAME.split('.')[1]

if YODA_READ_DATA_FROM_FILE:
    error_message = 'There are no data from ' + HARVEST_SOURCE + ' to read from file ' + data_file + '.\n'
    print('Reading data from ' + HARVEST_SOURCE + ' from file ' + data_file + '.')
else:
    error_message = 'There are no data from ' + HARVEST_SOURCE + ' to harvest.\n'
    print('Harvesting data from ' + HARVEST_SOURCE + '.')
    harvest_file = YODA_HARVEST_FILENAME.split('.')[0] \
                   + '-' + organization + '.' \
                   + YODA_HARVEST_FILENAME.split('.')[1]
    parse_yoda_data = harvest_and_parse_yoda_datacite_data(url=YODA_URL,
                                                           headers=YODA_HEADERS,
                                                           harvest_filename=harvest_file)
    rcg.write_dataframe_to_csv(filename=data_file, df=parse_yoda_data)

parse_yoda_data = rcg.read_dataframe_from_csv(filename=data_file, datatype=str)
if parse_yoda_data is None or parse_yoda_data.empty:
    print(error_message)
else:
    parsed_yoda_datacite_to_ricgraph(parsed_content=parse_yoda_data)

rcg.graphdb_nr_accesses_print()
rcg.close_ricgraph()
