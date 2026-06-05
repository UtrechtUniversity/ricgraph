# Learn more about Ricgraph

Ricgraph has been developed for the application area
[research information](what-is-ricgraph.md#research-information).
It can be used for other application areas that require
relations between items from various source systems.

## What can you do with Ricgraph?

In the menu bar, you can find more information on how to:

* [explore collaborations between (sub-)organizations with
  Ricgraph](collaborations-with-ricgraph.md).
* [explore the open science landscape with Ricgraph](open-science-with-ricgraph.md).
* [enhance research information systems with Ricgraph](enhancing-with-ricgraph.md).

Below, you will find more 
[use cases](#use-cases) and 
[example research questions](#example-research-questions).

## Use cases

### Use case for a journalist
As a journalist, I want to find researchers with a certain skill S and their publications,
so that I can interview them for a newspaper article.
Example skills can be: *climate change* or *stem cells*.
The items surrounded by the red line are the solution to this use case.

<img src="images/journalist-use-case.jpg" alt="Ricgraph use case for a journalist." width="70%">

### Use case for a librarian
As a librarian, I want to enrich my local research information system with research results
from person A that are in other systems (in orange, *RIS2*) but not in
ours (in green, *RIS1*), so that we have a more complete view of research at our university.
The items surrounded by the red line are the solution to this use case.

<img src="images/librarian-use-case.jpg" alt="Ricgraph use case for a librarian." width="75%"> 

### Use case for a researcher
As a researcher A, I want to find researchers from other universities that have
co-authored publications written by the co-authors of my own publications,
so that I can read their publications to find out if we share common research interests.
The items surrounded by the red line are the solution to this use case.

<img src="images/researcher-use-case.jpg" alt="Ricgraph use case for a researcher." width="35%">


## Example research questions

<img src="images/examples-of-research-questions-general.jpg" alt="Example research questions for Ricgraph." width="90%">

This figure shows eight example 
research questions that can be answered using Ricgraph:

* Figure a: What are the research results of person *A*?
* Figure b: Who has contributed to research result *R*?
* Figure c: With whom shares person *A* research results?
* Figure d: What research results have person *A* and person *B* in common?
* Figure e: What identifiers does a person *A* have 
* Figure f: What is common between *organization 1* and *organization 2*
  (e.g. persons, research results)?
* Figure g: How are persons *A* and *B* related?
* Figure h: With what universities (U) and departments of universities
  (U-D) does person *A* collaborate?

## Read more about Ricgraph

There are several places where you can start reading about Ricgraph:

* For a gentle introduction in Ricgraph, please read the reference publication:
  Rik D.T. Janssen (2024). *Ricgraph: A flexible and extensible graph to explore
  research in context from various systems*. SoftwareX, 26(101736).
  [https://doi.org/10.1016/j.softx.2024.101736](https://doi.org/10.1016/j.softx.2024.101736).
* We also have an article about collaborations and Ricgraph:
  Rik D.T. Janssen (2025).
  *Utilizing Ricgraph to gain insights into research collaborations across institutions,
  at every organizational level*. [preprint].
  [https://doi.org/10.2139/ssrn.5524439](https://doi.org/10.2139/ssrn.5524439).
* Play the [Ricgraph use cases video](https://docs.ricgraph.eu/docs/videos/ricgraph_usecases.mp4), or the
  [Ricgraph introduction video](https://docs.ricgraph.eu/docs/videos/ricgraph_intro_usecases.mp4).
* You can read the general presentation about Ricgraph, presenting Ricgraph in
  a visual   manner:
  [https://doi.org/10.5281/zenodo.12634234](https://doi.org/10.5281/zenodo.12634234).
* You can read the presentation explaining how to enrich the [Research
  Information System Pure](https://www.elsevier.com/solutions/pure)
  (and other source systems) using Ricgraph
  and [BackToPure](https://github.com/UtrechtUniversity/BackToPure):
  [https://doi.org/10.5281/zenodo.12634658](https://doi.org/10.5281/zenodo.12634658).
  This presentation explains that after harvesting several Pures
  (from different institutions)  and other source systems,
  such as [OpenAlex](https://openalex.org),
  one can enrich its own Pure _A_ by using information in other source
  systems, not present in one's own Pure _A_.
* Extensive documentation can be found on the
  [Ricgraph documentation website](https://docs.ricgraph.eu).
* Source code can be found
  in the [GitHub
  repository](https://github.com/UtrechtUniversity/ricgraph).
* Explore the Ricgraph outreach activities:
  [publications](https://docs.ricgraph.eu/docs/ricgraph_outreach.html#ricgraph-publications),
  [presentations](https://docs.ricgraph.eu/docs/ricgraph_outreach.html#ricgraph-presentations),
  [newsletters](https://docs.ricgraph.eu/docs/ricgraph_outreach.html#ricgraph-newsletters)
  (to subscribe, go to [Ricgraph
  Contact](contact.md)),
  [projects with students](https://docs.ricgraph.eu/docs/ricgraph_outreach.html#ricgraph-projects-with-students),
  [use](https://docs.ricgraph.eu/docs/ricgraph_outreach.html#ricgraph-use), and
  [mentions](https://docs.ricgraph.eu/docs/ricgraph_outreach.html#ricgraph-mentions)
  of Ricgraph.

## Install and use Ricgraph

You can use Ricgraph by going to the [Pilot project
Open Ricgraph demo server](pilot-project-open-ricgraph-demo-server.md).
Then you don't need to install anything.

You can install Ricgraph on your own computer or server,
and use it with the default sources, or with
your own sources.
Doing this has the advantage that you can modify Ricgraph so it suits your
needs. Please let me know if you create something that may benefit
other users, so I can add it to Ricgraph.

Please follow these steps (for more details go to
the [Ricgraph documentation website](https://docs.ricgraph.eu)):

* [Install and configure Ricgraph](https://docs.ricgraph.eu/docs/ricgraph_install_configure.html#install-and-configure-ricgraph).
  That page also describes how to harvest research information.
* Use [Ricgraph Explorer](https://docs.ricgraph.eu/docs/ricgraph_explorer.html#ricgraph-explorer),
  the exploration tool for Ricgraph. 
* Use the [Ricgraph REST API](https://docs.ricgraph.eu/docs/ricgraph_restapi.html#ricgraph-rest-api),
  the REST API for Ricgraph.

You can also download Ricgraph directly from the
[Ricgraph GitHub repository](https://github.com/UtrechtUniversity/ricgraph).

## Next steps
Go to the [Contact page](contact.md).
