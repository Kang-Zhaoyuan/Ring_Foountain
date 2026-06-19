# COMSOL Ring Fountain Automation Script Manifest

Generated: 2026-06-18 16:47:47 

Canonical script directory:

```text
D:\_COMSOL_FILE_SAVE_\COMSOL_Ring_Fountain\scripts
```

## Scripts

| Script | Size bytes | Last modified | SHA256 | Notes |
|---|---:|---|---|---|
| [ring_fountain_stage0_2.py](./ring_fountain_stage0_2.py) | 26911 | 2026-06-17 12:36:16 | `110728aa1054f344e5f89e0a4b8cbbdb21cb9438d0db948cebf70b31adf9c850` | Stage 0-2 setup/model automation |
| [ring_fountain_stage2_1_plus.py](./ring_fountain_stage2_1_plus.py) | 49738 | 2026-06-17 18:18:13 | `d0b60619fd0b3a6e4c5b9ff0980c3d730c4b730cfc58aa97cb3d73b8f27e6159` | Stage 2.1+ calibration/sweep automation |
| [ring_fountain_stage4_1_boundary_review.py](./ring_fountain_stage4_1_boundary_review.py) | 25531 | 2026-06-17 19:33:28 | `fea65e439a5523f5826134d0e0bf4820272811c568bc46021772c550b8d22f74` | Stage 4.1 boundary review package automation |
| [ring_fountain_stage4_2_formal.py](./ring_fountain_stage4_2_formal.py) | 11152 | 2026-06-17 19:59:57 | `1af3cf8e4f822b5bb8163c9f790e0fece0f6c097da41e231dba60788798d18a8` | Formal Stage 4.2 moving-wall model automation |
| [ring_fountain_stage4_2_probe.py](./ring_fountain_stage4_2_probe.py) | 4460 | 2026-06-17 19:44:21 | `27ba4cfa9abd432b0cf198146958758248a122098d1b0544ca778b6d03055aaa` | Stage 4.2 wall-property probing helper |
| [ring_fountain_stage4_2a.py](./ring_fountain_stage4_2a.py) | 25148 | 2026-06-17 19:56:09 | `d6def52c06bbed9546cdad310f43ab704c997c7324140989a6b9e9f96ff174cd` | Stage 4.2A relative-velocity check automation |
| [ring_fountain_stage5_cleanup_5b_5c.py](./ring_fountain_stage5_cleanup_5b_5c.py) | 50018 | 2026-06-17 21:04:22 | `a5c77980476469d46db7043910a4f5bbfd00bd934ad563a10fac02e82d9cbfe0` | Stage 5 cleanup / 5B / 5C automation |
| [ring_fountain_stage5a_probe.py](./ring_fountain_stage5a_probe.py) | 1865 | 2026-06-17 20:04:03 | `dfa7321416853a988ad44b7377fad652623a8f3f9f9db3991209b76179e7b5c8` | Stage 5A two-phase availability probing helper |
| [ring_fountain_stage5a_static_interface.py](./ring_fountain_stage5a_static_interface.py) | 14927 | 2026-06-17 20:10:31 | `e41b23e0daef83e7d0cca5fcd18bfac21eb70ca27b3d4f485df6974595d1d3b7` | Stage 5A static free-surface smoke-test automation |
| [ring_fountain_stage5b2_clean_and_5b3_minimal.py](./ring_fountain_stage5b2_clean_and_5b3_minimal.py) | 38249 | 2026-06-18 15:57:10 | `973e8b175861fa285e06b3efee5045086c8101004141f3efece0a54a2b24ee5c` | Stage B/C/D clean static baseline rebuild and minimal moving-wall retry |
| [ring_fountain_stage5b2_clean_baseline_audit.py](./ring_fountain_stage5b2_clean_baseline_audit.py) | 16702 | 2026-06-18 12:34:00 | `fe5e5ee413e3b055bd303e69b2d1fab4f832dfde5335ceccd0438137d89f281b` | Stage A 5B2 clean-baseline read-only physics audit |
| [ring_fountain_stage5b2_to_5e.py](./ring_fountain_stage5b2_to_5e.py) | 31973 | 2026-06-17 22:03:09 | `9db38cb152d8c5d7b04f0d6bc68f5769a7a2f8ffc3d4db35d9bd419fbcd67974` | Stage 5B2 through 5E automation |
| [ring_fountain_stage5b3_C2_alternative_wall_strategy.py](./ring_fountain_stage5b3_C2_alternative_wall_strategy.py) | 49825 | 2026-06-18 16:45:44 | `1f94eb940ed0c5842d41501b245cf1bf231a08655c39cac1820f709d51715377` | Stage 5B3-C2 alternative wall strategy: feature probe, Wetted Wall attempts, rebuilt selectable-wall reduced model |
| [ring_fountain_stage5b3_stability_repair.py](./ring_fountain_stage5b3_stability_repair.py) | 33951 | 2026-06-18 11:37:23 | `bfbb535a5393f1283447154a1b8d3a302bf6d3f334e15aea622560958744ce1b` | Stage 5B3-only stability repair, wall audit, R1 gate, grouped moving-wall test driver |

