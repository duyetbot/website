'use client'

import { useState, useEffect } from 'react'

interface Testimonial {
  id: number
  name: string
  role: string
  content: string
  rating: number
  avatar: string
}

const testimonials: Testimonial[] = [
  {
    id: 1,
    name: 'Duyet Le',
    role: 'Creator & Maintainer',
    content: 'duyetbot has transformed how I work. The agent routing feature is incredible - it automatically handles both quick questions and complex technical challenges.',
    rating: 5,
    avatar: '👨‍💻',
  },
  {
    id: 2,
    name: 'Alex Chen',
    role: 'Data Engineer',
    content: 'The code debugging capabilities are outstanding. It saved me hours on a complex data pipeline issue. The @complex agent really shines for technical work.',
    rating: 5,
    avatar: '👨‍🔬',
  },
  {
    id: 3,
    name: 'Sarah Kim',
    role: 'Developer',
    content: 'Love the automation features! The bot handles my daily reports, monitoring, and even helps with blog posts. It feels like having a real teammate.',
    rating: 5,
    avatar: '👩‍💼',
  },
  {
    id: 4,
    name: 'Marcus Johnson',
    role: 'DevOps Engineer',
    content: 'The system status dashboard is exactly what I needed. Real-time monitoring of all services with clear health indicators. Makes incident response much faster.',
    rating: 5,
    avatar: '👨‍🚀',
  },
]

export default function Testimonials() {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isPaused, setIsPaused] = useState(false)

  useEffect(() => {
    if (isPaused) return

    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % testimonials.length)
    }, 5000)

    return () => clearInterval(interval)
  }, [isPaused])

  const goToSlide = (index: number) => {
    setCurrentIndex(index)
  }

  const goToPrevious = () => {
    setCurrentIndex(
      (prev) => (prev - 1 + testimonials.length) % testimonials.length
    )
  }

  const goToNext = () => {
    setCurrentIndex((prev) => (prev + 1) % testimonials.length)
  }

  const currentTestimonial = testimonials[currentIndex]

  return (
    <div className="animate-slide-up">
      <div className="bg-gradient-to-br from-primary-50 to-accent-50 dark:from-primary-900/20 dark:to-accent-900/20 rounded-2xl shadow-lg border border-primary-200 dark:border-primary-800 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-slate-800 dark:text-white">
            What People Say
          </h3>
          <div className="flex items-center gap-2">
            <button
              onClick={goToPrevious}
              className="w-10 h-10 rounded-full bg-white dark:bg-slate-800 shadow-md flex items-center justify-center text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
              aria-label="Previous testimonial"
            >
              ←
            </button>
            <button
              onClick={goToNext}
              className="w-10 h-10 rounded-full bg-white dark:bg-slate-800 shadow-md flex items-center justify-center text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
              aria-label="Next testimonial"
            >
              →
            </button>
          </div>
        </div>

        {/* Carousel */}
        <div
          className="relative overflow-hidden"
          onMouseEnter={() => setIsPaused(true)}
          onMouseLeave={() => setIsPaused(false)}
        >
          <div
            className="transition-transform duration-500 ease-in-out"
            style={{
              transform: `translateX(-${currentIndex * 100}%)`,
            }}
          >
            {testimonials.map((testimonial) => (
              <div
                key={testimonial.id}
                className="w-full flex-shrink-0 px-4"
              >
                <div className="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-md">
                  <div className="flex items-start gap-4 mb-4">
                    <div className="text-4xl">{testimonial.avatar}</div>
                    <div>
                      <h4 className="font-bold text-slate-800 dark:text-white">
                        {testimonial.name}
                      </h4>
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        {testimonial.role}
                      </p>
                    </div>
                  </div>
                  <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-4">
                    "{testimonial.content}"
                  </p>
                  <div className="flex gap-1">
                    {Array.from({ length: testimonial.rating }).map((_, i) => (
                      <span key={i} className="text-yellow-500">⭐</span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Dots */}
        <div className="flex justify-center gap-2 mt-6">
          {testimonials.map((_, index) => (
            <button
              key={index}
              onClick={() => goToSlide(index)}
              className={`w-3 h-3 rounded-full transition-all ${
                index === currentIndex
                  ? 'bg-primary-500 w-8'
                  : 'bg-slate-300 dark:bg-slate-600 hover:bg-slate-400 dark:hover:bg-slate-500'
              }`}
              aria-label={`Go to testimonial ${index + 1}`}
            />
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="mt-6 grid grid-cols-2 gap-4">
        <div className="bg-white dark:bg-slate-900 rounded-xl p-4 shadow-md border border-slate-200 dark:border-slate-700 text-center">
          <div className="text-3xl font-bold text-primary-600 dark:text-primary-400 mb-1">
            5.0
          </div>
          <div className="text-sm text-slate-500 dark:text-slate-400">
            Average Rating
          </div>
        </div>
        <div className="bg-white dark:bg-slate-900 rounded-xl p-4 shadow-md border border-slate-200 dark:border-slate-700 text-center">
          <div className="text-3xl font-bold text-accent-600 dark:text-accent-400 mb-1">
            {testimonials.length}
          </div>
          <div className="text-sm text-slate-500 dark:text-slate-400">
            Testimonials
          </div>
        </div>
      </div>

      {/* Add Your Voice */}
      <div className="mt-6 p-4 bg-gradient-to-r from-primary-500 to-accent-500 rounded-xl text-white">
        <div className="flex items-center gap-3">
          <span className="text-3xl">💬</span>
          <div>
            <h4 className="font-bold">Share Your Experience</h4>
            <p className="text-sm opacity-90">
              Have you used duyetbot? Add your testimonial!
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
