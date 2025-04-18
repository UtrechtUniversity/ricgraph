# Ricgraph REST API

You can use the Ricgraph REST API to get data from Ricgraph, or 
to execute predefined queries in Ricgraph and Ricgraph Explorer, 
in such a way that your code is not dependent on any Ricgraph 
code. In your own code, you do not need to include any of the Ricgraph dependencies, nor 
include *ricgraph.py* or *ricgraph_explorer.py*.
You can use the Ricgraph REST API to programmatically get items from Ricgraph,
as an alternative to using the user
interface [Ricgraph Explorer](ricgraph_explorer.md#ricgraph-explorer). 

Note that this will only work if someone has a running Ricgraph and
Ricgraph Explorer instance available, which you can access over the web.
That someone can be yourself, where you run Ricgraph and
Ricgraph Explorer on your own computer or use a cloud service 
such as SURF Research Cloud.
Alternatively, it can be someone else, who is doing that for you or for a 
community of users.

If you use the Ricgraph REST API, will get these results 
in a [JSON format](https://en.wikipedia.org/wiki/JSON).
The Ricgraph REST API uses 
the [OpenAPI standard](https://www.openapis.org).
It gives access to Ricgraph function calls both in *ricgraph.py* 
and in *ricgraph_explorer.py*. 
Read more about 
[REST (representational state transfer)](https://en.wikipedia.org/wiki/REST), or
read more about 
[API (application programming interface)](https://en.wikipedia.org/wiki/API).

On this page, you can learn more about:

* [Installation of the Ricgraph REST API](#installation-of-the-ricgraph-rest-api)
* [Use of the Ricgraph REST API](#use-of-the-ricgraph-rest-api)
* [Ricgraph REST API endpoint documentation](#ricgraph-rest-api-endpoint-documentation)
* [Generate the Ricgraph REST API documentation page](#generate-the-ricgraph-rest-api-documentation-page)

[Return to main README.md file](../README.md#ricgraph---research-in-context-graph).

## Installation of the Ricgraph REST API
The Ricgraph REST API is part of Ricgraph Explorer. Read [how to start Ricgraph 
  Explorer](ricgraph_explorer.md#how-to-start-ricgraph-explorer).

Depending on your needs, you might also want to read:

* [Install and use a service unit file to run Ricgraph Explorer and the Ricgraph REST 
  API](ricgraph_as_server.md#use-a-service-unit-file-to-run-ricgraph-explorer-and-the-ricgraph-rest-api).
* [Use Apache, WSGI, and ASGI to make Ricgraph Explorer and the Ricgraph
  REST API accessible from outside your virtual 
  machine](ricgraph_as_server.md#use-apache-wsgi-and-asgi-to-make-ricgraph-explorer-and-the-ricgraph-rest-api-accessible-from-outside-your-virtual-machine).


## Use of the Ricgraph REST API
A call to a REST API consists of a hostname, sometimes a port number, 
the path */api/*, followed
by a REST API endpoint.
For example, in
```
http://127.0.0.1:3030/api/person/search?value=John+Doe
```
*/person/search* is the endpoint, *value* the name of a query parameter to the REST API,
and *John+Doe* the value for the query parameter.

You can use the online documentation in Ricgraph Explorer
for the REST API. It lists the various endpoints
and parameters, and you can try out each endpoint with values for parameters as you like.
To do this, click the "REST API doc" button in the top bar of 
Ricgraph Explorer, and you will get an explanation how to do this.
See the figure below, that shows part of the Home page of Ricgraph Explorer.

<img alt="Home page of Ricgraph Explorer." src="images/ricgraph-explorer-home-page.jpg" width="80%">


## Ricgraph REST API endpoint documentation
Read 
the [Ricgraph REST API documentation page](ricgraph_restapi_gendoc.md#ricgraph---research-in-context-graph-rest-api).
This page is automatically generated from the OpenAPI yaml specification file.

## Generate the Ricgraph REST API documentation page
Please read
[Create the Ricgraph REST API
documentation](ricgraph_misc_scripts.md#create-the-ricgraph-rest-api-documentation-convert_openapi_to_mddoc).
