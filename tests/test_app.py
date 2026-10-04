"""AppTest-Rauchtests: Voreinstellung, jedes Preset, jeder Schritt für jede Instanzart, bedingte Regler, Permalink-Grenzen, m<=m0-Kopplung, Footer."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import sk_constants as C

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _run(step=1, **state):
    at = AppTest.from_file(APP, default_timeout=300)
    state.setdefault("sk_step", step)
    for k, v in state.items():
        at.session_state[k] = v
    at.run()
    return at


def _ok(at):
    assert not at.exception, [e.value for e in at.exception]


def _click(at, key):
    next(b for b in at.button if b.key == key).click().run()


def test_default_run_shows_the_summary():
    at = _run()
    _ok(at)
    assert {"Clustering (Mittel)", "Transitivität", "Mittlere Weglänge", "Assortativität r"} <= {m.label for m in at.metric}


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_button_runs(name):
    at = _run(kind_select="city", side_slider=8)
    _click(at, f"preset_{name}")
    _ok(at)
    p, ss = C.PRESETS[name], at.session_state
    assert ss["kind_select"] == p["kind"] and ss["sk_step"] == p["step"]


@pytest.mark.parametrize("step", [1, 2, 3, 4])
@pytest.mark.parametrize("kind", ["city", "ring", "ba"])
def test_every_step_runs_for_every_kind(step, kind):
    at = _run(step=step, kind_select=kind, side_slider=8, nring_slider=60, nba_slider=60)
    _ok(at)
    assert at.session_state["sk_step"] == step


def test_step2_shows_hint_for_non_ring_kinds():
    at = _run(step=2, kind_select="city")
    _ok(at)
    assert any("nur für die Ring-Umverdrahtungs-Instanz" in c.value for c in at.info)


def test_step2_ring_shows_omega_metric():
    at = _run(step=2, kind_select="ring", nring_slider=60)
    _ok(at)
    assert any(m.label.startswith("ω") for m in at.metric)


@pytest.mark.parametrize("nettype", ["grid", "random"])
def test_step1_every_nettype(nettype):
    at = _run(step=1, kind_select="city", side_slider=8, nettype_select=nettype)
    _ok(at)


def test_blocked_slider_only_shown_for_grid_nettype():
    at = _run(kind_select="city", nettype_select="grid")
    assert any(w.key == "blocked_widget" for w in at.select_slider)
    at2 = _run(kind_select="city", nettype_select="random")
    assert not any(w.key == "blocked_widget" for w in at2.select_slider)


def test_nswaps_slider_only_shown_on_steps_1_and_4():
    at1 = _run(step=1)
    assert any(w.key == "nswaps_widget" for w in at1.slider)
    at2 = _run(step=2)
    assert not any(w.key == "nswaps_widget" for w in at2.slider)
    at3 = _run(step=3)
    assert not any(w.key == "nswaps_widget" for w in at3.slider)
    at4 = _run(step=4)
    assert any(w.key == "nswaps_widget" for w in at4.slider)


def test_sidebar_shows_the_controls_that_belong_to_the_instance():
    city = _run(kind_select="city")
    assert any(w.key == "side_widget" for w in city.slider) and not any(w.key == "nring_widget" for w in city.slider)
    ring = _run(kind_select="ring")
    assert any(w.key == "nring_widget" for w in ring.slider) and not any(w.key == "side_widget" for w in ring.slider)
    ba = _run(kind_select="ba")
    assert any(w.key == "nba_widget" for w in ba.slider) and not any(w.key == "nring_widget" for w in ba.slider)


def test_ba_m_slider_never_exceeds_m0():
    at = _run(kind_select="ba", m0ba_slider=3, mba_slider=10)          # m gespeichert > neues m0 -> muss geklemmt werden
    _ok(at)
    assert at.session_state["mba_slider"] <= 3


def test_dice_button_changes_the_seed_and_the_visible_widget():
    at = _run(kind_select="city")
    old = at.session_state["seed_input"]
    next(b for b in at.button if b.label == "🎲 Neue Instanz generieren").click().run()
    _ok(at)
    assert at.session_state["seed_input"] != old and at.session_state["seed_widget"] == at.session_state["seed_input"]


def test_permalink_values_are_clamped_and_invalid_choices_fall_back_to_the_default():
    at = AppTest.from_file(APP, default_timeout=300)
    for k, v in dict(kind="nope", side="9999", blocked="0.33", nettype="sideways", kring="7", prewire="0.5555", nba="99999", seed="-4", order="up", step="9").items():
        at.query_params[k] = v
    at.run()
    _ok(at)
    ss = at.session_state
    assert ss["kind_select"] == "city"
    assert ss["side_slider"] == C.SIDE_MAX
    assert ss["blocked_select"] == C.DEFAULT_BLOCKED
    assert ss["nettype_select"] == "grid"
    assert ss["kring_select"] == C.DEFAULT_K_RING
    assert ss["prewire_select"] == C.DEFAULT_P_REWIRE
    assert ss["nba_slider"] == C.N_BA_MAX
    assert ss["seed_input"] == 0
    assert ss["order_select"] == "fixed"
    assert ss["sk_step"] == 1


def test_permalink_accepts_valid_values_and_writes_them_back():
    at = AppTest.from_file(APP, default_timeout=300)
    for k, v in dict(kind="ring", nring="80", kring="6", prewire="0.03", seed="7", step="2").items():
        at.query_params[k] = v
    at.run()
    _ok(at)
    ss = at.session_state
    assert (ss["kind_select"], ss["nring_slider"], ss["kring_select"], ss["prewire_select"], ss["seed_input"], ss["sk_step"]) == ("ring", 80, 6, 0.03, 7, 2)
    assert at.query_params["seed"] in (["7"], "7") and at.query_params["step"] in (["2"], "2")
    assert ss["nring_widget"] == 80 and ss["seed_widget"] == 7


def test_switching_kind_back_and_forth_keeps_the_stored_values():
    at = _run(kind_select="city", side_slider=14, blocked_select=0.4, seed_input=11)
    at.session_state["kind_select"] = "ring"
    at.run()
    _ok(at)
    at.session_state["kind_select"] = "city"
    at.run()
    _ok(at)
    assert at.session_state["side_widget"] == 14 and at.session_state["blocked_widget"] == 0.4 and at.session_state["seed_widget"] == 11


@pytest.mark.parametrize("kw", [dict(kind_select="city", side_slider=C.SIDE_MIN), dict(kind_select="city", side_slider=C.SIDE_MAX), dict(kind_select="ring", nring_slider=C.N_RING_MIN),
                                 dict(kind_select="ring", nring_slider=C.N_RING_MAX), dict(kind_select="ba", nba_slider=C.N_BA_MIN), dict(kind_select="ba", nba_slider=C.N_BA_MAX),
                                 dict(kind_select="ba", m0ba_slider=C.M0_BA_MIN), dict(kind_select="ba", m0ba_slider=C.M0_BA_MAX)])
def test_extreme_settings_run_on_every_step(kw):
    for step in (1, 2, 3, 4):
        _ok(_run(step=step, **kw))


def test_footer_limits_and_literature_are_present():
    at = _run()
    assert any("Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net)" in c.value for c in at.caption)
    assert any("Wo die Annahmen enden" in s.value for s in at.subheader)
    assert any("Watts" in m.value and "Newman" in m.value for e in at.expander for m in e.markdown)
