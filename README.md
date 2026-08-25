# land-project

A hillside house on Koh Phangan, built from measured data rather than assumption.

A 1,000 m² leasehold plot at 80–96 m above sea level, falling 16.27 m at a mean
slope of 38.9%, inside a 59-rai parcel belonging to the lessor. Three buildings:
a **family house**, a **shala**, and a **studio house**.

## Layout

```
skills/       three Claude skills — land, buildings, Thai law
land/         survey points, boundaries, terrain, rock, tenure, coordinates
buildings/    family house, shala, studio house
scripts/      site model, pad finder, house fitter, 3D generator
designs/      Ana's professional files land here
docs/         index.html — published by GitHub Pages
reports/      plans, sections, site plan
```

**`land/` and `buildings/` are separate on purpose.** The design carries no
coordinates; the land carries no design. Move to a different parcel and only
`land/` changes.

## Quick start

```bash
pip install numpy scipy shapely pyproj

python scripts/find_pad.py --site land/site.json --width 14 --depth 14 \
       --bearings 250,262,274,286
python scripts/fit_house.py --site land/site.json --house buildings/family-house.json \
       --centre-e 609443.5 --centre-n 1077930.0 --bearing 274
python scripts/make_3d.py --site land/site.json --house buildings/family-house.json \
       --out docs/index.html
```

## Where it stands

| | |
|---|---|
| Survey | KC V2, September 2025, 71 points, 0.25 m contours |
| Covers | about 52 × 35 m only — outside that is extrapolation |
| Plot vs landlord parcel | **86.6% inside**; 134.2 m² out, P8 by 10.36 m |
| Family house | designed in full, but **136 m² coverage against a 90 m² cap** |
| Shala, studio house | sited, no earthworks, posts only |

## The three questions that decide everything

1. **How is the 6 m measured on a slope?** Per point, mean, or constructed
   level. Worth about 2 m of ceiling height.
2. **How many detached buildings are permitted on one plot?** บ้านเดี่ยว reads
   as a building *type*, not a count — but unconfirmed. Worth 90 m² of footprint
   per extra building.
3. **Does the Sor Kor 1 satisfy the pre-2014 possession gate?** If not, nothing
   else matters.

Wording to put to the OrBorTor is in `skills/thai-hillside-law/references/`.

## Before anything else

**KC must extend the survey 20–25 m north-east.** Every candidate re-negotiated
boundary is only 28–37% covered by the current survey. No corners can be agreed
on unmeasured ground.
