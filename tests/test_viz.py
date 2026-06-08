"""Tests for the constraint oscilloscope."""

import os
import sys
import tempfile

import mido
import numpy as np
import pytest

WORKSPACE = "/home/phoenix/.openclaw/workspace"
sys.path.insert(0, os.path.join(WORKSPACE, "constraint-viz"))
sys.path.insert(0, os.path.join(WORKSPACE, "constraint-synth"))

from constraint_viz.multi_scale import ConstraintOscilloscope


def _make_test_midi(path, notes=None):
    """Create a minimal MIDI file for testing."""
    if notes is None:
        # C4, E4, G4, C5 — a C major arpeggio
        notes = [(60, 100, 480), (64, 80, 480), (67, 90, 480), (72, 70, 480)]

    mid = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    mid.tracks.append(track)

    for pitch, velocity, duration in notes:
        track.append(mido.Message("note_on", note=pitch, velocity=velocity, time=0))
        track.append(mido.Message("note_off", note=pitch, velocity=0, time=duration))

    mid.save(path)
    return path


class TestExtractNotes:
    def test_basic_extraction(self):
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            path = _make_test_midi(f.name)

        try:
            mid = mido.MidiFile(path)
            scope = ConstraintOscilloscope()
            notes = scope._extract_notes(mid)

            assert len(notes) == 4
            assert notes[0][0] == 60  # pitch C4
            assert notes[1][0] == 64  # pitch E4
            # Durations should be positive
            for pitch, vel, dur, start in notes:
                assert dur > 0
                assert vel > 0
        finally:
            os.unlink(path)

    def test_empty_midi(self):
        mid = mido.MidiFile(ticks_per_beat=480)
        mid.tracks.append(mido.MidiTrack())
        scope = ConstraintOscilloscope()
        notes = scope._extract_notes(mid)
        assert notes == []

    def test_sorted_by_start_time(self):
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            # Overlapping notes
            path = _make_test_midi(f.name, [
                (60, 80, 960),  # starts at 0, ends at 960
                (64, 80, 480),  # starts at 0, ends at 480
                (67, 80, 480),  # starts at 0, ends at 480
            ])
        try:
            mid = mido.MidiFile(path)
            scope = ConstraintOscilloscope()
            notes = scope._extract_notes(mid)
            starts = [n[3] for n in notes]
            assert starts == sorted(starts)
        finally:
            os.unlink(path)


class TestVisualization:
    def test_produces_png(self):
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            _make_test_midi(f.name)
            midi_path = f.name

        out_path = midi_path.replace(".mid", "_scope.png")
        try:
            scope = ConstraintOscilloscope()
            result = scope.visualize_midi(midi_path, out_path)
            assert os.path.exists(result)
            assert os.path.getsize(result) > 1000  # non-trivial PNG
        finally:
            os.unlink(midi_path)
            if os.path.exists(out_path):
                os.unlink(out_path)

    def test_empty_midi_produces_png(self):
        mid = mido.MidiFile(ticks_per_beat=480)
        mid.tracks.append(mido.MidiTrack())
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            mid.save(f.name)
            midi_path = f.name

        out_path = midi_path.replace(".mid", "_scope.png")
        try:
            scope = ConstraintOscilloscope()
            result = scope.visualize_midi(midi_path, out_path)
            assert os.path.exists(result)
        finally:
            os.unlink(midi_path)
            if os.path.exists(out_path):
                os.unlink(out_path)


class TestIndividualPanels:
    def test_plot_piano_roll(self):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            _make_test_midi(f.name)
            midi_path = f.name

        try:
            mid = mido.MidiFile(midi_path)
            scope = ConstraintOscilloscope()
            fig, ax = plt.subplots()
            scope._plot_piano_roll(ax, mid)
            out = midi_path.replace(".mid", "_roll.png")
            fig.savefig(out)
            plt.close(fig)
            assert os.path.exists(out)
            os.unlink(out)
        finally:
            os.unlink(midi_path)

    def test_plot_holonomy(self):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            _make_test_midi(f.name)
            midi_path = f.name

        try:
            mid = mido.MidiFile(midi_path)
            scope = ConstraintOscilloscope()
            fig, ax = plt.subplots()
            scope._plot_holonomy(ax, mid)
            out = midi_path.replace(".mid", "_holonomy.png")
            fig.savefig(out)
            plt.close(fig)
            assert os.path.exists(out)
            os.unlink(out)
        finally:
            os.unlink(midi_path)

    def test_plot_density(self):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            _make_test_midi(f.name)
            midi_path = f.name

        try:
            mid = mido.MidiFile(midi_path)
            scope = ConstraintOscilloscope()
            fig, ax = plt.subplots()
            scope._plot_density(ax, mid)
            out = midi_path.replace(".mid", "_density.png")
            fig.savefig(out)
            plt.close(fig)
            assert os.path.exists(out)
            os.unlink(out)
        finally:
            os.unlink(midi_path)
