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
};

module.exports = config;
