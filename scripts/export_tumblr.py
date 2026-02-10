#!/usr/bin/env python3
"""
Export all posts from songfarmer.com (Tumblr) to Hugo-compatible Markdown files.

Usage:
    pip install requests markdownify
    export TUMBLR_API_KEY="your-api-key"
    python scripts/export_tumblr.py

Get an API key at: https://www.tumblr.com/oauth/apps

Output:
    content/blog/*.md   — one Markdown file per post with Hugo front matter
    static/images/tumblr/ — downloaded images from Tumblr-hosted media
"""

import os
import re
import sys
import json
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

try:
    from markdownify import markdownify as md
except ImportError:
    print("Install markdownify: pip install markdownify")
    sys.exit(1)

# ── Config ──────────────────────────────────────────────────────────────────

BLOG = "songfarmer.com"
API_KEY = os.environ.get("TUMBLR_API_KEY", "")
POSTS_PER_PAGE = 20

# Paths (relative to project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = PROJECT_ROOT / "content" / "blog"
IMAGE_DIR = PROJECT_ROOT / "static" / "images" / "tumblr"


def fetch_all_posts():
    """Fetch all posts from the Tumblr API v2, handling pagination."""
    if not API_KEY:
        print("ERROR: Set TUMBLR_API_KEY environment variable.")
        print("Get one at https://www.tumblr.com/oauth/apps")
        sys.exit(1)

    url = f"https://api.tumblr.com/v2/blog/{BLOG}/posts"
    all_posts = []
    offset = 0

    while True:
        params = {"api_key": API_KEY, "limit": POSTS_PER_PAGE, "offset": offset}
        print(f"  Fetching posts {offset}–{offset + POSTS_PER_PAGE}...")
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        posts = data["response"]["posts"]
        if not posts:
            break

        all_posts.extend(posts)
        offset += POSTS_PER_PAGE

        if offset >= data["response"]["total_posts"]:
            break

        time.sleep(0.5)  # be polite

    print(f"  Fetched {len(all_posts)} posts total.")
    return all_posts


def download_image(img_url):
    """Download an image and return the local path (relative to site root)."""
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    # Create a stable filename from the URL
    parsed = urlparse(img_url)
    ext = Path(parsed.path).suffix or ".jpg"
    url_hash = hashlib.md5(img_url.encode()).hexdigest()[:10]
    filename = f"{url_hash}{ext}"
    local_path = IMAGE_DIR / filename

    if local_path.exists():
        return f"/images/tumblr/{filename}"

    try:
        resp = requests.get(img_url, timeout=30)
        resp.raise_for_status()
        local_path.write_bytes(resp.content)
        print(f"    Downloaded: {filename}")
    except Exception as e:
        print(f"    WARN: Could not download {img_url}: {e}")
        return img_url  # fall back to remote URL

    return f"/images/tumblr/{filename}"


def html_to_markdown(html):
    """Convert HTML to Markdown, handling embeds specially."""
    if not html:
        return ""

    # Convert YouTube iframes to Hugo shortcodes before markdownify
    # Match YouTube embed URLs
    html = re.sub(
        r'<iframe[^>]*src=["\'](?:https?:)?//(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]+)[^"\']*["\'][^>]*>(?:</iframe>)?',
        r'{{< youtube \1 >}}',
        html,
        flags=re.IGNORECASE,
    )

    # Convert Spotify iframes to Hugo shortcodes
    html = re.sub(
        r'<iframe[^>]*src=["\'](?:https?:)?//open\.spotify\.com/embed/(track|album|playlist|episode)/([a-zA-Z0-9]+)[^"\']*["\'][^>]*>(?:</iframe>)?',
        r'{{< spotify \1 \2 >}}',
        html,
        flags=re.IGNORECASE,
    )

    # Convert to markdown
    text = md(html, heading_style="ATX", bullets="-")

    # Clean up excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def make_slug(post):
    """Extract or generate a URL slug for the post."""
    if post.get("slug"):
        return post["slug"]
    # Fall back to slugifying the title or using the ID
    title = post.get("title", "") or post.get("summary", "") or str(post["id"])
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:80]


