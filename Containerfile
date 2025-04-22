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
# - build the container on GitHub: https://github.com/UtrechtUniversity/ricgraph/actions
# - build the container locally: podman build -t ricgraph . [note the '.']
#
# - run latest version of GitHub container, and download it if you don't have it:
#   podman run --pull=newer --name ricgraph -d -p 3030:3030 ghcr.io/utrechtuniversity/ricgraph:latest
#   or: podman run --pull=newer --replace --name ricgraph -d -p 3030:3030 ghcr.io/utrechtuniversity/ricgraph:latest
#   (Ricgraph Explorer runs on port 3030)
# - run GitHub container, download it if you don't have it, and run local
#   (possibly old) version if you already have it (i.e. do not update to new version):
#   podman run --name ricgraph -d -p 3030:3030 ghcr.io/utrechtuniversity/ricgraph:latest
#   or: podman run --replace --name ricgraph -d -p 3030:3030 ghcr.io/utrechtuniversity/ricgraph:latest
# - run local container:
#   podman run --name ricgraph -d -p 3030:3030 ricgraph:latest
#   or: podman run --replace --name ricgraph -d -p 3030:3030 ricgraph:latest
#
# - stop: podman stop -a
# - status of all containers: podman ps
# - list of all containers: podman images
#
# - execute command in container: podman exec -it ricgraph [command]
#   e.g. podman exec -it ricgraph /bin/bash
#   or podman exec -it ricgraph ./harvest_multiple_sources/multiple_harvest_demo.sh
#   Note that after harvesting, you have to commit and restart the container.
# - make changes permanent in local generated container:
#   podman commit ricgraph ricgraph:latest
# - make changes permanent in GitHub generated container:
#   podman commit ricgraph ghcr.io/utrechtuniversity/ricgraph:latest
# - remove all podman containers: podman rmi -a -f
# - other useful: podman [inspect|restart|logs] ricgraph
# - the --pull flag in Podman is used to control when and how images are
#   pulled from remote registries. Options are:
#   --pull=always, --pull=newer, --pull=never.
#   For examples, see above.
#
# Note: use as least as possible RUN commands, since every RUN
# adds a layer to the container.
#
# ######################################################################

# Use the slim Python image as a base
FROM python:3.11-slim

# Set the time zone
ENV TZ="Europe/Amsterdam"

# Set container metadata according to
# OCI (Open Container Initiative) image specification.
# See https://github.com/opencontainers/image-spec/blob/main/annotations.md.
LABEL org.opencontainers.image.title=Ricgraph
LABEL org.opencontainers.image.description="Ricgraph - Research in context graph"
LABEL org.opencontainers.image.authors="Rik D.T. Janssen"
LABEL org.opencontainers.image.version=${ricgraph_version}
LABEL org.opencontainers.image.licenses=MIT
LABEL org.opencontainers.image.documentation="https://docs.ricgraph.eu"
LABEL org.opencontainers.image.source="https://github.com/UtrechtUniversity/ricgraph"
LABEL org.opencontainers.image.url="https://www.ricgraph.eu"

# This has to be an ENV instead of ARG because we use it in "CMD []" below.
ENV container_startscript=/usr/local/bin/start_services.sh

# Install and update packages.
RUN apt-get update && \
    apt-get install -y openjdk-21-jre-headless && \
    apt-get install -y wget vim make sudo && \
    apt-get clean

# Set working directory.
WORKDIR /app

# Install Neo4j and Ricgraph.
# 'systemctl_cmd=:' disables the systemctl command in the Makefile.
# The 'docs' directory is removed since it is large (mostly due to
# the videos) and we do not want a container of a large size.
RUN wget https://raw.githubusercontent.com/UtrechtUniversity/ricgraph/main/Makefile && \
    make ricgraph_server_install_dir=/app/ricgraph ask_are_you_sure=no systemctl_cmd=: full_server_install && \
    make ricgraph_server_install_dir=/app/ricgraph ask_are_you_sure=no clean && \
    rm -r ricgraph/docs && \
    cp Makefile ricgraph

# Only do this if you need to access Neo4j from outside the container.
# RUN sed -i 's/#server.default_listen_address=0.0.0.0/server.default_listen_address=0.0.0.0/' /etc/neo4j/neo4j.conf

WORKDIR ricgraph

# WARNING: DO NOT USE THIS PODMAN CONTAINER IN A PRODUCTION ENVIRONMENT.
# The container does not provide a web server (e.g. apache).
RUN echo "<p/><em>Note: you are running Ricgraph Explorer in a Podman container." >> ricgraph_explorer/static/homepage_intro.html && \
    echo "Only do this for instructional (personal) use, not for production use.</em>" >> ricgraph_explorer/static/homepage_intro.html

# Create wrapper start script.
RUN echo "#!/bin/bash" > ${container_startscript} && \
    echo "neo4j start" >> ${container_startscript} && \
    echo "bin/gunicorn --chdir /app/ricgraph/ricgraph_explorer --bind 0.0.0.0:3030 --workers 5 --worker-class uvicorn.workers.UvicornWorker ricgraph_explorer:create_ricgraph_explorer_app" >> ${container_startscript} && \
    echo "while true; do sleep 60; done" >> ${container_startscript} && \
    chmod +x ${container_startscript}

# Expose necessary ports.
# Port 3030: Ricgraph Explorer. Ports 7474 & 7687: Neo4j.
# EXPOSE 3030 7474 7687
EXPOSE 3030

CMD ["sh", "-c", "${container_startscript}"]
