# CoMPhy Drop-Impact 独立复现报告

日期：2026-07-18（Asia/Shanghai）

独立工作区：`/home/kqdx/basilisk_work/reproductions/drop_impact_20260718`

上游：`https://github.com/comphy-lab/Drop-Impact.git`

> 迁移说明（2026-07-18）：本报告及其参数、日志、表格、图件和本轮新建
> 审计工具源码现归档于 Ring Fountain 的
> `cases/13_comphy_drop_impact_reproduction/`。上游 GPL-3.0 源码、Basilisk
> 安装、编译产物、dump、Python 环境和 Git 历史均未迁入。本报告中的
> `upstream/` 路径始终指向上述独立工作区，不是当前仓库内的副本。

## 1. 最终结论

**PARTIAL。** 本轮达到“最低 PASS”，但未达到“科学复现 PASS”。

最低验收项均已完成：Git 与 Basilisk 被精确固定；原始默认源码在不改 `default.params` 的条件下编译成功；两个相同的 L8 冒烟算例可重复；We 变化产生了可辨识的物理响应；`restart` 与 snapshots 可被实际恢复；原生 PLIC/VOF 界面、footprint、帧图与视频可导出；所有编译/运行警告和失败均有解释及原始日志。

科学复现仍不成立，原因有四项：

1. L10/L11/L12 三级短时网格比较已完成，但默认 L14 根据实测外推明显超过 60 分钟资源门槛，未获确认前没有启动。
2. 短时参数只覆盖输入 `tmax=0.1`，即求解器时间 `tU/R=0.316228`；footprint 在最终快照仍增长，故报告中的“最大铺展”只是**当前时间窗最大值**，不是真实全程最大值。
3. L11→L12 的体积、动能和短时窗 footprint 均低于 5% 变化，但最大局部速度由 14.7933 增至 18.8743，变化 27.59%，局部极值未收敛。
4. 固壁处没有显式接触角/动态润湿模型，而 `f[left]=0` 是有效的 VOF ghost-cell 边界条件；长期 lamella 和铺展的物理含义需要上游确认。

本轮没有修改任何上游 tracked 物理源码，没有运行 Git commit/push，也没有进入圆环几何。

## 2. 版本、隔离与主仓库只读核查

| 对象 | 固定结果 |
|---|---|
| Drop-Impact Git SHA | `9fd0db798ec5a05f8410886231bdfbe30fac051d`，detached HEAD |
| Drop-Impact submodules | 无 |
| Drop-Impact license | GPL-3.0；保持在独立复现目录 |
| Basilisk ref | `v2026-01-13` |
| Basilisk lock patch | `2026-01-13-mpi-tree-dump-header-fix.patch` |
| 安装脚本 SHA-256 | `72bb2460abe9701a4f233dc4261283eea2b4f1fd543143f5137197aa3593e9aa` |
| 独立 qcc SHA-256 | `c40e73ea36d08459e28d99931314160c49fd4dfae62ead826ddb288f8b616407` |
| 独立 BASILISK | `upstream/basilisk/src` |

主项目的只读核查结果为：

```text
## main...origin/main
90f91c0 Add annotated laboratory key-frame atlas
90f91c0b17f5402532f3d9b4c56d2e359a1d4ed9
origin  https://github.com/Kang-Zhaoyuan/Ring_Foountain.git (fetch)
origin  https://github.com/Kang-Zhaoyuan/Ring_Foountain.git (push)
```

核查开始和结束时主项目状态一致，无未提交修改；未对它执行 pull、checkout、reset、clean、commit 或 push，也没有向其中复制任何文件。

克隆后的上游最初为 clean detached HEAD。最终 `git diff --exit-code` 仍通过，说明 tracked 文件未变。最终 `git status` 仅有一次审计辅助程序失败所保留的未跟踪诊断残留 `.qcc2XyEeQ/` 和 `upstream/report/`；按“不删除现有文件”和失败留痕原则保留，并在警告表中登记。

## 3. 完整命令链

