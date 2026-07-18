# Case 16 references and transferable evidence

No external source code is copied.  The repository has no root `LICENSE`, so
all third-party material is treated as read-only scientific or API evidence.

- Hou et al. (2019), *Investigations on the vertical water-entry of a hollow
  cylinder with deep-closure pattern*, DOI `10.1016/j.oceaneng.2019.106426`.
  The impact face creates high pressure; an inward/upward pressure gradient at
  the inner wall redirects liquid and opposing radial streams focus into an
  axial through-hole jet.  The later deep closure and secondary jet are a
  separate stage.  The paper's long cylinder, 2.84 m/s case, k-epsilon model,
  sliding mesh, and grid are not transferred.
- Jafari and Akbarzadeh (2022), *Experimental analysis of water entry problem
  considering hollow cylinders: The impact of hole geometry*, DOI
  `10.1016/j.oceaneng.2022.111906`.  Cylindrical, upward-conical, and
  downward-conical holes produce different through-hole jets; the real edge
  geometry cannot be assumed from an ideal rectangle.
- Ebrahimi and Azimi (2025), *Cavity dynamics by the entry of annular disks
  into non-Newtonian ambient*, DOI `10.1016/j.oceaneng.2025.120379`.  Annular
  disks can generate a through-hole jet and aperture, relative density, and
  Reynolds number matter.  Its non-Newtonian fluid and geometry are not used.
- Fan, Jain and van der Meer (2024), *Air-cushioning below an impacting
  wave-structured disk*, DOI `10.1103/PhysRevFluids.9.010501`.  Escaping air
  pre-deforms the free surface and changes contact order/load.  The current
  incompressible gas can only bracket pre-impact deformation sensitivity.
- Gekle and Gordillo (2010), *Generation and breakup of Worthington jets after
  cavity collapse*, DOI `10.1017/S0022112010003526`.  This defines the distinct
  cavity-collapse jet mechanism and is not an explanation for the open-cavity
  first jet at 52.5 ms.
- Basilisk official `src/embed.h`, `src/contact.h`,
  `src/navier-stokes/centered.h`, and `src/axi.h`, inspected at Darcs patch
  `586963ed3f4e8704f89b314b8d1f9e8a475a4065` on 2026-07-18.  AXI uses axial
  `x`, radial `y`; `contact.h` targets domain-boundary height functions, not a
  proven arbitrary EMBED dynamic contact line; `embed.h` documents cut-cell
  interpolation and small-cell restrictions.
