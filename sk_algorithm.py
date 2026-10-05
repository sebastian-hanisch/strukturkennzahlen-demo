"""Strukturkennzahlen des Netzes als Ganzes (nicht mehr einzelner Knoten/Kanten wie in der Zentralität-Demo) und die zwei Nullmodelle, gegen die sie geprüft werden.

**Clustering** (Watts und Strogatz 1998): wie oft sind die Nachbarn eines Knotens auch untereinander verbunden? Lokaler Koeffizient je Knoten, mittlerer Koeffizient, globale Transitivität.
**Mittlere Weglänge**: Mittelwert über alle erreichbaren ungeordneten Knotenpaare - wohldefiniert auch bei unzusammenhängenden Netzen (anders als `networkx.average_shortest_path_length`).
**Assortativität** (Newman 2002): Pearson-Korrelation der Grade an beiden Enden jeder Kante - hängen sich hochgradige Knoten eher an andere hochgradige (assortativ) oder an schwachgradige
(disassortativ)?
**Nullmodelle**: Erdős-Rényi G(n,m) (Erdős und Rényi 1959, gleiche Knoten-/Kantenzahl, Gradfolge selbst wird zerstört) und das gradfolgen-erhaltende Konfigurationsmodell (Maslov und Sneppen 2002,
Kanten-Doppeltausch: die Gradfolge bleibt dabei exakt erhalten - die zentrale methodische Frage dieser Demo: folgt eine gemessene Eigenschaft schon zwangsläufig aus der Gradfolge allein?).
**ω (Omega)** (Telesford u. a. 2011): zusammenfassende Kleine-Welt-Kennzahl, nur auf der Ring-Umverdrahtungs-Instanz sinnvoll definiert (dort ist C_lattice aus dem p=0-Fall bekannt)."""

import math
import random
from collections import deque


def adjacency(n, edges, order="fixed", seed=0):
    """Adjazenzliste aus Kanten (u, v, ...); "fixed" = aufsteigende Nachbarn, "shuffled" = je Knoten gemischt (Seed fest, Python-`random`). Wortgleiche Kopie aus `cen_algorithm.py`."""
    adj = [[] for _ in range(n)]
    for e in edges:
        u, v = int(e[0]), int(e[1])
        adj[u].append(v)
        adj[v].append(u)
    for lst in adj:
        lst.sort()
    if order == "shuffled":
        rng = random.Random(int(seed) * 1_000_003 + 5150)
        for lst in adj:
            rng.shuffle(lst)
    elif order != "fixed":
        raise ValueError(f"unbekannte Reihenfolge {order}")
    return adj


def bfs_distances(adj, s):
    """Abstand von s zu jedem erreichbaren Knoten (-1 = unerreichbar). Gibt (dist, Schritte) zurück. Wortgleiche Kopie aus `cen_algorithm.py`."""
    n = len(adj)
    dist = [-1] * n
    dist[s] = 0
    queue = deque([s])
    steps = 1
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            steps += 1
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                queue.append(v)
                steps += 1
    return dist, steps


# --- Clustering (Watts und Strogatz 1998) --------------------------------------------------------------------------------------------------------------


def clustering_coefficient(adj):
    """Lokaler Koeffizient je Knoten: C_v = 2*t_v / (d_v*(d_v-1)), wobei t_v die Zahl der Kanten zwischen Nachbarn von v ist (Dreiecke über v). Grad 0 oder 1 -> C_v = 0 per Konvention (wie
    `networkx.clustering`: kein Knotenpaar zum Verbinden vorhanden)."""
    n = len(adj)
    neighbour_sets = [set(a) for a in adj]
    out = [0.0] * n
    for v in range(n):
        nbrs = adj[v]
        d = len(nbrs)
        if d < 2:
            continue
        t = 0
        for i in range(d):
            ni = neighbour_sets[nbrs[i]]
            for j in range(i + 1, d):
                if nbrs[j] in ni:
                    t += 1
        out[v] = 2.0 * t / (d * (d - 1))
    return out


