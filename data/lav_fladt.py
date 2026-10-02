"""
Samler tabellerne til én flad tabel: en "view", som man ville kalde det i en database.

    python3 data/lav_fladt.py

Den afledte fil er en bekvemmelighed. Tabellerne er kilden; den her kan altid
laves igen. Derfor ligger den i data/afledt/.
"""
from pathlib import Path

import pandas as pd

D = Path(__file__).resolve().parent
TABELLER = ["brancher", "regioner", "sektorer", "stoerrelser", "dimensioner",
            "grupper", "fordelinger"]


def laes():
    return {navn: pd.read_csv(D / f"{navn}.csv") for navn in TABELLER}


def flad(t):
    return (t["fordelinger"]
            .merge(t["grupper"], on="gruppe_id")
            .merge(t["brancher"], on="branche_id")
            .merge(t["stoerrelser"], on="stoerrelse_id")
            .merge(t["sektorer"], on="sektor_id")
            .merge(t["regioner"], on="region_id")
            .merge(t["dimensioner"], on="dimension_id")
            [["aar", "dimension", "branche", "stoerrelse", "sektor", "region",
              "antal_arbejdssteder", "p10", "p25", "p50", "p75", "p90"]]
            .sort_values(["aar", "dimension", "branche", "stoerrelse", "sektor", "region"]))


if __name__ == "__main__":
    ud = D / "afledt" / "referencetal.csv"
    tabel = flad(laes())
    tabel.to_csv(ud, index=False)
    print(f"{len(tabel)} rækker skrevet til {ud.relative_to(D.parent)}")
