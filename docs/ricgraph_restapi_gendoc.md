






# Ricgraph - Research in context graph REST API

> Version 1.0.0

 ### What to find on this page?
This is the documentation page for the Ricgraph REST API. You can use the Ricgraph REST API to programmatically get items from Ricgraph, as an alternative to using the user interface. You will get these items in a [JSON format](https://en.wikipedia.org/wiki/JSON).
### How to use
In the left column of this page, you can explore the calls (i.e., the REST API operations) that are available. You can also try them out, by selecting a call, entering values in the 'Query-string parameters' subsection of the 'Request' section, and clicking the 'Try' button. Next, a gray tabbed box will appear. In the 'Response' tab of that box, you will get the JSON response. In the 'CURL' tab of that box, you will get a [curl](https://en.wikipedia.org/wiki/CURL#curl) call with an [URL](https://en.wikipedia.org/wiki/URL) (web link) that you can use in a browser or in your code.
You don't need to provide authentication to use these calls.
### Technicalities
The Ricgraph REST API uses the [OpenAPI standard](https://www.openapis.org). It gives access to Ricgraph function calls both in *ricgraph.py* and in *ricgraph_explorer.py*.
Read more about [REST (representational state transfer)](https://en.wikipedia.org/wiki/REST), or read more about [API (application programming interface)](https://en.wikipedia.org/wiki/API). 

## Base URL

| URL | Description |
|------|------|
| /api |  |




## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | [GET /person/search](#get-personsearch) | Search for a person |
| GET | [GET /person/all_information](#get-personall_information) | Show all information related to this person |
| GET | [GET /person/share_research_results](#get-personshare_research_results) | Find persons that share any share research result types with this person |
| GET | [GET /person/collaborating_organizations](#get-personcollaborating_organizations) | Find organizations that this person collaborates with |
| GET | [GET /person/enrich](#get-personenrich) | Find information harvested from other source systems, not present in this source system |
| GET | [GET /organization/search](#get-organizationsearch) | Search for a (sub-)organization |
| GET | [GET /organization/all_information](#get-organizationall_information) | Show all information related to this organization |
| GET | [GET /organization/information_persons_results](#get-organizationinformation_persons_results) | Find any information from persons or their results in this organization |
| GET | [GET /competence/search](#get-competencesearch) | Search for a skill, expertise area or research area |
| GET | [GET /competence/all_information](#get-competenceall_information) | Show all information related to this competence |
| GET | [GET /broad_search](#get-broad_search) | Search for anything (broad search) |
| GET | [GET /advanced_search](#get-advanced_search) | Advanced search |
| GET | [GET /get_all_personroot_nodes](#get-get_all_personroot_nodes) | Find all person-root nodes of this node |
| GET | [GET /get_all_neighbor_nodes](#get-get_all_neighbor_nodes) | Find all neighbor nodes of this node |
| GET | [GET /get_ricgraph_list](#get-get_ricgraph_list) | Get the values of an internal global Ricgraph list |





### GET /person/search

Search for a person




__Parameters__

| Name | Type | Required | Description |
|------|------|----------|-------------|
| value | string | False | Search for a value in Ricgraph field *value* |
| max_nr_items | string | False | The maximum number of items to return, or 0 to return all items |





__Responses__




* 200:  OK 

* 250:  Nothing found 

* 251:  Invalid search 





### GET /person/all_information

Show all information related to this person




__Parameters__

| Name | Type | Required | Description |
|------|------|----------|-------------|
| key | string | True | Search for a value in Ricgraph field *_key* |
| max_nr_items | string | False | The maximum number of items to return, or 0 to return all items |





__Responses__




* 200:  OK 

* 250:  Nothing found 

* 251:  Invalid search 





### GET /person/share_research_results

Find persons that share any share research result types with this person




__Parameters__

| Name | Type | Required | Description |
|------|------|----------|-------------|
| key | string | True | Search for a value in Ricgraph field *_key* |
| max_nr_items | string | False | The maximum number of items to return, or 0 to return all items |





__Responses__




* 200:  OK 

* 250:  Nothing found 

* 251:  Invalid search 





### GET /person/collaborating_organizations

Find organizations that this person collaborates with


With this call you will get an overview of organizations that his person collaborates with. A person *X* from organization *A* collaborates with a person *Y* from organization *B* if *X* and *Y* have both contributed to the same research result.



__Parameters__

| Name | Type | Required | Description |
|------|------|----------|-------------|
| key | string | True | Search for a value in Ricgraph field *_key* |
| max_nr_items | string | False | The maximum number of items to return, or 0 to return all items |





__Responses__




* 200:  OK 

* 250:  Nothing found 

* 251:  Invalid search 





### GET /person/enrich

Find information harvested from other source systems, not present in this source system


The process of improving or enhancing information in a source system is called *enriching* that source system. This is only possible if you have harvested more than one source system. By using information found in one or more other harvested systems, information in this source system can be improved or enhanced. With this call you can enter a name of one of your source systems. Ricgraph will show what information can be added to this source system, based on the information harvested from other source systems.



__Parameters__

| Name | Type | Required | Description |
|------|------|----------|-------------|
| key | string | True | Search for a value in Ricgraph field *_key* |
| source_system | string | True | The name of the source system you would like to enrich |
| max_nr_items | string | False | The maximum number of items to return, or 0 to return all items |





__Responses__




* 200:  OK 

* 250:  Nothing found 

* 251:  Invalid search 





### GET /organization/search

Search for a (sub-)organization




__Parameters__

| Name | Type | Required | Description |
|------|------|----------|-------------|
| value | string | False | Search for a value in Ricgraph field *value* |
| max_nr_items | string | False | The maximum number of items to return, or 0 to return all items |





__Responses__




* 200:  OK 

* 250:  Nothing found 

* 251:  Invalid search 





### GET /organization/all_information

Show all information related to this organization




__Parameters__

| Name | Type | Required | Description |
|------|------|----------|-------------|
| key | string | True | Search for a value in Ricgraph field *_key* |
| max_nr_items | string | False | The maximum number of items to return, or 0 to return all items |





__Responses__




* 200:  OK 

* 250:  Nothing found 

* 251:  Invalid search 





### GET /organization/information_persons_results

Find any information from persons or their results in this organization




__Parameters__

| Name | Type | Required | Description |
|------|------|----------|-------------|
| key | string | True | Search for a value in Ricgraph field *_key* |
| max_nr_items | string | False | The maximum number of items to return, or 0 to return all items |





__Responses__




* 200:  OK 

* 250:  Nothing found 

* 251:  Invalid search 





### GET /competence/search

Search for a skill, expertise area or research area




__Parameters__

| Name | Type | Required | Description |
|------|------|----------|-------------|
| value | string | False | Search for a value in Ricgraph field *value* |
| max_nr_items | string | False | The maximum number of items to return, or 0 to return all items |





__Responses__




* 200:  OK 

* 250:  Nothing found 

* 251:  Invalid search 





### GET /competence/all_information

Show all information related to this competence




__Parameters__

| Name | Type | Required | Description |
|------|------|----------|-------------|
| key | string | True | Search for a value in Ricgraph field *_key* |
| max_nr_items | string | False | The maximum number of items to return, or 0 to return all items |





__Responses__




* 200:  OK 

* 250:  Nothing found 

* 251:  Invalid search 





### GET /broad_search

Search for anything (broad search)




__Parameters__

| Name | Type | Required | Description |
|------|------|----------|-------------|
| value | string | False | Search for a value in Ricgraph field *value* |
| max_nr_items | string | False | The maximum number of items to return, or 0 to return all items |





__Responses__




* 200:  OK 

* 250:  Nothing found 

* 251:  Invalid search 





### GET /advanced_search

Advanced search


The fields you enter are case-sensitive and use exact match search. If you enter values in more than one field, these fields are combined using AND.



__Parameters__

| Name | Type | Required | Description |
|------|------|----------|-------------|
| name | string | False | Search for a value in Ricgraph field *name* |
| category | string | False | Search for a value in Ricgraph field *category* |
| value | string | False | Search for a value in Ricgraph field *value* |
| max_nr_items | string | False | The maximum number of items to return, or 0 to return all items |





__Responses__




* 200:  OK 

* 250:  Nothing found 

* 251:  Invalid search 





### GET /get_all_personroot_nodes

Find all person-root nodes of this node




__Parameters__

| Name | Type | Required | Description |
|------|------|----------|-------------|
| key | string | True | Search for a value in Ricgraph field *_key* |
| max_nr_items | string | False | The maximum number of items to return, or 0 to return all items |





__Responses__




* 200:  OK 

* 250:  Nothing found 

* 251:  Invalid search 





### GET /get_all_neighbor_nodes

Find all neighbor nodes of this node




__Parameters__

| Name | Type | Required | Description |
|------|------|----------|-------------|
| key | string | True | Search for a value in Ricgraph field *_key* |
| name_want | array | False | Return only neighbor nodes whose field *name* matches any value in the provided list; if the list is empty, return all neighbor nodes regardless of their field *name* |
| name_dontwant | array | False | Return only neighbor nodes whose field *name* does *not* match any value in the provided list; if the list is empty, return all neighbor nodes regardless of their field *name* |
| category_want | array | False | Return only neighbor nodes whose field *category* matches any value in the provided list; if the list is empty, return all neighbor nodes regardless of their field *category* |
| category_dontwant | array | False | Return only neighbor nodes whose field *category* does *not* match any value in the provided list; if the list is empty, return all neighbor nodes regardless of their field *category* |
| max_nr_items | string | False | The maximum number of items to return, or 0 to return all items |





__Responses__




* 200:  OK 

* 250:  Nothing found 

* 251:  Invalid search 





### GET /get_ricgraph_list

Get the values of an internal global Ricgraph list




__Parameters__

| Name | Type | Required | Description |
|------|------|----------|-------------|
| ricgraph_list_name | string | True | Return the values in the specified internal Ricgraph list. These are dependent on the data in your Ricgraph instance and on the systems you have harvested. Allowed Ricgraph lists are:
* name_all: all possible values of the *name* field in a Ricgraph node.
* name_personal_all: all possible values of the *name* field that contain personal data in a Ricgraph node.
* category_all: all possible values of the *category* field in a Ricgraph node.
* personal_types_all: all category values in list *category_all* that are applicable to a person.
* remainder_types_all: all other category values in list *category_all*, that is
  all values in list *category_all* minus those in *personal_types_all*.

* source_all: the names of all the harvested source systems.
* resout_types_all: all research result types defined in file *ricgraph.py*.
 |





__Responses__




* 200:  OK 

* 250:  Nothing found 

* 251:  Invalid search 




