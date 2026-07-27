# Assets necessari (metti qui i file PNG)

Tutti i file **devono essere PNG** ed avere le seguenti dimensioni esatte:

| File                     | Dimensione | Sfondo         | Descrizione                                              |
|--------------------------|------------|----------------|----------------------------------------------------------|
| `icon.png`               | 1024×1024  | Opaco          | Icona master (iOS + fallback Android)                    |
| `adaptive-icon.png`      | 1024×1024  | Trasparente    | Foreground Android adaptive (safe zone 66% centrale)     |
| `splash.png`             | 1284×2778  | Colore brand   | Splash screen (o 1242×2436 minimo). Logo centrato        |
| `notification-icon.png`  | 96×96      | Trasparente    | Icona notifiche (solo bianco su alpha, richiesto Android)|
| `favicon.png`            | 48×48      | Trasparente    | Favicon per la web build                                 |

## Regole importanti

### Adaptive Icon Android
Android ritaglia l'icona in cerchio/quadrato/goccia a seconda del lancher.
Il tuo logo deve stare nel **66% centrale** dell'immagine 1024×1024.
Aggiungi almeno **170px di padding** su ogni lato attorno al logo.

### Notification Icon
Deve essere **solo bianco con trasparenza** (silhouette). Android colora
automaticamente l'icona con il colore configurato (`notification.color`).
Se metti un'icona colorata, apparirà come un quadrato bianco pieno.

### Splash Screen
Con la nuova API `expo-splash-screen` basta un solo file (logo centrato)
con `resizeMode: contain`. Lo sfondo è impostato tramite `backgroundColor`
in `app.json`.

## Strumenti consigliati per generarli

1. **Figma** — Template ufficiale Expo:
   https://www.figma.com/community/file/1155362909441341285

2. **Expo Asset Generator** (gratis, online):
   https://expo-assets-generator.vercel.app

3. **Da riga di comando** (con ImageMagick installato):
```bash
# Da una singola sorgente 1024x1024 (icon-source.png)
convert icon-source.png -resize 1024x1024 icon.png
convert icon-source.png -resize 1024x1024 -background none -gravity center -extent 1024x1024 adaptive-icon.png
convert icon-source.png -resize 96x96 -background none notification-icon.png
convert icon-source.png -resize 48x48 favicon.png

# Splash: logo centrato su canvas 1284x2778
convert -size 1284x2778 xc:"#0F766E" \
  \( icon-source.png -resize 400x400 \) -gravity center -composite \
  splash.png
```
