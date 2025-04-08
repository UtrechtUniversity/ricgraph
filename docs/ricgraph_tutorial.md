# Tutorial Ricgraph - Research in context graph

## Ricgraph introduction

Ricgraph, also known as Research in context graph, enables the exploration of researchers,
teams, their results,
collaborations, skills, projects, and the relations between these items.

Ricgraph can store many types of items into a single graph.
These items can be obtained from various systems and from
multiple organizations. Ricgraph facilitates reasoning about these
items because it infers new relations between items,
relations that are not present in any of the separate source systems.
It is flexible and extensible, and can be
adapted to new application areas.

In this tutorial, we explain the possibilities of Ricgraph.
For a more detailed explanation, read the 
full documentation of Ricgraph on 
[https://docs.ricgraph.eu](https://docs.ricgraph.eu).

## Motivation

Ricgraph is software that is about
relations between items. These items can be collected from various source
systems and from multiple organizations. We
explain how Ricgraph works by applying it to the application area
*research information*. We show the insights that can be
obtained by combining information from various source systems,
insight arising from new relations that are not present
in each separate source system.

*Research information* is about anything related to research: research
results, the persons in a research team, their
collaborations, their skills, projects in which they have
participated, as well as the relations between these entities.
Examples of *research results* are publications, data sets, and software.

The following sections show three use cases 
that use different types of information (called *items*):
researchers, skills, publications,
etc. Most often, these types of information are not stored in
one system, so the use cases may be difficult or
time-consuming to answer. However, by using Ricgraph, these
use cases (and many others) are easy to answer.

### Use case for a journalist
As a journalist, I want to find researchers with a certain skill S and their publications, 
so that I can interview them for a newspaper article. 
Example skills can be: *climate change* or *stem cells*.
The items surrounded by the red line are the solution to this use case.

<!-- 
The '{width=...}' in the lines below to include a figure are necessary for 
the documentation generated with Quarto, a.o. for the documentation website.
We will need a width instead of a height to prevent right margin overflows
on small mobile screens.
On GitHub, it will unfortunately show this text.
-->

![Ricgraph use case for a journalist.](images/journalist-use-case.jpg){width=70%}

### Use case for a librarian
As a librarian, I want to enrich my local research information system with research results 
from person A that are in other systems (in orange, *RIS2*) but not in 
ours (in green, *RIS1*), so that we have a more complete view of research at our university. 
The items surrounded by the red line are the solution to this use case.

![Ricgraph use case for a librarian.](images/librarian-use-case.jpg){width=75%}

### Use case for a researcher
As a researcher A, I want to find researchers from other universities that have 
co-authored publications written by the co-authors of my own publications, 
so that I can read their publications to find out if we share common research interests.
The items surrounded by the red line are the solution to this use case.

![Ricgraph use case for a researcher.](images/researcher-use-case.jpg){width=35%}


## Main contributions of Ricgraph

* Ricgraph can store many types of items in a single graph.
* Ricgraph harvests multiple source systems into a single graph.
* Ricgraph Explorer is the exploration tool for Ricgraph.
* Ricgraph facilitates reasoning about items because it infers new relations between items.
* Ricgraph can be tailored for an application area.
* Ricgraph has a REST API to programmatically get items from Ricgraph.


## Installation guide

This section describes how to install both a graph database backend
and Ricgraph on a Linux machine. 
For this, you will need to be able to change to user *root*.
Read more about [installing Ricgraph without the need to be able to change to user
*root*](ricgraph_install_configure.md#fast-and-recommended-way-to-install-ricgraph-for-a-single-user),
or about [installing Ricgraph as a server on 
Linux](ricgraph_as_server.md#fast-and-recommended-way-to-install-ricgraph-as-a-server).

1. [Check the requirements](ricgraph_install_configure.md#requirements-for-ricgraph).
1. Get the most recent Ricgraph Makefile.
   Type as regular user (i.e., be sure you are not user *root*):
   ```
   cd
   wget https://raw.githubusercontent.com/UtrechtUniversity/ricgraph/main/Makefile
   ```
1. Install Neo4j Community Edition. Only for this step you need to be user *root*.
   Type:
   ```
   sudo bash
   make install_enable_neo4j_community
   exit
   ```
   On success, the Makefile will print *installed successfully*.
1. Download and install Ricgraph in your home directory.
   Type as regular user (i.e., be sure you are not user *root*):
   ```
   make install_ricgraph_singleuser_neo4jcommunity
   ```
   On success, the Makefile will print *installed successfully*.
1. For more detail, read 
   [Fast and recommended way to install Ricgraph for a single 
   user](ricgraph_install_configure.md#fast-and-recommended-way-to-install-ricgraph-for-a-single-user).
   This is also a good place to start if you encounter errors.
1. Done.

## Harvesting source systems
To be able to use Ricgraph, you will first need to harvest information.
For some source systems, you need an authentication key. For some others, this is not
necessary. To harvest two source systems in Ricgraph without the need for an
authentication key, type:

```
cd $HOME/ricgraph_venv
make run_batchscript
```
This will harvest
[the data repository Yoda](https://www.uu.nl/en/research/yoda) and
[the Research Software Directory](https://research-software-directory.org).
It will print a lot of output, and it will take a few minutes.
When ready, it will print *Done*.

To read more about harvesting,
see [Ricgraph harvest scripts](ricgraph_harvest_scripts.md#ricgraph-harvest-scripts).


## Browsing using Ricgraph Explorer
Ricgraph provides an exploration tool, so users do
not need to learn a graph query language. This tool is called
_Ricgraph Explorer_.
As it is a Python Flask application, it can be customized as needed.
New queries (buttons) can be added,
or the user interface can
be modified to fit a certain use case, user group, or application area.

Ricgraph Explorer
has several pre-build queries tailored to this application area,
each with its own button, for example:

* find a person, a (sub-)organization, a skill;
* when a person has been found, find its identities, skills, research results.

Ricgraph Explorer offers
[faceted navigation](https://en.wikipedia.org/wiki/Faceted_search).
That means, if a query results in a table with e.g. *journal articles*, *data sets*,
and *software*, you can narrow down on one or more of these categories by
checking or unchecking their corresponding checkbox.
An alternative view
uses [tabbed navigation](https://en.wikipedia.org/wiki/Tab_(interface)).

This section describes some possibilities of Ricgraph Explorer. 
For a more extensive description, read
[Ricgraph Explorer](ricgraph_explorer.md#ricgraph-explorer).

Start Ricgraph Explorer to browse the information harvested:

```
cd $HOME/ricgraph_venv
make run_ricgraph_explorer
```
The Makefile will tell you to go to
your web browser, and go to
[http://127.0.0.1:3030](http://127.0.0.1:3030).


###  A usage flow through Ricgraph Explorer

![Screenshots of a usage flow through Ricgraph Explorer.
Some field values have been blurred for privacy
reasons.](images/ricgraph-explorer-showing-research-results-person.jpg){width=90%}

The figure above shows screenshots of web pages of Ricgraph Explorer for
answering the research question “What are the research results of
person A”.

The screenshot at the top left is the [home page](ricgraph_explorer.md#home-page).
After clicking “search for a person”,
Ricgraph Explorer shows a [search page](ricgraph_explorer.md#search-page) (top right).
A user types a name, and the
[person options page](ricgraph_explorer.md#person-options-page) is shown (bottom
left). After clicking “show research results related to this person”, the
[results page](ricgraph_explorer.md#results-page) is shown (bottom right). In that
page, the rows in the second table are (in this case) the journal article neighbors of
the item in the first table (the
person the user searched). This person also has other types of research results:
book chapters, data sets, other
contributions, books, reviews, and software (cf. row with orange rectangle, this is an
example of the tabbed navigation). The “comment” column contains the titles of
the journal articles. By clicking on an entry in the “value” column, in this case a
DOI value, the user will go to this
neighbor. Ricgraph Explorer will show a page with persons who have contributed to
that journal article.

### Example research questions

In the figure in the previous section,
after a click on a value in the “value” column in the bottom right result
page, the user will get the persons who have contributed to that research
result, as in figure (b) below.

![Example research questions for Ricgraph.](images/examples-of-research-questions-general.jpg){width=90%}

Clicking “find
persons that share any result types with this person” in the bottom left
person option page (in the figure in the previous section) corresponds to figure (c),
and clicking “show personal information related to this person” corresponds to figure (e).

The research question “What are the research results of person A” from
the previous section corresponds to figure (a).


## More information

* Read the full documentation of Ricgraph on 
  [https://docs.ricgraph.eu](https://docs.ricgraph.eu).
* For a gentle introduction in Ricgraph, read the reference publication:
  Rik D.T. Janssen (2024). Ricgraph: A flexible and extensible graph to explore research in
  context from various systems. *SoftwareX*, 26(101736).
  [https://doi.org/10.1016/j.softx.2024.101736](https://doi.org/10.1016/j.softx.2024.101736).
* Read more about
  [publications](ricgraph_pubs_pres_news_use_ment.md#ricgraph-publications),
  [presentations](ricgraph_pubs_pres_news_use_ment.md#ricgraph-presentations),
  [newsletters](ricgraph_pubs_pres_news_use_ment.md#ricgraph-newsletters),
  [projects with students](ricgraph_pubs_pres_news_use_ment.md#ricgraph-projects-with-students),
  [use](ricgraph_pubs_pres_news_use_ment.md#ricgraph-use), and
  [mentions](ricgraph_pubs_pres_news_use_ment.md#ricgraph-mentions)
  of Ricgraph.

## Contact
Ricgraph has been created and is being maintained by
[Rik D.T. Janssen from Utrecht University in the Netherlands](https://www.uu.nl/staff/DTJanssen)
[(ORCID 0000-0001-9510-0802)](https://orcid.org/0000-0001-9510-0802).
You can contact him for presentations, demos and workshops.
