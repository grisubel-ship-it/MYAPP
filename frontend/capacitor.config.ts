import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  // Deve corrispondere all'Application ID che userai su Google Play.
  // Formato dominio inverso, non modificabile una volta pubblicato.
  appId: 'com.tuazienda.caregiversync',

  // Nome visualizzato sotto l'icona nel launcher Android.
  appName: 'Caregiver Sync',

  // Cartella con la build di produzione di React (output di `yarn build`).
  webDir: 'build',

  // Splash screen + icone di stato
  plugins: {
    SplashScreen: {
      launchShowDuration: 1200,
      launchAutoHide: true,
      backgroundColor: '#0F766E',
      androidSplashResourceName: 'splash',
      androidScaleType: 'CENTER_CROP',
      showSpinner: false,
    },
  },

  // Configurazione Android
  android: {
    // Permette al webview di accettare cookie/session dal tuo backend HTTPS
    allowMixedContent: false,
    // Splash sfondo di default (vedi anche il plugin SplashScreen)
    backgroundColor: '#F8F7F2',
  },

  // ------------------------------------------------------------
  //  IMPORTANTE — Come raggiungere il backend FastAPI
  // ------------------------------------------------------------
  //  L'APK/AAB conterrà solo il frontend statico. Il backend deve
  //  restare online su un URL HTTPS pubblico (la tua PRODUCTION).
  //
  //  Il codice React usa già `process.env.REACT_APP_BACKEND_URL`,
  //  che al momento del `yarn build` viene "impresso" nel bundle.
  //  Assicurati che quel valore punti al backend di PRODUZIONE:
  //
  //    frontend/.env.production:
  //      REACT_APP_BACKEND_URL=https://app-release-config.emergent.host
  // ------------------------------------------------------------
};

export default config;
