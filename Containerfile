# ######################################################################
# 
# MIT License
# 
# Copyright (c) 2024, 2025 Rik D.T. Janssen
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
# Updated Rik D.T. Janssen, January 2025.
#
# ######################################################################
#
# This Containerfile produces a Podman container that runs both 
# Neo4j Community Edition and Ricgraph. You can run a harvest
# script and then explore the results using Ricgraph Explorer.
# Ricgraph Explorer runs on port 3030.
# To use it, go to http://127.0.0.1:3030 (the actual port number
# depends on your 'podman run' command).
#
# You might want to modify the version numbers below.
#
# The results of an harvest are NOT stored in a separate volume
# on the host, but they are stored inside the container. This
# is a design decision. This means, that after harvest, you have
# to "add" (commit) the harvest results to the container (i.e. make the
# changes permanent to the container). See below.
#
# WARNING: DO NOT USE THIS PODMAN CONTAINER IN A PRODUCTION ENVIRONMENT.
# It is meant for instructional (personal) use only, as a demonstrator
# for Ricgraph. This container does not provide a web server (e.g. apache).
# If you want to use Ricgraph in a production environment, install it
# as a server, please read 
# https://github.com/UtrechtUniversity/ricgraph/blob/main/docs/ricgraph_as_server.md
#
# Possible Podman commands:
# - build the container locally: podman build -t ricgraph . [note the '.']
# - build the container on GitHub: https://github.com/UtrechtUniversity/ricgraph/actions
# - get the container from GitHub (not necessary if you
#   use the container ghcr.io/utrechtuniversity/ricgraph:latest):
#   podman pull ghcr.io/utrechtuniversity/ricgraph:latest
# - run local container:
#   podman run --name ricgraph -d -p 3030:3030 ricgraph:latest
#   (Ricgraph Explorer runs on port 3030)
#   or: podman run --replace --name ricgraph -d -p 3030:3030 ricgraph:latest
# - run GitHub container (will also download it if you don't have it):
#   podman run --name ricgraph -d -p 3030:3030 ghcr.io/utrechtuniversity/ricgraph:latest
#   or: podman run --replace --name ricgraph -d -p 3030:3030 ghcr.io/utrechtuniversity/ricgraph:latest
# - run GitHub container, but use the local, possibly old, version
#   and do not retrieve a new version:
#   podman run --pull=never --name ricgraph -d -p 3030:3030 ghcr.io/utrechtuniversity/ricgraph:latest
#   or: podman run --pull=never --replace --name ricgraph -d -p 3030:3030 ghcr.io/utrechtuniversity/ricgraph:latest
# - stop: podman stop -a
# - status of all containers: podman ps
# - list of all containers: podman images
# - get latest version of all containers: podman auto-update
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
# Note: use as least as possible RUN commands, since every RUN
# adds a layer to the container.
#
# ######################################################################

# Use the slim Python image as a base
FROM python:3.11-slim

# Set the time zone
ENV TZ="Europe/Amsterdam"

# General args
ARG ricgraph_version=2.7
ARG neo4j_community_version=5.24.0

# Set container metadata according to
# OCI (Open Container Initiative) image specification.
# See https://github.com/opencontainers/image-spec/blob/main/annotations.md.
LABEL org.opencontainers.image.title=Ricgraph
LABEL org.opencontainers.image.description="Ricgraph - Research in context graph"
LABEL org.opencontainers.image.authors="Rik D.T. Janssen"
LABEL org.opencontainers.image.version=${ricgraph_version}
LABEL org.opencontainers.image.licenses=MIT
LABEL org.opencontainers.image.documentation="https://github.com/UtrechtUniversity/ricgraph/blob/main/README.md"
LABEL org.opencontainers.image.source="https://github.com/UtrechtUniversity/ricgraph"
LABEL org.opencontainers.image.url="https://www.ricgraph.eu"

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

