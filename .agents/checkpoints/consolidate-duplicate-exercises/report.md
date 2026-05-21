# Duplicate Exercise Name Candidates

**Source file:** `workouts_start_20230308_end_20260416_num_437.json`  
**Total unique exercise names:** 594  
**Candidate groups found:** 43  
**Generated:** 2026-05-21 22:03:01  

> This report is for **human review only**. No data has been modified.
> Each group lists names that may refer to the same exercise.
> Groups marked ⚠️  differ by equipment/grip qualifiers and may be intentional distinct exercises.

---

## Post-Dedup Taxonomy Opportunity

**The core idea:** your naming convention already encodes a natural hierarchy — `biceps.` → `biceps. standing.` → `biceps. standing. ez bar.` — but it's implicit and inconsistent. After deduplication, you could formalize this as a two- or three-level taxonomy that lets you drill in or zoom out:

```
Level 1 (muscle/movement): biceps
Level 2 (position/equipment class): biceps > standing, biceps > seated, biceps > preacher
Level 3 (specific variant): biceps > preacher > machine, biceps > preacher > bench, biceps > preacher > bench (right only)
```

**Why the dot-separated format already works for this:** `"biceps. standing. ez bar."` parses cleanly — segment 0 is the root, each subsequent segment is a narrower qualifier. The dedup step just needs to agree on canonical segment spellings before the taxonomy is buildable.

**The two things to decide after dedup:**

1. **Which variants warrant a separate Level 2 node** (distinct progress tracking) vs. which are just noise qualifiers that should roll up? Examples from the data:
   - `biceps. preacher.` vs `biceps. standing.` — clearly distinct exercises (different ROM, different muscle emphasis) → **keep as separate Level 2 nodes**
   - `biceps. standing.` vs `biceps. standing. separate.` — same exercise, minor form note → **roll up to Level 2**
   - `pull-ups. wide.` vs `pull-ups. v grip.` vs `pull-ups.` — grip meaningfully changes stimulus → **keep as separate Level 3 nodes under pull-ups**
   - `pull-ups. high.` / `pull-ups. short.` / `pull-ups. tall.` — these look like bar-height notes, not distinct exercises → **roll up to pull-ups.**

2. **Whether to track progress at Level 2 or Level 3.** The data suggests you naturally zoomed in over time (early entries: `Biceps`, `Bicep`; later: `biceps. standing. ez bar.`). A taxonomy lets you query "all biceps sets" while still charting `biceps > standing > ez bar` separately.

**Suggested taxonomy for the major exercise families** (draft — decisions marked where data is ambiguous):

### biceps (P1)
```
biceps
├── standing
│   ├── [default — dumbbell implied]
│   ├── barbell / ez bar           ← worth separating (fixed ROM, heavier loads)
│   └── separate                   ← roll up to standing
├── seated
│   ├── [default — upright]
│   └── incline                    ← worth separating (longer ROM, stretch-focused)
├── preacher
│   ├── machine                    ← worth separating
│   └── bench                      ← worth separating
├── cable / bayesian               ← worth separating (constant tension)
└── [unqualified — early entries, roll up to root]
```
Note: triceps currently lives in the same P1 group due to union-find chaining through early Bicep/Tricep entries. **After dedup, biceps and triceps should be separate root nodes.**

### shoulders (P2)
```
shoulders
├── overhead press
│   ├── barbell (standing)
│   ├── dumbbell (seated or standing)
│   └── machine
├── incline press                  ← ambiguous: is this a separate movement or a modifier?
│   └── [variants: barbell, dumbbell, smith machine]
└── [unqualified — roll up to root]
```
Note: "incline shoulder press." (48 appearances, dominant variant) is almost certainly its own distinct movement vs a flat overhead press. Worth keeping as Level 2.

### abs (P3)
```
abs
├── core [general — most entries]
│   ├── cable / cable machine      ← worth separating (weighted, different stimulus)
│   └── [unqualified]
└── at home                        ← roll up to root or drop (location note, not exercise)
```

### pull-ups (P4)
```
pull-ups
├── [default — standard grip]
├── wide                           ← worth separating
├── v grip                         ← worth separating
├── assisted                       ← worth separating (different load)
└── height notes (high/short/tall/medium) ← roll up to default; these are bar-height cues, not distinct exercises
```

### chest fly (P5)
```
chest fly
├── machine / pec dec              ← keep separate (see P13 for seated pec dec)
├── cable                          ← keep separate
├── dumbbell flat                  ← worth separating
└── dumbbell bench (incline)       ← worth separating
```
Note: "chest flys." vs "chest fly." is a spelling dup — consolidate to one canonical spelling.

### dips / back extensions / leg extensions (P6)
Three separate exercises collapsed into one group by union-find. After dedup these should be three separate root nodes:
```
dips
├── [default — tricep dips]
├── back / lower back              ← back extension variant, keep separate
└── assisted

back extensions (lower back machine)

leg extensions (quad isolation)
```

### calves (P7)
```
calves
├── seated                         ← keep separate (soleus-dominant)
│   └── [default machine]
├── standing                       ← keep separate (gastrocnemius-dominant)
│   └── [default machine]
└── [unqualified — roll up to root]
```
Note: "calf calves." is a redundant phrasing; canonical should be just "calves." or "calf raises."

### bench press (P8)
```
bench press
├── flat
│   ├── barbell (implied default)
│   ├── dumbbell
│   └── smith machine
├── incline
│   ├── barbell
│   ├── dumbbell
│   └── machine
└── iso-lateral                    ← keep separate (unilateral machine movement)
```
Note: bare `bench.` (44 appearances) is the dominant canonical name; `incline bench.` (14 appearances) is a well-established Level 2 node.

### lat pull-down (P9)
```
lat pull-down
├── [default — standard grip]
├── diamond grip                   ← worth separating
├── cbum grip                      ← style note, could roll up
├── machine (various)              ← roll up to default
└── iso-lateral                    ← keep separate
```

### rows (P17)
Three different rowing movements are grouped together. After dedup, separate root nodes:
```
cable rows (seated low rows)
bent-over rows
│   ├── barbell
│   ├── dumbbell
│   └── cable
standing rows
```

