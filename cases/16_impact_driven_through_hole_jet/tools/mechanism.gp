if (!exists("base_flux")) base_flux = "baseline_flux.tsv"
if (!exists("candidate_flux")) candidate_flux = "candidate_flux.tsv"
if (!exists("base_pressure")) base_pressure = "baseline_pressure.tsv"
if (!exists("candidate_pressure")) candidate_pressure = "candidate_pressure.tsv"
if (!exists("output")) output = "mechanism.png"
set terminal pngcairo size 1400,800 font "DejaVu Sans,15"
set output output
set multiplot layout 1,2 title "Impact-to-aperture mechanism: measured diagnostics"
set grid
set xlabel "time after contact (ms)"
set ylabel "mid-plane liquid Q (m^3/s)"
plot base_flux using (($2)*1000):($4 == 0 ? $5 : 1/0) with points pt 7 ps 0.7 title "Case 15 physics", candidate_flux using (($2)*1000):($4 == 0 ? $5 : 1/0) with points pt 6 ps 0.5 title "instant inner"
set ylabel "inner lower-to-upper pressure difference (Pa)"
plot base_pressure using (($2)*1000):7 with lines lw 3 title "Case 15 physics", candidate_pressure using (($2)*1000):7 with lines dt 2 lw 2 title "instant inner"
unset multiplot
