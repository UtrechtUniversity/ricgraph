## Ricgraph videos

The following videos illustrate the possible uses of Ricgraph. 
Please note that these videos are not intended to demonstrate how an end-product 
for users would look like. They are meant to illustrate how data repositories can
be linked together and how metadata across several systems can be combined.
The videos give only a glimpse of possible use-cases. By adding more sources, 
more metadata can be harvested, and more insights can be obtained.

For these videos, Ricgraph has  harvested the following source systems:
* Utrecht University persons, organizations and research outputs from Pure;
* Utrecht University datasets
  from the data repository [Yoda](https://search.datacite.org/repositories/delft.uu);
* Utrecht University software
  from the [Research Software Directory](https://research-software-directory.org).

In the videos, you will observe nodes of several colors and sizes:
* blue nodes are persons;
* yellow nodes are journal articles;
* green nodes are datasets;
* red nodes are software;
* grey nodes are all other category nodes, such as organizations and other types of research outputs;
* small nodes are harvested from Yoda;
* medium-sized nodes are harvested from the Pure;
* large nodes are harvested from the Research Software Directory.

None of these videos have sound.

[Return to main README.md file](../README.md).

### Video Start with ORCID to find software
https://user-images.githubusercontent.com/121875841/226639991-28f279c4-17f8-49ab-8420-1676d3db2b74.mp4

This [video Start with ORCID to find 
software (45s) (click to download)](videos/ricgraph_find_software_from_orcid.mp4)
first finds the ORCID of a specific person. The ORCID is expanded to show its 
[*person-root* node, a node which "represents" a person](ricgraph_details.md#person-root-node-in-ricgraph).
Subsequently, from this node, we find three software packages from the Research
Software Directory, and we follow the link to the source system a node was harvested from.

### Video Find persons who contributed to a publication
https://user-images.githubusercontent.com/121875841/226640530-7dc59d48-4050-4390-bf2c-5e5b53849f71.mp4

In this [video Find persons who contributed to a 
publication (1m23s)](https://user-images.githubusercontent.com/121875841/226640530-7dc59d48-4050-4390-bf2c-5e5b53849f71.mp4)
we find people that have contributed to a specific publication. 
We copy and paste a DOI from a website. Then
Ricgraph shows all *person-root* nodes that it has found. From the contributors who work for Utrecht
University, we can also see their full names (for non Utrecht University contributors, this information
has not been harvested, so it cannot be shown). 
We see that one person has three (slightly) different FULL_NAMEs.

### Video Find outputs and organizations from a person
https://user-images.githubusercontent.com/121875841/226640670-0ca613b3-8a3e-4790-aa2d-41684e335159.mp4

In this [video Find outputs and organizations from 
a person (1m10s)](https://user-images.githubusercontent.com/121875841/226640670-0ca613b3-8a3e-4790-aa2d-41684e335159.mp4),
we first look up all nodes in Ricgraph that are connected to
one person, i.e. all publications, software, datasets and organizations the person has contributed to. 
Then we zoom in on the 
chair/subunit this person is a member of, and expand it to show his colleagues in the same chair/subunit.

### Video Traverse Utrecht University organizations
https://user-images.githubusercontent.com/121875841/226640771-ff5c0648-02d6-4428-8093-bf145c2ef238.mp4

In this [video Traverse Utrecht University 
organizations (1m12s)](https://user-images.githubusercontent.com/121875841/226640771-ff5c0648-02d6-4428-8093-bf145c2ef238.mp4)
we perform a top-down search in Ricgraph starting with the Pure ID of Utrecht University. 
Then we expand this node to show all its faculties. 
Next, we expand one faculty to show the people and
suborganizations that link to this faculty.

### Video Find output common to two persons
https://user-images.githubusercontent.com/121875841/226640906-7446aed6-c428-445b-b733-86b65aa7a070.mp4

This [video Find output common to two 
persons (1m5s)](https://user-images.githubusercontent.com/121875841/226640906-7446aed6-c428-445b-b733-86b65aa7a070.mp4)
demonstrates how insights can be obtained by harvesting several source systems. It shows the
relation between two individuals. First we find two persons using their last name. 
Then we let Ricgraph find the
shortest path between the two nodes. It finds one node, representing a publication. 
This means that both people have worked together on this publication.

### Video Ricgraph explorer
As mentioned, the videos in the previous sections 
demonstrate how the graph looks representing the information
in Ricgraph. This can be used to understand how nodes connect to each other.
However, for an end user this may not very useful, since it might be complicated to understand.
The [video Ricgraph explorer](videos/to_be_done.mp4)
shows how a more user centric interface may look like. We look
up a specific person with his last name and find all publications, software, datasets and organizations 
that this person has contributed to.

### Epilogue
Intrigued by the possibilities? Do you have a specific use case you would like to see? 
Don’t hestitate to contact us.

### Return to main README.md file

[Return to main README.md file](../README.md).
