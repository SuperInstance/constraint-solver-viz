"""Visualize MIDI files through the constraint oscilloscope."""

import glob
import os
import sys

WORKSPACE = "/home/phoenix/.openclaw/workspace"
sys.path.insert(0, os.path.join(WORKSPACE, "constraint-viz"))
sys.path.insert(0, os.path.join(WORKSPACE, "constraint-synth"))

from constraint_viz.multi_scale import ConstraintOscilloscope

scope = ConstraintOscilloscope()

midis = sorted(glob.glob(os.path.join(WORKSPACE, "*.mid")))[:5]
print(f"Visualizing {len(midis)} MIDI files...")

for midi_path in midis:
    name = os.path.basename(midi_path).replace(".mid", "")
    out = os.path.join(WORKSPACE, "constraint-viz", "output", f"{name}_scope.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    scope.visualize_midi(midi_path, out)
    print(f"  ✅ {name} → {out}")

print("\nDone!")
