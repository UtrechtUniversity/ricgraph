## Future work

* Create a more sophisticated end user web interface. This interface should allow
  easy browsing of Ricgraph. 
* Modify Ricgraph to allow the use of another, preferably open source graph database engine.
  It should be possible by changing minor bits of the code in file *ricgraph.py*.
* Make a web service of Ricgraph.
* Write harvesting scripts to get information from e.g. [Zenodo](https://zenodo.org),
  [ORCID](https://orcid.org), ~~[OpenAlex](https://openalex.org)~~, 
  [Scopus](https://www.scopus.com), [Lens](https://www.lens.org),
  [OpenAIRE](https://explore.openaire.eu), 
  [DataCite Commons](https://commons.datacite.org), 
  [GitHub](https://github.com) (and other Gits), etc.  
* Function `merge_two_personroot_nodes()` in *ricgraph.py* now uses `_graph.delete()`
  from *py2neo*, but that call has the side effect of removing nodes with more than one edge, 
  e.g. the organization nodes in *harvest_uustaffpages_to_ricgraph.py* 
  (after the call to `rcg.merge_personroots_of_two_nodes()` 
  and then `merge_two_personroot_nodes()`
  there is only one organization node left).
  It should use `_graph.separate()`, but the author did not get it working.

[Return to main README.md file](../README.md).
