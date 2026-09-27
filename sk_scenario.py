"""Drei Instanzen dieser Demo. **Betriebsnetz** (wortgleich aus `cen_scenario.py`/`brg_scenario.py` übernommen): ein gestörtes Straßenraster (oder ein Zufallsgraph gleicher Kantenzahl) - die
durchgehende "reale" Instanz der Reihe. NEU: **Ring-Umverdrahtung** (Watts und Strogatz 1998): n Knoten im Kreis, jeder mit den k nächsten Nachbarn je Seite verbunden (Ring-Gitter), dann wird jede
Kante mit Wahrscheinlichkeit p durch eine zufällige Kante ersetzt - reproduziert direkt das Watts-Strogatz-Experiment (hohe Clusterbildung UND kurze Wege gleichzeitig, schon bei winzigem p). NEU:
**Skalenfreies Netz** (Barabási und Albert 1999): ein Kern von m0 Knoten (Kreis, damit er von Anfang an zusammenhängend ist und jeder Kernknoten Grad 2 hat), jeder weitere Knoten hängt sich mit m
Kanten bevorzugt an bereits gut vernetzte Knoten an (Wahrscheinlichkeit proportional zum Grad, über eine Kantenenden-Liste effizient gezogen) - exakte Kantenzahl m0+(n-m0)*m, per Konstruktion
zusammenhängend.

Knoten sind von 0 bis n-1 durchnummeriert; Kanten (u, v, w) mit u < v, sortiert; w = Länge (nur zur Anzeige, für die Strukturkennzahlen ungewichtet)."""

import math
import random
from dataclasses import dataclass

import numpy as np

import sk_constants as C


@dataclass(frozen=True)
class Instance:
    xy: np.ndarray                 # (n, 2)
    edges: tuple                   # ((u, v, w), ...) sortiert
    kind: str = "city"             # "city" | "ring" | "ba"
    nettype: str = "grid"          # nur kind == "city": "grid" | "random"
    side: int = 0                  # nur kind == "city"
    blocked: float = 0.0           # nur kind == "city"
    seed: int = 0
    blocked_edges: tuple = ()      # gesperrte Straßen (u, v), nur zur Anzeige (nur beim Raster)
    k_ring: int = 0                # nur kind == "ring"
    p_rewire: float = 0.0          # nur kind == "ring"
    m_ba: int = 0                  # nur kind == "ba"
    m0_ba: int = 0                 # nur kind == "ba"

    @property
    def n(self):
        return len(self.xy)

    @property
    def m(self):
        return len(self.edges)


def make_rng(seed, salt):
    """Zufallsquelle mit fester, plattformunabhängiger Zahlenfolge (Python-`random`, nicht numpy: die Instanzen und alle daraus gezählten Zahlen ändern sich nie mit einer Bibliotheksversion)."""
    return random.Random(int(seed) * 1_000_003 + int(salt))


# --- Betriebsnetz (wortgleiche Kopie aus cen_scenario.py) --------------------------------------------------------------------------------------------


def grid_edges(side):
    out = []
    for r in range(side):
        for c in range(side):
            v = r * side + c
            if c + 1 < side:
                out.append((v, v + 1))
            if r + 1 < side:
                out.append((v, v + side))
    return out


def block(pairs, share, rng):
    """Sperrt genau `round(share * Zahl der Straßen)` Straßen, zufällig und OHNE Rücksicht auf den Zusammenhang. Gibt (verbleibende, gesperrte) zurück."""
    target = int(round(share * len(pairs)))
    order = list(range(len(pairs)))
    rng.shuffle(order)
    removed = set(order[:target])
    kept = [pairs[j] for j in range(len(pairs)) if j not in removed]
    return kept, [pairs[j] for j in sorted(removed)]


def random_pairs(n, m, rng):
    """`m` verschiedene Kanten zwischen zufälligen verschiedenen Knotenpaaren (einfacher Graph)."""
    max_m = n * (n - 1) // 2
    m = min(m, max_m)
    chosen = set()
    while len(chosen) < m:
        u = rng.randrange(n)
        v = rng.randrange(n)
        if u == v:
            continue
        chosen.add((min(u, v), max(u, v)))
    return sorted(chosen)


def generate(side=C.DEFAULT_SIDE, blocked=C.DEFAULT_BLOCKED, nettype="grid", seed=C.DEFAULT_SEED, jitter=C.JITTER):
    if nettype not in C.NETTYPES:
        raise ValueError(f"unbekannter Netztyp {nettype}")
    side = int(side)
    if side < 2:
        raise ValueError("Seitenlänge mindestens 2")
    n = side * side
    rng = make_rng(seed, 4711)
    xy = np.array([[c * C.SPACING + rng.uniform(-jitter, jitter) * C.SPACING, r * C.SPACING + rng.uniform(-jitter, jitter) * C.SPACING] for r in range(side) for c in range(side)], dtype=float)
    kept, removed = block(grid_edges(side), float(blocked), rng)
    if nettype == "random":
        rng2 = make_rng(seed, 9173)
        kept = random_pairs(n, len(kept), rng2)
        removed = []
    edges = tuple((u, v, float(np.hypot(*(xy[u] - xy[v])))) for u, v in kept)
    return Instance(xy, edges, "city", nettype, side, float(blocked), int(seed), tuple(removed))


# --- Ring-Umverdrahtung (Watts und Strogatz 1998) ----------------------------------------------------------------------------------------------------