全部实际命令、失败命令及未执行的资源门控命令逐行记录在 [`commands.log`](commands.log)。关键执行链如下；其中 installer 是先保存、哈希并完整阅读后才执行：

```bash
git clone https://github.com/comphy-lab/Drop-Impact.git upstream
git -C upstream checkout --detach 9fd0db798ec5a05f8410886231bdfbe30fac051d

cd upstream
curl -fL https://raw.githubusercontent.com/comphy-lab/basilisk-C/main/reset_install_basilisk-ref-locked.sh \
  -o reset_install_basilisk-ref-locked.sh
sha256sum reset_install_basilisk-ref-locked.sh
sed -n '1,700p' reset_install_basilisk-ref-locked.sh
./reset_install_basilisk-ref-locked.sh --ref=v2026-01-13 --hard
source .project_config

./runSimulation.sh --compile-only default.params
./runSimulation.sh ../report/params/smoke_l8_a.params
./runSimulation.sh ../report/params/smoke_l8_b.params
./runSimulation.sh ../report/params/smoke_we20.params

qcc -autolink postProcess/getFacet.c -o postProcess/getFacet -lm
qcc -disable-dimensions -autolink postProcess/getData-generic.c -o postProcess/getData-generic -lm
qcc -disable-dimensions -autolink postProcess/getFootPrint.c -o postProcess/getFootPrint -lm
PATH="$(pwd)/../report/bin:$PATH" PYTHONPATH="$(pwd)/../pydeps" \
  ./runPostProcess-Ncases.sh --CPUs 4 --nGFS 32 --tsnap 0.01 \
  --GridsPerR 64 --ZMAX 3 --RMAX 3 --ZMIN 0 1808

./runSimulation.sh ../report/params/grid_l10.params
./runSimulation.sh ../report/params/grid_l11.params
./runSimulation.sh ../report/params/grid_l12.params
```

默认 L14 的准确命令是：

```bash
cd /home/kqdx/basilisk_work/reproductions/drop_impact_20260718/upstream
source .project_config
./runSimulation.sh default.params
```

该命令**未执行**，不是失败，也没有用较低分辨率冒充默认算例。

## 4. 环境冻结

完整原始输出见 [`environment.txt`](environment.txt)。摘要：WSL2 Ubuntu，kernel `6.18.33.2-microsoft-standard-WSL2`，16 CPU，13 GiB RAM、4 GiB swap，捕获时可用内存约 10 GiB、磁盘可用 933 GiB；GCC 15.2.0、Git 2.53.0、Bash 5.3.9、Python 3.14.4。`mpirun` 为 Open MPI 5.0.6，但没有 `mpicc`，因此本轮为串行编译/运行。

初始 shell 的 `BASILISK`/`qcc` 指向 `/home/kqdx/basilisk/src`，但它们从未用于本复现。安装后 `.project_config` 将二者强制指向独立 `upstream/basilisk/src`，实际 qcc 命令与 SHA 已验证。README 中“换成最新 release”的提示没有采用，仍严格使用指定 `v2026-01-13`。

系统 Python 缺 pandas/matplotlib，且 `venv` 缺 ensurepip。失败的空 venv 被保留；依赖隔离安装到 `pydeps/`：NumPy 2.5.1、pandas 3.0.3、Matplotlib 3.11.1，并通过 `report/bin/python` shim 满足上游脚本的硬编码 `python` 命令。

## 5. 输入参数与无量纲定义

所有派生参数文件均是 `default.params` 的副本，只改变下表列出的键；其他参数保持默认。文件在 [`params/`](params/)。

