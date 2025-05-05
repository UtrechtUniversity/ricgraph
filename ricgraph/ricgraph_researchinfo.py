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
# Ricgraph functions related to research results and research information.
# For more information about Ricgraph and Ricgraph Explorer,
# go to https://www.ricgraph.eu and https://docs.ricgraph.eu.
#
# ########################################################################
#
# Original version Rik D.T. Janssen, December 2022.
# Updated Rik D.T. Janssen, February, March, September to December 2023.
# Updated Rik D.T. Janssen, February to June, September to December  2024.
# Updated Rik D.T. Janssen, January to June 2025.
#
# ########################################################################


import re
import numpy
import pandas


def create_well_known_url(name: str, value: str) -> str:
    """Create a URL to refer to the source of a 'well known' identifier (i.e. ORCID, ISNI, etc.).

    :param name: an identifier name, e.g. ORCID, ISNI, etc.
    :param value: the value.
    :return: URL.
    """
    if name == '' or value == '':
        return ''

    if name == 'DOI':
        return 'https://doi.org/' + value
    elif name == 'GITHUB':
        return 'https://www.github.com/' + value
    elif name == 'ISNI':
        return 'https://isni.org/isni/' + value
    elif name == 'LINKEDIN':
        return 'https://www.linkedin.com/in/' + value
    # elif name == 'OPENALEX':
    #     return 'https://openalex.org/' + value
    elif name == 'ORCID':
        return 'https://orcid.org/' + value
    elif name == 'RESEARCHER_ID':
        return 'https://www.webofscience.com/wos/author/record/' + value
    elif name == 'ROR':
        return 'https://ror.org/' + value
    elif name == 'SCOPUS_AUTHOR_ID':
        return 'https://www.scopus.com/authid/detail.uri?authorId=' + value
    elif name == 'TWITTER':
        return 'https://www.twitter.com/' + value
    else:
        return ''


def normalize_doi(identifier: str) -> str:
    """Normalize DOI.

    :param identifier: identifier to normalize.
    :return: Result of normalizing.
    """
    if identifier == '':
        return ''
    identifier = identifier.lower()
    identifier = re.sub(pattern=r'https|http', repl='', string=identifier)
    identifier = re.sub(pattern=r'://', repl='', string=identifier)
    identifier = re.sub(pattern=r'www.', repl='', string=identifier)
    identifier = re.sub(pattern=r'doi.org/', repl='', string=identifier)
    identifier = re.sub(pattern=r'doi', repl='', string=identifier)
    identifier = re.sub(pattern=r'.proxy.uu.nl/', repl='', string=identifier)
    return identifier


def normalize_ror(identifier: str) -> str:
    """Normalize ROR.

    :param identifier: identifier to normalize.
    :return: Result of normalizing.
    """
    if identifier == '':
        return ''
    identifier = identifier.lower()
    identifier = re.sub(pattern=r'https|http', repl='', string=identifier)
    identifier = re.sub(pattern=r'://', repl='', string=identifier)
    identifier = re.sub(pattern=r'www.', repl='', string=identifier)
    identifier = re.sub(pattern=r'ror.org/', repl='', string=identifier)
    return identifier


def normalize_orcid(identifier: str) -> str:
    """Normalize ORCID.

    :param identifier: identifier to normalize.
    :return: Result of normalizing.
    """
    if identifier == '':
        return ''
    identifier = identifier.lower()
    identifier = re.sub(pattern=r'https|http', repl='', string=identifier)
    identifier = re.sub(pattern=r'://', repl='', string=identifier)
    identifier = re.sub(pattern=r'www.', repl='', string=identifier)
    identifier = re.sub(pattern=r'orcid.org/', repl='', string=identifier)
    identifier = identifier.upper()
    return identifier


def normalize_isni(identifier: str) -> str:
    """Normalize ISNI.

    :param identifier: identifier to normalize.
    :return: Result of normalizing.
    """
    if identifier == '':
        return ''
    identifier = identifier.lower()
    identifier = re.sub(pattern=r'https|http', repl='', string=identifier)
    identifier = re.sub(pattern=r'://', repl='', string=identifier)
    identifier = re.sub(pattern=r'www.', repl='', string=identifier)
    identifier = re.sub(pattern=r'isni.org/isni/', repl='', string=identifier)
    identifier = identifier.upper()
    return identifier


def normalize_openalex(identifier: str) -> str:
    """Normalize OpenAlex identifier.

    :param identifier: identifier to normalize.
    :return: Result of normalizing.
    """
    if identifier == '':
        return ''
    identifier = identifier.lower()
    identifier = re.sub(pattern=r'https|http', repl='', string=identifier)
    identifier = re.sub(pattern=r'://', repl='', string=identifier)
    identifier = re.sub(pattern=r'www.', repl='', string=identifier)
    identifier = re.sub(pattern=r'openalex.org/', repl='', string=identifier)
    identifier = identifier.upper()
    return identifier


