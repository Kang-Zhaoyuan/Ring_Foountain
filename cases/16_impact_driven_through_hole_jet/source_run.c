/*
 * Case 16: impact-driven through-hole-jet diagnostics and inner-wetting modes.
 *
 * Coordinates are Basilisk AXI coordinates: x is axial/upward, y is radial,
 * and y = 0 is the symmetry axis.  The ring is fixed in its translating frame.
 * Liquid and gas enter upward at the measured ring speed.  The frame receives
 * gravity plus the fictitious acceleration associated with the prescribed
 * post-contact deceleration.
 *
 * The wetting closure is deliberately small and explicit.  A monotone scalar
 * propagates through a thin embedded-solid shell using physical arclength
 * measured from the leading face.  Its propagation speed is a model parameter
 * in m/s and does not depend on the number of cells through the ring.  The
 * scalar supplies liquid VOF values only in full-solid ghost cells; physical
 * cut-cell VOF is never overwritten.  Any resulting mobile-liquid source is
 * nevertheless measured at every step.
 */

#include "grid/multigrid.h"
#include "embed.h"
#include "axi.h"
#include "navier-stokes/centered.h"
#define FILTERED 1
#include "two-phase.h"
#include "tension.h"
#include "tag.h"
#include "output.h"

#include <errno.h>
#include <sys/stat.h>

typedef struct {
  int level;
  int wetting_mode, geometry_mode;
  double t_end, output_interval;
  double Ri, Ro, thickness, ring_mass;
  double rho_liquid, rho_gas, mu_liquid, mu_gas;
  double surface_tension, gravity;
  double impact_speed, terminal_speed, trajectory_decay_rate;
  double wetting_speed, wetting_band_cells, wetting_relaxation_time;
  double max_speed_abort;
} Config;

static Config cfg = {
  7, 0, 0, 0.006, 0.001,
  0.00505, 0.02007, 0.00286, 0.02615,
  998., 1.2, 1.e-3, 1.8e-5,
  0.072, 9.81,
  1.34555038115, 0.720414774329, 76.9112141855,
  0.0297916666667, 1.25, 0.005,
  100.
};

static const double domain_axial = 0.960;
static const double domain_radial = 0.120;
static const double domain_x_origin = -0.240;

scalar wet[];

static char output_directory[512] = ".";
static FILE * diagnostics_fp = NULL;
static FILE * jet_fp = NULL, * flux_fp = NULL, * pressure_fp = NULL;
static double initial_liquid_volume = 0.;
static double cumulative_wetting_source = 0.;
static int simulation_status = 0;
static double minimum_dt_seen = HUGE;
static bool previous_jet_detected = false;
static double jet_onset_time = -1.;

u.n[embed] = dirichlet (0.);
u.t[embed] = dirichlet (0.);

/* At the lower axial boundary u.n is the positive-x inflow velocity. */
static double frame_speed = 1.34555038115;
u.n[left] = dirichlet (frame_speed);
u.t[left] = dirichlet (0.);
f[left] = dirichlet (1.);
p[left] = neumann (0.);
pf[left] = neumann (0.);

u.n[right] = neumann (0.);
p[right] = dirichlet (0.);
pf[right] = dirichlet (0.);

/* The outer radial boundary is a slip/no-penetration boundary. */
u.n[top] = dirichlet (0.);
u.t[top] = neumann (0.);
p[top] = neumann (0.);
pf[top] = neumann (0.);

static double ring_levelset (double xx, double rr)
{
  if (cfg.geometry_mode == 1) /* no-ring regression */
    return 1.;
  if (cfg.geometry_mode == 2) /* closed disk regression */
    return max (rr - cfg.Ro, fabs(xx) - cfg.thickness/2.);
  return max (max (cfg.Ri - rr, rr - cfg.Ro),
              fabs (xx) - cfg.thickness/2.);
}

/* Shortest surface arclength from the leading lower face.  The bottom is wet
 * at first contact, both vertical faces advance over the physical thickness,
 * and arrival at the upper corners releases the complete trailing face. */
