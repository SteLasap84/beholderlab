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

## Scopus publications sync

An automated workflow keeps `assets/publications.json` up-to-date by querying the [Scopus](https://www.scopus.com/) API for the lab author profile.

### What it does
1. Fetches all publications for the configured Scopus Author ID (`36437362600`).
2. Merges new entries into `assets/publications.json` without overwriting manually curated `tech`/`project` fields.
3. Opens (or updates) a pull request titled **"chore(publications): sync from Scopus"** when new publications are found.
4. Does nothing if there are no new publications.

### Required secret
Add the following secret under **Settings → Secrets and variables → Actions → New repository secret**:

| Secret name      | Description                         |
|------------------|-------------------------------------|
| `SCOPUS_API_KEY` | Your Elsevier/Scopus API key        |

### Schedule
The workflow runs **every Monday at 01:00 UTC** (cron: `0 1 * * 1`).

### Manual run
1. Go to **Actions** → **Scopus publications sync**.
2. Click **Run workflow** → **Run workflow**.

The workflow will run immediately and open a PR if new publications are found.

## Developer notes
- No build step: pure HTML/CSS/JS.
- `.nojekyll` prevents Jekyll from interfering with asset paths.
- If you later want a CMS, consider moving to Netlify and wiring Netlify CMS.