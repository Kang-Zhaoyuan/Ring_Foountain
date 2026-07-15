/* Compile-and-initialize probe for the requested static ring/free-surface stack.
 * This is not an accepted contact-line model or a production simulation.
 */
#include "grid/quadtree.h"
#include "embed.h"
#include "axi.h"
#include "navier-stokes/centered.h"
#include "two-phase.h"
#include "tension.h"

static const double Ri = 2.5e-3;
static const double Ro = 15e-3;
static const double h = 4e-3;

static double ring_levelset (double xx, double yy)
{
  return max (max (Ri - yy, yy - Ro), fabs(xx) - h/2.);
}

u.n[embed] = dirichlet (0.);
u.t[embed] = dirichlet (0.);

int main (void)
{
  size (60e-3);
  origin (-30e-3, 0.);
  init_grid (16);

  rho1 = 998.;
  rho2 = 1.2;
  mu1 = 1.e-3;
  mu2 = 1.8e-5;
  f.sigma = 0.072;
  run();
}

event init (i = 0)
{
  solid (cs, fs, ring_levelset (x, y));
  fractions_cleanup (cs, fs);
  fraction (f, -x);
}

/* Stop after one solver step. Running this probe cannot validate
 * contact-line curvature or wetting because no embedded contact-angle API is
 * available in the inspected Basilisk tree. */
event stop_probe (i = 1, last)
{
  return 1;
}
