/*
 * minimal_ALE_single_physics_smoke_probe.java
 */

import com.comsol.model.*;
import com.comsol.model.util.*;

/** Model exported on Jun 19 2026, 12:34 by COMSOL 6.4.0.293. */
public class minimal_ALE_single_physics_smoke_probe {

  public static Model run() {
    Model model = ModelUtil.create("Model");

    model.label("minimal_ale_smoke_probe");

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

    model.sol().create("sol1");

    model.study("std1").feature("time").set("solnum", "auto");
    model.study("std1").run();

    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");

    return model;
  }

  public static void main(String[] args) {
    run();
  }

}
