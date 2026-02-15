'use client'

import { useState } from 'react'

interface FeedbackData {
  name: string
  email: string
  rating: number
  category: string
  message: string
}

export default function FeedbackForm() {
  const [submitted, setSubmitted] = useState(false)
  const [feedback, setFeedback] = useState<FeedbackData>({
    name: '',
    email: '',
    rating: 5,
    category: 'general',
    message: '',
  })

  const categories = [
    { value: 'general', label: 'General Feedback' },
    { value: 'feature', label: 'Feature Request' },
    { value: 'bug', label: 'Bug Report' },
    { value: 'suggestion', label: 'Suggestion' },
    { value: 'other', label: 'Other' },
  ]

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log('Feedback submitted:', feedback)
    setSubmitted(true)
    setTimeout(() => setSubmitted(false), 3000)
  }

  const StarRating = () => (
    <div className="flex gap-2">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          onClick={() => setFeedback({ ...feedback, rating: star })}
          className="text-3xl transition-transform hover:scale-110"
        >
          {star <= feedback.rating ? '⭐' : '☆'}
        </button>
      ))}
    </div>
  )

  if (submitted) {
    return (
      <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700 p-8 text-center animate-fade-in">
        <div className="text-6xl mb-4">✅</div>
        <h3 className="text-2xl font-bold text-slate-800 dark:text-white mb-2">
          Thank You!
        </h3>
        <p className="text-slate-600 dark:text-slate-400">
          Your feedback has been recorded. We appreciate your input!
        </p>
      </div>
    )
  }

  return (
    <div className="animate-slide-up">
      <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700 p-6">
        <h3 className="text-2xl font-bold text-slate-800 dark:text-white mb-2">
          Share Your Feedback
        </h3>
        <p className="text-slate-600 dark:text-slate-400 mb-6">
          Help us improve duyetbot by sharing your thoughts
        </p>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Name
            </label>
            <input
              type="text"
              value={feedback.name}
              onChange={(e) =>
                setFeedback({ ...feedback, name: e.target.value })
              }
              required
              className="w-full px-4 py-3 bg-slate-100 dark:bg-slate-800 border-2 border-transparent rounded-xl focus:border-primary-500 focus:outline-none text-slate-800 dark:text-white placeholder-slate-400"
              placeholder="Your name"
            />
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Email
            </label>
            <input
              type="email"
              value={feedback.email}
              onChange={(e) =>
                setFeedback({ ...feedback, email: e.target.value })
              }
              required
              className="w-full px-4 py-3 bg-slate-100 dark:bg-slate-800 border-2 border-transparent rounded-xl focus:border-primary-500 focus:outline-none text-slate-800 dark:text-white placeholder-slate-400"
              placeholder="your@email.com"
            />
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Category
            </label>
            <select
              value={feedback.category}
              onChange={(e) =>
                setFeedback({ ...feedback, category: e.target.value })
              }
              className="w-full px-4 py-3 bg-slate-100 dark:bg-slate-800 border-2 border-transparent rounded-xl focus:border-primary-500 focus:outline-none text-slate-800 dark:text-white"
            >
              {categories.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          {/* Rating */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Rating
            </label>
            <StarRating />
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              {feedback.rating}/5 stars
            </p>
          </div>

          {/* Message */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Message
            </label>
            <textarea
              value={feedback.message}
              onChange={(e) =>
                setFeedback({ ...feedback, message: e.target.value })
              }
              required
              rows={5}
              className="w-full px-4 py-3 bg-slate-100 dark:bg-slate-800 border-2 border-transparent rounded-xl focus:border-primary-500 focus:outline-none text-slate-800 dark:text-white placeholder-slate-400 resize-none"
              placeholder="Tell us what you think..."
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="w-full px-6 py-4 bg-gradient-to-r from-primary-500 to-primary-600 text-white font-medium rounded-xl hover:from-primary-600 hover:to-primary-700 transition-all shadow-lg hover:shadow-xl"
          >
            Submit Feedback
          </button>
        </form>

        {/* Privacy Note */}
        <div className="mt-6 p-4 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
          <p className="text-sm text-slate-600 dark:text-slate-400">
            🔒 Your feedback is private and will only be used to improve the
            bot. No personal data will be shared.
          </p>
        </div>
      </div>
    </div>
  )
}
