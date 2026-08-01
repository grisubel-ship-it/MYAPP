// hooks/useDeleteWithUndo.js
// -----------------------------------------------------------------------------
// Hook riutilizzabile: cancella un elemento + mostra Snackbar "Annulla" per 5s.
// Se l'utente preme Annulla entro 5s, ripristina l'elemento.
// Se non preme nulla, la cancellazione diventa permanente.
//
// Dipendenza raccomandata (Snackbar/Toast Expo-friendly):
//   npx expo install react-native-root-toast
// oppure usa il tuo Snackbar preferito (react-native-paper, sonner, ecc.)
// -----------------------------------------------------------------------------

import { useCallback, useRef } from 'react';
import { Alert } from 'react-native';
import Toast from 'react-native-root-toast';
import { deleteItem, addItem } from '../services/storageService';

const UNDO_WINDOW_MS = 5000;

/**
 * @param {string} storageKey - chiave AsyncStorage della collezione
 * @param {Function} refresh - funzione che ricarica la lista nello state del componente
 * @param {Object} options
 * @param {string} options.itemLabel - es. "paziente", "misurazione"
 * @param {boolean} options.confirm  - se true, mostra Alert di conferma prima (default true)
 */
export function useDeleteWithUndo(storageKey, refresh, options = {}) {
  const { itemLabel = 'elemento', confirm = true } = options;
  const undoTimersRef = useRef(new Map());

  /**
   * Cancella con toast Undo.
   */
  const softDelete = useCallback(
    async (item) => {
      const doDelete = async () => {
        const removed = await deleteItem(storageKey, item.id);
        if (!removed) return;
        refresh();

        // Mostra il toast Undo
        const toast = Toast.show(`${itemLabel} eliminato`, {
          duration: UNDO_WINDOW_MS,
          position: Toast.positions.BOTTOM,
          shadow: true,
          animation: true,
          hideOnPress: true,
          containerStyle: { paddingHorizontal: 16, borderRadius: 12 },
          onPress: async () => {
            // UNDO: ripristina l'elemento
            const timer = undoTimersRef.current.get(item.id);
            if (timer) clearTimeout(timer);
            undoTimersRef.current.delete(item.id);
            await addItem(storageKey, removed);
            refresh();
            Toast.hide(toast);
            Toast.show(`${itemLabel} ripristinato`, {
              duration: 1500,
              position: Toast.positions.BOTTOM,
            });
          },
        });

        // Al termine del countdown, la cancellazione diventa permanente
        const timerId = setTimeout(() => {
          undoTimersRef.current.delete(item.id);
        }, UNDO_WINDOW_MS);
        undoTimersRef.current.set(item.id, timerId);
      };

      if (!confirm) {
        await doDelete();
        return;
      }

      // Conferma nativa (raccomandata per dati sanitari)
      Alert.alert(
        `Elimina ${itemLabel}?`,
        'Puoi annullare l\'operazione entro 5 secondi.',
        [
          { text: 'Annulla', style: 'cancel' },
          {
            text: 'Elimina',
            style: 'destructive',
            onPress: doDelete,
          },
        ],
        { cancelable: true }
      );
    },
    [storageKey, refresh, itemLabel, confirm]
  );

  return { softDelete };
}
