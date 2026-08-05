# 📸 Screenshot Google Play Store — Caregiver Sync v1.1.0

5 screenshot **1080×1920 nativi** (deviceScaleFactor 2×), pronti da caricare nella scheda Play Store nella sezione **"Grafica → Screenshot smartphone"**.

## Ordine consigliato di caricamento

L'ordine dei primi 3 è **critico**: sono quelli visibili senza dover scorrere sulla Play Store card.

| # | File PNG | File JPG (più leggero) | Cosa mostra | Messaggio commerciale |
|---|---|---|---|---|
| 1 | `01-home.png` | `01-home.jpg` | Home con saluto contestuale + quick stats + lista assistiti con avatar | 👋 "Un'app pensata per i caregiver reali" |
| 2 | `02-detail.png` | `02-detail.jpg` | Scheda paziente con card **Consegna con IA** + storico + grafico | ⭐ Feature principale: coordinamento tra turni |
| 3 | `03-handover.png` | `03-handover.jpg` | Dialog **consegna generata dall'IA** con testo strutturato | 🤖 L'IA in azione (motivo n.1 di download) |
| 4 | `04-trend.png` | `04-trend.jpg` | Grafico andamento parametri vitali (Glicemia) | 📈 Trend clinici a colpo d'occhio |
| 5 | `05-menu.png` | `05-menu.jpg` | Menu ⋮ con "Modifica voce" e "Elimina voce" | ✏️ Correggi errori in un tap |

## Didascalie suggerite (max 80 caratteri, se Play Console lo permette)

1. `Un'app pensata per chi si prende cura di un anziano o cronico`
2. `Diario clinico condiviso tra caregiver, tutto ordinato in un posto`
3. `L'IA genera automaticamente la nota di passaggio consegne per il turno`
4. `Vedi come pressione, glicemia e altri parametri cambiano nel tempo`
5. `Correggi rapidamente ogni voce dal menu contestuale`

## Specifiche tecniche

- **Risoluzione**: 1080 × 1920 pixel (9:16, standard Google Play phone)
- **Formato**: PNG (senza compressione) + JPG q92 (versione leggera)
- **Colorspace**: sRGB
- **Dimensione media**: ~180 KB (JPG) / ~180 KB (PNG)
- **Contenuti**: interfaccia italiana, dati demo realistici (Maria Rossi 1942, Diabete tipo 2 · Ipertensione), 10 giorni di parametri vitali, 3 consegne IA storiche

## Cosa NON è in questa cartella (da preparare a parte)

Per completare la scheda Play Store servono anche:

| Asset | Dimensione | Note |
|---|---|---|
| **Icona alta risoluzione** | 512×512 PNG | Il logo cuore bianco su fondo teal `#0F766E` |
| **Feature graphic** | 1024×500 PNG/JPG | Immagine promozionale in cima alla scheda |
| **Video promozionale** | YouTube URL, 30-120s | Opzionale ma raddoppia il conversion rate |

Se vuoi te li genero anche questi — dimmi il tipo di stile (screenshot mockup con testo, illustrazione, foto di caregiver, ecc.).

## Come utilizzarli

1. Apri **Google Play Console** → la tua app → **Scheda del Play Store**
2. Scendi fino a **Grafica** → sezione **Screenshot smartphone**
3. Trascina i 5 PNG in ordine (`01-` → `05-`), lasciando le didascalie personalizzabili
4. Anteprima → Salva

Le versioni JPG sono un fallback: usale solo se Play Console rigetta i PNG per dimensione (mai capitato con questi file).