static double wetting_surface_distance (double xx, double rr)
{
  const double dlower = fabs(xx + cfg.thickness/2.);
  const double dupper = fabs(xx - cfg.thickness/2.);
  const double dinner = fabs(rr - cfg.Ri);
  const double douter = fabs(rr - cfg.Ro);
  const double nearest = min(min(dlower, dupper), min(dinner, douter));

  if (nearest == dlower)
    return 0.;
  if (nearest == dinner || nearest == douter)
    return clamp(xx + cfg.thickness/2., 0., cfg.thickness);
  return cfg.thickness;
}

static bool nearest_surface_is_inner (double xx, double rr)
{
  if (cfg.geometry_mode != 0)
    return false;
  const double dlower = fabs(xx + cfg.thickness/2.);
  const double dupper = fabs(xx - cfg.thickness/2.);
  const double dinner = fabs(rr - cfg.Ri);
  const double douter = fabs(rr - cfg.Ro);
  return dinner <= dlower && dinner <= dupper && dinner <= douter;
}

static double prescribed_speed (double tau)
{
  return cfg.terminal_speed +
    (cfg.impact_speed - cfg.terminal_speed)*
    exp (-cfg.trajectory_decay_rate*max(tau, 0.));
}

static double prescribed_speed_derivative (double tau)
{
  return -cfg.trajectory_decay_rate*
    (cfg.impact_speed - cfg.terminal_speed)*
    exp (-cfg.trajectory_decay_rate*max(tau, 0.));
}

static double prescribed_depth (double tau)
{
  if (tau <= 0.)
    return 0.;
  return cfg.terminal_speed*tau +
    (cfg.impact_speed - cfg.terminal_speed)*
    (1. - exp(-cfg.trajectory_decay_rate*tau))/cfg.trajectory_decay_rate;
}

static double undisturbed_surface_x (double tau)
{
  return -cfg.thickness/2. + prescribed_depth(tau);
}

static void make_output_path (char * path, size_t length, const char * name)
{
  if (snprintf(path, length, "%s/%s", output_directory, name) >= (int) length) {
    fprintf(stderr, "output path is too long: %s/%s\n", output_directory, name);
    exit(2);
  }
}

static int set_parameter (const char * key, const char * value)
{
  if (!strcmp(key, "level")) cfg.level = atoi(value);
  else if (!strcmp(key, "wetting_mode")) cfg.wetting_mode = atoi(value);
  else if (!strcmp(key, "geometry_mode")) cfg.geometry_mode = atoi(value);
  else if (!strcmp(key, "t_end")) cfg.t_end = atof(value);
  else if (!strcmp(key, "output_interval")) cfg.output_interval = atof(value);
  else if (!strcmp(key, "Ri")) cfg.Ri = atof(value);
  else if (!strcmp(key, "Ro")) cfg.Ro = atof(value);
  else if (!strcmp(key, "thickness")) cfg.thickness = atof(value);
  else if (!strcmp(key, "ring_mass")) cfg.ring_mass = atof(value);
  else if (!strcmp(key, "rho_liquid")) cfg.rho_liquid = atof(value);
  else if (!strcmp(key, "rho_gas")) cfg.rho_gas = atof(value);
  else if (!strcmp(key, "mu_liquid")) cfg.mu_liquid = atof(value);
  else if (!strcmp(key, "mu_gas")) cfg.mu_gas = atof(value);
  else if (!strcmp(key, "surface_tension")) cfg.surface_tension = atof(value);
  else if (!strcmp(key, "gravity")) cfg.gravity = atof(value);
  else if (!strcmp(key, "impact_speed")) cfg.impact_speed = atof(value);
  else if (!strcmp(key, "terminal_speed")) cfg.terminal_speed = atof(value);
  else if (!strcmp(key, "trajectory_decay_rate")) cfg.trajectory_decay_rate = atof(value);
  else if (!strcmp(key, "wetting_speed")) cfg.wetting_speed = atof(value);
  else if (!strcmp(key, "wetting_band_cells")) cfg.wetting_band_cells = atof(value);
  else if (!strcmp(key, "wetting_relaxation_time")) cfg.wetting_relaxation_time = atof(value);
  else if (!strcmp(key, "max_speed_abort")) cfg.max_speed_abort = atof(value);
  else {
    fprintf(stderr, "unknown parameter '%s'\n", key);
    return -1;
  }
  return 0;
}

