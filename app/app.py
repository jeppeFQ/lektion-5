"""
Diversitetsbarometeret — appen, version 2.

Kør den fra roden af repositoriet:
    python -m shiny run --reload app/app.py

Tre faner: Barometer, Opslag og Om. Appen regner stadig ikke selv noget ud —
den spørger jeres egne funktioner i barometer/ og viser svaret.
"""

from pathlib import Path

from shiny import App, reactive, render, req, ui

from barometer import Arbejdsplads, Referencetal, UgyldigArbejdsplads, vurder
from barometer.figur import tegn, tegn_opslag
from barometer.opslag import brancher
from barometer.tekst import beskeder

MAPPE = Path(__file__).parent
referencetal = Referencetal()
om_tekst = (MAPPE / "om.md").read_text(encoding="utf-8")

SYNTETISK = ui.div(
    "Tallene er syntetiske. Barometeret siger endnu intet om virkelige arbejdspladser.",
    class_="alert alert-secondary",
)

# ---------------------------------------------------------------- fanerne

barometer_side = ui.layout_sidebar(
    ui.sidebar(
        ui.input_select("branche", "Branche", referencetal.muligheder("branche")),
        ui.input_radio_buttons("sektor", "Sektor", ["Offentlig", "Privat"], inline=True),
        ui.input_select("region", "Region", referencetal.muligheder("region")),
        ui.input_numeric("ansatte", "Antal ansatte", 120, min=0),
        ui.input_numeric("kvinder", "Heraf kvinder", 84, min=0),
        ui.input_numeric("seniorer", "Heraf 55 år eller derover", 26, min=0),
        ui.input_numeric("indvandrere", "Heraf med indvandrerbaggrund", 9, min=0),
        width=320,
    ),
    SYNTETISK,
    ui.output_ui("advarsler"),
    ui.output_plot("figur", height="260px"),
    ui.output_ui("svar"),
)

opslag_side = ui.layout_sidebar(
    ui.sidebar(
        ui.input_radio_buttons(
            "dimension", "Hvad vil du se?",
            {"kvinder": "Kvinder", "seniorer": "Seniorer (55+)",
             "indvandrere": "Indvandrerbaggrund"},
        ),
        ui.p("Medianen i hver branche, for arbejdspladser med mindst 50 ansatte.",
             class_="text-muted small"),
        width=280,
    ),
    SYNTETISK,
    ui.output_plot("opslag_figur", height="380px"),
    ui.output_data_frame("opslag_tabel"),
)

app_ui = ui.page_navbar(
    ui.nav_panel("Barometer", barometer_side),
    ui.nav_panel("Opslag", opslag_side),
    ui.nav_panel("Om", ui.div(ui.markdown(om_tekst), class_="container", style="max-width: 760px;")),
    title="Diversitetsbarometeret",
)


# ---------------------------------------------------------------- serveren

def server(input, output, session):

    @reactive.calc
    def arbejdsplads():
        return Arbejdsplads(
            ansatte=int(input.ansatte() or 0),
            antal={"kvinder": int(input.kvinder() or 0),
                   "seniorer": int(input.seniorer() or 0),
                   "indvandrere": int(input.indvandrere() or 0)},
            branche=input.branche(),
            sektor=input.sektor(),
            region=input.region(),
        )

    @render.ui
    def advarsler():
        try:
            plads = arbejdsplads()
        except UgyldigArbejdsplads as fejl:
            return ui.div(str(fejl), class_="alert alert-warning")
        return ui.div(*[ui.div(b, class_="alert alert-info") for b in beskeder(plads, referencetal)])

    @render.plot
    def figur():
        try:
            return tegn(arbejdsplads(), referencetal)
        except UgyldigArbejdsplads:
            req(False)

    @render.ui
    def svar():
        try:
            linjer = vurder(arbejdsplads(), referencetal)
        except UgyldigArbejdsplads:
            return ui.div()
        return ui.div(*[ui.p(linje) for linje in linjer])

    @render.plot
    def opslag_figur():
        return tegn_opslag(brancher(referencetal, input.dimension()))

    @render.data_frame
    def opslag_tabel():
        return brancher(referencetal, input.dimension())


app = App(app_ui, server)
