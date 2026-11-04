import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  Worker,
  Session,
  RecognitionReview,
  Site,
  Operator,
  NavigationTab,
  SecondaryScreen,
  DeviceFrameMode,
} from '../types';
import {
  INITIAL_WORKERS,
  INITIAL_SESSIONS,
  INITIAL_REVIEWS,
  INITIAL_SITES,
  INITIAL_OPERATOR,
} from '../data/mockData';
import { apiClient } from '../services/api';

interface KoshaContextType {
  // Navigation & Shell State
  currentTab: NavigationTab;
  setCurrentTab: (tab: NavigationTab) => void;
  secondaryScreen: SecondaryScreen;
  setSecondaryScreen: (screen: SecondaryScreen) => void;
  selectedWorkerId: string | null;
  setSelectedWorkerId: (id: string | null) => void;
  deviceFrame: DeviceFrameMode;
  setDeviceFrame: (mode: DeviceFrameMode) => void;
  isDarkMode: boolean;
  toggleDarkMode: () => void;
  isAuthenticated: boolean;
  login: (email?: string, password?: string) => Promise<void>;
  signup: (data: {
    name: string;
    email: string;
    password?: string;
    role?: string;
    siteId?: string;
    badgeNumber?: string;
  }) => Promise<void>;
  logout: () => void;

  // Data Collections
  workers: Worker[];
  sessions: Session[];
  reviews: RecognitionReview[];
  sites: Site[];
  operator: Operator;
  activeSite: Site;

  // Actions
  updateActiveSite: (siteId: string) => void;
  registerWorker: (newWorkerData: Partial<Worker> & { name: string; age: number; weight: number }) => Promise<Worker>;
  createSession: (
    workerId: string,
    shift: Session['shift'],
    gate: string,
    notes?: string
  ) => Session;
  resolveReview: (
    reviewId: string,
    action: 'confirm' | 'reject' | 'recapture'
  ) => void;

  // Biometrics Simulator Presets
  scannerPreset: 'MATCH' | 'UNCERTAIN' | 'NO_MATCH';
  setScannerPreset: (preset: 'MATCH' | 'UNCERTAIN' | 'NO_MATCH') => void;
  preselectedWorkerForSession: Worker | null;
  setPreselectedWorkerForSession: (worker: Worker | null) => void;

  // Notification Drawer
  notificationTrayOpen: boolean;
  setNotificationTrayOpen: (open: boolean) => void;
  notifications: Array<{
    id: string;
    title: string;
    desc: string;
    time: string;
    type: 'info' | 'success' | 'warning';
  }>;
  dismissNotification: (id: string) => void;
}

const KoshaContext = createContext<KoshaContextType | undefined>(undefined);

