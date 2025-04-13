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

[Return to main README.md file](../README.md#ricgraph---research-in-context-graph).


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

## Scripts that harvest multiple sources
These bash scripts are in directory *harvest_mulitple_sources*.

There are two general scripts to harvest multiple sources:

* *multiple_harvest_organization_rsd_yoda.sh*: harvests the 
  [Research Software Directory](#harvest-of-software-from-the-research-software-directory-harvest_rsd_to_ricgraph) and
  [Yoda](#harvest-of-data-sets-from-yoda-datacite-harvest_yoda_datacite_to_ricgraph).
* *multiple_harvest_organization.sh*: harvest
  [Pure](#harvest-of-pure-harvest_pure_to_ricgraph) and
  [OpenAlex](#harvest-of-openalex-harvest_openalex_to_ricgraph).
  Then, it calls script  *multiple_harvest_organization_rsd_yoda.sh*.

```
Usage
./[script name].sh [options]

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

There are three wrapper scripts:

* *multiple_harvest_demo.sh*: 
  calls script *multiple_harvest_organization_rsd_yoda.sh* with organization *UU*. These sources can be used
  to demonstrate Ricgraph, since these sources do not need a REST API key.
* *multiple_harvest_uu.sh*: 
  calls *multiple_harvest_organization.sh* for organization *UU*, and also harvests 
  [the UU staff pages](#harvest-of-utrecht-university-staff-pages-harvest_uustaffpages_to_ricgraph).
* *multiple_harvest_rik.sh*: a script that harvests the favorite sources of the author of Ricgraph.

You can use the [Ricgraph Makefile](ricgraph_install_configure.md#ricgraph-makefile)
to run these harvest scripts, e.g. to run *multiple_harvest_demo.sh*,
execute command:

```
make run_bash_script bash_script=harvest_multiple_sources/multiple_harvest_demo.sh
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
*OPENALEX_RESOUT_YEARS* and *OPENALEX_MAX_RECS_TO_HARVEST*.

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
```
With this script, you can harvest persons, organizations and research outputs.
This script needs two parameters in the
[Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file):
the url to Pure in *pure_url_XXXX*, and the 
Pure [API](https://en.wikipedia.org/wiki/API) key in *pure_api_key_XXXX*.
*XXXX* is your [organization abbreviation](#organization-abbreviation).

#### Limit the amount of data to harvest from Pure
There is a lot of data in Pure, so your harvest may take a long time. You may
reduce this by adjusting parameters at the start of the script. Look in the sections
"Parameters for harvesting persons/organizations/research outputs from Pure".
E.g., for research outputs you can adjust
the years to harvest with the parameter *PURE_RESOUT_YEARS* and the maximum number of
records to harvest with *PURE_RESOUT_MAX_RECS_TO_HARVEST*.

#### Pure READ and Pure CRUD API
Pure has two APIs, a READ and a CRUD API.
The Pure READ API ("old" API) is only for reading data from Pure.
The Pure CRUD API ("new" API) can be used to create, read, update and delete data 
in Pure (hence the name: CRUD). You do not need to specify which API you want to use,
the script will be able to determine it for you
(just include the API key in the initialization file).
The author recommends to use the READ API.
You can use both of them to harvest data from Pure,
but each of them has its own advantages and disadvantages:

* The Pure READ API has a number of filters, which allow to reduce data requested from Pure
  on the Pure server,
  thereby preventing this data to be sent to the computer which is running the Pure harvest 
  script, and for the harvest script, to process all this data. 
  E.g., the READ API has a filter for persons, so only active persons in Pure will
  be sent to the harvesting computer, thereby reducing the number of persons to process in the harvest
  script from all persons in Pure to only active persons in Pure. 
  Another filter is the start and end publication year for research outputs. 
  This makes it possible for the Pure harvest script to only process research outputs from a
  certain year, instead of all research outputs in Pure. This prevents potential memory problems.
* The Pure CRUD API allows the Pure administrator to specify which Pure fields are allowed
  to be sent from the Pure server to the computer that is running the Pure harvest script.
  This allows for only sending data that is requested. However, since this API is in development,
  a lot of the filters present in the READ API do not exist (yet), especially the
  filters mentioned in the previous bullet. That means, if you run
  the Pure harvest script, you might encounter memory problems while harvesting 
  research outputs due to the number of research outputs in Pure, 
  unless you set *PURE_RESOUT_MAX_RECS_TO_HARVEST* in the Pure harvest script to some
  suitable value. 

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
The order of running the harvesting scripts does matter. The author harvests
only records for Utrecht University and uses this order:

1. *harvest_pure_to_ricgraph.py* (since it has a lot of data which is mostly correct);
1. *harvest_yoda_datacite_to_ricgraph.py* (not too much data, so harvest is fast, but it 
   contains several data entry errors);
1. *harvest_rsd_to_ricgraph.py* (not too much data);
1. *harvest_openalex_to_ricgraph.py* (a lot of data from a [number of 
   sources](https://docs.openalex.org/additional-help/faq#where-does-your-data-come-from)); 
1. *harvest_uustaffpages_to_ricgraph.py*.

Best practice is to start with that source that has the most data.
If you don't have an API key for Pure, one can best start with the harvest
script for OpenAlex.

## How to make your own harvesting scripts
For making your own harvesting scripts, refer to the code used in the
harvest scripts described above, and read 
[How to make your own harvesting 
scripts](ricgraph_script_writing.md#how-to-make-your-own-harvesting-scripts).
