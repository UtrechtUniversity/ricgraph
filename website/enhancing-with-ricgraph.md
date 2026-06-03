# Enhance research information systems with Ricgraph


## Introduction

Using Ricgraph in combination with
[BackToPure](https://github.com/UtrechtUniversity/BackToPure/tree/jobs-orientied),
you can enhance an organization's
[Research Information System Pure](https://www.elsevier.com/solutions/pure)
by enriching its content. BackToPure can identify items
(such as publications, data sets or software)
that exist in other external sources but are missing from the organization's Pure,
and then insert (enrich) those items into Pure.
The result is a more complete overview of research at that organization.

In an image, this looks as follows:

<img src="images/backtopure-for-uva.png" alt="BackToPure and Ricgraph for UvA" width="70%">

Suppose your organization is UvA (Universiteit van Amsterdam), and you would
like to enhance your Pure (Pure UvA). 
Suppose the Pure system of another organization, Pure AUMC (Amsterdam University
Medical Centers) has also been harvested in Ricgraph. 
Also, OpenAlex for both UvA en AUMC has been harvested in Ricgraph.
Ricgraph is depicted as the bottom right cloud.

Then, Ricgraph and BackToPure will find research results and IDs
from Pure AUMC and from OpenAlex UvA, that are relevant for UvA,
but are not in Pure UvA.
BackToPure will feed those back into Pure UvA via the blue box "enrichments".

## How to do this?

For this to work, you will need either 

* the REST API of the Open Ricgraph demo server, and
  your organization has to be included in the Open Ricgraph demo server, or
* your own installation of Ricgraph, where you have harvested sources relevant
  for your organization.

and a local BackToPure installation.

If you would like to do this, please contact us
using the [contact page](contact.md).

## Next steps
Read about using or participating in Ricgraph
with the [Pilot project Open Ricgraph demo 
server](pilot-project-open-ricgraph-demo-server.md).
Go to the [Contact page](contact.md).
