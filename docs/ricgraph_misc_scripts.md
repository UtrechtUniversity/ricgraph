# Ricgraph miscellaneous scripts

Ricgraph scripts can be found in various places:
* Directory [harvest_to_ricgraph_examples](../harvest_to_ricgraph_examples): 
  scripts for harvesting sources and inserting the results in Ricgraph.
  [Documentation for these scripts](ricgraph_harvest_scripts.md).
* Directory [export_ricgraph_examples](../export_ricgraph_examples):
  scripts to export items from Ricgraph.
  [Documentation for these scripts](ricgraph_misc_scripts.md) (this file).
* Directory [find_enrich_ricgraph_examples](../find_enrich_ricgraph_examples):
  scripts for finding and enriching items from Ricgraph.
  [Documentation for these scripts](ricgraph_misc_scripts.md) (this file).
* The module code *ricgraph.py* can be found in 
  directory [ricgraph](../ricgraph). 
* The code for *Ricgraph Explorer* can be found in
  directory [ricgraph_explorer](../ricgraph_explorer). 
* [Documentation for writing your own scripts](ricgraph_script_writing.md).

All code is documented and hints to use it can be found in the source files.

[Return to main README.md file](../README.md).

## Count the number of organizations that contributed to a category
To count the number of organizations that contributed to a category, 
use the script *count_organizations_contributed_to_category.py*.
You can find this script 
in the directory [export_ricgraph_examples](../export_ricgraph_examples).

This script 
counts the (sub-)organizations of persons who have contributed to all nodes of a
specified category (e.g., *data set* or *software*).
Both a histogram and a collaboration table will be
computed and written to a file.
The histogram contains the count of (sub-)organizations of all nodes of the
specified category.
The collaboration table contains the count of (sub-)organizations who have worked
together on all nodes of the specified category.

What makes this script interesting, is that it also counts collaborations of
sub-organizations, if you have harvested them. For example, the Research 
Information System Pure contains a full organization hierarchy for persons.
After harvesting Pure, Ricgraph contains this organization hierarchy. 
That is, not only the top level organization, such as *Utrecht University*, 
but also faculties, departments, units, and chairs.
Using these sub-organizations, this script is able to show collaborations 
between e.g. different departments in the same organization. 
In case you have harvested
organization hierarchies from different organizations, collaborations between e.g.
departments of two universities can be shown.


```
Usage
count_organizations_contributed_to_category.py [options]

Options:
  --sort_organization <organization name>
          Sort the collaboration table on this organization name.
          If the name has one or more spaces, enclose it with "...".
          If this option is not present, the script will prompt the user
          for a name.
  --category <category>
          Compute histogram and collaboration table for given category.
          If the name has one or more spaces, enclose it with "...".
          If this option is not present, the script will prompt the user
          for a name.
```


## Export nodes to a file
There are two scripts which allow to export *person* nodes to a csv file. These can be
found in the directory [export_ricgraph_examples](../export_ricgraph_examples).
* *export_person_identifiers.py*: exports
  all [person identifiers](ricgraph_details.md#person-identifiers)
  connected to a *person-root* node.
* *export_person_node_properties.py*: exports
  all [node properties](ricgraph_details.md#properties-of-nodes-in-ricgraph)
  for every *person* node connected to a *person-root* node.

Use the parameter *EXPORT_MAX_RECS* for the number of records to export and
*EXPORT_FILENAME* for the filename to export at the start of both scripts.


## Script to enrich persons
With the script *enrich_orcids_scopusids.py*, 
you can enrich persons having an ORCID but no SCOPUS_AUTHOR_ID
(using OpenAlex), or vice versa (using the Scopus API). Note that Scopus has 
a rate limit, and that 
you have to set some parameters in *ricgraph.ini*.
You can find this script in the directory 
[find_enrich_ricgraph_examples](../find_enrich_ricgraph_examples).


## Script to find person identifiers pointing to different persons
With the script *find_double_pids.py*, you can check if 
there are any personal identifiers that are
pointing to two or more different persons.
You can find this script in the directory
[find_enrich_ricgraph_examples](../find_enrich_ricgraph_examples).


## Return to main README.md file

[Return to main README.md file](../README.md).