def average_clustering(adj):
    """Ungewichtetes Mittel des lokalen Koeffizienten über ALLE Knoten (auch Grad 0/1, die mit C=0 eingehen - wie `networkx.average_clustering` mit `count_zeros=True`, dem Vorgabewert)."""
    n = len(adj)
    if n == 0:
        return 0.0
    return sum(clustering_coefficient(adj)) / n


def transitivity(adj):
    """Global: 3 * (Zahl der Dreiecke) / (Zahl offener + geschlossener Tripel) = Σ_v 2*t_v / Σ_v d_v*(d_v-1) (jedes Dreieck wird an jedem seiner 3 Knoten einmal als t_v gezählt, jedes Tripel an
    seinem Mittelknoten einmal als d_v*(d_v-1)/2 - die Faktoren kürzen sich zur oben stehenden Summenform). 0.0 wenn es keine möglichen Tripel gibt (wie `networkx.transitivity`)."""
    n = len(adj)
    num = 0
    den = 0
    neighbour_sets = [set(a) for a in adj]
    for v in range(n):
        nbrs = adj[v]
        d = len(nbrs)
        if d < 2:
            continue
        den += d * (d - 1)
        for i in range(d):
            ni = neighbour_sets[nbrs[i]]
            for j in range(i + 1, d):
                if nbrs[j] in ni:
                    num += 2
    return num / den if den else 0.0


# --- Mittlere Weglänge -----------------------------------------------------------------------------------------------------------------------------------


def average_distance(adj):
    """Mittelwert der Abstände über alle erreichbaren ungeordneten Knotenpaare - wohldefiniert auch bei unzusammenhängenden Netzen (anders als `networkx.average_shortest_path_length`, das dort
    einen Fehler wirft): nicht erreichbare Paare tragen einfach nicht bei. 0.0 bei n<=1 oder wenn kein Paar erreichbar ist."""
    n = len(adj)
    total = 0
    count = 0
    for u in range(n):
        dist, _ = bfs_distances(adj, u)
        for v in range(u + 1, n):
            if dist[v] > 0:
                total += dist[v]
                count += 1
    return total / count if count else 0.0


# --- Assortativität (Newman 2002) ------------------------------------------------------------------------------------------------------------------------


def _pearson(xs, ys):
    n = len(xs)
    if n == 0:
        return float("nan")
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denx = sum((x - mx) ** 2 for x in xs)
    deny = sum((y - my) ** 2 for y in ys)
    den = math.sqrt(denx * deny)
    return num / den if den > 0.0 else float("nan")


def degree_assortativity(adj):
    """Pearson-Korrelation der Grade an beiden Enden jeder Kante (Newman 2002): jede Kante liefert BEIDE Richtungen (u,v) und (v,u), wie `networkx.degree_pearson_correlation_coefficient` -
    Assortativ (r>0): hochgradige Knoten hängen sich eher an hochgradige. NaN bei konstantem Grad (keine Varianz, wie networkx) oder wenn es keine Kante gibt."""
    n = len(adj)
    deg = [len(a) for a in adj]
    xs, ys = [], []
    for u in range(n):
        for v in adj[u]:
            if u < v:
                xs.append(deg[u])
                ys.append(deg[v])
                xs.append(deg[v])
                ys.append(deg[u])
    return _pearson(xs, ys)


# --- Nullmodell 1: Erdős-Rényi G(n,m) (Erdős und Rényi 1959) ---------------------------------------------------------------------------------------------


def erdos_renyi_gnm(n, m, seed):
    """m verschiedene Kanten zwischen zufälligen verschiedenen Knotenpaaren, gleichverteilt gezogen (einfacher Graph, keine Selbstloops/Mehrfachkanten). Zerstört auch die Gradfolge selbst - im
    Gegensatz zum Konfigurationsmodell unten."""
    rng = random.Random(int(seed) * 1_000_003 + 7331)
    max_m = n * (n - 1) // 2
    m = min(int(m), max_m)
    chosen = set()
    while len(chosen) < m:
        u = rng.randrange(n)
        v = rng.randrange(n)
        if u == v:
            continue
        chosen.add((min(u, v), max(u, v)))
    return sorted(chosen)