**Implementation path (suggested order):**
1. Run dedup: consolidate all exact/near-exact matches → reduces ~594 names to maybe ~80–100 canonical names
2. Manually assign each canonical name a `root` tag and optional `modifier` tags
3. Build a simple taxonomy map (JSON dict: `canonical_name → {root, level2, level3}`)
4. The existing app can then query by root to get all sets, or filter by level2/level3 for specific tracking

---

## Exact Matches (after normalisation)

*These names normalise to the same string — safe to consolidate.*

### Group E1 — 3 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Vertical press` | 1 | 2023-07-10 | 2023-07-10 |
| `Vertical press.` | 1 | 2023-10-31 | 2023-10-31 |
| `vertical press.` | 1 | 2024-07-16 | 2024-07-16 |

### Group E2 — 3 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Lateral raise.` | 1 | 2024-02-25 | 2024-02-25 |
| `lateral raise.` | 2 | 2025-10-01 | 2025-10-27 |

## Prefix / Subset Matches

*One name appears to be a prefix/subset of others — review whether the longer name is a distinct exercise.*

### Group P1 — 380 total appearances
> **Taxonomy note:** Two separate root nodes collapsed here by union-find chaining — **biceps** and **triceps** should be split apart after dedup. Within biceps: `biceps.` (89×) is the canonical root; `biceps. standing.` (25×), `biceps. seated.` (16×), and `biceps. preacher.` (13×) are the natural Level 2 nodes worth tracking separately. Within triceps: `triceps.` (39×) is the root; `triceps. rope.`, `triceps. dumbbell.`, `triceps. overhead.`, and `triceps. bent over.` are candidate Level 2 nodes.

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Bicep` | 5 | 2023-03-17 | 2023-04-28 |
| `Bicep 35` | 1 | 2023-05-21 | 2023-05-21 |
| `Bicep curls.` | 1 | 2024-04-16 | 2024-04-16 |
| `Bicep curls. Standing together.` | 1 | 2024-04-10 | 2024-04-10 |
| `Bicep machine. Seat 5.` | 2 | 2024-03-03 | 2024-03-10 |
| `Bicep machine. Seat 6.` | 1 | 2024-03-21 | 2024-03-21 |
| `Bicep pulley 80` | 1 | 2023-10-15 | 2023-10-15 |
| `Bicep with cable. Face away from cable.` | 1 | 2024-03-14 | 2024-03-14 |
| `Bicep. 5` | 1 | 2023-04-20 | 2023-04-20 |
| `Biceps` | 8 | 2023-04-05 | 2024-05-07 |
| `Biceps 40 separate.` | 1 | 2024-01-03 | 2024-01-03 |
| `Biceps 40.` | 1 | 2023-11-12 | 2023-11-12 |
| `Biceps on bench. 30.` | 1 | 2024-02-25 | 2024-02-25 |
| `Biceps.` | 1 | 2024-05-13 | 2024-05-13 |
| `Biceps. 35` | 1 | 2023-04-20 | 2023-04-20 |
| `Biceps. 40. together.` | 1 | 2024-01-25 | 2024-01-25 |
| `Biceps. 70 Barbell.` | 1 | 2024-02-04 | 2024-02-04 |
| `Biceps. Barbell` | 1 | 2024-02-11 | 2024-02-11 |
| `Biceps. Hammer.` | 1 | 2023-11-29 | 2023-11-29 |
| `Biceps. Seated incline.` | 1 | 2024-04-20 | 2024-04-20 |
| `Biceps. Seated.` | 1 | 2024-05-05 | 2024-05-05 |
| `Biceps. Standing separate.` | 1 | 2024-01-09 | 2024-01-09 |
| `Biceps. Standing. Dumbbells. Together. Control negatives.` | 1 | 2024-01-28 | 2024-01-28 |
| `Incline Bicep` | 1 | 2024-05-10 | 2024-05-10 |
| `Seated biceps` | 1 | 2023-06-11 | 2023-06-11 |
| `Seated incline bicep.` | 1 | 2024-04-27 | 2024-04-27 |
| `Seated incline biceps.` | 1 | 2024-05-02 | 2024-05-02 |
| `Tricep` | 2 | 2023-04-07 | 2023-04-13 |
| `Tricep pull ups. With rope.` | 1 | 2024-03-14 | 2024-03-14 |
| `Tricep pull-down` | 2 | 2023-04-06 | 2023-04-11 |
| `Tricep pull-ups. With rope.` | 1 | 2024-04-16 | 2024-04-16 |
| `Tricep. Rope.` | 1 | 2024-03-10 | 2024-03-10 |
| `Triceps` | 3 | 2023-03-17 | 2023-11-29 |
| `Triceps. Rope.` | 1 | 2024-02-15 | 2024-02-15 |
| `Triceps. W-handle.` | 1 | 2024-02-13 | 2024-02-13 |
| `bayesian biceps.` | 1 | 2025-04-21 | 2025-04-21 |
| `bicep curl machine.` | 1 | 2024-06-29 | 2024-06-29 |
| `bicep curls. ez bar.` | 1 | 2026-01-04 | 2026-01-04 |
| `bicep machine.` | 5 | 2024-06-27 | 2024-09-16 |
| `bicep machine. hard.` | 1 | 2024-09-21 | 2024-09-21 |
| `bicep machine. preacher curl.` | 1 | 2024-07-02 | 2024-07-02 |
| `bicep preacher machine.` | 6 | 2025-06-17 | 2025-10-03 |
| `bicep preacher.` | 1 | 2024-11-28 | 2024-11-28 |
| `bicep preacher. right only.` | 1 | 2025-02-20 | 2025-02-20 |
| `bicep. preacher bench.` | 1 | 2025-02-15 | 2025-02-15 |
| `biceps` | 5 | 2023-10-03 | 2024-10-17 |
| `biceps incline.` | 1 | 2024-07-05 | 2024-07-05 |
| `biceps preacher machine.` | 3 | 2025-02-01 | 2025-06-24 |
| `biceps.` | 89 | 2023-04-10 | 2026-04-04 |
| `biceps. 40.` | 1 | 2023-09-30 | 2023-09-30 |
| `biceps. Standing.` | 1 | 2023-04-25 | 2023-04-25 |
| `biceps. barbell.` | 4 | 2023-07-27 | 2026-01-25 |
| `biceps. bayesian.` | 2 | 2025-04-22 | 2025-04-24 |
| `biceps. bench preacher.` | 1 | 2025-03-02 | 2025-03-02 |
| `biceps. bench.` | 4 | 2024-08-07 | 2026-03-23 |
| `biceps. bench. preacher.` | 1 | 2025-03-01 | 2025-03-01 |
| `biceps. cable.` | 1 | 2025-02-12 | 2025-02-12 |
| `biceps. cable. bayesian.` | 1 | 2025-02-26 | 2025-02-26 |
| `biceps. cables.` | 1 | 2024-07-27 | 2024-07-27 |
| `biceps. deeper lean.` | 1 | 2025-12-11 | 2025-12-11 |
| `biceps. easy curl bar.` | 1 | 2026-01-03 | 2026-01-03 |
| `biceps. ez bar.` | 14 | 2026-01-26 | 2026-04-13 |
| `biceps. ez curl.` | 1 | 2026-02-06 | 2026-02-06 |
| `biceps. incline bench.` | 3 | 2024-07-07 | 2025-08-26 |
| `biceps. incline bench. seated.` | 1 | 2025-08-28 | 2025-08-28 |
| `biceps. incline.` | 2 | 2024-07-25 | 2025-02-11 |
| `biceps. preacher barbells.` | 1 | 2024-07-16 | 2024-07-16 |
| `biceps. preacher bench.` | 1 | 2025-02-16 | 2025-02-16 |
| `biceps. preacher bench. right only.` | 2 | 2025-02-17 | 2025-04-02 |
| `biceps. preacher machine.` | 12 | 2024-01-28 | 2025-10-21 |
| `biceps. preacher.` | 13 | 2024-12-22 | 2025-07-22 |
| `biceps. preacher. bench.` | 1 | 2025-07-09 | 2025-07-09 |
| `biceps. preacher. bench. preacher. right only.` | 1 | 2025-02-27 | 2025-02-27 |
| `biceps. preacher. bench. separate.` | 1 | 2025-03-25 | 2025-03-25 |
| `biceps. preacher. just right.` | 1 | 2024-12-12 | 2024-12-12 |
| `biceps. preacher. machine.` | 1 | 2025-07-31 | 2025-07-31 |
| `biceps. preacher. right only.` | 2 | 2025-02-18 | 2025-03-07 |
| `biceps. right only. preacher` | 1 | 2024-12-15 | 2024-12-15 |
| `biceps. seated bench.` | 4 | 2025-09-15 | 2025-10-15 |
| `biceps. seated incline bench.` | 3 | 2025-08-30 | 2025-09-28 |
| `biceps. seated incline.` | 1 | 2025-09-17 | 2025-09-17 |
| `biceps. seated incline. cannot swing as much.` | 1 | 2026-03-03 | 2026-03-03 |
| `biceps. seated preacher. arm curl machine.` | 1 | 2025-08-18 | 2025-08-18 |
| `biceps. seated.` | 16 | 2025-10-18 | 2026-04-16 |
| `biceps. seated. bench.` | 2 | 2025-08-23 | 2025-10-25 |
| `biceps. seated. incline.` | 1 | 2026-03-13 | 2026-03-13 |
| `biceps. seated. upright.` | 1 | 2026-02-25 | 2026-02-25 |
| `biceps. standing barbell.` | 1 | 2025-01-28 | 2025-01-28 |
| `biceps. standing dumbbells.` | 1 | 2026-01-29 | 2026-01-29 |
| `biceps. standing,` | 1 | 2023-09-23 | 2023-09-23 |
| `biceps. standing.` | 25 | 2023-04-03 | 2026-03-05 |
| `biceps. standing. ez bar.` | 1 | 2026-03-04 | 2026-03-04 |
| `biceps. standing. ez curl.` | 1 | 2026-04-08 | 2026-04-08 |
| `biceps. standing. separate.` | 1 | 2023-10-11 | 2023-10-11 |
| `preacher biceps.` | 1 | 2025-04-29 | 2025-04-29 |
| `seated biceps. preacher. second machine from mirror.` | 1 | 2025-07-08 | 2025-07-08 |
| `tricep machine.` | 1 | 2024-10-09 | 2024-10-09 |
| `tricep press machine.` | 1 | 2026-01-29 | 2026-01-29 |
| `tricep.` | 2 | 2024-08-03 | 2024-10-20 |
| `tricep. dumbbell.` | 1 | 2024-10-03 | 2024-10-03 |
| `tricep. separate. easy machine.` | 1 | 2024-07-25 | 2024-07-25 |
| `triceps.` | 39 | 2023-03-08 | 2026-01-17 |
| `triceps. Short flat. Hands close grip` | 1 | 2023-07-27 | 2023-07-27 |
| `triceps. Standing diagonal` | 1 | 2023-08-21 | 2023-08-21 |
| `triceps. W handle` | 1 | 2023-06-13 | 2023-06-13 |
| `triceps. arm extension machine.` | 1 | 2025-08-15 | 2025-08-15 |
| `triceps. bar pull-down.` | 1 | 2026-02-04 | 2026-02-04 |
| `triceps. bent over.` | 1 | 2025-02-12 | 2025-02-12 |
| `triceps. bent over. nippard. height 15.` | 1 | 2025-02-08 | 2025-02-08 |
| `triceps. cables. kneeling.` | 1 | 2026-02-24 | 2026-02-24 |
| `triceps. double.` | 1 | 2025-08-08 | 2025-08-08 |
| `triceps. dumbbell.` | 7 | 2025-12-31 | 2026-01-27 |
| `triceps. dumbbells.` | 2 | 2025-03-09 | 2026-01-09 |
| `triceps. overhead.` | 1 | 2024-09-25 | 2024-09-25 |
| `triceps. overhead. right only.` | 1 | 2025-04-09 | 2025-04-09 |
| `triceps. overhear cable.` | 1 | 2026-02-04 | 2026-02-04 |
| `triceps. rope.` | 5 | 2023-11-19 | 2026-01-14 |
| `triceps. single down.` | 1 | 2025-03-27 | 2025-03-27 |

### Group P2 — 139 total appearances
> **Taxonomy note:** Root = **shoulders (press)**. `incline shoulder press.` (48×) is the dominant variant and warrants its own Level 2 node — it is mechanically distinct from a flat/standing overhead press. `shoulder press. barbell.` (5×+6×) and `shoulder press. dumbbells.` (2×+4×) are Level 3 nodes under a flat/standing press Level 2. `shoulders.` (5×) is the unqualified root catch-all.

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Dumbbell shoulder press` | 1 | 2023-08-01 | 2023-08-01 |
| `Incline dumbbell` | 1 | 2024-01-05 | 2024-01-05 |
| `Seated dumbbell shoulders.` | 1 | 2024-05-02 | 2024-05-02 |
| `Seated shoulder dumbbell` | 1 | 2023-10-26 | 2023-10-26 |
| `Seated shoulder press` | 2 | 2023-09-06 | 2024-01-03 |
| `Seated shoulder press 40` | 1 | 2024-01-07 | 2024-01-07 |
| `Seated shoulder press dumbbell.` | 1 | 2024-02-13 | 2024-02-13 |
| `Seated shoulder press dumbbells` | 1 | 2023-08-13 | 2023-08-13 |
| `Seated shoulder press.` | 1 | 2023-09-30 | 2023-09-30 |
| `Shoulder barbell` | 1 | 2024-02-15 | 2024-02-15 |
| `Shoulder barbell.` | 1 | 2024-03-10 | 2024-03-10 |
| `Shoulder barbell. No spotter.` | 1 | 2024-03-21 | 2024-03-21 |
| `Shoulder press` | 1 | 2024-05-10 | 2024-05-10 |
| `Shoulder press.` | 4 | 2023-09-26 | 2024-05-07 |
| `Shoulders barbell.` | 1 | 2024-02-11 | 2024-02-11 |
| `Shoulders. Barbell` | 1 | 2024-03-03 | 2024-03-03 |
| `Standing Shoulder` | 1 | 2023-07-29 | 2023-07-29 |
| `incline dumbbell shoulders.` | 1 | 2025-12-20 | 2025-12-20 |
| `incline shoulder press` | 1 | 2026-02-03 | 2026-02-03 |
| `incline shoulder press dumbbells.` | 1 | 2026-01-09 | 2026-01-09 |
| `incline shoulder press.` | 48 | 2023-04-10 | 2026-04-14 |
| `incline shoulder press. bar might be lighter.` | 1 | 2026-03-18 | 2026-03-18 |
| `incline shoulder press. bench.` | 1 | 2026-01-21 | 2026-01-21 |
| `incline shoulder press. dumbbells.` | 1 | 2026-01-18 | 2026-01-18 |
| `incline shoulder press. smith machine.` | 1 | 2026-03-13 | 2026-03-13 |
| `shoulder barbell.` | 4 | 2024-07-25 | 2025-03-11 |
| `shoulder incline bench.` | 1 | 2026-01-07 | 2026-01-07 |
| `shoulder incline press.` | 1 | 2026-01-12 | 2026-01-12 |
| `shoulder machine. incline.` | 1 | 2026-01-27 | 2026-01-27 |
| `shoulder press barbell.` | 5 | 2024-06-04 | 2025-12-07 |
| `shoulder press machine.` | 3 | 2026-01-19 | 2026-01-30 |
| `shoulder press machine. inclined.` | 1 | 2026-02-04 | 2026-02-04 |
| `shoulder press.` | 5 | 2024-05-23 | 2025-11-18 |
| `shoulder press. barbell.` | 6 | 2024-06-27 | 2025-12-13 |
| `shoulder press. dumbbell.` | 1 | 2026-01-03 | 2026-01-03 |
| `shoulder press. dumbbells.` | 2 | 2024-05-13 | 2025-11-17 |
| `shoulder press. dumbbells. Seated dumbbell shoulder press` | 1 | 2023-11-30 | 2023-11-30 |
| `shoulder press. no spotter.` | 1 | 2024-10-01 | 2024-10-01 |
| `shoulder. incline bench. barbell.` | 1 | 2026-01-15 | 2026-01-15 |
| `shoulders barbell.` | 1 | 2024-11-01 | 2024-11-01 |
| `shoulders clicking.` | 1 | 2026-01-19 | 2026-01-19 |
| `shoulders.` | 5 | 2024-09-02 | 2025-02-11 |
| `shoulders. barbell.` | 7 | 2023-07-10 | 2025-12-09 |
| `shoulders. barbell. raw.` | 1 | 2023-08-20 | 2023-08-20 |
| `shoulders. dumbbell.` | 4 | 2023-09-08 | 2024-04-20 |
| `shoulders. dumbbells.` | 4 | 2023-07-29 | 2026-02-24 |
| `shoulders. incline bench.` | 2 | 2023-03-08 | 2026-01-17 |
| `shoulders. incline bench. barbell.` | 1 | 2026-01-14 | 2026-01-14 |
| `shoulders. incline.` | 1 | 2026-01-13 | 2026-01-13 |
| `shoulders. incline. dumbbells.` | 1 | 2026-01-06 | 2026-01-06 |
| `shoulders. machine overhead press.` | 1 | 2025-07-26 | 2025-07-26 |
| `shoulders. standing barbell.` | 1 | 2026-03-26 | 2026-03-26 |

