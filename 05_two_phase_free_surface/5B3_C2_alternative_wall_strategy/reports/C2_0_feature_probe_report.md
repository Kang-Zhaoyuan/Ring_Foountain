# C2-0 Feature / Property Probe Report

Run time: 2026-06-18T16:46:26
Source clean baseline: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B2_clean_baseline_rebuild\models\ring_fountain_v5B2_clean_static_baseline_best.mph`

C2-0 review status: `PASS`

## Summary

- Wetted Wall creatable by tested API type names: `False`.
- Interior Wetted Wall creatable by tested API type names: `False`.
- Tested Wetted/Interior features selectable on ring `[4,5,6,7]`: `[]`.
- Formal Two-Phase Flow Level Set/Phase Field interface creatable by tested API type names: `False`.
- Laminar Flow `Wall` feature creatable and exposes moving-wall properties: `True`.
- Replacement/override of existing noneditable `spf.wallbc1`: not proven by API probe alone; C2-1 tests this without deleting `wallbc1`.

## Probe Table

- CSV: `D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\05_two_phase_free_surface\5B3_C2_alternative_wall_strategy\tables\C2_0_feature_probe.csv`

## Notable Rows

| probe | physics | candidate_type | create_status | can_select_ring | properties | error |
|---|---|---|---|---|---|---|
| `physics_interface` | `` | `LaminarTwoPhaseFlowLevelSet` | `FAIL` | `` | `` | `Exception:
	com.comsol.util.exceptions.FlException: Unknown physics interface.
Messages:
	Unknown physics interface.
	- Physics interface: LaminarTwoPhaseFlowLevelSet
` |
| `physics_interface` | `` | `TwoPhaseFlowLevelSet` | `FAIL` | `` | `` | `Exception:
	com.comsol.util.exceptions.FlException: Unknown physics interface.
Messages:
	Unknown physics interface.
	- Physics interface: TwoPhaseFlowLevelSet
` |
| `physics_interface` | `` | `TwoPhaseFlowLS` | `FAIL` | `` | `` | `Exception:
	com.comsol.util.exceptions.FlException: Unknown physics interface.
Messages:
	Unknown physics interface.
	- Physics interface: TwoPhaseFlowLS
` |
| `physics_interface` | `` | `TpfLevelSet` | `FAIL` | `` | `` | `Exception:
	com.comsol.util.exceptions.FlException: Unknown physics interface.
Messages:
	Unknown physics interface.
	- Physics interface: TpfLevelSet
` |
| `physics_interface` | `` | `LaminarTwoPhaseFlowPhaseField` | `FAIL` | `` | `` | `Exception:
	com.comsol.util.exceptions.FlException: Unknown physics interface.
Messages:
	Unknown physics interface.
	- Physics interface: LaminarTwoPhaseFlowPhaseField
` |
| `physics_interface` | `` | `TwoPhaseFlowPhaseField` | `FAIL` | `` | `` | `Exception:
	com.comsol.util.exceptions.FlException: Unknown physics interface.
Messages:
	Unknown physics interface.
	- Physics interface: TwoPhaseFlowPhaseField
` |
| `physics_interface` | `` | `TwoPhaseFlowPF` | `FAIL` | `` | `` | `Exception:
	com.comsol.util.exceptions.FlException: Unknown physics interface.
Messages:
	Unknown physics interface.
	- Physics interface: TwoPhaseFlowPF
` |
| `feature` | `ls` | `WettedWall` | `FAIL` | `False` | `` | `Exception:
	com.comsol.util.exceptions.FlException: Unknown feature ID: WettedWall.
Messages:
	Unknown feature ID: WettedWall.
` |
| `feature` | `ls` | `WettedWallLS` | `FAIL` | `False` | `` | `Exception:
	com.comsol.util.exceptions.FlException: Unknown feature ID: WettedWallLS.
Messages:
	Unknown feature ID: WettedWallLS.
` |
| `feature` | `ls` | `WallWetted` | `FAIL` | `False` | `` | `Exception:
	com.comsol.util.exceptions.FlException: Unknown feature ID: WallWetted.
