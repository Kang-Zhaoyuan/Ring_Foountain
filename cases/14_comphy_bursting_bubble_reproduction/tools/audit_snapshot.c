/** Read-only scalar and PLIC audit for a Bursting-Bubble dump. */
#include "axi.h"
#include "navier-stokes/centered.h"
#define FILTERED 1
#include "two-phase.h"
#include "fractions.h"
#include "tag.h"

static int largest_component (scalar d, int n) {
  int main = 0;
  if (n > 0) {
    double * count = calloc(n, sizeof(double));
    foreach(serial)
      if (d[] > 0.)
        count[(int)d[] - 1] += 1.;
    double largest = -1.;
    for (int j = 0; j < n; j++)
      if (count[j] > largest) {
        largest = count[j];
        main = j + 1;
      }
    free(count);
  }
  return main;
}

int main (int argc, char ** argv) {
  if (argc != 2) {
    fprintf(stderr, "usage: %s dump\n", argv[0]);
    return 2;
  }
  if (!restore(file = argv[1])) {
    fprintf(stderr, "restore failed: %s\n", argv[1]);
    return 1;
  }
  // Match the unchanged solver's phase densities. Basilisk's post-processing
  // default is rho1=rho2=1 unless these globals are reset explicitly.
  rho1 = 1.;
  rho2 = 1e-3;
#if TREE
  f.prolongation = fraction_refine;
#endif
  boundary((scalar *){f, u.x, u.y});

  double volume = 0., ke = 0., umax = -1., z_umax = 0., r_umax = 0.;
  double delta_min = HUGE;
  long leaves = 0;
  foreach(reduction(+:volume) reduction(+:ke) reduction(+:leaves)
          reduction(min:delta_min)) {
    const double weight = 2.*pi*y*sq(Delta);
    const double speed = sqrt(sq(u.x[]) + sq(u.y[]));
    volume += weight*f[];
    ke += weight*0.5*rho(f[])*sq(speed);
    leaves++;
    if (Delta < delta_min)
      delta_min = Delta;
  }
  foreach(serial) {
    const double speed = sqrt(sq(u.x[]) + sq(u.y[]));
    if (speed > umax) {
      umax = speed;
      z_umax = x;
      r_umax = y;
    }
  }

  scalar liquid[];
  foreach()
    liquid[] = f[] > 1e-4;
  int n_liquid = tag(liquid);
  int main_liquid = largest_component(liquid, n_liquid);
  boundary({liquid});

  const double center_tol = 2.*delta_min;
  double z_all = -HUGE, z_main = -HUGE, z_center = -HUGE;
  foreach(serial)
    if (f[] > 1e-6 && f[] < 1. - 1e-6) {
      coord normal = interface_normal(point, f);
      double alpha = plane_alpha(f[], normal);
      coord segment[2];
      if (facets(normal, alpha, segment) == 2)
        for (int k = 0; k < 2; k++) {
          const double zp = x + segment[k].x*Delta;
          const double rp = y + segment[k].y*Delta;
          if (zp > z_all)
            z_all = zp;
          if ((int)liquid[] == main_liquid) {
            if (zp > z_main)
              z_main = zp;
            if (rp <= center_tol && zp > z_center)
              z_center = zp;
          }
        }
    }

  fprintf(stdout,
          "time\tvolume\tke\tumax\tz_umax\tr_umax\tleaves\tdelta_min\t"
          "n_liquid\tz_all\tz_main\tz_center\n");
  fprintf(stdout,
          "%.17g\t%.17g\t%.17g\t%.17g\t%.17g\t%.17g\t%ld\t%.17g\t"
          "%d\t%.17g\t%.17g\t%.17g\n",
          t, volume, ke, umax, z_umax, r_umax, leaves, delta_min,
          n_liquid, z_all, z_main, z_center);
  return 0;
}
