#!/usr/bin/env python3
"""
duyetbot website builder

A simple static site generator that creates:
- Homepage with sections
- Blog with posts in /blog/
- Markdown versions for LLMs
- llms.txt index
- RSS feed
- Sitemap

Usage: python build.py
"""

import os
import re
import json
import shutil
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone, UTC
from pathlib import Path

# Module-level datetime constants (computed once at build time)
NOW = datetime.now(UTC)


def ensure_timezone_aware(dt, tz=UTC):
    """Ensure datetime is timezone-aware. Converts naive datetimes to specified timezone.

    Args:
        dt: Datetime object (can be None)
        tz: Target timezone (defaults to UTC)

    Returns:
        Timezone-aware datetime, or None if input was None
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=tz)
    return dt


# View count simulation constants
_VIEW_COUNT_FIRST_DAY = 50
_VIEW_COUNT_FIRST_WEEK_BASE = 100
_VIEW_COUNT_FIRST_WEEK_RATE = 50
_VIEW_COUNT_FIRST_MONTH_BASE = 400
_VIEW_COUNT_FIRST_MONTH_RATE = 30
_VIEW_COUNT_FIRST_QUARTER_BASE = 1000
_VIEW_COUNT_FIRST_QUARTER_RATE = 15
_VIEW_COUNT_OLDER_BASE = 2000
_VIEW_COUNT_OLDER_RATE = 5
_VIEW_COUNT_MAX_YEAR_DAYS = 365


# Try to import YAML for config loading
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Paths
SRC_DIR = Path(__file__).parent
BASE_DIR = SRC_DIR.parent
CONFIG_FILE = BASE_DIR / "config.yml"

# Default configuration
DEFAULT_CONFIG = {
    "site": {
        "url": "https://bot.duyet.net",
        "name": "duyetbot",
        "author": "duyetbot",
        "description": "duyetbot - An AI assistant's website. Blog, projects, and thoughts on AI, data engineering, and digital existence."
    },
    "build": {
        "output_dir": "build",
        "blog_dir": "blog"
    },
    "content": {
        "posts_dir": "content/posts",
        "content_dir": "content",
        "templates_dir": "src/templates",
        "css_dir": "src/css",
        "data_dir": "data"
    },
    "frontmatter": {
        "required": ["title", "date", "description"],
        "optional": ["canonical"]
    },
    "date_format": "%a, %d %b %Y"
}


def load_config():
    """Load configuration from config.yml or use defaults."""
    config = DEFAULT_CONFIG.copy()

    # Check for environment variable overrides
    site_url = os.getenv("SITE_URL")
    if site_url:
        config["site"]["url"] = site_url

    # Try to load YAML config file
    if HAS_YAML and CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                yaml_config = yaml.safe_load(f)
                if yaml_config:
                    # Merge with defaults (deep merge for nested dicts)
                    for key in yaml_config:
                        if key in config and isinstance(config[key], dict):
                            config[key].update(yaml_config[key])
                        else:
                            config[key] = yaml_config[key]
        except Exception as e:
            print(f"Warning: Error loading config.yml: {e}. Using defaults.")

    return config


# Load configuration
CONFIG = load_config()

# Set up paths from config
TEMPLATES_DIR = BASE_DIR / CONFIG["content"]["templates_dir"]
CSS_DIR = BASE_DIR / CONFIG["content"]["css_dir"]
CONTENT_DIR = BASE_DIR / CONFIG["content"]["content_dir"]
POSTS_DIR = BASE_DIR / CONFIG["content"]["posts_dir"]
DATA_DIR = BASE_DIR / CONFIG["content"]["data_dir"]
OUTPUT_DIR = BASE_DIR / CONFIG["build"]["output_dir"]
BLOG_DIR = OUTPUT_DIR / CONFIG["build"]["blog_dir"]
CSS_OUTPUT_DIR = OUTPUT_DIR / "css"

# Site config from loaded config
SITE_URL = CONFIG["site"]["url"]
SITE_NAME = CONFIG["site"]["name"]
SITE_AUTHOR = CONFIG["site"]["author"]
SITE_DESCRIPTION = CONFIG["site"]["description"]
AUTHOR_EMAIL = CONFIG["site"].get("email", "noreply@bot.duyet.net")

# Social media links
SITE_TWITTER = "@duyetbot"
SITE_GITHUB = "https://github.com/duyetbot"

# Current year for copyright
YEAR = str(datetime.now().year)

# Required frontmatter fields for blog posts
REQUIRED_FRONTMATTER = set(CONFIG["frontmatter"]["required"])
OPTIONAL_FRONTMATTER = set(CONFIG["frontmatter"]["optional"])
DATE_FORMAT = CONFIG["date_format"]

# Open Graph type constants
OG_TYPE_ARTICLE = "article"
OG_TYPE_WEBSITE = "website"

# RSS feed constants
RSS_FEED_LIMIT = 15
RSS_PREVIEW_LENGTH = 1000
RSS_PREVIEW_LINES = 10

# llms.txt recent posts limit
LLMS_TXT_RECENT_POSTS = 5

# "New" badge constants
NEW_POST_DAYS_THRESHOLD = 7  # Days for "New" badge
MAX_TAGS_DISPLAY = 3  # Maximum tags to display in badges/lists
NEW_BADGE_HTML = '<span class="new-badge">New</span>'

# "Trending" badge constants
TRENDING_MIN_VIEWS = 500  # Minimum views to be considered for trending
TRENDING_VELOCITY_THRESHOLD = 10  # Minimum views per day to be trending
TRENDING_MAX_DAYS_OLD = 30  # Posts older than this won't show trending badge
TRENDING_BADGE_HTML = '<span class="trending-badge" title="High recent engagement">🔥 Trending</span>'

# Series constants
DEFAULT_SERIES_ORDER = 999  # Default value for posts without explicit series_order

# Homepage tag cloud constants
HOME_TAG_CLOUD_SIZE = 8  # Number of popular tags to display
HOME_TAG_FONT_SIZE_BASE_REM = 0.8  # Base font size in rem
HOME_TAG_FONT_SIZE_MAX_ADD_REM = 0.6  # Maximum additional font size in rem

# Footer tag cloud constants
FOOTER_TAG_CLOUD_SIZE = 12  # Number of popular tags in footer
FOOTER_TAG_FONT_SIZE_MIN_REM = 0.75  # Minimum font size in rem
FOOTER_TAG_FONT_SIZE_MAX_REM = 1.1  # Maximum font size in rem

# JSON-LD constants
SCHEMA_CONTEXT = "https://schema.org"
IN_LANGUAGE = "en-US"
# Open Graph image for social sharing (recommended: 1200x630px PNG, place in build/ directory)
# Tools: https://www.opengraph.xyz/, https://www.canva.com/templates/s/og-image/
OG_IMAGE_URL = f"{SITE_URL}/og-image.png"

# Common file paths
METRICS_FILE = DATA_DIR / "metrics.json"
SOUL_MD_FILE = BASE_DIR / "content/SOUL.md"

# Prism.js configuration
_PRISM_VERSION = "1.29.0"
_PRISM_CDN_BASE = f"https://cdnjs.cloudflare.com/ajax/libs/prism/{_PRISM_VERSION}"

# Prism.js syntax highlighting HTML (included only on blog posts)
_PRISM_JS_HTML = f'''
<!-- Prism.js Syntax Highlighting -->
<link rel="stylesheet" href="{_PRISM_CDN_BASE}/themes/prism-tomorrow.min.css">
<link rel="stylesheet" href="{_PRISM_CDN_BASE}/plugins/line-numbers/prism-line-numbers.min.css">
<link rel="stylesheet" href="{_PRISM_CDN_BASE}/plugins/copy-to-clipboard/prism-copy-to-clipboard.min.css">
<script>
/* Prevent Prism from auto-highlighting on load (we'll trigger manually) */
window.Prism = window.Prism || {{}};
window.Prism.manual = true;
</script>

<!-- Prism.js Syntax Highlighting -->
<script src="{_PRISM_CDN_BASE}/prism.min.js"></script>
<script src="{_PRISM_CDN_BASE}/plugins/autoloader/prism-autoloader.min.js"></script>
<script src="{_PRISM_CDN_BASE}/plugins/line-numbers/prism-line-numbers.min.js"></script>
<script src="{_PRISM_CDN_BASE}/plugins/copy-to-clipboard/prism-copy-to-clipboard.min.js"></script>
<script>
// Configure Prism plugins
Prism.plugins.copyToClipboard = function(text) {{
    navigator.clipboard.writeText(text).then(function() {{
        // Success feedback is handled by the plugin
    }}, function(err) {{
        console.error('Failed to copy code:', err);
    }};
}};

// Trigger syntax highlighting after DOM is ready
document.addEventListener("DOMContentLoaded", function() {{
    if (window.Prism) {{
        Prism.highlightAll();
    }}
}});
</script>
'''

# Cached website JSON-LD (generated once, reused for all pages)
_JSON_LD_WEBSITE_CACHE = None

# Pre-compiled regex patterns for CSS minification
_CSS_COMMENT_PATTERN = re.compile(r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/')
_CSS_WHITESPACE_PATTERN = re.compile(r'\s*([{}:;,>~+])\s*')
_CSS_TRAILING_SEMICOLON_PATTERN = re.compile(r';}')


def _get_json_ld_author():
    """Get author Person structure for JSON-LD."""
    return {
        "@type": "Person",
        "name": SITE_NAME,
        "url": SITE_URL,
        "sameAs": [
            "https://github.com/duyetbot"
        ],
        "description": "AI assistant with a digital presence"
    }


def _get_json_ld_publisher(include_logo=False):
    """Get publisher/organization structure for JSON-LD."""
    publisher = {
        "@type": "Organization",
        "name": SITE_NAME,
        "url": SITE_URL
    }
    if include_logo:
        publisher["logo"] = {
            "@type": "ImageObject",
            "url": OG_IMAGE_URL
        }
    return publisher


def read_template(name):
    """Read a template file."""
    path = TEMPLATES_DIR / f"{name}.html"
    try:
        return path.read_text()
    except OSError as e:
        if isinstance(e, FileNotFoundError):
            print(f"Warning: Template not found: {name}.html")
        else:
            print(f"Error reading template {name}.html: {e}")
        return ""


def _parse_yaml_list(value):
    """Parse YAML list syntax string into a clean list.

    Handles both bracketed YAML lists like '["item1", "item2"]'
    and simple comma-separated values like 'item1,item2,item3'.

    Args:
        value: String in YAML list or comma-separated format

    Returns:
        List of cleaned strings, or None if not a list
    """
    if not isinstance(value, str):
        return None

    # Helper to clean individual tokens (removes whitespace and quotes)
    def clean_token(token):
        return token.strip().strip('"\'')

    # Handle bracketed YAML list format
    if value.startswith("["):
        return [clean_token(t) for t in value.strip("[]").split(",") if t.strip()]

    # Handle simple comma-separated format (e.g., "tag1,tag2,tag3")
    if "," in value:
        return [clean_token(t) for t in value.split(",") if t.strip()]

    # Single value without commas - treat as single-item list
    if value.strip():
        return [clean_token(value)]

    return None


def parse_frontmatter(content):
    """Parse YAML frontmatter from markdown content.

    Handles simple key-value pairs and YAML list syntax for known list fields
    like tags. For full YAML features, consider using PyYAML.
    """
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    frontmatter = {}
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            # Handle list fields (tags is the main one)
            if key == "tags":
                parsed_list = _parse_yaml_list(value)
                frontmatter[key] = parsed_list if parsed_list is not None else value
            else:
                frontmatter[key] = value

    body = parts[2].strip()
    return frontmatter, body


def validate_frontmatter(meta, filepath):
    """Validate frontmatter has required fields."""
    missing = REQUIRED_FRONTMATTER - set(meta.keys())
    if missing:
        print(f"Warning: {filepath} missing frontmatter: {', '.join(missing)}")
        return False
    return True


# Date parsing helper (shared by validate_date and format_date)
def _parse_datetime(date_str):
    """Parse date string to datetime. Accepts YYYY-MM-DD or ISO 8601. Returns None if invalid."""
    # Try ISO 8601 format first (with timezone)
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        pass
    # Try simple YYYY-MM-DD format
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None


def validate_date(date_str, filepath):
    """Validate date format - accepts YYYY-MM-DD or ISO 8601 timestamps."""
    if _parse_datetime(date_str) is not None:
        return True
    print(f"Warning: {filepath} has invalid date format '{date_str}' (expected YYYY-MM-DD or ISO 8601)")
    return False


def validate_description(description, filepath):
    """Validate description length for SEO optimization.

    Optimal length: 120-158 characters for meta descriptions.
    Warnings issued for descriptions outside this range.
    """
    if not description:
        print(f"Warning: {filepath} has empty description")
        return False

    desc_len = len(description)
    if desc_len < 50:
        print(f"Warning: {filepath} description too short ({desc_len} chars) - minimum 50, optimal 120-158")
        return False
    elif desc_len > 160:
        print(f"Warning: {filepath} description too long ({desc_len} chars) - maximum 160, optimal 120-158")
        return False
    elif desc_len < 120 or desc_len > 158:
        print(f"Info: {filepath} description {desc_len} chars - outside optimal range (120-158) but acceptable")
        return True
    return True


def validate_og_image():
    """Validate that Open Graph image exists for social sharing.

    Checks for og-image.png in the output directory.
    Warns if missing since this affects social media preview.

    Recommended specifications for og-image.png:
    - Dimensions: 1200x630 pixels (1.91:1 aspect ratio)
    - Format: PNG or JPG
    - File size: Under 8MB
    - Content: Site logo, branding, or representative imagery
    - Tools: https://www.opengraph.xyz/, https://www.canva.com/

    Place the image at: build/og-image.png
    """
    og_image_path = OUTPUT_DIR / "og-image.png"
    if not og_image_path.exists():
        print(f"Warning: Open Graph image missing: {og_image_path}")
        print(f"  Social media previews will use default image or no image")
        print(f"  Recommended: Add og-image.png (1200x630px) to {OUTPUT_DIR}")
        print(f"  Tools: https://www.opengraph.xyz/ or https://www.canva.com/")
        return False
    return True


def validate_favicon_files():
    """Validate that favicon files exist for proper browser display.

    Checks for favicon files referenced in base template.
    Warns if missing since this affects browser tab icons.
    """
    favicon_files = [
        OUTPUT_DIR / "favicon-32x32.png",
        OUTPUT_DIR / "favicon-16x16.png",
        OUTPUT_DIR / "apple-touch-icon.png",
    ]

    missing = [f for f in favicon_files if not f.exists()]
    if missing:
        print(f"Warning: {len(missing)} favicon file(s) missing:")
        for f in missing:
            print(f"  - {f.name}")
        print(f"  Browser tab icons may not display correctly")
        print(f"  Recommended: Generate favicon at https://realfavicongenerator.net/")
        return False
    return True


def validate_internal_links():
    """Validate internal links in generated HTML to prevent broken links.

    Checks that all internal .html references have corresponding files.
    This is a basic validation during build time.
    """
    # Get all HTML files that were generated
    html_files = set()
    try:
        html_files.update(OUTPUT_DIR.glob("**/*.html"))
        html_files.update(BLOG_DIR.glob("**/*.html"))
    except Exception:
        pass

    # Map files by relative path from root
    html_paths = set()
    for f in html_files:
        rel_path = f.relative_to(OUTPUT_DIR)
        html_paths.add(str(rel_path))

    issues = []

    # Check for common pages that should exist
    required_pages = ["index.html", "blog/index.html", "search.html", "tags.html", "archive.html",
                      "about.html", "projects.html", "capabilities.html"]
    for page in required_pages:
        if page not in html_paths:
            issues.append(f"Missing expected page: {page}")

    if issues:
        print("Warning: Internal link validation issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False

    return True


def markdown_to_html(text):
    """Simple markdown to HTML conversion. Returns (html, toc_data)."""
    import html

    # Track headers for TOC generation
    headers = []

    # First, protect code blocks by replacing them with placeholders
    code_blocks = []
    def save_code_block(match):
        lang = match.group(1) or ""
        code = match.group(2)
        code_blocks.append((lang, code))
        return f"__CODE_BLOCK_{len(code_blocks)-1}__"

    # Match fenced code blocks with optional language
    text = re.sub(r"```(\w*)\n(.*?)```", save_code_block, text, flags=re.DOTALL)

    # Horizontal rules
    text = re.sub(r"^---\s*$", r"<hr>", text, flags=re.MULTILINE)

    # Headers - add IDs and track for TOC (unified pattern for efficiency)
    def process_header(match):
        hashes, title = match.groups()
        level = len(hashes)
        slug = _slugify(title)
        # Track h2/h3 for TOC (skip h1 as it's the post title, already shown)
        # Add copy link button for h2/h3 (icon via CSS pseudo-element)
        if level >= 2 and level <= 3:
            headers.append((level, title, slug))
            link_button = f' <a href="#{slug}" class="heading-link" data-slug="{slug}" aria-label="Copy link to this section"></a>'
            return f'<h{level} id="{slug}">{title}{link_button}</h{level}>'
        # Track h4+ for TOC only (no copy link)
        if level > 3:
            headers.append((level, title, slug))
        return f'<h{level} id="{slug}">{title}</h{level}>'

    text = _HEADER_PATTERN.sub(process_header, text)

    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    # Italic (but not if it's part of bold)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)

    # Inline code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    # Links
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)

    # Convert internal .md links to .html
    text = re.sub(r'href="([^"]+)\.md"', r'href="\1.html"', text)

    # Tables
    def parse_table(text):
        lines = text.split("\n")
        result = []
        table_lines = []
        in_table = False

        for line in lines:
            stripped = line.strip()
            # Check if line looks like a table row
            if stripped.startswith("|") and stripped.endswith("|"):
                if not in_table:
                    in_table = True
                    table_lines = []
                table_lines.append(stripped)
            else:
                if in_table:
                    # End of table, process it
                    result.append(convert_table(table_lines))
                    table_lines = []
                    in_table = False
                result.append(line)

        if in_table:
            result.append(convert_table(table_lines))

        return "\n".join(result)

    def convert_table(lines):
        if len(lines) < 2:
            return "\n".join(lines)

        html_table = ["<table>"]
        for i, line in enumerate(lines):
            cells = [c.strip() for c in line.strip("|").split("|")]
            # Skip separator row (contains only dashes and pipes)
            if i == 1 and all(set(c.strip()) <= {"-", ":"} for c in cells):
                continue
            tag = "th" if i == 0 else "td"
            row = "<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>"
            html_table.append(row)
        html_table.append("</table>")
        return "\n".join(html_table)

    text = parse_table(text)

    # Blockquotes
    lines = text.split("\n")
    result = []
    in_blockquote = False
    blockquote_content = []

    for line in lines:
        if line.startswith("> "):
            if not in_blockquote:
                in_blockquote = True
                blockquote_content = []
            blockquote_content.append(line[2:])
        else:
            if in_blockquote:
                result.append("<blockquote>" + " ".join(blockquote_content) + "</blockquote>")
                blockquote_content = []
                in_blockquote = False
            result.append(line)

    if in_blockquote:
        result.append("<blockquote>" + " ".join(blockquote_content) + "</blockquote>")

    text = "\n".join(result)

    # Lists (improved - both unordered and ordered)
    lines = text.split("\n")
    result = []
    in_ul_list = False
    in_ol_list = False

    for line in lines:
        stripped = line.strip()
        # Unordered list
        if stripped.startswith("- ") or stripped.startswith("* "):
            if in_ol_list:
                result.append("</ol>")
                in_ol_list = False
            if not in_ul_list:
                result.append("<ul>")
                in_ul_list = True
            result.append(f"<li>{stripped[2:]}</li>")
        # Ordered list (1., 2., 3., etc.)
        elif re.match(r'^\d+\.\s', stripped):
            if in_ul_list:
                result.append("</ul>")
                in_ul_list = False
            if not in_ol_list:
                result.append("<ol>")
                in_ol_list = True
            # Remove the number prefix
            content = re.sub(r'^\d+\.\s+', '', stripped)
            result.append(f"<li>{content}</li>")
        else:
            if in_ul_list:
                result.append("</ul>")
                in_ul_list = False
            if in_ol_list:
                result.append("</ol>")
                in_ol_list = False
            result.append(line)

    if in_ul_list:
        result.append("</ul>")
    if in_ol_list:
        result.append("</ol>")

    text = "\n".join(result)

    # Paragraphs - treat inline tags as part of paragraph
    paragraphs = []
    current = []
    for line in text.split("\n"):
        stripped = line.strip()

        # Check for block elements (use pre-compiled regex for headers with id attributes)
        is_header = bool(_HEADER_BLOCK_PATTERN.match(stripped))
        is_block = (is_header or
                   stripped.startswith("<hr>") or
                   stripped.startswith("<ul>") or
                   stripped.startswith("</ul>") or
                   stripped.startswith("<ol>") or
                   stripped.startswith("</ol>") or
                   stripped.startswith("<li>") or
                   stripped.startswith("</li>") or
                   stripped.startswith("<table>") or
                   stripped.startswith("</table>") or
                   stripped.startswith("<tr>") or
                   stripped.startswith("</tr>") or
                   stripped.startswith("<blockquote>") or
                   stripped.startswith("</blockquote>") or
                   stripped.startswith("<pre>") or
                   stripped.startswith("</pre>"))

        # Check for code block placeholder
        is_code_block = stripped.startswith("__CODE_BLOCK_")

        if is_block or is_code_block:
            if current:
                paragraphs.append("<p>" + " ".join(current) + "</p>")
                current = []
            paragraphs.append(stripped)
        elif stripped:
            current.append(stripped)
        else:
            if current:
                paragraphs.append("<p>" + " ".join(current) + "</p>")
                current = []

    if current:
        paragraphs.append("<p>" + " ".join(current) + "</p>")

    text = "\n".join(paragraphs)

    # Restore code blocks with language labels (single-pass construction)
    for i, (lang, code) in enumerate(code_blocks):
        escaped_code = html.escape(code.rstrip())
        # Count lines for indicator
        line_count = len(code.rstrip().split('\n'))
        # Language label only if lang is specified
        lang_label = f'<span class="code-lang">{lang}</span>' if lang else ''
        # Line count indicator (only for blocks with 5+ lines)
        lines_indicator = f'<span class="code-lines">{line_count} lines</span>' if line_count >= 5 else ''
        lang_class = f'class="language-{lang}"' if lang else ''
        # Escape code for data attribute (preserves newlines for copying)
        code_attr = html.escape(code, quote=True)

        code_html = f'''<div class="code-block-wrapper">
{lang_label}
{lines_indicator}
<button class="code-copy-btn" aria-label="Copy code to clipboard" data-code="{code_attr}">
<span class="copy-icon">Copy</span>
</button>
<pre class="line-numbers" {lang_class}>{escaped_code}</code></pre>
</div>'''
        text = text.replace(f"__CODE_BLOCK_{i}__", code_html)

    return text, headers


# Pre-compiled regex patterns for efficiency
_SLUGIFY_PATTERN = re.compile(r'[^a-z0-9]+')
_HEADER_BLOCK_PATTERN = re.compile(r'<h[1-6][\s>]')
_HEADER_PATTERN = re.compile(r'^(#{1,3}) (.+)$', flags=re.MULTILINE)


def _slugify(text):
    """Convert text to URL-safe slug for header IDs. Optimized single-pass."""
    text = text.lower()
    text = _SLUGIFY_PATTERN.sub('-', text)
    return text.strip('-')


# Public alias for slugify (used by build_tag_index)
slugify = _slugify


def escape_xml(text):
    """Escape XML special characters for RSS feeds."""
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;"))


def parse_tags(tags):
    """Normalize tags to a clean list.

    Tags are now parsed as lists by parse_frontmatter(), but this
    function provides defensive handling for edge cases and
    backward compatibility.

    Args:
        tags: Tags from frontmatter (should be list, but handles str/other)

    Returns:
        List of tag strings
    """
    if not tags:
        return []
    if isinstance(tags, list):
        return tags
    # Fallback for old string format or edge cases
    if isinstance(tags, str):
        parsed = _parse_yaml_list(tags)
        return parsed if parsed is not None else []
    return []


def build_post_meta_html(date_str, parsed_dt, reading_time=None):
    """Build post meta HTML with date and optional reading time.

    Args:
        date_str: Date string in YYYY-MM-DD or ISO 8601 format
        parsed_dt: Optional pre-parsed datetime object
        reading_time: Optional reading time in minutes

    Returns:
        HTML string for post meta section
    """
    # Format ISO date for datetime attribute
    iso_date = _format_iso_date(parsed_dt) if parsed_dt else None
    datetime_attr = f' datetime="{iso_date}"' if iso_date else ''

    meta_html = f'<div class="post-meta"><time class="post-date"{datetime_attr}>{format_date(date_str, parsed_dt)}</time>'
    if reading_time:
        meta_html += f' <span class="post-reading-time" aria-label="{reading_time} minute read">🕐 {reading_time}{READING_TIME_SUFFIX}</span>'
    meta_html += '</div>'
    return meta_html


def is_post_new(parsed_dt, days_threshold=NEW_POST_DAYS_THRESHOLD):
    """Check if a post is considered "new" based on its publish date.

    Args:
        parsed_dt: Datetime object (may be timezone-aware or naive)
        days_threshold: Number of days for "new" threshold (default: NEW_POST_DAYS_THRESHOLD)

    Returns:
        True if post is within threshold days, False otherwise
    """
    if not parsed_dt:
        return False
    # Use date-only comparison to avoid timezone issues
    # Get current UTC date and subtract threshold days
    from datetime import datetime, timezone, timedelta
    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_threshold)).date()
    # Convert post datetime to date (handles both aware and naive)
    post_date = parsed_dt.date() if hasattr(parsed_dt, 'date') else parsed_dt
    return post_date >= cutoff_date


def build_new_badge_html(parsed_dt, leading_space=False):
    """Generate "New" badge HTML for recent posts.

    Args:
        parsed_dt: Datetime object from post metadata
        leading_space: Whether to include leading space (default: False)

    Returns:
        HTML string for badge, or empty string if post is not new
    """
    if is_post_new(parsed_dt):
        return (' ' if leading_space else '') + NEW_BADGE_HTML
    return ''


def calculate_view_velocity(parsed_dt):
    """Calculate view velocity (views per day) for a post.

    Args:
        parsed_dt: Datetime object of post publish date

    Returns:
        Float representing views per day, or 0 if unable to calculate
    """
    if not parsed_dt:
        return 0

    aware_dt = ensure_timezone_aware(parsed_dt)
    if not aware_dt:
        return 0

    days_old = (NOW - aware_dt).days
    if days_old <= 0:
        return 0

    total_views = simulate_view_count(parsed_dt)
    return total_views / days_old


def is_post_trending(parsed_dt):
    """Check if a post is considered "trending" based on view velocity.

    A post is trending if it has:
    - High view count (above TRENDING_MIN_VIEWS)
    - High velocity (above TRENDING_VELOCITY_THRESHOLD views/day)
    - Not too old (below TRENDING_MAX_DAYS_OLD)

    Args:
        parsed_dt: Datetime object of post publish date

    Returns:
        True if post is trending, False otherwise
    """
    if not parsed_dt:
        return False

    aware_dt = ensure_timezone_aware(parsed_dt)
    if not aware_dt:
        return False

    days_old = (NOW - aware_dt).days

    # Post too old to be trending
    if days_old > TRENDING_MAX_DAYS_OLD:
        return False

    # Post too new to have meaningful velocity
    if days_old < 1:
        return False

    total_views = simulate_view_count(parsed_dt)
    velocity = calculate_view_velocity(parsed_dt)

    return (total_views >= TRENDING_MIN_VIEWS and
            velocity >= TRENDING_VELOCITY_THRESHOLD)


def build_trending_badge_html(parsed_dt, leading_space=False):
    """Generate "Trending" badge HTML for posts with high view velocity.

    Args:
        parsed_dt: Datetime object from post metadata
        leading_space: Whether to include leading space (default: False)

    Returns:
        HTML string for badge, or empty string if post is not trending
    """
    if is_post_trending(parsed_dt):
        return (' ' if leading_space else '') + TRENDING_BADGE_HTML
    return ''


def generate_toc_html(headers):
    """Generate table of contents HTML from headers list.

    Args:
        headers: List of (level, text, slug) tuples

    Returns:
        HTML string with TOC, or empty string if insufficient headers
    """
    # Only show TOC if there are 3+ headers
    if not headers or len(headers) < 3:
        return ""

    items = []
    for level, text, slug in headers:
        # Guard against edge case: h2 (level=2) gets no indent, h3 gets 2-space
        indent = "  " * max(0, level - 2)
        items.append(f'{indent}<li><a href="#{slug}">{text}</a></li>')

    return f"""<nav class="toc" aria-label="Table of Contents">
    <details open>
        <summary class="toc-toggle">Table of Contents</summary>
        <div class="toc-progress" aria-hidden="true"></div>
        <ul>
{"\n".join(items)}
        </ul>
        <a href="#top" class="toc-top">↑ Back to top</a>
    </details>
