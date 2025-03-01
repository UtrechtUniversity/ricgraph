# Learn more about Ricgraph

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

Also, more elaborate information can be found using Ricgraph and
[Ricgraph Explorer](https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_explorer.md), the
exploration tool for Ricgraph:

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

With Ricgraph, you can get metadata from objects from any source system you’d
like.  You run the harvest script for that
system, and data will be imported in Ricgraph and will be
combined automatically with data which is already there.
Ricgraph provides harvest scripts for the systems mentioned above.
Scripts for other sources can be written easily.

## More information
You might want to continue reading at 
[Read more about Ricgraph](read-more-about-ricgraph.md), 
or to [Get Ricgraph](get-ricgraph.md).
