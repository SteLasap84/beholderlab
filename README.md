# Beholder Lab — GitHub Pages Starter

This is a ready‑to‑deploy static website for Beholder Lab.

## Quick start (GitHub Pages)
1. Create a new public repository on GitHub, named `beholderlab` (or any name).
2. Upload these files to the repo root.
3. Add a file named `CNAME` (no extension) that contains your domain: `beholderlab.it`
   - If you prefer `.com`, put `beholderlab.com` instead.
4. Add a file named `.nojekyll` (empty) to disable Jekyll auto-processing.
5. In the repo: **Settings → Pages → Build and deployment** → Source: `Deploy from a branch`, Branch: `main`, Folder: `/ (root)`.
6. Wait for the site to build. It will be available at `https://<username>.github.io/<repo>/` and on your domain once DNS is set.

## Custom domain (DNS)
In your domain provider's DNS panel, set either:
- **CNAME**: `www` → `<username>.github.io` (preferred, with a redirect from apex to www)
- For the apex (root) domain like `beholderlab.it`, add the GitHub A records:
    185.199.108.153
    185.199.109.153
    185.199.110.153
    185.199.111.153

Then in GitHub Pages custom domain, enter `www.beholderlab.it` (or your apex). Enable **Enforce HTTPS**.

## Netlify option for forms
The contact page includes a static form with `data-netlify="true"`. It will work if you deploy on Netlify; on GitHub Pages it stays static.

## Editing content
- Update text in the HTML files (Home, People, Research, Publications, Media, Contact).
- Replace `/assets/logo-placeholder.svg` with your real logo and update `<img>` if needed.
- Add publications in `publications.html` under `<ul class="publist">`.

## Developer notes
- No build step: pure HTML/CSS/JS.
- `.nojekyll` prevents Jekyll from interfering with asset paths.
- If you later want a CMS, consider moving to Netlify and wiring Netlify CMS.