"""
Opslag: fordelingen i hver branche, uden at taste noget ind.

Det var et af jeres egne ønsker: at man kan se udviklingen fra 2012 til 2022.
"""

DIMENSION_ID = {"kvinder": 1, "seniorer": 2, "indvandrere": 3}


def brancher(referencetal, dimension):
    """Medianen for hver branche i 2012 og 2022 — og ændringen. Returnerer en tabel."""
    tal = referencetal.tal

    udvalg = tal[(tal["dimension_id"] == DIMENSION_ID[dimension])
                 & (tal["branche"] != "Alle")
                 & (tal["stoerrelse"] == "Alle")
                 & (tal["sektor"] == "Alle")]

    # én række pr. branche, én kolonne pr. år
    tabel = udvalg.pivot(index="branche", columns="aar", values="p50") * 100
    tabel["Ændring"] = tabel[2022] - tabel[2012]

    tabel = tabel.round(1).reset_index()
    tabel.columns = ["Branche", "Median 2012 (%)", "Median 2022 (%)", "Ændring (procentpoint)"]
    return tabel.sort_values("Median 2022 (%)", ascending=False)
