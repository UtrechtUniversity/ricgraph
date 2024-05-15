# ########################################################################
#
# Ricgraph - Research in context graph
#
# ########################################################################
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
# ########################################################################
#
# This file is the Python script file for the Ricgraph REST API.
#
# Original version Rik D.T. Janssen, May 2024.
#
# ########################################################################

import os
import sys
import connexion
from ricgraph_explorer import create_ricgraph_explorer_app

app = connexion.App(__name__, specification_dir="./static/")
app.add_api("openapi.yaml")

# RICGRAPH_PATH = '/opt/ricgraph_venv'
RICGRAPH_PATH = '/home/rik-loc/software/ricgraph'
sys.path.insert(0, RICGRAPH_PATH)
sys.path.insert(0, RICGRAPH_PATH + '/ricgraph')
sys.path.insert(0, RICGRAPH_PATH + '/ricgraph_explorer')
os.chdir(RICGRAPH_PATH + '/ricgraph_explorer')

application = create_ricgraph_explorer_app()

app.run(port=3040)
