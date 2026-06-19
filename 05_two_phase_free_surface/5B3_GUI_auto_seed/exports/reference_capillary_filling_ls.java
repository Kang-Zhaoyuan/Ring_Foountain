/*
 * reference_capillary_filling_ls.java
 */

import com.comsol.model.*;
import com.comsol.model.util.*;

/** Model exported on Jun 18 2026, 17:48 by COMSOL 6.4.0.293. */
public class reference_capillary_filling_ls {

  public static Model run() {
    Model model = ModelUtil.create("Model");

    model.modelPath("D:\\COMSOL64\\Multiphysics\\applications\\CFD_Module\\Multiphase_Flow");

    model.component().create("comp1", true);

    model.component("comp1").geom().create("geom1", 2);
    model.component("comp1").geom("geom1").axisymmetric(true);

    model.component("comp1").mesh().create("mesh1");

    model.component("comp1").physics().create("spf", "LaminarFlow", "geom1");
    model.component("comp1").physics().create("ls", "LevelSet", "geom1");

    model.component("comp1").multiphysics().create("tpf1", "TwoPhaseFlowLevelSet", 2);
    model.component("comp1").multiphysics("tpf1").set("Fluid_physics", "spf");
    model.component("comp1").multiphysics("tpf1").set("Mathematics_physics", "ls");
    model.component("comp1").multiphysics("tpf1").selection().all();
    model.component("comp1").multiphysics().create("ww1", "WettedWall", 1);
    model.component("comp1").multiphysics("ww1").set("Fluid_physics", "spf");
    model.component("comp1").multiphysics("ww1").set("Mathematics_physics", "ls");

    model.study().create("std1");
    model.study("std1").create("phasei", "PhaseInitialization");
    model.study("std1").feature("phasei").set("solnum", "auto");
    model.study("std1").feature("phasei").set("notsolnum", "auto");
    model.study("std1").feature("phasei").set("outputmap", new String[]{});
    model.study("std1").feature("phasei").set("ngenAUX", "1");
    model.study("std1").feature("phasei").set("goalngenAUX", "1");
    model.study("std1").feature("phasei").set("ngenAUX", "1");
    model.study("std1").feature("phasei").set("goalngenAUX", "1");
    model.study("std1").feature("phasei").setSolveFor("/physics/spf", false);
    model.study("std1").feature("phasei").setSolveFor("/physics/spf", false);
    model.study("std1").create("time", "Transient");
    model.study("std1").feature("time").set("initstudy", "std1");
    model.study("std1").feature("time").set("notstudy", "std1");
    model.study("std1").feature("time").set("initialtime", "0");
    model.study("std1").feature("time").set("useinitsol", "on");
    model.study("std1").feature("time").set("notsolmethod", "sol");
    model.study("std1").feature("time").set("outputmap", new String[]{});

    model.component("comp1").geom("geom1").lengthUnit("mm");
    model.component("comp1").geom("geom1").create("r1", "Rectangle");
    model.component("comp1").geom("geom1").feature("r1").set("size", new double[]{0.3, 0.15});
    model.component("comp1").geom("geom1").feature("r1").set("pos", new double[]{0, -0.15});
    model.component("comp1").geom("geom1").run("r1");
    model.component("comp1").geom("geom1").create("r2", "Rectangle");
    model.component("comp1").geom("geom1").feature("r2").set("size", new double[]{0.15, 0.5});
    model.component("comp1").geom("geom1").run("r2");
    model.component("comp1").geom("geom1").run("fin");

    model.component("comp1").material().create("mpmat1", "Multiphase");
    model.component("comp1").material("mpmat1").selection().geom("geom1", 2);
    model.component("comp1").material("mpmat1").selection().set(1, 2);
    model.component("comp1").material("mpmat1").selection().inherit(false);
    model.component("comp1").material("mpmat1").selection().embedded(false);
    model.component("comp1").material("mpmat1").set("vfDefinition", "ls");
    model.component("comp1").material("mpmat1").feature().create("phase2", "PhaseLink", "comp1");

    model.component("comp1").multiphysics("tpf1").set("multiphaseMaterialList", "mpmat1");
    model.component("comp1").multiphysics("tpf1").set("IncludeSurfaceTension", true);

    model.material().create("mat1", "Common", "");
    model.material("mat1").propertyGroup("def").func().create("eta", "Piecewise");
    model.material("mat1").propertyGroup("def").func().create("Cp", "Piecewise");
    model.material("mat1").propertyGroup("def").func().create("rho", "Analytic");
    model.material("mat1").propertyGroup("def").func().create("k", "Piecewise");
    model.material("mat1").propertyGroup("def").func().create("cs", "Analytic");
    model.material("mat1").propertyGroup("def").func().create("an1", "Analytic");
    model.material("mat1").propertyGroup("def").func().create("an2", "Analytic");
    model.material("mat1").propertyGroup().create("RefractiveIndex", "RefractiveIndex", "Refractive index");
    model.material("mat1").propertyGroup().create("NonlinearModel", "NonlinearModel", "Nonlinear model");
    model.material("mat1").propertyGroup().create("idealGas", "idealGas", "Ideal gas");
    model.material("mat1").propertyGroup("idealGas").func().create("Cp", "Piecewise");
    model.material("mat1").label("Air");
    model.material("mat1").set("family", "air");
    model.material("mat1").propertyGroup("def").func("eta").set("arg", "T");
    model.material("mat1").propertyGroup("def").func("eta")
         .set("pieces", new String[][]{{"200.0", "1600.0", "-8.38278E-7+8.35717342E-8*T^1-7.69429583E-11*T^2+4.6437266E-14*T^3-1.06585607E-17*T^4"}});
    model.material("mat1").propertyGroup("def").func("eta").set("argunit", "K");
    model.material("mat1").propertyGroup("def").func("eta").set("fununit", "Pa*s");
    model.material("mat1").propertyGroup("def").func("Cp").set("arg", "T");
    model.material("mat1").propertyGroup("def").func("Cp")
         .set("pieces", new String[][]{{"200.0", "1600.0", "1047.63657-0.372589265*T^1+9.45304214E-4*T^2-6.02409443E-7*T^3+1.2858961E-10*T^4"}});
    model.material("mat1").propertyGroup("def").func("Cp").set("argunit", "K");
    model.material("mat1").propertyGroup("def").func("Cp").set("fununit", "J/(kg*K)");
    model.material("mat1").propertyGroup("def").func("rho").set("expr", "pA*0.02897/R_const[K*mol/J]/T");
    model.material("mat1").propertyGroup("def").func("rho").set("args", new String[]{"pA", "T"});
    model.material("mat1").propertyGroup("def").func("rho").set("fununit", "kg/m^3");
    model.material("mat1").propertyGroup("def").func("rho").set("argunit", new String[]{"Pa", "K"});
    model.material("mat1").propertyGroup("def").func("rho").set("plotaxis", new String[]{"off", "on"});
    model.material("mat1").propertyGroup("def").func("rho").set("plotfixedvalue", new String[]{"101325", "273.15"});
    model.material("mat1").propertyGroup("def").func("rho")
         .set("plotargs", new String[][]{{"pA", "101325", "101325"}, {"T", "273.15", "293.15"}});
    model.material("mat1").propertyGroup("def").func("k").set("arg", "T");
    model.material("mat1").propertyGroup("def").func("k")
         .set("pieces", new String[][]{{"200.0", "1600.0", "-0.00227583562+1.15480022E-4*T^1-7.90252856E-8*T^2+4.11702505E-11*T^3-7.43864331E-15*T^4"}});
    model.material("mat1").propertyGroup("def").func("k").set("argunit", "K");
    model.material("mat1").propertyGroup("def").func("k").set("fununit", "W/(m*K)");
    model.material("mat1").propertyGroup("def").func("cs").set("expr", "sqrt(1.4*R_const[K*mol/J]/0.02897*T)");
    model.material("mat1").propertyGroup("def").func("cs").set("args", new String[]{"T"});
    model.material("mat1").propertyGroup("def").func("cs").set("fununit", "m/s");
    model.material("mat1").propertyGroup("def").func("cs").set("argunit", new String[]{"K"});
    model.material("mat1").propertyGroup("def").func("cs").set("plotfixedvalue", new String[]{"273.15"});
    model.material("mat1").propertyGroup("def").func("cs")
         .set("plotargs", new String[][]{{"T", "273.15", "373.15"}});
    model.material("mat1").propertyGroup("def").func("an1").set("funcname", "alpha_p");
    model.material("mat1").propertyGroup("def").func("an1").set("expr", "-1/rho(pA,T)*d(rho(pA,T),T)");
    model.material("mat1").propertyGroup("def").func("an1").set("args", new String[]{"pA", "T"});
    model.material("mat1").propertyGroup("def").func("an1").set("fununit", "1/K");
    model.material("mat1").propertyGroup("def").func("an1").set("argunit", new String[]{"Pa", "K"});
    model.material("mat1").propertyGroup("def").func("an1").set("plotaxis", new String[]{"off", "on"});
    model.material("mat1").propertyGroup("def").func("an1").set("plotfixedvalue", new String[]{"101325", "273.15"});
    model.material("mat1").propertyGroup("def").func("an1")
         .set("plotargs", new String[][]{{"pA", "101325", "101325"}, {"T", "273.15", "373.15"}});
    model.material("mat1").propertyGroup("def").func("an2").set("funcname", "muB");
    model.material("mat1").propertyGroup("def").func("an2").set("expr", "0.6*eta(T)");
    model.material("mat1").propertyGroup("def").func("an2").set("args", new String[]{"T"});
    model.material("mat1").propertyGroup("def").func("an2").set("fununit", "Pa*s");
    model.material("mat1").propertyGroup("def").func("an2").set("argunit", new String[]{"K"});
    model.material("mat1").propertyGroup("def").func("an2").set("plotfixedvalue", new String[]{"200"});
    model.material("mat1").propertyGroup("def").func("an2").set("plotargs", new String[][]{{"T", "200", "1600"}});
    model.material("mat1").propertyGroup("def").set("thermalexpansioncoefficient", "");
    model.material("mat1").propertyGroup("def").set("molarmass", "");
    model.material("mat1").propertyGroup("def").set("bulkviscosity", "");
    model.material("mat1").propertyGroup("def")
         .set("thermalexpansioncoefficient", new String[]{"alpha_p(pA,T)", "0", "0", "0", "alpha_p(pA,T)", "0", "0", "0", "alpha_p(pA,T)"});
    model.material("mat1").propertyGroup("def").set("molarmass", "0.02897[kg/mol]");
    model.material("mat1").propertyGroup("def").set("bulkviscosity", "muB(T)");
    model.material("mat1").propertyGroup("def")
         .set("relpermeability", new String[]{"1", "0", "0", "0", "1", "0", "0", "0", "1"});
    model.material("mat1").propertyGroup("def")
         .set("relpermittivity", new String[]{"1", "0", "0", "0", "1", "0", "0", "0", "1"});
    model.material("mat1").propertyGroup("def").set("dynamicviscosity", "eta(T)");
    model.material("mat1").propertyGroup("def").set("ratioofspecificheat", "1.4");
    model.material("mat1").propertyGroup("def")
         .set("electricconductivity", new String[]{"0[S/m]", "0", "0", "0", "0[S/m]", "0", "0", "0", "0[S/m]"});
    model.material("mat1").propertyGroup("def").set("heatcapacity", "Cp(T)");
    model.material("mat1").propertyGroup("def").set("density", "rho(pA,T)");
    model.material("mat1").propertyGroup("def")
         .set("thermalconductivity", new String[]{"k(T)", "0", "0", "0", "k(T)", "0", "0", "0", "k(T)"});
    model.material("mat1").propertyGroup("def").set("soundspeed", "cs(T)");
    model.material("mat1").propertyGroup("def").addInput("temperature");
    model.material("mat1").propertyGroup("def").addInput("pressure");
    model.material("mat1").propertyGroup("RefractiveIndex")
         .set("n", new String[]{"1", "0", "0", "0", "1", "0", "0", "0", "1"});
    model.material("mat1").propertyGroup("NonlinearModel").set("BA", "def.gamma-1");
    model.material("mat1").propertyGroup("idealGas").func("Cp").label("Piecewise 2");
    model.material("mat1").propertyGroup("idealGas").func("Cp").set("arg", "T");
    model.material("mat1").propertyGroup("idealGas").func("Cp")
         .set("pieces", new String[][]{{"200.0", "1600.0", "1047.63657-0.372589265*T^1+9.45304214E-4*T^2-6.02409443E-7*T^3+1.2858961E-10*T^4"}});
    model.material("mat1").propertyGroup("idealGas").func("Cp").set("argunit", "K");
    model.material("mat1").propertyGroup("idealGas").func("Cp").set("fununit", "J/(kg*K)");
    model.material("mat1").propertyGroup("idealGas").set("Rs", "R_const/Mn");
    model.material("mat1").propertyGroup("idealGas").set("heatcapacity", "Cp(T)");
    model.material("mat1").propertyGroup("idealGas").set("ratioofspecificheat", "1.4");
    model.material("mat1").propertyGroup("idealGas").set("molarmass", "0.02897[kg/mol]");
    model.material("mat1").propertyGroup("idealGas").addInput("temperature");
    model.material("mat1").propertyGroup("idealGas").addInput("pressure");
    model.material("mat1").materialType("nonSolid");
    model.component("comp1").material("mpmat1").feature("phase1").set("link", "mat1");
    model.material().create("mat2", "Common", "");
    model.material("mat2").propertyGroup("def").func().create("eta", "Piecewise");
    model.material("mat2").propertyGroup("def").func().create("Cp", "Piecewise");
    model.material("mat2").propertyGroup("def").func().create("rho", "Piecewise");
    model.material("mat2").propertyGroup("def").func().create("k", "Piecewise");
    model.material("mat2").propertyGroup("def").func().create("cs", "Interpolation");
    model.material("mat2").propertyGroup("def").func().create("an1", "Analytic");
    model.material("mat2").propertyGroup("def").func().create("an2", "Analytic");
    model.material("mat2").propertyGroup("def").func().create("an3", "Analytic");
    model.material("mat2").label("Water, liquid");
    model.material("mat2").set("family", "water");
    model.material("mat2").propertyGroup("def").func("eta").set("arg", "T");
    model.material("mat2").propertyGroup("def").func("eta")
         .set("pieces", new String[][]{{"273.15", "413.15", "1.3799566804-0.021224019151*T^1+1.3604562827E-4*T^2-4.6454090319E-7*T^3+8.9042735735E-10*T^4-9.0790692686E-13*T^5+3.8457331488E-16*T^6"}, {"413.15", "553.75", "0.00401235783-2.10746715E-5*T^1+3.85772275E-8*T^2-2.39730284E-11*T^3"}});
    model.material("mat2").propertyGroup("def").func("eta").set("argunit", "K");
    model.material("mat2").propertyGroup("def").func("eta").set("fununit", "Pa*s");
    model.material("mat2").propertyGroup("def").func("Cp").set("arg", "T");
    model.material("mat2").propertyGroup("def").func("Cp")
         .set("pieces", new String[][]{{"273.15", "553.75", "12010.1471-80.4072879*T^1+0.309866854*T^2-5.38186884E-4*T^3+3.62536437E-7*T^4"}});
    model.material("mat2").propertyGroup("def").func("Cp").set("argunit", "K");
    model.material("mat2").propertyGroup("def").func("Cp").set("fununit", "J/(kg*K)");
    model.material("mat2").propertyGroup("def").func("rho").set("arg", "T");
    model.material("mat2").propertyGroup("def").func("rho").set("smooth", "contd1");
    model.material("mat2").propertyGroup("def").func("rho")
         .set("pieces", new String[][]{{"273.15", "293.15", "0.000063092789034*T^3-0.060367639882855*T^2+18.9229382407066*T-950.704055329848"}, {"293.15", "373.15", "0.000010335053319*T^3-0.013395065634452*T^2+4.969288832655160*T+432.257114008512"}});
    model.material("mat2").propertyGroup("def").func("rho").set("argunit", "K");
    model.material("mat2").propertyGroup("def").func("rho").set("fununit", "kg/m^3");
    model.material("mat2").propertyGroup("def").func("k").set("arg", "T");
    model.material("mat2").propertyGroup("def").func("k")
         .set("pieces", new String[][]{{"273.15", "553.75", "-0.869083936+0.00894880345*T^1-1.58366345E-5*T^2+7.97543259E-9*T^3"}});
    model.material("mat2").propertyGroup("def").func("k").set("argunit", "K");
    model.material("mat2").propertyGroup("def").func("k").set("fununit", "W/(m*K)");
    model.material("mat2").propertyGroup("def").func("cs")
         .set("table", new String[][]{{"273", "1403"}, 
         {"278", "1427"}, 
         {"283", "1447"}, 
         {"293", "1481"}, 
         {"303", "1507"}, 
         {"313", "1526"}, 
         {"323", "1541"}, 
         {"333", "1552"}, 
         {"343", "1555"}, 
         {"353", "1555"}, 
         {"363", "1550"}, 
         {"373", "1543"}});
    model.material("mat2").propertyGroup("def").func("cs").set("interp", "piecewisecubic");
    model.material("mat2").propertyGroup("def").func("cs").set("fununit", new String[]{"m/s"});
    model.material("mat2").propertyGroup("def").func("cs").set("argunit", new String[]{"K"});
    model.material("mat2").propertyGroup("def").func("an1").set("funcname", "alpha_p");
    model.material("mat2").propertyGroup("def").func("an1").set("expr", "-1/rho(T)*d(rho(T),T)");
    model.material("mat2").propertyGroup("def").func("an1").set("args", new String[]{"T"});
    model.material("mat2").propertyGroup("def").func("an1").set("fununit", "1/K");
    model.material("mat2").propertyGroup("def").func("an1").set("argunit", new String[]{"K"});
    model.material("mat2").propertyGroup("def").func("an1").set("plotfixedvalue", new String[]{"273.15"});
    model.material("mat2").propertyGroup("def").func("an1")
         .set("plotargs", new String[][]{{"T", "273.15", "373.15"}});
    model.material("mat2").propertyGroup("def").func("an2").set("funcname", "gamma_w");
    model.material("mat2").propertyGroup("def").func("an2").set("expr", "1+(T/Cp(T))*(alpha_p(T)*cs(T))^2");
    model.material("mat2").propertyGroup("def").func("an2").set("args", new String[]{"T"});
    model.material("mat2").propertyGroup("def").func("an2").set("fununit", "1");
    model.material("mat2").propertyGroup("def").func("an2").set("argunit", new String[]{"K"});
    model.material("mat2").propertyGroup("def").func("an2").set("plotfixedvalue", new String[]{"273.15"});
    model.material("mat2").propertyGroup("def").func("an2")
         .set("plotargs", new String[][]{{"T", "273.15", "373.15"}});
    model.material("mat2").propertyGroup("def").func("an3").set("funcname", "muB");
    model.material("mat2").propertyGroup("def").func("an3").set("expr", "2.79*eta(T)");
    model.material("mat2").propertyGroup("def").func("an3").set("args", new String[]{"T"});
    model.material("mat2").propertyGroup("def").func("an3").set("fununit", "Pa*s");
    model.material("mat2").propertyGroup("def").func("an3").set("argunit", new String[]{"K"});
    model.material("mat2").propertyGroup("def").func("an3").set("plotfixedvalue", new String[]{"273.15"});
    model.material("mat2").propertyGroup("def").func("an3")
         .set("plotargs", new String[][]{{"T", "273.15", "553.75"}});
    model.material("mat2").propertyGroup("def").set("thermalexpansioncoefficient", "");
    model.material("mat2").propertyGroup("def").set("bulkviscosity", "");
    model.material("mat2").propertyGroup("def")
         .set("thermalexpansioncoefficient", new String[]{"alpha_p(T)", "0", "0", "0", "alpha_p(T)", "0", "0", "0", "alpha_p(T)"});
    model.material("mat2").propertyGroup("def").set("bulkviscosity", "muB(T)");
    model.material("mat2").propertyGroup("def").set("dynamicviscosity", "eta(T)");
    model.material("mat2").propertyGroup("def").set("ratioofspecificheat", "gamma_w(T)");
    model.material("mat2").propertyGroup("def")
         .set("electricconductivity", new String[]{"5.5e-6[S/m]", "0", "0", "0", "5.5e-6[S/m]", "0", "0", "0", "5.5e-6[S/m]"});
    model.material("mat2").propertyGroup("def").set("heatcapacity", "Cp(T)");
    model.material("mat2").propertyGroup("def").set("density", "rho(T)");
    model.material("mat2").propertyGroup("def")
         .set("thermalconductivity", new String[]{"k(T)", "0", "0", "0", "k(T)", "0", "0", "0", "k(T)"});
    model.material("mat2").propertyGroup("def").set("soundspeed", "cs(T)");
    model.material("mat2").propertyGroup("def").addInput("temperature");
    model.component("comp1").material("mpmat1").feature("phase2").set("link", "mat2");

    model.component("comp1").multiphysics("ww1").selection().set(6, 7);
    model.component("comp1").multiphysics("ww1").set("thetaw", "(3*pi/8)[rad]");

    model.component("comp1").physics("ls").feature("lsm1").set("epsilon_ls", "5e-6");
    model.component("comp1").physics("ls").feature("initfluid2").selection().set(1);
    model.component("comp1").physics("spf").prop("PhysicalModelProperty").set("IncludeGravity", true);
    model.component("comp1").physics("spf").create("inl1", "InletBoundary", 1);
    model.component("comp1").physics("spf").feature("inl1").selection().set(8);
    model.component("comp1").physics("spf").feature("inl1").set("BoundaryCondition", "Pressure");
    model.component("comp1").physics("ls").create("inl1", "InletBoundary", 1);
    model.component("comp1").physics("ls").feature("inl1").selection().set(8);
    model.component("comp1").physics("ls").feature("inl1").set("lscond", "Fluid2ls");
    model.component("comp1").physics("ls").create("out1", "Outlet", 1);
    model.component("comp1").physics("ls").feature("out1").selection().set(5);
    model.component("comp1").physics("spf").create("out1", "OutletBoundary", 1);
    model.component("comp1").physics("spf").feature("out1").selection().set(5);
    model.component("comp1").physics("spf").feature("out1").set("CompensateForHydrostaticPressure", false);
    model.component("comp1").physics("spf").create("init2", "init", 2);
    model.component("comp1").physics("spf").feature("init2").selection().set(2);
    model.component("comp1").physics("spf").feature("init2").set("CompensateForHydrostaticPressure", false);

    model.component("comp1").variable().create("var1");
    model.component("comp1").variable("var1").set("theta", "(acos(tpf1.intnormr))[1/deg]");
    model.component("comp1").variable("var1").descr("theta", "Contact angle expression");

    model.component("comp1").probe().create("bnd1", "Boundary");
    model.component("comp1").probe("bnd1").set("intsurface", true);
    model.component("comp1").probe("bnd1").label("Meniscus Position");
    model.component("comp1").probe("bnd1").set("probename", "z_pos");
    model.component("comp1").probe("bnd1").set("intsurface", false);
    model.component("comp1").probe("bnd1").selection().set(6);
    model.component("comp1").probe("bnd1").set("expr", "ls.Vf2");
    model.component("comp1").probe("bnd1").set("descr", "Volume fraction of fluid 2");
    model.component("comp1").probe("bnd1").set("descractive", true);
    model.component("comp1").probe("bnd1").set("descr", "Contact point position");
    model.component("comp1").probe("bnd1").set("type", "integral");

    model.component("comp1").mesh("mesh1").create("map1", "Map");
    model.component("comp1").mesh("mesh1").feature("size").set("table", "cfd");
    model.component("comp1").mesh("mesh1").feature("size").set("hauto", 2);
    model.component("comp1").mesh("mesh1").run();

    model.study("std1").feature("time").set("tlist", "range(0,0.25e-4,1e-3)");
    model.study("std1").showAutoSequences("all");

    model.sol("sol1").feature("t1").set("tstepsbdf", "manual");
    model.sol("sol1").feature("t1").set("timestepbdf", "5e-6");
    model.sol("sol1").feature("t1").set("initialstepfractionbdf-2", "1e-3");

    model.study("std1").createAutoSequences("all");

    model.component("comp1").probe("bnd1").genResult("none");

    model.sol("sol1").runAll();

    model.result().dataset("dset1").set("geom", "geom1");
    model.result().create("pg2", "PlotGroup2D");
    model.result("pg2").label("Velocity (spf)");
    model.result("pg2").set("frametype", "spatial");
    model.result("pg2").set("smooth", "internal");
    model.result("pg2").feature().create("surf1", "Surface");
    model.result("pg2").feature("surf1").label("Surface");
    model.result("pg2").feature("surf1").set("smooth", "internal");
    model.result("pg2").feature("surf1").set("data", "parent");
    model.result().create("pg3", "PlotGroup2D");
    model.result("pg3").label("Pressure (spf)");
    model.result("pg3").set("frametype", "spatial");
    model.result("pg3").set("smooth", "internal");
    model.result("pg3").feature().create("surf1", "Surface");
    model.result("pg3").feature("surf1").set("expr", "p");
    model.result("pg3").feature("surf1").set("colortable", "Tectocoris");
    model.result("pg3").feature("surf1").set("colortabletype", "discrete");
    model.result("pg3").feature("surf1").set("bandcount", 25);
    model.result("pg3").feature("surf1").set("smooth", "internal");
    model.result("pg3").feature("surf1").set("data", "parent");
    model.result().dataset().create("rev1", "Revolve2D");
    model.result().dataset("rev1").label("Revolution 2D");
    model.result().dataset("rev1").set("data", "none");
    model.result().dataset("rev1").set("startangle", -90);
    model.result().dataset("rev1").set("revangle", 225);
    model.result().dataset("rev1").set("data", "dset1");
    model.result().create("pg4", "PlotGroup3D");
    model.result("pg4").label("Velocity, 3D (spf)");
    model.result("pg4").set("frametype", "spatial");
    model.result("pg4").set("smooth", "internal");
    model.result("pg4").feature().create("surf1", "Surface");
    model.result("pg4").feature("surf1").label("Surface");
    model.result("pg4").feature("surf1").set("smooth", "internal");
    model.result("pg4").feature("surf1").set("data", "parent");
    model.result().create("pg5", "PlotGroup2D");
    model.result("pg5").label("Volume Fraction of Fluid 1 (ls)");
    model.result("pg5").set("frametype", "spatial");
    model.result("pg5").feature().create("surf1", "Surface");
    model.result("pg5").feature("surf1").set("expr", "ls.Vf1");
    model.result("pg5").feature("surf1").set("smooth", "internal");
    model.result("pg5").feature("surf1").set("data", "parent");
    model.result("pg5").feature().create("con1", "Contour");
    model.result("pg5").feature("con1").set("expr", "ls.Vf1");
    model.result("pg5").feature("con1").set("levelmethod", "levels");
    model.result("pg5").feature("con1").set("levels", "0.5");
    model.result("pg5").feature("con1").set("coloring", "uniform");
    model.result("pg5").feature("con1").set("colorlegend", false);
    model.result("pg5").feature("con1").set("color", "gray");
    model.result("pg5").feature("con1").set("smooth", "none");
    model.result("pg5").feature("con1").set("data", "parent");
    model.result().dataset().create("rev2", "Revolve2D");
    model.result().dataset("rev2").label("Revolution 2D 1");
    model.result().dataset("rev2").set("data", "dset1");
    model.result().create("pg6", "PlotGroup3D");
    model.result("pg6").label("Volume Fraction of Fluid 1 (ls) 1");
    model.result("pg6").set("data", "rev2");
    model.result("pg6").set("frametype", "spatial");
    model.result("pg6").feature().create("iso1", "Isosurface");
    model.result("pg6").feature("iso1").set("expr", "ls.Vf1");
    model.result("pg6").feature("iso1").set("levelmethod", "levels");
    model.result("pg6").feature("iso1").set("levels", "0.5");
    model.result("pg6").feature("iso1").set("coloring", "uniform");
    model.result("pg6").feature("iso1").set("color", "gray");
    model.result("pg6").feature("iso1").set("smooth", "none");
    model.result("pg6").feature("iso1").set("data", "parent");
    model.result("pg2").run();
    model.result("pg5").run();
    model.result("pg5").run();
    model.result("pg5").feature("con1").set("contourtype", "filled");
    model.result("pg5").feature("con1").set("coloring", "colortable");
    model.result("pg5").feature("con1").set("colortable", "GrayScale");
    model.result("pg5").feature("con1").set("colorlegend", true);
    model.result("pg5").feature("con1").set("legendtype", "lines");
    model.result("pg5").run();
    model.result("pg5").feature().remove("surf1");
    model.result("pg5").run();
    model.result("pg5").run();
    model.result("pg5").setIndex("looplevel", 1, 0);
    model.result("pg5").run();
    model.result("pg5").setIndex("looplevel", 2, 0);
    model.result("pg5").run();
    model.result("pg5").setIndex("looplevel", 3, 0);
    model.result("pg5").run();
    model.result("pg5").setIndex("looplevel", 4, 0);
    model.result("pg5").run();
    model.result("pg5").setIndex("looplevel", 5, 0);
    model.result("pg5").run();
    model.result("pg5").setIndex("looplevel", 6, 0);
    model.result("pg5").run();
    model.result("pg5").setIndex("looplevel", 7, 0);
    model.result("pg5").run();
    model.result("pg2").run();
    model.result("pg2").run();
    model.result("pg2").feature().remove("surf1");
    model.result("pg2").run();
    model.result("pg2").create("arws1", "ArrowSurface");
    model.result("pg2").feature("arws1").set("evaluationsettings", "parent");
    model.result("pg2").feature("arws1").set("ynumber", 30);
    model.result("pg2").run();
    model.result("pg2").create("con1", "Contour");
    model.result("pg2").feature("con1").set("evaluationsettings", "parent");
    model.result("pg2").feature("con1").set("expr", "tpf1.Vf1");
    model.result("pg2").feature("con1").set("levelmethod", "levels");
    model.result("pg2").feature("con1").set("levels", 0.5);
    model.result("pg2").feature("con1").set("coloring", "uniform");
    model.result("pg2").feature("con1").set("color", "gray");
    model.result("pg2").run();
    model.result("pg2").setIndex("looplevel", 9, 0);
    model.result("pg2").run();
    model.result("pg2").setIndex("looplevel", 17, 0);
    model.result("pg2").run();
    model.result("pg2").setIndex("looplevel", 25, 0);
    model.result("pg2").run();
    model.result("pg2").setIndex("looplevel", 33, 0);
    model.result("pg2").run();
    model.result("pg4").run();
    model.result().dataset("rev1").set("startangle", 0);
    model.result().dataset("rev1").set("revangle", 360);
    model.result().dataset("rev2").set("revangle", 230);
    model.result().dataset().create("edg1", "Edge2D");
    model.result().dataset("edg1").selection().set(6, 7);
    model.result().dataset().create("rev3", "Revolve2D");
    model.result().dataset("rev3").set("data", "edg1");
    model.result().dataset("rev3").set("revangle", 230);
    model.result().dataset().create("edg2", "Edge2D");
    model.result().dataset("edg2").selection().set(2);
    model.result().dataset().create("rev4", "Revolve2D");
    model.result().dataset("rev4").set("data", "edg2");
    model.result("pg6").run();
    model.result("pg6").set("data", "rev1");
    model.result("pg6").setIndex("looplevel", 13, 0);
    model.result("pg6").set("view", "view2");
    model.result("pg6").set("edges", false);
    model.result("pg6").run();
    model.result("pg6").run();
    model.result("pg6").feature("iso1").set("color", "white");
    model.result("pg6").run();
    model.result("pg6").create("surf1", "Surface");
    model.result("pg6").feature("surf1").set("evaluationsettings", "parent");
    model.result("pg6").feature("surf1").set("expr", "ls.Vf1");
    model.result("pg6").feature("surf1").set("colortable", "Cividis");
    model.result("pg6").feature("surf1").set("data", "rev2");
    model.result("pg6").feature("surf1").setIndex("looplevel", 13, 0);
    model.result("pg6").run();
    model.result("pg6").run();
    model.result("pg6").create("surf2", "Surface");
    model.result("pg6").feature("surf2").set("evaluationsettings", "parent");
    model.result("pg6").feature("surf2").set("data", "rev3");
    model.result("pg6").feature("surf2").set("coloring", "uniform");
    model.result("pg6").feature("surf2").set("color", "gray");
    model.result("pg6").run();
    model.result("pg6").create("surf3", "Surface");
    model.result("pg6").feature("surf3").set("evaluationsettings", "parent");
    model.result("pg6").feature("surf3").set("data", "rev4");
    model.result("pg6").feature("surf3").set("coloring", "uniform");
    model.result("pg6").feature("surf3").set("color", "gray");
    model.result("pg6").run();
    model.result("pg3").run();
    model.result("pg3").setIndex("looplevel", 25, 0);
    model.result("pg3").run();
    model.result("pg3").feature("surf1").set("colortable", "JupiterAuroraBorealis");
    model.result("pg3").feature("surf1").set("colortabletrans", "reverse");
    model.result("pg3").run();
    model.result("pg1").set("window", "window1");
    model.result("pg1").run();
    model.result("pg1").label("Meniscus position");
    model.result("pg1").set("showlegends", false);
    model.result("pg1").set("window", "window1");
    model.result("pg1").run();
    model.result().create("pg7", "PlotGroup2D");
    model.result("pg7").run();
    model.result("pg7").setIndex("looplevel", 25, 0);
    model.result("pg7").create("con1", "Contour");
    model.result("pg7").feature("con1").set("evaluationsettings", "parent");

    return model;
  }

