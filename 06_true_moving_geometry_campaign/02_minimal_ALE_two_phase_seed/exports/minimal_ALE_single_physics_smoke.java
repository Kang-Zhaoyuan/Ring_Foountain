/*
 * minimal_ALE_single_physics_smoke_direct.java
 */

import com.comsol.model.*;
import com.comsol.model.util.*;

/** Model exported on Jun 19 2026, 12:35 by COMSOL 6.4.0.293. */
public class minimal_ALE_single_physics_smoke_direct {

  public static Model run() {
    Model model = ModelUtil.create("Model");

    model.label("minimal_ale_study_probe");

    model
         .modelPath("D:\\_COMSOL_FILE_SAVE_\\COMSOL_Ring_Fountain\\06_true_moving_geometry_campaign\\02_minimal_ALE_two_phase_seed\\models");

    model.param().set("Vtest", "1e-4[m/s]");
    model.param().set("t_end", "0.002[s]");
    model.param().set("dt", "1e-4[s]");

    model.component().create("comp1", true);

    model.component("comp1").geom().create("geom1", 2);
    model.component("comp1").geom("geom1").create("r1", "Rectangle");
    model.component("comp1").geom("geom1").feature("r1").set("size", new String[]{"0.02", "0.02"});
    model.component("comp1").geom("geom1").run();

    model.component("comp1").physics().create("ale", "MovingMesh", "geom1");
    model.component("comp1").physics("ale").create("free1", "FreeDeformation", 2);
    model.component("comp1").physics("ale").feature("free1").selection().all();
    model.component("comp1").physics("ale").create("move1", "PrescribedMeshDisplacement", 1);
    model.component("comp1").physics("ale").feature("move1").selection().set(3);
    model.component("comp1").physics("ale").feature("move1").set("useDx", new String[]{"0", "1"});
    model.component("comp1").physics("ale").feature("move1").set("dx", new String[]{"0", "-Vtest*t"});
    model.component("comp1").physics("ale").create("fixb", "PrescribedMeshDisplacement", 1);
    model.component("comp1").physics("ale").feature("fixb").selection().set(1, 2, 4);
    model.component("comp1").physics("ale").feature("fixb").set("useDx", new String[]{"1", "1"});
    model.component("comp1").physics("ale").feature("fixb").set("dx", new String[]{"0", "0"});

    model.component("comp1").mesh().create("mesh1");
    model.component("comp1").mesh("mesh1").autoMeshSize(4);
    model.component("comp1").mesh("mesh1").run();

    model.study().create("std1");
    model.study("std1").create("time", "Transient");
    model.study("std1").feature("time").set("tlist", "range(0,dt,t_end)");
    model.study("std1").run();

    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "ale.dX");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical("eva1").set("expr", "ale.dX");
    model.result().numerical("eva1").set("data", "dset1");
    model.result().numerical().create("eva2", "Eval");
    model.result().numerical().remove("eva2");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "ale.dY");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva2", "Eval");
    model.result().numerical("eva2").set("expr", "ale.dY");
    model.result().numerical("eva2").set("data", "dset1");
    model.result().numerical().create("eva3", "Eval");
    model.result().numerical().remove("eva3");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "ale.u");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva3", "Eval");
    model.result().numerical("eva3").set("expr", "ale.u");
    model.result().numerical("eva3").set("data", "dset1");
    model.result().numerical().create("eva4", "Eval");
    model.result().numerical().remove("eva4");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "ale.v");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva4", "Eval");
    model.result().numerical("eva4").set("expr", "ale.v");
    model.result().numerical("eva4").set("data", "dset1");
    model.result().numerical().create("eva5", "Eval");
    model.result().numerical().remove("eva5");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "x-X");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva5", "Eval");
    model.result().numerical("eva5").set("expr", "x-X");
    model.result().numerical("eva5").set("data", "dset1");
    model.result().numerical().remove("eva5");
    model.result().numerical().create("eva5", "Eval");
    model.result().numerical().remove("eva5");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "y-Y");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva5", "Eval");
    model.result().numerical("eva5").set("expr", "y-Y");
    model.result().numerical("eva5").set("data", "dset1");
    model.result().numerical().remove("eva5");
    model.result().numerical().create("eva5", "Eval");
    model.result().numerical().remove("eva5");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "x");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva5", "Eval");
    model.result().numerical("eva5").set("expr", "x");
    model.result().numerical("eva5").set("data", "dset1");
    model.result().numerical().remove("eva5");
    model.result().numerical().create("eva5", "Eval");
    model.result().numerical().remove("eva5");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "y");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva5", "Eval");
    model.result().numerical("eva5").set("expr", "y");
    model.result().numerical("eva5").set("data", "dset1");
    model.result().numerical().remove("eva5");

    return model;
  }

  public static void main(String[] args) {
    run();
  }

}
