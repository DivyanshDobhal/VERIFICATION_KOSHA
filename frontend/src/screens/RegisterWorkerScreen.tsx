import React, { useState, useRef } from 'react';
import { useKosha } from '../context/KoshaContext';
import { FingerType, EnrolledFinger, Worker } from '../types';
import { FingerprintIllustration } from '../components/biometrics/FingerprintIllustration';
import { ScannerStatusIndicator } from '../components/biometrics/ScannerStatusIndicator';
import { biometricsService, ExtractionResult } from '../services/biometrics';
import {
  CheckCircle2,
  ChevronRight,
  ChevronLeft,
  User,
  Briefcase,
  Fingerprint,
  FileCheck,
  RotateCcw,
  Plus,
  ShieldCheck,
  ArrowRight,
  AlertCircle,
  AlertTriangle,
  Upload,
  UserCheck,
  SlidersHorizontal,
  FileImage,
} from 'lucide-react';

export const RegisterWorkerScreen: React.FC = () => {
  const {
    registerWorker,
    sites,
    activeSite,
    setSecondaryScreen,
    setSelectedWorkerId,
  } = useKosha();

  // Wizard Step: 1, 2, 3, 4, 5 (Success)
  const [currentStep, setCurrentStep] = useState<number>(1);

  // Step 1: Personal Info
  const [fullName, setFullName] = useState('');
  const [age, setAge] = useState<number | ''>(28);
  const [weight, setWeight] = useState<number | ''>(65);
  const [gender, setGender] = useState<'Male' | 'Female' | 'Other' | 'Prefer not to say'>('Male');
  const [contactNumber, setContactNumber] = useState('+91 ');
  const [emergencyContact, setEmergencyContact] = useState('');
  const [bloodGroup, setBloodGroup] = useState('B+');

  // Step 2: Work Info
  const [siteId, setSiteId] = useState(activeSite.id);
  const [department, setDepartment] = useState('Structural Rigging');
  const [category, setCategory] = useState<Worker['category']>('General Labour');
  const [contractorMeta, setContractorMeta] = useState('L&T Infrastructure Corp');
  const [notes, setNotes] = useState('');

  // Step 3: Biometric Enrollment
  const [selectedFinger, setSelectedFinger] = useState<FingerType>('Right Thumb');
  const [enrolledFingers, setEnrolledFingers] = useState<EnrolledFinger[]>([]);
  const [isCapturing, setIsCapturing] = useState(false);
  const [captureProgress, setCaptureProgress] = useState(0);
  const [currentFingerQuality, setCurrentFingerQuality] = useState(94);
  const [lastCapturedFinger, setLastCapturedFinger] = useState<FingerType | null>(null);

  // Duplicate Check & Mode States (Steps 8 & 9)
  const [acquisitionMode, setAcquisitionMode] = useState<'scanner' | 'upload'>('scanner');
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [uploadedFileName, setUploadedFileName] = useState<string>('');
  const [simulateDuplicate, setSimulateDuplicate] = useState(false);
  const [duplicateMatch, setDuplicateMatch] = useState<{
    worker_id: string;
    worker_name: string;
    similarity: number;
    finger: string;
    worker?: any;
  } | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Step 4: Consent & Review
  const [consentAccepted, setConsentAccepted] = useState(false);
  const [registeredResult, setRegisteredResult] = useState<Worker | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Validation
  const [errorMessage, setErrorMessage] = useState('');

  // Available fingers for enrollment
  const fingerOptions: FingerType[] = [
    'Right Thumb',
    'Left Thumb',
    'Right Index',
    'Left Index',
    'Right Middle',
  ];

  // Handle high-res scanner file upload (BMP, PNG, JPG, WSQ)
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploadedFileName(file.name);
      const b64 = await biometricsService.fileToBase64(file);
      setUploadedImage(b64);
      setDuplicateMatch(null);
    } catch (err) {
      console.error('File read error:', err);
    }
  };

  // Live ML Biometric Capture & Duplicate Identity Check (Steps 4-9)
  const handleCaptureFingerprint = async () => {
    setIsCapturing(true);
    setDuplicateMatch(null);
    setErrorMessage('');
    setCaptureProgress(20);

    const progressTimer = setInterval(() => {
      setCaptureProgress((prev) => (prev >= 85 ? 85 : prev + 20));
    }, 120);

    try {
      // Send image to ML service (FastAPI or 128D Siamese engine)
      const res: ExtractionResult = await biometricsService.extract({
        imageBase64: uploadedImage || undefined,
        fingerType: selectedFinger,
        workerHint: fullName,
        forceDuplicate: simulateDuplicate,
      });

      clearInterval(progressTimer);
      setCaptureProgress(100);
      setIsCapturing(false);

      // STEP 8 & 9: Handle Duplicate Identity Detection
      if (res.is_duplicate && res.duplicate_match) {
        setDuplicateMatch(res.duplicate_match);
        setCurrentFingerQuality(res.quality_score);
        return; // Prevent adding template for duplicate identity
      }

      // Check minimum biometric quality threshold
      if (res.quality_score < 60) {
        setErrorMessage(
          `Fingerprint ridge quality score (${res.quality_score}%) is insufficient. Please clean scanner glass and recapture.`
        );
        return;
      }

      // Valid new identity: store template with 128D embedding
      setCurrentFingerQuality(res.quality_score);
      const todayStr = new Date().toISOString().split('T')[0];

      const newTemplate: EnrolledFinger = {
        finger: selectedFinger,
        quality: res.quality_score,
        enrolledAt: todayStr,
        templateHash: `HASH_${selectedFinger.replace(/\s+/g, '_').toUpperCase()}_${Date.now()}_OK`,
        embedding: res.embedding,
      };

      setEnrolledFingers((prev) => {
        const filtered = prev.filter((f) => f.finger !== selectedFinger);
        return [...filtered, newTemplate];
      });

      setLastCapturedFinger(selectedFinger);
    } catch (err: any) {
      clearInterval(progressTimer);
      setIsCapturing(false);
      setErrorMessage(err.message || 'Fingerprint feature extraction failed. Try again.');
    }
  };

  const handleRetake = () => {
    setEnrolledFingers((prev) => prev.filter((f) => f.finger !== selectedFinger));
    setLastCapturedFinger(null);
    setDuplicateMatch(null);
    setCaptureProgress(0);
    setUploadedImage(null);
    setUploadedFileName('');
  };

  // Step Navigations
  const handleNextFromStep1 = (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim()) {
      setErrorMessage('Worker full name is required.');
      return;
    }
    if (!age || Number(age) < 18) {
      setErrorMessage('Worker must be at least 18 years old.');
      return;
    }
    setErrorMessage('');
    setCurrentStep(2);
  };

  const handleNextFromStep2 = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setCurrentStep(3);
  };

  const handleNextFromStep3 = () => {
    if (enrolledFingers.length === 0) {
      setErrorMessage('Please capture at least one fingerprint template.');
      return;
    }
    setErrorMessage('');
    setCurrentStep(4);
  };

  // Final Registration Submission
  const handleFinalSubmit = async () => {
    if (!consentAccepted) {
      setErrorMessage('Worker biometric consent is mandatory for registration.');
      return;
    }

    setErrorMessage('');
    setIsSubmitting(true);

    try {
      const created = await registerWorker({
        name: fullName,
        age: Number(age) || 30,
        weight: Number(weight) || 68,
        gender,
        contact: contactNumber || '+91 98000 00000',
        emergencyContact: emergencyContact || 'Contractor Field Office',
        bloodGroup,
        siteId,
        department,
        category,
        enrolledFingers,
        notes: notes || `Contractor: ${contractorMeta}`,
      });

      setRegisteredResult(created);
      setCurrentStep(5); // Success state
    } catch (err: any) {
      if (err.status === 409 || err.message?.includes('Duplicate') || err.message?.includes('already enrolled')) {
        setErrorMessage(
          err.message ||
            'Duplicate worker registration detected! This worker already has an enrolled identity in the database.'
        );
      } else {
        setErrorMessage(err.message || 'Worker registration failed. Please verify data.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex-1 w-full bg-slate-900 text-slate-100 flex flex-col overflow-hidden pb-20">
      {/* Stepper Header (Only shown during steps 1-4) */}
      {currentStep <= 4 && (
        <div className="bg-slate-900 border-b border-slate-800 px-4 py-3 shrink-0">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-white">
              Step {currentStep} of 4:
              <span className="text-emerald-400 font-semibold ml-1.5">
                {currentStep === 1 && 'Personal Information'}
                {currentStep === 2 && 'Work & Site Details'}
                {currentStep === 3 && 'Fingerprint Enrollment'}
                {currentStep === 4 && 'Consent & Confirmation'}
              </span>
            </span>
            <span className="text-[11px] font-mono text-slate-400">
              {currentStep * 25}% Completed
            </span>
          </div>

          {/* Progress bar */}
          <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-emerald-500 rounded-full transition-all duration-300"
              style={{ width: `${currentStep * 25}%` }}
            />
          </div>
        </div>
      )}

      {/* Error alert banner */}
      {errorMessage && (
        <div className="mx-4 mt-3 p-3 rounded-xl bg-rose-500/15 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* STEP 1: PERSONAL INFORMATION */}
      {currentStep === 1 && (
        <form onSubmit={handleNextFromStep1} className="flex-1 overflow-y-auto no-scrollbar p-4 space-y-4">
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 space-y-3.5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
              <User className="w-4 h-4 text-emerald-400" />
              <span>Worker Identity Data</span>
            </h3>

            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">
                Full Legal Name <span className="text-emerald-400">*</span>
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="e.g. Rameshwar Prasad Gurjar"
                required
                className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium text-slate-300 block mb-1">
                  Age (Years) <span className="text-emerald-400">*</span>
                </label>
                <input
                  type="number"
                  min="18"
                  max="70"
                  value={age}
                  onChange={(e) => setAge(e.target.value ? Number(e.target.value) : '')}
                  required
                  className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-300 block mb-1">
                  Body Weight (kg) <span className="text-emerald-400">*</span>
                </label>
                <input
                  type="number"
                  min="40"
                  max="140"
                  value={weight}
                  onChange={(e) => setWeight(e.target.value ? Number(e.target.value) : '')}
                  required
                  className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium text-slate-300 block mb-1">
                  Gender
                </label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value as any)}
                  className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white focus:outline-none"
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                  <option value="Prefer not to say">Prefer not to say</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-medium text-slate-300 block mb-1">
                  Blood Group
                </label>
                <select
                  value={bloodGroup}
                  onChange={(e) => setBloodGroup(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white focus:outline-none"
                >
                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">
                Primary Contact Number (Optional)
              </label>
              <input
                type="tel"
                value={contactNumber}
                onChange={(e) => setContactNumber(e.target.value)}
                placeholder="+91 98XXX XXXXX"
                className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white font-mono placeholder-slate-500"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">
                Emergency Contact (Family / Kin)
              </label>
              <input
                type="text"
                value={emergencyContact}
                onChange={(e) => setEmergencyContact(e.target.value)}
                placeholder="e.g. Sunita Devi (Wife) +91 94140 12890"
                className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-md shadow-emerald-500/20 flex items-center justify-center gap-1.5"
          >
            <span>Proceed to Work Details</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </form>
      )}

      {/* STEP 2: WORK INFORMATION */}
      {currentStep === 2 && (
        <form onSubmit={handleNextFromStep2} className="flex-1 overflow-y-auto no-scrollbar p-4 space-y-4">
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 space-y-3.5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
              <Briefcase className="w-4 h-4 text-blue-400" />
              <span>Deployment & Category</span>
            </h3>

            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">
                Assigned Construction Site <span className="text-emerald-400">*</span>
              </label>
              <select
                value={siteId}
                onChange={(e) => setSiteId(e.target.value)}
                className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white focus:outline-none"
              >
                {sites.map((site) => (
                  <option key={site.id} value={site.id}>
                    {site.name} ({site.code})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">
                Trade Department <span className="text-emerald-400">*</span>
              </label>
              <select
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white focus:outline-none"
              >
                <option value="Structural Rigging">Structural Rigging</option>
                <option value="Tunneling Excavation">Tunneling Excavation</option>
                <option value="Electrical Systems & MEP">Electrical Systems & MEP</option>
                <option value="Concrete Operations">Concrete Operations</option>
                <option value="Safety & Scaffolding">Safety & Scaffolding</option>
                <option value="Heavy Earthworks">Heavy Earthworks</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">
                Worker Skill Category <span className="text-emerald-400">*</span>
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value as any)}
                className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white focus:outline-none"
              >
                <option value="General Labour">General Labour</option>
                <option value="Specialist Technician">Specialist Technician</option>
                <option value="Heavy Equipment Operator">Heavy Equipment Operator</option>
                <option value="Foreman / Supervisor">Foreman / Supervisor</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">
                Sub-Contractor / Vendor Agency
              </label>
              <input
                type="text"
                value={contractorMeta}
                onChange={(e) => setContractorMeta(e.target.value)}
                placeholder="e.g. L&T Infrastructure Corp"
                className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">
                Safety Notes & Certifications
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="e.g. Induction verified, PPE helmet and harness kit issued."
                rows={2}
                className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 resize-none"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setCurrentStep(1)}
              className="py-3 px-4 rounded-xl bg-slate-800 text-slate-300 font-semibold text-xs flex items-center justify-center gap-1"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Back</span>
            </button>

            <button
              type="submit"
              className="flex-1 py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-md shadow-emerald-500/20 flex items-center justify-center gap-1.5"
            >
              <span>Proceed to Biometric Enrollment</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </form>
      )}

      {/* STEP 3: FINGERPRINT ENROLLMENT */}
      {currentStep === 3 && (
        <div className="flex-1 overflow-y-auto no-scrollbar p-4 space-y-4">
          <ScannerStatusIndicator />

          {/* Acquisition Mode & Interactive Duplicate Simulator */}
          <div className="space-y-2">
            <div className="grid grid-cols-2 gap-1.5 bg-slate-800/60 p-1 rounded-2xl border border-slate-700/60">
              <button
                type="button"
                onClick={() => {
                  setAcquisitionMode('scanner');
                  setDuplicateMatch(null);
                }}
                className={`py-1.5 px-3 rounded-xl text-xs font-semibold transition-all flex items-center justify-center gap-1.5 ${
                  acquisitionMode === 'scanner'
                    ? 'bg-emerald-500 text-slate-950 shadow-md font-bold'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Fingerprint className="w-3.5 h-3.5" />
                <span>USB Scanner</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  setAcquisitionMode('upload');
                  setDuplicateMatch(null);
                }}
                className={`py-1.5 px-3 rounded-xl text-xs font-semibold transition-all flex items-center justify-center gap-1.5 ${
                  acquisitionMode === 'upload'
                    ? 'bg-emerald-500 text-slate-950 shadow-md font-bold'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Upload className="w-3.5 h-3.5" />
                <span>Upload Scan</span>
              </button>
            </div>

            {/* Duplicate Identity Simulation Toggle */}
            <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-2.5">
              <div className="flex items-center justify-between mb-1.5 px-1">
                <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 flex items-center gap-1">
                  <SlidersHorizontal className="w-3 h-3 text-emerald-400" />
                  <span>Deduplication Test Toggle</span>
                </span>
                <span className="text-[10px] text-amber-400/90 font-medium">Step 8 & 9 Check</span>
              </div>

              <div className="grid grid-cols-2 gap-1.5">
                <button
                  type="button"
                  onClick={() => {
                    setSimulateDuplicate(false);
                    setDuplicateMatch(null);
                  }}
                  className={`py-1.5 px-2 rounded-xl text-[11px] font-semibold transition-all ${
                    !simulateDuplicate
                      ? 'bg-emerald-500 text-slate-950 shadow-md font-bold'
                      : 'bg-slate-800 text-slate-300 hover:text-white'
                  }`}
                >
                  Fresh Identity (New Worker)
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setSimulateDuplicate(true);
                  }}
                  className={`py-1.5 px-2 rounded-xl text-[11px] font-semibold transition-all ${
                    simulateDuplicate
                      ? 'bg-amber-500 text-slate-950 shadow-md font-bold'
                      : 'bg-slate-800 text-slate-300 hover:text-white'
                  }`}
                >
                  Duplicate Test (Matches WK-1001)
                </button>
              </div>
            </div>
          </div>

          {/* STEP 8 & 9: DUPLICATE IDENTITY DETECTED ALERT CARD */}
          {duplicateMatch && (
            <div className="bg-amber-950/40 border-2 border-amber-500/80 rounded-2xl p-4 space-y-3 animate-in fade-in slide-in-from-top-2">
              <div className="flex items-start gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center shrink-0 mt-0.5">
                  <AlertTriangle className="w-5 h-5" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-amber-400">
                      DUPLICATE IDENTITY DETECTED ({duplicateMatch.similarity}%)
                    </span>
                    <span className="text-[10px] bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded-full font-medium">
                      Registration Blocked
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-white mt-0.5">
                    Worker already enrolled: {duplicateMatch.worker_name}
                  </h4>
                  <p className="text-[11px] text-slate-300 mt-0.5 leading-relaxed">
                    This biometric template matches permanent Worker ID{' '}
                    <strong className="text-amber-300 font-mono">{duplicateMatch.worker_id}</strong>. Central policy prevents duplicate identity registration.
                  </p>
                </div>
              </div>

              {/* Actions for duplicate */}
              <div className="grid grid-cols-2 gap-2 pt-1">
                <button
                  type="button"
                  onClick={() => {
                    setSelectedWorkerId(duplicateMatch.worker_id);
                    setSecondaryScreen('worker-detail');
                  }}
                  className="py-2.5 px-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition-colors flex items-center justify-center gap-1.5"
                >
                  <UserCheck className="w-4 h-4" />
                  <span>Open Existing Profile</span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setDuplicateMatch(null);
                    setSimulateDuplicate(false);
                    handleRetake();
                  }}
                  className="py-2.5 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs transition-colors flex items-center justify-center gap-1.5"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>Retake / Different Finger</span>
                </button>
              </div>
            </div>
          )}

          {/* Biometrics Capture Unit */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 flex flex-col items-center space-y-3">
            <div className="text-center">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Enroll Fingerprint Templates
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5">
                {acquisitionMode === 'upload'
                  ? 'Upload 500DPI scanner export or photo'
                  : 'Select finger and place on optical scanner window'}
              </p>
            </div>

            {/* Finger Selection Tabs */}
            <div className="w-full flex items-center justify-center gap-1.5 overflow-x-auto no-scrollbar py-1">
              {fingerOptions.map((f) => {
                const isEnrolled = enrolledFingers.some((ef) => ef.finger === f);
                const isSelected = selectedFinger === f;
                return (
                  <button
                    key={f}
                    type="button"
                    disabled={isCapturing}
                    onClick={() => {
                      setSelectedFinger(f);
                      setDuplicateMatch(null);
                    }}
                    className={`px-2.5 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors flex items-center gap-1 shrink-0 ${
                      isSelected
                        ? 'bg-emerald-500 text-slate-950 font-bold'
                        : isEnrolled
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                        : 'bg-slate-900 text-slate-400 border border-slate-700'
                    }`}
                  >
                    {isEnrolled && <CheckCircle2 className="w-3 h-3 text-emerald-400" />}
                    <span>{f}</span>
                  </button>
                );
              })}
            </div>

            {/* If Acquisition is Image Upload */}
            {acquisitionMode === 'upload' ? (
              <div className="w-full max-w-sm flex flex-col items-center">
                <input
                  type="file"
                  ref={fileInputRef}
                  accept="image/png,image/jpeg,image/bmp,.wsq"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                {uploadedImage ? (
                  <div className="relative group bg-slate-900 border border-slate-700 rounded-2xl p-3 flex flex-col items-center w-full">
                    <img
                      src={uploadedImage}
                      alt="Fingerprint Scan Preview"
                      className="w-28 h-36 object-contain rounded-lg border border-slate-700 bg-slate-950 p-1"
                    />
                    <span className="text-[11px] font-mono text-emerald-400 mt-2 truncate max-w-[200px]">
                      {uploadedFileName || 'Uploaded Ridge Scan'}
                    </span>
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="mt-1 text-[10px] text-slate-400 hover:text-white underline"
                    >
                      Change Image File
                    </button>
                  </div>
                ) : (
                  <div
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full border-2 border-dashed border-slate-700 hover:border-emerald-500/60 rounded-2xl p-5 text-center cursor-pointer transition-colors bg-slate-900/60 hover:bg-slate-900"
                  >
                    <div className="w-9 h-9 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto mb-2">
                      <FileImage className="w-4 h-4" />
                    </div>
                    <h4 className="text-xs font-semibold text-white">Click to Select Scan File</h4>
                    <p className="text-[10px] text-slate-400 mt-1">
                      BMP, PNG, JPG, or WSQ
                    </p>
                  </div>
                )}
              </div>
            ) : (
              /* Illustrative Biometric Artwork */
              <FingerprintIllustration
                isScanning={isCapturing}
                quality={currentFingerQuality}
                state={isCapturing ? 'scanning' : lastCapturedFinger === selectedFinger ? 'matched' : 'idle'}
                size="normal"
              />
            )}

            {/* Capture Action & Retake */}
            <div className="w-full space-y-2 pt-1">
              <button
                type="button"
                disabled={isCapturing}
                onClick={handleCaptureFingerprint}
                className="w-full py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 disabled:opacity-60 text-slate-950 font-bold text-xs shadow-md shadow-emerald-500/20 flex items-center justify-center gap-2 transition-all active:scale-[0.98]"
              >
                <Fingerprint className="w-4 h-4 stroke-[2.2]" />
                <span>
                  {isCapturing
                    ? 'Extracting 128D Embeddings...'
                    : acquisitionMode === 'upload' && uploadedImage
                    ? `Enroll Uploaded ${selectedFinger}`
                    : `Capture ${selectedFinger}`}
                </span>
              </button>

              {lastCapturedFinger === selectedFinger && (
                <button
                  type="button"
                  onClick={handleRetake}
                  className="w-full py-2 text-xs text-slate-400 hover:text-slate-200 flex items-center justify-center gap-1"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Retake {selectedFinger}</span>
                </button>
              )}
            </div>
          </div>

          {/* Enrolled Templates Summary List */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-3.5 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-300">
                Enrolled Finger Templates ({enrolledFingers.length})
              </span>
              <span className="text-[11px] text-emerald-400 font-mono">
                {enrolledFingers.length >= 2 ? 'Optimal (2+ Enrolled)' : 'Minimum 1 Required'}
              </span>
            </div>

            {enrolledFingers.length === 0 ? (
              <p className="text-xs text-slate-500 py-2 text-center">
                No templates captured yet. Select finger and capture above.
              </p>
            ) : (
              <div className="space-y-1.5">
                {enrolledFingers.map((ef, idx) => (
                  <div
                    key={idx}
                    className="p-2 bg-slate-900 rounded-xl flex items-center justify-between text-xs border border-slate-800"
                  >
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      <span className="font-medium text-slate-200">{ef.finger}</span>
                      <span className="text-[10px] font-mono text-slate-400">(128D Vector)</span>
                    </div>
                    <span className="text-[10px] font-mono text-emerald-400">
                      Quality: {ef.quality}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Navigation */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setCurrentStep(2)}
              className="py-3 px-4 rounded-xl bg-slate-800 text-slate-300 font-semibold text-xs flex items-center justify-center gap-1"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Back</span>
            </button>

            <button
              type="button"
              onClick={handleNextFromStep3}
              className="flex-1 py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-md shadow-emerald-500/20 flex items-center justify-center gap-1.5"
            >
              <span>Review & Sign Consent</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 4: CONSENT AND CONFIRMATION */}
      {currentStep === 4 && (
        <div className="flex-1 overflow-y-auto no-scrollbar p-4 space-y-4">
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 space-y-3.5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
              <FileCheck className="w-4 h-4 text-emerald-400" />
              <span>Verify Enrollment Summary</span>
            </h3>

            {/* Summary Review Card */}
            <div className="bg-slate-900 rounded-xl p-3 border border-slate-800 space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">Worker Name:</span>
                <span className="font-bold text-white">{fullName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Age & Weight:</span>
                <span className="text-slate-200">{age} yrs · {weight} kg</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Gender & Blood:</span>
                <span className="text-slate-200">{gender} · {bloodGroup}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Department:</span>
                <span className="text-slate-200">{department}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Site Assignment:</span>
                <span className="text-slate-200 truncate max-w-[180px]">
                  {sites.find((s) => s.id === siteId)?.name || activeSite.name}
                </span>
              </div>
              <div className="flex justify-between pt-1 border-t border-slate-800">
                <span className="text-slate-400">Enrolled Fingers:</span>
                <span className="font-mono font-bold text-emerald-400">
                  {enrolledFingers.map((f) => f.finger).join(', ')}
                </span>
              </div>
            </div>

            {/* Biometric Consent Clause */}
            <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-3 space-y-2">
              <label className="flex items-start gap-2.5 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={consentAccepted}
                  onChange={(e) => setConsentAccepted(e.target.checked)}
                  className="mt-0.5 w-4 h-4 rounded bg-slate-900 border-slate-700 text-emerald-500 focus:ring-emerald-500/30 shrink-0"
                />
                <span className="text-xs text-slate-200 leading-snug">
                  I certify that the worker has provided informed biometric consent under applicable workforce data protection guidelines. A permanent Worker ID will be minted for all future sessions.
                </span>
              </label>
            </div>
          </div>

          {/* Navigation & Final Register Action */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setCurrentStep(3)}
              className="py-3 px-4 rounded-xl bg-slate-800 text-slate-300 font-semibold text-xs flex items-center justify-center gap-1"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Back</span>
            </button>

            <button
              type="button"
              disabled={!consentAccepted || isSubmitting}
              onClick={handleFinalSubmit}
              className="flex-1 py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-500/25 flex items-center justify-center gap-1.5 active:scale-[0.98] transition-all"
            >
              {isSubmitting ? (
                <>
                  <span className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                  <span>Syncing with Supabase Cloud...</span>
                </>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4" />
                  <span>Register Worker & Issue ID</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* STEP 5: REGISTRATION SUCCESS CARD */}
      {currentStep === 5 && registeredResult && (
        <div className="flex-1 overflow-y-auto no-scrollbar p-5 flex flex-col justify-center items-center text-center space-y-5 animate-in fade-in zoom-in-95 duration-200">
          <div className="w-16 h-16 rounded-3xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center shadow-xl shadow-emerald-500/20">
            <CheckCircle2 className="w-10 h-10 stroke-[2.2]" />
          </div>

          <div>
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-emerald-400">
              Registration Successful
            </span>
            <h2 className="text-xl font-bold text-white mt-1">
              Permanent Identity Minted
            </h2>
            <p className="text-xs text-slate-400 max-w-xs mx-auto mt-1">
              Worker registered without duplicates. Future shifts will link directly to this Worker ID.
            </p>
          </div>

          {/* Database Confirmation Badge */}
          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[11px] font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>Persisted to Supabase PostgreSQL (bhnrrosrjednzctdirkn)</span>
          </div>

          {/* Minted Permanent Worker ID Badge */}
          <div className="w-full bg-slate-800/90 border-2 border-emerald-500/60 rounded-3xl p-4 shadow-xl text-left space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase">
                  Permanent Worker ID
                </span>
                <div className="font-mono font-extrabold text-2xl text-emerald-400">
                  {registeredResult.id}
                </div>
              </div>
              <div className="px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-[11px] font-semibold border border-emerald-500/30">
                Active Identity
              </div>
            </div>

            <div className="pt-2 border-t border-slate-700/60 text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-slate-400">Name:</span>
                <span className="font-semibold text-white">{registeredResult.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Department:</span>
                <span className="text-slate-200">{registeredResult.department}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Enrolled Fingerprints:</span>
                <span className="font-mono text-emerald-400">
                  {registeredResult.enrolledFingers.length} Templates Stored
                </span>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="w-full space-y-2">
            <button
              onClick={() => {
                setSelectedWorkerId(registeredResult.id);
                setSecondaryScreen('worker-detail');
              }}
              className="w-full py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-md shadow-emerald-500/20 flex items-center justify-center gap-1.5"
            >
              <span>View Worker Profile & Sessions</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={() => {
                setCurrentStep(1);
                setFullName('');
                setEnrolledFingers([]);
                setConsentAccepted(false);
                setRegisteredResult(null);
              }}
              className="w-full py-2.5 text-xs text-slate-400 hover:text-slate-200 font-medium"
            >
              Enroll Another Worker
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
