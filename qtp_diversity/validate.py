# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from json import loads

from skbio import (OrdinationResults, DistanceMatrix)
from qiita_client import ArtifactInfo

from qtp_diversity.summary import HTML_SUMMARIZERS


def _validate_distance_matrix(files, metadata, out_dir):
    """Validates a distance matrix artifact"""
    # Magic number [0] -> there is only one plain text file which is
    # the distance matrix
    dm_fp = files['plain_text'][0]
    dm_qza = None
    if 'qza' in files:
        dm_qza = files['qza'][0]
    dm = DistanceMatrix.read(dm_fp)

    # Get the ids of the distance matrix and the metadata
    dm_ids = set(dm.ids)
    metadata_ids = set(metadata)

    if not metadata_ids.issuperset(dm_ids):
        return (False, None, "The distance matrix contain samples not "
                             "present in the metadata")

    filepaths = [(dm_fp, 'plain_text')]
    if dm_qza is not None:
        filepaths.append((dm_qza, 'qza'))

    return True, [ArtifactInfo(None, 'distance_matrix', filepaths)], ""


def _validate_ordination_results(files, metadata, out_dir):
    # Magic number [0] -> there is only one plain text file, which is the
    # ordination results
    ord_res_fp = files['plain_text'][0]
    ord_res_qza = None
    if 'qza' in files:
        ord_res_qza = files['qza'][0]
    ord_res = OrdinationResults.read(ord_res_fp)

    # Get the ids of the ordination results and the metadata
    ord_res_ids = set(ord_res.samples.index)
    metadata_ids = set(metadata)

    if not metadata_ids.issuperset(ord_res_ids):
        return (False, None, "The ordination results contain samples not "
                             "present in the metadata")

    filepaths = [(ord_res_fp, 'plain_text')]
    if ord_res_qza is not None:
        filepaths.append((ord_res_qza, 'qza'))

    return True, [ArtifactInfo(None, 'ordination_results', filepaths)], ""


def _validate_alpha_vector(files, metadata, out_dir):
    # Magic number [0] -> there is only one plain text file, which is the
    # ordination results
    alpha_vector = files['plain_text'][0]
    alpha_qza = None
    if 'qza' in files:
        alpha_qza = files['qza'][0]

    # Parse the sample ids from the alphe_vector file
    alpha_ids = []
    with open(alpha_vector) as f:
        # Ignore the header line
        f.readline()
        for line in f:
            vals = line.strip().split('\t')
            if len(vals) != 2:
                return (False, None, "The alpha vector format is incorrect")
            alpha_ids.append(vals[0])

    metadata_ids = set(metadata)
    alpha_ids = set(alpha_ids)

    if not metadata_ids.issuperset(alpha_ids):
        return (False, None, "The alpha vector contains samples not present "
                             "in the metadata")

    filepaths = [(alpha_vector, 'plain_text')]
    if alpha_qza is not None:
        filepaths.append((alpha_qza, 'qza'))

    return True, [ArtifactInfo(None, 'alpha_vector', filepaths)], ""


def _validate_feature_data(files, metadata, out_dir):
    # Magic number [0] -> there is only one plain text file, which is the
    # ordination results
    fdt = files['plain_text'][0]
    fdt_qza = None
    if 'qza' in files:
        fdt_qza = files['qza'][0]

    # basic header check to verify that it looks like a taxonomy file
    with open(fdt) as f:
        line = f.readline()
        if ('Tax' not in line or 'ID' not in line) and line[0] != '>':
            return (False, None, 'The file header seems wrong "%s"' % line)

    filepaths = [(fdt, 'plain_text')]
    if fdt_qza is not None:
        filepaths.append((fdt_qza, 'qza'))

    return True, [ArtifactInfo(None, 'FeatureData', filepaths)], ""


def _validate_sample_data(files, metadata, out_dir):
    # Magic number [0] -> there is only one plain text file, which is the
    # ordination results
    fdt = files['plain_text'][0]
    if 'qza' not in files or not files['qza']:
        return False, None, 'The artifact is missing a QZA file'
    fdt_qza = files['qza'][0]

    filepaths = [(fdt, 'plain_text')]
    if fdt_qza is not None:
        filepaths.append((fdt_qza, 'qza'))

    return True, [ArtifactInfo(None, 'SampleData', filepaths)], ""


def validate(qclient, job_id, parameters, out_dir):
    """Validates and fix a new artifact

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
    bool, list of qiita_client.ArtifactInfo , str
        Whether the job is successful
        The artifact information, if successful
        The error message, if not successful
    """
    prep_id = parameters.get('template')
    analysis_id = parameters.get('analysis')
    files = loads(parameters['files'])
    a_type = parameters['artifact_type']

    validators = {'distance_matrix': _validate_distance_matrix,
                  'ordination_results': _validate_ordination_results,
                  'alpha_vector': _validate_alpha_vector,
                  'FeatureData': _validate_feature_data,
                  'SampleData': _validate_sample_data}

    # Check if the validate is of a type that we support
    if a_type not in validators:
        return (False, None, "Unknown artifact type %s. Supported types: %s"
                             % (a_type, ", ".join(sorted(validators))))

    # Get the metadata
    qclient.update_job_step(job_id, "Step 1: Collecting metadata")
    if prep_id is not None:
        metadata = qclient.get("/qiita_db/prep_template/%s/data/" % prep_id)
        metadata = metadata['data']
    elif analysis_id is not None:
        metadata = qclient.get("/qiita_db/analysis/%s/metadata/" % analysis_id)
    else:
        return (False, None, "Missing metadata information")

    # Validate the specific type
    success, ainfo, error_msg = validators[a_type](files, metadata, out_dir)

    if success:
        # Generate the summary in the validator to save GUI clicks
        html_fp, html_dir = HTML_SUMMARIZERS[a_type](files, metadata, out_dir)
        # Magic number 0, there is only 1 ArtifactInfo on the list
        ainfo[0].files.append((html_fp, 'html_summary'))
        if html_dir is not None:
            ainfo[0].files.append((html_dir, 'html_summary_dir'))

    return success, ainfo, error_msg
