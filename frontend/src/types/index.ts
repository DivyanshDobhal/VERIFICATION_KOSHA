export type FingerType =
  | 'Right Thumb'
  | 'Left Thumb'
  | 'Right Index'
  | 'Left Index'
  | 'Right Middle'
  | 'Left Middle';

export interface EnrolledFinger {
  finger: FingerType;
  quality: number; // 0 - 100
  enrolledAt: string;
  templateHash: string;
  embedding?: number[];
}

export interface Worker {
  id: string; // Permanent Worker ID (e.g. WK-1001)
  name: string;
  age: number;
  weight: number; // kg
  gender: 'Male' | 'Female' | 'Other' | 'Prefer not to say';
  contact: string;
  emergencyContact: string;
  bloodGroup: string;
  siteId: string;
  siteName: string;
  department: string;
  category: 'General Labour' | 'Specialist Technician' | 'Heavy Equipment Operator' | 'Foreman / Supervisor';
  registrationDate: string;
  status: 'Active' | 'Under Review' | 'Inactive';
  enrolledFingers: EnrolledFinger[];
  avatarColor: string;
  sessionsCount: number;
  lastSessionDate: string;
  notes?: string;
}

export interface Session {
  id: string; // Permanent Session ID (e.g. SES-9012)
  workerId: string; // Linked permanent Worker ID
  workerName: string;
  siteId: string;
  siteName: string;
  timestamp: string;
  shift: 'Morning Shift (06:00 - 14:00)' | 'General Shift (08:30 - 17:30)' | 'Night Shift (20:00 - 04:00)';
  gate: string;
  operator: string;
  recognitionMethod: 'Fingerprint Biometric - Optical 500DPI' | 'Manual Supervisor Override';
  status: 'Verified & Active' | 'Completed' | 'Safety Flagged';
  notes?: string;
}

export interface RecognitionReview {
  id: string;
  timestamp: string;
  siteId: string;
  siteName: string;
  scannedFinger: FingerType;
  confidenceScore: number; // 0 - 100
  operator: string;
  primaryCandidate: {
    workerId: string;
    name: string;
    department: string;
    similarity: number;
    avatarColor: string;
    enrolledDate: string;
  };
  secondaryCandidate?: {
    workerId: string;
    name: string;
    department: string;
    similarity: number;
    avatarColor: string;
    enrolledDate: string;
  };
  status: 'Pending Review' | 'Confirmed Match' | 'Rejected - Recapture Requested';
  resolvedAt?: string;
  resolvedBy?: string;
}

export interface Site {
  id: string;
  name: string;
  code: string;
  location: string;
  contractor: string;
  activeWorkers: number;
  todaySessions: number;
}

export interface Operator {
  id: string;
  name: string;
  email: string;
  role: string;
  badgeNumber: string;
  activeSiteId: string;
}

export type NavigationTab = 'home' | 'workers' | 'recognize' | 'sessions' | 'profile';
export type SecondaryScreen = 
  | 'none'
  | 'register-worker'
  | 'worker-detail'
  | 'create-session'
  | 'recognition-review'
  | 'sites'
  | 'analytics'
  | 'settings'
  | 'scanner-diagnostics';

export type DeviceFrameMode = 'iphone' | 'pixel' | 'tablet' | 'fluid';
