# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from os.path import join, basename
from urllib.parse import quote
from base64 import b64encode
from io import BytesIO
from json import dumps
from os import makedirs

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from emperor import Emperor
from skbio import OrdinationResults, DistanceMatrix, TreeNode
from scipy.cluster.hierarchy import linkage
from qiita_client.util import system_call
from qiime2 import Visualization


DM_HTML = """<b>Number of samples:</b> %d</br>
<b>Minimum distance:</b> %.4f<br/>
<b>Maximum distance:</b> %.4f<br/>
<b>Mean distance:</b> %.4f<br/>
<b>Median distance:</b> %.4f<br/>
<br/><hr/><br/>
<img src = "%s"/>"""

Q2_INDEX = """<!DOCTYPE html>
<html>
  <body>
    <iframe src="./support_files/%s" width="100%%" height="850" frameborder=0>
    </iframe>
  </body>
</html>"""


def _generate_distance_matrix_summary(files, metadata, out_dir):
    # Magic number [0] -> there is only one plain text file which is
    # the distance matrix
    dm = DistanceMatrix.read(files['plain_text'][0])
    data = dm.condensed_form()

    # Generate a heatmap with the distance matrix
    # The sorting in the heatmap is going to be based in hierarchical
    # clustering.
    tree = TreeNode.from_linkage_matrix(
        linkage(data, method='average'), id_list=dm.ids)
    ids = list(dm.ids)
    order = [ids.index(n.name) for n in tree.tips()]

    # Plotting code adapted from skbio's DistanceMatrix.plot()
    fig, ax = plt.subplots()
    heatmap = ax.pcolormesh(dm.data[order][:, order])
    fig.colorbar(heatmap)
    ax.invert_yaxis()
    ax.set_title('Distance Matrix - hierarchical clustering')
    ax.tick_params(axis='both', which='both', bottom='off', top='off',
                   left='off', right='off', labelbottom='off', labelleft='off')

    sc_plot = BytesIO()
    fig.savefig(sc_plot, format='png')
    sc_plot.seek(0)
    uri = 'data:image/png;base64,' + quote(b64encode(sc_plot.getbuffer()))

    html_summary_fp = join(out_dir, 'index.html')
    with open(html_summary_fp, 'w') as f:
        f.write(DM_HTML % (dm.shape[0], data.min(), data.max(),
                           data.mean(), np.median(data), uri))

    return html_summary_fp, None


def _generate_ordination_results_summary(files, metadata, out_dir):
    # Magic number [0] -> there is only one plain text file and it is the
    # ordination results
    ord_res = OrdinationResults.read(files['plain_text'][0])
    md_df = pd.DataFrame.from_dict(metadata, orient='index')
    emp = Emperor(ord_res, md_df, remote="emperor_support_files")

    html_summary_fp = join(out_dir, 'index.html')
    esf_dp = join(out_dir, 'emperor_support_files')
    makedirs(esf_dp)
    with open(html_summary_fp, 'w') as f:
        f.write(emp.make_emperor(standalone=True))
        emp.copy_support_files(esf_dp)

    return html_summary_fp, esf_dp


def _generate_alpha_vector_summary(files, metadata, out_dir):
    # Magic number [0] -> there is only one plain text file and it is the
    # alpha vector
    alpha_vector_fp = files['plain_text'][0]
    alpha_qza = join(out_dir, 'alpha_vectors.qza')
    alpha_qzv = join(out_dir, 'alpha_vectors.qzv')
    metadata_fp = join(out_dir, 'sample-metadata.tsv')

    # Get the SampleData[AlphaDiversity] qiime2 artifact
    cmd = ('qiime tools import --input-path %s --output-path %s '
           '--type "SampleData[AlphaDiversity]"'
           % (alpha_vector_fp, alpha_qza))
    std_out, std_err, return_value = system_call(cmd)
    if return_value != 0:
        error_msg = "Error converting the alpha vectors file to Q2 artifact"
        return False, None, error_msg

    # Generate the metadata file
    metadata = pd.DataFrame.from_dict(metadata, orient='index')
    metadata.to_csv(metadata_fp, index_label='#SampleID', na_rep='', sep='\t',
                    encoding='utf-8')

    # Execute alpha group significance
    cmd = ('qiime diversity alpha-group-significance --i-alpha-diversity %s '
           '--m-metadata-file %s --o-visualization %s'
           % (alpha_qza, metadata_fp, alpha_qzv))
    std_out, std_err, return_value = system_call(cmd)
    if return_value != 0:
        raise RuntimeError(
            "Error executing alpha-group-significance for the summary:\n%s"
            % std_err)

    # Extract the Q2 visualization to use it as html_summary
    q2vis = Visualization.load(alpha_qzv)
    html_dir = join(out_dir, 'support_files')
    html_fp = join(out_dir, 'index.html')

    q2vis.export_data(html_dir)
    index_paths = q2vis.get_index_paths()
    index_name = basename(index_paths['html'])
    with open(html_fp, 'w') as f:
        f.write(Q2_INDEX % index_name)

    return html_fp, html_dir


HTML_SUMMARIZERS = {
    'distance_matrix': _generate_distance_matrix_summary,
    'ordination_results': _generate_ordination_results_summary,
    'alpha_vector': _generate_alpha_vector_summary
}


def generate_html_summary(qclient, job_id, parameters, out_dir):
    """Generates the HTML summary of an artifact

    Parameters
    ----------
    qclient : qiita_client.QiitaClient
        The Qiita server client
    job_id : str
        The job id
    parameters : dict
        The parameter values to validate and create the artifact
    out_dir : str
        The path to the job's output directory

    Returns
    -------
    bool, None, str
        Whether the job is successful
        Ignored
        The error message, if not successful
    """
    artifact_id = parameters['input_data']
    qclient_url = "/qiita_db/artifacts/%s/" % artifact_id
    artifact_info = qclient.get(qclient_url)
    atype = artifact_info['type']
    preps = artifact_info['prep_information']
    analysis_id = artifact_info['analysis']

    if atype not in HTML_SUMMARIZERS:
        return (False, None, "Unknown artifact type %s. Supported types: %s"
                             % (atype, ", ".join(sorted(HTML_SUMMARIZERS))))

    # Get the metadata
    if preps:
        # Magic number 0 -> It returns a list but only 1 prep is
        # currently supported
        metadata = qclient.get("/qiita_db/prep_template/%s/data/" % preps[0])
        metadata = metadata['data']
    elif analysis_id is not None:
        metadata = qclient.get("/qiita_db/analysis/%s/metadata/" % analysis_id)
    else:
        return (False, None, "Missing metadata information")

    html_fp, html_dir = HTML_SUMMARIZERS[atype](artifact_info['files'],
                                                metadata, out_dir)

    if html_dir:
        patch_val = dumps({'html': html_fp, 'dir': html_dir})
    else:
        patch_val = html_fp

    success = True
    error_msg = ""
    try:
        qclient.patch(qclient_url, 'add', '/html_summary/', value=patch_val)
    except Exception as e:
        success = False
        error_msg = str(e)

    return success, None, error_msg
