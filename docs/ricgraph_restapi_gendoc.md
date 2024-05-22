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

## Path Table

| Method | Path | Description |
| --- | --- | --- |
| GET | [/person/search](#getpersonsearch) | Search for a person |
| GET | [/person/all_information](#getpersonall_information) | Show all information related to this person |
| GET | [/person/share_research_results](#getpersonshare_research_results) | Find persons that share any share research result types with this person |
| GET | [/person/collaborating_organizations](#getpersoncollaborating_organizations) | Find organizations that this person collaborates with |
| GET | [/person/enrich](#getpersonenrich) | Find information harvested from other source systems, not present in this source system |
| GET | [/organization/search](#getorganizationsearch) | Search for a (sub-)organization |
| GET | [/organization/all_information](#getorganizationall_information) | Show all information related to this organization |
| GET | [/organization/information_persons_results](#getorganizationinformation_persons_results) | Find any information from persons or their results in this organization |
| GET | [/competence/search](#getcompetencesearch) | Search for a skill, expertise area or research area |
| GET | [/competence/all_information](#getcompetenceall_information) | Show all information related to this competence |
| GET | [/broad_search](#getbroad_search) | Search for anything (broad search) |
| GET | [/advanced_search](#getadvanced_search) | Advanced search |
| GET | [/get_all_personroot_nodes](#getget_all_personroot_nodes) | Find all person-root nodes of this node |
| GET | [/get_all_neighbor_nodes](#getget_all_neighbor_nodes) | Find all neighbor nodes of this node |

## Reference Table

| Name | Path | Description |
| --- | --- | --- |
| name | [#/components/parameters/name](#componentsparametersname) | Search for a value in Ricgraph field *name* |
| category | [#/components/parameters/category](#componentsparameterscategory) | Search for a value in Ricgraph field *category* |
| value | [#/components/parameters/value](#componentsparametersvalue) | Search for a value in Ricgraph field *value* |
| key | [#/components/parameters/key](#componentsparameterskey) | Search for a value in Ricgraph field *_key* |
| max_nr_items | [#/components/parameters/max_nr_items](#componentsparametersmax_nr_items) | The maximum number of items to return, or 0 to return all items |
| source_system | [#/components/parameters/source_system](#componentsparameterssource_system) | The name of the source system you would like to enrich |
| name_want | [#/components/parameters/name_want](#componentsparametersname_want) | Return only neighbor nodes whose field *name* matches any value in the provided list; if the list is empty, return all neighbor nodes regardless of their field *name* |
| name_dontwant | [#/components/parameters/name_dontwant](#componentsparametersname_dontwant) | Return only neighbor nodes whose field *name* does *not* match any value in the provided list; if the list is empty, return all neighbor nodes regardless of their field *name* |
| category_want | [#/components/parameters/category_want](#componentsparameterscategory_want) | Return only neighbor nodes whose field *category* matches any value in the provided list; if the list is empty, return all neighbor nodes regardless of their field *category* |
| category_dontwant | [#/components/parameters/category_dontwant](#componentsparameterscategory_dontwant) | Return only neighbor nodes whose field *category* does *not* match any value in the provided list; if the list is empty, return all neighbor nodes regardless of their field *category* |

## Path Details

***

### [GET]/person/search

- Summary  
Search for a person

#### Parameters(Query)

```ts
value?: string
```

```ts
max_nr_items?: string //default: 250
```

#### Responses

- 200 OK

- 250 Nothing found

- 251 Invalid search

***

### [GET]/person/all_information

- Summary  
Show all information related to this person

#### Parameters(Query)

```ts
key: string
```

```ts
max_nr_items?: string //default: 250
```

#### Responses

- 200 OK

- 250 Nothing found

- 251 Invalid search

***

### [GET]/person/share_research_results

- Summary  
Find persons that share any share research result types with this person

#### Parameters(Query)

```ts
key: string
```

```ts
max_nr_items?: string //default: 250
```

#### Responses

- 200 OK

- 250 Nothing found

- 251 Invalid search

***

### [GET]/person/collaborating_organizations

- Summary  
Find organizations that this person collaborates with

- Description  
With this call you will get an overview of organizations that his person collaborates with. A person *X* from organization *A* collaborates with a person *Y* from organization *B* if *X* and *Y* have both contributed to the same research result.

#### Parameters(Query)

```ts
key: string
```

```ts
max_nr_items?: string //default: 250
```

#### Responses

- 200 OK

- 250 Nothing found

- 251 Invalid search

***

### [GET]/person/enrich

- Summary  
Find information harvested from other source systems, not present in this source system

- Description  
The process of improving or enhancing information in a source system is called *enriching* that source system. This is only possible if you have harvested more than one source system. By using information found in one or more other harvested systems, information in this source system can be improved or enhanced. With this call you can enter a name of one of your source systems. Ricgraph will show what information can be added to this source system, based on the information harvested from other source systems.

#### Parameters(Query)

```ts
key: string
```

```ts
source_system: string
```

```ts
max_nr_items?: string //default: 250
```

#### Responses

- 200 OK

- 250 Nothing found

- 251 Invalid search

***

### [GET]/organization/search

- Summary  
Search for a (sub-)organization

#### Parameters(Query)

```ts
value?: string
```

```ts
max_nr_items?: string //default: 250
```

#### Responses

- 200 OK

- 250 Nothing found

- 251 Invalid search

***

### [GET]/organization/all_information

- Summary  
Show all information related to this organization

#### Parameters(Query)

```ts
key: string
```

```ts
max_nr_items?: string //default: 250
```

#### Responses

- 200 OK

- 250 Nothing found

- 251 Invalid search

***

### [GET]/organization/information_persons_results

- Summary  
Find any information from persons or their results in this organization

#### Parameters(Query)

```ts
key: string
```

```ts
max_nr_items?: string //default: 250
```

#### Responses

- 200 OK

- 250 Nothing found

- 251 Invalid search

***

### [GET]/competence/search

- Summary  
Search for a skill, expertise area or research area

#### Parameters(Query)

```ts
value?: string
```

```ts
max_nr_items?: string //default: 250
```

#### Responses

- 200 OK

- 250 Nothing found

- 251 Invalid search

***

### [GET]/competence/all_information

- Summary  
Show all information related to this competence

#### Parameters(Query)

```ts
key: string
```

```ts
max_nr_items?: string //default: 250
```

#### Responses

- 200 OK

- 250 Nothing found

- 251 Invalid search

***

### [GET]/broad_search

- Summary  
Search for anything (broad search)

#### Parameters(Query)

```ts
value?: string
```

```ts
max_nr_items?: string //default: 250
```

#### Responses

- 200 OK

- 250 Nothing found

- 251 Invalid search

***

### [GET]/advanced_search

- Summary  
Advanced search

- Description  
The fields you enter are case-sensitive and use exact match search. If you enter values in more than one field, these fields are combined using AND.

#### Parameters(Query)

```ts
name?: string
```

```ts
category?: string
```

```ts
value?: string
```

```ts
max_nr_items?: string //default: 250
```

#### Responses

- 200 OK

- 250 Nothing found

- 251 Invalid search

***

### [GET]/get_all_personroot_nodes

- Summary  
Find all person-root nodes of this node

#### Parameters(Query)

```ts
key: string
```

```ts
max_nr_items?: string //default: 250
```

#### Responses

- 200 OK

- 250 Nothing found

- 251 Invalid search

***

### [GET]/get_all_neighbor_nodes

- Summary  
Find all neighbor nodes of this node

#### Parameters(Query)

```ts
key: string
```

```ts
name_want?: string[]
```

```ts
name_dontwant?: string[]
```

```ts
category_want?: string[]
```

```ts
category_dontwant?: string[]
```

```ts
max_nr_items?: string //default: 250
```

#### Responses

- 200 OK

- 250 Nothing found

- 251 Invalid search

## References

### #/components/parameters/name

```ts
name?: string
```

### #/components/parameters/category

```ts
category?: string
```

### #/components/parameters/value

```ts
value?: string
```

### #/components/parameters/key

```ts
key: string
```

### #/components/parameters/max_nr_items

```ts
max_nr_items?: string //default: 250
```

### #/components/parameters/source_system

```ts
source_system: string
```

### #/components/parameters/name_want

```ts
name_want?: string[]
```

### #/components/parameters/name_dontwant

```ts
name_dontwant?: string[]
```

### #/components/parameters/category_want

```ts
category_want?: string[]
```

### #/components/parameters/category_dontwant

```ts
category_dontwant?: string[]
```
