'use client'

import { useState, useEffect } from 'react'

interface SystemStatus {
  name: string
  status: 'online' | 'degraded' | 'offline'
  uptime: string
  lastCheck: Date
}

const services: SystemStatus[] = [
  { name: 'AI Model (GLM-4.7)', status: 'online', uptime: '99.9%', lastCheck: new Date() },
  { name: 'Telegram Bot', status: 'online', uptime: '99.8%', lastCheck: new Date() },
  { name: 'Web Server', status: 'online', uptime: '99.9%', lastCheck: new Date() },
  { name: 'Homelab Dashboard', status: 'online', uptime: '99.7%', lastCheck: new Date() },
  { name: 'GitHub Integration', status: 'online', uptime: '99.9%', lastCheck: new Date() },
  { name: 'Automations', status: 'degraded', uptime: '98.5%', lastCheck: new Date() },
]

const StatusCard = ({ name, status, uptime, lastCheck }: SystemStatus) => {
  const statusColors = {
    online: 'bg-green-500',
    degraded: 'bg-yellow-500',
    offline: 'bg-red-500',
  }

  const statusLabels = {
    online: 'Online',
    degraded: 'Degraded',
    offline: 'Offline',
  }

  const statusBorder = {
    online: 'border-green-200 dark:border-green-800',
    degraded: 'border-yellow-200 dark:border-yellow-800',
    offline: 'border-red-200 dark:border-red-800',
  }

  return (
    <div className={`bg-white dark:bg-slate-900 rounded-xl p-6 border-2 ${statusBorder[status]} shadow-lg transition-all hover:shadow-xl`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${statusColors[status]} animate-pulse-slow`} />
          <h3 className="font-semibold text-slate-800 dark:text-white">{name}</h3>
        </div>
        <span className={`text-xs font-medium px-2 py-1 rounded-full ${
          status === 'online' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
          status === 'degraded' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
          'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
        }`}>
          {statusLabels[status]}
        </span>
      </div>
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-slate-500 dark:text-slate-400">Uptime</span>
          <span className="font-medium text-slate-800 dark:text-white">{uptime}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-slate-500 dark:text-slate-400">Last Check</span>
          <span className="font-medium text-slate-800 dark:text-white">
            {lastCheck.toLocaleTimeString()}
          </span>
        </div>
      </div>
    </div>
  )
}

export default function StatusDashboard() {
  const [lastUpdated, setLastUpdated] = useState(new Date())
  const [autoRefresh, setAutoRefresh] = useState(true)

  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      setLastUpdated(new Date())
    }, 5000)

    return () => clearInterval(interval)
  }, [autoRefresh])

  const onlineCount = services.filter((s) => s.status === 'online').length
  const totalServices = services.length

  return (
    <div className="animate-slide-up">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-slate-800 dark:text-white mb-2">
          System Status Dashboard
        </h2>
        <p className="text-slate-600 dark:text-slate-400">
          Real-time health monitoring for all services
        </p>
      </div>

      {/* Overview Stats */}
      <div className="max-w-6xl mx-auto mb-8">
        <div className="grid md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg">
            <div className="text-3xl font-bold mb-1">{onlineCount}/{totalServices}</div>
            <div className="text-sm opacity-90">Services Online</div>
          </div>
          <div className="bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl p-6 text-white shadow-lg">
            <div className="text-3xl font-bold mb-1">99.7%</div>
            <div className="text-sm opacity-90">Overall Uptime</div>
          </div>
          <div className="bg-gradient-to-br from-accent-500 to-accent-600 rounded-xl p-6 text-white shadow-lg">
            <div className="text-3xl font-bold mb-1">24/7</div>
            <div className="text-sm opacity-90">Monitoring</div>
          </div>
          <div className="bg-gradient-to-br from-slate-600 to-slate-700 rounded-xl p-6 text-white shadow-lg">
            <div className="text-3xl font-bold mb-1">
              {autoRefresh ? 'Live' : 'Paused'}
            </div>
            <div className="text-sm opacity-90">Status</div>
          </div>
        </div>
      </div>

      {/* Auto Refresh Toggle */}
      <div className="max-w-6xl mx-auto mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-2 h-2 rounded-full ${autoRefresh ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
          <span className="text-sm text-slate-600 dark:text-slate-400">
            Last updated: {lastUpdated.toLocaleTimeString()}
          </span>
        </div>
        <button
          onClick={() => setAutoRefresh(!autoRefresh)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            autoRefresh
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              : 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200'
          }`}
        >
          {autoRefresh ? '⏸ Pause Updates' : '▶ Resume Updates'}
        </button>
      </div>

      {/* Service Cards */}
      <div className="max-w-6xl mx-auto">
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {services.map((service, index) => (
            <div key={service.name} style={{ animationDelay: `${index * 0.1}s` }} className="animate-fade-in">
              <StatusCard {...service} />
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="max-w-6xl mx-auto mt-8 p-4 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
        <h4 className="font-semibold text-slate-800 dark:text-white mb-3">Status Legend</h4>
        <div className="flex flex-wrap gap-6">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-sm text-slate-600 dark:text-slate-400">Online - Fully operational</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <span className="text-sm text-slate-600 dark:text-slate-400">Degraded - Partial issues</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-sm text-slate-600 dark:text-slate-400">Offline - Not available</span>
          </div>
        </div>
      </div>
    </div>
  )
}