# --- Nullmodell 2: Konfigurationsmodell per Kanten-Doppeltausch (Maslov und Sneppen 2002) -----------------------------------------------------------------


def try_double_swap(edges, nbrs, i, j, flip):
    """Ein Tauschversuch auf den Kanten i und j: (a,b), (c,d) -> (a,d), (c,b); mit `flip` wird die zweite Kante vorher umgedreht, also (a,b), (d,c) -> (a,c), (d,b). Beide Paarungen werden gebraucht:
    paart man immer nach (kleiner, größerer) Endpunkt nur in einer Richtung, erreicht die Kette nur einen Teil der Graphen mit dieser Gradfolge und ist nicht gleichverteilt (das verzerrt etwa
    die Assortativität des Nullmodells stark). Gibt True zurück, wenn getauscht wurde."""
    if i == j:
        return False
    a, b = edges[i]
    c, d = edges[j]
    if flip:
        c, d = d, c
    if len({a, b, c, d}) < 4:
        return False
    if d in nbrs[a] or b in nbrs[c]:
        return False                                            # würde eine Mehrfachkante erzeugen -- verwerfen, neu ziehen
    nbrs[a].discard(b)
    nbrs[b].discard(a)
    nbrs[c].discard(d)
    nbrs[d].discard(c)
    nbrs[a].add(d)
    nbrs[d].add(a)
    nbrs[c].add(b)
    nbrs[b].add(c)
    edges[i] = [min(a, d), max(a, d)]
    edges[j] = [min(c, b), max(c, b)]
    return True


def configuration_null(adj, n_swaps, seed):
    """Gradfolgen-erhaltende Randomisierung: `n_swaps` Versuche (nicht zwingend Erfolge). Je Versuch zwei zufällige Kanten (a,b) und (c,d) mit vier verschiedenen Knoten ziehen, mit einem Münzwurf die
    Richtung der zweiten Kante wählen und zu (a,d) und (c,b) tauschen, nur wenn beide neuen Kanten noch nicht existieren (sonst verwerfen und beim nächsten Versuch neu ziehen) - die Gradfolge
    (Multimenge) bleibt bei jedem einzelnen Tausch exakt unverändert, weil jeder Knoten dieselbe Zahl an Kantenenden behält, nur an einen anderen Partner umgehängt."""
    n = len(adj)
    nbrs = [set(a) for a in adj]
    edges = []
    for u in range(n):
        for v in adj[u]:
            if u < v:
                edges.append([u, v])
    rng = random.Random(int(seed) * 1_000_003 + 9241)
    m = len(edges)
    for _ in range(int(n_swaps)):
        if m < 2:
            break
        i, j = rng.randrange(m), rng.randrange(m)
        flip = rng.random() < 0.5
        try_double_swap(edges, nbrs, i, j, flip)
    return [(u, v) for u, v in edges]


# --- ω (Omega), Kleine-Welt-Kennzahl (Telesford u. a. 2011) -----------------------------------------------------------------------------------------------


def omega_watts_strogatz(c, c_lattice, l, l_rand):
    """ω = L_rand/L - C/C_lattice. ω nahe 0: klein-welt-artig (hohes Clustering wie ein Gitter UND kurze Wege wie ein Zufallsgraph). ω nahe -1: gitterartig (hohes Clustering, aber lange Wege).
    ω nahe +1: zufallsgraphartig (kurze Wege, aber kaum Clustering). Nur auf der Ring-Umverdrahtungs-Instanz sinnvoll definiert, weil dort C_lattice aus dem p=0-Fall bekannt ist."""
    if c_lattice == 0.0 or l == 0.0:
        return float("nan")
    return l_rand / l - c / c_lattice