def get_post_body(post):
    """Extract the body HTML from various Tumblr post types."""
    ptype = post.get("type", "text")

    if ptype == "text":
        return post.get("body", "")
    elif ptype == "photo":
        parts = []
        caption = post.get("caption", "")
        for photo in post.get("photos", []):
            alt = photo.get("caption", "")
            # Get the largest available image
            sizes = photo.get("alt_sizes", [])
            if sizes:
                img_url = sizes[0]["url"]
            else:
                img_url = photo.get("original_size", {}).get("url", "")
            if img_url:
                parts.append(f'<img src="{img_url}" alt="{alt}" />')
        if caption:
            parts.append(caption)
        return "\n".join(parts)
    elif ptype == "video":
        parts = []
        # Try to get the embed player
        players = post.get("player", [])
        if players:
            # Use the largest embed
            best = max(players, key=lambda p: p.get("width", 0))
            parts.append(best.get("embed_code", ""))
        caption = post.get("caption", "")
        if caption:
            parts.append(caption)
        return "\n".join(parts)
    elif ptype == "audio":
        parts = []
        player = post.get("player", "")
        if player:
            parts.append(player)
        caption = post.get("caption", "")
        if caption:
            parts.append(caption)
        return "\n".join(parts)
    elif ptype == "link":
        url = post.get("url", "")
        description = post.get("description", "")
        parts = []
        if url:
            title = post.get("title", url)
            parts.append(f'<a href="{url}">{title}</a>')
        if description:
            parts.append(description)
        return "\n".join(parts)
    elif ptype == "quote":
        text = post.get("text", "")
        source = post.get("source", "")
        parts = [f"<blockquote>{text}</blockquote>"]
        if source:
            parts.append(f"<p>— {source}</p>")
        return "\n".join(parts)
    elif ptype == "chat":
        lines = post.get("dialogue", [])
        return "\n".join(f"**{l.get('label', '')}** {l.get('phrase', '')}" for l in lines)
    else:
        return post.get("body", "") or post.get("caption", "") or ""


def process_images_in_markdown(markdown_text):
    """Find image URLs in markdown and download Tumblr-hosted ones."""
    # Match markdown images: ![alt](url)
    def replace_md_image(match):
        alt = match.group(1)
        url = match.group(2)
        if "tumblr.com" in url or "media.tumblr.com" in url:
            local = download_image(url)
            return f"![{alt}]({local})"
        return match.group(0)

    result = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_md_image, markdown_text)

    # Also catch raw <img> tags that markdownify might have left
    def replace_html_image(match):
        url = match.group(1)
        if "tumblr.com" in url or "media.tumblr.com" in url:
            local = download_image(url)
            return f"![image]({local})"
        return match.group(0)

    result = re.sub(r'<img[^>]*src=["\']([^"\']+)["\'][^>]*/?>',  replace_html_image, result)

    return result


def post_to_hugo(post):
    """Convert a single Tumblr post to a Hugo Markdown file."""
    slug = make_slug(post)
    date = datetime.fromtimestamp(post["timestamp"]).strftime("%Y-%m-%dT%H:%M:%S")
    title = post.get("title") or post.get("summary") or post.get("source_title") or slug.replace("-", " ").title()

    # Clean up title — remove markdown/html artifacts
    title = re.sub(r"<[^>]+>", "", title)
    title = title.strip().replace('"', '\\"')

    tags = post.get("tags", [])
    tumblr_url = post.get("post_url", "")
    post_id = post.get("id", "")

    # Build the alias for old Tumblr URL
    aliases = []
    if post_id and slug:
        aliases.append(f"/post/{post_id}/{slug}")
        aliases.append(f"/post/{post_id}")

    # Get body content
    body_html = get_post_body(post)
    body_md = html_to_markdown(body_html)
    body_md = process_images_in_markdown(body_md)

    # Build front matter
    front_matter = {
        "title": title,
        "date": date,
        "slug": slug,
        "tags": tags,
        "aliases": aliases,
        "original_url": tumblr_url,
    }

    # Write the file
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = CONTENT_DIR / f"{slug}.md"

    # Handle duplicate slugs
    counter = 1
    while filepath.exists():
        filepath = CONTENT_DIR / f"{slug}-{counter}.md"
        counter += 1

    lines = ["---"]
    lines.append(f'title: "{front_matter["title"]}"')
    lines.append(f'date: {front_matter["date"]}')
    lines.append(f'slug: "{front_matter["slug"]}"')
    if tags:
        lines.append(f'tags: {json.dumps(tags)}')
    if aliases:
        lines.append(f'aliases: {json.dumps(aliases)}')
    if tumblr_url:
        lines.append(f'original_url: "{tumblr_url}"')
    lines.append("---")
    lines.append("")
    lines.append(body_md)
    lines.append("")

    filepath.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Wrote: {filepath.relative_to(PROJECT_ROOT)}")
    return filepath


def main():
    print("=== Tumblr → Hugo Export ===")
    print(f"Blog: {BLOG}")
    print()

    print("[1/3] Fetching posts from Tumblr API...")
    posts = fetch_all_posts()

    print()
    print("[2/3] Converting posts to Hugo Markdown...")
    for post in posts:
        try:
            post_to_hugo(post)
        except Exception as e:
            print(f"  ERROR on post {post.get('id')}: {e}")

    print()
    print("[3/3] Done!")
    print(f"  Posts written to: {CONTENT_DIR.relative_to(PROJECT_ROOT)}/")
    print(f"  Images saved to:  {IMAGE_DIR.relative_to(PROJECT_ROOT)}/")
    print()
    print("Next steps:")
    print("  1. Review the generated .md files for formatting issues")
    print("  2. Run `hugo server` to preview the site")
    print("  3. Fix any broken embeds or image references")


if __name__ == "__main__":
    main()
