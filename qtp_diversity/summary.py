# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from os.path import join
from urllib.parse import quote
from base64 import b64encode
from io import BytesIO

import numpy as np
import pandas as pd
from emperor import Emperor
from skbio import OrdinationResults, DistanceMatrix


DM_HTML = """<b>Number of samples:</b> %d</br>
<b>Minimum distance:</b> %.4f<br/>
<b>Maximum distance:</b> %.4f<br/>
<b>Mean distance:</b> %.4f<br/>
<b>Median distance:</b> %.4f<br/>
<br/><hr/><br/>
<img src = "%s"/>"""


def _generate_distance_matrix_summary(files, metadata, out_dir):
    # Magic number [0] -> there is only one plain text file which is
    # the distance matrix
    dm = DistanceMatrix.read(files['plain_text'][0])
    data = dm.condensed_form()

    # Generate a heatmap with the distance matrix
    sc_plot = BytesIO()
    fig = dm.plot()
    fig.savefig(sc_plot, format='png')
    sc_plot.seek(0)
    uri = 'data:image/png;base64,' + quote(b64encode(sc_plot.getbuffer()))

    with open(join(out_dir, 'index.html'), 'w') as f:
        f.write(DM_HTML % (dm.shape[0], data.min(), data.max(),
                           data.mean(), np.median(data), uri))


def _generate_ordination_results_summary(files, metadata, out_dir):
    # Magic number [0] -> there is only one plain text file and it is the
    # ordination results
    ord_res = OrdinationResults.read(files['plain_text'][0])
    md_df = pd.DataFrame.from_dict(metadata, orient='index')
    emp = Emperor(ord_res, md_df, remote=".")

    with open(join(out_dir, 'index.html'), 'w') as f:
        f.write(emp.make_emperor(standalone=True))
        emp.copy_support_files(out_dir)


HTML_SUMMARIZERS = {
    'distance_matrix': _generate_distance_matrix_summary,
    'ordination_results': _generate_ordination_results_summary
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

    if atype not in HTML_SUMMARIZERS:
        return (False, None, "Unknown artifact type %s. Supported types: %s"
                             % (atype, ", ".join(sorted(HTML_SUMMARIZERS))))

    summary_fp = HTML_SUMMARIZERS[atype](artifact_info['files'], metadata,
                                         out_dir)
    return True, None, ""
