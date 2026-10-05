"""Jede Zahl aus README und sk_constants-Kommentar, nachgerechnet über die echten Auswertungsfunktionen."""

import pytest

import sk_algorithm as A
import sk_constants as C
import sk_evaluation as ev


def test_grid_is_always_triangle_free():
    """Bipartit -> C=T=0 EXAKT, nicht nur im Median - ueber mehrere Seeds/Sperranteile."""
    for side in (6, 8, 10, 12):
        for blocked in (0.0, 0.1, 0.2, 0.3, 0.5):
            for seed in (1, 2, 3):
                inst, a = ev.analyse(ev.Settings(kind="city", side=side, blocked=blocked, nettype="grid", seed=seed))
                assert a.avg_clustering == 0.0 and a.transitivity == 0.0


def test_watts_strogatz_transition_numbers():
    rows = {r["p"]: r for r in ev.rewiring_sweep(200, 8, 35)}
    assert round(rows[0.001]["c_ratio"], 4) == 0.9959
    assert round(rows[0.001]["l_ratio"], 4) == 0.9112
    assert round(rows[0.01]["c_ratio"], 4) == 0.9751
    assert round(rows[0.01]["l_ratio"], 4) == 0.5300
    assert round(rows[0.1]["l_ratio"], 4) == 0.2832
    assert round(rows[0.1]["c_ratio"], 4) == 0.7372


def test_watts_strogatz_length_drops_before_clustering_monotonically_in_p():
    rows = ev.rewiring_sweep(200, 8, 35)
    c_ratios = [r["c_ratio"] for r in rows]
    l_ratios = [r["l_ratio"] for r in rows]
    assert c_ratios == sorted(c_ratios, reverse=True)               # monoton fallend in p
    assert l_ratios == sorted(l_ratios, reverse=True)
    # im "kleine Welt"-Fenster (kleines bis moderates p) ist die relative Weglaenge schon staerker gefallen als das Clustering;
    # bei sehr grossem p (nahe am reinen Zufallsgraph) faellt auch das Clustering unter L/L0, das ist keine kleine-Welt-Situation mehr
    for r in rows:
        if 0.0 < r["p"] <= 0.1:
            assert r["l_ratio"] <= r["c_ratio"]


def test_heavy_tail_ratios():
    settings = ev.Settings(kind="city", side=10, blocked=0.2, nettype="grid", n_ba=200, m_ba=2, m0_ba=4, seed=35)
    hist = ev.degree_histograms(settings)
    assert round(ev.heavy_tail_ratio(hist["city"]), 2) == 1.39
    assert round(ev.heavy_tail_ratio(hist["er"]), 2) == 2.78
    assert round(ev.heavy_tail_ratio(hist["ba"]), 2) == 8.84


def test_assortativity_z_values():
    cases = [("city", ev.Settings(kind="city", side=10, blocked=0.2, nettype="grid", seed=35), 1.51),
             ("ring", ev.Settings(kind="ring", n_ring=200, k_ring=8, p_rewire=0.01, seed=35), -1.08),
             ("ba", ev.Settings(kind="ba", n_ba=200, m_ba=2, m0_ba=4, seed=35), -1.88)]
    for label, settings, want_z in cases:
        inst = ev.instance(settings)
        adj = A.adjacency(inst.n, inst.edges)
        d = ev.assortativity_null_distribution(adj, C.N_DRAWS_ASSORT, C.DEFAULT_N_SWAPS, settings.seed)
        assert d["z"] == pytest.approx(want_z, abs=0.05), label


def test_ba_disassortativity_is_mostly_explained_by_its_degree_sequence():
    """Die Disassortativitaet des skalenfreien Netzes folgt weitgehend aus der Gradfolge: Konfigurationsmodell-Mittel -0.11, z=-1.88 (frueher z=+25 durch einseitig gepaarten Doppeltausch)."""
    settings = ev.Settings(kind="ba", n_ba=200, m_ba=2, m0_ba=4, seed=35)
    inst = ev.instance(settings)
    adj = A.adjacency(inst.n, inst.edges)
    d = ev.assortativity_null_distribution(adj, C.N_DRAWS_ASSORT, C.DEFAULT_N_SWAPS, settings.seed)
    assert d["mean"] == pytest.approx(-0.1126, abs=0.002)
    assert abs(d["z"]) < 2.0                                          # nicht signifikant: mit der Gradfolge verträglich


def test_ring_lattice_closed_form_several_k():
    for k in (4, 6, 8, 10, 12, 16, 20):
        n = 10 * k + 1
        inst = ev.S.ring_lattice_instance(n, k, 0.0, 1)
        adj = A.adjacency(inst.n, inst.edges)
        c = A.average_clustering(adj)
        assert c == pytest.approx(3 * (k - 2) / (4 * (k - 1)), abs=1e-9)


def test_config_model_destroys_ring_clustering():
    inst, a = ev.analyse(ev.Settings(kind="ring", n_ring=200, k_ring=8, p_rewire=0.0, seed=35, n_swaps=C.DEFAULT_N_SWAPS))
    assert round(a.avg_clustering, 4) == 0.6429
    assert round(a.config.avg_clustering, 4) == 0.0268
    assert a.config.avg_clustering < a.avg_clustering / 10           # Groessenordnung zerstoert
