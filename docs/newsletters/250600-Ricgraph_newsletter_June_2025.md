**Subject:**	Ricgraph newsletter June 2025

**Sent:**	Wednesday, 11 June 2025 14:17

---

Dear colleague,

This newsletter tells you about some recent developments around Ricgraph. If
you would like to have a presentation or demo, or would like to discuss how
Ricgraph can help you for your specific use case, please do not hesitate to
contact me. Please feel free to share this newsletter with anyone you might
think is interested. 


**What is Ricgraph**

Ricgraph ([www.ricgraph.eu](https://www.ricgraph.eu)), 
also known as Research in context graph, enables
the exploration of researchers, teams, their results, collaborations, skills,
projects, and the relations between these items.

Ricgraph can store many types of items into a single graph. These items can be
obtained from various systems and from multiple organizations. Ricgraph
facilitates reasoning about these items because it infers new relations between
items, relations that are not present in any of the separate source systems.
Ricgraph is flexible and extensible, and can be adapted to new application
areas.


**Pilot project Open Ricgraph demo server starts in September**

In September, we will start a pilot project Open Ricgraph demo server. It aims
to demonstrate how a knowledge graph can provide insights into research
relations and collaborations, and how it can optimize the quality of research
information. This demo server will be accessible to anyone. We will focus on:

* Pilot A: Participating organizations can enrich Pure data using Ricgraph and
  BackToPure. BackToPure can insert (enrich) items from an organization that are
  absent from the Pure of that organization but are present in another source,
  back into the Pure of that organization.
* Pilot B: Participating organizations can explore collaborations between 
  sub-organizations (faculties, departments, chairs) using Ricgraph.

To read more: _Discovering insights from cross-organizational research
information and collaborations: A pilot project using Ricgraph_, Rik D.T.
Janssen (2025), 
[https://doi.org/10.5281/zenodo.15637647](https://doi.org/10.5281/zenodo.15637647). 
The Open Ricgraph demo
server will contain research information from Delft University of Technology
(thanks for making this possible!). It can also contain research information of
your organization! To learn what is necessary to accomplish this, read sections
1.6 and 1.7, and contact me.


**BackToPure to enhance an organization’s Pure**

[BackToPure](https://github.com/UtrechtUniversity/backtopure) 
is a tool designed to enhance an organization’s Research Information
System Pure by enriching its content. We use it in Pilot A above. BackToPure
can identify items (such as publications, data sets or software) that exist in
other external sources but are missing from the organization’s Pure, and then
insert (enrich) those items into Pure. The result is a more complete overview
of research at that organization. Status: experimental stage (beta).


**Chatbot to chat about research information**

A chatbot that allows you to “talk” to Ricgraph. You can formulate questions in
plain English, such as “Please give me the research results of the Geosciences
faculty of Utrecht University?” or “With what organizations does that faculty
collaborate?”. It uses a local Large Language Model. Status: planning stage
(pre-alpha).


**Ricgraph extended with topics**

A project that uses AI and Large Language Models to cluster and visualize large
amounts of research information. It assigns topics to publications, data sets,
and software. By selecting a number of topics, research results are grouped,
and possibly experts on these topics can be found. Status: planning stage
(pre-alpha).


**Exploring collaborations between (sub-)organizations of different universities**

Since the research information system Pure contains a full organization tree,
and these are inserted in Ricgraph, it is possible to find collaborations
between organizations, not only on a top level (i.e., an institution level),
but also on other levels, like faculties, departments, etc. We will explore
this in Pilot B above.

As an example, see the enclosed html file (thanks Vrije Universiteit Amsterdam
and Delft University of Techology!) 
_[not available in this newsletter archive]_. 
You will need to open it using your web
browser, because it contains JavaScript. If it doesn’t open directly, save it
to your computer, right click it, and choose something like “open with your
browser”. What you’ll see is a very first attempt to visualize collaborations
between UU, VUA, and DUT faculties for journal articles for years 2022-2025. Of
course, for each university there are many more journal articles, but this
figure is limited to journal articles that were created by authors of two or
more facutlies of UU, VUA, and DUT. You can hoover over the lines to get
numbers.


**Other recent developments**

* A tool that helps Pure administrators to clean up “external organizations” in
  Pure. Status: planning stage (pre-alpha).
* A documentation website for Ricgraph: 
  [https://docs.ricgraph.eu](https://docs.ricgraph.eu). 
* You also might want to read the reference publication: Rik D.T. Janssen
  (2024). Ricgraph: A flexible and extensible graph to explore research in
  context from various systems. SoftwareX, 26(101736).
  [https://doi.org/10.1016/j.softx.2024.101736](https://doi.org/10.1016/j.softx.2024.101736).
* Many other changes. Ricgraph is now on version v2.12. To see a full overview
  of all changes, go to the releases page:
  [https://github.com/UtrechtUniversity/ricgraph/releases](https://github.com/UtrechtUniversity/ricgraph/releases).


If you would like to have a presentation or demo, or would like to discuss how
Ricgraph can help you for your specific use case, please do not hesitate to
contact me. Please feel free to share this newsletter with anyone you might
think is interested. 

_This newsletter  has been sent to you because we have had a previous 
communication about Ricgraph. Please let me know if you would like to 
be removed from this list (or if you want to be added to it, if someone 
forwarded it to you). There will be about 2 to 3 newsletters per year about Ricgraph._

To subscribe to the newsletter email list, go to [Ricgraph Contact](../../README.md#contact).

