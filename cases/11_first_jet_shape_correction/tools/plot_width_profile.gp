if (!exists("baseline_file") || !exists("candidate_file") || \
    !exists("output_file") || !exists("candidate_label") || \
    !exists("event_ms")) {
  print "missing profile plot variables"
  exit error
}

set terminal pngcairo size 1100,900 enhanced font "DejaVu Sans,16"
set output output_file
set datafile separator "\t"
set key top left opaque box
set border linewidth 1.2
set tics out
set grid xtics ytics lc rgb "#d9d9d9" lw 1
set title sprintf("Central jet profile near %.1f ms", event_ms)
set xlabel "radius from axis (mm)"
set ylabel "height above undisturbed surface (mm)"
set xrange [-5:5]
set yrange [0:12]
set size ratio -1

plot baseline_file using \
       (abs($1-event_ms)<1e-6 ? $4 : 1/0):3 every ::1 with linespoints \
       lw 2 pt 7 ps 0.5 lc rgb "#b2182b" title "baseline", \
     baseline_file using \
       (abs($1-event_ms)<1e-6 ? -$4 : 1/0):3 every ::1 with linespoints \
       lw 2 pt 7 ps 0.5 lc rgb "#b2182b" notitle, \
     candidate_file using \
       (abs($1-event_ms)<1e-6 ? $4 : 1/0):3 every ::1 with linespoints \
       lw 3 pt 5 ps 0.5 lc rgb "#2166ac" title candidate_label, \
     candidate_file using \
       (abs($1-event_ms)<1e-6 ? -$4 : 1/0):3 every ::1 with linespoints \
       lw 3 pt 5 ps 0.5 lc rgb "#2166ac" notitle
