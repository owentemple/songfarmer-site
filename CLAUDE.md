# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## What This Is

Songfarmer marketing site — a Hugo static site for songfarmer.com. Markets the Songfarmer book, workshops, and app, plus hosts a blog (migrated from Tumblr).

The app lives separately at app.songfarmer.com (see the `songfarmer-app` repo).

## Tech Stack

- **Hugo** static site generator (no Node.js, no npm)
- **Netlify** hosting (auto-deploys from GitHub)
- Plain CSS in `assets/css/style.css` (Hugo Pipes for minification/fingerprinting)

## Project Structure

```
content/
  _index.md          — Homepage content
  about.md           — About page
  book.md            — Book page
  blog/
    _index.md        — Blog listing page
    *.md             — Individual blog posts (migrated from Tumblr)
layouts/
  index.html         — Homepage template
  _default/
    baseof.html      — Base HTML skeleton
    list.html        — Paginated list template (blog, tags)
    single.html      — Single page/post template
  partials/
    head.html        — <head> with OG tags, CSS
    nav.html         — Site navigation
    footer.html      — Site footer
    post-card.html   — Blog post card partial
  shortcodes/
    spotify.html     — Spotify embed shortcode
assets/css/
  style.css          — All styles (shares design tokens with the app)
static/
  artpick/           — ArtPick micro-app (standalone HTML/CSS/JS, not Hugo-managed)
  images/            — Logo, process diagram, Tumblr-migrated images
  favicon.png
  _redirects         — Netlify redirect rules
  robots.txt
scripts/
  export_tumblr.py   — One-time Tumblr export script
hugo.toml            — Site configuration
```

## Development

```bash
hugo server          # Local dev server with live reload
hugo server -D       # Include draft posts
hugo --minify        # Production build (output in public/)
```

## Adding a Blog Post

```bash
hugo new blog/my-post-title.md
```

Edit the generated file in `content/blog/`, set `draft: false` when ready.

## Key Patterns

- Design tokens (colors, fonts, spacing) match the app's CSS for brand continuity
- `unsafe = true` in Hugo's Goldmark config allows raw HTML in Markdown (needed for some Tumblr-migrated content)
- Old Tumblr URLs are preserved via Hugo `aliases` in post front matter and Netlify `_redirects`
- The `{{< spotify type id >}}` shortcode embeds Spotify players; YouTube uses Hugo's built-in `{{< youtube id >}}`
- **Nav structure** (consistent across main site, app, and artpick): Home, About, Book, Blog, App, Inspiration, Workshop
- **ArtPick** (`static/artpick/`) is standalone HTML outside Hugo templating — its nav links and styles are hardcoded inline. If the site nav changes, artpick's `index.html` must be updated manually to match.

## Completed: Book Chapter Sync to Updated PDF

The blog hosts the full text of the Songfarmer book as individual chapter posts in `content/blog/`. All chapters have been synced to the updated PDF at `book/UpdatedSongfarmerText.pdf`, which uses a co-author "we" voice and includes other text revisions. The blog posts keep their front matter, book cover image, chapter nav links, and Next chapter link — only the body text was synced.

**Chapter blog files**: `songfarmer-chapter-one.md`, `chapter-two-set-a-goal.md`, `chapter-3-create-songwriting-habits.md`, `chapter-4-recognizing-song-seeds.md`, `chapter-5-composing.md`, `chapter-six-improving-flow.md`, `chapter-seven-improving-edit.md`, `chapter-eight-strengthening-habits.md`, `chapter-nine-stickiness.md`, `chapter-ten-collaboration.md`, `prompts.md`, `conclusion.md`

**Summary of changes made**:
- Voice shift: "I/my/me" → "we/our/us" throughout all chapters
- Some first-person anecdotes reframed as third-person "Owen" quotes (Ch 6, 8)
- Minor wording changes, typo fixes, added/removed sentences across all chapters
- Ch 5 added Bob Dylan trivia section; Ch 7 fixed meaning-changing typos and old book cover image
- Ch 8 had the most changes (18) with several "Owen talks about..." reframings
- Prompts added Songfarmer App prompt; also added `static/images/image-001.jpg` to Ch 3

## Deployment

Push to `main` branch on GitHub. Netlify auto-builds with `hugo --minify`.

DNS: `songfarmer.com` and `www.songfarmer.com` point to Netlify. `app.songfarmer.com` stays on GoDaddy.