### Group P3 — 132 total appearances
> **Taxonomy note:** Root = **abs**. `abs core.` (58×+23×) dominates — "core" is a redundant qualifier in this dataset; canonical Level 1 should be `abs.`. `abs cable.` (25×) and `abs core. cable.` (23×) are the same thing and should consolidate to `abs. cable.` as a Level 2 node. `abs core. push machine.` (3×) → `abs. push machine.` Level 2.

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Abs at home.` | 4 | 2024-05-02 | 2024-05-13 |
| `Abs core.` | 2 | 2024-03-10 | 2024-04-27 |
| `Abs.` | 1 | 2024-02-06 | 2024-02-06 |
| `Abs. Core.` | 1 | 2024-02-25 | 2024-02-25 |
| `abs at home.` | 2 | 2024-05-15 | 2024-05-23 |
| `abs cable.` | 25 | 2024-12-07 | 2025-12-06 |
| `abs core` | 2 | 2025-03-29 | 2025-07-13 |
| `abs core.` | 58 | 2023-03-08 | 2026-02-12 |
| `abs core. belt.` | 1 | 2024-11-14 | 2024-11-14 |
| `abs core. cable.` | 23 | 2025-12-31 | 2026-04-16 |
| `abs core. cable. plastic grip.` | 1 | 2026-02-24 | 2026-02-24 |
| `abs core. cables.` | 1 | 2026-02-11 | 2026-02-11 |
| `abs core. push machine.` | 3 | 2026-01-30 | 2026-02-28 |
| `abs push machine.` | 1 | 2026-01-21 | 2026-01-21 |
| `abs.` | 4 | 2024-06-04 | 2025-04-17 |
| `abs. cable.` | 1 | 2025-03-25 | 2025-03-25 |
| `abs. core.` | 2 | 2025-02-01 | 2025-03-27 |

### Group P4 — 127 total appearances
> **Taxonomy note:** Root = **pull-ups**. `pull-ups.` (81×) is canonical. Natural Level 2 nodes: `pull-ups. wide.` (6×), `pull-ups. v grip.` (7×), `assisted pull-ups.` (7×+1×). **Roll up:** `pull-ups. high/short/tall/medium height/higher/mid height` — these are bar-height cues at a specific gym, not distinct exercises.

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Assisted pull-ups.` | 1 | 2024-08-26 | 2024-08-26 |
| `Pull ups.` | 1 | 2024-03-21 | 2024-03-21 |
| `Pull-ups` | 2 | 2023-05-10 | 2023-10-15 |
| `Pull-ups. 1 rep. Slow negative.` | 1 | 2024-05-10 | 2024-05-10 |
| `assisted pull ups.` | 1 | 2024-07-02 | 2024-07-02 |
| `assisted pull-ups` | 1 | 2024-07-14 | 2024-07-14 |
| `assisted pull-ups.` | 7 | 2024-07-12 | 2024-10-03 |
| `pull ups.` | 3 | 2025-04-24 | 2025-07-03 |
| `pull-ups` | 2 | 2023-03-08 | 2025-01-12 |
| `pull-ups  x15. hands slippery.` | 1 | 2025-12-12 | 2025-12-12 |
| `pull-ups 2.` | 1 | 2024-05-13 | 2024-05-13 |
| `pull-ups.` | 81 | 2024-09-11 | 2026-04-13 |
| `pull-ups. high.` | 2 | 2026-02-08 | 2026-02-19 |
| `pull-ups. high. jump.` | 1 | 2026-02-14 | 2026-02-14 |
| `pull-ups. higher.` | 1 | 2026-02-04 | 2026-02-04 |
| `pull-ups. medium height.` | 1 | 2026-02-06 | 2026-02-06 |
| `pull-ups. mid height.` | 1 | 2026-03-23 | 2026-03-23 |
| `pull-ups. short.` | 2 | 2026-02-03 | 2026-04-09 |
| `pull-ups. skip me.` | 1 | 2025-02-18 | 2025-02-18 |
| `pull-ups. tall.` | 2 | 2026-02-11 | 2026-03-04 |
| `pull-ups. v grip.` | 7 | 2025-12-20 | 2026-01-12 |
| `pull-ups. wide.` | 6 | 2025-05-20 | 2025-09-15 |
| `pull-ups. wider grip.` | 1 | 2025-06-26 | 2025-06-26 |

