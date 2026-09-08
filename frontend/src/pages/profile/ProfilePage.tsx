import React, { useState } from 'react';
import { User, Mail, Shield, CheckCircle, Save, KeyRound } from 'lucide-react';
import { useAuthStore } from '@/store/useAuthStore';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

export const ProfilePage: React.FC = () => {
  const { user, setUser } = useAuthStore();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [username, setUsername] = useState(user?.username || '');
  const [isSaved, setIsSaved] = useState(false);
  const [activeTab, setActiveTab] = useState<'details' | 'security'>('details');

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    if (user) {
      setUser({
        ...user,
        full_name: fullName,
        username: username,
      });
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 3000);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Profile Management</h2>
        <p className="text-sm text-slate-400">
          Manage your personal information, role permissions, and security settings.
        </p>
      </div>

      {/* User Summary Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 shadow-xl">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold text-2xl">
            {user?.email ? user.email.charAt(0).toUpperCase() : 'U'}
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h3 className="text-lg font-semibold text-white">
                {user?.full_name || user?.username || user?.email || 'Authenticated User'}
              </h3>
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 capitalize">
                {user?.role || 'user'}
              </span>
            </div>
            <p className="text-sm text-slate-400 flex items-center gap-1.5 mt-0.5">
              <Mail className="w-3.5 h-3.5" />
              {user?.email || 'user@company.com'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle className="w-3.5 h-3.5" />
            Active Account
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-800 flex gap-6">
        <button
          onClick={() => setActiveTab('details')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 ${
            activeTab === 'details'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Account Details
        </button>
        <button
          onClick={() => setActiveTab('security')}
          className={`pb-3 text-sm font-medium transition-colors border-b-2 ${
            activeTab === 'security'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Security & Roles
        </button>
      </div>

      {activeTab === 'details' ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6">
          {isSaved && (
            <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/30 p-3.5 flex items-center gap-2.5 text-emerald-300 text-sm">
              <CheckCircle className="w-4 h-4" />
              Profile updated successfully.
            </div>
          )}

          <form onSubmit={handleSaveProfile} className="space-y-4 max-w-xl">
            <Input
              label="Email Address"
              type="email"
              value={user?.email || ''}
              disabled
              helperText="Email cannot be changed directly."
              icon={<Mail className="w-4 h-4" />}
            />

            <Input
              label="Full Name"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Your full name"
              icon={<User className="w-4 h-4" />}
            />

            <Input
              label="Username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Your username"
              icon={<User className="w-4 h-4" />}
            />

            <Button
              type="submit"
              className="mt-2"
              icon={<Save className="w-4 h-4 mr-1.5" />}
            >
              Save Changes
            </Button>
          </form>
        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6">
          <div>
            <h4 className="text-base font-semibold text-white">Role & Permissions</h4>
            <p className="text-xs text-slate-400 mt-1">
              Your account role determines access to AI marketing tools and campaign publishing.
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-950 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-indigo-400" />
                <span className="text-sm font-medium text-slate-200">Current Role</span>
              </div>
              <span className="text-xs font-semibold uppercase px-2.5 py-1 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                {user?.role || 'user'}
              </span>
            </div>
            <p className="text-xs text-slate-400">
              {user?.role === 'admin'
                ? 'Full system privileges: campaign creation, agent configuration, user management.'
                : user?.role === 'manager'
                ? 'Manager privileges: create campaigns, execute AI workflows, view analytics.'
                : 'Standard privileges: view campaigns and interact with marketing assistant.'}
            </p>
          </div>

          <div className="border-t border-slate-800 pt-6">
            <h4 className="text-base font-semibold text-white">Password & Authentication</h4>
            <p className="text-xs text-slate-400 mt-1">
              Manage your password or request a secure reset.
            </p>

            <div className="mt-4">
              <a
                href="/forgot-password"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-sm font-medium transition-colors"
              >
                <KeyRound className="w-4 h-4 text-indigo-400" />
                Request Password Reset Token
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;
