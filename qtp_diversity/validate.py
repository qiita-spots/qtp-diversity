# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------


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
    # TODO
    return True, [], ""