### Group P5 — 107 total appearances
> **Taxonomy note:** Root = **chest fly**. `chest fly.` (78×) is canonical — consolidate `chest flys.` spelling variant. Level 2 nodes: `chest fly. bench.` (10×, dumbbell on flat/incline bench), `chest fly. cable.` (1×). `chest fly rear delt machine.` is a different exercise entirely (rear delt fly) — **should be its own root** after dedup.

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Chest fly` | 2 | 2023-06-06 | 2023-07-29 |
| `Chest fly.` | 1 | 2025-11-26 | 2025-11-26 |
| `chest fly bench.` | 1 | 2025-08-28 | 2025-08-28 |
| `chest fly rear delt machine.` | 1 | 2026-01-04 | 2026-01-04 |
| `chest fly seated cable.` | 1 | 2023-07-03 | 2023-07-03 |
| `chest fly.` | 78 | 2023-04-04 | 2026-04-16 |
| `chest fly. bench.` | 10 | 2025-08-27 | 2026-01-15 |
| `chest fly. cable.` | 1 | 2023-06-05 | 2023-06-05 |
| `chest fly. cables.` | 1 | 2024-05-13 | 2024-05-13 |
| `chest fly. jeff nippard.` | 1 | 2025-10-16 | 2025-10-16 |
| `chest flys.` | 3 | 2025-12-18 | 2026-03-05 |
| `chest flys. bench.` | 5 | 2025-08-30 | 2025-10-25 |
| `chest flys. dumbbells.` | 1 | 2025-08-24 | 2025-08-24 |
| `dumbbell chest fly.` | 1 | 2025-04-15 | 2025-04-15 |

### Group P6 — 100 total appearances
> **Taxonomy note:** Three separate root nodes merged here — split after dedup: **dips** (`dips.` 51×; `back dips.` 3× is lower-back hypers on a dip machine, not tricep dips — rename to avoid confusion), **back extensions** (`back extensions.` 4×), and **leg extensions** (`leg extensions.` 17×). `lower back dips.` / `lower back machine.` / `back dips.` all refer to the back extension movement and should unify under one root.

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Back dips` | 3 | 2023-03-17 | 2023-09-12 |
| `Back dips.` | 2 | 2024-02-15 | 2024-03-21 |
| `Back dips. Height. 4.` | 1 | 2023-12-03 | 2023-12-03 |
| `Leg extension` | 2 | 2023-07-16 | 2023-08-05 |
| `Leg extensions` | 1 | 2024-02-13 | 2024-02-13 |
| `Lower back` | 1 | 2023-05-10 | 2023-05-10 |
| `Lower back dips.` | 1 | 2024-02-04 | 2024-02-04 |
| `Lower back standing dips.` | 1 | 2024-01-15 | 2024-01-15 |
| `assisted dips.` | 3 | 2024-07-02 | 2024-09-14 |
| `back dips.` | 3 | 2024-10-13 | 2026-01-29 |
| `back extensions.` | 4 | 2025-09-17 | 2025-09-24 |
| `back extensions. no seatbelt.` | 1 | 2025-11-19 | 2025-11-19 |
| `dips.` | 51 | 2023-07-30 | 2026-04-16 |
| `leg extension.` | 1 | 2025-11-23 | 2025-11-23 |
| `leg extension. right only.` | 1 | 2024-07-27 | 2024-07-27 |
| `leg extensions` | 1 | 2024-08-01 | 2024-08-01 |
| `leg extensions.` | 17 | 2023-07-07 | 2026-02-05 |
| `low back dips.` | 1 | 2025-02-01 | 2025-02-01 |
| `lower back dips.` | 3 | 2023-06-30 | 2026-01-22 |
| `lower back machine.` | 1 | 2025-10-20 | 2025-10-20 |
| `lower back machine. back extensions.` | 1 | 2025-09-15 | 2025-09-15 |

