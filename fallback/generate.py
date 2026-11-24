import json
from html import escape
from pathlib import Path
from string import Template

base = Path(__file__).parent
template = Template((base / "template.html").read_text(encoding="utf-8"))
output = base / "dist"
output.mkdir(exist_ok=True)

for fichier in sorted((base / "pages").glob("*.json")):
    page = json.loads(fichier.read_text(encoding="utf-8"))
    valeurs = {cle: escape(str(valeur)) for cle, valeur in page.items()}
    html = template.substitute(valeurs)
    (output / f"{fichier.stem}.html").write_text(html, encoding="utf-8")
