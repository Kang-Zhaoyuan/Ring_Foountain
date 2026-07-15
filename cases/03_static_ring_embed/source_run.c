/* Static axisymmetric flat-ring geometry smoke test.
 * x is axial, y is radial, and y >= 0 is enforced by the domain origin.
 */
#include "grid/quadtree.h"
#include "embed.h"
#include "axi.h"
#include "utils.h"
#include "output.h"

double Ri = 2.5e-3;
double Ro = 15e-3;
double h = 4e-3;
double domain_size = 60e-3;
int baselevel = 4;
int maxlevel = 6;

static double ring_levelset (double xx, double yy)
{
  return max (max (Ri - yy, yy - Ro), fabs(xx) - h/2.);
}

static void write_geometry_report (void)
{
  double metric_volume = 0., min_cs = HUGE, max_cs = -HUGE;
  long cut_cells = 0, invalid_cs = 0, invalid_fs = 0, orphan_cut_cells = 0;
  foreach (reduction(+:metric_volume) reduction(min:min_cs)
           reduction(max:max_cs) reduction(+:cut_cells)
           reduction(+:invalid_cs) reduction(+:invalid_fs)
           reduction(+:orphan_cut_cells)) {
    double solid_fraction = 1. - cs[];
    /* axi.h uses cm=y for an unembedded metric.  Here the embedded cm
     * represents the fluid side, so integrate the complementary solid
     * fraction against the same meridional measure explicitly. */
    metric_volume += solid_fraction*y*sq(Delta);
    min_cs = min (min_cs, cs[]);
    max_cs = max (max_cs, cs[]);
    if (cs[] > 1e-12 && cs[] < 1. - 1e-12) {
      cut_cells++;
      if (fs.x[] + fs.x[1] + fs.y[] + fs.y[0,1] <= 1e-12)
        orphan_cut_cells++;
    }
    if (cs[] < -1e-12 || cs[] > 1. + 1e-12)
      invalid_cs++;
    if (fs.x[] < -1e-12 || fs.x[] > 1. + 1e-12 ||
        fs.x[1] < -1e-12 || fs.x[1] > 1. + 1e-12 ||
        fs.y[] < -1e-12 || fs.y[] > 1. + 1e-12 ||
        fs.y[0,1] < -1e-12 || fs.y[0,1] > 1. + 1e-12)
      invalid_fs++;
  }

  const double volume_3d = 2.*pi*metric_volume;
  const double exact_volume = pi*(sq(Ro) - sq(Ri))*h;
  const double relative_error = fabs(volume_3d - exact_volume)/exact_volume;
  FILE * fp = fopen ("ring_geometry.tsv", "w");
  fprintf (fp, "# units: lengths=m, volumes=m^3\n");
  fprintf (fp, "baselevel\tmaxlevel\tleaf_cells\tcut_cells\tmetric_volume\tvolume_3d\texact_volume\trelative_error\tmin_cs\tmax_cs\tinvalid_cs\tinvalid_fs\torphan_cut_cells\n");
  fprintf (fp, "%d\t%d\t%ld\t%ld\t%.17g\t%.17g\t%.17g\t%.17g\t%.17g\t%.17g\t%ld\t%ld\t%ld\n",
           baselevel, maxlevel, grid->n, cut_cells, metric_volume,
           volume_3d, exact_volume, relative_error, min_cs, max_cs,
           invalid_cs, invalid_fs, orphan_cut_cells);
  fclose (fp);

  FILE * facets = fopen ("solid_facets.dat", "w");
  output_facets (cs, facets, fs);
  fclose (facets);
  output_ppm (cs, file = "cs.ppm", n = 512, min = 0, max = 1);
  dump ("final.dump");
}

int main (int argc, char ** argv)
{
  if (argc > 1)
    maxlevel = atoi (argv[1]);
  if (argc > 2)
    baselevel = atoi (argv[2]);
  if (maxlevel < baselevel || baselevel < 2)
    return 2;

  size (60e-3);
  origin (-30e-3, 0.);
  init_grid (1 << baselevel);

  solid (cs, fs, ring_levelset (x, y));
  fractions_cleanup (cs, fs);

  /* Refine a narrow level-set band until all four rectangular boundaries
   * reach maxlevel, then reconstruct the embedded fractions on that mesh. */
  for (int pass = 0; pass < maxlevel - baselevel + 1; pass++)
    refine (level < maxlevel && fabs (ring_levelset (x, y)) < 4.*Delta);
  solid (cs, fs, ring_levelset (x, y));
  fractions_cleanup (cs, fs);
  write_geometry_report();
  return 0;
}
