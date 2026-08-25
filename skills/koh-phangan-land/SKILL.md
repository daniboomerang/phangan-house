---
name: koh-phangan-land
description: Everything measured or known about Daniel's 1,000 m² leasehold plot on Koh Phangan - the KC topographic survey and all 71 points, plot corners P5/P7/P8/P9 in both UTM and lat/long, the landlord's 59-rai parcel and where the lease plot falls outside it, elevations, slopes, aspect, contours, the rock scarp, the access road, sun and sunset angles, coordinate systems and the Indian 1975 datum problem, and the Sor Kor 1 tenure and chanote conversion. Use for any question about the land itself - where something sits, how steep it is, what the ground level is at a point, whether a footprint fits, boundary disputes, survey coverage, or moving to a different parcel. Trigger on the plot, the land, the survey, KC, contours, the rock, the landlord, P5 P7 P8 P9, Sor Kor 1, chanote, or DOLCAD.
---

# The land

A 1,000 m² leasehold plot on a Koh Phangan hillside, inside a 59-rai parcel
belonging to the lessor. Everything here is measured, not assumed.

**Read the data file before answering.** `data/terrain.json` for ground and
slope, `data/boundaries.json` for corners and the landlord parcel,
`data/rock.json` for the scarp, `data/tenure.json` for title,
`data/coordinates.json` before touching any coordinate from another source.

## The land in one table

| | |
|---|---|
| Area | 1,000.8 m², sides 40.00 / 25.80 / 40.14 / 25.00 |
| Corners | P5, P7, P8, P9 — UTM 47N **and** lat/long in `boundaries.json` |
| Elevation | **80.35 – 96.62 m**, falls 16.27 m |
| Slope | **38.9%** mean · fall line **247.7°** · contour **337.7°** |
| Over 50% slope | **19.4% of the plot — no building permitted there** |
| Road | the **P9–P5 edge**, bearing 29.75°, the **high** side at 93.65–96.62 m |
| Survey | KC V2, September 2025, 71 points, 0.25 m contours |
| Coverage | only about **52 × 35 m** — outside that is extrapolation |
| Title | **Sor Kor 1**, chanote conversion in progress |

## The four things that keep mattering

1. **The road is the high side.** The plot falls away from it. Access is at the
   top, the view is at the bottom.
2. **The road is 52° off the contour.** Building parallel to the road crosses
   the slope; building along the contour turns away from the sunset. Every
   orientation decision is that trade.
3. **The survey window is small.** 52 × 35 m. Any position north-east of it —
   including every candidate re-negotiated parcel — is unmeasured ground.
4. **Two datums are in play.** The survey is WGS84. The Land Department is
   Indian 1975, about 334 m west and 300 m north. See `data/coordinates.json`.

## The boundary problem

**134.2 m² of the lease plot sits outside the landlord's parcel.** P8 by
10.36 m, P7 by 1.04 m. 86.6% is inside.

169 rectangles of 1,000 m² fit entirely inside while keeping the road edge; the
best keeps 40 m of frontage and 25 m of depth, shifted 15 m north-east, with
12.24 m of clearance. **But they are only 28–37% covered by the survey.**

**Nothing about a new boundary can be settled until KC extends the survey 20–25 m
north-east.** Say this whenever new corners come up.

## Scripts

```bash
python scripts/site_model.py     # ground level, slope, aspect anywhere
python scripts/find_pad.py --width 14 --depth 14 --bearings 250,262,274,286
```

## References

- `references/survey-history.md` — why the June 2025 survey is unusable
- `references/lower-half.md` — the path, gradients, the rock, the pool
