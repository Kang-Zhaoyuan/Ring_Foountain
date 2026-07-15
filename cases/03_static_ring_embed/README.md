# Static annular ring geometry

The preceding official and publication smoke-test gates passed before this case was implemented. This case contains only a static axisymmetric rectangular annular embedded geometry, with no VOF, two-phase flow, surface tension, motion, free-fall, contact angle, or fountain physics.

Parameters are `Ri=2.5e-3 m`, `Ro=15e-3 m`, and `h=4e-3 m`. The level-set is negative inside the rectangular meridional section `Ri <= y <= Ro`, `-h/2 <= x <= h/2`; rotating that rectangle gives a flat washer, not a torus.

`dv()` is reported as Basilisk's axisymmetric metric integral. Since the installed `axi.h` sets `cm=y` and does not include the azimuthal `2*pi`, the reported three-dimensional volume is `2*pi*sum((1-cs)*dv())`. The analytical comparison is `pi*(Ro^2-Ri^2)*h`.

The geometry smoke test uses SI-valued numerical coordinates while leaving qcc's optional dimensional checker out of this purely geometric executable; `axi.h` supplies the metric at runtime and the volume formula is checked numerically.
