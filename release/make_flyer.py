"""Volantino A4 Caregiver Sync — layout richiesto:
- Logo banner intero in alto (ben visibile)
- Vantaggi in bullet points
- QR code sotto/laterale"""
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas

OUT_DIR = "/app/release"
PAGE_W, PAGE_H = A4

GREEN_DARK = HexColor("#2F6B3F")
GREEN_MID = HexColor("#4A8F5B")
STONE_900 = HexColor("#1C1917")
STONE_700 = HexColor("#3F3F46")
STONE_500 = HexColor("#71717A")
AMBER = HexColor("#F59E0B")


def build_logo_banner(path, w=1600, h=640):
    """Ricrea la banner-logo mostrata dall'utente: verde gradient + cuore bianco + 'Caregiver Sync'."""
    img = Image.new("RGB", (w, h), "#4A8F5B")
    draw = ImageDraw.Draw(img)
    # Gradient diagonale verde chiaro -> verde scuro
    for y in range(h):
        for x in range(0, w, 4):  # step 4 per velocità
            t_y = y / h
            t_x = x / w
            r = int(55 + (85 - 55) * (1 - t_x) + (30 - 55) * t_y * 0.3)
            g = int(130 + (160 - 130) * (1 - t_y) * 0.5 + (90 - 130) * t_y * 0.3)
            b = int(70 + (90 - 70) * (1 - t_x) + (50 - 70) * t_y * 0.3)
            draw.rectangle([x, y, x + 4, y + 1], fill=(r, g, b))

    # Cuore bianco centrato (parte alta)
    cx = w // 2
    cy = int(h * 0.38)
    r_heart = int(h * 0.22)
    # Due cerchi
    draw.ellipse([cx - int(r_heart*1.5), cy - r_heart, cx - int(r_heart*0.15), cy + r_heart], fill="white")
    draw.ellipse([cx + int(r_heart*0.15), cy - r_heart, cx + int(r_heart*1.5), cy + r_heart], fill="white")
    # Triangolo di base
    draw.polygon([
        (cx - int(r_heart*1.5), cy + int(r_heart*0.1)),
        (cx + int(r_heart*1.5), cy + int(r_heart*0.1)),
        (cx, cy + int(r_heart*1.8)),
    ], fill="white")

    # Testo "Caregiver Sync"
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    font_path = None
    for p in font_paths:
        if os.path.exists(p):
            font_path = p
            break
    try:
        font_size = int(h * 0.19)
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
    text = "Caregiver Sync"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (w - tw) // 2
    ty = int(h * 0.65)
    draw.text((tx, ty), text, fill="white", font=font)

    # Piccola sparkle in basso a destra
    sx, sy = int(w * 0.94), int(h * 0.85)
    size = 8
    draw.polygon([(sx, sy-size*2), (sx+size, sy), (sx, sy+size*2), (sx-size, sy)], fill="white")

    img.save(path, "PNG", optimize=True)


def make_qr_png(url, path, box_size=20, border=2):
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H,
                       box_size=box_size, border=border)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1C1917", back_color="white").convert("RGB")
    img.save(path, "PNG")


