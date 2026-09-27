"""Plotly-Figuren: Netz gegen seine zwei Nullmodelle (Karten mit denselben Knotenpositionen), Watts-Strogatz-Ring-Karte + Übergangskurve, Gradverteilungs-Histogramme (linear/log-log),
Grad-Grad-Streudiagramm samt Nullverteilung der Assortativität. Alle Achsen fest (fixedrange), Karten nutzen `scaleanchor` mit autorange und zwei unsichtbaren Eckpunkten (wie in den Geschwistern)."""

import math

import plotly.graph_objects as go
from plotly.subplots import make_subplots

TEAL, ORANGE, BLUE, RED, PURPLE, GREY, LIGHT = "#2F6B65", "#f58518", "#4c78a8", "#e45756", "#7b3fbf", "#b7bec7", "#e8ebee"


def _lines(xy, pairs):
    xs, ys = [], []
    for u, v in pairs:
        xs += [xy[u][0], xy[v][0], None]
        ys += [xy[u][1], xy[v][1], None]
    return xs, ys


def _corners_trace(xy):
    pad = 0.4
    return go.Scatter(x=[xy[:, 0].min() - pad, xy[:, 0].max() + pad], y=[xy[:, 1].min() - pad, xy[:, 1].max() + pad], mode="markers", marker=dict(opacity=0), hoverinfo="skip")


def _mini_map(fig, row, col, xy, pairs, color="#4c78a8"):
    ex, ey = _lines(xy, pairs)
    fig.add_trace(go.Scatter(x=ex, y=ey, mode="lines", line=dict(color=color, width=1.0), hoverinfo="skip", opacity=0.7), row=row, col=col)
    fig.add_trace(go.Scatter(x=xy[:, 0], y=xy[:, 1], mode="markers", marker=dict(size=4, color="#333"), hoverinfo="skip"), row=row, col=col)
    fig.add_trace(_corners_trace(xy), row=row, col=col)


# --- 1 · Netz gegen seine zwei Nullmodelle -----------------------------------------------------------------------------------------------------------------


def build_comparison_maps(xy, orig_pairs, er_pairs, config_pairs):
    """Drei Karten nebeneinander, SELBE Knotenpositionen: Original, Erdős-Rényi-Gegenstück (zerstört auch die Gradfolge), Konfigurationsmodell-Realisierung (Gradfolge exakt erhalten)."""
    fig = make_subplots(rows=1, cols=3, subplot_titles=("Original", "Erdős-Rényi G(n,m)", "Konfigurationsmodell"))
    _mini_map(fig, 1, 1, xy, orig_pairs, TEAL)
    _mini_map(fig, 1, 2, xy, er_pairs, RED)
    _mini_map(fig, 1, 3, xy, config_pairs, ORANGE)
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=36, b=10), showlegend=False, plot_bgcolor="white")
    fig.update_xaxes(visible=False, fixedrange=True, scaleanchor="y", scaleratio=1)
    fig.update_yaxes(visible=False, fixedrange=True)
    return fig


def _fmt(x):
    return f"{x:.4f}" if x == x else "NaN"                            # NaN != NaN


def comparison_table(a):
    """Kennzahltabelle: Original gegen beide Nullmodelle. Alle Werte als Text (gemischte Spalten - Grad-Extrema sind kein reiner Zahlenwert)."""
    def deg_extrema(degree):
        return f"{min(degree)}-{max(degree)}"
    rows = [
        {"Kennzahl": "Clustering (Mittel)", "Original": _fmt(a.avg_clustering), "Erdős-Rényi": _fmt(a.er.avg_clustering), "Konfigurationsmodell": _fmt(a.config.avg_clustering)},
        {"Kennzahl": "Transitivität", "Original": _fmt(a.transitivity), "Erdős-Rényi": _fmt(a.er.transitivity), "Konfigurationsmodell": _fmt(a.config.transitivity)},
        {"Kennzahl": "Mittlere Weglänge", "Original": _fmt(a.avg_distance), "Erdős-Rényi": _fmt(a.er.avg_distance), "Konfigurationsmodell": _fmt(a.config.avg_distance)},
        {"Kennzahl": "Assortativität r", "Original": _fmt(a.assortativity), "Erdős-Rényi": _fmt(a.er.assortativity), "Konfigurationsmodell": _fmt(a.config.assortativity)},
        {"Kennzahl": "Grad-Extrema (min-max)", "Original": deg_extrema(a.degree), "Erdős-Rényi": "gleiche Gradfolge zerstört", "Konfigurationsmodell": "== Original (per Konstruktion)"},
    ]
    return rows


