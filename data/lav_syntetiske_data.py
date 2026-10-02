"""
Laver et SYNTETISK referencedatasæt, delt op i tabeller som i en database.

    python3 data/lav_syntetiske_data.py

Tallene er opdigtede. De findes, så vi kan bygge barometeret, før de rigtige
aggregater fra Danmarks Statistik ligger klar. Strukturen er den rigtige, det
er kun værdierne, der ikke er det.

Tabellerne:

    brancher.csv      branche_id, branche
    regioner.csv      region_id, region
    sektorer.csv      sektor_id, sektor
    stoerrelser.csv   stoerrelse_id, stoerrelse, min_ansatte, max_ansatte
    dimensioner.csv   dimension_id, dimension, navn, beskrivelse
    grupper.csv       gruppe_id + de fem id'er + aar + antal_arbejdssteder
    fordelinger.csv   gruppe_id, dimension_id, p10, p25, p50, p75, p90
    metadata.csv      oplysninger om datasættet selv

Id 0 betyder "Alle" i alle opslagstabeller. Det er sådan, en bredere
sammenligningsgruppe bliver mulig.
"""

from pathlib import Path

import numpy as np
import pandas as pd

UD = Path(__file__).resolve().parent
rng = np.random.default_rng(2026)

# --- opslagstabeller --------------------------------------------------------

BRANCHER = [
    "Alle",
    "Undervisning",
    "Sundhed og socialvæsen",
    "Handel",
    "Industri",
    "Bygge og anlæg",
    "Transport",
    "Offentlig administration",
    "Information og kommunikation",
]

REGIONER = ["Alle", "Hovedstaden", "Sjælland", "Syddanmark", "Midtjylland", "Nordjylland"]

SEKTORER = ["Alle", "Offentlig", "Privat"]

STOERRELSER = [
    ("Alle", 50, 100000),
    ("50-99", 50, 99),
    ("100-249", 100, 249),
    ("250-499", 250, 499),
    ("500+", 500, 100000),
]

DIMENSIONER = [
    ("kvinder", "Kvinder", "Andel af stillingerne besat af kvinder"),
    ("seniorer", "Seniorer", "Andel af stillingerne besat af personer på 55 år eller derover"),
    ("indvandrere", "Indvandrerbaggrund",
     "Andel af stillingerne besat af indvandrere og efterkommere"),
]

AAR = [2012, 2022]

# Opdigtede niveauer pr. branche: (kvinder, seniorer, indvandrere)
NIVEAUER = {
    "Undervisning": (0.68, 0.26, 0.07),
    "Sundhed og socialvæsen": (0.80, 0.23, 0.12),
    "Handel": (0.45, 0.14, 0.13),
    "Industri": (0.28, 0.22, 0.17),
    "Bygge og anlæg": (0.11, 0.19, 0.15),
    "Transport": (0.24, 0.25, 0.21),
    "Offentlig administration": (0.58, 0.29, 0.06),
    "Information og kommunikation": (0.33, 0.15, 0.14),
}

# Opdigtet regional forskel, kun for indvandrerbaggrund
REGIONSFORSKEL = {
    "Hovedstaden": 0.055, "Sjælland": -0.010, "Syddanmark": 0.000,
    "Midtjylland": -0.005, "Nordjylland": -0.035,
}

# Opdigtet forskel mellem sektorerne
SEKTORFORSKEL = {"Offentlig": (0.09, 0.03, -0.02), "Privat": (-0.06, -0.02, 0.01)}

AARSSKIFT = {2012: -0.025, 2022: 0.0}      # lidt lavere andele i 2012


def percentiler(midte, spredning=0.12):
    """Fem percentiler omkring en midte. Afstandene er normalfordelingens."""
    afstande = np.array([-1.282, -0.674, 0.0, 0.674, 1.282]) * spredning
    return np.clip(midte + afstande, 0.0, 1.0).round(3)


