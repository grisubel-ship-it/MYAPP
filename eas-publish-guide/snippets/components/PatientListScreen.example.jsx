// components/PatientListScreen.example.jsx
// -----------------------------------------------------------------------------
// Esempio d'uso completo: schermata lista pazienti con swipe-to-delete + Undo.
// Copiala nel tuo progetto e adatta i campi al tuo modello dati.
//
// Dipendenze:
//   npx expo install @react-native-async-storage/async-storage react-native-gesture-handler react-native-root-toast
//
// In App.js (root) avvolgi tutto in <RootSiblingParent> per far funzionare i toast:
//   import { RootSiblingParent } from 'react-native-root-siblings';
//   export default () => <RootSiblingParent><NavigationContainer>...</NavigationContainer></RootSiblingParent>;
// -----------------------------------------------------------------------------

import React, { useCallback, useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { Swipeable, GestureHandlerRootView } from 'react-native-gesture-handler';
import { Trash2 } from 'lucide-react-native';

import { readList, STORAGE_KEYS } from '../services/storageService';
import { useDeleteWithUndo } from '../hooks/useDeleteWithUndo';

const KEY = STORAGE_KEYS.PATIENTS;

export default function PatientListScreen({ navigation }) {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    const list = await readList(KEY);
    // Ordino per createdAt DESC
    list.sort((a, b) => (a.createdAt < b.createdAt ? 1 : -1));
    setPatients(list);
    setLoading(false);
  }, []);

  useEffect(() => {
    refresh();
    const unsubscribe = navigation?.addListener?.('focus', refresh);
    return unsubscribe;
  }, [navigation, refresh]);

  const { softDelete } = useDeleteWithUndo(KEY, refresh, {
    itemLabel: 'Paziente',
    confirm: true,
  });

  const renderRightActions = (item) => (
    <TouchableOpacity
      style={styles.deleteAction}
      onPress={() => softDelete(item)}
      accessibilityLabel={`Elimina ${item.name}`}
      testID={`delete-patient-${item.id}`}
    >
      <Trash2 color="#fff" size={22} />
      <Text style={styles.deleteText}>Elimina</Text>
    </TouchableOpacity>
  );

  const renderItem = ({ item }) => (
    <Swipeable
      renderRightActions={() => renderRightActions(item)}
      overshootRight={false}
    >
      <View style={styles.card} testID={`patient-card-${item.id}`}>
        <Text style={styles.name}>{item.name}</Text>
        <Text style={styles.subtitle}>
          {item.pathology ?? '—'} · {item.birthYear ?? '—'}
        </Text>
      </View>
    </Swipeable>
  );

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <FlatList
        data={patients}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={refresh} />
        }
        contentContainerStyle={{ padding: 12 }}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={styles.emptyText}>Nessun paziente inserito</Text>
          </View>
        }
      />
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 2 },
    elevation: 2,
  },
  name: { fontSize: 16, fontWeight: '600', color: '#0F172A' },
  subtitle: { fontSize: 13, color: '#64748B', marginTop: 4 },
  deleteAction: {
    backgroundColor: '#DC2626',
    justifyContent: 'center',
    alignItems: 'center',
    width: 96,
    marginBottom: 8,
    borderRadius: 12,
    marginLeft: 8,
  },
  deleteText: { color: '#fff', fontWeight: '600', marginTop: 4 },
  empty: { padding: 48, alignItems: 'center' },
  emptyText: { color: '#94A3B8' },
});
