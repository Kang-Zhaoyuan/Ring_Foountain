/*
 * Prescribed-trajectory ring entry with a project-owned dynamic wetting front.
 *
 * Coordinates are Basilisk AXI coordinates: x is axial/upward, y is radial,
 * and y = 0 is the symmetry axis.  The ring is fixed in its translating frame.
 * Liquid and gas enter upward at the measured ring speed.  The frame receives
 * gravity plus the fictitious acceleration associated with the prescribed
 * post-contact deceleration.
 *
 * The wetting closure is deliberately small and explicit.  A monotone scalar
 * propagates through a thin embedded-solid shell when it touches physical
 * liquid or an already-wet shell neighbour.  Its propagation speed is a model
 * parameter in m/s.  The scalar supplies liquid VOF ghost/cut-cell values and
 * the resulting physical liquid source is measured at every step.
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
  double t_end, output_interval;
  double Ri, Ro, thickness, ring_mass;
  double rho_liquid, rho_gas, mu_liquid, mu_gas;
  double surface_tension, gravity;
  double impact_speed, terminal_speed, trajectory_decay_rate;
  double wetting_speed, wetting_band_cells, liquid_contact_threshold;
  double max_speed_abort;
} Config;

static Config cfg = {
  7, 0.006, 0.001,
  0.00505, 0.02007, 0.00286, 0.02615,
  998., 1.2, 1.e-3, 1.8e-5,
  0.072, 9.81,
  1.34555038115, 0.720414774329, 76.9112141855,
  0.0297916666667, 1.25, 0.5,
  100.
};

static const double domain_axial = 0.960;
static const double domain_radial = 0.120;
static const double domain_x_origin = -0.240;

scalar wet[];

static char output_directory[512] = ".";
static FILE * diagnostics_fp = NULL;
static double initial_liquid_volume = 0.;
static double cumulative_wetting_source = 0.;
static int simulation_status = 0;

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
  return max (max (cfg.Ri - rr, rr - cfg.Ro),
              fabs (xx) - cfg.thickness/2.);
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
  else if (!strcmp(key, "liquid_contact_threshold")) cfg.liquid_contact_threshold = atof(value);
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
    cfg.t_end > 0. && cfg.output_interval > 0. &&
    cfg.Ri > 0. && cfg.Ro > cfg.Ri && cfg.thickness > 0. &&
    cfg.rho_liquid > 0. && cfg.rho_gas > 0. &&
    cfg.mu_liquid >= 0. && cfg.mu_gas >= 0. &&
    cfg.surface_tension > 0. && cfg.gravity >= 0. &&
    cfg.impact_speed > 0. && cfg.terminal_speed >= 0. &&
    cfg.trajectory_decay_rate > 0. && cfg.wetting_speed >= 0. &&
    cfg.wetting_band_cells > 0. &&
    cfg.liquid_contact_threshold > 0. &&
    cfg.liquid_contact_threshold < 1. && cfg.max_speed_abort > 0.;
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
  fprintf(fp, "liquid_contact_threshold\t%.17g\t-\n", cfg.liquid_contact_threshold);
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
          "wet_shell_fraction\tkinetic_energy\tmax_speed\tleaf_cells\t"
          "liquid_components\tconnected_height\tcenter_height\tinvalid\n");
  fflush(diagnostics_fp);
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
  boundary ((scalar *){f, wet, cs});

  foreach() {
    const double phi = ring_levelset(x, y);
    const bool shell = phi <= 0. &&
      phi >= -cfg.wetting_band_cells*Delta && cs[] < 1.;
    if (!shell) {
      next_wet[] = wet[];
      continue;
    }

    double liquid_seed = 0.;
    if (cs[1,0] > 1.e-6 && f[1,0] >= cfg.liquid_contact_threshold)
      liquid_seed = 1.;
    if (cs[-1,0] > 1.e-6 && f[-1,0] >= cfg.liquid_contact_threshold)
      liquid_seed = 1.;
    if (cs[0,1] > 1.e-6 && f[0,1] >= cfg.liquid_contact_threshold)
      liquid_seed = 1.;
    if (cs[0,-1] > 1.e-6 && f[0,-1] >= cfg.liquid_contact_threshold)
      liquid_seed = 1.;

    const double neighbour_wet = max(max(wet[1,0], wet[-1,0]),
                                     max(wet[0,1], wet[0,-1]));
    const double drive = max(liquid_seed, neighbour_wet);
    const double increment = dt*cfg.wetting_speed/max(Delta, 1.e-30)*drive;
    next_wet[] = clamp(max(wet[], wet[] + increment), 0., 1.);
  }
  boundary ({next_wet});

  double added = 0.;
  foreach(reduction(+:added)) {
    const double oldf = f[];
    wet[] = next_wet[];
    if (ring_levelset(x, y) <= 0. &&
        ring_levelset(x, y) >= -cfg.wetting_band_cells*Delta &&
        cs[] < 1.)
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

event diagnostics (t = 0.; t += cfg.output_interval; t <= cfg.t_end)
{
  double volume = 0., kinetic_energy = 0., max_speed = 0.;
  double shell_measure = 0., wet_measure = 0.;
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
          "%.17g\t%.17g\t%.17g\t%.17g\t%.17g\t%ld\t%d\t%.17g\t%.17g\t%ld\n",
          i, t, dt, prescribed_speed(t),
          -cfg.gravity + prescribed_speed_derivative(t), depth,
          volume, expected, residual, cumulative_wetting_source,
          wet_fraction, kinetic_energy, max_speed, grid->n,
          components, connected_height, center_height, invalid);
  fflush(diagnostics_fp);

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

event stop_run (i++)
{
  if (t >= cfg.t_end)
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
}
