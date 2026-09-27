"""Rauchtests der drei Instanzen: Betriebsnetz (Raster/Zufallsgraph), Ring-Umverdrahtung, skalenfreies Netz."""

import networkx as nx
import pytest

import sk_scenario as S


def _graph(inst):
    g = nx.Graph()
    g.add_nodes_from(range(inst.n))
    g.add_edges_from([(u, v) for u, v, _ in inst.edges])
    return g


# --- Betriebsnetz (wie centrality-demo) --------------------------------------------------------------------------------------------------------------


def test_generate_grid_basic():
    inst = S.generate(6, 0.0, "grid", 1)
    assert inst.n == 36 and inst.kind == "city" and inst.nettype == "grid"
    assert inst.m == len(S.grid_edges(6))
    for u, v, w in inst.edges:
        assert u < v and w > 0


def test_generate_blocks_the_right_share():
    inst = S.generate(10, 0.3, "grid", 5)
    total = len(S.grid_edges(10))
    assert inst.m == total - int(round(0.3 * total))
    assert len(inst.blocked_edges) == int(round(0.3 * total))


def test_generate_random_same_edge_count_no_blocked_edges():
    inst_grid = S.generate(8, 0.4, "grid", 3)
    inst_rand = S.generate(8, 0.4, "random", 3)
    assert inst_rand.m == inst_grid.m
    assert inst_rand.blocked_edges == ()


def test_generate_invalid_nettype_or_side_raises():
    with pytest.raises(ValueError):
        S.generate(6, 0.0, "diagonal", 1)
    with pytest.raises(ValueError):
        S.generate(1, 0.0, "grid", 1)


def test_generate_is_deterministic():
    a = S.generate(9, 0.35, "grid", 42)
    b = S.generate(9, 0.35, "grid", 42)
    assert a.edges == b.edges and (a.xy == b.xy).all()


# --- Ring-Umverdrahtung -------------------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("n,k", [(20, 4), (20, 6), (30, 8), (41, 10)])
def test_ring_lattice_edge_count_and_degree(n, k):
    inst = S.ring_lattice_instance(n, k, 0.0, 1)
    assert inst.n == n and inst.m == n * k // 2
    g = _graph(inst)
    assert all(d == k for _, d in g.degree())


@pytest.mark.parametrize("p", [0.0, 0.001, 0.1, 0.5, 1.0])
def test_ring_lattice_rewiring_preserves_edge_count_no_self_loops_no_multi(p):
    for seed in range(1, 8):
        inst = S.ring_lattice_instance(40, 4, p, seed)
        assert inst.m == 40 * 4 // 2
        pairs = [(u, v) for u, v, _ in inst.edges]
        assert len(set(pairs)) == len(pairs)                    # keine Mehrfachkanten
        assert all(u != v for u, v in pairs)                     # keine Selbstloops
        assert all(u < v for u, v in pairs)


def test_ring_lattice_p0_is_a_pure_lattice():
    inst = S.ring_lattice_instance(24, 6, 0.0, 7)
    want = {(i, (i + j) % 24) for i in range(24) for j in range(1, 4)}
    want = {(min(u, v), max(u, v)) for u, v in want}
    got = {(u, v) for u, v, _ in inst.edges}
    assert got == want


def test_ring_lattice_invalid_params_raise():
    with pytest.raises(ValueError):
        S.ring_lattice_instance(2, 2, 0.0, 1)
    with pytest.raises(ValueError):
        S.ring_lattice_instance(10, 12, 0.0, 1)             # k zu groß fuer n
    with pytest.raises(ValueError):
        S.ring_lattice_instance(10, 3, 0.0, 1)              # k ungerade
    with pytest.raises(ValueError):
        S.ring_lattice_instance(10, 4, 1.5, 1)


def test_ring_lattice_is_deterministic():
    a = S.ring_lattice_instance(30, 6, 0.2, 5)
    b = S.ring_lattice_instance(30, 6, 0.2, 5)
    assert a.edges == b.edges


# --- Skalenfreies Netz ---------------------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("n,m,m0", [(20, 1, 3), (50, 2, 4), (80, 3, 5), (100, 4, 8)])
def test_ba_exact_edge_count_connected_no_multi(n, m, m0):
    for seed in range(1, 5):
        inst = S.barabasi_albert_instance(n, m, m0, seed)
        assert inst.n == n
        assert inst.m == m0 + (n - m0) * m
        pairs = [(u, v) for u, v, _ in inst.edges]
        assert len(set(pairs)) == len(pairs)
        assert all(u != v for u, v in pairs)
        g = _graph(inst)
        assert nx.is_connected(g)


def test_ba_invalid_params_raise():
    with pytest.raises(ValueError):
        S.barabasi_albert_instance(20, 1, 2, 1)             # m0 < 3
    with pytest.raises(ValueError):
        S.barabasi_albert_instance(20, 5, 3, 1)             # m > m0
    with pytest.raises(ValueError):
        S.barabasi_albert_instance(3, 1, 4, 1)              # n < m0


def test_ba_is_deterministic():
    a = S.barabasi_albert_instance(60, 2, 4, 3)
    b = S.barabasi_albert_instance(60, 2, 4, 3)
    assert a.edges == b.edges
