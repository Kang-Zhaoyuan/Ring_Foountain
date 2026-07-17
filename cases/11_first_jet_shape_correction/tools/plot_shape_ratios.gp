if (!exists("baseline_file") || !exists("candidate_file") || \
    !exists("output_file") || !exists("candidate_label")) {
  print "missing baseline_file, candidate_file, output_file, or candidate_label"
  exit error
}

set terminal pngcairo size 1400,850 enhanced font "DejaVu Sans,16"
set output output_file
set datafile separator "\t"
set key top left opaque box
set border linewidth 1.2
set tics out
set grid xtics ytics lc rgb "#d9d9d9" lw 1
set title "First-jet width ratios; 1.0 is equal width, not a fitted tolerance"
set xlabel "time after first water contact (ms)"
set ylabel "radius ratio"
set xrange [50:90]
set yrange [0.7:1.5]
set arrow 1 from graph 0, first 1 to graph 1, first 1 nohead \
  dt 2 lw 1.5 lc rgb "#555555"

plot baseline_file using 1:8 every ::1 with lines \
       lw 2 lc rgb "#b2182b" title "baseline: max/base", \
     candidate_file using 1:8 every ::1 with lines \
       lw 3 lc rgb "#2166ac" title sprintf("%s: max/base", candidate_label), \
     baseline_file using 1:11 every ::1 with lines \
       lw 2 dt 3 lc rgb "#ef8a62" title "baseline: upper/lower mean", \
     candidate_file using 1:11 every ::1 with lines \
       lw 3 dt 3 lc rgb "#67a9cf" \
       title sprintf("%s: upper/lower mean", candidate_label)
