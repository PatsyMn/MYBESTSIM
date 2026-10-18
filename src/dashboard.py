import re
import unicodedata
from html import escape
from pathlib import Path

from stats import (DATA_GB, NETWORK, PRICE, PROVIDER, TOP_UP, VALIDITY,
                   cheapest_by_provider, esims_of_country, format_data)

# These "countries" are in fact zones that cover several countries.
ZONES = ["Europe", "Asie", "Monde", "Amérique du Nord"]

STYLE = """
body { font-family: system-ui, sans-serif; margin: 24px; background: #f5f6f8; color: #1c2430; }
h1 { margin-bottom: 4px; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
         gap: 12px; margin: 20px 0; }
.card { background: white; border-radius: 10px; padding: 16px; }
.label { color: #5d6877; font-size: 0.9rem; }
.value { font-size: 1.9rem; font-weight: bold; margin: 4px 0; }
.detail { color: #5d6877; font-size: 0.85rem; }
.chart { background: white; border-radius: 10px; padding: 16px; margin: 12px 0; }
.chart h2 { font-size: 1.1rem; margin: 0 0 12px; }
.row { display: grid; grid-template-columns: 110px 1fr 80px; align-items: center;
       gap: 10px; margin: 5px 0; font-size: 0.9rem; }
.track { background: #e6e9ef; border-radius: 4px; height: 16px; }
.fill { background: #2f6fed; height: 100%; border-radius: 4px; }
.num { text-align: right; white-space: nowrap; }
.grid2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 12px; }
.grid2 .chart { margin: 0; }
.table-wrap { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: 0.9rem; }
th, td { padding: 6px 10px; text-align: right; border-bottom: 1px solid #e6e9ef; }
th:first-child, td:first-child { text-align: left; }
th { color: #5d6877; font-weight: 600; }
.notes li { margin: 6px 0; color: #5d6877; }
a { color: #2f6fed; }
.back { display: inline-block; margin-bottom: 8px; }
td.left, th.left { text-align: left; }
"""


def fr(value, decimals=2):
    """Number in French format: 1 234,56 (thousands space, decimal comma)."""
    text = f"{value:,.{decimals}f}"
    return text.replace(",", " ").replace(".", ",")


def fmt_count(value):
    return fr(value, 0)


def fmt_price(value):
    return f"{fr(value)} €"


def fmt_per_gb(value):
    return f"{fr(value)} €/Go"


def country_slug(name):
    """'Afrique du Sud' -> 'afrique-du-sud' (no accent, no space: safe in a file name)."""
    text = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def kpi(label, value, detail=""):
    return f"""<div class="card">
  <div class="label">{label}</div>
  <div class="value">{value}</div>
  <div class="detail">{detail}</div>
</div>"""


def bar_chart(title, items, formatter=fmt_count):
    """Horizontal bars. items = [(label, value), ...], already sorted."""
    biggest = max(value for label, value in items)
    rows = ""
    for label, value in items:
        width = value / biggest * 100
        rows += f"""<div class="row">
  <span>{escape(str(label))}</span>
  <div class="track"><div class="fill" style="width:{width:.1f}%"></div></div>
  <span class="num">{escape(formatter(value))}</span>
</div>"""
    return f'<section class="chart"><h2>{escape(title)}</h2>{rows}</section>'


def country_table(countries):
    """One row per country. countries = stats["by_country"]."""
    rows = ""
    for c in countries:
        per_gb = "-" if c["best_price_per_gb"] is None else fr(c["best_price_per_gb"])
        unlimited = "aucune" if c["cheapest_unlimited"] is None else fr(c["cheapest_unlimited"])
        rows += f"""<tr>
  <td><a href="pays/{country_slug(c["country"])}.html">{escape(c["country"])}</a></td><td>{c["cards"]}</td><td>{c["providers"]}</td>
  <td>{fr(c["cheapest"])}</td><td>{per_gb}</td>
  <td>{c["unlimited_cards"]}</td><td>{unlimited}</td>
</tr>"""
    return f"""<section class="chart"><h2>Disponibilité par pays</h2>
<p class="detail">Cliquez sur un pays pour voir toutes ses cartes.</p>
<div class="table-wrap"><table>
<tr><th>Pays</th><th>Cartes</th><th>Fournisseurs</th><th>Moins cher (€)</th>
<th>Meilleur prix au Go (€)</th><th>Cartes illimitées</th><th>Illimité le moins cher (€)</th></tr>
{rows}
</table></div></section>"""


