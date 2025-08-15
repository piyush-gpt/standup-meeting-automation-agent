"use client";

export default function Home() {
  const handleInstall = () => {
    // Redirect to the Slack install endpoint
    window.location.href = `${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:4000'}/slack/install`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          {/* Header */}
          <div className="mb-12">
            <h1 className="text-5xl font-bold text-gray-900 mb-6">
              🚀 Standup Bot
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Automate your daily standups with AI-powered summaries. 
              Collect responses from your team and get intelligent summaries posted to your chosen channel.
            </p>
          </div>

          {/* Features */}
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-3xl mb-4">🤖</div>
              <h3 className="text-lg font-semibold mb-2">AI-Powered Summaries</h3>
              <p className="text-gray-600">Get intelligent summaries of your team's standup responses</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-3xl mb-4">⏰</div>
              <h3 className="text-lg font-semibold mb-2">Automated Workflow</h3>
              <p className="text-gray-600">Set up once and let the bot handle the rest automatically</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-3xl mb-4">📊</div>
              <h3 className="text-lg font-semibold mb-2">Channel Integration</h3>
              <p className="text-gray-600">Post summaries to any channel of your choice</p>
            </div>
          </div>

          {/* Install Button */}
          <div className="mb-12">
            <button
              onClick={handleInstall}
              className="bg-green-600 hover:bg-green-700 text-white font-semibold py-4 px-8 rounded-lg text-lg shadow-lg transform transition-all duration-200 hover:scale-105"
            >
              <span className="flex items-center justify-center">
                <svg className="w-6 h-6 mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M6 15a2 2 0 1 1 0-4 2 2 0 0 1 0 4zm0-6a2 2 0 1 1 0-4 2 2 0 0 1 0 4zm6 0a2 2 0 1 1 0-4 2 2 0 0 1 0 4zm6 0a2 2 0 1 1 0-4 2 2 0 0 1 0 4zm-6 6a2 2 0 1 1 0-4 2 2 0 0 1 0 4zm6 0a2 2 0 1 1 0-4 2 2 0 0 1 0 4z"/>
                </svg>
                Install to Slack
              </span>
            </button>
          </div>

          {/* How it works */}
          <div className="bg-white p-8 rounded-lg shadow-md">
            <h2 className="text-2xl font-bold mb-6">How it works</h2>
            <div className="grid md:grid-cols-4 gap-6 text-center">
              <div>
                <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-blue-600 font-bold">1</span>
                </div>
                <h4 className="font-semibold mb-2">Install</h4>
                <p className="text-sm text-gray-600">Add the bot to your Slack workspace</p>
              </div>
              <div>
                <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-blue-600 font-bold">2</span>
                </div>
                <h4 className="font-semibold mb-2">Configure</h4>
                <p className="text-sm text-gray-600">Select a channel for summaries</p>
              </div>
              <div>
                <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-blue-600 font-bold">3</span>
                </div>
                <h4 className="font-semibold mb-2">Collect</h4>
                <p className="text-sm text-gray-600">Bot sends DMs to team members</p>
              </div>
              <div>
                <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-blue-600 font-bold">4</span>
                </div>
                <h4 className="font-semibold mb-2">Summarize</h4>
                <p className="text-sm text-gray-600">AI generates and posts summary</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
