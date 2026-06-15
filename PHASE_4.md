# PHASE 4

Use this file as Codex context instead of long prompts. Run one subtask at a time. Use 5.5 low + pursue goal unless a subtask fails twice.

## Goal

Make the Tkinter desktop MVP student-friendly for the two target problem types:
- general 2D frame/truss/static structures
- 2D shear-frame dynamic examples with story masses and diaphragms

Pipeline rule:

```text
Tkinter UI -> ModelBuilder -> StructuralModel -> existing validator/solver/export
```

No solver math in UI. XML remains backend save/load/export. Do not create model-type-specific solver paths.

## Current Completed Work

Done:
- 4A support + settlement UI
- 4B nodal load + member UDL + member point-load UI
- canvas redraw/template rendering fix
- object tree + inspector basics
- delete elements and safely block connected node deletion

Do not break these.

## Key Modeling Decisions

### Axially rigid members

Do not simulate axial rigidity using an arbitrary huge EA unless the backend already does that intentionally.

Preferred backend behavior:
- use existing `is_axially_rigid`/rigid-link constraint behavior if present
- expose it in UI as a member/element property later:
  `Axial behavior: normal / axially rigid`

For this phase, audit only unless a small UI checkbox can safely use an existing backend flag.

### Mass in shear-frame templates

The wizard mass represents story lateral mass, not self-weight.

For rigid-floor dynamic examples:
- use `Mass per floor` as a story mass value
- default one value applies to all stories
- user can later edit individual node/story masses through Assign Mass
- default mass placement: center floor node if one exists
- fallback: distribute equally to floor nodes
- if rigid diaphragm is active, distributed nodal masses still contribute to the shared lateral UX DOF

Do not create disconnected fake mass nodes.

Visualization:
- show mass as a red outline/ring/square around the representative mass node, not a filled red square above the node.

### Materials and sections

Do not add stiffness modifiers now.

Instead support different materials/sections:
- users can create separate sections such as `COL_2EI`, `COL_1EI`, `BEAM`
- users assign those sections to selected members later

Before temperature load UI, audit whether backend supports:
- material E
- material alpha
- section A
- section I
- section depth d
- optional direct EA/EI or equivalent effective stiffness helpers

Recommended backend contract:
```text
effective_EA = section.EA if provided else material.E * section.A
effective_EI = section.EI if provided else material.E * section.I
```

Do not change stiffness/thermal formulas in UI.

## Read / Modify Limits

Read as needed:
```text
AGENTS.md
src/model_builder.py
src/parser.py
src/element_physics.py
src/ui_desktop/template_dialog.py
src/ui_desktop/canvas.py
src/ui_desktop/property_panel.py
src/ui_desktop/object_tree.py
src/ui_desktop/main_window.py
```

Modify UI-only subtasks:
```text
src/ui_desktop/template_dialog.py
src/ui_desktop/canvas.py
src/ui_desktop/property_panel.py
src/ui_desktop/object_tree.py
src/ui_desktop/main_window.py
src/ui_desktop/dialogs.py
```

Modify backend only in a dedicated backend subtask:
```text
src/model_builder.py
src/parser.py
src/element_physics.py
tests/...
```

Do not modify controller/solver/math files unless the subtask explicitly says backend audit found a required tiny compatibility patch.

## UI Rule

```text
Left = command
Right = settings/properties
Canvas = target click
Bottom = instruction/status
Object tree = model contents
```

## Revised Subtask Order

### Task 4R0 — Backend Property Audit Only

Purpose:
Audit backend support for:
- Material E, alpha, density/type/name
- Section A, I, depth d
- optional EA/EI direct input or effective_EA/effective_EI helpers
- Element/member axial rigidity flag or constraint path
- ModelBuilder signatures for material/section/element creation
- XML export/import for these fields
- Does LumpedMass support independent mass in ux, uy, rz?
- Does ModelBuilder.add_lumped_mass allow direction-specific mass?
- Does dynamic assembly retain the correct active DOF when mass is assigned to uy instead of ux?
- Does modal analysis work for non-building models such as cantilever/beam lumped-mass examples?

Modify nothing.

Output:
- exact current backend support
- missing fields/methods
- whether a small backend patch is needed before 4R1/4C
- recommended minimal patch if needed

### Task 4R0b — Dynamic Mass Direction Audit Only

Purpose:
Confirm that the generalized dynamic pipeline works for arbitrary nodal masses, not only shear-frame story UX masses.

Inspect only:
- src/matrix_assembly.py
- src/modal_solver.py
- src/dof_optimizer.py
- tests/test_dynamic_assembly.py
- tests/test_modal_solver.py if needed

