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


def _validate_distance_matrix(files, metadata, out_dir):
    """Validates a distance matrix artifact"""
    # Magic number [0] -> there is only one plain text file which is
    # the distance matrix
    dm_fp = files['plain_text'][0]
    dm = DistanceMatrix.read(dm_fp)

    # Get the ids of the distance matrix and the metadata
    dm_ids = set(dm.ids)
    metadata_ids = set(metadata)

    if not metadata_ids.issuperset(dm_ids):
        return (False, None, "The distance matrix contain samples not "
                             "present in the metadata")

    filepaths = [(dm_fp, 'plain_text')]

    return True, [ArtifactInfo(None, 'distance_matrix', filepaths)], ""


def _validate_ordination_results(files, metadata, out_dir):
    # Magic number [0] -> there is only one plain text file, which is the
    # ordination results
    ord_res_fp = files['plain_text'][0]
    ord_res = OrdinationResults.read(ord_res_fp)

    # Get the ids of the ordination results and the metadata
    ord_res_ids = set(ord_res.samples.index)
    metadata_ids = set(metadata)

    if not metadata_ids.issuperset(ord_res_ids):
        return (False, None, "The ordination results contain samples not "
                             "present in the metadata")

    filepaths = [(ord_res_fp, 'plain_text')]

    return True, [ArtifactInfo(None, 'ordination_results', filepaths)], ""


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

    validators = {'distance_matrix': _validate_distance_matrix}

    # Check if the validate is of a type that we support
    if a_type not in validators:
        return (False, None, "Unknown artifact type %s. Supported types: %s"
                             % (a_type, ", ".join(validators)))

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
    return validators[a_type](files, metadata, out_dir)