# --- 2 · Watts-Strogatz-Übergang -----------------------------------------------------------------------------------------------------------------------------


def build_ring_map(xy, pairs, k_short_threshold):
    """Ring-Karte: kurze Kanten (Ring-Nachbarschaft) grau, lange "Abkürzungen" (Umverdrahtung) farbig hervorgehoben."""
    n = len(xy)
    fig = go.Figure()
    short_pairs = [(u, v) for u, v in pairs if min(abs(u - v), n - abs(u - v)) <= k_short_threshold]
    long_pairs = [(u, v) for u, v in pairs if min(abs(u - v), n - abs(u - v)) > k_short_threshold]
    sx, sy = _lines(xy, short_pairs)
    fig.add_trace(go.Scatter(x=sx, y=sy, mode="lines", line=dict(color="#c7ccd1", width=1.0), hoverinfo="skip"))
    lx, ly = _lines(xy, long_pairs)
    fig.add_trace(go.Scatter(x=lx, y=ly, mode="lines", line=dict(color=ORANGE, width=1.4), opacity=0.75, hoverinfo="skip", name="Umverdrahtete Kante ('Abkürzung')"))
    fig.add_trace(go.Scatter(x=xy[:, 0], y=xy[:, 1], mode="markers", marker=dict(size=5, color=TEAL), hoverinfo="skip"))
    fig.add_trace(_corners_trace(xy))
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=20, b=10), showlegend=len(long_pairs) > 0, legend=dict(orientation="h", y=1.08), plot_bgcolor="white")
    fig.update_xaxes(visible=False, fixedrange=True, scaleanchor="y", scaleratio=1)
    fig.update_yaxes(visible=False, fixedrange=True)
    return fig


def build_rewiring_sweep(rows, current_p, c_lattice_label="C(p)/C(0)"):
    """C(p)/C(0) und L(p)/L(0) über p (log-Achse), Watts-Strogatz Abb. 2 nachgebaut. Senkrechte Linie beim aktuell gewählten p."""
    ps = [r["p"] if r["p"] > 0 else 1e-5 for r in rows]                 # 0 auf der Log-Achse durch einen kleinen Platzhalter ersetzen
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ps, y=[r["c_ratio"] for r in rows], mode="lines+markers", line=dict(color=TEAL, width=2.6), name="C(p)/C(0)  (Clustering)"))
    fig.add_trace(go.Scatter(x=ps, y=[r["l_ratio"] for r in rows], mode="lines+markers", line=dict(color=ORANGE, width=2.6), name="L(p)/L(0)  (mittlere Weglänge)"))
    cur_x = current_p if current_p > 0 else 1e-5
    fig.add_vline(x=cur_x, line=dict(color=GREY, width=1.6, dash="dot"))
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.16), plot_bgcolor="white")
    fig.update_xaxes(title="Umverdrahtungswahrscheinlichkeit p", type="log", fixedrange=True)
    fig.update_yaxes(title="Verhältnis zu p=0", range=[0, 1.05], autorange=False, fixedrange=True, gridcolor=LIGHT)
    return fig


# --- 3 · Gradverteilung ------------------------------------------------------------------------------------------------------------------------------------------


def _degree_counts(degs):
    """{Grad: Zahl der Knoten mit diesem Grad}, sortiert."""
    counts = {}
    for d in degs:
        counts[d] = counts.get(d, 0) + 1
    return dict(sorted(counts.items()))