def draw_flyer(path, qr_url, title_badge, cta_text, steps):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle("Caregiver Sync — Volantino promozionale")

    # === 1) Logo banner GRANDE in alto (tutta la larghezza) — usa il logo reale dell'utente ===
    logo_src = "/app/release/logo-caregiver-sync.png"
    # Il logo ha aspect ratio 2000:814 (~2.457:1)
    banner_h = int(PAGE_W / (2000 / 814))  # mantieni ratio reale
    c.drawImage(logo_src, 0, PAGE_H - banner_h, width=PAGE_W, height=banner_h, mask='auto')

    # Badge arancione subito sotto il banner
    badge_y = PAGE_H - banner_h - 22
    c.setFillColor(AMBER)
    bw = 260
    c.roundRect((PAGE_W - bw) / 2, badge_y, bw, 28, 14, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(PAGE_W / 2, badge_y + 9, title_badge)

    # === 2) Titolo e sottotitolo ===
    y = PAGE_H - banner_h - 70
    c.setFillColor(STONE_900)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(PAGE_W / 2, y, "Il diario di cura per tutta la famiglia")
    y -= 24
    c.setFillColor(STONE_500)
    c.setFont("Helvetica", 12)
    c.drawCentredString(PAGE_W / 2, y, "Note condivise, consegne tra turni e un aiuto IA — gratis, senza registrazione.")

    # === 3) Vantaggi (bullet) a sinistra + QR a destra ===
    content_top = y - 50
    left_x = 50
    col_text_w = 320

    bullets = [
        ("Diario sempre aggiornato",
         "Annota osservazioni, farmaci, parametri in pochi tap. Tutti i caregiver vedono lo stesso diario."),
        ("Consegna automatica con IA",
         "Un riassunto chiaro per chi prende il turno dopo di te. Generato in italiano in 5 secondi."),
        ("Privacy GDPR — i dati sono tuoi",
         "Nessuna registrazione obbligatoria. Puoi cancellare tutto in qualsiasi momento dalla schermata Impostazioni."),
        ("100% in italiano, pensata per casa",
         "Interfaccia semplice adatta a familiari, badanti, OSS e assistenti. Nessun gergo medico."),
    ]

    yy = content_top
    for name, desc in bullets:
        # Pallino verde
        c.setFillColor(GREEN_MID)
        c.circle(left_x + 8, yy + 4, 7, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(left_x + 8, yy + 1, "✓")
        # Titolo bullet
        c.setFillColor(STONE_900)
        c.setFont("Helvetica-Bold", 12.5)
        c.drawString(left_x + 26, yy + 2, name)
        # Descrizione (wrap su 2 righe)
        c.setFillColor(STONE_700)
        c.setFont("Helvetica", 10.5)
        words = desc.split()
        line = ""
        line_y = yy - 14
        max_w = col_text_w - 26
        for w_ in words:
            test = (line + " " + w_).strip()
            if c.stringWidth(test, "Helvetica", 10.5) <= max_w:
                line = test
            else:
                c.drawString(left_x + 26, line_y, line)
                line_y -= 12
                line = w_
        if line:
            c.drawString(left_x + 26, line_y, line)
        yy = line_y - 22

    # QR code a destra
    qr_tmp = "/tmp/_qr.png"
    make_qr_png(qr_url, qr_tmp)
    qr_size = 180
    qr_x = PAGE_W - 50 - qr_size
    qr_y = content_top - qr_size + 10
    # Cornice morbida grigia
    c.setFillColor(HexColor("#F4F4F5"))
    c.roundRect(qr_x - 15, qr_y - 65, qr_size + 30, qr_size + 95, 14, fill=1, stroke=0)
    c.setFillColor(STONE_900)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(qr_x + qr_size/2, qr_y + qr_size + 12, "Scansiona per")
    c.drawCentredString(qr_x + qr_size/2, qr_y + qr_size - 2, "scaricare l'app")
    c.drawImage(qr_tmp, qr_x, qr_y, width=qr_size, height=qr_size, mask='auto')
    c.setFillColor(STONE_500)
    c.setFont("Helvetica", 9)
    c.drawCentredString(qr_x + qr_size/2, qr_y - 20, "con la fotocamera dello")
    c.drawCentredString(qr_x + qr_size/2, qr_y - 32, "smartphone")
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(qr_x + qr_size/2, qr_y - 50, cta_text)

    # === 4) Footer ===
    c.setFillColor(STONE_500)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(PAGE_W / 2, 52, "Caregiver Sync • App di annotazione per familiari")
    c.setFont("Helvetica", 8)
    c.drawCentredString(PAGE_W / 2, 38, "Non è un dispositivo medico • Non sostituisce il parere di un professionista sanitario")

    c.showPage()
    c.save()
    print(f"OK: {path}")


# Volantino Play Store
PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=com.caregiversync.app"
draw_flyer(
    f"{OUT_DIR}/volantino-caregiver-sync-playstore.pdf",
    qr_url=PLAY_STORE_URL,
    title_badge="DISPONIBILE SU GOOGLE PLAY",
    cta_text="o cerca 'Caregiver Sync' su Google Play",
    steps=[],
)

# Volantino Beta
BETA_URL = "https://play.google.com/apps/testing/com.caregiversync.app"
draw_flyer(
    f"{OUT_DIR}/volantino-caregiver-sync-beta.pdf",
    qr_url=BETA_URL,
    title_badge="ACCESSO BETA TESTER",
    cta_text="Il tuo email deve essere nella lista tester",
    steps=[],
)
print("Volantini aggiornati!")
