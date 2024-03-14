## Ricgraph Explorer

Ricgraph provides an exploration tool, so users do 
not need to learn a graph query language. This tool is called
_Ricgraph Explorer_. 
It can be customized as needed for
a certain application area (it is a Python Flask application).
In this documentation, we use the application area _research information_.
You can modify it if you use
Ricgraph in a different application area, if you need different queries,
or if you would like to have a different user interface.
The code for *Ricgraph Explorer* can be found in
  directory [ricgraph_explorer](../ricgraph_explorer).

Ricgraph Explorer 
has several pre-build queries tailored to the application area 
research information, each with its own button, for example:
* find a person, a (sub-)organization, a skill;
* when a person has been found, find its identities, skills, research results.

Ricgraph Explorer also offers
[Faceted navigation](https://en.wikipedia.org/wiki/Faceted_search).
That means, if a query results in a table with e.g. *journal articles*, *data sets*,
and *software*, you can narrow down on one or more of these categories by
checking or unchecking their corresponding checkbox.

This page describes what you can do with Ricgraph Explorer. It does this
by showing the flow through the web application by listing the buttons available. 
The text below lists
these buttons. For some of these buttons, a more extensive description is given.
After clicking a few buttons, and entering values in the fields
provided, the user will get a Results page. Since there are many possible result
pages, we only show one as example.

On this page, you can learn more about:
* Read about [how to start_Ricgraph Explorer](#how-to-start-ricgraph-explorer).
* The [Home page](#home-page) of Ricgraph Explorer.
* The [Person options page](#person-options-page) of Ricgraph Explorer.
* The [Organization options page](#organization-options-page) of Ricgraph Explorer.
* The [Results page](#results-page) of Ricgraph Explorer.
* Read about [browsing Ricgraph](#browsing-ricgraph).

[Return to main README.md file](../README.md).

### How to start Ricgraph Explorer

Depending on how Ricgraph has been installed, there are various ways to start it.
* If you have installed Ricgraph yourself, using your own user id,
  you have to follow the following steps:
  * [Start Neo4j Desktop](ricgraph_query_visualize.md#start-neo4j-desktop).
  * Run the *ricgraph_explorer.py* script in directory [ricgraph_explorer](../ricgraph_explorer).
     It will tell you which weblink and port to use, probably
     http://127.0.0.1:3030. Open a web browser and go to that link.
* If you use Ricgraph on a demo server, and you have used your own user id to log on to that server,
  you very probably do not need to start Neo4j.
  * Open a web browser and go to http://127.0.0.1:3030.
* If you have a domain name to access Ricgraph, for example _www.ricgraph-example.com_:
  * Open a web browser and go to https://www.ricgraph-example.com.

### Home page

The figure below shows part of the home page.
Click on it to enlarge.

<img src="images/ricgraph_explorer_home_page.jpg" width="400">

The home page lets the user choose between various methods to explore Ricgraph:
* Button _search for a person_.
  * in the webpage that is shown after you have clicked this button, 
    to search, type a full name or substring of a name.
  * if there is more than one result, select one person.
  * this person is shown on the [person options page](#person-options-page)
    for further exploration.
* Button _search for a (sub-)organization_. 
  * in the webpage that is shown after you have clicked this button, 
    to search, type a full organization name or substring of an organization name.
  * if there is more than one result, select one organization.
  * this organization is shown on the [organization options page](#organization-options-page)
    for further exploration.
* Button _search for a skill, expertise area or research area_
  [only available if you have nodes of category _competence_ in Ricgraph]:
  * in the webpage that is shown after you have clicked this button, 
    to search, type a skill, expertise area or research area, or
    substring of one of these.
  * if there is more than one result, select one.
  * the results are shown on the [results page](#results-page).
* Button _search for anything (broad search)_ or
  button _advanced search_.
  * in the webpage that is shown after you have clicked this button, 
    type something to search, the advanced search is a 
    case-sensitive exact match search 
    on one or more of the Ricgraph fields _name_, _category_, or _value_.
  * if there is more than one result, select one.
  * depending on the type of result:
    * if the result is a person, 
      the result is shown on the [person options page](#person-options-page)
      for further exploration.
    * if the result is an organization, 
      the result is shown on the [organization options page](#organization-options-page)
      for further exploration.
    * for all other results,
      the results are shown on the [results page](#results-page).

### Person options page
You only get on this page if the result of your search is a person.
The figure below shows the person options page. Click on it to enlarge.

<img src="images/ricgraph_explorer_personoptions_page.jpg" width="400">

You can use one of these exploration options:
* Button _show personal information related to this person_.
* Button _show organizations related to this person_.
* Button _show research results related to this person_.
* Button _show everything except identities related to this person_.
* Button _show all information related to this person_.
* Button _find persons that share any research result types with this person_.
* Button _find persons that share a specific research result type with this person_.
  
  You will need to enter a research result type from a drop-down list.
* Button _find organizations that this person collaborates with_.
  
  This button gives an overview of organizations that this person collaborates with. 
  A person _X_ from organization _A_ collaborates with a person _Y_ from 
  organization _B_ if _X_ and _Y_ have both contributed to the same research result.
* Button _find information harvested from other source systems,
  not present in this source system_.

  You will need to enter a source system from a drop-down list.
  Next, this button gives an overview
  of information that can be added to the source system entered, based on the information
  harvested from other source systems.
  The process of improving or enhancing information in a source system is called "enriching" 
  that source system. This is only possible if you have harvested more than one source 
  system. 
* Button _find the overlap in source systems for the neighbor nodes of this node_.
  
  In case more than one source systems have been harvested, and the information 
  in Ricgraph for the neighbors of this node have originated from more than 
  one source system, clicking this button will show you from which ones.
    
For each of these buttons, the results are shown on the [results page](#results-page).

### Organization options page
You only get on this page if the result of your search is an organization.
The figure below shows the organization options page. Click on it to enlarge.

<img src="images/ricgraph_explorer_organizationoptions_page.jpg" width="400">

You can use one of these buttons:
* Button _show persons related to this organization_.
* Button _show all information related to this organization_.
* Button _find research results from all persons in this organization_.
* Button _find skills from all persons in this organization_.
* Button _find any information from persons or their results in this organization_.
* Button _find specific information_.

  You will need to enter a value for Ricgraph fields _name_ or _category_
  from a drop-down list.
  Next, this button gives an overview of the persons or their results in 
  this organization.

For all of these buttons the results are shown on the [results page](#results-page).

### Results page
The results page will look different depending on what results are shown.
The figure below shows an example of a part of the skills in an organization.
Click on it to enlarge.

<img src="images/ricgraph_explorer_result_page.jpg" width="400">

### Browsing Ricgraph
You can browse the graph that Ricgraph has obtained by harvesting source systems
by clicking on a value in the _value_ column. 
In the figure in section [Results page](#results-page), 
the search was started with organization _Utrecht University_
(in the first table). 
The _SKILL_ neighbors of _Utrecht University_ are listed in the second table.
By clicking on e.g. _NVivo_, you will traverse to the _NVivo_ node,
and you will see the neighbors of this node. This can be repeated as desired.
It is also possible to start a new search using the buttons _Home_, _Advanced search_,
or _Broad search_ in the yellow title bar.

### Return to main README.md file
[Return to main README.md file](../README.md).

