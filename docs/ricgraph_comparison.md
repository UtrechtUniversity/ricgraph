# Ricgraph comparison

There are a number of approaches that collect research related information 
from various sources and 
combine them into one data structure. This section will give a short
explanation of some of these approaches and how they compare to Ricgraph.
This comparison was last updated in spring 2024.

[Return to main README.md file](../README.md#ricgraph---research-in-context-graph).

## General overview

| name                                                                           | data structure               | how does it obtain data?                                                                                        | fields (entities) in system                                                                                        | maturity                           |
|--------------------------------------------------------------------------------|------------------------------|-----------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|------------------------------------|
| [Ricgraph](https://www.ricgraph.eu)                                            | graph                        | harvesting of any source, not only research related entities, requires creation or adaptation of harvest script | any field (configurable), in standard configuration: research outputs, people (with any identifier), organizations | proof of concept                   | 
| [EOSC research discovery graph](https://faircore4eosc.eu/eosc-core-components) | probably graph               | in development                                                                                                  | in development                                                                                                     | does not exist yet                 | 
| [EOSC PID graph](https://faircore4eosc.eu/eosc-core-components)                | probably graph               | in development                                                                                                  | in development                                                                                                     | does not exist yet                 | 
| [Freya PID graph](https://www.project-freya.eu/the-pid-graph.html)             | graph                        | unclear                                                                                                         | unclear                                                                                                            | proof of concept, project finished | 
| [Lens](https://www.lens.org)                                                   | relational                   | harvesting of many sources, e.g. Microsoft Academic, Crossref, ORCID, Pubmed, EPO, USPTO, ...                   | research outputs, people, publishers, patents, organizations                                                       | mature                             | 
| [OpenAire graph](https://graph.openaire.eu)                                    | graph                        | harvesting of institutional, data, and software repositories, and many other (ca 70.000 sources)                | research outputs, people, organizations, funders, funding streams, projects, communities                           | mature                             | 
| [OpenAlex](https://openalex.org)                                               | NoSQL (unstructured)         | harvesting of many sources, e.g. Microsoft Academic, Crossref, ORCID, ROR, Pubmed, Internet Archive, ...        | research outputs, people, organizations, publishers, concepts, geo info                                            | mature                             | 
| [Research.fi](https://research.fi/en/)                                         | asp.net, probably relational | harvesting of Finnish institutional repositories and funder systems                                             | publications, people (beta), projects, research data, funding calls, infrastructures, organizations                | mature                             | 

All of these systems only store metadata, they do not store objects (e.g. pdfs, data files, software, etc.).
Often they store the link to the object.

A big difference between on the one hand Lens, OpenAire graph, OpenAlex and Research.fi
and on the other Ricgraph is their scale: the first group harvests a large number of sources. 
They also offer one single place of access for anyone. 
That also means that it will not be easy to extend these to your own needs (see next section), 
since one will need large computer facilities to host these systems 
and the data they contain.

Ricgraph follows a different approach: by selecting sources to harvest that are 
important to a user or organization, one is able to create a system that perfectly suits 
a certain information need of that person or organization. 
In creating harvest scripts, it is possible to harvest
only that information that is relevant for a certain purpose. 
For example, one of the example harvest
scripts harvests the Utrecht University staff pages. 
These pages cannot be harvested by other organizations
due to the privileges required. Also, it is possible to harvest a source that is internal
to an organization. 
Ricgraph can be installed on any internal or external accessible system according to your needs,
so the data in Ricgraph is only accessible for persons of a certain organization,
or for anyone.

## Extendability

| name                          | open source                                                     | extendable   | create your own visualizers or explorers | example code | harvest your own sources | additional information                                            |
|-------------------------------|-----------------------------------------------------------------|--------------|------------------------------------------|--------------|--------------------------|-------------------------------------------------------------------|
| Ricgraph                      | yes, [GitHub](https://github.com/UtrechtUniversity/ricgraph)    | yes          | yes                                      | yes          | yes                      | [read more](https://docs.ricgraph.eu)                             |
| EOSC research discovery graph | probably in the future                                          |              |                                          |              |                          | in development, does not exist yet                                |
| EOSC PID graph                | probably in the future                                          |              |                                          |              |                          | in development, does not exist yet                                |
| Freya PID graph               | unknown                                                         | unknown      | unknown                                  | unknown      | unknown                  | project has finished                                              |
| Lens                          | no                                                              | no           | no                                       | no           | no                       | [read more](https://about.lens.org)                               |
| OpenAire graph                | unknown                                                         | unknown      | probably not                             | probably not | no                       | [read more](https://graph.openaire.eu/what-is-the-openaire-graph) |
| OpenAlex                      | yes, [GitHub](https://github.com/orgs/ourresearch/repositories) | probably not | probably not                             | probably not | no                       | [read more](https://docs.openalex.org)                            |
| Research.fi                   | yes, [GitHub](https://github.com/CSCfi)                         | probably not | probably not                             | probably not | no                       | [read more](https://research.fi/en/service-info)                  |

As indicated above, systems such as Lens, OpenAire graph, OpenAlex and Research.fi
are difficult to extend due to their size. For the Freya PID graph the author could not find 
information, and the EOSC research discovery graph and PID graph do not exist yet.

Ricgraph is easy to extend: the code is concise and can be found on GitHub.
Also, it is possible to traverse the graph that has been constructed, either with 
[Ricgraph Explorer](ricgraph_explorer.md#ricgraph-explorer), 
the [Ricgraph REST API](ricgraph_restapi.md#ricgraph-rest-api)
or with any other visualizer or explorer that someone builds.
Also, Ricgraph can contain any field (entity) by changing the Ricgraph initialization file, 
creating a harvest script to fill this field, and modifying Ricgraph Explorer to show this field.
