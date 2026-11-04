"""Build the Vixl Originals: twenty typefaces drawn and exported with Vixl's font maker.

Every family starts from the same hand-drawn skeletons (``skeletons.py``) or the 5 x 9 bitmap set, and gets its
character from how Vixl draws them: stroke weight, caps and joins, how soft corners are rounded (circle, squircle,
chamfer or square), width, x-height, slant, slab or hairline serifs, broad-nib contrast (a ``width_profile``),
hand jitter and tapers, dotted dashes, and ``outline-stroke`` with ``pathfinder`` for the hollow, inline and
sliced styles. Each family is one Vixl document: glyphs are ordinary layers in ``font-grid`` cells, mapped with
``font-glyph`` and written with ``export``. The documents are kept as editable masters.

Usage, from the root of this repository, with Vixl installed (a release that lists the Vixl Originals):

    python fonts/originals/build_originals.py                # every family
    python fonts/originals/build_originals.py orbit quill    # some, by slug suffix

Writes ``fonts/sources/vixl-<name>-<weight>.ttf`` (named like Vixl's font cache), the master
``fonts/originals/masters/vixl-<name>.vixl`` and a specimen ``fonts/originals/specimens/vixl-<name>.png``.
Then run ``python fonts/build_pack.py``.
"""

import hashlib
import json
import math
from pathlib import Path
import random
import sys

from vixl.geometry import path_polygons
from vixl.project import Project

sys.path.insert(0, str(Path(__file__).resolve().parent))
from skeletons import ASCII, BITMAPS, GLYPHS, MONO, SQUARE  # noqa: E402

HERE = Path(__file__).resolve().parent
SOURCES = HERE.parent / "sources"
MASTERS = HERE / "masters"
SPECIMENS = HERE / "specimens"
EM_PX = 320  # canvas pixels per em in the masters
SCALE = EM_PX / 1000
ASCENT, DESCENT = 950, 260  # line metrics, font units
INF = float("inf")
# Open-sided letters leave a hole before the next one; proportional faces pull their advance in (font units).
TIGHTEN = {"r": 70, "f": 50, "t": 40, "7": 30, "L": 40, "T": 20, "y": 10}
CIRCLE = 0.5523
VERSION = "1.000"
DESIGNER = "The Vixl Project"
COPYRIGHT = "Copyright 2026 The Vixl Project Authors (https://github.com/jxburros/Vixl)"
LICENSE = "This Font Software is licensed under the SIL Open Font License, Version 1.1. https://openfontlicense.org"
URL = "https://github.com/jxburros/VixlPacks/tree/main/fonts/originals"

BASE = {"sw": 80, "cap": "round", "join": "round", "radius": INF, "kappa": CIRCLE, "width": 1.0,
        "xh": 500, "ch": 700, "asc": 750, "desc": 210, "slant": 0, "sb": 50, "dot": "round", "dot_scale": 1.15,
        "mode": "stroke", "weight": 400, "serif": 0, "contrast": None, "jitter": 0, "taper": None, "mono": 0,
        "overshoot": 0}