def build_html(stats):
    cheapest = stats["cheapest"]
    priciest = stats["priciest"]
    cards = "".join([
        kpi("Nombre total de cartes eSIM", fmt_count(stats["total"])),
        kpi("Cartes à plus de 100 €", stats["above_100"],
            f'{fr(stats["above_100"] / stats["total"] * 100, 1)} % du catalogue'),
        kpi("Fourchette de prix", f'{fr(cheapest[PRICE])} € - {fr(priciest[PRICE])} €',
            f'{cheapest[PROVIDER]} (le moins cher), {priciest[PROVIDER]} (le plus cher)'),
        kpi("Moyenne de data par carte", f'{fr(stats["avg_gb"])} Go',
            f'{fmt_count(stats["limited_count"])} forfaits limités, '
            f'{stats["unlimited_count"]} illimités exclus'),
        kpi("Prix moyen", fmt_price(stats["avg_price"])),
    ])
    providers_chart = bar_chart("Nombre de cartes par fournisseur", stats["by_provider"])
    price_chart = bar_chart("Prix moyen par fournisseur",
                            stats["avg_price_by_provider"], fmt_price)
    per_gb_chart = bar_chart("Prix par Go et par fournisseur (forfaits limités)",
                             stats["price_per_gb"], fmt_per_gb)
    countries = country_table(stats["by_country"])
    notes = f"""<section class="chart"><h2>Notes sur les données</h2><ul class="notes">
<li>La moyenne de data ignore les {stats["unlimited_count"]} forfaits illimités
(pas de valeur en Go). Le prix par Go les ignore aussi.</li>
<li>Le prix par Go favorise les gros forfaits : il sert à comparer les fournisseurs et
les pays, pas à choisir une carte. La durée du séjour du voyageur n'est pas dans les
données.</li>
<li>Europe, Asie, Monde et Amérique du Nord sont des cartes qui couvrent plusieurs
pays. Elles ont leur propre ligne et ne sont pas ajoutées aux lignes des pays
(par exemple, les cartes « Europe » ne sont pas comptées dans l'Espagne), car les
données ne précisent pas quels pays chaque zone couvre.</li>
</ul></section>"""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tableau de bord eSIM</title>
<style>{STYLE}</style>
</head>
<body>
<h1>Tableau de bord eSIM</h1>
<div class="cards">{cards}</div>
{providers_chart}
<div class="grid2">{price_chart}{per_gb_chart}</div>
{countries}
{notes}
</body>
</html>"""


def country_cards_table(country_esims):
    """Every card of one country, cheapest first."""
    rows = ""
    for esim in country_esims:
        data_gb = esim[DATA_GB]
        per_gb = "-" if data_gb is None else fr(esim[PRICE] / data_gb)
        rows += f"""<tr>
  <td class="left">{escape(esim[PROVIDER])}</td><td>{escape(format_data(data_gb))}</td>
  <td>{esim[VALIDITY]} j</td><td>{fr(esim[PRICE])}</td><td>{per_gb}</td>
  <td>{escape(esim[NETWORK])}</td><td>{escape(esim[TOP_UP])}</td>
</tr>"""
    return f"""<section class="chart"><h2>Toutes les cartes</h2>
<div class="table-wrap"><table>
<tr><th class="left">Fournisseur</th><th>Data</th><th>Validité</th><th>Prix (€)</th>
<th>Prix au Go (€)</th><th>Réseau</th><th>Rechargeable</th></tr>
{rows}
</table></div></section>"""


def build_country_html(country, country_esims):
    """One page for one country. country = one entry of stats["by_country"]."""
    name = country["country"]
    per_gb = "-" if country["best_price_per_gb"] is None else fmt_per_gb(country["best_price_per_gb"])
    unlimited_detail = ("aucune carte illimitée" if country["cheapest_unlimited"] is None
                        else f'la moins chère : {fmt_price(country["cheapest_unlimited"])}')
    cards = "".join([
        kpi("Cartes disponibles", fmt_count(country["cards"]),
            f'chez {country["providers"]} fournisseurs'),
        kpi("Prix le plus bas", fmt_price(country["cheapest"])),
        kpi("Meilleur prix au Go", per_gb, "forfaits limités"),
        kpi("Cartes illimitées", fmt_count(country["unlimited_cards"]), unlimited_detail),
    ])
    chart = bar_chart("Prix le plus bas par fournisseur",
                      cheapest_by_provider(country_esims), fmt_price)
    note = ""
    if name in ZONES:
        note = """<section class="chart"><h2>À savoir</h2><ul class="notes">
<li>Cette zone regroupe plusieurs pays. Les données ne précisent pas lesquels : vérifiez
la liste des pays couverts auprès du fournisseur avant d'acheter.</li>
</ul></section>"""
    title = f"eSIM pour {name}"
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<style>{STYLE}</style>
</head>
<body>
<a class="back" href="../index.html">&larr; Retour au tableau de bord</a>
<h1>{escape(title)}</h1>
<div class="cards">{cards}</div>
{chart}
{country_cards_table(country_esims)}
{note}
</body>
</html>"""


def write_country_pages(esims, stats, folder):
    """Write one HTML page per country in folder (old pages are removed first)."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for old_page in folder.glob("*.html"):
        old_page.unlink()
    for country in stats["by_country"]:
        page = build_country_html(country, esims_of_country(esims, country["country"]))
        (folder / f"{country_slug(country['country'])}.html").write_text(page, encoding="utf-8")
    return len(stats["by_country"])


def write_dashboard(stats, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_html(stats), encoding="utf-8")
    return output_path


if __name__ == "__main__":
    from read_data import load_all
    from stats import compute_stats
    esims = load_all('dataset')
    stats = compute_stats(esims)
    path = write_dashboard(stats, 'docs/index.html')
    print("Tableau de bord écrit dans", path)
    count = write_country_pages(esims, stats, 'docs/pays')
    print(count, "pages par pays écrites dans docs/pays")
