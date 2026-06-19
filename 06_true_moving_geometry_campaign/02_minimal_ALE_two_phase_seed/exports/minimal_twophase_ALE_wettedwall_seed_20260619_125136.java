/*
 * minimal_twophase_ALE_wettedwall_seed_20260619_125136.java
 */

import com.comsol.model.*;
import com.comsol.model.util.*;

/** Model exported on Jun 19 2026, 12:52 by COMSOL 6.4.0.293. */
public class minimal_twophase_ALE_wettedwall_seed_20260619_125136 {

  public static Model run() {
    Model model = ModelUtil.create("Model");

    model
         .modelPath("D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\06_true_moving_geometry_campaign\\02_minimal_ALE_two_phase_seed\\models");

    model.label("minimal_twophase_ALE_wettedwall_seed_20260619_125136");

    model.param().set("Rtank", "20[mm]");
    model.param().set("Zmin", "-15[mm]");
    model.param().set("Zmax", "15[mm]");
    model.param().set("z0", "0[mm]");
    model.param().set("eps_ls", "1[mm]");
    model.param().set("rho_w", "1000[kg/m^3]");
    model.param().set("mu_w", "1e-3[Pa*s]");
    model.param().set("rho_air", "1.2[kg/m^3]");
    model.param().set("mu_air", "1.8e-5[Pa*s]");
    model.param().set("sigma_wa", "0.072[N/m]");
    model.param().set("g0", "9.81[m/s^2]");
    model.param().set("Vtest", "1e-4[m/s]");
    model.param().set("t_end", "0.002[s]");
    model.param().set("dt", "1e-4[s]");

    model.component().create("comp1", true);

    model.component("comp1").geom().create("geom1", 2);
    model.component("comp1").geom("geom1").axisymmetric(true);
    model.component("comp1").geom("geom1").feature().create("tank", "Rectangle");
    model.component("comp1").geom("geom1").feature("tank").set("size", new String[]{"Rtank", "Zmax-Zmin"});
    model.component("comp1").geom("geom1").feature("tank").set("pos", new String[]{"0", "Zmin"});
    model.component("comp1").geom("geom1").run();

    model.component("comp1").selection().create("sel_axis", "Box");
    model.component("comp1").selection("sel_axis").geom("geom1", 1);
    model.component("comp1").selection("sel_axis").set("entitydim", "1");
    model.component("comp1").selection("sel_axis").set("xmin", "-0.0002");
    model.component("comp1").selection("sel_axis").set("xmax", "0.0002");
    model.component("comp1").selection("sel_axis").set("ymin", "-0.016");
    model.component("comp1").selection("sel_axis").set("ymax", "0.016");
    model.component("comp1").selection("sel_axis").set("condition", "inside");
    model.component("comp1").selection().create("sel_top", "Box");
    model.component("comp1").selection("sel_top").geom("geom1", 1);
    model.component("comp1").selection("sel_top").set("entitydim", "1");
    model.component("comp1").selection("sel_top").set("xmin", "-0.0002");
    model.component("comp1").selection("sel_top").set("xmax", "0.021");
    model.component("comp1").selection("sel_top").set("ymin", "0.0148");
    model.component("comp1").selection("sel_top").set("ymax", "0.0152");
    model.component("comp1").selection("sel_top").set("condition", "inside");
    model.component("comp1").selection().create("sel_bottom", "Box");
    model.component("comp1").selection("sel_bottom").geom("geom1", 1);
    model.component("comp1").selection("sel_bottom").set("entitydim", "1");
    model.component("comp1").selection("sel_bottom").set("xmin", "-0.0002");
    model.component("comp1").selection("sel_bottom").set("xmax", "0.021");
    model.component("comp1").selection("sel_bottom").set("ymin", "-0.0152");
    model.component("comp1").selection("sel_bottom").set("ymax", "-0.0148");
    model.component("comp1").selection("sel_bottom").set("condition", "inside");
    model.component("comp1").selection().create("sel_outer_moving", "Box");
    model.component("comp1").selection("sel_outer_moving").geom("geom1", 1);
    model.component("comp1").selection("sel_outer_moving").set("entitydim", "1");
    model.component("comp1").selection("sel_outer_moving").set("xmin", "0.0198");
    model.component("comp1").selection("sel_outer_moving").set("xmax", "0.0202");
    model.component("comp1").selection("sel_outer_moving").set("ymin", "-0.0155");
    model.component("comp1").selection("sel_outer_moving").set("ymax", "0.0155");
    model.component("comp1").selection("sel_outer_moving").set("condition", "inside");

    model.component("comp1").mesh().create("mesh1");
    model.component("comp1").mesh("mesh1").autoMeshSize(5);
    model.component("comp1").mesh("mesh1").run();

    model.component("comp1").physics().create("spf", "LaminarFlow", "geom1");
    model.component("comp1").physics().create("ls", "LevelSet", "geom1");

    model.component("comp1").multiphysics().create("tpf1", "TwoPhaseFlowLevelSet", 2);
    model.component("comp1").multiphysics("tpf1").set("Fluid_physics", "spf");
    model.component("comp1").multiphysics("tpf1").set("Mathematics_physics", "ls");
    model.component("comp1").multiphysics("tpf1").selection().all();
    model.component("comp1").multiphysics("tpf1").set("rho1_mat", "userdef");
    model.component("comp1").multiphysics("tpf1").set("rho1", "rho_air");
    model.component("comp1").multiphysics("tpf1").set("mu1_mat", "userdef");
    model.component("comp1").multiphysics("tpf1").set("mu1", "mu_air");
    model.component("comp1").multiphysics("tpf1").set("rho2_mat", "userdef");
    model.component("comp1").multiphysics("tpf1").set("rho2", "rho_w");
    model.component("comp1").multiphysics("tpf1").set("mu2_mat", "userdef");
    model.component("comp1").multiphysics("tpf1").set("mu2", "mu_w");
    model.component("comp1").multiphysics("tpf1").set("IncludeSurfaceTension", true);
    model.component("comp1").multiphysics("tpf1").set("SurfaceTensionCoefficient", "userdef");
    model.component("comp1").multiphysics("tpf1").set("sigma", "sigma_wa");
    model.component("comp1").multiphysics().create("ww1", "WettedWall", 1);
    model.component("comp1").multiphysics("ww1").set("Fluid_physics", "spf");
    model.component("comp1").multiphysics("ww1").set("Mathematics_physics", "ls");
    model.component("comp1").multiphysics("ww1").selection().set(4);
    model.component("comp1").multiphysics("ww1").set("BoundaryCondition", "NavierSlip");
    model.component("comp1").multiphysics("ww1").set("TranslationalVelocityOption", "Manual");
    model.component("comp1").multiphysics("ww1").set("utr", new String[]{"0", "-Vtest", "0"});
    model.component("comp1").multiphysics("ww1").set("SpecifyContactAngle", "SpecifyContactAngleDirectly");
    model.component("comp1").multiphysics("ww1").set("thetaw", "pi/2");
    model.component("comp1").multiphysics("ww1").set("beta", "eps_ls");

    model.component("comp1").physics("spf").feature().create("out_top", "OutletBoundary", 1);
    model.component("comp1").physics("spf").feature("out_top").selection().set(3);
    model.component("comp1").physics("ls").feature().create("out_top", "Outlet", 1);
    model.component("comp1").physics("ls").feature("out_top").selection().set(3);
    model.component("comp1").physics("ls").feature("init1").set("phils_init", "flc2hs(z0-z,eps_ls)");
    model.component("comp1").physics("ls").feature("init1").set("phils", "flc2hs(z0-z,eps_ls)");
    model.component("comp1").physics("ls").feature("lsm1").set("epsilon_ls", "eps_ls");
    model.component("comp1").physics("ls").feature("lsm1").set("gamma", "0.01[m/s]");
    model.component("comp1").physics("spf").prop("PhysicalModelProperty").set("IncludeGravity", true);
    model.component("comp1").physics("spf").feature("grav1").set("g", new String[]{"0", "-g0", "0"});
    model.component("comp1").physics().create("ale", "MovingMesh", "geom1");
    model.component("comp1").physics("ale").create("free1", "FreeDeformation", 2);
    model.component("comp1").physics("ale").feature("free1").selection().all();
    model.component("comp1").physics("ale").create("move1", "PrescribedMeshDisplacement", 1);
    model.component("comp1").physics("ale").feature("move1").selection().set(4);
    model.component("comp1").physics("ale").feature("move1").set("useDx", new String[]{"0", "1"});
    model.component("comp1").physics("ale").feature("move1").set("dx", new String[]{"0", "-Vtest*t"});
    model.component("comp1").physics("ale").create("fixb", "PrescribedMeshDisplacement", 1);
    model.component("comp1").physics("ale").feature("fixb").selection().set(1, 2, 3);
    model.component("comp1").physics("ale").feature("fixb").set("useDx", new String[]{"1", "1"});
    model.component("comp1").physics("ale").feature("fixb").set("dx", new String[]{"0", "0"});

    model.study().create("std1");
    model.study("std1").create("phasei", "PhaseInitialization");
    model.study("std1").feature("phasei").setSolveFor("/physics/spf", false);
    model.study("std1").create("time", "Transient");
    model.study("std1").feature("time").set("tlist", "range(0,dt,t_end)");
    model.study("std1").feature("time").set("initstudy", "std1");
    model.study("std1").feature("time").set("useinitsol", "on");
    model.study("std1").run();

    return model;
  }

  public static void main(String[] args) {
    run();
  }

}
