import csv
import io
from io import BytesIO

def render_pdf(name: str, period: str, dept: str, rows: list[dict[str, str]]) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle(name)
    
    # En-tête
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, 800, name)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, 780, f"Période : {period}")
    pdf.drawString(40, 765, f"Département : {dept}")
    
    # Contenu du tableau simple
    y = 730
    pdf.setFont("Helvetica-Bold", 9)
    # Ligne d'en-tête (on prend les clés du premier dict)
    if rows:
        headers = list(rows[0].keys())
        x_positions = [40, 200, 320, 440, 520]
        
        for i, header in enumerate(headers[:5]):  # Afficher les 5 premières colonnes pour l'exemple
            pdf.drawString(x_positions[i] if i < len(x_positions) else 500, y, str(header))
        
        pdf.line(40, y - 5, 550, y - 5)
        y -= 20
        
        pdf.setFont("Helvetica", 8)
        for row in rows[:50]:  # Limite pour l'exemple
            for i, col_key in enumerate(headers[:5]):
                pdf.drawString(x_positions[i] if i < len(x_positions) else 500, y, str(row[col_key]))
            y -= 15
            if y < 80:
                pdf.showPage()
                pdf.setFont("Helvetica", 8)
                y = 800
    
    pdf.save()
    return buffer.getvalue()


def render_csv(rows: list[dict[str, str]]) -> bytes:
    if not rows:
        return b""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue().encode("utf-8")


def render_xlsx(rows: list[dict[str, str]]) -> bytes:
    import pandas as pd
    buffer = BytesIO()
    dataframe = pd.DataFrame(rows or [])
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="Rapport")
    return buffer.getvalue()
