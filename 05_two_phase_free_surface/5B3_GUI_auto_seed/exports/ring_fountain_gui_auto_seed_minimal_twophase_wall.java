/*
 * ring_fountain_gui_auto_seed_minimal_twophase_wall.java
 */

import com.comsol.model.*;
import com.comsol.model.util.*;

/** Model exported on Jun 18 2026, 17:48 by COMSOL 6.4.0.293. */
public class ring_fountain_gui_auto_seed_minimal_twophase_wall {

  public static Model run() {
    Model model = ModelUtil.create("Model");

    model
         .modelPath("D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\05_two_phase_free_surface\\5B3_GUI_auto_seed\\models");

    model.label("ring_fountain_gui_auto_seed_minimal_twophase_wall");

    model.param().set("Rtank", "20[mm]");
    model.param().set("Hwater", "10[mm]");
    model.param().set("Hair", "20[mm]");
    model.param().set("eps_ls", "1[mm]");
    model.param().set("Vwall", "0[m/s]");
    model.param().set("rho_air", "1.225[kg/m^3]");
    model.param().set("mu_air", "1.8e-5[Pa*s]");
    model.param().set("rho_w", "1000[kg/m^3]");
    model.param().set("mu_w", "1e-3[Pa*s]");
    model.param().set("sigma_wa", "0.072[N/m]");
    model.param().set("g0", "9.81[m/s^2]");

    model.component().create("comp1", true);

    model.component("comp1").geom().create("geom1", 2);
    model.component("comp1").geom("geom1").axisymmetric(true);
    model.component("comp1").geom("geom1").feature().create("tank", "Rectangle");
    model.component("comp1").geom("geom1").feature("tank").set("size", new String[]{"Rtank", "Hwater+Hair"});
    model.component("comp1").geom("geom1").feature("tank").set("pos", new String[]{"0", "-Hwater"});
    model.component("comp1").geom("geom1").run();

    model.component("comp1").mesh().create("mesh1");
    model.component("comp1").mesh("mesh1").autoMeshSize(7);
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

    model.component("comp1").selection().create("sel_seed_right_moving_wall", "Box");
    model.component("comp1").selection("sel_seed_right_moving_wall").geom("geom1", 1);
    model.component("comp1").selection("sel_seed_right_moving_wall").set("entitydim", "1");
    model.component("comp1").selection("sel_seed_right_moving_wall").set("xmin", "0.0199");
    model.component("comp1").selection("sel_seed_right_moving_wall").set("xmax", "0.0201");
    model.component("comp1").selection("sel_seed_right_moving_wall").set("ymin", "-0.0101");
    model.component("comp1").selection("sel_seed_right_moving_wall").set("ymax", "0.0201");
    model.component("comp1").selection("sel_seed_right_moving_wall").set("condition", "inside");
    model.component("comp1").selection().create("sel_seed_top_open", "Box");
    model.component("comp1").selection("sel_seed_top_open").geom("geom1", 1);
    model.component("comp1").selection("sel_seed_top_open").set("entitydim", "1");
    model.component("comp1").selection("sel_seed_top_open").set("xmin", "-0.0001");
    model.component("comp1").selection("sel_seed_top_open").set("xmax", "0.0201");
    model.component("comp1").selection("sel_seed_top_open").set("ymin", "0.0199");
    model.component("comp1").selection("sel_seed_top_open").set("ymax", "0.0201");
    model.component("comp1").selection("sel_seed_top_open").set("condition", "inside");
    model.component("comp1").selection().create("sel_seed_bottom_wall", "Box");
    model.component("comp1").selection("sel_seed_bottom_wall").geom("geom1", 1);
    model.component("comp1").selection("sel_seed_bottom_wall").set("entitydim", "1");
    model.component("comp1").selection("sel_seed_bottom_wall").set("xmin", "-0.0001");
    model.component("comp1").selection("sel_seed_bottom_wall").set("xmax", "0.0201");
    model.component("comp1").selection("sel_seed_bottom_wall").set("ymin", "-0.0101");
    model.component("comp1").selection("sel_seed_bottom_wall").set("ymax", "-0.0099");
    model.component("comp1").selection("sel_seed_bottom_wall").set("condition", "inside");
    model.component("comp1").selection().create("sel_seed_axis", "Box");
    model.component("comp1").selection("sel_seed_axis").geom("geom1", 1);
    model.component("comp1").selection("sel_seed_axis").set("entitydim", "1");
    model.component("comp1").selection("sel_seed_axis").set("xmin", "-0.0001");
    model.component("comp1").selection("sel_seed_axis").set("xmax", "0.0001");
    model.component("comp1").selection("sel_seed_axis").set("ymin", "-0.0101");
    model.component("comp1").selection("sel_seed_axis").set("ymax", "0.0201");
    model.component("comp1").selection("sel_seed_axis").set("condition", "inside");
    model.component("comp1").selection().create("sel_seed_all_boundaries", "Box");
    model.component("comp1").selection("sel_seed_all_boundaries").geom("geom1", 1);
    model.component("comp1").selection("sel_seed_all_boundaries").set("entitydim", "1");
    model.component("comp1").selection("sel_seed_all_boundaries").set("xmin", "-0.0001");
    model.component("comp1").selection("sel_seed_all_boundaries").set("xmax", "0.0201");
    model.component("comp1").selection("sel_seed_all_boundaries").set("ymin", "-0.0101");
    model.component("comp1").selection("sel_seed_all_boundaries").set("ymax", "0.0201");
    model.component("comp1").selection("sel_seed_all_boundaries").set("condition", "inside");

    model.component("comp1").multiphysics().create("ww1", "WettedWall", 1);
    model.component("comp1").multiphysics("ww1").set("Fluid_physics", "spf");
    model.component("comp1").multiphysics("ww1").set("Mathematics_physics", "ls");
    model.component("comp1").multiphysics("ww1").selection().set(4);
    model.component("comp1").multiphysics("ww1").set("BoundaryCondition", "NavierSlip");
    model.component("comp1").multiphysics("ww1").set("TranslationalVelocityOption", "Manual");
    model.component("comp1").multiphysics("ww1").set("utr", new String[]{"0", "-Vwall", "0"});
    model.component("comp1").multiphysics("ww1").set("SpecifyContactAngle", "SpecifyContactAngleDirectly");
    model.component("comp1").multiphysics("ww1").set("thetaw", "pi/2");
    model.component("comp1").multiphysics("ww1").set("beta", "eps_ls");

    model.component("comp1").physics("spf").feature().create("out_top", "OutletBoundary", 1);
    model.component("comp1").physics("spf").feature("out_top").selection().set(3);
    model.component("comp1").physics("spf").feature("out_top").set("CompensateForHydrostaticPressure", false);
    model.component("comp1").physics("ls").feature().create("out_top", "Outlet", 1);
    model.component("comp1").physics("ls").feature("out_top").selection().set(3);
    model.component("comp1").physics("ls").feature("init1").set("phils_init", "flc2hs(-z,eps_ls)");
    model.component("comp1").physics("ls").feature("init1").set("phils", "flc2hs(-z,eps_ls)");
    model.component("comp1").physics("ls").feature("lsm1").set("epsilon_ls", "eps_ls");
    model.component("comp1").physics("ls").feature("lsm1").set("gamma", "0.01[m/s]");
    model.component("comp1").physics("spf").prop("PhysicalModelProperty").set("IncludeGravity", true);
    model.component("comp1").physics("spf").feature("grav1").set("g", new String[]{"0", "-g0", "0"});

    model.study().create("std1");
    model.study("std1").create("phasei", "PhaseInitialization");
    model.study("std1").feature("phasei").setSolveFor("/physics/spf", false);
    model.study("std1").create("time", "Transient");
    model.study("std1").feature("time").set("tlist", "range(0,1e-4,0.002)");
    model.study("std1").feature("time").set("initstudy", "std1");
    model.study("std1").feature("time").set("useinitsol", "on");

    model.param().set("Vwall", "0[m/s]");

    model.study("std1").run();

    model.param().set("Vwall", "1e-4[m/s]");

    model.study("std1").run();

    return model;
  }

  public static void main(String[] args) {
    run();
  }

}
