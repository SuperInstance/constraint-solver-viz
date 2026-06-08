# constraint-solver-viz

**Multi-scale visualization tools for constraint solving** — funnel plots, holonomy trajectories, lattice snap geometry, density arcs, and more.

This package provides the `ConstraintOscilloscope`, a 5-panel visualization system that renders the same constraint structure at five different scales:

1. **Sample Level** — rendered audio waveform showing lattice snap geometry
2. **Note Level** — piano roll with pitch lattice quantization and timing grids
3. **Phrase Level** — holonomy trajectory (cumulative key drift, color-coded)
4. **Piece Level** — note density over time revealing structural arcs
5. **Lattice Snap** — Eisenstein lattice snap visualization mapping input points to the nearest lattice points

## Why Visualize Constraints?

Constraint solving on lattices (hexagonal, Eisenstein, etc.) produces rich mathematical structures that are hard to inspect numerically. Visualization reveals:

- **Holonomy violations** — face cycles that don't close to zero indicate broken constraints
- **Structural arcs** — density profiles that should match expected distributions
- **Quantization artifacts** — points that snap incorrectly on the lattice
- **Rigidity failures** — under-constrained regions that deform unexpectedly

The `ConstraintOscilloscope` treats these like an oscilloscope treats electrical signals: probe at multiple time scales to diagnose what's going wrong.

## Installation

```bash
pip install -e .
```

Or install directly:

```bash
pip install numpy matplotlib mido
```

### Requirements

- Python ≥ 3.10
- NumPy ≥ 1.24
- Matplotlib ≥ 3.7
- Mido ≥ 1.3 (for MIDI file parsing)

## Quick Start

### Visualize a MIDI file

```python
from constraint_solver_viz import ConstraintOscilloscope

scope = ConstraintOscilloscope()
scope.visualize_midi(
    "my_piece.mid",
    output_path="scope_output.png",
    title="My Piece — Constraint Analysis",
    high_res=True,  # 300 DPI
)
```

This produces a 5-panel PNG:

| Panel | Scale | What it shows |
|-------|-------|---------------|
| Top-left | Sample | Waveform amplitude over time — lattice snap geometry at the audio sample level |
| Top-center | Note | Piano roll with velocity coloring — pitch lattice quantization |
| Bottom-left | Phrase | Cumulative pitch-class drift from tonic, detrended and color-coded |
| Bottom-center | Piece | Note density histogram with velocity overlay |
| Right (full height) | Lattice | Eisenstein lattice snap — input vs. nearest lattice points |

### Export visualization data as JSON

```python
from constraint_solver_viz import ConstraintOscilloscope

scope = ConstraintOscilloscope()
json_data = scope.export_data("my_piece.mid")

# Parse and inspect
import json
data = json.loads(json_data)
print(f"Notes: {data['note_count']}")
print(f"Holonomy drift range: {min(data['holonomy']['drift'])} to {max(data['holonomy']['drift'])}")
```

### Use individual panel plotting functions

```python
import matplotlib.pyplot as plt
import mido
from constraint_solver_viz import ConstraintOscilloscope

scope = ConstraintOscilloscope()
mid = mido.MidiFile("my_piece.mid")

fig, axes = plt.subplots(2, 2, figsize=(16, 10))

# Just plot holonomy and density
scope._plot_holonomy(axes[0, 0], mid)
scope._plot_density(axes[0, 1], mid)
scope._plot_piano_roll(axes[1, 0], mid)
scope._plot_lattice_snap(axes[1, 1], mid)

plt.tight_layout()
plt.savefig("custom_panels.png", dpi=150)
```

## Panel Details

### 1. Sample Level — Waveform

Renders a short segment of the audio waveform produced by the constraint system. When the `constraint-synth` package is available, it uses the actual `LatticeOscillator` to produce waveform samples. Otherwise, it falls back to a synthetic sine-based rendering.

**What to look for:**
- Clean periodicity → well-constrained lattice
- Noise or jitter → snap failures or constraint violations
- Amplitude modulation → metronome timing instability

### 2. Note Level — Piano Roll

Standard piano roll with velocity-based coloring (viridis colormap). Red grid lines mark C-major scale degrees, revealing pitch quantization to the lattice.

**What to look for:**
- Notes clustering on grid lines → strong lattice snap
- Notes between grid lines → snap failures or intentional chromaticism
- Timing gaps → constraint underflow regions

### 3. Phrase Level — Holonomy (Key Drift)

Computes cumulative pitch-class drift from the tonic (C = pitch class 0), then detrends to reveal winding behavior. Color-coded from blue (near tonic) to red (far from tonic) using the coolwarm colormap.

