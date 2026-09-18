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
    <div className="max-w-4xl mx-auto space-y-8 text-[#18181B]">
      {/* Header */}
      <div>
        <h2 className="text-3xl sm:text-4xl font-serif tracking-tight text-[#18181B]">Profile Management</h2>
        <p className="text-sm text-[#71717A] mt-1">
          Manage your personal information, role permissions, and security settings.
        </p>
      </div>

      {/* User Summary Card */}
      <div className="bg-white border border-[#E8E8E3] rounded-2xl p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 shadow-xs">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-[#18181B] text-white flex items-center justify-center font-bold text-2xl shadow-xs">
            {user?.email ? user.email.charAt(0).toUpperCase() : 'U'}
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h3 className="text-lg font-bold text-[#18181B]">
                {user?.full_name || user?.username || user?.email || 'Authenticated User'}
              </h3>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono uppercase font-semibold bg-[#F3F3EE] text-[#52525B] border border-[#E4E4DC]">
                {user?.role || 'user'}
              </span>
            </div>
            <p className="text-xs text-[#71717A] flex items-center gap-1.5 mt-0.5">
              <Mail className="w-3.5 h-3.5 text-[#A1A1AA]" />
              {user?.email || 'user@company.com'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-mono uppercase font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle className="w-3 h-3 text-emerald-600" />
            Active Account
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-[#E8E8E3] flex gap-6">
        <button
          onClick={() => setActiveTab('details')}
          className={`pb-3 text-xs sm:text-sm font-semibold transition-all border-b-2 ${
            activeTab === 'details'
              ? 'border-[#18181B] text-[#18181B]'
              : 'border-transparent text-[#71717A] hover:text-[#18181B]'
          }`}
        >
          Account Details
        </button>
        <button
          onClick={() => setActiveTab('security')}
          className={`pb-3 text-xs sm:text-sm font-semibold transition-all border-b-2 ${
            activeTab === 'security'
              ? 'border-[#18181B] text-[#18181B]'
              : 'border-transparent text-[#71717A] hover:text-[#18181B]'
          }`}
        >
          Security &amp; Roles
        </button>
      </div>

      {activeTab === 'details' ? (
        <div className="bg-white border border-[#E8E8E3] rounded-2xl p-6 sm:p-8 space-y-6 shadow-xs">
          {isSaved && (
            <div className="rounded-xl bg-emerald-50 border border-emerald-200 p-3.5 flex items-center gap-2.5 text-emerald-800 text-xs font-semibold shadow-xs">
              <CheckCircle className="w-4 h-4 text-emerald-600" />
              Profile updated successfully.
            </div>
          )}

          <form onSubmit={handleSaveProfile} className="space-y-4 max-w-xl">
            <Input
              label="User ID"
              type="text"
              value={user?.id?.toString() || ''}
              disabled
              helperText="System-generated account identifier."
              icon={<Shield className="w-4 h-4" />}
            />

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
              icon={<Save className="w-4 h-4 text-amber-400 mr-1.5" />}
            >
              Save Changes
            </Button>
          </form>
        </div>
      ) : (
        <div className="bg-white border border-[#E8E8E3] rounded-2xl p-6 sm:p-8 space-y-6 shadow-xs">
          <div>
            <h4 className="text-base font-bold text-[#18181B]">Role &amp; Permissions</h4>
            <p className="text-xs text-[#71717A] mt-1">
              Your account role determines access to AI marketing tools and campaign publishing.
            </p>
          </div>

          <div className="rounded-xl border border-[#E8E8E3] bg-[#F8F8F6] p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-[#18181B]" />
                <span className="text-xs font-bold text-[#18181B]">Current Role</span>
              </div>
              <span className="text-[10px] font-mono uppercase font-semibold px-2.5 py-1 rounded bg-white text-[#18181B] border border-[#E4E4DC]">
                {user?.role || 'user'}
              </span>
            </div>
            <p className="text-xs text-[#71717A] leading-relaxed">
              {user?.role === 'admin'
                ? 'Full system privileges: campaign creation, agent configuration, user management.'
                : user?.role === 'manager'
                ? 'Manager privileges: create campaigns, execute AI workflows, view analytics.'
                : 'Standard privileges: view campaigns and interact with marketing assistant.'}
            </p>
          </div>

          <div className="border-t border-[#F2F2ED] pt-6">
            <h4 className="text-base font-bold text-[#18181B]">Password &amp; Authentication</h4>
            <p className="text-xs text-[#71717A] mt-1">
              Manage your password or request a secure reset.
            </p>

            <div className="mt-4">
              <a
                href="/forgot-password"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white hover:bg-[#F3F3EE] text-[#18181B] border border-[#E4E4DC] text-xs font-semibold shadow-xs transition-colors"
              >
                <KeyRound className="w-4 h-4 text-[#71717A]" />
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
