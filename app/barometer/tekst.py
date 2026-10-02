"""
Beskeder til brugeren.

Barometeret skal sige det, når en sammenligning måtte gøres bredere, fordi den
præcise gruppe ikke findes i tallene. Ellers tror brugeren, at hun er sammenlignet
med noget, hun ikke er.
"""

from .referencetal import DIMENSIONER


def bredere_besked(beskrivelse):
    """Returnér en besked, hvis gruppen blev gjort bredere. Ellers None."""
    if "begge sektorer" in beskrivelse or "alle størrelser" in beskrivelse:
        return ("Der var ikke tal nok til den præcise sammenligning. "
                f"I stedet sammenlignes med: {beskrivelse}.")
    return None


def beskeder(arbejdsplads, referencetal):
    """Alle beskeder for én arbejdsplads — hver besked kun én gang."""
    ud = []
    for dimension_id in DIMENSIONER:
        _, beskrivelse = referencetal.find(arbejdsplads, dimension_id)
        besked = bredere_besked(beskrivelse)
        if besked is not None and besked not in ud:
            ud.append(besked)
    return ud
