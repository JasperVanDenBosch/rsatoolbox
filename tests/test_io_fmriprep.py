"""Test input/output for fmriprep 
"""
from unittest import TestCase
from unittest.mock import patch, Mock
import pandas


class TestFindFmriprepRuns(TestCase):

    @patch('rsatoolbox.io.fmriprep.BidsLayout')
    @patch('rsatoolbox.io.fmriprep.FmriprepRun')
    def test_find_fmriprep_runs(self, FmriprepRun, BidsLayout):
        from rsatoolbox.io.fmriprep import find_fmriprep_runs
        BidsLayout().find_mri_derivative_files.return_value = ['a', 'b']
        FmriprepRun.side_effect = lambda f: 'run-'+f
        out = find_fmriprep_runs('/path')
        BidsLayout.assert_called_with('/path')
        self.assertEqual(out, ['run-a', 'run-b'])


class TestFmriprepRun(TestCase):

    def test_FmriprepRun_siblings(self):
        from rsatoolbox.io.fmriprep import FmriprepRun
        bidsFile = Mock()
        sibs = dict(
            brain_mask=Mock(),
            aparcaseg=Mock()
        )
        bidsFile.get_mri_sibling.side_effect = lambda desc: sibs[desc]
        run = FmriprepRun(bidsFile)
        self.assertIs(run.get_brain_mask(), sibs['brain_mask'].get_data())
        self.assertIs(run.get_parcellation(), sibs['aparcaseg'].get_data())

    def test_FmriprepRun_to_descriptors(self):
        from rsatoolbox.io.fmriprep import FmriprepRun
        bidsFile = Mock()
        bidsFile.modality = 'moda'
        bidsFile.sub = '05'
        bidsFile.ses = '04'
        bidsFile.task = 'T1'
        bidsFile.run = '03'
        bidsFile.mod = 'mod'
        bidsFile.get_events.return_value = pandas.DataFrame([
            dict(trial_type='s1'),
            dict(trial_type='s2'),
            dict(trial_type='s1'),
            dict(trial_type='s3'),
        ])
        run = FmriprepRun(bidsFile)
        descs = run.to_descriptors()
        self.assertIn('descriptors', descs)
        self.assertEqual(descs['descriptors'], dict(
            sub='05', ses='04', run='03', task='T1'
        ))
        self.assertIn('obs_descriptors', descs)
        self.assertIn('trial_type', descs['obs_descriptors'])
        self.assertEqual(
            list(descs['obs_descriptors']['trial_type']), 
            ['s1', 's2', 's1', 's3']
        )
        self.assertIn('channel_descriptors', descs)
        self.assertEqual(descs['channel_descriptors'], dict())

    def test_FmriprepRun_to_descriptors_collapsed(self):
        """If we set collapse_by_trial_type=true,
        observations should be collapsed by trial_type.
        """
        from rsatoolbox.io.fmriprep import FmriprepRun
        bidsFile = Mock()
        bidsFile.get_events.return_value = pandas.DataFrame([
            dict(trial_type='s1'),
            dict(trial_type='s2'),
            dict(trial_type='s1'),
            dict(trial_type='s3'),
        ])
        run = FmriprepRun(bidsFile)
        descs = run.to_descriptors(collapse_by_trial_type=True)
        self.assertIn('obs_descriptors', descs)
        self.assertIn('trial_type', descs['obs_descriptors'])
        self.assertEqual(
            list(descs['obs_descriptors']['trial_type']), 
            ['s1', 's2', 's3']
        )


class TestEventsDesignMatrix(TestCase):

    def test_make_design_matrix(self):
        from rsatoolbox.io.fmriprep import make_design_matrix
        events = pandas.DataFrame([
            dict(onset=1, duration=0.5, trial_type='a'),
            dict(onset=2, duration=0.5, trial_type='b'),
            dict(onset=3, duration=0.5, trial_type='a'),
            dict(onset=4, duration=0.5, trial_type='b'),
            dict(onset=5, duration=0.5, trial_type='a'),
            dict(onset=6, duration=0.5, trial_type='b'),
        ])
        dm = make_design_matrix(events, tr=2.0, n_vols=4)
        self.assertEqual(dm.shape, (4, 2))
