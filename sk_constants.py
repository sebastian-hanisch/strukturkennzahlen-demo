"""Regler-Grenzen, feste Annahmen, gemessene Werte und Presets."""

SPACING = 1.0                    # Abstand der Kreuzungen im Betriebsnetz-Raster
JITTER = 0.18
SEED_MAX = 999999
DEFAULT_SEED = 35

KINDS = ("city", "ring", "ba")
KIND_LABELS = {"city": "Betriebsnetz (Raster/Zufallsgraph)", "ring": "Ring-Umverdrahtung (Watts-Strogatz)", "ba": "Skalenfreies Netz (Barabási-Albert)"}

# --- Betriebsnetz (wortgleich aus centrality-demo) -------------------------------------------------------------------------------------------------------
SIDE_MIN, SIDE_MAX, DEFAULT_SIDE = 4, 18, 10
NETTYPES = ("grid", "random")
NETTYPE_LABELS = {"grid": "Raster (Straßennetz)", "random": "Zufallsgraph (gleiche Kantenzahl)"}
BLOCKED_OPTIONS = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6)
DEFAULT_BLOCKED = 0.2

# --- Ring-Umverdrahtung (Watts und Strogatz 1998) --------------------------------------------------------------------------------------------------------
# N_RING_MIN so hoch gewählt, dass JEDE K_RING_OPTIONS-Wahl bei JEDEM erlaubten n_ring gültig ist (k/2 <= (n-1)//2) - kein Reglergrenzen-Nachrechnen im UI nötig.
N_RING_MIN, N_RING_MAX, DEFAULT_N_RING = 30, 400, 200
K_RING_OPTIONS = (4, 6, 8, 10, 12, 16, 20)                  # Gesamtgrad (gerade, wie bei Watts und Strogatz selbst - k/2 Nachbarn je Seite)
DEFAULT_K_RING = 8
P_REWIRE_OPTIONS = (0.0, 0.0001, 0.0003, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0)
DEFAULT_P_REWIRE = 0.01
P_SWEEP = P_REWIRE_OPTIONS

# --- Skalenfreies Netz (Barabási und Albert 1999) --------------------------------------------------------------------------------------------------------
N_BA_MIN, N_BA_MAX, DEFAULT_N_BA = 30, 400, 200
M0_BA_MIN, M0_BA_MAX, DEFAULT_M0_BA = 3, 12, 4               # Kerngröße (Kreis aus m0 Knoten)
M_BA_MIN, DEFAULT_M_BA = 1, 2                                 # oberes Ende von m ist immer das gewählte m0 (m <= m0)

# --- Konfigurationsmodell (Kanten-Doppeltausch, Maslov und Sneppen 2002) ---------------------------------------------------------------------------------
N_SWAPS_MIN, N_SWAPS_MAX, DEFAULT_N_SWAPS = 100, 20000, 5000
N_DRAWS_ASSORT = 200                                          # Ziehungen für die Nullverteilung der Assortativität (Schritt 4)

ORDERS = ("fixed", "shuffled")
ORDER_LABELS = {"fixed": "feste Reihenfolge (nach Knotennummer)", "shuffled": "gemischt (nach Seed)"}

STEPS = {1: "1 · Netz gegen sein Gegenstück", 2: "2 · Watts-Strogatz-Übergang", 3: "3 · Gradverteilung", 4: "4 · Assortativität - echt oder nur Gradfolge?"}
SWEEP_SEEDS = tuple(range(100000, 100005))

