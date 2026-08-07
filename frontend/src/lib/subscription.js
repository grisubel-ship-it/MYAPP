// src/lib/subscription.js
// Wrapper per RevenueCat Purchases con fallback sicuro su web (dove il plugin non funziona).
// Persiste un appUserID stabile via localStorage.

import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const APP_USER_ID_KEY = "cgsync.app_user_id";
const RC_ANDROID_KEY = process.env.REACT_APP_RC_ANDROID_KEY || "";

// Rileva se siamo nell'app nativa Capacitor
export function isNative() {
  return typeof window !== "undefined"
    && window.Capacitor
    && typeof window.Capacitor.isNativePlatform === "function"
    && window.Capacitor.isNativePlatform();
}

// Ottiene o crea un ID stabile per l'utente/dispositivo
export function getAppUserId() {
  if (typeof localStorage === "undefined") return "anon";
  let id = localStorage.getItem(APP_USER_ID_KEY);
  if (!id) {
    id = `u_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 10)}`;
    localStorage.setItem(APP_USER_ID_KEY, id);
  }
  return id;
}

// Configura RevenueCat SDK (solo su native)
let _rcConfigured = false;
export async function configureRevenueCat() {
  if (!isNative() || _rcConfigured) return;
  if (!RC_ANDROID_KEY) {
    console.warn("[subscription] REACT_APP_RC_ANDROID_KEY non configurata — paywall in modalità demo");
    return;
  }
  try {
    const { Purchases, LOG_LEVEL } = await import("@revenuecat/purchases-capacitor");
    await Purchases.setLogLevel({ level: LOG_LEVEL.INFO });
    await Purchases.configure({
      apiKey: RC_ANDROID_KEY,
      appUserID: getAppUserId(),
    });
    _rcConfigured = true;
  } catch (e) {
    console.error("[subscription] Errore init RevenueCat", e);
  }
}

// Recupera le offerte da RevenueCat
export async function getOfferings() {
  if (!isNative() || !_rcConfigured) return null;
  try {
    const { Purchases } = await import("@revenuecat/purchases-capacitor");
    const result = await Purchases.getOfferings();
    return result.current || null;
  } catch (e) {
    console.error("[subscription] getOfferings", e);
    return null;
  }
}

// Acquisto pacchetto
export async function purchasePackage(pkg) {
  if (!isNative() || !_rcConfigured) {
    throw new Error("L'acquisto è disponibile solo nell'app Android");
  }
  const { Purchases } = await import("@revenuecat/purchases-capacitor");
  const result = await Purchases.purchasePackage({ aPackage: pkg });
  return result.customerInfo;
}

// Ripristina acquisti
export async function restorePurchases() {
  if (!isNative() || !_rcConfigured) return null;
  const { Purchases } = await import("@revenuecat/purchases-capacitor");
  const result = await Purchases.restorePurchases();
  return result.customerInfo;
}

// Entitlement server-side (fonte di verità)
export async function fetchEntitlement() {
  const uid = getAppUserId();
  const { data } = await axios.get(`${API}/subscription/entitlement`, { params: { app_user_id: uid } });
  return data;
}

// Uso corrente handover (per mostrare "N/3 rimasti")
export async function fetchUsage() {
  const uid = getAppUserId();
  const { data } = await axios.get(`${API}/subscription/usage`, { params: { app_user_id: uid } });
  return data;
}