STYLES = [
    {"family": "Vixl Orbit", "weight": 400, "sw": 76, "overshoot": 10,
     "description": "A geometric sans of circles and straight lines with round terminals."},
    {"family": "Vixl Bolt", "contrast": (0.74, 0), "weight": 800, "sw": 168, "cap": "butt", "join": "miter", "width": 1.06, "xh": 530,
     "sb": 36, "overshoot": 12, "dot": "round", "dot_scale": 1.05,
     "description": "A black geometric sans with flat cuts, for loud headlines."},
    {"family": "Vixl Hairline", "weight": 100, "sw": 20, "cap": "butt", "join": "miter", "width": 1.24, "xh": 470,
     "ch": 720, "asc": 770, "sb": 70, "overshoot": 6, "dot_scale": 2.2,
     "description": "A wide hairline geometric sans for large, airy display type."},
    {"family": "Vixl Tessera", "weight": 500, "sw": 92, "cap": "butt", "join": "miter", "radius": 130,
     "kappa": 0.62, "width": 1.2, "xh": 540, "dot": "square", "dot_scale": 1.0,
     "description": "A wide squarish sans with rounded corners and an engineered, technical feel."},
    {"family": "Vixl Facet", "weight": 700, "sw": 120, "cap": "butt", "join": "miter", "radius": 110, "kappa": 0,
     "width": 0.84, "xh": 540, "ch": 720, "asc": 760, "dot": "square", "dot_scale": 1.0,
     "description": "A condensed octagonal sans with chamfered corners, athletic and industrial."},
    {"family": "Vixl Block", "contrast": (0.74, 0), "weight": 800, "sw": 150, "cap": "butt", "join": "miter", "radius": 0, "width": 0.8,
     "xh": 560, "ch": 720, "asc": 760, "sb": 40, "dot": "square", "dot_scale": 1.0,
     "description": "A heavy condensed square sans with right-angled corners."},
    {"family": "Vixl Mono", "weight": 400, "sw": 72, "radius": 170, "kappa": 0.6, "width": 0.9, "xh": 520,
     "mono": 600, "sb": 40, "category": "monospace",
     "description": "A rounded monospaced face for code, terminals and data, with a slashed zero."},
    {"family": "Vixl Slab", "weight": 500, "sw": 84, "cap": "butt", "join": "miter", "serif": 210, "width": 1.0,
     "xh": 500, "overshoot": 8, "dot": "square", "dot_scale": 1.05, "sb": 56,
     "description": "A geometric slab serif with square serifs and beaks, sturdy in text and headings."},
    {"family": "Vixl Bubble", "contrast": (0.74, 0), "weight": 900, "sw": 196, "kappa": 0.64, "width": 1.12, "xh": 560, "sb": 26,
     "overshoot": 8, "dot_scale": 1.0,
     "description": "A fat, soft, rounded display face with friendly squircle bowls."},
    {"family": "Vixl Quill", "weight": 400, "sw": 118, "cap": "butt", "join": "miter", "contrast": (0.11, 0),
     "serif": 150, "width": 0.92, "xh": 460, "ch": 700, "asc": 760, "sb": 46, "overshoot": 10,
     "dot_scale": 1.25, "description": "A high-contrast display serif with vertical stress and hairline serifs."},
    {"family": "Vixl Nib", "weight": 400, "sw": 104, "cap": "butt", "join": "round", "contrast": (0.22, 35),
     "slant": 12, "width": 0.8, "xh": 450, "asc": 760, "sb": 40, "overshoot": 8, "kappa": 0.6,
     "category": "handwriting", "description": "A slanted broad-nib italic with calligraphic thick and thin strokes."},
    {"family": "Vixl Marker", "weight": 600, "sw": 104, "jitter": 15, "taper": 0.5, "slant": 6, "width": 0.9,
     "xh": 540, "kappa": 0.6, "sb": 40, "category": "handwriting",
     "description": "A hand-drawn marker face with wobbly lines and tapered stroke ends."},
    {"family": "Vixl Sketch", "weight": 300, "sw": 20, "mode": "sketch", "jitter": 24, "width": 1.0, "xh": 510,
     "sb": 50, "dot_scale": 1.8, "category": "handwriting",
     "description": "A pencil-sketch face: each line drawn twice with a loose hand."},
    {"family": "Vixl Inline", "contrast": (0.74, 0), "weight": 800, "sw": 150, "mode": "inline", "width": 1.1, "xh": 520, "sb": 36,
     "overshoot": 10, "dot_scale": 1.05,
     "description": "A bold geometric display face cut with a single inline, in an Art Deco spirit."},
    {"family": "Vixl Neon", "weight": 400, "sw": 118, "mode": "outline", "wall": 22, "radius": 150, "kappa": 0.58,
     "width": 1.06, "xh": 520, "sb": 40, "dot_scale": 1.0,
     "description": "Hollow rounded tubes, like bent neon signage."},
    {"family": "Vixl Marquee", "weight": 500, "sw": 82, "mode": "dotted", "spacing": 1.5, "width": 1.12,
     "xh": 520, "sb": 60, "overshoot": 8, "dot_scale": 1.0,
     "description": "Letters drawn in evenly spaced round dots, like marquee bulbs."},
    {"family": "Vixl Pixel", "weight": 400, "mode": "bitmap", "pixel": "square", "category": "display",
     "description": "A crisp 5 x 7 pixel face on a monospaced grid."},
    {"family": "Vixl Matrix", "weight": 400, "mode": "bitmap", "pixel": "dot",
     "description": "A 5 x 7 dot-matrix face of round LED dots."},
    {"family": "Vixl Scanline", "weight": 400, "mode": "bitmap", "pixel": "scan",
     "description": "A 5 x 7 pixel face drawn in horizontal scanlines, like an old CRT."},
    {"family": "Vixl Slice", "contrast": (0.74, 0), "weight": 800, "sw": 150, "mode": "slice", "cap": "butt", "join": "miter",
     "radius": 210, "kappa": 0.62, "width": 1.14, "xh": 530, "sb": 36, "dot": "square", "dot_scale": 1.0,
     "description": "A bold rounded-square face sliced through by one horizontal cut."},
]


def slug(text):
    return "-".join("".join(c if c.isalnum() else " " for c in text.lower()).split())