# This has to be an ENV instead of ARG because we use it in "CMD []" below.
ENV container_startscript=/usr/local/bin/start_services.sh

# Install and update packages & Neo4j Community Edition.
# The neo4j-admin command sets the Neo4j DB password to a string that can be
# observed using 'podman inspect'.
# WARNING: This might not be a good idea for production use.
# This can only be done if you have not started Neo4j yet.
RUN apt-get update && \
    apt-get install -y wget vim && \
    wget -O /tmp/package_tempfile.deb ${neo4j_cyphershell_path} && \
    apt-get install -y /tmp/package_tempfile.deb && \
    wget -O /tmp/package_tempfile.deb ${neo4j_community_path} && \
    apt-get install -y /tmp/package_tempfile.deb && \
    rm /tmp/package_tempfile.deb && \
    apt-get clean && \
    /bin/neo4j-admin dbms set-initial-password SecretPassword

# Only do this if you need to access Neo4j from outside the container.
# RUN sed -i 's/#server.default_listen_address=0.0.0.0/server.default_listen_address=0.0.0.0/' /etc/neo4j/neo4j.conf

# Set working directory
WORKDIR /app

# Install Ricgraph
RUN wget -O /tmp/ricgraph_tempfile.tar.gz ${ricgraph_path} && \
    tar -zxvf /tmp/ricgraph_tempfile.tar.gz && \
    rm /tmp/ricgraph_tempfile.tar.gz && \
    mv ricgraph-${ricgraph_version} ricgraph && \
    ln -s ricgraph ricgraph-${ricgraph_version}

WORKDIR ricgraph

# Note the setting of the fixed Neo4j password that has been defined above.
# The 'docs' directory is removed since it is large (mostly due to
# the videos) and we do not want a container of a large size.
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -r docs && \
    cp ricgraph.ini-sample ricgraph.ini && \
    sed -i 's/^graphdb_password =/graphdb_password = SecretPassword/' ricgraph.ini && \
    sed -i 's/^graphdb_scheme = bolt/###graphdb_scheme = bolt/' ricgraph.ini && \
    sed -i 's/^graphdb_port = 7687/###graphdb_port = 7687/' ricgraph.ini && \
    sed -i 's/^#graphdb_scheme = neo4j/graphdb_scheme = neo4j/' ricgraph.ini && \
    sed -i 's/^#graphdb_port = 7687/graphdb_port = 7687/' ricgraph.ini && \
    mv ricgraph.ini /usr/local

# WARNING: DO NOT USE THIS PODMAN CONTAINER IN A PRODUCTION ENVIRONMENT.
# The container does not provide a web server (e.g. apache).
RUN echo "<p/><em>Note: you are running Ricgraph Explorer in a Podman container." >> ricgraph_explorer/static/homepage_intro.html && \
    echo "Only do this for instructional (personal) use, not for production use.</em>" >> ricgraph_explorer/static/homepage_intro.html

# Create wrapper start script
RUN echo "#!/bin/bash" > ${container_startscript} && \
    echo "neo4j start" >> ${container_startscript} && \
    echo "gunicorn --chdir /app/ricgraph/ricgraph_explorer --bind 0.0.0.0:3030 --workers 5 --worker-class uvicorn.workers.UvicornWorker ricgraph_explorer:create_ricgraph_explorer_app" >> ${container_startscript} && \
    echo "while true; do sleep 60; done" >> ${container_startscript} && \
    chmod +x ${container_startscript}

# Expose necessary ports.
# Port 3030: Ricgraph Explorer. Ports 7474 & 7687: Neo4j.
# EXPOSE 3030 7474 7687
EXPOSE 3030

# Go to the directory with the harvest scripts. Then we can harvest
# from outside the container using e.g. 
# podman exec -it ricgraph python batch_harvest.py
WORKDIR harvest

CMD ["sh", "-c", "${container_startscript}"]
