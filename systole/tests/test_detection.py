# Author: Nicolas Legrand <nicolas.legrand@cfin.au.dk>

import unittest
from unittest import TestCase

import numpy as np

from systole import import_dataset1, import_ppg
from systole.detection import ecg_peaks, interpolate_clipping, ppg_peaks, rr_artefacts


class TestDetection(TestCase):
    def test_ppg_peaks(self):
        """Test ppg_peaks function"""
        df = import_ppg()  # Import PPG recording
        signal, peaks = ppg_peaks(df.ppg.to_numpy(), clean_extra=True)
        assert len(signal) == len(peaks)
        assert np.all(np.unique(peaks) == [0, 1])
        assert np.mean(np.where(peaks)[0]) == 165778.0

    def test_rr_artefacts(self):
        ppg = import_ppg().ppg.to_numpy()
        _, peaks = ppg_peaks(ppg)
        rr_ms = np.diff(np.where(peaks)[0])
        artefacts_ms = rr_artefacts(rr_ms, input_type="rr_ms")
        artefacts_peaks = rr_artefacts(peaks, input_type="peaks")
        assert all(
            377 == x for x in [len(artefacts_ms[k]) for k in artefacts_ms.keys()]
        )
        assert all(
            377 == x for x in [len(artefacts_peaks[k]) for k in artefacts_peaks.keys()]
        )

    def test_interpolate_clipping(self):
        df = import_ppg()
        clean_signal = interpolate_clipping(df.ppg.to_numpy())
        assert clean_signal.mean().round() == 100
        clean_signal = interpolate_clipping(list(df.ppg.to_numpy()))
        assert clean_signal.mean().round() == 100
        clean_signal = interpolate_clipping(df.ppg.to_numpy())
        df.ppg.iloc[0], df.ppg.iloc[-1] = 255, 255
        clean_signal = interpolate_clipping(df.ppg.to_numpy())

    def test_ecg_peaks(self):
        signal_df = import_dataset1()[: 20 * 2000]
        _, peaks = ecg_peaks(
            signal_df.ecg.to_numpy(), method="hamilton", sfreq=2000, find_local=True
        )
        for method in [
            "christov",
            "engelse-zeelenberg",
            "hamilton",
            "pan-tompkins",
            "moving-average",
        ]:
            _, peaks = ecg_peaks(
                signal_df.ecg, method=method, sfreq=2000, find_local=True
            )
            assert not np.any(peaks > 1)

        with self.assertRaises(ValueError):
            _, peaks = ecg_peaks(
                signal_df.ecg.to_numpy(), method="error", sfreq=2000, find_local=True
            )


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
