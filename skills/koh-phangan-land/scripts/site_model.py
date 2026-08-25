"""Load a survey and answer questions about the ground.

Works with any site whose survey is a CSV of id,northing,easting,elev,code.
Nothing here is specific to Koh Phangan except the defaults in data/site.json.
"""
import csv, json, math
import numpy as np
from scipy.interpolate import LinearNDInterpolator


class Site:
    def __init__(self, survey_csv, site_json=None):
        pts = []
        with open(survey_csv) as f:
            for r in csv.DictReader(f):
                pts.append((float(r["easting"]), float(r["northing"]),
                            float(r["elev"]), r["code"]))
        self.points = pts
        self.meta = json.load(open(site_json)) if site_json else {}
        arr = np.array([(p[0], p[1], p[2]) for p in pts])
        self._z = LinearNDInterpolator(arr[:, :2], arr[:, 2])

    def z(self, e, n):
        """Ground level at an easting/northing. NaN outside the survey."""
        return float(self._z(e, n))

    def slope_pct(self, e, n, h=2.5):
        zs = [self.z(e - h, n), self.z(e + h, n), self.z(e, n - h), self.z(e, n + h)]
        if any(math.isnan(v) for v in zs):
            return float("nan")
        return math.hypot((zs[1] - zs[0]) / (2 * h), (zs[3] - zs[2]) / (2 * h)) * 100

    def best_fit_plane(self, poly):
        """Gradient and downhill bearing over a polygon of (e,n) corners."""
        g = [(e, n) for e, n in self._grid(poly)]
        A = np.array([[e, n, 1.0] for e, n in g])
        b = np.array([self.z(e, n) for e, n in g])
        ok = ~np.isnan(b)
        c, *_ = np.linalg.lstsq(A[ok], b[ok], rcond=None)
        grad = math.hypot(c[0], c[1])
        aspect = math.degrees(math.atan2(-c[0], -c[1])) % 360
        return {"gradient_pct": grad * 100, "downhill_bearing_deg": aspect,
                "contour_bearing_deg": (aspect + 90) % 360}

    def _grid(self, poly, step=1.0):
        es = [p[0] for p in poly]; ns = [p[1] for p in poly]
        for e in np.arange(min(es), max(es), step):
            for n in np.arange(min(ns), max(ns), step):
                if point_in(e, n, poly):
                    yield e, n

    def area(self, poly):
        s = 0
        for i in range(len(poly)):
            x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % len(poly)]
            s += x1 * y2 - x2 * y1
        return abs(s) / 2

    def rock(self):
        return [(p[0], p[1], p[2]) for p in self.points if p[3] in ("BRK", "SH")]


def point_in(x, y, poly):
    c = False; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i - 1) % n]
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
            c = not c
    return c


def boundary(site_json):
    m = json.load(open(site_json))["boundary"]["markers"]
    return [(k["easting"], k["northing"]) for k in m]
