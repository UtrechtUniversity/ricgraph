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
# Ricgraph general REST API functions.
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


from typing import Tuple
from .ricgraph_constants import HTTP_RESPONSE_OK, HTTP_RESPONSE_NOTHING_FOUND


def create_http_response_auto(result_list: list = None,
                              message: str = '',
                              next_cursor: str = '') -> Tuple[dict, int]:
    """Create an HTTP response, based on result_list.
    This is a wrapper for create_http_response().

    :param result_list: A list of dicts, to be put in the 'result' section of
      the response.
    :param message: An optional message to be put in the 'meta' section of
      the response.
    :param next_cursor: The cursor for the next set of results.
    :return: An HTTP response (as dict, to be translated to JSON)
      and an HTTP response code.
    """
    if result_list is None:
        result_list = []

    if len(result_list) == 0:
        message += 'Nothing found'
        http_status = HTTP_RESPONSE_NOTHING_FOUND
    else:
        message += str(len(result_list)) + ' items found'
        http_status = HTTP_RESPONSE_OK

    response, status = create_http_response(result_list=result_list,
                                            message=message,
                                            http_status=HTTP_RESPONSE_OK,
                                            next_cursor=next_cursor)
    return response, http_status


def create_http_response(result_list: list = None,
                         message: str = '',
                         http_status: int = HTTP_RESPONSE_OK,
                         next_cursor: str = '') -> Tuple[dict, int]:
    """Create an HTTP response.

    :param result_list: A list of dicts, to be put in the 'result' section of
      the response.
    :param message: An optional message to be put in the 'meta' section of
      the response.
    :param http_status: The HTTP status code to be put in the 'meta' section of
      the response.
    :param next_cursor: The cursor for the next set of results.
    :return: An HTTP response (as dict, to be translated to JSON)
      and an HTTP response code.
    """
    if result_list is None:
        result_list = []

    meta = {'count': len(result_list),
            # 'page': 1,                      # More pages not implemented yet.
            # 'per_page': len(result_list),   # Should be page length, not implemented yet.
            'status': http_status,
            'message': '',
            'next_cursor': next_cursor}
    if message != '':
        meta['message'] = message

    response = {'meta': meta,
                'results': result_list}
    return response, http_status