| Case | 目的 | We | Ohd | Ohs | rho_g/rho_l | MAXlevel | 输入 tmax | 求解器终点 tU/R |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 默认源码 compile-only | 10 | 0.01 | 1e-5 | 1e-3 | 14 | 1.0 | 未运行 |
| 1808 | 冒烟重复 A | 10 | 0.01 | 1e-5 | 1e-3 | 8 | 0.1 | 0.316228 |
| 1809 | 冒烟重复 B | 10 | 0.01 | 1e-5 | 1e-3 | 8 | 0.1 | 0.316228 |
| 1820 | We 响应 | 20 | 0.01 | 1e-5 | 1e-3 | 8 | 0.1 | 0.447214 |
| 1810 | 网格 L10 | 10 | 0.01 | 1e-5 | 1e-3 | 10 | 0.1 | 0.316228 |
| 1811 | 网格 L11 | 10 | 0.01 | 1e-5 | 1e-3 | 11 | 0.1 | 0.316228 |
| 1812 | 网格 L12 | 10 | 0.01 | 1e-5 | 1e-3 | 12 | 0.1 | 0.316228 |

共同默认值：`Ldomain=8`、`drop_x=1.05`、`drop_y=0`、`drop_radius=1`、`impact_velocity=-1`、`MINlevel=6`、初始 level 6、`fErr=1e-3`、`KErr=1e-4`、`VelErr=1e-2`、输入 `tsnap=0.01`。

本仓库采用滴半径而非圆环外径作为尺度：长度 `R`，速度 `U`，密度 `rho_l`；代码中 `R=U=rho_l=1`。因此

```text
We = rho_l U^2 R / sigma
Oh_l = mu_l / sqrt(rho_l sigma R)
Re = rho_l U R / mu_l = sqrt(We)/Oh_l
solver time = t U/R
capillary-inertial time tau_sigma = sqrt(rho_l R^3/sigma) = sqrt(We) R/U
```

默认 `We=10, Ohd=0.01` 给出 `Re=316.228`，不是参数注释中的约 100。`apply_physics_scaling()` 把输入 `tmax` 乘以 `sqrt(We)`，所以输入 `tmax` 实际等于 `t/tau_sigma`；当前注释把它称为 convective time 不准确。`Ohs` 的代码实现为 `mu2=Ohs/sqrt(We)`，没有按 gas density 构造常规气相 Oh，定义需要确认。输入 `tsnap` 被解析、验证和打印，但实际快照周期来自源码常量 `TSNAP=0.01`。

## 6. 坐标与边界条件审计

Basilisk pinned `axi.h` 的真实约定是：`x` 为轴向/longitudinal，`y` 为径向，`y=0` 是旋转对称轴。Drop-Impact 的若干注释把它们写反。

| 代码对象 | 实际含义 | 注释不一致 | 物理影响判断 |
|---|---|---|---|
| `(drop_x, drop_y)=(1.05,0)` | 滴心位于轴向 x=1.05、径向轴 y=0；半径 1，离 x=0 固壁间隙 0.05 | 注释称 x radial、y axial | 初始化实际正确；文档错误 |
| `u.x=-f` | 沿轴向负 x 冲向 x=0 | 注释易被理解为径向 | 运动方向实际正确 |
| `left` | x=0 的固体冲击平面 | helper 注释称 axis | 速度边界形成无滑移壁；注释错误 |
| `bottom` | y=0 旋转轴 | 部分注释称 surface | 默认轴对称边界实际正确 |
| `right` / `top` | 轴向远场 / 径向远场 | 名称被错误坐标说明混淆 | 实际出流位置合理 |
| `f[left]=0` | 固壁 ghost-cell 的 VOF Dirichlet 条件 | 注释称“axis 上无液体” | 不只是文档：会参与接触线/壁面 VOF 行为 |

诊断积分中的 `2*pi*y` 正好使用径向坐标，轴对称体积/动能积分是正确的。应变率实现的数学分量也与真实几何一致，只是说明中的分量命名反了。`Video-generic.py` 读取 raw `(x,y)` 后显式交换为 `(Z,R)`，所以图像方向正确。

`getFootPrint` 以 `x < x_cutoff` 选择靠近 x=0 固壁的界面，再取最大 y，实际输出是径向 footprint；其“axis/height/metre”注释和图例单位均不正确。该条件本身按实际坐标是合理的，但 cutoff 选择会影响数值。

## 7. 默认源码编译

命令 `./runSimulation.sh --compile-only default.params` 退出 0，完整输出见 `logs/stage_a_default_compile.log`。实际编译命令是：