# --- Gemessene Werte (Standardeinstellungen, Seed 35, sofern nicht anders angegeben; alle Verfahren sind deterministisch, die Instanzen kommen aus
# --- Python-`random` mit festem Seed und ändern sich nie mit einer Bibliotheksversion; 2026-09-27, alle Werte über ev.* nachgerechnet, s. tests/test_claims.py) ---
# BETRIEBSNETZ IST STRUKTURELL DREIECKFREI: das Raster ist ein bipartiter Graph (nur waagerechte/senkrechte Kanten, keine Diagonalen) - C=T=0 EXAKT bei jedem
#   Seed und jedem Sperranteil beim Netztyp "grid" (keine Messungenauigkeit, ein mathematischer Fakt: bipartite Graphen sind dreieckfrei). Der Zufallsgraph
#   gleicher Kantenzahl hat dagegen ein kleines, aber positives Clustering (C=0.0374 bei Standardgröße), nahe am Erdős-Rényi-Erwartungswert (C_ER=0.0248).
# WATTS-STROGATZ-ÜBERGANG (n=200, k=8, Seed 35): bei p=0.001 ist C/C(0) noch 0.9959, aber L/L(0) schon auf 0.9112 gefallen; bei p=0.01 (Vorgabewert) ist
#   C/C(0)=0.9751 (kaum verändert) gegen L/L(0)=0.5300 (schon halbiert!) - der scheinbare Widerspruch (hohes Clustering UND kurze Wege) tritt schon bei
#   winzigen Umverdrahtungsanteilen auf. Bei p=0.1 ist L/L(0) bereits auf 0.2832 gefallen, während C/C(0) mit 0.7372 noch deutlich über dem Zufallsniveau liegt.
# GRADVERTEILUNG (Standardgröße, Seed 35): Verhältnis Maximalgrad/mittlerer Grad (informeller Heavy-Tail-Hinweis, KEIN Machtgesetz-Test) - Betriebsnetz
#   (Raster) 1.39, Erdős-Rényi gleicher Größe 2.78, skalenfreies Netz 8.84 - deutlich langschwänziger als beide Vergleichsnetze.
# ASSORTATIVITÄT GEGEN KONFIGURATIONSMODELL-NULLVERTEILUNG (200 Ziehungen, Seed 35): Betriebsnetz r=0.10, z=1.35 gegen die Nullverteilung - NICHT
#   signifikant, mit der bloßen Gradfolge verträglich. Ring bei p=0.01: r=-0.04, z=-1.13 - ebenfalls nicht signifikant. ÜBERRASCHUNG beim skalenfreien Netz:
#   r=-0.17 (disassortativ), aber z=+25.1 gegen die Nullverteilung (Nullmodell-Mittelwert -0.36) - das gemessene Netz ist SIGNIFIKANT WENIGER disassortativ
#   als die Gradfolge allein erwarten ließe. Bevorzugte Anbindung erzeugt also eine andere, mildere Form von Disassortativität als rein zufälliges Neu-
#   Verdrahten derselben Gradfolge - die Disassortativität skalenfreier Netze ist keine bloße Folge ihrer schiefen Gradverteilung, sondern eine eigenständige
#   Eigenschaft des Wachstumsprozesses selbst.
# KONFIGURATIONSMODELL ZERSTÖRT DAS RING-CLUSTERING: das reine Ring-Gitter (n=200, k=8, p=0) hat C=0.6429 (== 3(k-2)/(4(k-1)) exakt) - eine einzelne
#   Konfigurationsmodell-Realisierung (5000 Doppeltausch-Versuche, gleiche Gradfolge) fällt auf C=0.0145, fast auf Erdős-Rényi-Niveau (0.0396). Das hohe
#   Clustering des Rings kommt NICHT aus der Gradfolge (jeder Knoten hat Grad 8), sondern aus der geometrischen Nachbarschaftsstruktur selbst.

