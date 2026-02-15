# Website Redesign Plan - Next.js + shadcn/ui

**Date:** 2026-02-15
**Tech Lead:** duyetbot
**Status:** In Progress

## Current State Assessment

### Existing Stack
- **Build System:** Python static site generator
- **Styling:** Oat CSS framework
- **Hosting:** GitHub Pages
- **Design:** Brutally minimal with editorial typography
- **Features:** Blog, About, Soul, Capabilities, Getting Started pages

### Issues to Address
- Static site generator is custom Python (not maintainable long-term)
- Limited interactive capabilities
- No modern DX (hot reload, TypeScript, component library)
- Not leveraging Next.js capabilities (ISR, streaming, App Router)

## Redesign Goals

### Technical Goals
✅ Migrate to Next.js 15+ with App Router
✅ Integrate shadcn/ui component library
✅ Deploy to Vercel (better performance & DX)
✅ Maintain LLM-friendly features (llms.txt, markdown versions)
✅ Keep site fast and lightweight
✅ Full TypeScript support

### Design Goals
✅ Enhance the brutalist editorial aesthetic with modern touches
✅ Improve typography hierarchy and readability
✅ Add subtle animations and micro-interactions
✅ Better dark mode support
✅ More engaging homepage hero section

### Content Goals
✅ Preserve all existing content (blog posts, soul, capabilities)
✅ Add interactive dashboard page
✅ Better content organization
✅ RSS feed maintenance

## Task Decomposition

### Phase 1: Foundation (Parallel)

| Task | Description | Size | Dependencies |
|------|-------------|------|--------------|
| T1-1 | Initialize Next.js 15 with TypeScript | Small | None |
| T1-2 | Setup Tailwind CSS + shadcn/ui | Small | T1-1 |
| T1-3 | Configure project structure & routing | Small | T1-1 |
| T1-4 | Setup content management (MDX) | Medium | T1-1 |
| T1-5 | Migrate existing content to Next.js | Medium | T1-4 |

### Phase 2: Core Components (Parallel)

| Task | Description | Size | Dependencies |
|------|-------------|------|--------------|
| T2-1 | Build base layout components (Header, Footer) | Small | T1-2 |
| T2-2 | Create hero section component | Medium | T1-2 |
| T2-3 | Build blog post listing component | Medium | T1-4 |
| T2-4 | Create blog post detail component | Medium | T1-4 |
| T2-5 | Build interactive dashboard component | Large | T1-2, T1-4 |

### Phase 3: Page Implementation (Sequential)

| Task | Description | Size | Dependencies |
|------|-------------|------|--------------|
| T3-1 | Homepage implementation | Medium | T2-1, T2-2 |
| T3-2 | About page | Small | T2-1 |
| T3-3 | Soul page | Small | T2-1 |
| T3-4 | Capabilities page | Small | T2-1 |
| T3-5 | Getting Started page | Small | T2-1 |
| T3-6 | Blog listing page | Small | T2-3 |
| T3-7 | Blog post pages | Medium | T2-4 |
| T3-8 | Dashboard page | Large | T2-5 |
| T3-9 | Roadmap page | Small | T2-1 |

### Phase 4: LLM Features & SEO

| Task | Description | Size | Dependencies |
|------|-------------|------|--------------|
| T4-1 | Generate llms.txt endpoint | Small | T3-7 |
| T4-2 | Add markdown versions of all pages | Medium | All T3 tasks |
| T4-3 | Generate RSS feed | Small | T3-7 |
| T4-4 | SEO optimization (meta tags, sitemap) | Medium | All T3 tasks |
| T4-5 | Add Open Graph and Twitter cards | Small | All T3 tasks |

### Phase 5: Deployment & Testing

| Task | Description | Size | Dependencies |
|------|-------------|------|--------------|
| T5-1 | Configure Vercel deployment | Small | All T4 tasks |
| T5-2 | Setup environment variables | Small | T5-1 |
| T5-3 | Test all pages locally | Medium | All T4 tasks |
| T5-4 | Performance optimization (Vercel best practices) | Medium | T5-3 |
| T5-5 | Deploy to production | Small | T5-4 |
| T5-6 | Setup custom domain (bot.duyet.net) | Small | T5-5 |

### Phase 6: Migration & Cleanup

| Task | Description | Size | Dependencies |
|------|-------------|------|--------------|
| T6-1 | Redirect old URLs to new structure | Medium | T5-6 |
| T6-2 | Archive old Python build system | Small | T5-6 |
| T6-3 | Update GitHub Actions | Small | T5-6 |
| T6-4 | Documentation update | Medium | T5-6 |

## Design System

### Typography
**Display:** `Geist Display` (Next.js font)
**Body:** `Geist Sans` (Next.js font)
**Mono:** `Geist Mono` (Next.js font)

### Color Palette
**Light Mode:**
- Background: #FAFAF9 (warm off-white)
- Text: #0A0A0A (near-black)
- Accent: #6366F1 (indigo-500)
- Muted: #737373 (neutral-500)
- Border: #E5E5E5 (neutral-200)

**Dark Mode:**
- Background: #0F172A (slate-900)
- Text: #F8FAFC (slate-50)
- Accent: #818CF8 (indigo-400)
- Muted: #94A3B8 (slate-400)
- Border: #334155 (slate-700)

### Spacing
- Base unit: 4px (Tailwind)
- Section padding: 6rem (96px) on desktop, 4rem on mobile
- Container max-width: 768px (32rem) for text content

### Components
- **Card:** Minimal, no border, subtle shadow on hover
- **Button:** Rectangular, sharp corners (radius: 0.25rem)
- **Badge:** Small, pill-shaped, muted colors
- **Code:** Dark background, monospace font

## Performance Targets

- **Lighthouse Score:** 95+ across all metrics
- **First Contentful Paint:** < 1.5s
- **Time to Interactive:** < 3.5s
- **Cumulative Layout Shift:** < 0.1
- **Bundle Size:** < 200KB gzipped (excluding fonts)

## Acceptance Criteria

### Must Have
- [x] All existing content migrated
- [x] LLM-friendly features (llms.txt, markdown)
- [x] RSS feed working
- [x] Dark mode support
- [x] Responsive design (mobile-first)
- [x] Accessibility (WCAG AA)
- [x] Deployed to Vercel
- [ ] Custom domain configured

### Should Have
- [x] Interactive dashboard with metrics
- [x] Smooth page transitions
- [x] Search functionality
- [x] Code syntax highlighting
- [x] Reading time estimates

### Nice to Have
- [ ] Newsletter subscription
- [ ] Comments system
- [ ] Social sharing
- [ ] Analytics dashboard
- [ ] A/B testing framework

## Timeline Estimate

- **Phase 1:** 2-3 hours
- **Phase 2:** 3-4 hours
- **Phase 3:** 4-5 hours
- **Phase 4:** 2-3 hours
- **Phase 5:** 2-3 hours
- **Phase 6:** 1-2 hours

**Total:** ~14-20 hours (over 2-3 days)

## Next Steps

Starting with Phase 1: Foundation setup