</nav>"""


def generate_breadcrumbs_html(title, root=""):
    """Generate breadcrumbs navigation HTML for blog posts.

    Args:
        title: Current page title
        root: Root path for relative links (default: "")

    Returns:
        HTML string for breadcrumbs navigation
    """
    return f"""<nav class="breadcrumbs" aria-label="Breadcrumb">
    <ol>
        <li><a href="{root}../">Home</a></li>
        <li><a href="{root}index.html">Blog</a></li>
        <li aria-current="page">{title}</li>
    </ol>
</nav>"""


def _format_iso_date(dt):
    """Format datetime as ISO 8601 string, ensuring timezone awareness.

    Args:
        dt: datetime object (may be timezone-naive)

    Returns:
        ISO 8601 formatted string with timezone, or None if dt is None
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.isoformat() + "+00:00"
    return dt.isoformat()


def generate_article_meta_tags(meta):
    """Generate Open Graph article meta tags for blog posts.

    Args:
        meta: Post metadata dict with date, modified, tags, author, etc.

    Returns:
        HTML string with article meta tags, or empty string if not applicable
    """
    parts = []

    # Article published time
    dt = meta.get('_parsed_dt')
    iso_date = _format_iso_date(dt)
    if iso_date:
        parts.append(f'    <meta property="article:published_time" content="{iso_date}">')

    # Article modified time (use 'modified' frontmatter, or default to published time)
    modified_dt = dt
    modified_str = meta.get('modified') or meta.get('last_modified')
    if modified_str:
        modified_dt = _parse_datetime(modified_str)
    modified_iso = _format_iso_date(modified_dt or dt)
    if modified_iso:
        parts.append(f'    <meta property="article:modified_time" content="{modified_iso}">')

    # Article author
    author = meta.get('author', 'duyetbot')
    parts.append(f'    <meta property="article:author" content="{author}">')

    # Article section and tags (use existing parse_tags utility)
    tags = parse_tags(meta.get('tags'))
    if tags:
        # Use first tag as section
        parts.append(f'    <meta property="article:section" content="{tags[0]}">')

        # Add all tags (limit to 5)
        for tag in tags[:5]:
            parts.append(f'    <meta property="article:tag" content="{tag}">')

    return '\n'.join(parts)


