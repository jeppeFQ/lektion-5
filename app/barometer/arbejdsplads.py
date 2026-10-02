from .fejl import UgyldigArbejdsplads

MINDSTE_STOERRELSE = 50
DIMENSIONER = ["kvinder", "seniorer", "indvandrere"]
STOERRELSESGRUPPER = [(50, 99, "50-99"), (100, 249, "100-249"),
                      (250, 499, "250-499"), (500, 1000000, "500+")]


class Arbejdsplads:
    def __init__(self, ansatte, antal, branche, sektor, region):
        self.ansatte = ansatte
        self.antal = antal
        self.branche = branche
        self.sektor = sektor
        self.region = region

        if ansatte < MINDSTE_STOERRELSE:
            raise UgyldigArbejdsplads(
                f"Barometeret dækker kun arbejdspladser med mindst {MINDSTE_STOERRELSE} ansatte.")
        for dimension in DIMENSIONER:
            if antal[dimension] < 0:
                raise UgyldigArbejdsplads(f"Antallet for {dimension} kan ikke være negativt.")
            if antal[dimension] > ansatte:
                raise UgyldigArbejdsplads(
                    f"Der kan ikke være flere i gruppen {dimension} end der er ansatte.")

    def andel(self, dimension):
        return self.antal[dimension] / self.ansatte

    @property
    def stoerrelsesgruppe(self):
        for fra, til, navn in STOERRELSESGRUPPER:
            if fra <= self.ansatte <= til:
                return navn
        return "Alle"

    def __str__(self):
        return (f"{self.ansatte} ansatte i {self.branche}, {self.sektor}, "
                f"{self.region} — {self.andel('kvinder'):.0%} kvinder")