```bash
cd simulationCases/1000
/home/kqdx/basilisk_work/reproductions/drop_impact_20260718/upstream/basilisk/src/qcc \
  -I../../src-local -O2 -Wall -disable-dimensions dropImpact.c -o dropImpact -lm
```

Drop-Impact 编译无 warning。`simulationCases/1000/` 包含 `case.params` 3774 B、`dropImpact.c` 12141 B、可执行文件 `dropImpact` 438160 B。参数和源码副本分别与原文件 SHA-256 完全一致。

## 8. 冒烟、重复性与参数响应

三个算例均正常退出，`log`、`restart` 和全部 intermediate snapshots 非空；没有 NaN、Inf、SIGFPE 或段错误。原始摘要见 [`tables/smoke_summary.tsv`](tables/smoke_summary.tsv)。

1808 与 1809：116 步；solver 时间分别 1.546 s 和 1.543 s；标量日志 SHA-256 都是 `31dcc757...ad8`；`t=0.1` 的 PLIC 界面 SHA-256 都是 `a5497808...e6b`；最终 snapshot 的体积、动能、最大速度、cell count 等也完全一致。这比要求的浮点容差一致更强，但没有要求二进制 dump 逐字节相同。

We 响应不是“只改参数文件但结果不变”：

| tU/R | footprint R（We=10） | footprint R（We=20） | KE（We=10） | KE（We=20） |
|---:|---:|---:|---:|---:|
| 0.1 | 0.474992 | 0.474087 | 1.93740 | 1.94324 |
| 0.2 | 0.698840 | 0.751345 | 1.85714 | 1.89317 |
| 0.3 | 0.944984 | 1.070900 | 1.83775 | 1.87642 |

较高 We 在后期铺展更大、动能衰减较慢，方向合理。该结果仍只属于低分辨率功能响应，不是物理验证。

## 9. 输出文件、单位与可追溯含义

| 输出 | 内容 | 尺度/单位 |
|---|---|---|
| `results/log` | iteration、dt、solver time、kinetic energy | dt/time 为 `R/U`；KE 为 `rho_l U^2 R^3` 归一化 |
| `results/restart` | 最终 Basilisk dump | 二进制、无物理单位；已实际 restore |
| `results/intermediate/snapshot-*` | 逐时刻 Basilisk dump | 文件名时间为 `tU/R`；已实际 restore |
| facet `.dat` | 每个 PLIC 界面段的 `(x1,y1),(x2,y2)` | raw x 为 axial `x/R`，raw y 为 radial `r/R` |
| `rFootvsTime_*.csv` | time、靠壁区域界面最大径向坐标 | time 为 `tU/R`；rf 与 cutoff 都为 `R`，不是 metre |
| `getData-generic` stream | raw x、y、`log10(f D:D)`、`|u|` | x/R、r/R；速度 U；梯度 U/R 的无量纲实现 |
| snapshot audit TSV | 轴对称 VOF 体积、KE proxy、max speed、leaf cells、min Delta | `R^3`、`rho_l U^2R^3`、U、个数、R |
| PNG/PDF/MP4 | 镜像界面、应变率和速度演化 | 坐标 R；上游标题 `t/tau0` 实际取 snapshot 的 `tU/R` |

体积代理计算为 `sum(2*pi*y*f*Delta^2)`；动能代理为 `sum(2*pi*y*0.5*rho(f)*|u|^2*Delta^2)`。两者从 dump 只读计算，不依赖动画观感。

运行脚本的覆盖行为单列在 [`tables/file_side_effects.tsv`](tables/file_side_effects.tsv)。最重要的审计风险是重复 CaseNo 会重用目录并覆盖 case 副本/可执行文件；求解器在 restore 前以 `w` 打开 log，会截断已有历史；restart 与同名 snapshot 会覆盖。历史复现不应复用 CaseNo。

## 10. AMR 策略与初步网格收敛

