# Aggiungere la cancellazione dati alla tua app "Cronici"

Snippet pronti per implementare **eliminazione singola**, **eliminazione multipla**, **Undo** e **reset totale** in un'app Expo/React Native.

## 📦 Cosa contiene questa cartella

```
snippets/
├── services/
│   └── storageService.js         → CRUD generico su AsyncStorage
├── hooks/
│   └── useDeleteWithUndo.js      → Hook: cancella + Snackbar Undo 5s
└── components/
    ├── PatientListScreen.example.jsx   → Lista con swipe-to-delete
    └── DataSettingsScreen.example.jsx  → Impostazioni → gestione dati + reset totale
```

## 🔧 Installazione dipendenze (una tantum)

Nel tuo progetto Expo esegui:

```bash
npx expo install @react-native-async-storage/async-storage react-native-gesture-handler react-native-root-toast react-native-root-siblings
npm install lucide-react-native
```

## 🧩 Integrazione in 4 step

### 1. Copia i file
Sposta la cartella `snippets/` dentro `src/` del tuo progetto (rinominala pure `lib/` se preferisci).

### 2. Avvolgi l'app in RootSiblingParent
In `App.js` (o `_layout.tsx` se usi expo-router):

```jsx
import { RootSiblingParent } from 'react-native-root-siblings';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <RootSiblingParent>
        {/* ...il tuo NavigationContainer o Stack... */}
      </RootSiblingParent>
    </GestureHandlerRootView>
  );
}
```

### 3. Usa il service dove crei i dati
Nel form di creazione paziente:

```jsx
import { addItem, STORAGE_KEYS } from './lib/services/storageService';

const salva = async () => {
  await addItem(STORAGE_KEYS.PATIENTS, {
    name: nome,
    pathology: patologia,
    birthYear: anno,
  });
  navigation.goBack();
};
```

### 4. Usa l'hook nella lista
Nella schermata lista pazienti:

```jsx
import { useDeleteWithUndo } from './lib/hooks/useDeleteWithUndo';
import { STORAGE_KEYS } from './lib/services/storageService';

const { softDelete } = useDeleteWithUndo(STORAGE_KEYS.PATIENTS, refresh, {
  itemLabel: 'Paziente',
  confirm: true,     // Alert di conferma prima (raccomandato per dati sanitari)
});

// ...
<Button title="Elimina" onPress={() => softDelete(paziente)} />
```

## 🎯 Pattern implementati

| Pattern | Componente | Uso tipico |
|---|---|---|
| **Swipe-to-delete** | `PatientListScreen.example.jsx` | Cancellazione rapida singola dalla lista |
| **Alert nativo + Undo 5s** | `useDeleteWithUndo.js` | Conferma sicura + possibilità di annullare |
| **Bulk clear per collezione** | `DataSettingsScreen.example.jsx` | "Svuota tutte le misurazioni" |
| **Reset totale (doppia conferma)** | `DataSettingsScreen.example.jsx` | GDPR / diritto all'oblio |

## ⚕️ Note per un'app medicale

- **Conferma obbligatoria** per dati clinici → `confirm: true` sempre
- **Registra le eliminazioni** (audit log) se serve conformità → aggiungi `logDeletion(item)` in `deleteItem`
- **Il reset totale** in `DataSettingsScreen` copre il "diritto all'oblio" GDPR — mettilo in *Impostazioni → Privacy*
- Nella **Play Store data safety** dichiara "Data deletion available in-app"

## 🔒 Se usi un backend remoto

Sostituisci le chiamate a `AsyncStorage` con fetch/axios verso i tuoi endpoint DELETE. Il pattern hook `useDeleteWithUndo` rimane identico: cambia solo l'implementazione di `deleteItem`/`addItem`.

Esempio:

```js
export async function deleteItem(key, id) {
  const res = await fetch(`${API}/api/${key}/${id}`, { method: 'DELETE' });
  return res.ok ? await res.json() : null;
}
```

## ✅ TestID inclusi

Ogni elemento interattivo ha già `testID` per il testing E2E:
- `delete-patient-${id}` – bottone swipe elimina
- `patient-card-${id}` – card lista
- `clear-patients-btn`, `clear-measurements-btn`, `clear-therapies-btn`
- `wipe-all-data-btn`

## 📱 Screenshot mentale del risultato

1. Utente **scorre a sinistra** una card paziente → appare bottone rosso "Elimina"
2. Tap → **Alert nativo**: "Elimina Paziente?" (Annulla / Elimina)
3. Conferma → paziente sparisce → **toast in basso**: "Paziente eliminato" con tap per annullare
4. Se non tocca il toast entro 5s → cancellazione permanente