def build_degree_histograms(hist):
    """Zwei Zeilen (linear, log-log), drei Spalten (Betriebsnetz, Erdős-Rényi, skalenfreies Netz), gemeinsame Grad-Achse in jeder Zeile. Als Balken über die tatsächlich beobachteten Grade (nicht
    Plotlys eigenes Histogram-Binning), weil Grad=0 und leere Bins auf einer LOG-Achse sonst die automatische Achsenskalierung entgleisen lassen (log(0) ist undefiniert)."""
    names = [("city", "Betriebsnetz"), ("er", "Erdős-Rényi"), ("ba", "Skalenfreies Netz")]
    colors = {"city": TEAL, "er": RED, "ba": ORANGE}
    fig = make_subplots(rows=2, cols=3, subplot_titles=[label for _, label in names] + ["", "", ""], vertical_spacing=0.14)
    max_count = 1
    max_count_log = 1
    for col, (key, _) in enumerate(names, start=1):
        counts = _degree_counts(hist[key])
        degrees = list(counts)
        freqs = list(counts.values())
        max_count = max(max_count, max(freqs, default=1))
        fig.add_trace(go.Bar(x=degrees, y=freqs, marker_color=colors[key], hovertext=[f"Grad {d}: {c} Knoten" for d, c in counts.items()], hoverinfo="text"), row=1, col=col)
        # log-log: Grad=0 kann auf einer log-Achse nicht dargestellt werden (log(0) undefiniert) -- konsequent ausgeschlossen, wie ueblich bei Grad-Verteilungs-Plots
        log_degrees = [d for d in degrees if d > 0]
        log_freqs = [counts[d] for d in log_degrees]
        max_count_log = max(max_count_log, max(log_freqs, default=1))
        fig.add_trace(go.Bar(x=log_degrees, y=log_freqs, marker_color=colors[key], hovertext=[f"Grad {d}: {c} Knoten" for d, c in zip(log_degrees, log_freqs)], hoverinfo="text"), row=2, col=col)
    fig.update_layout(height=560, margin=dict(l=10, r=10, t=40, b=10), showlegend=False, plot_bgcolor="white", bargap=0.15)
    fig.update_xaxes(title="Grad", fixedrange=True, row=1)
    fig.update_xaxes(title="Grad (log, Grad=0 ausgeschlossen)", type="log", fixedrange=True, row=2)
    fig.update_yaxes(title="Zahl der Knoten", range=[0, max_count * 1.08], autorange=False, fixedrange=True, gridcolor=LIGHT, row=1, col=1)
    fig.update_yaxes(title="Zahl der Knoten (log)", type="log", range=[-0.3, math.log10(max_count_log) + 0.3], autorange=False, fixedrange=True, gridcolor=LIGHT, row=2, col=1)
    fig.update_yaxes(range=[0, max_count * 1.08], autorange=False, fixedrange=True, gridcolor=LIGHT, row=1)
    fig.update_yaxes(type="log", range=[-0.3, math.log10(max_count_log) + 0.3], autorange=False, fixedrange=True, gridcolor=LIGHT, row=2)
    return fig


# --- 4 · Assortativität - echt oder nur Gradfolge? -------------------------------------------------------------------------------------------------------------------


def build_degree_degree_scatter(adj):
    """Grad-Grad-Streudiagramm: jeder Punkt eine Kante (beide Richtungen), leicht verrauscht (Jitter) gegen Überlappung."""
    import random as _random
    rng = _random.Random(0)
    deg = [len(a) for a in adj]
    xs, ys = [], []
    for u in range(len(adj)):
        for v in adj[u]:
            if u < v:
                xs += [deg[u] + rng.uniform(-0.15, 0.15), deg[v] + rng.uniform(-0.15, 0.15)]
                ys += [deg[v] + rng.uniform(-0.15, 0.15), deg[u] + rng.uniform(-0.15, 0.15)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers", marker=dict(size=5, color=TEAL, opacity=0.45), hoverinfo="skip"))
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="white")
    fig.update_xaxes(title="Grad des einen Kantenendes", fixedrange=True, gridcolor=LIGHT)
    fig.update_yaxes(title="Grad des anderen Kantenendes", fixedrange=True, gridcolor=LIGHT)
    return fig


def build_assortativity_null_histogram(null):
    """Histogramm der Assortativität unter dem Konfigurationsmodell (viele Ziehungen), Original-r als senkrechte Linie, z-Wert als Annotation."""
    draws = [r for r in null["draws"] if r == r]
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=draws, marker_color=GREY, nbinsx=30, name="Konfigurationsmodell-Ziehungen"))
    if null["original"] == null["original"]:
        fig.add_vline(x=null["original"], line=dict(color=RED, width=2.6), annotation_text=f"Original r={null['original']:.3f}", annotation_position="top")
    z = null["z"]
    z_label = f"z = {z:.2f}" if z == z else "z nicht definiert"
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10), showlegend=False, plot_bgcolor="white", title=dict(text=z_label, x=0.02, font=dict(size=14)))
    fig.update_xaxes(title="Assortativität r (Konfigurationsmodell-Ziehungen)", fixedrange=True)
    fig.update_yaxes(title="Häufigkeit", fixedrange=True, gridcolor=LIGHT)
    return fig
