# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from qiita_client import QiitaTypePlugin, QiitaArtifactType

from .validate import validate
from .summary import generate_html_summary

# Define the supported artifact types
artifact_types = [
    QiitaArtifactType('distance_matrix',
                      'Distance matrix holding pairwise distance between '
                      'samples', False, False, [('plain_text', True)]),
    QiitaArtifactType('ordination_results',
                      'Ordination results', False, False,
                      [('plain_text', True)]),
    QiitaArtifactType('alpha_vector', 'Alpha Diversity per sample results',
                      False, False, [('plain_text', True)])]

# Initialize the plugin
plugin = QiitaTypePlugin('Diversity types', '0.1.0',
                         'Diversity artifacts type plugin',
                         validate, generate_html_summary,
                         artifact_types)