static int read_parameters (const char * path)
{
  FILE * fp = fopen(path, "r");
  if (!fp) {
    fprintf(stderr, "cannot open parameter file '%s': %s\n",
            path, strerror(errno));
    return -1;
  }
  char line[512];
  int lineno = 0;
  while (fgets(line, sizeof line, fp)) {
    lineno++;
    char * cursor = line;
    while (*cursor == ' ' || *cursor == '\t') cursor++;
    if (*cursor == '#' || *cursor == '\n' || *cursor == '\0')
      continue;
    char key[128], value[256], extra;
    if (sscanf(cursor, " %127[^=]=%255s %c", key, value, &extra) < 2) {
      fprintf(stderr, "%s:%d: expected key=value\n", path, lineno);
      fclose(fp);
      return -1;
    }
    size_t n = strlen(key);
    while (n && (key[n - 1] == ' ' || key[n - 1] == '\t'))
      key[--n] = '\0';
    if (set_parameter(key, value)) {
      fprintf(stderr, "%s:%d: invalid parameter\n", path, lineno);
      fclose(fp);
      return -1;
    }
  }
  fclose(fp);
  return 0;
}

static int parameters_are_valid (void)
{
  return cfg.level >= 5 && cfg.level <= 9 &&
    cfg.wetting_mode >= 0 && cfg.wetting_mode <= 2 &&
    cfg.geometry_mode >= 0 && cfg.geometry_mode <= 2 &&
    cfg.t_end > 0. && cfg.output_interval > 0. &&
    cfg.Ri > 0. && cfg.Ro > cfg.Ri && cfg.thickness > 0. &&
    cfg.rho_liquid > 0. && cfg.rho_gas > 0. &&
    cfg.mu_liquid >= 0. && cfg.mu_gas >= 0. &&
    cfg.surface_tension > 0. && cfg.gravity >= 0. &&
    cfg.impact_speed > 0. && cfg.terminal_speed >= 0. &&
    cfg.trajectory_decay_rate > 0. && cfg.wetting_speed >= 0. &&
    cfg.wetting_band_cells > 0. && cfg.wetting_relaxation_time > 0. &&
    cfg.max_speed_abort > 0.;
}

static double liquid_volume (void)
{
  double volume = 0.;
  foreach(reduction(+:volume))
    volume += 2.*pi*y*sq(Delta)*cs[]*clamp(f[], 0., 1.);
  return volume;
}

static void write_parameters (void)
{
  char path[1024];
  make_output_path(path, sizeof path, "effective_parameters.tsv");
  FILE * fp = fopen(path, "w");
  if (!fp) {
    fprintf(stderr, "cannot write %s\n", path);
    exit(2);
  }
  fprintf(fp, "parameter\tvalue\tunit\n");
  fprintf(fp, "level\t%d\t-\n", cfg.level);
  fprintf(fp, "wetting_mode\t%d\t0=legacy,1=contact_inner,2=instant_inner\n",
          cfg.wetting_mode);
  fprintf(fp, "geometry_mode\t%d\t0=ring,1=no_ring,2=closed_disk\n",
          cfg.geometry_mode);
  fprintf(fp, "t_end\t%.17g\ts\n", cfg.t_end);
  fprintf(fp, "output_interval\t%.17g\ts\n", cfg.output_interval);
  fprintf(fp, "Ri\t%.17g\tm\n", cfg.Ri);
  fprintf(fp, "Ro\t%.17g\tm\n", cfg.Ro);
  fprintf(fp, "thickness\t%.17g\tm\n", cfg.thickness);
  fprintf(fp, "ring_mass\t%.17g\tkg\n", cfg.ring_mass);
  fprintf(fp, "rho_liquid\t%.17g\tkg/m3\n", cfg.rho_liquid);
  fprintf(fp, "rho_gas\t%.17g\tkg/m3\n", cfg.rho_gas);
  fprintf(fp, "mu_liquid\t%.17g\tPa*s\n", cfg.mu_liquid);
  fprintf(fp, "mu_gas\t%.17g\tPa*s\n", cfg.mu_gas);
  fprintf(fp, "surface_tension\t%.17g\tN/m\n", cfg.surface_tension);
  fprintf(fp, "gravity\t%.17g\tm/s2\n", cfg.gravity);
  fprintf(fp, "impact_speed\t%.17g\tm/s\n", cfg.impact_speed);
  fprintf(fp, "terminal_speed\t%.17g\tm/s\n", cfg.terminal_speed);
  fprintf(fp, "trajectory_decay_rate\t%.17g\t1/s\n", cfg.trajectory_decay_rate);
  fprintf(fp, "wetting_speed\t%.17g\tm/s\n", cfg.wetting_speed);
  fprintf(fp, "wetting_band_cells\t%.17g\tcells\n", cfg.wetting_band_cells);
  fprintf(fp, "wetting_relaxation_time\t%.17g\ts\n", cfg.wetting_relaxation_time);
  fclose(fp);
}

