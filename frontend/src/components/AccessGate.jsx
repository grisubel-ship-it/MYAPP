import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { Link, Navigate, useLocation } from "react-router-dom";
import { Clock } from "lucide-react";
import { fetchAccess, hasLocalStorePro } from "@/lib/subscription";

const AccessContext = createContext({ status: null, refresh: () => {} });
export const useAccess = () => useContext(AccessContext);

const OPEN_PATHS = ["/pro", "/admin"];

export function AccessProvider({ children }) {
  const [status, setStatus] = useState(null);
  const refresh = useCallback(async () => {
    try {
      const data = await fetchAccess();
      if (!data.access && hasLocalStorePro()) data.access = true;
      setStatus(data);
    } catch {
      // In caso di rete assente non blocchiamo l'utente
      setStatus({ access: true, reason: "offline" });
    }
  }, []);
  useEffect(() => {
    refresh();
  }, [refresh]);
  return <AccessContext.Provider value={{ status, refresh }}>{children}</AccessContext.Provider>;
}

export function AccessGate({ children }) {
  const { status } = useAccess();
  const { pathname } = useLocation();
  if (OPEN_PATHS.includes(pathname)) return children;
  if (!status) {
    return (
      <div className="py-24 text-center text-stone-500 text-sm" data-testid="access-loading">
        Caricamento…
      </div>
    );
  }
  if (!status.access) return <Navigate to="/pro" replace />;
  return children;
}

export function TrialBanner() {
  const { status } = useAccess();
  const { pathname } = useLocation();
  if (!status || status.reason !== "trial" || pathname === "/admin") return null;
  const days = status.trial_days_left;
  return (
    <div className="bg-amber-50 border-b border-amber-200" data-testid="trial-banner">
      <div className="max-w-4xl mx-auto px-5 py-2 flex items-center justify-between gap-3 text-sm">
        <span className="flex items-center gap-2 text-amber-900">
          <Clock size={15} />
          <span data-testid="trial-days-left">
            Prova gratuita: {days} {days === 1 ? "giorno rimasto" : "giorni rimasti"}
          </span>
        </span>
        {pathname !== "/pro" && (
          <Link to="/pro" className="text-teal-700 font-medium whitespace-nowrap" data-testid="trial-banner-cta">
            Abbonati o usa un codice
          </Link>
        )}
      </div>
    </div>
  );
}
