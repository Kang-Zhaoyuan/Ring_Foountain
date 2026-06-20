/*
 * G0_no_ring_rectangular_repeat_20260619_221811.java
 */

import com.comsol.model.*;
import com.comsol.model.util.*;

/** Model exported on Jun 20 2026, 00:32 by COMSOL 6.4.0.293. */
public class G0_no_ring_rectangular_repeat_20260619_221811 {

  public static Model run() {
    Model model = ModelUtil.create("Model");

    model
         .modelPath("D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\06_true_moving_geometry_R3_ring_contactline_isolation\\03_ring_geometry_position_controls\\models");

    model.label("R3_G0_no_ring_rectangular_repeat_20260619_221811");

    model.param().set("Rtank", "40[mm]");
    model.param().set("Zmin", "-30[mm]");
    model.param().set("Zmax", "30[mm]");
    model.param().set("Ro", "0.012[m]");
    model.param().set("Ri", "0.006[m]");
    model.param().set("h_ring", "0.002[m]");
    model.param().set("z_ring0", "-0.002[m]");
    model.param().set("z0", "0[mm]");
    model.param().set("eps_ls", "1[mm]");
    model.param().set("Vring", "0[m/s]");
    model.param().set("rho_w", "1000[kg/m^3]");
    model.param().set("mu_w", "1e-3[Pa*s]");
    model.param().set("rho_air", "1.2[kg/m^3]");
    model.param().set("mu_air", "1.8e-5[Pa*s]");
    model.param().set("sigma_wa", "0.072[N/m]");
    model.param().set("g0", "9.81[m/s^2]");
    model.param().set("t_end", "0.005[s]");
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
    model.component("comp1").selection("sel_axis").set("ymin", "-0.0305");
    model.component("comp1").selection("sel_axis").set("ymax", "0.0305");
    model.component("comp1").selection("sel_axis").set("condition", "inside");
    model.component("comp1").selection().create("sel_top_open", "Box");
    model.component("comp1").selection("sel_top_open").geom("geom1", 1);
    model.component("comp1").selection("sel_top_open").set("entitydim", "1");
    model.component("comp1").selection("sel_top_open").set("xmin", "-0.0002");
    model.component("comp1").selection("sel_top_open").set("xmax", "0.0405");
    model.component("comp1").selection("sel_top_open").set("ymin", "0.0298");
    model.component("comp1").selection("sel_top_open").set("ymax", "0.030199999999999998");
    model.component("comp1").selection("sel_top_open").set("condition", "inside");
    model.component("comp1").selection().create("sel_bottom_wall", "Box");
    model.component("comp1").selection("sel_bottom_wall").geom("geom1", 1);
    model.component("comp1").selection("sel_bottom_wall").set("entitydim", "1");
    model.component("comp1").selection("sel_bottom_wall").set("xmin", "-0.0002");
    model.component("comp1").selection("sel_bottom_wall").set("xmax", "0.0405");
    model.component("comp1").selection("sel_bottom_wall").set("ymin", "-0.030199999999999998");
    model.component("comp1").selection("sel_bottom_wall").set("ymax", "-0.0298");
    model.component("comp1").selection("sel_bottom_wall").set("condition", "inside");
    model.component("comp1").selection().create("sel_outer_wall", "Box");
    model.component("comp1").selection("sel_outer_wall").geom("geom1", 1);
    model.component("comp1").selection("sel_outer_wall").set("entitydim", "1");
    model.component("comp1").selection("sel_outer_wall").set("xmin", "0.0398");
    model.component("comp1").selection("sel_outer_wall").set("xmax", "0.0402");
    model.component("comp1").selection("sel_outer_wall").set("ymin", "-0.0305");
    model.component("comp1").selection("sel_outer_wall").set("ymax", "0.0305");
    model.component("comp1").selection("sel_outer_wall").set("condition", "inside");

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

    model.study().create("std1");
    model.study("std1").create("phasei", "PhaseInitialization");
    model.study("std1").feature("phasei").setSolveFor("/physics/spf", false);
    model.study("std1").create("time", "Transient");
    model.study("std1").feature("time").set("tlist", "range(0,dt,t_end)");
    model.study("std1").feature("time").set("initstudy", "std1");
    model.study("std1").feature("time").set("useinitsol", "on");
    model.study("std1").run();

    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "t");
    model.result().numerical("gev1").set("unit", "s");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical("gev1").computeResult();
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "r");
    model.result().numerical("gev1").set("unit", "m");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical("eva1").set("expr", "r");
    model.result().numerical("eva1").set("unit", "m");
    model.result().numerical("eva1").set("data", "dset1");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "z");
    model.result().numerical("gev1").set("unit", "m");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical("eva1").set("expr", "z");
    model.result().numerical("eva1").set("unit", "m");
    model.result().numerical("eva1").set("data", "dset1");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "phils");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical("eva1").set("expr", "phils");
    model.result().numerical("eva1").set("data", "dset1");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "reldetjacmin");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical("eva1").set("expr", "reldetjacmin");
    model.result().numerical("eva1").set("data", "dset1");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "reldetjac");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical("eva1").set("expr", "reldetjac");
    model.result().numerical("eva1").set("data", "dset1");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "qual");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical("gev1").computeResult();
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "dvol");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical("gev1").computeResult();
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "r");
    model.result().numerical("gev1").set("unit", "m");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical("eva1").set("expr", "r");
    model.result().numerical("eva1").set("unit", "m");
    model.result().numerical("eva1").set("data", "dset1");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "z");
    model.result().numerical("gev1").set("unit", "m");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical("eva1").set("expr", "z");
    model.result().numerical("eva1").set("unit", "m");
    model.result().numerical("eva1").set("data", "dset1");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "Z");
    model.result().numerical("gev1").set("unit", "m");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical("eva1").set("expr", "Z");
    model.result().numerical("eva1").set("unit", "m");
    model.result().numerical("eva1").set("data", "dset1");
    model.result().numerical().remove("eva1");

    return model;
  }

  public static void main(String[] args) {
    run();
  }

}
