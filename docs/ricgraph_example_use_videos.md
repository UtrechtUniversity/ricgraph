## Ricgraph videos

The following videos illustrate the possible uses of Ricgraph. 
These are not intended to demonstrate how an interface
for users would look like, they are meant to illustrate how data repositories can
be linked together and how metadata across several systems can be combined.
The videos only give a glimpse of possible use-cases. By adding more sources, 
more metadata can be harvested, and more insights can be obtained.

For these videos, Ricgraph has harvested the following source systems:
* Utrecht University persons, organizations and research outputs from Pure;
* Utrecht University data sets
  from the data repository [Yoda](https://search.datacite.org/repositories/delft.uu);
* Utrecht University software
  from the [Research Software Directory](https://research-software-directory.org).

In the videos, you will observe nodes of several colors and sizes:
* blue nodes indicate persons;
* yellow nodes indicate journal articles;
* green nodes indicate data sets;
* red nodes indicate software;
* grey nodes indicate all other category nodes, such as organizations and other types of research outputs;
* small nodes are harvested from Yoda;
* medium-sized nodes are harvested from the Pure;
* large nodes are harvested from the Research Software Directory.

None of these videos have sound.

For other illustrations of Ricgraph, see the
[publications](ricgraph_pubs_pres_news_use_ment#ricgraph-publications),
[presentations](ricgraph_pubs_pres_news_use_ment#ricgraph-presentations),
[newsletters](ricgraph_pubs_pres_news_use_ment#ricgraph-newsletters)
(to subscribe, go to [Ricgraph Contact](../README.md#contact)),
[use](ricgraph_pubs_pres_news_use_ment#ricgraph-use), and
[mentions](ricgraph_pubs_pres_news_use_ment#ricgraph-mentions)
of Ricgraph.

[Return to main README.md file](../README.md).

### Video Start with ORCID to find software
https://user-images.githubusercontent.com/121875841/226639991-28f279c4-17f8-49ab-8420-1676d3db2b74.mp4

This [video Start with ORCID to find 
software (45s) (click to download)](videos/ricgraph_find_software_from_orcid.mp4)
first finds the ORCID of a specific person. The ORCID is expanded to show its 
[*person-root* node, a node which "represents" a person](ricgraph_details.md#person-root-node-in-ricgraph).
Subsequently, from this node, we find three software packages from the Research
Software Directory. In a next step we follow the link to the source system a node was harvested from.

### Video Find persons who contributed to a publication
https://user-images.githubusercontent.com/121875841/226640530-7dc59d48-4050-4390-bf2c-5e5b53849f71.mp4

In this [video Find persons who contributed to a 
publication (1m23s) (click to download)](videos/ricgraph_find_persons_who_contributed_to_output.mp4)
we find people that have contributed to a specific publication. 
We copy and paste a DOI from a website. Then
Ricgraph shows all *person-root* nodes that it has found. From the contributors who work for Utrecht
University, we can also see their full names. 
We see that one person has three (slightly) different FULL_NAMEs.
For non Utrecht University contributors, this information
has not been harvested, so it cannot be shown. 

### Video Find outputs and organizations from a person
https://user-images.githubusercontent.com/121875841/226640670-0ca613b3-8a3e-4790-aa2d-41684e335159.mp4

In this [video Find outputs and organizations from 
a person (1m10s) (click to download)](videos/ricgraph_find_outputs_and_organizations_from_person.mp4),
we first look up all nodes in Ricgraph that are connected to
one person, i.e. publications, software and data sets the person has contributed to, 
and organizations the person is a member of.
Then we zoom in on the 
chair/subunit this person is a member of, and expand it to show his colleagues in the same chair/subunit.

### Video Traverse Utrecht University organizations
https://user-images.githubusercontent.com/121875841/226640771-ff5c0648-02d6-4428-8093-bf145c2ef238.mp4

In this [video Traverse Utrecht University 
organizations (1m12s) (click to download)](videos/ricgraph_traverse_uu_organizations.mp4)
we do a top-down search in Ricgraph starting with the Pure ID of Utrecht University. 
Then we expand this node to show all Utrecht University faculties. 
Next, we expand one faculty to show the people and
sub organizations that link to this faculty.

### Video Find output common to two persons
https://user-images.githubusercontent.com/121875841/226640906-7446aed6-c428-445b-b733-86b65aa7a070.mp4

This [video Find output common to two 
persons (1m5s) (click to download)](videos/ricgraph_find_output_common_to_2_persons.mp4)
demonstrates how insights can be obtained by harvesting several source systems. It shows the
relation between two individuals. First we find two persons using their last name. 
Then we let Ricgraph find the
shortest path between the two nodes. It finds one node, representing a publication. 
This means that both people have worked together on this publication.

### Video Ricgraph Explorer
https://user-images.githubusercontent.com/121875841/228465992-993dc8ec-0bd9-4985-b2d9-3200f50d558b.mp4

As mentioned, the videos in the previous sections 
show how the graph looks like that represents the information
in Ricgraph. This can be used to understand how nodes connect to each other.
However, for an end user it might be complicated to use the correct
search queries. Also, expanding nodes may result in a lot of nodes, so the user might
get confused what there is to be learned. That is why we have made 
[Ricgraph Explorer](ricgraph_explorer.md).

The [video Ricgraph Explorer (2m20s) (click to download)](videos/ricgraph_ricgraph_explorer.mp4)
shows how a more user-centric interface may look like. 
This video uses Ricgraph Explorer from March 2023.
In this video, we look
up a specific person with his last name. As can be observed, there are three *FULL_NAME*
nodes
for this person, each with a different spelling, from four different sources we have
harvested. 
If we click on one of them, we observe that we have found a lot of information about
this person. 

The first table shows the node used for the search.
The second table displays the IDs of the person found, connected to the *person-root*
node, and the third table shows all other nodes connected to the *person-root* node.
This includes research outputs like publications, data sets and software, as well as
the (sub)organization this person works. We can sort columns, and we can use 
faceted navigation (i.e. filter on *name* or *category* nodes).

### Epilogue
Intrigued by the possibilities? Do you have a specific use case you would like to see? 
Don’t hesitate to contact us.

### Return to main README.md file

[Return to main README.md file](../README.md).