export const KoshaProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Navigation states
  const [currentTab, setCurrentTab] = useState<NavigationTab>('home');
  const [secondaryScreen, setSecondaryScreen] = useState<SecondaryScreen>('none');
  const [selectedWorkerId, setSelectedWorkerId] = useState<string | null>(null);
  const [deviceFrame, setDeviceFrame] = useState<DeviceFrameMode>('iphone');
  const [isDarkMode, setIsDarkMode] = useState<boolean>(true);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(true);

  // Entities
  const [workers, setWorkers] = useState<Worker[]>(() => {
    const saved = localStorage.getItem('kosha_workers');
    return saved ? JSON.parse(saved) : INITIAL_WORKERS;
  });

  const [sessions, setSessions] = useState<Session[]>(() => {
    const saved = localStorage.getItem('kosha_sessions');
    return saved ? JSON.parse(saved) : INITIAL_SESSIONS;
  });

  const [reviews, setReviews] = useState<RecognitionReview[]>(() => {
    const saved = localStorage.getItem('kosha_reviews');
    return saved ? JSON.parse(saved) : INITIAL_REVIEWS;
  });

  const [sites, setSites] = useState<Site[]>(INITIAL_SITES);
  const [operator, setOperator] = useState<Operator>(INITIAL_OPERATOR);
  const [scannerPreset, setScannerPreset] = useState<'MATCH' | 'UNCERTAIN' | 'NO_MATCH'>('MATCH');
  const [preselectedWorkerForSession, setPreselectedWorkerForSession] = useState<Worker | null>(null);

  // Notifications
  const [notificationTrayOpen, setNotificationTrayOpen] = useState(false);
  const [notifications, setNotifications] = useState([
    {
      id: 'notif-1',
      title: 'Biometric Scanner Calibrated',
      desc: 'Optical 500DPI unit at Shaft 4 Access Bay calibrated with 99.4% sensor cleanliness score.',
      time: '12 min ago',
      type: 'info' as const,
    },
    {
      id: 'notif-2',
      title: 'Duplicate Attempt Prevented',
      desc: 'Operator attempted re-enrollment for existing Worker WK-1001. System merged to existing identity.',
      time: '34 min ago',
      type: 'warning' as const,
    },
    {
      id: 'notif-3',
      title: 'Shift Quorum Reached',
      desc: 'Metro Line 4 morning roster reached 184 active verified check-ins.',
      time: '1 hr ago',
      type: 'success' as const,
    },
  ]);

  // Sync to local storage for realistic prototype state retention
  useEffect(() => {
    localStorage.setItem('kosha_workers', JSON.stringify(workers));
  }, [workers]);

  useEffect(() => {
    localStorage.setItem('kosha_sessions', JSON.stringify(sessions));
  }, [sessions]);

  useEffect(() => {
    localStorage.setItem('kosha_reviews', JSON.stringify(reviews));
  }, [reviews]);

  // Handle dark mode class on root document
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  // Load initial dataset from backend REST API
  useEffect(() => {
    async function initBackendData() {
      try {
        const [workersData, sessionsData] = await Promise.all([
          apiClient.getWorkers(),
          apiClient.getSessions(),
        ]);
        if (workersData && Array.isArray(workersData.items) && workersData.items.length > 0) {
          setWorkers(workersData.items);
        }
        if (sessionsData && Array.isArray(sessionsData) && sessionsData.length > 0) {
          setSessions(sessionsData);
        }
      } catch {
        // Fallback gracefully to offline seed cache
      }
    }
    initBackendData();
  }, []);

  const toggleDarkMode = () => setIsDarkMode((prev) => !prev);

  const login = async (email?: string, password?: string) => {
    const targetEmail = email || operator.email;
    const res = await apiClient.login(targetEmail, password);
    if (res?.operator) {
      setOperator((prev) => ({
        ...prev,
        id: res.operator.id || prev.id,
        name: res.operator.name || prev.name,
        email: res.operator.email || targetEmail,
        role: res.operator.role || prev.role,
        badgeNumber: res.operator.badgeNumber || prev.badgeNumber,
        activeSiteId: res.operator.activeSiteId || prev.activeSiteId,
      }));
    }
    setIsAuthenticated(true);
  };

  const signup = async (data: {
    name: string;
    email: string;
    password?: string;
    role?: string;
    siteId?: string;
    badgeNumber?: string;
  }) => {
    const res = await apiClient.signup(data);
    if (res?.operator) {
      setOperator({
        id: res.operator.id,
        name: res.operator.name,
        email: res.operator.email,
        role: res.operator.role,
        badgeNumber: res.operator.badgeNumber,
        activeSiteId: res.operator.activeSiteId || 'SITE-M4',
      });
    }
    setIsAuthenticated(true);
  };

  const logout = () => {
    apiClient.logout().catch(() => {});
    setIsAuthenticated(false);
    setCurrentTab('home');
    setSecondaryScreen('none');
  };

  const activeSite = sites.find((s) => s.id === operator.activeSiteId) || sites[0];

  const updateActiveSite = (siteId: string) => {
    setOperator((prev) => ({ ...prev, activeSiteId: siteId }));
  };

  // Register Worker: assigns immutable permanent Worker ID
  const registerWorker = async (
    newWorkerData: Partial<Worker> & { name: string; age: number; weight: number }
  ): Promise<Worker> => {
    // Call backend API first to let database sequence generate permanent Worker ID and execute duplicate prevention!
    const res = await apiClient.registerWorker({
      name: newWorkerData.name,
      age: newWorkerData.age,
      weight: newWorkerData.weight,
      gender: newWorkerData.gender,
      contact: newWorkerData.contact,
      emergencyContact: newWorkerData.emergencyContact,
      bloodGroup: newWorkerData.bloodGroup,
      siteId: newWorkerData.siteId || operator.activeSiteId,
      department: newWorkerData.department,
      category: newWorkerData.category,
      enrolledFingers: newWorkerData.enrolledFingers,
      consent_accepted: true,
      notes: newWorkerData.notes,
    });

    const permanentWorkerId = res.worker_id || res.id || `WK-${1000 + workers.length + 1}`;
    const colors = [
      'bg-emerald-600',
      'bg-blue-600',
      'bg-purple-600',
      'bg-amber-600',
      'bg-teal-600',
      'bg-indigo-600',
      'bg-rose-600',
    ];
    const assignedColor = colors[workers.length % colors.length];

    const todayStr = new Date().toISOString().split('T')[0];

    const newWorker: Worker = {
      id: permanentWorkerId,
      name: res.name || newWorkerData.name,
      age: res.age || Number(newWorkerData.age) || 30,
      weight: res.weight || Number(newWorkerData.weight) || 68,
      gender: (res.gender as any) || newWorkerData.gender || 'Male',
      contact: res.contact || newWorkerData.contact || '+91 98000 00000',
      emergencyContact: res.emergencyContact || newWorkerData.emergencyContact || 'Family (+91 98000 11111)',
      bloodGroup: res.bloodGroup || newWorkerData.bloodGroup || 'B+',
      siteId: res.siteId || newWorkerData.siteId || operator.activeSiteId,
      siteName:
        res.siteName ||
        sites.find((s) => s.id === (newWorkerData.siteId || operator.activeSiteId))?.name ||
        activeSite.name,
      department: res.department || newWorkerData.department || 'Structural Rigging',
      category: res.category || newWorkerData.category || 'General Labour',
      registrationDate: res.registrationDate || todayStr,
      status: 'Active',
      enrolledFingers:
        res.enrolledFingers && res.enrolledFingers.length > 0
          ? res.enrolledFingers
          : newWorkerData.enrolledFingers || [
              {
                finger: 'Right Thumb',
                quality: 95,
                enrolledAt: todayStr,
                templateHash: `HASH_RT_${permanentWorkerId}_OK`,
              },
            ],
      avatarColor: assignedColor,
      sessionsCount: 0,
      lastSessionDate: 'Never (New Registration)',
      notes: newWorkerData.notes || 'Enrolled via Kosha Labs Mobile Biometric Scanner.',
    };

    setWorkers((prev) => [newWorker, ...prev.filter((w) => w.id !== newWorker.id && w.name !== newWorker.name)]);

    // Add activity notification
    setNotifications((prev) => [
      {
        id: `notif-${Date.now()}`,
        title: 'New Worker Enrolled in Supabase',
        desc: `Permanent ID ${permanentWorkerId} assigned to ${newWorker.name} with ${newWorker.enrolledFingers.length} finger templates.`,
        time: 'Just now',
        type: 'success',
      },
      ...prev,
    ]);

    return newWorker;
  };

  // Create Recording Session: strictly links to existing permanent Worker ID!
  const createSession = (
    workerId: string,
    shift: Session['shift'],
    gate: string,
    notes?: string
  ): Session => {
    const worker = workers.find((w) => w.id === workerId);
    if (!worker) {
      throw new Error(`Worker with ID ${workerId} not found.`);
    }

    const nextSessionNum = String(sessions.length + 1).padStart(3, '0');
    const sessionId = `SES-${nextSessionNum}`;
    const now = new Date();
    const timeFormatted = now.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    });
    const dateFormatted = now.toISOString().split('T')[0];
    const timestampStr = `${dateFormatted} ${timeFormatted}`;

    const newSession: Session = {
      id: sessionId,
      workerId: worker.id, // Linking to permanent Worker ID
      workerName: worker.name,
      siteId: operator.activeSiteId,
      siteName: activeSite.name,
      timestamp: timestampStr,
      shift,
      gate,
      operator: `${operator.name} (ID: ${operator.badgeNumber})`,
      recognitionMethod: 'Fingerprint Biometric - Optical 500DPI',
      status: 'Verified & Active',
      notes: notes || 'Biometric identity matched and session recorded.',
    };

    setSessions((prev) => [newSession, ...prev]);

    // Asynchronously synchronize session with Backend REST API with idempotency key
    apiClient.createSession({
      worker_id: worker.id,
      shift,
      gate,
      notes,
      idempotency_key: `IDEMP-${worker.id}-${Date.now()}`,
    }).catch(() => {});

    // Update worker's session count & last session date
    setWorkers((prev) =>
      prev.map((w) => {
        if (w.id === workerId) {
          return {
            ...w,
            sessionsCount: w.sessionsCount + 1,
            lastSessionDate: `Today, ${timeFormatted}`,
          };
        }
        return w;
      })
    );

    // Update site's session count
    setSites((prev) =>
      prev.map((s) => {
        if (s.id === operator.activeSiteId) {
          return { ...s, todaySessions: s.todaySessions + 1 };
        }
        return s;
      })
    );

    // Notification
    setNotifications((prev) => [
      {
        id: `notif-${Date.now()}`,
        title: 'Session Recorded',
        desc: `Session ${sessionId} successfully logged for Worker ${worker.id} (${worker.name}).`,
        time: 'Just now',
        type: 'success',
      },
      ...prev,
    ]);

    return newSession;
  };

  // Resolve Ambiguous Review
  const resolveReview = (
    reviewId: string,
    action: 'confirm' | 'reject' | 'recapture'
  ) => {
    if (action === 'confirm') {
      apiClient.approveReview(reviewId).catch(() => {});
    } else {
      apiClient.rejectReview(reviewId).catch(() => {});
    }

    setReviews((prev) =>
      prev.map((rev) => {
        if (rev.id === reviewId) {
          return {
            ...rev,
            status:
              action === 'confirm'
                ? 'Confirmed Match'
                : 'Rejected - Recapture Requested',
            resolvedAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            resolvedBy: operator.name,
          };
        }
        return rev;
      })
    );
  };

  const dismissNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  return (
    <KoshaContext.Provider
      value={{
        currentTab,
        setCurrentTab,
        secondaryScreen,
        setSecondaryScreen,
        selectedWorkerId,
        setSelectedWorkerId,
        deviceFrame,
        setDeviceFrame,
        isDarkMode,
        toggleDarkMode,
        isAuthenticated,
        login,
        signup,
        logout,
        workers,
        sessions,
        reviews,
        sites,
        operator,
        activeSite,
        updateActiveSite,
        registerWorker,
        createSession,
        resolveReview,
        scannerPreset,
        setScannerPreset,
        preselectedWorkerForSession,
        setPreselectedWorkerForSession,
        notificationTrayOpen,
        setNotificationTrayOpen,
        notifications,
        dismissNotification,
      }}
    >
      {children}
    </KoshaContext.Provider>
  );
};

export const useKosha = () => {
  const context = useContext(KoshaContext);
  if (!context) {
    throw new Error('useKosha must be used within a KoshaProvider');
  }
  return context;
};

// Backwards-compatible alias
export const useAuth = useKosha;

