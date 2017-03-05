# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from json import loads
from os.path import exists, join
from functools import partial
from glob import glob

from qiita_client import ArtifactInfo

def _files_checker(dir_path, to_check):
    """"""
    path_builder = partial(join, dir_path)
    for fp, error_msg in to_check:
        fps = glob(path_builder(fp))
        if fps:
            if not exists(fps[0]):
                return False, error_msg
        else:
            return False, error_msg
    return True, ""


def _validate_distance_matrix(dir_path):
    """Validate a distance matrix artifact

    Parameters
    ----------
    dir_path : str
        The path to the directory with the artifact files

    Returns
    -------
    bool, str
        Whether the dir_path is a valid artifact
        The error message, if not successful
    """
    # Check that the directory contains the log file, the distance matrix file,
    # the principal coordinates file, the emperor plots directory.
    # Check that the emperor directory folder contains the HTML file and the
    # emperor_required_resources directory
    to_check = [
        ("log_*.txt", "Missing log file"),
        ("*_dm.txt", "Missing distance matrix file"),
        ("*_pc.txt", "Missing principal coordinates file"),
        ("*_emperor_pcoa_plot", "Missing emperor plots directory"),
        ("*_emperor_pcoa_plot/index.html", "Missing emperor index HTML file"),
        ("*_emperor_pcoa_plot/emperor_required_resources",
         "Missing emperor required resources directory")]
    return _files_checker(dir_path, to_check)


def _validate_rarefaction_curves(dir_path):
    """Validates a rarefaction curves artifact

    Parameters
    ----------
    dir_path : str
        The path to the directory with the artifact files

    Returns
    -------
    bool, str
        Whether the dir_path is a valid artifact
        The error message, if not successful
    """
    # Check that the directory contains the log file, the alpha_div_collated
    # directory and the alpha_rarefaction_plots directory
    # Check that the alpha_div_collated dir contains txt files
    # Check that the alpha_rarefaction_plots dir contains the
    # rarefaction_plots.html and the average_plots dir
    to_check = [
        ("log_*.txt", "Missing log file"),
        ("alpha_div_collated", "Missing alpha_div_collated directory"),
        ("alpha_rarefaction_plots",
         "Missing alpha_rarefaction_plots directory"),
        ("alpha_div_collated/*.txt", "Empty alpha_div_collated directory"),
        ("alpha_rarefaction_plots/rarefaction_plots.html",
         "Missing rarefaction plots HTML file"),
        ("alpha_rarefaction_plots/average_plots",
         "Missing average plots directory"),
        ("alpha_rarefaction_plots/average_plots/*.png",
         "Empty average plots directory")]
    return _files_checker(dir_path, to_check)


def _validate_taxa_summary(dir_path):
    """Validates a taxa summary artifact

    Parameters
    ----------
    dir_path : str
        The path to the directory with the artifact files

    Returns
    -------
    bool, str
        Whether the dir_path is a valid artifact
        The error message, if not successful
    """
    # Check that the directory contains the log file
    # Check that the directory contains BIOM tables
    # Check that the directory contains BIOM tables in TXT format
    # Check that the directory contains the taxa_summary_plots folder
    # Check that the taxa_summary_plots dir contains the area_charts.html
    # and bar_charts.html file
    # Check that the taxa_summary_plots dir contains the charts, css, js and
    # raw_data dirs
    to_check = [
        ("log_*.txt", "Missing log file"),
        ("*_L[0-9].biom", "Missing summarized biom files"),
        ("*_L[0-9].txt", "Missing summarized txt files"),
        ("taxa_summary_plots", "Missing taxonomy summary plots directory"),
        ("taxa_summary_plots/area_charts.html", "Missing area charts file"),
        ("taxa_summary_plots/bar_charts.html", "Missing bar charts file"),
        ("taxa_summary_plots/charts", "Missing charts directory"),
        ("taxa_summary_plots/charts/*.png", "Empty charts directory"),
        ("taxa_summary_plots/css", "Missing css directory"),
        ("taxa_summary_plots/css/qiime_style.css",
         "Missing qiime style css file"),
        ("taxa_summary_plots/js", "Missing js directory"),
        ("taxa_summary_plots/js/overlib.js", "Missing overlib js file"),
        ("taxa_summary_plots/raw_data", "Missing raw data directory"),
        ("taxa_summary_plots/raw_data/*.txt", "Empty raw data directory")]
    return _files_checker(dir_path, to_check)


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
    # Given the current analyses available in the system, we are going to
    # assume that the outputs are in QIIME 1 style.
    files = loads(parameters['files'])
    a_type = parameters['artifact_type']

    validator_dict = {'distance_matrix': _validate_distance_matrix,
                      'rarefaction_curves': _validate_rarefaction_curves,
                      'taxa_summary': _validate_taxa_summary}
    if a_type not in validator_dict:
        return False, None, ("Unknown artifact type %s. Supported types: %s"
                             % (a_type, ', '.join(validator_dict.keys())))

    qclient.update_job_step(job_id, "Step 1: Validating files")

    # There is only one directory
    dir_fp = files['directory'][0]
    success, error_msg = validator_dict[a_type](dir_fp)

    artifact_info = None
    if success:
        artifact_info = [ArtifactInfo(None, 'BIOM', [(dir_fp, 'directory')])]

    return success, artifact_info, error_msg
