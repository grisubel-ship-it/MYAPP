// components/DataSettingsScreen.example.jsx
// -----------------------------------------------------------------------------
// Schermata "Impostazioni → Gestione dati" con:
//  - contatore elementi per collezione
//  - pulsante "Svuota [collezione]" (con conferma)
//  - pulsante "Reset totale" a doppia conferma (per GDPR / diritto all'oblio)
// -----------------------------------------------------------------------------

import React, { useCallback, useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ScrollView,
} from 'react-native';
import Toast from 'react-native-root-toast';

import {
  STORAGE_KEYS,
  clearCollection,
  getStorageStats,
  wipeAllAppData,
} from '../services/storageService';

const COLLECTIONS = [
  { name: 'PATIENTS', label: 'Pazienti', key: STORAGE_KEYS.PATIENTS },
  { name: 'MEASUREMENTS', label: 'Misurazioni', key: STORAGE_KEYS.MEASUREMENTS },
  { name: 'THERAPIES', label: 'Terapie', key: STORAGE_KEYS.THERAPIES },
];

export default function DataSettingsScreen() {
  const [stats, setStats] = useState({});

  const refresh = useCallback(async () => {
    setStats(await getStorageStats());
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleClearOne = (col) => {
    Alert.alert(
      `Svuota ${col.label}?`,
      `Verranno eliminati ${stats[col.name] ?? 0} elementi. L'operazione è irreversibile.`,
      [
        { text: 'Annulla', style: 'cancel' },
        {
          text: 'Svuota',
          style: 'destructive',
          onPress: async () => {
            await clearCollection(col.key);
            await refresh();
            Toast.show(`${col.label} svuotati`, { duration: 1500 });
          },
        },
      ]
    );
  };

  const handleWipeAll = () => {
    // Prima conferma
    Alert.alert(
      'Reset totale dell\'app',
      'Verranno eliminati TUTTI i dati salvati (pazienti, misurazioni, terapie, impostazioni). L\'operazione non è annullabile.',
      [
        { text: 'Annulla', style: 'cancel' },
        {
          text: 'Continua',
          style: 'destructive',
          onPress: () => {
            // Seconda conferma
            Alert.alert(
              'Sei davvero sicuro?',
              'Digita "Elimina" nella tua testa e conferma. Non potrai recuperare i dati.',
              [
                { text: 'No, annulla', style: 'cancel' },
                {
                  text: 'Sì, elimina tutto',
                  style: 'destructive',
                  onPress: async () => {
                    const count = await wipeAllAppData();
                    await refresh();
                    Toast.show(`Cancellate ${count} collezioni`, {
                      duration: 2000,
                    });
                  },
                },
              ]
            );
          },
        },
      ]
    );
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Gestione dati</Text>
      <Text style={styles.hint}>
        Puoi cancellare singole collezioni o eseguire un reset totale dell'app.
      </Text>

      {COLLECTIONS.map((col) => (
        <View key={col.name} style={styles.row}>
          <View style={{ flex: 1 }}>
            <Text style={styles.rowLabel}>{col.label}</Text>
            <Text style={styles.rowCount}>
              {stats[col.name] ?? 0} elementi salvati
            </Text>
          </View>
          <TouchableOpacity
            style={styles.clearBtn}
            onPress={() => handleClearOne(col)}
            disabled={(stats[col.name] ?? 0) === 0}
            testID={`clear-${col.name.toLowerCase()}-btn`}
          >
            <Text style={styles.clearBtnText}>Svuota</Text>
          </TouchableOpacity>
        </View>
      ))}

      <TouchableOpacity
        style={styles.dangerBtn}
        onPress={handleWipeAll}
        testID="wipe-all-data-btn"
      >
        <Text style={styles.dangerBtnText}>Reset totale dell'app</Text>
      </TouchableOpacity>

      <Text style={styles.legal}>
        I dati sono salvati solo sul tuo dispositivo. Eliminandoli non sarà
        possibile recuperarli.
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20, backgroundColor: '#F8FAFC', flexGrow: 1 },
  title: { fontSize: 24, fontWeight: '700', color: '#0F172A', marginBottom: 4 },
  hint: { color: '#64748B', marginBottom: 24 },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 14,
    borderRadius: 12,
    marginBottom: 10,
  },
  rowLabel: { fontSize: 16, fontWeight: '600', color: '#0F172A' },
  rowCount: { fontSize: 12, color: '#64748B', marginTop: 2 },
  clearBtn: {
    borderColor: '#DC2626',
    borderWidth: 1,
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 999,
  },
  clearBtnText: { color: '#DC2626', fontWeight: '600' },
  dangerBtn: {
    marginTop: 24,
    backgroundColor: '#DC2626',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  dangerBtnText: { color: '#fff', fontWeight: '700', fontSize: 16 },
  legal: {
    marginTop: 16,
    color: '#94A3B8',
    fontSize: 12,
    textAlign: 'center',
    lineHeight: 18,
  },
});