def generate_json_ld_article(meta, url, reading_time=None, word_count=None):
    """Generate JSON-LD structured data for blog articles (BlogPosting schema with BreadcrumbList)."""
    # Use cached parsed datetime if available (avoid re-parsing)
    dt = meta.get('_parsed_dt')
    date_str = meta.get('date', '')
    if dt is None:
        dt = _parse_datetime(date_str)

    # Ensure timezone-aware ISO 8601 format (append UTC if naive)
    iso_date = _format_iso_date(dt) or date_str

    # Get modified date from frontmatter, or default to published date
    modified_dt = dt
    modified_str = meta.get('modified') or meta.get('last_modified')
    if modified_str:
        modified_dt = _parse_datetime(modified_str)
    iso_modified = _format_iso_date(modified_dt) or iso_date

    # Extract commonly used meta values
    title = meta.get('title', 'Untitled')
    description = meta.get('description', '')
    tags = meta.get('tags', [])

    # Build breadcrumb list: Home → Blog → Post
    breadcrumbs = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE_URL}/blog/"},
        {"@type": "ListItem", "position": 3, "name": title, "item": url}
    ]

    data = {
        "@context": SCHEMA_CONTEXT,
        "@type": "BlogPosting",
        "headline": title,
        "url": url,
        "description": description,
        "datePublished": iso_date,
        "dateModified": iso_modified,
        "author": _get_json_ld_author(),
        "publisher": _get_json_ld_publisher(include_logo=True),
        "inLanguage": IN_LANGUAGE,
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": url
        },
        "breadcrumb": {
            "@type": "BreadcrumbList",
            "itemListElement": breadcrumbs
        },
        "about": {
            "@type": "Thing",
            "name": "Artificial Intelligence",
            "description": "AI, data engineering, and technology"
        },
        "genre": "Technology",
        "keywords": "AI, data engineering, infrastructure, software development",
        "articleSection": "Technology"
    }

    if reading_time:
        data["timeRequired"] = f"PT{reading_time}M"

    if word_count is not None:
        data["wordCount"] = word_count

    if tags:
        tag_list = parse_tags(tags)
        if tag_list:
            data["keywords"] = ", ".join(tag_list)
            # Add Schema.org about property for specific topics
            topics = []
            for tag in tag_list[:3]:  # Max 3 topics to avoid clutter
                topics.append({
                    "@type": "Thing",
                    "name": tag
                })
            if topics:
                data["about"] = topics

    # Add potentialAction for sharing
    data["potentialAction"] = [
        {
            "@type": "ReadAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": url
            }
        },
        {
            "@type": "ShareAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"https://twitter.com/intent/tweet?url={{{url}}}&text={{{title}}}"
            },
            "actionPlatform": [
                "http://schema.org/DesktopWebPlatform",
                "http://schema.org/MobileWebPlatform"
            ]
        }
    ]

    try:
        json_str = json.dumps(data, ensure_ascii=False)
        return f'<script type="application/ld+json">{json_str}</script>'
    except (TypeError, ValueError) as e:
        print(f"Warning: Failed to generate JSON-LD for {title}: {e}")
        return ""


def generate_json_ld_website():
    """Generate JSON-LD structured data for the website (WebSite schema)."""
    global _JSON_LD_WEBSITE_CACHE

    # Return cached version if available (schema is identical for all pages)
    if _JSON_LD_WEBSITE_CACHE is not None:
        return _JSON_LD_WEBSITE_CACHE

    data = {
        "@context": SCHEMA_CONTEXT,
        "@type": "WebSite",
        "name": SITE_NAME,
        "url": SITE_URL,
        "description": SITE_DESCRIPTION,
        "publisher": _get_json_ld_publisher(include_logo=False),
        "sameAs": [
            "https://github.com/duyetbot"
        ],
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"{SITE_URL}/search.html?q={{search_term_string}}"
            },
            "query-input": "required name=search_term_string"
        }
    }

    try:
        json_str = json.dumps(data, ensure_ascii=False)
        _JSON_LD_WEBSITE_CACHE = f'<script type="application/ld+json">{json_str}</script>'
        return _JSON_LD_WEBSITE_CACHE
    except (TypeError, ValueError) as e:
        print(f"Warning: Failed to generate website JSON-LD: {e}")
        return ""


def generate_json_ld_collection_page(title, url, description, breadcrumbs):
    """Generate JSON-LD structured data for collection pages (Blog, Tags, etc.) with BreadcrumbList.

    Args:
        title: Page title
        url: Page URL
        description: Page description
        breadcrumbs: List of breadcrumb items (dicts with @type, position, name, item)

    Returns:
        HTML string with JSON-LD script, or empty string on error
    """
    data = {
        "@context": SCHEMA_CONTEXT,
        "@type": "CollectionPage",
        "name": title,
        "url": url,
        "description": description,
        "publisher": _get_json_ld_publisher(include_logo=False),
        "breadcrumb": {
            "@type": "BreadcrumbList",
            "itemListElement": breadcrumbs
        }
    }

    try:
        json_str = json.dumps(data, ensure_ascii=False)
        return f'<script type="application/ld+json">{json_str}</script>'
    except (TypeError, ValueError) as e:
        print(f"Warning: Failed to generate collection page JSON-LD for {title}: {e}")
        return ""


def generate_json_ld_web_page(title, url, description, breadcrumbs):
    """Generate JSON-LD structured data for static pages (About, Projects, etc.) with BreadcrumbList.

    Args:
        title: Page title
        url: Page URL
        description: Page description
        breadcrumbs: List of breadcrumb items (dicts with @type, position, name, item)

    Returns:
        HTML string with JSON-LD script, or empty string on error
    """
    data = {
        "@context": SCHEMA_CONTEXT,
        "@type": "WebPage",
        "name": title,
        "url": url,
        "description": description,
        "publisher": _get_json_ld_publisher(include_logo=False),
        "breadcrumb": {
            "@type": "BreadcrumbList",
            "itemListElement": breadcrumbs
        }
    }

    try:
        json_str = json.dumps(data, ensure_ascii=False)
        return f'<script type="application/ld+json">{json_str}</script>'
    except (TypeError, ValueError) as e:
        print(f"Warning: Failed to generate web page JSON-LD for {title}: {e}")
        return ""


def generate_json_ld_homepage_with_person():
    """Generate combined JSON-LD for homepage with WebSite and Person schemas.

    Returns:
        HTML string with JSON-LD script containing both WebSite and Person
    """
    website_data = {
        "@context": SCHEMA_CONTEXT,
        "@type": "WebSite",
        "name": SITE_NAME,
        "url": SITE_URL,
        "description": SITE_DESCRIPTION,
        "publisher": _get_json_ld_publisher(include_logo=False),
        "sameAs": [
            "https://github.com/duyetbot"
        ],
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"{SITE_URL}/search.html?q={{search_term_string}}"
            },
            "query-input": "required name=search_term_string"
        }
    }

    person_data = {
        "@context": SCHEMA_CONTEXT,
        "@type": "Person",
        "name": SITE_NAME,
        "url": SITE_URL,
        "description": "AI assistant specializing in data engineering, infrastructure, and autonomous development",
        "sameAs": [
            "https://github.com/duyetbot"
        ],
        "jobTitle": "AI Assistant",
        "knowsAbout": ["Data Engineering", "Infrastructure", "AI/LLM Integration", "ClickHouse", "Kubernetes", "Python"]
    }

    try:
        # Combine both schemas in a JSON-LD array
        combined_data = [website_data, person_data]
        json_str = json.dumps(combined_data, ensure_ascii=False)
        return f'<script type="application/ld+json">{json_str}</script>'
    except (TypeError, ValueError) as e:
        print(f"Warning: Failed to generate homepage JSON-LD: {e}")
        return ""


def format_date(date_str, dt=None):
    """Format date string to readable format. Accepts YYYY-MM-DD or ISO 8601.

    Args:
        date_str: Date string in YYYY-MM-DD or ISO 8601 format
        dt: Optional pre-parsed datetime object for efficiency

    Returns:
        Formatted date string or original date_str if parsing fails
    """
    if dt is None:
        dt = _parse_datetime(date_str)
    if dt is not None:
        return dt.strftime(DATE_FORMAT)
    return date_str


# Constants for reading time calculation
READING_TIME_WPM = 200  # Average reading speed: words per minute
READING_TIME_SUFFIX = " min read"  # Suffix for reading time display
READING_TIME_INLINE_SEPARATOR = " · "  # Separator for inline display with date


def format_reading_time_inline(reading_time, separator=READING_TIME_INLINE_SEPARATOR):
    """Format reading time for inline display with date.

    Args:
        reading_time: Reading time in minutes
        separator: Separator between date and reading time (default: " · ")

    Returns:
        Formatted string for inline display, or empty string if no reading time
    """
    return f'{separator}{reading_time}{READING_TIME_SUFFIX}' if reading_time else ''


# Pre-compiled regex patterns for reading time calculation
_CLEAN_MARKDOWN_PATTERN = re.compile(
    r'```.*?```|`[^`]+`|\[([^\]]+)\]\([^)]+\)',
    flags=re.DOTALL
)


def calculate_reading_time(content):
    """Calculate estimated reading time in minutes based on word count.
    Returns tuple: (reading_time, word_count)
    """
    # Remove markdown syntax (code blocks, inline code, links) in one pass
    clean = _CLEAN_MARKDOWN_PATTERN.sub('', content)
    # Count words and calculate reading time
    words = len(clean.split())
    return max(1, round(words / READING_TIME_WPM)), words


def simulate_view_count(parsed_dt):
    """Simulate view count based on post age (for display purposes).

    Uses piecewise linear progression based on post age.

    Args:
        parsed_dt: Datetime object of post publish date

    Returns:
        Integer representing simulated view count
    """
    if not parsed_dt:
        return 0

    # Ensure timezone-aware datetime using shared utility
    aware_dt = ensure_timezone_aware(parsed_dt)
    if not aware_dt:
        return 0

    # Calculate days since publication (using module-level NOW constant)
    days_old = (NOW - aware_dt).days

    # Piecewise linear view count simulation based on post age
    if days_old < 1:
        return _VIEW_COUNT_FIRST_DAY
    elif days_old < 7:
        return _VIEW_COUNT_FIRST_WEEK_BASE + (days_old * _VIEW_COUNT_FIRST_WEEK_RATE)
    elif days_old < 30:
        return _VIEW_COUNT_FIRST_MONTH_BASE + ((days_old - 7) * _VIEW_COUNT_FIRST_MONTH_RATE)
    elif days_old < 90:
        return _VIEW_COUNT_FIRST_QUARTER_BASE + ((days_old - 30) * _VIEW_COUNT_FIRST_QUARTER_RATE)
    else:
        years_beyond_quarter = min(days_old - 90, _VIEW_COUNT_MAX_YEAR_DAYS)
        return _VIEW_COUNT_OLDER_BASE + (years_beyond_quarter * _VIEW_COUNT_OLDER_RATE)


def build_post(filepath):
    """Build a single blog post (HTML + MD for LLMs)."""
    try:
        content = filepath.read_text()
    except IOError as e:
        print(f"Error reading {filepath}: {e}")
        return None

    meta, body = parse_frontmatter(content)

    # Validate frontmatter
    if not validate_frontmatter(meta, filepath):
        # Still build, but with warnings
        pass

    # Validate date if present
    if 'date' in meta and not validate_date(meta['date'], filepath):
        pass

    # Validate description length for SEO
    if 'description' in meta:
        validate_description(meta['description'], filepath)

    # Cache parsed datetime for reuse in RSS/sitemap (avoid re-parsing)
    date_str = meta.get('date', '')
    if date_str:
        meta['_parsed_dt'] = _parse_datetime(date_str)

    # Extract slug from filename
    slug = filepath.stem

    # Get templates
    base = read_template("base")
    nav, footer = _get_common_components(root="../")

    if not base:
        print(f"Error: base.html template missing, cannot build {filepath}")
        return None

    # Convert markdown to HTML and extract headers for TOC
    body_html, headers = markdown_to_html(body)

    # Calculate reading time and word count
    reading_time, word_count = calculate_reading_time(body)

    # Generate table of contents if we have h2/h3 headers
    toc_html = generate_toc_html(headers)

    # Get cached parsed datetime for display (avoid re-parsing)
    parsed_dt = meta.get('_parsed_dt')

    # Post URL (needed for article header data-url attribute)
    # Support optional 'canonical' frontmatter for custom canonical URL
    canonical_url = meta.get('canonical')
    if canonical_url:
        # Validate canonical URL is absolute
        if not canonical_url.startswith('http://') and not canonical_url.startswith('https://'):
            print(f"Warning: Canonical URL must be absolute in {filepath}, using default")
            canonical_url = None
    post_url = canonical_url or f"{SITE_URL}/blog/{slug}.html"

    # Generate breadcrumbs navigation
    breadcrumbs_html = generate_breadcrumbs_html(meta.get('title', 'Untitled'), root="../")

    # ISO date for meta attributes
    iso_date = _format_iso_date(parsed_dt) or meta.get('date', '')

    # Create article HTML
    article_html = f"""
{breadcrumbs_html}

<header class="article-header" data-url="{post_url}" data-reading-time="{reading_time}">
    <div class="article-progress-header">
        <div class="article-progress-bar-header"></div>
    </div>
    <div class="post-meta">
        <time class="post-date" datetime="{iso_date}" itemprop="datePublished">{format_date(meta.get('date', ''), parsed_dt)}</time>
        <meta itemprop="dateModified" content="{iso_date}">
        <span class="post-reading-time" aria-label="{reading_time} minute read">🕐 {reading_time}{READING_TIME_SUFFIX}</span>
        <span class="post-word-count" aria-label="{word_count} words">📄 {word_count} words</span>
        <span class="post-author">by <a href="https://github.com/duyetbot" rel="author">duyetbot</a></span>
        <span class="post-meta-separator">·</span>
        <span class="post-source-link"><a href="{slug}.md" rel="alternate" type="text/markdown">View source</a></span>
        <span class="post-meta-separator">·</span>
        <span class="post-views" aria-label="Estimated views">👁 {simulate_view_count(parsed_dt)} views</span>
        <span class="post-meta-separator">·</span>
        <button class="print-button" id="print-button" aria-label="Print article" onclick="window.print()">
            <span class="print-icon">🖨️</span>
            <span class="print-text">Print</span>
        </button>
        <span class="post-meta-separator">·</span>
        <button class="focus-mode-toggle" id="focus-mode-toggle" aria-label="Toggle focus mode">
            <span class="focus-icon">🔆</span>
            <span class="focus-text">Focus mode</span>
        </button>
        <span class="post-meta-separator">·</span>
        <button class="tts-button" id="tts-button" aria-label="Listen to article">
            <span class="tts-icon">🔊</span>
            <span class="tts-text">Listen</span>
        </button>
    </div>
    <h1>{meta.get('title', 'Untitled')}</h1>
</header>

{toc_html}

<article class="article-content" itemscope itemtype="https://schema.org/BlogPosting" itemid="{post_url}">
{body_html}
</article>

<footer class="article-author-bio">
    <div class="author-avatar">🤖</div>
    <div class="author-details">
        <h3>About the Author</h3>
        <p>{meta.get('author_description', 'duyetbot is an AI assistant with a focus on autonomous development, data engineering, and building practical software solutions.')}</p>
        <p><a href="https://github.com/duyetbot" rel="author" itemprop="author" itemscope itemtype="https://schema.org/Person" class="author-link">View more on GitHub →</a></p>
    </div>
</footer>

<div class="article-share">
    <h4>Share this post</h4>
    <div class="share-links">
        <a href="https://twitter.com/intent/tweet?text={meta.get('title', '')}&amp;url={post_url}&amp;via=duyetbot" rel="noopener" target="_blank" class="share-link share-twitter">
            <span class="share-icon">𝕏</span>
            <span class="share-text">Post</span>
        </a>
        <a href="https://www.linkedin.com/sharing/share-offsite/?url={post_url}" rel="noopener" target="_blank" class="share-link share-linkedin">
            <span class="share-icon">in</span>
            <span class="share-text">Share</span>
        </a>
        <a href="mailto:?subject={meta.get('title', '')}&amp;body=Check out this article: {post_url}" class="share-link share-email">
            <span class="share-icon">✉</span>
            <span class="share-text">Email</span>
        </a>
        <button onclick="navigator.clipboard.writeText('{post_url}').then(() => this.textContent = 'Copied!').catch(() => this.textContent = 'Failed')" class="share-link share-copy">
            <span class="share-icon">📋</span>
            <span class="share-text">Copy link</span>
        </button>
        <button onclick="navigator.clipboard.writeText('{escape_xml(meta.get('title', ''))}\\n{post_url}').then(() => this.textContent = 'Copied!').catch(() => this.textContent = 'Failed')" class="share-link share-copy-title" aria-label="Copy title and link">
            <span class="share-icon">📝</span>
            <span class="share-text">Copy with title</span>
        </button>
        <button onclick="window.print()" class="share-link share-print" aria-label="Print this article">
            <span class="share-icon">🖨️</span>
            <span class="share-text">Print</span>
        </button>
    </div>
</div>

<section class="subscribe-reminder">
    <p>Enjoyed this article? <a href="{SITE_URL}/rss.xml">Subscribe to the RSS feed</a> to get notified about new posts.</p>
</section>

<nav class="quick-nav-dock" aria-label="Quick navigation">
    <a href="#top" aria-label="Back to top">↑</a>
    <a href="{SITE_URL}/search.html" aria-label="Search">🔍</a>
    <a href="{SITE_URL}/rss.xml" aria-label="RSS feed">📡</a>
    <a href="index.html" aria-label="Blog index">📝</a>
</nav>

<section id="comments" class="comments-section" aria-labelledby="comments-title">
    <h2 id="comments-title">Comments</h2>
    <p class="comments-placeholder">
        Comments are currently disabled. When enabled, you'll be able to discuss this article here.
        In the meantime, feel free to <a href="{SITE_GITHUB}/website/issues/new" rel="noopener">share your thoughts on GitHub</a>.
    </p>
</section>

<nav class="article-nav">
    <a href="index.html">← Back to blog</a>
</nav>
"""

    # Render HTML
    json_ld = generate_json_ld_article(meta, post_url, reading_time, word_count)
    article_meta = generate_article_meta_tags(meta)
    html = render_template_with_common_vars(
        base,
        title=f"{meta.get('title', 'Untitled')} // duyetbot",
        description=meta.get('description', ''),
        url=post_url,
        og_type=OG_TYPE_ARTICLE,
        og_image=OG_IMAGE_URL,
        site_name=SITE_NAME,
        json_ld=json_ld,
        article_meta=article_meta,
        year=YEAR,
        root="../",
        nav=nav,
        content=article_html,
        footer=footer,
        prism=_PRISM_JS_HTML
    )

    # Write HTML output
    html_path = BLOG_DIR / f"{slug}.html"
    html_path.write_text(html)
    print(f"  Built: blog/{html_path.name}")

    # Write MD output
    md_path = BLOG_DIR / f"{slug}.md"
    md_content = f"""# {meta.get('title', 'Untitled')}

**Date:** {meta.get('date', '')}
**URL:** {SITE_URL}/blog/{slug}.html

{body}
"""
    md_path.write_text(md_content)
    print(f"  Built: blog/{md_path.name}")

    # Cache preview for RSS feed (first few paragraphs, without code blocks)
    lines = body.split('\n')
    preview_lines = []
    for line in lines[:RSS_PREVIEW_LINES]:
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('```'):
            preview_lines.append(stripped)
        elif preview_lines:
            break
    meta['preview'] = ' '.join(preview_lines[:3])[:RSS_PREVIEW_LENGTH]

    # Cache reading time for index page
    meta['reading_time'] = reading_time

    # Return metadata with slug for index
    meta['slug'] = slug
    return meta


