# novisentinel-site

Landing page for [novisentinel.com](https://novisentinel.com).

Plain static HTML + CSS — no build step, no framework. Open `index.html` in a browser to preview locally.

## Preview locally

```bash
# any of these work
python -m http.server 5500
# or
npx serve .
```

Then visit `http://localhost:5500`.

## Deploy to Cloudflare Pages

1. Push this repo to GitHub.
2. Cloudflare Dashboard → Workers & Pages → **Create application** → **Pages** → **Connect to Git**.
3. Select the `novisentinel-site` repo.
4. Build settings:
   - **Build command**: leave empty
   - **Build output directory**: `/`
5. Deploy.
6. Custom domain: Cloudflare Pages → your project → **Custom domains** → add `novisentinel.com`.
   - Cloudflare automatically creates the CNAME if the domain is already in your Cloudflare account.

## Files

- `index.html` — the whole page
- `styles.css` — design tokens + layout
- `_redirects` — optional, for Cloudflare Pages redirects (e.g., `/github → repo`)
- `_headers` — optional, for cache/security headers

## Design tokens

The colors and typography are carried over from the internal NoviSentinel wireframe. Edit the `:root` block in `styles.css` to change the palette globally.
