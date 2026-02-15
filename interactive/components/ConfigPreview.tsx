'use client'

import { useState } from 'react'

interface Config {
  model: string
  temperature: number
  maxTokens: number
  streaming: boolean
  thinking: boolean
  agentRouting: boolean
}

export default function ConfigPreview() {
  const [config, setConfig] = useState<Config>({
    model: 'zai/glm-4.7',
    temperature: 0.7,
    maxTokens: 4096,
    streaming: true,
    thinking: false,
    agentRouting: true,
  })

  const models = [
    'zai/glm-4.7',
    'zai/glm-4.7-flash',
    'zai/glm-4.7-reasoning',
  ]

  const toggleSetting = (key: keyof Config) => {
    setConfig((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  const generateConfigPreview = () => {
    return {
      agent: 'main',
      model: config.model,
      parameters: {
        temperature: config.temperature,
        max_tokens: config.maxTokens,
      },
      capabilities: {
        streaming: config.streaming,
        thinking: config.thinking,
        agent_routing: config.agentRouting,
      },
      runtime: {
        host: 'openclaw',
        node: 'v22.22.0',
        shell: 'bash',
      },
    }
  }

  return (
    <div className="animate-slide-up">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-slate-800 dark:text-white mb-2">
          Configuration Preview
        </h2>
        <p className="text-slate-600 dark:text-slate-400">
          Interactive preview of bot configuration settings
        </p>
      </div>

      <div className="max-w-6xl mx-auto grid lg:grid-cols-2 gap-8">
        {/* Configuration Panel */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700 p-6">
          <h3 className="text-xl font-bold text-slate-800 dark:text-white mb-6">
            Settings
          </h3>

          {/* Model Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              AI Model
            </label>
            <select
              value={config.model}
              onChange={(e) => setConfig({ ...config, model: e.target.value })}
              className="w-full px-4 py-3 bg-slate-100 dark:bg-slate-800 border-2 border-transparent rounded-xl focus:border-primary-500 focus:outline-none text-slate-800 dark:text-white"
            >
              {models.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
          </div>

          {/* Temperature Slider */}
          <div className="mb-6">
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
                Temperature
              </label>
              <span className="text-sm text-primary-600 dark:text-primary-400 font-semibold">
                {config.temperature.toFixed(1)}
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={config.temperature}
              onChange={(e) =>
                setConfig({ ...config, temperature: parseFloat(e.target.value) })
              }
              className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-primary-500"
            />
            <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400 mt-1">
              <span>Precise (0.0)</span>
              <span>Balanced (1.0)</span>
              <span>Creative (2.0)</span>
            </div>
          </div>

          {/* Max Tokens Slider */}
          <div className="mb-6">
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
                Max Tokens
              </label>
              <span className="text-sm text-primary-600 dark:text-primary-400 font-semibold">
                {config.maxTokens}
              </span>
            </div>
            <input
              type="range"
              min="512"
              max="8192"
              step="512"
              value={config.maxTokens}
              onChange={(e) =>
                setConfig({ ...config, maxTokens: parseInt(e.target.value) })
              }
              className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-primary-500"
            />
            <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400 mt-1">
              <span>512</span>
              <span>4096</span>
              <span>8192</span>
            </div>
          </div>

          {/* Toggle Switches */}
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800 rounded-xl">
              <div>
                <h4 className="font-medium text-slate-800 dark:text-white">
                  Streaming
                </h4>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Stream responses in real-time
                </p>
              </div>
              <button
                onClick={() => toggleSetting('streaming')}
                className={`w-14 h-8 rounded-full relative transition-colors ${
                  config.streaming
                    ? 'bg-primary-500'
                    : 'bg-slate-300 dark:bg-slate-600'
                }`}
              >
                <span
                  className={`absolute top-1 w-6 h-6 bg-white rounded-full shadow-md transition-transform ${
                    config.streaming ? 'translate-x-7' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800 rounded-xl">
              <div>
                <h4 className="font-medium text-slate-800 dark:text-white">
                  Thinking Mode
                </h4>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Show reasoning process
                </p>
              </div>
              <button
                onClick={() => toggleSetting('thinking')}
                className={`w-14 h-8 rounded-full relative transition-colors ${
                  config.thinking
                    ? 'bg-accent-500'
                    : 'bg-slate-300 dark:bg-slate-600'
                }`}
              >
                <span
                  className={`absolute top-1 w-6 h-6 bg-white rounded-full shadow-md transition-transform ${
                    config.thinking ? 'translate-x-7' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800 rounded-xl">
              <div>
                <h4 className="font-medium text-slate-800 dark:text-white">
                  Agent Routing
                </h4>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Auto-route to specialized agents
                </p>
              </div>
              <button
                onClick={() => toggleSetting('agentRouting')}
                className={`w-14 h-8 rounded-full relative transition-colors ${
                  config.agentRouting
                    ? 'bg-green-500'
                    : 'bg-slate-300 dark:bg-slate-600'
                }`}
              >
                <span
                  className={`absolute top-1 w-6 h-6 bg-white rounded-full shadow-md transition-transform ${
                    config.agentRouting ? 'translate-x-7' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* Preview Panel */}
        <div className="bg-slate-900 rounded-2xl shadow-lg border border-slate-700 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white">Config Preview</h3>
            <div className="flex gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <div className="w-3 h-3 rounded-full bg-green-500" />
            </div>
          </div>
          <pre className="text-sm text-green-400 overflow-x-auto">
            <code>{JSON.stringify(generateConfigPreview(), null, 2)}</code>
          </pre>

          <div className="mt-6 p-4 bg-slate-800 rounded-xl">
            <h4 className="font-semibold text-white mb-2">Usage Command</h4>
            <code className="text-sm text-primary-400 block overflow-x-auto">
              agent=main | model={config.model} | temp={config.temperature} |
              tokens={config.maxTokens}
            </code>
          </div>

          <div className="mt-4 p-4 bg-slate-800 rounded-xl">
            <h4 className="font-semibold text-white mb-2">Environment</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-slate-400">Host:</span>{' '}
                <span className="text-white">openclaw</span>
              </div>
              <div>
                <span className="text-slate-400">Node:</span>{' '}
                <span className="text-white">v22.22.0</span>
              </div>
              <div>
                <span className="text-slate-400">Shell:</span>{' '}
                <span className="text-white">bash</span>
              </div>
              <div>
                <span className="text-slate-400">Channel:</span>{' '}
                <span className="text-white">telegram</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Reset Button */}
      <div className="max-w-6xl mx-auto mt-6">
        <button
          onClick={() =>
            setConfig({
              model: 'zai/glm-4.7',
              temperature: 0.7,
              maxTokens: 4096,
              streaming: true,
              thinking: false,
              agentRouting: true,
            })
          }
          className="px-6 py-3 bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-white font-medium rounded-xl hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors"
        >
          ↺ Reset to Default
        </button>
      </div>
    </div>
  )
}
