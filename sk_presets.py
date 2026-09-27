"""SETTING_SPECS-Permalink-Muster, Presets und Zufalls-Seed-Buttons (Standardmuster aus dem Demo-Portfolio, wie in `cen_presets.py`)."""

import random
from dataclasses import dataclass
from typing import Callable, Optional

import streamlit as st

import sk_constants as C


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: Callable
    default: object
    lo: Optional[float] = None
    hi: Optional[float] = None


def _int_choice(options):
    def cast(value):
        value = int(value)
        if value not in options:
            raise ValueError(value)
        return value
    return cast


def _float_choice(options):
    def cast(value):
        value = float(value)
        if value not in options:
            raise ValueError(value)
        return value
    return cast


def _choice_from(options):
    def cast(value):
        value = str(value)
        if value not in options:
            raise ValueError(value)
        return value
    return cast


SETTING_SPECS = {
    "kind_select": SettingSpec("kind", _choice_from(C.KINDS), "city"),
    "side_slider": SettingSpec("side", int, C.DEFAULT_SIDE, C.SIDE_MIN, C.SIDE_MAX),
    "blocked_select": SettingSpec("blocked", _float_choice(C.BLOCKED_OPTIONS), C.DEFAULT_BLOCKED),
    "nettype_select": SettingSpec("nettype", _choice_from(C.NETTYPES), "grid"),
    "nring_slider": SettingSpec("nring", int, C.DEFAULT_N_RING, C.N_RING_MIN, C.N_RING_MAX),
    "kring_select": SettingSpec("kring", _int_choice(C.K_RING_OPTIONS), C.DEFAULT_K_RING),
    "prewire_select": SettingSpec("prewire", _float_choice(C.P_REWIRE_OPTIONS), C.DEFAULT_P_REWIRE),
    "nba_slider": SettingSpec("nba", int, C.DEFAULT_N_BA, C.N_BA_MIN, C.N_BA_MAX),
    "m0ba_slider": SettingSpec("m0ba", int, C.DEFAULT_M0_BA, C.M0_BA_MIN, C.M0_BA_MAX),
    "mba_slider": SettingSpec("mba", int, C.DEFAULT_M_BA, C.M_BA_MIN, C.M0_BA_MAX),
    "seed_input": SettingSpec("seed", int, C.DEFAULT_SEED, 0, C.SEED_MAX),
    "order_select": SettingSpec("order", _choice_from(C.ORDERS), "fixed"),
    "nswaps_slider": SettingSpec("nswaps", int, C.DEFAULT_N_SWAPS, C.N_SWAPS_MIN, C.N_SWAPS_MAX),
    "sk_step": SettingSpec("step", _int_choice(tuple(C.STEPS)), 1),
}
PRESET_KEYS = {"kind": "kind_select", "side": "side_slider", "blocked": "blocked_select", "nettype": "nettype_select", "nring": "nring_slider", "kring": "kring_select",
               "prewire": "prewire_select", "nba": "nba_slider", "m0ba": "m0ba_slider", "mba": "mba_slider", "seed": "seed_input", "order": "order_select", "nswaps": "nswaps_slider",
               "step": "sk_step"}
WIDGET_KEYS = {"side_slider": "side_widget", "blocked_select": "blocked_widget", "nettype_select": "nettype_widget", "nring_slider": "nring_widget", "kring_select": "kring_widget",
               "prewire_select": "prewire_widget", "nba_slider": "nba_widget", "m0ba_slider": "m0ba_widget", "mba_slider": "mba_widget", "seed_input": "seed_widget",
               "nswaps_slider": "nswaps_widget"}


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def load_permalink_settings():
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            try:
                value = spec.caster(qp[spec.url_param])
                if spec.lo is not None:
                    value = max(spec.lo, value)
                if spec.hi is not None:
                    value = min(spec.hi, value)
                st.session_state[state_key] = value
            except (ValueError, TypeError):
                pass
    # m <= m0: nach dem Laden erzwingen (die Permalink-Werte werden unabhängig voneinander geladen)
    if st.session_state.get("mba_slider", C.DEFAULT_M_BA) > st.session_state.get("m0ba_slider", C.DEFAULT_M0_BA):
        st.session_state["mba_slider"] = st.session_state.get("m0ba_slider", C.DEFAULT_M0_BA)
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    """`values`: {state_key: aktueller Wert}."""
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def store_from_widget(state_key):
    """Callback: übernimmt den Wert eines nur zeitweise sichtbaren Reglers in den dauerhaft gespeicherten Wert."""
    st.session_state[state_key] = st.session_state[WIDGET_KEYS[state_key]]


def push_to_widget(state_key):
    """Ist der Regler gerade sichtbar, muss ein geänderter gespeicherter Wert (Preset, Würfel) auch ihn selbst ändern."""
    widget_key = WIDGET_KEYS[state_key]
    if widget_key in st.session_state:
        st.session_state[widget_key] = st.session_state[state_key]


def apply_preset(name):
    p = C.PRESETS[name]
    for key, state_key in PRESET_KEYS.items():
        if key in p:
            st.session_state[state_key] = p[key]
    for state_key in WIDGET_KEYS:
        push_to_widget(state_key)


def randomize_seed():
    st.session_state["seed_input"] = random.randint(0, C.SEED_MAX)
    push_to_widget("seed_input")