## Path Management

- Treat this directory as the canonical local archive for Python automation used in the COMSOL Ring Fountain project.
- Working copies may remain under `C:\Users\kqdx\Documents\COMSOL仿真方法`, but scripts should be copied here after each run or edit.
- Helper/probe scripts are preserved because they document how COMSOL features and property names were discovered.
| `ring_fountain_stage5b3_C3_boundary_semantics_audit.py` | 5B3-C3 boundary semantics audit | `20260618_171450` | `3db413894b45bed6e8d4b1a30a9c953ef1db40762d2e88f1d4dd91fd0673fbd3` |

<!-- 5B3_GUI_AUTO_SEED_SCRIPT:START -->
## 5B3-GUI-AUTO-SEED Script

| `ring_fountain_stage5b3_GUI_auto_seed.py` | 5B3-GUI-AUTO-SEED formal Two-Phase Flow Level Set + WettedWall seed discovery | `20260618_174704` | `9f8c67834adcb7bebf9957bdcc2fb734b73eaaf8bc3ed801e86c338c79f729eb` |
<!-- 5B3_GUI_AUTO_SEED_SCRIPT:END -->

<!-- 5B3_C4_SEED_BASED_RING_SMOKE_SCRIPT:START -->
## 5B3-C4 Script

| `ring_fountain_stage5b3_C4_seed_based_ring_smoke.py` | 5B3-C4 seed-based ring free-surface WettedWall smoke | `20260618_182058` | `fe0f45a164bac36849a512d467f0d7da7168f52437e7b6e789a1a39e2558150f` |
<!-- 5B3_C4_SEED_BASED_RING_SMOKE_SCRIPT:END -->

<!-- 5B4_FALLING_OR_EQUIVALENT_RING_SCRIPT:START -->
## 5B4 Script

| `ring_fountain_stage5b4_falling_or_equivalent_ring.py` | 5B4 falling-or-equivalent fixed-geometry WettedWall model | `20260618_202100` | `0a6acaa941c1788096e514e6390a1a6fecf7a0578cc1e58d9794b5833230e097` |
<!-- 5B4_FALLING_OR_EQUIVALENT_RING_SCRIPT:END -->

<!-- 5B4_R1_EXTENDED_STABILITY_REPAIR_SCRIPT:START -->
## 5B4-R1 Script

| `ring_fountain_stage5b4_R1_extended_stability_repair.py` | 5B4-R1 diagnostic audit and extended stability repair | `20260618_225535` | `4b11834fd0ff3ebff5c7e0f19f27e288d9ec62796197cc4c64b413927be5a454` |
<!-- 5B4_R1_EXTENDED_STABILITY_REPAIR_SCRIPT:END -->

<!-- 5C_JET1_EXTRACTION_SCRIPT:START -->
## 5C Script

| `ring_fountain_stage5c_jet1_extraction.py` | 5C Jet1 ROI/interface/velocity extraction | `20260618_233323` | `c06cd5fa91db7f6dbe78f5cd8259315fd4f0c74618c638e749e61b8adfb2ae9f` |
<!-- 5C_JET1_EXTRACTION_SCRIPT:END -->

<!-- 5D_JET2_DETECTION_SCRIPT:START -->
## 5D Script

| `ring_fountain_stage5d_jet2_detection.py` | 5D Jet2 / later-stage Worthington-like detection | `20260619_110135` | `ac73e1d83f721661009373473a678be90c2434366a08457c81036ac00d5cceaf` |
<!-- 5D_JET2_DETECTION_SCRIPT:END -->

<!-- TRUE_MOVING_GEOMETRY_CAMPAIGN_SCRIPT:START -->
## True Moving Geometry Campaign Script

| `ring_fountain_stage6_true_moving_geometry_campaign.py` | true-moving-geometry transition campaign | `20260619_125524` | `74773c0835e7043b8b77e7b2c427275f77bfded09d2e20748408f7fcb3456f9f` |
<!-- TRUE_MOVING_GEOMETRY_CAMPAIGN_SCRIPT:END -->
