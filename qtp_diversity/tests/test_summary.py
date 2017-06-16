# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------


from unittest import main
from tempfile import mkdtemp, mkstemp
from os.path import exists, isdir
from os import remove, close
from shutil import rmtree

from qiita_client.testing import PluginTestCase
from skbio import DistanceMatrix

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
        obs = _generate_distance_matrix_summary(
            {'plain_text': [fp]}, self.metadata, self.out_dir)
        exp = []
        self.assertEqual(obs, exp)

    def test_generate_ordination_results_summary(self):
        _generate_ordination_results_summary()

    def test_generate_html_summary(self):
        generate_html_summary()


if __name__ == '__main__':
    main()
