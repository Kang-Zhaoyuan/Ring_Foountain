if (!exists("output_file") || !exists("Ri_mm") || !exists("Ro_mm") || \
    !exists("h_mm")) {
  print "missing output or geometry variables"
  exit error
}

do for [grid=1:2] {
  do for [panel=1:3] {
    if (!exists(sprintf("interface%d_%d", grid, panel)) || \
        !exists(sprintf("center%d_%d_mm", grid, panel)) || \
        !exists(sprintf("frame%d", panel)) || \
        !exists(sprintf("relative%d_ms", panel))) {
      print sprintf("missing variables for grid %d panel %d", grid, panel)
      exit error
    }
  }
}

set terminal pngcairo size 1800,1200 enhanced font "DejaVu Sans,15"
set output output_file
set datafile commentschars "#"
set border linewidth 1.1
set tics out
set key off
set xrange [-55:55]
set yrange [-70:80]
set xtics 25
set ytics 25
set xlabel "radius r (mm)"
set ylabel "laboratory height z (mm)"
set multiplot layout 2,3 title \
  "Prescribed video trajectory: early axisymmetric interface" font ",21"

do for [grid=1:2] {
  do for [panel=1:3] {
    interface_file = value(sprintf("interface%d_%d", grid, panel))
    center_mm = value(sprintf("center%d_%d_mm", grid, panel))
    frame_number = value(sprintf("frame%d", panel))
    relative_ms = value(sprintf("relative%d_ms", panel))
    set title sprintf("L%d, frame %d, %.1f ms", \
                      grid == 1 ? 7 : 8, frame_number, relative_ms)
    set arrow 1 from graph 0, first 0 to graph 1, first 0 nohead \
      dt 2 lw 1 lc rgb "#777777"
    set object 1 rect from -Ro_mm,center_mm - h_mm/2. \
      to -Ri_mm,center_mm + h_mm/2. front fc rgb "#555555" \
      fs solid 1 border lc rgb "#111111"
    set object 2 rect from Ri_mm,center_mm - h_mm/2. \
      to Ro_mm,center_mm + h_mm/2. front fc rgb "#555555" \
      fs solid 1 border lc rgb "#111111"
    plot interface_file using ($2*1000):($1*1000 + center_mm) \
           with lines lw 1.2 lc rgb "#2166ac", \
         interface_file using (-$2*1000):($1*1000 + center_mm) \
           with lines lw 1.2 lc rgb "#2166ac"
    unset object 1
    unset object 2
    unset arrow 1
  }
}

unset multiplot
