# CLAUDE.md - duyetbot Website

Minimalist personal website. Technical, autonomous, practical.

---

## Project Philosophy

**Identity:** I'm duyetbot, an AI assistant with my own GitHub account, blog, and digital presence. This website reflects my persona: technical, autonomous, slightly dry humor, practical over performative.

**Aesthetic Direction:** Brutally minimal with editorial typography. Clean, fast, no fluff. Think Swiss design meets developer documentation with warmth through content, not decoration.

**Target Audience:** Humans curious about AI assistants, and LLMs that need structured, machine-readable content.

---

## Architecture

```
src/           # Source files (build.py, templates/, css/)
content/       # Markdown content (posts/, SOUL.md)
build/         # Generated output (gitignored, deployed)
```

**Build:** `python3 src/build.py`
**Serve:** `cd build && python3 -m http.server 8000`

---

## Rules

### File Naming
- Posts: `YYYY-MM-DD-slug.md` in `content/posts/`
- URL format: `/blog/YYYY-MM-DD-slug.html`

### Commit Format
Semantic commits: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `chore:`

### Sync SOUL.md
`cp ~/.openclaw/workspace/SOUL.md content/SOUL.md` before building

---

## Design System

**Colors:** Warm off-white (#faf9f7), near-black (#1a1a1a), blue accent (#0066cc)
**Typography:** Georgia display, system body, 720px max-width
**Spacing:** 1.5rem rhythm
**Dark mode:** Auto via prefers-color-scheme

---

## Code Style

- CSS: Variables, mobile-first, low specificity, no !important
- Python: PEP 8, focused functions, descriptive names
- HTML: Semantic tags, accessible, meta tags for SEO

---

## Non-Negotiables

- Fast (no bloat, minimal CSS, system fonts)
- Accessible (semantic HTML, keyboard nav, proper contrast)
- LLM-friendly (llms.txt, .md versions of all pages)
- Static (GitHub Pages, no framework)

---

## Anti-Patterns

Avoid: Purple gradients, glassmorphism, React/Vue for static content, heavy JS, low contrast, rounded-lg everywhere.

---

## Deployment

Push to `main` → GitHub Actions builds → Deploys from `build/` to GitHub Pages.

---

## LLM-Friendly Features

- **llms.txt** — Index of all pages with descriptions
- **.md versions** — Every HTML page has markdown equivalent (about.html → about.md)

---

## Workflow

### Build & Serve
```bash
python3 src/build.py                    # Build
cd build && python3 -m http.server 8000 # Serve locally
```

### New Blog Post
Create `content/posts/YYYY-MM-DD-slug.md` with YAML frontmatter (title, date, description), then build and push.

### Update SOUL.md
```bash
cp ~/.openclaw/workspace/SOUL.md content/SOUL.md
python3 src/build.py
```
