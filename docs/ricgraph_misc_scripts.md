# Ricgraph miscellaneous scripts

This page describes scripts for 
importing and exporting items from
Ricgraph, about
scripts to enhance (deleting personal data, renaming (sub-)organizations, etc.) 
information in
Ricgraph, and about Ricgraph maintenance scripts.
Read more about [scripts for harvesting sources and inserting the results in
Ricgraph](ricgraph_harvest_scripts.md#ricgraph-harvest-scripts),
or about
[writing your own scripts](ricgraph_script_writing.md#ricgraph-script-writing).

On this page, you can find:

* Script for collaborations between (sub-)organizations ((directory *enhance*):
* Scripts for importing and exporting (directory *import_export*):
  * [Construct a Ricgraph from a csv file (construct_ricgraph_from_csv)](#construct-a-ricgraph-from-a-csv-file-construct_ricgraph_from_csv)
  * [Import nodes and edges from a csv file, raw version (ricgraph_import_raw_from_csv)](#import-nodes-and-edges-from-a-csv-file-raw-version-ricgraph_import_raw_from_csv)
  * [Export nodes and edges to a csv file, raw version (ricgraph_export_raw_to_csv)](#export-nodes-and-edges-to-a-csv-file-raw-version-ricgraph_export_raw_to_csv)
  * [Count the number of organizations that contributed to a category (count_organizations_contributed_to_category)](#count-the-number-of-organizations-that-contributed-to-a-category-count_organizations_contributed_to_category)
  * [Export nodes to a file (export_person_identifiers and export_person_node_properties)](#export-nodes-to-a-file-export_person_identifiers-and-export_person_node_properties)
* Scripts to enhance (finding, enriching, etc.) information (directory *enhance*):
  * [Delete personal data from Ricgraph (delete_personal_data)](#delete-personal-data-from-ricgraph-delete_personal_data)
  * [Rename (sub-)organizations in Ricgraph (rename_organizations)](#rename-sub-organizations-in-ricgraph-rename_organizations)
  * [Script to enrich persons (enrich_orcids_scopusids)](#script-to-enrich-persons-enrich_orcids_scopusids)
  * [Script to find person identifiers pointing to different persons (find_double_pids)](#script-to-find-person-identifiers-pointing-to-different-persons-find_double_pids)
* Ricgraph maintenance scripts (directory *maintenance*): 
  * [Create a table of contents of the Ricgraph documentation (create_toc_documentation)](#create-a-table-of-contents-of-the-ricgraph-documentation-create_toc_documentation)
  * [Create an index of the Ricgraph documentation (create_index_documentation)](#create-an-index-of-the-ricgraph-documentation-create_index_documentation)
  * [Create the Ricgraph REST API documentation (convert_openapi_to_mddoc)](#create-the-ricgraph-rest-api-documentation-convert_openapi_to_mddoc)

All code is documented and hints to use it can be found in the source files.

[Return to main README.md file](../README.md#ricgraph---research-in-context-graph).


## Find (sub-)organization collaborations (organization_collaborations_batch.csv)
This script collects collaborations within and between (sub-)organizations
in Ricgraph. You can choose between two types of diagrams: 
[Chord diagrams](https://en.wikipedia.org/wiki/Chord_diagram_(information_visualization))
and [Sankey diagrams](https://en.wikipedia.org/wiki/Sankey_diagram).
The script is a batch example script, so you can adapt it for your own situation by
writing the exact function calls to obtain the collaborations.
To be able to use this script, it is necessary to have
organization hierarchies. If you don't have these, you can still use it,
but you will only be able to get collaborations between top-level organizations.

This script assumes organization hierarchies for:

* Utrecht University, the Netherlands - UU;
* Vrije Universiteit Amsterdam, the Netherlands - VUA;
* Delft University of Technology, the Netherlands - DUT.

If you have these, and run this script, you will get organization
collaborations between:

* UU Faculty and VUA Faculty, in a Sankey diagram;
* UU Faculty, VUA Faculty, and DUT Faculty, in a Chord diagram;
* UU Faculty and UU Faculty, in a Sankey diagram.

For more information about collaborations and Ricgraph (including
the diagrams above), please read
Rik D.T. Janssen (2025).
*Utilizing Ricgraph to gain insights into research collaborations across institutions,
at every organizational level*. [preprint].
[https://doi.org/10.2139/ssrn.5524439](https://doi.org/10.2139/ssrn.5524439).

```
Usage:
organization_collaborations_batch.py

Options:
  No command line options.
```

For this script to work, copy it to directory *../ricgraph_explorer*.
Then run it in that directory.


## Construct a Ricgraph from a csv file (construct_ricgraph_from_csv)
To construct a Ricgraph from a csv file,
use the script *construct_ricgraph_from_csv.py*.
You can find this script in the directory *import_export*.

Nodes and edges are inserted with Ricgraph calls. That means,
that nodes are inserted in pairs connected by an edge. 
*Person-root* nodes cannot be inserted
with this script, they will be created whenever necessary. 
If a node in the nodes import file is not connected to another
node by an edge in de the edge import file, 
it will not be created. This is due to the way Ricgraph works.

This script is different compared to
[Import nodes and edges from a csv file,
raw version](#import-nodes-and-edges-from-a-csv-file-raw-version-ricgraph_import_raw_from_csv)
and
[Export nodes and edges to a csv file,
raw version](#export-nodes-and-edges-to-a-csv-file-raw-version-ricgraph_export_raw_to_csv),
since the "raw" scripts import and export with Cypher queries.

```
Usage:
construct_ricgraph_from_csv.py [options]

Options:
  --empty_ricgraph <yes|no>
          'yes': Ricgraph will be emptied before importing.
          'no': Ricgraph will not be emptied before importing.
          If this option is not present, the script will prompt the user
          what to do.
  --filename <filename>
          Import nodes and edges from a csv file starting with <filename>.
          The file with nodes is <filename>-nodes.csv.
          The file with edges is <filename>-edges.csv.
```

The import file containing nodes should be a csv file. At least the following columns should be
present:

* name
* category
* value

Other fields that may be present:

* All fields in parameter *ricgraph_properties_additional* in the
  [Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file),
  but not the fields *source_event* and *history_event*.

The import file containing edges should be a csv file containing exactly four columns:

* name_from, value_from: the from node for the edge.
* name_to, value_to: the to node for the edge.


## Import nodes and edges from a csv file, raw version (ricgraph_import_raw_from_csv)
To import nodes and edges from a csv file,
use the script *ricgraph_import_raw_from_csv.py*.
You can find this script in the directory *import_export*.

This is a "raw" import, because *person-root* nodes are also imported, as
are the connections between e.g. an *ORCID* node and its *person-root* node.
When you do the import, all nodes and edges
will be inserted directly in the graph database backend using a Cypher
query. That means that no checking is done at all if the resulting nodes
and edges conform to the "Ricgraph model". This may result in a graph
not consistent with the Ricgraph model. Due to this, Ricgraph Explorer
may not work as expected.

This script forms a pair with
[Export nodes and edges to a csv file,
raw version](#export-nodes-and-edges-to-a-csv-file-raw-version-ricgraph_export_raw_to_csv).
```
Usage:
ricgraph_import_raw_from_csv.py [options]

Options:
  --empty_ricgraph <yes|no>
          'yes': Ricgraph will be emptied before importing.
          'no': Ricgraph will not be emptied before importing.
          If this option is not present, the script will prompt the user
          what to do.
  --filename <filename>
          Import nodes and edges from a csv file starting with <filename>.
          The file with nodes is <filename>-nodes.csv.
          The file with edges is <filename>-edges.csv.
```

The import file containing nodes should be a csv file. At least the following columns should be
present:

* name
* category
* value
* _key

Other fields that may be present:

* The remaining fields in parameter *ricgraph_properties_hidden* in the
  [Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file).
* The fields in parameter *ricgraph_properties_additional* in the
  [Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file).

The import file containing edges should be a csv file containing exactly four columns:

* name_from, value_from: the from node for the edge.
* name_to, value_to: the to node for the edge.

For an example import file, export the nodes and edges in Ricgraph using
[Export nodes and edges to a csv file,
raw version](#export-nodes-and-edges-to-a-csv-file-raw-version-ricgraph_export_raw_to_csv).


## Export nodes and edges to a csv file, raw version (ricgraph_export_raw_to_csv)
To export nodes and edges to a csv file,
use the script *ricgraph_export_raw_to_csv.py*.
You can find this script in the directory *import_export*.

This is a "raw" export, because person-root nodes are also exported, as
are the connections between e.g. an ORCID node and its person-root node.
The export is done using a Cypher query. 
When you import the export generated by this script, all nodes and edges
will be inserted directly in the graph database backend using a Cypher
query. That means that no checking is done at all if the resulting nodes
and edges conform to the "Ricgraph model". This may result in a graph
not consistent with the Ricgraph model. Due to this, Ricgraph Explorer
may not work as expected.

This script forms a pair with 
[Import nodes and edges from a csv file,
raw version](#import-nodes-and-edges-from-a-csv-file-raw-version-ricgraph_import_raw_from_csv).

```
Usage:
ricgraph_export_raw_to_csv.py [options]

Options:
  --filename <filename>
          Export all nodes and edges in Ricgraph
          to a csv file starting with <filename>.
          The file with nodes is <filename>-nodes.csv.
          The file with edges is <filename>-edges.csv.
```

The export file containing nodes will be a csv file. All fields in Ricgraph will be exported.

The export file containing edges will be a csv file containing exactly four columns:

* name_from, value_from: the from node for the edge.
* name_to, value_to: the to node for the edge.



## Count the number of organizations that contributed to a category (count_organizations_contributed_to_category)
To count the number of organizations that contributed to a category, 
use the script *count_organizations_contributed_to_category.py*.
You can find this script in the directory *import_export*.

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
Usage:
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


## Export nodes to a file (export_person_identifiers and export_person_node_properties)
[This is an old script, you might want to use
[Export nodes and edges to a csv file,
raw version](#import-nodes-and-edges-from-a-csv-file-raw-version-ricgraph_import_raw_from_csv)].

There are two scripts which allow to export *person* nodes to a csv file. These can be
found in the directory *import_export*.

* *export_person_identifiers.py*: exports
  all [person identifiers](ricgraph_details.md#person-identifiers)
  connected to a *person-root* node.
* *export_person_node_properties.py*: exports
  all [node properties](ricgraph_details.md#properties-of-nodes-in-ricgraph)
  for every *person* node connected to a *person-root* node.

Use the parameter *EXPORT_MAX_RECS* for the number of records to export and
*EXPORT_FILENAME* for the filename to export at the start of both scripts.


## Delete personal data from Ricgraph (delete_personal_data)
This script deletes all personal data of one or more persons from Ricgraph.
The bash script *delete_personal_data.sh* is a wrapper for the
Python script *delete_pers_data.py*.
Both can be found in the directory *enhance*.
These persons need to be listed in a csv file.
An example csv file *pers_to_delete.csv* can also be found in directory *enhance*.

The script will delete all nodes of category *person* that are related with
the person whose personal data have to be deleted (except for the *person-root* node,
this node will not be deleted since it does not contain personal information).

Bash script:
```
Usage:
delete_personal_data.sh [options]

Options:
        -o, --organization [organization]
                The organization to harvest. Specify the organization
                abbreviation.
        -e, --empty_ricgraph [yes|no]
                Whether to empty Ricgraph before harvesting the
                first organization. If absent, Ricgraph will not be emptied.
        -c, --python_cmd [python interpreter]
                The python interpreter to use. If absent, and a python
                virtual environment is used, that interpreter is used.
        -p, --python_path [python path]
                The value for PYTHONPATH, the path to python libraries.
                If absent, the current directory is used.
        -h, --help
                Show this help text.
```

Python script:
```
Usage:
delete_pers_data.py [options]

Options:
  --filename <filename>
          Specifies a csv file that has columns 'name' and 'value'.
          Every row in this file contains a personal identifier of
          a person whose personal data needs to be deleted from Ricgraph.
  --are_you_sure <yes>
          Safety check since the script will delete items from Ricgraph.
          'yes': This script will run.
          any other value: This script will not run.
          If this option is not present, the script will prompt the user
          whether to run the script.
```

The file *filename* contains identifiers for persons whose personal data have to
be deleted from Ricgraph.
It contains exactly two columns and can have as many rows as necessary.
The columns are:

* name, value: values to identify the person in Ricgraph.


## Rename (sub-)organizations in Ricgraph (rename_organizations)
This script renames (sub-)organizations in Ricgraph
that are listed in a csv file.
The bash script *rename_organizations.sh* is a wrapper for the
Python script *rename_orgs.py*.
Both can be found in the directory *enhance*.
Example corresponding csv files can also be found in directory *enhance*.
The script will read a line from the csv file. Then it will
rename the (sub-)organization.

For (sub-)organization naming conventions read
[Conventions for names of (sub-)organizations in 
Ricgraph](ricgraph_details.md#conventions-for-names-of-sub-organizations-in-ricgraph).

You can also use this script to "unify" organization names. This may be necessary
because not every organization name has been spelled the same in the
sources you have harvested. Also, an organization name may be spelled differently
in the same source system. For example:

| orgname_old           | orgname_new           |
|-----------------------|-----------------------|
| University of Utrecht | UU Utrecht University |
| University Utrecht    | UU Utrecht University |
| Utrecht Univ.         | UU Utrecht University |
| Utrecht Unversiteit   | UU Utrecht University |

However, it is advisable to
do this only for those organizations that you have harvested,
or that you are specifically interested in,
and not for all organizations that your organization relates to,
because the latter may be a lot of work.

Bash script:
```
Usage:
rename_organizations.sh [options]

Options:
        -o, --organization [organization]
                The organization to harvest. Specify the organization
                abbreviation.
        -e, --empty_ricgraph [yes|no]
                Whether to empty Ricgraph before harvesting the
                first organization. If absent, Ricgraph will not be emptied.
        -c, --python_cmd [python interpreter]
                The python interpreter to use. If absent, and a python
                virtual environment is used, that interpreter is used.
        -p, --python_path [python path]
                The value for PYTHONPATH, the path to python libraries.
                If absent, the current directory is used.
        -h, --help
                Show this help text.
```

Python script:
```
Usage:
rename_orgs.py [options]

Options:
  --filename <filename>
          Specifies a csv file that has columns 'orgname_old'
          and 'orgname_new'.
          Every row in this file contains an organization name
          that has to be renamed to a new organization name.
  --are_you_sure <yes>
          Safety check since the script will modify Ricgraph.
          'yes': This script will run.
          any other value: This script will not run.
          If this option is not present, the script will prompt the user
          whether to run the script.
```

The file *filename* contains (sub-)organization names.
It contains exactly two columns and can have as many rows as necessary.
The columns are:

* orgname_old: the old (sub-)organization name;
* orgname_new: the new (sub-)organization name.


## Script to enrich persons (enrich_orcids_scopusids)
With the script *enrich_orcids_scopusids.py*, 
you can enrich persons having an ORCID but no SCOPUS_AUTHOR_ID
(using OpenAlex), or vice versa (using the Scopus API). Note that Scopus has 
a rate limit, and that 
you have to set some parameters in *ricgraph.ini*.
You can find this script in the directory *enhance*.


## Script to find person identifiers pointing to different persons (find_double_pids)
With the script *find_double_pids.py*, you can check if 
there are any personal identifiers that are
pointing to two or more different persons.
You can find this script in the directory *enhance*.


## Create a table of contents of the Ricgraph documentation (create_toc_documentation)
To create a table of contents of the Ricgraph documentation 
use the script *create_toc_documentation.py*.
You can find this script in the directory *maintenance*.
The table of contents will be created in file 
[ricgraph_toc_documentation.md](ricgraph_toc_documentation.md#table-of-contents-ricgraph-documentation).
```
Usage:
create_toc_documentation.py
```

## Create an index of the Ricgraph documentation (create_index_documentation)
To create an index of the Ricgraph documentation
use the script *create_index_documentation.py*.
You can find this script in the directory *maintenance*.
The index will be created in file
[ricgraph_index_documentation.md](ricgraph_index_documentation.md#index-ricgraph-documentation).
```
Usage:
create_index_documentation.py
```


## Create the Ricgraph REST API documentation (convert_openapi_to_mddoc)
To create the Ricgraph REST API documentation 
use the script *convert_openapi_to_mddoc.py*.
This documentation is based on the Ricgraph OpenAPI yaml file *openapi.yaml*
in the directory *ricgraph_explorer/static*.
You can find this script in the directory *maintenance*.
The REST API documentation will be created in file
[ricgraph_restapi_gendoc.md](ricgraph_restapi_gendoc.md#ricgraph---research-in-context-graph-rest-api).
```
Usage:
convert_openapi_to_mddoc.py
```