求解器使用 axisymmetric quadtree。初始网格 level 6，并在滴附近预细化到 MAXlevel；运行中以 `f`、曲率 `KAPPA`、`u.x`、`u.y` 做 wavelet AMR，容差分别为 `1e-3`、`1e-4`、`1e-2`，最低 level 6。代码还对 `x>4` 或 `y>8` 区域 unrefine；因 `Ldomain=8`，后一个条件对域内基本不生效。

三级主比较如下，完整精度见 [`tables/grid_convergence.tsv`](tables/grid_convergence.tsv)：

| level | 最大 leaf cells | 最终 leaf cells | min Delta/R | min dt | 最大体积漂移 | KE(t=.3) | 时间窗最大 footprint/R @ t | 最大 snapshot speed/U | solver s | case MB |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 33,004 | 9,640 | 0.0078125 | 3.542e-6 | 1.430e-5 | 1.82764 | 0.890829 @ .31 | 11.7074 | 18.07 | 37.27 |
| 11 | 118,930 | 16,141 | 0.00390625 | 1.252e-6 | 5.677e-6 | 1.84566 | 0.894809 @ .31 | 14.7933 | 100.6 | 69.72 |
| 12 | 460,933 | 27,862 | 0.001953125 | 4.427e-7 | 2.502e-6 | 1.85405 | 0.895490 @ .31 | 18.8743 | 924.0 | 146.61 |

初始体积由 L10/L11/L12 的 4.1887263、4.1887742、4.1887862 逼近单位球解析体积 `4*pi/3=4.1887902`；L12 时间窗最大相对体积漂移仅 `2.50e-6`，且随细化下降。

L11→L12 原始差值与相对变化：

| 指标 | L11 | L12 | L12-L11 | 相对变化 |
|---|---:|---:|---:|---:|
| 最终体积 | 4.1887504462 | 4.1887757287 | +2.52825e-5 | 0.000604% |
| 最大相对体积漂移 | 5.67699e-6 | 2.50224e-6 | -3.17474e-6 | 降低 55.92% |
| 最终 KE | 1.83447 | 1.84276 | +0.00829 | 0.4519% |
| KE(t=.1/.2/.3) | 2.04664/1.95342/1.84566 | 2.05507/1.96235/1.85405 | +.00843/.00893/.00839 | 0.412/0.457/0.455% |
| 时间窗最大 footprint | 0.894809 | 0.895490 | +0.000681 | 0.0761% |
| 出现时间 | 0.31 | 0.31 | 0 | 0% |
| 最大局部速度 | 14.7933 | 18.8743 | +4.08098 | 27.59% |

体积漂移“相对变化超过 5%”是误差量大幅减小，不是守恒变差。主要积分量满足 5% 工程门槛；局部速度不满足。L11/L12 界面的对称 Hausdorff 距离在 `t=.1/.2/.3` 分别为 0.002914、0.002795、0.002670 R，约为 1.49、1.43、1.37 个 L12 最细网格宽度，显示界面在改善但尚不能代替长期收敛验证。

## 11. 后处理流程与图件

优先使用未修改的上游 `runPostProcess-Ncases.sh`、`getFacet`、`getData-generic`、`getFootPrint`、`Video-generic.py`。pinned Basilisk 的维度检查使后两项普通 `-autolink` 编译失败；保持源码不变，加入仓库自身求解器也使用的 `-disable-dimensions` 后编译成功。

Case 1808 原生流程输出 32 个 PNG、一个 MP4、五个 footprint CSV 和一个 PDF。三个实际 PLIC 时刻已导出到 `figures/interface_case1808_t*.dat`，界面演化图为 [`figures/interface_evolution_case1808.png`](figures/interface_evolution_case1808.png)。三级公共时刻界面图为 [`figures/grid_interface_common_times.png`](figures/grid_interface_common_times.png)，另有体积、KE、footprint 对比图。

原生 cutoff `0.001, 0.0025, 0.005, 0.01` 在 L8 均小于首个 cell center，故返回零；不是“无铺展”。`x/R<=0.05` 才得到有效 L8 footprint。上游 PDF 图例错误地标为 metre；本报告全部按无量纲 R 解释。

