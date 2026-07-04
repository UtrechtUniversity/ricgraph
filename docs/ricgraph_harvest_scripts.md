# Ricgraph harvest scripts

This page describes scripts for harvesting sources and inserting the results in Ricgraph.
They can be found in directory *harvest* and *harvest_multiple_sources*.
Read more about [scripts to import and export items from 
Ricgraph](ricgraph_misc_scripts.md#ricgraph-miscellaneous-scripts), 
about [scripts to enhance (finding, enriching, etc.) information in
Ricgraph](ricgraph_misc_scripts.md#ricgraph-miscellaneous-scripts), 
or about
[writing your own scripts](ricgraph_script_writing.md#ricgraph-script-writing).

On this page, you can find:

* [Introduction to harvest scripts](#introduction-to-harvest-scripts)
* [Organization abbreviation](#organization-abbreviation)
* [Demo harvest script (multiple_harvest_demo)](#demo-harvest-script-multiple_harvest_demo)
* [Scripts that harvest multiple sources](#scripts-that-harvest-multiple-sources)
* [Scripts that harvest a single source](#scripts-that-harvest-a-single-source)
  * [Harvest of OpenAlex (harvest_openalex_to_ricgraph)](#harvest-of-openalex-harvest_openalex_to_ricgraph)
  * [Harvest of Pure (harvest_pure_to_ricgraph)](#harvest-of-pure-harvest_pure_to_ricgraph)
  * [Harvest of data sets from Yoda-DataCite (harvest_yoda_datacite_to_ricgraph)](#harvest-of-data-sets-from-yoda-datacite-harvest_yoda_datacite_to_ricgraph)
  * [Harvest of Utrecht University staff pages (harvest_uustaffpages_to_ricgraph)](#harvest-of-utrecht-university-staff-pages-harvest_uustaffpages_to_ricgraph)
  * [Harvest of software from the Research Software Directory (harvest_rsd_to_ricgraph)](#harvest-of-software-from-the-research-software-directory-harvest_rsd_to_ricgraph)
* [Order of running the harvest scripts](#order-of-running-the-harvest-scripts)
* [How to make your own harvesting scripts](#how-to-make-your-own-harvesting-scripts)

All code is documented and hints to use it can be found in the source files.


## Introduction to harvest scripts

One of the most useful features of Ricgraph is that
it is possible to harvest sources that are
important to a user or organization.
By doing this, one is able to create a system that perfectly suits
a certain information need of that person or organization.
In creating harvest scripts, it is possible to harvest
only that information that is relevant for a certain purpose.

E.g., one can harvest generally available sources such as OpenAlex.
It is also possible to harvest sources that are specific for a certain organization.
For example, one of the harvest
scripts harvests the Utrecht University staff pages.
These pages cannot be harvested by other organizations
due to the privileges required. Also, it is possible to harvest a source that is internal
to an organization.

Ricgraph can be installed on any internal or external accessible system according to your needs,
so the data in Ricgraph is only accessible for persons of a certain organization,
or for anyone.

Ricgraph provides a number of scripts for batch harvesting multiple sources
with one script.
These are in directory *harvest_multiple_sources*.
Read more in the 
[section that describes the scripts that harvest multiple sources](#scripts-that-harvest-multiple-sources).
These scripts are based on the Ricgraph harvest scripts to harvest a single source.
They are in directory *harvest*.
Read more in the 
[section that describes the scripts that harvest a single source](#scripts-that-harvest-a-single-source).

Each of these scripts can be adapted to your needs, see their code. 
It is best to [run harvest scripts in a specific 
order](#order-of-running-the-harvest-scripts).
 
## Organization abbreviation
Ricgraph uses the term *organization abbreviation*.
This is a string of a few letters that can be passed to some harvest
scripts to determine for which organization such a script will harvest
data.  Examples are *UU* or *UMCU*.
You will find this in keys in the
[Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file).
Examples are *organization_name_UU* or
*organization_name_UMCU*. The general format is *key_XXXX*, with *XXXX* 
the organization abbreviation.

If your organization abbreviation is not in the Ricgraph
initialization file, feel free to add one. 
You can use any (short) string and pass it to a harvest script. You only
need to insert keys (and values) for the organization(s) you are planning
to harvest.

## Demo harvest script (multiple_harvest_demo)
This bash script can be found in directory *harvest_multiple_sources*.

*multiple_harvest_demo.sh* harvests the
[Research Software Directory](#harvest-of-software-from-the-research-software-directory-harvest_rsd_to_ricgraph)
and [Yoda-DataCite](#harvest-of-data-sets-from-yoda-datacite-harvest_yoda_datacite_to_ricgraph)
for Utrecht University.
These sources can be used
to demonstrate Ricgraph, since these sources do not need a REST API key.

You can use the [Ricgraph Makefile](ricgraph_install_configure.md#ricgraph-makefile)
to run this harvest script. To run *multiple_harvest_demo.sh*,
execute command:

```
make run_bash_script bash_script=harvest_multiple_sources/multiple_harvest_demo.sh
```

## Scripts that harvest multiple sources
These bash scripts are in directory *harvest_multiple_sources*.

There is one general script to harvest multiple sources:
*multiple_harvest_organization.sh*. This script harvests, in turn:

* [Pure](#harvest-of-pure-harvest_pure_to_ricgraph);
* Only if your organization is Utrecht University:
  [Utrecht University staff pages](#harvest-of-utrecht-university-staff-pages-harvest_uustaffpages_to_ricgraph);
* [Research Software Directory](#harvest-of-software-from-the-research-software-directory-harvest_rsd_to_ricgraph);
* Only if there is a *set name* for your organization 
  in *ricgraph.ini*: [Yoda-DataCite](#harvest-of-data-sets-from-yoda-datacite-harvest_yoda_datacite_to_ricgraph);
* [OpenAlex](#harvest-of-openalex-harvest_openalex_to_ricgraph).

To be able to do this, the correct entries have to be set in the
[Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file).

```
Usage:
./[script name].sh [options]

Options:
        -o, --organization [organization]
                The organization to harvest. Specify the organization
                abbreviation.
        -e, --empty_ricgraph [yes|no]
                Whether to empty Ricgraph before harvesting the
                first organization. If absent, Ricgraph will not be emptied.
        -f, --year_first [year]
                First year of the harvest.
        -l, --year_last [year]
                Last year of the harvest.
        -c, --python_cmd [python interpreter]
                The python interpreter to use. If absent, and a python
                virtual environment is used, that interpreter is used.
        -p, --python_path [python path]
                The value for PYTHONPATH, the path to python libraries.
                If absent, the current directory is used.
        -h, --help
                Show this help text.
```

There is a wrapper script:

* *multiple_harvest_open_ricgraph_demo_server.sh*: a script that harvests 
  the organizations for the [Open Ricgraph demo 
  server](https://www.ricgraph.eu/pilot-project-open-ricgraph-demo-server.html).

You can use the [Ricgraph Makefile](ricgraph_install_configure.md#ricgraph-makefile)
to run these harvest scripts. 

To run *multiple_harvest_organization.sh*,
you will need to pass arguments, execute command:
```
make run_bash_script bash_script=harvest_multiple_sources/multiple_harvest_organization.sh cmd_args="--organization UU --empty_ricgraph yes"
```

To run *multiple_harvest_open_ricgraph_demo_server.sh*, execute command:
```
make run_bash_script bash_script=harvest_multiple_sources/multiple_harvest_open_ricgraph_demo_server.sh
```

## Scripts that harvest a single source
These Python scripts are in directory *harvest*. 

### Harvest of OpenAlex (harvest_openalex_to_ricgraph)

To harvest  [OpenAlex](https://openalex.org), use the script *harvest_openalex_to_ricgraph.py*.
```
Usage:
harvest_openalex_to_ricgraph.py [options]

Options:
  --empty_ricgraph <yes|no>
          'yes': Ricgraph will be emptied before harvesting.
          'no': Ricgraph will not be emptied before harvesting.
          If this option is not present, the script will prompt the user
          what to do.
  --organization <organization abbreviation>
          Harvest data from organization <organization abbreviation>.
          The organization abbreviations are specified in the Ricgraph ini
          file.
          If this option is not present, the script will prompt the user
          what to do.
  --year_first <first year of harvest>
          Start the harvest from this year on.
  --year_last <last year of harvest>
          End the harvest at this year.
```
This script harvests OpenAlex Works, and by harvesting these
Works, it also harvests OpenAlex Authors.
This script needs the parameters *organization_name_XXXX*, 
*organization_ror_XXXX*
and *openalex_polite_pool_email* to be set in the
[Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file).
*XXXX* is your [organization abbreviation](#organization-abbreviation).

There is a lot of data in OpenAlex, so your harvest may take a long time. You may
reduce this by adjusting parameters at the start of the script. Look in the section
"Parameters for harvesting persons and research outputs from OpenAlex":
*OPENALEX_MAX_RECS_TO_HARVEST*.

### Harvest of Pure (harvest_pure_to_ricgraph)

To harvest [Pure](https://www.elsevier.com/solutions/pure), 
use the script *harvest_pure_to_ricgraph.py*. 
```
Usage:
harvest_pure_to_ricgraph.py [options]

Options:
  --empty_ricgraph <yes|no>
          'yes': Ricgraph will be emptied before harvesting.
          'no': Ricgraph will not be emptied before harvesting.
          If this option is not present, the script will prompt the user
          what to do.
  --organization <organization abbreviation>
          Harvest data from organization <organization abbreviation>.
          The organization abbreviations are specified in the Ricgraph ini
          file.
          If this option is not present, the script will prompt the user
          what to do.
  --harvest_projects <yes|no>
          'yes': projects will be harvested.
          'no' (or any other answer): projects will not be harvested.
          If this option is not present, projects will not be harvested,
          the script will not prompt the user.
  --year_first <first year of harvest>
          Start the harvest from this year on.
  --year_last <last year of harvest>
          End the harvest at this year.
```
With this script, you can harvest persons, organizations, research outputs,
data sets, and press media items.
This script needs two parameters in the
[Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file):
the url to Pure in *pure_url_XXXX*, and the 
Pure [API](https://en.wikipedia.org/wiki/API) key in *pure_api_key_XXXX*.
*XXXX* is your [organization abbreviation](#organization-abbreviation).

#### Limit the amount of data to harvest from Pure
There is a lot of data in Pure, so your harvest may take a long time. You may
reduce this by adjusting parameters at the start of the script. Look in the sections
"Parameters for harvesting persons/organizations/research outputs from Pure".
E.g., for the maximum number of
records to harvest you can adjust *PURE_RESOUT_MAX_RECS_TO_HARVEST*.

#### Pure READ API and Pure CRUD API
Pure has two APIs, a READ and a CRUD API.
The Pure READ API ("old" API) is only for reading data from Pure.
The Pure CRUD API ("new" API) can be used to create, read, update and delete data 
in Pure (hence the name: CRUD).
The Pure administrator hands out Pure API keys. Such a key determines
whether the READ API or CRUD API will be used, what endpoints are accessible, and
(for the CRUD API) which fields can be accessed and whether you can only read from
or also write to Pure.

For the Pure harvest script, you do not need to specify which 
API you want to use, the script will be able to determine it for you
(just include the API key in the initialization file).

For now, it is recommended to use the Pure READ API.
The reason for this is two important missing features in the Pure CRUD API
(missing at the time of writing, July 2026, but this has been a
feature request for Pure since at least 2023).
For the Pure CRUD API, there is no way to harvest
research outputs and press media items from the CRUD API endpoint by

1. filtering on year;
2. on fields to be returned.

Both (1) and (2) imply that the harvest script will
need to retrieve every research output and press media item and then filter
(in the script, not on the Pure server as one would expect) on year. 
It will lead to a very long execution
time and a lot of data transferred from Pure to this script.
This will especially hurt harvesting research outputs,
since there are so many of them.

For instance, there are two constants
that determine the number of items to be harvested from Pure CRUD API:
for research outputs and press media items
*PURE_CRUD_RESOUTS_MAX_RECS_TO_HARVEST_PER_YEAR* and
*PURE_CRUD_PRESS_MEDIA_MAX_RECS_TO_HARVEST_PER_YEAR*.
Both of these numbers are multiplied by the number
of years to harvest to determine the total number of records to 
be harvested. If your Pure has far less records for the research outputs
for the years you want to have harvested, it will still harvest this
number of records. If you have more, the surplus will not be harvested.

For more details, see the comments in the Pure harvest script
*harvest_pure_to_ricgraph.py*. You can [access it on 
GitHub](https://github.com/UtrechtUniversity/ricgraph/blob/main/harvest/harvest_pure_to_ricgraph.py).

Note that the above only holds for the CRUD API. 
The READ API can filter on year and on fields to be returned. 
That is why using the Pure READ API is recommended.

#### Pure endpoints
For harvesting Pure, you will need the following endpoints:

| what to harvest  | endpoint Pure READ API | endpoint Pure CRUD API  |
|------------------|------------------------|-------------------------|
| persons          | persons                | persons/search          |
| organizations    | organisational-units   | organizations/search    |
| research outputs | research-outputs       | research-outputs/search |
| data sets        | datasets               | data-sets/search        |
| press media      | press-media            | pressmedia/search       |


#### Pure fields that are harvested

For the precise fields that are harvested, you will need to look at the
Python code of the Pure harvest script
*harvest_pure_to_ricgraph.py* (this is to prevent a mismatch
between this documentation and the harvest code). 
You can [access the script on
GitHub](https://github.com/UtrechtUniversity/ricgraph/blob/main/harvest/harvest_pure_to_ricgraph.py).
The table below specifies what to look for.

| endpoint         | Pure READ API                  | Pure CRUD API                  |
|------------------|--------------------------------|--------------------------------|
| persons          | PURE_READ_PERSONS_FIELDS       | PURE_CRUD_PERSONS_FIELDS       |
| organizations    | PURE_READ_ORGANIZATIONS_FIELDS | PURE_CRUD_ORGANIZATIONS_FIELDS |
| research outputs | PURE_READ_RESOUTS_FIELDS       | PURE_CRUD_RESOUTS_FIELDS       |
| data sets        | PURE_READ_DATASETS_FIELDS      | PURE_CRUD_DATASETS_FIELDS      |
| press media      | PURE_READ_PRESS_MEDIA_FIELDS   | PURE_CRUD_PRESS_MEDIA_FIELDS   |


The fields to be harvested are in Python lists, that are itself part of
Python dicts. So, to find the exact fields, click on the link 
to the Pure harvest script above.
Then, for a parameter name in the table, search for it in the harvest script.
If you look at the harvest script in a webbrowser, depending on
your browser, you very probably use *&lt;control key&gt; F* to search.

If you have found the corresponding parameter in the code, the fields
that are imported from pure are found in the list *fields*. If a list item
starts with a '#', that field is not imported from Pure, the '#' is a
Python comment sign.

For an element in the list, if it ends with '\*', as in _period.*_,
everything in the tree under the field _period_ is imported from Pure. If it does not 
have a star, e.g. as in _uuid_, then only the _uuid_ field is imported from Pure.

Not all the elements of the *fields* will be included in Ricgraph, some are only used
to determine whether e.g. a person should be included in Ricgraph or not. For example,
the start and
end date of a person determine if a person should be included in Ricgraph, but both
the start and end date itself are not in Ricgraph.

The fields that are actually included in Ricgraph
can be found at the bottom of the home page of
[Ricgraph Explorer](ricgraph_explorer.md).
For example, look at the bottom of the home page of the
Open Ricgraph demo server. You can find the link to the demo server at
the webpage of the
[Pilot Open Ricgraph demo 
server](https://www.ricgraph.eu/pilot-project-open-ricgraph-demo-server.html).


#### Pure harvesting of projects
You can also harvest projects from Pure, if your organization uses them. You will
need to use the Pure READ API, harvesting projects with the PURE CRUD API has not
been implemented yet.

Projects will be connected to related persons, related organizations
(the chair/department/faculty the person is from), related research outputs, and
related projects (if any).

Note that it can happen that you may find a project that is connected to a 
*person-root* which only has a *PURE_UUID_PERS* and nothing else, or that you
may find a project that is connected to a research output which only
has a *PURE_UUID_RESOUT* and nothing else.
This is probably caused by the Pure harvest script that (in its standard
configuration) only harvests active persons, those are
persons who are working at your organization at the time of harvest
(so you will not have any information about persons that have worked
on the project, e.g. PhDs or postdocs, since they may already have left 
your organization),
and only harvests research outputs from 2020 onward,
and your project may have research outputs from before 2020.

### Harvest of data sets from Yoda-DataCite (harvest_yoda_datacite_to_ricgraph)

To harvest data sets from the data repository 
[Yoda](https://www.uu.nl/en/research/yoda) (via DataCite),
use the script
*harvest_yoda_datacite_to_ricgraph.py*.
```
Usage:
harvest_yoda_datacite_to_ricgraph.py [options]

Options:
  --empty_ricgraph <yes|no>
          'yes': Ricgraph will be emptied before harvesting.
          'no': Ricgraph will not be emptied before harvesting.
          If this option is not present, the script will prompt the user
          what to do.
  --organization <organization abbreviation>
          Harvest data from organization <organization abbreviation>.
          The organization abbreviations are specified in the Ricgraph ini
          file.
          If this option is not present, the script will prompt the user
          what to do.
```
This script can be used out of the box since it doesn't need an
[API](https://en.wikipedia.org/wiki/API) key.

### Harvest of Utrecht University staff pages (harvest_uustaffpages_to_ricgraph)

To harvest the 
[Utrecht University staff pages](https://www.uu.nl/medewerkers), 
use the script *harvest_uustaffpages_to_ricgraph.py*.

```
Usage:
harvest_uustaffpages_to_ricgraph.py [options]

Options:
  --empty_ricgraph <yes|no>
          'yes': Ricgraph will be emptied before harvesting.
          'no': Ricgraph will not be emptied before harvesting.
          If this option is not present, the script will prompt the user
          what to do.
```
This script needs the parameter *uustaff_url* to be set in the
[Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file).

### Harvest of software from the Research Software Directory (harvest_rsd_to_ricgraph)

To harvest software packages from the 
[Research Software Directory](https://research-software-directory.org),
use the script *harvest_rsd_to_ricgraph.py*.
```
Usage:
harvest_rsd_to_ricgraph.py [options]

Options:
  --empty_ricgraph <yes|no>
          'yes': Ricgraph will be emptied before harvesting.
          'no': Ricgraph will not be emptied before harvesting.
          If this option is not present, the script will prompt the user
          what to do.
  --organization <organization abbreviation>
          Harvest data from organization <organization abbreviation>.
          The organization abbreviations are specified in the Ricgraph ini
          file.
          If this option is not present, the script will prompt the user
          what to do.
```
This script needs one parameter in the
[Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file):
*rsd_organization_XXXX*.
*XXXX* is your [organization abbreviation](#organization-abbreviation).
It can be used out of the box since it doesn't need an
[API](https://en.wikipedia.org/wiki/API) key.

## Order of running the harvest scripts
The order of running the harvesting scripts does matter. When the author 
is harvesting records for Utrecht University, the following order is used:

1. *harvest_pure_to_ricgraph.py* (since it has a lot of data which is mostly correct);
1. *harvest_uustaffpages_to_ricgraph.py* (results in a lot of personal identifiers,
   which is useful for following harvests);
1. *harvest_rsd_to_ricgraph.py* (not too much data, so harvest is fast);
1. *harvest_yoda_datacite_to_ricgraph.py* (not too much data, so harvest is fast, but it
   contains several data entry errors);
1. *harvest_openalex_to_ricgraph.py* (a lot of data from a [number of 
   sources](https://developers.openalex.org/#data)).

Note that the same order is used in *multiple_harvest_organization.sh*.

Best practice is to start with that source that has the most data.
If you don't have an API key for Pure, one can best start with the harvest
script for OpenAlex.

## How to make your own harvesting scripts
For making your own harvesting scripts, refer to the code used in the
harvest scripts described above, and read 
[How to make your own harvesting 
scripts](ricgraph_script_writing.md#how-to-make-your-own-harvesting-scripts).
