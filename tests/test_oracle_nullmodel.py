"""Unabhängiges Orakel für das Konfigurationsmodell (Kanten-Doppeltausch) und die Strukturkennzahlen.

Orakel 1 (exakt): auf winzigen Gradfolgen werden ALLE einfachen Graphen aufgezählt und die Übergangsmatrix EINES Tauschversuchs aus `try_double_swap` aufgebaut (jedes Indexpaar i, j und
jede Richtung gleich wahrscheinlich, wie in `configuration_null`). Die Kette muss irreduzibel sein und die Gleichverteilung über alle Graphen der Gradfolge als stationäre Verteilung haben.
Die frühere Fassung paarte die Kanten immer als (kleiner, größerer) Endpunkt (nur eine Richtung): das ist nicht irreduzibel und nicht gleichverteilt (Negativkontrolle unten) und ließ das
skalenfreie Netz fälschlich "signifikant weniger disassortativ" aussehen (z=+25 statt z=-2).
Orakel 2 (statistisch): Nullverteilung der Assortativität gegen `networkx.double_edge_swap`. Orakel 3: Kennzahlen gegen networkx bzw. Floyd-Warshall (mittlere Weglänge)."""

import itertools
import math
import random
import warnings

import networkx as nx
import numpy as np
import pytest

import sk_algorithm as A
import sk_scenario as S


def _graphs_with_degrees(deg):
    n = len(deg)
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    out = []
    for comb in itertools.combinations(pairs, sum(deg) // 2):
        d = [0] * n
        for u, v in comb:
            d[u] += 1
            d[v] += 1
        if d == list(deg):
            out.append(frozenset(comb))
    return out


def _transition_matrix(deg, flips):
    gs = _graphs_with_degrees(deg)
    idx = {g: k for k, g in enumerate(gs)}
    n = len(deg)
    P = np.zeros((len(gs), len(gs)))
    for g in gs:
        edges0 = [list(e) for e in sorted(g)]
        m = len(edges0)
        for i in range(m):
            for j in range(m):
                for flip in flips:
                    edges = [list(e) for e in edges0]
                    nbrs = [set() for _ in range(n)]
                    for u, v in edges:
                        nbrs[u].add(v)
                        nbrs[v].add(u)
                    A.try_double_swap(edges, nbrs, i, j, flip)
                    P[idx[g], idx[frozenset(tuple(e) for e in edges)]] += 1.0 / (m * m * len(flips))
    return gs, P


def _irreducible(P):
    reach = np.linalg.matrix_power((P > 0).astype(float) + np.eye(len(P)), len(P)) > 0
    return bool(reach.all())


DEGS = [(2, 2, 2, 2, 1, 1), (3, 2, 2, 1, 1, 1), (3, 3, 2, 2, 2, 2)]


@pytest.mark.parametrize("deg", DEGS)
def test_double_edge_swap_chain_is_irreducible_and_uniform(deg):
    gs, P = _transition_matrix(deg, (False, True))
    assert np.allclose(P.sum(axis=1), 1.0)
    uniform = np.full(len(gs), 1.0 / len(gs))
    assert np.allclose(uniform @ P, uniform, atol=1e-12)         # Gleichverteilung ist stationär
    assert _irreducible(P)                                       # jeder Graph der Gradfolge ist erreichbar


def test_oracle_detects_the_one_sided_pairing_of_the_old_version():
    """Negativkontrolle: nur eine Paarung (alte Fassung) ist nicht irreduzibel und hat nicht die Gleichverteilung als stationäre Verteilung."""
    gs, P = _transition_matrix((3, 2, 2, 1, 1, 1), (False,))
    uniform = np.full(len(gs), 1.0 / len(gs))
    assert not _irreducible(P) and not np.allclose(uniform @ P, uniform, atol=1e-9)


def test_configuration_null_assortativity_matches_networkx_double_edge_swap():
    inst = S.barabasi_albert_instance(120, 2, 4, 7)
    adj = A.adjacency(inst.n, inst.edges)
    g0 = nx.Graph()
    g0.add_nodes_from(range(inst.n))
    g0.add_edges_from((u, v) for u, v, _ in inst.edges)
    ours = [A.degree_assortativity(A.adjacency(inst.n, A.configuration_null(adj, 3000, 100 + i))) for i in range(40)]
    ref = []
    for i in range(40):
        g = g0.copy()
        nx.double_edge_swap(g, nswap=900, max_tries=100000, seed=i)
        ref.append(nx.degree_pearson_correlation_coefficient(g))
    se = math.sqrt(np.var(ours) / 40 + np.var(ref) / 40)
    assert abs(np.mean(ours) - np.mean(ref)) < 4 * se + 0.01


def test_structure_measures_against_networkx_and_floyd_warshall():
    rng = random.Random(5)
    for _ in range(150):
        n = rng.randint(1, 14)
        p = rng.choice([0, 0.1, 0.25, 0.5, 1.0])
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n) if rng.random() < p]
        g = nx.Graph()
        g.add_nodes_from(range(n))
        g.add_edges_from(pairs)
        adj = A.adjacency(n, pairs)
        assert A.average_clustering(adj) == pytest.approx(nx.average_clustering(g), abs=1e-12)
        assert A.transitivity(adj) == pytest.approx(nx.transitivity(g), abs=1e-12)
        dist = np.full((n, n), np.inf)
        np.fill_diagonal(dist, 0)
        for u, v in pairs:
            dist[u, v] = dist[v, u] = 1
        for k in range(n):
            dist = np.minimum(dist, dist[:, [k]] + dist[[k], :])
        d = dist[np.triu_indices(n, 1)]
        d = d[np.isfinite(d)]
        assert A.average_distance(adj) == pytest.approx(d.mean() if len(d) else 0.0, abs=1e-12)
        if pairs:
            r = A.degree_assortativity(adj)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                want = nx.degree_pearson_correlation_coefficient(g)
            assert (math.isnan(r) and math.isnan(want)) or r == pytest.approx(want, abs=1e-9)