def ring_lattice_instance(n, k, p, seed):
    """n Knoten im Kreis, jeder mit den k NÄCHSTEN NACHBARN VERBUNDEN (k = GESAMTGRAD jedes Knotens im Ring-Gitter, wie bei Watts und Strogatz 1998 selbst: k/2 Nachbarn je Seite, k muss darum gerade
    sein). Danach wird jede Kante in fester Reihenfolge (Distanz j=1..k/2, dann Knoten i=0..n-1 - Watts und Strogatz' eigener Algorithmus) mit Wahrscheinlichkeit p durch eine zufällige Kante von i zu
    einem noch nicht verbundenen, verschiedenen Knoten ersetzt (kein Selbstloop, keine Mehrfachkante). p=0 ergibt das reine Ring-Gitter (Lehrbuch-Clustering C = 3(k-2)/(4(k-1)), Watts und Strogatz
    1998), p=1 einen fast zufälligen Graphen bei gleicher Kantenzahl."""
    n = int(n)
    k = int(k)
    p = float(p)
    if n < 3:
        raise ValueError("n muss mindestens 3 sein")
    if k % 2 != 0:
        raise ValueError("k (Gesamtgrad) muss gerade sein (k/2 Nachbarn je Seite)")
    k_half = k // 2
    if not (1 <= k_half <= (n - 1) // 2):
        raise ValueError(f"k muss zwischen 2 und {2 * ((n - 1) // 2)} liegen (gerade)")
    if not (0.0 <= p <= 1.0):
        raise ValueError("p muss zwischen 0 und 1 liegen")
    rng = make_rng(seed, 6203)
    nbrs = [set() for _ in range(n)]
    for i in range(n):
        for j in range(1, k_half + 1):
            nbrs[i].add((i + j) % n)
            nbrs[(i + j) % n].add(i)
    for j in range(1, k_half + 1):
        for i in range(n):
            v = (i + j) % n
            if v not in nbrs[i]:
                continue                                        # diese Kante wurde schon (als Ziel eines früheren Umverdrahtungs-Schritts) entfernt
            if rng.random() < p:
                candidates = [w for w in range(n) if w != i and w not in nbrs[i]]
                if not candidates:
                    continue                                    # Knoten schon mit allen anderen verbunden - Umverdrahtung würde nichts ändern
                w = rng.choice(candidates)
                nbrs[i].discard(v)
                nbrs[v].discard(i)
                nbrs[i].add(w)
                nbrs[w].add(i)
    pairs = sorted({(min(u, v), max(u, v)) for u in range(n) for v in nbrs[u]})
    xy = np.array([[math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n)] for i in range(n)], dtype=float)
    edges = tuple((u, v, float(np.hypot(*(xy[u] - xy[v])))) for u, v in pairs)
    return Instance(xy, edges, "ring", "grid", 0, 0.0, int(seed), (), int(k), float(p))


# --- Skalenfreies Netz (Barabási und Albert 1999) -----------------------------------------------------------------------------------------------------


def barabasi_albert_instance(n, m, m0, seed):
    """Kern: ein Kreis über m0 Knoten (m0 Kanten, jeder Kernknoten Grad 2, von Anfang an zusammenhängend). Jeder weitere Knoten t=m0..n-1 hängt sich mit m Kanten an m verschiedene bereits vorhandene
    Knoten an, gezogen proportional zum aktuellen Grad (bevorzugte Anbindung): eine Liste der Kantenenden (jeder Knoten so oft darin, wie er schon Kanten hat) macht die gewichtete Ziehung effizient -
    ein zufällig gezogenes Element der Liste trifft jeden Knoten mit Wahrscheinlichkeit proportional zu seinem Grad. Exakte Kantenzahl m0+(n-m0)*m."""
    n = int(n)
    m = int(m)
    m0 = int(m0)
    if m0 < 3:
        raise ValueError("m0 muss mindestens 3 sein (Kern ist ein Kreis über m0 Knoten, ein Kreis über 2 Knoten wäre eine Mehrfachkante)")
    if not (1 <= m <= m0):
        raise ValueError(f"m muss zwischen 1 und m0={m0} liegen")
    if n < m0:
        raise ValueError("n muss mindestens m0 sein")
    rng = make_rng(seed, 8117)
    edges = []
    stubs = []
    for i in range(m0):
        j = (i + 1) % m0
        u, v = min(i, j), max(i, j)
        edges.append((u, v))
        stubs.append(u)
        stubs.append(v)
    for new in range(m0, n):
        chosen = set()
        while len(chosen) < m:
            cand = stubs[rng.randrange(len(stubs))]
            if cand != new and cand not in chosen:
                chosen.add(cand)
        for t in sorted(chosen):
            edges.append((t, new))
            stubs.append(t)
            stubs.append(new)
    edges.sort()
    xy = np.zeros((n, 2), dtype=float)
    for i in range(m0):
        ang = 2 * math.pi * i / m0
        xy[i] = [1.6 * math.cos(ang), 1.6 * math.sin(ang)]
    layout_rng = make_rng(seed, 2477)
    for i in range(m0, n):
        ang = 2 * math.pi * layout_rng.random()
        rad = 0.3 + 1.3 * layout_rng.random()
        xy[i] = [rad * math.cos(ang), rad * math.sin(ang)]
    out_edges = tuple((u, v, float(np.hypot(*(xy[u] - xy[v])))) for u, v in edges)
    return Instance(xy, out_edges, "ba", "grid", 0, 0.0, int(seed), (), 0, 0.0, int(m), int(m0))
