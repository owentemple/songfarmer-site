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

## In-Progress: Syncing Book Chapters to Updated PDF

The blog hosts the full text of the Songfarmer book as individual chapter posts in `content/blog/`. These were originally posted from a first-person "I" voice. An updated PDF of the book text exists at `book/UpdatedSongfarmerText.pdf` which uses a co-author "we" voice and includes other text revisions.

**The task**: Compare each chapter blog post against the corresponding chapter in the PDF and update the blog text to match the PDF. Changes typically include:
- Voice shift: "I/my/me" → "we/our/us" (the updated book uses co-author voice)
- Minor wording changes, typo fixes, added/removed words
- The blog posts keep their front matter, book cover image, chapter nav links, Kindle link, and Next chapter link — only the body text is synced to the PDF

**Chapter files and their PDF page ranges** (PDF has 13 pages of front matter before book page 1):
| Chapter | Blog file | PDF pages (of file) |
|---------|-----------|-------------------|
| 1 - Overview | `songfarmer-chapter-one.md` | 14-18 |
| 2 - Set a Goal | `chapter-two-set-a-goal.md` | 19-23 |
| 3 - Create Songwriting Habits | `chapter-3-create-songwriting-habits.md` | 24-32 |
| 4 - Recognizing Song Seeds | `chapter-4-recognizing-song-seeds.md` | 33-35 |
| 5 - Composing | `chapter-5-composing.md` | 36-47 |
| 6 - Improving FLOW | `chapter-six-improving-flow.md` | 48-55 |
| 7 - Improving EDIT | `chapter-seven-improving-edit.md` | 56-68 |
| 8 - Strengthening Habits | `chapter-eight-strengthening-habits.md` | 69-81 |
| 9 - Stickiness | `chapter-nine-stickiness.md` | 82-87 |
| 10 - Collaboration | `chapter-ten-collaboration.md` | 88-91 |
| Prompts | `prompts.md` | 92-93 |
| Conclusion | `conclusion.md` | 94-96 |

**Completed so far**: Chapters 1, 2, 3, 4 (no differences), 5, 6

**Process**: Read 10-20 PDF pages at a time for the chapter, read the blog post, compare section by section, list all differences, then apply edits. Watch for non-breaking spaces (U+00A0) and smart quotes in the blog files — use Python for replacements if the Edit tool fails on special characters.

Also added `book/image-001.jpg` → `static/images/image-001.jpg` (mini habits tracking chart) to Chapter 3.

## Deployment

Push to `main` branch on GitHub. Netlify auto-builds with `hugo --minify`.

DNS: `songfarmer.com` and `www.songfarmer.com` point to Netlify. `app.songfarmer.com` stays on GoDaddy.
