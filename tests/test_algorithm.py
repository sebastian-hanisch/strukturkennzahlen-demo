"""Zentrale Korrektheits-Kette (9 Punkte, gegen networkx als Gegenprobe, vor jeder Messung):
1) Lokaler/mittlerer Clustering-Koeffizient und Transitivität == networkx auf >= 300 Instanzen.
2) Mittlere Weglänge == networkx.average_shortest_path_length auf >= 200 ZUSAMMENHÄNGENDEN Instanzen; bei unzusammenhängenden nur größte Komponente verglichen.
3) Assortativität == networkx.degree_pearson_correlation_coefficient auf >= 200 Instanzen inkl. Stern (r=-1) und regulärem Graphen (NaN).
4) Erdős-Rényi: exakte Kantenzahl, keine Mehrfachkanten/Schleifen; Einschlusshäufigkeit nahe der theoretischen Wahrscheinlichkeit.
5) Konfigurationsmodell: Gradfolge exakt unverändert vor/nach jedem Tausch und nach vielen Versuchen, nie Mehrfachkante/Schleife, über >= 200 Instanzen.
6) Barabási-Albert: exakte Kantenzahl, zusammenhängend, keine Mehrfachkanten (Wiederholung der Scenario-Kette hier als Teil der Algorithmus-Kette).
7) Ring-Gitter von Hand: C(p=0) == 3(k-2)/(4(k-1)) exakt für mehrere k.
8) ω-Formel gegen Handrechnung; Buchführung: Determinismus, Nachbarreihenfolge ändert nie eine Kennzahl.
9) Sonderfälle: n<=2, vollständiger Graph, Baum ohne Dreiecke, unzusammenhängend."""

import math

import networkx as nx
import pytest

import sk_algorithm as A
import sk_scenario as S


def _graph(inst_or_pair):
    if isinstance(inst_or_pair, tuple):
        n, pairs = inst_or_pair
    else:
        n, pairs = inst_or_pair.n, [(u, v) for u, v, _ in inst_or_pair.edges]
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(pairs)
    return g


def _city_instances():
    out = []
    for side in (3, 4, 5, 6, 7, 8):
        for nettype in S.C.NETTYPES:
            for blocked in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
                for seed in (1, 2, 3):
                    out.append(S.generate(side, blocked, nettype, seed))
    return out


def _ring_instances():
    out = []
    for n in (12, 20, 30, 41, 60):
        for k in (4, 6, 8, 10):
            if k // 2 > (n - 1) // 2:
                continue
            for p in (0.0, 0.05, 0.2, 0.5, 1.0):
                for seed in (1, 2, 3):
                    out.append(S.ring_lattice_instance(n, k, p, seed))
    return out


def _ba_instances():
    out = []
    for n in (15, 30, 50, 80):
        for m in (1, 2, 3):
            for m0 in (3, 4, 5):
                if m > m0 or m0 > n:
                    continue
                for seed in (1, 2, 3):
                    out.append(S.barabasi_albert_instance(n, m, m0, seed))
    return out


CITY = _city_instances()
RING = _ring_instances()
BA = _ba_instances()
ALL_INSTANCES = CITY + RING + BA


def _special():
    """n<=2, vollständiger Graph, Baum (kreisfrei), unzusammenhängend, Stern, regulärer Graph."""
    return {
        "n0": (0, []),
        "n1": (1, []),
        "n2_no_edge": (2, []),
        "n2_edge": (2, [(0, 1)]),
        "path3": (3, [(0, 1), (1, 2)]),
        "triangle": (3, [(0, 1), (1, 2), (0, 2)]),
        "tree": (7, [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]),
        "complete5": (5, [(i, j) for i in range(5) for j in range(i + 1, 5)]),
        "star9": (9, [(0, i) for i in range(1, 9)]),
        "cycle6": (6, [(i, (i + 1) % 6) for i in range(6)]),
        "disconnected": (8, [(0, 1), (1, 2), (0, 2), (3, 4)]),
    }


SPECIAL = _special()


# --- 1. Clustering/Transitivität == networkx ------------------------------------------------------------------------------------------------------------


def test_clustering_and_transitivity_match_networkx_on_many_instances():
    assert len(ALL_INSTANCES) >= 300
    checked = 0
    for inst in ALL_INSTANCES:
        g = _graph(inst)
        adj = A.adjacency(inst.n, inst.edges)
        local = A.clustering_coefficient(adj)
        want_local = nx.clustering(g)
        for v in range(inst.n):
            assert local[v] == pytest.approx(want_local[v], abs=1e-9)
        assert A.average_clustering(adj) == pytest.approx(nx.average_clustering(g), abs=1e-9)
        assert A.transitivity(adj) == pytest.approx(nx.transitivity(g), abs=1e-9)
        checked += 1
    assert checked >= 300


