## Ricgraph harvest scripts

Ricgraph harvest scripts can be found in the directory
[harvest_to_ricgraph_examples](../harvest_to_ricgraph_examples).
The code is
documented and hints to use it can be found in those files.
You can write your own harvest scripts:
for more information 
see [Ricgraph script writing](ricgraph_script_writing.md).

One of the most useful features of Ricgraph is that
it is possible to harvest sources that are
important to a user or organization.
By doing this, one is able to create a system that perfectly suits
a certain information need of that person or organization.
In creating harvest scripts, it is possible to harvest
only that information that is relevant for a certain purpose.
For example, one of the example harvest
scripts harvests the Utrecht University staff pages.
These pages cannot be harvested by other organizations
due to the privileges required. Also, it is possible to harvest a source that is internal
to an organization.
Ricgraph can be installed on any internal or external accessible system according to your needs,
so the data in Ricgraph is only accessible for persons of a certain organization,
or for anyone.

There are five examples of harvest scripts provided, for
* [harvest of OpenAlex](#harvest-of-openalex);
* [harvest of Pure](#harvest-of-pure);
* [harvest of Utrecht University 
  datasets](#harvest-of-utrecht-university-datasets);
* [harvest of Utrecht University staff 
  pages](#harvest-of-utrecht-university-staff-pages);
* [harvest of software from the Research Software 
  Directory](#harvest-of-software-from-the-research-software-directory).

There is also a script for batch harvesting, *batch_harvest.py*. You can
use this script to run a number of harvest scripts after each other.
It can be adapted to your needs, see the Python code in the script.

It is best to [run harvest scripts in a specific 
order](#order-of-running-the-harvest-scripts).
 
[Return to main README.md file](../README.md).

### Organization abbreviation
Ricgraph uses the term *organization abbreviation*.
This is a string of a few letters that can be passed to some harvest
scripts to determine for which organization such a script will harvest
data.  Examples are *UU* or *UMCU*.

You will see this in keys in the
[Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file).
Examples are *organization_name_UU* or
*organization_name_UMCU*. The general format is *key_XXXX*, with *XXXX* 
the organization abbreviation.

If your organization abbreviation is not in the Ricgraph
initialization file, feel free to add one. 
You can use any (short) string and pass it to a harvest script. You only
need to insert keys (and values) for the organization(s) you are planning
to harvest.

### Harvest of OpenAlex

To harvest  [OpenAlex](https://openalex.org), use the script *harvest_openalex_to_ricgraph.py*.
```
Usage
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

### Harvest of Pure

To harvest [Pure](https://www.elsevier.com/solutions/pure), 
use the script *harvest_pure_to_ricgraph.py*. 
```
Usage
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
```
With this script, you can harvest persons, organizations and research outputs.
This script needs two parameters in the
[Ricgraph initialization file](ricgraph_install_configure.md#ricgraph-initialization-file):
the url to Pure in *pure_url_XXXX*, and the Pure API key in *pure_api_key_XXXX*.
*XXXX* is your [organization abbreviation](#organization-abbreviation).

There is a lot of data in Pure, so your harvest may take a long time. You may
reduce this by adjusting parameters at the start of the script. Look in the sections
"Parameters for harvesting persons/organizations/research outputs from Pure".
E.g., for research outputs you can adjust
the years to harvest with the parameter *PURE_RESOUT_YEARS* and the maximum number of
records to harvest with *PURE_RESOUT_MAX_RECS_TO_HARVEST*.

### Harvest of Utrecht University datasets

To harvest Utrecht University datasets
from the data repository 
[Yoda](https://search.datacite.org/repositories/delft.uu),
use the script
*harvest_yoda_datacite_to_ricgraph.py*.
```
Usage
harvest_yoda_datacite_to_ricgraph.py [options]

Options:
  --empty_ricgraph <yes|no>
          'yes': Ricgraph will be emptied before harvesting.
          'no': Ricgraph will not be emptied before harvesting.
          If this option is not present, the script will prompt the user
          what to do.
```
This script can be used out of the box since it doesn't need an
[API](https://en.wikipedia.org/wiki/API) key.

### Harvest of Utrecht University staff pages

To harvest the 
[Utrecht University staff pages](https://www.uu.nl/medewerkers), 
use the script *harvest_uustaffpages_to_ricgraph.py*.

```
Usage
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

### Harvest of software from the Research Software Directory

To harvest software packages from the 
[Research Software Directory](https://research-software-directory.org),
use the script *harvest_rsd_to_ricgraph.py*.
```
Usage
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

### Order of running the harvest scripts
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

### How to make your own harvesting scripts
For making your own harvesting scripts, refer to the code used in the
harvest scripts described above, and read 
[How to make your own harvesting 
scripts](ricgraph_script_writing.md#how-to-make-your-own-harvesting-scripts).

### Return to main README.md file

[Return to main README.md file](../README.md).

