import io
from pathlib import Path

import qrcode
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

PAGE_W, PAGE_H = A4
LOGO = Path(__file__).parent / "assets" / "logo-caregiver-sync.png"
PLAY_URL = "https://play.google.com/store/apps/details?id=com.caregiversync.app"
GREEN = HexColor("#4A8F5B")
GREEN_DARK = HexColor("#2F6B3F")
STONE_900 = HexColor("#1C1917")
STONE_700 = HexColor("#3F3F46")
STONE_500 = HexColor("#71717A")
AMBER = HexColor("#F59E0B")

BULLETS = [
    ("Diario sempre aggiornato", "Osservazioni, farmaci e parametri in pochi tap, condivisi tra tutti i caregiver."),
    ("Consegna automatica con IA", "Un riassunto chiaro per chi prende il turno dopo di te, in pochi secondi."),
    ("Privacy GDPR", "Nessuna registrazione obbligatoria. Puoi cancellare tutto quando vuoi."),
    ("Semplice e in italiano", "Pensata per familiari, badanti e OSS. Nessun gergo medico."),
]


def _wrap(c, text, font, size, max_w):
    lines, line = [], ""
    for w in text.split():
        test = f"{line} {w}".strip()
        if c.stringWidth(test, font, size) <= max_w:
            line = test
        else:
            lines.append(line)
            line = w
    return lines + ([line] if line else [])


def _qr():
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=20, border=2)
    qr.add_data(PLAY_URL)
    qr.make(fit=True)
    buf = io.BytesIO()
    qr.make_image(fill_color="#1C1917", back_color="white").convert("RGB").save(buf, "PNG")
    buf.seek(0)
    return ImageReader(buf)


def build_coop_flyer(cooperative_name: str, code: str, duration_months: int) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"Caregiver Sync - {cooperative_name}")

    banner_h = PAGE_W / (2000 / 814)
    c.drawImage(ImageReader(str(LOGO)), 0, PAGE_H - banner_h, width=PAGE_W, height=banner_h, mask="auto")

    badge = f"OFFERTO DA {cooperative_name.upper()}"
    c.setFont("Helvetica-Bold", 11)
    bw = min(PAGE_W - 80, c.stringWidth(badge, "Helvetica-Bold", 11) + 40)
    by = PAGE_H - banner_h - 22
    c.setFillColor(AMBER)
    c.roundRect((PAGE_W - bw) / 2, by, bw, 28, 14, fill=1, stroke=0)
    c.setFillColor(white)
    c.drawCentredString(PAGE_W / 2, by + 9, badge)

    y = by - 42
    c.setFillColor(STONE_900)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(PAGE_W / 2, y, "Il diario di cura per tutta la famiglia")
    y -= 22
    c.setFillColor(STONE_500)
    c.setFont("Helvetica", 12)
    mesi = "mese" if duration_months == 1 else "mesi"
    c.drawCentredString(PAGE_W / 2, y, f"Premium gratuito per {duration_months} {mesi} grazie a {cooperative_name}")

    # Box codice
    y -= 110
    box_w, box_h = PAGE_W - 100, 88
    c.setFillColor(HexColor("#ECF5EE"))
    c.setStrokeColor(GREEN)
    c.setDash(6, 4)
    c.setLineWidth(2)
    c.roundRect(50, y, box_w, box_h, 14, fill=1, stroke=1)
    c.setDash()
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(PAGE_W / 2, y + box_h - 22, "IL TUO CODICE CONVENZIONE")
    c.setFillColor(STONE_900)
    c.setFont("Courier-Bold", 30)
    c.drawCentredString(PAGE_W / 2, y + 26, code)

    # Bullet a sinistra
    top = y - 40
    yy = top
    for name, desc in BULLETS:
        c.setFillColor(GREEN)
        c.circle(58, yy + 4, 6, fill=1, stroke=0)
        c.setFillColor(STONE_900)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(74, yy, name)
        c.setFillColor(STONE_700)
        c.setFont("Helvetica", 10)
        for line in _wrap(c, desc, "Helvetica", 10, 250):
            yy -= 13
            c.drawString(74, yy, line)
        yy -= 24

    # QR a destra
    qs = 150
    qx, qy = PAGE_W - 50 - qs, top - qs + 4
    c.setFillColor(HexColor("#F4F4F5"))
    c.roundRect(qx - 12, qy - 20, qs + 24, qs + 52, 12, fill=1, stroke=0)
    c.setFillColor(STONE_900)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(qx + qs / 2, qy + qs + 12, "Scansiona e scarica l'app")
    c.drawImage(_qr(), qx, qy, width=qs, height=qs, mask="auto")
    c.setFillColor(STONE_500)
    c.setFont("Helvetica", 8.5)
    c.drawCentredString(qx + qs / 2, qy - 12, "o cerca 'Caregiver Sync' su Google Play")

    # Passi
    sy = min(yy, qy - 30) - 10
    c.setFillColor(STONE_900)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, sy, "Come attivare Premium")
    steps = [
        "Scarica Caregiver Sync da Google Play",
        "Tocca Premium in alto a destra",
        f"Inserisci il codice {code} e tocca Attiva",
    ]
    c.setFont("Helvetica", 11)
    for i, s in enumerate(steps, 1):
        sy -= 20
        c.setFillColor(GREEN)
        c.circle(58, sy + 4, 8, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(58, sy + 1, str(i))
        c.setFillColor(STONE_700)
        c.setFont("Helvetica", 11)
        c.drawString(74, sy, s)

    c.setFillColor(STONE_500)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(PAGE_W / 2, 52, "Caregiver Sync - App di annotazione per familiari e caregiver")
    c.setFont("Helvetica", 8)
    c.drawCentredString(PAGE_W / 2, 38, "Non è un dispositivo medico - Non sostituisce il parere di un professionista sanitario")
    c.showPage()
    c.save()
    return buf.getvalue()
