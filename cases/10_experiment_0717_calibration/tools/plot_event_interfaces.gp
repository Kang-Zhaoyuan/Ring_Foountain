if (!exists("output_file") || !exists("Ri_mm") || !exists("Ro_mm") || \
    !exists("h_mm") || !exists("y_min_mm") || !exists("y_max_mm")) {
  print "missing output or geometry/window variables"
  exit error
}

do for [panel=1:6] {
  if (!exists(sprintf("interface%d", panel)) || \
      !exists(sprintf("center%d_mm", panel)) || \
      !exists(sprintf("relative%d_ms", panel)) || \
      !exists(sprintf("event%d", panel))) {
    print sprintf("missing variables for panel %d", panel)
    exit error
  }
}

set terminal pngcairo size 1800,1100 enhanced font "DejaVu Sans,15"
set output output_file
set encoding utf8
set datafile commentschars "#"
set border linewidth 1.1
set tics out
set key off
set xrange [-35:35]
set yrange [y_min_mm:y_max_mm]
set xtics 10
set ytics 20
set xlabel "radius r (mm)"
set ylabel "laboratory height z (mm)"
set multiplot layout 2,3 title \
  "Provisional specimen L7 at experimental event times" font ",20"

do for [panel=1:6] {
  interface_file = value(sprintf("interface%d", panel))
  center_mm = value(sprintf("center%d_mm", panel))
  relative_ms = value(sprintf("relative%d_ms", panel))
  event_name = value(sprintf("event%d", panel))
  set title sprintf("%s, t-contact = %.1f ms", event_name, relative_ms)
  set arrow 1 from graph 0, first 0 to graph 1, first 0 nohead \
    dt 2 lw 1 lc rgb "#777777"
  set object 1 rect from -Ro_mm,center_mm - h_mm/2. \
    to -Ri_mm,center_mm + h_mm/2. front fc rgb "#555555" \
    fs solid 1 border lc rgb "#111111"
  set object 2 rect from Ri_mm,center_mm - h_mm/2. \
    to Ro_mm,center_mm + h_mm/2. front fc rgb "#555555" \
    fs solid 1 border lc rgb "#111111"
  plot interface_file using ($2*1000):($1*1000 + center_mm) \
         with lines lw 1.4 lc rgb "#2166ac", \
       interface_file using (-$2*1000):($1*1000 + center_mm) \
         with lines lw 1.4 lc rgb "#2166ac"
  unset object 1
  unset object 2
  unset arrow 1
}

unset multiplot
