# F Exported Java API Analysis

Run time: 2026-06-18T17:48:33

## Extracted API Names

- Component dimension: `2D axisymmetric` via `geom('geom1').axisymmetric(true)`.
- Laminar Flow tag/type: `spf` / `LaminarFlow`.
- Level Set tag/type: `ls` / `LevelSet`.
- Two-Phase Flow coupling tag/type: `tpf1` / `TwoPhaseFlowLevelSet`.
- Wetted Wall feature tag/type: `ww1` / `WettedWall`.
- Moving wall velocity option/property: `TranslationalVelocityOption = Manual`, `utr = ['0', '-Vwall', '0']`.
- Default wall behavior: official `WettedWall` multiphysics coupling overrides the Laminar Flow `Wall` and Level Set no-flow semantics on its selection.

## Key Exported Java Snippets

```java
model.component("comp1").physics().create("spf", "LaminarFlow", "geom1");
model.component("comp1").physics().create("ls", "LevelSet", "geom1");
model.component("comp1").multiphysics().create("tpf1", "TwoPhaseFlowLevelSet", 2);
model.component("comp1").multiphysics().create("ww1", "WettedWall", 1);
model.component("comp1").multiphysics("ww1").set("TranslationalVelocityOption", "Manual");
model.component("comp1").multiphysics("ww1").set("utr", new String[]{"0", "-Vwall", "0"});
```

Machine-readable table: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_GUI_auto_seed\tables\F_extracted_api_names.csv`
Interesting rows: `10` of `52`