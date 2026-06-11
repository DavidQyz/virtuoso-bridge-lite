# WORKLOG — virtuoso-bridge-lite

Durable, in-repo record of what was done and why. Newest entries on top.
Read the top few entries at the start of a session to recover project state.
Append a short entry when wrapping up substantial work (or run `/eod`).

Scope: one entry per working session or milestone. Keep it short — link to the
real artifacts (ota5t/ READMEs, git commits, Claude memory) instead of duplicating
detail here. Project-specific design knowledge also lives in Claude memory;
generalizable workflow lessons go to `project_management/agentos_lesson_candidates.md`.

---

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