  public static Model run2(Model model) {
    model.result("pg7").feature("con1").set("levelmethod", "levels");
    model.result("pg7").feature("con1").set("expr", "ls.Vf1");
    model.result("pg7").feature("con1").set("levels", 0.5);
    model.result("pg7").feature("con1").create("col1", "Color");
    model.result("pg7").run();
    model.result("pg7").feature("con1").feature("col1").set("expr", "theta");
    model.result("pg7").feature("con1").feature("col1").set("descr", "Contact angle expression");
    model.result("pg7").run();
    model.result("pg7").label("Meniscus Angle");
    model.result("pg7").set("showlegendsmaxmin", true);
    model.result("pg7").run();
    model.result("pg6").run();

    model.title("Capillary Filling \u2014 Level Set Method");

    model
         .description("Transient model that simulates the filling of a narrow channel due to surface tension and wall adhesion. The capillary channel is initially filled with air. Because it is attached to a water reservoir, capillary forces cause water to rise through the channel. The contact angle, the angle between the water surface and the wall, is fixed to 67.5 degrees. The model can be solved using either a level set or a phase field method to track the fluid interface. This example uses the level set method.");

    model.mesh().clearMeshes();

    model.sol("sol1").clearSolutionData();
    model.sol("sol2").clearSolutionData();

    model.label("capillary_filling_ls.mph");

    return model;
  }

  public static void main(String[] args) {
    Model model = run();
    run2(model);
  }

}
