if (!exists("height_file") || !exists("experiment_file") || \
    !exists("output_file")) {
  print "missing height_file, experiment_file, or output_file"
  exit error
}
if (!exists("plot_title")) {
  plot_title = "Height-proxy workflow check: old CFD geometry is not calibrated"
}
if (!exists("all_label")) {
  all_label = "old L7: all water"
}
if (!exists("core_label")) {
  core_label = "old L7: pool-connected core"
}

set terminal pngcairo size 1400,850 enhanced font "DejaVu Sans,16"
set output output_file
set datafile separator "\t"
set key top left opaque box
set border linewidth 1.2
set tics out
set grid xtics ytics lc rgb "#d9d9d9" lw 1
set title plot_title
set xlabel "time after first water contact (ms)"
set ylabel "height above undisturbed surface (mm)"
set xrange [0:185]
set yrange [0:75]
set xtics 20
set ytics 10

plot height_file using 2:($4*1000) every ::1 with lines \
       lw 1.5 dt 2 lc rgb "#7f7f7f" title all_label, \
     height_file using 2:($5*1000) every ::1 with lines \
       lw 3 lc rgb "#2166ac" title core_label, \
     experiment_file using \
       (strcol(3) eq "crown" ? $7 : 1/0):4 every ::1 with points \
       pt 7 ps 1.5 lc rgb "#e08214" title "experiment: crown", \
     experiment_file using \
       (strcol(3) eq "first_jet" ? $7 : 1/0):4 every ::1 with points \
       pt 9 ps 1.7 lc rgb "#b2182b" title "experiment: first jet", \
     experiment_file using \
       (strcol(3) eq "worthington" ? $7 : 1/0):4 every ::1 with points \
       pt 5 ps 1.6 lc rgb "#1b7837" title "experiment: Worthington"