**Holonomy** in constraint theory means: "when you go around a closed loop, do you return to where you started?" In music, this translates to: "after a phrase, does the key center return to where it was?"

**What to look for:**
- Flat trajectory (stays near zero) → strong holonomy closure
- Wandering trajectory → key drift, possibly unconstrained modulation
- Sudden jumps → constraint violations

### 4. Piece Level — Density Arc

Histogram of note density over time (green bars) with average velocity overlay (orange line). Binned into ~200ms windows.

**What to look for:**
- Bell curve → classical structural arc
- Flat → uniform density (e.g., etudes)
- Bimodal → binary form (A-B)

### 5. Lattice Snap — Eisenstein

Maps (pitch, time) pairs to the Eisenstein lattice spanned by the basis vectors:
- **e₁** = (1, 0)
- **e₂** = (cos 120°, sin 120°) = (−½, √3/2)

Each input point is snapped to the nearest lattice point by rounding the coordinates in the Eisenstein basis. Blue dots = input, red × = snapped points, gray lines = snap distance.

**What to look for:**
- Short gray lines → points are close to lattice (good quantization)
- Long gray lines → points are far from any lattice point (quantization error)
- Clusters of snapped points on same lattice site → lattice is too coarse

## Architecture

```
constraint_solver_viz/
├── __init__.py           # Exports ConstraintOscilloscope
└── multi_scale.py        # Full implementation of 5-panel visualizer
```

The `ConstraintOscilloscope` class:
- Takes a MIDI file path
- Extracts notes via `mido`
- Generates 5 panels using Matplotlib
- Supports both PNG output and JSON data export

### Data Flow

```
MIDI File
    │
    ▼
_extract_notes()  →  [(pitch, velocity, duration, start), ...]
    │
    ├─→ _plot_waveform()     (sample-level)
    ├─→ _plot_piano_roll()   (note-level)
    ├─→ _plot_holonomy()     (phrase-level)
    ├─→ _plot_density()      (piece-level)
    └─→ _plot_lattice_snap() (lattice-level)
    │
    ▼
PNG (5 panels) or JSON
```

## API Reference

### `ConstraintOscilloscope`

#### `visualize_midi(midi_path, output_path="constraint_scope.png", title=None, high_res=False)`

Full 5-panel visualization of a MIDI file.

**Parameters:**
- `midi_path` (str): Path to the MIDI file.
- `output_path` (str): Output PNG path. Default: `"constraint_scope.png"`.
- `title` (str | None): Custom title. Default: auto-generated from filename.
- `high_res` (bool): 300 DPI if True, 150 DPI if False. Default: `False`.

**Returns:** The output path string.

#### `export_data(midi_path)`

Export all visualization data as JSON.

**Parameters:**
- `midi_path` (str): Path to the MIDI file.

**Returns:** JSON string with keys: `source`, `note_count`, `notes`, `holonomy`, `density`, `lattice_snap`.

## Mathematical Background

### Eisenstein Integers

The Eisenstein integers ℤ[ω] where ω = e^{2πi/3} form a hexagonal lattice in the complex plane:

```
ω = -1/2 + i√3/2
ω² = -1/2 - i√3/2
ω³ = 1
1 + ω + ω² = 0
```

The norm N(a + bω) = a² − ab + b² is preserved under D₆ symmetries (6 rotations × 2 conjugations).

### Holonomy on Lattices

On a triangular lattice graph, each edge carries a value. A **face** is a triangle of three edges. Holonomy checks that the sum of oriented edge values around every face equals zero — this is the discrete analog of curl-free vector fields.

When holonomy holds, the edge values derive from a **potential function**: edge(u,v) = φ(v) − φ(u). This is guaranteed by spanning-tree propagation.

### Laman Rigidity

A graph G = (V, E) is **Laman rigid** in 2D if |E| ≥ 2|V| − 3. Hexagonal lattices have |E| ≈ 3|V|, giving a redundancy ratio of 1.5× — meaning constraints are 50% overdetermined.

## Related SuperInstance Projects

- **[eisenstein-triples](https://github.com/SuperInstance/eisenstein-triples)** — Eisenstein integer triple generation and analysis
- **[hex-graph-constraint](https://github.com/SuperInstance/hex-graph-constraint)** — Hexagonal graph constraint theory and Laman rigidity proofs
- **[constraint-theory-core](https://github.com/SuperInstance/constraint-theory-core)** — Core constraint solving engine
- **[constraint-synth](https://github.com/SuperInstance/constraint-synth)** — Constraint-based audio synthesis
- **[lau-constellation](https://github.com/SuperInstance/lau-constellation)** — Monorepo containing all constraint theory tools

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## License

Extracted from [lau-constellation](https://github.com/SuperInstance/lau-constellation). See parent repo for license information.
