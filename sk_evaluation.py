"""Auswertung: Analyse einer Instanz (Clustering, Transitivität, mittlere Weglänge, Assortativität, Vergleich mit Erdős-Rényi- und Konfigurationsmodell-Nullmodell, ω wo definiert), Watts-Strogatz-
Umverdrahtungs-Sweep, Nullverteilung der Assortativität unter dem Konfigurationsmodell, Gradverteilungen nebeneinander."""

from dataclasses import dataclass
from functools import lru_cache

import sk_algorithm as A
import sk_constants as C
import sk_scenario as S


@dataclass
class Settings:
    kind: str = "city"                  # "city" | "ring" | "ba"
    # Betriebsnetz
    side: int = C.DEFAULT_SIDE
    blocked: float = C.DEFAULT_BLOCKED
    nettype: str = "grid"               # "grid" | "random"
    # Ring-Umverdrahtung
    n_ring: int = C.DEFAULT_N_RING
    k_ring: int = C.DEFAULT_K_RING
    p_rewire: float = C.DEFAULT_P_REWIRE
    # Skalenfreies Netz
    n_ba: int = C.DEFAULT_N_BA
    m_ba: int = C.DEFAULT_M_BA
    m0_ba: int = C.DEFAULT_M0_BA
    # gemeinsam
    seed: int = C.DEFAULT_SEED
    order: str = "fixed"                # ändert nie eine Kennzahl - nur die Wiedergabe-/Buchführungsreihenfolge
    n_swaps: int = C.DEFAULT_N_SWAPS    # Doppeltausch-Versuche fürs Konfigurationsmodell


@dataclass
class NullStats:
    avg_clustering: float
    transitivity: float
    avg_distance: float
    assortativity: float


@dataclass
class Analysis:
    n: int
    m: int
    degree: list
    local_clustering: list
    avg_clustering: float
    transitivity: float
    avg_distance: float
    connected: bool
    largest_cc_size: int
    assortativity: float
    er: NullStats                       # Erdős-Rényi G(n,m): zerstört auch die Gradfolge
    config: NullStats                   # eine Konfigurationsmodell-Realisierung: Gradfolge exakt erhalten
    omega: float                        # nur beim Ring definiert (sonst NaN)
    c_lattice: float                    # nur beim Ring definiert (sonst NaN) - Referenzwert bei p=0


def instance(settings):
    if settings.kind == "city":
        return S.generate(settings.side, settings.blocked, settings.nettype, settings.seed)
    if settings.kind == "ring":
        return S.ring_lattice_instance(settings.n_ring, settings.k_ring, settings.p_rewire, settings.seed)
    if settings.kind == "ba":
        return S.barabasi_albert_instance(settings.n_ba, settings.m_ba, settings.m0_ba, settings.seed)
    raise ValueError(f"unbekannte Instanzart {settings.kind}")


def _largest_cc_size(adj):
    n = len(adj)
    seen = [False] * n
    best = 0
    for s in range(n):
        if seen[s]:
            continue
        dist, _ = A.bfs_distances(adj, s)
        comp = [v for v, d in enumerate(dist) if d >= 0]
        for v in comp:
            seen[v] = True
        best = max(best, len(comp))
    return best


def _null_stats(adj):
    return NullStats(A.average_clustering(adj), A.transitivity(adj), A.average_distance(adj), A.degree_assortativity(adj))


def analyse(settings):
    inst = instance(settings)
    adj = A.adjacency(inst.n, inst.edges, settings.order, settings.seed)
    degree = [len(a) for a in adj]
    local = A.clustering_coefficient(adj)
    avgc = A.average_clustering(adj)
    trans = A.transitivity(adj)
    avg_dist = A.average_distance(adj)
    largest = _largest_cc_size(adj)
    connected = largest == inst.n
    assort = A.degree_assortativity(adj)

    er_pairs = A.erdos_renyi_gnm(inst.n, inst.m, settings.seed)
    er_adj = A.adjacency(inst.n, er_pairs)
    er_stats = _null_stats(er_adj)

    config_pairs = A.configuration_null(adj, settings.n_swaps, settings.seed)
    config_adj = A.adjacency(inst.n, config_pairs)
    config_stats = _null_stats(config_adj)

    omega = c_lattice = float("nan")
    if settings.kind == "ring":
        lattice = S.ring_lattice_instance(settings.n_ring, settings.k_ring, 0.0, settings.seed)
        lattice_adj = A.adjacency(lattice.n, lattice.edges)
        c_lattice = A.average_clustering(lattice_adj)
        omega = A.omega_watts_strogatz(avgc, c_lattice, avg_dist, er_stats.avg_distance)

    a = Analysis(inst.n, inst.m, degree, local, avgc, trans, avg_dist, connected, largest, assort, er_stats, config_stats, omega, c_lattice)
    return inst, a


