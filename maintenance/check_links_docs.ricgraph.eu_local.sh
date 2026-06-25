#!/bin/bash
# ############################################################
# Check whether all the internal and external links of the
# Ricgraph website docs.ricgraph.eu (local) are satisfied.
#
# For more information see the linkchecker module conf file
# ricgraph_linkchecker.conf in this directory.
#
# Original version Rik D.T. Janssen, June 2026.
# ############################################################

linkchecker --config=ricgraph-linkchecker.conf ../../ricgraph-documentation/build_documentation/index.html

echo ""
echo "For the errors or warnings reported above,"
echo "note that links that go through Cloudflare and the like"
echo "will be reported as errors. They will report"
echo "'Result Error: 403 Forbidden', while they are correct."
echo "This happens e.g. for DOI links."
echo ""