def test_clustering_degree_0_1_gives_zero():
    for n, pairs in (SPECIAL["path3"], SPECIAL["star9"]):
        pass
    adj = A.adjacency(4, [(0, 1)])                                # Knoten 2, 3 haben Grad 0; Knoten 0, 1 haben Grad 1
    local = A.clustering_coefficient(adj)
    assert local == [0.0, 0.0, 0.0, 0.0]


# --- 2. Mittlere Weglänge == networkx.average_shortest_path_length (nur zusammenhängend) -----------------------------------------------------------------


def _connected_instances():
    out = [inst for inst in CITY if nx.is_connected(_graph(inst))]
    out += RING                                                  # Ring-Instanzen sind per Konstruktion immer zusammenhängend (k>=1 verbindet den ganzen Kreis)
    out += BA                                                     # BA ist per Konstruktion immer zusammenhängend
    return out


CONNECTED = _connected_instances()


def test_average_distance_matches_networkx_on_connected_instances():
    assert len(CONNECTED) >= 200
    checked = 0
    for inst in CONNECTED:
        g = _graph(inst)
        adj = A.adjacency(inst.n, inst.edges)
        got = A.average_distance(adj)
        want = nx.average_shortest_path_length(g)
        assert got == pytest.approx(want, abs=1e-9)
        checked += 1
    assert checked >= 200


def test_average_distance_on_disconnected_compares_only_the_largest_component():
    n, pairs = SPECIAL["disconnected"]
    adj = A.adjacency(n, [(u, v, 1.0) for u, v in pairs])
    g = _graph((n, pairs))
    largest = max(nx.connected_components(g), key=len)
    sub = sorted(largest)
    remap = {old: new for new, old in enumerate(sub)}
    sub_pairs = [(remap[u], remap[v]) for u, v in pairs if u in remap and v in remap]
    sub_adj = A.adjacency(len(sub), [(u, v, 1.0) for u, v in sub_pairs])
    got = A.average_distance(sub_adj)
    want = nx.average_shortest_path_length(g.subgraph(largest))
    assert got == pytest.approx(want, abs=1e-9)
    # average_distance auf dem GANZEN (unzusammenhängenden) Graphen ist wohldefiniert und schließt nur unerreichbare Paare aus
    whole = A.average_distance(adj)
    assert whole >= 0.0


# --- 3. Assortativität == networkx.degree_pearson_correlation_coefficient ---------------------------------------------------------------------------------


def test_assortativity_matches_networkx_on_many_instances():
    assert len(ALL_INSTANCES) >= 200
    checked = 0
    for inst in ALL_INSTANCES:
        if inst.m == 0:
            continue
        g = _graph(inst)
        adj = A.adjacency(inst.n, inst.edges)
        got = A.degree_assortativity(adj)
        want = nx.degree_pearson_correlation_coefficient(g)
        if math.isnan(want):
            assert math.isnan(got)
        else:
            assert got == pytest.approx(want, abs=1e-6)
        checked += 1
    assert checked >= 200


def test_assortativity_star_is_exactly_minus_one():
    n, pairs = SPECIAL["star9"]
    adj = A.adjacency(n, [(u, v, 1.0) for u, v in pairs])
    got = A.degree_assortativity(adj)
    g = _graph((n, pairs))
    want = nx.degree_pearson_correlation_coefficient(g)
    assert got == pytest.approx(-1.0, abs=1e-9)
    assert got == pytest.approx(want, abs=1e-9)


def test_assortativity_regular_graph_is_nan_like_networkx():
    n, pairs = SPECIAL["cycle6"]                                   # regulär: jeder Knoten Grad 2
    adj = A.adjacency(n, [(u, v, 1.0) for u, v in pairs])
    got = A.degree_assortativity(adj)
    g = _graph((n, pairs))
    want = nx.degree_pearson_correlation_coefficient(g)
    assert math.isnan(got) and math.isnan(want)


# --- 4. Erdős-Rényi: exakte Kantenzahl, keine Mehrfachkanten/Schleifen, Einschlusshäufigkeit ------------------------------------------------------------


def test_erdos_renyi_exact_edge_count_no_self_loops_no_multi():
    for n in (5, 10, 20, 50):
        for m in (3, 10, 25):
            max_m = n * (n - 1) // 2
            if m > max_m:
                continue
            for seed in range(1, 6):
                pairs = A.erdos_renyi_gnm(n, m, seed)
                assert len(pairs) == m
                assert len(set(pairs)) == m
                assert all(u != v for u, v in pairs)
                assert all(u < v for u, v in pairs)


def test_erdos_renyi_edge_inclusion_frequency_matches_theory():
    n, m, trials = 8, 10, 4000
    max_m = n * (n - 1) // 2
    target = (2, 5)                                                 # ein beliebiges festes Paar
    hits = 0
    for seed in range(trials):
        pairs = set(A.erdos_renyi_gnm(n, m, seed))
        if target in pairs:
            hits += 1
    theory = m / max_m
    empirical = hits / trials
    assert abs(empirical - theory) < 0.03


