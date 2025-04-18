# Documentation Ricgraph - Research in context graph

## What is Ricgraph?

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

Currently, there are people working on the following extensions for Ricgraph:

* [BackToPure](https://github.com/UtrechtUniversity/backtopure)
  is a tool designed to enhance an organization's
  [Research Information System Pure](https://www.elsevier.com/solutions/pure)
  by enriching its content. BackToPure can identify items
  (such as publications, data sets or software)
  that exist in other external sources but are missing from the organization's Pure,
  and then insert (enrich) those items into Pure.
  The result is a more complete overview of research at that organization.
  Status: experimental stage (beta).
* A chatbot that allows you to "talk" to Ricgraph. You can formulate questions in
  plain English, such as "Please give me the research results of the Geosciences
  faculty of Utrecht University?"
  or "With what organizations does that faculty collaborate?".
  It uses a local Large Language Model.
  Status: planning stage (pre-alpha).
* A project that uses
  [AI and Large Language Models to cluster and visualize large amounts of research
  information](https://docs.ricgraph.eu/docs/ricgraph_pubs_pres_news_use_ment.html#ricgraph-projects-with-students).
  It assigns *topics* to publications,
  data sets, and software. By selecting a number of topics, research results are
  grouped, and possibly experts on these topics can be found.
  Status: planning stage (pre-alpha).
* A tool that helps Pure administrators to clean up "external organizations" in Pure.
  Status: planning stage (pre-alpha).

## What to find on the Documentation website for Ricgraph?

This documentation website offers quite a bit of information about Ricgraph.
In the yellow sidebar you can find the various options.
Basically, you can read the Ricgraph tutorial, 
or browse through the full documentation:

* Ricgraph tutorial:
  * Read the [tutorial on this webpage](ricgraph_tutorial.md#tutorial-ricgraph---research-in-context-graph).
  * Read the [tutorial as pdf](https://docs.ricgraph.eu/ricgraph_tutorial.pdf).
* Full documentation:
  * Start reading at the [Ricgraph README](../README.md#ricgraph---research-in-context-graph).
  * Choose something from the documentation tree in the yellow sidebar.
  * Use the search box.
  * Of course, every webpage has links that allow you to go to other sections
    or webpages.
  * Read the [full documentation as pdf](https://docs.ricgraph.eu/ricgraph_fulldocumentation.pdf).
    This pdf is the concatenation of all Ricgraph documentation pages in one pdf.

This website has been generated from the
[Ricgraph GitHub](https://github.com/UtrechtUniversity/ricgraph) documentation.

## Contact

Ricgraph has been created and is being maintained by
Rik D.T. Janssen from Utrecht University in the Netherlands.
You can find contact details at
[his Utrecht University employee page](https://www.uu.nl/staff/DTJanssen).
He also has an ORCID profile on
[ORCID 0000-0001-9510-0802](https://orcid.org/0000-0001-9510-0802).
You can contact him for presentations, demos and workshops.

He is also very interested in collaborating on projects involving Ricgraph.
Ricgraph is a flexible platform that brings
together information from multiple systems into a single graph,
allowing users to explore and analyze this information and their relationships.
Collaborations could focus on applying Ricgraph to
research information, such as exploring collaborations
and contributions, or analyzing networks.
They could also explore entirely different domains.
Any application that involves representing and analyzing
interconnected information as nodes and relationships in a graph,
regardless of the field, is of interest