Check:
- UY nodal masses are retained as active dynamic DOFs.
- UX, UY, and RZ mass/inertia are assembled independently.
- Modal analysis can run on a simple non-building beam/cantilever model with UY lumped mass.
- Rigid diaphragm UX grouping does not override general nodal mass assignment.
- Existing dynamic tests already cover this, or identify the missing focused test.

Modify nothing.

Output:
- <=8 bullet summary.
- Whether a focused dynamic test is needed.
- Whether any backend patch is required before 4D mass UI.

### Task 4R0c — UY-Only Dynamic Mass Regression Test

Purpose:
Add one focused backend test proving the dynamic pipeline supports non-shear-frame vertical vibration examples.

Implement:
- Cantilever/beam-style frame model with a free node carrying only mass_uy.
- Confirm UY mass is retained as the active dynamic DOF.
- Confirm reduced Mff contains the assigned UY mass.
- Confirm modal solve produces a valid positive frequency.

Rules:
- No UI changes.
- No solver math changes unless the test exposes a real bug.
- Keep test hand-checkable and small.

### Task 4R1 — New Model Wizard + Shear-Frame Mass UX

UI-only unless audit says otherwise.

Implement:
- default project name: `New Model`
- units dropdown: `N_m_kg`, `kN_m_tonne`, `kN_m_kNsec2_per_m`
- for `2D General Structure`: grey/disable column/beam/shear-frame-only fields
- for `2D Shear Frame`: show column and beam section fields
- remove base support dropdown; always generate fixed base
- rename checkbox to `Rigid floor diaphragm system`
- mass fields:
  - `Mass per floor`
  - `Mass placement`: `center floor node` / `distribute to floor nodes`
  - one value applies to all stories
- keep later manual mass editing through Assign Mass
- no stiffness modifiers

Validate:
- 2D General Structure wizard has only relevant fields active
- 2D Shear Frame generates fixed bases
- one mass value applies to all floors
- center-node placement works for 2-bay frame
- previous 4A/4B tools still work

### Task 4R2 — Mass Symbol Refinement

UI-only.

Implement:
- replace filled red mass square above node with red outline/ring/square around node
- keep object tree/inspector unchanged unless needed
- redraw preserves mass symbols after template/new model/delete

Validate:
- shear frame template masses visible as outlines
- Assign Mass symbols also use outline style
- no stale old red squares

### Task 4R3 — Material/Section Manager UI

Implement a simple manager, not wizard clutter.

Required:
- create/edit materials:
  - name
  - type: Generic / Steel / Concrete
  - E
  - alpha
  - density if backend supports it
- create/edit sections:
  - name
  - A
  - I
  - depth d if backend supports it
  - EA/EI only if backend audit/patch supports direct EA/EI
- refresh active material/section dropdowns
- inspector shows assigned material/section

Rules:
- use ModelBuilder
- no solver math in UI
- no stiffness modifiers

### Task 4C — Temperature Load

Continue only after material/section support is clear.

Implement:
- Assign Load -> target Member -> Temperature
- fields: Tu, Tb, load case LC1
- store via existing TemperatureL/backend path
- show red `T` marker
- tree/inspector display
- no FEF math in UI

### Task 4D — Mass + Diaphragm Manual Tools

Implement:
- Assign Mass edits/overwrites node mass values
- Assign Diaphragm creates group by typed node ids or click collection
- tree/inspector/symbol refresh
- wrong-target blocking

Principle:
- Mass assignment is general nodal mass assignment, not story-only mass assignment. The 2D Shear Frame wizard may offer `Mass per floor` as a template convenience, but the core UI must let users assign lumped masses to arbitrary nodes and DOFs for general dynamic examples such as cantilever or beam vibration problems.

Field naming / conventions:
- Replace legacy field names `mass_x`, `mass_y`, `rotational_inertia_rz` with `mass_ux`, `mass_uy`, `mass_rz` (rotational inertia). Active directions should be referred to as `UX`, `UY`, and `RZ`.

## Validation Commands

For UI subtasks:
```bash
python -m py_compile src/ui_desktop/dialogs.py src/ui_desktop/canvas.py src/ui_desktop/property_panel.py src/ui_desktop/main_window.py src/ui_desktop/object_tree.py src/ui_desktop/template_dialog.py
python -m src.ui_desktop.app
```

For backend subtasks:
```bash
pytest tests/ -q
```

Run full suite only after backend changes or at phase completion.

## Expected Codex Output

```text
Changed files:
- ...

Summary:
- <=8 bullets

Validation:
- imports/compile/tests/manual smoke

Implemented:
- list done features

Placeholders/TODO:
- unavoidable only
```

## Abort

Stop and report if:
- backend axial rigidity path is unclear
- TemperatureL requires solver changes
- EA/EI support requires broad refactor
- more than 5 files need modification
- more than 3 revision prompts are needed
