# Strukturkennzahlen & Nullmodelle – Clustering, Kleine Welt, Assortativität – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-strukturkennzahlen-demo.streamlit.app/)**

Siebtes Stück der **Graphen-und-Netzwerke-Reihe** der "Konzepte"-Reihe für die Website "Sebastian Hanisch – Operations Research und Machine Learning", Kind von Stück 6 (Zentralität, [centrality-demo](https://github.com/sebastian-hanisch/centrality-demo)): dort wurden einzelne Knoten und Kanten bewertet, jetzt geht es um das Netz als Ganzes. Drei klassische Fragen der Netzwerkanalyse, jede über einen Vergleich mit einem **Nullmodell** beantwortet, nicht durch bloßes Ansehen: **Clustering** (wie oft sind die Nachbarn eines Knotens auch untereinander verbunden?), die **Kleine-Welt-Eigenschaft** (Watts und Strogatz 1998: hohes Clustering UND kurze mittlere Weglänge gleichzeitig – ein scheinbarer Widerspruch, den schon eine winzige zufällige Umverdrahtung auflöst), **Assortativität** (Newman 2002: hängen sich hochgradige Knoten eher an andere hochgradige oder an schwachgradige?). Die zentrale methodische Frage: ist eine gemessene Eigenschaft etwas Eigenes, oder folgt sie schon zwangsläufig aus der bloßen Gradfolge? Antwort über **gradfolgen-erhaltende Randomisierung** (Maslov und Sneppen 2002, Kanten-Doppeltausch) gegen **Erdős-Rényi** G(n,m) (Erdős und Rényi 1959, zerstört auch die Gradfolge selbst).

**Einordnung in die Reihe:** die Reihe hat dreizehn Stücke (zwölf im Baum, dazu die Fall-Demo interne-verlinkung-demo), dies ist das siebte (Details in `graphen-planung/PLAN.md` des Portfolio-Ordners):

```
1 BFS und DFS (Wurzel)                                                        [gebaut: bfs-dfs-demo]
 ├─ 2 Brücken und Artikulationspunkte ─ 4 Euler-Touren                        [gebaut: bridges-demo, euler-tour-demo]
 ├─ 3 Starke Zusammenhangskomponenten, topologische Sortierung                [gebaut: scc-demo]
 ├─ 5 Graphfärbung                                                            [gebaut: graph-coloring-demo]
 ├─ 6 Zentralität ─ 7 Strukturkennzahlen                                      [gebaut: centrality-demo ─ DIESES STÜCK]
 │        ├─ 8 Robustheit ─ 9 Kaskaden und Ausbreitung                        [gebaut: robustheit-demo ─ kaskaden-demo]
 │        └─ 10 Kritische Knoten härten                                       [gebaut: haertung-demo]
 └─ 11 Bandbreite ─ 12 Bandbreite von G(n,k,b) und Cliquenüberdeckung         [gebaut: bandbreite-demo ─ cliquenbandbreite-demo]
```

Ergebnis in Kürze: Das Betriebsnetz (Straßenraster) ist **strukturell dreieckfrei** (bipartiter Graph – Clustering und Transitivität sind exakt 0, kein Messfehler). Schon bei einer Umverdrahtungswahrscheinlichkeit von **p=0.01** (1 % der Kanten) fällt die mittlere Weglänge eines Ring-Gitters auf **53 %** ihres Ausgangswerts, während das Clustering noch bei **98 %** bleibt – genau die Watts-Strogatz-Signatur. Die Disassortativität des skalenfreien Netzes (Barabási-Albert, r=−0.17) folgt dagegen weitgehend schon aus seiner **Gradfolge**: das Konfigurationsmodell liefert im Mittel −0.11 (z=−1.88 gegen 200 Ziehungen, knapp unter der Schwelle |z|=2) – ebenso wie Assortativität und Clustering des Betriebsnetzes bzw. des Rings bei p=0.01, die **nicht** signifikant von der bloßen Gradfolge unterscheidbar sind (|z|<2).

## Warum dieses Problem

Ist ein gemessenes Netzwerkmerkmal – hohes Clustering, positive oder negative Assortativität – eine eigenständige, interessante Eigenschaft des Netzes, oder folgt es schon zwangsläufig aus etwas viel Einfacherem: der bloßen Verteilung der Grade? Diese Frage lässt sich nicht durch Anschauen beantworten, nur durch einen Vergleich mit einem **Nullmodell**, das genau die interessierende Eigenschaft (hier: die Gradfolge) exakt beibehält, aber alles andere randomisiert. Das Konfigurationsmodell (Maslov und Sneppen 2002, Kanten-Doppeltausch) leistet das; Erdős-Rényi G(n,m) dient als Kontrast, der auch die Gradfolge selbst zerstört. Die Watts-Strogatz-Kleine-Welt-Konstruktion zeigt zusätzlich, wie ein scheinbarer Widerspruch (hohes Clustering und kurze Wege) durch einen winzigen Kontrollparameter (die Umverdrahtungswahrscheinlichkeit p) aufgelöst wird.

Abgrenzung: kein formaler Machtgesetz-Test für die Gradverteilung (Clauset, Shalizi und Newman 2009 nur genannt) – nur Histogramme und ein informelles Heavy-Tail-Verhältnis (Maximalgrad/mittlerer Grad).

## Vorab-Hypothesen (vor der Messung notiert, hier geprüft)

| Hypothese | Ergebnis |
|---|---|
| **H1** Clustering, Transitivität, mittlere Weglänge und Assortativität stimmen mit networkx überein. | ✅ Bestätigt auf über 380 Instanzen (Betriebsnetz, Ring, skalenfreies Netz, Sonderfälle). |
| **H2** Das Betriebsnetz (Raster) hat wie ein echtes Straßennetz ein kleines, aber positives Clustering. | ❌ **Widerlegt:** das Raster ist bipartit und darum STRUKTURELL dreieckfrei – C=T=0 exakt, bei jedem Seed und Sperranteil. Erst der Zufallsgraph gleicher Kantenzahl zeigt positives Clustering (0.0374). |
| **H3** Schon eine winzige Umverdrahtung (kleines p) senkt die mittlere Weglänge stark, ohne das Clustering nennenswert zu senken. | ✅ Bestätigt: bei p=0.01 ist L/L(0)=0.53 (fast halbiert), C/C(0)=0.975 (kaum verändert) – die klassische Watts-Strogatz-Kleine-Welt-Signatur. |
| **H4** Das Ring-Gitter-Clustering bei p=0 stimmt mit der geschlossenen Form C=3(k-2)/(4(k-1)) exakt überein. | ✅ Bestätigt als **Satz**, nicht nur beobachtet: exakte Übereinstimmung für k=4,6,8,10,12,16,20. |
| **H5** Das skalenfreie Netz ist disassortativ, weil seine schiefe Gradverteilung das erzwingt. | ✅ **Weitgehend bestätigt:** r=−0.17; das Konfigurationsmodell (gleiche Gradfolge) liefert im Mittel −0.11 (Std 0.029), z=−1.88 gegen 200 Ziehungen – knapp nicht signifikant (Betrag von z unter 2), der Großteil der Disassortativität folgt also aus der Gradfolge. (Eine frühere Fassung zeigte z=+25: ein Artefakt des Doppeltauschs, der die Kanten immer als (kleiner, größerer) Endpunkt paarte und so nicht gleichverteilt zog; mit zufälliger Paarung und gegen `networkx.double_edge_swap` geprüft verschwindet der Effekt.) |
| **H6** Die Assortativität des Betriebsnetzes und des Rings ist eine eigenständige Eigenschaft, keine Folge der Gradfolge. | ❌ **Widerlegt:** Betriebsnetz z=1.51, Ring (p=0.01) z=−1.08 – beide NICHT signifikant (\|z\|<2), mit der bloßen Gradfolge verträglich. |
| **H7** Das Konfigurationsmodell zerstört das hohe Clustering eines Ring-Gitters trotz identischer Gradfolge. | ✅ Bestätigt: Ring-Clustering 0.6429 fällt bei einer Konfigurationsmodell-Realisierung auf 0.0268 (Erdős-Rényi-Niveau 0.0396) – das Clustering kommt aus der geometrischen Anordnung, nicht aus der Gradfolge. |
| **H8** Das skalenfreie Netz zeigt eine sichtbar langschwänzigere Gradverteilung als Betriebsnetz und Erdős-Rényi. | ✅ Bestätigt: Verhältnis Maximalgrad/mittlerer Grad 8.84 (BA) gegen 2.78 (Erdős-Rényi) gegen 1.39 (Betriebsnetz). |

## Befunde (gemessen, keine Behauptungen)

Standardeinstellungen, Seed 35, sofern nicht anders angegeben; alle Verfahren sind deterministisch, die Instanzen kommen aus Python-`random` mit festem Seed.

| Frage | Ergebnis |
|---|---|
| **Stimmt das Verfahren?** | ✅ Clustering/Transitivität/mittlere Weglänge/Assortativität == networkx auf über 380 Instanzen; Erdős-Rényi- und Konfigurationsmodell-Invarianten (exakte Kantenzahl bzw. Gradfolge) über je ≥200 Instanzen |
| **Betriebsnetz Raster (100 Knoten, 144 Straßen)** | C=T=0.0000 EXAKT (bipartit), L=7.1516, r=0.10 (z=1.51, nicht signifikant) |
| **Zufallsgraph gleicher Größe (180 Kanten)** | C=0.0374 (nahe einer Erdős-Rényi-Stichprobe 0.0248, Erwartungswert 0.0364), L=3.5066 |
| **Watts-Strogatz-Übergang** (n=200, k=8) | p=0.001: C/C(0)=0.9959, L/L(0)=0.9112 — p=0.01: C/C(0)=0.9751, **L/L(0)=0.5300** — p=0.1: C/C(0)=0.7372, L/L(0)=0.2832 |
| **Ring-Gitter von Hand** | C(p=0) exakt gleich 3(k-2)/(4(k-1)) für k=4,6,8,10,12,16,20 (z. B. k=8: 0.642857) |
| **Konfigurationsmodell zerstört Ring-Clustering** | C=0.6429 (Original) → C=0.0268 (Konfigurationsmodell, 5000 Doppeltausch-Versuche) |
| **Gradverteilung (Heavy-Tail-Verhältnis Max/Mittel)** | Betriebsnetz 1.39, Erdős-Rényi 2.78, skalenfreies Netz **8.84** |
| **Assortativität gegen Konfigurationsmodell-Nullverteilung (200 Ziehungen)** | Betriebsnetz r=0.10, z=1.51 (nicht signifikant) — Ring (p=0.01) r=−0.04, z=−1.08 (nicht signifikant) — skalenfreies Netz r=−0.17, z=−1.88 (Nullmodell-Mittel −0.11, knapp nicht signifikant) |

Presets (8), alle mit den Zahlen in ihren Hilfetexten (`tests/test_presets.py`):

| Preset | Was es zeigt |
|---|---|
| Betriebsnetz Standardfall | 100 Kreuzungen, 144 Straßen: C=T=0 exakt (bipartit) |
| Zufallsgraph-Kontrast | 100 Knoten, 180 Kanten: C=0.0374, nahe Erdős-Rényi (Erwartungswert 0.0364; Stichprobe 0.0248) |
| Watts-Strogatz-Lehrbuch (Ring von Hand) | Reines Ring-Gitter (p=0): C=0.6429 exakt = 3(k-2)/(4(k-1)), ω=−0.79 (gitterartig) |
| Kleine-Welt-Übergang (p-Sweep) | p=0.01: L/L(0)=0.53, C/C(0)=0.975 – die Watts-Strogatz-Signatur |
| Skalenfreies Netz (Heavy Tail) | Heavy-Tail-Verhältnis 8.84 gegen 1.39 (Betriebsnetz) und 2.78 (Erdős-Rényi) |
| Assortativität-Test (Betriebsnetz gegen Konfigurationsmodell) | r=0.10, z=1.51 – nicht signifikant |
| Konfigurationsmodell zerstört Clustering | Ring-C fällt von 0.6429 auf 0.0268 unter dem Konfigurationsmodell |
| BA ist disassortativ | r=−0.17, Konfigurationsmodell im Mittel −0.11 (z=−1.88): die Disassortativität folgt weitgehend aus der Gradfolge |

## Modell und Verfahren

- **Betriebsnetz** (`sk_scenario.py`, `generate`): gestörtes Straßenraster mit gesperrtem Anteil oder Zufallsgraph gleicher Kantenzahl (wortgleich aus `centrality-demo`/`cen_scenario.py` übernommen).
- **Ring-Umverdrahtung** (`ring_lattice_instance`, Watts und Strogatz 1998): n Knoten im Kreis, Gesamtgrad k (k/2 Nachbarn je Seite, wie im Originalpapier), jede Kante wird mit Wahrscheinlichkeit p durch eine zufällige Kante ersetzt.
- **Skalenfreies Netz** (`barabasi_albert_instance`, Barabási und Albert 1999): Kern aus m0 Knoten (Kreis, m0 Kanten), jeder weitere Knoten hängt sich mit m Kanten proportional zum Grad an bereits vorhandene Knoten an (Kantenenden-Liste für effiziente gewichtete Ziehung). Exakte Kantenzahl m0+(n-m0)·m, per Konstruktion zusammenhängend.
- **Clustering** (`clustering_coefficient`, `average_clustering`, `transitivity`): lokaler Koeffizient je Knoten, mittlerer Koeffizient, globale Transitivität (Watts und Strogatz 1998).
- **Mittlere Weglänge** (`average_distance`): Mittelwert über alle erreichbaren ungeordneten Knotenpaare – wohldefiniert auch bei unzusammenhängenden Netzen, anders als `networkx.average_shortest_path_length`.
- **Assortativität** (`degree_assortativity`, Newman 2002): Pearson-Korrelation der Grade an beiden Enden jeder Kante (beide Richtungen).
- **Erdős-Rényi G(n,m)** (`erdos_renyi_gnm`, Erdős und Rényi 1959): m verschiedene Kantenpaare gleichverteilt gezogen – zerstört auch die Gradfolge.
- **Konfigurationsmodell** (`configuration_null`, Maslov und Sneppen 2002): Kanten-Doppeltausch (zufällige Paarung der Endpunkte), Gradfolge exakt erhalten.
- **ω** (`omega_watts_strogatz`, Telesford u. a. 2011): ω = L_rand/L − C/C_lattice, nur auf der Ring-Umverdrahtungs-Instanz definiert.

## Was die App zeigt

1. **Vier Schritte** (Schritt-Regler): **Netz gegen sein Gegenstück** (drei Karten mit denselben Knotenpositionen: Original, Erdős-Rényi, Konfigurationsmodell, plus Kennzahltabelle) → **Watts-Strogatz-Übergang** (Ring-Karte mit hervorgehobenen "Abkürzungen", C(p)/C(0)- und L(p)/L(0)-Kurve über p, ω-Metrik) → **Gradverteilung** (Histogramme linear und log-log, Betriebsnetz/Erdős-Rényi/skalenfreies Netz nebeneinander, Heavy-Tail-Verhältnis) → **Assortativität – echt oder nur Gradfolge?** (Grad-Grad-Streudiagramm, Nullverteilung unter dem Konfigurationsmodell mit Original-r und z-Wert).
2. Regler: Instanz (Betriebsnetz / Ring-Umverdrahtung / Skalenfreies Netz), instanzspezifische Parameter (Seitenlänge/Netztyp/Sperranteil bzw. n/k/p bzw. n/m0/m), Zahl der Doppeltausch-Versuche (nur Schritte 1 und 4, wo das Konfigurationsmodell tatsächlich verwendet wird), Zufalls-Seed (+🎲), Nachbarreihenfolge; Permalink in der Adresszeile.
3. Schritt 2 (Watts-Strogatz-Übergang) ist nur für die Ring-Umverdrahtungs-Instanz sinnvoll definiert – bei anderen Instanzen erscheint ein Hinweis statt eines Absturzes.

## Was nicht funktioniert hat / Grenzen

- **ω nur auf dem Ring-Modell definiert.** Bei Betriebsnetz und skalenfreiem Netz fehlt ein natürliches "C_lattice" – nur die rohen Kennzahlen gegen die Nullmodelle sind gezeigt, kein ω.
- **Ring-Gitter-Parameter k ist der GESAMTGRAD**, nicht "Nachbarn je Seite" – nötig, damit die geschlossene Form C=3(k-2)/(4(k-1)) exakt gilt (Watts und Strogatz 1998 selbst verwenden k als Gesamtgrad; eine erste Implementierung mit "k Nachbarn je Seite" hätte die Formel nicht exakt erfüllt).
- **Konfigurationsmodell-Doppeltausch ist ein fester Vorgabewert**, keine Konvergenzprüfung der Mischzeit.
- **Heavy-Tail-Verhältnis ist informell.** Kein formaler Machtgesetz-Test (Clauset, Shalizi und Newman 2009 nur genannt, bewusst nicht gebaut).
- **Betriebsnetz-Raster ist strukturell dreieckfrei** (bipartit) – für ein Clustering-Beispiel ist der Zufallsgraph oder das Ring-Modell aussagekräftiger.
- **Assortativität ist ein globaler Mittelwert.** Sagt nichts über lokale Cluster hochgradiger Knoten aus.
- **Synthetische Instanzen.** Betriebsnetz, Ring und skalenfreies Netz sind erzeugt, keine echten Sozial- oder Infrastrukturnetzdaten.

## Design-Entscheidung: Ring-Gitter-Parameter k als Gesamtgrad

Die erste Fassung parametrisierte das Ring-Gitter über "k Nachbarn je Seite" (Knotengrad 2k). Die Korrektheits-Kette (Punkt 7: C(p=0) muss exakt der geschlossenen Form 3(k-2)/(4(k-1)) entsprechen) deckte dabei einen Widerspruch auf: diese Formel ist bei Watts und Strogatz (1998) selbst mit k als **Gesamtgrad** definiert, nicht mit "Nachbarn je Seite". Die Demo übernimmt darum die Original-Konvention: k ist der Gesamtgrad (muss gerade sein, k/2 Nachbarn je Seite) – damit stimmt die geschlossene Form exakt, für mehrere k gegengerechnet.

## Tests

`tests/test_scenario.py` (Rauchtests der drei Instanzen), `tests/test_algorithm.py` (Korrektheits-Kette, 9 Punkte: Clustering/Transitivität/mittlere Weglänge/Assortativität gegen networkx auf über 380 Instanzen, Erdős-Rényi- und Konfigurationsmodell-Invarianten, Ring-Gitter von Hand für 7 k-Werte, ω-Formel, Sonderfälle), `tests/test_evaluation.py`, `tests/test_presets.py` (jede Zahl der Hilfetexte), `tests/test_claims.py` (jede README-Zahl über die echten Auswertungsfunktionen, inkl. des überraschenden BA-Befunds), `tests/test_app.py` (AppTest – Voreinstellung, jedes Preset, jeder Schritt für jede Instanzart, bedingte Regler inkl. m≤m0-Kopplung beim skalenfreien Netz, Permalink-Grenzen, Footer). 124 Tests insgesamt.

```
python -m pytest tests/ -v
```

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-App |
| `sk_algorithm.py` | Clustering, Transitivität, mittlere Weglänge, Assortativität, Erdős-Rényi, Konfigurationsmodell, ω |
| `sk_scenario.py` | Betriebsnetz, Ring-Umverdrahtung, skalenfreies Netz |
| `sk_evaluation.py` | Analyse, Watts-Strogatz-Sweep, Assortativitäts-Nullverteilung, Gradverteilungen |
| `sk_visualization.py` | Plotly-Figuren (Netzvergleich, Ring-Karte, Übergangskurve, Histogramme, Streudiagramm) |
| `sk_presets.py`, `sk_constants.py` | Permalink, Presets, gemessene Werte |
| `tests/` | Tests |

## Bewusst nicht umgesetzt

Robustheit, Kaskaden und Ausbreitung, kritische Knoten härten, Bandbreite – eigene Stücke der Reihe. Formaler Machtgesetz-Test der Gradverteilung (Clauset, Shalizi und Newman 2009).

## Lokal ausführen

```
python -m venv venv
venv\Scripts\pip install -r requirements-dev.txt
venv\Scripts\streamlit run app.py
```

## Literatur

- Watts, D. J., & Strogatz, S. H. (1998). *Collective dynamics of 'small-world' networks.* Nature 393, 440–442.
- Newman, M. E. J. (2002). *Assortative mixing in networks.* Physical Review Letters 89(20), 208701.
- Maslov, S., & Sneppen, K. (2002). *Specificity and stability in topology of protein networks.* Science 296(5569), 910–913.
- Barabási, A.-L., & Albert, R. (1999). *Emergence of scaling in random networks.* Science 286(5439), 509–512.
- Telesford, Q. K., Joyce, K. E., Hayasaka, S., Burdette, J. H., & Laurienti, P. J. (2011). *The ubiquity of small-world networks.* Brain Connectivity 1(5), 367–375.
- Erdős, P., & Rényi, A. (1959). *On random graphs I.* Publicationes Mathematicae Debrecen 6, 290–297.
- Clauset, A., Shalizi, C. R., & Newman, M. E. J. (2009). *Power-law distributions in empirical data.* SIAM Review 51(4), 661–703 (nur als rigoroser Weg genannt, einen Machtgesetz-Test durchzuführen – hier bewusst nicht gebaut).

Gebaut mit Streamlit, Plotly, NumPy und pandas.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Graphen und Netzwerke: BFS bis Cliquenbandbreite](https://sebastianhanisch.net/konzepte-graphen-netzwerke.html).
