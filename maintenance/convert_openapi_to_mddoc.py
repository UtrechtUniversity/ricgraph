# ############################################################
# This script converts the openapi.yaml file that specifies the
# Ricgraph REST API to a markdown documentation file.
#
# Original version Rik D.T. Janssen, October 2024.
#
# Run it in directory 'maintenance'. It needs a template
# file that is in subdirectory 'openapi_markdown_templates'.
# Use the python in the bin directory of your virtual environment.
# ############################################################

from openapi_markdown.generator import to_markdown

# Path to your OpenAPI YAML file.
input_file = '../ricgraph_explorer/static/openapi.yaml'

# Path for the output Markdown file
output_file = '../docs/ricgraph_restapi_gendoc.md'

# Convert the OpenAPI spec to Markdown
to_markdown(api_file=input_file,
            output_file=output_file,
            templates_dir='openapi_markdown_templates')

print(f'Markdown documentation generated: {output_file}.')