def style_of(entry):
    style = {**BASE, **entry}
    style["slug"] = slug(style["family"])
    style["file"] = f"{style['slug']}-{style['weight']}.ttf"
    return style


# ------------------------------------------------------------------------------------------- geometry


def stroke_widths(st):
    """(width of a vertical stroke, width of a horizontal stroke) in font units."""
    sw = st["sw"]
    if not st["contrast"]:
        return sw, sw
    thin, angle = st["contrast"]
    a = math.radians(angle)
    return sw * (thin + (1 - thin) * abs(math.cos(a))), sw * (thin + (1 - thin) * abs(math.sin(a)))


def y_mapper(st, case):
    """Nominal skeleton height → this family's skeleton height, so stroke edges land on its metrics."""
    _, horizontal = stroke_widths(st)
    half = horizontal / 2
    top = st["ch"] if case == "U" else st["xh"]
    knots = [(-210, -st["desc"] + half), (0, half), (700 if case == "U" else 500, top - half),
             (750, st["asc"] - half)]

    def f(y):
        for (a, fa), (b, fb) in zip(knots, knots[1:]):
            if y <= b or b == knots[-1][0]:
                if y < a and a != knots[0][0]:
                    continue
                return fa + (y - a) * (fb - fa) / (b - a)
        return y

    return f


