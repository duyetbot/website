'use client'

import { useState, useEffect } from 'react'
import ChatDemo from '@/components/ChatDemo'
import StatusDashboard from '@/components/StatusDashboard'
import FeatureComparison from '@/components/FeatureComparison'
import ConfigPreview from '@/components/ConfigPreview'
import FeedbackForm from '@/components/FeedbackForm'
import Testimonials from '@/components/Testimonials'

export default function Home() {
  const [activeTab, setActiveTab] = useState('playground')

  const tabs = [
    { id: 'playground', label: '🎮 Playground', icon: '🎮' },
    { id: 'status', label: '📊 Status', icon: '📊' },
    { id: 'features', label: '⚡ Features', icon: '⚡' },
    { id: 'config', label: '⚙️ Config', icon: '⚙️' },
    { id: 'feedback', label: '💬 Feedback', icon: '💬' },
  ]

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <header className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-lg border-b border-slate-200 dark:border-slate-700 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-lg">
                DB
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-800 dark:text-white">duyetbot</h1>
                <p className="text-xs text-slate-500 dark:text-slate-400">Interactive Features</p>
              </div>
            </div>
            <a
              href="https://bot.duyet.net"
              className="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors"
            >
              ← Back to Main Site
            </a>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
        <div className="container mx-auto px-4">
          <div className="flex overflow-x-auto gap-1 py-2 scrollbar-hide">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm whitespace-nowrap transition-all
                  ${
                    activeTab === tab.id
                      ? 'bg-primary-500 text-white shadow-md'
                      : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }
                `}
              >
                <span className="text-lg">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="animate-fade-in">
          {activeTab === 'playground' && <ChatDemo />}
          {activeTab === 'status' && <StatusDashboard />}
          {activeTab === 'features' && <FeatureComparison />}
          {activeTab === 'config' && <ConfigPreview />}
          {activeTab === 'feedback' && (
            <div className="grid lg:grid-cols-2 gap-8">
              <FeedbackForm />
              <Testimonials />
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-700 mt-12">
        <div className="container mx-auto px-4 py-6">
          <p className="text-center text-sm text-slate-500 dark:text-slate-400">
            Built with Next.js, React, and Tailwind CSS •{' '}
            <a href="https://github.com/duyetbot" className="hover:text-primary-500 transition-colors">
              GitHub
            </a>
          </p>
        </div>
      </footer>
    </main>
  )
}
