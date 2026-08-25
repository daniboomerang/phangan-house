---
name: koh-phangan-buildings
description: The three buildings Daniel is designing for his Koh Phangan plot - the family house, the shala, and the studio house - with every dimension, level, ceiling height, opening and post height so far decided, plus his brief and the history of what was tried and rejected. Use for any question about the family house, the C-shape, the courtyard, the platform or mezzanine, the master bedroom or its dressing area, ceiling heights, the benches and floor levels, the stairs, the portholes, the sliding glass to the courtyard, the shala and its posts, or the studio house. Also use when generating plans, sections or the interactive 3D model. Trigger on family house, villa, shala, sala, studio house, courtyard, platform, master bedroom, or any request to draw or render the buildings.
---

# The three buildings

**Family house · shala · studio house.** Use those names, always. Never just
"the house" — there are three buildings and the distinction matters.

| Building | Size | Level | State |
|---|---|---|---|
| **Family house** | 14 × 14 C-shape | 93.35 / 92.47 / 91.46 | designed in full; **over the 90 m² coverage cap** |
| **Shala** | 6 × 6 on nine posts | deck 90.55 | sited, no earthworks |
| **Studio house** | 16 × 5 floating | deck 85.90 | sited, no earthworks |

**Read `references/the-brief.md` before proposing anything.** It records what
Daniel wants and what must not be traded away. **Read
`references/design-history.md`** before suggesting an approach — it lists what
was already tried and why it failed.

Land, survey and levels live in the **koh-phangan-land** skill. Limits live in
**thai-hillside-law**. This skill is the buildings only.

## Family house

`data/family-house.json`. A C wrapping a 6 × 10 courtyard that opens west, base
band along the road. Three stepped floors — **93.35, 92.47, 91.46 m**, steps
0.88 and 1.01 m, every cut at or under 1.00 m.

One arm open to its roof at **4.85 / 4.71 / 4.61 m**. The other carries the
second floor: platform, bath and dressing at 96.08; master bedroom and terrace
at 95.20; one step of 0.88 m at the bedroom door. Main stair 15 risers × 0.182,
3.64 m run.

Courtyard terraced to the room levels, **paving only against the inner walls**,
the middle planted. Both far rooms open outward onto flat ground.

**It is 136 m² of ground coverage against a 90 m² cap.** Do not present it as
buildable without saying so.

## Shala

`data/shala.json`. Nine posts, **0.35 m at the uphill corner to 3.09 m at the
downhill one**, over ground that drops 2.74 m. Deck level at 90.55.

The height limit is measured from the **low** corner, so the 3.09 m post and the
roof compete for the same 6 m. That leaves 2.91 m above the deck — a low, wide
pavilion. Which is right for it.

## Studio house

`data/studio-house.json`. **16 × 5 = 80 m², long axis on the contour**, floating
on posts of 0.30 to 1.86 m, **4.14 m of headroom**, zero earthworks.

The proportion is the whole trick. Across 5 m the ground falls 1.55 m; across a
square of the same area it falls twice that and the headroom is gone. For a
full 100 m², two decks of 10 × 5 linked by a bridge.

## Scripts

```bash
python scripts/fit_house.py --centre-e <E> --centre-n <N> --bearing <deg>
python scripts/make_3d.py --out house-3d.html
```

`make_3d.py` derives the whole model from the land data plus
`data/family-house.json`. It prints the levels it computed — check them before
trusting the picture.

## Two errors that keep recurring

- **Mirroring.** The 2D plans draw local **u leftward**. The 3D must match. If a
  model looks flipped against a plan, that mapping in `assets/viewer.html` is
  where to look.
- **Ground bleeding through a doorway.** The terrain grid must be cut flat under
  the footprint, and fine enough that the cut edge is sharp.
