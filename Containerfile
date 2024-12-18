# ######################################################################
# 
# MIT License
# 
# Copyright (c) 2024 Rik D.T. Janssen
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# ######################################################################
# 
# Original version Rik D.T. Janssen, December 2024.
#
# ######################################################################
#
# This Containerfile produces a Podman container that runs both 
# Neo4j Community Edition and Ricgraph. You might want to modify 
# the version numbers below.
# Ricgraph Explorer runs on internal port 3030, external port 8092.
# To use it, go to http://127.0.0.1:8092.
#
# WARNING: DO NOT USE THIS PODMAN CONTAINER IN A PRODUCTION ENVIRONMENT.
# It is meant for instructional (personal) use only, as a demonstrator
# for Ricgraph.
# This is because it exposes Ricgraph Explorer in a insecure way.
# If you want to use Ricgraph in a production environment, install it
# as a server, please read 
# https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_as_server.md
#
# Possible Podman commands:
# - build the container locally: podman build -t ricgraph . [note the '.']
# - build the container on GitHub: https://github.com/UtrechtUniversity/ricgraph/actions
# - get the container from GitHub:
#   podman pull ghcr.io/utrechtuniversity/ricgraph:latest
# - run locally generated container:
#   podman run --name ricgraph -d -p 8092:3030 ricgraph:latest
#   (Ricgraph Explorer runs on internal port 3030, external port 8092)
#   or: podman run --replace --name ricgraph -d -p 8092:3030 ricgraph:latest
# - run GitHub generated container:
#   podman run --name ricgraph -d -p 8092:3030 ghcr.io/utrechtuniversity/ricgraph:latest
#   or: podman run --replace --name ricgraph -d -p 8092:3030 ghcr.io/utrechtuniversity/ricgraph:latest
# - stop: podman stop -a
# - status of all containers: podman ps
# - list of all containers: podman images
# - remove all podman containers: podman rmi -a -f
# - other useful: podman [inspect|restart|logs] ricgraph
# - execute command in container: podman exec -it ricgraph [command]
#   e.g. podman exec -it ricgraph /bin/bash
#   or podman exec -it ricgraph python batch_harvest.py
#   Note that after harvesting, you have to commit and restart the container.
# - make changes permanent in locally generated container:
#   podman commit ricgraph ricgraph:latest
# - make changes permanent in GitHub generated container:
#   podman commit ricgraph ghcr.io/utrechtuniversity/ricgraph:latest
#
# ######################################################################

# Use the slim Python image as a base
FROM python:3.11-slim

# General args
ARG ricgraph_version=2.7
ARG neo4j_community_version=5.24.0

# Ricgraph paths
ARG ricgraph_download=https://github.com/UtrechtUniversity/ricgraph
ARG ricgraph_path=${ricgraph_download}/archive/refs/tags/v${ricgraph_version}.tar.gz

# Neo4j paths
ARG neo4j_download=https://dist.neo4j.org
ARG neo4j_cyphershell_path=${neo4j_download}/cypher-shell/cypher-shell_${neo4j_community_version}_all.deb
ARG neo4j_community_path=${neo4j_download}/deb/neo4j_${neo4j_community_version}_all.deb
# We need these since Containerfile cannot deal easily with 'basename'.
ARG neo4j_cyphershell=cypher-shell_${neo4j_community_version}_all.deb
ARG neo4j_community=neo4j_${neo4j_community_version}_all.deb

# Misc variables, these are files in the container
ARG package_tempfile=/tmp/package_tempfile.deb
ARG ricgraph_tempfile=/tmp/ricgraph_tempfile.tar.gz
# This has to be an ENV instead of ARG because we use it in "CMD []" below
ENV container_startscript=/usr/local/bin/start_services.sh

# Install and update packages & Neo4j Community Edition
RUN apt-get update
RUN apt-get install -y wget vim
RUN wget -O ${package_tempfile} ${neo4j_cyphershell_path}
RUN apt-get install -y ${package_tempfile}
RUN wget -O ${package_tempfile} ${neo4j_community_path}
RUN apt-get install -y ${package_tempfile}
RUN rm ${package_tempfile}

# Set the Neo4j DB password. 
# This can only be done if you have not started Neo4j yet.
RUN /bin/neo4j-admin dbms set-initial-password SecretPassword

# Only do this if you need to access Neo4j from outside the container.
# RUN sed -i 's/#server.default_listen_address=0.0.0.0/server.default_listen_address=0.0.0.0/' /etc/neo4j/neo4j.conf

# Set working directory
WORKDIR /app

# Install Ricgraph
RUN wget $ricgraph_path -O ${ricgraph_tempfile}
RUN tar -zxvf ${ricgraph_tempfile}
RUN rm ${ricgraph_tempfile}

WORKDIR ricgraph-${ricgraph_version}
RUN pip install --no-cache-dir -r requirements.txt
RUN cp ricgraph.ini-sample ricgraph.ini
# Note: Neo4j password has been set above
RUN sed -i 's/^graphdb_password =/graphdb_password = SecretPassword/' ricgraph.ini
RUN sed -i 's/^graphdb_scheme = bolt/###graphdb_scheme = bolt/' ricgraph.ini
RUN sed -i 's/^graphdb_port = 7687/###graphdb_port = 7687/' ricgraph.ini
RUN sed -i 's/^#graphdb_scheme = neo4j/graphdb_scheme = neo4j/' ricgraph.ini
RUN sed -i 's/^#graphdb_port = 7687/graphdb_port = 7687/' ricgraph.ini
RUN mv ricgraph.ini /usr/local

# WARNING: DO NOT USE THIS PODMAN CONTAINER IN A PRODUCTION ENVIRONMENT.
# Make Ricgraph Explorer accessible from anywhere.
RUN sed -i 's/ricgraph_explorer.run(port=3030)/ricgraph_explorer.run(host="0.0.0.0", port=3030)/' ricgraph_explorer/ricgraph_explorer.py
RUN echo "<p/><em>Note: you are running Ricgraph Explorer in a Podman container." >> ricgraph_explorer/static/homepage_intro.html
RUN echo "Only do this for instructional (personal) use, not for production use.</em>" >> ricgraph_explorer/static/homepage_intro.html

# Create wrapper start script
RUN echo "#!/bin/bash" > ${container_startscript}
RUN echo "neo4j start" >> ${container_startscript}
RUN echo "python /app/ricgraph-${ricgraph_version}/ricgraph_explorer/ricgraph_explorer.py" >> ${container_startscript}
RUN echo "while true; do sleep 60; done" >> ${container_startscript}
RUN chmod +x ${container_startscript}

# Expose necessary ports.
# Port 3030: Ricgraph Explorer. Ports 7474 & 7687: Neo4j.
# EXPOSE 3030 7474 7687
EXPOSE 3030

# Go to the directory with the harvest scripts. Then we can harvest
# from outside the container using e.g. 
# podman exec -it ricgraph python batch_harvest.py
WORKDIR harvest

CMD ["sh", "-c", "${container_startscript}"]

