# B Seed Java Reusable API Skeleton

Extracted real Java/API fragments from the GUI-auto-seed export:

```java
multiphysics().create("tpf1", "TwoPhaseFlowLevelSet", 2)
multiphysics().create("ww1", "WettedWall", 1)
multiphysics("tpf1").set("Fluid_physics", "spf");
multiphysics("tpf1").set("Mathematics_physics", "ls");
multiphysics("tpf1").set("rho1_mat", "userdef");
multiphysics("tpf1").set("rho1", "rho_air");
multiphysics("tpf1").set("mu1_mat", "userdef");
multiphysics("tpf1").set("mu1", "mu_air");
multiphysics("tpf1").set("rho2_mat", "userdef");
multiphysics("tpf1").set("rho2", "rho_w");
multiphysics("tpf1").set("mu2_mat", "userdef");
multiphysics("tpf1").set("mu2", "mu_w");
multiphysics("tpf1").set("IncludeSurfaceTension", true);
multiphysics("tpf1").set("SurfaceTensionCoefficient", "userdef");
multiphysics("tpf1").set("sigma", "sigma_wa");
multiphysics("ww1").set("Fluid_physics", "spf");
multiphysics("ww1").set("Mathematics_physics", "ls");
multiphysics("ww1").set("BoundaryCondition", "NavierSlip");
multiphysics("ww1").set("TranslationalVelocityOption", "Manual");
multiphysics("ww1").set("utr", new String[]{"0", "-Vwall", "0"});
multiphysics("ww1").set("SpecifyContactAngle", "SpecifyContactAngleDirectly");
multiphysics("ww1").set("thetaw", "pi/2");
multiphysics("ww1").set("beta", "eps_ls");
physics("ls").feature("lsm1").set("epsilon_ls", "eps_ls");
physics("ls").feature("lsm1").set("gamma", "0.01[m/s]");
physics("spf").feature("grav1").set("g", new String[]{"0", "-g0", "0"});
multiphysics("ww1").selection().set(4);
```

Key transferred names:

- Physics: `LaminarFlow`, `LevelSet`.
- Multiphysics: `TwoPhaseFlowLevelSet`, `WettedWall`.
- WettedWall properties: `BoundaryCondition`, `TranslationalVelocityOption`, `utr`, `SpecifyContactAngle`, `thetaw`, `beta`.
- Initial Level Set: `phils_init`, `phils`.
- Surface tension: `IncludeSurfaceTension`, `SurfaceTensionCoefficient`, `sigma`.
- Gravity: `spf/grav1 g = {0,-g0,0}`.