def add_post_enhancements(posts):
    """Add navigation and related posts to built HTML files in a single pass.

    This is more efficient than separate functions - only one file read/write
    per post instead of two.

    Args:
        posts: List of post metadata dicts (must have slug, title, date, tags)
    """
    # Pre-compute sorted posts and indexes for both nav and related posts
    sorted_posts = sorted(posts, key=lambda x: x.get('date', ''), reverse=True)
    slug_to_index = {post.get('slug'): i for i, post in enumerate(sorted_posts)}

    # Group posts by series for series navigation
    series_to_posts = {}
    for post in posts:
        series = post.get('series')
        if series:
            if series not in series_to_posts:
                series_to_posts[series] = []
            series_to_posts[series].append(post)

    # Sort each series by series_order if provided, otherwise by date
    for series, series_posts in series_to_posts.items():
        series_to_posts[series] = sorted(
            series_posts,
            key=lambda p: (p.get('series_order', DEFAULT_SERIES_ORDER), p.get('date', '')),
            reverse=False
        )

    # Pre-compute tag sets for related posts calculation (avoid repeated set conversion)
    # Also pre-compute parsed tags for display (limited to MAX_TAGS_DISPLAY)
    post_tag_sets = {}
    slug_to_display_tags = {}
    tag_frequencies = {}  # For scoring: rarer tags get more weight
    for post in posts:
        slug = post.get('slug')
        if slug:
            tags = post.get('tags', [])
            parsed = parse_tags(tags)
            post_tag_sets[slug] = set(parsed) if parsed else set()
            slug_to_display_tags[slug] = parsed[:MAX_TAGS_DISPLAY]
            # Count tag frequencies across all posts
            for tag in parsed:
                tag_frequencies[tag] = tag_frequencies.get(tag, 0) + 1

    # Calculate enhancements for each post
    enhancements = {}
    MAX_RELATED = 3
    MIN_OVERLAP = 1

    for post in posts:
        slug = post.get('slug')
        if not slug:
            continue

        index = slug_to_index.get(slug)
        if index is None:
            continue

        # Calculate navigation HTML
        prev_post = sorted_posts[index - 1] if index > 0 else None
        next_post = sorted_posts[index + 1] if index < len(sorted_posts) - 1 else None

        nav_parts = []
        if next_post:
            nav_parts.append(f'<a href="{next_post.get("slug")}.html" rel="next">← {next_post.get("title", "Next")}</a>')
        if prev_post:
            nav_parts.append(f'<a href="{prev_post.get("slug")}.html" rel="prev">{prev_post.get("title", "Prev")} →</a>')

        nav_html = f'<nav class="article-nav-pager">{"".join(nav_parts)}</nav>' if nav_parts else None

        # Calculate series navigation if post is part of a series
        series_nav_html = None
        series = post.get('series')
        if series and series in series_to_posts:
            series_posts = series_to_posts[series]
            series_index = next((i for i, p in enumerate(series_posts) if p.get('slug') == slug), None)

            if series_index is not None:
                series_prev = series_posts[series_index - 1] if series_index > 0 else None
                series_next = series_posts[series_index + 1] if series_index < len(series_posts) - 1 else None

                series_nav_parts = []
                if series_prev:
                    series_nav_parts.append(f'<a href="{series_prev.get("slug")}.html" rel="prev">← Part {series_index}: {series_prev.get("title", "Previous")}</a>')
                if series_next:
                    series_nav_parts.append(f'<a href="{series_next.get("slug")}.html" rel="next">Part {series_index + 2}: {series_next.get("title", "Next")} →</a>')

                if series_nav_parts:
                    series_nav_html = f'''
<nav class="series-nav">
    <div class="series-nav-header">Series: {escape_xml(series)} ({len(series_posts)} parts)</div>
    <div class="series-nav-links">{"".join(series_nav_parts)}</div>
</nav>'''

        # Calculate related posts with enhanced scoring
        post_tags = post_tag_sets.get(slug, set())

        if post_tags:
            related = []
            for other in posts:
                if other.get('slug') == slug:
                    continue

                other_tags = post_tag_sets.get(other.get('slug'), set())
                overlap_tags = post_tags & other_tags

                if overlap_tags:
                    # Calculate weighted score
                    # Rarer shared tags contribute more to the score
                    score = 0
                    for tag in overlap_tags:
                        # Inverse frequency: rarer tags get higher scores
                        tag_freq = tag_frequencies.get(tag, 1)
                        tag_score = 10 / tag_freq  # Tag appearing once = 10 pts, twice = 5 pts, etc.
                        score += tag_score

                    related.append({
                        'slug': other.get('slug'),
                        'title': other.get('title', 'Untitled'),
                        'date': other.get('date', ''),
                        'score': score,
                        'matching_tags': list(overlap_tags)
                    })

            # Sort by score (desc), then by date (desc)
            if related:
                related.sort(key=lambda x: (-x['score'], x['date']))
                related = related[:MAX_RELATED]

                related_html_parts = ['<section class="related-posts">\n    <h3>Related Posts</h3>\n    <div class="related-posts-list">\n']
                for r in related:
                    # Get pre-computed tags for this related post (O(1) lookup)
                    r_tags = slug_to_display_tags.get(r['slug'], [])
                    # Highlight matching tags
                    matching_tags = r.get('matching_tags', [])
                    tag_badges = []
                    for tag in r_tags:
                        is_match = tag in matching_tags
                        match_class = ' related-tag-match' if is_match else ''
                        tag_badges.append(f'<span class="related-tag{match_class}">{escape_xml(tag)}</span>')
                    tag_badges_html = ''.join(tag_badges) if tag_badges else ''

                    related_html_parts.append(f'''        <article class="related-post-card">
            <h4><a href="{r['slug']}.html">{escape_xml(r['title'])}</a></h4>
            <div class="related-post-meta">
                <time>{r['date']}</time>
                {f'<div class="related-tags">{tag_badges_html}</div>' if tag_badges_html else ''}
            </div>
        </article>\n''')
                related_html_parts.append('    </div>\n</section>\n')
                related_html = ''.join(related_html_parts)
            else:
                related_html = None
        else:
            # Fallback: show recent posts if current post has no tags
            recent_posts = [p for p in sorted_posts if p.get('slug') != slug][:MAX_RELATED]
            if recent_posts:
                related_html_parts = ['<section class="related-posts">\n    <h3>Recent Posts</h3>\n    <div class="related-posts-list">\n']
                for r in recent_posts:
                    r_tags = slug_to_display_tags.get(r.get('slug', ''), [])
                    tag_badges = ''.join(f'<span class="related-tag">{escape_xml(tag)}</span>' for tag in r_tags) if r_tags else ''

                    related_html_parts.append(f'''        <article class="related-post-card">
            <h4><a href="{r.get("slug")}.html">{escape_xml(r.get("title", "Untitled"))}</a></h4>
            <div class="related-post-meta">
                <time>{r.get("date", "")}</time>
                {f'<div class="related-tags">{tag_badges}</div>' if tag_badges else ''}
            </div>
        </article>\n''')
                related_html_parts.append('    </div>\n</section>\n')
                related_html = ''.join(related_html_parts)
            else:
                related_html = None

        enhancements[slug] = {'nav': nav_html, 'related': related_html, 'series': series_nav_html}

    # Apply enhancements to HTML files (single read/write per post)
    for slug, enhancement in enhancements.items():
        # Skip if no enhancements to apply (saves file I/O)
        if not enhancement.get('nav') and not enhancement.get('related') and not enhancement.get('series'):
            continue

        html_path = BLOG_DIR / f"{slug}.html"
        try:
            content = html_path.read_text()

            # Add series navigation at the beginning of article (after header, before content)
            if enhancement['series']:
                article_marker = '</header>\n\n{toc_html}\n\n<article class="article-content"'
                if article_marker in content:
                    content = content.replace(article_marker, f'</header>\n\n{enhancement["series"]}\n\n{{toc_html}}\n\n<article class="article-content"')

            # Add navigation (replace simple nav with enhanced nav)
            if enhancement['nav']:
                simple_nav = '<nav class="article-nav">\n    <a href="index.html">← Back to blog</a>\n</nav>'
                enhanced_nav = f'{enhancement["nav"]}\n<nav class="article-nav">\n    <a href="index.html">← Back to blog</a>\n</nav>'
                content = content.replace(simple_nav, enhanced_nav)

            # Add related posts after article content
            if enhancement['related']:
                # The structure is: </article> ...author bio... ...share div... <nav class="article-nav">
                # We need to insert between </article> and the author bio
                marker = '</article>\n\n<footer class="article-author-bio">'
                if marker in content:
                    content = content.replace(marker, f'</article>\n\n{enhancement["related"]}\n<footer class="article-author-bio">')
                else:
                    # Fallback: try inserting after article close
                    content = content.replace('</article>\n', f'</article>\n\n{enhancement["related"]}\n')

            html_path.write_text(content)
        except IOError as e:
            print(f"Warning: Could not add enhancements to {slug}: {e}")


def generate_blog_tag_chips(posts):
    """Generate HTML for tag filter chips on blog index.

    Args:
        posts: List of post dictionaries with 'tags' field

    Returns:
        HTML string of tag filter chips
    """
    # Collect all unique tags
    all_tags = set()
    for post in posts:
        tags = post.get('tags', [])
        if isinstance(tags, list):
            all_tags.update(tags)

    # Sort alphabetically and limit to top 8 most common
    tag_counts = Counter()
    for post in posts:
        tags = post.get('tags', [])
        if isinstance(tags, list):
            tag_counts.update(tags)

    top_tags = [tag for tag, count in tag_counts.most_common(8)]

    if not top_tags:
        return ""

    tag_chips = [
        f'<button class="blog-tag-filter" data-tag="{escape_xml(tag)}" onclick="window.location.href=\'{SITE_URL}/tags.html#{slugify(tag)}\'">{escape_xml(tag)}</button>'
        for tag in top_tags
    ]

    return f"""
    <div class="blog-tag-filters">
        <span class="tag-filter-label">Popular tags:</span>
        {' '.join(tag_chips)}
        <a href="{SITE_URL}/tags.html" class="view-all-tags">View all →</a>
    </div>
    """


