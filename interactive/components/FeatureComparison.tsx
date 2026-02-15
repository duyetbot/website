'use client'

import { useState } from 'react'

interface Feature {
  name: string
  main: '✓' | '○' | '×'
  complex: '✓' | '○' | '×'
  description: string
}

const features: Feature[] = [
  { name: 'General Chat', main: '✓', complex: '✓', description: 'Conversational assistance and Q&A' },
  { name: 'Code Generation', main: '✓', complex: '✓', description: 'Write, debug, and review code' },
  { name: 'Web Browsing', main: '✓', complex: '✓', description: 'Browse and interact with websites' },
  { name: 'File Operations', main: '✓', complex: '✓', description: 'Read, write, and manage files' },
  { name: 'Complex Debugging', main: '○', complex: '✓', description: 'Deep code analysis and bug fixes' },
  { name: 'Architecture Design', main: '○', complex: '✓', description: 'System architecture and patterns' },
  { name: 'Performance Optimization', main: '○', complex: '✓', description: 'Code and database optimization' },
  { name: 'Quick Tasks', main: '✓', complex: '×', description: 'Fast responses and simple queries' },
]

const models = [
  {
    id: 'main',
    name: 'Main Agent (GLM-4.7)',
    description: 'General-purpose AI assistant for everyday tasks',
    color: 'from-primary-500 to-primary-600',
    icon: '🤖',
  },
  {
    id: 'complex',
    name: 'Complex Agent (@complex)',
    description: 'Specialized agent for technical challenges',
    color: 'from-accent-500 to-accent-600',
    icon: '⚙️',
  },
]

export default function FeatureComparison() {
  const [selectedFeature, setSelectedFeature] = useState<Feature | null>(null)

  const getFeatureClass = (value: string) => {
    if (value === '✓') return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
    if (value === '○') return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
    return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
  }

  return (
    <div className="animate-slide-up">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-slate-800 dark:text-white mb-2">
          Feature Comparison
        </h2>
        <p className="text-slate-600 dark:text-slate-400">
          Compare capabilities between main and specialized agents
        </p>
      </div>

      {/* Model Cards */}
      <div className="max-w-5xl mx-auto mb-8 grid md:grid-cols-2 gap-6">
        {models.map((model) => (
          <div
            key={model.id}
            className="bg-white dark:bg-slate-900 rounded-2xl shadow-lg overflow-hidden border border-slate-200 dark:border-slate-700"
          >
            <div className={`bg-gradient-to-r ${model.color} p-6 text-white`}>
              <div className="flex items-center gap-3 mb-2">
                <span className="text-3xl">{model.icon}</span>
                <h3 className="text-xl font-bold">{model.name}</h3>
              </div>
              <p className="text-sm opacity-90">{model.description}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Comparison Table */}
      <div className="max-w-5xl mx-auto">
        <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-xl overflow-hidden border border-slate-200 dark:border-slate-700">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gradient-to-r from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-800">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-800 dark:text-white">
                    Feature
                  </th>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-slate-800 dark:text-white">
                    Main Agent
                  </th>
                  <th className="px-6 py-4 text-center text-sm font-semibold text-slate-800 dark:text-white">
                    Complex Agent
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-800 dark:text-white">
                    Description
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                {features.map((feature) => (
                  <tr
                    key={feature.name}
                    className={`transition-colors ${
                      selectedFeature?.name === feature.name
                        ? 'bg-blue-50 dark:bg-blue-900/20'
                        : 'hover:bg-slate-50 dark:hover:bg-slate-800'
                    }`}
                    onClick={() => setSelectedFeature(feature)}
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        {feature.name}
                        {selectedFeature?.name === feature.name && (
                          <span className="text-primary-500">←</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span
                        className={`inline-block w-8 h-8 rounded-full ${getFeatureClass(
                          feature.main
                        )} font-semibold`}
                      >
                        {feature.main}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span
                        className={`inline-block w-8 h-8 rounded-full ${getFeatureClass(
                          feature.complex
                        )} font-semibold`}
                      >
                        {feature.complex}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">
                      {feature.description}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Feature Detail Panel */}
      {selectedFeature && (
        <div className="max-w-5xl mx-auto mt-6 animate-fade-in">
          <div className="bg-gradient-to-r from-primary-50 to-accent-50 dark:from-primary-900/20 dark:to-accent-900/20 rounded-xl p-6 border border-primary-200 dark:border-primary-800">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-bold text-lg text-slate-800 dark:text-white mb-2">
                  {selectedFeature.name}
                </h3>
                <p className="text-slate-600 dark:text-slate-400">
                  {selectedFeature.description}
                </p>
                <div className="mt-4 flex flex-wrap gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <span className="text-slate-500">Main Agent:</span>
                    <span
                      className={`px-2 py-1 rounded ${getFeatureClass(
                        selectedFeature.main
                      )}`}
                    >
                      {selectedFeature.main === '✓'
                        ? 'Supported'
                        : selectedFeature.main === '○'
                        ? 'Partial'
                        : 'Not Supported'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-500">Complex Agent:</span>
                    <span
                      className={`px-2 py-1 rounded ${getFeatureClass(
                        selectedFeature.complex
                      )}`}
                    >
                      {selectedFeature.complex === '✓'
                        ? 'Supported'
                        : selectedFeature.complex === '○'
                        ? 'Partial'
                        : 'Not Supported'}
                    </span>
                  </div>
                </div>
              </div>
              <button
                onClick={() => setSelectedFeature(null)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
              >
                ✕
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Usage Tips */}
      <div className="max-w-5xl mx-auto mt-8 p-6 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
        <h4 className="font-semibold text-slate-800 dark:text-white mb-3">
          💡 Usage Tips
        </h4>
        <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
          <li className="flex items-start gap-2">
            <span className="text-primary-500 mt-0.5">•</span>
            <span>
              Use the <strong>main agent</strong> for quick questions, general
              assistance, and everyday tasks
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-accent-500 mt-0.5">•</span>
            <span>
              Mention <code>@complex</code> for code debugging, architecture
              design, and performance optimization tasks
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary-500 mt-0.5">•</span>
            <span>
              The bot will automatically route to the appropriate agent based
              on your request context
            </span>
          </li>
        </ul>
      </div>
    </div>
  )
}
