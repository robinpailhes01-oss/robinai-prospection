import csv
from fpdf import FPDF

CSV_PATH = "entreprises-seminaires-montpellier.csv"
PDF_PATH = "entreprises-seminaires-montpellier.pdf"

with open(CSV_PATH, newline="", encoding="utf-8") as f:
    rows = list(csv.reader(f))

headers, data = rows[0], rows[1:]

n_emails = sum(1 for r in data if r[2])
n_forms = sum(1 for r in data if not r[2] and r[3])

pdf = FPDF(orientation="L", unit="mm", format="A4")
pdf.set_auto_page_break(auto=True, margin=12)
pdf.add_page()

pdf.set_font("Helvetica", "B", 14)
pdf.cell(0, 9, "Prospection seminaires - Entreprises 1-10 salaries Montpellier & Herault",
         ln=1, align="C")
pdf.set_font("Helvetica", "", 9)
pdf.cell(0, 5,
         f"{len(data)} entreprises  -  {n_emails} emails verifies  -  {n_forms} formulaires de contact",
         ln=1, align="C")
pdf.ln(2)

display_headers = ["NOM", "SECTEUR", "EMAIL / FORMULAIRE", "ADRESSE", "VILLE", "TELEPHONE"]
col_widths = [42, 32, 70, 65, 35, 26]
line_height = 4.2

def draw_row(values, fill=False, bold=False, header_row=False):
    pdf.set_font("Helvetica", "B" if bold else "", 7.5 if not header_row else 8)
    if header_row:
        pdf.set_fill_color(20, 50, 100)
        pdf.set_text_color(255, 255, 255)
    elif fill:
        pdf.set_fill_color(238, 242, 248)
        pdf.set_text_color(0, 0, 0)
    else:
        pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(0, 0, 0)

    x_start = pdf.get_x()
    y_start = pdf.get_y()

    cell_lines = []
    for value, width in zip(values, col_widths):
        text = (value or "").encode("latin-1", "replace").decode("latin-1")
        lines = pdf.multi_cell(width, line_height, text, border=0, align="L",
                               dry_run=True, output="LINES")
        cell_lines.append(lines)

    row_height = line_height * max(len(l) for l in cell_lines)

    pdf.set_xy(x_start, y_start)
    for value, width, lines in zip(values, col_widths, cell_lines):
        x = pdf.get_x()
        y = pdf.get_y()
        cell_text = "\n".join(lines)
        pdf.multi_cell(width, line_height, cell_text,
                       border=1, align="L", fill=True, max_line_height=line_height)
        pdf.set_xy(x + width, y)
    pdf.set_xy(x_start, y_start + row_height)

draw_row(display_headers, header_row=True)

for i, row in enumerate(data):
    nom, secteur, email, formulaire, adresse, cp, ville, tel, site = row
    contact = email if email else (formulaire if formulaire else "")
    if not email and formulaire:
        contact = "[FORM] " + formulaire
    ville_full = f"{cp} {ville}".strip()
    draw_row([nom, secteur, contact, adresse, ville_full, tel], fill=(i % 2 == 1))

pdf.ln(4)
pdf.set_font("Helvetica", "I", 7)
pdf.set_text_color(80, 80, 80)
pdf.multi_cell(0, 3.5,
    "Sources : sites officiels, mentions legales, Pages Jaunes, Societe.com, Pappers, Annuaire des entreprises (data.gouv.fr). "
    "Cible TPE/PME independantes locales (chaines exclues). Effectifs non systematiquement disponibles - verifier sur Pappers "
    "avant prospection si critere strict <=10 salaries. RGPD : interet legitime B2B, opt-out clair obligatoire.")

pdf.output(PDF_PATH)
print(f"PDF genere: {PDF_PATH} ({len(data)} contacts)")