## 12. Warning、失败与资源门控

逐项表见 [`tables/warnings_and_failures.tsv`](tables/warnings_and_failures.tsv)，原始 stdout/stderr 均在 `logs/`。

- Basilisk 自身安装产生 5 个上游编译 warning：wsServer discarded const 1 个、TinyPngOut nonnull compare 1 个、display.h discarded const 3 个；最终 qcc 检查成功。
- Drop-Impact 默认编译与所有求解运行无 warning，无无效数值。
- getData/getFootPrint 的首次编译因维度约束退出，已用 `-disable-dimensions` 兼容，未改源码。
- Matplotlib 找不到 Computer Modern，只影响字体并回退 DejaVu。
- 第一次审计 helper 以跨目录 source 路径交给 qcc 时退出 139；同一 helper 从其目录用 basename 编译成功。失败临时目录完整保留。

资源外推见 [`tables/resource_estimates.tsv`](tables/resource_estimates.tsv)。基于 L11→L12 实测 runtime 比 9.185、磁盘比 2.103：短时 L14 约 21.7 h、0.65 GB（保守 2.35 GB）；默认时窗粗略线性外推约 216.5 h/9.0 天、6.5 GB（保守 23.5 GB）。后期动力学可能比线性外推更贵。L12 初始最大 leaf cells 460,933，L14 仅按四倍/level 外推可达约 7.37 million，估计运行内存约 4--8 GiB。因时间明确超过 60 分钟，且默认磁盘保守值超过 20 GB，按用户门槛暂停等待确认。

## 13. 可迁移与不可迁移内容

适合迁移到圆环项目的是**方法**：固定 commit/tag 和安装器哈希、独立环境文件、参数副本和 checksum、每 case 唯一编号、snapshot 的体积/动能/速度/cell/dt 数值审计、公共时刻 PLIC 比较、先短时三级网格再做资源门控、明确 raw coordinate 到物理坐标的转换。

不能直接迁移的是：GPL-3.0 的 Drop-Impact 源码、脚本或其代码片段（除非圆环项目完成兼容的许可证决定）；独立 Basilisk 安装产物；滴撞击几何和固壁 `f[left]=0` 假设；错误的 x/y 注释；以滴半径定义的 We/Oh/Re 直接套用到以圆环外径定义的体系；本轮短时 L8/L10--L12 数值结果；会覆盖旧 CaseNo 的目录策略。

## 14. 下一步 Bursting-Bubble 复现建议

Bursting-Bubble 应作为新的独立复现目录和审计对象：先固定仓库 SHA、license 与指定 Basilisk tag，逐文件读取其 AGENTS/README/source；先核对 axisymmetric 坐标、自由表面/气泡相定义、重力与 Laplace/Oh/Bond 数尺度；用两个相同低成本算例验证重复性，再改变一个明确的物理参数；从 dump 数值记录气泡/液体体积、界面拓扑事件时刻、最大速度、最小 dt、动能和 cell counts；导出真实 PLIC；最后在相同物理时窗上做至少三级网格比较，并在启动默认最细网格前应用同样的 60 分钟/20 GB 门控。不要把本仓库 GPL 源码或本次 Drop-Impact case 复制到 Ring_Foountain。

## 15. 交付物索引

- 环境：[`environment.txt`](environment.txt)
- 命令：[`commands.log`](commands.log)
- 独立运行原始校验和：[`external_run_checksums.sha256`](external_run_checksums.sha256)
- 仓库内迁移产物校验和：[`artifact_manifest.sha256`](artifact_manifest.sha256)
- 参数：[`params/`](params/)
- 收敛表：[`tables/grid_convergence.tsv`](tables/grid_convergence.tsv)
- 资源估计：[`tables/resource_estimates.tsv`](tables/resource_estimates.tsv)
- 图件：[`figures/`](figures/)
- 未决问题：[`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md)

所有正式报告产物位于独立 `report/`；上游求解输出保留在各自 `upstream/simulationCases/<CaseNo>/`，没有覆盖 Ring_Foountain 的任何历史结果。
