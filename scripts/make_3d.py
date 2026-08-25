"""Generate the interactive 3D model from data/site.json + data/house.json.

    python scripts/make_3d.py --centre-e 609443 --centre-n 1077930.6 --bearing 274 \
        --out house-3d.html

Everything is derived. Change the site file to move to other land, change the
house file to change the design, and rerun. Nothing is hard-coded here.
"""
import argparse, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from site_model import Site, boundary, point_in

CX, CY, Z0 = 22.0, 13.0, 88.0          # scene origin, metres


def build(site_json, house_json, ce, cn, bearing, out_path,
          max_cut=1.00, limit=6.0, grid_nu=132, grid_nv=80):
    root = os.path.dirname(os.path.dirname(os.path.abspath(site_json)))
    meta = json.load(open(site_json))
    S = Site(os.path.join(root, meta["survey"]["file"]), site_json)
    H = json.load(open(house_json))
    D = H["footprint"]["depth_m"]; W = H["footprint"]["width_m"]
    RF = H["roof"]["thickness_m"]; EAVE = H["roof"]["eaves_m"]
    SF = H["second_floor"]; UP = SF["ceiling_m"]; SLAB = SF["slab_m"]
    GFU = SF["ground_ceiling_under_m"]
    bands = H["grid"]["depth_bands"]
    ARM = H["grid"]["width_bands"][0]["to"]          # arm width, 4 m
    COURT = (ARM, W - ARM)

    sa, ca = math.sin(math.radians(bearing)), math.cos(math.radians(bearing))
    sp, cp = math.sin(math.radians(bearing + 90)), math.cos(math.radians(bearing + 90))
    # house coords: d 0..D from the road, w 0..W across. centre at (ce,cn).
    def EN(d, w):
        a = d - D / 2; b = w - W / 2
        return ce + a * sa + b * sp, cn + a * ca + b * cp
    def g(d, w):
        return S.z(*EN(d, w))
    def rng(d0, d1, w0, w1, step=0.4):
        zs = [g(d, w) for d in np.arange(d0, d1 + .01, step)
                      for w in np.arange(w0, w1 + .01, step)]
        zs = [z for z in zs if not math.isnan(z)]
        return (min(zs), max(zs)) if zs else (float("nan"),) * 2
    def uv(d, w):
        e, n = EN(d, w)
        du, dv = e - meta["boundary"]["markers"][0]["easting"], n - meta["boundary"]["markers"][0]["northing"]
        bu = math.radians(289.87); bv = math.radians(199.87)
        return (du * math.sin(bu) + dv * math.cos(bu), du * math.sin(bv) + dv * math.cos(bv))
    def q(d0, d1, w0, w1, e=0.0):
        return [uv(d0 - e, w0 - e), uv(d1 + e, w0 - e), uv(d1 + e, w1 + e), uv(d0 - e, w1 + e)]

    # ---- levels ----
    floors, info = [], []
    for b in bands:
        lo, hi = rng(b["from"], b["to"], 0, W)
        floors.append(round(hi - max_cut, 2))
        info.append((b, lo, hi))
    sf_level = [round(f + GFU + SLAB, 2) for f in floors]
    TERR = sf_level[1]

    vols, eaves = [], []
    def add(d0, d1, w0, w1, z0, z1, kind, eave=False):
        vols.append({"q": q(d0, d1, w0, w1), "z0": round(z0, 2), "z1": round(z1, 2), "k": kind})
        if eave:
            eaves.append({"q": q(d0, d1, w0, w1, EAVE), "z0": round(z1 - 0.22, 2), "z1": round(z1, 2)})
    left_ch = []
    for i, (b, lo, hi) in enumerate(info):
        alo, _ = rng(b["from"], b["to"], 0, ARM)
        ch = round(alo + limit - floors[i] - RF, 2)
        left_ch.append(ch)
        add(b["from"], b["to"], 0, ARM, floors[i], floors[i] + ch + RF, "mass", True)
    for i, (b, lo, hi) in enumerate(info):
        if i < len(bands) - 1:
            add(b["from"], b["to"], W - ARM, W, floors[i], sf_level[i] + UP + RF, "mass", True)
        else:
            add(b["from"], b["to"], W - ARM, W, floors[i], TERR + SLAB, "mass")
            vols.append({"q": q(b["from"], b["to"], W - ARM, W, 0.15),
                         "z0": round(TERR + SLAB, 2), "z1": round(TERR + 1.15, 2), "k": "rail"})
    b0 = bands[0]
    add(b0["from"], b0["to"], ARM, W - ARM, floors[0], sf_level[0] + UP + RF, "mass", True)

    # ---- terrain, cut flat under the footprint and courtyard ----
    poly = boundary(site_json)
    es = [p[0] for p in poly]; ns = [p[1] for p in poly]
    def platform_at(e, n):
        de, dn = e - ce, n - cn
        d = de * sa + dn * ca + D / 2
        w = de * sp + dn * cp + W / 2
        if not (-0.15 <= d <= D + 0.15 and -0.15 <= w <= W + 0.15):
            return None
        for i, b in enumerate(bands):
            if d <= b["to"] + 0.001:
                return floors[i]
        return floors[-1]
    du, dv = 44.0 / grid_nu, 26.0 / grid_nv
    p5 = meta["boundary"]["markers"][0]
    bu, bv = math.radians(289.87), math.radians(199.87)
    def UVtoEN(u, v):
        return (p5["easting"] + u * math.sin(bu) + v * math.sin(bv),
                p5["northing"] + u * math.cos(bu) + v * math.cos(bv))
    grid = []
    for j in range(grid_nv + 1):
        row = []
        for i in range(grid_nu + 1):
            e, n = UVtoEN(i * du, j * dv)
            z = S.z(e, n)
            if math.isnan(z): row.append(None); continue
            pf = platform_at(e, n)
            row.append(round(pf if pf is not None else z, 2))
        grid.append(row)

    # ---- yard paving and stairs, against the walls only ----
    PW = 1.2
    path, steps = [], []
    def pave(d0, d1, w0, w1, z):
        path.append({"q": q(d0, d1, w0, w1), "z0": round(z - 0.07, 2), "z1": round(z + 0.02, 2)})
    def stair(d0, d1, w0, w1, zhi, zlo, n):
        rise = (zhi - zlo) / n
        for k in range(n):
            z = zlo + rise * (k + 1)
            t0 = d1 - (d1 - d0) * (k + 1) / n; t1 = d1 - (d1 - d0) * k / n
            steps.append({"q": q(t0, t1, w0, w1), "z0": round(z - 0.9, 2), "z1": round(z, 2)})
    b1, b2 = bands[1], bands[2]
    pave(b0["to"] - PW, b0["to"], COURT[0], COURT[1], floors[0])
    for w0, w1 in ((COURT[0], COURT[0] + PW), (COURT[1] - PW, COURT[1])):
        pave(b1["from"] + 0.9, b1["to"], w0, w1, floors[1])
        pave(b2["from"] + 0.8, b2["to"], w0, w1, floors[2])
        stair(b0["to"], b1["from"] + 0.9, w0, w1, floors[0], floors[1], 5)
        stair(b2["from"], b2["from"] + 0.8, w0, w1, floors[1], floors[2], 5)
    pave(D - 0.6, D, COURT[0] + PW, COURT[1] - PW, floors[2])

    # ---- openings ----
    T = 0.14
    def panD(d, w0, w1, z0, z1, o):
        e = o * T / 2
        return {"q": [uv(d + e - T / 2, w0), uv(d + e + T / 2, w0),
                      uv(d + e + T / 2, w1), uv(d + e - T / 2, w1)],
                "z0": round(z0, 2), "z1": round(z1, 2)}
    def panW(w, d0, d1, z0, z1, o):
        e = o * T / 2
        return {"q": [uv(d0, w + e - T / 2), uv(d0, w + e + T / 2),
                      uv(d1, w + e + T / 2), uv(d1, w + e - T / 2)],
                "z0": round(z0, 2), "z1": round(z1, 2)}
    glass, doors = [], []
    glass.append(panD(b0["to"], COURT[0] + 0.15, COURT[1] - 0.15, floors[0] + 0.05, floors[0] + 2.45, +1))
    glass.append(panD(b0["to"], COURT[0] + 0.15, COURT[1] - 0.15, sf_level[0] + 0.05, sf_level[0] + UP - 0.15, +1))
    glass.append(panD(b2["from"], W - ARM + 0.25, W - 0.25, TERR + 0.05, TERR + UP - 0.15, +1))
    for w, o in ((COURT[0], -1), (COURT[1], +1)):
        glass.append(panW(w, b1["from"] + 0.8, b1["to"] - 0.8, floors[1] + 1.45, floors[1] + 2.45, o))
        doors.append(panW(w, b2["from"] + 1.0, b2["from"] + 2.2, floors[2] + 0.02, floors[2] + 2.30, o))
        glass.append(panW(w, b2["from"] + 2.6, b2["to"] - 0.5, floors[2] + 1.10, floors[2] + 2.45, o))
    glass.append(panD(D, 0.4, ARM - 0.6, floors[2] + 0.85, floors[2] + left_ch[2] - 0.9, +1))
    glass.append(panD(D, W - ARM + 0.4, W - 0.6, floors[2] + 0.85, floors[2] + 2.55, +1))
    doors.append(panD(0, W - ARM + 0.25, W - ARM + 1.35, floors[0], floors[0] + 2.30, -1))
    # portholes
    def wxz(d, w):
        u, v = uv(d, w); return (CX - u, v - CY)
    o0 = np.array(wxz(0, 0)); dd = np.array(wxz(1, 0)) - o0; dw = np.array(wxz(0, 1)) - o0
    dd /= np.linalg.norm(dd); dw /= np.linalg.norm(dw)
    rounds = []
    def rd(d, w, z, r, nvec):
        x, zz = wxz(d, w)
        rounds.append({"x": round(x, 3), "z": round(zz, 3), "y": round(z, 2), "r": r,
                       "phi": round(math.atan2(nvec[0], nvec[1]), 4)})
    for i, b in enumerate(bands):
        dc = (b["from"] + b["to"]) / 2
        rd(dc, -0.06, floors[i] + min(2.05, left_ch[i] / 2 + 0.4), 0.88, -dw)
        rd(dc, W + 0.06, floors[i] + 1.35, 0.80, dw)
    rd((b1["from"] + b1["to"]) / 2, W + 0.06, TERR + 1.10, 0.72, dw)
    rd(-0.06, W / 2, sf_level[0] + UP / 2, 1.05, -dd)

    payload = {"grid": grid, "nu": grid_nu, "nv": grid_nv, "du": du, "dv": dv,
               "vols": vols, "eaves": eaves, "path": path, "steps": steps,
               "glass": glass, "door": doors, "rounds": rounds,
               "rock": [list(_uv_en(S, p, p5, bu, bv)) for p in S.rock()],
               "levels": {"floors": floors, "second_floor": sf_level, "terrace": TERR,
                          "left_ceilings": left_ch, "steps": [round(floors[i] - floors[i+1], 2)
                                                              for i in range(len(floors) - 1)]}}
    payload["plot"] = [list(_uv_en(S, (m["easting"], m["northing"], 0), p5, bu, bv))
                       for m in meta["boundary"]["markers"]]
    html = TEMPLATE.replace("__DATA__", json.dumps(payload))
    open(out_path, "w").write(html)
    return payload["levels"]


def _uv_en(S, p, p5, bu, bv):
    de, dn = p[0] - p5["easting"], p[1] - p5["northing"]
    return (de * math.sin(bu) + dn * math.cos(bu), de * math.sin(bv) + dn * math.cos(bv))


TEMPLATE = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "viewer.html")).read()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--site", default="data/site.json")
    p.add_argument("--house", default="data/house.json")
    p.add_argument("--centre-e", type=float, default=609443.5)
    p.add_argument("--centre-n", type=float, default=1077930.0)
    p.add_argument("--bearing", type=float, default=274.0)
    p.add_argument("--out", default="house-3d.html")
    a = p.parse_args()
    lv = build(a.site, a.house, a.centre_e, a.centre_n, a.bearing, a.out)
    print(json.dumps(lv, indent=1))
    print("wrote", a.out)
