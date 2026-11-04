/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { KoshaProvider, useKosha } from './context/KoshaContext';
import { DeviceFrameWrapper } from './components/common/DeviceFrameWrapper';
import { MobileStatusBar } from './components/navigation/MobileStatusBar';
import { MobileHeader } from './components/navigation/MobileHeader';
import { BottomNavigation } from './components/navigation/BottomNavigation';
import { NotificationDrawer } from './components/common/NotificationDrawer';
import { Capacitor } from '@capacitor/core';
import { App as CapApp } from '@capacitor/app';
import { StatusBar, Style } from '@capacitor/status-bar';
import { SplashScreen as CapSplashScreen } from '@capacitor/splash-screen';

// Screens
import { SplashScreen } from './screens/SplashScreen';
import { LoginScreen } from './screens/LoginScreen';
import { HomeScreen } from './screens/HomeScreen';
import { RecognizeScreen } from './screens/RecognizeScreen';
import { WorkersScreen } from './screens/WorkersScreen';
import { WorkerDetailScreen } from './screens/WorkerDetailScreen';
import { RegisterWorkerScreen } from './screens/RegisterWorkerScreen';
import { CreateSessionScreen } from './screens/CreateSessionScreen';
import { SessionsScreen } from './screens/SessionsScreen';
import { RecognitionReviewScreen } from './screens/RecognitionReviewScreen';
import { AnalyticsScreen } from './screens/AnalyticsScreen';
import { SitesScreen } from './screens/SitesScreen';
import { ProfileMoreScreen } from './screens/ProfileMoreScreen';

const MainAppContent: React.FC = () => {
  const [showSplash, setShowSplash] = useState(true);
  const { isAuthenticated, currentTab, setCurrentTab, secondaryScreen, setSecondaryScreen } = useKosha();

  // Initialize native mobile status bar and capacitor runtime
  useEffect(() => {
    if (Capacitor.isNativePlatform()) {
      try {
        StatusBar.setStyle({ style: Style.Dark });
        StatusBar.setBackgroundColor({ color: '#020617' });
        CapSplashScreen.hide();
      } catch (e) {
        // Safe fallback
      }
    }
  }, []);

  // Hardware Back Button Navigation Handler for Android
  useEffect(() => {
    if (!Capacitor.isNativePlatform()) return;

    const backListener = CapApp.addListener('backButton', () => {
      if (secondaryScreen !== null) {
        setSecondaryScreen(null);
      } else if (currentTab !== 'home') {
        setCurrentTab('home');
      } else {
        CapApp.exitApp();
      }
    });

    return () => {
      backListener.then((listener) => listener.remove());
    };
  }, [secondaryScreen, currentTab, setSecondaryScreen, setCurrentTab]);

  if (showSplash) {
    return <SplashScreen onFinish={() => setShowSplash(false)} />;
  }

  if (!isAuthenticated) {
    return <LoginScreen />;
  }

  // Render active screen
  const renderActiveScreen = () => {
    if (secondaryScreen === 'register-worker') return <RegisterWorkerScreen />;
    if (secondaryScreen === 'worker-detail') return <WorkerDetailScreen />;
    if (secondaryScreen === 'create-session') return <CreateSessionScreen />;
    if (secondaryScreen === 'recognition-review') return <RecognitionReviewScreen />;
    if (secondaryScreen === 'analytics') return <AnalyticsScreen />;
    if (secondaryScreen === 'sites') return <SitesScreen />;

    switch (currentTab) {
      case 'home':
        return <HomeScreen />;
      case 'workers':
        return <WorkersScreen />;
      case 'recognize':
        return <RecognizeScreen />;
      case 'sessions':
        return <SessionsScreen />;
      case 'profile':
        return <ProfileMoreScreen />;
      default:
        return <HomeScreen />;
    }
  };

  return (
    <div className="flex-1 flex flex-col w-full h-full overflow-hidden bg-slate-900 relative">
      {/* Native Mobile Status Bar */}
      <MobileStatusBar />

      {/* Mobile Top App Bar */}
      <MobileHeader />

      {/* Screen Body View */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
        {renderActiveScreen()}
      </div>

      {/* System Notifications Drawer Modal */}
      <NotificationDrawer />

      {/* Bottom Tab Bar with elevated central Recognize action */}
      <BottomNavigation />
    </div>
  );
};

export default function App() {
  return (
    <KoshaProvider>
      <DeviceFrameWrapper>
        <MainAppContent />
      </DeviceFrameWrapper>
    </KoshaProvider>
  );
}
