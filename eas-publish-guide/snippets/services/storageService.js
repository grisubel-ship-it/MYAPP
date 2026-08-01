// services/storageService.js
// -----------------------------------------------------------------------------
// Servizio CRUD generico basato su AsyncStorage.
// Adatto ad app Expo per gestire liste di entità (pazienti, misurazioni, terapie...).
//
// Installazione (una volta sola):
//   npx expo install @react-native-async-storage/async-storage
// -----------------------------------------------------------------------------

import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * Chiavi usate nell'app. Centralizzale qui per evitare typo.
 */
export const STORAGE_KEYS = {
  PATIENTS: '@cronici/patients',
  MEASUREMENTS: '@cronici/measurements',
  THERAPIES: '@cronici/therapies',
  SETTINGS: '@cronici/settings',
};

/**
 * Legge una lista di elementi.
 * @param {string} key
 * @returns {Promise<Array>}
 */
export async function readList(key) {
  const raw = await AsyncStorage.getItem(key);
  if (!raw) return [];
  try {
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

/**
 * Salva l'intera lista (sovrascrive).
 */
export async function writeList(key, list) {
  await AsyncStorage.setItem(key, JSON.stringify(list));
}

/**
 * Aggiunge un elemento generando un id univoco se manca.
 */
export async function addItem(key, item) {
  const list = await readList(key);
  const withId = {
    id: item.id ?? `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    createdAt: item.createdAt ?? new Date().toISOString(),
    ...item,
  };
  list.push(withId);
  await writeList(key, list);
  return withId;
}

/**
 * Aggiorna un elemento tramite id.
 */
export async function updateItem(key, id, patch) {
  const list = await readList(key);
  const idx = list.findIndex((x) => x.id === id);
  if (idx === -1) return null;
  list[idx] = { ...list[idx], ...patch, updatedAt: new Date().toISOString() };
  await writeList(key, list);
  return list[idx];
}

// -----------------------------------------------------------------------------
// FUNZIONI DI CANCELLAZIONE
// -----------------------------------------------------------------------------

/**
 * Elimina un singolo elemento per id.
 * @returns l'elemento eliminato (utile per l'UNDO) oppure null se non trovato.
 */
export async function deleteItem(key, id) {
  const list = await readList(key);
  const idx = list.findIndex((x) => x.id === id);
  if (idx === -1) return null;
  const [removed] = list.splice(idx, 1);
  await writeList(key, list);
  return removed;
}

/**
 * Elimina più elementi passando un array di id.
 */
export async function deleteMany(key, ids) {
  const set = new Set(ids);
  const list = await readList(key);
  const kept = list.filter((x) => !set.has(x.id));
  const removed = list.filter((x) => set.has(x.id));
  await writeList(key, kept);
  return removed;
}

/**
 * Elimina in base a un predicato (es. cancella tutte le misurazioni di un mese).
 */
export async function deleteWhere(key, predicate) {
  const list = await readList(key);
  const kept = list.filter((x) => !predicate(x));
  const removed = list.filter((x) => predicate(x));
  await writeList(key, kept);
  return removed;
}

/**
 * Svuota una singola collezione.
 */
export async function clearCollection(key) {
  await AsyncStorage.removeItem(key);
}

/**
 * WIPE totale: elimina TUTTI i dati dell'app.
 * ATTENZIONE: rimuove ogni chiave prefissata '@cronici/'.
 */
export async function wipeAllAppData() {
  const allKeys = await AsyncStorage.getAllKeys();
  const appKeys = allKeys.filter((k) => k.startsWith('@cronici/'));
  if (appKeys.length > 0) {
    await AsyncStorage.multiRemove(appKeys);
  }
  return appKeys.length;
}

/**
 * Restituisce le statistiche di storage (utile per una schermata Impostazioni → Dati).
 */
export async function getStorageStats() {
  const stats = {};
  for (const [name, key] of Object.entries(STORAGE_KEYS)) {
    const list = await readList(key);
    stats[name] = Array.isArray(list) ? list.length : 0;
  }
  return stats;
}