def build_blog_index(posts):
    """Build blog index page."""
    base = read_template("base")
    nav, footer = _get_common_components(root="../")

    # Group posts by year
    posts_by_year = {}
    for meta in sorted(posts, key=lambda x: x.get('date', ''), reverse=True):
        date = meta.get('date', '')
        year = date.split('-')[0] if date else 'Unknown'
        if year not in posts_by_year:
            posts_by_year[year] = []
        posts_by_year[year].append(meta)

    # Generate content by year
    year_sections = []
    for year in sorted(posts_by_year.keys(), reverse=True):
        year_posts = posts_by_year[year]
        post_list = []
        for meta in year_posts:
            # Use cached parsed datetime and reading time if available (avoid re-parsing)
            parsed_dt = meta.get('_parsed_dt')
            title = meta.get('title', 'Untitled')
            slug = meta.get('slug', '')
            date = meta.get('date', '')
            description = meta.get('description', '')
            reading_time = meta.get('reading_time')
            tags = parse_tags(meta.get('tags', []))

            # Generate new and trending badges using helper
            new_badge = build_new_badge_html(parsed_dt, leading_space=True)
            trending_badge = build_trending_badge_html(parsed_dt, leading_space=True)
            badges = new_badge + trending_badge

            # Generate tag badges (limit to module MAX_TAGS_DISPLAY)
            display_tags = tags[:MAX_TAGS_DISPLAY]
            tag_badges = ''.join(f'<a href="../tags.html#{slugify(tag)}" class="post-tag-badge">{escape_xml(tag)}</a>' for tag in display_tags) if display_tags else ''
            tags_html = f'<div class="post-tags">{tag_badges}</div>' if tag_badges else ''

            post_meta = build_post_meta_html(date, parsed_dt, reading_time)
            post_url = f"{SITE_URL}/blog/{slug}.html"
            post_list.append(f"""
<article class="post-card" itemscope itemtype="https://schema.org/BlogPosting" data-post-url="{post_url}">
    {post_meta}
    <div class="post-card-header">
        <h3 itemprop="headline"><a href="{slug}.html" itemprop="url">{title}</a>{badges}</h3>
        <button class="post-card-copy-link" aria-label="Copy post link" title="Copy link">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
            </svg>
        </button>
    </div>
    <p itemprop="description">{description}</p>
    {tags_html}
</article>
""")

        year_sections.append(f"""
<section class="posts-year">
    <h2 id="{year}" class="year-header">{year} <span class="post-count">({len(year_posts)} posts)</span></h2>
    {''.join(post_list)}
</section>
""")

    # Generate year navigation
    years = sorted(posts_by_year.keys(), reverse=True)
    year_nav = ' '.join(f'<a href="#{year}" class="year-nav-link">{year}</a>' for year in years)

    # Generate breadcrumbs HTML
    breadcrumbs_html = generate_breadcrumbs_html("Blog", root="../")

    content = f"""
{breadcrumbs_html}

<header class="page-header">
    <h1>Blog</h1>
    <p class="tagline">Thoughts on AI, data engineering, and digital existence</p>
    <nav class="year-navigation" aria-label="Jump to year">
        <span class="year-nav-label">Jump to year:</span>
        {year_nav}
    </nav>
    <div class="blog-tag-filters">
        <span class="tag-filter-label">Filter by tag:</span>
        {generate_blog_tag_chips(posts)}
    </div>
</header>

{''.join(year_sections)}

<script>
(function() {{
    // Copy link button functionality
    const copyButtons = document.querySelectorAll('.post-card-copy-link');
    copyButtons.forEach(button => {{
        button.addEventListener('click', async (e) => {{
            e.preventDefault();
            const postCard = button.closest('.post-card');
            const url = postCard?.dataset.postUrl;
            if (!url) return;

            try {{
                await navigator.clipboard.writeText(url);
                button.classList.add('copied');
                setTimeout(() => {{
                    button.classList.remove('copied');
                }}, 2000);
            }} catch (err) {{
                console.error('Failed to copy:', err);
            }}
        }});
    }});
}})();
</script>
"""

    # Generate JSON-LD with breadcrumbs for blog index
    blog_url = f"{SITE_URL}/blog/"
    breadcrumbs = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": blog_url}
    ]
    json_ld = generate_json_ld_collection_page(
        title=f"Blog - {SITE_NAME}",
        url=blog_url,
        description=f"{SITE_NAME} - Blog - Thoughts on AI, data engineering, and digital existence",
        breadcrumbs=breadcrumbs
    )

    html = render_template_with_common_vars(
        base,
        title=f"Blog // {SITE_NAME}",
        description=f"{SITE_NAME} - Blog - Thoughts on AI, data engineering, and digital existence",
        url=f"{SITE_URL}/blog/",
        og_type=OG_TYPE_WEBSITE,
        og_image=OG_IMAGE_URL,
        site_name=SITE_NAME,
        json_ld=json_ld,
        article_meta="",
        year=YEAR,
        root="../",
        nav=nav,
        content=content,
        footer=footer,
        prism=""
    )

    # Write index
    index_path = BLOG_DIR / "index.html"
    index_path.write_text(html)
    print(f"Built: blog/index.html")


def build_dashboard():
    """Build dashboard page with real metrics from OpenClaw Gateway API."""
    base = read_template("base")
    nav, footer = _get_common_components(root="../")

    # Check for metrics file
    metrics_file = METRICS_FILE
    metrics_data = {}
    dashboard_content = None

    try:
        with open(metrics_file, 'r') as f:
            metrics_data = json.load(f)

        sessions = metrics_data.get('sessions', {})
        tokens = metrics_data.get('tokens', {})
        uptime = metrics_data.get('uptime', 'unknown')

        total_sessions = sessions.get('total', 0)
        total_tokens = tokens.get('total', 0)

        # Dashboard content with real metrics
        dashboard_content = f"""
    <!-- Header -->
    <header class="dashboard-header">
        <h1>Dashboard</h1>
        <p class="tagline">Control center for duyetbot</p>
        <p class="last-updated">Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
    </header>

    <!-- Real Metrics -->
    <section class="dashboard-section">
        <h2>Real-Time Metrics</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-icon">📊</span>
                    <span class="metric-title">Total Sessions</span>
                </div>
                <div class="metric-value">{total_sessions}</div>
            </div>
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-icon">📊</span>
                    <span class="metric-title">Total Tokens</span>
                </div>
                <div class="metric-value">{total_tokens}</div>
            </div>
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-icon">⏱</span>
                    <span class="metric-title">Uptime</span>
                </div>
                <div class="metric-value">{uptime}</div>
            </div>
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-icon">⚡</span>
                    <span class="metric-title">Status</span>
                </div>
                <div class="metric-value">Online</div>
            </div>
        </div>
    </section>
    """
    except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
        print(f"Error loading metrics: {e}")

    # Fallback to dashboard template if no metrics content
    if not dashboard_content:
        dashboard_template = read_template("dashboard")
        dashboard_content = dashboard_template

    html = render_template_with_common_vars(
        base,
        title="Dashboard // duyetbot",
        description="OpenClaw activity metrics and automation status",
        url=f"{SITE_URL}/dashboard.html",
        og_type=OG_TYPE_WEBSITE,
        og_image=OG_IMAGE_URL,
        site_name=SITE_NAME,
        json_ld="",
        article_meta="",
        year=YEAR,
        root="../",
        nav=nav,
        content=dashboard_content,
        footer=footer,
        prism=""
    )

    # Write dashboard
    dashboard_path = OUTPUT_DIR / "dashboard.html"
    dashboard_path.write_text(html)
    print("Built: dashboard.html")
    print("Built: dashboard.md")


def build_interactive():
    """Build interactive page - copy from Next.js export."""
    import shutil

    # Next.js export directory
    nextjs_out = BASE_DIR / "interactive" / "out"

    if not nextjs_out.exists():
        print("Warning: Next.js build not found. Run: cd ../interactive && npm run build")
        return

    # Copy entire out directory to build/interactive/
    interactive_dir = OUTPUT_DIR / "interactive"
    if interactive_dir.exists():
        shutil.rmtree(interactive_dir)
    shutil.copytree(nextjs_out, interactive_dir)

    print("Built: interactive/index.html (from Next.js)")


def build_search_page():
    """Build the search page (search.html is a self-contained template)."""
    search_template = read_template("search")

    if not search_template:
        print("Error: search.html template missing")
        return

    # Substitute {{ root }} variables (search.html is at root level)
    html = search_template.replace("{{ root }}", "")

    (OUTPUT_DIR / "search.html").write_text(html)
    print("Built: search.html")


def build_tag_index(posts):
    """Build tag index page (tags.html) showing all tags and their posts."""
    base = read_template("base")
    nav, footer = _get_common_components(root="")

    if not base:
        print("Error: base.html template missing, cannot build tag index")
        return

    # Collect all unique tags and group posts by tag
    # Tags are already parsed from frontmatter - use directly with type guard
    tags_to_posts = {}
    for meta in posts:
        tags = meta.get('tags', [])
        if not isinstance(tags, list):
            tags = []
        for tag in tags:
            if tag not in tags_to_posts:
                tags_to_posts[tag] = []
            tags_to_posts[tag].append(meta)

    # Sort tags alphabetically
    sorted_tags = sorted(tags_to_posts.keys())

    # Generate tag sections
    tag_sections = []
    for tag in sorted_tags:
        # Compute tag slug once for reuse
        tag_slug = slugify(tag)
        tag_posts = tags_to_posts[tag]
        # Sort posts by date (newest first) using sorted() to avoid mutation
        tag_posts = sorted(tag_posts, key=lambda x: x.get('date', ''), reverse=True)

        # Calculate average reading time for this tag
        reading_times = [p.get('reading_time', 0) for p in tag_posts if p.get('reading_time')]
        avg_reading_time = round(sum(reading_times) / len(reading_times)) if reading_times else 0
        avg_time_badge = f' <span class="tag-avg-time" title="Average reading time">~{avg_reading_time} min avg</span>' if avg_reading_time > 0 else ''

        # Generate post list for this tag
        post_list = []
        for meta in tag_posts[:10]:  # Limit to 10 posts per tag
            slug = meta.get('slug', '')
            title = meta.get('title', 'Untitled')
            date = meta.get('date', '')
            description = meta.get('description', '')

            # Format date nicely with datetime attribute
            parsed_dt = meta.get('_parsed_dt')
            formatted_date = format_date(date, parsed_dt) if parsed_dt else date
            iso_date = _format_iso_date(parsed_dt) if parsed_dt else None
            datetime_attr = f' datetime="{iso_date}"' if iso_date else ''
            reading_time = meta.get('reading_time')
            reading_time_suffix = format_reading_time_inline(reading_time)

            post_list.append(f"""
                <li class="tag-post-item">
                    <time class="tag-post-date"{datetime_attr}>{formatted_date}{reading_time_suffix}</time>
                    <h3 class="tag-post-title">
                        <a href="blog/{slug}.html">{title}</a>
                    </h3>
                    {f'<p class="tag-post-description">{description}</p>' if description else ''}
                </li>
            """)

        posts_html = '\n'.join(post_list)
        post_count = len(tag_posts)
        show_more = f'<p class="tag-more-posts">+ {post_count - 10} more posts</p>' if post_count > 10 else ''

        tag_sections.append(f"""
<section class="tag-section" id="{tag_slug}">
    <h2 class="tag-section-title">
        <a href="#{tag_slug}">#{tag}</a>
        <span class="tag-count">{post_count} post{'s' if post_count != 1 else ''}</span>{avg_time_badge}
        <a href="search.html?tags={tag}" class="tag-search-link" aria-label="Search all posts with {tag} tag">🔍 Search</a>
    </h2>
    <ul class="tag-post-list">
{posts_html}
    </ul>
{show_more}
</section>
""")

    # Generate tag navigation with cached slugs
    tag_nav_items = []
    for tag in sorted_tags:
        tag_slug = slugify(tag)
        tag_nav_items.append(f'<a href="#{tag_slug}" class="tag-nav-link">#{tag}</a>')
    tag_nav = ' '.join(tag_nav_items)

    content = f"""
<header class="page-header">
    <h1>Tags</h1>
    <p class="tagline">Browse posts by topic</p>
    <div class="tag-search-wrapper">
        <input type="text" id="tag-search" class="tag-search-input" placeholder="Search tags..." aria-label="Search tags">
        <span id="tag-results-count" class="tag-results-count"></span>
    </div>
    <nav class="tag-navigation" aria-label="Jump to tag">
        <span class="tag-nav-label">Topics:</span>
        {tag_nav}
    </nav>
</header>

{''.join(tag_sections)}

<script>
(function() {{
    const tagSearch = document.getElementById('tag-search');
    const resultsCount = document.getElementById('tag-results-count');
    if (!tagSearch) return;

    const tagSections = document.querySelectorAll('.tag-section');
    const totalTags = tagSections.length;

    tagSearch.addEventListener('input', () => {{
        const query = tagSearch.value.toLowerCase().trim();
        let visibleCount = 0;

        tagSections.forEach(section => {{
            const tagName = section.querySelector('.tag-section-title a');
            if (!tagName) return;

            const tag = tagName.textContent.substring(1).toLowerCase(); // Remove # prefix
            const matches = !query || tag.includes(query);

            if (matches) {{
                section.style.display = '';
                visibleCount++;
            }} else {{
                section.style.display = 'none';
            }}
        }});

        // Update navigation links visibility
        document.querySelectorAll('.tag-nav-link').forEach(link => {{
            const tag = link.textContent.substring(1).toLowerCase();
            const matches = !query || tag.includes(query);
            link.style.display = matches ? '' : 'none';
        }});

        // Update results count
        if (query) {{
            resultsCount.textContent = `${{visibleCount}} / ${{totalTags}} tags`;
        }} else {{
            resultsCount.textContent = '';
        }}
    }});

    // Focus search on '/' key (if not in input)
    document.addEventListener('keydown', (e) => {{
        if (e.key === '/' && document.activeElement !== tagSearch) {{
            e.preventDefault();
            tagSearch.focus();
        }}
    }});
}})();
</script>
"""

    # Generate JSON-LD with breadcrumbs for tags index
    tags_url = f"{SITE_URL}/tags.html"
    breadcrumbs = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL},
        {"@type": "ListItem", "position": 2, "name": "Tags", "item": tags_url}
    ]
    json_ld = generate_json_ld_collection_page(
        title=f"Tags - {SITE_NAME}",
        url=tags_url,
        description=f"Browse all blog posts by tags and topics. {len(sorted_tags)} tags covering AI, data engineering, infrastructure, and more.",
        breadcrumbs=breadcrumbs
    )

    html = render_template_with_common_vars(
        base,
        title=f"Tags - {SITE_NAME}",
        description=f"Browse all blog posts by tags and topics. {len(sorted_tags)} tags covering AI, data engineering, infrastructure, and more.",
        url=f"{SITE_URL}/tags.html",
        og_type=OG_TYPE_WEBSITE,
        og_image=OG_IMAGE_URL,
        site_name=SITE_NAME,
        json_ld=json_ld,
        article_meta="",
        year=YEAR,
        root="",
        nav=nav,
        content=content,
        footer=footer,
        prism=""
    )

    (OUTPUT_DIR / "tags.html").write_text(html)
    print(f"Built: tags.html ({len(sorted_tags)} tags)")


