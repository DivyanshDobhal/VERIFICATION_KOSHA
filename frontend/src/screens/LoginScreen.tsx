import React, { useState } from 'react';
import { useKosha } from '../context/KoshaContext';
import {
  Fingerprint,
  Eye,
  EyeOff,
  Lock,
  Mail,
  ShieldCheck,
  ArrowRight,
  User,
  Building2,
  BadgeAlert,
  CheckCircle2,
  AlertCircle,
  UserPlus,
  LogIn,
} from 'lucide-react';

export const LoginScreen: React.FC = () => {
  const { login, signup, operator, sites } = useKosha();

  // Mode: 'signin' | 'signup'
  const [mode, setMode] = useState<'signin' | 'signup'>('signin');

  // Sign In State
  const [email, setEmail] = useState(operator.email || 'v.sethi@koshalabs.internal');
  const [password, setPassword] = useState('kosha2026');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);

  // Sign Up State
  const [regName, setRegName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regRole, setRegRole] = useState<'operator' | 'supervisor' | 'admin'>('operator');
  const [regSiteId, setRegSiteId] = useState(sites[0]?.code || 'SITE-M4');
  const [regBadge, setRegBadge] = useState(`KOSHA-OP-${Math.floor(100 + Math.random() * 900)}`);

  // UI States
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');
    setLoading(true);

    try {
      await login(email, password);
    } catch (err: any) {
      setErrorMessage(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');

    if (!regName.trim()) {
      setErrorMessage('Full name is required.');
      return;
    }
    if (!regEmail.trim()) {
      setErrorMessage('Operator email is required.');
      return;
    }

    setLoading(true);

    try {
      await signup({
        name: regName.trim(),
        email: regEmail.trim(),
        password: regPassword || 'kosha2026',
        role: regRole,
        siteId: regSiteId,
        badgeNumber: regBadge.trim(),
      });
      setSuccessMessage('Operator registered successfully in Supabase!');
    } catch (err: any) {
      setErrorMessage(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoFill = () => {
    setEmail('v.sethi@koshalabs.internal');
    setPassword('KoshaPass@2026');
    setErrorMessage('');
  };

  const handleSwitchMode = (newMode: 'signin' | 'signup') => {
    setMode(newMode);
    setErrorMessage('');
    setSuccessMessage('');
  };

  return (
    <div className="flex-1 w-full bg-slate-900 text-slate-100 flex flex-col justify-between p-6 overflow-y-auto no-scrollbar">
      {/* Brand Header */}
      <div className="pt-2 text-center shrink-0">
        <div className="inline-flex w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 items-center justify-center text-emerald-400 mb-3 shadow-lg shadow-emerald-500/10">
          <Fingerprint className="w-8 h-8 stroke-[1.8]" />
        </div>
        <h1 className="text-xl font-bold tracking-tight text-white">
          KOSHA LABS
        </h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Intelligent Worker Identity Management System
        </p>
        <div className="mt-2 inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-800 text-[11px] font-mono text-emerald-400 border border-slate-700">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span>Connected to Supabase PostgreSQL</span>
        </div>
      </div>

      {/* Mode Selector Tabs: Sign In vs Sign Up */}
      <div className="w-full max-w-sm mx-auto my-4 shrink-0">
        <div className="grid grid-cols-2 p-1 bg-slate-800/80 rounded-xl border border-slate-700 text-xs font-semibold">
          <button
            type="button"
            onClick={() => handleSwitchMode('signin')}
            className={`py-2 rounded-lg flex items-center justify-center gap-1.5 transition-all ${
              mode === 'signin'
                ? 'bg-emerald-500 text-slate-950 shadow-sm font-bold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <LogIn className="w-3.5 h-3.5" />
            <span>Sign In</span>
          </button>
          <button
            type="button"
            onClick={() => handleSwitchMode('signup')}
            className={`py-2 rounded-lg flex items-center justify-center gap-1.5 transition-all ${
              mode === 'signup'
                ? 'bg-emerald-500 text-slate-950 shadow-sm font-bold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <UserPlus className="w-3.5 h-3.5" />
            <span>Register Operator</span>
          </button>
        </div>
      </div>

      {/* Alert Banners */}
      {errorMessage && (
        <div className="w-full max-w-sm mx-auto mb-3 p-3 rounded-xl bg-rose-500/15 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {successMessage && (
        <div className="w-full max-w-sm mx-auto mb-3 p-3 rounded-xl bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* SIGN IN FORM                                                  */}
      {/* ------------------------------------------------------------- */}
      {mode === 'signin' && (
        <form onSubmit={handleSignIn} className="w-full max-w-sm mx-auto space-y-4 my-auto">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Operator Email or Badge ID
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="v.sethi@koshalabs.internal"
                className="w-full pl-10 pr-4 py-3 bg-slate-800/90 border border-slate-700 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Security PIN / Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••"
                className="w-full pl-10 pr-11 py-3 bg-slate-800/90 border border-slate-700 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-colors"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 transition-colors"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs pt-1">
            <label className="flex items-center gap-2 cursor-pointer select-none text-slate-300">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="w-4 h-4 rounded bg-slate-800 border-slate-700 text-emerald-500 focus:ring-emerald-500/30"
              />
              <span>Remember terminal</span>
            </label>

            <button
              type="button"
              onClick={handleDemoFill}
              className="text-emerald-400 hover:text-emerald-300 font-medium transition-colors"
            >
              Fill Demo Operator
            </button>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 h-12 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20 active:scale-[0.98] transition-all disabled:opacity-50"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                Authenticating...
              </span>
            ) : (
              <>
                <span>Sign In to Terminal</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>

          <p className="text-center text-xs text-slate-400 pt-1">
            New operator?{' '}
            <button
              type="button"
              onClick={() => handleSwitchMode('signup')}
              className="text-emerald-400 font-semibold hover:underline"
            >
              Create Account
            </button>
          </p>
        </form>
      )}

      {/* ------------------------------------------------------------- */}
      {/* SIGN UP / REGISTER OPERATOR FORM                              */}
      {/* ------------------------------------------------------------- */}
      {mode === 'signup' && (
        <form onSubmit={handleSignUp} className="w-full max-w-sm mx-auto space-y-3.5 my-auto">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Operator Full Name <span className="text-emerald-400">*</span>
            </label>
            <div className="relative">
              <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                value={regName}
                onChange={(e) => setRegName(e.target.value)}
                required
                placeholder="e.g. Arunachalam Murugan"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-800/90 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Operator Work Email <span className="text-emerald-400">*</span>
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="email"
                value={regEmail}
                onChange={(e) => setRegEmail(e.target.value)}
                required
                placeholder="operator@koshalabs.internal"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-800/90 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2.5">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Access Role
              </label>
              <select
                value={regRole}
                onChange={(e) => setRegRole(e.target.value as any)}
                className="w-full px-3 py-2.5 bg-slate-800/90 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
              >
                <option value="operator">Field Operator</option>
                <option value="supervisor">Site Supervisor</option>
                <option value="admin">System Admin</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Assigned Site
              </label>
              <select
                value={regSiteId}
                onChange={(e) => setRegSiteId(e.target.value)}
                className="w-full px-3 py-2.5 bg-slate-800/90 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
              >
                {sites.map((s) => (
                  <option key={s.id} value={s.code}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2.5">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Badge Identifier
              </label>
              <input
                type="text"
                value={regBadge}
                onChange={(e) => setRegBadge(e.target.value)}
                required
                placeholder="KOSHA-OP-101"
                className="w-full px-3 py-2.5 bg-slate-800/90 border border-slate-700 rounded-xl text-xs font-mono text-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                PIN / Password
              </label>
              <input
                type="password"
                value={regPassword}
                onChange={(e) => setRegPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3 py-2.5 bg-slate-800/90 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 h-11 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20 active:scale-[0.98] transition-all disabled:opacity-50"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                Registering in Supabase...
              </span>
            ) : (
              <>
                <UserPlus className="w-4 h-4" />
                <span>Create & Register Operator</span>
              </>
            )}
          </button>

          <p className="text-center text-xs text-slate-400 pt-0.5">
            Already registered?{' '}
            <button
              type="button"
              onClick={() => handleSwitchMode('signin')}
              className="text-emerald-400 font-semibold hover:underline"
            >
              Sign In
            </button>
          </p>
        </form>
      )}

      {/* Footer Info */}
      <div className="text-center text-xs text-slate-500 pb-1 shrink-0">
        <p className="flex items-center justify-center gap-1.5 text-slate-400">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>PostgreSQL Supabase · AES-256 Biometric Security</span>
        </p>
        <p className="text-[10px] text-slate-600 mt-0.5">
          Kosha Labs Enterprise Biometric Mobile Client
        </p>
      </div>
    </div>
  );
};
