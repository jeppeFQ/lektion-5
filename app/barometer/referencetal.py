"""
Referencetallene.

Det her er den kode, I skrev i notebooken (trin 8 til 12) samlet i én fil og
pakket ind i en klasse. I skal ikke rette i den i dag. Læs den igennem: I kan
genkende hver eneste linje.

Næste gang bygger vi videre på den.
"""

from pathlib import Path

import pandas as pd

DIMENSIONER = {1: "kvinder", 2: "seniorer", 3: "indvandrere"}
TABELLER = ["fordelinger", "grupper", "brancher", "stoerrelser", "sektorer", "regioner"]


def find_datamappe():
    """Find mappen data/ — både når appen køres lokalt og når den er bygget."""
    her = Path(__file__).resolve()
    for kandidat in [her.parent.parent / "data", her.parents[2] / "data"]:
        if (kandidat / "grupper.csv").exists():
            return kandidat
    raise FileNotFoundError("Kunne ikke finde mappen data/ med referencetallene.")


class Referencetal:
    """Alle referencetallene, sat sammen fra tabellerne i data/."""

    def __init__(self, mappe=None):
        mappe = Path(mappe) if mappe else find_datamappe()
        t = {navn: pd.read_csv(mappe / f"{navn}.csv") for navn in TABELLER}

        self.tal = (t["fordelinger"]
                    .merge(t["grupper"], on="gruppe_id")
                    .merge(t["brancher"], on="branche_id")
                    .merge(t["stoerrelser"], on="stoerrelse_id")
                    .merge(t["sektorer"], on="sektor_id")
                    .merge(t["regioner"], on="region_id"))

    def muligheder(self, kolonne):
        """De værdier, en kolonne kan have, uden 'Alle'."""
        return sorted(v for v in self.tal[kolonne].unique() if v != "Alle")

    def find(self, arbejdsplads, dimension_id, aar=2022):
        """Den mest præcise sammenligningsgruppe, der findes.

        Mangler den, prøves en bredere. Returnerer rækken og en beskrivelse af,
        hvilken gruppe det blev.
        """
        branche = arbejdsplads.branche
        stoerrelse = arbejdsplads.stoerrelsesgruppe
        sektor = arbejdsplads.sektor

        forsoeg = [
            (stoerrelse, sektor, f"{branche}, {stoerrelse} ansatte, {sektor.lower()} sektor"),
            (stoerrelse, "Alle", f"{branche}, {stoerrelse} ansatte, begge sektorer"),
            ("Alle", "Alle", f"{branche}, alle størrelser"),
        ]

        for stoerrelse_nu, sektor_nu, beskrivelse in forsoeg:
            raekker = self.tal[(self.tal["aar"] == aar)
                               & (self.tal["dimension_id"] == dimension_id)
                               & (self.tal["branche"] == branche)
                               & (self.tal["stoerrelse"] == stoerrelse_nu)
                               & (self.tal["sektor"] == sektor_nu)]
            if len(raekker) > 0:
                return raekker.iloc[0], beskrivelse

        return None, "ingen sammenlignelig gruppe fundet"


def placering(andel, raekke):
    """Hvor ligger andelen i fordelingen: lav, middel eller høj?"""
    if andel < raekke["p25"]:
        return "i den laveste fjerdedel"
    elif andel < raekke["p75"]:
        return "i midten"
    else:
        return "i den højeste fjerdedel"


def vurder(arbejdsplads, referencetal):
    """Alle tre dimensioner. Returnerer en liste af sætninger."""
    linjer = []
    for dimension_id, navn in DIMENSIONER.items():
        egen_andel = arbejdsplads.andel(navn)
        raekke, beskrivelse = referencetal.find(arbejdsplads, dimension_id)
        if raekke is None:
            linjer.append(f"{navn}: der findes ingen sammenlignelig gruppe.")
            continue
        linjer.append(f"Andelen af {navn} er {egen_andel:.0%}. "
                      f"Det er {placering(egen_andel, raekke)} blandt {beskrivelse}.")
    return linjer