# --- Watts-Strogatz-Umverdrahtungs-Sweep: C(p)/C(0) und L(p)/L(0) über p (Abb. 2, Watts und Strogatz 1998) -----------------------------------------------


@lru_cache(maxsize=None)
def rewiring_sweep(n, k, seed, ps=C.P_SWEEP):
    ps = tuple(ps)
    base = S.ring_lattice_instance(n, k, 0.0, seed)
    base_adj = A.adjacency(base.n, base.edges)
    c0 = A.average_clustering(base_adj)
    l0 = A.average_distance(base_adj)
    rows = []
    for p in ps:
        inst = S.ring_lattice_instance(n, k, p, seed)
        adj = A.adjacency(inst.n, inst.edges)
        c = A.average_clustering(adj)
        length = A.average_distance(adj)
        rows.append({"p": p, "c": c, "l": length, "c_ratio": c / c0 if c0 else 0.0, "l_ratio": length / l0 if l0 else 0.0})
    return rows


# --- Nullverteilung der Assortativität unter dem Konfigurationsmodell (z-Wert des Original-r) -------------------------------------------------------------


def assortativity_null_distribution(adj, n_draws, n_swaps, seed):
    """`n_draws` unabhängige Konfigurationsmodell-Ziehungen (verschiedene Salt-Seeds), je der Assortativitätskoeffizient. Original-r dagegen als z-Wert."""
    r_orig = A.degree_assortativity(adj)
    draws = []
    for i in range(int(n_draws)):
        pairs = A.configuration_null(adj, n_swaps, seed=int(seed) * 1_000_003 + i)
        d_adj = A.adjacency(len(adj), pairs)
        draws.append(A.degree_assortativity(d_adj))
    valid = [r for r in draws if r == r]                            # NaN herausfiltern (regulärer Graph -> konstanter Grad in jeder Ziehung)
    mean = sum(valid) / len(valid) if valid else float("nan")
    var = sum((r - mean) ** 2 for r in valid) / len(valid) if valid else float("nan")
    std = var ** 0.5 if valid else float("nan")
    z = (r_orig - mean) / std if valid and std > 0 else float("nan")
    return {"original": r_orig, "draws": draws, "mean": mean, "std": std, "z": z}


# --- Gradverteilungen nebeneinander: Betriebsnetz, Erdős-Rényi (gleiches n, m), skalenfreies Netz ----------------------------------------------------------


def degree_histograms(settings):
    city = S.generate(settings.side, settings.blocked, settings.nettype, settings.seed)
    city_adj = A.adjacency(city.n, city.edges)
    city_deg = [len(a) for a in city_adj]

    er_pairs = A.erdos_renyi_gnm(city.n, city.m, settings.seed)
    er_adj = A.adjacency(city.n, er_pairs)
    er_deg = [len(a) for a in er_adj]

    ba = S.barabasi_albert_instance(settings.n_ba, settings.m_ba, settings.m0_ba, settings.seed)
    ba_adj = A.adjacency(ba.n, ba.edges)
    ba_deg = [len(a) for a in ba_adj]

    return {"city": city_deg, "er": er_deg, "ba": ba_deg}


def heavy_tail_ratio(degree_sequence):
    """Verhältnis Maximalgrad/mittlerer Grad - informeller Hinweis auf einen langschwänzigen Grad (KEIN formaler Machtgesetz-Test, s. Clauset u. a. 2009 in den Grenzen)."""
    if not degree_sequence:
        return float("nan")
    mean_deg = sum(degree_sequence) / len(degree_sequence)
    return max(degree_sequence) / mean_deg if mean_deg > 0 else float("nan")
