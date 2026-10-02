# Appen

Barometeret som en rigtig brugerflade, bygget med **Shiny for Python**.

Appen regner ikke selv noget ud. Den læser felterne, laver en `Arbejdsplads` og beder `vurder()` om svaret. Al logikken ligger i `barometer/`.

## Trin for trin

**1: Installér det, der skal bruges.** Én gang pr. maskine:

```bash
pip install shiny pandas
```

Virker `pip` ikke, så prøv `pip3` eller `python3 -m pip`.

**2: Stå i roden af repositoriet.** Ikke inde i `app/`:

```bash
cd sti/til/diversitetsbarometer
```

Tjek med `ls`: I skal kunne se mapperne `app`, `data` og `tests`.

**3: Start appen:**

```bash
shiny run --reload app/app.py
```

`--reload` betyder, at appen starter forfra af sig selv, hver gang I gemmer en fil.

**4: Åbn den i browseren:** <http://127.0.0.1:8000>

Adressen står også i terminalen. I VS Code kan I som regel klikke på den.

**5: Prøv den.** Skru på felterne i venstre side. Svaret opdaterer sig selv.

**6: Stop appen** med `Ctrl + C` i terminalen.

## Forventede fefl

| Det, I ser | Det betyder |
|---|---|
| `command not found: shiny` | Pakken er ikke installeret. |
| `ModuleNotFoundError: No module named 'barometer'` | I står det forkerte sted. Kør kommandoen fra roden af repositoriet |
| `FileNotFoundError: ... data/` | Mappen `data/` mangler. Hent den med *Sync fork* og `git pull` |
| `AttributeError: ... has no attribute 'branche'` | `Arbejdsplads` er ikke bygget færdig. Kør testene |
| `Address already in use` | Appen kører allerede i et andet vindue. Luk det, eller brug `--port 8001` |
| Siden er tom og hvid | Kig i terminalen. Fejlen står der |

## Hvad der sker inde i appen

```python
from barometer import Arbejdsplads, Referencetal, UgyldigArbejdsplads, vurder

referencetal = Referencetal()          # læser de syv tabeller i data/ én gang

@render.ui
def svar():
    return ui.div(*[ui.p(linje) for linje in vurder(arbejdsplads(), referencetal)])
```

Det er hele koblingen mellem brugerfladen og jeres egen kode. Skal barometeret svare
noget andet, retter I i `barometer/` og ikke i `app.py`.