# --- 5. Konfigurationsmodell: Gradfolge exakt erhalten, nie Mehrfachkante/Schleife ------------------------------------------------------------------------


def _degree_multiset(pairs, n):
    deg = [0] * n
    for u, v in pairs:
        deg[u] += 1
        deg[v] += 1
    return sorted(deg)


def test_configuration_null_preserves_degree_sequence_exactly():
    checked = 0
    for inst in (CITY + RING + BA)[::2]:
        adj = A.adjacency(inst.n, inst.edges)
        want_deg = _degree_multiset([(u, v) for u, v, _ in inst.edges], inst.n)
        for n_swaps in (0, 1, 5, 50):
            pairs = A.configuration_null(adj, n_swaps, seed=inst.seed)
            assert _degree_multiset(pairs, inst.n) == want_deg
            assert len(set(pairs)) == len(pairs)
            assert all(u != v for u, v in pairs)
        checked += 1
    assert checked >= 200


def test_configuration_null_single_swap_preserves_degree_sequence_step_by_step():
    """Buchführung nach JEDEM einzelnen Tausch, nicht nur am Ende."""
    inst = S.generate(8, 0.2, "grid", 3)
    adj = A.adjacency(inst.n, inst.edges)
    want_deg = _degree_multiset([(u, v) for u, v, _ in inst.edges], inst.n)
    for k in range(1, 30):
        pairs = A.configuration_null(adj, k, seed=1)
        assert _degree_multiset(pairs, inst.n) == want_deg


# --- 6. Barabási-Albert (Wiederholung als Teil der Algorithmus-Kette) --------------------------------------------------------------------------------------


def test_ba_edge_count_connected_no_multi_via_algorithm_module():
    for inst in BA:
        assert inst.m == inst.m0_ba + (inst.n - inst.m0_ba) * inst.m_ba
        g = _graph(inst)
        assert nx.is_connected(g)
        assert g.number_of_edges() == inst.m


# --- 7. Ring-Gitter von Hand: C(p=0) == 3(k-2)/(4(k-1)) -----------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("k", [4, 6, 8, 10, 12, 16, 20])
def test_ring_lattice_clustering_matches_closed_form(k):
    """k ist hier der GESAMTGRAD (wie bei Watts und Strogatz 1998 selbst) -- die geschlossene Form C = 3(k-2)/(4(k-1)) ist mit dieser Konvention definiert, nicht mit "Nachbarn je Seite"."""
    n = 10 * k + 1                                                  # groß genug, um Randeffekte durch Überlappung auszuschließen
    inst = S.ring_lattice_instance(n, k, 0.0, 1)
    adj = A.adjacency(inst.n, inst.edges)
    c = A.average_clustering(adj)
    want = 3 * (k - 2) / (4 * (k - 1))
    assert c == pytest.approx(want, abs=1e-9)
    # jeder einzelne Knoten hat denselben lokalen Koeffizienten (Ring-Gitter ist knoten-transitiv)
    local = A.clustering_coefficient(adj)
    assert all(v == pytest.approx(want, abs=1e-9) for v in local)


def test_ring_lattice_k2_has_zero_clustering():
    """k=2 (Gesamtgrad, 1 Nachbar je Seite): Nachbarn eines Knotens sind selbst nicht benachbart (kein Dreieck möglich) -- Formel ergibt 0."""
    inst = S.ring_lattice_instance(21, 2, 0.0, 1)
    adj = A.adjacency(inst.n, inst.edges)
    assert A.average_clustering(adj) == pytest.approx(0.0, abs=1e-9)


# --- 8. ω-Formel und Buchführung -----------------------------------------------------------------------------------------------------------------------------


def test_omega_formula_by_hand():
    assert A.omega_watts_strogatz(c=0.6, c_lattice=0.6, l=2.0, l_rand=2.0) == pytest.approx(0.0)
    assert A.omega_watts_strogatz(c=0.6, c_lattice=0.6, l=1.0, l_rand=2.0) == pytest.approx(2.0 / 1.0 - 0.6 / 0.6)
    assert A.omega_watts_strogatz(c=0.3, c_lattice=0.6, l=2.0, l_rand=4.0) == pytest.approx(4.0 / 2.0 - 0.3 / 0.6)
    assert math.isnan(A.omega_watts_strogatz(c=0.0, c_lattice=0.0, l=1.0, l_rand=1.0))


