if (!exists("field_file") || !exists("interface_file") || \
    !exists("output_file") || !exists("time_ms") || \
    !exists("drop_mm") || !exists("speed_down") || \
    !exists("ring_center_mm") || !exists("speed_cap")) {
  print "missing required -e variables"
  exit error
}

set terminal pngcairo size 1600,1000 enhanced font "DejaVu Sans,16"
set output output_file
set encoding utf8
set datafile commentschars "#"
set border linewidth 1.2
set tics out
set key off
set view map
set pm3d map
set pm3d corners2color c1
set palette defined (0.00 "#08306b", \
                     0.20 "#2171b5", \
                     0.40 "#41b6c4", \
                     0.60 "#ffffbf", \
                     0.80 "#fdae61", \
                     1.00 "#b2182b")
set cbrange [0:speed_cap]
set format cb "%.0f"

set label 90 sprintf("t = %.0f ms    drop = %.1f mm    ring speed = %.3f m/s", \
                     time_ms, drop_mm, speed_down) \
    at screen 0.5,0.965 center front font ",19"
set label 91 sprintf("water |u_{lab}| (m/s); red >= %.0f", speed_cap) \
    at screen 0.493,0.48 center rotate by 90 front font ",14"

set multiplot

# Full fixed laboratory window. The border is the rendered model window, not a
# claim that the numerical open boundaries are physical tank walls.
set origin 0.035,0.07
set size 0.42,0.84
set title "Fixed laboratory frame: full trajectory" offset 0,0.5
set xlabel "radius r (mm)"
set ylabel "laboratory height z (mm)"
set xrange [-120:120]
set yrange [-1120:100]
set xtics 40
set ytics 200
set colorbox user origin 0.435,0.18 size 0.015,0.56
set object 1 rect from -15,ring_center_mm - 2 to -2.5,ring_center_mm + 2 \
    front fc rgb "#5a5a5a" fs solid 1.0 border lc rgb "#101010" lw 1.0
set object 2 rect from 2.5,ring_center_mm - 2 to 15,ring_center_mm + 2 \
    front fc rgb "#5a5a5a" fs solid 1.0 border lc rgb "#101010" lw 1.0
set arrow 1 from graph 0, first 0 to graph 1, first 0 nohead \
    front dt 2 lw 1.2 lc rgb "#303030"

splot field_file using \
        ($2*1000):($1*1000 + ring_center_mm): \
        ($5 > 1e-6 && $4 > 0.01 ? ($3 < speed_cap ? $3 : speed_cap) : 1/0) \
        with pm3d, \
      field_file using \
        (-$2*1000):($1*1000 + ring_center_mm): \
        ($5 > 1e-6 && $4 > 0.01 ? ($3 < speed_cap ? $3 : speed_cap) : 1/0) \
        with pm3d, \
      interface_file using ($2*1000):($1*1000 + ring_center_mm):(speed_cap + 1) \
        with lines lc rgb "#111111" lw 0.8, \
      interface_file using (-$2*1000):($1*1000 + ring_center_mm):(speed_cap + 1) \
        with lines lc rgb "#111111" lw 0.8

# A second fixed laboratory view keeps the free surface readable while the ring
# continues down through the full-window panel.
unset colorbox
set origin 0.535,0.07
set size 0.44,0.84
set title "Fixed surface window" offset 0,0.5
set ylabel "z (mm)"
set xrange [-60:60]
set yrange [-300:100]
set xtics 20
set ytics 50

splot field_file using \
        ($2*1000):($1*1000 + ring_center_mm): \
        ($5 > 1e-6 && $4 > 0.01 ? ($3 < speed_cap ? $3 : speed_cap) : 1/0) \
        with pm3d, \
      field_file using \
        (-$2*1000):($1*1000 + ring_center_mm): \
        ($5 > 1e-6 && $4 > 0.01 ? ($3 < speed_cap ? $3 : speed_cap) : 1/0) \
        with pm3d, \
      interface_file using ($2*1000):($1*1000 + ring_center_mm):(speed_cap + 1) \
        with lines lc rgb "#111111" lw 1.0, \
      interface_file using (-$2*1000):($1*1000 + ring_center_mm):(speed_cap + 1) \
        with lines lc rgb "#111111" lw 1.0

unset multiplot
