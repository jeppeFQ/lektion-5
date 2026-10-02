"""
Figurerne.

tegn() laver barometerets figur: tre paneler, ét pr. dimension. Aldrig ét samlet tal.
tegn_opslag() laver figuren til opslagssiden.

Begge returnerer figuren. De printer ikke, og de viser den ikke — det gør appen.
"""

import matplotlib.pyplot as plt

from .referencetal import DIMENSIONER

NAVNE = {"kvinder": "Kvinder", "seniorer": "Seniorer (55+)", "indvandrere": "Indvandrerbaggrund"}

LYS = "#dbe6f6"
MELLEM = "#8fb0e3"
MOERK = "#1f5fbf"
ROED = "#c0392b"


def tegn_panel(ax, navn, egen_andel, raekke):
    """Tegn ét panel: fordelingen i sammenligningsgruppen og arbejdspladsens egen andel."""
    # det brede bånd: fra p10 til p90
    ax.barh(0, raekke["p90"] - raekke["p10"], left=raekke["p10"], height=0.5, color=LYS)

    # det smalle bånd: fra p25 til p75, altså den midterste halvdel
    ax.barh(0, raekke["p75"] - raekke["p25"], left=raekke["p25"], height=0.5, color=MELLEM)

    # medianen som en lodret streg
    ax.plot([raekke["p50"], raekke["p50"]], [-0.25, 0.25], color=MOERK, linewidth=2)

    # arbejdspladsen selv: en rød trekant
    ax.plot(egen_andel, 0, marker="v", markersize=12, color=ROED)

    ax.set_title(NAVNE[navn], fontsize=10)
    ax.set_xlim(0, 1)
    ax.set_yticks([])
    ax.xaxis.set_major_formatter(lambda x, _: f"{x:.0%}")


def tegn(arbejdsplads, referencetal):
    """Tegn alle tre paneler for én arbejdsplads. Returnerer figuren."""
    fig, akser = plt.subplots(1, 3, figsize=(10, 2.6))

    for ax, (dimension_id, navn) in zip(akser, DIMENSIONER.items()):
        raekke, _ = referencetal.find(arbejdsplads, dimension_id)
        tegn_panel(ax, navn, arbejdsplads.andel(navn), raekke)

    fig.tight_layout()
    return fig


def tegn_opslag(tabel):
    """Medianen for hver branche: 2022 som søjle, 2012 som prik. Returnerer figuren."""
    fig, ax = plt.subplots(figsize=(8, 3.8))
    tabel = tabel.sort_values("Median 2022 (%)")

    ax.barh(tabel["Branche"], tabel["Median 2022 (%)"], color=MELLEM, label="2022")
    ax.plot(tabel["Median 2012 (%)"], tabel["Branche"], "o", color=MOERK, label="2012")

    ax.set_xlabel("Median, procent")
    ax.legend(loc="lower right", frameon=False)
    fig.tight_layout()
    return fig
