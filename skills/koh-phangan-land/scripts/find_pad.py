"""Search a site for the flattest place to put a footprint of a given size.

    python scripts/find_pad.py --site data/site.json --width 14 --depth 14
"""
import argparse, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from site_model import Site, boundary, point_in


def search(site_json, W, D, bearings, max_slope=50.0, step=1.0):
    root = os.path.dirname(os.path.dirname(os.path.abspath(site_json)))
    meta = json.load(open(site_json))
    S = Site(os.path.join(root, meta["survey"]["file"]), site_json)
    poly = boundary(site_json)
    es = [p[0] for p in poly]; ns = [p[1] for p in poly]
    out = []
    for br in bearings:
        sa, ca = math.sin(math.radians(br)), math.cos(math.radians(br))
        sp, cp = math.sin(math.radians(br + 90)), math.cos(math.radians(br + 90))
        for ce in np.arange(min(es), max(es), step):
            for cn in np.arange(min(ns), max(ns), step):
                pts = [(ce + a * sa + b * sp, cn + a * ca + b * cp)
                       for a in (-D/2, D/2) for b in (-W/2, W/2)]
                if not all(point_in(e, n, poly) for e, n in pts):
                    continue
                gr = [(ce + a * sa + b * sp, cn + a * ca + b * cp)
                      for a in np.linspace(-D/2, D/2, 9) for b in np.linspace(-W/2, W/2, 9)]
                zs = [S.z(e, n) for e, n in gr]
                if any(math.isnan(z) for z in zs):
                    continue
                sl = max(S.slope_pct(e, n) for e, n in gr[::7])
                if math.isnan(sl) or sl > max_slope:
                    continue
                out.append({"bearing": br, "e": round(ce, 1), "n": round(cn, 1),
                            "fall": round(max(zs) - min(zs), 2),
                            "mean_elev": round(float(np.mean(zs)), 2),
                            "max_slope_pct": round(sl, 1)})
    out.sort(key=lambda r: r["fall"])
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--site", default="data/site.json")
    p.add_argument("--width", type=float, required=True)
    p.add_argument("--depth", type=float, required=True)
    p.add_argument("--bearings", default="274")
    p.add_argument("--top", type=int, default=8)
    a = p.parse_args()
    brs = [float(x) for x in a.bearings.split(",")]
    for r in search(a.site, a.width, a.depth, brs)[:a.top]:
        print(json.dumps(r))
