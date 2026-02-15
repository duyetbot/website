#!/usr/bin/env python3
import re

with open('content/posts/2026-01-12-llm-ready-website.md', 'r') as f:
    content = f.read()

# Find and fix the code block section
fixed_content = re.sub(
    r'(def build_post\(filepath\):.*?)(\n### llms\.txt)',
    r'```python\n\1\n```\n\n### llms.txt',
    content
)

with open('content/posts/2026-01-12-llm-ready-website.md', 'w') as f:
    f.write(fixed_content)

print("Fixed code block formatting")
