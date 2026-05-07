import csv
from fpdf import FPDF

CSV_PATH = "cuisinistes-montpellier.csv"
PDF_PATH = "cuisinistes-montpellier.pdf"

with open(CSV_PATH, newline="", encoding="utf-8") as f:
    rows = list(csv.reader(f))

headers, data = rows[0], rows[1:]

pdf = FPDF(orientation="L", unit="mm", format="A4")
pdf.set_auto_page_break(auto=True, margin=12)
pdf.add_page()

pdf.set_font("Helvetica", "B", 16)
pdf.cell(0, 10, "Cuisinistes indépendants - Montpellier et alentours", ln=1, align="C")
pdf.set_font("Helvetica", "", 10)
pdf.cell(0, 6, f"Liste de prospection - {len(data)} contacts", ln=1, align="C")
pdf.ln(4)

col_widths = [50, 55, 55, 18, 30, 28, 42]
line_height = 5

def draw_row(values, fill=False, bold=False):
    pdf.set_font("Helvetica", "B" if bold else "", 8)
    if fill:
        pdf.set_fill_color(30, 60, 110)
        pdf.set_text_color(255, 255, 255)
    else:
        pdf.set_fill_color(245, 245, 245)
        pdf.set_text_color(0, 0, 0)

    x_start = pdf.get_x()
    y_start = pdf.get_y()

    cell_lines = []
    for value, width in zip(values, col_widths):
        text = (value or "").encode("latin-1", "replace").decode("latin-1")
        lines = pdf.multi_cell(width, line_height, text, border=0, align="L",
                               split_only=True)
        cell_lines.append(lines)

    row_height = line_height * max(len(l) for l in cell_lines)

    pdf.set_xy(x_start, y_start)
    for value, width, lines in zip(values, col_widths, cell_lines):
        x = pdf.get_x()
        y = pdf.get_y()
        pdf.multi_cell(width, line_height, "\n".join(lines),
                       border=1, align="L", fill=True, max_line_height=line_height)
        pdf.set_xy(x + width, y)
        if row_height > line_height * len(lines):
            pass
    pdf.set_xy(x_start, y_start + row_height)

draw_row([h.replace("_", " ").upper() for h in headers], fill=True, bold=True)

for i, row in enumerate(data):
    draw_row(row, fill=(i % 2 == 1))

pdf.ln(6)
pdf.set_font("Helvetica", "I", 8)
pdf.set_text_color(80, 80, 80)
pdf.multi_cell(0, 4,
    "Note: tous les contacts sont des magasins independants (pas de chaines type Schmidt, Mobalpa, Ixina, "
    "Cuisinella, Cuisine Plus, Arthur Bonnet). Verifiez chaque email avant tout envoi en masse "
    "et respectez le RGPD (interet legitime B2B, opt-out clair).")

pdf.output(PDF_PATH)
print(f"PDF genere: {PDF_PATH}")
