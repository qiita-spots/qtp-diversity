# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------


from unittest import main
from tempfile import mkdtemp, mkstemp
from os.path import exists, isdir, join
from os import remove, close
from shutil import rmtree

import pandas as pd
import numpy as np
from qiita_client.testing import PluginTestCase
from skbio import DistanceMatrix, OrdinationResults

from qtp_diversity.summary import (
    _generate_distance_matrix_summary, _generate_ordination_results_summary,
    generate_html_summary)


class SummaryTests(PluginTestCase):
    def setUp(self):
        self.out_dir = mkdtemp()
        self._clean_up_files = [self.out_dir]
        self.metadata = {
            '1.SKM4.640180': {'col': "group1"},
            '1.SKB8.640193': {'col': "group1"},
            '1.SKD8.640184': {'col': "group2"},
            '1.SKM9.640192': {'col': "group2"},
            '1.SKB7.640196': {'col': "group2"}}

    def tearDown(self):
        for fp in self._clean_up_files:
            if exists(fp):
                if isdir(fp):
                    rmtree(fp)
                else:
                    remove(fp)

    def test_generate_distance_matrix_summary(self):
        dm = DistanceMatrix([[0.0, 0.850, 0.250],
                             [0.850, 0.0, 0.500],
                             [0.250, 0.500, 0.0]])
        fd, fp = mkstemp(suffix='.txt', dir=self.out_dir)
        close(fd)
        dm.write(fp)
        obs_fp, obs_dp = _generate_distance_matrix_summary(
            {'plain_text': [fp]}, self.metadata, self.out_dir)
        self.assertEqual(obs_fp, join(self.out_dir, 'index.html'))
        self.assertIsNone(obs_dp)

        self.assertTrue(exists(obs_fp))
        with open(obs_fp) as f:
            obs = f.read()

        self.assertRegex(obs, EXP_HTML_REGEXP)

    def test_generate_ordination_results_summary(self):
        eigvals = [0.51236726, 0.30071909, 0.26791207, 0.20898868]
        proportion_explained = [0.2675738328, 0.157044696, 0.1399118638,
                                0.1091402725]
        sample_ids = ['1.SKM4.640180', '1.SKB8.640193', '1.SKD8.640184',
                      '1.SKM9.640192', '1.SKB7.640196']
        axis_labels = ['PC1', 'PC2', 'PC3', 'PC4']
        samples = [[-2.584, 1.739, 3.828, -1.944],
                   [-2.710, -1.859, -8.648, 1.180],
                   [2.350, 9.625, -3.457, -3.208],
                   [2.614, -1.114, 1.476, 2.908],
                   [2.850, -1.925, 6.232, 1.381]]
        ord_res = OrdinationResults(
            short_method_name='PCoA',
            long_method_name='Principal Coordinate Analysis',
            eigvals=pd.Series(eigvals, index=axis_labels),
            samples=pd.DataFrame(np.asarray(samples), index=sample_ids,
                                 columns=axis_labels),
            proportion_explained=pd.Series(proportion_explained,
                                           index=axis_labels))
        fd, fp = mkstemp(suffix='.txt', dir=self.out_dir)
        close(fd)
        ord_res.write(fp)

        obs_fp, obs_dp = _generate_ordination_results_summary(
            {'plain_text': [fp]}, self.metadata, self.out_dir)
        self.assertEqual(obs_fp, join(self.out_dir, 'index.html'))
        self.assertEqual(obs_dp, join(self.out_dir, 'emperor_support_files'))
        self.assertTrue(exists(obs_fp))
        self.assertTrue(exists(obs_dp))

        with open(obs_fp) as f:
            obs = f.read()

        self.assertIn('<title>Emperor</title>', obs)

    def test_generate_html_summary(self):
        pass
        # generate_html_summary()


EXP_HTML_REGEXP = """<b>Number of samples:</b> 3</br>
<b>Minimum distance:</b> 0.2500<br/>
<b>Maximum distance:</b> 0.8500<br/>
<b>Mean distance:</b> 0.5333<br/>
<b>Median distance:</b> 0.5000<br/>
<br/><hr/><br/>
<img src = "data:image/png;base64,.*"/>"""

if __name__ == '__main__':
    main()
