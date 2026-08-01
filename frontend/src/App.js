import { useEffect, useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Link, useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import { Toaster, toast } from "sonner";
import {
  Users,
  Plus,
  Trash2,
  ChevronLeft,
  Settings as SettingsIcon,
  Activity,
  Pill,
  AlertCircle,
  StickyNote,
  Undo2,
  Heart,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// ---------- Utility: Undo toast ----------
const UNDO_MS = 5000;

async function deleteWithUndo({ label, doDelete, doRestore }) {
  const removed = await doDelete();
  toast(`${label} eliminato`, {
    duration: UNDO_MS,
    action: {
      label: "Annulla",
      onClick: async () => {
        await doRestore(removed);
        toast.success(`${label} ripristinato`);
      },
    },
  });
  return removed;
}

// ---------- Confirm Dialog ----------
function ConfirmDialog({ trigger, title, description, confirmText = "Elimina", onConfirm, destructive = true, testId }) {
  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>{trigger}</AlertDialogTrigger>
      <AlertDialogContent data-testid={`${testId}-dialog`}>
        <AlertDialogHeader>
          <AlertDialogTitle>{title}</AlertDialogTitle>
          <AlertDialogDescription>{description}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel data-testid={`${testId}-cancel`}>Annulla</AlertDialogCancel>
          <AlertDialogAction
            data-testid={`${testId}-confirm`}
            onClick={onConfirm}
            className={destructive ? "bg-red-600 hover:bg-red-700 text-white" : ""}
          >
            {confirmText}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

// ---------- Layout ----------
function Shell({ children }) {
  return (
    <div className="min-h-screen bg-stone-50">
      <header className="border-b border-stone-200 bg-white sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-5 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 group" data-testid="home-link">
            <div className="w-9 h-9 rounded-xl bg-teal-600 grid place-items-center">
              <Heart size={18} className="text-white" fill="white" />
            </div>
            <div>
              <div className="font-semibold text-stone-900 leading-tight">Caregiver Sync</div>
              <div className="text-xs text-stone-500 leading-tight">Anziani & Cronici</div>
            </div>
          </Link>
          <Link to="/impostazioni" data-testid="settings-link">
            <Button variant="ghost" size="icon" aria-label="Impostazioni">
              <SettingsIcon size={20} />
            </Button>
          </Link>
        </div>
      </header>
      <main className="max-w-4xl mx-auto px-5 py-6">{children}</main>
      <Toaster position="bottom-center" richColors closeButton />
    </div>
  );
}

// ---------- Patients List ----------
function PatientsList() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const load = async () => {
    setLoading(true);
    try {
      const { data } = await axios.get(`${API}/patients`);
      setPatients(data);
    } catch (e) {
      toast.error("Impossibile caricare l'elenco pazienti");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleDelete = async (patient) => {
    await deleteWithUndo({
      label: `Assistito ${patient.name}`,
      doDelete: async () => {
        const { data } = await axios.delete(`${API}/patients/${patient.id}`);
        setPatients((prev) => prev.filter((p) => p.id !== patient.id));
        return data;
      },
      doRestore: async (removed) => {
        await axios.post(`${API}/patients/restore`, {
          patient: removed.patient,
          entries: removed.entries,
        });
        load();
      },
    });
  };

  return (
    <div className="space-y-5">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-serif text-stone-900" data-testid="patients-title">Assistiti</h1>
          <p className="text-stone-500 text-sm mt-1">
            {patients.length === 0
              ? "Nessun assistito registrato"
              : `${patients.length} ${patients.length === 1 ? "assistito" : "assistiti"} in cura`}
          </p>
        </div>
        <Button
          onClick={() => navigate("/nuovo")}
          className="bg-teal-600 hover:bg-teal-700"
          data-testid="add-patient-btn"
        >
          <Plus size={16} className="mr-1" /> Nuovo
        </Button>
      </div>

      {loading && <div className="text-stone-500 text-sm py-8 text-center">Caricamento…</div>}

      {!loading && patients.length === 0 && (
        <Card className="border-dashed">
          <CardContent className="py-12 text-center space-y-3">
            <Users className="mx-auto text-stone-300" size={48} />
            <p className="text-stone-600">Registra il primo assistito per iniziare</p>
            <Button onClick={() => navigate("/nuovo")} className="bg-teal-600 hover:bg-teal-700" data-testid="empty-add-btn">
              <Plus size={16} className="mr-1" /> Aggiungi assistito
            </Button>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-3">
        {patients.map((p) => (
          <Card
            key={p.id}
            className="hover:border-teal-300 transition-colors"
            data-testid={`patient-card-${p.id}`}
          >
            <CardContent className="p-4 flex items-center justify-between gap-3">
              <button
                className="flex-1 text-left"
                onClick={() => navigate(`/paziente/${p.id}`)}
                data-testid={`open-patient-${p.id}`}
              >
                <div className="font-medium text-stone-900">{p.name}</div>
                <div className="text-sm text-stone-500 mt-0.5 flex gap-2 items-center flex-wrap">
                  {p.pathology && <Badge variant="secondary" className="font-normal">{p.pathology}</Badge>}
                  {p.birth_year && <span className="text-xs">nato nel {p.birth_year}</span>}
                </div>
              </button>
              <ConfirmDialog
                testId={`delete-patient-${p.id}`}
                title={`Eliminare ${p.name}?`}
                description="Verranno eliminati anche tutti i dati clinici associati (parametri, farmaci, sintomi, note). Avrai 5 secondi per annullare."
                confirmText="Elimina assistito"
                onConfirm={() => handleDelete(p)}
                trigger={
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    aria-label="Elimina"
                    data-testid={`delete-patient-${p.id}-btn`}
                  >
                    <Trash2 size={18} />
                  </Button>
                }
              />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

// ---------- New Patient ----------
function NewPatient() {
  const [form, setForm] = useState({ name: "", pathology: "", birth_year: "", notes: "" });
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    if (!form.name.trim()) {
      toast.error("Il nome è obbligatorio");
      return;
    }
    setSaving(true);
    try {
      const payload = { ...form, birth_year: form.birth_year ? parseInt(form.birth_year, 10) : null };
      await axios.post(`${API}/patients`, payload);
      toast.success("Assistito registrato");
      navigate("/");
    } catch {
      toast.error("Errore durante il salvataggio");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-5 max-w-lg">
      <Link to="/" className="text-teal-700 text-sm inline-flex items-center gap-1" data-testid="back-to-list">
        <ChevronLeft size={16} /> Torna all'elenco
      </Link>
      <h1 className="text-2xl font-serif text-stone-900">Nuovo assistito</h1>

      <form onSubmit={submit} className="space-y-4">
        <div>
          <Label htmlFor="name">Nome e cognome *</Label>
          <Input
            id="name"
            data-testid="patient-name-input"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            placeholder="Es. Maria Rossi"
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label htmlFor="pathology">Patologia principale</Label>
            <Input
              id="pathology"
              data-testid="patient-pathology-input"
              value={form.pathology}
              onChange={(e) => setForm({ ...form, pathology: e.target.value })}
              placeholder="Es. Diabete tipo 2"
            />
          </div>
          <div>
            <Label htmlFor="birth_year">Anno di nascita</Label>
            <Input
              id="birth_year"
              data-testid="patient-birth-input"
              type="number"
              value={form.birth_year}
              onChange={(e) => setForm({ ...form, birth_year: e.target.value })}
              placeholder="1945"
            />
          </div>
        </div>
        <div>
          <Label htmlFor="notes">Note</Label>
          <Textarea
            id="notes"
            data-testid="patient-notes-input"
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
            placeholder="Allergie, routine, note utili al passaggio di consegne…"
            rows={4}
          />
        </div>
        <div className="flex gap-2">
          <Button type="submit" disabled={saving} className="bg-teal-600 hover:bg-teal-700" data-testid="save-patient-btn">
            {saving ? "Salvataggio…" : "Salva assistito"}
          </Button>
          <Button type="button" variant="ghost" onClick={() => navigate("/")}>Annulla</Button>
        </div>
      </form>
    </div>
  );
}

// ---------- Patient Detail (diary) ----------
const KIND_META = {
  vital: { label: "Parametro", icon: Activity, color: "text-blue-600 bg-blue-50" },
  medication: { label: "Farmaco", icon: Pill, color: "text-purple-600 bg-purple-50" },
  symptom: { label: "Sintomo", icon: AlertCircle, color: "text-orange-600 bg-orange-50" },
  note: { label: "Nota", icon: StickyNote, color: "text-stone-600 bg-stone-100" },
};

function PatientDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [patient, setPatient] = useState(null);
  const [entries, setEntries] = useState([]);
  const [entryForm, setEntryForm] = useState({ kind: "vital", label: "", value: "", unit: "" });

  const load = async () => {
    try {
      const [pRes, eRes] = await Promise.all([
        axios.get(`${API}/patients/${id}`),
        axios.get(`${API}/entries?patient_id=${id}`),
      ]);
      setPatient(pRes.data);
      setEntries(eRes.data);
    } catch {
      toast.error("Assistito non trovato");
      navigate("/");
    }
  };

  useEffect(() => {
    load();
  }, [id]);

  const addEntry = async (e) => {
    e.preventDefault();
    if (!entryForm.label.trim()) {
      toast.error("Indica un'etichetta (es. 'Pressione', 'Metformina')");
      return;
    }
    try {
      await axios.post(`${API}/entries`, { ...entryForm, patient_id: id });
      setEntryForm({ kind: entryForm.kind, label: "", value: "", unit: "" });
      toast.success("Voce aggiunta al diario");
      load();
    } catch {
      toast.error("Errore nel salvataggio");
    }
  };

  const handleDeleteEntry = async (entry) => {
    await deleteWithUndo({
      label: `${KIND_META[entry.kind]?.label ?? "Voce"} "${entry.label}"`,
      doDelete: async () => {
        const { data } = await axios.delete(`${API}/entries/${entry.id}`);
        setEntries((prev) => prev.filter((x) => x.id !== entry.id));
        return data;
      },
      doRestore: async (removed) => {
        await axios.post(`${API}/entries/restore`, { entry: removed.entry });
        load();
      },
    });
  };

  const bulkDelete = async (kind) => {
    try {
      const { data } = await axios.post(`${API}/entries/bulk-delete`, {
        patient_id: id,
        kind,
      });
      toast.success(`${data.count} voci eliminate`);
      load();
    } catch {
      toast.error("Errore durante l'eliminazione");
    }
  };

  if (!patient) return <div className="text-stone-500">Caricamento…</div>;

  const counts = entries.reduce((acc, e) => {
    acc[e.kind] = (acc[e.kind] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      <Link to="/" className="text-teal-700 text-sm inline-flex items-center gap-1" data-testid="back-btn">
        <ChevronLeft size={16} /> Elenco assistiti
      </Link>

      <div className="flex items-start justify-between gap-3">
        <div>
          <h1 className="text-3xl font-serif text-stone-900" data-testid="patient-detail-name">{patient.name}</h1>
          <div className="mt-2 flex gap-2 flex-wrap">
            {patient.pathology && <Badge variant="secondary">{patient.pathology}</Badge>}
            {patient.birth_year && <Badge variant="outline">nato nel {patient.birth_year}</Badge>}
          </div>
          {patient.notes && (
            <p className="mt-3 text-stone-600 text-sm max-w-xl whitespace-pre-wrap">{patient.notes}</p>
          )}
        </div>
      </div>

      {/* Add entry form */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Aggiungi al diario clinico</CardTitle>
          <CardDescription>Parametri, farmaci, sintomi o note del turno</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={addEntry} className="grid gap-3 md:grid-cols-[140px_1fr_140px_100px_auto]">
            <Select value={entryForm.kind} onValueChange={(v) => setEntryForm({ ...entryForm, kind: v })}>
              <SelectTrigger data-testid="entry-kind-select"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="vital">Parametro</SelectItem>
                <SelectItem value="medication">Farmaco</SelectItem>
                <SelectItem value="symptom">Sintomo</SelectItem>
                <SelectItem value="note">Nota</SelectItem>
              </SelectContent>
            </Select>
            <Input
              placeholder={entryForm.kind === "medication" ? "Nome farmaco" : entryForm.kind === "vital" ? "Es. Pressione" : "Descrizione"}
              value={entryForm.label}
              onChange={(e) => setEntryForm({ ...entryForm, label: e.target.value })}
              data-testid="entry-label-input"
            />
            <Input
              placeholder="Valore"
              value={entryForm.value}
              onChange={(e) => setEntryForm({ ...entryForm, value: e.target.value })}
              data-testid="entry-value-input"
            />
            <Input
              placeholder="Unità"
              value={entryForm.unit}
              onChange={(e) => setEntryForm({ ...entryForm, unit: e.target.value })}
              data-testid="entry-unit-input"
            />
            <Button type="submit" className="bg-teal-600 hover:bg-teal-700" data-testid="add-entry-btn">
              <Plus size={16} />
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Bulk delete by kind */}
      {entries.length > 0 && (
        <div className="flex gap-2 flex-wrap items-center text-sm">
          <span className="text-stone-500">Cancella in massa:</span>
          {Object.entries(counts).map(([kind, count]) => (
            <ConfirmDialog
              key={kind}
              testId={`bulk-delete-${kind}`}
              title={`Cancellare tutti i ${KIND_META[kind]?.label.toLowerCase() ?? "voci"}?`}
              description={`Verranno eliminati ${count} voci di questo tipo per ${patient.name}. L'operazione non è annullabile.`}
              confirmText="Cancella"
              onConfirm={() => bulkDelete(kind)}
              trigger={
                <Button variant="outline" size="sm" data-testid={`bulk-delete-${kind}-btn`}>
                  <Trash2 size={14} className="mr-1" />
                  {KIND_META[kind]?.label ?? kind} ({count})
                </Button>
              }
            />
          ))}
        </div>
      )}

      {/* Entries list */}
      <div className="space-y-2">
        <h2 className="text-lg font-semibold text-stone-800">Diario clinico</h2>
        {entries.length === 0 && (
          <div className="text-stone-500 text-sm py-8 text-center bg-white rounded-lg border border-dashed">
            Nessuna voce registrata. Aggiungi la prima usando il form sopra.
          </div>
        )}
        {entries.map((e) => {
          const meta = KIND_META[e.kind] ?? KIND_META.note;
          const Icon = meta.icon;
          return (
            <div
              key={e.id}
              className="flex items-center gap-3 bg-white border border-stone-200 rounded-lg p-3"
              data-testid={`entry-${e.id}`}
            >
              <div className={`w-9 h-9 rounded-lg grid place-items-center shrink-0 ${meta.color}`}>
                <Icon size={16} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-medium text-stone-900 truncate">{e.label}</div>
                <div className="text-xs text-stone-500 flex gap-2">
                  <span>{new Date(e.created_at).toLocaleString("it-IT")}</span>
                  {(e.value || e.unit) && (
                    <span className="font-medium text-stone-700">
                      {e.value} {e.unit}
                    </span>
                  )}
                </div>
              </div>
              <ConfirmDialog
                testId={`delete-entry-${e.id}`}
                title="Eliminare questa voce?"
                description="Puoi annullare l'operazione entro 5 secondi dal toast."
                onConfirm={() => handleDeleteEntry(e)}
                trigger={
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-red-600 hover:bg-red-50"
                    aria-label="Elimina voce"
                    data-testid={`delete-entry-${e.id}-btn`}
                  >
                    <Trash2 size={16} />
                  </Button>
                }
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ---------- Settings / Data management ----------
function SettingsPage() {
  const [stats, setStats] = useState(null);

  const load = async () => {
    const { data } = await axios.get(`${API}/data/stats`);
    setStats(data);
  };

  useEffect(() => {
    load();
  }, []);

  const clearCollection = async (name, label) => {
    try {
      await axios.delete(`${API}/data/collection/${name}`);
      toast.success(`${label} svuotati`);
      load();
    } catch {
      toast.error("Errore durante l'eliminazione");
    }
  };

  const wipeAll = async () => {
    try {
      await axios.delete(`${API}/data/wipe`);
      toast.success("Tutti i dati sono stati eliminati");
      load();
    } catch {
      toast.error("Errore durante il reset");
    }
  };

  return (
    <div className="space-y-6">
      <Link to="/" className="text-teal-700 text-sm inline-flex items-center gap-1" data-testid="settings-back">
        <ChevronLeft size={16} /> Torna alla home
      </Link>
      <div>
        <h1 className="text-3xl font-serif text-stone-900">Gestione dati</h1>
        <p className="text-stone-500 text-sm mt-1">
          Elimina singole categorie o esegui un reset totale (diritto all'oblio GDPR).
        </p>
      </div>

      {stats && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Riepilogo</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            {[
              ["Assistiti", stats.patients],
              ["Parametri", stats.vitals],
              ["Farmaci", stats.medications],
              ["Sintomi", stats.symptoms],
              ["Note", stats.notes],
              ["Totale voci diario", stats.entries],
            ].map(([label, value]) => (
              <div key={label} className="rounded-lg border border-stone-200 p-3">
                <div className="text-2xl font-serif text-stone-900">{value}</div>
                <div className="text-xs text-stone-500">{label}</div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Cancellazione per categoria</CardTitle>
          <CardDescription>Le operazioni sono irreversibili.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between p-3 rounded-lg border border-stone-200">
            <div>
              <div className="font-medium">Diario clinico</div>
              <div className="text-xs text-stone-500">Parametri, farmaci, sintomi, note ({stats?.entries ?? 0})</div>
            </div>
            <ConfirmDialog
              testId="clear-entries"
              title="Svuotare tutto il diario clinico?"
              description={`Verranno eliminate ${stats?.entries ?? 0} voci di tutti gli assistiti. Gli assistiti verranno mantenuti.`}
              confirmText="Svuota diario"
              onConfirm={() => clearCollection("entries", "Diario clinico")}
              trigger={
                <Button variant="outline" className="text-red-600 border-red-200 hover:bg-red-50" data-testid="clear-entries-btn">
                  <Trash2 size={14} className="mr-1" /> Svuota
                </Button>
              }
            />
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg border border-stone-200">
            <div>
              <div className="font-medium">Tutti gli assistiti</div>
              <div className="text-xs text-stone-500">Assistiti ({stats?.patients ?? 0}) + tutto il loro diario</div>
            </div>
            <ConfirmDialog
              testId="clear-patients"
              title="Eliminare tutti gli assistiti?"
              description="Verranno rimossi anche tutti i dati clinici associati. L'operazione non è annullabile."
              confirmText="Elimina tutti"
              onConfirm={() => clearCollection("patients", "Assistiti")}
              trigger={
                <Button variant="outline" className="text-red-600 border-red-200 hover:bg-red-50" data-testid="clear-patients-btn">
                  <Trash2 size={14} className="mr-1" /> Svuota
                </Button>
              }
            />
          </div>
        </CardContent>
      </Card>

      <Card className="border-red-200">
        <CardHeader>
          <CardTitle className="text-base text-red-700">Zona pericolosa</CardTitle>
          <CardDescription>Reset totale dell'app — utile per il diritto all'oblio (GDPR).</CardDescription>
        </CardHeader>
        <CardContent>
          <ConfirmDialog
            testId="wipe-all"
            title="Reset totale dei dati"
            description="Verranno eliminati TUTTI gli assistiti e TUTTO il diario clinico. Questa operazione non è annullabile e non è possibile recuperare i dati. Vuoi davvero procedere?"
            confirmText="Sì, elimina tutto"
            onConfirm={wipeAll}
            trigger={
              <Button className="w-full bg-red-600 hover:bg-red-700" data-testid="wipe-all-btn">
                <Trash2 size={16} className="mr-2" /> Reset totale dell'app
              </Button>
            }
          />
          <p className="text-xs text-stone-500 mt-3">
            I dati sono salvati sul server dell'app. Cancellandoli, l'operazione è definitiva.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

// ---------- App ----------
function App() {
  return (
    <BrowserRouter>
      <Shell>
        <Routes>
          <Route path="/" element={<PatientsList />} />
          <Route path="/nuovo" element={<NewPatient />} />
          <Route path="/paziente/:id" element={<PatientDetail />} />
          <Route path="/impostazioni" element={<SettingsPage />} />
        </Routes>
      </Shell>
    </BrowserRouter>
  );
}

export default App;
