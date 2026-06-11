# WORKLOG — virtuoso-bridge-lite

Durable, in-repo record of what was done and why. Newest entries on top.
Read the top few entries at the start of a session to recover project state.
Append a short entry when wrapping up substantial work (or run `/eod`).

Scope: one entry per working session or milestone. Keep it short — link to the
real artifacts (ota5t/ READMEs, git commits, Claude memory) instead of duplicating
detail here. Project-specific design knowledge also lives in Claude memory;
generalizable workflow lessons go to `project_management/agentos_lesson_candidates.md`.

---

## 2026-06-12 (later) — OTA_V3 paused at a decision point (class-AB stage)

- New device attempt `ota5t/ota_v3/`: RFC stage 1 (~2.1uA, FC-like) + Monticelli
  class-AB output + Miller comp. AC converged: A0=111.9dB, GBW=57.5MHz, PM=62°,
  7.05uW, PSRR 71dB.
- **Key finding**: at CL=50fF the comp cap gates the slew (SR=I1/Cc): 3-way
  buffer-step test gives FC 12/16, V2 40/70 (wins), V3 25/47 V/us. Ahuja comp
  worse here (fold-node resonance forces bigger Cc). Class-AB's value needs a
  heavier/nonlinear load to show.
- User defined the next-phase load: **nmos5v gate, w=6u l=600n nf=4** (OTA out
  drives that gate). Design paused until user resumes ("next year") — resume
  plan + full state in Claude memory `project_ota_v3`; schematic figure done
  (`ota_v3_schematic.yaml`, input-left/load-middle/output-right per user).

## 2026-06-12 — OTA_V2: recycling folded cascode (GBW ×3.1)

- New device `ota5t/ota_v2/`: RFC redesign of fc_ota per spec "same DC gain,
  ~2x power, maximize GBW, keep Vcm=0.3V + medium swing".
- Result: A0 75.6dB (+1.1), **GBW 69.5MHz (×3.1)**, PM 61°, 7.17µW (1.89×),
  PSRR 67dB, one bias pin eliminated. Full report: `ota5t/ota_v2/README.md`.
- Key findings recorded there: sub-um mirrors need unit devices (model-bin
  trap gave 1.6:1 from a 3:1 W ratio); non-dominant poles bind (wider input
  pair trades 24% GBW for −24° PM); current scaling is PM-neutral in weak
  inversion (GBW is linearly purchasable with power, table in README §4).

## 2026-06-11 — AgentOS onboarding (Stage 0 + Stage 1)

- Adopted the AgentOS management framework. Control hub created at
  `GitHub/agentos/` with a registry entry for this project (language, sync,
  subagent, memory, visualization profiles + allow/block sync paths).
- Resolved decisions: keep public fork; ota5t/ may stay public.
- Stage 1 wiring added here: this WORKLOG, two AGENTS.md continuity rules, and
  the `/eod` command. `docs/` is a published GitHub Pages site
  (virtuoso-bridge.tokenzhang.com), so project-management records live in
  top-level `project_management/`, not `docs/`.

## 2026-06-11 — Comparator COMP_V2 + library work (earlier sessions)

- **COMP_V2** (`test/COMP_V2`): dual-threshold redesign of the common-gate
  comparator. tprop 0.923 ns @ INN=1V (V4: 1.015), up to −27% at high INN,
  power flat (+30% budget unused). Full write-up: `ota5t/comp_v2/README.md`.
- **3-way comparison** (original V4 / COMP_CG replica / COMP_V2) via si
  ground-truth netlist: `ota5t/comp_v2/comp_v2_*_vs_v4.png`.
- **test_rect migrated to local disk** (`/home/IC/test_rect`) on the VM: hgfs
  share can't create OA edit locks (no hard-link support); cds.lib repointed.
  Also cleared stale cross-host `.cdslck` locks. See Claude memory
  `test_rect_stale_locks`.
- Folder reorg: `ota5t/` is now one-folder-per-device (ota_5t / fc_ota /
  comp_cg / comp_v2 / tools), each with its own README.

> Detailed design knowledge for the above is in the per-device READMEs and in
> Claude memory. This entry is the index, not the record.