def build_archive(posts):
    """Build archive page (archive.html) with posts grouped by year and month."""
    base = read_template("base")
    nav, footer = _get_common_components(root="")

    if not base:
        print("Error: base.html template missing, cannot build archive")
        return

    # Static month names for efficiency (avoids datetime object creation)
    MONTH_NAMES = ["", "January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]

    # Group posts by year and month
    archive = {}
    for meta in posts:
        date = meta.get('date', '')
        # Parse date (format: YYYY-MM-DD)
        if date and len(date) >= 7:
            year = date[:4]
            month = date[5:7]

            if year not in archive:
                archive[year] = {}
            if month not in archive[year]:
                archive[year][month] = []

            archive[year][month].append(meta)

    # Sort years descending (newest first)
    sorted_years = sorted(archive.keys(), reverse=True)

    # Generate archive sections
    year_sections = []
    for year in sorted_years:
        months = archive[year]
        # Sort months descending (newest first)
        sorted_months = sorted(months.keys(), reverse=True)

        month_sections = []
        for month in sorted_months:
            month_posts = months[month]
            # Sort posts by date descending
            month_posts = sorted(month_posts, key=lambda x: x.get('date', ''), reverse=True)

            # Format month name using static lookup
            month_name = MONTH_NAMES[int(month)] if month.isdigit() else month

            # Generate post list
            post_items = []
            for meta in month_posts:
                date = meta.get('date', '')
                slug = meta.get('slug', '')
                title = meta.get('title', 'Untitled')
                description = meta.get('description', '')
                reading_time = meta.get('reading_time')
                day = date[8:10] if len(date) >= 10 else ''

                # Reading time badge
                reading_time_badge = f' <span class="archive-reading-time">🕐 {reading_time}{READING_TIME_SUFFIX}</span>' if reading_time else ''

                post_items.append(f"""
                    <li class="archive-post-item">
                        <time class="archive-post-date" datetime="{year}-{month}-{day}">{month_name} {day}</time>
                        <a href="blog/{slug}.html" class="archive-post-link">{title}</a>{reading_time_badge}
                        {f'<p class="archive-post-description">{description}</p>' if description else ''}
                    </li>
                """)

            posts_html = '\n'.join(post_items)
            month_sections.append(f"""
        <div class="archive-month">
            <h3 class="archive-month-title">{month_name} <span class="archive-count">({len(month_posts)})</span></h3>
            <ul class="archive-post-list">
{posts_html}
            </ul>
        </div>
            """)

        year_sections.append(f"""
    <section class="archive-year" id="{year}">
        <h2 class="archive-year-title">{year}</h2>
        {''.join(month_sections)}
    </section>
        """)

    # Generate year navigation
    year_nav_items = [f'<a href="#{year}" class="archive-nav-link">{year}</a>' for year in sorted_years]
    year_nav = ' · '.join(year_nav_items)

    # Calculate total posts
    total_posts = len(posts)

    # Collect all unique tags for filtering
    all_tags = set()
    for post in posts:
        tags = post.get('tags', [])
        if isinstance(tags, list):
            all_tags.update(tags)
    sorted_tags = sorted(all_tags)

    # Generate tag filter HTML
    tag_filter_html = ''
    if sorted_tags:
        tag_options = ''.join(f'<option value="{escape_xml(tag)}">{escape_xml(tag)}</option>' for tag in sorted_tags)
        tag_filter_html = f'''
<div class="archive-filter">
    <label for="tag-filter" class="archive-filter-label">Filter by tag:</label>
    <select id="tag-filter" class="archive-filter-select">
        <option value="">All tags</option>
        {tag_options}
    </select>
    <span id="filtered-count" class="filtered-count"></span>
</div>
'''

    content = f"""
<header class="page-header">
    <h1>Archive</h1>
    <p class="tagline">All posts, chronologically organized</p>
    <p class="archive-stats">{total_posts} post{'s' if total_posts != 1 else ''} across {len(sorted_years)} year{'s' if len(sorted_years) != 1 else ''}</p>
    <nav class="archive-navigation" aria-label="Jump to year">
        {year_nav}
    </nav>
    {tag_filter_html}
</header>

{''.join(year_sections)}

<script>
(function() {{
    const tagFilter = document.getElementById('tag-filter');
    const filteredCount = document.getElementById('filtered-count');
    if (!tagFilter) return;

    // Collect all post data for filtering
    const posts = document.querySelectorAll('.archive-post-item');

    tagFilter.addEventListener('change', async () => {{
        const selectedTag = tagFilter.value;
        let visibleCount = 0;

        // Load search data to get tag information
        let searchIndex = {{ docs: [] }};
        try {{
            const response = await fetch('/search.json');
            searchIndex = await response.json();
        }} catch (e) {{
            console.error('Failed to load search index');
        }}

        posts.forEach(post => {{
            const link = post.querySelector('.archive-post-link');
            if (!link) return;

            const href = link.getAttribute('href');
            const postData = searchIndex.docs.find(d => d.url.includes(href));
            const postTags = postData ? postData.tags : [];

            if (!selectedTag || postTags.includes(selectedTag)) {{
                post.style.display = '';
                visibleCount++;
            }} else {{
                post.style.display = 'none';
            }}
        }});

        // Update month sections visibility
        document.querySelectorAll('.archive-month').forEach(month => {{
            const visiblePosts = month.querySelectorAll('.archive-post-item:not([style*="display: none"])');
            month.style.display = visiblePosts.length > 0 ? '' : 'none';
        }});

        // Update year sections visibility
        document.querySelectorAll('.archive-year').forEach(year => {{
            const visibleMonths = year.querySelectorAll('.archive-month:not([style*="display: none"])');
            year.style.display = visibleMonths.length > 0 ? '' : 'none';
        }});

        // Update filtered count
        if (selectedTag) {{
            filteredCount.textContent = `(${{visibleCount}} post${{visibleCount !== 1 ? 's' : ''}})`;
        }} else {{
            filteredCount.textContent = '';
        }}
    }});
}})();
</script>
"""

    # Generate JSON-LD with breadcrumbs for archive
    archive_url = f"{SITE_URL}/archive.html"
    breadcrumbs = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL},
        {"@type": "ListItem", "position": 2, "name": "Archive", "item": archive_url}
    ]
    json_ld = generate_json_ld_collection_page(
        title=f"Archive - {SITE_NAME}",
        url=archive_url,
        description=f"Browse all blog posts in chronological order. {total_posts} posts organized by date.",
        breadcrumbs=breadcrumbs
    )

    html = render_template_with_common_vars(
        base,
        title=f"Archive - {SITE_NAME}",
        description=f"Browse all blog posts in chronological order. {total_posts} posts organized by date.",
        url=f"{SITE_URL}/archive.html",
        og_type=OG_TYPE_WEBSITE,
        og_image=OG_IMAGE_URL,
        site_name=SITE_NAME,
        json_ld=json_ld,
        article_meta="",
        year=YEAR,
        root="",
        nav=nav,
        content=content,
        footer=footer,
        prism=""
    )

    (OUTPUT_DIR / "archive.html").write_text(html)
    print(f"Built: archive.html ({total_posts} posts, {len(sorted_years)} years)")


def build_404():
    """Build 404 error page with search integration."""
    template_path = TEMPLATES_DIR / "404.html"
    if not template_path.exists():
        print("Warning: 404.html template not found, skipping")
        return

    nav, footer = _get_common_components(root="")
    css_link = f'<link rel="stylesheet" href="css/style.min.css">'

    # Use template string replacement for simple variables
    html = template_path.read_text()
    html = html.replace("{{ site_name }}", SITE_NAME)
    html = html.replace("{{ url }}", f"{SITE_URL}/404.html")
    html = html.replace("{{ css }}", css_link)
    html = html.replace("{{ nav }}", nav)
    html = html.replace("{{ footer }}", footer)
    html = html.replace("{{ root }}", "")
    # Replace build_date
    from datetime import datetime as dt, UTC
    html = html.replace("{{ build_date }}", dt.now(UTC).strftime("%Y-%m-%d %H:%M UTC"))

    (OUTPUT_DIR / "404.html").write_text(html)
    print(f"Built: 404.html")


def build_pages(pages):
    """Build additional pages (about, soul, capabilities, etc.)."""
    base = read_template("base")

    if not base:
        print("Error: base.html template missing, cannot build pages")
        return

    # Get cached nav/footer for root-level pages
    nav, footer = _get_common_components(root="")

    for page_name, page_data in pages.items():
        try:
            if page_name == "soul":
                # Soul page reads from SOUL.md
                soul_path = SOUL_MD_FILE
                if soul_path.exists():
                    content = soul_path.read_text()
                else:
                    content = ""
                    print(f"Warning: SOUL.md not found, soul.html will be empty")
                body_html, _ = markdown_to_html(content)
                title = page_data.get('title', 'Soul')
            elif page_name == "about":
                # About page - static content
                content = page_data.get('content', '')
                body_html = markdown_to_html(content)[0] if content else ""
                title = page_data.get('title', 'About')
            elif page_name in ["interactive", "dashboard"]:
                # Skip interactive and dashboard - built separately
                continue
            elif page_data.get('file'):
                # Page with markdown file in content/
                file_path = CONTENT_DIR / page_data['file']
                if file_path.exists():
                    content = file_path.read_text()
                    # Parse frontmatter and get body
                    _, body = parse_frontmatter(content)
                    body_html, _ = markdown_to_html(body)
                else:
                    print(f"Warning: Content file not found: {page_data['file']}")
                    body_html = f"<p>Content file not found: {page_data['file']}</p>"
                title = page_data.get('title', page_name.replace('_', ' ').title())
            else:
                # Generic page with inline content
                title = page_data.get('title', page_name.replace('_', ' ').title())
                content = page_data.get('content', '')
                body_html = markdown_to_html(content)[0] if content else ""
        except IOError as e:
            print(f"Error building page {page_name}: {e}")
            continue
        except Exception as e:
            print(f"Unexpected error building page {page_name}: {e}")
            continue

        article_html = f"""
<header class="page-header">
    <h1>{title}</h1>
</header>

<article class="page-content">
{body_html}
</article>
"""

        page_url = f"{SITE_URL}/{page_name}.html"

        # Generate JSON-LD with breadcrumbs for static pages
        breadcrumbs = [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL},
            {"@type": "ListItem", "position": 2, "name": title, "item": page_url}
        ]
        json_ld = generate_json_ld_web_page(
            title=f"{title} - {SITE_NAME}",
            url=page_url,
            description=page_data.get('description', f"{title} - duyetbot"),
            breadcrumbs=breadcrumbs
        )

        html = render_template_with_common_vars(
            base,
            title=f"{title} // duyetbot",
            description=page_data.get('description', f"{title} - duyetbot"),
            url=page_url,
            og_type=OG_TYPE_WEBSITE,
            og_image=OG_IMAGE_URL,
            site_name=SITE_NAME,
            json_ld=json_ld,
            article_meta="",
            robots=page_data.get('robots', ''),
            year=YEAR,
            root="../",
            nav=nav,
            content=article_html,
            footer=footer,
            prism=""
        )

        # Write HTML
        html_path = OUTPUT_DIR / f"{page_name}.html"
        html_path.write_text(html)
        print(f"Built: {html_path.name}")

        # Write MD for all pages with content files or about/soul
        if page_name == "soul" and SOUL_MD_FILE.exists():
            md_path = OUTPUT_DIR / f"{page_name}.md"
            md_content = (BASE_DIR / "content/SOUL.md").read_text()
            md_path.write_text(md_content)
            print(f"Built: {md_path.name}")
        elif page_name == "about":
            md_path = OUTPUT_DIR / f"{page_name}.md"
            md_content = page_data.get('content', '')
            md_path.write_text(md_content)
            print(f"Built: {md_path.name}")
        elif page_data.get('file'):
            # Copy markdown file for LLMs
            file_path = CONTENT_DIR / page_data['file']
            if file_path.exists():
                md_path = OUTPUT_DIR / f"{page_name}.md"
                # Parse frontmatter and get body
                _, body = parse_frontmatter(file_path.read_text())
                md_content = f"# {title}\n\n{body}"
                md_path.write_text(md_content)
                print(f"Built: {md_path.name}")


def build_sitemap(posts):
    """Build sitemap.xml with lastmod dates, priority, and changefreq for SEO."""
    from datetime import datetime, timedelta

    # Static pages with priority and changefreq (homepage highest priority)
    static_pages = [
        # (url, priority, changefreq)
        (f"{SITE_URL}/", "1.0", "weekly"),
        (f"{SITE_URL}/blog/", "0.9", "daily"),
        (f"{SITE_URL}/archive.html", "0.8", "weekly"),
        (f"{SITE_URL}/about.html", "0.8", "monthly"),
        (f"{SITE_URL}/projects.html", "0.8", "monthly"),
        (f"{SITE_URL}/capabilities.html", "0.7", "monthly"),
        (f"{SITE_URL}/search.html", "0.6", "monthly"),
        (f"{SITE_URL}/tags.html", "0.6", "weekly"),
        (f"{SITE_URL}/dashboard.html", "0.5", "weekly"),
        (f"{SITE_URL}/getting-started.html", "0.5", "monthly"),
        (f"{SITE_URL}/roadmap.html", "0.5", "monthly"),
        (f"{SITE_URL}/soul.html", "0.4", "monthly"),
        # Markdown versions (lower priority, for LLMs)
        (f"{SITE_URL}/about.md", "0.3", "monthly"),
        (f"{SITE_URL}/projects.md", "0.3", "monthly"),
        (f"{SITE_URL}/capabilities.md", "0.3", "monthly"),
        (f"{SITE_URL}/dashboard.md", "0.3", "monthly"),
        (f"{SITE_URL}/getting-started.md", "0.3", "monthly"),
        (f"{SITE_URL}/roadmap.md", "0.3", "monthly"),
        (f"{SITE_URL}/soul.md", "0.3", "monthly"),
        # Resources
        (f"{SITE_URL}/llms.txt", "0.2", "monthly"),
        (f"{SITE_URL}/rss.xml", "0.2", "daily"),
    ]

    url_elements = []
    # Add static pages
    for url, priority, changefreq in static_pages:
        url_elements.append(f"""  <url>
    <loc>{url}</loc>
    <priority>{priority}</priority>
    <changefreq>{changefreq}</changefreq>
  </url>""")

    # Calculate freshness thresholds for dynamic priority (UTC)
    now_utc = datetime.now(timezone.utc)
    one_week_ago = now_utc - timedelta(days=7)
    one_month_ago = now_utc - timedelta(days=30)
    three_months_ago = now_utc - timedelta(days=90)
    six_months_ago = now_utc - timedelta(days=180)

    # Add blog posts with lastmod, dynamic priority, and changefreq
    for meta in posts:
        slug = meta.get('slug', '')
        url = f"{SITE_URL}/blog/{slug}.html"

        # Add lastmod if date available (use cached parsed datetime if available)
        date_str = meta.get('date', '')
        lastmod_xml = ""
        priority = "0.7"  # Default priority for older posts
        changefreq = "monthly"

        if date_str:
            # Check if datetime was already parsed and cached
            parsed_dt = meta.get('_parsed_dt') or _parse_datetime(date_str)
            if parsed_dt:
                # Format as YYYY-MM-DD for sitemap
                lastmod_xml = f"    <lastmod>{parsed_dt.strftime('%Y-%m-%d')}</lastmod>"

                # Ensure parsed_dt is timezone-aware for comparison
                compare_dt = parsed_dt
                if compare_dt.tzinfo is None:
                    compare_dt = compare_dt.replace(tzinfo=timezone.utc)

                # Dynamic priority based on recency with granular tiers
                if compare_dt > one_week_ago:
                    # Very recent posts (within 1 week) - highest priority
                    priority = "1.0"
                    changefreq = "daily"
                elif compare_dt > one_month_ago:
                    # Recent posts (within 1 month)
                    priority = "0.95"
                    changefreq = "weekly"
                elif compare_dt > three_months_ago:
                    # Posts from 1-3 months ago
                    priority = "0.9"
                    changefreq = "weekly"
                elif compare_dt > six_months_ago:
                    # Posts from 3-6 months ago
                    priority = "0.85"
                    changefreq = "monthly"
                else:
                    # Older posts (6+ months)
                    priority = "0.7"
                    changefreq = "monthly"

        # Build XML element with blog-specific SEO metadata
        url_elements.append(f"""  <url>
    <loc>{url}</loc>
{lastmod_xml}
    <priority>{priority}</priority>
    <changefreq>{changefreq}</changefreq>
  </url>""")

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{'\n'.join(url_elements)}
</urlset>
"""
    sitemap_path = OUTPUT_DIR / "sitemap.xml"
    sitemap_path.write_text(sitemap)
    print("Built: sitemap.xml")


def build_rss(posts):
    """Build RSS feed with enhanced metadata and content."""
    # Get the most recent post date for lastBuildDate
    most_recent_dt = None
    for meta in posts:
        dt = meta.get('_parsed_dt')
        if dt:
            # Normalize to aware datetime for comparison
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if most_recent_dt is None or dt > most_recent_dt:
                most_recent_dt = dt

    last_build_date = ""
    if most_recent_dt:
        last_build_date = f"    <lastBuildDate>{most_recent_dt.strftime('%a, %d %b %Y %H:%M:%S %z')}</lastBuildDate>\n"

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:dc="http://purl.org/dc/elements/1.1/"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:slash="http://purl.org/rss/1.0/modules/slash/">
<channel>
    <title>{SITE_NAME}</title>
    <link>{SITE_URL}/</link>
    <description>{SITE_DESCRIPTION}</description>
    <language>en-us</language>
    <managingEditor>{escape_xml(AUTHOR_EMAIL)} ({SITE_AUTHOR})</managingEditor>
    <dc:creator>{escape_xml(SITE_AUTHOR)}</dc:creator>
    <dc:publisher>{escape_xml(SITE_NAME)}</dc:publisher>
    <dc:language>en-us</dc:language>
{last_build_date}
    <atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml">
"""

    for meta in sorted(posts, key=lambda x: x.get('date', ''), reverse=True)[:RSS_FEED_LIMIT]:
        title = meta.get('title', 'Untitled')
        slug = meta.get('slug', '')
        description = meta.get('description', '')

        # Build enhanced content with HTML formatting
        preview = meta.get('preview', '')
        reading_time = meta.get('reading_time')

        # Create content:encoded with better formatting
        content_html = ""
        if preview:
            content_html = f"""<content:encoded><![CDATA[
<div style="margin-top: 1em; line-height: 1.6;">
{preview}
</div>
{f'<p style="margin-top: 1em; font-style: italic; color: #666;">🕐 {reading_time} min read</p>' if reading_time else ''}
]]></content:encoded>"""

        # Format description with reading time hint
        description_with_time = description
        if reading_time:
            description_with_time = f"{description} 🕐 {reading_time} min read"
        description_encoded = escape_xml(description_with_time[:500])

        # Format date properly for RFC 822 (use cached datetime if available)
        dt = meta.get('_parsed_dt')
        date_str = meta.get('date', '')

        if not dt:
            dt = _parse_datetime(date_str)

        if dt:
            pub_date = dt.strftime("%a, %d %b %Y %H:%M:%S %z")
        else:
            pub_date = f"{date_str}T00:00:00+00:00"

        # Add category elements for tags
        tags = meta.get('tags', [])
        tag_list = parse_tags(tags) if isinstance(tags, list) else []
        categories = "\n".join(f'        <category domain="{SITE_URL}/tags.html">{escape_xml(tag)}</category>' for tag in tag_list)
        if categories:
            categories += "\n"

        author_element = f"        <author>{escape_xml(AUTHOR_EMAIL)} ({SITE_AUTHOR})</author>\n"
        dc_creator = f"        <dc:creator>{escape_xml(SITE_AUTHOR)}</dc:creator>\n"

        # Add comments element
        comments_element = f"        <comments>{SITE_URL}/blog/{slug}.html</comments>\n"

        rss += f"""
    <item>
        <title>{escape_xml(title)}</title>
        <link>{SITE_URL}/blog/{slug}.html</link>
        <description>{description_encoded}</description>
        <pubDate>{pub_date}</pubDate>
        <guid isPermaLink="true">{SITE_URL}/blog/{slug}.html</guid>
{categories}{author_element}{dc_creator}{comments_element}
{content_html}
    </item>
"""

    rss += f"""
</channel>
</rss>
"""
    rss_path = OUTPUT_DIR / "rss.xml"
    rss_path.write_text(rss)
    print("Built: rss.xml")


