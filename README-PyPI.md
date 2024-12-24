[![DOI software](https://img.shields.io/badge/DOI%20%20software-10.5281/zenodo.7524314-blue)](https://doi.org/10.5281/zenodo.7524314)
[![DOI reference publication](https://img.shields.io/badge/DOI%20reference%20publication-10.1016%2Fj.softx.2024.101736-blue)](https://doi.org/10.1016/j.softx.2024.101736)
[![website](https://img.shields.io/badge/website-www.ricgraph.eu-blue)](https://www.ricgraph.eu)  
![GitHub release date](https://img.shields.io/github/release-date/UtrechtUniversity/ricgraph?color=%234c1)
[![GitHub latest release](https://img.shields.io/github/release/UtrechtUniversity/ricgraph?color=%234c1)](https://github.com/UtrechtUniversity/ricgraph/releases)
![GitHub commits since latest release](https://img.shields.io/github/commits-since/UtrechtUniversity/ricgraph/latest?color=%234c1)
![GitHub last commit](https://img.shields.io/github/last-commit/UtrechtUniversity/ricgraph?color=%234c1)
[![PyPI version](https://img.shields.io/pypi/v/ricgraph?label=PyPI%20version&color=%234c1)](https://pypi.org/project/ricgraph)
[![PyPI downloads](https://img.shields.io/pypi/dm/ricgraph?label=PyPI%20downloads&color=%234c1)](https://pypistats.org/packages/ricgraph)  
[![Ricgraph container doc](https://img.shields.io/badge/Ricgraph_container_doc-click_here-%234c1)](https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_containerized.md)
[![Podman container version](https://ghcr-badge.egpl.dev/utrechtuniversity/ricgraph/latest_tag?color=%234c1&label=container+version)](https://github.com/utrechtuniversity/ricgraph/pkgs/container/ricgraph)  
[![GitHub license](https://img.shields.io/github/license/UtrechtUniversity/ricgraph?color=%234c1)](LICENSE)
[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![Technology Readiness Level 7/9 - Release Candidate - Technology ready enough and in initial use by end-users in intended scholarly environments](https://w3id.org/research-technology-readiness-levels/Level7ReleaseCandidate.svg)](https://github.com/CLARIAH/clariah-plus/blob/main/requirements/software-metadata-requirements.md#15--you-should-express-a-technology-readiness-level)
[![FAIR checklist badge](https://fairsoftwarechecklist.net/badge.svg)](https://fairsoftwarechecklist.net/v0.2?f=31&a=32113&i=32110&r=123)

<!---
Note, the lines 'Website' and
'PyPI downloads' end in two spaces, to force a line break but not a paragraph break.
Similar for others.
We use color=#4c1 (green), that color is used by the 'repo status' badge.
Documentation about the Podman badges can be found here: https://github.com/eggplants/ghcr-badge.
--->

<img alt="Ricgraph logo" src="https://raw.githubusercontent.com/UtrechtUniversity/ricgraph/refs/heads/main/docs/images/ricgraph_logo.png" height="30"> 

# Ricgraph - Research in context graph 

## What is Ricgraph?

Ricgraph, also known as Research in context graph, enables the exploration of researchers, 
teams, their results,
collaborations, skills, projects, and the relations between these items.

Ricgraph can store many types of items into a single graph. 
These items can be obtained from various systems and from
multiple organizations. Ricgraph facilitates reasoning about these 
items because it infers new relations between items,
relations that are not present in any of the separate source systems. 
It is flexible and extensible, and can be
adapted to new application areas.

### Motivation

Ricgraph, also known as Research in context graph, is software that is about
relations between items. These items can be collected from various source 
systems and from multiple organizations. We
explain how Ricgraph works by applying it to the application area 
*research information*. We show the insights that can be
obtained by combining information from various source systems, 
insight arising from new relations that are not present
in each separate source system.

*Research information* is about anything related to research: research 
results, the persons in a research team, their
collaborations, their skills, projects in which they have 
participated, as well as the relations between these entities.
Examples of *research results* are publications, data sets, and software.

Example use cases from the application area research information are:

| Use case                                                                                                                                                                                                                                                        | In Ricgraph                                                                                                                   |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| As a journalist, I want to find researchers with a certain skill S and their publications, so that I can interview them for a newspaper article. Example skills can be: *climate change* or *stem cells*.                                                       | <img src="https://raw.githubusercontent.com/UtrechtUniversity/ricgraph/main/docs/images/journalist-use-case.jpg" width="700"> |
| As a librarian, I want to enrich my local research information system with research results from person A that are in other systems (in orange, *RIS2*) but not in ours (in green, *RIS1*), so that we have a more complete view of research at our university. | <img src="https://raw.githubusercontent.com/UtrechtUniversity/ricgraph/main/docs/images/librarian-use-case.jpg" width="700">  |
| As a researcher A, I want to find researchers from other universities that have co-authored publications written by the co-authors of my own publications, so that I can read their publications to find out if we share common research interests.             | <img src="https://raw.githubusercontent.com/UtrechtUniversity/ricgraph/main/docs/images/researcher-use-case.jpg" width="700"> |


These use cases use different types of information (called *items*):
researchers, skills, publications,
etc. Most often, these types of information are not stored in 
one system, so the use cases may be difficult or
time-consuming to answer. However, by using Ricgraph, these 
use cases (and many others) are easy to answer, as will be
explained throughout this documentation.

Although this documentation illustrates Ricgraph in the application area 
research information, the principle “relations
between items from various source systems” is general, 
so Ricgraph can be used in other application areas.

### Main contributions of Ricgraph

* Ricgraph can store many types of items in a single graph.
* Ricgraph harvests multiple source systems into a single graph.
* Ricgraph Explorer is the exploration tool for Ricgraph.
* Ricgraph facilitates reasoning about items because it infers new relations between items.
* Ricgraph can be tailored for an application area.

### Read more about Ricgraph

For a gentle introduction in Ricgraph, read the reference publication: 
Rik D.T. Janssen (2024). Ricgraph: A flexible and extensible graph to explore research in
context from various systems. *SoftwareX*, 26(101736).
https://doi.org/10.1016/j.softx.2024.101736.

You might also want to read the documentation in 
the [Ricgraph GitHub repository](https://github.com/UtrechtUniversity/ricgraph).
To use Ricgraph, installing the [Ricgraph package from PyPI](https://pypi.org/project/ricgraph) 
is not sufficient. Please read the
installation instructions in the Ricgraph GitHub repository.
