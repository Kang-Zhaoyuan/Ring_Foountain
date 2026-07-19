if (!exists("input")) input = "interface.dat"
if (!exists("output")) output = "panel.png"
if (!exists("surface")) surface = 0
if (!exists("ri")) ri = 0.00505
if (!exists("ro")) ro = 0.02007
if (!exists("thickness")) thickness = 0.00286
if (!exists("title_text")) title_text = "Case 17 prediction"
set terminal pngcairo size 700,760 enhanced font "DejaVu Sans,14"
set output output
set title title_text
set xlabel "radial position (mm)"
set ylabel "height from initial waterline (mm)"
set xrange [-30:30]
set yrange [-150:100]
set xtics 20
set size ratio -1
set grid xtics ytics lc rgb "#dddddd"
set arrow 1 from -30,0 to 30,0 nohead lw 2 lc rgb "#2878b5"
set object 1 rect from ri*1000,(-thickness/2.-surface)*1000 to ro*1000,(thickness/2.-surface)*1000 fc rgb "#666666" fs solid 0.55 border rgb "#222222"
set object 2 rect from -ro*1000,(-thickness/2.-surface)*1000 to -ri*1000,(thickness/2.-surface)*1000 fc rgb "#666666" fs solid 0.55 border rgb "#222222"
plot input using ($2*1000):(($1-surface)*1000) with lines lw 1.4 lc rgb "#111111" notitle, \
     input using (-$2*1000):(($1-surface)*1000) with lines lw 1.4 lc rgb "#111111" notitle