### Group P7 — 99 total appearances
> **Taxonomy note:** Root = **calves**. `calf calves.` is a redundant double-naming — canonical should be `calves.`. Clear Level 2 split: `calves. seated.` (38×+4×, soleus-dominant) and `calves. standing.` (10×+1×+7×, gastrocnemius-dominant) — these target different muscles and should be tracked separately.

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Calf` | 1 | 2023-06-24 | 2023-06-24 |
| `Calf calves.` | 3 | 2024-02-25 | 2024-04-27 |
| `Calf machine.` | 1 | 2024-01-15 | 2024-01-15 |
| `Calf raises` | 1 | 2023-06-11 | 2023-06-11 |
| `Calf. Calves.` | 1 | 2024-03-03 | 2024-03-03 |
| `Seated calf calves.` | 1 | 2024-02-04 | 2024-02-04 |
| `calf calves.` | 32 | 2023-11-08 | 2026-01-25 |
| `calf calves. seated.` | 38 | 2023-04-26 | 2026-04-16 |
| `calf calves. seated. rainbow.` | 2 | 2026-01-30 | 2026-02-04 |
| `calf calves. standing.` | 10 | 2023-03-08 | 2026-01-27 |
| `calf extension machine.` | 1 | 2025-06-27 | 2025-06-27 |
| `calf. calves.` | 1 | 2025-02-08 | 2025-02-08 |
| `seated calf calves.` | 4 | 2024-08-05 | 2025-09-17 |
| `seated calf machine.` | 2 | 2024-10-01 | 2024-10-13 |
| `standing calf calves.` | 1 | 2025-08-12 | 2025-08-12 |

### Group P8 — 95 total appearances
> **Taxonomy note:** Root = **bench press**. `bench.` (44×) is the canonical flat bench. `incline bench.` (14×) is a well-established Level 2 node. `iso lateral bench.` / `isolateral bench.` (3×+3×+2×) is a distinct machine movement — keep as Level 2. `bench smith.` / `Bench press. Smith.` — smith machine is a meaningful qualifier, keep as Level 3 under flat bench.

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Bench` | 5 | 2024-02-04 | 2024-03-10 |
| `Bench press. Smith.` | 1 | 2025-11-26 | 2025-11-26 |
| `Bench.` | 1 | 2024-04-27 | 2024-04-27 |
| `Incline bench 45.` | 1 | 2024-01-30 | 2024-01-30 |
| `Incline bench. (Last time in July 35).` | 1 | 2023-10-26 | 2023-10-26 |
| `Incline bench. 45.` | 1 | 2024-01-25 | 2024-01-25 |
| `bench` | 6 | 2024-06-04 | 2025-02-08 |
| `bench press. dumbbells.` | 2 | 2025-11-25 | 2025-12-11 |
| `bench smith.` | 1 | 2024-12-03 | 2024-12-03 |
| `bench.` | 44 | 2023-04-03 | 2026-04-04 |
| `bench. home.` | 1 | 2024-12-22 | 2024-12-22 |
| `incline bench machine.` | 1 | 2025-04-05 | 2025-04-05 |
| `incline bench.` | 14 | 2024-05-23 | 2024-12-15 |
| `incline bench. dumbbells.` | 2 | 2025-08-24 | 2025-12-31 |
| `iso lateral bench press.` | 1 | 2024-10-09 | 2024-10-09 |
| `iso lateral bench.` | 2 | 2025-03-09 | 2025-03-27 |
| `iso lateral bench. right only.` | 1 | 2025-03-07 | 2025-03-07 |
| `iso lateral bench. right only. seat 6.` | 1 | 2025-02-20 | 2025-02-20 |
| `iso lateral incline bench. right only.` | 1 | 2025-02-15 | 2025-02-15 |
| `iso lateral. bench.` | 1 | 2025-04-22 | 2025-04-22 |
| `isolateral bench press.` | 3 | 2025-05-22 | 2025-06-03 |
| `isolateral bench.` | 3 | 2025-03-29 | 2025-04-30 |
| `preacher single bench.` | 1 | 2024-04-16 | 2024-04-16 |

