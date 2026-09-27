"""Rauchtests der Auswertung: analyse (alle drei Instanzarten), rewiring_sweep, assortativity_null_distribution, degree_histograms, heavy_tail_ratio."""

import math

import pytest

import sk_algorithm as A
import sk_constants as C
import sk_evaluation as ev


def test_analyse_city_default():
    inst, a = ev.analyse(ev.Settings(kind="city", side=8, blocked=0.2, nettype="grid", seed=1))
    assert a.n == 64 and a.m == inst.m
    assert len(a.degree) == a.n and len(a.local_clustering) == a.n
    assert a.avg_clustering == pytest.approx(0.0)                  # Raster ist bipartit -- strukturell dreieckfrei
    assert a.transitivity == pytest.approx(0.0)
    assert math.isnan(a.omega) and math.isnan(a.c_lattice)          # nur beim Ring definiert


def test_analyse_ring_default_defines_omega():
    inst, a = ev.analyse(ev.Settings(kind="ring", n_ring=60, k_ring=8, p_rewire=0.05, seed=1, n_swaps=2000))
    assert a.n == 60 and a.connected
    assert not math.isnan(a.omega) and not math.isnan(a.c_lattice)
    assert a.c_lattice == pytest.approx(3 * (8 - 2) / (4 * (8 - 1)), abs=1e-9)


def test_analyse_ba_default():
    inst, a = ev.analyse(ev.Settings(kind="ba", n_ba=60, m_ba=2, m0_ba=4, seed=1, n_swaps=2000))
    assert a.n == 60 and a.connected and a.m == 4 + (60 - 4) * 2
    assert math.isnan(a.omega)


def test_analyse_null_stats_config_preserves_degree_extrema():
    inst, a = ev.analyse(ev.Settings(kind="city", side=8, blocked=0.2, nettype="grid", seed=3, n_swaps=3000))
    settings = ev.Settings(kind="city", side=8, blocked=0.2, nettype="grid", seed=3, n_swaps=3000)
    adj = A.adjacency(inst.n, inst.edges)
    config_pairs = A.configuration_null(adj, settings.n_swaps, settings.seed)
    config_adj = A.adjacency(inst.n, config_pairs)
    config_deg = sorted(len(x) for x in config_adj)
    assert sorted(a.degree) == config_deg


def test_instance_invalid_kind_raises():
    with pytest.raises(ValueError):
        ev.instance(ev.Settings(kind="nope"))


# --- rewiring_sweep ------------------------------------------------------------------------------------------------------------------------------------


def test_rewiring_sweep_basic_shape_and_p0_ratio_is_one():
    rows = ev.rewiring_sweep(60, 8, 1, ps=(0.0, 0.1, 1.0))
    assert [r["p"] for r in rows] == [0.0, 0.1, 1.0]
    assert rows[0]["c_ratio"] == pytest.approx(1.0) and rows[0]["l_ratio"] == pytest.approx(1.0)


def test_rewiring_sweep_length_drops_faster_than_clustering_at_small_p():
    rows = ev.rewiring_sweep(200, 8, 35, ps=C.P_SWEEP)
    row = next(r for r in rows if r["p"] == 0.01)
    assert row["l_ratio"] < 0.6                                     # Weglaenge schon deutlich gefallen
    assert row["c_ratio"] > 0.9                                     # Clustering fast erhalten -- die kleine-Welt-Signatur


def test_rewiring_sweep_p1_is_much_shorter_and_less_clustered_than_p0():
    rows = ev.rewiring_sweep(100, 8, 5, ps=(0.0, 1.0))
    r0, r1 = rows
    assert r1["l"] < r0["l"]
    assert r1["c"] < r0["c"]


# --- assortativity_null_distribution -------------------------------------------------------------------------------------------------------------------


def test_assortativity_null_distribution_shape():
    inst = ev.instance(ev.Settings(kind="ba", n_ba=60, m_ba=2, m0_ba=4, seed=1))
    adj = A.adjacency(inst.n, inst.edges)
    d = ev.assortativity_null_distribution(adj, 30, 1000, 1)
    assert len(d["draws"]) == 30
    assert d["original"] == pytest.approx(A.degree_assortativity(adj))
    assert -1.0 <= d["mean"] <= 1.0


def test_assortativity_null_distribution_handles_regular_graph_nan():
    n, pairs = 6, [(i, (i + 1) % 6) for i in range(6)]              # Kreis, regulaer
    adj = A.adjacency(n, [(u, v, 1.0) for u, v in pairs])
    d = ev.assortativity_null_distribution(adj, 20, 200, 1)
    assert math.isnan(d["original"])


# --- degree_histograms / heavy_tail_ratio -----------------------------------------------------------------------------------------------------------------


def test_degree_histograms_shapes():
    settings = ev.Settings(kind="city", side=8, blocked=0.2, nettype="grid", n_ba=60, m_ba=2, m0_ba=4, seed=1)
    hist = ev.degree_histograms(settings)
    assert set(hist) == {"city", "er", "ba"}
    assert len(hist["city"]) == 64 and len(hist["ba"]) == 60


def test_heavy_tail_ratio_ba_higher_than_city():
    settings = ev.Settings(kind="city", side=10, blocked=0.2, nettype="grid", n_ba=200, m_ba=2, m0_ba=4, seed=35)
    hist = ev.degree_histograms(settings)
    r_city = ev.heavy_tail_ratio(hist["city"])
    r_ba = ev.heavy_tail_ratio(hist["ba"])
    assert r_ba > r_city


def test_heavy_tail_ratio_empty_is_nan():
    assert math.isnan(ev.heavy_tail_ratio([]))
