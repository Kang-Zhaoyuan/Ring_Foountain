if (!exists("input")) input = "interface.dat"
if (!exists("output")) output = "panel.png"
if (!exists("surface")) surface = 0
if (!exists("title_text")) title_text = "CFD PLIC"
set terminal pngcairo size 520,720 enhanced font "DejaVu Sans,14"
set output output
set title title_text
set xlabel "radius (mm)"
set ylabel "height from original waterline (mm)"
set xrange [0:30]
set yrange [-65:120]
set size ratio -1
set grid xtics ytics lc rgb "#dddddd"
set arrow 1 from 0,0 to 30,0 nohead lw 2 lc rgb "#2878b5"
set object 1 rect from 5.05,(-0.00143-surface)*1000 to 20.07,(0.00143-surface)*1000 fc rgb "#666666" fs solid 0.55 border rgb "#222222"
plot input using ($2*1000):(($1-surface)*1000) with lines lw 1.4 lc rgb "#111111" notitle