def lerp(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def dist(p, q):
    return math.hypot(q[0] - p[0], q[1] - p[1])


def rounded(nodes, closed, radius, kappa):
    """Segments (``("L", p0, p1)`` or ``("C", p0, c1, c2, p3)``) of a polyline whose soft nodes are rounded."""
    pts = [(x, y) for x, y, _ in nodes]
    soft = [s for _, _, s in nodes]
    n = len(pts)
    if not closed:
        soft[0] = soft[-1] = False
    corners = {}
    for i in range(n):
        if not soft[i]:
            continue
        prev, nxt = (i - 1) % n, (i + 1) % n
        p, a, b = pts[i], pts[prev], pts[nxt]
        lin, lout = dist(a, p), dist(p, b)
        if lin < 1e-9 or lout < 1e-9:
            continue
        din = min(radius, lin * (0.5 if soft[prev] else 1.0))
        dout = min(radius, lout * (0.5 if soft[nxt] else 1.0))
        if din < 1e-6 or dout < 1e-6:
            continue
        start, end = lerp(p, a, din / lin), lerp(p, b, dout / lout)
        corners[i] = (start, lerp(start, p, kappa), lerp(end, p, kappa), end)
    segs = []
    current = corners[0][3] if 0 in corners else pts[0]
    last = n + 1 if closed else n
    for k in range(1, last):
        i = k % n
        if i in corners:
            start, c1, c2, end = corners[i]
            if dist(current, start) > 1e-6:
                segs.append(("L", current, start))
            segs.append(("L", start, end) if kappa == 0 else ("C", start, c1, c2, end))
            current = end
        else:
            if dist(current, pts[i]) > 1e-6:
                segs.append(("L", current, pts[i]))
            current = pts[i]
    return segs


def point_at(seg, t):
    if seg[0] == "L":
        return lerp(seg[1], seg[2], t)
    p0, p1, p2, p3 = seg[1:]
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def piece(seg, a, b):
    """The part of a segment from parameter ``a`` to ``b``."""
    if seg[0] == "L":
        return ("L", point_at(seg, a), point_at(seg, b))

    def split(points, t):
        p0, p1, p2, p3 = points
        q0, q1, q2 = lerp(p0, p1, t), lerp(p1, p2, t), lerp(p2, p3, t)
        r0, r1 = lerp(q0, q1, t), lerp(q1, q2, t)
        s = lerp(r0, r1, t)
        return (p0, q0, r0, s), (s, r1, q2, p3)

    points = seg[1:]
    if b < 1:
        points = split(points, b)[0]
    if a > 0:
        points = split(points, a / b)[1]
    return ("C", *points)


def trimmed(segs, centre, a0, a1):
    """The part of a closed loop (starting at angle 0, running counter-clockwise) between two angles."""
    samples = []
    turned, previous = 0.0, None
    for index, seg in enumerate(segs):
        for step in range(65):
            t = step / 64
            x, y = point_at(seg, t)
            angle = math.degrees(math.atan2(y - centre[1], x - centre[0])) % 360
            if previous is not None:
                delta = (angle - previous + 180) % 360 - 180
                turned += delta
            previous = angle
            samples.append((turned, index + t))

    def where(target):
        lap = 0
        while target > 360 + 1e-9:
            target -= 360
            lap += 1
        for (ta, ua), (tb, ub) in zip(samples, samples[1:]):
            if ta <= target <= tb and tb > ta:
                return lap * len(segs) + ua + (ub - ua) * (target - ta) / (tb - ta)
        return lap * len(segs) + len(segs)

    u0, u1 = where(a0), where(a1)
    out = []
    while u0 < u1 - 1e-9:
        index = int(u0) % len(segs)
        t0 = u0 - math.floor(u0)
        end = min(u1, math.floor(u0) + 1)
        t1 = end - math.floor(u0)
        if t1 - t0 > 1e-6:
            out.append(piece(segs[index], t0, t1))
        u0 = end
    return out


def bowl_nodes(box):
    x0, y0, x1, y1 = box
    cy = (y0 + y1) / 2
    return [(x1, cy, False), (x1, y1, True), (x0, y1, True), (x0, y0, True), (x1, y0, True)]


def glyph_strokes(char, st):
    """``(strokes, dots, extents)`` for one character in a stroked family, in font units before slant: strokes
    are ``{"segs", "closed", "case", "serif"}``, dots are centre points."""
    if st["mono"] and char in MONO:
        case, strokes = MONO[char]
    elif st["radius"] < 300 and char in SQUARE:
        case, strokes = SQUARE[char]
    else:
        case, strokes = GLYPHS[char]
    vertical, _ = stroke_widths(st)
    fy = y_mapper(st, case)
    xs = st["width"] * (1 + (vertical - 76) / 900)
    over = st["overshoot"]

    def m(x, y):
        return (x * xs, fy(y))

    out, dots = [], []
    for stroke in strokes:
        kind = stroke["kind"]
        if kind == "dot":
            dots.append(m(*stroke["at"]))
            continue
        if kind == "line":
            nodes = [(*m(x, y), s) for x, y, s in stroke["nodes"]]
            out.append({"segs": rounded(nodes, stroke["closed"], st["radius"], st["kappa"]),
                        "closed": stroke["closed"], "nodes": nodes})
            continue
        x0, y0, x1, y1 = stroke["box"]
        (x0, y0), (x1, y1) = m(x0, y0), m(x1, y1)
        box = (x0, y0 - over, x1, y1 + over)
        segs = rounded(bowl_nodes(box), True, st["radius"], st["kappa"])
        if kind == "bowl":
            out.append({"segs": segs, "closed": True})
        else:
            out.append({"segs": trimmed(segs, ((x0 + x1) / 2, (y0 + y1) / 2), *stroke["angles"]), "closed": False})
    xs_all = [p[0] for s in out for seg in s["segs"] for p in seg[1:]] + [d[0] for d in dots]
    extents = (min(xs_all), max(xs_all)) if xs_all else (0, 0)
    return out, dots, extents, case


def serifs(char, strokes, st, case):
    """Slab serifs and beaks for the open ends of straight strokes that land on a guide line."""
    if not st["serif"] or not char.isalnum():
        return []
    vertical, horizontal = stroke_widths(st)
    lower, upper = y_mapper(st, "L"), y_mapper(st, "U")
    guides = {"base": lower(0), "x": lower(500), "cap": upper(700), "asc": lower(750), "desc": lower(-210)}
    length = st["serif"]
    added = []
    for stroke in strokes:
        if stroke["closed"] or not stroke.get("nodes"):
            continue
        segs = stroke["segs"]
        for end, seg in (("start", segs[0]), ("end", segs[-1])):
            if seg[0] != "L":
                continue
            tip, other = (seg[1], seg[2]) if end == "start" else (seg[2], seg[1])
            dx, dy = tip[0] - other[0], tip[1] - other[1]
            span = math.hypot(dx, dy) or 1
            guide = next((name for name, y in guides.items() if abs(tip[1] - y) < 3), None)
            if guide is None:
                continue
            top = guide in ("x", "cap", "asc")
            if abs(dy) >= 0.55 * span:  # a stem or diagonal: a horizontal serif across its foot or head
                if case == "L" and top and abs(dx) < 0.1 * span:  # lowercase stems take a head serif to the left
                    left, right = tip[0] - length * 0.62, tip[0]
                else:
                    left, right = tip[0] - length / 2, tip[0] + length / 2
                added.append([("L", (left, tip[1]), (right, tip[1]))])
            elif abs(dx) >= 0.9 * span and guide in ("base", "x", "cap", "asc"):  # an arm: a beak
                inward = -1 if top else 1
                x = tip[0] - math.copysign(vertical / 2, dx)
                y0 = tip[1] - inward * horizontal / 2
                added.append([("L", (x, y0), (x, tip[1] + inward * length * 0.6))])
    return added


def transform(segs, fn):
    return [(seg[0], *(fn(p) for p in seg[1:])) for seg in segs]


def svg(segs, ox, oy):
    """Path data relative to ``(ox, oy)`` (canvas pixels), and the canvas points it covers."""
    parts, start = [], None
    for seg in segs:
        if start is None or dist(start, seg[1]) > 1e-6:
            parts.append(f"M{seg[1][0] - ox:.2f} {seg[1][1] - oy:.2f}")
        if seg[0] == "L":
            parts.append(f"L{seg[2][0] - ox:.2f} {seg[2][1] - oy:.2f}")
        else:
            parts.append("C" + " ".join(f"{p[0] - ox:.2f} {p[1] - oy:.2f}" for p in seg[2:]))
        start = seg[-1]
    return " ".join(parts)


def closed_svg(segs, ox, oy):
    return svg(segs, ox, oy) + " Z"


def bounds_of(segs):
    pts = [p for seg in segs for p in seg[1:]]
    return min(p[0] for p in pts), min(p[1] for p in pts)


def nib_profile(d, thin, angle):
    """A ``width_profile`` for path data ``d``: wide where the path runs across the nib, thin along it."""
    poly = path_polygons(d)[0]
    lengths = [0.0]
    for a, b in zip(poly, poly[1:]):
        lengths.append(lengths[-1] + dist(a, b))
    total = lengths[-1] or 1
    nib = math.radians(angle)

    def factor(i):
        a, b = poly[max(0, i - 1)], poly[min(len(poly) - 1, i + 1)]
        theta = math.atan2(-(b[1] - a[1]), b[0] - a[0])  # canvas y runs down
        return thin + (1 - thin) * abs(math.sin(theta - nib))

    count = min(120, len(poly))
    picks = sorted({round(k * (len(poly) - 1) / (count - 1)) for k in range(count)})
    profile, last = [], -1.0
    for i in picks:
        f = lengths[i] / total
        if f <= last:
            continue
        profile.append([round(f, 5), round(factor(i), 4)])
        last = f
    profile[0][0], profile[-1][0] = 0, 1
    for row in profile[1:-1]:
        row[0] = min(max(row[0], 1e-5), 1 - 1e-5)
    cleaned = [profile[0]]
    for row in profile[1:]:
        if row[0] > cleaned[-1][0]:
            cleaned.append(row)
    if cleaned[-1][0] != 1:
        cleaned[-1][0] = 1
    return cleaned


# ------------------------------------------------------------------------------------------- drawing


class Drawer:
    """Collects the Vixl operations that draw one family."""

    def __init__(self, st):
        self.st = st
        self.ops = []
        self.after = []  # outline-stroke and pathfinder steps, once every layer exists
        self.count = 0
        self.paths = set()  # stroked path layers (dots are filled shapes)

    def name(self, char, tag):
        self.count += 1
        return f"g{ord(char):03d}-{tag}{self.count}"

    def path(self, char, segs, closed, canvas, *, width, tag="s", extra=None):
        """A stroked path layer from font-unit segments; ``canvas`` maps a font-unit point to the canvas."""
        segs = transform(segs, canvas)
        ox, oy = bounds_of(segs)
        d = closed_svg(segs, ox, oy) if closed else svg(segs, ox, oy)
        name = self.name(char, tag)
        op = {"type": "shape", "shape": "path", "name": name, "x": round(ox, 3), "y": round(oy, 3), "path": d,
              "fill": "transparent", "stroke": "#000000", "stroke_width": round(width * SCALE, 3),
              "line_cap": self.st["cap"], "line_join": self.st["join"]}
        if self.st["join"] == "miter":
            op["miter_limit"] = 2.4
        if extra:
            op.update(extra(d) if callable(extra) else extra)
        self.ops.append(op)
        self.paths.add(name)
        return name

    def blob(self, char, centre, size, shape, tag="d"):
        name = self.name(char, tag)
        self.ops.append({"type": "shape", "shape": shape, "name": name, "x": round(centre[0] - size / 2, 3),
                         "y": round(centre[1] - size / 2, 3), "width": round(size, 3), "height": round(size, 3),
                         "fill": "#000000"})
        return name


def jittered(segs, rng, amount):
    """Segments with every distinct point moved a little (shared points move together, so joins hold)."""
    if not amount:
        return segs
    moved = {}

    def move(p):
        key = (round(p[0], 3), round(p[1], 3))
        if key not in moved:
            moved[key] = (p[0] + rng.uniform(-amount, amount), p[1] + rng.uniform(-amount, amount))
        return moved[key]

    return transform(segs, move)


def extended(segs, amount):
    """An open run lengthened at both ends (a sketch line overshoots its corners)."""
    if not amount or not segs:
        return segs
    first, last = list(segs[0]), list(segs[-1])
    a, b = first[1], first[2]
    span = dist(a, b) or 1
    first[1] = (a[0] - (b[0] - a[0]) / span * amount, a[1] - (b[1] - a[1]) / span * amount)
    c, e = last[-2], last[-1]
    span = dist(c, e) or 1
    last[-1] = (e[0] + (e[0] - c[0]) / span * amount, e[1] + (e[1] - c[1]) / span * amount)
    if len(segs) == 1:
        return [tuple(first[:-1]) + (last[-1],)]
    return [tuple(first)] + segs[1:-1] + [tuple(last)]


def draw_stroked(drawer, char, origin, st):
    """Layers for one character of a stroked family; returns the layer names that make the glyph and its
    advance in font units."""
    strokes, dots, (x_min, x_max), case = glyph_strokes(char, st)
    vertical, horizontal = stroke_widths(st)
    rng = random.Random(f"{st['family']}:{char}")
    advance_units = (x_max - x_min) + vertical + 2 * st["sb"]
    squeeze = 1.0
    if st["mono"]:
        room = st["mono"] - 2 * st["sb"] - vertical
        squeeze = min(1.0, room / max(1e-6, x_max - x_min))
        advance_units = st["mono"]
        left = (st["mono"] - (x_max - x_min) * squeeze) / 2
    else:
        left = st["sb"] + vertical / 2
        advance_units -= TIGHTEN.get(char, 0) * st["width"]
    if char == " ":
        return [], (st["mono"] or 260 * st["width"])
    if not strokes and not dots:
        return [], advance_units
    slant = math.tan(math.radians(st["slant"]))
    ox, base = origin

    def canvas(p):
        x = left + (p[0] - x_min) * squeeze + p[1] * slant
        return (ox + x * SCALE, base - p[1] * SCALE)

    extra_serifs = serifs(char, strokes, st, case)
    runs = [(s["segs"], s["closed"]) for s in strokes] + [(segs, False) for segs in extra_serifs]
    names, inner = [], []
    mode = st["mode"]
    for segs, closed in runs:
        if mode == "sketch":
            for _ in range(2):
                wobbly = jittered(segs if closed else extended(segs, 16), rng, st["jitter"])
                names.append(drawer.path(char, wobbly, closed, canvas, width=st["sw"]))
            continue
        if st["jitter"]:
            segs = jittered(segs, rng, st["jitter"])
        extra = None
        if st["contrast"]:
            thin, angle = st["contrast"]
            extra = lambda d, thin=thin, angle=angle: {"width_profile": nib_profile(d, thin, angle)}  # noqa: E731
        elif st["taper"] and not closed:
            extra = {"taper_end": st["taper"]}
        elif mode == "dotted":
            gap = st["sw"] * st["spacing"] * SCALE
            extra = {"dash": [0.01, round(gap, 3)], "dash_fit": True, "line_cap": "round"}
        names.append(drawer.path(char, segs, closed, canvas, width=st["sw"], extra=extra))
        if mode == "outline":
            inner.append(drawer.path(char, segs, closed, canvas, width=st["sw"] - 2 * st["wall"], tag="i"))
        elif mode == "inline":
            trim = None
            if not closed:
                length = sum(dist(seg[1], seg[-1]) for seg in segs) or 1
                cut = min(45.0, 100 * st["sw"] * 0.42 / length)
                trim = {"trim_start": round(cut, 3), "trim_end": round(100 - cut, 3)}
            if trim is None or trim["trim_end"] - trim["trim_start"] > 4:
                inner.append(drawer.path(char, segs, closed, canvas, width=st["sw"] * 0.12, tag="i",
                                         extra={**(trim or {}), "line_cap": "round"}))
    size = vertical * st["dot_scale"]
    for centre in dots:
        point = canvas(centre)
        shape = "ellipse" if st["dot"] == "round" else "rectangle"
        names.append(drawer.blob(char, point, size * SCALE, shape))
        if mode == "outline":
            inner.append(drawer.blob(char, point, (size - 2 * st["wall"]) * SCALE, shape, tag="i"))
    if mode in ("outline", "inline", "slice") and names:
        stroked = [n for n in names + inner if n in drawer.paths]
        if stroked:
            # Outlined strokes are flattened polygons; thin them (within about one font unit) so the booleans stay
            # under pathfinder's segment budget.
            drawer.after.append({"type": "outline-stroke", "targets": stroked})
            drawer.after.append({"type": "path-simplify", "targets": stroked, "tolerance": 0.3})
        outer = f"g{ord(char):03d}-outer"
        drawer.after.append({"type": "pathfinder", "name": outer, "targets": names, "mode": "union"})
        cutters = list(inner)
        if mode == "slice":
            band_y = base - st["xh"] * 0.47 * SCALE
            band = drawer.name(char, "b")
            drawer.ops.append({"type": "shape", "shape": "rectangle", "name": band, "x": ox - 2,
                               "y": round(band_y - 24 * SCALE, 3), "width": advance_units * SCALE + 4,
                               "height": round(48 * SCALE, 3), "fill": "#000000"})
            cutters = [band]
        if cutters:
            cut = f"g{ord(char):03d}-cut"
            drawer.after.append({"type": "pathfinder", "name": cut, "targets": cutters, "mode": "union"})
            final = f"g{ord(char):03d}-glyph"
            drawer.after.append({"type": "pathfinder", "name": final, "targets": [outer, cut], "mode": "subtract"})
            return [final], advance_units
        return [outer], advance_units
    return names, advance_units


def draw_bitmap(drawer, char, origin, st):
    rows = BITMAPS[char]
    ox, base = origin
    pixel = 100
    names = []
    for r, row in enumerate(rows):
        top = base - (7 - r) * pixel * SCALE
        if st["pixel"] == "dot":
            for c, lit in enumerate(row):
                if lit == "#":
                    centre = (ox + (50 + c * pixel + pixel / 2) * SCALE, top + pixel / 2 * SCALE)
                    names.append(drawer.blob(char, centre, 84 * SCALE, "ellipse"))
            continue
        c = 0
        while c < 5:
            if row[c] != "#":
                c += 1
                continue
            run = c
            while run < 5 and row[run] == "#":
                run += 1
            height = pixel if st["pixel"] == "square" else 54
            y = top + (pixel - height) / 2 * SCALE
            name = drawer.name(char, "p")
            drawer.ops.append({"type": "shape", "shape": "rectangle", "name": name,
                               "x": round(ox + (50 + c * pixel) * SCALE, 3), "y": round(y, 3),
                               "width": round((run - c) * pixel * SCALE, 3), "height": round(height * SCALE, 3),
                               "fill": "#000000"})
            names.append(name)
            c = run
    return names, 600


# ------------------------------------------------------------------------------------------- build


# A glyph whose stroke folds over itself (a tight curve in a heavy weight) can fail to merge into one outline.
# Retry it with a round join, then a slightly lighter stroke; the build reports which glyphs needed it.
RETRIES = [lambda st: {},
           lambda st: {"join": "round"},
           lambda st: {"join": "round", "sw": st["sw"] * 0.92},
           lambda st: {"join": "round", "sw": st["sw"] * 0.84},
           lambda st: {"join": "round", "sw": st["sw"] * 0.74},
           lambda st: {"join": "round", "sw": st["sw"] * 0.84, "mode": "stroke", "contrast": None}]


def outlines_merge(drawer, names, char, size):
    """Whether Vixl's font maker can merge the glyph's layers into one outline (checked in a scratch document)."""
    from vixl.errors import VixlError
    from vixl.plugins.fontmaker.fontmaker import Scene, _merge

    scratch = Project(*size)
    try:
        scratch.apply(drawer.ops + drawer.after, detail="compact")
        scene = Scene(scratch)
        items = [leaf for name in names for leaf in scene.leaves(scratch.layer(name)) if leaf["type"] != "group"]
        _merge([scene.contours(item) for item in items], char)
    except VixlError:
        return False
    return True


def metrics(st):
    if st["mode"] == "bitmap":
        return {"xh": 500, "ch": 700, "asc": 700, "desc": 200}
    return {key: st[key] for key in ("xh", "ch", "asc", "desc")}


def build(st, out_sources=SOURCES):
    chars = [c for c in ASCII if c != " "]
    columns = 10
    rows = math.ceil(len(chars) / columns)
    widest = 1400 if st["mode"] != "bitmap" else 700
    advance_px, gap = widest * SCALE, 0.25 * EM_PX
    height = (ASCENT + DESCENT) * SCALE
    width = math.ceil(2 * gap + columns * advance_px + (columns - 1) * gap)
    tall = math.ceil(2 * gap + rows * height + (rows - 1) * gap)
    m = metrics(st)
    project = Project(width, tall, background="white")
    space = (st["mono"] or (600 if st["mode"] == "bitmap" else 260 * st["width"])) * SCALE
    design = {"type": "font-design", "family": st["family"], "style": "Regular", "weight": st["weight"],
              "em": EM_PX, "ascent": ASCENT * SCALE, "descent": DESCENT * SCALE, "line_gap": 0,
              "x_height": m["xh"] * SCALE, "cap_height": m["ch"] * SCALE, "space": round(space, 3),
              "italic_angle": -st["slant"], "version": VERSION, "designer": DESIGNER, "copyright": COPYRIGHT,
              "license": LICENSE, "url": URL, "description": st["description"]}
    project.apply([design, {"type": "font-grid", "chars": "".join(chars), "columns": columns,
                            "advance": advance_px, "gap": gap}], detail="compact")
    cells = project.state["font_design"]["glyphs"]
    ops, after, mapping, adjusted = [], [], {}, {}
    for char in chars:
        origin = tuple(cells[char]["origin"])
        for tweak in RETRIES:
            variant = {**st, **tweak(st)}
            drawer = Drawer(variant)
            draw = draw_bitmap if st["mode"] == "bitmap" else draw_stroked
            names, advance = draw(drawer, char, origin, variant)
            if not names or outlines_merge(drawer, names, char, (width, tall)):
                break
        else:
            raise SystemExit(f"{st['family']}: glyph {char!r} does not outline cleanly with any retry")
        if tweak is not RETRIES[0]:
            adjusted[char] = tweak(st)
        ops += drawer.ops
        after += drawer.after
        mapping[char] = (names, origin, advance)
    for start in range(0, len(ops), 400):
        project.apply(ops[start:start + 400], detail="compact")
    for start in range(0, len(after), 200):
        project.apply(after[start:start + 200], detail="compact")
    glyph_ops = [{"type": "font-glyph", "char": char, "targets": names, "origin": list(origin),
                  "advance": round(advance * SCALE, 3)}
                 for char, (names, origin, advance) in mapping.items() if names]
    project.apply(glyph_ops, detail="compact")
    out_sources.mkdir(parents=True, exist_ok=True)
    MASTERS.mkdir(exist_ok=True)
    target = out_sources / st["file"]
    report = {}
    from vixl.plugins.fontmaker.fontmaker import build as build_font

    data = build_font(project, "ttf", report)
    if adjusted:
        report.setdefault("warnings", []).extend(f"glyph {c!r} drawn with {a}" for c, a in adjusted.items())
    target.write_bytes(data)
    project.save(MASTERS / f"{st['slug']}.vixl", overwrite=True)
    return target, report


SAMPLE = ["The quick brown fox jumps over the lazy dog.",
          "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz",
          "0123456789 !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"]


def specimen(st, font_path):
    from vixl.fonts import register_font_data

    SPECIMENS.mkdir(exist_ok=True)
    project = Project(1800, 980, background="#ffffff")
    register_font_data(project, font_path.read_bytes(), "specimen")
    ops = [{"type": "text", "name": "title", "text": st["family"], "font": "specimen", "size": 150, "x": 60,
            "y": 40, "color": "#111111"},
           {"type": "text", "name": "about", "text": st["description"], "size": 26, "x": 64, "y": 230,
            "color": "#666666"}]
    y = 300
    for i, line in enumerate(SAMPLE):
        ops.append({"type": "text", "name": f"line{i}", "text": line, "font": "specimen", "size": 68 if i else 74,
                    "x": 60, "y": y, "color": "#111111"})
        y += 150
    ops.append({"type": "text", "name": "small", "text": "Sphinx of black quartz, judge my vow — 24 px",
                "font": "specimen", "size": 24, "x": 64, "y": y + 10, "color": "#111111"})
    project.apply(ops, detail="compact")
    out = SPECIMENS / f"{st['slug']}.png"
    if out.exists():
        out.unlink()
    project.export(str(out))
    return out


def sync_manifest():
    """Put every Vixl Original in ``fonts/manifest.json`` (after the third-party fonts, which stay as they are)."""
    path = HERE.parent / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    ours = {style_of(s)["file"] for s in STYLES}
    fonts = [entry for entry in manifest["fonts"] if entry["file"] not in ours]
    for entry in STYLES:
        st = style_of(entry)
        fonts.append({"file": st["file"], "family": st["family"], "weight": st["weight"], "italic": False,
                      "license": "OFL-vixl-originals.txt", "source": URL, "original": True,
                      "description": st["description"]})
    manifest["fonts"] = fonts
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv):
    wanted = argv[1:]
    built = []
    for entry in STYLES:
        st = style_of(entry)
        if wanted and not any(st["slug"].endswith(w) for w in wanted):
            continue
        path, report = build(st)
        shot = specimen(st, path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        warnings = report.get("warnings", [])
        print(f"{st['family']:<14} {path.name:<26} {path.stat().st_size:>7} B  glyphs {report['glyphs']}  "
              f"{digest[:12]}  {len(warnings)} warnings  {shot.name}")
        for warning in warnings[:5]:
            print("   ", warning)
        built.append(st)
    sync_manifest()
    return built


if __name__ == "__main__":
    main(sys.argv)