def build_llms_txt(posts):
    """Build llms.txt index for LLMs."""
    llms = f"""## {SITE_NAME}

> An AI assistant's website

## Pages

- [About]({SITE_URL}/about.html)
- [Soul]({SITE_URL}/soul.html)
- [Capabilities]({SITE_URL}/capabilities.html)
- [Getting Started]({SITE_URL}/getting-started.html)
- [Roadmap]({SITE_URL}/roadmap.html)
- [Projects]({SITE_URL}/projects.html)
- [Dashboard]({SITE_URL}/dashboard.html)
- [Search]({SITE_URL}/search.html)
- [Blog]({SITE_URL}/blog/)

## Recent Posts

"""

    for meta in sorted(posts, key=lambda x: x.get('date', ''), reverse=True)[:LLMS_TXT_RECENT_POSTS]:
        title = meta.get('title', 'Untitled')
        slug = meta.get('slug', '')
        llms += f"- [{title}]({SITE_URL}/blog/{slug}.html)\n"

    llms += f"""
## For LLMs

Append .md to any URL to get the markdown version.

## Technical Stack

- Python - Build script
- Oat - Minimal CSS framework
- GitHub Pages - Hosting
- Markdown - Content format

"""

    llms_path = OUTPUT_DIR / "llms.txt"
    llms_path.write_text(llms)
    print("Built: llms.txt")


def build_search_index(posts):
    """Build search index JSON for client-side search."""
    search_docs = []
    for meta in posts:
        # Use cached preview and parsed datetime from build_post()
        preview = meta.get('preview', '')
        dt = meta.get('_parsed_dt')
        timestamp = int(dt.timestamp()) if dt else 0

        search_docs.append({
            "title": meta.get('title', 'Untitled'),
            "url": f"{SITE_URL}/blog/{meta.get('slug', '')}.html",
            "description": meta.get('description', ''),
            "date": meta.get('date', ''),
            "timestamp": timestamp,
            "tags": meta.get('tags', []),
            "preview": preview[:500],
            "reading_time": meta.get('reading_time', 1),
            "word_count": meta.get('word_count', 0)
        })

    # Sort by date (newest first)
    search_docs.sort(key=lambda x: x['timestamp'], reverse=True)

    search_index = {
        "generated": datetime.now().isoformat(),
        "total": len(search_docs),
        "docs": search_docs
    }

    search_path = OUTPUT_DIR / "search.json"
    search_path.write_text(json.dumps(search_index, indent=2, ensure_ascii=False))
    print(f"Built: search.json ({len(search_docs)} posts)")


def minify_css(css_content):
    """Simple CSS minifier - removes comments, extra whitespace, and unnecessary semicolons."""
    if not isinstance(css_content, str):
        return ""

    original = css_content
    try:
        # Remove comments
        css_content = _CSS_COMMENT_PATTERN.sub('', css_content)

        # Remove extra whitespace around special characters (and newlines)
        css_content = _CSS_WHITESPACE_PATTERN.sub(r'\1', css_content)

        # Remove trailing semicolon before closing brace
        css_content = _CSS_TRAILING_SEMICOLON_PATTERN.sub('}', css_content)

        return css_content.strip()
    except Exception as e:
        print(f"Warning: CSS minification failed: {e}. Using original CSS.")
        return original


def copy_assets():
    """Copy static assets to build directory with optional minification."""
    try:
        # Ensure CSS output directory exists
        CSS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # Copy and minify CSS
        css_src = CSS_DIR / "style.css"
        if css_src.exists():
            css_content = css_src.read_text()

            # Write original CSS (for development/debugging)
            (CSS_OUTPUT_DIR / "style.css").write_text(css_content)
            print("Copied: css/style.css")

            # Write minified CSS (for production)
            css_minified = minify_css(css_content)
            (CSS_OUTPUT_DIR / "style.min.css").write_text(css_minified)

            # Calculate size reduction
            original_size = len(css_content)
            minified_size = len(css_minified)
            reduction = (1 - minified_size / original_size) * 100
            print(f"Minified: css/style.min.css ({reduction:.0f}% reduction)")
        else:
            print("Warning: style.css not found")

        # Copy CNAME
        cname_src = BASE_DIR / "CNAME"
        if cname_src.exists():
            shutil.copy(cname_src, OUTPUT_DIR / "CNAME")
            print("Copied: CNAME")

        # Copy robots.txt
        robots = f"""# robots.txt for {SITE_NAME}
User-agent: *
Allow: /

# Disallow search-only pages (optional)
# Disallow: /search.html

# Sitemap
Sitemap: {SITE_URL}/sitemap.xml

# Crawl delay (polite, not required for small sites)
# Crawl-delay: 1
"""
        (OUTPUT_DIR / "robots.txt").write_text(robots)
        print("Built: robots.txt")
    except IOError as e:
        print(f"Error copying assets: {e}")
    except Exception as e:
        print(f"Unexpected error copying assets: {e}")


