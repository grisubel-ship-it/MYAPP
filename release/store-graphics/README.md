# 🎨 Grafica Google Play Store

Asset grafici pronti da caricare in **Play Console → Scheda del Play Store → Grafica**.

## 📱 Icona alta risoluzione (obbligatoria)

| File | Dimensione | Formato | Uso |
|---|---|---|---|
| **`icon-512.png`** | 512×512 | PNG opaco sRGB | ⭐ Da caricare nel campo **"Icona"** della scheda Play Store |
| `icon-512.jpg` | 512×512 | JPEG q92 | Fallback (raramente serve) |
| `icon-1024.png` | 1024×1024 | PNG opaco | Master per usi futuri (App Store iOS, siti web, ecc.) |
| `icon-192.png` | 192×192 | PNG opaco | Anteprima social / manifest web |

### Specifiche Play Store rispettate ✅
- 512×512 pixel esatti
- Formato **PNG a 32 bit**
- Sfondo **opaco** (Play Store non accetta trasparenza per l'icona hi-res)
- **≤ 1024 KB** (il file è 31 KB, ben sotto il limite)
- **sRGB** colorspace
- Nessun testo, nessun watermark, nessun contatto commerciale (norme Google)

### Design
- **Sfondo**: gradiente diagonale teal (da `#14A395` a `#0A5651`), passa per `#0F766E` che è il colore del brand
- **Icona**: cuore Lucide bianco pieno, ombreggiatura sottile drop-shadow
- **Composizione**: cuore centrato visivamente (leggero offset in alto per compensare il baricentro visivo)
- **Corner radius**: nessuno (Play Store applica automaticamente il masking Material)

## 🤖 Adaptive Icon Foreground (Android in-app)

| File | Uso |
|---|---|
| `adaptive-icon-fg.png` (512×512) | Foreground con sfondo trasparente, safe zone 66% |
| `adaptive-icon-fg-1024.png` (1024×1024) | Versione ad alta risoluzione |

L'app Android già include le versioni per tutte le densità Android (mdpi/hdpi/xhdpi/xxhdpi/xxxhdpi) nella cartella `frontend/android/app/src/main/res/mipmap-*`. La `v1.1.1` dell'AAB include già questa icona: quando l'utente installa l'app sul telefono vede lo stesso cuore che appare in-app.

## ⏳ Ancora da preparare

- **Feature graphic 1024×500** — l'immagine promo in cima alla scheda Play Store. Dimmi *"generami il feature graphic"* e la produco allo stesso livello di qualità.

## 🔄 Come rigenerare le icone

Se in futuro cambi la palette o il logo, modifica `../icon-source.svg` e rilancia:

```bash
cd /app/release
rsvg-convert -w 512 -h 512 icon-source.svg -o store-graphics/icon-512.png
rsvg-convert -w 1024 -h 1024 icon-source.svg -o store-graphics/icon-1024.png
# ...più le densità Android in frontend/android/app/src/main/res/mipmap-*
```

## 🔍 Anteprima

L'icona nell'app store apparirà così:

- Su lancher Android standard → viene ritagliata in cerchio → si vede il cuore centrato
- Su lancher a goccia → il cuore rimane visibile (safe zone 66% rispettata)
- Nella scheda Play Store → viene visualizzata in un rettangolo con corner radius uniforme

## 📦 Da caricare in Play Console

1. **Play Console** → tua app → **Scheda del Play Store** → **Grafica**
2. **Icona dell'app** → carica `icon-512.png`
3. Anteprima → Salva
