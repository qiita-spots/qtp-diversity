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
from json import dumps

from skbio.stats.distance import randdm
from qiita_client import ArtifactInfo
from qiita_client.testing import PluginTestCase

from qtp_diversity.validate import (
    _validate_distance_matrix, _validate_ordination_results, validate)


class ValidateTests(PluginTestCase):
    def setUp(self):
        self.out_dir = mkdtemp()
        self._clean_up_files = [self.out_dir]

    def tearDown(self):
        for fp in self._clean_up_files:
            if exists(fp):
                if isdir(fp):
                    rmtree(fp)
                else:
                    remove(fp)

    def _create_distance_matrix(self, sample_ids):
        dm = randdm(len(sample_ids), sample_ids)
        fd, fp = mkstemp(suffix='.txt', dir=self.out_dir)
        close(fd)
        dm.write(fp)
        return fp

    def _create_job(self, a_type, files):
        parameters = {'template': None,
                      'files': dumps(files),
                      'artifact_type': a_type,
                      'analysis': 1}
        data = {'command': dumps(['Diversity types', '0.1.0', 'Validate']),
                'parameters': dumps(parameters),
                'status': 'running'}
        return self.qclient.post('/apitest/processing_job', data=data)['job']

    def test_validate_distance_matrix(self):
        # Create a distance matrix
        sample_ids = ['1.SKM4.640180', '1.SKB8.640193', '1.SKD8.640184',
                      '1.SKM9.640192', '1.SKB7.640196']
        dm_fp = self._create_distance_matrix(sample_ids)
        # Create som sample metadata
        metadata = {
            '1.SKM4.640180': {'col': "doesn't really matters"},
            '1.SKB8.640193': {'col': "doesn't really matters"},
            '1.SKD8.640184': {'col': "doesn't really matters"},
            '1.SKM9.640192': {'col': "doesn't really matters"},
            '1.SKB7.640196': {'col': "doesn't really matters"}}

        # Test success
        obs_success, obs_ainfo, obs_error = _validate_distance_matrix(
            {'plain_text': [dm_fp]}, metadata, self.out_dir)
        self.assertTrue(obs_success)
        exp_ainfo = [ArtifactInfo(None, "distance_matrix",
                                  [(dm_fp, 'plain_text')])]
        self.assertEqual(obs_ainfo, exp_ainfo)
        self.assertEqual(obs_error, "")

        # Test failure
        sample_ids = ['1.SKM4.640180', '1.SKB8.640193', '1.SKD8.640184',
                      '1.SKM9.640192', 'NotASample']
        dm_fp = self._create_distance_matrix(sample_ids)
        obs_success, obs_ainfo, obs_error = _validate_distance_matrix(
            {'plain_text': [dm_fp]}, metadata, self.out_dir)
        self.assertFalse(obs_success)
        self.assertIsNone(obs_ainfo)
        self.assertEqual(obs_error, "The distance matrix contain samples not "
                                    "present in the metadata")

    def test_validate_ordination_results(self):
        # _validate_ordination_results()
        pass

    def test_validate(self):
        # validate()
        pass

if __name__ == '__main__':
    main()
