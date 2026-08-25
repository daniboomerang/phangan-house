"""Place a parametric house on a site and report levels, cuts, posts, compliance.

    python scripts/fit_house.py --site data/site.json --house data/house.json \
        --centre-e 609438 --centre-n 1077930 --bearing 274

Change --centre-e/--centre-n/--bearing to move the house, or point --site at a
different survey to move to different land entirely.
"""
import argparse, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from site_model import Site


def run(site_json, house_json, ce, cn, bearing, max_cut=1.00, height_limit=6.0):
    root = os.path.dirname(os.path.dirname(os.path.abspath(site_json)))
    S = Site(os.path.join(root, json.load(open(site_json))["survey"]["file"]), site_json)
    H = json.load(open(house_json))
    D = H["footprint"]["depth_m"]; W = H["footprint"]["width_m"]
    sa, ca = math.sin(math.radians(bearing)), math.cos(math.radians(bearing))
    sp, cp = math.sin(math.radians(bearing + 90)), math.cos(math.radians(bearing + 90))
    def EN(a, b):                       # house coords -> easting/northing
        return ce + a * sa + b * sp, cn + a * ca + b * cp
    def g(a, b):
        return S.z(*EN(a, b))
    def band_ground(d0, d1, w0, w1, step=0.4):
        zs = [g(a - D / 2, b - W / 2)
              for a in np.arange(d0, d1 + .01, step)
              for b in np.arange(w0, w1 + .01, step)]
        zs = [z for z in zs if not math.isnan(z)]
        return (min(zs), max(zs)) if zs else (float("nan"),) * 2

    out = {"centre": [ce, cn], "bearing_deg": bearing, "benches": []}
    for band in H["grid"]["depth_bands"]:
        d0, d1 = band["from"], band["to"]
        lo, hi = band_ground(d0, d1, 0, W)
        floor = round(hi - max_cut, 2)
        row = {"band": band["name"], "depth_m": [d0, d1], "floor": floor,
               "ground": [round(lo, 2), round(hi, 2)],
               "cut": round(hi - floor, 2), "post": round(max(0, floor - lo), 2),
               "arms": {}}
        for arm, w0, w1 in (("left", 0, 4), ("right", W - 4, W)):
            alo, ahi = band_ground(d0, d1, w0, w1)
            row["arms"][arm] = {"ground": [round(alo, 2), round(ahi, 2)],
                                "envelope": round(alo + height_limit, 2),
                                "headroom_above_floor": round(alo + height_limit - floor, 2)}
        out["benches"].append(row)
    steps = [round(out["benches"][i]["floor"] - out["benches"][i + 1]["floor"], 2)
             for i in range(len(out["benches"]) - 1)]
    out["floor_steps"] = steps
    out["legal"] = {"max_cut_ok": all(b["cut"] <= max_cut + 0.005 for b in out["benches"]),
                    "cuts": [b["cut"] for b in out["benches"]]}
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--site", default="data/site.json")
    p.add_argument("--house", default="data/house.json")
    p.add_argument("--centre-e", type=float, required=True)
    p.add_argument("--centre-n", type=float, required=True)
    p.add_argument("--bearing", type=float, default=274.0)
    p.add_argument("--max-cut", type=float, default=1.00)
    p.add_argument("--height-limit", type=float, default=6.0)
    a = p.parse_args()
    r = run(a.site, a.house, a.centre_e, a.centre_n, a.bearing, a.max_cut, a.height_limit)
    print(json.dumps(r, indent=1))