def normalize_scopus_author_id(identifier: str) -> str:
    """Normalize SCOPUS_AUTHOR_ID. Return a uniform value.

    :param identifier: identifier to normalize.
    :return: Result of normalizing.
    """
    if identifier == '':
        return ''
    identifier = identifier.lower()
    identifier = re.sub(pattern=r'https|http', repl='', string=identifier)
    identifier = re.sub(pattern=r'://', repl='', string=identifier)
    identifier = re.sub(pattern=r'www.', repl='', string=identifier)
    identifier = re.sub(pattern=r'scopus.com/authid/detail.uri', repl='', string=identifier)
    identifier = re.sub(pattern=r'\?authorid\=', repl='', string=identifier)
    return identifier


def normalize_researcher_id(identifier: str) -> str:
    """Normalize RESEARCHER_ID.

    :param identifier: identifier to normalize.
    :return: Result of normalizing.
    """
    if identifier == '':
        return ''
    identifier = identifier.lower()
    identifier = re.sub(pattern=r'https|http', repl='', string=identifier)
    identifier = re.sub(pattern=r'://', repl='', string=identifier)
    identifier = re.sub(pattern=r'www.', repl='', string=identifier)
    identifier = re.sub(pattern=r'researcherid.com/rid/', repl='', string=identifier)
    identifier = identifier.upper()
    return identifier


def normalize_digital_author_id(identifier: str) -> str:
    """Normalize DIGITAL_AUTHOR_ID.

    :param identifier: identifier to normalize.
    :return: Result of normalizing.
    """
    if identifier == '':
        return ''
    identifier = identifier.lower()
    identifier = re.sub(pattern=r'urn:nbn:nl:ui:', repl='', string=identifier)
    identifier = re.sub(pattern=r'info:eu-repo/dai/nl/', repl='', string=identifier)
    identifier = identifier.upper()
    return identifier


def normalize_email(identifier: str) -> str:
    """Normalize email address.

    :param identifier: identifier to normalize.
    :return: Result of normalizing.
    """
    if identifier == '':
        return ''
    identifier = identifier.lower()
    return identifier


def normalize_identifiers(df: pandas.DataFrame) -> pandas.DataFrame:
    """Normalize selected identifiers in the dataframe.
    Delete empty rows and duplicates.

    :param df: dataframe with identifiers.
    :return: Result of normalizing.
    """
    df_mod = df.copy(deep=True)

    # Ensure that all '' values are NaN, so that those rows can be easily removed with dropna()
    df_mod.replace('', numpy.nan, inplace=True)
    # dropna(how='all'): drop row if all row values contain NaN
    df_mod.dropna(axis=0, how='all', inplace=True)
    df_mod.drop_duplicates(keep='first', inplace=True, ignore_index=True)

    # The values in this list correspond to the normalize functions above,
    # such as normalize_doi(), normalize_ror(), etc.
    for identifier in ['DOI', 'ROR', 'ORCID', 'ISNI', 'OPENALEX',
                       'SCOPUS_AUTHOR_ID', 'RESEARCHER_ID', 'DIGITAL_AUTHOR_ID',
                       'EMAIL']:
        function_name = f'normalize_{identifier.lower()}'
        if not callable(globals().get(function_name)):
            print('normalize_identifiers(): Error, function "' + function_name + '"')
            print('  does not exist, exiting.')
            exit(1)

        if identifier in df_mod.columns:
            df_mod[identifier] = df_mod[identifier].apply(
                lambda x: globals()[function_name](x) if isinstance(x, str) else x)
    return df_mod


def lookup_resout_type(research_output_type: str,
                       research_output_mapping: dict) -> str:
    """Convert a research output type from a harvested system
    to a shorter and easier Ricgraph research output type, according to a certain mapping.
    The reason for doing this is to ensure a constant naming of research output
    types for objects harvested from different sources.
    For more explanation, see the text at 'Research output types used in Ricgraph' at
    the start of this file.

    :param research_output_type: A research output type from a source system.
    :param research_output_mapping: The mapping from the source system to Ricgraph
    research output types.
    :return: The result, in a few words.
    """
    if research_output_type == '':
        print('lookup_resout_type(): no research output type specified .')
        return 'empty'

    if research_output_type not in research_output_mapping:
        print('lookup_resout_type(): unknown research output type: "' + research_output_type + '".')
        return 'unknown'

    return research_output_mapping[research_output_type]
