"""Presets: gültige Werte und jede Zahl der Hilfetexte gegen die echten Auswertungsfunktionen."""

import sk_constants as C
import sk_evaluation as ev
from sk_presets import PRESET_KEYS, SETTING_SPECS


def _settings(name):
    p = C.PRESETS[name]
    return ev.Settings(kind=p.get("kind", "city"), side=p.get("side", C.DEFAULT_SIDE), blocked=p.get("blocked", C.DEFAULT_BLOCKED), nettype=p.get("nettype", "grid"),
                        n_ring=p.get("nring", C.DEFAULT_N_RING), k_ring=p.get("kring", C.DEFAULT_K_RING), p_rewire=p.get("prewire", C.DEFAULT_P_REWIRE), n_ba=p.get("nba", C.DEFAULT_N_BA),
                        m_ba=p.get("mba", C.DEFAULT_M_BA), m0_ba=p.get("m0ba", C.DEFAULT_M0_BA), seed=p.get("seed", C.DEFAULT_SEED), n_swaps=C.DEFAULT_N_SWAPS)


def _has(name, *values):
    for v in values:
        assert v in C.PRESET_HELP[name], (name, v)


def test_every_preset_has_valid_values_and_a_help_text():
    assert list(C.PRESETS) == list(C.PRESET_HELP) and len(C.PRESETS) == 8
    for name, p in C.PRESETS.items():
        assert set(p) <= set(PRESET_KEYS) and {"kind", "step"} <= set(p) and p["step"] in C.STEPS
        for key, state_key in PRESET_KEYS.items():
            if key in p and state_key in SETTING_SPECS:
                spec = SETTING_SPECS[state_key]
                assert spec.caster(p[key]) == p[key], (name, key)
                if spec.lo is not None:
                    assert spec.lo <= p[key] <= spec.hi, (name, key)
        assert C.PRESET_HELP[name].strip()


def test_help_betriebsnetz_standardfall():
    inst, a = ev.analyse(_settings("Betriebsnetz Standardfall"))
    assert a.n == 100 and a.m == 144
    assert a.avg_clustering == 0.0 and a.transitivity == 0.0
    _has("Betriebsnetz Standardfall", "100 Kreuzungen", "144 Straßen", "0.0000")


def test_help_zufallsgraph_kontrast():
    inst, a = ev.analyse(_settings("Zufallsgraph-Kontrast"))
    assert a.n == 100 and a.m == 180
    assert round(a.avg_clustering, 4) == 0.0374
    _has("Zufallsgraph-Kontrast", "100 Knoten", "180 Kanten", "0.0374")


def test_help_watts_strogatz_lehrbuch():
    inst, a = ev.analyse(_settings("Watts-Strogatz-Lehrbuch (Ring von Hand)"))
    assert a.n == 200 and a.m == 200 * 8 // 2
    assert round(a.avg_clustering, 4) == 0.6429
    assert round(a.avg_clustering, 6) == round(3 * (8 - 2) / (4 * (8 - 1)), 6)
    _has("Watts-Strogatz-Lehrbuch (Ring von Hand)", "0.6429", "18/28")


def test_help_kleine_welt_uebergang():
    inst, a = ev.analyse(_settings("Kleine-Welt-Übergang (p-Sweep)"))
    rows = ev.rewiring_sweep(200, 8, 35)
    row = next(r for r in rows if r["p"] == 0.01)
    assert round(row["c_ratio"], 3) == 0.975
    assert round(row["l_ratio"], 2) == 0.53
    _has("Kleine-Welt-Übergang (p-Sweep)", "0.53", "0.975")


def test_help_skalenfreies_netz():
    inst, a = ev.analyse(_settings("Skalenfreies Netz (Heavy Tail)"))
    assert a.n == 200 and a.m == 4 + (200 - 4) * 2
    hist = ev.degree_histograms(_settings("Skalenfreies Netz (Heavy Tail)"))
    ratio = ev.heavy_tail_ratio(hist["ba"])
    assert round(ratio, 2) == 8.84
    _has("Skalenfreies Netz (Heavy Tail)", "8.84")


def test_help_assortativitaet_test():
    settings = _settings("Assortativität-Test (Betriebsnetz gegen Konfigurationsmodell)")
    inst = ev.instance(settings)
    import sk_algorithm as A
    adj = A.adjacency(inst.n, inst.edges)
    d = ev.assortativity_null_distribution(adj, C.N_DRAWS_ASSORT, C.DEFAULT_N_SWAPS, settings.seed)
    assert round(d["original"], 2) == 0.10
    assert round(d["z"], 2) == 1.35
    _has("Assortativität-Test (Betriebsnetz gegen Konfigurationsmodell)", "0.10", "1.35")


def test_help_config_zerstoert_clustering():
    settings = _settings("Konfigurationsmodell zerstört Clustering")
    inst, a = ev.analyse(settings)
    assert round(a.avg_clustering, 4) == 0.6429
    assert round(a.config.avg_clustering, 4) == 0.0145
    _has("Konfigurationsmodell zerstört Clustering", "0.6429", "0.0145")


def test_help_ba_disassortativ():
    import sk_algorithm as A
    settings = _settings("BA ist disassortativ")
    inst = ev.instance(settings)
    adj = A.adjacency(inst.n, inst.edges)
    d = ev.assortativity_null_distribution(adj, C.N_DRAWS_ASSORT, C.DEFAULT_N_SWAPS, settings.seed)
    assert round(d["original"], 2) == -0.17
    assert round(d["z"], 1) == 25.1
    _has("BA ist disassortativ", "-0.17", "+25.1")