### Group P9 — 77 total appearances
> **Taxonomy note:** Root = **lat pull-down**. `lat pull-down.` (53×) is canonical. `lat pull-downs.` is a spelling variant — consolidate. `iso lateral front lat pull-down.` (1×) is a distinct unilateral machine — keep as Level 2. `last pulldown.` is a typo of `lat pulldown.`. Grip variants (`diamond grip`, `cbum grip`) are Level 3 qualifiers worth keeping if you track them consistently.

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Lat pull-down` | 1 | 2024-02-06 | 2024-02-06 |
| `Lat pull-down 160` | 1 | 2024-02-04 | 2024-02-04 |
| `Lat pull-down machine.` | 4 | 2023-10-05 | 2024-03-21 |
| `Lat pull-down.` | 2 | 2024-02-25 | 2024-03-03 |
| `iso lateral front lat pull-down.` | 1 | 2024-08-01 | 2024-08-01 |
| `iso lateral front lat pull-down. right only.` | 1 | 2025-02-20 | 2025-02-20 |
| `last pulldown.` | 1 | 2025-08-22 | 2025-08-22 |
| `lat pull-down` | 2 | 2024-06-09 | 2025-07-22 |
| `lat pull-down diamond grip.` | 1 | 2024-11-28 | 2024-11-28 |
| `lat pull-down machine.` | 1 | 2024-06-27 | 2024-06-27 |
| `lat pull-down.` | 53 | 2023-03-17 | 2026-03-01 |
| `lat pull-down. (hoist and weird)` | 1 | 2025-01-28 | 2025-01-28 |
| `lat pull-down. cbum grip.` | 2 | 2026-04-05 | 2026-04-16 |
| `lat pull-down. machine.` | 1 | 2023-06-30 | 2023-06-30 |
| `lat pull-downs.` | 2 | 2025-08-06 | 2025-11-24 |
| `lat pulldown` | 1 | 2024-10-19 | 2024-10-19 |
| `lat pulldown.` | 2 | 2024-07-02 | 2025-08-23 |

### Group P10 — 61 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Fore arms` | 1 | 2023-07-18 | 2023-07-18 |
| `Forearms curls. 45.` | 1 | 2024-01-30 | 2024-01-30 |
| `Forearms.` | 1 | 2024-01-28 | 2024-01-28 |
| `forearms` | 1 | 2024-05-23 | 2024-05-23 |
| `forearms.` | 54 | 2023-05-10 | 2026-02-26 |
| `forearms. barbell.` | 2 | 2026-02-22 | 2026-02-23 |
| `forearms. right only.` | 1 | 2025-02-15 | 2025-02-15 |

