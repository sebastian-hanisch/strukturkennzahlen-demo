"""Strukturkennzahlen & Nullmodelle: Clustering, Kleine-Welt, Assortativität, gradfolgen-erhaltende Randomisierung - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Siebtes Stück der Graphen-und-Netzwerke-Reihe, Kind der Zentralität (Stück 6): dort wurden einzelne Knoten/Kanten bewertet, jetzt geht es um das Netz als Ganzes. Drei klassische Fragen, jede über
einen Vergleich mit einem Nullmodell beantwortet: Clustering, Kleine-Welt-Eigenschaft (Watts und Strogatz 1998), Assortativität (Newman 2002). Die zentrale methodische Frage: ist eine gemessene
Eigenschaft etwas Eigenes, oder folgt sie schon zwangsläufig aus der bloßen Gradfolge? Antwort über gradfolgen-erhaltende Randomisierung (Maslov und Sneppen 2002) gegen Erdős-Rényi.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import sk_algorithm as A
import sk_constants as C
import sk_evaluation as ev
import sk_visualization as viz
from sk_presets import apply_preset, bounds, init_session_state_defaults, load_permalink_settings, randomize_seed, store_from_widget, sync_query_params, push_to_widget

st.set_page_config(page_title="Strukturkennzahlen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return ev.analyse(settings)


@st.cache_data(show_spinner=False)
def _rewiring_sweep(n, k, seed):
    return ev.rewiring_sweep(n, k, seed)


@st.cache_data(show_spinner=False)
def _degree_histograms(settings):
    return ev.degree_histograms(settings)


@st.cache_data(show_spinner=False)
def _assortativity_null(settings):
    inst = ev.instance(settings)
    adj = A.adjacency(inst.n, inst.edges, settings.order, settings.seed)
    return ev.assortativity_null_distribution(adj, C.N_DRAWS_ASSORT, settings.n_swaps, settings.seed)


def _german(x):
    return f"{x:,}".replace(",", ".") if isinstance(x, int) else x


st.title("🕸️ Strukturkennzahlen – Clustering, Kleine Welt, Assortativität")
st.markdown(
    """
**Siebtes Stück der Graphen-und-Netzwerke-Reihe**, Kind der Zentralität (Stück 6: dort einzelne Knoten/Kanten, jetzt das Netz als Ganzes). Drei klassische Fragen: **Clustering** (wie oft sind die
Nachbarn eines Knotens auch untereinander verbunden?), **Kleine-Welt-Eigenschaft** (Watts und Strogatz 1998: hohes Clustering UND kurze Wege gleichzeitig - ein scheinbarer Widerspruch, den schon eine
winzige zufällige Umverdrahtung auflöst), **Assortativität** (Newman 2002: hängen sich hochgradige Knoten eher an andere hochgradige oder an schwachgradige?). Die zentrale methodische Frage: ist eine
gemessene Eigenschaft etwas Eigenes, oder folgt sie schon zwangsläufig aus der bloßen Gradfolge? Antwort über **gradfolgen-erhaltende Randomisierung** (Maslov und Sneppen 2002, Kanten-Doppeltausch)
gegen **Erdős-Rényi** G(n,m) (zerstört auch die Gradfolge selbst).
"""
)
st.caption(
    "Kind der Zentralität-Demo (siebtes Stück der Graphen-und-Netzwerke-Reihe); geplante Nachfolger (nicht gebaut): Robustheit, Kaskaden, kritische Knoten härten, Bandbreite. Drei Instanzen: das "
    "Betriebsnetz aus den vorigen Stücken, ein NEUES Ring-Umverdrahtungs-Modell (Watts-Strogatz) und ein NEUES skalenfreies Netz (Barabási-Albert, bevorzugte Anbindung)."
)

with st.expander("So funktionieren die drei Fragen", expanded=True):
    st.markdown(
        """
