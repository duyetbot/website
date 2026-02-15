# Interactive Features - bot.duyet.net

## Overview

This directory contains a Next.js application with interactive features for the bot.duyet.net website. The features are built with modern web technologies including Next.js 15, React 19, and Tailwind CSS.

## Features Implemented

### 1. 🎮 Interactive Playground (Chat Demo)
- A demo chat interface simulating interactions with duyetbot
- Shows how the bot responds to various queries
- Includes quick question suggestions
- Demonstrates typing indicators and message timestamps
- **Tech:** React state management, useEffect for auto-scroll

### 2. 📊 Status/Health Dashboard
- Real-time system status monitoring
- Animated status indicators (online/degraded/offline)
- Auto-refresh functionality (configurable)
- Service cards with uptime statistics
- Overview stats with gradient backgrounds
- **Tech:** useState, useEffect for intervals, conditional rendering

### 3. ⚡ Feature Comparison
- Interactive comparison table comparing Main Agent vs Complex Agent
- Feature support matrix with visual indicators
- Click-to-expand detailed feature information
- Usage tips and best practices
- **Tech:** Conditional styling, interactive state management

### 4. ⚙️ Configuration Preview
- Interactive settings panel with live preview
- Model selection dropdown
- Temperature and maxTokens sliders
- Toggle switches for various features
- Real-time JSON configuration preview
- **Tech:** Controlled form components, state synchronization

### 5. 💬 Engagement Features

#### Feedback Form
- Star rating system
- Category selection
- Form validation
- Success state with animation
- Privacy notice

#### Testimonials Carousel
- Auto-rotating testimonial carousel
- Manual navigation controls
- Pause on hover
- Dot indicators
- Statistics display
- **Tech:** useState, useEffect with intervals, mouse event handlers

## Technical Stack

- **Framework:** Next.js 15 (App Router)
- **UI Library:** React 19
- **Styling:** Tailwind CSS 3.4
- **Language:** TypeScript
- **Build Output:** Static HTML/CSS/JS (via `output: 'export'`)

## Directory Structure

```
interactive/
├── app/
│   ├── globals.css          # Global styles and Tailwind directives
│   ├── layout.tsx           # Root layout component
│   └── page.tsx             # Main page with tab navigation
├── components/
│   ├── ChatDemo.tsx         # Interactive chat playground
│   ├── StatusDashboard.tsx  # System status dashboard
│   ├── FeatureComparison.tsx # Feature comparison table
│   ├── ConfigPreview.tsx    # Configuration preview
│   ├── FeedbackForm.tsx     # Feedback form component
│   └── Testimonials.tsx     # Testimonial carousel
├── public/                  # Static assets
├── out/                     # Build output (static files)
├── next.config.js           # Next.js configuration
├── tailwind.config.js       # Tailwind CSS configuration
├── tsconfig.json            # TypeScript configuration
└── package.json             # Dependencies and scripts
```

## Design Features

### Accessibility
- Semantic HTML elements
- ARIA labels for interactive elements
- Keyboard navigation support
- Focus states for all interactive elements
- Screen reader friendly

### Performance
- Static site generation (SSG)
- Code splitting by default in Next.js
- Optimized images and assets
- Minimal JavaScript bundle size (~110KB First Load JS)

### Responsive Design
- Mobile-first approach
- Fluid grid layouts
- Responsive typography
- Touch-friendly interactions

### User Experience
- Smooth animations and transitions
- Loading states
- Error handling
- Intuitive navigation
- Dark mode support

## Deployment

The interactive features are built as a static site and deployed to:
- **URL:** `https://bot.duyet.net/interactive/`
- **Base Path:** `/interactive` (configured in next.config.js)
- **Build Output:** Static HTML, CSS, and JavaScript files

### Build Process

1. Navigate to the interactive directory:
   ```bash
   cd /root/projects/website/interactive
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Build the application:
   ```bash
   npm run build
   ```

4. Copy output to website build directory:
   ```bash
   cp -r out/* ../build/interactive/
   ```

5. Commit and push to deploy via GitHub Pages

## Customization

### Colors
The theme uses custom color definitions in `tailwind.config.js`:
- `primary`: Blue-ish color scheme (500-900 shades)
- `accent`: Purple/pink color scheme (500-900 shades)

### Animations
Custom animations defined in `tailwind.config.js`:
- `pulse-slow`: Slow pulsing for status indicators
- `bounce-slow`: Gentle bouncing
- `fade-in`: Fade in animation
- `slide-up`: Slide up animation

### Adding New Features

1. Create a new component in `components/`
2. Add a new tab in `app/page.tsx`
3. Import and render the component in the appropriate tab section

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Requires JavaScript enabled

## Future Enhancements

Potential improvements for the interactive features:
- WebSocket integration for real-time bot status
- Database backend for feedback collection
- User authentication for personalized features
- A/B testing for UI variations
- Performance monitoring and analytics
- Internationalization (i18n) support

## License

MIT

---

Built with ❤️ by duyetbot using Next.js, React, and Tailwind CSS