int main (int argc, char ** argv)
{
  if (argc > 2) {
    fprintf(stderr, "usage: %s [parameter-file]\n", argv[0]);
    return 2;
  }
  if (argc == 2 && read_parameters(argv[1]))
    return 2;
  if (!parameters_are_valid()) {
    fprintf(stderr, "invalid parameter set\n");
    return 2;
  }

  const char * requested_output = getenv("RUN_OUTPUT_DIR");
  if (requested_output && *requested_output) {
    strncpy(output_directory, requested_output, sizeof output_directory - 1);
    output_directory[sizeof output_directory - 1] = '\0';
  }

  dimensions (nx = 8);
  size (domain_axial);
  origin (domain_x_origin, 0.);
  /* cfg.level is the radial level.  The 8:1 domain therefore needs three
   * additional axial levels: L7 -> 1024 x 128 and Delta = 0.9375 mm. */
  init_grid (1 << (cfg.level + 3));

  rho1 = cfg.rho_liquid;
  rho2 = cfg.rho_gas;
  mu1 = cfg.mu_liquid;
  mu2 = cfg.mu_gas;
  f.sigma = cfg.surface_tension;

  CFL = 0.4;
  DT = 1.e-4;
  TOLERANCE = 1.e-5;
  frame_speed = cfg.impact_speed;

  write_parameters();
  run();
  return simulation_status;
}

event init (t = 0)
{
  solid (cs, fs, ring_levelset(x, y));
  fractions_cleanup (cs, fs);

  const double surface = -cfg.thickness/2.;
  fraction (f, surface - x);
  foreach() {
    wet[] = 0.;
    if (cs[] <= 1.e-12)
      f[] = 0.;
    u.x[] = cfg.impact_speed*cs[];
    u.y[] = 0.;
  }
  boundary ((scalar *){f, wet, u});

  initial_liquid_volume = liquid_volume();
  char path[1024];
  make_output_path(path, sizeof path, "diagnostics.tsv");
  diagnostics_fp = fopen(path, "w");
  if (!diagnostics_fp) {
    fprintf(stderr, "cannot write %s\n", path);
    simulation_status = 2;
    return 1;
  }
  fprintf(diagnostics_fp,
          "i\tt\tdt\tframe_speed\tframe_acceleration\tring_depth\t"
          "liquid_volume\texpected_volume\tbudget_residual\twetting_source\t"
          "wetting_front_distance\twet_shell_fraction\tkinetic_energy\t"
          "max_speed\tmax_speed_x\tmax_speed_r\tmax_speed_f\tmax_speed_cs\t"
          "min_dt\tleaf_cells\tliquid_components\tconnected_height\t"
          "center_height\tinvalid\n");
  fflush(diagnostics_fp);

  make_output_path(path, sizeof path, "jet_metrics.tsv");
  jet_fp = fopen(path, "w");
  make_output_path(path, sizeof path, "aperture_flux.tsv");
  flux_fp = fopen(path, "w");
  make_output_path(path, sizeof path, "pressure_budget.tsv");
  pressure_fp = fopen(path, "w");
  if (!jet_fp || !flux_fp || !pressure_fp) {
    fprintf(stderr, "cannot open Case 16 diagnostic tables\n");
    simulation_status = 2;
    return 1;
  }
  fprintf(jet_fp, "i\tt\tjet_detected\tjet_onset_time\tH_through\tH_PLIC\t"
          "jet_base_radius\tjet_tip_radius\tjet_column_length\t"
          "main_pool_connected\tisolated_drop_included\tpersistent\n");
  fprintf(flux_fp, "i\tt\tstation\tx_ring\tQ\tpositive_Q\tnegative_Q\t"
          "mass_flow\taxial_momentum_flux\tliquid_area\tmean_ring_velocity\t"
          "mean_lab_velocity\n");
  fprintf(pressure_fp, "i\tt\timpact_pressure\tinner_lower_pressure\t"
          "axis_pressure\tinner_upper_pressure\tinner_edge_dp\t"
          "inner_grad_x\tinner_grad_r\tinward_velocity\tupward_velocity\t"
          "max_speed\tmax_speed_x\tmax_speed_r\tmax_speed_f\tmax_speed_cs\n");
  fflush(jet_fp); fflush(flux_fp); fflush(pressure_fp);
}

