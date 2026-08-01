/**
 * Capacitor config for Caregiver Sync Android build.
 * @type {import('@capacitor/cli').CapacitorConfig}
 */
const config = {
  appId: 'com.caregiversync.app',
  appName: 'Caregiver Sync',
  webDir: 'build',
  android: {
    allowMixedContent: false,
    backgroundColor: '#F8F7F2',
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 1200,
      launchAutoHide: true,
      backgroundColor: '#0F766E',
      androidScaleType: 'CENTER_CROP',
      showSpinner: false,
    },
  },
};

module.exports = config;