def test_omega_on_ring_instance_matches_hand_reference():
    n, k, seed = 61, 4, 5
    lattice = S.ring_lattice_instance(n, k, 0.0, seed)
    lattice_adj = A.adjacency(lattice.n, lattice.edges)
    c_lattice = A.average_clustering(lattice_adj)
    assert c_lattice == pytest.approx(3 * (k - 2) / (4 * (k - 1)), abs=1e-9)
    rewired = S.ring_lattice_instance(n, k, 0.1, seed)
    r_adj = A.adjacency(rewired.n, rewired.edges)
    c = A.average_clustering(r_adj)
    length = A.average_distance(r_adj)
    er_pairs = A.erdos_renyi_gnm(rewired.n, rewired.m, seed)
    er_adj = A.adjacency(rewired.n, er_pairs)
    l_rand = A.average_distance(er_adj)
    got = A.omega_watts_strogatz(c, c_lattice, length, l_rand)
    hand = l_rand / length - c / c_lattice
    assert got == pytest.approx(hand, abs=1e-12)


def test_neighbour_order_never_changes_a_structural_measure():
    for inst in ALL_INSTANCES[::11]:
        adj_fixed = A.adjacency(inst.n, inst.edges, "fixed")
        adj_shuffled = A.adjacency(inst.n, inst.edges, "shuffled", seed=inst.seed + 1)
        assert A.clustering_coefficient(adj_fixed) == pytest.approx(A.clustering_coefficient(adj_shuffled), abs=1e-9)
        assert A.average_clustering(adj_fixed) == pytest.approx(A.average_clustering(adj_shuffled), abs=1e-9)
        assert A.transitivity(adj_fixed) == pytest.approx(A.transitivity(adj_shuffled), abs=1e-9)
        assert A.average_distance(adj_fixed) == pytest.approx(A.average_distance(adj_shuffled), abs=1e-9)
        got_fixed, got_shuffled = A.degree_assortativity(adj_fixed), A.degree_assortativity(adj_shuffled)
        if math.isnan(got_fixed):
            assert math.isnan(got_shuffled)
        else:
            assert got_fixed == pytest.approx(got_shuffled, abs=1e-9)


def test_determinism():
    inst = S.generate(8, 0.3, "grid", 5)
    adj1 = A.adjacency(inst.n, inst.edges)
    adj2 = A.adjacency(inst.n, inst.edges)
    assert A.clustering_coefficient(adj1) == A.clustering_coefficient(adj2)
    assert A.average_distance(adj1) == A.average_distance(adj2)
    assert A.configuration_null(adj1, 100, seed=1) == A.configuration_null(adj2, 100, seed=1)
    assert A.erdos_renyi_gnm(20, 30, seed=1) == A.erdos_renyi_gnm(20, 30, seed=1)


def test_invalid_order_raises():
    with pytest.raises(ValueError):
        A.adjacency(3, [], "sorted")


# --- 9. Sonderfälle -------------------------------------------------------------------------------------------------------------------------------------------


def test_n0_n1_n2():
    adj0 = A.adjacency(0, [])
    assert A.clustering_coefficient(adj0) == []
    assert A.average_clustering(adj0) == 0.0
    assert A.transitivity(adj0) == 0.0
    assert A.average_distance(adj0) == 0.0

    adj1 = A.adjacency(1, [])
    assert A.clustering_coefficient(adj1) == [0.0]
    assert A.average_distance(adj1) == 0.0

    adj2 = A.adjacency(2, [(0, 1, 1.0)])
    assert A.clustering_coefficient(adj2) == [0.0, 0.0]
    assert A.average_distance(adj2) == pytest.approx(1.0)
    assert math.isnan(A.degree_assortativity(adj2))                # konstanter Grad (beide 1)


def test_complete_graph_clustering_is_one_transitivity_is_one():
    n, pairs = SPECIAL["complete5"]
    adj = A.adjacency(n, [(u, v, 1.0) for u, v in pairs])
    local = A.clustering_coefficient(adj)
    assert all(v == pytest.approx(1.0) for v in local)
    assert A.average_clustering(adj) == pytest.approx(1.0)
    assert A.transitivity(adj) == pytest.approx(1.0)
    assert A.average_distance(adj) == pytest.approx(1.0)


def test_tree_has_zero_clustering_and_transitivity():
    n, pairs = SPECIAL["tree"]
    adj = A.adjacency(n, [(u, v, 1.0) for u, v in pairs])
    assert A.average_clustering(adj) == pytest.approx(0.0)
    assert A.transitivity(adj) == pytest.approx(0.0)                # kreisfrei -- keine Dreiecke möglich


def test_disconnected_graph_does_not_crash_and_average_distance_is_finite():
    n, pairs = SPECIAL["disconnected"]
    adj = A.adjacency(n, [(u, v, 1.0) for u, v in pairs])
    d = A.average_distance(adj)
    assert d >= 0.0 and math.isfinite(d)
    A.degree_assortativity(adj)                                     # läuft ohne Fehler durch
