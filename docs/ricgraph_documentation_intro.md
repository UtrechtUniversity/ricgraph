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

Throughout this documentation, we illustrate how Ricgraph works by applying
it to the application area research information.

## Ricgraph news

Read my recent preprint:

* Rik D.T. Janssen (2025).
  *Utilizing Ricgraph to gain insights into research collaborations across institutions,
  at every organizational level*. Submitted to SoftwareX [preprint].
  [https://doi.org/10.2139/ssrn.5524439](https://doi.org/10.2139/ssrn.5524439).

See Ricgraph in action:

* Use the Open Ricgraph demo server
  via [https://explorer.ricgraph.eu](https://explorer.ricgraph.eu).
  Read more (and join) at
  [pilot project Open Ricgraph demo
  server](https://www.ricgraph.eu/pilot-project-open-ricgraph-demo-server.html).


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
* A project with six students from the University of Applied Sciences, Utrecht, that aims to
  [create a general harvester for
  Ricgraph](ricgraph_outreach.md#ricgraph-projects-with-students).
  It will remove a lot of code duplication in the harvest scripts, and will
  make it easier to add new harvest sources.
  Status: planning stage (pre-alpha).
* A project with a student from the University of Applied Sciences, Utrecht, that aims to use
  [AI and Large Language Models to find topics and visualize large amounts of research
  information](ricgraph_outreach.md#ricgraph-projects-with-students).
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

He is also very interested in working together on projects involving Ricgraph.
Ricgraph is a flexible platform that brings
together information from multiple systems into a single graph.
It allows users to analyze this information and explore how it relates
to other types of information.
We could work together on use cases applying Ricgraph to
research information, such as exploring collaborations or
analyzing how people or organizations contribute to research results.
We could also explore entirely different domains.
Any application that involves representing and analyzing
interconnected information as nodes and relations in a graph,
regardless of the field, is of interest.
