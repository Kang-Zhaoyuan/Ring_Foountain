/** Read-only diagnostics for Drop-Impact Basilisk snapshots. */
#include "utils.h"

scalar f[];
vector u[];

int main (int argc, char const *argv[])
{
  if (argc != 3) {
    fprintf (stderr, "usage: %s SNAPSHOT RHO_RATIO\n", argv[0]);
    return 2;
  }

  if (!restore (file = argv[1])) {
    fprintf (stderr, "restore failed: %s\n", argv[1]);
    return 1;
  }

  const double rho_ratio = atof (argv[2]);
  double volume = 0., kinetic_proxy = 0., max_speed = 0.;
  double min_delta = HUGE, f_min = HUGE, f_max = -HUGE;
  long leaf_cells = 0, invalid = 0;
  int maximum_level = 0;

  foreach (reduction(+:volume) reduction(+:kinetic_proxy)
           reduction(max:max_speed) reduction(min:min_delta)
           reduction(min:f_min) reduction(max:f_max)
           reduction(+:leaf_cells) reduction(+:invalid)
           reduction(max:maximum_level)) {
    const double speed = sqrt (sq(u.x[]) + sq(u.y[]));
    const double rho_local = f[] + rho_ratio*(1. - f[]);
    const double dvolume_axi = 2.*pi*y*sq(Delta);
    volume += f[]*dvolume_axi;
    kinetic_proxy += 0.5*rho_local*sq(speed)*dvolume_axi;
    if (speed > max_speed)
      max_speed = speed;
    if (Delta < min_delta)
      min_delta = Delta;
    if (f[] < f_min)
      f_min = f[];
    if (f[] > f_max)
      f_max = f[];
    if (!isfinite(f[]) || !isfinite(u.x[]) || !isfinite(u.y[]))
      invalid++;
    leaf_cells++;
    if (level > maximum_level)
      maximum_level = level;
  }

  printf ("time\tvolume_axi\tkinetic_proxy\tmax_speed\tleaf_cells"
          "\tmax_level\tmin_delta\tf_min\tf_max\tinvalid\n");
  printf ("%.17g\t%.17g\t%.17g\t%.17g\t%ld\t%d\t%.17g"
          "\t%.17g\t%.17g\t%ld\n",
          t, volume, kinetic_proxy, max_speed, leaf_cells, maximum_level,
          min_delta, f_min, f_max, invalid);
  return 0;
}
