'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';

interface Channel {
  id: string;
  name: string;
  is_private: boolean;
}

interface Workspace {
  workspace_id: string;
  workspace_name: string;
}

function SetupPageContent() {
  const searchParams = useSearchParams();
  const workspaceId = searchParams.get('workspace_id');
  
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [selectedChannel, setSelectedChannel] = useState<string>('');
  const [standupTime, setStandupTime] = useState<string>('09:00');
  const [timezone, setTimezone] = useState<string>('America/New_York');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<{ type: 'success' | 'error' | 'loading' | null; message: string }>({ type: null, message: '' });

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:4000';

  useEffect(() => {
    if (workspaceId) {
      loadWorkspaceInfo();
      loadChannels();
      loadChannelPreferences();
    }
  }, [workspaceId]);

  const loadWorkspaceInfo = async () => {
    try {
      const response = await fetch(`${backendUrl}/workspaces/${workspaceId}`);
      if (response.ok) {
        const workspace = await response.json();
        setWorkspace(workspace);
      } else {
        setWorkspace({
          workspace_id: workspaceId!,
          workspace_name: 'Your Workspace'
        });
      }
    } catch (error) {
      console.error('Error loading workspace info:', error);
      setWorkspace({
        workspace_id: workspaceId!,
        workspace_name: 'Your Workspace'
      });
    }
  };

  const loadChannels = async () => {
    try {
      setStatus({ type: 'loading', message: 'Loading channels...' });
      
      const response = await fetch(`${backendUrl}/api/channels/${workspaceId}`);
      const data = await response.json();
      
      if (response.ok && data.channels) {
        setChannels(data.channels);
        setStatus({ type: null, message: '' });
      } else {
        setStatus({ type: 'error', message: `Error loading channels: ${data.error || 'Unknown error'}` });
      }
    } catch (error) {
      console.error('Error loading channels:', error);
      setStatus({ type: 'error', message: 'Error loading channels. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const loadChannelPreferences = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/workspace/${workspaceId}/channel`);
      if (response.ok) {
        const data = await response.json();
        if (data.selected_channel) {
          setSelectedChannel(data.selected_channel.id);
          // Load existing preferences if available
          if (data.selected_channel.standup_time) {
            setStandupTime(data.selected_channel.standup_time);
          }
          if (data.selected_channel.timezone) {
            setTimezone(data.selected_channel.timezone);
          }
        }
      }
    } catch (error) {
      console.error('Error loading channel preferences:', error);
    }
  };

  const handleSaveChannel = async () => {
    if (!selectedChannel) {
      setStatus({ type: 'error', message: 'Please select a channel' });
      return;
    }
    
    if (!standupTime) {
      setStatus({ type: 'error', message: 'Please select a standup time' });
      return;
    }
    
    if (!timezone) {
      setStatus({ type: 'error', message: 'Please select a timezone' });
      return;
    }

    try {
      setSaving(true);
      setStatus({ type: 'loading', message: 'Saving channel selection...' });
      
      const selectedChannelData = channels.find(ch => ch.id === selectedChannel);
      
      const response = await fetch(`${backendUrl}/api/channels/${workspaceId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          channel_id: selectedChannel,
          channel_name: selectedChannelData?.name || selectedChannel,
          standup_time: standupTime,
          timezone: timezone
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setStatus({ type: 'success', message: '✅ Channel and schedule saved successfully! Don\'t forget to invite the bot to your channel using /invite @your-bot-name' });
      } else {
        setStatus({ type: 'error', message: `Error saving settings: ${data.error || 'Unknown error'}` });
      }
    } catch (error) {
      console.error('Error saving channel:', error);
      setStatus({ type: 'error', message: 'Error saving channel. Please try again.' });
    } finally {
      setSaving(false);
    }
  };

  if (!workspaceId) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Error</h1>
          <p className="text-gray-600">No workspace ID provided</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white p-8 rounded-lg shadow-md">
            <h1 className="text-3xl font-bold text-gray-900 mb-6 text-center">
              🚀 Setup Your Standup Bot
            </h1>
            
            {/* Workspace Info */}
            <div className="bg-blue-50 p-4 rounded-lg mb-6">
              <div className="text-sm text-gray-600 mb-1">Workspace</div>
              <div className="font-semibold">{workspace?.workspace_name || 'Loading...'}</div>
              <div className="text-sm text-gray-500">ID: {workspaceId}</div>
            </div>

            {/* Channel Selection */}
            <div className="mb-6">
              <label htmlFor="channel-select" className="block text-sm font-medium text-gray-700 mb-2">
                Select Channel for Standup Summaries
              </label>
              <select
                id="channel-select"
                value={selectedChannel}
                onChange={(e) => setSelectedChannel(e.target.value)}
                disabled={loading}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
              >
                <option value="">
                  {loading ? 'Loading channels...' : 'Select a channel...'}
                </option>
                {channels.map((channel) => (
                  <option key={channel.id} value={channel.id}>
                    #{channel.name}{channel.is_private ? ' (private)' : ''}
                  </option>
                ))}
              </select>
            </div>

            {/* Standup Time Selection */}
            <div className="mb-6">
              <label htmlFor="standup-time" className="block text-sm font-medium text-gray-700 mb-2">
                Daily Standup Time
              </label>
              <input
                type="time"
                id="standup-time"
                value={standupTime}
                onChange={(e) => setStandupTime(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="text-sm text-gray-500 mt-1">When should the bot start collecting standup responses?</p>
            </div>

            {/* Timezone Selection */}
            <div className="mb-6">
              <label htmlFor="timezone-select" className="block text-sm font-medium text-gray-700 mb-2">
                Timezone
              </label>
              <select
                id="timezone-select"
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="America/New_York">Eastern Time (ET)</option>
                <option value="America/Chicago">Central Time (CT)</option>
                <option value="America/Denver">Mountain Time (MT)</option>
                <option value="America/Los_Angeles">Pacific Time (PT)</option>
                <option value="Europe/London">London (GMT/BST)</option>
                <option value="Europe/Paris">Paris (CET/CEST)</option>
                <option value="Asia/Tokyo">Tokyo (JST)</option>
                <option value="Asia/Kolkata">India (IST)</option>
                <option value="Australia/Sydney">Sydney (AEST/AEDT)</option>
                <option value="UTC">UTC</option>
              </select>
              <p className="text-sm text-gray-500 mt-1">Timezone for the standup time above</p>
            </div>

            {/* Save Button */}
            <button
              onClick={handleSaveChannel}
              disabled={!selectedChannel || !standupTime || !timezone || saving}
              className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
            >
              {saving ? 'Saving...' : 'Save Channel & Schedule'}
            </button>

            {/* Status Message */}
            {status.type && (
              <div className={`mt-4 p-4 rounded-lg ${
                status.type === 'success' ? 'bg-green-100 text-green-800 border border-green-200' :
                status.type === 'error' ? 'bg-red-100 text-red-800 border border-red-200' :
                'bg-blue-100 text-blue-800 border border-blue-200'
              }`}>
                {status.message}
              </div>
            )}

            {/* Important: Invite Bot to Channel */}
            {selectedChannel && (
              <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h3 className="font-semibold mb-2 text-yellow-800 flex items-center">
                  <span className="mr-2">⚠️</span>
                  Important: Invite Bot to Channel
                </h3>
                <p className="text-sm text-yellow-700 mb-3">
                  Before the bot can post summaries, you need to invite it to the selected channel.
                </p>
                <div className="bg-white p-3 rounded border border-yellow-300">
                  <p className="text-sm font-mono text-gray-800">
                    Go to <strong>#{channels.find(ch => ch.id === selectedChannel)?.name}</strong> in Slack and type:
                  </p>
                  <div className="mt-2 p-2 bg-gray-100 rounded font-mono text-sm">
                    /invite @your-bot-name
                  </div>
                </div>
              </div>
            )}

            {/* Instructions */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold mb-2">What happens next?</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• <strong>First:</strong> Invite the bot to your selected channel using <code className="bg-gray-200 px-1 rounded">/invite @your-bot-name</code></li>
                <li>• The bot will send DMs to your team members for standup responses</li>
                <li>• After collecting responses, it will generate an AI summary</li>
                <li>• The summary will be posted to the selected channel</li>
                <li>• You can trigger standups manually or set up automated schedules</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function SetupPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <SetupPageContent />
    </Suspense>
  );
}
