# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------


from unittest import main
from tempfile import mkdtemp
from os import remove, makedirs
from os.path import isdir, exists, join
from shutil import rmtree
from json import dumps
from functools import partial

from qiita_client.testing import PluginTestCase

from qtp_diversity.validate import (
    _validate_taxa_summary, _validate_distance_matrix,
    _validate_rarefaction_curves, validate)


class ValidateTests(PluginTestCase):
    def setUp(self):
        self.tmp_dir = mkdtemp()
        self._clean_up_files = [self.tmp_dir]

    def tearDown(self):
        for fp in self._clean_up_files:
            if exists(fp):
                if isdir(fp):
                    rmtree(fp)
                else:
                    remove(fp)

    def _create_job(self, atype):
        # Craete a new job
        parameters = {'template': None,
                      'files': dumps({'directory': [self.tmp_dir]}),
                      'artifact_type': atype,
                      'analysis': None}
        data = {'command': dumps(['Diversity types', '0.1.0', 'Validate']),
                'parameters': dumps(parameters),
                'status': 'running'}
        res = self.qclient.post('/apitest/processing_job/', data=data)
        return res['job'], parameters

    def test_validate_distance_matrix(self):
        # Construct the directory structure
        path_builder = partial(join, self.tmp_dir)
        logfp = path_builder('log_SOMEDATE.txt')
        open(logfp, 'a').close()
        dmfp = path_builder('SOME_METRIC_dm.txt')
        open(dmfp, 'a').close()
        pcfp = path_builder('SOME_METRIC_pc.txt')
        open(pcfp, 'a').close()
        emperor_plots_dir = path_builder('SOME_METRIC_emperor_pcoa_plot')
        makedirs(emperor_plots_dir)
        path_builder_plots = partial(join, emperor_plots_dir)
        htmlfp = path_builder_plots('index.html')
        open(htmlfp, 'a').close()
        emp_req_resources = path_builder_plots('emperor_required_resources')
        makedirs(emp_req_resources)

        # Valid artifact
        obs_success, obs_msg = _validate_distance_matrix(self.tmp_dir)
        self.assertEqual(obs_msg, "")
        self.assertTrue(obs_success)

        # Missing emperor_required_resources
        rmtree(emp_req_resources)
        obs_success, obs_msg = _validate_distance_matrix(self.tmp_dir)
        self.assertEqual(
            obs_msg, "Missing emperor required resources directory")
        self.assertFalse(obs_success)

        # Missing emperor HTML file
        remove(htmlfp)
        obs_success, obs_msg = _validate_distance_matrix(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing emperor index HTML file")
        self.assertFalse(obs_success)

        # Missing emperor_plots_folder
        rmtree(emperor_plots_dir)
        obs_success, obs_msg = _validate_distance_matrix(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing emperor plots directory")
        self.assertFalse(obs_success)

        # Missing principal coordinates file
        remove(pcfp)
        obs_success, obs_msg = _validate_distance_matrix(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing principal coordinates file")
        self.assertFalse(obs_success)

        # Missing distance matrix file
        remove(dmfp)
        obs_success, obs_msg = _validate_distance_matrix(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing distance matrix file")
        self.assertFalse(obs_success)

        # Missing log file
        remove(logfp)
        obs_success, obs_msg = _validate_distance_matrix(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing log file")
        self.assertFalse(obs_success)

    def test_validate_rarefaction_curves(self):
        # Construct the directory structure
        path_builder = partial(join, self.tmp_dir)
        logfp = path_builder('log_SOMEDATE.txt')
        open(logfp, 'a').close()
        adcdp = path_builder('alpha_div_collated')
        makedirs(adcdp)
        pdwtfp = path_builder('alpha_div_collated', 'PD_whole_tree.txt')
        open(pdwtfp, 'a').close()
        arpdp = path_builder('alpha_rarefaction_plots')
        makedirs(arpdp)
        plotsfp = path_builder('alpha_rarefaction_plots',
                               'rarefaction_plots.html')
        open(plotsfp, 'a').close()
        apdp = path_builder('alpha_rarefaction_plots', 'average_plots')
        makedirs(apdp)
        pngfp = path_builder('alpha_rarefaction_plots', 'average_plots',
                             'image.png')
        open(pngfp, 'a').close()

        # Valid artifact
        obs_success, obs_msg = _validate_rarefaction_curves(self.tmp_dir)
        self.assertEqual(obs_msg, "")
        self.assertTrue(obs_success)

        # Empty average_plots dir
        remove(pngfp)
        obs_success, obs_msg = _validate_rarefaction_curves(self.tmp_dir)
        self.assertEqual(obs_msg, "Empty average plots directory")
        self.assertFalse(obs_success)

        # Missing average_plots dir
        rmtree(apdp)
        obs_success, obs_msg = _validate_rarefaction_curves(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing average plots directory")
        self.assertFalse(obs_success)

        # Missing rarefaction_plots.html
        remove(plotsfp)
        obs_success, obs_msg = _validate_rarefaction_curves(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing rarefaction plots HTML file")
        self.assertFalse(obs_success)

        # Empty alpha_div_collated dir
        remove(pdwtfp)
        obs_success, obs_msg = _validate_rarefaction_curves(self.tmp_dir)
        self.assertEqual(obs_msg, "Empty alpha_div_collated directory")
        self.assertFalse(obs_success)

        # Missing alpha_rarefaction_plots dir
        rmtree(arpdp)
        obs_success, obs_msg = _validate_rarefaction_curves(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing alpha_rarefaction_plots directory")
        self.assertFalse(obs_success)

        # Missing alpha_div_collated dir
        rmtree(adcdp)
        obs_success, obs_msg = _validate_rarefaction_curves(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing alpha_div_collated directory")
        self.assertFalse(obs_success)

        # Missing log file
        remove(logfp)
        obs_success, obs_msg = _validate_rarefaction_curves(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing log file")
        self.assertFalse(obs_success)

    def test_validate_taxa_summaries(self):
        # Construct the directory structure
        path_builder = partial(join, self.tmp_dir)
        logfp = path_builder('log_SOMEDATE.txt')
        open(logfp, 'a').close()
        # Create the biom tables
        for ext in ['txt', 'biom']:
            for i in range(2, 7):
                open(path_builder('table_L%d.%s' % (i, ext)), 'a').close()
        tspdp = path_builder('taxa_summary_plots')
        makedirs(tspdp)
        path_builder_tsp = partial(join, tspdp)
        areafp = path_builder_tsp('area_charts.html')
        open(areafp, 'a').close()
        barfp = path_builder_tsp('bar_charts.html')
        open(barfp, 'a').close()
        chartsdp = path_builder_tsp('charts')
        makedirs(chartsdp)
        open(join(chartsdp, 'figure.png'), 'a').close()
        cssdp = path_builder_tsp('css')
        makedirs(cssdp)
        open(join(cssdp, 'qiime_style.css'), 'a').close()
        jsdp = path_builder_tsp('js')
        makedirs(jsdp)
        open(join(jsdp, 'overlib.js'), 'a').close()
        raw_datadp = path_builder_tsp('raw_data')
        makedirs(raw_datadp)
        raw_data_table_fp = join(raw_datadp, 'table.txt')
        open(raw_data_table_fp, 'a').close()

        # Valid artifact
        obs_success, obs_msg = _validate_taxa_summary(self.tmp_dir)
        self.assertEqual(obs_msg, "")
        self.assertTrue(obs_success)

        # Empty raw_data dir
        remove(raw_data_table_fp)
        obs_success, obs_msg = _validate_taxa_summary(self.tmp_dir)
        self.assertEqual(obs_msg, "Empty raw data directory")
        self.assertFalse(obs_success)

        # Missing raw_data dir
        rmtree(raw_datadp)
        obs_success, obs_msg = _validate_taxa_summary(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing raw data directory")
        self.assertFalse(obs_success)

        # Missing js file
        remove(join(jsdp, 'overlib.js'))
        obs_success, obs_msg = _validate_taxa_summary(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing overlib js file")
        self.assertFalse(obs_success)

        # Missing js directory
        rmtree(jsdp)
        obs_success, obs_msg = _validate_taxa_summary(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing js directory")
        self.assertFalse(obs_success)

        # Missing css file
        remove(join(cssdp, 'qiime_style.css'))
        obs_success, obs_msg = _validate_taxa_summary(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing qiime style css file")
        self.assertFalse(obs_success)

        # Missing css dir
        rmtree(cssdp)
        obs_success, obs_msg = _validate_taxa_summary(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing css directory")
        self.assertFalse(obs_success)

        # Empty charts directory
        remove(join(chartsdp, 'figure.png'))
        obs_success, obs_msg = _validate_taxa_summary(self.tmp_dir)
        self.assertEqual(obs_msg, "Empty charts directory")
        self.assertFalse(obs_success)

        # Missing charts directory
        rmtree(chartsdp)
        obs_success, obs_msg = _validate_taxa_summary(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing charts directory")
        self.assertFalse(obs_success)

        # Missing bar_charts.html
        remove(barfp)
        obs_success, obs_msg = _validate_taxa_summary(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing bar charts file")
        self.assertFalse(obs_success)

        # Missing area_charts.html
        remove(areafp)
        obs_success, obs_msg = _validate_taxa_summary(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing area charts file")
        self.assertFalse(obs_success)

        # Missing taxa_summary_plots directory
        rmtree(tspdp)
        obs_success, obs_msg = _validate_taxa_summary(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing taxonomy summary plots directory")
        self.assertFalse(obs_success)

        # Missing summarized txt files
        for i in range(2, 7):
            remove(path_builder('table_L%d.txt' % i))
        obs_success, obs_msg = _validate_taxa_summary(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing summarized txt files")
        self.assertFalse(obs_success)

        # Missing summarized biom files
        for i in range(2, 7):
            remove(path_builder('table_L%d.biom' % i))
        obs_success, obs_msg = _validate_taxa_summary(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing summarized biom files")
        self.assertFalse(obs_success)

        # Missing log file
        remove(logfp)
        obs_success, obs_msg = _validate_taxa_summary(self.tmp_dir)
        self.assertEqual(obs_msg, "Missing log file")
        self.assertFalse(obs_success)

    def test_validate(self):
        # Valid artifact
        path_builder = partial(join, self.tmp_dir)
        logfp = path_builder('log_SOMEDATE.txt')
        open(logfp, 'a').close()
        dmfp = path_builder('SOME_METRIC_dm.txt')
        open(dmfp, 'a').close()
        pcfp = path_builder('SOME_METRIC_pc.txt')
        open(pcfp, 'a').close()
        emperor_plots_dir = path_builder('SOME_METRIC_emperor_pcoa_plot')
        makedirs(emperor_plots_dir)
        path_builder_plots = partial(join, emperor_plots_dir)
        htmlfp = path_builder_plots('index.html')
        open(htmlfp, 'a').close()
        emp_req_resources = path_builder_plots('emperor_required_resources')
        makedirs(emp_req_resources)

        parameters = {'template': None,
                      'files': dumps({'directory': self.tmp_dir}),
                      'artifact_type': 'distance_matrix',
                      'analysis': 1}

        data = {'command': dumps(['Diversity types', '0.1.0', 'Validate']),
                'parameters': dumps(parameters),
                'status': 'running'}

        res = self.qclient.post('/apitest/processing_job/', data=data)
        job_id = res['job']

        obs_success, obs_ainfo, obs_error = validate(
            self.qclient, job_id, parameters, 'ignored')

        # job_id, parameters = self._create_job()
        # validate(self.qclient, job_id, parameters, 'ignored')
        # Unkown artifact_type
        pass

if __name__ == '__main__':
    main()