def byg():
    brancher = pd.DataFrame({"branche_id": range(len(BRANCHER)), "branche": BRANCHER})
    regioner = pd.DataFrame({"region_id": range(len(REGIONER)), "region": REGIONER})
    sektorer = pd.DataFrame({"sektor_id": range(len(SEKTORER)), "sektor": SEKTORER})
    stoerrelser = pd.DataFrame(STOERRELSER, columns=["stoerrelse", "min_ansatte", "max_ansatte"])
    stoerrelser.insert(0, "stoerrelse_id", range(len(stoerrelser)))
    dimensioner = pd.DataFrame(DIMENSIONER, columns=["dimension", "navn", "beskrivelse"])
    dimensioner.insert(0, "dimension_id", range(1, len(dimensioner) + 1))

    grupper, fordelinger = [], []
    gruppe_id = 0

    for aar in AAR:
        for _, b in brancher.iterrows():
            for _, s in stoerrelser.iterrows():
                for _, sek in sektorer.iterrows():
                    for _, r in regioner.iterrows():
                        # Region krydses kun med "alle brancher". Ellers bliver
                        # cellerne for små til at måtte offentliggøres.
                        if r.region != "Alle" and (b.branche != "Alle"
                                                   or s.stoerrelse != "Alle"
                                                   or sek.sektor != "Alle"):
                            continue
                        # Størrelse og sektor krydses kun for en konkret branche
                        if b.branche == "Alle" and (s.stoerrelse != "Alle" or sek.sektor != "Alle"):
                            continue

                        detaljeret = s.stoerrelse != "Alle" and sek.sektor != "Alle"
                        if detaljeret and rng.random() < 0.22:
                            continue      # undertrykt: for få arbejdssteder

                        gruppe_id += 1
                        antal = int(rng.integers(14, 90) if detaljeret else rng.integers(90, 2600))
                        grupper.append([gruppe_id, int(b.branche_id), int(s.stoerrelse_id),
                                        int(sek.sektor_id), int(r.region_id), aar, antal])

                        for _, d in dimensioner.iterrows():
                            nummer = list(dimensioner.dimension).index(d.dimension)
                            if b.branche == "Alle":
                                midte = float(np.mean([n[nummer] for n in NIVEAUER.values()]))
                            else:
                                midte = NIVEAUER[b.branche][nummer]
                            if sek.sektor != "Alle":
                                midte += SEKTORFORSKEL[sek.sektor][nummer]
                            if r.region != "Alle" and d.dimension == "indvandrere":
                                midte += REGIONSFORSKEL[r.region]
                            midte += AARSSKIFT[aar] + rng.normal(0, 0.015)

                            p = percentiler(max(midte, 0.01))
                            fordelinger.append([gruppe_id, int(d.dimension_id), *p])

    grupper = pd.DataFrame(grupper, columns=["gruppe_id", "branche_id", "stoerrelse_id",
                                             "sektor_id", "region_id", "aar",
                                             "antal_arbejdssteder"])
    fordelinger = pd.DataFrame(fordelinger, columns=["gruppe_id", "dimension_id",
                                                     "p10", "p25", "p50", "p75", "p90"])

    metadata = pd.DataFrame([
        ["navn", "Diversitetsbarometeret · referencetal"],
        ["syntetisk", "ja"],
        ["version", "1.0"],
        ["grundlag", "Formatet følger Mod diversitet på arbejdspladsen (Qvist & Larsen)"],
        ["enhed", "Arbejdssteder med mindst 50 stillinger"],
        ["aar", "2012 og 2022"],
        ["advarsel", "Tallene er opdigtede og siger intet om virkelige arbejdspladser"],
    ], columns=["noegle", "vaerdi"])

    return {"brancher": brancher, "regioner": regioner, "sektorer": sektorer,
            "stoerrelser": stoerrelser, "dimensioner": dimensioner,
            "grupper": grupper, "fordelinger": fordelinger, "metadata": metadata}


if __name__ == "__main__":
    tabeller = byg()
    for navn, tabel in tabeller.items():
        sti = UD / f"{navn}.csv"
        tabel.to_csv(sti, index=False)
        print(f"{sti.name:<20} {len(tabel):>6} rækker")
