if (!exists("output_file") || !exists("candidate_label") || \
    !exists("Ri_mm") || !exists("Ro_mm") || !exists("h_mm") || \
    !exists("y_min_mm") || !exists("y_max_mm")) {
  print "missing comparison montage variables"
  exit error
}

do for [panel=1:6] {
  if (!exists(sprintf("interface%d", panel)) || \
      !exists(sprintf("center%d_mm", panel)) || \
      !exists(sprintf("relative%d_ms", panel))) {
    print sprintf("missing variables for panel %d", panel)
    exit error
  }
}

set terminal pngcairo size 1800,1100 enhanced font "DejaVu Sans,15"
set output output_file
set datafile commentschars "#"
set border linewidth 1.1
set tics out
set key off
set xrange [-20:20]
set yrange [y_min_mm:y_max_mm]
set xtics 10
set ytics 5
set xlabel "radius r (mm)"
set ylabel "laboratory height z (mm)"
set multiplot layout 2,3 title \
  "First-jet interface comparison in the fixed laboratory frame" font ",20"

do for [panel=1:6] {
  interface_file = value(sprintf("interface%d", panel))
  center_mm = value(sprintf("center%d_mm", panel))
  relative_ms = value(sprintf("relative%d_ms", panel))
  row_label = panel <= 3 ? "baseline" : candidate_label
  set title sprintf("%s, t-contact = %.1f ms", row_label, relative_ms)
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
