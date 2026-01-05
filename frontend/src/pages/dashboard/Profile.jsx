import React, { useState, useEffect } from 'react';
import { showToast } from '../../components/CustomToast';
import { useAuthStore } from '../../store/authStore';
import api from '../../services/api';
import {
  HiUser,
  HiMail,
  HiPhone,
  HiLocationMarker,
  HiCamera,
  HiShieldCheck,
  HiKey,
  HiLogout,
  HiTrash,
  HiSave,
  HiPencil,
  HiCheck,
  HiX,
} from 'react-icons/hi';

const Profile = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const { user, updateUser } = useAuthStore();

  const [profile, setProfile] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    company: '',
    role: '',
    location: '',
    timezone: 'America/Toronto',
    avatar: null,
  });

  // Load user data on component mount
  useEffect(() => {
    const loadUserData = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/auth/me');
        const userData = response.data;

        // Parse full_name into firstName and lastName
        const nameParts = (userData.full_name || '').split(' ');
        const firstName = nameParts[0] || '';
        const lastName = nameParts.slice(1).join(' ') || '';

        setProfile({
          firstName,
          lastName,
          email: userData.email || '',
          phone: userData.phone || '',
          company: userData.company || '',
          role: userData.role || '',
          location: userData.location || '',
          timezone: userData.timezone || 'America/Toronto',
          avatar: null,
        });
      } catch (error) {
        console.error('Failed to load user data:', error);
        showToast('Failed to load user data', 'error');
      } finally {
        setIsLoading(false);
      }
    };

    loadUserData();
  }, []);

  const [passwords, setPasswords] = useState({
    current: '',
    new: '',
    confirm: '',
  });

  const [sessions] = useState([
    { id: 1, device: 'Chrome on Windows', location: 'Toronto, Canada', lastActive: 'Now', current: true },
    { id: 2, device: 'Safari on iPhone', location: 'Toronto, Canada', lastActive: '2 hours ago', current: false },
    { id: 3, device: 'Firefox on MacOS', location: 'Nairobi, Kenya', lastActive: '5 days ago', current: false },
  ]);

  const handleSave = async () => {
    try {
      setIsSaving(true);

      // Prepare the update data
      const updateData = {
        full_name: `${profile.firstName} ${profile.lastName}`.trim(),
        phone: profile.phone || null,
        // Add any other fields your backend supports
      };

      // Send update request to backend
      await api.put('/auth/me', updateData);

      // Update local user state
      updateUser({
        full_name: updateData.full_name,
        firstName: profile.firstName,
        lastName: profile.lastName,
        phone: profile.phone,
      });

      showToast('Profile updated successfully', 'success');
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update profile:', error);
      showToast(error.response?.data?.detail || 'Failed to update profile', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const handleChangePassword = async () => {
    if (passwords.new !== passwords.confirm) {
      showToast('Passwords do not match', 'error');
      return;
    }
    if (passwords.new.length < 8) {
      showToast('Password must be at least 8 characters', 'error');
      return;
    }

    try {
      await api.post('/auth/change-password', {
        current_password: passwords.current,
        new_password: passwords.new,
      });

      showToast('Password changed successfully', 'success');
      setShowChangePassword(false);
      setPasswords({ current: '', new: '', confirm: '' });
    } catch (error) {
      console.error('Failed to change password:', error);
      showToast(error.response?.data?.detail || 'Failed to change password', 'error');
    }
  };

  const handleRevokeSession = (sessionId) => {
    showToast('Session revoked', 'success');
  };

  // Show loading state while fetching user data
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="spinner w-12 h-12"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-display font-bold text-white">Profile</h1>
          <p className="text-slate-400">Manage your account settings and preferences</p>
        </div>
        {isEditing ? (
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsEditing(false)}
              className="btn-ghost flex items-center gap-2 border border-slate-700"
            >
              <HiX className="w-5 h-5" />
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="btn-primary flex items-center gap-2"
            >
              {isSaving ? (
                <>
                  <span className="spinner-small" />
                  Saving...
                </>
              ) : (
                <>
                  <HiSave className="w-5 h-5" />
                  Save Changes
                </>
              )}
            </button>
          </div>
        ) : (
          <button
            onClick={() => setIsEditing(true)}
            className="btn-primary flex items-center gap-2"
          >
            <HiPencil className="w-5 h-5" />
            Edit Profile
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Card */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Info */}
          <div className="card">
            <h2 className="text-lg font-semibold text-white mb-6">Personal Information</h2>

            {/* Avatar */}
            <div className="flex items-center gap-6 mb-6">
              <div className="relative">
                <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-3xl font-bold">
                  {profile.firstName?.[0] || 'U'}{profile.lastName?.[0] || 'N'}
                </div>
                {isEditing && (
                  <button className="absolute -bottom-2 -right-2 w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center text-white shadow-lg">
                    <HiCamera className="w-4 h-4" />
                  </button>
                )}
              </div>
              <div>
                <h3 className="text-xl font-semibold text-white">
                  {profile.firstName} {profile.lastName}
                </h3>
                <p className="text-slate-400">{profile.role} at {profile.company}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">First Name</label>
                <input
                  type="text"
                  value={profile.firstName}
                  onChange={(e) => setProfile({ ...profile, firstName: e.target.value })}
                  disabled={!isEditing}
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Last Name</label>
                <input
                  type="text"
                  value={profile.lastName}
                  onChange={(e) => setProfile({ ...profile, lastName: e.target.value })}
                  disabled={!isEditing}
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Email</label>
                <div className="relative">
                  <HiMail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
                  <input
                    type="email"
                    value={profile.email}
                    onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                    disabled={!isEditing}
                    className="input pl-10"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Phone</label>
                <div className="relative">
                  <HiPhone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
                  <input
                    type="tel"
                    value={profile.phone}
                    onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                    disabled={!isEditing}
                    className="input pl-10"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Company</label>
                <input
                  type="text"
                  value={profile.company}
                  onChange={(e) => setProfile({ ...profile, company: e.target.value })}
                  disabled={!isEditing}
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Role</label>
                <input
                  type="text"
                  value={profile.role}
                  onChange={(e) => setProfile({ ...profile, role: e.target.value })}
                  disabled={!isEditing}
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Location</label>
                <div className="relative">
                  <HiLocationMarker className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
                  <input
                    type="text"
                    value={profile.location}
                    onChange={(e) => setProfile({ ...profile, location: e.target.value })}
                    disabled={!isEditing}
                    className="input pl-10"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Timezone</label>
                <select
                  value={profile.timezone}
                  onChange={(e) => setProfile({ ...profile, timezone: e.target.value })}
                  disabled={!isEditing}
                  className="input"
                >
                  <option value="America/Toronto">Eastern Time (Toronto)</option>
                  <option value="America/New_York">Eastern Time (New York)</option>
                  <option value="America/Los_Angeles">Pacific Time</option>
                  <option value="Africa/Nairobi">East Africa Time</option>
                </select>
              </div>
            </div>
          </div>

          {/* Security */}
          <div className="card">
            <h2 className="text-lg font-semibold text-white mb-6">Security</h2>

            {/* Change Password */}
            {showChangePassword ? (
              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Current Password</label>
                  <input
                    type="password"
                    value={passwords.current}
                    onChange={(e) => setPasswords({ ...passwords, current: e.target.value })}
                    className="input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">New Password</label>
                  <input
                    type="password"
                    value={passwords.new}
                    onChange={(e) => setPasswords({ ...passwords, new: e.target.value })}
                    className="input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Confirm New Password</label>
                  <input
                    type="password"
                    value={passwords.confirm}
                    onChange={(e) => setPasswords({ ...passwords, confirm: e.target.value })}
                    className="input"
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={handleChangePassword}
                    className="btn-primary"
                  >
                    Update Password
                  </button>
                  <button
                    onClick={() => {
                      setShowChangePassword(false);
                      setPasswords({ current: '', new: '', confirm: '' });
                    }}
                    className="btn-ghost border border-slate-700"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <button
                onClick={() => setShowChangePassword(true)}
                className="flex items-center gap-3 w-full p-4 rounded-xl bg-slate-800/50 hover:bg-slate-800 transition-colors text-left mb-4"
              >
                <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
                  <HiKey className="w-5 h-5 text-primary-400" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-white">Change Password</p>
                  <p className="text-sm text-slate-400">Update your password regularly for security</p>
                </div>
              </button>
            )}

            {/* Two-Factor Auth */}
            <div className="flex items-center justify-between p-4 rounded-xl bg-slate-800/50">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                  <HiShieldCheck className="w-5 h-5 text-emerald-400" />
                </div>
                <div>
                  <p className="font-medium text-white">Two-Factor Authentication</p>
                  <p className="text-sm text-slate-400">Extra layer of security for your account</p>
                </div>
              </div>
              <span className="badge bg-emerald-500/20 text-emerald-400">Enabled</span>
            </div>
          </div>

          {/* Active Sessions */}
          <div className="card">
            <h2 className="text-lg font-semibold text-white mb-6">Active Sessions</h2>

            <div className="space-y-3">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  className="flex items-center justify-between p-4 rounded-xl bg-slate-800/50"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      session.current ? 'bg-emerald-500/20' : 'bg-slate-700'
                    }`}>
                      <HiUser className={`w-5 h-5 ${session.current ? 'text-emerald-400' : 'text-slate-400'}`} />
                    </div>
                    <div>
                      <p className="font-medium text-white">{session.device}</p>
                      <p className="text-sm text-slate-400">{session.location} • {session.lastActive}</p>
                    </div>
                  </div>
                  {session.current ? (
                    <span className="badge bg-emerald-500/20 text-emerald-400">Current</span>
                  ) : (
                    <button
                      onClick={() => handleRevokeSession(session.id)}
                      className="text-sm text-red-400 hover:text-red-300"
                    >
                      Revoke
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Account Stats */}
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">Account Stats</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Member since</span>
                <span className="font-medium text-white">Jan 2024</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Plan</span>
                <span className="badge badge-primary">Professional</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">API Calls</span>
                <span className="font-medium text-white">12,450 / 50,000</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Storage Used</span>
                <span className="font-medium text-white">2.4 GB / 10 GB</span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <button className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-slate-800 transition-colors text-left">
                <HiMail className="w-5 h-5 text-slate-400" />
                <span className="text-slate-300">Export Account Data</span>
              </button>
              <button className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-slate-800 transition-colors text-left">
                <HiLogout className="w-5 h-5 text-slate-400" />
                <span className="text-slate-300">Sign Out All Devices</span>
              </button>
              <button className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-red-500/10 transition-colors text-left text-red-400">
                <HiTrash className="w-5 h-5" />
                <span>Delete Account</span>
              </button>
            </div>
          </div>

          {/* Support */}
          <div className="card bg-gradient-to-br from-primary-600/20 to-secondary-600/20 border-primary-500/30">
            <h3 className="text-lg font-semibold text-white mb-2">Need Help?</h3>
            <p className="text-slate-400 text-sm mb-4">
              Our support team is available 24/7 to assist you.
            </p>
            <button className="btn-primary w-full">Contact Support</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
