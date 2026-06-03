# Learn more about Ricgraph

## What can you do with Ricgraph?

Ricgraph can answer questions like:

* Which researcher has contributed to which publication, dataset, 
  software package, project, etc.?
* Given e.g. a dataset, software package, or project, who has contributed to it?
* What identifiers does a researcher have 
  (e.g. [ORCID](https://en.wikipedia.org/wiki/ORCID),
  [ISNI](https://en.wikipedia.org/wiki/International_Standard_Name_Identifier),   organization employee ID, email address)?
* What skills does a researcher have?
* Show a network of researchers who have worked together?
* Which organizations have worked together?

You can also:

* [explore collaborations between (sub-)organizations with
  Ricgraph](collaborations-with-ricgraph.md).
* [explore the open science landscape with Ricgraph](open-science-with-ricgraph.md).
* [enhance research information systems with Ricgraph](enhancing-with-ricgraph.md).

Also, more elaborate information can be found using Ricgraph and
[Ricgraph Explorer](https://docs.ricgraph.eu/docs/ricgraph_explorer.html#ricgraph-explorer),
the exploration tool for Ricgraph:

* You can find information about persons or their results in a
  (sub-)organization (unit, department, faculty, university).
  For example, you can find out what data sets or software are produced in your
  faculty. Or the skills of all persons in your department. Of course this is
  only possible in case you have harvested them.
* You can find out with whom a person shares research output types.
  For example, you can find out with whom someone shares software or data sets.
* You can get tables showing how you can enrich a source system based on other
  systems you have harvested. For example, suppose you have harvested both the
  [Research Information System Pure](https://www.elsevier.com/solutions/pure)
  and [OpenAlex](https://openalex.org), using this feature you can find out
  which publications in OpenAlex are not in Pure. You might want to add those
  to Pure.
* You can get a table that shows the overlap in harvests from different source
  systems.
  For example, after a query to show all ORCID nodes,
  the table summarizes the number of ORCID nodes which were
  only found in one source, and which were found in multiple sources.
  Another table gives a detailed overview how many
  nodes originate from which different source systems. Then, you can 
  drill down by
  clicking on a number in one of these
  two tables to find the nodes corresponding to that number.

If you would like to get this information programmatically, you can use
the [Ricgraph REST API](https://docs.ricgraph.eu/docs/ricgraph_restapi.html#ricgraph-rest-api).

With Ricgraph, you can get metadata from objects from any source system you’d
like.  You run the harvest script for that
system, and data will be imported in Ricgraph and will be
combined automatically with data which is already there.
Ricgraph provides harvest scripts for the systems mentioned above.
Scripts for other sources can be written easily.

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
* Explore
  [publications](https://docs.ricgraph.eu/docs/ricgraph_outreach.html#ricgraph-publications),
  [presentations](https://docs.ricgraph.eu/docs/ricgraph_outreach.html#ricgraph-presentations),
  [newsletters](https://docs.ricgraph.eu/docs/ricgraph_outreach.html#ricgraph-newsletters)
  (to subscribe, go to [Ricgraph
  Contact](contact.md)),
  [projects with students](https://docs.ricgraph.eu/docs/ricgraph_outreach.html#ricgraph-projects-with-students),
  [use](https://docs.ricgraph.eu/docs/ricgraph_outreach.html#ricgraph-use), and
  [mentions](https://docs.ricgraph.eu/docs/ricgraph_outreach.html#ricgraph-mentions)
  of Ricgraph.


## Download Ricgraph

To download Ricgraph, go to the 
[Ricgraph GitHub repository](https://github.com/UtrechtUniversity/ricgraph).


## Install and use Ricgraph

You can [use Ricgraph by going to the Pilot project
Open Ricgraph demo server](pilot-project-open-ricgraph-demo-server.md).
Then you don't need to install anything.

You can install and use Ricgraph with the default sources, or with
your own sources.
Doing this has the advantage that you can modify Ricgraph so it suits your
needs. Please let me know if you create something that may benefit
other users, so I can add it to Ricgraph.

Please follow these steps (for more details go to
the [Ricgraph documentation website](https://docs.ricgraph.eu)):

* [Install and configure Ricgraph](https://docs.ricgraph.eu/docs/ricgraph_install_configure.html#install-and-configure-ricgraph).
* Start harvesting data, see [Ricgraph harvest scripts](https://docs.ricgraph.eu/docs/ricgraph_harvest_scripts.html#ricgraph-harvest-scripts).
  If you would like to start with a default demo data set, read
  [Demo harvest script (multiple_harvest_demo)](https://docs.ricgraph.eu/docs/ricgraph_harvest_scripts.html#demo-harvest-script-multiple_harvest_demo).
* Use [Ricgraph Explorer](https://docs.ricgraph.eu/docs/ricgraph_explorer.html#ricgraph-explorer),
  the exploration tool for Ricgraph. 
* Use the [Ricgraph REST API](https://docs.ricgraph.eu/docs/ricgraph_restapi.html#ricgraph-rest-api),
  the REST API for Ricgraph.

## Next steps
Go to the [Contact page](contact.md).
