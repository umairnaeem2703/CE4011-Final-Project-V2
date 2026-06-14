# CE 4011 Structural Analysis Application

An educational 2D structural analysis application for building, solving, and visualizing truss, frame, beam, and benchmark models. The project is designed to expose the full analysis pipeline for learning: model input, DOF mapping, stiffness/mass/damping assembly, solver execution, result objects, diagrams, and exportable intermediate data.

XML is the current backend save/load format. The intended input direction is spreadsheet-style tables, forms, templates, and graphical model editing that build the same `StructuralModel` objects before analysis.

## Implemented

- Static analysis for 2D truss, frame, and beam-style models using assembled global stiffness matrices, reduced systems, displacements, reactions, element forces, and axial/shear/moment data.
- Modal analysis with dynamic assembly, mass handling, eigenvalues, frequencies, periods, mode shapes, modal mass, participation factors, and effective modal mass outputs.
- Response Spectrum Analysis (RSA) with spectrum interpolation, modal response vectors, SRSS/CQC combination, and peak response quantities.
- Time-History Analysis (THA) using Newmark average-acceleration integration, ground-motion input handling, displacement/velocity/acceleration histories, and base response histories.
- Educational intermediate outputs, including DOF maps, full and reduced matrices/vectors, solver inputs, solver outputs, and post-processing data for reports and tests.
- XML parsing as the backend model format, including nodes, elements, supports, loads, masses, materials, sections, and analysis settings.
- Visualization and post-processing through matplotlib, including model preview, deformed shapes, axial/shear/moment diagrams, mode shapes, response spectrum plots, and THA histories.
- A Streamlit local UI/dashboard for XML upload, table/form-based model input, static and dynamic analysis controls, cached results, and visualization display.
- Focused pytest coverage for model input, static analysis, dynamic assembly, modal analysis, RSA, THA/Newmark, UI helpers, and visualization behavior.

## Under Development

- Broader graphical model editing and richer spreadsheet-style workflows on top of the XML backend.
- More complete export/report flows for classroom use.
- Expanded templates and validation examples for common educational structures.
- Continued refinement of result presentation, diagrams, and end-to-end UI ergonomics.

## Architecture

The project follows a layered educational pipeline:

```text
input tables/XML/templates -> StructuralModel -> DOF/K/M/C/F assembly -> solvers -> result objects -> plots/export
```

Solvers operate on assembled matrices and vectors rather than branching by structure type. Structure families such as shear frames, cantilevers, frames, trusses, and benchmarks are represented as ordinary models or templates. The solver, model, IO, UI, and visualization layers are kept separate so the numerical workflow remains transparent and testable.

## Repository Map

```text
src/
  model/input/parser and validation code
  assembly, DOF, matrix, modal, RSA, and Newmark solver modules
  result containers, post-processing, educational export, and visualization
  ui/ Streamlit dashboard modules

data/      XML examples and schema material
tests/     focused unit, integration, UI-helper, and visualization tests
results/   generated reports and figures when analyses are run locally
```