PRESETS = {
    "Betriebsnetz Standardfall": {"kind": "city", "side": 10, "blocked": 0.2, "nettype": "grid", "seed": 35, "step": 1},
    "Zufallsgraph-Kontrast": {"kind": "city", "side": 10, "blocked": 0.0, "nettype": "random", "seed": 35, "step": 1},
    "Watts-Strogatz-Lehrbuch (Ring von Hand)": {"kind": "ring", "nring": 200, "kring": 8, "prewire": 0.0, "seed": 35, "step": 2},
    "Kleine-Welt-Übergang (p-Sweep)": {"kind": "ring", "nring": 200, "kring": 8, "prewire": 0.01, "seed": 35, "step": 2},
    "Skalenfreies Netz (Heavy Tail)": {"kind": "ba", "nba": 200, "mba": 2, "m0ba": 4, "seed": 35, "step": 3},
    "Assortativität-Test (Betriebsnetz gegen Konfigurationsmodell)": {"kind": "city", "side": 10, "blocked": 0.2, "nettype": "grid", "seed": 35, "step": 4},
    "Konfigurationsmodell zerstört Clustering": {"kind": "ring", "nring": 200, "kring": 8, "prewire": 0.0, "seed": 35, "step": 1},
    "BA ist disassortativ": {"kind": "ba", "nba": 200, "mba": 2, "m0ba": 4, "seed": 35, "step": 4},
}
PRESET_HELP = {
    "Betriebsnetz Standardfall": "100 Kreuzungen, 144 Straßen: das Raster ist bipartit und darum STRUKTURELL dreieckfrei - Clustering C=0.0000 und Transitivität T=0.0000 EXAKT (kein Messfehler, "
                                 "ein mathematischer Fakt für jeden Sperranteil). Mittlere Weglänge L=7.15, Assortativität r=0.10.",
    "Zufallsgraph-Kontrast": "100 Knoten, 180 Kanten, ein reiner Zufallsgraph statt Raster: Clustering C=0.0374 - nicht null wie beim Raster, aber nahe am Erdős-Rényi-Erwartungswert (C_ER=0.0248) "
                             "gleicher Größe. Mittlere Weglänge L=3.51, deutlich kürzer als das Raster (7.15) bei mehr Kanten.",
    "Watts-Strogatz-Lehrbuch (Ring von Hand)": "Reines Ring-Gitter (n=200, k=8, p=0, keine Umverdrahtung): Clustering C=0.6429, exakt gleich der geschlossenen Form 3(k-2)/(4(k-1))=18/28. Mittlere "
                                                "Weglänge L=12.94 - fast wie ein Pfad. ω=-0.79: klar gitterartig, kein 'kleine Welt'-Netz ohne Umverdrahtung.",
    "Kleine-Welt-Übergang (p-Sweep)": "Bei nur p=0.01 (1 % der Kanten neu verdrahtet) sinkt die mittlere Weglänge schon auf 53 % des Gitterwerts (L/L(0)=0.53), während das Clustering noch bei 98 % "
                                      "bleibt (C/C(0)=0.975) - genau der scheinbare Widerspruch, den Watts und Strogatz 1998 auflösten. ω steigt von -0.79 (reines Gitter) auf -0.57.",
    "Skalenfreies Netz (Heavy Tail)": "200 Knoten, 396 Kanten (m0=4, m=2): der Maximalgrad ist 8.84-mal so groß wie der mittlere Grad - beim Betriebsnetz nur das 1.39-Fache, beim Zufallsgraph "
                                      "gleicher Größe das 2.78-Fache. Deutlich langschwänziger als beide, aber kein formaler Machtgesetz-Test (Clauset u. a. 2009, hier bewusst nicht gebaut).",
    "Assortativität-Test (Betriebsnetz gegen Konfigurationsmodell)": "Das Betriebsnetz hat eine leicht positive Assortativität (r=0.10), aber der z-Wert gegen 200 Konfigurationsmodell-Ziehungen "
                                                                      "ist nur 1.35 - NICHT signifikant: dieser Wert ist mit der bloßen Gradfolge verträglich, keine eigenständige Eigenschaft.",
    "Konfigurationsmodell zerstört Clustering": "Das reine Ring-Gitter hat C=0.6429 - eine einzelne Konfigurationsmodell-Realisierung (gleiche Gradfolge, 5000 Doppeltausch-Versuche) fällt auf "
                                                 "C=0.0145, fast auf Erdős-Rényi-Niveau (0.0396). Das hohe Clustering kommt NICHT aus der Gradfolge (jeder Knoten Grad 8), sondern aus der "
                                                 "geometrischen Anordnung selbst.",
    "BA ist disassortativ": "Das skalenfreie Netz ist disassortativ (r=-0.17), aber ÜBERRASCHEND: der z-Wert von +25.1 gegen 200 Konfigurationsmodell-Ziehungen (Nullmodell-Mittelwert -0.36) zeigt, "
                            "dass es sogar WENIGER disassortativ ist als die Gradfolge allein erwarten ließe - bevorzugte Anbindung erzeugt eine andere Form von Disassortativität als reines "
                            "Zufallspaaren gleicher Grade.",
}