1. **Clustering:** lokaler Koeffizient C_v (Nachbarn von v, die auch untereinander verbunden sind, geteilt durch alle möglichen Paare), mittlerer Koeffizient über alle Knoten, globale Transitivität
   (3 · Dreiecke / Tripel). Grad 0 oder 1 -> C_v = 0 per Konvention.
2. **Kleine-Welt-Eigenschaft (Watts und Strogatz 1998):** ein Ring-Gitter hat hohes Clustering, aber lange Wege; ein Zufallsgraph kurze Wege, aber kaum Clustering. Schon eine winzige zufällige
   Umverdrahtung (kleines p) senkt die mittlere Weglänge drastisch, ohne das Clustering nennenswert zu senken - **ω (Telesford u. a. 2011)** fasst das in einer Zahl zusammen.
3. **Assortativität (Newman 2002):** Pearson-Korrelation der Grade an beiden Enden jeder Kante. r>0: hochgradige Knoten hängen sich eher an hochgradige (assortativ, oft in sozialen Netzen); r<0:
   an schwachgradige (disassortativ, oft in technischen/biologischen Netzen).
4. **Nullmodelle:** Erdős-Rényi G(n,m) (Erdős und Rényi 1959, zerstört auch die Gradfolge) gegen das **Konfigurationsmodell** (Maslov und Sneppen 2002, Kanten-Doppeltausch - die Gradfolge bleibt
   exakt erhalten). Weicht eine Kennzahl vom Konfigurationsmodell ab, ist sie NICHT allein durch die Gradfolge erklärt.
        """
    )

if C.PRESETS:
    st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
    preset_names = list(C.PRESETS.keys())
    for row in (preset_names[:4], preset_names[4:]):
        if not row:
            continue
        cols = st.columns(len(row))
        for col, name in zip(cols, row):
            with col:
                st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}")

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()
ss = st.session_state

with st.sidebar:
    st.header("⚙️ Einstellungen")
    kind = st.radio("Instanz", options=list(C.KINDS), format_func=lambda v: C.KIND_LABELS[v], key="kind_select",
                     help="Betriebsnetz: gestörtes Straßenraster (oder Zufallsgraph gleicher Kantenzahl). Ring-Umverdrahtung: Watts-Strogatz. Skalenfreies Netz: Barabási-Albert, bevorzugte Anbindung.")

    side, blocked, nettype = C.DEFAULT_SIDE, C.DEFAULT_BLOCKED, "grid"
    n_ring, k_ring, p_rewire = C.DEFAULT_N_RING, C.DEFAULT_K_RING, C.DEFAULT_P_REWIRE
    n_ba, m_ba, m0_ba = C.DEFAULT_N_BA, C.DEFAULT_M_BA, C.DEFAULT_M0_BA

    if kind == "city":
        side = st.slider("Seitenlänge des Rasters", *bounds("side_slider"), value=int(ss["side_slider"]), key="side_widget", on_change=store_from_widget, args=("side_slider",),
                          help="Die Instanz hat Seitenlänge² Kreuzungen.")
        nettype = st.radio("Netztyp", options=list(C.NETTYPES), format_func=lambda v: C.NETTYPE_LABELS[v], key="nettype_widget", on_change=store_from_widget, args=("nettype_select",),
                            index=list(C.NETTYPES).index(ss["nettype_select"]))
        if nettype == "grid":
            blocked = st.select_slider("Gesperrter Anteil der Straßen", options=list(C.BLOCKED_OPTIONS), value=float(ss["blocked_select"]), format_func=lambda v: f"{v * 100:.0f} %",
                                        key="blocked_widget", on_change=store_from_widget, args=("blocked_select",))
        else:
            blocked = 0.0
    elif kind == "ring":
        n_ring = st.slider("Zahl der Knoten n", *bounds("nring_slider"), value=int(ss["nring_slider"]), key="nring_widget", on_change=store_from_widget, args=("nring_slider",),
                            help="Knoten im Kreis des Ring-Gitters.")
        k_ring = st.select_slider("Gesamtgrad k (im Ring-Gitter, vor der Umverdrahtung)", options=list(C.K_RING_OPTIONS), value=int(ss["kring_select"]), format_func=lambda v: f"{v} ({v // 2} je Seite)",
                                   key="kring_widget", on_change=store_from_widget, args=("kring_select",))
        p_rewire = st.select_slider("Umverdrahtungswahrscheinlichkeit p", options=list(C.P_REWIRE_OPTIONS), value=float(ss["prewire_select"]),
                                     format_func=lambda v: f"{v * 100:g} %", key="prewire_widget", on_change=store_from_widget, args=("prewire_select",),
                                     help="p=0: reines Ring-Gitter. p=1: fast zufällig verdrahtet (gleiche Kantenzahl).")
    else:
        n_ba = st.slider("Zahl der Knoten n", *bounds("nba_slider"), value=int(ss["nba_slider"]), key="nba_widget", on_change=store_from_widget, args=("nba_slider",))
        m0_ba = st.slider("Kerngröße m0 (Kreis aus m0 Knoten)", *bounds("m0ba_slider"), value=int(ss["m0ba_slider"]), key="m0ba_widget", on_change=store_from_widget, args=("m0ba_slider",))
        if ss["mba_slider"] > m0_ba:
            ss["mba_slider"] = m0_ba
            push_to_widget("mba_slider")
        if C.M_BA_MIN < m0_ba:
            m_ba = st.slider("Neue Kanten je Knoten m (bevorzugte Anbindung)", C.M_BA_MIN, m0_ba, value=int(ss["mba_slider"]), key="mba_widget", on_change=store_from_widget, args=("mba_slider",),
                              help="Jeder neue Knoten hängt sich mit m Kanten an m bereits vorhandene Knoten an, proportional zu deren Grad gezogen.")
        else:
            m_ba = C.M_BA_MIN                                        # m0 == M_BA_MIN: keine Wahl möglich (min==max würde den Regler zum Absturz bringen)

    seed = st.number_input("Zufalls-Seed der Instanz", *bounds("seed_input"), value=int(ss["seed_input"]), key="seed_widget", step=1, on_change=store_from_widget, args=("seed_input",))
    st.button("🎲 Neue Instanz generieren", width="stretch", on_click=randomize_seed)
    order = st.radio("Nachbarreihenfolge", options=list(C.ORDERS), format_func=lambda v: C.ORDER_LABELS[v], key="order_select",
                      help="Ändert nie eine Strukturkennzahl - nur die interne Buchführungsreihenfolge (Determinismus-Test).")

step = st.select_slider("Schritt", options=list(C.STEPS), key="sk_step", format_func=lambda s: C.STEPS[s])

if step in (1, 4):
    n_swaps = st.slider("Doppeltausch-Versuche (Konfigurationsmodell)", *bounds("nswaps_slider"), value=int(ss["nswaps_slider"]), key="nswaps_widget", on_change=store_from_widget,
                         args=("nswaps_slider",), help="Zahl der Kanten-Doppeltausch-Versuche für das gradfolgen-erhaltende Nullmodell (Maslov und Sneppen 2002) - nicht zwingend Erfolge.")
else:
    n_swaps = int(ss["nswaps_slider"])

sync_query_params({"kind_select": kind, "side_slider": int(side) if kind == "city" else int(ss["side_slider"]), "blocked_select": float(blocked) if kind == "city" and nettype == "grid" else float(ss["blocked_select"]),
                    "nettype_select": nettype if kind == "city" else ss["nettype_select"], "nring_slider": int(n_ring) if kind == "ring" else int(ss["nring_slider"]),
                    "kring_select": int(k_ring) if kind == "ring" else int(ss["kring_select"]), "prewire_select": float(p_rewire) if kind == "ring" else float(ss["prewire_select"]),
                    "nba_slider": int(n_ba) if kind == "ba" else int(ss["nba_slider"]), "m0ba_slider": int(m0_ba) if kind == "ba" else int(ss["m0ba_slider"]),
                    "mba_slider": int(m_ba) if kind == "ba" else int(ss["mba_slider"]), "seed_input": int(seed), "order_select": order, "nswaps_slider": int(n_swaps), "sk_step": int(step)})

settings = ev.Settings(kind=kind, side=int(side), blocked=float(blocked), nettype=nettype, n_ring=int(n_ring), k_ring=int(k_ring), p_rewire=float(p_rewire), n_ba=int(n_ba), m_ba=int(m_ba),
                        m0_ba=int(m0_ba), seed=int(seed), order=order, n_swaps=int(n_swaps))

with st.spinner("Rechne..."):
    inst, a = _analysis(settings)
adj = A.adjacency(inst.n, inst.edges, settings.order, settings.seed)

st.markdown("## 🎯 Das Netz und seine Strukturkennzahlen")
conn_txt = "zusammenhängend" if a.connected else f"unzusammenhängend, größte Komponente {_german(a.largest_cc_size)} Knoten"
st.markdown(f"**{_german(a.n)} Knoten, {_german(a.m)} Kanten** ({conn_txt}). Clustering C={a.avg_clustering:.4f}, Transitivität T={a.transitivity:.4f}, mittlere Weglänge L={a.avg_distance:.4f}, "
            f"Assortativität r={a.assortativity:.4f}" + (f", ω={a.omega:.4f}" if kind == "ring" else "") + ".")

if step == 1:
    with st.spinner("Rechne Nullmodelle..."):
        er_pairs = A.erdos_renyi_gnm(inst.n, inst.m, settings.seed)
        config_pairs = A.configuration_null(adj, settings.n_swaps, settings.seed)
    orig_pairs = [(u, v) for u, v, _ in inst.edges]
    st.plotly_chart(viz.build_comparison_maps(inst.xy, orig_pairs, er_pairs, config_pairs), width="stretch", key=f"s1_maps_{kind}_{seed}")
    st.dataframe(viz.comparison_table(a), width="stretch", hide_index=True)
    st.caption("Erdős-Rényi zerstört auch die Gradfolge selbst; das Konfigurationsmodell erhält sie exakt (gleiche Grad-Extrema) und randomisiert nur, WER mit wem verbunden ist.")
elif step == 2:
    if kind != "ring":
        st.info("Der Watts-Strogatz-Übergang ist nur für die Ring-Umverdrahtungs-Instanz definiert - links **Ring-Umverdrahtung** wählen.")
    else:
        st.plotly_chart(viz.build_ring_map(inst.xy, [(u, v) for u, v, _ in inst.edges], k_ring // 2), width="stretch", key=f"s2_map_{n_ring}_{k_ring}_{p_rewire}_{seed}")
        with st.spinner("Rechne Übergang..."):
            rows = _rewiring_sweep(n_ring, k_ring, seed)
        st.plotly_chart(viz.build_rewiring_sweep(rows, p_rewire), width="stretch", key=f"s2_sweep_{n_ring}_{k_ring}_{seed}")
        st.metric("ω (Telesford u. a. 2011)", f"{a.omega:.4f}", help="ω nahe 0: klein-welt-artig. Nahe -1: gitterartig. Nahe +1: zufallsgraphartig.")
        st.caption(f"C_lattice (p=0, Referenz) = {a.c_lattice:.4f}. Schon bei kleinem p sinkt die mittlere Weglänge stark, während das Clustering fast erhalten bleibt.")
elif step == 3:
    with st.spinner("Rechne Gradverteilungen..."):
        hist = _degree_histograms(settings)
    st.plotly_chart(viz.build_degree_histograms(hist), width="stretch", key=f"s3_hist_{settings.side}_{settings.blocked}_{settings.nettype}_{settings.n_ba}_{settings.m_ba}_{settings.m0_ba}_{seed}")
    ratios = {name: ev.heavy_tail_ratio(degs) for name, degs in hist.items()}
    st.caption(f"Verhältnis Maximalgrad/mittlerer Grad (informeller Heavy-Tail-Hinweis, KEIN Machtgesetz-Test): Betriebsnetz {ratios['city']:.2f}, Erdős-Rényi {ratios['er']:.2f}, "
               f"skalenfreies Netz {ratios['ba']:.2f}.")
else:
    st.plotly_chart(viz.build_degree_degree_scatter(adj), width="stretch", key=f"s4_scatter_{kind}_{seed}")
    with st.spinner("Ziehe Konfigurationsmodell-Stichprobe..."):
        null = _assortativity_null(settings)
    st.plotly_chart(viz.build_assortativity_null_histogram(null), width="stretch", key=f"s4_null_{kind}_{seed}_{settings.n_swaps}")
    z = null["z"]
    if z == z:
        verdict = "NICHT signifikant (|z|<2) - mit der bloßen Gradfolge verträglich" if abs(z) < 2 else "signifikant (|z|>=2) - eine eigenständige Eigenschaft dieses Netzes, nicht allein Folge der Gradfolge"
        st.caption(f"Original-r={null['original']:.4f} gegen {C.N_DRAWS_ASSORT} Konfigurationsmodell-Ziehungen (Mittel {null['mean']:.4f}, Std {null['std']:.4f}): z={z:.2f} - {verdict}.")
    else:
        st.caption("z-Wert nicht definiert (konstanter Grad in der Nullverteilung oder im Original).")

st.markdown("---")

st.markdown("## 🎯 Was das Netz verrät")
r1, r2, r3, r4 = st.columns(4)
r1.metric("Clustering (Mittel)", f"{a.avg_clustering:.4f}", delta_color="off")
r2.metric("Transitivität", f"{a.transitivity:.4f}", delta_color="off")
r3.metric("Mittlere Weglänge", f"{a.avg_distance:.4f}", delta_color="off")
r4.metric("Assortativität r", f"{a.assortativity:.4f}" if a.assortativity == a.assortativity else "NaN", delta_color="off")

st.markdown("---")

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **ω ist nur auf dem Ring-Umverdrahtungs-Modell definiert** | Bei Betriebsnetz und skalenfreiem Netz gibt es kein "C_lattice" - nur die rohen Verhältnisse C/C_ER und L/L_ER sind gezeigt, kein ω. | - |
| **Konfigurationsmodell-Doppeltausch ist ein fester Vorgabewert** | Keine Konvergenzprüfung der Mischzeit - bei sehr wenigen Versuchen bleibt die Randomisierung unvollständig. | - |
| **Heavy-Tail-Verhältnis ist informell** | Kein formaler Machtgesetz-Test (Clauset u. a. 2009) - nur ein grober Hinweis, keine geschätzte Exponente. | - |
| **Mittlere Weglänge bei unzusammenhängenden Netzen** | `average_distance` zählt nur erreichbare Paare - anders als `networkx.average_shortest_path_length`, das dort einen Fehler wirft. | - |
| **Assortativität ist ein globaler Mittelwert** | Sie sagt nichts über lokale Cluster hochgradiger Knoten (z. B. ein einzelner dominanter Hub) - dafür bräuchte es andere Maße. | - |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lokaler Clustering-Koeffizient (Watts und Strogatz 1998).** $C_v = \dfrac{2 t_v}{d_v (d_v - 1)}$, wobei $t_v$ die Zahl der Kanten zwischen Nachbarn von $v$ ist. $C_v = 0$ bei $d_v \le 1$.

**Transitivität.** $T = \dfrac{3 \cdot \text{Dreiecke}}{\text{Tripel (offen + geschlossen)}} = \dfrac{\sum_v 2 t_v}{\sum_v d_v(d_v-1)}$.

**Mittlere Weglänge.** $L = \dfrac{1}{|P|}\sum_{(u,v) \in P} d(u,v)$ über alle erreichbaren ungeordneten Paare $P$ - wohldefiniert auch bei unzusammenhängenden Netzen.

**Assortativität (Newman 2002).** Pearson-Korrelation der Grade an beiden Enden jeder Kante (beide Richtungen): $r = \dfrac{\sum_e j_e k_e / M - \left[\sum_e (j_e+k_e)/(2M)\right]^2}{\sum_e (j_e^2+k_e^2)/(2M) - \left[\sum_e (j_e+k_e)/(2M)\right]^2}$.

**Ring-Gitter (Watts und Strogatz 1998).** $n$ Knoten im Kreis, Gesamtgrad $k$ ($k/2$ Nachbarn je Seite). Geschlossene Form bei $p=0$: $C(0) = \dfrac{3(k-2)}{4(k-1)}$.

**ω, Kleine-Welt-Kennzahl (Telesford u. a. 2011).** $\omega = \dfrac{L_{rand}}{L} - \dfrac{C}{C_{lattice}}$. Nahe 0: klein-welt-artig. Nahe $-1$: gitterartig. Nahe $+1$: zufallsgraphartig.

**Erdős-Rényi G(n,m) (Erdős und Rényi 1959).** $m$ verschiedene Kantenpaare gleichverteilt aus allen $\binom{n}{2}$ möglichen gezogen - zerstört auch die Gradfolge selbst.

**Konfigurationsmodell per Kanten-Doppeltausch (Maslov und Sneppen 2002).** Zwei Kanten $(a,b)$, $(c,d)$ mit vier verschiedenen Knoten zu $(a,d)$, $(c,b)$ getauscht, nur wenn beide neuen Kanten noch
nicht existieren - die Gradfolge (Multimenge) bleibt bei jedem einzelnen Tausch exakt erhalten.

**Barabási-Albert, bevorzugte Anbindung (Barabási und Albert 1999).** Kern aus $m_0$ Knoten (Kreis), jeder weitere Knoten hängt sich mit $m$ Kanten an $m$ vorhandene Knoten proportional zu deren
Grad an. Exakte Kantenzahl $m_0 + (n - m_0) \cdot m$.

**Literatur.** Watts, D. J., & Strogatz, S. H. (1998). *Collective dynamics of 'small-world' networks.* Nature 393, 440–442. Newman, M. E. J. (2002). *Assortative mixing in networks.* Physical Review
Letters 89(20), 208701. Maslov, S., & Sneppen, K. (2002). *Specificity and stability in topology of protein networks.* Science 296(5569), 910–913. Barabási, A.-L., & Albert, R. (1999). *Emergence of
scaling in random networks.* Science 286(5439), 509–512. Telesford, Q. K., Joyce, K. E., Hayasaka, S., Burdette, J. H., & Laurienti, P. J. (2011). *The ubiquity of small-world networks.* Brain
Connectivity 1(5), 367–375. Erdős, P., & Rényi, A. (1959). *On random graphs I.* Publicationes Mathematicae Debrecen 6, 290–297. Clauset, A., Shalizi, C. R., & Newman, M. E. J. (2009). *Power-law
distributions in empirical data.* SIAM Review 51(4), 661–703 (nur als der rigorose Weg genannt, einen Machtgesetz-Test durchzuführen - hier bewusst nicht gebaut).

Implementiert in `sk_algorithm.py` (Clustering, Transitivität, mittlere Weglänge, Assortativität, Nullmodelle, ω), `sk_scenario.py` (Instanzen), `sk_evaluation.py` (Analyse, Sweeps).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning. Interesse an einer maßgeschneiderten Lösung für "
    "Ihr Unternehmen? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html)"
)