### Group P11 — 38 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `ISO decline press.` | 1 | 2024-02-13 | 2024-02-13 |
| `Leg press` | 4 | 2023-03-08 | 2023-08-24 |
| `Leg press. 4.` | 1 | 2023-06-16 | 2023-06-16 |
| `Leg press. Seat distance 4. Too close hip cramps.` | 1 | 2024-02-01 | 2024-02-01 |
| `Overhead press` | 1 | 2023-07-18 | 2023-07-18 |
| `Overhead press. Seat at level 5` | 1 | 2023-06-13 | 2023-06-13 |
| `leg press.` | 5 | 2025-09-28 | 2026-04-16 |
| `overhead press machine.` | 1 | 2025-11-18 | 2025-11-18 |
| `overhead press.` | 4 | 2025-10-15 | 2025-12-10 |
| `seated leg press.` | 15 | 2025-09-24 | 2026-04-05 |
| `seated leg press. inside machine.` | 2 | 2025-10-18 | 2025-10-20 |
| `seated leg press. outside machine.` | 1 | 2025-10-27 | 2025-10-27 |
| `seated leg press. seat all the way back. 3.` | 1 | 2025-01-18 | 2025-01-18 |

### Group P12 — 33 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Lat raise` | 3 | 2023-03-17 | 2023-07-07 |
| `lat raises.` | 29 | 2025-08-28 | 2026-04-08 |
| `lat raises. stretch in between.` | 1 | 2026-03-05 | 2026-03-05 |

### Group P13 — 27 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `seated pec dec.` | 25 | 2023-08-09 | 2025-11-16 |
| `seated pec dec. seat 2.5.` | 1 | 2025-07-03 | 2025-07-03 |
| `seated pec dec. seat. 1.5.` | 1 | 2025-06-10 | 2025-06-10 |

### Group P14 — 19 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Calves 40` | 1 | 2024-01-03 | 2024-01-03 |
| `Standing calves` | 1 | 2024-02-01 | 2024-02-01 |
| `Standing calves. 6 holes. Usually 5.` | 1 | 2024-02-11 | 2024-02-11 |
| `Standing calves. Height 6 holes.` | 1 | 2024-02-13 | 2024-02-13 |
| `calves.` | 4 | 2024-10-20 | 2026-03-25 |
| `seated calves` | 1 | 2024-06-04 | 2024-06-04 |
| `seated calves.` | 3 | 2024-07-20 | 2024-10-09 |
| `standing calves.` | 7 | 2024-09-14 | 2025-03-11 |

### Group P15 — 19 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Sit-ups` | 2 | 2024-01-09 | 2024-05-13 |
| `Sit-ups 10` | 1 | 2024-01-30 | 2024-01-30 |
| `Sit-ups full.` | 1 | 2024-05-05 | 2024-05-05 |
| `sit-ups` | 2 | 2024-05-15 | 2024-08-10 |
| `sit-ups.` | 13 | 2024-05-23 | 2026-03-05 |

### Group P16 — 19 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Forearm curls` | 3 | 2023-07-27 | 2024-01-25 |
| `Forearm curls.` | 9 | 2024-01-15 | 2024-05-10 |
| `forearm curl.` | 1 | 2024-07-05 | 2024-07-05 |
| `forearm curls.` | 6 | 2024-05-26 | 2024-08-02 |

### Group P17 — 18 total appearances
> **Taxonomy note:** Multiple root nodes merged — split after dedup: **cable rows** (seated, `cable rows.` 7×+2×), **low rows** (`Low rows` 1× — same as seated cable rows, consolidate), **standing rows** (`Standing rows` 1×, `rows. standing barbell.` 2×). These are distinct movements (seated pull vs. standing pull) and should be separate roots.

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Cable rows.` | 2 | 2024-03-10 | 2024-03-21 |
| `Low rows` | 1 | 2023-07-30 | 2023-07-30 |
| `Seated Low rows` | 1 | 2023-08-07 | 2023-08-07 |
| `Standing rows` | 1 | 2023-07-29 | 2023-07-29 |
| `Standing rows dumbbells` | 1 | 2023-09-10 | 2023-09-10 |
| `cable low rows.` | 1 | 2024-08-30 | 2024-08-30 |
| `cable rows.` | 7 | 2024-06-09 | 2025-05-20 |
| `low cable rows.` | 1 | 2025-06-24 | 2025-06-24 |
| `low rows. cable.` | 1 | 2026-01-04 | 2026-01-04 |
| `rows. standing barbell.` | 2 | 2026-03-26 | 2026-04-05 |

### Group P18 — 13 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Squats 30 total.` | 1 | 2024-01-09 | 2024-01-09 |
| `Squats.` | 1 | 2024-02-01 | 2024-02-01 |
| `squats.` | 10 | 2023-09-08 | 2026-02-02 |
| `squats. dumbbells.` | 1 | 2025-12-31 | 2025-12-31 |

### Group P19 — 11 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Side planks` | 1 | 2024-05-07 | 2024-05-07 |
| `Side planks.` | 3 | 2024-05-02 | 2024-05-13 |
| `side plank` | 1 | 2024-05-23 | 2024-05-23 |
| `side plank.` | 1 | 2024-08-06 | 2024-08-06 |
| `side plank. left only.` | 1 | 2024-08-10 | 2024-08-10 |
| `side planks` | 2 | 2024-05-15 | 2024-06-17 |
| `side planks.` | 2 | 2024-05-21 | 2024-07-14 |

### Group P20 — 7 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Low pull` | 3 | 2023-04-04 | 2023-07-14 |
| `Low pulls` | 2 | 2023-04-17 | 2023-04-20 |
| `low pull.` | 1 | 2023-04-03 | 2023-04-03 |
| `pull machine.` | 1 | 2026-03-25 | 2026-03-25 |