Messages:
	Unknown feature ID: WallWetted.
` |
| `feature` | `ls` | `InteriorWettedWall` | `FAIL` | `False` | `` | `Exception:
	com.comsol.util.exceptions.FlException: Unknown feature ID: InteriorWettedWall.
Messages:
	Unknown feature ID: InteriorWettedWall.
` |
| `feature` | `ls` | `InteriorWettedWallLS` | `FAIL` | `False` | `` | `Exception:
	com.comsol.util.exceptions.FlException: Unknown feature ID: InteriorWettedWallLS.
Messages:
	Unknown feature ID: InteriorWettedWallLS.
` |
| `feature` | `ls` | `NoFlow` | `PASS` | `[4, 5, 6, 7]` | `StudyStep, showPhysicsSymbols, pairContrib` | `` |
| `feature` | `ls` | `LevelSetNoFlow` | `FAIL` | `False` | `` | `Exception:
	com.comsol.util.exceptions.FlException: Unknown feature ID: LevelSetNoFlow.
Messages:
	Unknown feature ID: LevelSetNoFlow.
` |
| `feature` | `ls` | `Wall` | `FAIL` | `False` | `` | `Exception:
	com.comsol.util.exceptions.FlException: Unknown feature ID: Wall.
Messages:
	Unknown feature ID: Wall.
` |
| `feature` | `ls` | `OpenBoundary` | `PASS` | `[4, 5, 6, 7]` | `lscond, ls0, StudyStep, showPhysicsSymbols, pairContrib` | `` |
| `feature` | `spf` | `Wall` | `PASS` | `[4, 5, 6, 7]` | `BoundaryCondition, uleak, UseViscousSlip, UseThermalCreep, SlipLengthOption, Ls, alphav, lambda, sigmat, ElectroosmoticOption, mueo, zeta` | `` |
| `feature` | `spf` | `Inlet` | `PASS` | `[4, 5, 6, 7]` | `BoundaryCondition, ComponentWise, U0in, u0, p0, LaminarInflowOption, Uav, V0, p0_entr, CompensateForHydrostaticPressureApproximationIO, CompensateForHydrostaticPressureIO, Lentr` | `` |
| `feature` | `spf` | `Outlet` | `PASS` | `[4, 5, 6, 7]` | `BoundaryCondition, ComponentWise, U0out, u0, p0, f0, LaminarOutflowOption, Uav, V0, Lexit, p0_exit, CompensateForHydrostaticPressureApproximationIO` | `` |
| `feature` | `spf` | `OpenBoundary` | `PASS` | `[4, 5, 6, 7]` | `BoundaryCondition, f0, CompensateForHydrostaticPressureApproximation, CompensateForHydrostaticPressure, RANSVarOption, RANSAnisotropyOption, IT_list, LT_list, IT, LT, Uref, k0` | `` |
| `feature` | `spf` | `SlipWall` | `FAIL` | `False` | `` | `Exception:
	com.comsol.util.exceptions.FlException: Unknown feature ID: SlipWall.
Messages:
	Unknown feature ID: SlipWall.
` |
| `feature` | `spf` | `WettedWall` | `FAIL` | `False` | `` | `Exception:
	com.comsol.util.exceptions.FlException: Unknown feature ID: WettedWall.
Messages:
	Unknown feature ID: WettedWall.
` |
| `feature` | `spf` | `InteriorWettedWall` | `FAIL` | `False` | `` | `Exception:
	com.comsol.util.exceptions.FlException: Unknown feature ID: InteriorWettedWall.
Messages:
	Unknown feature ID: InteriorWettedWall.
` |
| `feature` | `spf` | `MovingWall` | `FAIL` | `False` | `` | `Exception:
	com.comsol.util.exceptions.FlException: Unknown feature ID: MovingWall.
Messages:
	Unknown feature ID: MovingWall.
` |
| `feature` | `spf` | `NoFlow` | `FAIL` | `False` | `` | `Exception:
	com.comsol.util.exceptions.FlException: Unknown feature ID: NoFlow.
Messages:
	Unknown feature ID: NoFlow.
` |