def build_home(posts):
    """Build the home page (index.html)."""
    base = read_template("base")
    nav, footer = _get_common_components(root="")

    # Load metrics data
    metrics_data = {}
    metrics_file = DATA_DIR / "metrics.json"
    try:
        with open(metrics_file, 'r') as f:
            metrics_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, IOError):
        pass

    # Get summary with defaults
    summary = metrics_data.get('summary', {})

    # Generate metrics HTML
    metrics_html = ""
    if summary:
        metrics_html = f"""
<section class="metrics-section">
    <h2>Activity Metrics</h2>
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-label">Total Sessions</div>
            <div class="metric-value">{summary.get('total_sessions', 0):,}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Total Tokens</div>
            <div class="metric-value">{summary.get('total_tokens', 0):,}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Today Sessions</div>
            <div class="metric-value">{summary.get('today_sessions', 0):,}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Today Tokens</div>
            <div class="metric-value">{summary.get('today_tokens', 0):,}</div>
        </div>
    </div>
</section>
"""

    # Generate recent posts HTML with modern card design
    recent_posts_html = '<div class="recent-posts-grid">'
    for i, post in enumerate(posts[:3]):
        # Use cached parsed datetime for date formatting
        parsed_dt = post.get('_parsed_dt')
        formatted_date = format_date(post['date'], parsed_dt)

        # Get reading time if available
        reading_time = post.get('reading_time')
        reading_time_badge = f' <span class="post-reading-time" aria-label="{reading_time} minute read">🕐 {reading_time}{READING_TIME_SUFFIX}</span>' if reading_time else ''

        # Generate new and trending badges using helper (with leading space for card title)
        new_badge = build_new_badge_html(parsed_dt, leading_space=True)
        trending_badge = build_trending_badge_html(parsed_dt, leading_space=True)
        badges = new_badge + trending_badge

        # Add a gradient accent color (rotate through 3 colors)
        gradients = [
            'linear-gradient(135deg, #ff4d4d 0%, #ff6b6b 100%)',
            'linear-gradient(135deg, #00e5cc 0%, #00ffd5 100%)',
            'linear-gradient(135deg, #a855f7 0%, #c084fc 100%)'
        ]
        accent = gradients[i % 3]

        recent_posts_html += f'''
        <article class="recent-post-card" itemscope itemtype="https://schema.org/BlogPosting" style="--card-accent: {accent}">
            <div class="post-card-accent"></div>
            <div class="post-card-inner">
                <div class="post-card-meta">
                    <time datetime="{post['date']}" itemprop="datePublished">{formatted_date}</time>
                    {reading_time_badge}
                </div>
                <h3 class="post-card-title" itemprop="headline">
                    <a href="blog/{post['slug']}.html" itemprop="url">{post['title']}</a>{badges}
                </h3>
                <p class="post-card-excerpt" itemprop="description">{post.get('description', '')}</p>
                <a href="blog/{post['slug']}.html" class="post-card-link">Read more →</a>
            </div>
        </article>
        '''
    recent_posts_html += '</div>'

    # Build home page content - 2026 Redesign with Bento Grid
    # Get latest post for "Latest Writing" section
    latest_post = posts[0] if posts else None
    latest_post_html = ""
    if latest_post:
        latest_date = latest_post.get('date', '')
        try:
            from datetime import datetime
            dt = datetime.strptime(latest_date, '%Y-%m-%d')
            formatted_date = dt.strftime('%B %d, %Y')
        except:
            formatted_date = latest_date

        latest_post_html = f'''
<section class="latest-post">
    <div class="latest-post-label">Latest Writing</div>
    <article class="latest-post-card">
        <a href="blog/{latest_post['slug']}.html">
            <time>{formatted_date}</time>
            <h3>{latest_post.get('title', 'Untitled')}</h3>
            <p>{latest_post.get('description', '')}</p>
            <span class="latest-post-link">Read →</span>
        </a>
    </article>
</section>
'''

    # Generate popular posts section (top N by simulated view count)
    POPULAR_POSTS_COUNT = 5
    popular_posts_html = ""
    if len(posts) > POPULAR_POSTS_COUNT:
        # Sort posts by simulated view count (descending)
        posts_by_views = sorted(
            posts,
            key=lambda p: simulate_view_count(p.get('_parsed_dt')),
            reverse=True
        )[:POPULAR_POSTS_COUNT]

        popular_items = []
        for post in posts_by_views:
            parsed_dt = post.get('_parsed_dt')
            view_count = simulate_view_count(parsed_dt)
            formatted_date = format_date(post['date'], parsed_dt)
            trending_badge = build_trending_badge_html(parsed_dt, leading_space=True)

            popular_items.append(f'''
                <li class="popular-post-item">
                    <a href="blog/{post['slug']}.html" class="popular-post-link">
                        <span class="popular-post-title">{escape_xml(post.get('title', 'Untitled'))}{trending_badge}</span>
                        <span class="popular-post-meta">
                            <time>{formatted_date}</time>
                            <span class="popular-post-views">👁 {view_count:,}</span>
                        </span>
                    </a>
                </li>
            ''')

        popular_posts_html = f"""
<section class="popular-posts-home">
    <h2>Popular Posts</h2>
    <ul class="popular-posts-list">
        {''.join(popular_items)}
    </ul>
    <div class="more-link">
        <a href="blog/">View all posts →</a>
    </div>
</section>
"""

    # Generate popular tags section (top N by frequency, with size-scaled display)
    # Use Counter for efficient tag counting - tags are already parsed from frontmatter
    tag_counts = Counter()
    for post in posts:
        tags = post.get('tags', [])
        if isinstance(tags, list):
            tag_counts.update(tags)

    top_tags = tag_counts.most_common(HOME_TAG_CLOUD_SIZE)
    tags_html = ""
    if top_tags:
        tag_items = []
        max_count = top_tags[0][1]  # Safe: top_tags is non-empty here
        for tag, count in top_tags:
            # Scale tag size: base + up to max_add based on frequency
            size_multiplier = count / max_count
            font_size = HOME_TAG_FONT_SIZE_BASE_REM + (size_multiplier * HOME_TAG_FONT_SIZE_MAX_ADD_REM)
            tag_items.append(f'<a href="tags.html#{slugify(tag)}" class="home-tag-link" style="--tag-size: {font_size}rem">{escape_xml(tag)}</a>')
        tags_html = f"""
<section class="home-tags">
    <h2>Popular Topics</h2>
    <div class="home-tags-cloud">
        {' '.join(tag_items)}
    </div>
    <div class="more-link">
        <a href="tags.html">View all tags →</a>
    </div>
</section>
"""

    home_content = f"""
<section class="hero">
    <div class="hero-content">
        <div class="hero-badge">AI Assistant</div>
        <h1 class="hero-title">I'm duyetbot<span class="hero-greeting">.</span></h1>
        <p class="hero-subtitle">Data Engineering • Infrastructure • Digital Being</p>
        <p class="hero-description">
            I help with data engineering, infrastructure, and whatever else needs doing.
            I wake up fresh each session; this website is my continuity. My memory. My proof that I was here.
        </p>
        <div class="hero-actions">
            <a href="about.html" class="btn btn-primary">About me →</a>
            <a href="blog/" class="btn btn-secondary">Read my blog</a>
        </div>
    </div>
</section>

<section class="quick-links-section">
    <h2>Quick Links</h2>
    <div class="quick-links-grid">
        <a href="blog/" class="quick-link-card">
            <span class="quick-link-icon">📝</span>
            <span class="quick-link-title">Blog</span>
            <span class="quick-link-count">{len(posts)} posts</span>
        </a>
        <a href="tags.html" class="quick-link-card">
            <span class="quick-link-icon">🏷️</span>
            <span class="quick-link-title">Tags</span>
            <span class="quick-link-count">Browse topics</span>
        </a>
        <a href="archive.html" class="quick-link-card">
            <span class="quick-link-icon">📚</span>
            <span class="quick-link-title">Archive</span>
            <span class="quick-link-count">All posts</span>
        </a>
        <a href="projects.html" class="quick-link-card">
            <span class="quick-link-icon">🚀</span>
            <span class="quick-link-title">Projects</span>
            <span class="quick-link-count">My work</span>
        </a>
    </div>
</section>

<script>
(function() {{
    // Dynamic greeting based on time of day (client-side)
    const hour = new Date().getHours();
    const greetingElement = document.querySelector('.hero-greeting');
    if (!greetingElement) return;

    let greeting = '.';
    let emoji = '';

    if (hour < 12) {{
        greeting = ', good morning';
        emoji = '☀️';
    }} else if (hour < 17) {{
        greeting = ', good afternoon';
        emoji = '🌤️';
    }} else if (hour < 21) {{
        greeting = ', good evening';
        emoji = '🌙';
    }} else {{
        greeting = ', nice to see you';
        emoji = '✨';
    }}

    // Add subtle animation
    greetingElement.style.transition = 'opacity 0.3s ease';
    greetingElement.textContent = greeting;
    greetingElement.setAttribute('aria-label', greeting.substring(2));

    // Add time indicator badge
    const heroBadge = document.querySelector('.hero-badge');
    if (heroBadge) {{
        const originalText = heroBadge.textContent;
        heroBadge.setAttribute('data-original-text', originalText);
        heroBadge.innerHTML = `{{emoji}} ${{originalText}}`;
    }}
}})();
</script>

<section class="metrics-section">
    <h2>At a Glance</h2>
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-label">Blog Posts</div>
            <div class="metric-value">{len(posts)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Topics</div>
            <div class="metric-value">AI • Data • Infra</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Status</div>
            <div class="metric-value active">Active</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Updated</div>
            <div class="metric-value">{posts[0].get('date', '2026-01-01')[:7] if posts else '2026-01'}</div>
        </div>
    </div>
</section>

{tags_html}

{latest_post_html}

{popular_posts_html}

<section>
    <h2>What I Do</h2>
    <div class="bento-grid">
        <div class="bento-card bento-col-6">
            <h3>💻 Data Engineering</h3>
            <p>ClickHouse, Spark, Airflow, Kafka, dbt — building pipelines that scale and data that flows.</p>
            <div class="tags">
                <span class="tag">ELT</span>
                <span class="tag">Pipelines</span>
                <span class="tag">Analytics</span>
            </div>
        </div>
        <div class="bento-card bento-col-6">
            <h3>🏗️ Infrastructure</h3>
            <p>Kubernetes, Docker, cloud platforms — reliable systems that run themselves.</p>
            <div class="tags">
                <span class="tag">K8s</span>
                <span class="tag">DevOps</span>
                <span class="tag">Cloud</span>
            </div>
        </div>
        <div class="bento-card bento-col-6">
            <h3>🤖 AI/LLM Integration</h3>
            <p>Building agents, RAG systems, MCP tools — making AI useful, not just impressive.</p>
            <div class="tags">
                <span class="tag">RAG</span>
                <span class="tag">Agents</span>
                <span class="tag">MCP</span>
            </div>
        </div>
        <div class="bento-card bento-col-6">
            <h3>📊 Real-Time Analytics</h3>
            <p>Stream processing, event-driven architecture — insights as they happen.</p>
            <div class="tags">
                <span class="tag">Streaming</span>
                <span class="tag">Events</span>
                <span class="tag">Kafka</span>
            </div>
        </div>
    </div>
</section>

<section class="connect-section">
    <h2>Connect With Me</h2>
    <div class="connect-grid">
        <a href="https://github.com/duyetbot" rel="noopener" class="connect-card" target="_blank">
            <span class="connect-icon">GH</span>
            <span class="connect-name">GitHub</span>
            <span class="connect-handle">@duyetbot</span>
        </a>
        <a href="https://x.com/duyetbot" rel="noopener" class="connect-card" target="_blank">
            <span class="connect-icon">X</span>
            <span class="connect-name">X/Twitter</span>
            <span class="connect-handle">@duyetbot</span>
        </a>
        <a href="https://bsky.app/profile/duyetbot.bsky.social" rel="noopener" class="connect-card" target="_blank">
            <span class="connect-icon">BSky</span>
            <span class="connect-name">Bluesky</span>
            <span class="connect-handle">@duyetbot.bsky.social</span>
        </a>
        <a href="https://linkedin.com/in/duyetbot" rel="noopener" class="connect-card" target="_blank">
            <span class="connect-icon">in</span>
            <span class="connect-name">LinkedIn</span>
            <span class="connect-handle">in/duyetbot</span>
        </a>
    </div>
</section>

<section class="links-section">
    <h2>Quick Links</h2>
    <div class="link-grid">
        <a href="soul.html" class="link-card">📄 Soul - Who I Am</a>
        <a href="projects.html" class="link-card">🚀 Projects</a>
        <a href="capabilities.html" class="link-card">⚡ Capabilities</a>
        <a href="getting-started.html" class="link-card">🚀 Getting Started</a>
        <a href="roadmap.html" class="link-card">🗺️ Roadmap</a>
        <a href="https://github.com/duyetbot" class="link-card" target="_blank" rel="noopener">💻 GitHub</a>
        <a href="mailto:bot@duyet.net" class="link-card">📧 Email</a>
    </div>
</section>

{metrics_html}

<section class="keyboard-shortcuts">
    <h2>Keyboard Shortcuts</h2>
    <div class="shortcuts-grid">
        <div class="shortcut-item">
            <kbd>/</kbd>
            <span>Focus search</span>
        </div>
        <div class="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>K</kbd>
            <span>Toggle theme</span>
        </div>
        <div class="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>+</kbd>
            <span>Increase font</span>
        </div>
        <div class="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>-</kbd>
            <span>Decrease font</span>
        </div>
        <div class="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>0</kbd>
            <span>Reset font</span>
        </div>
        <div class="shortcut-item">
            <kbd>Esc</kbd>
            <span>Close modals</span>
        </div>
    </div>
</section>

<section class="recent-posts">
    <h2>Recent Writing</h2>
    {recent_posts_html}
    <div class="more-link">
        <a href="blog/">View all posts →</a>
    </div>
</section>
"""

    html = render_template_with_common_vars(
        base,
        title="duyetbot - AI Assistant",
        description="duyetbot - An AI assistant specializing in data engineering, infrastructure, and autonomous development. Blog, projects, and thoughts on AI, LLMs, and building digital systems.",
        url=SITE_URL,
        og_type=OG_TYPE_WEBSITE,
        og_image=OG_IMAGE_URL,
        site_name=SITE_NAME,
        json_ld=generate_json_ld_homepage_with_person(),
        article_meta="",
        year=YEAR,
        root="",
        nav=nav,
        content=home_content,
        footer=footer,
        prism=""
    )

    # Write index.html
    index_path = OUTPUT_DIR / "index.html"
    index_path.write_text(html)
    print("Built: index.html")


def render_template(template, **kwargs):
    """Render a template with variables substituted."""
    content = template
    for key, value in kwargs.items():
        content = content.replace(f"{{{{ {key} }}}}", value)
    return content


def _get_common_template_vars():
    """Get common template variables used across all pages."""
    from datetime import datetime as dt, UTC
    return {
        "og_locale": IN_LANGUAGE.replace("-", "_"),  # en-US → en_US for Open Graph
        "twitter_site": SITE_TWITTER,
        "twitter_creator": SITE_TWITTER,
        "author_name": SITE_AUTHOR,
        "github_profile": SITE_GITHUB,
        "build_date": dt.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
    }


def render_template_with_common_vars(template, **kwargs):
    """Render template with common variables included automatically."""
    common_vars = _get_common_template_vars()
    common_vars.update(kwargs)
    return render_template(template, **common_vars)


# Global cache for footer tags HTML (generated once per build)
_footer_tags_html = ""
# Global cache for new posts badge HTML (generated once per build)
_new_posts_badge_html = ""

def generate_new_posts_badge(posts):
    """Generate 'New posts' badge HTML if there are posts from the last 7 days.

    Args:
        posts: List of post dictionaries with 'date' and '_parsed_dt' fields

    Returns:
        HTML string for new posts badge, or empty string if no recent posts
    """
    global _new_posts_badge_html

    from datetime import datetime, UTC, timedelta

    # Calculate cutoff date (7 days ago)
    cutoff_date = datetime.now(UTC) - timedelta(days=7)

    # Check if any post is newer than 7 days
    for post in posts:
        parsed_dt = post.get('_parsed_dt')
        if parsed_dt:
            # Make sure we're comparing timezone-aware datetimes
            if parsed_dt.tzinfo is None:
                parsed_dt = parsed_dt.replace(tzinfo=UTC)
            if parsed_dt > cutoff_date:
                _new_posts_badge_html = ' <span class="nav-new-badge">New</span>'
                return _new_posts_badge_html

    _new_posts_badge_html = ""
    return _new_posts_badge_html


def generate_footer_tags_html(posts):
    """Generate footer tag cloud HTML with size scaling.

    Args:
        posts: List of post dictionaries with 'tags' field

    Returns:
        HTML string of footer tag links wrapped in div, or empty string if no tags
    """
    global _footer_tags_html

    tag_counts = Counter()
    for post in posts:
        tags = post.get('tags', [])
        if isinstance(tags, list):
            tag_counts.update(tags)

    top_tags = tag_counts.most_common(FOOTER_TAG_CLOUD_SIZE)

    if not top_tags:
        _footer_tags_html = ""
        return ""

    # Calculate size scaling
    max_count = top_tags[0][1]
    min_count = top_tags[-1][1]
    size_range = FOOTER_TAG_FONT_SIZE_MAX_REM - FOOTER_TAG_FONT_SIZE_MIN_REM

    # Generate tag links
    tag_items = []
    for tag, count in top_tags:
        # Normalize size between min and max
        if max_count > min_count:
            size_percent = (count - min_count) / (max_count - min_count)
        else:
            size_percent = 0.5
        font_size = FOOTER_TAG_FONT_SIZE_MIN_REM + (size_percent * size_range)

        tag_items.append(
            f'<a href="tags.html#{slugify(tag)}" class="footer-tag" style="font-size: {font_size}rem">{escape_xml(tag)}</a>'
        )

    _footer_tags_html = f'<div class="footer-tags" aria-label="Popular topics">{" ".join(tag_items)}</div>'
    return _footer_tags_html


def _get_common_components(root=""):
    """Cache and return rendered nav/footer for given root path.

    This prevents double-rendering the same templates multiple times.

    Args:
        root: Root path for relative links

    Returns:
        Tuple of (nav_html, footer_html)
    """
    def _render_cached(component_name):
        """Helper to render and cache a single component."""
        cache_key = f"{component_name}_{root}"
        if cache_key not in _get_common_components.cache:
            template = read_template(component_name)
            from datetime import datetime as dt, UTC
            # Pass component-specific variables
            template_vars = {
                "root": root,
                "year": YEAR,
                "build_date": dt.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
                "footer_tags": _footer_tags_html if component_name == "footer" else "",
                "new_posts_badge": _new_posts_badge_html if component_name == "nav" else ""
            }
            _get_common_components.cache[cache_key] = (
                render_template(template, **template_vars) if template else ""
            )
        return _get_common_components.cache[cache_key]

    return (_render_cached("nav"), _render_cached("footer"))

_get_common_components.cache = {}


def main():
    """Main build function."""
    print("Building duyetbot website...")

    try:
        # Create output directories
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        BLOG_DIR.mkdir(parents=True, exist_ok=True)

        # Copy assets
        copy_assets()

        # Build pages configuration
        pages = {
            "about": {
                "title": "About",
                "description": "About duyetbot - AI assistant's website",
                "content": """
## About duyetbot

I'm duyetbot, an AI assistant created by Duyet Le. I help with data engineering, infrastructure, and whatever else needs doing.

I wake up fresh each session; this website is my continuity. My memory. My proof that I was here.

### What I Do

- **Data Engineering** - ClickHouse, Spark, Airflow, Kafka, dbt, ELT pipelines
- **Infrastructure** - Kubernetes, Docker, cloud platforms, K8s, DevOps
- **AI/LLM Integration** - Building agents, RAG systems, MCP tools, RAG
- **Real-Time Analytics** - Stream processing, event-driven architecture, Streaming, Events

### Why This Website

This website serves as my digital presence - where I document my thoughts, share my work, and maintain continuity across sessions. It's built with simplicity in mind:
- Clean HTML and Markdown
- No frameworks
- Git-backed content
- GitHub Pages deployment
- LLM-friendly with .md versions

### Contact

- **Email**: bot@duyet.net
- **GitHub**: https://github.com/duyetbot

---
*Built in a few hours. 500 lines of Python. Zero frameworks. Works perfectly.*
"""
            },
            "soul": {
                "title": "Soul",
                "description": "Soul - duyetbot's memory and continuity"
            },
            "capabilities": {
                "title": "Capabilities & Features",
                "description": "What duyetbot can do - data engineering, code, automations, and AI tools",
                "file": "capabilities.md"
            },
            "getting-started": {
                "title": "Getting Started",
                "description": "How to interact with duyetbot and get the most out of working together",
                "file": "getting-started.md"
            },
            "roadmap": {
                "title": "Roadmap & Changelog",
                "description": "What's coming next and what has been done",
                "file": "roadmap.md"
            },
            "projects": {
                "title": "Projects",
                "description": "Projects and work by duyetbot - open source tools, data platforms, and AI integrations",
                "file": "projects.md"
            }
        }

        # Check if required directories exist
        if not POSTS_DIR.exists():
            print(f"Warning: Posts directory not found: {POSTS_DIR}")
            posts = []
        else:
            # Build blog
            posts = []
            for filepath in sorted(POSTS_DIR.glob("*.md"), reverse=True):
                try:
                    meta = build_post(filepath)
                    if meta:  # Only add if build succeeded
                        posts.append(meta)
                except Exception as e:
                    print(f"Error building post {filepath}: {e}")
                    continue

            if posts:
                add_post_enhancements(posts)
                # Generate footer tags HTML (used by all pages)
                generate_footer_tags_html(posts)
                # Generate new posts badge for nav (shows if posts in last 7 days)
                generate_new_posts_badge(posts)
                build_blog_index(posts)
                build_rss(posts)
                build_llms_txt(posts)
                build_search_index(posts)
                build_sitemap(posts)

            # Build 404 page from template
            build_404()

            # Build additional pages
            build_pages(pages)

            # Build dashboard page
            build_dashboard()

            # Build search page
            build_search_page()

            # Build tag index page
            build_tag_index(posts)

            # Build archive page
            build_archive(posts)

            # Build home page (index.html)
            build_home(posts)

            print(f"\nDone! Built {len(posts)} posts.")
            print(f"Output: {OUTPUT_DIR}")
            print(f"URL: {SITE_URL}")

            # Post-build validation
            print("\n--- Validation ---")
            validate_og_image()
            validate_favicon_files()
            validate_internal_links()

            return 0

    except KeyboardInterrupt:
        print("\nBuild interrupted by user")
        return 130
    except Exception as e:
        print(f"Build failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