event acceleration (i++)
{
  frame_speed = prescribed_speed(t);
  const double frame_acceleration = -cfg.gravity +
    prescribed_speed_derivative(t);
  face vector av = a;
  foreach_face(x)
    av.x[] += frame_acceleration;
}

event dynamic_wetting (i++)
{
  scalar next_wet[];
  const double front_distance = cfg.wetting_speed*t;

  foreach() {
    const double phi = ring_levelset(x, y);
    const bool shell = phi <= 0. &&
      phi >= -cfg.wetting_band_cells*Delta && cs[] < 1.;
    if (!shell) {
      next_wet[] = wet[];
      continue;
    }

    const double surface_distance = wetting_surface_distance(x, y);
    double target = 0.;
    const bool inner = nearest_surface_is_inner(x, y);
    if (inner && cfg.wetting_mode == 2)
      target = 1.;
    else if (inner && cfg.wetting_mode == 1) {
      double adjacent_liquid = 0.;
      foreach_neighbor(1)
        if (cs[] > 1.e-6 && f[] >= 0.5)
          adjacent_liquid = 1.;
      target = adjacent_liquid;
    }
    else if (surface_distance <= 0.)
      target = 1.;
    else if (front_distance > surface_distance)
      target = clamp((front_distance - surface_distance)/
                     max(cfg.wetting_speed*cfg.wetting_relaxation_time,
                         1.e-30), 0., 1.);
    next_wet[] = max(wet[], target);
  }
  boundary ({next_wet});

  double added = 0.;
  foreach(reduction(+:added)) {
    const double oldf = f[];
    wet[] = next_wet[];
    /* Write only full-solid ghost cells.  Physical cut cells are never
     * converted into liquid by the closure. */
    if (ring_levelset(x, y) <= 0. &&
        ring_levelset(x, y) >= -cfg.wetting_band_cells*Delta &&
        cs[] <= 1.e-12)
      f[] = max(f[], wet[]);
    added += 2.*pi*y*sq(Delta)*cs[]*max(f[] - oldf, 0.);
  }
  cumulative_wetting_source += added;
  boundary ((scalar *){f, wet});
}

static void connected_heights (int * component_count,
                               double * connected_height,
                               double * center_height)
{
  scalar labels[];
  foreach()
    labels[] = cs[] > 1.e-6 && f[] > 1.e-4;
  int n = tag(labels);
  *component_count = n;
  *connected_height = 0.;
  *center_height = 0.;
  if (n <= 0)
    return;

  double * volumes = (double *) calloc(n, sizeof(double));
  foreach(serial) {
    const int label = (int) labels[];
    if (label > 0)
      volumes[label - 1] += 2.*pi*y*sq(Delta)*cs[]*clamp(f[], 0., 1.);
  }
  int main_label = 1;
  for (int j = 1; j < n; j++)
    if (volumes[j] > volumes[main_label - 1])
      main_label = j + 1;
  free(volumes);

  const double surface = undisturbed_surface_x(t);
  double h_main = -HUGE, h_center = -HUGE;
  foreach(reduction(max:h_main) reduction(max:h_center)) {
    if ((int) labels[] == main_label && cs[] > 1.e-6 && f[] > 1.e-4) {
      const double height = x - surface;
      h_main = max(h_main, height);
      if (y <= 2.*Delta)
        h_center = max(h_center, height);
    }
  }
  *connected_height = h_main > -HUGE/2. ? max(h_main, 0.) : 0.;
  *center_height = h_center > -HUGE/2. ? max(h_center, 0.) : 0.;
}

