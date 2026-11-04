import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.koshalabs.workerverification',
  appName: 'Kosha Labs',
  webDir: 'dist',
  server: {
    androidScheme: 'https',
    cleartext: true,
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 1500,
      launchAutoHide: true,
      backgroundColor: '#020617',
      showSpinner: true,
      spinnerColor: '#10b981',
    },
    StatusBar: {
      style: 'DARK',
      backgroundColor: '#020617',
    },
    App: {
      // Hardware back button behavior handling
    },
  },
};

export default config;