### Group P21 — 7 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `deadlift` | 1 | 2024-08-24 | 2024-08-24 |
| `deadlift bars.` | 1 | 2026-01-25 | 2026-01-25 |
| `deadlift.` | 3 | 2025-05-22 | 2025-09-28 |
| `deadlift. cables.` | 1 | 2025-11-29 | 2025-11-29 |
| `deadlifts.` | 1 | 2026-02-24 | 2026-02-24 |

### Group P22 — 5 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Face pull.` | 1 | 2023-09-08 | 2023-09-08 |
| `Face pulls` | 1 | 2023-08-07 | 2023-08-07 |
| `Face pulls.` | 1 | 2024-01-05 | 2024-01-05 |
| `Face pulls. Stagger stance. Height 3.` | 1 | 2024-01-15 | 2024-01-15 |
| `face pulls. rope.` | 1 | 2026-01-03 | 2026-01-03 |

### Group P23 — 5 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `jeff nippard lat raises.` | 1 | 2025-10-15 | 2025-10-15 |
| `jeff nippard lat raises. right only.` | 1 | 2025-09-19 | 2025-09-19 |
| `jeff nippard. lat raises.` | 3 | 2025-08-27 | 2025-10-03 |

### Group P24 — 4 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Flutter` | 1 | 2024-05-07 | 2024-05-07 |
| `Flutter kicks` | 2 | 2024-05-02 | 2024-05-13 |
| `Flutter kicks.` | 1 | 2024-05-05 | 2024-05-05 |

### Group P25 — 4 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Leg curl` | 2 | 2023-07-16 | 2023-08-05 |
| `leg curl.` | 1 | 2025-04-05 | 2025-04-05 |
| `seated leg curl.` | 1 | 2026-01-30 | 2026-01-30 |

### Group P26 — 4 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Hammer` | 1 | 2023-08-11 | 2023-08-11 |
| `Hammer curls` | 1 | 2023-08-05 | 2023-08-05 |
| `Hammer curls. 2 reps` | 1 | 2023-06-11 | 2023-06-11 |
| `arm curls.` | 1 | 2025-08-22 | 2025-08-22 |

### Group P27 — 3 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `rear delt machine.` | 1 | 2023-11-30 | 2023-11-30 |
| `rear delt.` | 1 | 2026-01-04 | 2026-01-04 |
| `rear delts.` | 1 | 2024-08-30 | 2024-08-30 |

### Group P28 — 3 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `pushups` | 1 | 2024-07-11 | 2024-07-11 |
| `pushups.` | 1 | 2024-08-25 | 2024-08-25 |
| `pushups. wide. rice.` | 1 | 2024-11-07 | 2024-11-07 |

### Group P29 — 2 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `galileo leg press.` | 1 | 2026-04-05 | 2026-04-05 |
| `galileo leg press. basically pilates.` | 1 | 2026-01-22 | 2026-01-22 |

### Group P30 — 2 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Chin up.` | 1 | 2024-05-10 | 2024-05-10 |
| `chin up 2.` | 1 | 2024-05-13 | 2024-05-13 |

### Group P31 — 2 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Low row.` | 1 | 2023-03-08 | 2023-03-08 |
| `low row cable. dead lift.` | 1 | 2025-11-28 | 2025-11-28 |

### Group P32 — 2 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `bayesian curls.` | 1 | 2026-01-03 | 2026-01-03 |
| `bayesian curls. right only.` | 1 | 2025-04-09 | 2025-04-09 |

### Group P33 — 2 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Sit ups` | 1 | 2024-05-07 | 2024-05-07 |
| `Sit ups. 10.` | 1 | 2024-01-25 | 2024-01-25 |

## Fuzzy / Root Matches

*Names share the same root or have high edit-distance similarity — possible typo or inconsistent naming.*

### Group F1 — 2 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Prone leg curl.` | 1 | 2023-09-14 | 2023-09-14 |
| `Prone leg curls` | 1 | 2023-08-11 | 2023-08-11 |

### Group F2 — 2 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Hamstring` | 1 | 2023-06-16 | 2023-06-16 |
| `Hamstrings` | 1 | 2023-06-24 | 2023-06-24 |

## Qualifier Differences (⚠️  Possible Separate Tracking Intent)

*⚠️  Names differ only by equipment/grip qualifiers — **possible separate tracking intent**. Review carefully before merging.*

### Group Q1 — 5 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `chest press machine.` | 1 | 2025-06-27 | 2025-06-27 |
| `chest press.` | 3 | 2025-08-22 | 2025-08-28 |
| `incline chest press.` | 1 | 2024-07-14 | 2024-07-14 |

### Group Q2 — 3 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Standing Pull-down` | 1 | 2023-04-05 | 2023-04-05 |
| `Standing back pull-down` | 2 | 2023-04-07 | 2023-04-11 |

### Group Q3 — 3 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Bent over cable rows` | 1 | 2023-11-08 | 2023-11-08 |
| `Standing bent over dumbbell rows back` | 1 | 2023-10-31 | 2023-10-31 |
| `standing bent over rows.` | 1 | 2024-08-24 | 2024-08-24 |

### Group Q4 — 2 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Bent forward dumbbell rows` | 1 | 2023-06-11 | 2023-06-11 |
| `back. bent forward T rows.` | 1 | 2026-01-03 | 2026-01-03 |

### Group Q5 — 2 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Seated chest machine` | 1 | 2023-12-28 | 2023-12-28 |
| `chest. wide machine.` | 1 | 2025-08-18 | 2025-08-18 |

### Group Q6 — 2 total appearances

| Exercise Name | Count | First Seen | Last Seen |
|---|---|---|---|
| `Pull up.` | 1 | 2024-05-10 | 2024-05-10 |
| `Wide pull up.` | 1 | 2024-05-10 | 2024-05-10 |

---

## How to Use This Report

1. **Exact matches**: These are the lowest-hanging fruit — safe to consolidate in your JSON.
2. **Prefix matches**: Check whether the shorter name is a general category or a specific exercise.
3. **Fuzzy matches**: These may be typos or genuinely different exercises with similar names.
4. **Qualifier differences** (⚠️ ): These require the most care — different equipment or grip often means different muscle activation and separate progress tracking is valuable.

Re-run this script after any consolidation: `python scripts/find_duplicate_exercises.py`