static void through_hole_metrics (bool * detected, double * h_cell,
                                  double * h_plic, double * base_radius,
                                  double * tip_radius, double * column_length)
{
  *detected = false;
  *h_cell = *h_plic = *base_radius = *tip_radius = *column_length = -1.;
  if (cfg.geometry_mode != 0)
    return;

  scalar labels[];
  foreach()
    labels[] = cs[] > 1.e-6 && f[] > 1.e-4;
  int nlabels = tag(labels);
  if (nlabels <= 0)
    return;
  double * volumes = (double *) calloc(nlabels, sizeof(double));
  foreach(serial) {
    int label = (int) labels[];
    if (label > 0)
      volumes[label - 1] += 2.*pi*y*sq(Delta)*cs[]*clamp(f[], 0., 1.);
  }
  int main_label = 1;
  for (int j = 1; j < nlabels; j++)
    if (volumes[j] > volumes[main_label - 1])
      main_label = j + 1;
  free(volumes);

  int below = 0, inside = 0, above = 0;
  double top_cell_x = -HUGE, base_r = 0.;
  foreach(reduction(max:below) reduction(max:inside) reduction(max:above)
          reduction(max:top_cell_x) reduction(max:base_r)) {
    if ((int) labels[] != main_label || f[] < 0.5 || cs[] <= 1.e-6 ||
        y > cfg.Ri - Delta/2.)
      continue;
    if (x < -cfg.thickness/2. - Delta/2.) below = 1;
    if (fabs(x) <= cfg.thickness/2.) inside = 1;
    if (x > cfg.thickness/2. + Delta/2.) above = 1;
    if (x > cfg.thickness/2.)
      top_cell_x = max(top_cell_x, x);
    if (fabs(x - (cfg.thickness/2. + Delta)) <= Delta)
      base_r = max(base_r, y + Delta/2.);
  }
  if (!(below && inside && above) || top_cell_x <= -HUGE/2.)
    return;

  vector normal[];
  scalar alpha[];
  reconstruction(f, normal, alpha);
  double top_plic_x = -HUGE;
  foreach(reduction(max:top_plic_x)) {
    if ((int) labels[] != main_label || cs[] <= 1.e-6 ||
        f[] <= 1.e-6 || f[] >= 1. - 1.e-6 || y > cfg.Ri + Delta)
      continue;
    coord nn = {normal.x[], normal.y[]}, segment[2];
    if (facets(nn, alpha[], segment) == 2)
      for (int k = 0; k < 2; k++) {
        const double px = x + segment[k].x*Delta;
        const double pr = y + segment[k].y*Delta;
        if (pr >= 0. && pr <= cfg.Ri - Delta/2. &&
            px > cfg.thickness/2.)
          top_plic_x = max(top_plic_x, px);
      }
  }
  if (top_plic_x <= -HUGE/2.)
    return;
  double tip_r = 0.;
  foreach(reduction(max:tip_r))
    if ((int) labels[] == main_label && f[] >= 0.5 && cs[] > 1.e-6 &&
        fabs(x - top_plic_x) <= 2.*Delta && y <= cfg.Ri - Delta/2.)
      tip_r = max(tip_r, y + Delta/2.);

  const double surface = undisturbed_surface_x(t);
  *detected = true;
  *h_cell = max(top_cell_x - surface, 0.);
  *h_plic = max(top_plic_x - surface, 0.);
  *base_radius = min(base_r, cfg.Ri);
  *tip_radius = min(tip_r, cfg.Ri);
  *column_length = max(top_plic_x - cfg.thickness/2., 0.);
}

static void write_flux_station (int iteration, const char * name, double station)
{
  double q = 0., qp = 0., qn = 0., momentum = 0., area = 0.;
  foreach(reduction(+:q) reduction(+:qp) reduction(+:qn)
          reduction(+:momentum) reduction(+:area))
    if (fabs(x - station) <= Delta/2. && y <= cfg.Ri && cs[] > 1.e-6) {
      const double dA = 2.*pi*y*Delta*cs[]*clamp(f[], 0., 1.);
      const double dq = dA*u.x[];
      q += dq;
      if (dq >= 0.) qp += dq; else qn += dq;
      momentum += cfg.rho_liquid*dA*u.x[]*fabs(u.x[]);
      area += dA;
    }
  const double mean = area > 0. ? q/area : 0.;
  fprintf(flux_fp, "%d\t%.17g\t%s\t%.17g\t%.17g\t%.17g\t%.17g\t"
          "%.17g\t%.17g\t%.17g\t%.17g\t%.17g\n", iteration, t, name, station,
          q, qp, qn, cfg.rho_liquid*q, momentum, area, mean,
          mean - prescribed_speed(t));
}

static double region_mean_pressure (double xmin, double xmax,
                                    double rmin, double rmax)
{
  double sum = 0., weight = 0.;
  foreach(reduction(+:sum) reduction(+:weight))
    if (x >= xmin && x <= xmax && y >= rmin && y <= rmax && cs[] > 1.e-6) {
      const double w = 2.*pi*y*sq(Delta)*cs[]*clamp(f[], 0., 1.);
      sum += w*p[]; weight += w;
    }
  return weight > 0. ? sum/weight : 0.;
}

event diagnostics (t = 0.; t += cfg.output_interval;
                   t <= cfg.t_end + 1.e-12)
{
  double volume = 0., kinetic_energy = 0., max_speed = 0.;
  double shell_measure = 0., wet_measure = 0.;
  double max_x = 0., max_r = 0., max_f = 0., max_cs = 0.;
  long invalid = 0;
  foreach(reduction(+:volume) reduction(+:kinetic_energy)
          reduction(max:max_speed) reduction(+:shell_measure)
          reduction(+:wet_measure) reduction(+:invalid)) {
    const double dv = 2.*pi*y*sq(Delta)*cs[];
    const double fc = clamp(f[], 0., 1.);
    const double speed = sqrt(sq(u.x[]) + sq(u.y[]));
    volume += dv*fc;
    kinetic_energy += 0.5*dv*rho(fc)*sq(speed);
    max_speed = max(max_speed, speed);
    if (ring_levelset(x, y) <= 0. &&
        ring_levelset(x, y) >= -cfg.wetting_band_cells*Delta) {
      const double shell_dv = 2.*pi*y*sq(Delta);
      shell_measure += shell_dv;
      wet_measure += shell_dv*clamp(wet[], 0., 1.);
    }
    if (!isfinite(f[]) || !isfinite(u.x[]) || !isfinite(u.y[]))
      invalid++;
  }
  foreach(serial) {
    const double speed = sqrt(sq(u.x[]) + sq(u.y[]));
    if (speed >= max_speed*(1. - 1.e-12)) {
      max_x = x; max_r = y; max_f = f[]; max_cs = cs[];
    }
  }
  minimum_dt_seen = min(minimum_dt_seen, dt);

  int components = 0;
  double connected_height = 0., center_height = 0.;
  connected_heights(&components, &connected_height, &center_height);

  const double depth = prescribed_depth(t);
  const double expected = initial_liquid_volume +
    pi*sq(domain_radial)*depth + cumulative_wetting_source;
  const double residual = expected > 0. ? (volume - expected)/expected : 0.;
  const double wet_fraction = shell_measure > 0. ? wet_measure/shell_measure : 0.;

  fprintf(diagnostics_fp,
          "%d\t%.17g\t%.17g\t%.17g\t%.17g\t%.17g\t%.17g\t%.17g\t"
          "%.17g\t%.17g\t%.17g\t%.17g\t%.17g\t%.17g\t%.17g\t%.17g\t"
          "%.17g\t%.17g\t%.17g\t%ld\t%d\t%.17g\t%.17g\t%ld\n",
          i, t, dt, prescribed_speed(t),
          -cfg.gravity + prescribed_speed_derivative(t), depth,
          volume, expected, residual, cumulative_wetting_source,
          cfg.wetting_speed*t, wet_fraction, kinetic_energy, max_speed,
          max_x, max_r, max_f, max_cs, minimum_dt_seen, grid->n,
          components, connected_height, center_height, invalid);
  fflush(diagnostics_fp);

  bool jet_detected = false;
  double h_through, h_plic, base_radius, tip_radius, column_length;
  through_hole_metrics(&jet_detected, &h_through, &h_plic, &base_radius,
                       &tip_radius, &column_length);
  const bool persistent = jet_detected && previous_jet_detected;
  if (persistent && jet_onset_time < 0.)
    jet_onset_time = max(t - cfg.output_interval, 0.);
  fprintf(jet_fp, "%d\t%.17g\t%d\t%.17g\t%.17g\t%.17g\t%.17g\t%.17g\t"
          "%.17g\t%d\t%d\t%d\n", i, t, jet_detected, jet_onset_time,
          h_through, h_plic, base_radius, tip_radius, column_length,
          jet_detected, 0, persistent);
  fflush(jet_fp);
  previous_jet_detected = jet_detected;

  const double delta = domain_radial/(1 << cfg.level);
  write_flux_station(i, "below_lower", -cfg.thickness/2. - delta);
  write_flux_station(i, "midplane", 0.);
  write_flux_station(i, "above_upper", cfg.thickness/2. + delta);
  write_flux_station(i, "upper_plus_2Delta", cfg.thickness/2. + 2.*delta);
  fflush(flux_fp);

  const double impact_p = region_mean_pressure(-cfg.thickness/2. - 2.*delta,
    -cfg.thickness/2., cfg.Ri, cfg.Ro);
  const double inner_lower_p = region_mean_pressure(-cfg.thickness/2. - delta,
    -cfg.thickness/2. + delta, max(cfg.Ri - 2.*delta, 0.), cfg.Ri + 2.*delta);
  const double axis_p = region_mean_pressure(-cfg.thickness/2.,
    cfg.thickness/2., 0., 2.*delta);
  const double inner_upper_p = region_mean_pressure(cfg.thickness/2. - delta,
    cfg.thickness/2. + delta, max(cfg.Ri - 2.*delta, 0.), cfg.Ri + 2.*delta);
  double inward_sum = 0., upward_sum = 0., inner_weight = 0.;
  foreach(reduction(+:inward_sum) reduction(+:upward_sum)
          reduction(+:inner_weight))
    if (fabs(y - cfg.Ri) <= 2.*Delta && fabs(x) <= cfg.thickness &&
        cs[] > 1.e-6 && f[] > 0.5) {
      const double w = 2.*pi*y*sq(Delta)*cs[]*f[];
      inward_sum += w*(-u.y[]);
      upward_sum += w*u.x[];
      inner_weight += w;
    }
  const double inward = inner_weight > 0. ? inward_sum/inner_weight : 0.;
  const double upward = inner_weight > 0. ? upward_sum/inner_weight : 0.;
  fprintf(pressure_fp, "%d\t%.17g\t%.17g\t%.17g\t%.17g\t%.17g\t%.17g\t"
          "%.17g\t%.17g\t%.17g\t%.17g\t%.17g\t%.17g\t%.17g\t%.17g\t%.17g\n",
          i, t, impact_p, inner_lower_p, axis_p, inner_upper_p,
          inner_lower_p - inner_upper_p,
          (inner_upper_p - inner_lower_p)/max(cfg.thickness, 1.e-30),
          (axis_p - inner_lower_p)/max(cfg.Ri, 1.e-30), inward, upward,
          max_speed, max_x, max_r, max_f, max_cs);
  fflush(pressure_fp);

  char name[128], path[1024];
  snprintf(name, sizeof name, "interface-%08.5f.dat", t);
  make_output_path(path, sizeof path, name);
  FILE * fp = fopen(path, "w");
  if (fp) {
    output_facets(f, fp);
    fclose(fp);
  }

  if (invalid || !isfinite(volume) || !isfinite(kinetic_energy) ||
      !isfinite(max_speed) || max_speed > cfg.max_speed_abort) {
    fprintf(stderr, "safety stop at t=%g: invalid=%ld max_speed=%g\n",
            t, invalid, max_speed);
    simulation_status = 3;
    return 1;
  }
}

event stop_run (t = cfg.t_end)
{
  return 1;
}

event finalize (t = end)
{
  char path[1024];
  make_output_path(path, sizeof path, "final.dump");
  dump(file = path);
  make_output_path(path, sizeof path, "solid_facets.dat");
  FILE * fp = fopen(path, "w");
  if (fp) {
    output_facets(cs, fp, fs);
    fclose(fp);
  }
  if (diagnostics_fp) {
    fclose(diagnostics_fp);
    diagnostics_fp = NULL;
  }
  if (jet_fp) fclose(jet_fp);
  if (flux_fp) fclose(flux_fp);
  if (pressure_fp) fclose(pressure_fp);
  jet_fp = flux_fp = pressure_fp = NULL;
}
